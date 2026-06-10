CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS publish;
CREATE SCHEMA IF NOT EXISTS source_register;

SET search_path = source_register, public;

CREATE TABLE IF NOT EXISTS source_register.sources (
  id serial PRIMARY KEY,
  name text NOT NULL,
  source_type text NOT NULL,
  url_or_contact text,
  retrieved_on date,
  license_or_permission text,
  publish_status text,
  confidence_default text,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS source_register.feature_sources (
  id serial PRIMARY KEY,
  feature_schema text NOT NULL,
  feature_table text NOT NULL,
  feature_id integer NOT NULL,
  source_id integer NOT NULL REFERENCES source_register.sources(id),
  claim text,
  confidence text,
  last_checked date,
  review_status text,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

SET search_path = core, public;

-- The ONE converged geo table (going gold, slice 2+; the 2026-06-07 table
-- cleanup folded the eight per-layer core.* tables into it). One row shape for
-- every layer: the CMFS spine columns + a free-form JSONB `attrs` for per-domain
-- extras (a building's facility_role, a trail's difficulty, a parcel's owner +
-- assessment metadata, a field track's segment_index, an observation's
-- review_status). `attrs` has NO key allowlist and NO CHECK -- unknown domain
-- keys are stored, never rejected (C5/no_limiting_code_mvp). `layer` names the
-- source layer ('buildings', 'cemeteries', 'trails', 'poi', 'trail_centerlines',
-- 'park_boundaries', 'trailheads', 'parcels', 'observations', 'field_tracks',
-- ...). geom is mixed (Geometry) because the layers span points, lines, and
-- polygons. source_key + archived_at give a deterministic upsert identity + soft
-- delete. The publish view is the ONLY gate; reference layers (buildings, etc.)
-- bake to their own served file WITHOUT the publish gate.
-- Card: 06_going_gold/gold_migration.md, 07_tables/tables_diagram.md.
CREATE TABLE IF NOT EXISTS core.features (
  id serial PRIMARY KEY,
  layer text,
  name text,
  kind text,
  description text,   -- the human description (CMFS canonical name; renamed from `blurb` 2026-06-08, see 07_tables/description_blurb_convergence.md). Distinct from core.activities.description (sibling table, the reusable activity WHAT).
  is_destination boolean DEFAULT false,
  status text,
  confidence text,
  permission text,
  publish_status text,
  source_key text UNIQUE,
  archived_at timestamptz,
  source_id integer REFERENCES source_register.sources(id),
  geom geometry(Geometry,4326),
  attrs jsonb,
  notes text,
  last_verified timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- The WHEN junction (going gold, sprint 07 slice 1). One row per occurrence/
-- session of an event. place_key is the schedule #location tag, a SOFT reference
-- resolved at bake against core.features.attrs->'event_location'->>'tag' -- plain
-- text, NO FK, NO CHECK: an occurrence pointing at a not-yet-present place is
-- stored and resolved later, never rejected (C5/no_limiting_code_mvp). event_id is
-- the umbrella event (soft). attrs holds inspired_by/route_tags and any other
-- session field with no allowlist. The bake (export_publish_geojson.sh) rebuilds
-- aop_event_schedule.json from this table + the event-place rows in core.features.
-- Card: brain/tasks/07_tables/tables_model.md.
CREATE TABLE IF NOT EXISTS core.events (
  id serial PRIMARY KEY,
  event_id text,
  source_key text UNIQUE,
  sort_order integer,
  title text,
  date_label text,
  start_local text,
  time_label text,
  status text,
  place_key text,
  activity_key text,
  attrs jsonb,
  archived_at timestamptz,
  source_id integer REFERENCES source_register.sources(id),
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- The reusable, place-agnostic WHAT (going gold, sprint 07 slice 2). One row per
-- reusable activity (Night Crawl, hill climb, RC rally...). core.events.activity_key
-- SOFT-references activity_key -- plain text, NO FK, NO CHECK: an occurrence citing
-- a not-yet-defined activity is stored and resolved later, never rejected
-- (C5/no_limiting_code_mvp). NO geometry, NO place column -- the place binds on the
-- OCCURRENCE (core.events), never on the activity (it can move places). Same CMFS
-- shape as core.features MINUS geometry -- one vocabulary. attrs holds the activity's
-- "specific data" (grade, length, gate list) with no allowlist. Card: 07_tables.
CREATE TABLE IF NOT EXISTS core.activities (
  id serial PRIMARY KEY,
  activity_key text UNIQUE,
  name text,
  kind text,
  description text,
  attrs jsonb,
  source_id integer REFERENCES source_register.sources(id),
  archived_at timestamptz,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- The umbrella EVENT metadata (going gold slice 6, G_E, 2026-06-10). One row per
-- umbrella event -- the WHO/WHEN-banner the schedule document wraps its sessions
-- in. It used to be a hardcoded heredoc in export_publish_geojson.sh
-- (audit `event-umbrella-metadata-hardcoded-in-bake`); now the bake reads it from
-- this store of record. `event_id` SOFT-references core.events.event_id (plain
-- text, NO FK, NO CHECK -- C5/no_limiting_code_mvp). CMFS: `label` is the Tier1
-- name, `status` the Tier2 maturity, `schema` the served document schema id; the
-- date-range / source / caveat strings round-trip the served `event{}` block.
-- attrs holds any future umbrella field with no allowlist. Seeded by
-- mvp/scripts/seed_event_meta.py; the bake composes the document wrapper from it.
CREATE TABLE IF NOT EXISTS core.event_meta (
  id serial PRIMARY KEY,
  event_id text UNIQUE,
  schema text,
  label text,
  status text,
  date_range_label text,
  end_date_label text,
  source_context text,
  source_summary text,
  caveat text,
  schedule_updated_at text,
  attrs jsonb,
  source_id integer REFERENCES source_register.sources(id),
  archived_at timestamptz,
  notes text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.gpx_captures (
  id serial PRIMARY KEY,
  source_id integer REFERENCES source_register.sources(id),
  file_name text NOT NULL,
  track_name text,
  creator text,
  recorded_at timestamptz,
  segment_count integer,
  point_count integer,
  raw_xml text NOT NULL,
  captured_at timestamptz DEFAULT now(),
  notes text,
  -- Named so import_gpx_track.sql's ON CONFLICT ON CONSTRAINT resolves on a
  -- fresh volume (the live DB carries this name; the prior unnamed UNIQUE
  -- auto-named differently -- a pre-existing drift caught by fresh-volume repro).
  CONSTRAINT gpx_captures_file_recorded_uniq UNIQUE (file_name, recorded_at)
);

CREATE TABLE IF NOT EXISTS raw.arcgis_feature_captures (
  id serial PRIMARY KEY,
  source_id integer REFERENCES source_register.sources(id),
  source_url text NOT NULL,
  query_where text NOT NULL,
  fetched_at timestamptz DEFAULT now(),
  feature_json jsonb NOT NULL,
  notes text
);

-- The converged publish view (going gold; the 2026-06-07 cleanup retired the
-- five per-layer publish.* views in favour of this one). Same publish gate as
-- those did, and it MUST select `attrs` explicitly so the JSONB isn't dropped by
-- omission (the limiting-by-omission Mason caught). The bake reads published map
-- layers (poi, trail_centerlines, park_boundaries, trailheads, hazards) from
-- here, filtered by `layer`. Reference layers (buildings/cemeteries/...) carry
-- non-'publish' permission and so are CORRECTLY absent here; they bake to their
-- own served files without this gate. Card: 06_going_gold/gold_migration.md.
CREATE OR REPLACE VIEW publish.features AS
  SELECT id, layer, name, kind, description, is_destination,
         status, confidence, permission, publish_status, attrs, geom
  FROM core.features
  WHERE permission = 'publish'
    AND publish_status = 'publish'
    AND archived_at IS NULL;

-- Indexes -----------------------------------------------------------------

CREATE INDEX IF NOT EXISTS features_geom_gix           ON core.features          USING GIST (geom);
CREATE INDEX IF NOT EXISTS features_layer_idx          ON core.features          (layer);
CREATE INDEX IF NOT EXISTS events_sort_idx             ON core.events            (sort_order);
CREATE INDEX IF NOT EXISTS events_place_key_idx        ON core.events            (place_key);
CREATE INDEX IF NOT EXISTS events_activity_key_idx     ON core.events            (activity_key);

-- Provenance links are always looked up by the feature they describe.
CREATE INDEX IF NOT EXISTS feature_sources_feature_idx
  ON source_register.feature_sources (feature_schema, feature_table, feature_id);

-- updated_at maintenance ---------------------------------------------------
-- One trigger keeps updated_at honest so importers do not have to remember.

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
  t text;
BEGIN
  FOREACH t IN ARRAY ARRAY[
    'source_register.sources',
    'source_register.feature_sources',
    'core.features',
    'core.events',
    'core.activities',
    'core.event_meta'
  ]
  LOOP
    EXECUTE format('DROP TRIGGER IF EXISTS trg_set_updated_at ON %s', t);
    EXECUTE format(
      'CREATE TRIGGER trg_set_updated_at BEFORE UPDATE ON %s '
      'FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()', t);
  END LOOP;
END $$;
