# Session Handoff

Date: 20260614

Short pointer for the next session. The durable record lives in the cards
(`tasks/*/_done/<feature>.md`), `research/viewer.md`, `search_map.md`, and
`spinup/mvp_runbook.md`. The session-by-session changelog is archived — see
**Archive convention** below.

-----

## Latest (2026-06-14)

**Council made task-scoped (durable rule fix).** Multi-agent commingling was causing the
council to be deferred / its clearance to go stale (`coord/five-item-review.md` +
`six-item-viewer-batch.md` say so in their own words). Fixed: the council now reviews the
current task's `claim:`, not the whole working tree, and a commingled tree is never grounds
to defer — *"get the council together on that and ignore what is not yours."* Codified in
`council/completion_gate.md` ("Scoped to your task" + best-effort-marker note),
`council/_readme.md`, `council/steward.md`, `.claude/commands/council.md`,
`handoff/coord/_protocol.md`. Then ran the now-scoped council retrospectively over the
recent batch (`305fcc3..HEAD`): Witness/Quartermaster/Mason **clear**; Warden **andon →
resolved clear** (it flagged a third card's work the batch spans — the illustrator-trace
waypoints/Shower House/scripts — which has its own card + its own council clearance on
disk). No code defect; the only residual is the user's commits commingling three cards,
which is the git gate. Receipt: `brain/output/council/recent_batch_retro_20260614.md`.

The 2026-06-14 session-by-session changelog is archived →
`session_context_20260614.md`. Headline state for the next session:

- **Gold-promotion + pins + publish-curation batch — v90 (UNCOMMITTED).** A 9-item
  user batch: (1) location pins (camp waypoints + facility pins) gated to **Park +
  Topo only** (out of Trace/Satellite) in `viewer_core.js` `applyPreset`; (2/8)
  Saturday-segment trail_centerlines removed from publish + their `aop_poi_index.json`
  orphans; (3) **Shower House starred** (`highlight:true`, stays bronze); (4) the 20
  `sfwda-*` placeholder trail names set to null; (5) **Launchpad → "1 Launchpad"** (data
  + a `trailDisplayName` no-double-prefix guard); (6/7) both remaining **silver files
  promoted to gold** — `silver_publish.geojson`→`gold_publish.geojson` and
  `silver_aop_visitor_context_callouts.geojson`→`gold_aop_visitor_context_callouts.geojson`
  (rename + `_meta`/per-feature re-stamp + reference sweep + `stamp_maturity.MATURITY`),
  with the duplicate Ellis **POI** dropped (inholding parcel kept); (9) **Jackson Point**
  (OSM peak) added to the gold publish group. **This batch performs the `v89→v90` bump**
  (the working tree was actually at v89 — index.html had been reverted mid-session — so
  the one bump covers the pending cemetery fix below AND this batch). **Pins directive
  REVERSED by the user 2026-06-14** (verbatim: *"the pins show up on satellite but not
  topo. this is backwards."*): the original "no pins in trace or topo" (→ Park+Satellite,
  first shipped + verified) became **Park+Topo** (`viewer_core.js:774` `pinsOn = park ||
  topo`; pins on the Topo navigational read, off the Satellite imagery). Code + verifier
  + card all agree on Park+Topo; re-verified by observation 20/20 (the only flake is the
  external `tnmap.tn.gov` satellite tile in headless). Pin-flip cleared by a core-three
  council (`brain/output/council/pins_topo_not_satellite_20260614.md`). Card:
  `tasks/01_mvp/gold_promotion_pins_curation_v90.md` (RESOLVED → SHIPPED). **Durability gap:**
  `raw/publish.geojson` + PostGIS `publish` view still carry the removed Saturday
  segments + Ellis POI and lack Jackson Point (served-only curation; DB owed).

- **Off-park cemeteries removed from gold waypoints + the trace round-trip
  (UNCOMMITTED; the `v89`→`v90` bump is now PERFORMED by the v90 batch above).** The satellite
  trace had swept all four county cemeteries into
  `gold_aop_waypoints_traced.geojson`, so the read viewer drew Tate/Bible/Gilliam/Ellis.
  User: only Ellis (the in-park inholding) belongs; the other three are bronze reference
  (already in `bronze_aop_cemeteries.geojson`). (1) Removed the three from the served
  file (26→23 feats, Ellis kept);
  verified rendered cemetery-kind == `['Ellis Cemetery']`, 0 console errors (the served
  data change is what makes the `v89`→`v90` bump owed — see header). (2) Then
  closed the durability gap so a re-upload can't reintroduce them: dropped
  `aop_cemeteries.geojson` from `export_illustrator_trace.py`'s waypoint sources (Ellis
  still seeds via the publish POI), added a name-based cemetery drop to
  `import_illustrator_trace.py` (keeps Ellis), and fixed both scripts' **stale medallion
  paths** (the round-trip had been broken since commit `91a017e` renamed served files).
  Verified by running the fixed import against the real Affinity master — "waypoints: 23
  (dropped 3 off-park cemeteries)", served files backed-up + restored after. **Owed
  (flagged, user's call):** a re-import still strips authored waypoint
  descriptions/`kind`/tags (mirror the trail provenance-carry for waypoints to fix) and
  writes without `_meta` (needs a re-stamp; `stamp_maturity.py` also has stale medallion
  keys). Card: `tasks/14_illustrator_trace/satellite_illustrator_export.md` ("Off-park
  cemeteries de-promoted from gold" + "Durability gap CLOSED").

- **POI search/click/links + G-Central scrub — shipped v89 (UNCOMMITTED).** Camp
  POIs (waypoints) are now searchable + clickable with descriptions (Hot Rocks Comp
  Pad reads as an RC-crawl comp pad); AOP badge + Rock Warblers logos got real
  tooltips; a data-driven final `link` renders in popups (region callouts → Marion
  County tourism, AOP → its site, Rock Warblers → FB event). "G-Central" removed from
  all product data/code (served + `raw/` + manifest + poi_index + the active
  `show_and_shine_northstar.md`). Authored fields live ON the data in served **and**
  `raw/`; only a generic link renderer in `feature_display.js`. Verified
  (`/tmp/verify_poi_batch.py`, all PASS, 0 console errors). Diff: `viewer_core.js`,
  `feature_display.js`, `viewer.css`, `sw.js`, `index.html` + the data files. Card:
  `tasks/01_mvp/poi_search_click_links.md`. The "no-trails" SFWDA paper overlay
  for Trace is **also done** — the user supplied a clean trail-free sheet
  (`sfwda_aop_trail_map_no_trails.webp`), wired as a 6x6 warp-mesh of
  `sfwda-notrails-tile-r-c` image sources (the old page's bake), default-on in Trace
  at raster-opacity 0.7. `core` DB not scrubbed of G-Central (no Docker).
- **Landcover tree cover — hand-edited + integrated.** The user traced the 9-patch
  vegetation in Affinity (165→159 polys); baked to
  `website/data/aop_landcover_9patch.geojson` (318 features, subdivided), recolored
  **`#D1D2B8`**, non-park context at **60%** opacity (park solid, `fill-antialias:false`,
  borderless — the opacity step at the park edge is the separator). `sw.js`/`#appVersion`
  **v88**. Council-cleared; `.council-cleared` written. **UNCOMMITTED** (`viewer_core.js`
  + `sw.js` + `index.html` — a clean one-task diff). Card:
  `tasks/01_mvp/_done/landcover_layer.md`; the full export/import/preview/map-test pipeline
  (`export_landcover_svg.py` / `import_landcover_svg.py` / `build_landcover_map_test.py` /
  `verify_landcover_svg_roundtrip.py`, shared `RasterFrame` + `recover_frame` +
  `vegetation_features`) and the opacity iteration are in the archive.
- **Committed by the user as HEAD `91a017e` ("medallion rename")**: the six-item viewer
  batch (v87 — trail `display_name`, borderless tree cover, medallion data tiers,
  production-tier alert, persistent active item, Pro-Line@firepit), the first Affinity
  satellite-trace ingest (130 trails / 26 waypoints / 6 buildings + `aop-waypoints` layer
  + facility pins), and the v69–v83 viewer-extraction stretch. (Earlier the user committed
  `59e4686`, subject "v84", which held v86.)
- **Owed:** name the 10 new user-traced trails; richer POI-tab (blurbs/icons/search) for
  the waypoints; apply Front Office's refined footprint; editor (`panel.js`) medallion
  re-group + landcover-paint cleanup; the data-integrity / 600-acre publishability items
  below.

## Where we are

Sprint 01 (MVP), Sprint 02 (Editor & Polish), and Sprint 03 (Event App Loop)
are closed. Sprint 03's reviewed cards live in `tasks/03_event_app/_done/`.
`tasks/03_event_app/misc_3.md` was left active by request. Sprint 04 starts at
`tasks/04_event_app/_readme.md`; it was triaged 2026-05-30 to `_done/` or
`tasks/10_deferred/`. The current active lane is the viewer extraction at
`tasks/13_viewer_extraction/` (slate closed-done; landcover lives under
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
- `session_context_20260613.md` — the 2026‑05‑27 → 2026‑06‑13 stretch: PWA QA swarms (`pwa_qa.md`, `pwa_qa_2.md`) + data-bakes, icon master sheet, editor unified-tree → three-bucket V3c, the Going-Gold ralph loop (slices 1–5 + Retirement, committed `ce920bd`/`737fc26`), trail-research integration, the viewer extraction into `viewer_core.js`/`viewer.css` (`tasks/13_viewer_extraction/`), banded-map draping (`viewer_band.js`), the `?tester=1` GPS offset, and the left-rail drawer persistence through v70.
- `session_context_20260614.md` — the v71→v88 stretch: the six-item viewer batch (v87), the first Affinity satellite-trace ingest + waypoint/facility wiring, the vegetation editable-SVG round-trip → integrated `#D1D2B8` tree cover (60% non-park, `fill-antialias` seam fix), the v83 five-item review, the Illustrator trace export, and the v69–v82 viewer-extraction landings (Locate travel-to-park, schedule spinner, band merge, drawer persistence, tester mode).

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
