\set ON_ERROR_STOP on

-- Promote field tracks for a given GPX file_name into a published trail.
-- Source and target now both live in the converged core.features (2026-06-07
-- table cleanup): field tracks are layer='field_tracks', promoted trails are
-- layer='trail_centerlines' with publish/publish gates, linked back to the same
-- source for provenance. The validation loop (capture -> field track -> promote
-- -> publish) is unchanged in shape -- it just runs on one table now.
--
-- Usage:
--   docker compose exec -T db psql -U aop -d aop_map \
--     -v file_name='Saturday_Afternoon_Activity.gpx' \
--     < mvp/scripts/promote_gpx_to_trail.sql

BEGIN;

WITH source_row AS (
  SELECT id
  FROM source_register.sources
  WHERE source_type = 'field_track_gpx'
    AND url_or_contact = 'first-party GPX export: ' || :'file_name'
  ORDER BY id
  LIMIT 1
),
candidates AS (
  SELECT
    ft.id          AS field_track_id,
    ft.name        AS track_name,
    ft.attrs ->> 'segment_index' AS segment_index,
    ft.geom,
    ft.source_id,
    ft.confidence,
    format('%s (segment %s)', ft.name, ft.attrs ->> 'segment_index') AS trail_name
  FROM core.features ft
  JOIN source_row sr ON sr.id = ft.source_id
  WHERE ft.layer = 'field_tracks'
),
upserted AS (
  INSERT INTO core.features (
    layer, name, kind, description, status, confidence,
    permission, publish_status, source_key, source_id, geom, attrs, notes, last_verified
  )
  SELECT
    'trail_centerlines',
    c.trail_name,
    NULL, NULL,
    'observed',
    c.confidence,
    'publish',
    'publish',
    'trail_centerlines:promote:' || c.source_id || ':' || c.segment_index,
    c.source_id,
    c.geom,
    jsonb_build_object('difficulty', 'unrated'),
    format(
      'Promoted from field track (core.features id %s, GPX %s). First-party GaiaGPS recording; difficulty unrated until field review.',
      c.field_track_id, :'file_name'
    ),
    now()
  FROM candidates c
  WHERE NOT EXISTS (
    SELECT 1 FROM core.features t
    WHERE t.layer = 'trail_centerlines'
      AND t.name = c.trail_name AND t.source_id = c.source_id
  )
  ON CONFLICT (source_key) DO NOTHING
  RETURNING id, name, source_id
),
promoted_tracks AS (
  -- Mark the source field track promoted. The track stays held; the promoted
  -- trail centerline is the publishable artifact, not the raw track.
  UPDATE core.features ft
  SET
    status = 'promoted',
    publish_status = 'hold',
    updated_at = now()
  FROM candidates c
  WHERE ft.layer = 'field_tracks' AND ft.id = c.field_track_id
  RETURNING ft.id
)
INSERT INTO source_register.feature_sources (
  feature_schema, feature_table, feature_id, source_id,
  claim, confidence, last_checked, review_status, notes
)
SELECT
  'core', 'features', u.id, u.source_id,
  'first-party GPX ride promoted into trail centerline',
  'medium', CURRENT_DATE, 'verified',
  'Promotion path: raw.gpx_captures -> core.features field_tracks -> core.features trail_centerlines.'
FROM upserted u
WHERE NOT EXISTS (
  SELECT 1 FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'features'
    AND fs.feature_id = u.id
    AND fs.source_id = u.source_id
    AND fs.claim = 'first-party GPX ride promoted into trail centerline'
);

COMMIT;

SELECT 'promotion_summary' AS result;

SELECT
  t.id, t.name, t.status, t.publish_status, t.permission, t.confidence,
  ROUND(ST_Length(t.geom::geography)::numeric, 1) AS length_m,
  ROUND(ST_Length(t.geom::geography)::numeric / 1609.344, 2) AS length_mi
FROM core.features t
JOIN source_register.sources s ON s.id = t.source_id
WHERE t.layer = 'trail_centerlines'
  AND s.source_type = 'field_track_gpx'
  AND s.url_or_contact = 'first-party GPX export: ' || :'file_name'
ORDER BY t.id;

SELECT count(*) AS publish_trail_count
FROM publish.features WHERE layer = 'trail_centerlines';
