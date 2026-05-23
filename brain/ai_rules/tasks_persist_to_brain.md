# Tasks persist to brain

TL;DR: All durable tasks go in the brain. Not in the session task list. You are not the only contributor.

#ai_rules #tasks #durability

-----

The session task list (`TaskCreate` / `TaskUpdate`) is ephemeral to one Claude conversation. The AOP project has other contributors — human and AI — who never see it. Anything that needs to survive the session or be visible to anyone else must land in the brain.

The user said this directly: "all tasks go in the brain. you are not the only contributor."

How to apply:

- The session task list is fine for tracking my own in-progress work within one conversation. It is not where work is *recorded*.
- Before ending a turn that introduces new pending work, write it into the brain.
- Default homes:
  - `tasks/02_edit/_readme.md` and the cards beside it — the active sprint.
  - `tasks/01_mvp/_readme.md` "Immediate next work" checklist — pending MVP items.
  - `tasks/03_deferred/` — work with a known shape but waiting on a gating decision.
  - `tasks/backlog/` — research and feature-review notes.
  - `handoff/session_context.md` — short pointer for the next session; durable record lives in the cards.

See `brain_is_durable.md` for the general principle.
