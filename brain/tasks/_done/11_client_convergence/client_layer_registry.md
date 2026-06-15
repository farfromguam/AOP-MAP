# Client layer registry — ALREADY MET (C1=0). Corrected finding + the real punch list.

This card was opened to "converge the client's per-layer sprawl onto one descriptor." On inspection
(2026-06-10) **that convergence is already done and meets its own enforced contract** — so this card
does NOT drive a refactor loop. It records the finding, the small honest residual, and the real
remaining work that is NOT this.

**Do not spin a ralph loop to redo the convergence.** That would be exactly the make-work the user is
exhausted by.

-----

## The finding (verified by observation, not the opening grep)

The opening assessment read a raw grep (~800 per-layer name hits) as adapter slop. Direct contract checks
correct that:

- **C1 = 0** — `python3 -c "[print(i+1,l.strip()) for i,l in enumerate(open('website/js/main.js')) if \"layerKey === '\" in l and not l.strip().startswith('//')]"` → no rows. No per-layer behavior branches at call sites.
- **C6 = 0** — no `class [A-Z]` hierarchy in main.js.
- The `FEATURE_LIST_LAYERS` registry (main.js:2187) is a rich declarative descriptor — list mode, predicates,
  row builders, served-source strategy, name field, fields, targets — all co-located per layer, with
  generic spec-driven functions (`positionedFeatureIdFor`, `savePositionedFeature`, `renderFeatureList`)
  dispatching through it. `TUNABLE_LAYERS` (main.js:1711) is the paint descriptor. Prior sprints (06/08/09)
  built this. The "one descriptor the data has" already exists in the client.

So the urgent paper-mache fear about the client is **not borne out**. The bones are load-bearing.

## The honest residual (optional, not urgent)

- **File size / modularity.** `main.js` is one 10.6k-line file. That is hard to navigate, but it is not
  un-converged — splitting it into modules is an *optional* ergonomics refactor, verifier-gated, that can
  wait. It is not the user's "looks good only from the front" problem.

## The real punch list (what actually remains — sorted by who it needs)

**Needs the user's judgment (curation / permission / real-world data — by the northstar's own design):**
- **Publishability gap.** Only 6 of 160 `core.features` pass the publish gate. The spine is built; the
  *published* map is thin. Which features are publishable is a permission/curation call only the user can
  make (`northstar/source_register.md`). This is the biggest real product gap.
- **Real data owed** (MVP backlog, `tasks/01_mvp/_readme.md`): real source-backed trail data (item 9),
  QGIS connected to `localhost:55432` (item 3), the 600-acre claim vs parcel envelope (item 8).

**Autonomous + verifiable (a loop CAN do these — each behind an existing verifier):**
- **Sprint 09 editor maturity** (`../../09_editor_maturity/editor_completeness.md`): restore the retired
  drawn-POI editor node, give trailheads/event-anchors a list. Council-reviewed plan already exists.
- **Dead scratch cleanup**: ~80 mockup/compare `*.html` in `website/` (bottombar_v*, editor_unified_v*,
  floatgroup_v*, add_any_type_v*, …) the brain already routes for retirement. Safe (not loaded by the
  app, git-recoverable), visible declutter — but confirm each is unreferenced before removing.

## Acceptance

[x] Convergence contract confirmed met (C1=0, C6=0) — recorded, no redundant loop spun.
[ ] (If pursued) Sprint 09 editor-maturity slices land behind their verifiers.

## Notes

No commits without the user's git gate (`no_commits.md`). The convergence sprint premise is closed by
this finding; the live work moves to the punch list above.
