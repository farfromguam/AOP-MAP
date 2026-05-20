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

## Files added
- `mvp/docker-compose.yml`
- `mvp/init_db.sql`
- `mvp/README.md`
- `website/index.html`
- `website/README.md`
- `website/data/publish.geojson`
