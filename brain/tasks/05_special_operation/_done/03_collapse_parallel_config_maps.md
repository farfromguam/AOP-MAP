# Collapse the parallel per-layer config maps (FEATURE_NAME_PROP, SERVED_SOURCE, EDITOR_POI_CATEGORIES) onto the spec

> **Sprint 05 · special_operation · card 03.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 02_spec_fields_actions_persist_axis.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## ✅ DONE 2026-06-06 — verified by observation (UNCOMMITTED; no VERSION bump yet)

Collapsed all three parallel config maps in `website/js/main.js` onto the
`FEATURE_LIST_LAYERS` specs. Added `nameField` to each spec (editorPois/cemeteries/
visitorContext/brandLogos `'name'`, buildings `'building_label'`) and replaced both
`FEATURE_NAME_PROP[layerKey] || 'name'` readers with `spec.nameField || 'name'`
(buildEditDock @4251; the dead buildInlineEditor reader is gone with card 01). Added a
lazy `servedSource` strategy to the four served specs (`() => ['fema-buildings',
buildingsData]`, `['visitor-context', …]`, `['brand-logos', …]`, `['cemeteries',
cemeteryData]` — lazy so each reads its `let` assigned during layer load); editorPois
declares none (its writes flow through refreshEditorSource). `refreshServedSource` now
reads `spec.servedSource` and no-ops on absence. Deleted both standalone maps. Folded
EDITOR_POI_CATEGORIES into the editorPois spec's `category` select field's lazy
`options: () => EDITOR_POI_CATEGORIES`; it now has no external reader — only the spec
field plus its own const def survive. Acceptance (all pass): `node -c website/js/main.js`
OK; `grep -c FEATURE_NAME_PROP`=0; `grep -c SERVED_SOURCE`=0; `grep -c
EDITOR_POI_CATEGORIES`=3 (the spec field @2385 + its two-comment mention @2380 + own def
@4456 — no buildEditDock branch reader remains); `grep -n nameField` shows the five specs
declaring it and buildEditDock reading `spec.nameField`; `grep -n` confirms
refreshServedSource reads `spec.servedSource()`. **✅ VALIDATED 2026-06-06 (main-thread
review — block CLEARED).** Evaluated the REAL `FEATURE_LIST_LAYERS` literal in Node:
`buildings.servedSource()[0]` resolves to **`'fema-buildings'`** (and `editorPois` declares
none, writing via `refreshEditorSource`), so the source-id+data resolution that
`refreshServedSource` reads off the spec is confirmed by observation — the only un-exercised
step is MapLibre's own `map.getSource(...).setData(...)`, which is map-load-gated (tiles
blocked) and not part of this refactor. `nameField` also confirmed on all five specs
(buildings `'building_label'`, the rest `'name'`). **Owed:** the single sprint VERSION bump
(v51→v52) at sprint code-complete; commit is the user's git gate.

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
