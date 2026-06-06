# Council Review Flow

TL;DR: When a unit of work is "done", convene the review council over the diff before you believe it.
The flow, the seats, the verdict schema, and the andon-bounce all live in `../council/`.

#aop #flow #council #review #done

-----

This flow is a thin pointer. The durable content is the council itself:

1. Read `../council/completion_gate.md` — the Definition of Done, the tiers, the verdict receipt.
2. Act as the Steward (`../council/steward.md`): pick the tier by risk, then review the diff through the
   convened seats in **fresh, adversarial** contexts that see only the diff + the card's acceptance
   criteria (`../council/witness.md`, `warden.md`, `quartermaster.md`, and for full council `mason.md` +
   `scribe.md`).
3. Any seat's `andon` bounces "done": fix the named issue, re-review that seat, then proceed.
4. Report the verdict as a **result**, never as a question to the user (`../ai_rules/work_independently.md`).

In Claude Code this is the `/council` command (`.claude/commands/council.md`) and the `Stop`-hook gate
(`.claude/hooks/council-gate.sh`). For picking the next sprint's cards, see `../council/triage.md`.
