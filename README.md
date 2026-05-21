# AOP MAP MVP

This repository contains the Adventure Off Road Park map brain and a minimal MVP scaffold for the first PostGIS/QGIS/MapLibre build.

## Current progress

- [X] Scaffold PostGIS container and init SQL
- [X] Add static MapLibre viewer skeleton
- [X] Add root README and website README
- [X] Confirm Docker container startup
- [X] Prove observation capture, review, promotion, provenance, and export with a smoke test
- [X] Import the first real source-backed AOP boundary slice from the Tennessee Comptroller Marion County parcel layer
- [X] Wire reference layers into the viewer: TNMap satellite, lidar hillshade and 3D terrain, lidar 5 ft contours, the 9-patch AOI and lidar tile index, USGS roads and water, OSM community layers, and the SFWDA 2015 paper map
- [X] Add an in-viewer POI/footprint editor and a feature search box
- [X] Add a searchable Marion County cemeteries layer and confirm the Ellis Cemetery inholding
- [ ] Connect QGIS and verify schema
- [ ] Reconcile the official 600+ acre AOP claim against parcel data and any related parcels

## Spinup instructions

### 1. Start Docker Desktop

Make sure Docker is installed and the Docker daemon is running.
On macOS this typically means opening Docker Desktop and waiting for it to become ready.

### 2. Start the PostGIS database

From the repository root:

```bash
cd mvp
docker compose up -d
```

This will launch a PostGIS container with the following settings:
- Host: `localhost`
- Port: `55432`
- Database: `aop_map`
- Username: `aop`
- Password: `aop`

The container still listens on `5432` internally. The host port defaults to
`55432` so local Postgres installations can keep using `localhost:5432`.
Override it with `AOP_DB_HOST_PORT` if needed.

### 3. Verify the container

Run:

```bash
docker compose ps
```

If the container is running, you should see the `db` service listed.

From the repository root, `./cwc` also runs a non-mutating continuation check
against Docker, Postgres, and the current publish GeoJSON.

If QGIS or `psql` appears to connect to the wrong database, use
`brain/spinup/mvp_runbook.md` before changing Docker volumes.

### 4. Connect QGIS

In QGIS, create a new PostGIS connection using:
- Host: `localhost`
- Port: `55432`
- Database: `aop_map`
- Username: `aop`
- Password: `aop`

Then inspect these schemas:
- `source_register`
- `core`
- `publish`

### 5. Preview the viewer

Use a simple local web server from the repository root:

```bash
cd website
python3 -m http.server 8000
```

Then browse to `http://localhost:8000`.

The viewer fetches `website/data/publish.geojson`, so serving over HTTP is preferred over opening `index.html` directly.

### 6. Refresh the current AOP boundary slice

From the repository root:

```bash
cd mvp
./scripts/import_aop_parcel_boundary.sh
./scripts/export_publish_geojson.sh
```

This refreshes the parcel-derived candidate boundary for `ELLIS COVE RD 1040` and writes the publishable viewer data to `website/data/publish.geojson`.

## Troubleshooting

- If `docker compose up -d` fails with `Cannot connect to the Docker daemon`, the Docker daemon is not running.
- On macOS, open Docker Desktop and wait until it indicates it is ready.
- If the compose service fails to start, run:

```bash
cd mvp
docker compose logs db
```

- If the database port is already in use, either stop the conflicting service or edit `mvp/docker-compose.yml`.

## What is included

- `mvp/docker-compose.yml` — PostGIS container definition
- `mvp/init_db.sql` — initial database schema for sources, park boundaries, parcels, trails, observations, hazards, trailheads, and publish views
- `mvp/scripts/import_aop_parcel_boundary.sh` — imports the current source-backed AOP parcel boundary slice
- `mvp/scripts/run_validation_loop_smoke.sh` — proves observation-to-promotion plumbing with demo rows
- `mvp/scripts/export_publish_geojson.sh` — exports publish views to the static viewer
- `website/index.html` — static MapLibre viewer
- `website/data/publish.geojson` — current publish layer export

This is the initial scaffold set. The MVP has grown well past it; see
`mvp/README.md`, `mvp/scripts/README.md`, and `website/README.md` for the
current files, scripts, and viewer layers.
