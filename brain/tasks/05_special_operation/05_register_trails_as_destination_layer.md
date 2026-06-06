# Register trails as a FEATURE_LIST_LAYERS destination layer so they are starrable like everything else

> **Sprint 05 · special_operation · card 05.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 04_dedup_hotspot_spec_twins.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## Goal

Add a `trails` (aop-trail-network) entry to FEATURE_LIST_LAYERS with highlightable:true and a registerFeatureListLayer('trails', aopTrailNetworkCache) call at load, plus the dedup-per-trail/catalog-lookup logic expressed as spec strategies. This is the prerequisite that lets card 06's single collector cover trails instead of the bespoke wholesale-dump block.

## Root problem

trails are NEVER registered as a feature-LIST layer (the `trails:` key at 2090 is in TUNABLE_LAYERS, a paint registry, not FEATURE_LIST_LAYERS at 2240). So featureListRuntime['trails'] never exists, the right ★ list can never show a starred trail, and buildPoiGroups' trails block (1221) reads aopTrailNetworkCache directly and dumps one row per trail ungated. universal_feature_layer.md stage 3 and star_driven_poi_list.md #1 both require trails to be starrable.

## Steps

1. Add a `trails` spec to FEATURE_LIST_LAYERS with idField (trail_number/name), rowLabel, highlightable:true, and a destination flag (see card 06's contract); move the dedupe-by-trail_number logic (currently buildPoiGroups 1230-1238) and the trailCatalogLookup blurb enrichment into the spec's groups/rowSort/listRow strategies.
2. Add registerFeatureListLayer('trails', aopTrailNetworkCache) at the trail-network load site (near the existing trailheads registration at 9293).
3. Do NOT yet remove the buildPoiGroups trails block — that happens in card 06 when the collector consumes the registered layer. This card only makes trails registrable/starrable.
4. Run node -c js/main.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -n "FEATURE_LIST_LAYERS" plus a structural read shows a `trails` key in the registry; grep -n "registerFeatureListLayer('trails'" js/main.js returns 1.
- node -c js/main.js passes.
- Node harness: after registerFeatureListLayer('trails', <fixture FeatureCollection>), featureListRuntime['trails'] exists and setting a trail feature's highlight=true makes it eligible for the ★ collector (assertable without a map).
- DOM-level Playwright (no tiles, build editor tree first): a trail row with highlight set appears in the right ★ Visitor list.

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
