-- Seed the real published park_boundary rows into core.features (layer='park_boundaries').
--
-- Background: the AOP working-envelope park_boundary lives in core via the one-time
-- migrate_layers_to_core_features.sql, but the Ellis Cemetery inholding parcel was
-- SERVED-ONLY -- it lived only in website/data/publish.geojson and no table held it,
-- so the DB-only bake (export_publish_geojson.sh) dropped it. Going gold, the bake is
-- the sole writer of the served files, so every published feature must live in core.
-- This migrates the Ellis inholding into core so the bake preserves it.
-- Card: brain/tasks/07_tables/description_blurb_convergence.md (Slice 5).
--
-- Idempotent via ON CONFLICT (source_key) DO NOTHING -- re-running never duplicates
-- and never mutates an existing row (loop contract: no DELETE/clobber of core).
-- Self-seeds its provenance source so a fresh volume carries it too (the source row
-- is otherwise created by a live parcel import that is not mounted on fresh volumes).

\set ON_ERROR_STOP on

BEGIN;

-- Provenance: the TN Comptroller Marion County parcel layer. On the live DB this
-- row already exists (id 3, created by import_aop_parcel_boundary.sql, which is NOT
-- mounted on fresh volumes), so the guard skips. The field values below are copied
-- VERBATIM from that canonical definition so a fresh-volume self-seed is byte-identical
-- to live -- one definition of the source, not a second divergent spelling.
INSERT INTO source_register.sources
  (name, source_type, url_or_contact, retrieved_on, license_or_permission,
   publish_status, confidence_default, notes)
SELECT
  'Tennessee Comptroller Marion County parcel layer',
  'arcgis_feature_service',
  'https://services.arcgis.com/rD2ylXRs80UroD90/arcgis/rest/services/TN_County_Parcel_Map/FeatureServer/35',
  '2026-05-20',
  'Public Tennessee Comptroller GIS parcel data product. Parcel GIS is reference data, not a legal survey.',
  'reference_publish', 'medium',
  'Layer: TN_County_Parcel_Map FeatureServer/35 Marion_Parcels. Comptroller parcel page says county parcel data is downloadable and updated monthly around the first business day.'
WHERE NOT EXISTS (
  SELECT 1 FROM source_register.sources WHERE name = 'Tennessee Comptroller Marion County parcel layer'
);

-- The Ellis Cemetery inholding parcel (parcel 110 008.04, ~0.12 ac) -- the interior
-- parcel excluded from the AOP working envelope. publish/publish so the gate serves it.
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, notes, last_verified)
SELECT 'park_boundaries',
       'Ellis Cemetery (inholding parcel)',
       'cemetery',
       'Ellis Cemetery — the AOP inholding. The interior parcel (110 008.04, ~0.12 ac) excluded from the AOP working envelope: the hole carved out of parent parcel 110 008.00. Reached from Ellis Cove Road just past the Battle Creek bridge. Private family cemetery; stay clear of the parcel.',
       false, 'parcel record', 'high', 'publish', 'publish',
       'park_boundaries:ellis-inholding',
       (SELECT id FROM source_register.sources WHERE name = 'Tennessee Comptroller Marion County parcel layer'),
       ST_SetSRID(ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[-85.7436206431795,35.089559579303],[-85.7436660622773,35.0894623211707],[-85.744114042731,35.0894792321848],[-85.7441055298638,35.0895802044173],[-85.7436206431795,35.089559579303]]]}'), 4326),
       'Migrated from served-only publish.geojson (id=5) into core so the bake preserves it (the DB-only bake dropped it). Card: 07_tables/description_blurb_convergence.md (Slice 5).',
       now()
ON CONFLICT (source_key) DO NOTHING;

COMMIT;

-- Report what landed and what the publish gate lets through.
SELECT 'PARK_BOUNDARIES_IN_CORE=' || count(*) FROM core.features WHERE layer = 'park_boundaries' AND archived_at IS NULL;
SELECT 'ELLIS_PUBLISHED=' || count(*) FROM publish.features WHERE layer = 'park_boundaries' AND name = 'Ellis Cemetery (inholding parcel)';
