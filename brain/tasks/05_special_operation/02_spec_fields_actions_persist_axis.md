# Stage 2 — migrate the live dock property/field/action axis into spec strategies (no layerKey at call sites)

> **Sprint 05 · special_operation · card 02.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: 01_delete_dead_inline_editor.md. Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## Goal

Push the live buildEditDock per-layer behavior into FEATURE_LIST_LAYERS spec strategies so the dock, setFeatureProperty, and dockGroupContext dispatch through the spec and name no layerKey. Covers: editorPois Category field, buildings Status field, editorPois Duplicate/Delete actions, the setFeatureProperty array-vs-override fork, and the dockGroupContext fork.

## Root problem

editorPois is still a subclass-by-conditional. The 5 live branches remaining after card 01 — dockGroupContext (4096), Category select (4168), buildings Status (4180), Duplicate/Delete actions (4215), setFeatureProperty persist fork (4583) — re-introduce per-layer dispatch that stage-1 (onMutate/persistFlag at 3300/3389) already proved unnecessary. The property-write path at 4583 is a parallel un-migrated copy of the same array-vs-override fork stage-1 eliminated for the flag path.

## Steps

1. Add a `fields` array strategy to the relevant specs: editorPois declares { key:'category', label:'Category', type:'select', options:()=>EDITOR_POI_CATEGORIES }; buildings declares { key:'status', label:'Status', readonly:true, value:(props)=>... }. buildEditDock loops `for (const f of (spec.fields||[]))` and renders via dockFieldRow/dockReadonly, naming no layerKey. Removes 4168, 4180.
2. Add an `actions` capability (or canDelete/canDuplicate) to the editorPois spec; add generic deleteFeature(layerKey,id)/duplicateFeature(layerKey,id) that route mutation through the persistFlag/onMutate seam. buildEditDock loops the declared actions. Served layers omit the capability. Removes 4215; updates deleteEditorFeature/duplicateEditorFeature to be spec-routed, not editorPois-hardcoded.
3. Add a `persistProperty(feature,key,value)` strategy: editorPois => saveEditorPois()+refreshEditorSource(); default => savePositionedFeature()+refreshServedSource(layerKey). setFeatureProperty dispatches through spec exactly like persistFeatureFlagChange. Removes 4583.
4. Add a `groupContext(item)` strategy: editorPois returns the geometry bucket label; default returns spec.label. dockGroupContext dispatches. Removes 4096.
5. Rewrite the seed loop guard at 7132 as a named self-constant (const SELF='editorPois'; if (layerKey === SELF) continue) OR document it explicitly as intentional self-exclusion (not a dispatch site) and exclude it from the branch count.
6. Run node -c js/main.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -n "layerKey === 'editorPois'" js/main.js returns 0 hits in the buildEditDock region (4096/4168/4215) and in setFeatureProperty (4583); grep -n "layerKey === 'buildings'" js/main.js returns 0 (4180 gone).
- After the 7132 guard is renamed: grep -c "layerKey === 'editorPois'" js/main.js returns at most 2 (the two comment lines at 2334/3296 only); if the guard is intentionally left, document it and the count is 3.
- grep -n 'fields:\|actions:\|persistProperty\|groupContext' js/main.js shows the strategies declared on the editorPois and buildings specs.
- node -c js/main.js passes.
- DOM-level Playwright (no tiles, build the dock from runtime/cache data): rendering buildEditDock for an editorPois feature still produces a Category select populated from EDITOR_POI_CATEGORIES plus Duplicate + Delete buttons; for a buildings feature a read-only Status row and neither Duplicate nor Delete.
- Node harness spy: editing a drawn-POI name still calls saveEditorPois+refreshEditorSource; a buildings name edit hits savePositionedFeature+refreshServedSource — asserted by spying those functions, no map load.
- C1 region guard (the exact command, not a naive whole-file `grep -c` which returns ~9 because of the 2334/3296 comments): `python3 -c "import sys;[print(i+1,l.strip()) for i,l in enumerate(open('website/js/main.js')) if \"layerKey === '\" in l and not l.strip().startswith('//')]"` — must list 0 lines inside buildEditDock/setFeatureProperty/dockGroupContext (the 7132 self-guard, if left, is the only allowed survivor).
- `grep` proves `fields:` / `actions` / `persistProperty` / `groupContext` appear INSIDE the editorPois and buildings spec blocks specifically (not just anywhere in the file).

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
