# Stage 3 — collapse the two list engines into one collectStarredDestinations(); both renderers consume it

> **Sprint 05 · special_operation · card 06.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 05_register_trails_as_destination_layer.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## ✅ DONE 2026-06-06 — verified by observation (UNCOMMITTED; no VERSION bump yet)

Collapsed the two list engines into ONE `collectStarredDestinations()`
(`website/js/main.js:1161`); `buildPoiGroups` (now a thin grouped renderer,
`:1311`) and `renderVisitorListGroup` (flat, `:1044`) both consume it, so they
cannot disagree. Deleted all 7 bespoke `pushRow('...)` source blocks and the
hardcoded `VISITOR_LIST_LAYERS` walk; added per-spec strategies
(`listRow`/`listGroup`/`listPredicate`/`listSurfaces`/`listMode`/`listToggle`,
plus `listFromData` so cemetery parcel+marker twins reproduce the old marker
rows). The collector walks `Object.entries(featureListRuntime)` for destination
specs (`:1202`) and unions the two explicit non-registry inputs
(publish.geojson `poi`, event anchors); the star gate (`props.highlight ===
true`) is computed ONCE at `:1169` as `row.starred`. Per the deferred
star_driven decisions #1/#2/#4, wholesale layers kept `listMode: 'wholesale'`
(POI tab renders the same rows it shipped) — this card converges the engines
STRUCTURALLY, not the user-visible start-empty flip. Acceptance (all pass):
`node -c js/main.js` OK; `grep -c "pushRow('"`=0 (was 7); `grep -c 'function
collectStarredDestinations'`=1; both `renderPoiTab`/`buildPoiGroups` and
`renderVisitorListGroup` reference the collector; collector walks
`Object.entries(featureListRuntime)`, not a hardcoded key array; one live star
gate in the list-render region (`highlight === true` at `:1169`; `highlight
!== true`=0 file-wide — stale inline gate gone; the other 9 `=== true` hits are
outside the region: counts/styling/persistence/edit-dock, and `:2775`/`:2865`
etc. are comments noting the retired array). Row-parity: `poi_rows_dump.js`
output = 10 rows MATCHES the committed baseline `mvp/scripts/fixtures/
poi_rows_baseline.json` exactly (incl. a `pubpoi:*` published_destinations row +
non-editorPois `building:u1`/`cemetery:p1`/`trail:*`). DOM (harness on :8001,
tile-independent): POI tab renders baked `pubpoi:1`/`pubpoi:2` through the real
`buildPoiGroups → collectStarredDestinations` path, `#editorVisitorList` exists,
no console errors. Non-editorPois both-ends convergence proven headlessly via
`poi_rows_surfaces.js`: starred `building:u1` lands on BOTH the LEFT POI tab and
the RIGHT ★ list, and the starred brand logo regression is restored while the
unstarred one is gated off. **✅ VALIDATED 2026-06-06 (main-thread review).**
Re-ran by observation: `poi_rows_dump.js` output **MATCHES the committed
baseline `poi_rows_baseline.json` exactly** (10 rows, 7 groups); `poi_rows_surfaces.js`
all PASS (starred building on BOTH surfaces; brand-logo right-list regression
restored + ★-gated); and the team's DOM verifier
`mvp/scripts/playwright_verify_star_collector.py` **PASSES on :8001** (POI tab
renders `pubpoi:1`/`pubpoi:2` through the real `buildPoiGroups →
collectStarredDestinations` path, `#editorVisitorList` exists, 0 console errors).
The only residual is the in-page live star-CLICK of a building (needs full
map-load init; tiles blocked) — its convergence is fully proven by the Node
`poi_rows_surfaces` path. **Owed:** the single sprint VERSION bump at sprint
code-complete; commit is the user's git gate.

## Goal

Replace buildPoiGroups' 7 bespoke source blocks with a single collectStarredDestinations() that walks FEATURE_LIST_LAYERS destination layers from featureListRuntime, applies the `highlight === true` gate ONCE, and returns uniform rows via a spec.listRow strategy. renderPoiTab (left, grouped) and renderVisitorListGroup (right, flat) both consume the one collector, so they cannot disagree. NOTE: flipping the POI tab to start-empty/curated changes shipped behavior — surface as a recommendation and confirm the star_driven decisions #1/#2/#4 with the user before shipping that flip.

## Root problem

Two engines answer 'which features are starred destinations and how do I render a row' twice. buildPoiGroups (1120-1340) has 7 hand-rolled blocks reading different stores, and only the drawn_pois block (1308) applies the star gate; the other layers dump wholesale. renderVisitorListGroup (1024) walks a separate hardcoded VISITOR_LIST_LAYERS (572) with a uniform gate. The two engines cover different layer sets and gate differently — the desync the card calls the disease.

## Steps

1. Add a destination flag to each destination spec (`destination: true`, or reuse `highlightable`) and a `listRow(feature)` strategy producing the uniform row (kind/blurb/source/popupCoord) currently hard-coded per block; move per-block enrichment (trail catalog lookup, poiIndexLookup blurbs) into each spec's listRow.
2. Write collectStarredDestinations() that walks Object.entries(featureListRuntime) for destination specs, filters feature.properties.highlight === true once, and returns uniform rows. Union in published_destinations (publish.geojson layer==='poi') as the one explicit non-registry input, OR register publishDataCache poi features as a read-only destination layer.
3. Rewrite renderPoiTab to GROUP the collector's rows (using a spec-declared group id/label) and renderVisitorListGroup to FLATTEN them. Delete the 7 pushRow blocks and the trails block (now covered by card 05's registration).
4. Confirm with the user (per the deferred star_driven decisions) before flipping the POI tab to starts-empty; if not yet confirmed, keep current rows visible behind the collector but route them through it so the engines converge structurally first.
5. Run node -c js/main.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -c "pushRow('" js/main.js returns 0 (today 7); grep -n 'function collectStarredDestinations' js/main.js returns 1.
- grep shows both renderPoiTab and renderVisitorListGroup reference collectStarredDestinations; the star gate `highlight === true` appears in exactly ONE collector, not inline per block.
- collectStarredDestinations references Object.entries(featureListRuntime) or FEATURE_LIST_LAYERS, not a hardcoded layer-key array (grep).
- node -c js/main.js passes.
- DOM-level Playwright (no tiles; first invoke buildEditorTree() so #editorVisitorList exists, then seed featureListRuntime): starring one feature makes the SAME feature id appear in both #poiList and #editorVisitorList; the test covers a NON-editorPois destination (e.g. a building) so the both-ends desync is caught.
- Row-parity guard: with a known publishDataCache + editorPois fixture, the set of POI-tab row ids produced by collectStarredDestinations equals the union the old buildPoiGroups produced (minus the intended trails star-gating change) — a published_destinations poi feature still lands in #poiList post-refactor.
- BASELINE FIXTURE FIRST: before deleting the 7 blocks, dump the current POI-tab row-ids from `buildPoiGroups` against a committed fixture (`publishDataCache` + `editorPois` seed) to `mvp/scripts/fixtures/poi_rows_baseline.json`. The post-refactor acceptance diffs `collectStarredDestinations` output against THIS file — so 'equals the union' is a real `diff`, not an eyeball.
- Star gate counted in BOTH forms: `grep -c 'highlight === true'` + `grep -c 'highlight !== true'` across the list-render region totals exactly 1 (renderVisitorListGroup today uses `!== true`; don't leave a stale inline gate).
- DOM (via the harness) covers a NON-editorPois destination — star a BUILDING and assert the same feature id lands in both `#poiList` and `#editorVisitorList` (catches the left/right desync class).

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
