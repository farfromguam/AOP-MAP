# AOP Map MVP

This repository currently contains project brain and research notes for the Adventure Off Road Park map.
This MVP scaffold is the first practical step toward the build card:
- a PostGIS-backed data spine
- a schema for source-aware trail and boundary layers
- a static read-only map viewer skeleton

## MVP scope

### Phase 1: Data spine
- PostGIS database with `raw`, `core`, and `publish` schemas
- source register tables and feature-source linkage
- core feature tables for park boundaries, parcels, trail centerlines, observations, hazards, trailheads, and print annotations
- publication views for safe web export

### Phase 2: Base map assembly
- connect QGIS to the database
- add parcel data, imagery, DEM, and derived terrain layers
- create candidate trail and boundary layers with confidence/permission fields
- keep source provenance relational and visible

### Phase 3: Static website V1
- read-only MapLibre viewer for publishable trails and boundaries
- layer toggles for the publish layer set
- feature popups with name, difficulty, source, confidence, and status

### Phase 4: Validation loop
- use print board / wall map as the first observation workflow
- transcribe review observations into the database
- promote reviewed items into `publish`

## Immediate next work

1. [X] Launch the PostGIS container in `mvp/`
2. [X] Confirm `mvp/init_db.sql` created the database schema
3. [ ] Connect QGIS to `localhost:55432` and inspect source/feature tables
4. [X] Load a placeholder `publish.geojson` into `website/`
5. [X] Preview `website/index.html`
6. [X] Run a demo validation-loop smoke test from observation capture to promoted publish export
7. [X] Replace the demo publish boundary with a source-backed AOP parcel-derived candidate boundary
8. [ ] Reconcile the 600+ acre official AOP claim against related parcels or current holdings
9. [ ] Replace demo/smoke trail and trailhead placeholders with actual AOP trail/observation data and verify the live viewer shows real map data
10. [ ] Swap the AWS terrarium DEM in `website/index.html` for AOP-specific tiles derived from the USGS 3DEP 1m DEM. Steps: `brew install gdal` and `pip install rio-rgbify`; download `USGS_one_meter_x61y389_TN_27County_blk4_2015.tif` (~500MB) into `mvp/data/dem/` per `brain/output/aop_9_patch_data_acquisition_manifest.md`; clip to the 9-patch bbox `-85.782935283, 35.067164188, -85.717154097, 35.117928496`; reproject to EPSG:3857; encode with `rio rgbify -b -10000 -i 0.1`; tile with `gdal2tiles.py -z 10-16 -r bilinear --xyz` into `website/data/terrain/`; add an `aop-1m-dem` raster-dem source (`encoding: mapbox`) and rebind the `lidar-hillshade` layer + `setTerrain()` call to it; keep AWS terrarium as the fallback outside the AOI; extend `mvp/scripts/playwright_verify_terrain.py` to assert the new source loads at high zoom.
11. [ ] Work the code-health remediation pass: `code_health_pass.md`. Schema constraints, viewer de-duplication, and repo housekeeping from a deep code review.
12. [X] Generate lidar-grade 5 ft contour lines for the 9-patch from the USGS 3DEP 1m DEM and wire them into the viewer. See `lidar_contour_pipeline.md`.
13. [X] Add a web-viewer map editor (Terra Draw): draw/label/persist/export point POIs and polygon footprints (pavilions, buildings, etc.) in `website/index.html`. PostGIS write-back is the remaining follow-up. See `poi_editor.md`.
14. [X] Add a searchable cemeteries layer. Confirmed the hole in the AOP boundary polygon is the Ellis Cemetery inholding (parcel `110 008.04`). See `cemeteries_layer.md` and `brain/research/aop_ellis_cemetery.md`.
15. [X] Vectorize the satellite imagery into a forest land-cover layer (NAIP 2021 4-band -> texture classification -> forest polygons) and restyle the viewer into the Muted Earth palette. See `landcover_layer.md`.
16. [X] Review/import 9-patch building footprints. FEMA USA Structures returned 202 footprints; OSM returned 11 `building=*` ways; TNMap FEMA BLE returned 0. Imported FEMA as a default-off viewer layer. See `buildings_layer.md`.
17. [X] Add USDA NAIP as a tracing imagery layer and extend the viewer editor
    with raw LineString trace capture. The 2025 county archive is cached but
    blocked by MrSID support in the current toolchain; the browser layer uses
    USDA's public 2023 Tennessee NAIP cache. See `imagery_tracing_layer.md`.
18. [X] Add visitor support callout circles for South Pittsburg/Kimball and
    Monteagle services. See `visitor_context_callouts.md`.

## Initial scaffold files

The first MVP scaffold added:
- `mvp/docker-compose.yml`
- `mvp/init_db.sql`
- `mvp/README.md`
- `website/index.html`
- `website/README.md`
- `website/data/publish.geojson`

The MVP has grown well past this -- a viewer with ~20 toggleable layers, a POI
editor, a contour pipeline, and ~25 importer/verifier scripts. For the current
file set see `mvp/README.md`, `mvp/scripts/README.md`, and `website/README.md`.
