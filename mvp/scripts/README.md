# import_geojson helper

This folder contains small helpers for moving data through the MVP PostGIS database.

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

## import_geojson helper

Requirements:
- `ogr2ogr` (GDAL) installed on the host.
- Database accessible at `localhost:5432` with user `aop` / password `aop` (adjust in script if needed).

Example:

```
cd mvp/scripts
./import_geojson.sh ../../website/data/publish.geojson publish.publish_features
```

The script uses `-append` so it will add rows if the table exists. Adjust as needed for safe imports.
