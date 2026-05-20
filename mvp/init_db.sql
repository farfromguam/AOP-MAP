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
  geom geometry(Polygon,4326),
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
  source_id integer REFERENCES source_register.sources(id),
  geom geometry(Polygon,4326),
  metadata jsonb,
  notes text,
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
  geom geometry(Point,4326),
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

CREATE VIEW IF NOT EXISTS publish.trail_centerlines AS
  SELECT id, name, difficulty, status, confidence, permission, geom
  FROM core.trail_centerlines
  WHERE permission = 'publish'
    AND publish_status = 'publish';

CREATE VIEW IF NOT EXISTS publish.park_boundaries AS
  SELECT id, name, status, confidence, permission, geom
  FROM core.park_boundaries
  WHERE permission = 'publish'
    AND publish_status = 'publish';

CREATE VIEW IF NOT EXISTS publish.trailheads AS
  SELECT id, name, status, confidence, permission, geom
  FROM core.trailheads
  WHERE permission = 'publish'
    AND publish_status = 'publish';

CREATE VIEW IF NOT EXISTS publish.hazards AS
  SELECT id, hazard_type, severity, status, confidence, permission, geom
  FROM core.hazards
  WHERE permission = 'publish'
    AND publish_status = 'publish';
