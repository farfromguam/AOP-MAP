# Factor the byte-identical activityHotspots / syntheticActivity spec twins into one makeHotspotSpec helper

> **Sprint 05 · special_operation · card 04.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 03_collapse_parallel_config_maps.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## Goal

Collapse the two near-identical FEATURE_LIST_LAYERS specs (activityHotspots 2465-2492, syntheticActivity 2495-2522) — which differ only in label and targetLayers — into a makeHotspotSpec(label, layerPrefix) factory, removing ~24 lines of copy-paste and the duplicated rowLabel/rowSort.

## Root problem

The two specs are structurally identical: byte-for-byte identical rowLabel (intensity_class formatting), rowSort ({high:0,medium:1,low:2}), and groups; they differ only in label and the activity-hotspots-* vs synthetic-activity-hotspots-* targetLayers arrays. The spec comment at 2493-2494 literally says 'mirror the activity-hotspot pipeline. Same shape, same scope.'

## Steps

1. Write makeHotspotSpec(label, layerPrefix) returning the shared spec with targetLayers derived as ['<prefix>-heat','<prefix>-fill','<prefix>-outline','<prefix>-labels'] and rowLabel/rowSort shared by reference.
2. Replace the activityHotspots literal with makeHotspotSpec('Activity hotspots','activity-hotspots') and syntheticActivity with makeHotspotSpec('Simulated Saturday activity','synthetic-activity-hotspots').
3. Verify the registerFeatureListLayer wiring at 7812/7927 and the toggle wiring still reference the same keys.
4. Run node -c js/main.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -c 'intensity_class ?' js/main.js drops from 2 to 1 (the rowLabel pattern lives once in the factory).
- grep -n 'makeHotspotSpec' js/main.js shows one factory def + two call sites.
- node -c js/main.js passes.
- Node harness: registering a synthetic FeatureCollection under each key produces identical row labels and sort order (behavior preserved, no map).

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
