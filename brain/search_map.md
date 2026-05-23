# AOP Search Map

TL;DR:
- Keyword routing for the staged AOP brain.
- Use this before grepping blindly.
- If a question asks "what did we decide," start in `northstar/`; if it asks "where did that fact come from," start in `research/`.

#aop #search #routing

-----

## Map project

- AOP, Adventure Off Road Park, South Pittsburg, Ellis Cove Road: `research/aop_south_pittsburg_sources.md`
- bounds, AOI, 9-patch, current parcel envelope, data acquisition: `research/aop_data_bounds.md`, then `research/aop_south_pittsburg_sources.md`
- viewer, web map, `index.html`, layers, toggles, satellite, hillshade, 3D terrain, contours, roads, water, lidar tile index, search box, calendar, MapLibre: `research/viewer.md`
- imagery tracing, USDA NAIP, 2023 NAIP, 2025 NAIP, MrSID, trace line, raw image traces: `tasks/01_mvp/imagery_tracing_layer.md`, then `research/viewer.md`
- POI editor, draw, footprint, pavilion, building, Terra Draw, on-map editing: `tasks/01_mvp/poi_editor.md`
- feature list panel, per-feature visibility, drag-to-move, move mode, ✋ button, long-press, fly to feature, `aop_feature_visibility_v1`, `aop_visitor_context_overrides_v1`, find and move, shared primitive, map-click panel reveal, revealFeatureInPanel, bindPanelReveal, .revealed flash, per-section export, import, ↑Export, ↓Import, Export all, Import all, `aop-section-state-v1`, `aop-viewer-preset-settings-v2`, retired Snapshot Preset: `tasks/02_edit/poi_editor_v2.md`
- building footprints, FEMA USA Structures, structures layer, ORNL footprints: `tasks/01_mvp/buildings_layer.md`, then `research/viewer.md`
- visitor context, support towns, South Pittsburg, Kimball, Monteagle, food, fuel, hotels, callout circles: `tasks/01_mvp/visitor_context_callouts.md`, then `research/viewer.md`
- GPX, field track, ride recording, observation import: `import/_readme.md`, then `tasks/01_mvp/mvp_validation_loop.md`
- activity hotspots, heatmap, dwell time, user-entered trail hotspots, timestamped GPX, synthetic Saturday activity, simulated users, OSM-following routes, GPS recorder: `tasks/01_mvp/activity_hotspots.md`, then `research/viewer.md`
- event schedule, event calendar, RC event, G6, Pro-Line, schedule rows, `#pavilion`, `#registration`, event POI: `tasks/01_mvp/event_schedule_layer.md`, then `research/viewer.md`
- database schema, `init_db.sql`, tables, raw/core/publish zones, publish views, status vocabularies: `tasks/01_mvp/code_health_pass.md`
- contour build, gdal_contour, GDAL Docker, DEM clip: `tasks/01_mvp/lidar_contour_pipeline.md`, then `spinup/mvp_runbook.md`
- map build, PostGIS, QGIS, MapLibre, PMTiles, Cloudflare, Phoenix: `tasks/01_mvp/aop_south_pittsburg_map_build_card.md`
- spinup, runbook, CWC, database port, PostGIS connection, QGIS connection, Docker, `localhost:55432`, static viewer port, manual preview, Playwright port, `localhost:8000`, `localhost:8001`, port collision: `spinup/mvp_runbook.md`, then `spinup/discovery.md`
- source ledger, permission, confidence, provenance, publishable: `northstar/source_register.md`
- community trail pull, OSM 9-patch, SFWDA 2015 raster, raw zone, import staging: `import/_readme.md`
- cemetery, Ellis Cemetery, hole in the plot, inholding, carve-out, interior ring, gap in the boundary: `research/aop_ellis_cemetery.md`, then `tasks/01_mvp/cemeteries_layer.md`
- forest, land cover, 9-patch land cover, vegetation, tree canopy, canopy height, CHM, lidar canopy, hag, PDAL, NAIP, vectorize satellite, classification, Muted Earth palette, viewer restyle: `tasks/01_mvp/landcover_layer.md`, then `research/viewer.md`
- print map, wall map, whiteboard validation, board markup: `northstar/map_northstar.md`, then `tasks/01_mvp/aop_south_pittsburg_map_build_card.md`

## Working method

- open question, should we, decision: `practices/01_apparent_answers_first.md`
- conflicting facts, sources disagree, evidence mismatch: `practices/02_triangulation.md`
- stop the line, drift, unreconciled conflict: `practices/03_andon.md`
- first pass, slice, V1, proof: `practices/04_thin_vertical_slices.md`
- research brief: `flows/research_flow.md`
- task planning: `flows/plan_task.md`, `tasks/_extend.md`
- task execution: `flows/work_task.md`

## Collaboration

- durable rules, memory vs brain: `ai_rules/brain_is_durable.md`
- extract before invent: `ai_rules/extract_before_invent.md`
- don't touch git: `ai_rules/no_commits.md`
- cards are direction: `ai_rules/cards_not_gospel.md`
- preserve user directives in cards: `ai_rules/preserve_card_directives.md`
- recommendation requested, option menu, decision: `ai_rules/commit_in_prose.md`
- writing style: `ai_rules/user_writing_style.md`, `voice/voice_guide.md`
