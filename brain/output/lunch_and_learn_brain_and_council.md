# Brain Before Agent

## A repo-native operating system for autonomous AI work

Lunch & Learn talk on the AOP brain, the council, and how to replicate both.

**Format:** 35-minute talk + 10-minute discussion  
**Audience:** Engineers, technical leads, and teams using coding agents  
**Thesis:** The brain tells an agent what must stay true. The council challenges the agent when it thinks it has kept that promise.

#ai #agents #brain #council #l-and-l #replication

-----

## Slide 1 -- The problem is not context length

**On slide**

An agent can read the whole repo and still do the wrong work.

The common failures:

- It starts before learning what the project is for.
- It treats stale task prose as current truth.
- It invents a second pattern instead of extending the first.
- It calls something "verified" after checking its own reasoning.
- It finishes in chat, leaving the next contributor blind.
- It asks the user to supervise every reversible step.

**Speaker notes**

Teams often call this a context problem. It is usually an authority and control problem.

More tokens do not tell an agent which document outranks another. They do not distinguish a locked product promise from a rough task card. They do not make a test independent from the implementation that generated it. They do not create a stopping rule.

The AOP project addresses those problems with two linked systems:

1. A **brain** that stores durable, ranked project knowledge in the repo.
2. A **council** that adversarially reviews material work when an agent thinks it is done.

-----

## Slide 2 -- The brain is not "AI memory"

**On slide**

The brain is the project's written operating model.

```text
AGENTS.md
    |
    v
brain/_readme.md
    |
    +--> brain_map.md ------> where to look
    +--> northstar/ --------> what must stay true
    +--> research/ ---------> what we know and why
    +--> tasks/ ------------> what is being changed
    +--> practices/ --------> how we reason
    +--> flows/ ------------> how work moves
    +--> ai_rules/ ---------> how agents collaborate
    +--> handoff/ ----------> what the last session left
    +--> council/ ----------> what challenges "done"
```

**Speaker notes**

Calling this memory undersells it. Memory sounds private, probabilistic, and owned by one model.

The brain is:

- Versioned with the code.
- Readable by humans and every agent harness.
- Organized by authority and purpose.
- Reviewable in the same diff as implementation work.
- Portable enough to move between projects.

The key design decision is that different kinds of truth have different homes. A project promise does not sit beside a session note as if they carry equal weight.

-----

## Slide 3 -- Authority has a shape

**On slide**

```text
             NORTHSTAR
       "What must stay true?"
                 |
       RESEARCH / EVIDENCE
      "What do we know now?"
                 |
              TASKS
       "What are we changing?"
                 |
              CODE
        "What does it do?"
```

Supporting layers:

- `practices/` shape reasoning.
- `flows/` shape execution.
- `ai_rules/` shape collaboration.
- `handoff/` restores session state.

**Speaker notes**

This is the first part to replicate. Do not begin with a giant instruction file.

The authority gradient resolves ordinary conflicts:

- If a task drifts from the northstar, the task changes.
- If research disproves a task assumption, the task changes.
- If running code disproves the docs, the disagreement is named and reconciled.
- If a handoff contradicts a durable rule, the durable rule wins.

The AOP northstar is intentionally short: build a trustworthy, source-traceable map before building an interactive contribution app. That one promise settles a surprising number of product and architecture questions.

-----

## Slide 4 -- Progressive disclosure is the navigation model

**On slide**

Authors **loft** knowledge upward.

Readers **disclose** downward.

```text
Question
  |
  v
TL;DR -> branch readme -> focused doc -> task detail -> code
  ^
  |
Durable lessons are lofted back up
```

**Speaker notes**

Every substantial brain document starts with the gist, then a divider, then depth. Branch readmes explain what lives below them. `brain_map.md` maps the territory. `search_map.md` routes keywords before anyone greps blindly.

This creates a bidirectional loop:

- The writer lifts durable knowledge to the highest useful level.
- The reader descends only as far as the question requires.

The important coupling is this: drift between levels is not merely documentation rot. It is a quality signal. If a northstar says "DB is the store of record" while a browser store still controls publication, the disagreement tells us exactly where work remains.

-----

## Slide 5 -- Boot order is a control, not a suggestion

**On slide**

Every new agent starts in the same order:

1. Brain orientation.
2. Territory map.
3. Session handoff.
4. Product northstar.
5. Collaboration rules.
6. Current task.

Then act.

**Speaker notes**

The boot order is written in `AGENTS.md`. It prevents a stateless agent from beginning in the nearest open file and treating that file as the whole project.

This is spec-first as a ritual, not a hope that somebody reads the docs.

The AOP rules also set a hard collaboration bar: work independently, do not ask for approval on reversible mechanics, stay inside the directed scope, and never cross the user's git gate.

Those rules look tense until the distinction is clear:

- Autonomous on the means.
- Disciplined on the ends.

-----

## Slide 6 -- The brain turns corrections into infrastructure

**On slide**

A repeated correction becomes a durable rule.

Examples:

- "Did you actually observe it?" -> `verify_by_observation.md`
- "Stop asking me every two steps." -> `work_independently.md`
- "Do not create a second editor." -> `editor_is_the_viewer.md`
- "Do not hide unexpected data." -> `no_limiting_code_mvp.md`
- "The harness must point to the brain." -> `harness_adapters_are_thin.md`

**Speaker notes**

The brain grows from real project pain. It is not a speculative policy library.

One file per rule matters. It makes corrections addressable and lets the council partition ownership later. It also keeps the rule's origin and reasoning available, instead of reducing everything to a terse command with no context.

The result is cumulative. The user does not have to repeat the same correction to every agent in every session.

-----

## Slide 7 -- Thin adapters prevent split-brain

**On slide**

```text
Durable truth: brain/

Claude command ------\
Claude skill ---------+--> read brain/<authoritative file>
Claude hook ----------/
Codex / other agent --/
```

The harness routes. It does not own policy.

**Speaker notes**

Every agent platform has its own commands, skills, hooks, and configuration slots. Copying durable instructions into each slot creates multiple sources of truth.

In AOP:

- `.claude/skills/work-task/SKILL.md` points to `brain/flows/work_task.md`.
- `.claude/commands/council.md` points to `brain/council/`.
- Council agent files point to their seat definitions in the brain.
- The Stop hook runs deterministic logic and points back to the completion-gate contract.

This lets different harnesses share one project model. Change the brain, not five adapters.

-----

## Slide 8 -- The council is the rules given faces

**On slide**

The council fires when the working agent thinks it is done.

| Seat | Adversarial question |
|---|---|
| Steward | Is this the right product result? |
| Witness | Was "done" observed in the real system? |
| Warden | Did the diff stay inside the card and git boundary? |
| Quartermaster | Did we extend the system or build a second one? |
| Mason | Is the implementation clean, minimal, and permissive? |
| Scribe | Did the result land durably and honestly? |

**Speaker notes**

The council is not six generic personas discussing code.

Each seat owns a non-overlapping cluster of existing project rules. The names make the lenses memorable, but the authority remains in the brain documents.

The council is also not a user-approval step. It is self-served review. The agent asks fresh critics "what did I miss?" and continues until the evidence-backed objections are resolved.

That supports independent work. It does not replace it.

-----

## Slide 9 -- Cheap checks first, judgment second

**On slide**

```text
Agent says "done"
       |
       v
Tier 0: deterministic gate
  syntax, structural greps, materiality
       |
       v
Tier 1: core three
  Witness + Warden + Quartermaster
       |
       v
Tier 2: full six for high-risk work
       |
       v
Steward clears only when every seat is clear
```

**Speaker notes**

The ordering matters.

Do not spend model judgment on a JavaScript syntax error. Run the parser first. Do not convene six critics for a conversational turn with no material diff. Check materiality first.

AOP uses three tiers:

- Tier 0 is deterministic and automatic.
- Tier 1 catches the most common failures: fake verification, scope drift, and duplication.
- Tier 2 adds implementation restraint, durable record, and product synthesis for high-risk changes.

The gate is tuned, not absolute. The hook hard-blocks unambiguous breakage and nudges once for review. A diff hash prevents the hook from repeatedly nagging after the exact diff has cleared.

-----

## Slide 10 -- The unit of trust is a receipt

**On slide**

```text
SEAT: witness
VERDICT: andon
ISSUE: The rendered result was inferred, not observed.
EVIDENCE: No screenshot, DOM read, or live verifier output.
NEXT: Run the tile-independent verifier and attach the result.
```

Narration is not evidence.

**Speaker notes**

"I reviewed it and it looks good" is not a review artifact.

Each seat returns a small verdict:

- `clear`, or
- `andon` with issue, evidence, and the smallest next step.

Substantial reviews are saved under `brain/output/council/`. That means "the council cleared this" can itself be audited.

If a seat pulls andon, the work is not abandoned and the user is not asked to arbitrate. The producer fixes the grounded issue, then the affected seat re-reviews. Broad fixes can trigger a broader re-review.

-----

## Slide 11 -- Case study: the plan was not ready

**On slide**

Gold migration plan, round 1:

- Witness: the cited verifier was render-bound and could not prove the claim.
- Scribe: "stable key" was ambiguous.
- Quartermaster: the plan invited a second parser.
- Mason: the DB path could silently skip or lose rows.
- Warden: one slice was unbounded and crossed the version-bump gate.
- Steward: no clear.

Four rounds later: full clear.

**Speaker notes**

This is the strongest evidence that the council is not ceremony.

The first gold-migration plan looked complete. All six seats found material defects.

The plan changed:

- It specified exact identity rules.
- It extracted one shared parser for two justified sinks.
- It replaced silent update failure with upserts and count checks.
- It defined tile-independent acceptance.
- It bounded held work.
- It moved version bump language back behind the user's gate.

The council did not merely approve the plan. It made the autonomous execution loop safer to run.

Source: `brain/output/council/gold_migration_review_20260606.md`.

-----

## Slide 12 -- Case study: the facts changed under review

**On slide**

Left POI list diagnosis, first pass:

- "Three wholesale inputs."
- "Nothing is starred anywhere."

Witness observation:

- There were **two** wholesale inputs.
- One seeded local star existed.
- Controlled experiment: total rows changed **10 -> 9** when the seed star was removed.

Conclusion corrected before it became durable truth.

**Speaker notes**

This example matters because the producer had already done a serious code read. The first answer was still wrong.

The Witness did not debate the interpretation. It ran a controlled observation. That changed the model from "the star path is broken" to "the DB-star path is plumbed but unfed, while wholesale inputs dominate the visible list."

The resulting recommendation changed too: author data through the existing DB path rather than write another code fix.

Source: `brain/output/council/left_poi_list_source_consult_20260608.md`.

-----

## Slide 13 -- Case study: review protects the planning surface

**On slide**

DB-first spike audit, first draft:

- Proposed a new sprint.
- Framed two deliberate apply scripts as duplication.
- Used estimated row counts.

Council correction:

- Re-home the work in the existing held Gold Slice 6.
- Preserve the deliberate two-sink split.
- Measure the DB: **160 live / 7 fresh seed / 153 live-only**.

**Speaker notes**

The Quartermaster does more than deduplicate code. It prevents duplicate plans, duplicate stores, and duplicate sources of truth.

The Witness correction is equally important. Estimated counts were wrong even though the live database was available. The council forced measurement before the audit was recorded.

The Scribe then made sure the result landed in the existing card and handoff, instead of living only in a receipt.

Source: `brain/output/council/spike_code_dbfirst_audit_20260608.md`.

-----

## Slide 14 -- What this system is not

**On slide**

It is not:

- A giant prompt.
- A wiki nobody must read.
- Six agents voting on taste.
- A replacement for tests.
- A replacement for human product authority.
- A replacement for the user's diff and git gate.
- A reason to review every typo with six critics.

**Speaker notes**

The brain and council work because their boundaries are explicit.

The brain carries project authority. The council operationalizes that authority at the done boundary. Tests and deterministic checks still do what they do best. Human gates remain human.

The system also avoids role-play as factual authority. A seat is a checklist with judgment, not an oracle. The Witness still needs an observation. The Steward still needs the northstar.

-----

## Slide 15 -- Replicate the brain first

**On slide**

Start with the smallest useful tree:

```text
AGENTS.md
brain/
  _readme.md
  brain_map.md
  search_map.md
  northstar/
    product_northstar.md
  research/
  tasks/
    _readme.md
    _extend.md
  practices/
  flows/
    plan_task.md
    work_task.md
  ai_rules/
  handoff/
    session_context.md
  output/
```

**Speaker notes**

Do not copy AOP's whole brain into another repo. Copy the structure and fill it from that project's real corrections.

Minimum viable brain:

1. One short northstar.
2. One territory map.
3. One search router.
4. One task-card shape.
5. One handoff file.
6. A few collaboration rules born from actual pain.
7. A boot order in `AGENTS.md`.

The first success criterion is simple: a new agent can answer "what are we building, what is current, what is locked, and where do I look next?" without asking the user.

-----

## Slide 16 -- Replicate the authority gradient

**On slide**

Give every document class one job.

| Branch | Question |
|---|---|
| `northstar/` | What must stay true? |
| `research/` | What do we know, and from where? |
| `tasks/` | What are we changing now? |
| `practices/` | How do we reason? |
| `flows/` | How does work move? |
| `ai_rules/` | How should agents collaborate here? |
| `handoff/` | What does the next session need immediately? |
| `output/` | What artifact needs a temporary home? |

**Speaker notes**

Most failed "memory bank" implementations flatten all context into one pile. That makes retrieval harder and conflict resolution impossible.

The branches are useful because they answer different questions. Their boundaries also tell the Scribe where an outcome belongs.

One rule: if a fact matters next session, it cannot live only in chat.

-----

## Slide 17 -- Build rules from failure, not imagination

**On slide**

For each repeated failure:

1. Name the failure plainly.
2. Record the concrete incident.
3. Write the durable rule.
4. Say when it applies.
5. Say what evidence proves compliance.
6. Give it one file.

**Speaker notes**

Bad rule: "Always write high-quality code."

Useful rule: "Verification means observing the running system; re-derived math is not verification."

Bad rule: "Avoid duplication."

Useful rule: "There must be exactly one destination-row collector; both list surfaces render its rows."

Specific rules can later become deterministic checks or council lenses. Vague virtues cannot.

-----

## Slide 18 -- Add the council only after the rules exist

**On slide**

Council design recipe:

1. Inventory recurrent failure modes.
2. Group rules into non-overlapping lenses.
3. Name one chair that holds goal, scope, and termination.
4. Define a binary Definition of Done.
5. Put deterministic checks before model review.
6. Run critics in fresh contexts.
7. Show them only the diff and acceptance criteria.
8. Prompt them to refute.
9. Require receipts.
10. Re-review after grounded fixes.

**Speaker notes**

Do not begin by inventing colorful roles. Begin with failure clusters.

A generic software project might use:

- Product: does the result serve the requirement?
- Verification: was behavior observed?
- Scope: is every hunk traceable to the request?
- Architecture: did the change extend the existing model?
- Implementation: is it idiomatic and minimal?
- Record: can the next contributor recover the truth?

If two seats ask the same question, merge them. Overlap creates cost and false confidence.

-----

## Slide 19 -- Minimal council files

**On slide**

```text
brain/council/
  _readme.md
  completion_gate.md
  steward.md
  witness.md
  scope.md
  architecture.md
  implementation.md
  record.md
```

Each seat needs:

- Rules owned.
- Mandate.
- Review questions.
- Andon conditions.
- Clear condition.

**Speaker notes**

The seat file should be short enough to load into a fresh critic context and specific enough to produce a falsifiable verdict.

Starter seat:

```md
# Verification Seat

Owns: verify_by_observation.md

Mandate: Refute every claim of working behavior that lacks a real observation.

Review:
- Where is the artifact?
- Was the behavior observed or re-derived?
- Were counts measured?

Andon when:
- A material claim has no receipt.

Clear when:
- Every material claim points to a reproducible observation.
```

-----

## Slide 20 -- Minimal completion gate

**On slide**

```md
Done means:

1. Changed code parses or compiles.
2. Project architecture contracts still hold.
3. User-visible behavior was observed.
4. Every diff hunk belongs to the task.
5. No dead or limiting code was introduced.
6. The outcome and remaining work are recorded.
```

**Speaker notes**

Make the gate binary where possible. "Good quality" cannot gate anything. "Every changed JavaScript file passes `node --check`" can.

Avoid one universal score. It will be gamed. A collection of independent pass/fail claims is harder to satisfy cosmetically.

Also state what the gate cannot clear. In AOP, the council cannot commit, push, or replace the user's review. That boundary is part of the design.

-----

## Slide 21 -- The hook should be boring

**On slide**

Hook responsibilities:

- Detect material changes.
- Run cheap deterministic checks.
- Fail open on unexpected hook errors.
- Nudge once per distinct diff.
- Recognize an exact cleared-diff hash.
- Point to the brain.

No durable policy prose in the hook.

**Speaker notes**

Hooks are good at syntax, file patterns, counts, and hashes. They are bad places for nuanced policy.

The AOP Stop hook:

- Ignores non-material turns.
- Parses changed JavaScript.
- Reports structural and version findings.
- Hashes the exact `website/` and `mvp/` diff, including untracked files.
- Stops nudging once that exact diff is cleared.
- Exits safely if the hook itself cannot understand the environment.

Keep the hook replaceable. The completion-gate contract should survive a harness change.

-----

## Slide 22 -- Keep the critics independent

**On slide**

Bad:

```text
Producer explanation -> critic repeats producer explanation -> clear
```

Better:

```text
Northstar + card + diff + artifacts -> fresh critic -> verdict
```

**Speaker notes**

Consistency is not corroboration when every artifact was derived from the same implementation.

The council reduces that risk by:

- Starting fresh critic contexts.
- Withholding the producer's reasoning narrative.
- Asking critics to refute rather than confirm.
- Anchoring each lens to a different source: product promise, observed behavior, task boundary, architecture contract, implementation idiom, durable record.

This does not produce perfect independence. It does prevent the easiest form of self-approval.

-----

## Slide 23 -- Failure modes of the system itself

**On slide**

Watch for:

- Brain rot: stale docs nobody reconciles.
- Rule sprawl: every preference becomes policy.
- Seat overlap: six critics find the same issue.
- Rubber stamps: a seat never pulls andon.
- Ceremony creep: full council on trivial work.
- Receipt theater: verdicts cite no artifacts.
- Common-ancestor tests: code, tests, and docs all copied from one wrong assumption.
- Adapter drift: harness files grow their own policy.

**Speaker notes**

The system is not self-justifying. It needs maintenance.

The cure is the same mechanism:

- Treat drift as signal.
- Delete or merge rules that no longer earn their cost.
- Track which andons changed the work.
- Tune tiers by observed risk.
- Keep the brain authoritative and adapters thin.

The most important health signal is not council pass rate. It is whether grounded review findings materially improve plans, code, evidence, or records.

-----

## Slide 24 -- Adoption path

**On slide**

Stage A -- Brain:

- Add boot order, northstar, map, task shape, and handoff.

Stage B -- Durable corrections:

- Convert repeated user corrections into focused rules.

Stage C -- Manual council:

- Run three lenses over material diffs: verification, scope, duplication.

Stage D -- Completion gate:

- Add deterministic checks and receipts.

Stage E -- Full council:

- Add product, implementation, and record lenses only when the work justifies them.

**Speaker notes**

This can be adopted incrementally. The brain provides value before any multi-agent tooling exists.

The core-three council can run manually in one model if fresh subagents are unavailable, though the independence is weaker. The important behaviors still apply: separate passes, separate criteria, evidence-backed verdicts, and explicit andon.

Automate only after the manual flow is useful.

-----

## Slide 25 -- Live demo

**On slide**

One question, top to bottom:

> "Why is this list showing data that is not in the database?"

Demo path:

1. `AGENTS.md` boot order.
2. `brain/search_map.md` routing.
3. Northstar architecture contract C3.
4. Current task and handoff.
5. Running-system observation.
6. Council receipt correcting the first answer.
7. Durable card update.

**Speaker notes**

Use the left-POI-list case.

The point is not the map code. The point is how the system narrows:

- The search map gets us to the relevant contract and card.
- C3 tells us browser state cannot be publication truth.
- The task explains the intended star path.
- Observation shows ten actual rows and their sources.
- The Witness catches two wrong claims.
- The corrected conclusion lands in a receipt, card, and handoff.

The audience should see the loop, not just the folder tree.

-----

## Slide 26 -- The takeaway

**On slide**

The brain makes autonomy possible.

The council makes "done" expensive to fake.

Together:

- Authority is explicit.
- Context is progressively disclosed.
- Corrections survive sessions.
- Agents act without constant supervision.
- Review attacks claims instead of admiring prose.
- The user keeps the final gate.

**Speaker notes**

The useful unit is not a smarter agent. It is a better-governed project.

The brain lets an agent recover product intent, evidence, current work, and collaboration boundaries without asking the user to replay the project.

The council makes the agent earn completion with independent lenses and observable artifacts.

That is the replication target: not this project's exact files, names, or rules. Replicate the authority gradient, the boot ritual, the durable correction loop, and the adversarial done boundary.

-----

# Presenter Appendix

## One-page replication checklist

### Brain

[ ] `AGENTS.md` defines an exact boot order.  
[ ] One short northstar states what must stay true.  
[ ] `brain_map.md` maps the branches and names current authority.  
[ ] `search_map.md` routes common questions to focused docs.  
[ ] Research, tasks, rules, and handoff have separate homes.  
[ ] Task cards carry scope, acceptance, and reproducible verification.  
[ ] Repeated corrections become one-rule-per-file durable rules.  
[ ] Harness skills and commands point to the brain instead of copying it.  
[ ] Outcomes that matter next session are written before the turn ends.  

### Council

[ ] Review lenses come from actual failure clusters.  
[ ] Seat ownership does not overlap.  
[ ] One chair owns goal, scope, tier, synthesis, and termination.  
[ ] Deterministic checks run before model judgment.  
[ ] Critics see the diff and acceptance criteria, not the producer's sales pitch.  
[ ] Critics are prompted to refute.  
[ ] Every seat returns `clear` or `andon` with evidence and next action.  
[ ] Grounded andons bounce done and trigger re-review.  
[ ] Substantial verdicts are stored as receipts.  
[ ] Clearance applies to the exact reviewed diff.  
[ ] Human review and git boundaries remain intact.  

## Suggested starter `AGENTS.md`

```md
# AGENTS

Before acting:

1. Read `brain/_readme.md`.
2. Read `brain/brain_map.md`.
3. Read `brain/handoff/session_context.md`.
4. Read `brain/northstar/product_northstar.md`.
5. Read `brain/ai_rules/`.
6. Read the current card named in `brain_map.md`.

Then take the request end-to-end:
read -> change -> observe -> record -> report.

Stop only for a real product fork, a destructive action, or missing authority
that cannot be discovered from the repo.
```

## Suggested verdict receipt

```md
SEAT: <seat>
VERDICT: <clear|andon>
ISSUE: <one specific defect, or "none found">
EVIDENCE: <file, command result, screenshot, DOM read, test output>
NEXT: <smallest action that would settle the issue>
```

## Suggested review prompt

```text
Act as the <seat> defined in brain/council/<seat>.md.

Review only:
- the task's goal and acceptance criteria
- the current diff
- the named verification artifacts

Try to refute the claim that this work is done.
Do not rely on the producer's explanation.
Return the verdict receipt exactly.
```

## Questions for discussion

1. Which corrections does your team currently repeat to agents?
2. Which document in your repo actually outranks a task ticket?
3. What does your team call "verified" that is really inferred?
4. Which two systems in your codebase solve the same problem?
5. What work routinely finishes in chat but never reaches the repo?
6. Which review checks are deterministic enough to move ahead of human or model judgment?
7. What must remain a human gate?

## Source path

Core local sources used for this talk:

- `AGENTS.md`
- `brain/brain_map.md`
- `brain/search_map.md`
- `brain/northstar/map_northstar.md`
- `brain/northstar/source_register.md`
- `brain/northstar/editor_architecture_contracts.md`
- `brain/practices/progressive_disclosure_spec.md`
- `brain/ai_rules/`
- `brain/flows/`
- `brain/council/`
- `brain/output/council/gold_migration_review_20260606.md`
- `brain/output/council/gold_migration_slice1_review_20260606.md`
- `brain/output/council/left_poi_list_source_consult_20260608.md`
- `brain/output/council/spike_code_dbfirst_audit_20260608.md`
