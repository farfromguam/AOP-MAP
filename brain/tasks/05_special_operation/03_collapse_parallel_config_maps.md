# Collapse the parallel per-layer config maps (FEATURE_NAME_PROP, SERVED_SOURCE, EDITOR_POI_CATEGORIES) onto the spec

> **Sprint 05 · special_operation · card 03.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 02_spec_fields_actions_persist_axis.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## Goal

Remove the standalone per-layer lookup tables that live next to FEATURE_LIST_LAYERS and fold their data onto each spec, so the registry is the single config home. FEATURE_NAME_PROP -> spec.nameField; EDITOR_POI_CATEGORIES -> the editorPois category field's options source (co-located with card 02's field); SERVED_SOURCE -> a spec.servedSource (or persistProperty default) reader.

## Root problem

Three parallel registries sit beside the real one: FEATURE_NAME_PROP (4547, read at 4109/4284), SERVED_SOURCE (4558, read by refreshServedSource at 4565), and EDITOR_POI_CATEGORIES (4488, read by the category branches). These are 'a parallel registry next to the registry' the universal-interface goal collapses; the editable name property and served-refresh resolver should be spec keys, not separate maps that drift on rename.

## Steps

1. Add `nameField` to each spec (default 'name'): editorPois 'name', buildings 'building_label', cemeteries 'name', visitorContext 'name', brandLogos 'name'. Replace `FEATURE_NAME_PROP[layerKey] || 'name'` at 4109/4284 with `spec.nameField || 'name'`. Delete the FEATURE_NAME_PROP map.
2. Fold EDITOR_POI_CATEGORIES into the editorPois category field's options source from card 02; if no external reader remains, it survives only as that field's options factory.
3. Move SERVED_SOURCE entries (srcId+data per layerKey for buildings/visitorContext/brandLogos/cemeteries) onto each spec as a `servedSource` strategy; refreshServedSource reads `spec.servedSource` instead of the SERVED_SOURCE table. Delete the standalone map.
4. Run node -c js/main.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -c 'FEATURE_NAME_PROP' js/main.js returns 0; grep -n 'nameField' js/main.js shows specs declaring it and the two former readers using spec.nameField.
- grep -c 'SERVED_SOURCE' js/main.js returns 0; refreshServedSource reads spec.servedSource (grep confirms).
- EDITOR_POI_CATEGORIES is referenced only inside the editorPois spec block (grep shows no other reader).
- node -c js/main.js passes.
- Node harness: refreshServedSource('buildings') still resolves the buildings source id + data via the spec (assertable without a map).

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
