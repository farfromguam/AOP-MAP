# Extract one makeFlyButton helper for the 4 hand-built fly-to row builders

> **Sprint 05 · special_operation · card 08.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 06_one_star_driven_collector.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

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
