# import_geojson helper

This folder contains small helpers for moving data through the MVP PostGIS database.

## Canonical psql invocation

Every shell importer that talks to the database does it the same way:

```
docker compose exec -T db psql -U aop -d aop_map < script.sql
```

The SQL files themselves carry `\set ON_ERROR_STOP on`, so the wrapper does
not need the older `-v ON_ERROR_STOP=1` flag. Match this form in new importers
so the invocation does not drift again.

## Validation-loop smoke test

Run one repeatable demo pass through the observation review and promotion path:

```
cd mvp
./scripts/run_validation_loop_smoke.sh
./scripts/export_publish_geojson.sh
```

The smoke test:
- inserts a board-review source if it does not exist
- captures one reviewed observation
- promotes that reviewed observation into a publishable demo trail
- records `source_register.feature_sources` links for the observation, promoted trail, and original demo features

The generated rows are intentionally named `MVP smoke...` so they can be separated from real AOP data later.

## AOP parcel boundary import

Run the first source-backed AOP map slice:

```
cd mvp
./scripts/import_aop_parcel_boundary.sh
./scripts/export_publish_geojson.sh
```

The importer queries the Tennessee Comptroller `Marion_Parcels` FeatureServer layer for `ELLIS COVE RD 1040` and the connected `093 030.01` / `058 093 03001 000` parcel lead, stores the captured GeoJSON features in `raw.arcgis_feature_captures`, upserts the parcels into `core.parcels`, publishes a candidate multipolygon park boundary in `core.park_boundaries`, links the features to `source_register.sources`, and moves demo/smoke publish rows to `demo_hold`.

The imported boundary is a parcel-reference working envelope, not a legal survey or a complete confirmed park boundary.

## GPX observation import

Import a field track as observation evidence:

```
cd mvp
./scripts/import_gpx_track.sh ../brain/import/Saturday_Afternoon_Activity.gpx
```

The importer parses the GPX track, stores the raw XML in `raw.gpx_captures`, inserts segment rows into `core.field_tracks`, and links them to `source_register.feature_sources`. It does not promote the track into `core.trail_centerlines`; review should happen first.

## Activity hotspot export

Build the static viewer hotspot layer from timestamped GPX:

```
python3 mvp/scripts/build_activity_hotspots.py
```

The builder writes `website/data/aop_activity_hotspots.geojson`, a mixed
FeatureCollection with Polygon hotspot cells plus centroid Points for the
MapLibre heatmap/labels. It is a derived raw-evidence layer; it does not promote
tracks into trails.

Verification:

```
cd website
python3 -m http.server 8001
```

Then, from the repo root:

```
python3 mvp/scripts/playwright_verify_activity_hotspots.py
```

Playwright verifier scripts default to `http://localhost:8001/`. If that port is
busy, start the viewer on another open port and pass `WEBSITE_URL=...`.

## Event schedule sidebar verification

The viewer schedule consumes `website/data/aop_event_schedule.json` directly.
Session rows reference location tags such as `#pavilion` and `#registration`;
the viewer resolves those tags into map points/routes at load time.

Serve the viewer, then run:

```
python3 mvp/scripts/playwright_verify_event_schedule.py
```

## import_geojson helper

The ad-hoc ingest path for one-off GeoJSON files that do not yet have a
dedicated importer. Use a schema-specific importer when one exists; this
wrapper does not set source provenance.

Requirements:
- `ogr2ogr` (GDAL) installed on the host.
- Database accessible at `localhost:55432` with user `aop` / password `aop`.
  Override `PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`, or `PGPASSWORD` if needed.

Example (drop a generic geometry set into `core.observations` for review):

```
cd mvp/scripts
./import_geojson.sh ../../website/data/aop_buildings.geojson core.observations
```

The script uses `-append` so it adds rows if the table exists. ogr2ogr maps
GeoJSON properties to matching column names; unmapped properties are dropped.
After import the script prints a SQL hint for back-filling `source_id`.

## 9-patch reference imports

These scripts write static viewer reference layers under `website/data/`:

```
python3 mvp/scripts/import_fema_buildings.py
```

`import_fema_buildings.py` pulls FEMA USA Structures / ORNL building footprints
for the AOP 9-patch and writes `website/data/aop_buildings.geojson`.
