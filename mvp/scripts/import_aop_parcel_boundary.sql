\set ON_ERROR_STOP on

-- Schema (core.features + the publish.features view) is owned by mvp/init_db.sql.
-- This script only imports data; run init_db.sql first if the DB is fresh.
--
-- 2026-06-07 table cleanup: parcels and the park boundary envelope now live in
-- the converged core.features (layer='parcels' / layer='park_boundaries'); the
-- per-parcel assessment columns + the GIS metadata land in attrs (no allowlist,
-- no CHECK -- C5). The parcel upsert keys on attrs->>'parcel_id'; the envelope is
-- the union of the included parcel geometries.

BEGIN;

WITH inserted_source AS (
  INSERT INTO source_register.sources (
    name,
    source_type,
    url_or_contact,
    retrieved_on,
    license_or_permission,
    publish_status,
    confidence_default,
    notes
  )
  SELECT
    'Tennessee Comptroller Marion County parcel layer',
    'arcgis_feature_service',
    :'parcel_service_url',
    CURRENT_DATE,
    'Public Tennessee Comptroller GIS parcel data product. Parcel GIS is reference data, not a legal survey.',
    'reference_publish',
    'medium',
    'Layer: TN_County_Parcel_Map FeatureServer/35 Marion_Parcels. Comptroller parcel page says county parcel data is downloadable and updated monthly around the first business day.'
  WHERE NOT EXISTS (
    SELECT 1
    FROM source_register.sources
    WHERE name = 'Tennessee Comptroller Marion County parcel layer'
  )
  RETURNING id
),
source_row AS (
  SELECT id FROM inserted_source
  UNION ALL
  SELECT id
  FROM source_register.sources
  WHERE name = 'Tennessee Comptroller Marion County parcel layer'
  ORDER BY id
  LIMIT 1
)
UPDATE source_register.sources s
SET
  url_or_contact = :'parcel_service_url',
  retrieved_on = CURRENT_DATE,
  notes = 'Layer: TN_County_Parcel_Map FeatureServer/35 Marion_Parcels. Comptroller parcel page says county parcel data is downloadable and updated monthly around the first business day.',
  updated_at = now()
FROM source_row r
WHERE s.id = r.id;

WITH inserted_source AS (
  INSERT INTO source_register.sources (
    name,
    source_type,
    url_or_contact,
    retrieved_on,
    license_or_permission,
    publish_status,
    confidence_default,
    notes
  )
  SELECT
    'Official Adventure Off Road Park website',
    'official_site',
    :'official_aop_url',
    CURRENT_DATE,
    'Public web reference. Digital trail-map reuse permission is not established by this row.',
    'reference_only',
    'medium',
    'Used for current public claims such as 600+ acres and 120+ trails. Ask AOP directly before reusing official map artwork or trail data.'
  WHERE NOT EXISTS (
    SELECT 1
    FROM source_register.sources
    WHERE name = 'Official Adventure Off Road Park website'
  )
  RETURNING id
),
source_row AS (
  SELECT id FROM inserted_source
  UNION ALL
  SELECT id
  FROM source_register.sources
  WHERE name = 'Official Adventure Off Road Park website'
  ORDER BY id
  LIMIT 1
)
UPDATE source_register.sources s
SET
  url_or_contact = :'official_aop_url',
  retrieved_on = CURRENT_DATE,
  notes = 'Used for current public claims such as 600+ acres and 120+ trails. Ask AOP directly before reusing official map artwork or trail data.',
  updated_at = now()
FROM source_row r
WHERE s.id = r.id;

-- Demo MVP scaffolding rows (now core.features carrying their old layer tag).
UPDATE core.features
SET permission = 'internal', publish_status = 'demo_hold', updated_at = now()
WHERE layer = 'trail_centerlines'
  AND name IN ('Demo Ridge Trail', 'MVP Smoke: Board-Validated Connector');

UPDATE core.features
SET permission = 'internal', publish_status = 'demo_hold', updated_at = now()
WHERE layer = 'trailheads' AND name = 'Demo Trailhead';

UPDATE core.features
SET permission = 'internal', publish_status = 'demo_hold', updated_at = now()
WHERE layer = 'park_boundaries' AND name = 'Demo Park Boundary';

WITH parcel_features AS (
  SELECT value AS feature
  FROM jsonb_array_elements(:'parcel_features'::jsonb) AS features(value)
),
parcel_parts AS (
  SELECT
    feature,
    feature -> 'properties' AS attrs,
    feature -> 'geometry' AS geometry,
    feature -> 'properties' ->> 'Assessment_Data_58_ID' AS parcel_id,
    feature -> 'properties' ->> 'Assessment_Data_58_ADDRESS' AS address,
    ST_SetSRID(ST_GeomFromGeoJSON((feature -> 'geometry')::text), 4326)::geometry(Polygon,4326) AS geom
  FROM parcel_features
),
parcel_source AS (
  SELECT id
  FROM source_register.sources
  WHERE name = 'Tennessee Comptroller Marion County parcel layer'
  ORDER BY id
  LIMIT 1
),
official_source AS (
  SELECT id
  FROM source_register.sources
  WHERE name = 'Official Adventure Off Road Park website'
  ORDER BY id
  LIMIT 1
),
raw_capture AS (
  INSERT INTO raw.arcgis_feature_captures (
    source_id,
    source_url,
    query_where,
    feature_json,
    notes
  )
  SELECT
    ps.id,
    :'parcel_service_url',
    :'query_where',
    pp.feature,
    format(
      'AOP candidate parcel capture for included parcel %s at %s.',
      pp.parcel_id,
      coalesce(nullif(pp.address, ''), 'unknown address')
    )
  FROM parcel_parts pp
  CROSS JOIN parcel_source ps
  WHERE NOT EXISTS (
    SELECT 1
    FROM raw.arcgis_feature_captures existing
    WHERE existing.source_url = :'parcel_service_url'
      AND existing.query_where = :'query_where'
      AND existing.feature_json -> 'properties' ->> 'GlobalID' = pp.feature -> 'properties' ->> 'GlobalID'
  )
  RETURNING id
),
-- The per-parcel attrs bag the converged row carries (assessment + GIS metadata
-- + the identity columns parcels used to hold as their own fields).
parcel_attrs AS (
  SELECT
    pp.parcel_id,
    pp.geom,
    nullif(trim(concat_ws(' ', pp.attrs ->> 'Assessment_Data_58_OWNER', nullif(pp.attrs ->> 'Assessment_Data_58_OWNER2', ' '))), '') AS owner,
    nullif(pp.attrs ->> 'Parcels_CALC_ACRE', '')::numeric AS land_area,
    jsonb_strip_nulls(jsonb_build_object(
      'parcel_id', pp.parcel_id,
      'owner', nullif(trim(concat_ws(' ', pp.attrs ->> 'Assessment_Data_58_OWNER', nullif(pp.attrs ->> 'Assessment_Data_58_OWNER2', ' '))), ''),
      'land_area', nullif(pp.attrs ->> 'Parcels_CALC_ACRE', '')::numeric,
      'objectid', pp.attrs -> 'OBJECTID',
      'globalid', pp.attrs ->> 'GlobalID',
      'gislink', pp.attrs ->> 'Parcels_GISLINK',
      'parcelid', pp.attrs ->> 'Assessment_Data_58_PARCELID',
      'assessment_id', pp.attrs ->> 'Assessment_Data_58_ID',
      'address', pp.attrs ->> 'Assessment_Data_58_ADDRESS',
      'class', pp.attrs ->> 'Assessment_Data_58_CLASS',
      'deed_acres', nullif(pp.attrs ->> 'Assessment_Data_58_DEEDAC', '')::numeric,
      'landuse', pp.attrs ->> 'Assessment_Data_58_LANDUSE',
      'source_layer', 'Marion_Parcels',
      'source_query_where', :'query_where'
    )) AS attrs
  FROM parcel_parts pp
),
updated_parcels AS (
  UPDATE core.features p
  SET
    name = 'Parcel ' || pa.parcel_id,
    source_id = ps.id,
    geom = pa.geom,
    attrs = pa.attrs,
    notes = 'AOP candidate parcel from Tennessee Comptroller Marion County parcel layer. Reference only; not a legal survey.',
    status = 'candidate',
    confidence = 'medium',
    permission = 'publish',
    publish_status = 'hold',
    last_verified = now(),
    updated_at = now()
  FROM parcel_attrs pa
  CROSS JOIN parcel_source ps
  WHERE p.layer = 'parcels'
    AND p.attrs ->> 'parcel_id' = pa.parcel_id
  RETURNING p.id, p.attrs ->> 'parcel_id' AS parcel_id, p.attrs, p.geom
),
inserted_parcels AS (
  INSERT INTO core.features (
    layer, name, source_key, source_id, geom, attrs, notes,
    status, confidence, permission, publish_status, last_verified
  )
  SELECT
    'parcels',
    'Parcel ' || pa.parcel_id,
    'parcels:' || pa.parcel_id,
    ps.id,
    pa.geom,
    pa.attrs,
    'AOP candidate parcel from Tennessee Comptroller Marion County parcel layer. Reference only; not a legal survey.',
    'candidate',
    'medium',
    'publish',
    'hold',
    now()
  FROM parcel_attrs pa
  CROSS JOIN parcel_source ps
  WHERE NOT EXISTS (
    SELECT 1
    FROM core.features existing
    WHERE existing.layer = 'parcels'
      AND existing.attrs ->> 'parcel_id' = pa.parcel_id
  )
  -- A batch can carry the same parcel twice (duplicate ArcGIS capture); both
  -- rows pass the pre-statement NOT EXISTS guard and generate the same
  -- source_key. DO NOTHING stores the first and skips the rest -- never throws,
  -- never rejects the batch (C5/no_limiting_code_mvp).
  ON CONFLICT (source_key) DO NOTHING
  RETURNING id, attrs ->> 'parcel_id' AS parcel_id, attrs, geom
),
parcel_rows AS (
  SELECT DISTINCT ON (parcel_id)
    id,
    parcel_id,
    attrs,
    geom
  FROM (
    SELECT id, parcel_id, attrs, geom FROM updated_parcels
    UNION ALL
    SELECT id, parcel_id, attrs, geom FROM inserted_parcels
    UNION ALL
    SELECT p.id, p.attrs ->> 'parcel_id' AS parcel_id, p.attrs, p.geom
    FROM core.features p
    JOIN parcel_attrs pa ON p.attrs ->> 'parcel_id' = pa.parcel_id
    WHERE p.layer = 'parcels'
  ) rows
  ORDER BY parcel_id, id
),
boundary_stats AS (
  SELECT
    count(*) AS parcel_count,
    sum((attrs ->> 'land_area')::numeric) AS calculated_acres,
    sum(nullif(attrs ->> 'deed_acres', '')::numeric) AS deed_acres,
    string_agg(
      format(
        '%s at %s',
        parcel_id,
        coalesce(nullif(attrs ->> 'address', ''), 'unknown address')
      ),
      ', '
      ORDER BY parcel_id
    ) AS parcel_list,
    ST_Multi(ST_UnaryUnion(ST_Collect(geom)))::geometry(MultiPolygon,4326) AS geom
  FROM parcel_rows
),
existing_boundary AS (
  SELECT id
  FROM core.features
  WHERE layer = 'park_boundaries'
    AND name IN (
      'AOP working parcel envelope - Ellis Cove Road 1040',
      'AOP working parcel envelope - included parcel candidates'
    )
  ORDER BY id
  LIMIT 1
),
updated_boundary AS (
  UPDATE core.features b
  SET
    name = 'AOP working parcel envelope - included parcel candidates',
    status = 'candidate',
    confidence = 'medium',
    permission = 'publish',
    publish_status = 'publish',
    source_id = ps.id,
    geom = bs.geom,
    notes = format(
      'Working AOP envelope from %s Tennessee Comptroller parcels: %s. Included parcels total %s calculated acres and %s deed acres; official AOP site says 600+ acres, so current holdings still need verification. Public GIS reference only; not a legal survey.',
      bs.parcel_count,
      bs.parcel_list,
      bs.calculated_acres,
      bs.deed_acres
    ),
    last_verified = now(),
    updated_at = now()
  FROM boundary_stats bs
  CROSS JOIN parcel_source ps
  CROSS JOIN existing_boundary eb
  WHERE b.id = eb.id
  RETURNING b.id
),
inserted_boundary AS (
  INSERT INTO core.features (
    layer,
    name,
    status,
    confidence,
    permission,
    publish_status,
    source_key,
    source_id,
    geom,
    attrs,
    notes,
    last_verified
  )
  SELECT
    'park_boundaries',
    'AOP working parcel envelope - included parcel candidates',
    'candidate',
    'medium',
    'publish',
    'publish',
    'park_boundaries:envelope',
    ps.id,
    bs.geom,
    '{}'::jsonb,
    format(
      'Working AOP envelope from %s Tennessee Comptroller parcels: %s. Included parcels total %s calculated acres and %s deed acres; official AOP site says 600+ acres, so current holdings still need verification. Public GIS reference only; not a legal survey.',
      bs.parcel_count,
      bs.parcel_list,
      bs.calculated_acres,
      bs.deed_acres
    ),
    now()
  FROM boundary_stats bs
  CROSS JOIN parcel_source ps
  WHERE NOT EXISTS (
      SELECT 1
      FROM core.features existing
      WHERE existing.layer = 'park_boundaries'
        AND existing.name IN (
          'AOP working parcel envelope - Ellis Cove Road 1040',
          'AOP working parcel envelope - included parcel candidates'
        )
    )
  ON CONFLICT (source_key) DO NOTHING
  RETURNING id
),
boundary_row AS (
  SELECT id FROM updated_boundary
  UNION ALL
  SELECT id FROM inserted_boundary
  UNION ALL
  SELECT id
  FROM core.features
  WHERE layer = 'park_boundaries'
    AND name IN (
      'AOP working parcel envelope - Ellis Cove Road 1040',
      'AOP working parcel envelope - included parcel candidates'
    )
  ORDER BY id
  LIMIT 1
)
INSERT INTO source_register.feature_sources (
  feature_schema,
  feature_table,
  feature_id,
  source_id,
  claim,
  confidence,
  last_checked,
  review_status,
  notes
)
SELECT
  'core',
  'features',
  pr.id,
  ps.id,
  format('parcel geometry and assessment attributes for included AOP parcel %s', pr.parcel_id),
  'medium',
  CURRENT_DATE,
  'reviewed',
  format(
    'Imported from Tennessee Comptroller Marion_Parcels FeatureServer layer. Source parcel id: %s.',
    pr.attrs ->> 'parcelid'
  )
FROM parcel_rows pr
CROSS JOIN parcel_source ps
WHERE NOT EXISTS (
  SELECT 1
  FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'features'
    AND fs.feature_id = pr.id
    AND fs.source_id = ps.id
    AND fs.claim = format('parcel geometry and assessment attributes for included AOP parcel %s', pr.parcel_id)
)
UNION ALL
SELECT
  'core',
  'features',
  br.id,
  ps.id,
  'candidate AOP envelope from included Tennessee Comptroller parcel geometries',
  'medium',
  CURRENT_DATE,
  'needs_field_check',
  format('Parcel boundary is reference geometry only and should not be treated as a legal survey. Included parcels: %s.', bs.parcel_list)
FROM boundary_row br
CROSS JOIN parcel_source ps
CROSS JOIN boundary_stats bs
WHERE NOT EXISTS (
  SELECT 1
  FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'features'
    AND fs.feature_id = br.id
    AND fs.source_id = ps.id
    AND fs.claim = 'candidate AOP envelope from included Tennessee Comptroller parcel geometries'
)
UNION ALL
SELECT
  'core',
  'features',
  br.id,
  os.id,
  'official AOP site says 600+ acres and 120+ trails',
  'medium',
  CURRENT_DATE,
  'needs_field_check',
  'Imported candidate parcel acreage partially reconciles the official acreage claim, but current holdings still need verification.'
FROM boundary_row br
CROSS JOIN official_source os
WHERE NOT EXISTS (
  SELECT 1
  FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'features'
    AND fs.feature_id = br.id
    AND fs.source_id = os.id
    AND fs.claim = 'official AOP site says 600+ acres and 120+ trails'
);

COMMIT;

SELECT 'aop_parcel_boundary_import_summary' AS result;

SELECT
  p.id,
  p.attrs ->> 'parcel_id' AS parcel_id,
  (p.attrs ->> 'land_area')::numeric AS calculated_acres,
  p.attrs ->> 'deed_acres' AS deed_acres,
  p.status,
  p.confidence,
  p.publish_status,
  p.attrs ->> 'address' AS address
FROM core.features p
WHERE p.layer = 'parcels'
  AND p.attrs ->> 'parcel_id' IN (
    SELECT feature -> 'properties' ->> 'Assessment_Data_58_ID'
    FROM jsonb_array_elements(:'parcel_features'::jsonb) AS features(feature)
  )
ORDER BY p.id;

SELECT
  id,
  name,
  status,
  confidence,
  permission,
  publish_status,
  ST_GeometryType(geom) AS geometry_type,
  round((ST_Area(geom::geography) / 4046.8564224)::numeric, 2) AS approximate_geometry_acres
FROM core.features
WHERE layer = 'park_boundaries'
  AND name IN (
    'AOP working parcel envelope - Ellis Cove Road 1040',
    'AOP working parcel envelope - included parcel candidates'
  )
ORDER BY id;
