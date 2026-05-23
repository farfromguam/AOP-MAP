# Session Handoff: MVP map work

Date: 20260522

This is the live session-handoff pointer for the AOP MVP map work. It is short by design — the brain holds the durable record.

## Archive convention

Each session pruned out of here lands at `session_context_<YYYYMMDD>.md`:

- `session_context_202605201517.md` — original handoff shape (the template).
- `session_context_20260522.md` — full work log from the 2026‑05‑20 → 2026‑05‑22 sessions (lidar contours, water, search, cemeteries, land cover on lidar CHM, NAIP tracing, presets, panel collapse, activity hotspots, event schedule).

Read the archive only if you need to retrace why something was built. The durable record for each feature lives in its `tasks/01_mvp/<feature>.md` build card, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.

## Where we are

The static viewer at `website/index.html` is the live work surface. It carries ~25 toggleable layers, a POI / line-trace editor, a JSON-driven event schedule sidebar, and Region / Park / Pavilion zoom presets bounded to the 9-patch. The Docker/PostGIS MVP database is wired but only holds demo data and one source-backed AOP parcel boundary; everything else in the viewer reads from `website/data/*.geojson` exports and public imagery/terrain tiles.

Last shipped: feature list panel — POI consumer + drag-to-move primitive + visitor-context drag + map→panel reveal + per-section/bulk Export-Import (2026-05-23). The shared find+move primitive has four consumers (POIs + buildings + cemeteries + visitor-context callouts) and a fifth panel-side hook (revealFeatureInPanel) closes the map-click → panel-row loop. Each panel section now has its own ↑/↓ Export/Import on its header (schema `aop-section-state-v1`); the panel footer has Export-all / Import-all (`aop-viewer-preset-settings-v2`). Snapshot Preset + the in-drawer Export Settings buttons retired. Build card `tasks/02_edit/poi_editor_v2.md`, verifier `mvp/scripts/playwright_verify_feature_list.py`. Bucket B's "region circle callouts need to be positionable" closes through this work. Sprint 02 branding asset drop is staged at `tasks/02_edit/assets/branding/raw/` awaiting placement + AOP permission decisions (Bucket F).

Current synthetic activity work: `mvp/scripts/simulate_saturday_activity.py` generates the pavilion-start Saturday model; `mvp/scripts/build_activity_hotspots.py` extracts both raw GPX and synthetic hotspots. The current synthetic layer follows nearby OSM `highway=track` / `service` linework, then filters hotspot output to stopped+slow dwell/crawl cells (`rank_by=stop_slow`) so it no longer renders as a dotted route. Pickup docs: `tasks/01_mvp/activity_hotspots.md`, `research/viewer.md`, and `mvp/scripts/README.md`. Likely next tweak: add a region/AOI argument to the simulator or hotspot builder so a user can force activity into a smaller polygon/bbox and produce more crossover/localized hotspots.

Previous shipped: tag-driven event schedule sidebar (2026-05-22). Build card `tasks/01_mvp/event_schedule_layer.md`.

Last code-health pass: Pass 2 closed (2026-05-22). Three sources-of-truth for the viewer toggle set collapsed to one (`LAYER_TOGGLES` is now authoritative). Playwright URL drift across 7 verifiers fixed; `WEBSITE_URL` env override now uniform. Pulse-animation constants named, `sliderPercent` helper extracted, two Python `except BaseException` blocks scoped, a NULL-edge-case in `import_gpx_track.sql` closed with `IS NOT DISTINCT FROM`. The three Pass 1 user-call items resolved (`import_geojson.sh` wired up, `secondary`/`ramp` road classes styled defensively, repo litter removed: `mvp/db-data-broken-*`, `mvp/website/`, 100 PNGs in `brain/output/`). Card: `tasks/01_mvp/code_health_pass.md`.

## Live preview ports

- Human/manual preview: `cd website && python3 -m http.server 8000` → `http://localhost:8000/`
- Playwright verifiers: `cd website && python3 -m http.server 8001` → `http://localhost:8001/`. If 8001 is occupied, use the next open port and pass `WEBSITE_URL=http://localhost:<port>/`. Do not fall back to 8000 for Playwright.

## What to pick up next

The MVP backlog is the source of truth — see `tasks/01_mvp/_readme.md`. Unstarted items, in roughly the order that unblocks the V1 publishable map:

1. Item 9 — replace demo `trail_centerlines` / `trailheads` placeholders with real source-backed AOP data, then re-export `publish.geojson`. This is the gap between "lots of context layers" and "actual AOP map."
2. Item 3 — connect QGIS to `localhost:55432` and inspect `raw.arcgis_feature_captures`, `core.parcels`, `core.park_boundaries`, `source_register.feature_sources`.
3. Item 8 — reconcile the 600+ acre official AOP claim against the imported `110 008.00` + `093 030.01` envelope (currently ~592 calc acres / ~573 deed acres).
4. ~~Item 11 — code-health remediation pass per `code_health_pass.md`.~~ Pass 2 closed (2026-05-22). Cosmetic deferrals carried forward for a Pass 3 when adjacent code is being touched.
5. Item 10 — swap the AWS Terrarium DEM for AOP-specific tiles from the USGS 3DEP 1 m DEM. Half-day toolchain + ~500 MB download; only worth it once the 10 m terrarium look has earned its keep.

## Loose ends not yet on a card

- SFWDA paper-map alignment: the 4-corner image-warp is inspection-grade. Decision still owed on whether true georeferencing (GCPs + affine/projective in GDAL/QGIS) is required before any SFWDA trail centerline can be promoted to `core.trail_centerlines`. Captured in `tasks/01_mvp/community_trails_import.md`.
- `source_register.sources` rows still owed before any raw-zone context (OSM tracks/landmarks, NHD water, USGenWeb Ellis burial roster, FEMA building footprints) is promoted to a `publish.*` view. Rules: `northstar/source_register.md`.

## Sidecar artifact kept in this folder

- `event_schedule_context_20260522.json` — actively referenced by `tasks/01_mvp/event_schedule_layer.md` and `research/viewer.md` as the sister-event research input. Leave in place until the event schedule card is closed.

## Session note

This file is handoff context, not a durable policy document. Keep it short. When a session ends, prune this file back to a pointer and archive the changelog to `session_context_<YYYYMMDD>.md`. Do not append session-by-session update blocks here — they belong in build cards, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.
