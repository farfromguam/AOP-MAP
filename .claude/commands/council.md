---
name: council
description: Convene the AOP review council over the current diff before declaring work done (or pass "triage" to rank backlog cards for the next swarm).
---

Read `brain/council/completion_gate.md` (for a done-review) or `brain/council/triage.md` (if the argument
is `triage`), then run it as written.

Default (done-review): act as the **Steward** (`brain/council/steward.md`) — pick the tier by risk
(core three: witness·warden·quartermaster; full six for sprint boundaries / publish-zone data / high
risk), spawn each convened seat as a fresh `council-<seat>` subagent over **only this task's diff + the card's
acceptance criteria** (prompted to refute). Scope the diff to the current task's changes — the
coord-board `claim:` (`git diff HEAD -- <claimed paths>`), not the whole working tree — and tell the
seats to ignore hunks owned by another live session ("review that, ignore what is not yours"). A
commingled tree is never grounds to defer. Collect their verdict receipts, and clear only when every
convened seat is `clear`. On a full clear, write the current diff hash to `.claude/.council-cleared`. On
any `andon`, report the grounded issue to the working agent and bounce "done". Report results — never a
question to the user.

$ARGUMENTS

The brain is the source of truth; this command only points to it.
