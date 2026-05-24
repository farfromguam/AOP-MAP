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

Shared helpers live in `playwright_base.py` next to the verifiers. A new
verifier imports what it needs:

```python
from playwright_base import WEBSITE_URL, set_toggle, layer_visibility, rendered_count
```

`set_toggle` drives `.checked` + a bubbling `change` event so a checkbox
inside a collapsed `.panel-section` still flips correctly (a `.click()`
call would time out on the hidden element). Never inline copies of these
helpers — the Sprint 02 viewer grew enough collapsed panels that two
divergent `set_toggle` forms became a real regression risk.

## Simulated Saturday activity

Generate a deterministic multi-user Saturday-afternoon test set, then extract a
separate synthetic hotspot layer. The simulator uses the observed Saturday trail,
event anchors, existing GPX hotspots, and nearby OSM `highway=track` /
`highway=service` linework from `website/data/osm_aop_9patch.geojson`.

```
python3 mvp/scripts/simulate_saturday_activity.py
python3 mvp/scripts/build_activity_hotspots.py \
  brain/import/synthetic_saturday_activity.gpx \
  --output website/data/aop_synthetic_activity_hotspots.geojson \
  --name aop_synthetic_activity_hotspots \
  --source-type synthetic_activity_gpx \
  --confidence synthetic_multi_user_model \
  --review-status "synthetic Saturday activity model; not field evidence or validated trail/facility data" \
  --min-cell-seconds 90 \
  --rank-by stop_slow \
  --intensity-cap-seconds 7200 \
  --min-stop-slow-seconds 300 \
  --max-moving-fraction 0.7 \
  --label-rank-limit 12 \
  --label-min-seconds 1800
```

The simulator writes:
- `brain/import/synthetic_saturday_activity.gpx`
- `website/data/aop_synthetic_activity_tracks.geojson`
- `website/data/aop_synthetic_activity_report.json`
- `website/data/aop_synthetic_activity_hotspots.geojson`

Viewer verification:

```
python3 mvp/scripts/playwright_verify_synthetic_activity.py
```

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
