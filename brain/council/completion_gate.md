# The completion gate — what fires when an agent thinks it's done

TL;DR:
- This is the **Definition of Done** for AOP work, and the contract for the hooks that enforce it.
- **Tier 0** is deterministic and automatic (the Stop hook): cheap, binary checks run the instant a main
  agent tries to stop with material changes. Unambiguous breakage hard-blocks; the rest is advisory.
- **Tier 1/2** is the council ([[_readme]]): the agent convenes the seats over its own diff in fresh
  contexts, each seat returns a small **verdict receipt**, and any `andon` bounces "done" back.
- The gate is **specific and binary** by design — no checklist theater, no single gameable metric.

#aop #council #gate #done #hooks #stop

-----

## The Definition of Done (binary — each line is pass/fail, not vibes)

A unit of AOP work is "done" only when **all** of these hold. Make each one objectively checkable; that
is the antidote to checklist theater and to Goodhart-gaming a single number.

1. **Compiles.** `node --check` passes on every changed `website/js/*.js`.
2. **Contracts hold.** The C1 region grep is at target (0 non-comment `layerKey === '` branches in
   `main.js`, or 1 for the kept `editorPois` self-guard); no new `class [A-Z]` in `main.js`; no second
   destination-row builder; no new editor `*.html`. (C1/C2/C6 — Quartermaster.)
3. **Observed, not narrated.** Every "works / verified / done" points at a real observation of the
   running system, with the artifact named (screenshot, live DOM/paint read, Playwright output, real
   bake). Re-derived math and estimates are not verification. (C4 / verify_by_observation — Witness.)
4. **On the farm.** Every diff hunk is traceable to the card; adjacent work is reported, not done; the
   git gate is untouched (no mutating git, no attribution). (Warden.)
5. **Non-limiting & clean.** No constraint / validator / row-dropping filter added; no spec strategy
   that throws on an unknown value; no dead code; idiomatic to its file. (C5 — Mason.)
6. **Recorded.** The outcome is written to the brain — card → `_done/` with its acceptance result,
   `handoff/session_context.md` updated, what's owed and what's the user's git gate (the `vNN` bump,
   the commit) stated plainly. (Scribe.)

The user's git gate is **not** part of "done" the agent can clear — the commit and the version bump stay
the user's (`no_commits`, `stay_on_the_farm`). The gate's job is to make the diff clean *before* it
reaches the user, never to push it past them.

## Tier 0 — the objective gate (the Stop hook, deterministic)

`.claude/hooks/council-gate.sh` is a `command`-type `Stop` hook. The instant a main agent tries to
finish a turn, it:

1. **Loop guard.** If the hook payload's `stop_hook_active` is `true`, exit 0 immediately — never trap
   the agent in a re-block loop.
2. **Materiality.** Read-only `git status`/`diff` (allowed). If nothing material changed under
   `website/` or `mvp/`, exit 0 silently — a conversational turn is not a "done."
3. **Hard checks (block on real breakage only).** `node --check` each changed `website/js/*.js`. A syntax
   error exits 2 with the error on stderr — that is unambiguous and worth stopping for.
4. **Advisory checks (carried into the nudge, never block).** The C1 region grep count; whether a shell
   asset changed without a `sw.js` / `#appVersion` bump (the bump is the **user's**, so this is a
   reminder, not a gate). These are findings, not failures.
5. **Clearance marker.** If `.claude/.council-cleared` holds a hash equal to the current diff hash, the
   council already cleared *this exact diff* — exit 0. Any new change invalidates the hash (so you can't
   clear once and keep coding — Goodhart-resistant). **The hash is computed EXACTLY as** (the hook,
   `council-gate.sh`): `sha1( git diff HEAD -- website mvp  +  git status --porcelain -- website mvp )`
   — scoped to `website`/`mvp`, and the porcelain term means **untracked** new files under them are part
   of the hash too. When the Steward clears, write the marker with that same formula (NOT
   `git hash-object`, NOT an all-paths diff) or it will never match and the gate keeps nudging:
   `python3 -c "import subprocess,hashlib; g=lambda *a: subprocess.run(['git',*a],capture_output=True,text=True).stdout; open('.claude/.council-cleared','w').write(hashlib.sha1((g('diff','HEAD','--','website','mvp')+g('status','--porcelain','--','website','mvp')).encode()).hexdigest())"`
6. **Nudge once.** Otherwise exit 2 with stderr instructing the agent to **convene the council**
   (`/council`) over the diff before declaring done, with the advisory findings inline. Because of the
   loop guard, this fires at most once per stop — it never babysits.

The hook holds **no rule content** of its own (`harness_adapters_are_thin`) — it runs the deterministic
checks and points at this file.

## Tier 1/2 — convening the council (the LLM critics)

Driven by `/council` (`.claude/commands/council.md`) or run directly by the working agent. The rules,
from the evidence base:

- **Fresh, independent contexts.** Each seat is a separate subagent (`.claude/agents/council-*.md`) that
  sees **only the diff + the card's acceptance criteria** — not the reasoning that produced the change.
  This defeats the producer's blindness to its own errors and self-preference bias.
- **Prompted to refute.** Each seat tries to find where the work is *wrong* against its lens, not to
  confirm it's right. A seat that only ever clears is rubber-stamping.
- **Tier by risk** (the Steward chooses): **core three** (Witness · Warden · Quartermaster) by default;
  **full six** for sprint boundaries, publish-zone data, or anything high-risk.
- **Jury, not solo.** The Steward aggregates the seats' verdicts; clearance requires every convened seat
  `clear`. One real `andon` bounces "done."

### The verdict receipt (each seat returns this — never a narrated "looks good")

```md
SEAT: witness
VERDICT: andon            # clear | andon
ISSUE: "trail-fade verified" rests on re-run interpolate math, not an observed render.
EVIDENCE: no screenshot / live getPaintProperty read in the card; only a JS re-derivation.
NEXT: hold the camera at trail 41, read getPaintProperty live, attach the shot — then re-review.
```

Receipts are the artifact the gate trusts — store them under `brain/output/council/` when the review is
substantial, so a "the council passed" claim is itself backed by a receipt, not a narration. On a full
clear, `/council` writes the current diff hash to `.claude/.council-cleared` so Tier 0 stops nudging for
that diff.

### The andon bounce (the only regime where self-correction reliably works)

A seat's `andon` does not end the task — it returns grounded feedback for the next iteration. The working
agent fixes the named issue, then the affected seat **re-reviews** (not the whole council, unless the fix
was broad). Self-correction works when it's anchored to a real external signal; the receipt is that
signal.

## The dials (tune it; don't rip it out)

- **Advisory vs blocking.** Default: hard-block only on `node --check` failure; everything else nudges
  once. To make the council nudge advisory-only (never exit 2), flip `BLOCKING=0` at the top of
  `council-gate.sh`. To make a clean council pass *required* before any stop on material changes, that's
  the blocking default already — it self-terminates via the loop guard and the clearance marker.
- **Scope.** Tier 0 watches `website/` + `mvp/`. Widen/narrow the `MATERIAL` globs in the hook.
- **Disable.** Remove the `Stop` block from `.claude/settings.local.json`, or `chmod -x` the script. The
  council still exists as a brain discipline and an on-demand `/council` even with the hook off.

## Related

- [[_readme]] — the council, the seats, the evidence base.
- [[triage]] — the council selecting backlog cards for the next swarm.
- `.claude/hooks/council-gate.sh` · `.claude/commands/council.md` · `.claude/agents/council-*.md` — the
  thin adapters that point here.
