# Session Handoff

Date: 20260615

Short pointer for the next session. The durable record lives in the cards
(`tasks/*/_done/<feature>.md`), `research/viewer.md`, `search_map.md`, and
`spinup/mvp_runbook.md`. The session-by-session changelog is archived — see
**Archive convention** below.

-----

## Latest — pointer (the v88→v97 changelog is archived → `session_context_20260615.md`)

Headline state for the next session:

- **A large uncommitted body of work rides up to v97, awaiting the user's commit (the
  git gate).** HEAD is `0d7b750` "v96"; the working tree carries the v97 region-callout
  copy + CSS/JS cache-versioning on top of the earlier v88→v95 stretch (trail-permission
  gold, the trace round-trip bakes for line/point/polygon, load-pipeline parallelization,
  waypoint ★ durability, contours curation + lazy-load, POI/About/schedule polish, the v90
  gold-promotion batch). Every piece was verified by observation and council-cleared on
  disk; the commit + push are the user's. `.council-cleared` holds the current `website/mvp`
  diff hash.
- **Cut-off recovery — DONE (2026-06-15).** Re-ran every in-flight verifier GREEN by
  observation (callouts 10/10, cache-versioning 5/5, 3D-spin 7/7, park-border 8/8, contour
  mockup 13/13, persistence 13/13, dethrone 8/8); repaired 3 stale **dev-verifiers**
  (`verify_five.py` renamed-path crash + items 1-2 re-observed `display_name`/real POI rows;
  `verify_contour_styling_mockup.py` `.grid p`→`.grid > p`). No product code touched.
  Full-six council CLEAR.
- **DB reconciliation — DIAGNOSED, not done (2026-06-15, the user's call).** Docker is up;
  the GeoJSON export pipeline (`export_publish_geojson.sh`) diverged from the served `gold_`
  filenames at `91a017e`, so the served gold is **not reproducible from the DB**, and the DB
  is stale (G-Central in `core.features`, old Monteagle copy, 120 stale `trails` rows vs the
  130 file-based traces, Saturday segments still in the publish gate). DB left **UNTOUCHED**
  (160 features / 6 publish). Full diagnosis + recommended reconcile path + the exact staged
  copy → **2026-06-15 addendum on `tasks/20_deferred/data_integrity_publishability.md`**.
- **Full 3D camera re-enabled — v98 (2026-06-15).** User: "enable the 3d features … it
  seems we can only pivot around a center point." Reversed the button-only-pitch lock in
  `viewer_core.js`: removed `touchPitch.disable()` and set `pitchWithRotate:true`. Every
  camera gesture is now live (pan, pinch-zoom, two-finger/right-drag rotate,
  two-finger/vertical-drag tilt); the 3D toggle still jumps to 60°. Tilt ceiling kept at the
  MapLibre default 60° — the council Warden caught a first pass that also baked `maxPitch:80`
  as unrequested scope; reverted, and the 80° horizon ceiling is **offered to the user as an
  option, not done**. Cache bumped v97→v98 across sw.js + index.html (appVersion + 3× `?v=`);
  the user folded their ⓘ-background-update fix into the same v98 (see next bullet), so one
  bump serves both. Verified by observation 7/7 — `brain/output/verify_spin_while_tilted.py`
  (touchPitch ENABLED, maxPitch 60, and a right-drag-UP that tilts pitch 8°→60° to the ceiling,
  proving tilt-INTO-3D works rather than a fall to the 0 floor; blocked-tile "Failed to fetch"
  filtered as headless-env noise). Council: Witness + Warden andons both resolved and
  re-reviewed; Quartermaster clear. NOTE: rotate/tilt pivots around the viewport center for
  mouse-drag (MapLibre default) and the finger-midpoint for two-finger touch; true
  orbit-around-an-arbitrary-point would be a custom handler — not built.
- **ⓘ background-update fix — v98 (2026-06-15).** User: "make the i button … do a reload in
  the background for the pwa? it … 'not updated' often." Installed PWAs kept serving the
  cached build; root cause is iOS PWAs resumed from the app switcher never re-running `load`,
  plus GitHub Pages' max-age=600 on `sw.js`. Fix folds into v98 (no extra bump): in
  `index.html`'s SW registration — `updateViaCache:'none'`, `reg.update()` on load + on
  `visibilitychange`(visible) + `pageshow`, a `controllerchange`→reload-once guard, and a
  `window.AOPCheckForUpdate()` lever; in `viewer_core.js` the bottom-left ⓘ tap now calls it
  (delegated off `.maplibregl-ctrl-bottom-left`, fires on `.maplibregl-ctrl-attrib-button`).
  Tapping ⓘ = silent "get latest" → reloads only if a new build exists; attribution expand
  unchanged. Verified by observation 9/9 — `brain/output/verify_info_button_update.py`
  (steady-state warm-SW reload; flaky single-thread-server fetches re-checked, not gated).
  **Bumped v98→v99 (2026-06-15) at the user's request to test the update path on-device** —
  5 stamps (sw.js VERSION + #appVersion + 3× `?v=`); re-verified 9/9 + `node --check`. The
  test needs an OLD build already loaded: load v98, deploy v99, then tap ⓘ on the v98 client →
  it pulls v99 and reloads (the version label ticks 98→99). Commit/push stays the user's.
- **Owed (external-blocked):** on-device re-check of the full 3D camera (tilt + spin + pinch-
  zoom) now that v98 enables gesture pitch; on-device confirm the ⓘ-tap/foreground update
  actually pulls a fresh build past Fastly's ~600s edge TTL; the DB↔served reconcile above
  (the user directs when).

## Where we are

Sprint 01 (MVP), Sprint 02 (Editor & Polish), and Sprint 03 (Event App Loop)
are closed. Sprint 03's reviewed cards live in `tasks/03_event_app/_done/`.
`tasks/03_event_app/misc_3.md` was left active by request. Sprint 04 starts at
`tasks/04_event_app/_readme.md`; it was triaged 2026-05-30 to `_done/` or
`tasks/10_deferred/`. The current active lane is the viewer extraction at
`tasks/_done/13_viewer_extraction/` (slate closed-done; landcover lives under
`tasks/01_mvp/_done/landcover_layer.md`).

The Sprint 02 carryover router is archived at
`tasks/03_event_app/_done/viewer_polish_carryover.md`. The 2026-05-25 camera
correction is applied: zoom shortcuts reset to flat west-up, while Park / Topo
/ Trace layer presets preserve zoom, pitch, bearing, and independent 3D state.

Sprint 04's main app thrust is `tasks/04_event_app/event_crud_upload_loop.md`
— event setup, CRUD, uploads, and the submission -> review -> publish loop.
`tasks/04_event_app/dev_db_snapshot_reseed.md` carries the dev DB dump/reseed
need. `tasks/03_event_app/_done/left_panel_poi_browser.md` shipped the third
left-rail `POI` tab (grouped index of anchors, buildings, observed trails,
cemeteries, off-park support, drawn POIs). Visitor blurbs live in
`website/data/aop_poi_index.json` (source GeoJSONs stay clean so re-exports
can't overwrite authored copy).

The MVP backlog at `tasks/01_mvp/_readme.md` "Immediate next work" still has
open data-integrity items that unblock V1 publishable: item 9 (replace demo
trail/trailhead placeholders with real source-backed AOP data), item 3 (connect
QGIS to `localhost:55432`), item 8 (reconcile the 600+ acre official claim
against the parcel envelope), and item 10 (swap the AWS Terrarium DEM for USGS
3DEP 1 m tiles, deferred until the 10 m look earns its keep). Sprint 04 also
collects those blockers at `tasks/04_event_app/data_integrity_publishability.md`.

## Live preview ports

- Human/manual preview: `cd website && python3 -m http.server 8000` → `http://localhost:8000/`
- Playwright verifiers: `cd website && python3 -m http.server 8001` → `http://localhost:8001/`. If 8001 is occupied, clean up the stale Playwright viewer and reload 8001 instead of starting a new numbered localhost. Do not fall back to 8000 for Playwright.

## Loose ends not yet on a card

- SFWDA paper-map alignment: the 4-corner image-warp is inspection-grade. Decision still owed on whether true georeferencing (GCPs + affine/projective in GDAL/QGIS) is required before any SFWDA trail centerline can be promoted to `core.trail_centerlines`. Captured in `tasks/01_mvp/_done/community_trails_import.md`.
- `source_register.sources` rows still owed before any raw-zone context (OSM tracks/landmarks, NHD water, USGenWeb Ellis burial roster, FEMA building footprints) is promoted to a `publish.*` view. Rules: `northstar/source_register.md`.

## Sidecar artifact kept in this folder

- `event_schedule_context_20260522.json` — actively referenced by `tasks/01_mvp/_done/event_schedule_layer.md` and `research/viewer.md` as the sister-event research input. Leave in place until the schedule card is re-opened or retired.

## Archive convention

Each session pruned out of here lands at `session_context_<YYYYMMDD>.md`:

- `session_context_202605201517.md` — original handoff shape (the template).
- `session_context_20260522.md` — work log from the 2026‑05‑20 → 2026‑05‑22 sessions (lidar contours, water, search, cemeteries, land cover, NAIP tracing, presets, panel collapse, activity hotspots, initial event schedule).
- `session_context_20260524.md` — work log for the 2026‑05‑23 → 2026‑05‑24 sessions, covering the full Sprint 02 close (Buckets A–H), schedule clock-times, calendar current-time indicator, left hot button, hot-control two-lane, branding logos, named-feature tagging, search tags, viewer chrome polish, default-layer policy, and code-health Pass 3.
- `session_context_202605241228.md` — CWC dump after Sprint 03 carryover lanes 1–5 shipped.
- `session_context_20260525.md` — left-rail manilla-tab design exploration; five HTML mockup variants checked in under `website/leftrail_v*.html`. Build card: `tasks/03_event_app/_done/left_rail_collapse_tabs.md`. No `website/index.html` changes.
- `session_context_20260527.md` — misc_4 items 1–5 shipped, plus the POI/About empty-space CSS fix and the tab-restore fix. All in the working tree (uncommitted). See `tasks/04_event_app/misc_4.md` "What shipped (2026-05-27)" block for the full close-out and the trail-lane verifier residue routed to `viewer_polish_followups.md`.
- `session_context_20260613.md` — the 2026‑05‑27 → 2026‑06‑13 stretch: PWA QA swarms (`pwa_qa.md`, `pwa_qa_2.md`) + data-bakes, icon master sheet, editor unified-tree → three-bucket V3c, the Going-Gold ralph loop (slices 1–5 + Retirement, committed `ce920bd`/`737fc26`), trail-research integration, the viewer extraction into `viewer_core.js`/`viewer.css` (`tasks/_done/13_viewer_extraction/`), banded-map draping (`viewer_band.js`), the `?tester=1` GPS offset, and the left-rail drawer persistence through v70.
- `session_context_20260614.md` — the v71→v88 stretch: the six-item viewer batch (v87), the first Affinity satellite-trace ingest + waypoint/facility wiring, the vegetation editable-SVG round-trip → integrated `#D1D2B8` tree cover (60% non-park, `fill-antialias` seam fix), the v83 five-item review, the Illustrator trace export, and the v69–v82 viewer-extraction landings (Locate travel-to-park, schedule spinner, band merge, drawer persistence, tester mode).
- `session_context_20260615.md` — the v88→v97 stretch: the v90 gold-promotion/pins/publish-curation batch, off-park cemetery de-promotion, the POI/G-Central scrub, contours gold/silver split + lazy-load, load-pipeline parallelization, waypoint ★ durability, the trace round-trip bakes (line/point/polygon), trail-permission gold (v94→v95), the park-border faint + 3D-spin re-enable (committed v96 `0d7b750`), the v97 region-callout copy + CSS/JS cache-versioning, the 2026-06-15 cut-off-recovery verifier sweep, and the Docker-up DB↔served reproducibility diagnosis.

Read an archive only if you need to retrace why something was built. The durable record for each feature lives in its `tasks/*/_done/<feature>.md` build card, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.

## Session note

This file is handoff context, not a durable policy document. Keep it short.

**Prune at session end.** When a session ends, prune this file back to a
pointer and archive the changelog to `session_context_<YYYYMMDD>.md` (add a one-
line entry to the Archive convention index above). Do NOT append
session-by-session update blocks here — they belong in build cards,
`research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`, with at most a
short pointer under **Latest** here. This file ballooned to 4,261 lines / 376 KB
before the 2026-06-13 prune because ~17 days of session blocks were appended
without archiving; keep it under a few hundred lines so the next session can read
it whole. If it grows past that, archive and reset it as part of wrapping up.

The council gate enforces this: `.claude/hooks/council-gate.sh`, **once the
council has cleared the diff** (the genuine "work is done" moment — the assistant
does not commit), nudges once (per 100-line bucket) to prune if this file passes
**400 lines** — a thin pointer to this note; it never edits. Tune via
`AOP_HANDOFF_MAX_LINES`; downgrade to advisory with `AOP_HANDOFF_BLOCKING=0`.
