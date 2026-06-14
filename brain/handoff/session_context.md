# Session Handoff

Date: 20260613

Short pointer for the next session. The durable record lives in the cards
(`tasks/*/_done/<feature>.md`), `research/viewer.md`, `search_map.md`, and
`spinup/mvp_runbook.md`. The session-by-session changelog is archived — see
**Archive convention** below.

-----

## Latest (2026-06-14)

- **First real Affinity hand-trace ingested (satellite trace round-trip).** The
  user traced/refined in **Affinity Designer** and dropped the edited SVG at
  `brain/import/trace_upload/aop_satellite_trace.svg`. Hardened
  `mvp/scripts/import_illustrator_trace.py` for Affinity's export (metadata-frame
  fallback, wrapper-`<g>` name inheritance + transform compose, `serif:id` layer
  match, leading-trail-number provenance match, `<n> name` label-doubling strip,
  stray-circle sweep). **Ingested + verified by observation:**
  `website/data/aop_trail_network.geojson` = **130** trails (120 gold-provenance
  carried incl. 8 renamed→clean-name, **10** new user-traced needing names),
  `aop_waypoints_traced.geojson` = **26** named POIs (RV sites, cabins, entrances,
  comp pad, racetrack…), `aop_buildings_traced.geojson` = **6** (Front Office moved
  + Shower House new). Live viewer ingests all 130, clean un-doubled labels, **0
  fatal console errors** (`brain/output/verify_ingest_viewer.py` PASS); overlay
  `brain/output/illustrator_trace/_verify_ingest{,_camp}.png`. Trail 67 split per
  the user (short=67 gold, long=blank/unknown). Re-import is read-modify-write on the
  gold file → run once from the committed baseline. **Then wired into the read viewer**
  (user "not seeing it in the map"): the SW precaches data + only refreshes on a
  `VERSION` bump, and the waypoints had no layer — so added an `aop-waypoints`
  circle+label layer in `viewer_core.js` (reads `aop_waypoints_traced.geojson`,
  precached in `sw.js`), merged **Shower House** into the wired `aop_buildings.geojson`
  (merge, not swap — keeps the 5 existing buildings' FEMA provenance), and bumped
  `v83`→`v84` (`sw.js` + `index.html`). Verified on `:8001`
  (`brain/output/verify_waypoints_layer.py` PASS — 26/26 waypoints render, Shower
  House present, 0 fatal errors; `node --check` clean). **Then building name labels**
  (user: facilities "need labels … maybe a pin on top"): derived `aop-facilities`
  point source from the 4 facility-building centroids → rust `aop-facility-pin` +
  `aop-facility-labels` (allow-overlap) for Front Office/Farmhouse/Pavilion/Shower
  House; private houses stay presence-boxes. `v85`→`v86`. Verified `:8001` (4/4 pins +
  names, 0 errors). **Owed:** name the 10 new trails; richer POI-tab integration
  (blurbs/icons/search) for the waypoints; apply Front Office's refined footprint;
  camp area is getting dense (26 waypoints + 4 facility pins) → may want zoom-gated
  declutter later. Card:
  `tasks/14_illustrator_trace/satellite_illustrator_export.md`. **Git (observed): the
  user committed all the code** (`website/`+`mvp/`, incl. `v86`) as their own commit
  `59e4686` — `git diff HEAD -- website mvp` empty; no agent touched git. (That commit
  is subject-titled "v84" but holds v86 and commingles the trace/landcover/v83 sessions
  — the user's commit, left as-is.) Only the brain records remain uncommitted.

- **Vegetation land cover → editable SVG round-trip (NEW).** The user: *"I need the
  landcover exported to a svg so I can edit it … some polygons … manually resolved …
  single green for treecover."* Built the vegetation sibling of the satellite trace:
  `mvp/scripts/export_landcover_svg.py` writes the **dissolved canopy** (forest classes
  unioned, clearings as holes — the editable tree mass, NOT the viewer's 324 grid-render
  pieces) as named, filled, editable compound `<path>`s in a **Vegetation** layer over a
  locked **Satellite** backdrop, in the raster's own UTM-16N round-trip frame →
  `brain/output/landcover_trace/aop_landcover_trace.svg` (park, 18 polys) +
  `aop_landcover_9patch_trace.svg` (165 polys). **Reuse, not a 2nd pipeline:** extracted
  a shared `RasterFrame` (frame+backdrop+metadata) from `export_illustrator_trace.py` and
  a shared `vegetation_features()` (viewer fill/outline contract) from
  `simplify_landcover_vegetation.py` — both refactors **output-neutral** (HEAD vs
  refactored script bake byte-identical on the same inputs; the viewer geojson
  re-bakes unchanged). `import_landcover_svg.py` closes the loop (reads edited
  Vegetation back, re-bakes the viewer file via the shared contract; reads its OWN
  metadata, not the trail frame). **Verified by observation:** durable verifier
  `verify_landcover_svg_roundtrip.py` (uncommitted per git gate) → **RESULT: PASS**
  (max **Hausdorff 0.912 cm**, poly+ring parity, canopy area drift ~0%, park 523 ac /
  9-patch 6944 ac); Playwright render shows green on forest, fields/staging as bare
  satellite (`_render_park_{full,crop}.png`). **Council: all five seats clear** —
  Warden·Quartermaster·Mason·Scribe clear first pass; Witness **andon** on a
  "byte-identical" wording overclaim (a fresh trail-trace bake drifts ~2 cm — cause is
  a *concurrent session editing the input trail geojson*, NOT this refactor; proven
  HEAD==refactored) → records corrected to "output-neutral" + round-trip verifier
  added, Witness **re-review clear**. **Then: user hand-edited the 9-patch in Affinity**
  (`brain/import/trace_upload/aop_landcover_trace.svg`, 165→159 polys; Affinity strips
  the `<metadata>`+satellite, viewBox still = the raster metre grid). Built
  `mvp/scripts/build_landcover_edit_preview.py` → a self-contained lightweight page
  (`brain/output/landcover_trace/landcover_edit_preview.html`, served `:8002`) that
  re-attaches the satellite and overlays the edited shapes (zoom/pan, sat + fill/outline
  + opacity toggles); verified by observation, 0 console errors
  (`_preview_{default,outline,zoom}.png`). **Then (user: "test it in a map, no opacity/
  borders, light sage; high-vertex broke rendering before; test separately then
  integrate"):** built `mvp/scripts/build_landcover_map_test.py` → a standalone MapLibre
  page (`landcover_map_test.html`, `:8003`) flipping **RAW** (159 shapes incl. one
  3969-vert monster) vs **SUBDIVIDED** (317 grid pieces via `vegetation_features`), solid
  light sage `#cfdabf`, no border, no opacity. **Verified `:8003`, 0 errors:** subdivided
  renders the full canopy clean; **the raw monster also rendered fully** (overview/z13/z14/
  corners — the old bug did NOT reproduce in this isolated single-layer test). **Recommend
  shipping SUBDIVIDED regardless** (proven/de-risked). Council-cleared 4 seats (Witness ·
  Warden · Mason · Quartermaster). **Owed: the actual viewer re-bake** via
  `import_landcover_svg.py` — recover the stripped 9-patch frame (share `recover_frame`,
  don't duplicate — Quartermaster), bake `aop_landcover_9patch.geojson`, bump version.
  Card: `tasks/01_mvp/_done/landcover_layer.md` ("vegetation → editable SVG round-trip");
  search-map routed. **No `.council-cleared`** (working tree still commingled with the
  concurrent illustrator-trace / waypoints changes). UNCOMMITTED (user's git gate).
- **v83 — five-item viewer review (concurrent session; coord claim
  `handoff/coord/five-item-review.md`).** The user listed five fixes; all shipped and
  **verified by observation** on `:8001` (fresh SW-cold context, 0 console errors):
  (1) **Trail labels number-first** — `aop-trail-network-labels` `text-field` now reads
  `"N Name"` for a known-name trail (`1 Launchpad`), the bare number when unnamed (`15`),
  name-only for the rare unnumbered trail; AOP labels by number. (2) **POI/search
  selection persists** — the highlight pulse now SETTLES to a steady visible state and
  holds on the selected feature until the next selection re-pulses (was: 2.6 s pulse then
  hide, and a trail's backing layer can be off in the active preset → nothing remained;
  the user: "they highlight … but do not persist"). (3) **3D orientation locked** —
  `touchPitch.disable()` + `dragRotate.disable()` (plus the existing
  `touchZoomRotate.disableRotation()`) so stray fingers can't tilt/spin the 3D map
  ("maybe it's my fingers"); pan + pinch/scroll zoom unchanged; the `3D` button still eases
  to pitch 60 (verified). (4) **Park no-tree base = `#e7ddc4`** — the warm tan Topo/Trace
  already share, per "update park to have this as the no tree cover color" (initial bg +
  Park preset; Satellite keeps `#efe7d5`). (5) **Vegetation corners** — the v81 complexity
  cap did NOT hold (the 3976-vert/47-hole single fill polygon still degenerated → whole
  9-patch rendered as a central blob). Real fix: `simplify_landcover_vegetation.py` now
  **grid-subdivides** the canopy into ~550 m cells for the fill (9-patch 1 giant → **324
  pieces, worst 202 verts**; park unchanged) and emits the edge as a separate **LineString**
  outline; fill layers filter to `geometry-type=Polygon`, `-outline` layers to `LineString`
  (`viewer_core.js` + `main.js`). Both data files regenerated from the 5class cache. Now
  renders in **all 4 quadrants / 354 features across the AOI** (`brain/output/v5_region.png`).
  `playwright_verify_landcover.py` updated to the new contract → **23 PASS** (also fixed two
  pre-existing Map-serialization hangs in it). `sw.js`/`#appVersion` **v82→v83**. **One
  fork to flag for the user:** item 4 reads "this" as the Topo/Trace base `#e7ddc4` — trivial
  to flip if a different no-tree tone was meant. Cards: `tasks/01_mvp/_done/landcover_layer.md`
  (corner fix part 2), `research/viewer.md` (labels/persist/3D/base/landcover). **No
  `.council-cleared`** (tree commingled with the illustrator session). UNCOMMITTED (git gate).
- **Satellite 9-patch → Illustrator hand-trace export + round-trip (NEW).** The
  user: *"export the satellite map 9 patch for illustrator hand tracing — include
  gold trails / waypoints / buildings … the names need to be the layer names …
  on re-import we use those."* Built the satellite/Illustrator sibling of the
  paper-map extraction: `mvp/scripts/export_illustrator_trace.py` writes a 4-layer
  SVG (`brain/output/illustrator_trace/aop_satellite_trace.svg`, 9.2 MB; backdrop
  `satellite_9patch.jpg`) — **Satellite** (locked NAIP 2023 ortho) + **Buildings**
  (5) + **Waypoints** (5) + **Gold Trails** (120, colour=difficulty). **Each feature
  is ONE named geometry object** (`<path>`/`<circle>`, no wrapper group, NO drawn
  text — the user's correction: "the Front office should be a polygon named as an
  object name not a physical document object") carrying the name in all editor
  channels (Illustrator `_xHH_` `id`, `inkscape:label`, `serif:id`, `<title>`).
  Frame = the raster's own **UTM 16N** grid
  (vectors land 1:1 on imagery, no resampling; lng/lat→UTM via a self-contained
  TM series — no GDAL/pyproj/Docker on this box). `mvp/scripts/import_illustrator_trace.py`
  reads it back (default → `aop_trail_network.geojson`; `--all` also waypoints/
  buildings), then `export_gold_trail_network.py` re-stamps gold `_meta`.
  **Verified by observation:** projection round-trips sub-mm + doc bbox inside the
  raster; building footprints land on real rooftops (`_verify_buildings_3x.png`);
  full export→import round-trip 120/120 trails, max vertex error **0.911 cm**,
  names exact (100/120; 20 are genuinely unnamed → placeholder id), WP/bldg 5/5.
  Card: `tasks/14_illustrator_trace/satellite_illustrator_export.md`; search-map
  routed. **Next: the user edits in Illustrator, then we re-import** (the importer
  is self-round-trip-verified but its real test is the first Illustrator-saved
  SVG). **Council-cleared twice** (Witness · Quartermaster · Mason; receipt
  `brain/output/council/illustrator_trace_export.md`). Round 1: Mason andon — the
  importer rebuilt trail props from 5 keys, dropping gold provenance; **fixed** by
  embedding `data-fid` and re-merging the full prior gold props by id→name (120/120
  keep `maturity=gold`). Round 2 (after the user's no-text correction): re-cleared
  by Witness + Mason — SVG now has **0 `<text>` objects**, each feature one named
  `<path>`/`<circle>` (no wrapper groups); round-trip still 120/120 @ 0.91 cm.
  **Warden andon, NOT on this work:** the working tree is commingled with a
  **concurrent session's** unreviewed changes — `website/js/viewer_core.js`,
  `main.js`, `index.html`, `sw.js`, `aop_landcover*.geojson`,
  `simplify_landcover_vegetation.py` + `obs5_*`/`v5_*`/`observe_five.py`
  ("five-item review"). The coord board has no claim posted for it. My 6 paths are
  on-farm + gate-clean (served gold byte-identical to HEAD; importer never run on
  real data). **No `.council-cleared` marker written** — its hash spans all of
  `website/`+`mvp/`, so it would falsely certify the other session's code; the Stop
  hook will keep nudging until the trees are separated/reviewed or committed.
  UNCOMMITTED (user's git gate).
- **Task-tree sweep (card hygiene, no code).** Reviewed every numbered-sprint root
  card. **Sprint 13 (viewer extraction) closed:** all 9 slice cards were `[x]` done +
  verified but had never moved — created `tasks/13_viewer_extraction/_done/` and moved
  them in; the slate-complete status is recorded in that sprint's `_readme.md`; the one
  future item (on-tester edit FAB) was extracted to `tasks/20_deferred/tester_edit_fab.md`.
  **`gold_slice6_backlog.md` closed:** its done bulk moved to
  `tasks/06_going_gold/_done/`, its four still-open items (G_D destructive parity, G_B
  finding 5, GAP B, G_F) extracted to `tasks/20_deferred/gold_slice6_remainder.md`.
  **`universal_feature_layer.md`** banner updated to DONE (work shipped via the eight
  Sprint-05 sub-cards; kept at root for its inbound links incl. the northstar). Done
  spine cards the brain deliberately keeps at root (`gold_migration.md`,
  `08_data_normalization/star_driven_poi_normalization.md`,
  `09_editor_maturity/editor_completeness.md` + the two `shadow_*` cards,
  `11_client_convergence/client_layer_registry.md`) were assessed + left in place (they
  already carry DONE/status banners; their held remainders are tracked elsewhere).
  `06_going_gold/schema_conformance_audit.md` is genuinely **unstarted** (Sprint 06's
  guardrail slate) → left as open sprint work. `03_event_app/misc_3.md` left active per
  the user's standing request. No code/version touched; nothing committed.

The prior thrust is **extracting the read viewer into a standalone shell**
(`website/viewer_core.js` + `viewer.css`, served as `SHELL_ASSETS`/SWR) and
re-attaching the pieces that were severed in the split. Most recent landings,
all **UNCOMMITTED** (user's git gate):

- **v82 — Locate: keep "as the bird flies" + drive time back, and hide the FAB
  without GPS.** The user kept the on-theme bird framing (Rock Warblers) and reversed
  the v81 drop: the off-park card is now two lines — *"&lt;dist&gt; away, as the bird
  flies"* + *"about a &lt;t&gt; drive"* (`fmtDrive` restored). And the Locate FAB now
  **ships hidden** (`index.html` `hidden` + `.locate-fab[hidden]{display:none}`),
  revealed by `viewer_core.js` only inside `if (locateBtn && navigator.geolocation)` —
  no geolocation API → no button (the unreachable `!navigator.geolocation` click branch
  was removed). Verified by observation (`verify_locate_travel.py`, now 5 cases incl.
  **no-geolocation → FAB hidden**; 4 runs PASS, 0 real errors; screenshots add
  `locate_travel_nogps.png`). `sw.js`/`#appVersion` v81→v82. **Council cleared (Witness ·
  Warden · Mason, first pass; receipts `brain/output/council/v82_locate_gps_gate.md`).**
  Working tree = exactly this locate diff (landcover landed in the user's v81 commit), so
  `.claude/.council-cleared` written. UNCOMMITTED (user's git gate). *(User self-committed
  v80 `cdcc918`, v81 `692464b`.)* **Then (same undeployed v82) the notice was moved to the
  LEFT of the FAB** per the user (`.locate-notice` `right:12→80px; bottom:84→18px`,
  CSS-only); Witness-cleared at reduced tier, verified at 1200px + 390px (left of FAB,
  on-screen, no overlap); marker re-written.
- **v81 — Locate copy = bird-flies miles, drop drive time, and a VISIBLE failure
  path.** Testing v80 on the phone (confirmed on v80), the user saw nothing off-park.
  Root cause wasn't cache: the v80 high-accuracy read hit the error path on a
  slow/blocked phone GPS and fell back to a *silent* `geolocate.trigger()` (no-op
  off-park) — dead button again. Fix (`viewer_core.js` only): far notice now reads
  *"You're &lt;dist&gt; away / from the park, as the bird flies"* (drive-time estimate
  removed); a denied/failed fix now SHOWS *"Couldn't get your location / Turn on
  Location access and try again"* instead of no-op'ing; and the branch read is coarse +
  fast (`enableHighAccuracy:false`) so it doesn't stall on a GPS lock (the on-site dot
  still uses the control's high accuracy). Verified by observation
  (`verify_locate_travel.py`, now 4 cases incl. revoked-permission; screenshots add
  `locate_travel_denied.png`). `sw.js`/`#appVersion` v80→v81. Card addendum (same
  card, now under `_done/`). **Council cleared (Witness · Warden · Mason; receipts
  `brain/output/council/v81_locate_followup.md`).** The Witness pulled one andon — not
  on the feature but on an over-stated stability claim; the *verifier harness* was
  hardened (nav-retry + gl/transient/real noise classifier), re-run reproducibly clean
  (10/10 + 5/5, 0 real errors), and re-reviewed → clear. UNCOMMITTED (user's git gate).
- **v80 — off-park Locate now shows travel-to-park, not a dead button.** The user:
  "the blue button does nothing if you are not on the park." Right — the camera is
  leashed to the printed sheet (`maxBounds`), so a real GPS fix from home lands
  outside bounds and the blue dot can't show. The Locate FAB now reads the fix once
  and branches on haversine distance to the park anchor: ≤3 mi → the normal blue-dot
  flow (unchanged); >3 mi → a small blue notice above the FAB, *"&lt;dist&gt; to the
  park — about a &lt;drive&gt; drive — your live dot shows on-site"*. Estimate is
  **offline-only** (great-circle ×1.2 ÷ 32/55 mph; no routing key, per the offline-first
  northstar). `TESTER_ANCHOR` renamed `PARK_ANCHOR` (one constant for both the tester
  shim and the distance check). 3 files: `viewer_core.js` handler + `viewer.css`
  `.locate-notice` + one `index.html` el. Verified by observation
  (`brain/output/verify_locate_travel.py`, Playwright :8001 spoofed geolocation,
  3/3 PASS, 0 errors; screenshots `locate_travel_{chattanooga,nashville,atpark}.png`).
  `sw.js`/`#appVersion` v79→v80. Card addendum:
  `tasks/13_viewer_extraction/_done/viewer_locate_install_version.md`. **Council cleared
  (core three; receipts `brain/output/council/v80_locate_travel.md`).** **COMMITTED by
  the user** as `cdcc918 v80` ("wanted to see it in the remote") — the user's own git
  gate; no agent touched git.
- **Ground cover simplified to one vegetation layer (data mutation).** The
  user's call: combine the two forest greens into a single `vegetation` layer
  and let every non-tree area read as the base map paper.
  `mvp/scripts/simplify_landcover_vegetation.py` dissolves the two forest
  classes (shapely unary union) and drops the three open classes; wired as the
  final step of `build_landcover.sh` / `build_landcover_9patch.sh` with the
  5-class export kept in the gitignored cache. Park 154→18 features, 9-patch
  3430→165; `viewer_core.js` land-cover paint collapsed from a 5-class `match`
  to a flat vegetation green per preset (`main.js`/`panel.js` editor host still
  carry the old `match`, falls through to the same green — cleanup owed on
  editor port). `playwright_verify_landcover.py` updated to the vegetation
  contract: single class, retired sub-classes gone, flat green, base-of-stack,
  18/165 render. **Committed by the user as `da5d032 v79`.** Council reviewed
  (Witness·Warden·Quartermaster·Mason clear; Scribe andon → records corrected).
  **Then a real render bug surfaced:** the user saw empty TR/BR/BL corners + zoom
  "pop" where the satellite shows dense trees. Cause: the `unary_union` dissolve
  merged the canopy into one ~28k-vertex/282-hole polygon and MapLibre's fill
  tessellation dropped chunks (forest area WAS present in all quadrants — it just
  wasn't drawn). **Fixed (data only):** the simplify script now caps per-polygon
  complexity — drop interior holes <~5000 m² (`HOLE_MIN_DEG2`) + light DP simplify
  (`SIMPLIFY_DEG` ~3 m) → max 3976 verts/47 holes (was 28107/282), 187/0 for the
  park, coverage ±0.1%, natural edge kept so the outline still works (no viewer
  change). Verified by observation (fresh render agent: corners fill, one
  continuous canopy, stable across zoom, 0 console errors;
  `brain/output/veg_fixed_*.png` vs `diag_veg_*.png`; receipt
  `brain/output/council/witness_vegetation_render.md`). **Committed as
  `692464b v81`** (HEAD carries the 3976/47 data; `sw.js`/`#appVersion` now v82).
  Card `tasks/01_mvp/_done/landcover_layer.md` (two addenda); `research/viewer.md`
  updated.
- **v79 — all event copy rewritten from `brain/import/TBI.copy`** (the event lead's
  real copy). Council-cleared at v78 (core three: witness·warden·quartermaster, all
  `clear`; receipts in `brain/output/council/*_tbi_copy.md`); v79 is the one
  follow-up word the user chose — The Crew's Rock Warbler call is now "caw-craaawl!"
  (Steward tier: copy-only, re-cleared at Tier-0). Closes the
  long-deferred content audit
  (`tasks/20_deferred/_done/rock_warblers_content_audit.md`). About tab
  (`aop_about.json`): new intro, five real reference items (Mandatory skills = "Good
  attitude"; Rigs +2.2″ +"No bashers"; park/map/crew rewritten), placeholder
  Format/Trail-buddies/Night-crawl dropped, and a **new Driver's Meeting prose
  section** (welcome script + weekend rules — small `renderAbout` add in
  `viewer_core.js` + `info-subhead`/`info-rules` CSS in `viewer.css`). Schedule
  (`aop_event_schedule.json`): real 18-session Fri/Sat/Sun timetable, `status:
  live`; **fork decision — keep the pavilion pin, drop the rest** (only `#pavilion`
  has coordinates; `#trails`/`#camping-field` are named but coordinate-less → no
  fabricated pins). Stale provenance copy fixed (map attribution + editor `<small>`
  no longer says "proposed / sister-event"). Registry flipped About + schedule
  `proposed → live`. Verified by observation (`brain/output/verify_tbi_copy.py`
  30/30; About DOM + GL-independent `eventScheduleToGeojson` transform; Events
  screenshot shows live calendar + "Gates open in 5d 15h"; `tbi_about.png`,
  `tbi_events.png`). `#appVersion` + `sw.js` v76→v79. **UNCOMMITTED** (user's git
  gate). Owed: the 600-acre parcel reconcile (the Rock Warbler call is now filled).
- **v76 — index opens at park zoom and holds; no on-load jump.** The user reversed
  the earlier "it needs to stay": removed the on-load park → region → park reveal
  animation (the self-contained `autoPeek` / `schedulePeek` / `killPeek` block in
  `website/js/viewer_band.js`, committed `c157acc v75`). The council Witness then
  caught a **second, pre-existing** jump: `viewer_core.js` built the map at `zoom: 12`
  (clamped to ~12.5 by the band's maxBounds), held that region-wide view ~4.4 s, then
  snapped to park z14 when data loaded. Fixed at the source — construct at `zoom: 14`
  (center was already park). The verifier's racy `>12.5` sample gate (which flapped
  PASS/FAIL) was rewritten to sample from t=0 with no gate. Verified by observation
  (`:8001`, `brain/output/verify_no_load_peek.py`): 5/5 runs open at z14, span 0,
  deterministic; 3/3 PASS; band still renders (38 layers), 0 console errors.
  `#appVersion` + `sw.js` `VERSION` v74→v75. **The peek removal + version bump are
  COMMITTED** as `c157acc v75` (user committed mid-task). A follow-up pass then
  **retired the now-spent band proof scaffolding** (unreferenced by the shipped viewer):
  `rm`'d `viewer_banded.html`, `viewer_banded_compare.html`, `css/viewer_band.css`, and
  cleaned the one dangling `viewer_core.js` comment that named the proof page — this
  clears the long-standing "retire the spent scaffolding" owed item. Because the
  `viewer_core.js` comment touch is a precached shell asset, `#appVersion` + `sw.js`
  `VERSION` advance **v75 → v76** (comment-only delta; satisfies the shell-asset → bump
  discipline). Those deletions + the comment fix + the v76 bump + this card/handoff
  update are **UNCOMMITTED** (user's git gate). Card addendum on
  `tasks/13_viewer_extraction/_done/viewer_band_merge.md`.
- **Schedule loading spinner + single-number search review.** Card:
  `tasks/13_viewer_extraction/_done/viewer_schedule_loading.md`. (1) The Events tab's bare
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
  `tasks/13_viewer_extraction/_done/viewer_drawer_schedule.md`.
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
  presets PASS). Card: `tasks/13_viewer_extraction/_done/viewer_band_merge.md`. Council
  reviewed on the diff. **Owed (user's gate):** the commit. (The spent scaffolding —
  `viewer_banded.html`, `viewer_banded_compare.html`, `css/viewer_band.css` — was retired
  2026-06-14; see the v75 entry above.)
- **v70 — left-rail drawer open/close now persists.** `aop_left_rail_drawer_v1`
  stores `{search,hot,cal}` booleans, read on init / written on each tab click in
  `viewer_core.js`; clipboard drawer height (`aop_lr_card_height_v1`) verified
  end-to-end. 18/18 Playwright PASS (`verify_drawer_persist.py`), 0 errors. Card
  addendum on `tasks/13_viewer_extraction/_done/viewer_drawer_schedule.md`. Council not
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
