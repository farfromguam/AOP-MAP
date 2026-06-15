# AOP MAP MVP

This repository contains the Adventure Off Road Park map brain and a minimal MVP scaffold for the first PostGIS/QGIS/MapLibre build.

## Stack at a glance

The repo has two tiers. Only the second one ships.

**Authoring tier — local only, never deployed.**

- PostGIS 15 / PostGIS 3.4 in a Docker container (`postgis/postgis:15-3.4`, declared in `mvp/docker-compose.yml`). Host port defaults to `55432` to avoid colliding with a local Postgres on `5432`.
- Schemas: `raw` (captures from ArcGIS / GPX / etc.), `source_register` (provenance), `core` (working features), `publish` (read-only views filtered to `permission='publish' AND publish_status='publish'`). Definitions in `mvp/init_db.sql`.
- QGIS as the editor against `localhost:55432`.
- Shell + Python ingest/build scripts in `mvp/scripts/` (Tennessee Comptroller parcel pulls, GPX parsers, USGS NHD / roads, FEMA structures, Marion cemeteries, activity-hotspot builder, etc.).
- Ad-hoc raster/contour work runs through a pinned GDAL container (`ghcr.io/osgeo/gdal:alpine-small-latest`); lidar CHMs through `pdal/pdal:latest`. macOS staging path is `/private/tmp` because Docker can't read `~/Documents`. See `brain/spinup/mvp_runbook.md`.
- Verifier scripts (`mvp/scripts/playwright_verify_*.py`) drive the static viewer through Playwright on port `8001`.

**Viewer tier — the deployable surface.**

- Single-file MapLibre app: `website/index.html`. Pure HTML/CSS/JS, no build step, no framework.
- Map runtime vendored in `website/vendor/`: `maplibre-gl.{js,css}`, `terra-draw.umd.js`, `terra-draw-maplibre-gl-adapter.umd.js`. No CDN dependency for the runtime itself.
- Reads its data from static files under `website/data/` (`publish.geojson`, plus per-layer GeoJSON for water, roads, buildings, cemeteries, contours, lidar tiles, activity hotspots, OSM extracts, event schedule JSON, and the SFWDA paper-map raster).
- At runtime it does fetch a few public tile services for backdrop layers: AWS Terrarium terrain tiles, TNMap satellite imagery, and USDA NAIP. Outbound HTTPS is required.

**Pipeline glue.** `mvp/scripts/export_publish_geojson.sh` reads the `publish.*` views from PostGIS and writes `website/data/publish.geojson`. The DB itself never goes to production; only the regenerated GeoJSON files do.

## Deployment

The deliverable is the `website/` directory as a static site. There is nothing server-side to deploy.

**What to upload.** The entire `website/` tree:

- `website/index.html`
- `website/vendor/` (MapLibre + Terra Draw)
- `website/data/` (current `publish.geojson` and per-layer GeoJSON / JSON / WebP assets)
- `website/assets/` (branding)

Regenerate `website/data/publish.geojson` locally before each deploy:

```bash
cd mvp
./scripts/export_publish_geojson.sh
```

**Hosting options.** Any static host works — S3 + CloudFront, Cloudflare Pages, Netlify, Vercel, GitHub Pages, or a plain nginx box. No environment variables, no runtime config file. The site must be served over HTTP(S); opening `index.html` over `file://` breaks the GeoJSON `fetch()` calls.

**MIME types.** Confirm the host serves `.geojson` as `application/geo+json` or `application/json` and `.webp` as `image/webp`. Most managed hosts handle this; bare nginx may need a `mime.types` line.

**Outbound tile services.** The browser fetches map tiles at runtime from:

- `s3.amazonaws.com/elevation-tiles-prod/terrarium/...` — AWS Open Data terrain
- `tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/...` — Tennessee state imagery
- `gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/...` — USDA NAIP

These are public and unauthenticated, but they are third-party services with their own rate limits and terms. A production deploy should confirm acceptable-use terms and decide whether to proxy or cache them. The viewer does not require an API key today.

**No backend.** There is no API, no auth, no database call from the browser. The viewer's "editor" controls (Terra Draw POIs, schedule edits, SFWDA alignment) currently persist to the browser only and are exported via the panel's Export buttons; nothing writes back to the cloud. If/when Sprint 03's `full_loop_crud_upload_audit` lands, deployment will grow a server tier — until then, this is a pure static site.

**Smoke test after deploy.** Load the site, open the layer panel, confirm the AOP parcel boundary draws over satellite imagery, and confirm at least one toggle (e.g. Buildings, Cemeteries) renders features. If GeoJSON 404s, MIME types are the usual cause.

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


# Note on the development:
Thanks for reading the documentation. 

This repo and project is specifically designed as a AI agent first and only coding experiment so any patterns here, I may not recommend you follow.

If you want to see more about the context harness, see the brain. Coding done May & June 2006 with techniques at the time.