# Session Handoff: Sprint 04 pickup

Date: 20260527

Short pointer for the next session. The durable record lives in the cards.

## Archive convention

Each session pruned out of here lands at `session_context_<YYYYMMDD>.md`:

- `session_context_202605201517.md` — original handoff shape (the template).
- `session_context_20260522.md` — work log from the 2026‑05‑20 → 2026‑05‑22 sessions (lidar contours, water, search, cemeteries, land cover, NAIP tracing, presets, panel collapse, activity hotspots, initial event schedule).
- `session_context_20260524.md` — work log for the 2026‑05‑23 → 2026‑05‑24 sessions, covering the full Sprint 02 close (Buckets A–H), schedule clock-times, calendar current-time indicator, left hot button, hot-control two-lane, branding logos, named-feature tagging, search tags, viewer chrome polish, default-layer policy, and code-health Pass 3.
- `session_context_202605241228.md` — CWC dump after Sprint 03 carryover lanes 1–5 shipped.
- `session_context_20260525.md` — left-rail manilla-tab design exploration; five HTML mockup variants checked in under `website/leftrail_v*.html`. Build card: `tasks/03_event_app/_done/left_rail_collapse_tabs.md`. No `website/index.html` changes.
- `session_context_20260527.md` — misc_4 items 1–5 shipped, plus the POI/About empty-space CSS fix and the tab-restore fix. All in the working tree (uncommitted). See `tasks/04_event_app/misc_4.md` "What shipped (2026-05-27)" block for the full close-out and the trail-lane verifier residue routed to `viewer_polish_followups.md`.

**2026-05-30 (triage) — Sprint 04 reviewed and sorted (no code).** Every card in
`tasks/04_event_app/` was assessed done / partial / not-done and moved.
**Shipped → `04_event_app/_done/`:** `calendar_group_icon_review`,
`editor_unified_tree`, `editor_three_buckets_v3c`,
`editor_unified_positioned_features`, `misc_4` (close-out header added), and a
**new split card** `bake_first_poi_serve_slice` (the shipped bake-first POI SERVE
pipeline carved out of `star_driven_poi_list` + `dev_db_snapshot_reseed`).
**Deferred → `tasks/10_deferred/`** (each got a "Deferred because" header):
`event_crud_upload_loop`, `paper_map_trail_extraction` (partial/active — flagged
it may belong on an active sprint if the edited-SVG loop continues),
`star_driven_poi_list`, `dev_db_snapshot_reseed`, `data_integrity_publishability`,
`brand_assets_and_permissions`, `calendar_placeholder_state`,
`park_bounds_icon_apply`, `rock_warblers_content_audit`, `poi_editor_followups`,
`viewer_polish_followups`. `source_layers.md` left in place (reference list, not a
card). `04_event_app/_readme.md` + `10_deferred/_readme.md` updated with the
disposition; pre-triage card list kept for history. Doc moves only, uncommitted.

**2026-05-30 (session 5g) — Locate + Install moved into left-rail float groups (V2).**
Two utility buttons that were scattered on the map chrome now stack as their own
floating groups below the calendar tab icon in `.left-controls`: **Locate** (neutral
cream 44px square, GPS-crosshair glyph) and **Install** (rust 44px square, download-to-tray
glyph). Picked V2 ("accented install") from a 4-up compare round. Implementation in
`website/index.html`: (1) new `.util-group`/`.util-btn`/`#pwaInstallBtn.util-install` CSS
matched to the `.lr-icon-col` chrome; (2) MapLibre's default top-right `GeolocateControl`
button is hidden (`.maplibregl-ctrl-top-right .maplibregl-ctrl-group{display:none}`) and
surfaced via a new `#locateBtn` that calls `geolocate.trigger()` and mirrors
`trackuserlocationstart/end`+`error` onto an `.active` (moss) state; (3) the old fixed
bottom-left `#pwaInstallBtn` + `#pwaIosHint` were relocated into `.left-controls` — the
install button *is* its own group and self-hides via the `hidden` attr until
`beforeinstallprompt` (so no empty rust card shows), single id preserved, PWA script
untouched (it's getElementById-based). Verified live (Playwright, geolocation granted):
locate visible at x13/y697 44×44 below the drawer, install rust square at y750, default
geolocate hidden, click → tracking + active state, 0 console errors. Compare round shipped
as review artifacts linked from the right panel **Comparisons** section
(`floatgroup_compare.html` + `floatgroup_v1_twins`/`v2_accent`/`v3_joined`/`v4_labeled`.html)
— retire per the `misc_4` mockup-cleanup routing once the look is locked. `website/index.html`
+ the 5 `floatgroup_*.html` mockups uncommitted.

**2026-05-30 (session 5f) — snap_trim "dangling" detector de-noised + the 3 ends verified.**
User challenged the "3 dangling ends" warning; all three verified and they were right.
`snap_trim_trails.py` had flagged any end >18 m from another feature, over-counting. Now
it classifies: **self-loops** (end rejoins its OWN line — trail "9" closes onto its own
vertex #6 at 0 m, a lollipop; not a gap), **road dead-ends** (a road that terminates in
space but joins the network at its other end — the unnamed road connects at 0 m one end,
74 m spur the other), and **trail danglers** (the real review set). Result on edited_10:
1 self-loop + 1 road dead-end + **1 true trail dangler** (unnamed trail start, 88 m from
trail 50). New `SELF_LOOP_M=2.0`; report now lists each by kind/name/gap. Served gold data
unchanged (re-run is 0 trim / 0 snap on edited_10). Minor latent bug noted: passing a
*relative* out-path trips `out.relative_to(REPO)`; default in-place run is unaffected.
`mvp/scripts/snap_trim_trails.py` uncommitted.

**2026-05-30 (session 5e) — trail search wired up.** The merged `aop-trail-network`
layer was never indexed for search, so trails were unfindable. Fixed in
`website/index.html`: (1) `indexFeatures(aopTrailNetworkData, 'trail', aopTrailNetworkToggle,
null, name→['trail <name>'])` registers every NAMED trail (number "32" or string "Riot
Hill"); unnamed edges are skipped. (2) The 2-char search floor now lets a lone digit
through (`/^\d$/`) so trails 1–9 are searchable. (3) New `searchRank()` orders matches
exact→prefix→substring, so a bare number floats the trail above building addresses that
merely contain the digit (without it, "9" buried trail 9 under "1094 Kelly Cove Road"…).
Selecting a trail flies there, flips the network layer on, pulses the highlight. Durable
coverage added to `playwright_verify_search.py` (trail-by-number, single-digit, string
name, fly+auto-enable) — PASS, no regressions. NOTE: the **20 unnamed trails** (from the
5d marker-rename fix) have no name → not searchable until the user names them in Affinity.
`website/index.html` + `mvp/scripts/playwright_verify_search.py` uncommitted.

**2026-05-29 (session 5d) — IMPORTER BUG FIXED (marker auto-renaming) + edited_10 reimported (current served).**
User: "something is renaming 32 and 58." Root cause found in `import_trace_svg.py`
`reattach_from_markers`: it stamped a nearby marker's `trail_number` onto UNNAMED
trails (then the name-fallback turned that number into the `name`). So one hand-typed
"32" became three "32"s — the #32 marker cluster sat near two unnamed neighbours — and
phantom "58"s appeared from a #58 marker on an unnamed trail the user never named.
Proof: edited_10 SVG has exactly one path named 32 and every SVG name unique, but the
importer output three 32s (sfwda-42/43 were `name=None` in the SVG). **Fix: markers no
longer assign `trail_number`/name at all — the user's typed object-name (`_editable_name`)
is the SOLE source of a trail's number/identity; markers still bootstrap DIFFICULTY for
uncoloured trails only.** Re-imported edited_10 with the fix → **0 duplicate numbers**,
32→1, 58→gone, 87 numbered / 100 named / 20 genuinely-unnamed (left for the user to name,
not auto-stamped). snap_trim 3 dangling, gold stamped, `playwright_verify_sfwda_trace.py`
PASS. This (edited_10 + fix) is the current served `aop_trail_network.geojson`,
superseding edited_11. The earlier dup find-and-fix loop (flag-red SVGs) is now moot for
auto-created dups; any remaining dups would be genuinely user-typed. `import_trace_svg.py`
+ `website/data/` uncommitted.

**2026-05-29 (session 5c) — edited_11 imported + dup find-and-fix (superseded by 5d).**
Pipeline `import → snap_trim → export_gold_trail_network --from …edited_11.svg`: 120
feats, 91 numbered, 0 grey (Easy 30 / Mod 42 / Diff 44 / Road 4). Verifier PASS.
Duplicate-number QA loop with the user: I flag duplicate-number trails RED in a
throwaway working copy → `export_trace_svg.py --color feature` → editable SVG
`aop_trail_network_2025_dupflag_edit.svg` (gold geojson left untouched; temp file
deleted after export). edited_11 cleared dups **1/47/90** (green 47→42, added 97) but
**28, 32(×3), 55 still duplicated** (55 is new — a 56 was renamed to an already-used
55). Also colour-vs-marker mismatches open: 35/95/97 green but markers moderate; 28(×2)
& one 32 colored black but markers moderate (markers = sheet symbols, stronger than the
number-band guess). Re-flagged SVG regenerated for the next pass. CAVEAT logged for the
user: don't leave any stroke red on re-export — red's nearest import anchor is orange,
so a leftover red imports as a *road*; recolour each to its real difficulty.

**2026-05-29 (session 5b) — edited_9 imported.** Same pipeline; identical aggregate
shape (120 / 94 numbered / 0 grey), diff geometric — 4 trails repositioned (11, 34, 47,
Pretender). Verifier PASS. Superseded by edited_11.

**2026-05-29 (session 5) — edited_8 imported + gold-export script.** Imported
`aop_trail_network_2025_edited_8.svg` (120 trails, osm merged into the one
`traced_trails` layer) → `website/data/aop_trail_network.geojson`: 120 edges, 94
numbered, 103 named, **0 grey** (Easy 30 / Moderate 46 / Difficult 40 / Road 4).
`snap_trim_trails.py` fixed 1 overshoot + 1 gap, 3 dangling >18 m left for review.
New **`mvp/scripts/export_gold_trail_network.py`** makes the "gold" step
reproducible: it rewrites only `_meta` (crs, colour legend, difficulty band, counts,
schema, auto-computed band-vs-colour `review_flags`) so the served file is the
self-contained gold the static viewer loads directly on a new install (no DB /
pipeline / localStorage). Run order: `import_trace_svg.py <svg>` →
`snap_trim_trails.py` → `export_gold_trail_network.py --from <svg>`. Verified: bbox
inside envelope, 0 degenerate, `playwright_verify_sfwda_trace.py` PASS. Review flags
this run: trails 35, 1, 95, 47 (colour vs number-band disagreements). Details in
`tasks/04_event_app/paper_map_trail_extraction.md` "edited_8 imported" block. All
`website/data/` + `mvp/scripts/` uncommitted.

**2026-05-29 (session 4) — string trail names + difficulty colours + snap/trim
(golden-data prep).** The merged network dropped `JW2`/`JW20` and other **named**
trails because the round-trip treated name as an integer. Fixed in
`import_trace_svg.py` (`_editable_name`: serif:id → inkscape:label → id; import
every name except `?`; non-numeric names locked) + `export_trace_svg.py` (writes
the name to both `inkscape:label` and `serif:id`). Re-import → 119 trails, 104
named, all 9 non-numeric names land (Area 51, GWT, JW1–4, JW20, Pretender, Riot
Hill). Colours switched from per-trail rainbow to **green/blue/black by difficulty**
(`assign_difficulty` band fallback; 22 grey unknowns flagged). New
`mvp/scripts/snap_trim_trails.py` cleans topology — 31 overshoots trimmed, 48 gaps
snapped, 3 dangling left for review. Re-exported the stack over the 2025 backdrop:
`brain/output/paper_trace/aop_trail_network_2025_edit.svg` (difficulty colours,
names on editable channels) — **this is the artifact for the user's review/edit pass
→ re-import = golden data.** `playwright_verify_sfwda_trace.py` PASS; overlay
`brain/output/net_2025_difficulty_overlay.png`. Details in
`tasks/04_event_app/paper_map_trail_extraction.md` "String trail names…" block. All
`website/data/` + `mvp/scripts/` + `website/index.html` uncommitted.

**2026-05-29 (session 3) — paper-map trail extraction PROTOTYPE.** New card
`tasks/04_event_app/paper_map_trail_extraction.md`. User goal: the SFWDA 2015
paper map is the only surviving record of trails the prior owner lost; extract
them cleanly. User corrected my framing — the sheet was **printed from a mapping
system, so it is positionally accurate once the (already-correct) warp is applied**;
"high for shape, low for current trails" was about 2015 *vintage*, not precision.
Built three `mvp/scripts/` scripts (need `numpy opencv-python-headless pillow
scikit-image shapely`, pip'd into the global Python): `extract_paper_trails.py`
(124 markers — 40 green Easy / 42 blue Moderate / 42 black-triangle Difficult;
triangles solved via close+OPEN since they fuse to the trail lines + trail-line
isolation), `paper_trace_warp.py` (`PaperWarp` exactly replicates the viewer's
270°-rotate + 6×6 bilinear mesh — corner self-check passes), `vectorize_paper_trails.py`
(skeletonize → graph walk → DP simplify → warp = 382 edges/1521 vertices, 116/124
markers matched). Outputs in `brain/output/paper_trace/` (scratch): `sfwda_markers.geojson`,
`sfwda_trails.geojson`, debug overlays. Verified by observation (overlays) + georef
self-check + bbox-inside-envelope. Per user ("load the data in the app to review,
refine after"), wired into `website/index.html` as two default-OFF, in-no-preset
review layers (`sfwda-trace-trails` + `sfwda-trace-markers`, toggles under External
reference) with data copied to `website/data/sfwda_traced_{trails,markers}.geojson`;
verifier `mvp/scripts/playwright_verify_sfwda_trace.py` PASS (512 features, survives
preset switch, 0 console errors). Visual: Trace preset + SFWDA raster + traced trails
shows the trace landing on the paper-map ink (`brain/output/sfwda_trace_review_traceonly.png`).
Open (refine pass): trail-number OCR (deferred, no higher-res scan), boundary-split,
camping-icon false positives, junction topology. `website/index.html` +
`website/data/` changes are UNCOMMITTED.

**2026-05-29 (session 2) — bake-first POI slice SHIPPED.** Acting on the
push-order decision (bake first; one `publish.geojson`), the SERVE half of the
star-driven pipeline now runs end-to-end: new `core.pois` table + `publish.pois`
gate in `mvp/init_db.sql`, `export_publish_geojson.sh` UNION extended with a
`layer='poi'` branch, idempotent `mvp/scripts/seed_core_pois.sql` (Pavilion +
Ellis Cemetery publish; a Proving-Grounds candidate left unpublished to prove
the gate excludes it — `core.pois`=3 rows, `publish.pois`=2), and `index.html`
renders the baked set as a `published_destinations` POI-tab group + `publish-pois`
map layer. Verifier `mvp/scripts/playwright_verify_baked_pois.py` PASS; adjacent
verifiers show only documented pre-existing fails. Authoring surface still NOT
chosen (fork open); legacy `buildPoiGroups()` scaffolding still renders alongside.
Full close-out + deferred items in `tasks/04_event_app/star_driven_poi_list.md`
"Bake-first slice — SHIPPED" block. All uncommitted.

**2026-05-29 — star-driven POI list: pipeline design (no code).** New card
`tasks/04_event_app/star_driven_poi_list.md`. Reviewed how the right-rail ★
Visitor list maps to the left POI tab; they're two lists built two ways and
only coincide for drawn POIs. Locked principle: **★ is the one curation gate;
the starred set _is_ the POI list** (all destination layers starrable, tab
starts empty, brand logos leave the ★ axis). User rejected designing against
the current files — the seed/index/localStorage stores are prototype
scaffolding. Target is **one pipeline: author → save to PostGIS → bake to file
→ static viewer serves the baked file** (= the northstar spine + source_register
`raw→core→publish`). The ★ collapses to one DB attribute + a publish-zone view;
the seed-vs-index file question is void. Gap: nothing wires the web editor to
the DB, and the DB→file bake is unwritten. Next decision owed: push order
between **(a) authoring surface — who writes the DB** and **(b) the bake**. This
was design/feeling-out only — no `website/index.html` change, tree clean.

**2026-05-28 — editor three-bucket V3c shipped.** Supersedes the unified-tree pass below. `tasks/04_event_app/editor_three_buckets_v3c.md`. The right-rail Map editor section collapses from 5 buckets to **3** (Point / Line / Polygon) plus the ★ Visitor list; Image and Callout fold into Point and Polygon by geometry (brand logos → Point/Brand, visitor context → Polygon/Visitor). Inside each bucket, source sub-groups split rows by origin (Drawn / Trailheads / Brand / Visitor) — Drawn is open by default, references collapse with their count visible. The 5-toggle layer strip is gone; the 5 `show*` inputs survive inside a hidden `#legacyLayerToggles` form block so preset capture/apply, MapLibre layer-visibility wiring, and Terra-Draw class flips keep working unchanged. Sub-group head bulk-checkboxes are the visible mirror, two-way bridged via change events. Each bucket head carries a green `+` that opens an inline `.editor-create-inline` row right inside the bucket body (bucket-scoped category select + matching primary action + cancel `✕` + help text); the footer shrinks to Export / Clear / status / help. `setDrawMode` now flips active state on every bucket's `+` and start-btn alongside the legacy hidden buttons. `draw.on('finish')` reads category from `currentCreateBucket.categorySelect.value`. A `FEATURE_LIST_LAYERS.trailheads` spec was added (read-only, no ★, no accordion); `publish.geojson` ships zero trailhead features today so the sub-group head reads `—` until trailhead data lands. **Event-schedule POIs are regular drawn POIs** — they render alongside editorPois Points inside the Point/Drawn sub-group with their `#tag` visible on the row. Mockups under `website/editor_unified_*.html` (compare pages: `editor_unified_compare.html` for V1–V4 axis pick, `editor_unified_v3_create_compare.html` for V3a/b/c create-flow pick) — retire per `misc_4` mockup-cleanup routing. Verifier impact: `playwright_verify_poi_editor.py` rewritten for the per-bucket selectors (PASS); `playwright_verify_presets.py` editor-tree assertion updated for 3-bucket shape (PASS on V3c assertions, 3 pre-existing fails remain — publishable-section / OSM-section-move / mobile-overlap, all routed to `viewer_polish_followups.md`); `playwright_verify_session_tools.py` PASS; `playwright_verify_synthetic_activity.py` PASS; `playwright_verify_feature_list.py` PASS on cemeteries/buildings/visitor/brand (3 fails pre-existing on retired publishable-section export path); `playwright_verify_event_schedule.py` PASS on tag-driven/clock-times blocks (6 fails pre-existing on trail-lane fallback). DOM snapshot screenshot at `/tmp/aop_editor_v3c.png` (not durable).

**2026-05-27 (later) — editor unified tree shipped.** `tasks/04_event_app/editor_unified_tree.md`. The right rail's `data-section="poi"` block (group toggle deck + `wirePoiPanel` two-way bridge) was deleted. The `data-section="editor"` section now hosts a five-bucket tree by renderable kind: ● Point · ╱ Line · ▭ Polygon · ⌗ Image · ⌑ Callout, plus a virtual `★ Visitor list` group at the top that live-mirrors every highlighted feature across `editorPois`, `brandLogos`, and `visitorContext` (the last two newly opted into `highlightable: true`; brand-logos and visitor-context override stores now carry `highlight` so the flag survives reload). editorPois renders three times via the new `renderFeatureList(layerKey, { onlyGroupId })` opt arg so its Point / Polygon / LineString groups split across the three matching buckets. The 5 layer toggles (`showEventSchedule`, `showTrailheads`, `showVisitorContext`, `showBrandLogos`, `showEditorPois`) move to a thin strip at the top of the editor section; the create row (category + Place / Draw / Trace + Export / Clear + status + help) drops to a `.editor-create-footer` at the bottom. `setEditorFeatureNotes` trim fix bundled in (one of the two S3 review items from `poi_editor_followups.md`). Verifier impact: `playwright_verify_poi_editor.py` PASS, `playwright_verify_synthetic_activity.py` PASS, `playwright_verify_session_tools.py` PASS, `playwright_verify_presets.py` PASS on editor-tree + console assertions (one pre-existing mobile-overlap 4 px boundary remains), `playwright_verify_feature_list.py` PASS on editor-tree + visitor-context reveal path (three `data-section="publishable"` failures pre-existing — that section does not exist), `playwright_verify_event_schedule.py` trail-lane fallback failures pre-existing per the earlier 2026-05-27 routing.

Read an archive only if you need to retrace why something was built. The durable record for each feature lives in its `tasks/*/_done/<feature>.md` build card, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.

## Where we are

Sprint 01 (MVP), Sprint 02 (Editor & Polish), and Sprint 03 (Event App Loop)
are closed. Sprint 03's reviewed cards live in `tasks/03_event_app/_done/`.
`tasks/03_event_app/misc_3.md` was left active by request. Sprint 04 starts at
`tasks/04_event_app/_readme.md`.

The Sprint 02 carryover router is archived at
`tasks/03_event_app/_done/viewer_polish_carryover.md`. Lanes 1–5 shipped
2026-05-24 (hot-control two-lane, calendar expand + scroll-into-view,
collapse-icon uniformity, default-layer audit table in `research/viewer.md`,
brand-logo size slider + add-image runbook). Lane 6 shipped its main pass in
`tasks/03_event_app/_done/code_health_pass_4.md`; residual viewer polish now
lives at `tasks/04_event_app/viewer_polish_followups.md`. Lane 7 stays on
`tasks/01_mvp/_done/community_trails_import.md` and is also visible in
`tasks/04_event_app/data_integrity_publishability.md`. The 2026-05-25 camera
correction is applied: zoom shortcuts reset to flat west-up, while Park / Topo
/ Trace layer presets preserve zoom, pitch, bearing, and independent 3D state.

**2026-05-25 Pass 4 + misc landings.** Calendar-card cream-surface chrome restored (`misc.md` "left side event calendar transparent" item — `.calendar-card` is back in the shared cream-surface group at `website/index.html:31`). Pass 4 first wave shipped via four parallel agents and landed in main: (1) `!important` cluster fully eliminated in the right-rail collapse-button + tune-control region by raising specificity to `.panel`-scoped selectors; (2) 8 safe palette token swaps (`#d8cdb4 → var(--cream-border)`, etc.); (3) full theme readability report (8 surfaces, 13 KEEP / 6 TWEAK / 4 FIX with WCAG math) recorded in `tasks/03_event_app/_done/code_health_pass_4.md`; (4) Critique-C1 hot-button copy renamed off "heat" wording — `Trail heat / Activity evidence` → `Trail activity / Where rigs spent time` in HTML defaults, `refreshHotButton` fallbacks, aria-labels, and the matching verifier assertion. Residual Pass 4 follow-ups now live in `tasks/04_event_app/viewer_polish_followups.md`.

Sprint 04's main app thrust is `tasks/04_event_app/event_crud_upload_loop.md`
— event setup, CRUD, uploads, and the submission -> review -> publish loop.
`tasks/04_event_app/dev_db_snapshot_reseed.md` carries the dev DB dump/reseed
need from `misc.md`. `tasks/03_event_app/_done/left_panel_poi_browser.md`
shipped 2026-05-25 — the viewer now has a third left-rail `POI` tab sitting
between `Events` and `About`, rendering a grouped index of event anchors,
in-park buildings, observed trails, cemeteries, off-park visitor support, and
drawn POIs. Visitor blurbs + revisit-note placeholders live in
`website/data/aop_poi_index.json` (6 groups, 20 entries, 10 placeholders
flagged for follow-up); the source GeoJSONs stay clean so re-exports can't
overwrite authored copy. Smoke checks land in the extended
`playwright_verify_presets.py`; a dedicated `playwright_verify_left_poi_browser.py`
is now carried by `tasks/04_event_app/viewer_polish_followups.md`.

**2026-05-26 — left-rail drawer shipped.** `tasks/03_event_app/_done/left_rail_collapse_tabs.md` shipped into `website/index.html`: Search / Hot / Calendar now live in a two-column left drawer with per-card icons, persisted open/closed state, hot-data auto-open that respects user-close, all-closed standalone state, and the calendar resize handle. Focused coverage: `mvp/scripts/playwright_verify_left_rail_drawer.py`.

**2026-05-26 — right-panel editor consistency.** `tasks/03_event_app/_done/right_panel_editor_consistency.md` shipped. `⧉ Export all` moved into the panel header beside `▾ Collapse panel` (the old `.panel-actions` row at the bottom of `#panelBody` is gone). Publishable section header gained its own `⧉` for parity with Source / Derived / Map editor; the POI section was deliberately not given one (its `poiGroup*` IDs don't match `sectionInputs`' `show*` filter, so the payload would be empty). Three layers that previously appeared as bare checkboxes in Publishable now get the full editor treatment: `activityHotspots`, `syntheticActivity`, and `eventSchedule` are registered in both `TUNABLE_LAYERS` (paint drawers) and `FEATURE_LIST_LAYERS` (CRUD index — 65 / 18 / 8 rows respectively, each with visibility + fly). New `refreshFeatureListData` helper lets `rebuildEventScheduleData` push fresh anchor data into the runtime without recursing through `registerFeatureListLayer`. The two failures in `playwright_verify_event_schedule.py` (search magnifier missing, hot-button click timeout) were verified pre-existing by stash + replay — not caused by this card.

**2026-05-26 — session tools shipped.** `tasks/03_event_app/_done/viewer_session_state_test_clock.md` shipped from `misc_2.md`: right-panel virtual clock controls (`aop_virtual_clock_v1`), Reset viewer, and pocket-map reload state (`aop_viewer_session_state_v1`) for active preset, active left tab, search query, and selected event. Landmark-hot decision: keep landmarks in POI/search, not a third Hot lane. Focused coverage: `mvp/scripts/playwright_verify_session_tools.py`; adjacent suites `playwright_verify_left_rail_drawer.py`, `playwright_verify_event_schedule.py`, and `playwright_verify_presets.py` passed after the startup-order fix for restoring the POI tab.

**2026-05-26 — drawn-POI CRUD reshaped.** `tasks/03_event_app/_done/poi_editor_tree_inline_accordion.md` shipped. The flat editorPois list is now a kind-grouped tree — `Drawn POI → POI / Footprint / Line → named item` (`FEATURE_LIST_LAYERS.editorPois.groups` matches on `feature.geometry.type`, and `groupForFeature` now passes `feature` through alongside `props` so other layers ignore the 2nd arg). Each leaf carries a trailing `▸` chevron that opens an inline accordion editor below the row: name, category (now mutable post-create), tag, notes (new `feature.properties.notes` field), geometry summary, action row (`🎯 Fly · ✋ Move · ⎘ Duplicate · ⧉ Copy GeoJSON · Delete`). Tag input and `⧉` copy button move off the row into the editor; visibility checkbox, `★` highlight, name (click=fly), `🎯`, `✋`, and the new `▸` chevron stay on the row. The MapLibre rename/delete popup (`openPoiPopup`) retired — map-click on a drawn POI now expands the leaf's editor in the right panel and flashes the row. Card mockup pass: `website/poi_crud_compare.html` + four `poi_crud_v{1..4}_*.html` variants; V1 (inline accordion) chosen. Same session shipped the editor seed + dump-to-GeoJSON path: `website/data/aop_editor_seed_pois.geojson` (schema `aop_editor_seed_v1`, first entry the `aop_seed_pavilion` POI at the 1010 Ellis Cove centroid carrying `seed_tag: '#pavilion'`); `maybeSeedEditorPois` runs on a fresh install or after Reset viewer and writes both the POI store and the `#pavilion` tag binding, stripping the matching tag off any other layer one-shot (migration: 1010 building → seeded POI). The building-side `maybeSeedFeatureTags` + `FEATURE_TAG_SEEDED_KEY` constant retired (the literal stays in the wipe list so existing installs get the sticky flag cleared on Reset). Workflow to update the seed lives in the create-row help text: `Export GeoJSON → replace the seed file with the download → commit`. Verifiers green: `playwright_verify_poi_editor.py` (asserts inline editor + delete; clean-slate now writes `[]` to leave the seed gate closed), `playwright_verify_feature_list.py` (POI copy path rewritten to expand the leaf first; same `[]` swap), `playwright_verify_presets.py`, `playwright_verify_session_tools.py` (Reset now asserts the seed re-installs `aop_editor_pois_v1` + `aop_feature_tags_v1` while the other ten viewer-owned keys stay cleared), `playwright_verify_event_schedule.py` (Tag-driven block rewritten: `#pavilion → editorPois/aop_seed_pavilion`, no building row pre-bound; live re-resolve test driven via `setFeatureTag` rather than the buildings drawer DOM).

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

## Session note

This file is handoff context, not a durable policy document. Keep it short. When a session ends, prune this file back to a pointer and archive the changelog to `session_context_<YYYYMMDD>.md`. Do not append session-by-session update blocks here — they belong in build cards, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.
