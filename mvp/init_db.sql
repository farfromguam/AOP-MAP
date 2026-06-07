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

CREATE TABLE IF NOT EXISTS core.park_boundaries (
  id serial PRIMARY KEY,
  name text,
  status text,
  confidence text,
  permission text,
  publish_status text,
  source_id integer REFERENCES source_register.sources(id),
  geom geometry(MultiPolygon,4326),
  notes text,
  last_verified timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.parcels (
  id serial PRIMARY KEY,
  parcel_id text,
  owner text,
  land_area numeric,
  status text,
  confidence text,
  permission text,
  publish_status text,
  source_id integer REFERENCES source_register.sources(id),
  geom geometry(Polygon,4326),
  metadata jsonb,
  notes text,
  last_verified timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.trail_centerlines (
  id serial PRIMARY KEY,
  name text,
  difficulty text,
  status text,
  confidence text,
  permission text,
  publish_status text,
  source_id integer REFERENCES source_register.sources(id),
  geom geometry(LineString,4326),
  notes text,
  last_verified timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.observations (
  id serial PRIMARY KEY,
  observation_type text,
  source_id integer REFERENCES source_register.sources(id),
  status text,
  confidence text,
  review_status text,
  measured_at timestamptz,
  notes text,
  geom geometry(Geometry,4326),
  metadata jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.hazards (
  id serial PRIMARY KEY,
  hazard_type text,
  severity text,
  status text,
  confidence text,
  permission text,
  publish_status text,
  source_id integer REFERENCES source_register.sources(id),
  notes text,
  geom geometry(Point,4326),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.trailheads (
  id serial PRIMARY KEY,
  name text,
  status text,
  confidence text,
  permission text,
  publish_status text,
  source_id integer REFERENCES source_register.sources(id),
  notes text,
  geom geometry(Point,4326),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.print_annotations (
  id serial PRIMARY KEY,
  annotation_type text,
  status text,
  source_id integer REFERENCES source_register.sources(id),
  notes text,
  geom geometry(Geometry,4326),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS core.field_tracks (
  id serial PRIMARY KEY,
  track_name text,
  segment_index integer,
  point_count integer,
  recorded_start timestamptz,
  recorded_end timestamptz,
  status text,
  confidence text,
  permission text,
  publish_status text,
  source_id integer REFERENCES source_register.sources(id),
  geom geometry(LineString,4326),
  metadata jsonb,
  notes text,
  last_verified timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Destination POIs: the ★ "visitor list" set as first-class rows.
-- A POI is any feature a visitor would browse to as a goal (pavilion,
-- cemetery, trailhead, course feature). `is_destination` is the ★ curation
-- axis; `blurb` is the visitor-facing copy that used to live in
-- website/data/aop_poi_index.json. Card:
-- brain/tasks/04_event_app/star_driven_poi_list.md.
CREATE TABLE IF NOT EXISTS core.pois (
  id serial PRIMARY KEY,
  name text,
  kind text,
  blurb text,
  is_destination boolean DEFAULT true,
  status text,
  confidence text,
  permission text,
  publish_status text,
  -- The stable external identity = the panel export's "<source>:<canonical id>"
  -- string. The author path (apply_panel_overrides_to_core.py) upserts
  -- ON CONFLICT (source_key), so matching is deterministic and idempotent
  -- regardless of the serial id. Card: 06_going_gold/gold_migration.md (slice 1).
  source_key text UNIQUE,
  -- Soft-delete. A panel delete[] ARCHIVES (sets archived_at); it never
  -- hard-deletes. publish.pois excludes archived rows.
  archived_at timestamptz,
  source_id integer REFERENCES source_register.sources(id),
  geom geometry(Point,4326),
  notes text,
  last_verified timestamptz,
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
  UNIQUE (file_name, recorded_at)
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

CREATE OR REPLACE VIEW publish.trail_centerlines AS
  SELECT id, name, difficulty, status, confidence, permission, geom
  FROM core.trail_centerlines
  WHERE permission = 'publish'
    AND publish_status = 'publish';

CREATE OR REPLACE VIEW publish.park_boundaries AS
  SELECT id, name, status, confidence, permission, geom
  FROM core.park_boundaries
  WHERE permission = 'publish'
    AND publish_status = 'publish';

CREATE OR REPLACE VIEW publish.parcels AS
  SELECT id, parcel_id, status, confidence, permission, land_area, geom
  FROM core.parcels
  WHERE permission = 'publish'
    AND publish_status = 'publish';

CREATE OR REPLACE VIEW publish.trailheads AS
  SELECT id, name, status, confidence, permission, geom
  FROM core.trailheads
  WHERE permission = 'publish'
    AND publish_status = 'publish';

CREATE OR REPLACE VIEW publish.hazards AS
  SELECT id, hazard_type, severity, status, confidence, permission, geom
  FROM core.hazards
  WHERE permission = 'publish'
    AND publish_status = 'publish';

-- The ★ POI list = destinations cleared for publish. The card states the gate
-- as `publish_status='publish' AND is_destination`; permission is added here
-- to match the sibling views and the northstar publish rule ("unknown
-- permission does not publish"). The baked publish.geojson is the only POI
-- source the static viewer should ultimately read.
CREATE OR REPLACE VIEW publish.pois AS
  SELECT id, name, kind, blurb, status, confidence, permission, geom
  FROM core.pois
  WHERE is_destination = true
    AND permission = 'publish'
    AND publish_status = 'publish'
    AND archived_at IS NULL;

-- Indexes -----------------------------------------------------------------

CREATE INDEX IF NOT EXISTS park_boundaries_geom_gix   ON core.park_boundaries   USING GIST (geom);
CREATE INDEX IF NOT EXISTS parcels_geom_gix           ON core.parcels           USING GIST (geom);
CREATE INDEX IF NOT EXISTS trail_centerlines_geom_gix ON core.trail_centerlines USING GIST (geom);
CREATE INDEX IF NOT EXISTS observations_geom_gix      ON core.observations      USING GIST (geom);
CREATE INDEX IF NOT EXISTS hazards_geom_gix           ON core.hazards           USING GIST (geom);
CREATE INDEX IF NOT EXISTS trailheads_geom_gix        ON core.trailheads        USING GIST (geom);
CREATE INDEX IF NOT EXISTS pois_geom_gix               ON core.pois              USING GIST (geom);
CREATE INDEX IF NOT EXISTS print_annotations_geom_gix ON core.print_annotations USING GIST (geom);
CREATE INDEX IF NOT EXISTS field_tracks_geom_gix      ON core.field_tracks      USING GIST (geom);

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
    'core.park_boundaries',
    'core.parcels',
    'core.trail_centerlines',
    'core.observations',
    'core.hazards',
    'core.trailheads',
    'core.pois',
    'core.print_annotations',
    'core.field_tracks'
  ]
  LOOP
    EXECUTE format('DROP TRIGGER IF EXISTS trg_set_updated_at ON %s', t);
    EXECUTE format(
      'CREATE TRIGGER trg_set_updated_at BEFORE UPDATE ON %s '
      'FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()', t);
  END LOOP;
END $$;
