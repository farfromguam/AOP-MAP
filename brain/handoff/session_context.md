# Session Handoff

Date: 20260613

Short pointer for the next session. The durable record lives in the cards
(`tasks/*/_done/<feature>.md`), `research/viewer.md`, `search_map.md`, and
`spinup/mvp_runbook.md`. The session-by-session changelog is archived — see
**Archive convention** below.

-----

## Latest (2026-06-13)

The recent thrust is **extracting the read viewer into a standalone shell**
(`website/viewer_core.js` + `viewer.css`, served as `SHELL_ASSETS`/SWR) and
re-attaching the pieces that were severed in the split. Most recent landings,
all **UNCOMMITTED** (user's git gate):

- **Schedule loading spinner + single-number search review.** Card:
  `tasks/13_viewer_extraction/viewer_schedule_loading.md`. (1) The Events tab's bare
  `Loading schedule...` text is now the designed **spinner row** from
  `calendar_placeholder_v2_spinner.html` ("V2"): ring + "Loading events… / Schedule
  arriving shortly", shown only while the schedule JSON loads (the existing
  `calendarDays.innerHTML` swap removes it on data — the user's "only if it's actually
  loading"). 2 files, +24/−1, **no JS** — `index.html` markup + `viewer.css` spinner
  block. Verified by observation (Playwright 11/11, 0 errors; 13 real rows replace the
  spinner; `brain/output/schedule_spinner_leftrail.png`). (2) Single-number search
  ("1" → trail 1 **and** 1X) reviewed and **verified identical** between `old_index.html`
  and the extracted viewer (same 12 rows, 0 errors) — **no change owed**; left untouched
  per the "dont change yet" hold. `sw.js`/`#appVersion` bump owed on commit (shell assets
  changed) — the user's git gate. UNCOMMITTED. (An early misread chased the
  `load_animations.html` entrance choreography — reverted, no stray change.)
- **v72 — left-controls overlay no longer eats map drags over its empty regions.**
  CSS-only fix in `viewer.css`: `.left-controls` was a fixed 340px-wide overlay with
  default `pointer-events`, so its grid gaps, the pill-bar gaps, and the full-width
  `.lr-drawer` row beside the narrow icon column (when the drawer is collapsed) all
  intercepted map pan/zoom and showed the arrow cursor instead of the grab-hand.
  Standard pass-through: `.left-controls{pointer-events:none}` + `auto` re-armed on the
  visible cards (`.pill`, `.lr-icon-col`, `.lr-content-col`, `.util-install`,
  `.util-ios-hint`). Verified by observation (Playwright `:8001`): the empty regions now
  return `canvas` `cur=grab`, every control still clicks. v71→v72 (`sw.js` + `#appVersion`).
  **UNCOMMITTED** (user's git gate). Addendum on
  `tasks/13_viewer_extraction/viewer_drawer_schedule.md`.
- **v71 — the off-edge band is merged into the clean read viewer.** The geolocated
  neat-line band (`viewer_band.js`, 38 layers: paper mask + keyline + 36 draped art
  tiles) now ships in `index.html`, not just the proof page. `viewer_core.js` grew
  the seam: `window.AOPViewer = { map, regionBounds }` and a padded camera leash
  (`BAND_PAD = 0.13` → `REGION_MAXBOUNDS`) so the whole printed sheet seats; the
  Region preset now outsets ~7% (was inset ~15%) so the frame doesn't crop. One
  robustness fix to the council-cleared band module: `raiseBand` re-floats on every
  `styledata` (the core adds ~50 layers async over ~8 s, each landing on top), not
  idle-only. `sw.js` precaches `viewer_band.js` + `rw-mark.svg`; both bumped v70→v71.
  No CRUD crossed (read viewer stays read-only). Verified by observation (real Chrome
  / Playwright: 38 layers, z-order holds top, 8-point paper-perimeter PIL sample,
  presets PASS). Card: `tasks/13_viewer_extraction/viewer_band_merge.md`. Council
  reviewed on the diff. **Owed (user's gate):** the commit + retire the spent
  scaffolding (`viewer_banded.html`, `viewer_banded_compare.html`, `css/viewer_band.css`).
- **v70 — left-rail drawer open/close now persists.** `aop_left_rail_drawer_v1`
  stores `{search,hot,cal}` booleans, read on init / written on each tab click in
  `viewer_core.js`; clipboard drawer height (`aop_lr_card_height_v1`) verified
  end-to-end. 18/18 Playwright PASS (`verify_drawer_persist.py`), 0 errors. Card
  addendum on `tasks/13_viewer_extraction/viewer_drawer_schedule.md`. Council not
  yet run.
- **v69 — tester mode = `?tester=1`** (not a `tester.html`; `editor_is_the_viewer`).
  Date offset stays `?clock=`; added a lat/long GPS offset that wraps
  `navigator.geolocation` before `GeolocateControl` reads it, pinning the first fix
  to the park pavilion and preserving real movement delta → walking the real
  neighborhood walks the dot around the park. Rust "TESTER" chip + `.tester` class
  (future edit-FAB hook). Card: `viewer_locate_install_version.md`; `pages.md`
  updated. **Council core-three cleared**, but the `.council-cleared` marker was
  **not** written — the Tier-0 hash spans all of `website/`. The band is now merged
  and council-reviewed (see v71 above); the remaining unreviewed surface in the
  hash is the data-editor (`data_editor_map.js`) work from other sessions. The
  Stop hook will keep nudging until that is reviewed or this work is committed
  apart from it.

**Still future:** the on-tester **edit FAB** waits on the editor porting into the
extracted read core (editor still lives in `panel.js` / `old_index.html`).

Full per-session detail for 2026-05-27 → 2026-06-13 is in
`session_context_20260613.md`.

## Where we are

Sprint 01 (MVP), Sprint 02 (Editor & Polish), and Sprint 03 (Event App Loop)
are closed. Sprint 03's reviewed cards live in `tasks/03_event_app/_done/`.
`tasks/03_event_app/misc_3.md` was left active by request. Sprint 04 starts at
`tasks/04_event_app/_readme.md`; it was triaged 2026-05-30 to `_done/` or
`tasks/10_deferred/`. The current active lane is the viewer extraction at
`tasks/13_viewer_extraction/`.

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
- `session_context_20260613.md` — the 2026‑05‑27 → 2026‑06‑13 stretch: PWA QA swarms (`pwa_qa.md`, `pwa_qa_2.md`) + data-bakes, icon master sheet, editor unified-tree → three-bucket V3c, the Going-Gold ralph loop (slices 1–5 + Retirement, committed `ce920bd`/`737fc26`), trail-research integration, the viewer extraction into `viewer_core.js`/`viewer.css` (`tasks/13_viewer_extraction/`), banded-map draping (`viewer_band.js`), the `?tester=1` GPS offset, and the left-rail drawer persistence through v70.

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
