# Stage 3 — collapse the two list engines into one collectStarredDestinations(); both renderers consume it

> **Sprint 05 · special_operation · card 06.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 05_register_trails_as_destination_layer.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

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
