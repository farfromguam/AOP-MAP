# Session Handoff: Sprint 03 pickup

Date: 20260524

Short pointer for the next session. The durable record lives in the cards.

## Archive convention

Each session pruned out of here lands at `session_context_<YYYYMMDD>.md`:

- `session_context_202605201517.md` — original handoff shape (the template).
- `session_context_20260522.md` — work log from the 2026‑05‑20 → 2026‑05‑22 sessions (lidar contours, water, search, cemeteries, land cover, NAIP tracing, presets, panel collapse, activity hotspots, initial event schedule).
- `session_context_20260524.md` — work log for the 2026‑05‑23 → 2026‑05‑24 sessions, covering the full Sprint 02 close (Buckets A–H), schedule clock-times, calendar current-time indicator, left hot button, hot-control two-lane, branding logos, named-feature tagging, search tags, viewer chrome polish, default-layer policy, and code-health Pass 3.
- `session_context_202605241228.md` — CWC dump after Sprint 03 carryover lanes 1–5 shipped.
- `session_context_20260525.md` — left-rail manilla-tab design exploration; five HTML mockup variants checked in under `website/leftrail_v*.html`. Build card: `tasks/03_event_app/left_rail_collapse_tabs.md`. No `website/index.html` changes.

Read an archive only if you need to retrace why something was built. The durable record for each feature lives in its `tasks/*/_done/<feature>.md` build card, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.

## Where we are

Sprint 01 (MVP) and Sprint 02 (Editor & Polish) are both closed. All their build cards are in their respective `_done/` folders.

The Sprint 02 carryover router is `tasks/03_event_app/viewer_polish_carryover.md`. Lanes 1–5 shipped 2026-05-24 (hot-control two-lane, calendar expand + scroll-into-view, collapse-icon uniformity, default-layer audit table in `research/viewer.md`, brand-logo size slider + add-image runbook). Lane 6 now lives at `tasks/03_event_app/code_health_pass_4.md`; Lane 7 stays on `tasks/01_mvp/_done/community_trails_import.md`. The 2026-05-25 camera correction is applied: zoom shortcuts reset to flat west-up, while Park / Topo / Trace layer presets preserve zoom, pitch, bearing, and independent 3D state.

**2026-05-25 Pass 4 + misc landings.** Calendar-card cream-surface chrome restored (`misc.md` "left side event calendar transparent" item — `.calendar-card` is back in the shared cream-surface group at `website/index.html:31`). Pass 4 first wave shipped via four parallel agents and landed in main: (1) `!important` cluster fully eliminated in the right-rail collapse-button + tune-control region by raising specificity to `.panel`-scoped selectors; (2) 8 safe palette token swaps (`#d8cdb4 → var(--cream-border)`, etc.); (3) full theme readability report (8 surfaces, 13 KEEP / 6 TWEAK / 4 FIX with WCAG math) recorded in `code_health_pass_4.md`; (4) Critique-C1 hot-button copy renamed off "heat" wording — `Trail heat / Activity evidence` → `Trail activity / Where rigs spent time` in HTML defaults, `refreshHotButton` fallbacks, aria-labels, and the matching verifier assertion. `code_health_pass_4.md` acceptance is now 7 of 8 boxes ticked (adjacent-JS-smells is the open one, deferred). Open follow-ups named at the bottom of that card: `--brown-soft` contrast bump to `#6a5638`, focus-visible outline alpha lift, `.layer-row.active` rust stripe, four remaining ≥3-count hex literals waiting for new role names.

Sprint 03's main thrust is `tasks/03_event_app/full_loop_crud_upload_audit.md` — event setup, CRUD, uploads, and the submission → review → publish loop. `tasks/03_event_app/dev_db_snapshot_reseed.md` carries the dev DB dump/reseed need from `misc.md`. `tasks/03_event_app/left_panel_poi_browser.md` shipped 2026-05-25 — the viewer now has a third left-rail `POI` tab sitting between `Events` and `About`, rendering a grouped index of event anchors, in-park buildings, observed trails, cemeteries, off-park visitor support, and drawn POIs. Visitor blurbs + revisit-note placeholders live in `website/data/aop_poi_index.json` (6 groups, 20 entries, 10 placeholders flagged for follow-up); the source GeoJSONs stay clean so re-exports can't overwrite authored copy. Smoke checks land in the extended `playwright_verify_presets.py`; a dedicated `playwright_verify_left_poi_browser.py` is the remaining acceptance box.

**2026-05-25 — left-rail manilla-tab design.** `tasks/03_event_app/left_rail_collapse_tabs.md` opens as design exploration. Five HTML mockup variants of a "unified drawer" for the search / hot / calendar cards live at `website/leftrail_v{1..5}_*.html`, indexed by `website/leftrail_compare.html`. Locked behavior: per-card icon toggle, upward absorption with island cut-out, E1 downward absorb for the bottom card. Variant pick is the open decision; nothing has touched `website/index.html` yet. CWC dump: `handoff/session_context_20260525.md`.

**2026-05-26 — right-panel editor consistency.** `tasks/03_event_app/right_panel_editor_consistency.md` shipped. `⧉ Export all` moved into the panel header beside `▾ Collapse panel` (the old `.panel-actions` row at the bottom of `#panelBody` is gone). Publishable section header gained its own `⧉` for parity with Source / Derived / Map editor; the POI section was deliberately not given one (its `poiGroup*` IDs don't match `sectionInputs`' `show*` filter, so the payload would be empty). Three layers that previously appeared as bare checkboxes in Publishable now get the full editor treatment: `activityHotspots`, `syntheticActivity`, and `eventSchedule` are registered in both `TUNABLE_LAYERS` (paint drawers) and `FEATURE_LIST_LAYERS` (CRUD index — 65 / 18 / 8 rows respectively, each with visibility + fly). New `refreshFeatureListData` helper lets `rebuildEventScheduleData` push fresh anchor data into the runtime without recursing through `registerFeatureListLayer`. The two failures in `playwright_verify_event_schedule.py` (search magnifier missing, hot-button click timeout) were verified pre-existing by stash + replay — not caused by this card.

The MVP backlog at `tasks/01_mvp/_readme.md` "Immediate next work" still has three open data-integrity items that unblock V1 publishable: item 9 (replace demo trail/trailhead placeholders with real source-backed AOP data), item 3 (connect QGIS to `localhost:55432`), item 8 (reconcile the 600+ acre official claim against the parcel envelope), and item 10 (swap the AWS Terrarium DEM for USGS 3DEP 1 m tiles, deferred until the 10 m look earns its keep).

## Live preview ports

- Human/manual preview: `cd website && python3 -m http.server 8000` → `http://localhost:8000/`
- Playwright verifiers: `cd website && python3 -m http.server 8001` → `http://localhost:8001/`. If 8001 is occupied, clean up the stale Playwright viewer and reload 8001 instead of starting a new numbered localhost. Do not fall back to 8000 for Playwright.

## Loose ends not yet on a card

- SFWDA paper-map alignment: the 4-corner image-warp is inspection-grade. Decision still owed on whether true georeferencing (GCPs + affine/projective in GDAL/QGIS) is required before any SFWDA trail centerline can be promoted to `core.trail_centerlines`. Captured in `tasks/01_mvp/_done/community_trails_import.md`.
- `source_register.sources` rows still owed before any raw-zone context (OSM tracks/landmarks, NHD water, USGenWeb Ellis burial roster, FEMA building footprints) is promoted to a `publish.*` view. Rules: `northstar/source_register.md`.

## Sidecar artifact kept in this folder

- `event_schedule_context_20260522.json` — actively referenced by `tasks/01_mvp/_done/event_schedule_layer.md` and `research/viewer.md` as the sister-event research input. Leave in place until the schedule card is re-opened or retired.

## Session note

This file is handoff context, not a durable policy document. Keep it short. When a session ends, prune this file back to a pointer and archive the changelog to `session_context_<YYYYMMDD>.md`. Do not append session-by-session update blocks here — they belong in build cards, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.
