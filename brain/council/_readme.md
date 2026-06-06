# The Council

TL;DR:
- The council is a standing review layer that fires **when a main agent thinks it's done**.
- It is the `ai_rules` given faces: **six seats**, each an independent adversarial lens over one
  non-overlapping cluster of this project's standing rules, chaired by a product keeper (the Steward).
- It is **self-served, not approval-seeking**. The working agent runs the council over its *own* work
  and reports the findings. It never asks the user "is this ok?" — it asks the seats "what did I miss?"
  This is the adversarial-review-before-done that catches slop, **not** the babysitting THE BAR forbids.
- Objective checks gate **first**; the council convenes only on material "done"; **any seat can pull
  andon** and bounce "done" back with grounded evidence.

#aop #council #review #gate #slop #the_bar

-----

## Why this exists

The seal team got us past Sprint 05 by brute force — eight cards, one at a time, hand-verified. That
does not scale and it leaves the door open to the exact slop the refactor was fighting: per-layer
branches, duplicate engines, browser-state curation, "verified" claims that were only re-derived. The
council is the standing answer. It encodes **everything the user would otherwise have to be on an agent
about, every single turn, but can't because it's too much to type.** Profile-based guardrails that
resist the slop on their own.

The council is not new policy. It is the policy we already have — `ai_rules/`, `practices/`,
`northstar/editor_architecture_contracts.md` — **partitioned into review lenses and given a firing
trigger.** Nothing here overrides the brain; it operationalizes it at the "done" boundary.

## The seats → the rules each one owns

Each seat owns a **non-overlapping** cluster. No two seats cover the same ground (overlap is a known
multi-agent failure mode, not extra safety — see Evidence). Together the six tile the whole rule set.

| Seat | One-line mandate | Owns (brain rules / contracts) |
|------|------------------|--------------------------------|
| **[[steward]]** (Chair) | Keeps the work true to the product and keeps the other seats focused. | `northstar/map_northstar`, `northstar/whats_this_for`, `northstar/personas`, `northstar/validation_loop`, `move_slowly` (core forks) |
| **[[warden]]** | Did the work stay on the farm and inside the card? | `stay_on_the_farm`, `preserve_card_directives`, `cards_not_gospel`, `no_commits`, `no_schedule_pitches`, `editor_is_the_viewer` (as scope) |
| **[[witness]]** | Is every "done / works / verified" backed by an observation of the real running system? | `verify_by_observation`, contract **C4**, `triangulation`, `andon` |
| **[[quartermaster]]** | Did this reuse what exists, or quietly build a second one? | `extract_before_invent`, contracts **C1 / C2 / C6**, `harness_adapters_are_thin`, `editor_is_the_viewer` (as no-second-surface) |
| **[[mason]]** | Is the code clean, minimal, idiomatic, and non-limiting? | `no_limiting_code_mvp` / contract **C5**, `opacity_and_multiply_separate`, plain clean-code craft |
| **[[scribe]]** | Did the outcome land durably in the brain, in the user's voice? | `tasks_persist_to_brain`, `brain_is_durable`, `commit_in_prose`, `references_are_not_analogies`, `fix_misspellings`, `user_writing_style` |

`work_independently` and `act_dont_ask` are not seats — they govern the *gate's own behavior*: the
council must run fast and self-served, never as a reason to stop and poll the user.

## How it convenes — in tiers (cheap first)

1. **Tier 0 — objective gate (deterministic, automatic).** The Stop hook
   (`.claude/hooks/council-gate.sh`) runs the cheap, unambiguous checks the moment a main agent tries
   to stop with material changes: `node --check` on changed JS, the C1 region grep, a version-bump
   note. Unambiguous breakage hard-blocks. Everything else is an advisory line carried into the nudge.
   No LLM judgment spent until this passes. See [[completion_gate]].
2. **Tier 1 — the core three (default on every material "done").** **Witness · Warden ·
   Quartermaster.** These catch the three slop families that actually bite here: fake verification,
   scope drift, and duplication. Cheap, and they cover the 80%.
3. **Tier 2 — full council (sprint boundaries, publish-zone data, anything high-risk).** Add **Mason**
   and **Scribe**, chaired by the **Steward**, who synthesizes and is the only seat that clears the gate.

The seat that convenes the council picks the tier honestly by risk. A one-line copy edit does not need
six critics; a data merge into the publish zone or a sprint-closing refactor does.

## The self-served principle (reconciling with THE BAR)

THE BAR (`ai_rules/work_independently`) forbids stopping every two steps to seek approval. The council
does **not** violate it — it *serves* it. The agent convenes the council on its **own** finished work,
in **fresh** critic contexts, and reports the verdict as a result ("Witness pulled andon: the trail-fade
claim was re-derived, not observed — re-checking"), not as a question. Independent self-review before
declaring done is exactly the move; asking the user to do that review for you is the failure.

Two failure modes the council itself must avoid: **approval-seeking theater** (turning a verdict into a
"should I?") and **rubber-stamping** (a seat that always passes). A seat that never pulls andon is not
doing its job; a verdict that ends in a question to the user is off the rails.

## How a seat returns its verdict (the receipt, not a narration)

Each seat returns a small structured verdict — never trust a narrated "I reviewed it." Schema and the
andon-bounce loop live in [[completion_gate]]. A seat's two jobs: **refute** (try to find where the work
is wrong, prompted to disprove, not confirm) and, if it finds nothing real, **clear** its lens.

## What the council is NOT

- **Not the product personas.** `northstar/personas.md` (Driver, Trail Buddy, Host, Visitor, …) are
  map *users* — a view-default filter. The council are *reviewers* of agent work. Different axis. If you
  came here looking for who the map is for, you want `northstar/personas.md`.
- **Not a second source of truth.** Per `harness_adapters_are_thin`, the durable council lives here in
  the brain; `.claude/agents/council-*.md`, `.claude/commands/council.md`, and the Stop hook are thin
  pointers into these files. Edit the seat here, not the adapter.
- **Not a replacement for the user's git gate.** The council reviews; the user still reads the diff and
  decides what is real (`no_commits`, `stay_on_the_farm`). The council makes that diff cleaner before it
  reaches the gate — it does not bypass it.

## Evidence base (why it's shaped this way)

Researched 2026-06-06; full notes folded into [[completion_gate]]. The load-bearing findings:

- **Independent, adversarial critics — not self-review.** Models are largely blind to their own
  reasoning errors; unaided self-correction can *degrade* accuracy (Huang et al., ICLR 2024,
  arxiv 2310.01798). A dedicated critic catches more real bugs than unaided review (CriticGPT /
  McAleese 2024, arxiv 2407.00215). Verifiers are subject to **self-preference bias** — score their own
  work higher — so a critic should be a *fresh* context, ideally not the producer (arxiv 2504.03846).
  Verification questions answered *independently* of the draft work better (Chain-of-Verification,
  arxiv 2309.11495). → Seats run fresh, see only the diff + criteria, prompted to refute.
- **Gate on artifacts, not narration.** Agents hallucinate tool calls and execution traces; you cannot
  tell a real "I ran it" from a fabricated one in the transcript (arxiv 2509.18970). → The Witness
  demands the receipt; the gate stores verdicts as files.
- **Small, non-overlapping council.** Most gain is in the first 1–2 critics; duplicate roles are a named
  failure mode (MAST, arxiv 2503.13657). → Six seats, strictly partitioned, convened in tiers.
- **Objective checks first.** Gate fast, unambiguous, execution-backed checks before slow/subjective
  ones (DORA continuous-delivery; Toyota jidoka / andon). → Tier 0 in the hook.
- **Orchestrator holds goal + scope + termination.** A lead that holds direction beats parallel workers
  that drift; drift comes from ambiguous roles and missing stop conditions (Anthropic multi-agent
  research system; MAST). → The Steward chairs and is the only seat that clears.
- **Personas help judgment but can hurt facts.** Role-play can dent factual accuracy; keep personas as
  thin *what-to-look-for* framing, not knowledge authorities (arxiv 2408.08631). → Seats are review
  lenses, not domain oracles; correctness still rests on observation.

## Related

- [[completion_gate]] — the Definition-of-Done gate, the verdict schema, the Stop-hook contract, the dials.
- [[triage]] — how the council picks cards from the backlog for the next swarm.
- `../flows/council_review.md` — the one-line flow pointer (sits beside plan_task / work_task).
- `../northstar/editor_architecture_contracts.md` — C1–C6, the contracts the seats enforce.
- `../practices/03_andon.md`, `../practices/02_triangulation.md` — the stop-the-line + evidence methods.
