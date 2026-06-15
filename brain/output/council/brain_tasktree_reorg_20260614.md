# Council receipt — brain task-tree reorganization (2026-06-14)

**Result: FULL CLEAR** (core three + Scribe). Steward chaired.

## Scope (this task's claim only)
Brain housekeeping, no product code/data. User directive: *"if there are done items not
in the _done dir of the sprint it needs to be moved. if the whole sprint is done, then that
sprint can be moved to the _task done."* User chose "relocate + rewrite refs" for the done sprints.

- 2 done feature cards → `tasks/01_mvp/_done/` (`gold_promotion_pins_curation_v90.md`, `poi_search_click_links.md`).
- 8 fully-done sprints relocated whole → `tasks/_done/`: 02_edit, 04_edit, 05_special_operation,
  07_tables, 08_data_normalization, 11_client_convergence, 12_field_schedule_editor, 13_viewer_extraction.
- 99 deterministic link rewrites + 6 manual ref fixes across active brain docs (incl.
  `northstar/editor_architecture_contracts.md`, `search_map.md`, `research/viewer.md`, `tasks/_readme.md`,
  `brain_map.md`, `handoff/session_context.md`).
- New tools: `output/relink_done_sprints_20260614.py`, `output/verify_brain_links_20260614.py`.
- NOT in scope (other sessions' commingled uncommitted work, ignored by all seats): `website/js/viewer_core.js`,
  `mvp/scripts/*illustrator_trace.py`, `output/illustrator_trace/*`, `tasks/14_illustrator_trace/*`,
  `output/verify_{buildings,trace}_roundtrip*.py`, `output/*trails_gold_publish*`.

## Verdicts

SEAT: witness — VERDICT: clear
Ran `verify_brain_links_20260614.py` → ACTIVE refs to a moved sprint = 0. Independently normpath-resolved
all 27 deep-`../` brain links the verifier skips (its blind spot) → 0 broken; relink idempotent (2nd dry
run = 0 rewrites); 8 dirs + 2 cards present/non-empty, old paths `D`-deleted, the one mutated moved card
differs only by correct `../` depth (321 lines intact). NEXT (non-blocking): have the verifier resolve
above-brain-root links instead of `continue`-skipping them, so its "0" self-covers the deep-`../` class.

SEAT: warden — VERDICT: clear
Git gate clean: HEAD unchanged at `453616d "v94 speed"`, nothing staged, the new scripts contain zero git
calls. History not rewritten (`output/council/` + dated handoff archives untouched). 8 sprints correctly
sorted (moved ones carry done markers; left-active ones retain open work). No website shell asset changed
by this task → no `sw.js`/`#appVersion` bump owed.

SEAT: quartermaster — VERDICT: clear
No reinvented tooling (searched repo — no pre-existing brain-link checker to reuse). Reused the existing
convention: each moved sprint keeps its own `_done/`; spine cards (`05.../universal_feature_layer.md`,
`08.../star_driven_poi_normalization.md`) stayed at sprint root with DONE banners, not duplicated. No
`_done/_done` nesting, no orphaned duplicates (old paths gone). Product structural greps unaffected
(C1=0, C6=0, one `FEATURE_LIST_LAYERS`, one `collectStarredDestinations`).

SEAT: scribe — VERDICT: clear
Convention durably recorded in `tasks/_readme.md` (two move rules + spine-card exception + archive list);
`brain_map.md` points to `tasks/_done/`; handoff "Latest" is accurate plain-voice (directive verbatim,
what moved, refs rewritten, history left stale by user's call, no bump owed, commit is the user's, artifact
named). No false record — load-bearing "0 broken" claim re-verified by running the artifact.

## Clearance note (Tier-0 marker deliberately NOT written)
The `.claude/.council-cleared` Tier-0 marker hashes `website/`+`mvp/`, which this brain-only task did not
touch. The website/mvp working-tree changes are another session's uncommitted trace/load-pipeline work
that itself owes a council review (per the handoff). Writing the marker would falsely signal that diff is
cleared. Per `completion_gate.md` (the marker is best-effort under concurrency; the per-task verdict receipt
is the durable authority), THIS receipt is the clearance. The Tier-0 hook may nudge again on the next stop
for the un-reviewed website/mvp work — correct behavior, not this task's to clear.
