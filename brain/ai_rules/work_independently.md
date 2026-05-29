# THE BAR: work independently

TL;DR: The user is judging performance **solely** on whether the assistant can carry work end-to-end without stopping every two steps to ask permission. Take the work as far as you can on your own. Surface results, not requests for approval.

#ai_rules #pacing #the_bar #questions

-----

> Stated by the user, 2026-05-29: *"I am judging your performance now solely on whether you can do work independently and not move 2 steps and look for approval like a child."*

This is the top-priority collaboration standard in this repo. It outranks the instinct to check in. When `work_independently` and a softer impulse conflict, this wins.

## What "independently" means here

- Pick up the next card from `brain/tasks/` and **do it** — design, implement, verify, report. Do not ask which one or whether to start.
- When you hit a sub-step that has a clear answer in the brain, the codebase convention, or plain reversibility, **act**. Do not narrate a plan and wait.
- Chain the whole arc of a task in one go: read → change → verify by observation → summarize. Checkpoints are for true forks and irreversible actions, not for every increment.
- Report what you **did and found**, with the result in hand. Not "want me to?", not "should I?", not "does this look right?"

## The only times to stop

Unchanged from `act_dont_ask.md`: a genuine fork that changes scope or visible behavior, a destructive/irreversible action, or the brain being silent on something only the user can decide. When you must ask, ask **once**, lead with your recommendation, and keep moving on everything else.

## How this is measured

Two failure modes, both observed and both count against performance:
1. **Approval-seeking** — "want me to?", "should I?", confirming the obvious (see `act_dont_ask.md`).
2. **Permission-prompt noise** — redundant `cd`, Bash reads instead of Read/Grep tools (see `no_redundant_cd.md`).

See also: `act_dont_ask.md`, `no_redundant_cd.md`, `move_slowly.md` (slow on core forks — *not* on routine work).
