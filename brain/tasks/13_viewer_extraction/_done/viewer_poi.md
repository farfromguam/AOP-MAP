# Slice 4 — POI: feature popups (4a) + the ★-destinations directory (4b)

TL;DR:
- **4a (done):** the normalized **feature click popup** — click any curated/published feature → its
  "what is this line, where did it come from?" card (name · blurb/revisit · Kind/Status/Source/Caveat),
  via the **one shared `window.AOPFeatureDisplay`** strategy. This is the northstar's core product test,
  and what slice 1 deferred when it dropped `bindPopup`.
- **4b (deferred):** the **POI-tab directory** in the drawer — `renderPoiTab` + `buildPoiGroups` (the
  `aop_poi_index.json` ↔ feature join) + the ★-curated destinations + `gotoPoi`. A bigger piece; next.

#aop #sprint #13 #viewer #poi #popups #slice

-----

## 4a — feature click popups (shipped)

Instead of porting `main.js`'s per-layer `bindPopup` calls (each with its own `detailRows`), the clean
core uses the **one text strategy** the user mandated (`feature_display.js`,
`normalize_feature_display.md`): a single map-click handler over the interactive layers reads the clicked
feature's props through `window.AOPFeatureDisplay.featureDisplay(props)` and renders
`window.AOPFeatureDisplay.popupHtml(model)`. Branch-free — every feature reads the same fallback chain;
the values live on the baked feature, not in per-layer code.

**Built:** `viewer.html` loads `./js/feature_display.js` before `viewer_core.js`. `viewer.css` carries the
`.poi-tab-popup .poi-popup-*` rules (app.css:748-754). `viewer_core.js` adds `INTERACTIVE_POPUP_LAYERS`
(the carried layers worth a popup) + a `map.on('click')` that queries the topmost rendered interactive
feature and opens the normalized popup (reusing `closeAllMapPopups` / `visibleMapRect` / `panPopupIntoView`
from the schedule slice), plus a `mousemove` pointer-cursor.

### Done — 2026-06-13 (verified by observation)

`/tmp/verify_viewer_popups.py`: **6/6 PASS, 0 console errors.** Click a **visitor callout** → popup with
the `.poi-popup-title` "South Pittsburg / Kimball supply run", the blurb, and the Kind/Status/Source meta
(screenshot `viewer_popup_callout.png`). Click a **building facility** (fresh page, Pavilion zoom →
click) → "Pavilion | Kind building · Status raw context · Source ORNL" — proving the one strategy works
across layers. `viewer_core.js` 2151 → **2187** (+36); `viewer.html` +3; `viewer.css` +8. `index.html`
untouched. (Note: the popup harness needs a fresh page per feature — a second click-interaction on the
same page is eaten by leftover popup/search state; a test artifact, not a viewer bug. MapLibre's
`closeOnClick` closes the popup when a click lands on empty map.)

**Reuse:** `feature_display.js` is loaded as a `<script>` (not re-ported), same as the schedule resolver;
the popup positioning reuses the schedule slice's `closeAllMapPopups`/`visibleMapRect`/`panPopupIntoView`.

### Addendum — 2026-06-13 (hover-cursor throttle — user reported a beachball over the trails)

User: *"there also seems to be a beachball when hovering over the trails."* The 4a hover-cursor was a bare
`map.on('mousemove')` that ran `queryRenderedFeatures` over all ~12 `INTERACTIVE_POPUP_LAYERS` on **every
raw mousemove** — including during a pan (where the read is pointless and competes with the camera move +
the band's `raiseBand` for the main thread). That per-mousemove query is the one plausible per-hover cost
and the prime suspect for the beachball.

**Could NOT reproduce the beachball in headless** (verify_by_observation, honest): Playwright over `:8001`,
750 hover moves across region/park/pavilion → **0 long-tasks, 0 re-renders**, `queryRenderedFeatures`
avg **0.57 ms** (max 4.7), trail GeoJSON only 130 KB, `getStyle()` 0.1–0.3 ms. So in headless Chromium it
is not heavy — the beachball is likely environment-specific (real Safari/Retina, where
`queryRenderedFeatures` can be markedly slower). It is **not** related to the v72 left-controls
pointer-events fix: that hover handler fired over the trails (open map field) before that CSS change too.

**Fix (defensive, `viewer_core.js`):** throttle the hover query to **one `queryRenderedFeatures` per
animation frame** and **skip while `map.isMoving()`**. Cursor *logic* is unchanged (pointer over a feature,
grab off it); only *when* it runs changes. Verified: `node --check` clean; **120 synthetic mousemoves →
1 query** (rAF-coalesced); cursor still resolves to `pointer` over a real feature off the overlay, and the
"pointer everywhere in the park" is the pre-existing big-`visitor-context-fill` behavior, unchanged.
**Honest status:** removes the per-mousemove query storm; **not confirmed** to be the beachball cure since
it could not be reproduced here — owed: user confirmation on the real device. **UNCOMMITTED**, and it landed
in `viewer_core.js` alongside the user's live `BAND_PAD` border tuning (separate, the user's work).

**Follow-up (2026-06-13) — user narrowed it: "safari hover only, center area."** Reproduced Safari's engine
with Playwright **WebKit** (Version/26.4, real WebCore/JSC) and measured:
- hover `queryRenderedFeatures` over the center is cheap — avg **1 ms** (max 11), **0 long-tasks** across a
  10 s continuous center-hover burst;
- hovering triggers **0 map re-renders**; frame pacing holds a steady **16.7 ms / 60 fps**;
- removing all **38 band layers** changes center-hover frame pacing by **0.0 ms** (band not implicated).

So JS, re-renders, and the band are **ruled out by observation in both engines** — the throttle is good
hygiene but is **not** the cure. Headless WebKit renders in *software*, so it cannot exercise the remaining
suspect: **real Safari's GPU compositor** on the dense center layer stack. That needs the user's real Safari
(real GPU) — handed off: (1) Safari Web-Inspector **Timeline** recording while hovering the center
(Scripting vs Rendering/Compositing settles it); (2) live band A/B via
`AOPViewerBand.bandLayers().forEach(id=>AOPViewer.map.getLayer(id)&&AOPViewer.map.removeLayer(id))`. Awaiting
the user's real-device signal before any further fix.

## 4b — POI-tab directory (shipped, index-driven)

**The andon that shaped this.** `main.js`'s `buildPoiGroups` → `collectStarredDestinations` builds the POI
tab from the editor's `featureListRuntime` + `FEATURE_LIST_LAYERS` registry, filtered to **★-curated**
(`highlight===true`) rows. Two blockers for the read core: (1) that whole registry is editor machinery the
clean core doesn't have; (2) **the ★ curation is NOT baked onto the served data** — verified: 0
`highlight===true` features in `aop_buildings`/`aop_trail_network`/`aop_visitor`/`aop_cemeteries`; the stars
live in editor localStorage. So a verbatim port would yield an empty directory.

**The clean re-derivation.** The published curation is `aop_poi_index.json` itself — 12 hand-curated
`{group, match, blurb}` entries. The read-core directory is **index-driven**: each entry is joined to its
loaded feature (by `match.source` + address/name/layer) for fly-to + the normalized popup; rows group by
the index's group order. No editor registry, no ★ store.

**Built:** the POI sub-tab `<button>` + `poiList` panel in viewer.html; the `.poi-list*`/`.poi-row*` CSS
(app.css:736-747); `fetchPoiIndex` + `resolvePoiFeature` + `buildPoiGroups` + `renderPoiTab` + `gotoPoi`
(reuses `flyToFeature` + the normalized popup + `closeAllMapPopups`/`visibleMapRect`/`panPopupIntoView`).
The three joined datasets (`poiBuildingsData`/`poiVisitorData`/`poiPublishData`) are retained at module
scope from the load handler.

### Done — 2026-06-13 (verified by observation)

`/tmp/verify_viewer_poitab.py`: **8/8 PASS, 0 console errors** (one re-run — a transient headless WebGL
"fragment shader" GPU hiccup, environmental, not the viewer). The directory renders **7 curated rows**
across **Buildings in the park** (Pavilion / Farmhouse / Front Office), **Trails** (Saturday Afternoon
Activity seg 1/2), **Visitor support** (South Pittsburg / Monteagle); clicking a row flies + opens the
normalized popup ("Pavilion"). Screenshot `viewer_poitab.png`. `viewer_core.js` 2187 → **2354** (+167);
viewer.html +6; viewer.css +13. `index.html` untouched.

**Published-line gap (surfaced, the user's call — fork 2 family).** The index also has **cemeteries** (4)
and **drawn_pois** (1) groups; those yield no rows because the read core doesn't carry the
`aop_cemeteries` layer (excluded slice 1) or the editor drawn-POI layer. Carrying cemeteries (public TN
Comptroller data — the Ellis inholding et al.) would complete the directory's cemeteries group; that's the
same published-layer-line call the user made for hotspots. Surfaced, not decided.

### Addendum — 2026-06-13 (★ MOVED INTO THE DATA MODEL — the user's hard requirement)

User, on the index-driven directory: *"STARS. if it's not in the data model we need to add it. THIS IS THE
ONLY THING I WILL ACCEPT."* Correct — the index side-join was a workaround. The ★ is now a **published,
source-traceable field on the feature** (`properties.highlight`), read end-to-end. Three changes:

1. **Reversed the "a star is not a fact" policy** (`mvp/scripts/panel_overrides.py`). The editor already
   exported `highlight` (`panel.js` `EDITABLE_SERVED_KEYS`), but BOTH bake sinks stripped it via
   `VIEW_STATE_KEYS`. Split the contract: `SERVED_SKIP_KEYS` (panel-internal only) for the **file sink**
   (`bake_panel_overrides.py`, the prod data — there is no DB in prod) so it now **bakes the ★**;
   `VIEW_STATE_KEYS` (still includes `highlight`) for the **DB sink** (`apply_panel_overrides_to_core.py`,
   dev only) which keeps skipping it until the core gets a `highlight` column (noted follow-up — avoids
   mis-folding the star into `notes`). `panel.js` comment fixed (comment-only, no behavior change).
   Verified by a synthetic dry-run: a `highlight` edit now bakes (`1 edited`) where it was dropped before.
2. **Seeded the data model** with the current curation: `mvp/scripts/bake_poi_stars.py` reads the
   git-tracked `aop_poi_index.json` and stamps `highlight: true` (+ the blurb as `description` where
   missing) onto the 12 curated served features (3 buildings, 2 trails, 4 cemeteries, 2 visitor, 1 drawn).
   Idempotent; runs after `rebake_canonical.py`.
3. **Viewer reads the ★** (`buildPoiGroups` rewritten): the directory IS `properties.highlight === true`,
   grouped by an inline `STAR_GROUPS` taxonomy. The `aop_poi_index.json` runtime side-join, `fetchPoiIndex`,
   and `resolvePoiFeature` are **deleted** — the read core now reads the SAME field the live page reads, so
   editor and viewer agree on one published source.

**Verified:** `/tmp/verify_viewer_poitab.py` 8/8 PASS, 0 errors — same 7 rows, now ★-driven off the served
`highlight` field. The live page (`main.js` untouched) reads the same baked stars too — durable
convergence (Sprint 08's direction, finally landed).

**Caveat (publish.geojson):** it's PostGIS-exported, so the 2 trail stars baked there are overwritten on
the next `export_publish_geojson.sh`. To make a publish-layer star durable it must be carried into the
publish view (follow-up). File-based layers (buildings, visitor, cemeteries, editor seed) are safe.

### Addendum 2 — 2026-06-13 (ALL star follow-ups closed — no pending star tasks)

1. **Publish-export durability — CLOSED + VERIFIED.** `export_publish_geojson.sh` rebakes ALL the
   reference + publish served files from core, and core has no `highlight` column, so a re-export wiped
   EVERY baked star (not just publish's). The `--check` proved the **only** drift between the served tree
   and a fresh core bake was the stars (everything else byte-identical). Fix: wired `bake_poi_stars.py` as
   the export's final step (the "machine refresh THEN re-apply human curation" order, like
   `rebake_canonical → bake_panel_overrides`), with a new `--check` flag that stamps the `.check` side
   files. **`export_publish_geojson.sh --check` now reports NO REVERT** — the ★ is part of the bake's
   fixed point, so a re-export re-applies it. `aop_poi_index.json` stays the single curation source-of-record.
2. **Live-page bake verifiers — RUN.** `playwright_verify_starred_poi_flip.py` **PASS** — the live page
   (`main.js`, untouched) reads the baked `highlight` and shows the curated ★ set (visitor 2/2, a cemetery
   row renders, the removed wholesale unions stay gone). Editor + read viewer + live page all read the SAME
   published field. **`playwright_verify_baked_pois.py` FAILS on 2 — but STALE:** it expects the "Published
   destinations" wholesale group the **2026-06-08 star-only change removed** (the star-aware verifier
   asserts it's GONE and passes). Pre-dates this work, unrelated (no `main.js`/publish-POI change here);
   retire/rewrite it to the star-only model — flagged, not a star-data-model defect.
3. **DB-core ★ column — UNNECESSARY now (not pending).** The export re-stamp makes the served-file ★ the
   durable layer end-to-end, so the DB sink keeps deferring ★ (no `notes` mis-fold). Carrying ★ into
   `core.features.attrs.highlight` so the SQL bake emits it directly is an OPTIONAL future cleanup
   (documented in both scripts) — not required for correctness or durability.
4. **Quartermaster DRY note (non-blocking):** the inline highlight-pulse block recurs across
   `gotoEventSession`/`gotoMatch`/`flyToFeature` — an optional `highlightFeatures()` extraction, not star
   work; noted, not done.

## Owed / git gate

UNCOMMITTED (the user's gate). `viewer.html` still not in `sw.js` → no `#appVersion` bump owed. Remaining
slate: Locate / Install / version (slice 6), the swap to `index.html` (slice 7). Optional: carry the
cemeteries layer (now ★-baked in the data) to fill the directory's cemeteries group.

## Owed / git gate

UNCOMMITTED (the user's gate). `viewer.html` still not in `sw.js` → no `#appVersion` bump owed. Remaining
slate after 4b: Locate / Install / version (slice 6), the swap to `index.html` (slice 7).

## Addendum 2026-06-14 — Camp POIs group + Hot Rocks Comp Pad starred (rides v92)

User: *"Hot rock comp pad needs to be starred and show up in poi list."* The pad is a
camp **waypoint** (`gold_aop_waypoints_traced.geojson`), but the reader POI directory's
`STAR_GROUPS` only sourced buildings / trails / visitor-support — there was **no camp-
waypoints group**, so starring the feature alone wouldn't surface it. Two parts:

- **Data (★ curation):** Hot Rocks Comp Pad gets `highlight:true` in
  `gold_aop_waypoints_traced.geojson` (the ★ gate `buildPoiGroups` reads). It's the only
  highlighted waypoint, so only it appears — RV sites / cabins / firepit stay out.
- **Viewer:** exposed the loaded waypoints as module-scoped `poiWaypointsData`
  (`viewer_core.js`, assigned right after the `gold_aop_waypoints_traced.geojson` fetch)
  and added a `{ id:'waypoints', label:'Camp POIs', data:()=>poiWaypointsData }` entry to
  `STAR_GROUPS` (after Buildings). No new list engine — same `buildPoiGroups`/`renderPoiTab`
  path, one more source. The row renders name + blurb with no kind/status chips (consistent
  with the 2026-06-14 metadata-removal change).

**Owed — user's git gate (v92→v93 bump):** v92 is now **committed** (HEAD `813d4c9`
"schedule tweaks"; `sw.js VERSION`/`#appVersion` = v92, which shipped the about-rework +
schedule-#tag + POI-metadata work). This change is a shell-asset (`viewer_core.js`) + data
edit *on top of* committed v92 with **no version bump**, so a returning PWA client holding
the v92 caches won't pick it up until `VERSION`/`#appVersion` bump **v92→v93** (re-keys
SHELL_CACHE + DATA_CACHE). Per `no_commits` the bump **and** the commit stay the user's —
flagged here, not performed. (Fresh loads have no stale cache, so the verifier passes; the
bump is what reaches already-cached clients.)

Verified by observation on `:8001` — `brain/output/verify_hot_rocks_in_poi_list.py`
**11/11 PASS**, 0 console errors: live source has exactly `['Hot Rocks Comp Pad']`
highlighted; the "Camp POIs" group renders with count 1 and that single row; clicking it
opens the world popover titled "Hot Rocks Comp Pad" with its description and no
Kind/Status/Source.

**Owed / known gaps (flagged, user's call):**
- **Durability:** the ★ lives on the served gold file (like the Shower House star), not a
  bake. The Affinity waypoint round-trip (`import_illustrator_trace.py`) already strips
  authored waypoint fields (descriptions/kind/tags — see handoff "Owed"), so a re-import
  would strip this `highlight` too. `bake_poi_stars.py` curates the publish/reference POIs
  via `aop_poi_index.json`, not this trace file — so the star is authored-on-served until
  the waypoint round-trip carries authored fields.
- **Editor parity:** the editor POI list (`main.js` `collectStarredDestinations` over
  `FEATURE_LIST_LAYERS`) has no camp-waypoints layer, so Hot Rocks shows in the **reader**
  POI tab only. Adding it to the editor would need a new `FEATURE_LIST_LAYERS` waypoints
  spec (bigger change, not requested). The two lists already source different sets.

## Addendum 2026-06-14 — Gravity Gauntlet starred (rides the same wiring; data-only)

User: *"add this to the map as a pin and star it to make it into the poi list as
#gravity-gauntlet make sure it ends up in the correct gold data source
`Wpt_5-16-26-144753_race_driver_position.gpx` in import dir."* The GaiaGPS export
(`brain/import/Wpt_5-16-26-144753_race_driver_position.gpx`, a single `red-pin-down`
waypoint at lat `35.091910` / lon `-85.751500`, named "race driver position") is the
**raw input**; the **gold data source** it flows into is
`gold_aop_waypoints_traced.geojson`.

Because the Camp POIs `STAR_GROUP` + the `aop-waypoints` pin layer already exist (the Hot
Rocks addendum above), this is **data-only — no JS change**. Added one feature to the gold
waypoints file:

```json
{"name":"Gravity Gauntlet","kind":"comp pad","location_tag":"#gravity-gauntlet",
 "description":"The Gravity Gauntlet — one of Saturday afternoon's scale RC driving challenges at the park.",
 "highlight":true}  // geometry [-85.7515, 35.09191]
```

- **Pin:** all waypoints draw on `aop-waypoints` (Park/Topo only), so the feature renders
  as a pin with no wiring.
- **★ into the POI list:** `highlight:true` lands it in the reader's "Camp POIs" group —
  now holds **two** starred pads (Hot Rocks + Gravity Gauntlet).
- **`#gravity-gauntlet`:** carried as `location_tag` (same field as Firepit's `#firepit`),
  honoring the user's literal tag and making it a real schedule join-target. Blurb is
  source-honest from `brain/import/TBI.copy` (a Saturday-afternoon RC driving challenge);
  `kind:"comp pad"` matches its sibling competition feature and is not visitor-facing.

Verified by observation on `:8001` — `brain/output/verify_gravity_gauntlet_in_poi_list.py`
**16/16 PASS**, 0 console errors: live source has exactly `['Hot Rocks Comp Pad','Gravity
Gauntlet']` highlighted; GG carries `#gravity-gauntlet` + highlight at the GPX coords;
renders as a pin on the Park preset; the "Camp POIs" group reads count 2 with both rows;
clicking the row opens the world popover titled "Gravity Gauntlet" with its blurb and no
Kind/Status/Source.

**Owed:** same gaps as the Hot Rocks addendum — (1) the v92→v93 bump already flagged above
now also covers this data edit (still **not performed**, user's git gate); (2) durability —
the ★ + authored fields live on the served gold file, so the Affinity waypoint round-trip
would strip them; (3) editor-list parity (reader-only). Not re-flagged separately; this
change adds nothing new to the owed list beyond riding it.

**Council (POI/pin pass):** cleared **5/5** (full six — publish-zone gold data) over the
scoped GG hunk — witness (re-ran the verifier, 16/16) · warden (git gate untouched, schedule
genuinely unedited) · quartermaster (data-only, 100% wiring reuse) · mason (well-formed,
non-limiting, coords correct) · scribe (recorded + honest). Receipt:
`brain/output/council/gravity_gauntlet_in_poi_list_20260614.md`.

### Follow-up 2026-06-14 — schedule session linked to the point (was "not done", user asked for it)

User: *"make sure the schedule links to the proper point. there should be examples."* The
`sat-gravity-gauntlet` session ("The Gravity Gauntlet") was tagged `location_tag:"#trails"` —
and `#trails` is **coordinate-less on purpose** (it spans the park), so the schedule join
(`event_schedule_geojson.js`) gave the session a **null geometry**: clicking its calendar row
flew nowhere and opened no popup. The **example** to follow is `#firepit` in
`aop_event_schedule.json` `locations`: a tag whose baked `coordinates` match a waypoint, so its
sessions land on that point. Mirrored it — **data-only, no JS**:

- **`aop_event_schedule.json` `locations`:** added `"#gravity-gauntlet"` (modeled on `#firepit`)
  with `coordinates:[-85.7515,35.09191]` — **identical to the gold waypoint** — `confidence:"high"`,
  `role:"event_stage_start"` (same role `#trails` carried), and a `source` line naming the GPX.
- **The session:** `sat-gravity-gauntlet` `location_tag` `#trails` → `#gravity-gauntlet` (the other
  four `#trails` sessions are untouched).

The transform now emits an `event_anchor` Point at the GG coords and a Point geometry for the
session there, so `gotoEventSession` (`viewer_core.js:1517`) flies to the point and opens the
session popup at it — exactly like Firepit. Verified by observation on `:8001` —
`brain/output/verify_gravity_gauntlet_schedule_link.py` **15/15 PASS**, 0 console errors:
the live join has the anchor + session Point both at `[-85.7515, 35.09191]`; clicking the
"The Gravity Gauntlet" calendar row opens the popup (title "The Gravity Gauntlet", Location
"Gravity Gauntlet", Tag "#gravity-gauntlet"), turns the event-anchor layer on, flies the camera,
and the schedule **anchor renders at the SAME projected point as the waypoint pin** (both
queried at the GG point). Rides the same uncommitted v92→v93 bump; git gate still the user's.

**Council (schedule-link pass):** cleared **5/5** (full six — published event data) — witness
(re-ran the verifier, 15/15) · warden (2 hunks only, other #trails sessions untouched, git gate
intact) · quartermaster (data-only, schedule-join path 100% reuse, mirrors #firepit) · mason
(valid JSON, coords = gold waypoint, role permissive) · scribe (recorded + honest, #firepit is the
real mirrored example). Receipt: `brain/output/council/gravity_gauntlet_schedule_link_20260614.md`.
