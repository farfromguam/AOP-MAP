# AOP Map MVP - PostGIS Setup

This directory contains a minimal PostGIS-backed MVP scaffold for the AOP map.

## Start the database

From `/Users/christopherfryman/Documents/code/AOP MAP/mvp`:

```bash
docker compose up -d
```

The container will launch a PostGIS database on `localhost:55432` with:
- user: `aop`
- password: `aop`
- database: `aop_map`

The schema is initialized by `init_db.sql`.

The database still listens on `5432` inside the container. The Compose host
port defaults to `55432` so a local Postgres service can continue using
`localhost:5432`. Override it with `AOP_DB_HOST_PORT` if needed.

For the full continuation and troubleshooting path, see
`../brain/spinup/mvp_runbook.md`.

> Note: On macOS, the container entrypoint may fail to read a bind-mounted `init_db.sql` file with "Operation not permitted." If that happens, verify Docker Desktop is running, then manually apply the SQL with:
>
> ```bash
> cd mvp
> cat init_db.sql | docker exec -i mvp-db-1 psql -U aop -d aop_map
> ```
>
> If the database volume contains a partial initialization, stop the container and remove or back up `mvp/db-data` before restarting.

## Connect QGIS

Use the following connection settings:
- Host: `localhost`
- Port: `55432`
- Database: `aop_map`
- Username: `aop`
- Password: `aop`

Once connected, inspect schemas:
- `source_register`
- `core`
- `publish`

## What is in the database

`source_register` contains:
- `sources`
- `feature_sources`

`core` contains working feature tables:
- `park_boundaries`
- `parcels`
- `trail_centerlines`
- `observations`
- `hazards`
- `trailheads`
- `print_annotations`

`publish` contains views for safe exported layers.

## Validation-loop smoke test

After the database is running, use this to prove the MVP observation review and promotion path:

```bash
./scripts/run_validation_loop_smoke.sh
./scripts/export_publish_geojson.sh
```

The smoke test inserts demo-only rows named `MVP smoke...`, links them through `source_register.feature_sources`, promotes one reviewed observation into a publishable trail, and refreshes `../website/data/publish.geojson`.

## Import the first real AOP boundary slice

```bash
./scripts/import_aop_parcel_boundary.sh
./scripts/export_publish_geojson.sh
```

This imports the Tennessee Comptroller Marion County parcel features for `ELLIS COVE RD 1040` and the connected `093 030.01` / `058 093 03001 000` parcel lead, stores the raw captures, upserts `core.parcels`, creates a publishable candidate multipolygon boundary in `core.park_boundaries`, and archives demo publish rows. The boundary is a parcel-reference working envelope, not a legal survey or complete confirmed park boundary.

## Import field GPX evidence

```bash
./scripts/import_gpx_track.sh ../brain/import/Saturday_Afternoon_Activity.gpx
```

This stores the GPX raw XML and parsed track segments as `core.field_tracks`. It remains unpromoted until review.

## Next steps

1. Verify the imported `ELLIS COVE RD 1040` and `093 030.01` / `058 093 03001 000` parcels in QGIS and identify any additional related parcels needed to reconcile the official 600+ acre claim.
2. Load candidate trail lines into `core.trail_centerlines`.
3. Add source rows for each imported dataset.
4. Use QGIS to style by `confidence`, `permission`, and `status`.
5. Export publishable layers as GeoJSON and preview the static viewer in `../website/`.
