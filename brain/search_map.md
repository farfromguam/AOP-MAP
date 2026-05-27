# AOP Search Map

TL;DR:
- Keyword routing for the staged AOP brain.
- Use this before grepping blindly.
- If a question asks "what did we decide," start in `northstar/`; if it asks "where did that fact come from," start in `research/`.

#aop #search #routing

-----

## Map project

- AOP, Adventure Off Road Park, South Pittsburg, Ellis Cove Road: `research/aop_south_pittsburg_sources.md`
- personas, users, driver, marshal, spectator, volunteer, vendor, sponsor, kid crawl, hot button audience, view defaults: `northstar/personas.md`
- bounds, AOI, 9-patch, current parcel envelope, data acquisition: `research/aop_data_bounds.md`, then `research/aop_south_pittsburg_sources.md`
- viewer, web map, `index.html`, layers, toggles, satellite, hillshade, 3D terrain, contours, roads, water, lidar tile index, search box, calendar, MapLibre: `research/viewer.md`
- imagery tracing, USDA NAIP, 2023 NAIP, 2025 NAIP, MrSID, trace line, raw image traces: `tasks/01_mvp/_done/imagery_tracing_layer.md`, then `research/viewer.md`
- POI editor, draw, footprint, pavilion, building, Terra Draw, on-map editing: `tasks/04_event_app/poi_editor_followups.md`, then `tasks/03_event_app/_done/poi_editor_tree_inline_accordion.md`, then `tasks/01_mvp/_done/poi_editor.md`
- POI browser, left-rail POI tab, `aop_poi_index.json`, info needed revisit chips, owed work, visitor blurbs: `tasks/04_event_app/data_integrity_publishability.md`, then `tasks/04_event_app/viewer_polish_followups.md`, then `tasks/03_event_app/_done/left_panel_poi_browser.md`
- feature list panel, per-feature visibility, drag-to-move, move mode, ✋ button, long-press, fly to feature, `aop_feature_visibility_v1`, `aop_visitor_context_overrides_v1`, find and move, shared primitive, map-click panel reveal, revealFeatureInPanel, bindPanelReveal, .revealed flash, per-section export, import, ↑Export, ↓Import, Export all, Import all, `aop-section-state-v1`, `aop-viewer-preset-settings-v2`, retired Snapshot Preset: `tasks/02_edit/_done/poi_editor_v2.md`
- building footprints, FEMA USA Structures, structures layer, ORNL footprints: `tasks/01_mvp/_done/buildings_layer.md`, then `research/viewer.md`
- visitor context, support towns, South Pittsburg, Kimball, Monteagle, food, fuel, hotels, callout circles: `tasks/01_mvp/_done/visitor_context_callouts.md`, then `research/viewer.md`
- GPX, field track, ride recording, observation import: `import/_readme.md`, then `tasks/01_mvp/_done/mvp_validation_loop.md`
- activity hotspots, heatmap, dwell time, user-entered trail hotspots, timestamped GPX, synthetic Saturday activity, simulated users, OSM-following routes, GPS recorder: `tasks/01_mvp/_done/activity_hotspots.md`, then `research/viewer.md`
- event schedule, event calendar, RC event, G6, Pro-Line, schedule rows, `#pavilion`, `#registration`, event POI: `tasks/04_event_app/rock_warblers_content_audit.md`, then `tasks/01_mvp/_done/event_schedule_layer.md`, then `research/viewer.md`
- show and shine, show & shine, concours, build theme, Trail Blazing theme, Advance Party, scout build, field detail, rig awards, People's Choice: `northstar/show_and_shine_northstar.md`, then `tasks/04_event_app/rock_warblers_content_audit.md`
- feature tag binding, `#tag` on feature, `aop_feature_tags_v1`, tagToFeature, feature tag input, pavilion → 1010 building, schedule without coordinates, tag a building, tag a POI, named-feature tagging, seed `#pavilion`, refresh search index, refreshEventScheduleSearchIndex: `tasks/02_edit/_done/named_feature_tagging.md`, then `research/viewer.md`
- event app, CRUD, uploads, contributor submissions, trail submission, landmark submission, moderation queue, attachment model, invite codes: `tasks/04_event_app/event_crud_upload_loop.md`, then `tasks/03_event_app/_done/full_loop_crud_upload_audit.md`
- virtual clock, test clock, date time slider, reset local overrides, reset new user, pocket map persistence, left drawer persistence, active tab persistence, landmark hot lane: `tasks/03_event_app/_done/viewer_session_state_test_clock.md`
- load animation, loading intro, left-rail intro, drawer teaching animation, intro jank, startup choreography: `tasks/backlog/load_animation_intro.md`, then `tasks/04_event_app/viewer_polish_followups.md`, then `tasks/03_event_app/_done/load animations.md`
- calendar placeholder, loading schedule, loading events, skeleton rows, spinner row, dot-progress, mockup compare: `tasks/04_event_app/calendar_placeholder_state.md`, then `tasks/04_event_app/viewer_polish_followups.md`
- viewer polish carryover, hot control two-lane, calendar expand on wide, scroll-into-view, collapse chevron uniformity, default-layer audit, brand-logo size slider, add-image runbook, preset tilt reset, preset rotation reset: `tasks/04_event_app/viewer_polish_followups.md`, then `tasks/03_event_app/_done/viewer_polish_carryover.md`
- Pass 4 CSS, theme review, code smell review, `!important` cluster, inline display hygiene, viewer visual audit: `tasks/04_event_app/viewer_polish_followups.md`, then `tasks/03_event_app/_done/code_health_pass_4.md`
- dev DB seed, database dump, reseed, configured data, pre-prod seed, spinup consistency: `tasks/04_event_app/dev_db_snapshot_reseed.md`, then `tasks/03_event_app/_done/dev_db_snapshot_reseed.md`
- brand logos, AOP logo, Rock Warblers logo, asset permission, transparent logo, icon-size slider, branding assets: `tasks/04_event_app/brand_assets_and_permissions.md`, then `tasks/02_edit/_done/branding.md`
- Park bounds icon, low-poly boundary icon, `#zoomPark`, park zoom button, icon picker: `tasks/04_event_app/park_bounds_icon_apply.md`, then `tasks/03_event_app/_done/park_bounds_icon_review.md`
- publishability, real trail data, trailhead placeholders, acreage reconciliation, 600+ acres, 3DEP DEM, synthetic activity boundary: `tasks/04_event_app/data_integrity_publishability.md`, then `tasks/01_mvp/_readme.md`
- database schema, `init_db.sql`, tables, raw/core/publish zones, publish views, status vocabularies: `tasks/01_mvp/_done/code_health_pass.md`
- contour build, gdal_contour, GDAL Docker, DEM clip: `tasks/01_mvp/_done/lidar_contour_pipeline.md`, then `spinup/mvp_runbook.md`
- map build, PostGIS, QGIS, MapLibre, PMTiles, Cloudflare, Phoenix: `tasks/01_mvp/_done/aop_south_pittsburg_map_build_card.md`
- spinup, runbook, CWC, database port, PostGIS connection, QGIS connection, Docker, `localhost:55432`, static viewer port, manual preview, Playwright port, `localhost:8000`, `localhost:8001`, port collision: `spinup/mvp_runbook.md`, then `spinup/discovery.md`
- localStorage migration, viewer storage key bump, `_v1` to `_v2`, schema bump, bundle schema, forward-only migration, no in-place adapter, reset overrides, `VIEWER_OWNED_STORAGE_KEYS`: `spinup/viewer_storage_migration.md`
- source ledger, permission, confidence, provenance, publishable: `northstar/source_register.md`
- community trail pull, OSM 9-patch, SFWDA 2015 raster, raw zone, import staging: `import/_readme.md`
- cemetery, Ellis Cemetery, hole in the plot, inholding, carve-out, interior ring, gap in the boundary: `research/aop_ellis_cemetery.md`, then `tasks/01_mvp/_done/cemeteries_layer.md`
- forest, land cover, 9-patch land cover, vegetation, tree canopy, canopy height, CHM, lidar canopy, hag, PDAL, NAIP, vectorize satellite, classification, Muted Earth palette, viewer restyle: `tasks/01_mvp/_done/landcover_layer.md`, then `research/viewer.md`
- print map, wall map, whiteboard validation, board markup: `northstar/map_northstar.md`, then `tasks/01_mvp/_done/aop_south_pittsburg_map_build_card.md`

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
