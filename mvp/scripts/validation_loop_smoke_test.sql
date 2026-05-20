\set ON_ERROR_STOP on

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
    'MVP smoke board review',
    'board_review',
    'local validation-loop smoke test',
    DATE '2026-05-20',
    'generated internal smoke-test data; publishable as demo only',
    'publish',
    'medium',
    'Created by mvp/scripts/validation_loop_smoke_test.sql to prove observation review and promotion wiring.'
  WHERE NOT EXISTS (
    SELECT 1
    FROM source_register.sources
    WHERE name = 'MVP smoke board review'
  )
  RETURNING id
),
smoke_source AS (
  SELECT id FROM inserted_source
  UNION ALL
  SELECT id
  FROM source_register.sources
  WHERE name = 'MVP smoke board review'
  ORDER BY id
  LIMIT 1
),
demo_source AS (
  SELECT id
  FROM source_register.sources
  WHERE name = 'Demo publish sample'
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
  'trail_centerlines',
  t.id,
  d.id,
  'demo publish sample seed',
  t.confidence,
  DATE '2026-05-20',
  t.status,
  'Backfilled provenance link for the original MVP demo trail.'
FROM core.trail_centerlines t
CROSS JOIN demo_source d
WHERE t.name = 'Demo Ridge Trail'
  AND NOT EXISTS (
    SELECT 1
    FROM source_register.feature_sources fs
    WHERE fs.feature_schema = 'core'
      AND fs.feature_table = 'trail_centerlines'
      AND fs.feature_id = t.id
      AND fs.source_id = d.id
      AND fs.claim = 'demo publish sample seed'
  )
UNION ALL
SELECT
  'core',
  'park_boundaries',
  b.id,
  d.id,
  'demo publish sample seed',
  b.confidence,
  DATE '2026-05-20',
  b.status,
  'Backfilled provenance link for the original MVP demo boundary.'
FROM core.park_boundaries b
CROSS JOIN demo_source d
WHERE b.name = 'Demo Park Boundary'
  AND NOT EXISTS (
    SELECT 1
    FROM source_register.feature_sources fs
    WHERE fs.feature_schema = 'core'
      AND fs.feature_table = 'park_boundaries'
      AND fs.feature_id = b.id
      AND fs.source_id = d.id
      AND fs.claim = 'demo publish sample seed'
  )
UNION ALL
SELECT
  'core',
  'trailheads',
  h.id,
  d.id,
  'demo publish sample seed',
  h.confidence,
  DATE '2026-05-20',
  h.status,
  'Backfilled provenance link for the original MVP demo trailhead.'
FROM core.trailheads h
CROSS JOIN demo_source d
WHERE h.name = 'Demo Trailhead'
  AND NOT EXISTS (
    SELECT 1
    FROM source_register.feature_sources fs
    WHERE fs.feature_schema = 'core'
      AND fs.feature_table = 'trailheads'
      AND fs.feature_id = h.id
      AND fs.source_id = d.id
      AND fs.claim = 'demo publish sample seed'
  );

WITH smoke_source AS (
  SELECT id
  FROM source_register.sources
  WHERE name = 'MVP smoke board review'
  ORDER BY id
  LIMIT 1
),
inserted_observation AS (
  INSERT INTO core.observations (
    observation_type,
    source_id,
    status,
    confidence,
    review_status,
    measured_at,
    notes,
    geom,
    metadata
  )
  SELECT
    'trail_correction',
    s.id,
    'reviewed',
    'medium',
    'verified',
    TIMESTAMPTZ '2026-05-20 15:45:00-05',
    'Smoke test observation: board review marked a connector candidate near the demo ridge trail.',
    ST_SetSRID(ST_Point(-85.8525, 35.0355), 4326),
    jsonb_build_object(
      'capture_method', 'board_mark_transcription',
      'review_result', 'verified_for_smoke_test',
      'promotion_target', 'core.trail_centerlines',
      'publish_scope', 'demo_only'
    )
  FROM smoke_source s
  WHERE NOT EXISTS (
    SELECT 1
    FROM core.observations
    WHERE notes = 'Smoke test observation: board review marked a connector candidate near the demo ridge trail.'
  )
  RETURNING id
),
observation_row AS (
  SELECT id FROM inserted_observation
  UNION ALL
  SELECT id
  FROM core.observations
  WHERE notes = 'Smoke test observation: board review marked a connector candidate near the demo ridge trail.'
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
  'observations',
  o.id,
  s.id,
  'board mark captured as review evidence',
  'medium',
  DATE '2026-05-20',
  'verified',
  'Observation source link created by validation-loop smoke test.'
FROM observation_row o
CROSS JOIN smoke_source s
WHERE NOT EXISTS (
  SELECT 1
  FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'observations'
    AND fs.feature_id = o.id
    AND fs.source_id = s.id
    AND fs.claim = 'board mark captured as review evidence'
);

WITH smoke_source AS (
  SELECT id
  FROM source_register.sources
  WHERE name = 'MVP smoke board review'
  ORDER BY id
  LIMIT 1
),
observation_row AS (
  SELECT id
  FROM core.observations
  WHERE notes = 'Smoke test observation: board review marked a connector candidate near the demo ridge trail.'
  ORDER BY id
  LIMIT 1
),
updated_trail AS (
  UPDATE core.trail_centerlines t
  SET
    difficulty = 'green',
    status = 'verified',
    confidence = 'medium',
    permission = 'publish',
    publish_status = 'publish',
    source_id = s.id,
    geom = ST_SetSRID(ST_MakeLine(ARRAY[
      ST_Point(-85.8550, 35.0330),
      ST_Point(-85.8525, 35.0355),
      ST_Point(-85.8500, 35.0370)
    ]), 4326),
    notes = format(
      'Promoted from smoke validation observation id %s on 2026-05-20. Demo geometry only; replace with real AOP trail data before production use.',
      o.id
    ),
    last_verified = TIMESTAMPTZ '2026-05-20 15:50:00-05',
    updated_at = now()
  FROM smoke_source s, observation_row o
  WHERE t.name = 'MVP Smoke: Board-Validated Connector'
  RETURNING t.id
),
inserted_trail AS (
  INSERT INTO core.trail_centerlines (
    name,
    difficulty,
    status,
    confidence,
    permission,
    publish_status,
    source_id,
    geom,
    notes,
    last_verified
  )
  SELECT
    'MVP Smoke: Board-Validated Connector',
    'green',
    'verified',
    'medium',
    'publish',
    'publish',
    s.id,
    ST_SetSRID(ST_MakeLine(ARRAY[
      ST_Point(-85.8550, 35.0330),
      ST_Point(-85.8525, 35.0355),
      ST_Point(-85.8500, 35.0370)
    ]), 4326),
    format(
      'Promoted from smoke validation observation id %s on 2026-05-20. Demo geometry only; replace with real AOP trail data before production use.',
      o.id
    ),
    TIMESTAMPTZ '2026-05-20 15:50:00-05'
  FROM smoke_source s, observation_row o
  WHERE NOT EXISTS (
    SELECT 1
    FROM core.trail_centerlines
    WHERE name = 'MVP Smoke: Board-Validated Connector'
  )
  RETURNING id
),
trail_row AS (
  SELECT id FROM updated_trail
  UNION ALL
  SELECT id FROM inserted_trail
  UNION ALL
  SELECT id
  FROM core.trail_centerlines
  WHERE name = 'MVP Smoke: Board-Validated Connector'
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
  'trail_centerlines',
  t.id,
  s.id,
  'verified observation promoted into trail centerline',
  'medium',
  DATE '2026-05-20',
  'verified',
  format('Promotion is traceable from core.observations id %s to this demo trail feature.', o.id)
FROM trail_row t
CROSS JOIN smoke_source s
CROSS JOIN observation_row o
WHERE NOT EXISTS (
  SELECT 1
  FROM source_register.feature_sources fs
  WHERE fs.feature_schema = 'core'
    AND fs.feature_table = 'trail_centerlines'
    AND fs.feature_id = t.id
    AND fs.source_id = s.id
    AND fs.claim = 'verified observation promoted into trail centerline'
);

WITH observation_row AS (
  SELECT id
  FROM core.observations
  WHERE notes = 'Smoke test observation: board review marked a connector candidate near the demo ridge trail.'
  ORDER BY id
  LIMIT 1
),
trail_row AS (
  SELECT id
  FROM core.trail_centerlines
  WHERE name = 'MVP Smoke: Board-Validated Connector'
  ORDER BY id
  LIMIT 1
)
UPDATE core.observations o
SET
  metadata = coalesce(o.metadata, '{}'::jsonb) || jsonb_build_object(
    'promoted_feature_schema', 'core',
    'promoted_feature_table', 'trail_centerlines',
    'promoted_feature_id', t.id
  ),
  updated_at = now()
FROM trail_row t, observation_row target
WHERE o.id = target.id;

COMMIT;

SELECT 'validation_loop_smoke_summary' AS result;

SELECT
  'sources' AS table_name,
  count(*) AS row_count
FROM source_register.sources
UNION ALL
SELECT 'feature_sources', count(*) FROM source_register.feature_sources
UNION ALL
SELECT 'observations', count(*) FROM core.observations
UNION ALL
SELECT 'trail_centerlines', count(*) FROM core.trail_centerlines
UNION ALL
SELECT 'publish_trails', count(*) FROM publish.trail_centerlines
ORDER BY table_name;

SELECT
  o.id AS observation_id,
  o.observation_type,
  o.review_status,
  o.confidence,
  o.metadata ->> 'promoted_feature_table' AS promoted_feature_table,
  o.metadata ->> 'promoted_feature_id' AS promoted_feature_id
FROM core.observations o
WHERE o.notes = 'Smoke test observation: board review marked a connector candidate near the demo ridge trail.'
ORDER BY o.id;
