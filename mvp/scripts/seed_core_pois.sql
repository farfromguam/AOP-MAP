-- Bake-first slice seed: load a small, honest set of destination POIs into
-- core.pois so the DB -> publish.pois -> export -> publish.geojson -> viewer
-- pipeline has real input to prove end-to-end.
--
-- These rows are derived (one-time) from existing website/data files:
--   - AOP Pavilion        : aop_editor_seed_pois.geojson  (confirmed pavilion)
--   - Ellis Cemetery       : aop_cemeteries.geojson         (parcel 110 008.04)
--   - Proving Grounds cand.: aop_buildings.geojson          (665 Ellis Cove)
--
-- Idempotent: rows are owned by the named seed source and deleted by that
-- source_id before re-insert, so re-running this script is safe.
--
-- The Proving Grounds candidate is intentionally NOT publishable
-- (permission='unknown', publish_status='candidate'): it must be EXCLUDED by
-- publish.pois, proving the gate works. Card:
-- brain/tasks/04_event_app/star_driven_poi_list.md.

\set ON_ERROR_STOP on

BEGIN;

-- Register the seed as a source so the rows carry provenance.
INSERT INTO source_register.sources
  (name, source_type, url_or_contact, retrieved_on, license_or_permission,
   publish_status, confidence_default, notes)
SELECT
  'AOP bake-first POI seed', 'derived',
  'mvp/scripts/seed_core_pois.sql', '2026-05-29',
  'internal — derived from existing website/data files',
  'publish', 'mixed',
  'One-time seed of destination POIs to prove the DB->bake->serve pipeline.'
WHERE NOT EXISTS (
  SELECT 1 FROM source_register.sources WHERE name = 'AOP bake-first POI seed'
);

-- Clear any prior seed rows so this is a clean re-load.
DELETE FROM core.pois
WHERE source_id = (
  SELECT id FROM source_register.sources WHERE name = 'AOP bake-first POI seed'
);

-- source_key = the stable external identity (the panel export's
-- "<source>:<canonical id>"). The author path upserts ON CONFLICT (source_key),
-- so an editor edit to one of these seeded destinations matches deterministically
-- regardless of the serial id. Card: 06_going_gold/gold_migration.md (slice 1).
INSERT INTO core.pois
  (name, kind, blurb, is_destination, status, confidence, permission,
   publish_status, source_key, source_id, geom, notes, last_verified)
SELECT v.name, v.kind, v.blurb, v.is_destination, v.status, v.confidence,
       v.permission, v.publish_status, v.source_key, s.id,
       ST_SetSRID(ST_MakePoint(v.lng, v.lat), 4326), v.notes, now()
FROM source_register.sources s,
(VALUES
  ('AOP Pavilion', 'pavilion',
   'AOP Pavilion / G-Central. Registration, driver meeting, awards, and the campfire all happen here. Resolved to the 1010 Ellis Cove Road building footprint via the #pavilion tag.',
   true, 'confirmed', 'high', 'publish', 'publish', 'editorPois:aop-pavilion',
   -85.7482512, 35.0907264,
   'Confirmed pavilion; derived from aop_editor_seed_pois.geojson.'),
  ('Ellis Cemetery', 'cemetery',
   'Ellis Cemetery — the AOP inholding. A 0.12-acre family cemetery carved out of the working envelope. Treat as private; stay clear of the parcel.',
   true, 'parcel record', 'high', 'publish', 'publish', 'editorPois:ellis-cemetery',
   -85.7438766, 35.0895203,
   'Derived from aop_cemeteries.geojson marker, parcel 110 008.04.'),
  ('Proving Grounds (candidate)', 'course candidate',
   NULL,
   true, 'candidate', 'low', 'unknown', 'candidate', 'editorPois:proving-grounds-candidate',
   -85.7456022, 35.0872181,
   'Unconfirmed. 665 Ellis Cove building tagged Proving Grounds candidate from a hotspot read; must be excluded by publish.pois until AOP confirms.')
) AS v(name, kind, blurb, is_destination, status, confidence, permission,
       publish_status, source_key, lng, lat, notes)
WHERE s.name = 'AOP bake-first POI seed';

COMMIT;

-- Report what landed and what the publish gate lets through.
SELECT name, publish_status, permission, is_destination FROM core.pois ORDER BY id;
SELECT 'publish.pois ->' AS gate, name FROM publish.pois ORDER BY name;
