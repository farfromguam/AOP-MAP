# Council receipt — retrospective over the recent batch (task-scoped rule applied)

Date: 2026-06-14
Chair: Steward (this session)
Trigger: user — *"review our recent work… we should have had the items go past the
council. but because we are working with multiple agents in different areas the council
has been deferred… you get the council together on that and ignore what is not yours."*

## Why this pass happened

The recent work shipped without a clean council pass because two live sessions
commingled the working tree. The receipts prove it in the sessions' own words:
- `handoff/coord/five-item-review.md`: *"No `.council-cleared` written (tree commingled
  with the illustrator session)… Council review owed if/when the two sessions' trees are
  separated."*
- `handoff/coord/six-item-viewer-batch.md`: *"COMMINGLED… tree cover v88, its own
  `.council-cleared` = c91d81a, now STALE because my rename changed the diff."*

The root cause: both the Tier-0 hash and the "review the diff" model spanned the **whole**
`website`+`mvp` tree. Fixed durably this session (see "Rule change" below).

## Scope reviewed

`git diff 305fcc3..HEAD -- website mvp` — 5 commits (illustrator-trace, v84, v86,
medallion-rename, v88): `viewer_core.js` +315, `main.js` +111, `panel.js`,
`data_editor_map.js`, the medallion file-rename sweep across 25+ data files, `sw.js`.
Cards handed to the seats: `tasks/02_edit/_done/six_item_viewer_batch_20260614.md`,
`tasks/01_mvp/_done/landcover_layer.md`.

Tier (Steward call): core-three + Mason — publish-zone-adjacent (rename across every data
tier) + a large read-core logic change. Tier-0 hard check: `node --check` clean on all
four changed JS.

## Seat verdicts

| Seat | Verdict | Risk | One line |
|------|---------|------|----------|
| Witness | clear | low | Live HTTP probe: all 23 geojson return 200 across the rename; sw.js precaches them; v88 in sync. No layer silently 404s. |
| Quartermaster | clear | low | C1=0 / C6=0 / C2=1; the three new scripts extend (`rename_data_medallion.py` imports `stamp_maturity.MATURITY`, no dup). |
| Mason | clear | low | No limiting / row-dropping code; opacity vs multiply separate; no dead code from the rename; idiomatic. |
| Warden | **andon → resolved clear** | medium | Batch spans a third card's work not in the two cards handed the seats. |

### Witness residual (non-blocking)
The cards' headless-render claims (borderless paint, highlight-persist, alert-fires) were
not re-executed this pass; they rest on named, re-runnable Playwright scripts + screenshots
that exist. Re-observe live if a future pass wants it.

### Warden andon — and its resolution
Warden (handed only the two cards) correctly flagged that the 5-commit batch also contains
the illustrator-trace tooling, a new "Shower House" building, and a new rendered "Camp
waypoints" layer — which trace to `tasks/14_illustrator_trace/satellite_illustrator_export.md`
and `tasks/01_mvp/_done/buildings_layer.md`, **not** the two cards it was given.

Steward resolution — **clear**: that third card documents every flagged item
(`aop-waypoints` source+layers, Shower House merge, facility pins, export/import scripts)
with verification artifacts, AND records its own full-council clearance. Verified the
receipts exist on disk (not the card's narration): `brain/output/council/illustrator_trace_export.md`,
`brain/output/council/illustrator_trace_import.md`, plus `verify_waypoints_layer.py`,
`verify_ingest_viewer.py`, and 11 `illustrator_trace/_verify_*.png`. The work was reviewed
against its own card in a prior pass; it was simply outside this retrospective's two cards.

Residual (the user's git gate, not a defect): the five commits commingle three cards' work.
The trace card already records this as *the user's commit + message, left as-is — not the
agent's to rewrite* (`no_commits` / `stay_on_the_farm`).

## Outcome

**Cleared.** All recent work traces to an accepted card; nothing is off-farm; no code
defect found. The one gap the andon exposed was a **review-coverage** gap (a card's work
reviewed against the wrong subset), not a code gap — exactly the failure the rule change
below prevents going forward.

## Rule change shipped this session (the durable fix)

The council is now **scoped to the current task's `claim:`, never to the whole working
tree** — and a commingled tree is never grounds to defer. Codified in:
`council/completion_gate.md` (substantive: "Scoped to your task" + the best-effort
marker note), `council/_readme.md`, `council/steward.md`, `.claude/commands/council.md`,
and `handoff/coord/_protocol.md` (council your claim before draining). The per-task verdict
receipt (this file / the card) is the authority under concurrency; the whole-tree Tier-0
marker is best-effort and may go stale — that is correct, not a bug.
