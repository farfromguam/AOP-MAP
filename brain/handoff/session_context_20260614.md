# Session changelog — 2026-06-14

Archived from `session_context.md` at the 2026-06-14 session end. The durable
record for each feature lives in its `tasks/*/_done/<feature>.md` build card,
`research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`. Read this only
to retrace why something was built. Covers the v71→v88 stretch plus the
2026-06-14 trace / landcover / six-item work.

-----

## 2026-06-14 landings

- **Six-item viewer batch (v87) — shipped + verified.** One user drop: (1) trail
  number-first **display name** as a single source — `trailDisplayName()` stamps
  `display_name` on each trail at load; the map label AND search now both read
  "1 Launchpad" (was a label-only concat; name/number stay separate so the trace
  re-import round-trips). (2) **Borderless tree cover** — removed both landcover
  `-outline` layers + refs + unused consts; solid fill (opacity 1). (3) **Medallion
  data tiers** — re-tiered every served file via `stamp_maturity.py` (now bronze/
  silver/gold; delete kept as a lifecycle flag) + new `set_feature_maturity.py`
  (per-feature: Ellis→gold, others bronze; 5 buildings→gold, Shower House→bronze);
  gold=9 silver=2 bronze=11 delete=3. Decisions (asked): **full rename**, and
  **derived/reference layers that render in production = gold**. (4) **Production
  data-tier alert** — `auditProductionTiers()` console.warns on bronze/silver in
  production (Shower House, callouts, publish), never hides ([[no-limiting-code-mvp]]).
  (5) **One persistent active item** — search de-thrones an active event row; the
  selection (search or event) stays highlighted until the next pick (popup-close no
  longer clears it). (6) **Pro-Line at the firepit** — `sat-proline-fire`
  `location_tag`→`#firepit` + baked `#firepit` location; Firepit waypoint tagged.
  **Verified by observation** `:8001`: `brain/output/verify_label_border_persist_firepit.py`
  13/13 + `verify_production_tier_alert.py` PASS, 0 console errors; screenshot
  `verify_treecover_borderless.png`. Card:
  `tasks/02_edit/_done/six_item_viewer_batch_20260614.md`. **Owed:** editor
  (`panel.js`) medallion re-group (chip learns bronze; tree layout deferred).

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
  — the user's commit, left as-is.)

- **Vegetation land cover → editable SVG round-trip → integrated tree cover.** The
  user: *"I need the landcover exported to a svg so I can edit it … single green for
  treecover."* Built the vegetation sibling of the satellite trace:
  `mvp/scripts/export_landcover_svg.py` writes the **dissolved canopy** (forest classes
  unioned, clearings as holes) as named editable compound `<path>`s in a **Vegetation**
  layer over the satellite, in the raster's own UTM-16N round-trip frame. **Reuse, not a
  2nd pipeline:** extracted a shared `RasterFrame` from `export_illustrator_trace.py` and
  a shared `vegetation_features()` from `simplify_landcover_vegetation.py` — both
  refactors **output-neutral** (HEAD vs refactored bake byte-identical).
  `import_landcover_svg.py` closes the loop; durable verifier
  `verify_landcover_svg_roundtrip.py` → PASS (max Hausdorff 0.912 cm, area drift ~0%).
  Then a self-contained preview (`build_landcover_edit_preview.py`, `:8002`) and a
  standalone MapLibre raw-vs-subdivided render test (`build_landcover_map_test.py`,
  `:8003`) — the high-vertex 3969-vert monster rendered fine isolated, but shipped the
  **subdivided** form (proven/de-risked). **Then integrated** (user "ship the subdivided
  form, make the green `#D1D2B8`"): `import_landcover_svg.py … --target 9patch` recovered
  the Affinity-stripped frame (shared `recover_frame`) and re-baked
  `aop_landcover_9patch.geojson` = **318 features** (317 fill + 1 outline, hand-resolved
  165→159 polys); `viewer_core.js` recolored `#D1D2B8`. **Then opacity** (user "no
  opacity" → solid `v86→v87`; then "slight on the non-park, no border, make mockups" →
  built an interactive chooser `brain/output/landcover_trace/mockups/compare.html` at
  `:8005`, found the **opacity-seam → `fill-antialias:false`** fix). **Final (user "60%"):**
  non-park `landcover-9patch-forest` fill-opacity **0.6**, park `landcover-forest` **1
  (solid)**, `fill-antialias:false` on both, `landcover9Opacity` slider 60, **v87→v88**.
  Verified `:8001`: non-park 0.6 / park 1 / antialias false / `#D1D2B8`, opacity step
  separates park from context, no seams, 0 errors. Council-cleared across every step;
  **`.council-cleared` written** once the user committed the concurrent work (HEAD
  `91a017e`) and the tree decommingled. Card: `tasks/01_mvp/_done/landcover_layer.md`
  (multiple addenda); search-map routed.

- **v83 — five-item viewer review (concurrent session).** All five shipped + verified
  on `:8001`: (1) trail labels number-first; (2) POI/search selection persists (pulse
  settles + holds); (3) 3D orientation locked (`touchPitch`/`dragRotate` disabled);
  (4) Park no-tree base `#e7ddc4`; (5) vegetation corners — the v81 cap didn't hold, real
  fix is `simplify_landcover_vegetation.py` **grid-subdivides** the canopy into ~550 m
  cells (9-patch → 324 pieces) + LineString outline, fill filters Polygon / outline
  filters LineString. `playwright_verify_landcover.py` → 23 PASS. `v82→v83`. Cards:
  `tasks/01_mvp/_done/landcover_layer.md`, `research/viewer.md`.

- **Satellite 9-patch → Illustrator hand-trace export + round-trip.** The user:
  *"export the satellite map 9 patch for illustrator hand tracing … the names need to be
  the layer names."* `mvp/scripts/export_illustrator_trace.py` writes a 4-layer SVG
  (Satellite + Buildings 5 + Waypoints 5 + Gold Trails 120, colour=difficulty); each
  feature is ONE named geometry object (no wrapper group, no drawn text), name in all
  editor channels. Frame = the raster's own UTM 16N grid (self-contained TM series, no
  GDAL/pyproj/Docker). `import_illustrator_trace.py` reads it back; `export_gold_trail_network.py`
  re-stamps gold `_meta`. Verified: projection round-trips sub-mm; round-trip 120/120
  trails @ max 0.911 cm; WP/bldg 5/5. **Council-cleared twice** (Witness · Quartermaster
  · Mason; receipt `brain/output/council/illustrator_trace_export.md`) — round 1 Mason
  andon (importer dropped gold provenance → fixed by `data-fid` re-merge); round 2 after
  the user's no-text correction (0 `<text>` objects). Card:
  `tasks/14_illustrator_trace/satellite_illustrator_export.md`.

- **Task-tree sweep (card hygiene, no code).** Sprint 13 (viewer extraction) closed —
  9 slice cards moved to `tasks/13_viewer_extraction/_done/`; on-tester edit FAB
  extracted to `tasks/20_deferred/tester_edit_fab.md`. `gold_slice6_backlog.md` closed
  (done bulk → `tasks/06_going_gold/_done/`, four open items →
  `tasks/20_deferred/gold_slice6_remainder.md`). `universal_feature_layer.md` banner →
  DONE. `06_going_gold/schema_conformance_audit.md` left as open sprint work;
  `03_event_app/misc_3.md` left active per the user.

## Viewer-extraction stretch (v69 → v82)

The thrust was **extracting the read viewer into a standalone shell**
(`website/viewer_core.js` + `viewer.css`, served as `SHELL_ASSETS`/SWR) and
re-attaching the pieces severed in the split.

- **v82 — Locate: keep "as the bird flies" + drive time, hide the FAB without GPS.**
  Off-park card two lines (*"<dist> away, as the bird flies"* + *"about a <t> drive"*,
  `fmtDrive` restored); Locate FAB ships hidden, revealed only inside
  `if (locateBtn && navigator.geolocation)`. `verify_locate_travel.py` 5 cases (incl.
  no-geolocation → FAB hidden), 0 real errors. `v81→v82`. Council cleared (Witness ·
  Warden · Mason). Then the notice moved LEFT of the FAB (CSS-only), Witness re-cleared.
- **v81 — Locate copy = bird-flies miles, drop drive time, VISIBLE failure path.**
  v80's high-accuracy read hit the error path on a slow phone GPS → silent no-op (dead
  button). Far notice now bird-flies only; a denied/failed fix SHOWS "Couldn't get your
  location…"; branch read coarse + fast (`enableHighAccuracy:false`). `v80→v81`. Council
  cleared; Witness andon on an over-stated stability claim → verifier hardened, re-cleared.
- **v80 — off-park Locate shows travel-to-park, not a dead button.** Camera leashed to
  `maxBounds`, so a home GPS fix can't show the dot; FAB now branches on haversine
  distance: ≤3 mi normal flow, >3 mi a blue notice (offline great-circle estimate, no
  routing key). `TESTER_ANCHOR`→`PARK_ANCHOR`. `v79→v80`. Council cleared. **COMMITTED
  by the user** `cdcc918 v80`.
- **Ground cover → one vegetation layer (data mutation).**
  `simplify_landcover_vegetation.py` dissolves the two forest greens, drops the open
  classes; park 154→18, 9-patch 3430→165; viewer paint collapsed to a flat green.
  **Committed `da5d032 v79`.** Then the empty-corner render bug surfaced (28k-vertex
  union dropped chunks) → complexity cap (holes <5000 m², DP simplify) → 3976 verts/47
  holes. **Committed `692464b v81`.**
- **v79 — all event copy rewritten from `brain/import/TBI.copy`.** About tab + 18-session
  schedule `status: live`; kept the pavilion pin, dropped coordinate-less rows. Council
  cleared at v78; v79 = the "caw-craaawl!" word. `v76→v79`.
- **v76 — index opens at park zoom, no on-load jump.** Removed the `autoPeek` reveal
  (committed `c157acc v75`); Witness caught a second pre-existing jump (built at zoom 12,
  snapped to 14) → construct at zoom 14. Then retired the spent band scaffolding
  (`viewer_banded*.html`, `css/viewer_band.css`). `v75→v76`.
- **Schedule loading spinner + single-number search review.** Events tab bare "Loading
  schedule…" → the designed spinner row (V2); single-number search verified identical
  old vs extracted (no change owed). Card: `viewer_schedule_loading.md`.
- **v72 — left-controls overlay no longer eats map drags.** CSS-only
  `.left-controls{pointer-events:none}` + `auto` on the visible cards. `v71→v72`.
- **v71 — off-edge band merged into the read viewer.** `viewer_band.js` (38 layers) ships
  in `index.html`; `window.AOPViewer = {map, regionBounds}` + padded camera leash;
  `raiseBand` re-floats on every `styledata`. `v70→v71`.
- **v70 — left-rail drawer open/close persists** (`aop_left_rail_drawer_v1`). 18/18 PASS.
- **v69 — tester mode = `?tester=1`** (not a `tester.html`); GPS offset wraps
  `navigator.geolocation` to pin the first fix to the pavilion while preserving movement
  delta. Rust "TESTER" chip.

**Still future:** the on-tester **edit FAB** waits on the editor porting into the
extracted read core (editor still lives in `panel.js` / `old_index.html`).
