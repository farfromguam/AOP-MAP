\set ON_ERROR_STOP on

-- One-shot migration: fold the 8 per-layer geo tables into the converged
-- core.features (the "so many tables" cleanup, 2026-06-07; user directive:
-- "figure out the minimum and migrate data into that shape" -> full fold to
-- 7 tables + 1 view). Every row MOVES; nothing is lost. The CMFS spine columns
-- map straight across; each table's domain-specific columns + its jsonb side-bag
-- land in core.features.attrs (no allowlist, no CHECK -- C5/no_limiting_code).
--
-- source_key = '<layer>:<old_id>' (faithful provenance of where the row came
-- from). The rewritten pipeline scripts dedup on row CONTENT (layer + name +
-- source_id / segment), so a live re-run sees these migrated rows and never
-- double-inserts -- the source_key scheme need not match.
--
-- Run once against the live volume AFTER pg_dump backup:
--   docker compose exec -T db psql -U aop -d aop_map < mvp/scripts/migrate_layers_to_core_features.sql
-- This targets tables that are DROPPED at the end of the cleanup, so it is a
-- historical one-shot, not part of fresh-volume init (init_db.sql has no
-- per-layer tables after the cleanup).

BEGIN;

-- 1. trail_centerlines (LineString; difficulty -> attrs) -------------------
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes, last_verified,
   created_at, updated_at)
SELECT 'trail_centerlines', name, NULL, NULL, false, status, confidence,
       permission, publish_status, 'trail_centerlines:'||id, source_id, geom,
       jsonb_strip_nulls(jsonb_build_object('difficulty', difficulty)),
       notes, last_verified, created_at, updated_at
FROM core.trail_centerlines
ON CONFLICT (source_key) DO NOTHING;

-- 2. park_boundaries (MultiPolygon; no domain extras) ----------------------
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes, last_verified,
   created_at, updated_at)
SELECT 'park_boundaries', name, NULL, NULL, false, status, confidence,
       permission, publish_status, 'park_boundaries:'||id, source_id, geom,
       '{}'::jsonb, notes, last_verified, created_at, updated_at
FROM core.park_boundaries
ON CONFLICT (source_key) DO NOTHING;

-- 3. trailheads (Point; no domain extras) ----------------------------------
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes,
   created_at, updated_at)
SELECT 'trailheads', name, NULL, NULL, false, status, confidence,
       permission, publish_status, 'trailheads:'||id, source_id, geom,
       '{}'::jsonb, notes, created_at, updated_at
FROM core.trailheads
ON CONFLICT (source_key) DO NOTHING;

-- 4. parcels (Polygon; parcel_id/owner/land_area + metadata -> attrs) -------
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes, last_verified,
   created_at, updated_at)
SELECT 'parcels', 'Parcel '||parcel_id, NULL, NULL, false, status, confidence,
       permission, publish_status, 'parcels:'||id, source_id, geom,
       jsonb_strip_nulls(jsonb_build_object(
         'parcel_id', parcel_id, 'owner', owner, 'land_area', land_area))
         || coalesce(metadata, '{}'::jsonb),
       notes, last_verified, created_at, updated_at
FROM core.parcels
ON CONFLICT (source_key) DO NOTHING;

-- 5. observations (Geometry; type/review/measured + metadata -> attrs) ------
--    no permission/publish_status columns -> NULL (correctly never published).
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes,
   created_at, updated_at)
SELECT 'observations', observation_type, NULL, NULL, false, status, confidence,
       NULL, NULL, 'observations:'||id, source_id, geom,
       jsonb_strip_nulls(jsonb_build_object(
         'observation_type', observation_type, 'review_status', review_status,
         'measured_at', measured_at))
         || coalesce(metadata, '{}'::jsonb),
       notes, created_at, updated_at
FROM core.observations
ON CONFLICT (source_key) DO NOTHING;

-- 6. field_tracks (LineString; segment/point_count/recorded + metadata) -----
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes, last_verified,
   created_at, updated_at)
SELECT 'field_tracks', track_name, NULL, NULL, false, status, confidence,
       permission, publish_status, 'field_tracks:'||id, source_id, geom,
       jsonb_strip_nulls(jsonb_build_object(
         'segment_index', segment_index, 'point_count', point_count,
         'recorded_start', recorded_start, 'recorded_end', recorded_end))
         || coalesce(metadata, '{}'::jsonb),
       notes, last_verified, created_at, updated_at
FROM core.field_tracks
ON CONFLICT (source_key) DO NOTHING;

-- 7. hazards (Point; type/severity -> attrs) -- 0 rows today, kept for repro -
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes,
   created_at, updated_at)
SELECT 'hazards', hazard_type, NULL, NULL, false, status, confidence,
       permission, publish_status, 'hazards:'||id, source_id, geom,
       jsonb_strip_nulls(jsonb_build_object(
         'hazard_type', hazard_type, 'severity', severity)),
       notes, created_at, updated_at
FROM core.hazards
ON CONFLICT (source_key) DO NOTHING;

-- 8. print_annotations (Geometry; annotation_type -> attrs) -- 0 rows today --
INSERT INTO core.features
  (layer, name, kind, description, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, attrs, notes,
   created_at, updated_at)
SELECT 'print_annotations', annotation_type, NULL, NULL, false, status, NULL,
       NULL, NULL, 'print_annotations:'||id, source_id, geom,
       jsonb_strip_nulls(jsonb_build_object('annotation_type', annotation_type)),
       notes, created_at, updated_at
FROM core.print_annotations
ON CONFLICT (source_key) DO NOTHING;

-- 9. Re-point provenance: every feature_sources row that named a per-layer
--    table now points at core.features (feature_table='features', new id).
--    Matched via the source_key we just assigned ('<table>:<old_id>').
UPDATE source_register.feature_sources fs
SET feature_table = 'features',
    feature_id = cf.id
FROM core.features cf
WHERE fs.feature_schema = 'core'
  AND fs.feature_table IN ('trail_centerlines','park_boundaries','trailheads',
                           'parcels','observations','field_tracks','hazards',
                           'print_annotations')
  AND cf.source_key = fs.feature_table || ':' || fs.feature_id;

COMMIT;

-- Report -------------------------------------------------------------------
SELECT 'core.features by migrated layer' AS report, layer, count(*)
FROM core.features
WHERE layer IN ('trail_centerlines','park_boundaries','trailheads','parcels',
                'observations','field_tracks','hazards','print_annotations')
GROUP BY layer ORDER BY layer;

SELECT 'feature_sources still pointing at a per-layer table (should be 0)' AS check,
       count(*)
FROM source_register.feature_sources
WHERE feature_schema = 'core'
  AND feature_table IN ('trail_centerlines','park_boundaries','trailheads',
                        'parcels','observations','field_tracks','hazards',
                        'print_annotations');
