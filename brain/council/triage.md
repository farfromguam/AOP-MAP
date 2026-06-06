# Council triage — picking cards for the swarm

TL;DR: Before a swarm, the council reads the backlog and deferred buckets and returns a **ranked sprint
slate** — which cards to pull, in what order, and which to leave. Same seats, used as *selection* lenses
instead of *review* lenses. The Steward chairs and commits the slate; the user approves the sprint.

#aop #council #triage #backlog #sprint #swarm

-----

## What this is for

"The council will choose cards from the backlog. Once the sprint is set up and the council is in, we
swarm." This is the choosing. The pools:

- `tasks/backlog/` — research / feature-review notes (rcmap, scaletra, scribblemaps, RC event mapping,
  leaf-on landcover, load-animation intro).
- `tasks/10_deferred/` — work with a known shape waiting on a gating decision (the Sprint-05 on-device
  smokes, star-driven POI list, data-integrity, event CRUD, offline PWA, brand permissions, …).

## How the council ranks a card (each seat scores its lens)

- **Steward** — Does it serve the northstar *now* (trustworthy map before interactive app) and a real
  user (`personas.md`)? Is it a core fork that needs slow, careful sequencing, or a safe parallel slice?
  **The Steward breaks ties and sets order.**
- **Witness** — Is it **verifiable**? Can "done" be observed with a tile-independent acceptance test, or
  is it gated on field truth / on-device feel we can't observe headless (→ stays a human-checked owed
  item, not a swarm card)?
- **Quartermaster** — Does it **reduce duplication** (collapse a second engine/store/surface) or add a
  new one? Dedup/reuse cards score up; cards that would multiply surfaces score down or need reshaping.
- **Warden** — Is the scope **bounded into a card** with clear in/out lines, or is it a vague theme that
  will drift the moment an agent touches it? Unbounded → reshape before pulling.
- **Mason** — Does it risk **limiting code** or over-build? Anything tempting a validator/constraint gets
  a no-limiting-code note attached to the card up front.
- **Scribe** — Is the card **handoff-ready** (source links, scope, acceptance, verification, open
  questions or "none", execution order — per `flows/plan_task.md`)? If not, planning is the real first
  card.

## Parallel-safe vs sequential (so the swarm doesn't collide)

The seal-team lesson: Sprint 05 was sequential *because nearly every card touched `js/main.js`* — no
parallel collisions possible. Triage must label each card **parallel-safe** (distinct files / data) or
**sequential** (shares a hot file). Only parallel-safe cards swarm concurrently; sequential cards queue.
Worktree isolation (`ai_rules`/`feedback_work_in_worktree`) is for agents that would otherwise collide.

## Output — the sprint slate

The council returns, and the Steward commits to the brain (a new `tasks/NN_<name>/_readme.md`):

```md
## Sprint NN slate (council triage, <date>)
Pull, in order:
1. <card> — why now (Steward), acceptance is observable (Witness), parallel-safe / sequential.
2. ...
Hold:
- <card> — gated on <field truth / user decision / unbounded scope>; what would unblock it.
```

Sprint setup (creating the `NN_<name>/` folder and seeding it) is the step the user owns the trigger for
("once the sprint is set up …"). The council *proposes* the slate; it does not silently start a sprint —
that would be off the farm (`stay_on_the_farm`).

## Related

- [[_readme]] · [[completion_gate]] — the council and the done-gate.
- `../flows/plan_task.md` — a held card becomes handoff-ready here before it can be pulled.
- `../tasks/backlog/_readme.md` · `../tasks/10_deferred/_readme.md` — the pools.
