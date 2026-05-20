\set ON_ERROR_STOP on

-- Promote field tracks for a given GPX file_name into core.trail_centerlines.
-- Each segment becomes one trail centerline with publish/publish gates,
-- linked back to the same source for provenance.
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
    ft.track_name,
    ft.segment_index,
    ft.geom,
    ft.source_id,
    ft.confidence,
    format('%s (segment %s)', ft.track_name, ft.segment_index) AS trail_name
  FROM core.field_tracks ft
  JOIN source_row sr ON sr.id = ft.source_id
),
upserted AS (
  INSERT INTO core.trail_centerlines (
    name, difficulty, status, confidence,
    permission, publish_status, source_id, geom, notes, last_verified
  )
  SELECT
    c.trail_name,
    'unrated',
    'observed',
    c.confidence,
    'publish',
    'publish',
    c.source_id,
    c.geom,
    format(
      'Promoted from core.field_tracks id %s (GPX %s). First-party GaiaGPS recording; difficulty unrated until field review.',
      c.field_track_id, :'file_name'
    ),
    now()
  FROM candidates c
  WHERE NOT EXISTS (
    SELECT 1 FROM core.trail_centerlines t
    WHERE t.name = c.trail_name AND t.source_id = c.source_id
  )
  RETURNING id, name, source_id
),
promoted_tracks AS (
  -- Mark the source field_tracks as promoted (status update only).
  UPDATE core.field_tracks ft
  SET
    status = 'promoted',
    publish_status = 'reference_publish',
    updated_at = now()
  FROM candidates c
  WHERE ft.id = c.field_track_id
  RETURNING ft.id
)
INSERT INTO source_register.feature_sources (
  feature_schema, feature_table, feature_id, source_id,
  claim, confidence, last_checked, review_status, notes
)
SELECT
  'core', 'trail_centerlines', u.id, u.source_id,
  'first-party GPX ride promoted into trail centerline',
  'medium', CURRENT_DATE, 'verified',
  'Promotion path: raw.gpx_captures -> core.field_tracks -> core.trail_centerlines.'
FROM upserted u
WHERE NOT EXISTS (
  SELECT 1 FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'trail_centerlines'
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
FROM core.trail_centerlines t
JOIN source_register.sources s ON s.id = t.source_id
WHERE s.source_type = 'field_track_gpx'
  AND s.url_or_contact = 'first-party GPX export: ' || :'file_name'
ORDER BY t.id;

SELECT count(*) AS publish_trail_count FROM publish.trail_centerlines;
