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

1. [ ] Launch the PostGIS container in `mvp/`
2. [ ] Confirm `mvp/init_db.sql` created the database schema
3. [ ] Connect QGIS to `localhost:5432` and inspect source/feature tables
4. [X] Load a placeholder `publish.geojson` into `website/`
5. [ ] Preview `website/index.html`
6. [ ] Replace placeholders with actual AOP parcel/trail/observation data as available

## Files added
- `mvp/docker-compose.yml`
- `mvp/init_db.sql`
- `mvp/README.md`
- `website/index.html`
- `website/README.md`
- `website/data/publish.geojson`
