# Session Handoff Archive — the v88→v97 stretch (through 2026-06-15)

Frozen point-in-time snapshot pruned out of `session_context.md` on 2026-06-15.
It holds the session-by-session changelog for the v88→v97 stretch (the durable
record for each feature lives in its `tasks/*/_done/<feature>.md` build card —
read this only to retrace why something was built). The live handoff pointer is
`session_context.md`; the durable sections near the bottom here are a frozen copy
of that file as it stood at the prune.

-----

## Latest (2026-06-15)

**Docker back up → DB↔served reproducibility found BROKEN; DIAGNOSED, no DB change
(user direction).** User: *"docker is up now."* Brought PostGIS up and traced the bake
pipeline before mutating the canonical DB. **Root finding: the GeoJSON export pipeline
(`export_publish_geojson.sh`) silently diverged from the served filenames at the medallion
`gold_` rename (`91a017e`)** — it still writes `publish.geojson`/`aop_*.geojson` (none on
disk), the viewer reads `gold_publish.geojson`/`gold_aop_*.geojson`, so **the served gold is
NOT reproducible from the DB** (going-gold slice-6 promise broken; the schedule arm →
`aop_event_schedule.json` is the one still-connected pipeline). DB is also stale: G-Central
still in `core.features` (poi 139 + building 2), Monteagle callout old copy, **120 stale
`trails` rows vs the 130 file-based traces** (trail data-model fork), Saturday segments still
in the publish gate (cemeteries already correct). The prior "set trail permission when Docker
returns" item **can't run as written.** Offered full-reconcile / scrubs-only / diagnose-only →
**user chose DIAGNOSE ONLY; DB untouched (160 features / 6 publish, as found).** Full diagnosis +
recommended reconcile path + exact staged copy recorded as the **2026-06-15 addendum on
`tasks/20_deferred/data_integrity_publishability.md`**. No fire — served viewer unaffected; this
is restoring DB→served reproducibility, the user's call when to do it.

**Cut-off recovery — all in-flight work re-verified GREEN; 3 stale dev-verifiers
repaired (UNCOMMITTED).** User: *"we got cut off mid work. make sure every task is
finished and we are happy."* Re-ran every verifier touching the working tree against
live `:8001`, by observation: region-callout caveat+Monteagle **10/10**, css cache
versioning v97 **5/5**, 3D spin-while-tilted **7/7**, park-border faint **8/8**,
contour styling mockup **13/13**, label/persist firepit **13/13**, search-clear
dethrone **8/8** — all PASS, 0 product console errors. Version is consistent v97
everywhere (`sw.js VERSION`, `#appVersion`, three `?v=v97` asset stamps). Fixed three
**dev-verifier-only** staleness issues surfaced in the sweep (no product code/data
touched, all `brain/output/`): (1) `verify_five.py` line 66 fetched the renamed-away
`data/aop_landcover_9patch.geojson` (now `gold_aop_…`) → **crashed before items 1-3
ran** (the flagged pre-existing debt); repointed to the served `gold_` file so the
script completes. (2) With the crash gone, `verify_five.py` items 1-2 surfaced as
stale assertions testing *replaced* implementations — item 1 asserted the old
`trail_number` text-field expression (the layer now reads the baked `display_name`
field, v87; its re-derivation even produced a bogus "1 1 Launchpad"), item 2 clicked a
`/trail/i` POI group that no longer exists (the reader directory renders only STARRED
groups — Buildings/Camp POIs/Visitor support; no trail is starred). Rewrote both to
**observe** current reality (read `display_name`; click the first real POI row) — now
**ALL items PASS**, product proven correct by the passing dedicated `verify_label_border_persist_firepit.py`. (3) `verify_contour_styling_mockup.py`
check-3 used `.grid p` (descendant) which false-matched the 5 panel `.caption` blurbs;
the real load-error fallback is a direct-child `.grid > p` (`grid.innerHTML='<p…>'`) —
tightened the selector → **13/13**. No `vNN` bump owed (dev verifiers only). The
uncommitted product work below (callouts + css-versioning) still **rides v97; the
commit is the user's git gate.** Owed items unchanged (DB `core.features` when Docker
returns; on-device pinch-zoom re-check) — both blocked on external dependencies, not
cut-off work.

**Region callouts: caveat dropped + Monteagle popup extended (UNCOMMITTED).** User:
*"review the region callouts and get rid of caveat — people understand what they are
getting. monteagle seems to duplicate some things … extend as appropriate. it seems
terser than it has been"* + *"clicking the poi goes to the poi with more information.
its redundant to have the exact data in two places."* Design: the on-map **label** is
the terse teaser (direction · time · category), the **popup/POI** carries the detail —
they must not be word-for-word. (1) **Caveat gone from BOTH callout popovers** — the
"Caveat: planning estimate…" line was the callouts' `drive_time_note` surfacing through
`feature_display.js`'s `caveat` pick-chain; dropped `drive_time_note` from that chain
(renderer-only; `drive_time_note` stays on the data as author provenance, and the explicit
`caveat` channel is untouched for any feature that has a real one). (2) **Monteagle popup
re-written richer + de-duplicated** — was terse and led with `~30 min northwest via I-24`
(a verbatim echo of its own label); now names the venues and gives the "why" (the plateau
cluster / second base after the South Pittsburg–Kimball run) with no drive-time/direction
echo. South Pittsburg's popup already exemplified the ideal (Ellis Cove Road + Chattanooga
detail) → left as-is (no scope creep). **Both live popover engines covered:** the
reader (`index.html`→`viewer_core.js`) renders the callout click via the shared
`popupHtml`, and the live field editor (`data_editor.html`→`data_editor_map.js`) builds
its preview/Caveat from the SAME `featureDisplay()` (`m.caveat` is now empty for callouts)
— so the one `feature_display.js` edit fixes both. The council Quartermaster flagged a
THIRD path — `main.js` `bindPopup` (visitor-context) still emitting a `['Drive time',
drive_time_note]` row — but `main.js` is **dead code**: no HTML loads it (only a stale
`sw.js` precache comment claims `right_panel.html` does; it loads `panel.js`). Dropped that
row anyway for consistency (one line, on-directive). Edited the served
`gold_aop_visitor_context_callouts.geojson`
**and** the upstream `aop_poi_index.json` blurb so a future fold+DB bake reproduces it
(the served file is DB-baked via `export_publish_geojson.sh`; DB is down → core.features
owed when Docker returns). **Verified by observation** —
`brain/output/verify_callout_caveat_monteagle.py` **10/10 PASS**, 0 console errors (real
popovers: both callouts have no Caveat meta, Monteagle blurb = the new copy, names venues,
no label echo, on-map label still terse); screenshot `brain/output/callout_monteagle_no_caveat.png`.
`feature_display.js` is a precached shell asset + a served-data change → owes a cache re-key;
a concurrent session already has an uncommitted **v96→v97** bump in flight (sw.js URL-fingerprint
rewrite) that re-keys SHELL+DATA, so these changes **ride v97** — no separate bump, **commit is
the user's**. Don't touch `sw.js`/`index.html` (the concurrent session owns them).

**CSS/JS cache versioning — deploys now reach the client; v96→v97 (UNCOMMITTED).**
User: *"review our css caching policy. it seems as if its not being refreshed on the
remote … can we tag that with a version as well?"* + *"I am not seeing the new park
border styles."* Diagnosed by observation: the **remote was NOT stale** — live GitHub
Pages already served `VERSION=v96`, `#appVersion=v96`, and the faint park-border colors
(`#c4b48c`/`#d4b974`); the deploy had succeeded. The **client** was stale because GitHub
Pages serves **every file (sw.js included) `Cache-Control: max-age=600` on a STABLE url**
(a header you can't change on GH Pages), and the SW's background-refresh + install `addAll`
fetches didn't bypass that HTTP cache — so a VERSION bump could activate yet still serve
10-min-stale bytes (the park border lives in `viewer_core.js` paint, served
stale-while-revalidate). Fix, two layers: (1) **URL-fingerprinted the three viewer shell
assets** — `viewer.css`/`viewer_core.js`/`viewer_band.js` now carry `?v=vNN` in `index.html`
+ `sw.js` SHELL_ASSETS (driven by the one `VERSION` const), so a release is a never-seen url
no browser/Fastly/SW cache can shadow; (2) **SW precache + revalidation + navigate fetches use
`cache:'reload'`** so the un-fingerprintable HTML shell + copy/data JSON pull fresh (≤600s
Fastly edge is the irreducible floor). `sw.js` RELEASE CHECKLIST + `index.html` head comment
rewritten to document the `?v=` ritual. **v96→v97 bump performed** (shell change); **commit/push
is the user's git gate.** Verified by observation — `brain/output/verify_css_cache_versioning.py`
**5/5 PASS**, 0 console errors: a fresh page loads the three `?v=v97` assets and the live map reads
the faint `#c4b48c` border off the fingerprinted JS (`css_cache_versioning_park.png`). **To see the
already-live v96 border RIGHT NOW** (before pushing v97), bust the current client cache once —
desktop: DevTools→Application→Clear site data + hard reload; iOS PWA: delete the home-screen app
and re-add. After v97 ships, future deploys self-heal within ~10 min, no manual clearing.

**3D map spin RE-ENABLED while tilted — v95→v96 (COMMITTED `0d7b750` "v96").** User: *"review the
3d map. we used to be able to spin it around while it was tilted. now it seems to be
disabled. we want to enable it."* `viewer_core.js` had locked all orientation gestures
(`touchZoomRotate.disableRotation()` + `dragRotate.disable()` + `touchPitch.disable()`)
after the `pwa_qa.md` item-7 pinch-responsiveness fix + a "maybe it's my fingers"
accidental-tilt report. Removed the two rotate-killing calls so **spin is back** — two-finger
twist (touch) and right-click/ctrl-drag (desktop) now rotate the bearing, so the tilted 3D
view orbits again. **Pitch stays BUTTON-only:** kept `touchPitch.disable()` and added
`pitchWithRotate:false` to the map constructor, so the rotate gesture can't sneak in a tilt
and stray fingers still can't accidentally pitch (3D toggle eases to 60°; zoom presets reset
flat west-up — unchanged). `viewer_core.js` is a precached shell asset → **v95→v96** bump
performed (`sw.js`+`#appVersion`); the user **committed** it (HEAD `0d7b750`) together with the
concurrent park-border session's hunks. Verified by observation —
`brain/output/verify_spin_while_tilted.py` **7/7 PASS** (live handlers read dragRotate=on /
touchZoomRotate=on / touchPitch=off; a **real right-drag spun the bearing 16° (-90→-106) while
pitch held at 58° (Δ0.0°)**). **Honesty note (council Witness):** some runs throw an
**intermittent** `Could not compile fragment shader:` pageerror (it fired on one re-run, not on
6 others) — the sky/atmosphere shader failing under **headless software WebGL (SwiftShader)**,
environmental and provably not from this diff (it touches no shaders); the verifier now filters it
like the existing external-tile errors, so the "7/7 / no product errors" claim matches the run
(earlier this entry said a flat "0 errors", which a re-run contradicted at 6/7 before the filter). **Contract updated (council Quartermaster):**
`brain/output/verify_five.py` item 3 flipped from "drag-rotate disabled" → "drag-rotate ENABLED"
so the two camera verifiers no longer contradict. **Trade-off owed (on-device):** re-enabling the
two-finger twist may regress the item-7 pinch-zoom-start responsiveness (the handler again
disambiguates pinch vs twist) — confirm on the phone. **Pre-existing debt flagged (not mine):**
`verify_five.py` item 5 (line 66) crashes fetching the renamed-away
`data/aop_landcover_9patch.geojson` (now `gold_aop_landcover_9patch.geojson`), so the script dies
before item 3 runs in-script; item 3's flipped assertion is the same live handler the spin
verifier reads True. Addendum on `tasks/_done/04_edit/_done/pwa_qa.md` item 7.

**Park-bounds border toned to a faint tint-edge — shipped in v96 (committed `0d7b750`).** User:
*"the park bounds have a dark border. remove the border. there is a tint on the land
that should do the same"* → then *"ok keep the border if you need it to click on. make
it way less visible. only a tad darker than the fill."* The `publish-boundaries` line is
**kept** (it's the boundary's click target in `INTERACTIVE_POPUP_LAYERS` — clicking it gives
the "what is this line / where from" card), but re-painted from a dark brown edge to a faint
tan/gold just a step darker than the `publish-boundary-fill` tint, so the fill's opacity step
does the park/off-park separating (same borderless logic as the landcover edge). 3 paint edits
in `viewer_core.js`: base `addLayer` + the two presets that actually draw it — **Park**
`#6e5a3c` w2.5 → `#c4b48c` w1.5 op0.5 (fill `#d8c8a2`@0.10); **Topo** `#4d3928` w3 → `#d4b974`
w1.5 op0.5 (fill `#e7c982`@0.08). Trace/Satellite have `showBoundaries:false` so their
`publish-boundaries` override is a no-op — left untouched. **Verified by observation**
(`brain/output/verify_park_border_faint.py` **8/8 PASS**, 0 console errors): live
`getPaintProperty` reads the new faint values in both presets, layer still present+visible
(clickable); framed + z17 close-up screenshots
(`brain/output/park_border_faint_{park,topo}[_closeup].png`) show a soft tint-edge, not a dark
line. `viewer_core.js` is a precached shell asset; the user committed it (with the concurrent
3D-spin change, the contour-mockup cleanup, and a task-move) as **HEAD `0d7b750` "v96"** — the
v95→v96 cache bump (`sw.js`+`#appVersion`) rode that same commit, so **no separate bump owed**.
The paint change is observation-clean and on-farm; the commit commingling several tasks is the
user's git-gate call, not a defect in this work. Council: witness·quartermaster CLEAR; warden
andon was a staleness flag on this note's git claims (v96 committed, not uncommitted) — resolved
by this edit.

**Mockup HTML cleanup + new contour-styling compare page (UNCOMMITTED).** User:
*"we have a few mockup html pages that are no longer needed. find them and remove them.
Create a new mockup for CSS styling of major and minor topography contour lines. I want
to see a few variations we can barely see the minor lines."* (1) **16 dead mockups
removed** from `website/` — the brain-flagged junk set (`old_index.html`, the 12
`leftrail_*.html`, `icon_master.html`) plus two more orphans with no live refs
(`load_animations.html`, `calendar_placeholder_v2_spinner.html`; the spinner already
shipped into `index.html`). Confirmed first that all references were comments/doc-pointers,
not runtime links, and that `sw.js` does **not** precache any of them. The 6 surviving
HTML are all live tools (`index.html`, the standalone field editors `data_editor.html` /
`schedule_editor.html` / `right_panel.html`, `copy_review.html`, `data_sources.html`).
Dangling comments in `index.html` (×3) + `sw.js` (×1) + `css/viewer.css` (×1) that pointed
at deleted files were corrected — **comment-only, no functional shell change → no `vNN`
bump owed.** Council core-three cleared 3/3 (witness·warden·quartermaster); the
`viewer.css` comment was the warden/quartermaster advisory, now fixed
(`brain/output/council/contour_mockup_cleanup_20260615.md`). (2) **New
`website/contour_styling_mockup.html`** (dev-only, not served/precached): 5 synced
MapLibre panels rendering the **real** `gold_aop_contours.geojson` over the real lidar
hillshade, major (index) lines held constant while the minor line steps from the current
Topo style down to barely-visible across three levers — opacity (Faint / Ghost), width
(Hairline), hue (Tonal blend). Each panel prints its exact paint values to lift straight
into `viewer_core.js` (`contours-minor`/`contours-index` + Topo preset overrides).
**Verified by observation** (`brain/output/verify_contour_styling_mockup.py`, served
:8001): all 5 canvases paint, **0 console errors**; close-ups
(`brain/output/contour_closeup_*.png`) confirm the minor-line faintness gradient is real.
Awaiting the user's pick of a variation. **Brain/dev artifacts only — no served product
change; the commit is the user's git gate.**

## Latest (2026-06-14)

**Trail PERMISSION blocker resolved → trails are publish-clean gold — v94→v95 (UNCOMMITTED).**
User: *"these guys give permission for people to put the map up on the internet, and we are
tracing the unmapped trails manually. the trails should be rendering and gold for all intensive
purposes."* The `"SFWDA paper map — permission TBD"` on the trail network was **stale** — AOP (the
landowner) grants public web publishing, and the trails are first-party manual traces. Set all
**130** trails in `gold_aop_trail_network.geojson` to `permission:"publish"` (the
`publish.features` gate value; was 120×TBD + 10×missing), and made it durable: the
`import_illustrator_trace.py` new-trail default now sets `permission:"publish"` so a re-import of
the Affinity master keeps the clean posture. Verified by observation
(`brain/output/verify_trails_gold_publish_permission.py` **4/4 PASS**, 0 errors: trails visible on
Park, 136 rendered fragments = 130 source trails across tiles, live source reads publish×130, no
TBD; screenshot beside it). Served-data
change → **v94→v95** bump performed (`sw.js`+`#appVersion`); **commit remains the user's**.
**Still owed (not permission):** name the 109 numbered trails (content, in progress); DB carries
old permission — when Docker returns set `permission='publish'`+`publish_status='publish'` so the
formal publish view (`gold_publish.geojson`, 0 trails today) regenerates with the network.
Addendum: `tasks/20_deferred/data_integrity_publishability.md`.

**Task-tree swept: done cards + fully-done sprints archived (UNCOMMITTED).** User:
*"if there are done items not in the _done dir of the sprint it needs to be moved. if the
whole sprint is done, then that sprint can be moved to the _task done."* (1) The two done
`01_mvp` feature cards (`gold_promotion_pins_curation_v90.md` v90, `poi_search_click_links.md`
v89) moved into `tasks/01_mvp/_done/`. (2) **Eight fully-done sprints relocated whole** to
`tasks/_done/`: `02_edit`, `04_edit`, `05_special_operation`, `07_tables`,
`08_data_normalization`, `11_client_convergence`, `12_field_schedule_editor`,
`13_viewer_extraction`. Active/open sprints stay at the `tasks/` top level (`01_mvp`,
`03_event_app`, `06_going_gold`, `09_editor_maturity`, `14_illustrator_trace`, `20_deferred`,
`backlog`). **Refs rewritten deterministically** (`output/relink_done_sprints_20260614.py` — recomputes
each link from its new location; 99 rewrites across 30 active files incl.
`northstar/editor_architecture_contracts.md`, `search_map.md`, `research/viewer.md`);
point-in-time records (`output/` council receipts, dated handoff archives) left pointing at old
paths as history (user's call). Verified by `output/verify_brain_links_20260614.py`: **0 active
references to a moved sprint left broken** (pre-existing
debt — stale `04_event_app`/`10_deferred` names, etc. — untouched). Convention recorded in
`tasks/_readme.md` (two move rules; spine cards stay at sprint root). **Brain reorg only — no
product code/data touched, no `vNN` bump owed; the commit is the user's git gate.**

**Trace round-trip reviewed + 2 bakes before the next re-edit (UNCOMMITTED).** User:
*"review the trail point polygon export process. we have some data updates that need to be
baked into the gold data before I edit the sheet again and re-upload."* Reviewed all three
layers by observation; export was out of sync with served gold. **(1) Waypoints export
re-sourced** — `export_illustrator_trace.py` now reads `gold_aop_waypoints_traced.geojson`
(the 24 served waypoints) instead of the pre-trace publish/editor-seed stubs (which held
only the user-deleted "AOP Pavilion" = 1 circle); a re-export+re-upload would have dropped
~18 authored waypoints. **(2) Import stops stripping the baked number-name** —
`import_illustrator_trace.py` no longer reverts `1 Launchpad`→`Launchpad` (stored
convention is now Number-Name; 80 trails); stale `viewer_core.js trailDisplayName` comment
corrected (comment-only). **Build-pipeline + 1 JS comment — no served-data change, no `vNN`
bump owed.** Verified `brain/output/verify_trace_roundtrip_baked.py` **24/24 PASS** (read-
only; star-durability regression still PASS). Fresh faithful export at
`brain/output/illustrator_trace/aop_satellite_trace.svg` (Trails 130 | Waypoints 24 |
Buildings 6) = the sheet to open in Affinity next. **(3) Buildings (polygon) round-trip
wired** (user: *"we need the full loop working for all types … polygons … not ideal long
term"*) — `import_polys` now provenance-preserving + writes the SERVED
`gold_aop_buildings.geojson` (was the dead `bronze_aop_buildings_traced.geojson`): FEMA
provenance carried by name, an unchanged footprint carried VERBATIM (centroid/area/geometry
exact — FEMA area must not be overwritten; equirect re-measure is up to 11% off), an edited
footprint recomputes centroid+area (pin + editor Area track it via
`import_fema_buildings.ring_centroid/signed_ring_area`), unmatched-preserve, and
`_clean_ring` fixes the export's explicit-close-plus-`Z` double-close. **The full loop now
works for trails (line) · waypoints (point) · buildings (polygon).** Verified
`brain/output/verify_buildings_roundtrip.py` **22/22 PASS** + a real `import --all`
backup/restore (130 trails · 6 buildings · 24 waypoints to served gold, `_meta` preserved,
tree restored clean) + trail/waypoint regressions still PASS. `bronze_aop_buildings_traced.geojson`
now orphaned (cleanup candidate). Build-pipeline only — no served-data change now; a real
re-upload changes all 3 gold files → owes the user's `vNN` bump THEN. Council re-run owed
over the larger diff. Addendum on `tasks/14_illustrator_trace/satellite_illustrator_export.md`.

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
Addendum on `tasks/_done/13_viewer_extraction/_done/viewer_poi.md`.

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
`tasks/_done/13_viewer_extraction/_done/viewer_poi.md`.

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
Addendum on `tasks/_done/12_field_schedule_editor/_done/normalize_feature_display.md`.

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
v90→v91. Addendum on `tasks/_done/02_edit/_done/six_item_viewer_batch_20260614.md`.

**S'mores moved to the firepit — rides v91 (UNCOMMITTED, separate session).** The v87
batch tagged the PRO Line *race* to `#firepit` but left both "Fire + s'mores" sessions
(`fri-fire`, `sat-fire`) at `#pavilion`, so the firepit POI showed the obstacle race but
not the campfire. User: *"Smores should be at the firepit. what happened?"* Source
(`brain/import/TBI.copy`) — they *"head to the fire pit for some smores"* — so both
sessions retagged `#pavilion`→`#firepit` in `aop_event_schedule.json` (data-only; no JS).
Rides the concurrent session's v90→v91 bump (re-keys `DATA_CACHE`; no second bump).
Verified by observation on `:8001` — `brain/output/verify_smores_at_firepit.py` **12/12
PASS**, 0 errors. Coord: `handoff/coord/smores-at-firepit.md`. Addendum (item 6) on
`tasks/_done/02_edit/_done/six_item_viewer_batch_20260614.md`.

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
  `tasks/01_mvp/_done/gold_promotion_pins_curation_v90.md` (RESOLVED → SHIPPED). **Durability gap:**
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
  `tasks/01_mvp/_done/poi_search_click_links.md`. The "no-trails" SFWDA paper overlay
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
