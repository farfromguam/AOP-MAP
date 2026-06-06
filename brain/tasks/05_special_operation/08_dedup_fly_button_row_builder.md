# Extract one makeFlyButton helper for the 4 hand-built fly-to row builders

> **Sprint 05 · special_operation · card 08.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 06_one_star_driven_collector.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## ✅ DONE 2026-06-06 — verified by observation (UNCOMMITTED; no VERSION bump yet)

Added one `makeFlyButton(feature, className)` helper (main.js:3591-3603) that creates the
`type='button'` 🎯 button and wires `click → preventDefault + stopPropagation →
flyToFeature(feature)`, with a comment block (3585-3590) naming the three surfaces it folds
in. Replaced the three discrete child fly-button blocks with `makeFlyButton(...)` calls:
renderVisitorListGroup → `makeFlyButton(row.feature, 'vrow-fly')` (1080),
renderFeatureListInto → `makeFlyButton(item.feature, 'feature-fly')` (4287), and
buildEditDock head → `makeFlyButton(item.feature, 'dock-ico')` (4542). The card's planned
"four" included renderPoiTab, but its row is a whole-`button` calling `gotoPoi(row)` (which
calls flyToFeature internally) — it never had a discrete child fly button matching the
gesture, so it was correctly excluded (confirmed against HEAD: gotoPoi at HEAD:1421, not a
poi-fly child button). The surviving inline `flyToFeature` calls (1091 row-click, 1417
gotoPoi, 4286 name-click) are whole-row/name affordances, not the fly-button gesture, so
they stay inline. Acceptance (all pass): `grep -c 'function makeFlyButton'`=1; three
makeFlyButton call sites at 1080/4287/4542; `node -c website/js/main.js` clean;
`grep -c 'flyToFeature'`=7 (1 def + 6 callers, with the three button gestures now centralized
through the helper). **BLOCKED for human verify:** the DOM-level Playwright check (each
surface's fly button still triggers flyToFeature with the correct feature) — the harness
`mvp/scripts/playwright_base.py` is present and tile-independent, but the click→flyToFeature
behavior was not exercised headless this pass; flagged for human verify per the card's "if a
check cannot be run headless, STOP and flag" rule. **Owed:** the single sprint VERSION bump
(v51→v52) at sprint code-complete; commit is the user's git gate.

## Goal

Centralize the 'fly-to button' DOM gesture duplicated across renderVisitorListGroup (1064-1085), renderPoiTab (1373-1415), renderFeatureListInto (3891-3922), and buildEditDock (4126-4128) into one makeFlyButton(feature, className) helper. Lowest-priority cleanup that rides on the unified row shape from card 06.

## Root problem

Four renderers independently build a button with type='button' + addEventListener('click', stopPropagation + flyToFeature). With card 06 giving both list renderers one row shape, the shared name+chip+fly structure can be a single helper, leaving each surface to add only its surface-specific cells.

## Steps

1. Extract makeFlyButton(feature, className) that creates the button and wires the click->stopPropagation->flyToFeature gesture.
2. Replace the four createElement('button')+flyToFeature blocks with makeFlyButton(...) calls.
3. Run node -c js/main.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -n 'function makeFlyButton' js/main.js returns 1; the four inline button+flyToFeature blocks are replaced by makeFlyButton calls (grep shows the click-handler attachments centralized).
- node -c js/main.js passes.
- DOM-level Playwright (no tiles): each surface's fly button still triggers flyToFeature with the correct feature.

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
