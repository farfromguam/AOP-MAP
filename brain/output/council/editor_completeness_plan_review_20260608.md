# Council plan-review — editor completeness (restore + complete the right-panel editor, DB-first)

Date: 2026-06-08
Mode: PLAN-REVIEW (review the plan before any code). Chair: Steward. Tier: full six.
Plan: `brain/tasks/09_editor_maturity/editor_completeness.md`.
Result: **FULL CLEAR** (1 round + 1 Mason re-review). Brain-only; no `website/`/`mvp/` touched.

-----

## What the plan proposes

Trigger (user): *"I dont know why the editor was retired. this is a needed surface. put it in. make sure
everything is visible on the right side and editable. consult the council for a full robust plan. No
shortcuts. we are trying to mature the project and not maintain shortcuts or MVP code."*

Restore the right-panel drawn-POI editor (retired `7cd51fa "v50 styles"`, 2026-06-05), spec-complete the
curated-but-uneditable layers (trailheads), reconcile the half-retirement (live create button + stale
help text vs. the deleted node), and make every editable surface persist DB-first — coordinating gold
slice 6's F1/F2 DB doors, not duplicating them. Reference/imagery layers stay visibility-only by design.

## Seat verdicts

**Witness — CLEAR (2 factual corrections, folded).** Re-observed the premise live (injected a drawn POI:
shows on map + left list + right ★ Visitor list, but no editable panel node). Corrections: (1) the plan's
verify recipe `git show 7cd51fa -- panel.js` returns an EMPTY diff — recover the retired node from
`7cd51fa^:website/js/panel.js` instead; (2) the create control is `#placePoiBtn` (not `#placePoi`), and
it sits in a hidden legacy block — the visible affordance is the per-bucket inline "+ add" row. Both
folded. The editability table, the retirement commit, the half-retirement contradiction, and F2 all
verified exact.

**Quartermaster — CLEAR.** Reuse confirmed: restoring is re-registration into the live engine (`refItems`
`:569`, the one inline frame `:1334`, `applyStoredOverrides` `:167`), the retired node is recoverable from
`7cd51fa^`. No duplication of gold slice 6 — the two-card split is clean (this = UI-completeness axis;
gold slice 6 = store-of-record axis, F1/F2 referenced as dependencies). Sprint 09 is a justified NEW
planning surface for the UI axis (the prior audit's "no new sprint" andon was about DB work gold slice 6
already owned; this axis it does not own). Reuses the one apply sink (no second sink). C1/C2/C6 hold at
baseline.

**Mason — ANDON → folded → CLEAR.** The load-bearing catch: the plan's grounding wrongly treated the host
editor as retired. In fact the host engine (`buildEditDock` `:4538`, the `editorPois` array →
`aop_editor_pois_v1`, the draw path) is **live but `display:none` in embedded mode**
(`panel-embed.css:271-273`). So there are TWO live editor engines, and naively re-adding the panel node
would stand up a SECOND editor for one feature class plus a TWIN-STORE desync (panel `OVERRIDES` vs host
`aop_editor_pois_v1`, both writing the one `editor-poi` source — the F6 bug class). `seedLoadedFromHost`
only READS the host source; it does not push panel edits back. **Fold:** corrected grounding (two live
engines); Slice 1 rewritten — 1a consolidate to ONE engine (retire the redundant other; rec the panel
survives), 1b add the missing write-back bridge (new `AOP_HOST_*` property/geometry/delete hooks mirroring
`AOP_HOST_SET_HIGHLIGHT`) so panel edits land in the one host store; acceptance asserts "only one editor
opens" + "host `buildEditDock` path gone"; Fork #0 (which engine survives) added; Slice 4 generic-draw
restore marked DOA (empty `userFeatures` in embedded); Slice 3 trailheads key/label fallback; guardrails
"ONE engine" + "one store per class (no twin stores)". **Mason re-reviewed all six → CLEAR**, grounding
re-verified against live code. C5/R13 non-limiting posture clean throughout (the DB door reuse folds
unknown keys to notes, asserts no-drop, no allowlist).

**Warden — CLEAR (2 execution-time notes, folded).** Scope right: "everything editable" correctly scoped
to first-party/curated (reference/imagery stay visibility-only); generic-draw restore fork-gated, not
creep; all forks left to the user with recs, none pre-decided. Gold slice 6's HELD status respected (F1/F2
referenced as a dependency, not executed/re-carded). Git gate untouched (brain-only, nothing staged).
Reversing the retirement via `cards_not_gospel` is correct (the user disputes the "user dropped it"
record). Folded notes: annotate the `panel.js` retirement comment as reversed rather than delete it;
report the owed `sw.js`/`#appVersion` bump to the user at code time (do not perform/commit).

**Scribe — CLEAR (anchor fix folded).** Executor-runnable: each slice has concrete tile-independent
acceptance; references are the thing, not analogies (gold slice 6 `:565`/F1-F2 `:579-580`, spike audit F2
`:69`/F7 `:141`, the retirement commit, `panel.js` anchors all verified live). Cross-linked (_readme ↔
card ↔ gold slice 6). Voice plain; the user's directive quoted verbatim with the misspelling preserved.
The one stale anchor (`#placePoi` → `#placePoiBtn`) folded.

## Steward synthesis

Full six clear after one round + one Mason re-review. The plan-review earned its keep: the Mason andon
caught a real two-engine/twin-store architecture error that a naive "restore the node" would have shipped
as a second-editor + desync bug — exactly the MVP-shortcut the user said to avoid. The corrected plan
frames the work honestly as *consolidate to one engine + one store of record with a write-back bridge*,
not a cosmetic node re-add. The plan stays on the farm (UI axis; gold slice 6 keeps the DB axis), leaves
every fork to the user, and keeps hands off the git gate.

**Owed (the user's):** decide the forks — especially **Fork #0** (which editor survives; rec: the panel
inline frame, host `buildEditDock` drawn-POI path retired, host array as the single store) — then the
commit-pause (commit the plan) and the ralph-loop in a fresh session. Nothing committed; no shell asset
touched this turn.
