# Delete dead buildInlineEditor (+ makeEditorLabel) before migrating — shrink the stage-2 surface

> **Sprint 05 · special_operation · card 01.** Executes part of the
> universal feature-layer refactor (`universal_feature_layer.md`). **Sequential** —
> depends on: none (runs first). Touches `website/js/main.js`: yes.

#aop #05_special_operation #editor #refactor #universal #slop

-----

## ✅ DONE 2026-06-06 — verified by observation (UNCOMMITTED; no VERSION bump yet)

Deleted `buildInlineEditor` (was main.js:4278-4440) + its private `makeEditorLabel`
(4442-4446) + the now-stale "kept temporarily" NOTE comment (4275-4277), and reworded
the lone surviving mention at main.js:4011 (`buildInlineEditor` → "old inline-accordion
editor") so the token is gone. 172 lines removed (main.js 10301 → 10129). Confirmed
dead first: zero live callers; `makeEditorAction`/`describeGeometry`/`toggleFeatureEditor`
all have live callers in `buildEditDock` (kept). Acceptance (all pass): `node -c` OK;
`grep -c buildInlineEditor`=0; `grep -c makeEditorLabel`=0; `grep -c "layerKey ===
'editorPois'"`=7 (was 9 — exactly the dead 4328/4427 branches gone); C1 non-comment
branch list dropped 4328/4427, kept the live 4583→4410 + 7132→6959. No DOM check needed
(function was never invoked; the zero-caller grep is the behavior proof, per this card).
**Owed:** the single sprint VERSION bump (v51→v52) at sprint code-complete; commit is the
user's git gate.

## Goal

Delete the dead buildInlineEditor function (main.js:4278-4441) and its private helper makeEditorLabel (4442), removing 2 of the editorPois branches (4328 Category, 4427 Duplicate/Delete) by deletion rather than migration. This must happen FIRST so stage-2 (card 02) does not waste effort 'fixing' dead branches and the branch count it works against is honest.

## Root problem

buildInlineEditor is the superseded inline-accordion editor (comments at 4011 and 4275 say it is no longer called and safe to delete). It has zero live callers but carries two more `layerKey === 'editorPois'` branches (4328, 4427) that duplicate the live buildEditDock branches. makeEditorLabel (4442) is called ONLY from inside buildInlineEditor (4316/4329/4347/4368/4383/4395), so it becomes dead on deletion.

## Steps

1. Confirm zero live callers: grep -n 'buildInlineEditor' js/main.js returns only the definition (4278) and the two comment lines (4011, 4275).
2. Confirm makeEditorLabel is local: grep -n 'makeEditorLabel' shows it called only within the buildInlineEditor body (4316/4329/4347/4368/4383/4395) plus its own def (4442).
3. Delete buildInlineEditor entirely (def through its closing brace) and delete makeEditorLabel.
4. Leave the 4011/4275 comments or update them to note the function was removed.
5. Run node -c js/main.js.

## Observable acceptance (tile-independent — no rendered basemap)

- grep -c 'buildInlineEditor' js/main.js returns 0 (definition gone; no callers ever existed).
- grep -c 'makeEditorLabel' js/main.js returns 0.
- grep -c "layerKey === 'editorPois'" js/main.js drops by exactly 2 from the deletion alone (the dead 4328 + 4427 branches are gone).
- node -c js/main.js passes.
- No DOM/behavior change is required since the function was never invoked — assert no live caller existed via the grep above.

DOM checks run through the existing tracked harness `mvp/scripts/playwright_base.py` (boots the viewer on :8001, queries the DOM). It is tile-independent — it does NOT wait on `networkidle` or call `queryRenderedFeatures`, so it works even though the external basemap tiles are blocked in the sandbox and MapLibre `load` never fires.

## Done when

Every acceptance check above passes and `node -c website/js/main.js` (or `panel.js`) is clean. Record the result on this card; if a check cannot be run headless, STOP and flag for human verify — do not mark done.
