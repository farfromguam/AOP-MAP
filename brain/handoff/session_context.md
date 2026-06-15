# Session Handoff

Date: 20260614

Short pointer for the next session. The durable record lives in the cards
(`tasks/*/_done/<feature>.md`), `research/viewer.md`, `search_map.md`, and
`spinup/mvp_runbook.md`. The session-by-session changelog is archived — see
**Archive convention** below.

-----

## Latest (2026-06-14)

**Load pipeline PARALLELIZED — v94 bump PERFORMED (UNCOMMITTED).** User: *"take a look
at the loading pipeline … what makes it take so long. can we speed it up?"* Found
`map.on('load')` in `viewer_core.js` was a **serial `await` chain** — the ~13 remaining
served files downloaded one-at-a-time (the lazy-contours fix had only removed the 13 MB
blocker, not the chain shape). Bytes are small (~1.4 MB) so it's invisible on wifi, but
on a phone every round-trip pays full RTT with the connection idle between. Fix: a
**parallel kickoff** at the top fires all independent fetches at once; `fetchJson`
memoizes so the existing downstream awaits resolve in-flight requests — **`addLayer`
stacking unchanged**. `gold_publish` started up-front (kept its raw fetch for
error-surfacing); Trace `.webp` + brand logos cache-warmed. **Verified by observation**
(`brain/output/verify_load_pipeline_parallel.py`, SW blocked, 120 ms RTT): **max
concurrency 2→13, data span 4,113 ms→~400 ms (~10×)**, 14/14 PASS, 0 errors ×3 runs;
Park screenshot paints all layers; SFWDA overlay (36 tiles) + lazy contours intact.
viewer_core.js is a shell asset → **v93→v94 bump performed** (`sw.js` + `#appVersion`);
**commit remains the user's**. Addendum on `tasks/01_mvp/_done/lidar_contour_pipeline.md`
(sibling to the lazy-contours update — same handler).

**Waypoint ★ durability CLOSED — re-import now carries authored fields (UNCOMMITTED).**
User: *"fix the star durability … survive a db export or a re-import. save it to the gold
data directly. no shortcuts."* (1) DB export = non-threat: `gold_aop_waypoints_traced.geojson`
is file-based, no DB/canonical bake regenerates it (`bake_poi_stars` doesn't cover waypoints).
(2) Real threat was `import_illustrator_trace.py` `import_points()` rebuilding waypoints as
bare `{name,kind}`. Fix: `import_points()` is now provenance-preserving (mirrors
`import_trails` — carries `highlight`/`description`/`location_tag`/tags from prior gold by
name; edited geometry+name win), plus `preserve_unmatched_authored()` keeps ★/`#tag` POIs not
in the SVG (so the GPX-sourced Gravity Gauntlet survives). `_is_dropped_cemetery` lifted to
module scope (reused, never resurrects dropped cemeteries). **Build-pipeline only — no served
change, no `vNN` bump owed** (v93 already covers the star data). Verified —
`brain/output/verify_waypoint_star_durability.py` **14/14 PASS** (real code path, synthetic
edited SVG vs the actual gold; live gold untouched). Caveat: not run against the user's real
Affinity master (binary; in-repo SVG is a stale stub — always re-import from the complete
master). Council: `brain/output/council/waypoint_star_durability_20260614.md`. Addendum on
`tasks/14_illustrator_trace/satellite_illustrator_export.md`.

**v92→v93 bump PERFORMED (UNCOMMITTED).** All the v92-era uncommitted work below (About
rework, schedule #tag, POI kind/status/source, Hot Rocks + Gravity Gauntlet stars, contours
lazy-load, contours gold/silver split) shipped on committed v92 with no cache key change, so a
returning PWA browser kept serving stale v92 caches (the user couldn't see the changes on
`:8000` — code self-heals via SWR but `/data/` is cache-first). Bumped `sw.js VERSION` +
`index.html #appVersion` **v92→v93** to re-key SHELL_CACHE + DATA_CACHE. **The commit remains
the user's** (`no_commits`) — only the version strings were edited. The "owes v93" notes in the
entries below are now satisfied by this bump (commit still owed).

**Contours curated: GOLD lean (~3.9 MB), full set demoted to SILVER (UNCOMMITTED, owes
v93).** Measured the 13 MB contour layer: 560k vertices, **88% are the dense minor lines
in the outer 8 patches** (coords already 6dp — precision wasn't the lever). User: *"the
major lines for the whole 9 patch and the minor lines for just the park bounds … current
data demoted to silver and this new bit our gold dataset."* Built the medallion lineage
**raw → silver (full) → gold (served lean)**: `silver_aop_contours.geojson` (~12.9 MB,
2,831 feats, maturity silver, NOT served) = full set; `gold_aop_contours.geojson` (**~3.9
MB**, 911 feats, maturity gold) = ALL 501 index lines whole across the 9-patch + 410 minor
lines clipped to the park center cell (the `aop_data_bounds.md` working-envelope bbox); 1,920
outer minor lines dropped (~70% cut). New `mvp/scripts/curate_contours_gold.py` (shapely, no
GDAL), wired into `build_contours.sh` (full→silver→curate→gold; also fixed its stale
un-prefixed output path — GDAL portion unverified here). **No JS change** (viewer reads gold,
filters by idx). `_data_manifest.json` re-stamped + silver entry added. Verified on `:8001` —
`brain/output/verify_contours_curated_gold.py` **13/13 PASS**, 0 errors (minor all in park;
index reaches outside + inside; Topo loads 911 feats, both layers visible). Council
cleared 5/5 (witness·warden·quartermaster·mason·scribe):
`brain/output/council/contours_gold_silver_split_20260614.md`. Rides the same owed **v92→v93
bump** (served-data change). Addendum on `tasks/01_mvp/_done/lidar_contour_pipeline.md`.

**Contours lazy-load — phone-load fix (UNCOMMITTED, owes v93).** User: viewer *"takes a
long time to load on phones."* Cause: `viewer_core.js` fetched the **~13 MB**
`gold_aop_contours.geojson` with a **blocking `await` in `map.on('load')`**, though
contours are `visibility:none` in every preset but **Topo** (default Park) — and the load
handler is a sequential await chain, so **all park content (water/roads/buildings/trails/
waypoints/parcel/schedule) was serialized BEHIND** that 13 MB download+parse. Fix: removed
the eager fetch; added idempotent `ensureContours()` that `applyPreset` calls only when a
preset turns contours on (Topo), reading live `activePresetId` at resolve. No data/pipeline
change. Verified on `:8001` — `brain/output/verify_contours_lazy_load.py` **9/9 PASS**, 0
errors (PARK: no contour fetch, no source, but waypoints+buildings present; TOPO: fetched
once, source added, contours-index visible). Council: `brain/output/council/
contours_lazy_load_20260614.md`. Addendum on `tasks/01_mvp/_done/lidar_contour_pipeline.md`.
**Also flagged (NOT load-critical — deploy junk, not fetched/precached, user's call):**
`website/data/raw/` (~20 MB raw zone), `website/compare_data/` (~3.5 MB), **`website/brain/`
(an untracked COPY of the brain inside the served dir — shipped publicly if deployed)**,
and `old_index.html` + `leftrail_*.html`/`icon_master.html` mockup pages. (NOT junk, don't
delete: two `data/delete_*.geojson` are misnamed but **precached + active** in `sw.js` —
`delete_aop_synthetic_activity_hotspots.geojson`, `delete_sfwda_traced_trails.geojson`;
only `delete_aop_synthetic_activity_tracks.geojson` is genuinely unused.)

**Gravity Gauntlet starred into the POI list as a pin — data-only, rides v92 (UNCOMMITTED).**
User: *"add this to the map as a pin and star it to make it into the poi list as
#gravity-gauntlet make sure it ends up in the correct gold data source
`Wpt_5-16-26-144753_race_driver_position.gpx` in import dir."* The GaiaGPS waypoint (import
dir, lat 35.091910 / lon -85.751500) flows into the gold source
`gold_aop_waypoints_traced.geojson` as one feature: `name:"Gravity Gauntlet"`,
`location_tag:"#gravity-gauntlet"`, `highlight:true`, blurb from `TBI.copy`. **No JS change** —
the `aop-waypoints` pin layer + Camp POIs ★-group already exist (Hot Rocks pass), so it renders
as a pin and lands in the reader POI list (Camp POIs now holds **2** pads). Verified on `:8001`
— `brain/output/verify_gravity_gauntlet_in_poi_list.py` **16/16 PASS**, 0 console errors. **Owed:**
rides the same already-flagged v92→v93 bump + waypoint-round-trip durability gap as Hot Rocks
(not re-flagged). **Follow-up (user: *"make sure the schedule links to the proper point. there
should be examples"*) — DONE:** mirrored the `#firepit` example in `aop_event_schedule.json` —
added a `locations["#gravity-gauntlet"]` with `coordinates` identical to the waypoint and retagged
the `sat-gravity-gauntlet` session `#trails`→`#gravity-gauntlet`, so clicking that calendar row now
flies to the GG point + opens its popup, and the schedule anchor renders on the pin. Data-only, no
JS. Verified — `brain/output/verify_gravity_gauntlet_schedule_link.py` **15/15 PASS**, 0 errors.
Addendum on `tasks/13_viewer_extraction/_done/viewer_poi.md`.

**Hot Rocks Comp Pad starred into the POI list — rides v92 (UNCOMMITTED).** User:
*"Hot rock comp pad needs to be starred and show up in poi list."* The pad is a camp
**waypoint** (`gold_aop_waypoints_traced.geojson`), but the reader POI directory's
`STAR_GROUPS` sourced only buildings/trails/visitor-support — no waypoints group. Two
parts: (1) data — Hot Rocks Comp Pad gets `highlight:true` (only highlighted waypoint,
so only it appears); (2) `viewer_core.js` — exposed the loaded waypoints as
module-scoped `poiWaypointsData` + added a `{ id:'waypoints', label:'Camp POIs' }`
`STAR_GROUP` (same `buildPoiGroups`/`renderPoiTab`, one more source). Verified on `:8001`
— `brain/output/verify_hot_rocks_in_poi_list.py` **11/11 PASS**, 0 errors. **NOTE:** the
user committed v92 mid-session (HEAD `813d4c9` "schedule tweaks"), so this is uncommitted
*on top of* committed v92 with no bump — **owed a v92→v93 bump (user's git gate)** for the
shell-asset (`viewer_core.js`) + data change to reach cached PWA clients. **Owed (data):**
★ is authored-on-served (the waypoint round-trip strips authored fields; `bake_poi_stars`
doesn't cover this trace file); editor POI list (`main.js` `FEATURE_LIST_LAYERS`) has no
waypoints layer, so it's reader-only. Council core-three clear:
`brain/output/council/hot_rocks_in_poi_list_20260614.md`. Addendum on
`tasks/13_viewer_extraction/_done/viewer_poi.md`.

**Kind/Status/Source off the user-facing POI surfaces — rides v92 (UNCOMMITTED).**
User: *"we have kind and status as visible. we dont need those in the poi list. we
dont even need them in the world popovers. in the world there is a third source. that
also needs to go."* Three surfaces, one change: (1) `feature_display.js` `popupHtml`
(the ONE shared popover renderer) dropped the `Kind`/`Status`/`Source` `<dt>/<dd>`
lines — only an author-facing `Caveat` survives, and the meta `<dl>` is omitted when
empty; (2) `viewer_core.js` `renderPoiTab` (reader list) dropped the kind/status chips
+ `kind · status` subtitle fallback (+ removed the now-dead row fields); (3) `main.js`
`renderPoiTab` (editor list) same, keeping the "info needed — revisit" placeholder
chip. `featureDisplay()` still returns the fields — the editor's identify dock keeps
them for editing; only the visitor popover/list stop showing them. Rides the existing
v90→v92 shell bump (no second bump). Verified by observation on `:8001` —
`brain/output/verify_poi_no_kind_status_source.py` **9/9 PASS**, 0 console errors.
Addendum on `tasks/12_field_schedule_editor/_done/normalize_feature_display.md`.

**About tab reworked into web copy — v92 (UNCOMMITTED).** The user found the About
tab "mixed up": the v78 TBI pass had stapled the spoken Driver's Meeting transcript
onto the fact card (welcomed twice, repeated the spec + schedule). Reworked into
website copy — `aop_about.json` schema `v1→v2`: one welcome (good-attitude line folded
in), crew lore as prose, two subhead sections (**The park & the map**, **What to
expect**), `rules` lifted top-level. **Dropped at the user's direction:** the one-item
"Mandatory skills" row and the **rig spec entirely** (*"people can bring whatever RCs
they want"* — open event), plus the "traces back" / "weekend fills in" lines.
`renderAbout()` in `viewer_core.js` generalized from items[]/driver_meeting to
`sections[]+rules` (same DOM + safe-link/textContent). Verified on live `:8001`:
`verify_tbi_copy.py` rewritten, **18/18 About checks pass**, `tbi_about.png` shows the
render, no new console errors. Manifest + copy_registry updated; scratch
`about_preview.html` removed. Rides the shared `sw.js`/`#appVersion` **v92** bump (this
task performed the v91→v92; the schedule-tag session below rides it — one bump).
Addendum on `tasks/20_deferred/_done/rock_warblers_content_audit.md`. Council-cleared
5/5 (witness·warden·quartermaster·mason·scribe) over the scoped diff —
`brain/output/council/about_rework_v92_20260614.md`. (Pre-existing non-About tree state,
not this task: the schedule `#firepit` anchor; the bronze fema-buildings tier alert.)

**Schedule rows drop the raw #tag prefix — rides v92 (UNCOMMITTED).** Calendar rows
read `#pavilion - Pavilion (base camp)` — the internal join-key tag printed in front
of its own human name. User: *"I dont want to see #pavilion followed by pavilion.
feels redundant."* Dropped the `${tag} - ` prefix from the `.calendar-location` span
in **both** calendar renders (`viewer_core.js` `renderEventCalendar` + `main.js`'s
editor copy); rows now show just `location_label`. UI-only, schedule data unchanged;
the popup's labelled `Tag` diagnostic row left intact. Rides the existing v90→v92
shell bump (no second bump). Verified by observation on `:8001` —
`brain/output/verify_schedule_no_tag_prefix.py` **8/8 PASS**, 0 console errors.
Addendum on `tasks/01_mvp/_done/event_schedule_layer.md`.

**Search-clear de-thrones the held highlight — v91 (UNCOMMITTED).** Item 5 of the
six-item batch made a selection HOLD until the next one replaced it, but nothing ever
*removed* it. User: *"the app holds the highlight until something else takes it. -- if the
searchbar is cleared then the highlighted item also needs to be cleared. this defocuses it
as well."* New `clearActiveSelection()` in `viewer_core.js` (cancels the pulse, empties the
`search-highlight` source, de-thrones `activeEventSessionId` + re-renders the schedule) is
wired into both clear paths — the `input` listener when the field goes empty, and `Escape`.
Verified by observation (`brain/output/verify_search_clear_dethrone.py` 8/8, 0 errors;
regression `verify_label_border_persist_firepit.py` still 13/13). `sw.js`/`#appVersion`
v90→v91. Addendum on `tasks/02_edit/_done/six_item_viewer_batch_20260614.md`.

**S'mores moved to the firepit — rides v91 (UNCOMMITTED, separate session).** The v87
batch tagged the PRO Line *race* to `#firepit` but left both "Fire + s'mores" sessions
(`fri-fire`, `sat-fire`) at `#pavilion`, so the firepit POI showed the obstacle race but
not the campfire. User: *"Smores should be at the firepit. what happened?"* Source
(`brain/import/TBI.copy`) — they *"head to the fire pit for some smores"* — so both
sessions retagged `#pavilion`→`#firepit` in `aop_event_schedule.json` (data-only; no JS).
Rides the concurrent session's v90→v91 bump (re-keys `DATA_CACHE`; no second bump).
Verified by observation on `:8001` — `brain/output/verify_smores_at_firepit.py` **12/12
PASS**, 0 errors. Coord: `handoff/coord/smores-at-firepit.md`. Addendum (item 6) on
`tasks/02_edit/_done/six_item_viewer_batch_20260614.md`.

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
