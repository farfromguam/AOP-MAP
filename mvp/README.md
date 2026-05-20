# AOP Map MVP - PostGIS Setup

This directory contains a minimal PostGIS-backed MVP scaffold for the AOP map.

## Start the database

From `/Users/christopherfryman/Documents/code/AOP MAP/mvp`:

```bash
docker compose up -d
```

The container will launch a PostGIS database on `localhost:5432` with:
- user: `aop`
- password: `aop`
- database: `aop_map`

The schema is initialized by `init_db.sql`.

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
- Port: `5432`
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

## Next steps

1. Load AOP parcel and boundary data into `core.parcels` and `core.park_boundaries`.
2. Load candidate trail lines into `core.trail_centerlines`.
3. Add source rows for each imported dataset.
4. Use QGIS to style by `confidence`, `permission`, and `status`.
5. Export publishable layers as GeoJSON and preview the static viewer in `../website/`.
