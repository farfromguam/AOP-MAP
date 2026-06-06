# panel.js — replace the cemeteries create-defaults branch and HOST_HIGHLIGHT_LAYER identity map with node-spec fields

> **Sprint 05 · special_operation · card 07.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 06_one_star_driven_collector.md. Touches `website/js/main.js`: no.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## Goal

Remove the two per-layer special cases in panel.js: the `node.id === 'cemeteries'` geom_role stamp in canonicalDefaults (1234) becomes a per-node createDefaults(geomType) hook; the HOST_HIGHLIGHT_LAYER identity map (814) becomes a `hostKey` field on the node spec so hostHighlight/pushTagToHost read node.hostKey directly.

## Root problem

panel.js carries its own per-layer special-casing: canonicalDefaults branches on cemeteries to stamp geom_role='marker', and HOST_HIGHLIGHT_LAYER is a hand-maintained identity map ({buildings:'buildings',...}) whose keys equal their values, existing only to whitelist which node ids bridge star/tag to the host (read at 817/830). Both drift on rename and are the same dispatch-by-literal smell as the main.js work.

## Steps

1. Add a per-node createDefaults(geomType) hook returning extra props; cemeteries returns {geom_role:'marker'} for Point. canonicalDefaults calls node.createDefaults(geomType) and merges; delete the cemeteries branch.
2. Add a `hostKey` (or bridgeStar) field to the node specs that bridge to the host; hostHighlight and pushTagToHost read node.hostKey instead of HOST_HIGHLIGHT_LAYER. Delete the identity map. Since keys already equal values, this is mechanical.
3. Run node -c js/panel.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -c "node.id === 'cemeteries'" js/panel.js returns 0; grep -c 'HOST_HIGHLIGHT_LAYER' js/panel.js returns 0.
- grep -n 'createDefaults\|hostKey\|bridgeStar' js/panel.js shows the spec-side declarations.
- node -c js/panel.js passes.
- Node harness: calling canonicalDefaults for a Point in the cemeteries node still stamps geom_role='marker'; a node with hostKey set still bridges star/tag to the host (assertable without a map).

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
