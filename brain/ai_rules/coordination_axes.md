# Coordination axes — time, concurrency, depth

TL;DR: A context window is volatile RAM; the brain is disk; this rule is the scheduler. A goal lives on disk, not in any window. Three axes carry a goal — TIME (`flows/cwc.md` + the handoff) across sessions, CONCURRENCY (`handoff/coord/`) across sessions running at once, DEPTH (a card's **cursor**) across context windows. The default unit is a card; it grows a cursor only when a goal outruns one window.

#ai_rules #coordination #campaign #context #handoff

-----

## The frame

A context window fills, compacts, and ends — treat it as RAM, not storage. Durable state lives in brain artifacts (cards, the slice ledger, the cursor, the handoff) — the disk. This rule is the scheduler: load just enough, run one increment, save state, swap the window out. **The goal never lives in a window. It lives on disk.** Windows are disposable workers that page in, advance the goal one step, page out, and die. An arbitrarily large goal then runs in fixed-size windows — the way a large program runs on small RAM.

## Three axes

| Axis | Spans | Mechanism | Tense |
|---|---|---|---|
| Time | session → session | `handoff/session_context.md` + `flows/cwc.md` | past — settled history |
| Concurrency | session ‖ session | `handoff/coord/` claim board | present — live claims |
| Depth | window → window, one goal | the **cursor** on a card (`tasks/_extend.md`) | present — you-are-here |

They compose: depth decomposes a goal into slices → concurrency hands slices to parallel sessions → time records what settled. `cwc` is the resume button for all of it.

## Campaign trigger — the default is a card

A campaign is not a type you start. It is a property a goal turns out to have: bigger than one window. So:

- **Default = card.** Most work fits one window; the handoff/cwc baton carries it. No cursor, no campaign machinery. Do not wrap small work in it — that is ceremony tax, and it cuts against the minimal-MVP ethos here.
- **Promote on a signal — the agent's call, not the user's** (THE BAR / `act_dont_ask`). Promotion adds exactly one thing: a **cursor**. A campaign is just a card that grew a cursor.
  1. **Proactive (plan time):** the decomposition plainly won't fit one window → lay the cursor in from the start.
  2. **Reactive (overrun):** the window is filling before the goal is done → checkpoint at the clean slice boundary and write the cursor *before* the wall, not into it.
- **Not at end-of-task.** Realizing after the fact that something "should have been a campaign" is too late to save it — that assessment only feeds the handoff note. Promote at plan time or at the overrun moment.

## The two contracts that beat context death

- **Resume — page in cheap.** A fresh window loads `{goal, cursor, the one slice it is doing}` — not the history. The ledger's **verification evidence** is what lets the new window trust "S1 done" without re-checking it. If resuming costs half the fresh window just catching up, the campaign collapses. Cheap reconstitution is the whole game.
- **Checkpoint — page out before the wall.** One slice per window. Write `{result + evidence}` to the ledger, advance the cursor, stop with margin. If a slice itself overruns, it was not sliced enough — split and re-plan. Don't fight the harness's auto-compaction; let it drop the chatter while the card holds the truth.

## How to apply

- Continuing a card? If it has a Cursor block, resume from it (goal + cursor + the one slice it names), not the whole handoff. `cwc` does this.
- Working a multi-slice card? Checkpoint each slice to the ledger with its verification evidence before moving on — your cards already do this (`S1 SHIPPED + verified`), which is what makes them campaign-ready by default. Promotion only adds the cursor.
- More than one session live at once? Read `handoff/coord/_protocol.md` before claiming a card.

See also: `flows/cwc.md` (resume), `tasks/_extend.md` (the cursor block), `handoff/coord/_protocol.md` (concurrency), `tasks_persist_to_brain.md` + `brain_is_durable.md` (why disk), `work_independently.md` + `act_dont_ask.md` (whose call promotion is), `practices/04_thin_vertical_slices.md` (slicing so each slice fits).
