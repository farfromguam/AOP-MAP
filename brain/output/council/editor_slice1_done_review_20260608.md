# Council done-review — Sprint 09 Slice 1 (drawn-POI editor restored, one engine + one store)

Date: 2026-06-08
Mode: DONE-REVIEW over the diff. Chair: Steward. Seats: Mason + Witness (the load-bearing seats for an
editor-architecture change; the plan was already full-six cleared and this executed exactly that Slice 1).
Result: **CLEAR** (Mason clear; Witness andon → 3 folds → re-review clear).

-----

## What was reviewed

`main.js` — 3 bridge hooks (`AOP_HOST_SET_FEATURE_PROPS`/`_GEOM`/`AOP_HOST_DELETE_FEATURE`), pure
delegation to the spec-routed host writers. `panel.js` — restored the Drawn POIs (`editorPois`) node
(`hostKey:'editorPois'`+`hostEdit:true`); `commitChange`/`persistDelete` route to the bridge for hostEdit
nodes (before the OVERRIDES path, returns). `sw.js`+`index.html` v57→v58. New
`playwright_verify_drawn_poi_editor.py`; updated `playwright_verify_data_groups_embed.py`.

## Verdicts

**Mason — CLEAR.** One store of record: the hostEdit branch sits after the `isUserFeature` guard and
BEFORE the served OVERRIDES path, and `return`s — no twin write (panel.js:146/170). The bridge adds no
editing logic — pure delegation to `setFeatureProperty`/`deleteFeature` → the editorPois spec's
`persistProperty`/`removeFeature` → `saveEditorPois`. Consolidation complete: `buildEditDock` is
CSS-hidden in embedded (`panel-embed.css:273`) — not a user-reachable second editor; left in place
because it is still the standalone editor (correct scoping, not dead code). C5/R13: all three hooks
fail-safe (try/catch → false, no throw; missing feature → false). C1/C6: no `layerKey===` branch, no
`class`; routing is spec-driven via `node.hostEdit`. node --check passes.

**Witness — ANDON → folded → CLEAR.** Confirmed the product by observation (one store, no twin-store
leak, only the panel editor opens, no product regression). Three gaps, all folded: (1)
`playwright_verify_data_groups_embed.py` was RED — it asserted the 2026-06-05 retirement this card
reverses → updated to the new contract (8 sections incl Map editor, Drawn POIs present, generic draw
gone) → PASS; (2) the durable verifier deleted via the bridge and never read `aop_panel_overrides_v1` →
now drives DELETE through the panel UI 🗑 and asserts the twin-store check (reads
`aop_panel_overrides_v1`, no `editor-poi:` entry) → PASS; (3) the Slice-1 outcome wasn't recorded →
handoff entry + card "SLICE 1 — DONE" block added. Re-reviewed all three by observation (with
triangulation on a false-negative `ls`) → CLEAR. `playwright_verify_starred_poi_flip.py` still PASS.

## Steward synthesis

Mason + Witness clear. The slice executed exactly the council-cleared Slice 1 (panel survives, one store,
write-back bridge), verified end-to-end through the real UI, with the no-twin-store and UI-delete
assertions now carried by the durable verifier (not the Witness's re-probe). Scope/git-gate clean: the
retirement comment was annotated (not deleted), the v58 bump performed, the commit left to the user.
**OWED (the user's git gate):** the commit (`main.js`+`panel.js`+`sw.js`+`index.html` + the new/updated
verifiers + brain) with the v58 bump. **NEXT:** Slice 2 (reconcile the half-retirement — the create
affordance over the one store), Slice 3 (trailheads), Slice 5 (DB doors — gold slice 6).
