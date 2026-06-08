\set ON_ERROR_STOP on

BEGIN;

WITH payload AS (
  SELECT :'gpx_payload'::jsonb AS p
),
inserted_source AS (
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
    'GaiaGPS field track - ' || COALESCE(p ->> 'track_name', :'file_name'),
    'field_track_gpx',
    'first-party GPX export: ' || :'file_name',
    CURRENT_DATE,
    'First-party field collection. Publishable at owner discretion; hold until board validation.',
    'reference_publish',
    'medium',
    format(
      'Creator: %s. Recorded at: %s. Imported from %s.',
      COALESCE(p ->> 'creator', 'unknown'),
      COALESCE(p ->> 'recorded_at', 'unknown'),
      :'file_name'
    )
  FROM payload
  WHERE NOT EXISTS (
    SELECT 1 FROM source_register.sources s
    WHERE s.source_type = 'field_track_gpx'
      AND s.url_or_contact = 'first-party GPX export: ' || :'file_name'
  )
  RETURNING id
),
source_row AS (
  SELECT id FROM inserted_source
  UNION ALL
  SELECT id FROM source_register.sources
  WHERE source_type = 'field_track_gpx'
    AND url_or_contact = 'first-party GPX export: ' || :'file_name'
  ORDER BY id
  LIMIT 1
),
inserted_capture AS (
  INSERT INTO raw.gpx_captures (
    source_id,
    file_name,
    track_name,
    creator,
    recorded_at,
    segment_count,
    point_count,
    raw_xml,
    notes
  )
  SELECT
    sr.id,
    :'file_name',
    p ->> 'track_name',
    p ->> 'creator',
    NULLIF(p ->> 'recorded_at', '')::timestamptz,
    jsonb_array_length(p -> 'segments'),
    (p ->> 'total_point_count')::integer,
    convert_from(decode(p ->> 'raw_xml_b64', 'base64'), 'UTF8'),
    'GPX capture for ' || :'file_name'
  FROM payload, source_row sr
  ON CONFLICT ON CONSTRAINT gpx_captures_file_recorded_uniq DO NOTHING
  RETURNING id
),
seg_rows AS (
  SELECT
    sr.id AS source_id,
    p ->> 'track_name' AS track_name,
    seg
  FROM payload, source_row sr,
       LATERAL jsonb_array_elements(p -> 'segments') AS seg
),
inserted_tracks AS (
  -- Field tracks now live in the converged core.features (layer='field_tracks');
  -- segment_index/point_count/recorded_*/ele_* land in attrs (2026-06-07 table
  -- cleanup). No FK/CHECK; the segment data is stored, never rejected (C5).
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
    'field_tracks',
    seg_rows.track_name,
    'candidate',
    'medium',
    'publish',
    'hold',
    'field_tracks:' || seg_rows.source_id || ':' || (seg ->> 'segment_index'),
    seg_rows.source_id,
    ST_SetSRID(ST_GeomFromText(seg ->> 'wkt'), 4326),
    jsonb_strip_nulls(jsonb_build_object(
      'segment_index', (seg ->> 'segment_index')::integer,
      'point_count', (seg ->> 'point_count')::integer,
      'recorded_start', NULLIF(seg ->> 'recorded_start', '')::timestamptz,
      'recorded_end', NULLIF(seg ->> 'recorded_end', '')::timestamptz,
      'ele_min', seg -> 'ele_min',
      'ele_max', seg -> 'ele_max',
      'source_file', :'file_name'
    )),
    format(
      'Field track segment %s from %s. Recorded with %s. Candidate evidence; not validated against board markup.',
      seg ->> 'segment_index',
      :'file_name',
      COALESCE((SELECT p ->> 'creator' FROM payload), 'unknown')
    ),
    now()
  FROM seg_rows
  WHERE NOT EXISTS (
    -- IS NOT DISTINCT FROM treats NULL = NULL as TRUE; a plain `=` returns
    -- UNKNOWN there and would silently re-import segments with no recorded_start.
    -- Content match (layer + source + segment + recorded_start) -- so a re-run
    -- after the migration sees the moved rows and never double-imports.
    SELECT 1 FROM core.features existing
    WHERE existing.layer = 'field_tracks'
      AND existing.source_id = seg_rows.source_id
      AND (existing.attrs ->> 'segment_index')::integer = (seg ->> 'segment_index')::integer
      AND NULLIF(existing.attrs ->> 'recorded_start', '')::timestamptz IS NOT DISTINCT FROM
          NULLIF(seg ->> 'recorded_start', '')::timestamptz
  )
  ON CONFLICT (source_key) DO NOTHING
  RETURNING id, (attrs ->> 'segment_index') AS segment_index, source_id
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
  it.id,
  it.source_id,
  format('GPX field track segment %s recorded by GaiaGPS', it.segment_index),
  'medium',
  CURRENT_DATE,
  'needs_field_check',
  'First-party field recording. Hold publish until reconciled against board markup or repeat tracks.'
FROM inserted_tracks it
WHERE NOT EXISTS (
  SELECT 1 FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'features'
    AND fs.feature_id = it.id
    AND fs.source_id = it.source_id
);

COMMIT;

SELECT 'gpx_import_summary' AS result;

SELECT
  ft.id,
  ft.name AS track_name,
  ft.attrs ->> 'segment_index' AS segment_index,
  ft.attrs ->> 'point_count' AS point_count,
  ft.attrs ->> 'recorded_start' AS recorded_start,
  ft.attrs ->> 'recorded_end' AS recorded_end,
  ft.status,
  ft.confidence,
  ft.permission,
  ft.publish_status,
  ROUND(ST_Length(ft.geom::geography)::numeric, 1) AS length_m,
  ROUND(ST_Length(ft.geom::geography)::numeric / 1609.344, 2) AS length_mi
FROM core.features ft
JOIN source_register.sources s ON s.id = ft.source_id
WHERE ft.layer = 'field_tracks'
  AND s.source_type = 'field_track_gpx'
  AND s.url_or_contact = 'first-party GPX export: ' || :'file_name'
ORDER BY (ft.attrs ->> 'segment_index')::integer;

SELECT
  id,
  file_name,
  track_name,
  creator,
  recorded_at,
  segment_count,
  point_count,
  length(raw_xml) AS raw_xml_bytes
FROM raw.gpx_captures
WHERE file_name = :'file_name'
ORDER BY id;
