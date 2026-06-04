# How to Build a Brain, v2

TL;DR:
- v1 (`how_to_build_a_brain.md`) is the seed. Five steps: start with truths, append context, ask of AI and document, track todos, get stuff done, reflect. Keep it.
- v2 is the matured form -- what those five steps look like after the brain has been built once and used in anger. Same arc, filled in.
- The molecule the brain operates on (loft/disclose loop + triangulation + drift-as-signal, anchored to a northstar) is now a working spec, not advice. Most steps below are the molecule wearing one face or another.
- One rule the original didn't name and it should: **anchor each leg of the triangle to a different source of truth, never all three to the code.** Otherwise an agent collapses the triangle and the work proves nothing.

#prose #brain #how-to #v2 #meta

-----

The v1 doc is good and stays. This is what each of its steps grew into after the brain was built once, broken once, and rebuilt.

## 0. Before the steps -- two priors

**The brain is the durable artifact.** Anything that matters past this session goes in `brain/`, in version control. Memory is for genuine session-ephemera and nothing else. This rule is so load-bearing that it has its own ai_harness rule (`brain_is_durable.md`) and the rule extends to the AI rules themselves -- they live in `brain/ai_harness/rules/`, not memory.

**The brain practices the pattern on itself.** The doc you are reading is at the bottom of the loft (`brain/prose/` -- warm, reflective). The contracts it crystallizes into live at the top (`brain/northstar/`). The disclosure shape used here -- TL;DR up top, divider, body -- is the same shape every other brain doc uses. The brain isn't a doc about how to write docs. It is the spec, operating on itself.

## 1. Start with truths

The original line: "1) start with truths."

Truths in this brain mean **northstar promises** -- contracts about what the project promises to do, kept above implementation. Three kinds:

- **Philosophy** (`brain/northstar/10_philosophy/`) -- principles that govern how *everything* should be shaped. Progressive disclosure, triangulation, ubiquitous language.
- **Component specs** -- per-system contracts. What this module owns, what it doesn't, what invariants must hold.
- **Journeys** -- the user-facing behavior promises. What does the system *do* from outside.

Truths are written *before* the code that implements them, when you can. When you can't (most retrofits), they're extracted from the code into the northstar layer the first time you have to reason about that area twice. The cost of writing a truth retroactively is much lower than the cost of *not having one* when an agent has to make a judgment call.

A truth doc is one page, max. If it grows past that, the disclosure broke -- there are two truths in one doc, split them.

Adjacent practice: **Apparent Answers First** (`brain/northstar/11_practices/05_apparent_answers_first.md`). Before treating a question as open, dissolve it against the northstar. The number of "new" questions that turn out to be already-answered by an existing truth is high. The brain is dense; the failure mode is inventing around an existing answer because you didn't look first.

## 2. Append your context

The original arc: in the file -> in a doc -> in a meta-workflow.

This is the **lofting loop** named explicitly. Knowledge starts inside a function body. The most valuable insight rises to where it has the highest leverage:

- A line of code -> a function comment (intent, sharp edges).
- Multi-function constraint -> a module header.
- Cross-cutting rule -> a repo doc.
- Project-wide principle -> a northstar.

The discipline is choosing what rises. **Loft nothing and everyone excavates from scratch. Loft everything and the top is noise.** Rule of thumb: loft anything you'd be annoyed to rediscover. Obvious from the code? Delete it. Multi-function dependency? Module header. Crossing boundaries or causing bugs? Repo doc.

The reverse direction is **progressive disclosure**. A reader walks down the loft only as deep as their question needs. Repo docs answer "what is this," module headers answer "what does this file own," function comments answer "what does calling this cost," code body answers "how does it do it." If a developer has to read every function body to understand a module, lofting failed.

This is one loop, not two practices. Author lofts up. Reader discloses down. Same structure, opposite direction. (Full thinking: `brain/northstar/10_philosophy/04_progressive_disclosure.md`.)

The meta-workflow level the original named is the **flow**. A flow is a repeatable execution pattern lofted to its own doc, callable as `~~name`. `~~start_sprint`, `~~finish_sprint`, `~~cwc`, `~~orient`. Each one is the loft loop applied to a process -- the work was done many times, the shared shape rose to a flow doc, and the doc became the trigger.

## 3. Ask of AI and document how you like to work

The original line: "ask of AI and document how you like to work. -- early on !!!validate the hallucinations!!! the less truths you have the more is inferred."

Two ideas in there that grew up.

**First, AI rules are first-class brain content.** They used to live in claude memory (opaque, unreviewable, drifted silently). They moved to `brain/ai_harness/rules/`, one rule per file, with the rule above a divider and the origin story below. When a session produces a durable rule, the move is to propose a brain doc edit, not save to memory. Memory is for session-ephemera only.

**Second, validate the hallucinations early.** This is the triangulation principle showing through. Code says what the system does, tests say what we enforce, comments say what was intended. Three independent views. When they disagree, the disagreement is the signal -- one is lying, the other two narrow the fault. Reality (production logs, the spec, a minimal repro) is the final arbiter. (`brain/northstar/10_philosophy/06_triangulation.md`.)

The original's "the less truths you have the more is inferred" is the same observation from the AI direction. If the northstar layer is thin, the agent infers from code alone -- one seismometer, can't locate anything. The cure isn't fewer questions to the agent; it's more truths in the brain.

**The agent-era addition the original didn't name.** When one agent regenerates more than one leg of the triangle in a single pass, the triangle collapses -- the code becomes the common ancestor of all three legs and consistency proves nothing. The cure is anchor discipline (`brain/ai_harness/rules/triangle_anchor_discipline.md`):

- Code is anchored to behavior (what runs).
- Tests are anchored to the northstar (what we promised).
- Comments are anchored to intent (why the author believed it should work).

Never derive more than one leg from the code in a single pass. Change one, hold the others, verify. This is the single most important rule the original didn't carry, and it earns its own line in the v2 because the failure mode is now common.

**Verification is observation, not re-derivation.** Run the app, see the change. Read the test runner output. Don't reimplement the expected math in your head and check the code against your math -- that's a single leg checked against itself. (`brain/ai_harness/rules/verify_by_observation.md`.)

## 4. Track todos

The original line: "4) track todos."

This grew into a sprint system. Three layers:

- **Backlog** (`brain/tasks/20_backlog/`) -- unsorted future work, triage-shaped. Not specs; snapshots.
- **Active sprints** (`brain/tasks/10_active_sprints/`) -- promoted backlog items rewritten as cards. The current work.
- **Resolved sprints** (`brain/tasks/00_resolved_sprints/`) -- history. Cards land here in `_done/` when they ship; the sprint folder moves here at close.

A card has a clear shape: source block (what backlog row, what northstar, what contracts), slices, outcome section. When a card ships, the outcome section gets written by the implementer (1-3 changelog-voice bullets at top, detail below). At sprint close, the close flow concatenates outcome bullets into the changelog -- O(grep) instead of O(judgment).

Sprints carry a **handoff** (`_handoff.md`) for session-to-session and agent-to-agent continuation. Two tiers: a mutable **working set** that gets rewritten on session exit, and an append-only **log** that accumulates within the sprint. The working set answers "what does the next agent need to know to start"; the log records "what happened." Don't conflate them.

The handoff is sprint-bounded on purpose. **Sessions don't have a natural prune signal; sprints do.** When the sprint closes, the handoff archives with it -- no agent makes a judgment call about "is this still relevant" mid-sprint, because the sprint close already answered it. (Full thinking: `brain/flows/cwc.md`.)

Multi-agent reality: the working set has an **in flight** section with one slot per live agent. Arriving agent reads first, claims a slot, picks a card not in flight with another agent. Slots are owner-only -- you don't rewrite another agent's slot, you reclaim with a log note if it's stale.

## 5. Get stuff done

The original line: "5) get stuff done. resist the pile of crap. if you are migrating, do it. shit then get off the pot. don't shit and smear."

This stays, almost verbatim. The matured form names the failure modes the original was warning against:

- **Don't invent around an existing answer.** Extract before invent (`brain/ai_harness/rules/extract_before_invent.md`). The brain is dense with answers; new abstractions are usually re-derivations of something already lofted.
- **Don't add features the task doesn't require.** No half-finished migrations, no speculative adapters. Three similar lines is better than a premature abstraction.
- **Don't build error handling for scenarios that can't happen.** Validate at boundaries, trust internal code. Backward-compatibility shims for code you control are pure cost.
- **Andon pull on conflict.** When sources disagree and you can't reconcile in one pass, stop. Don't silently pick one and override. Name the disagreement, surface it, resolve it. (`brain/northstar/11_practices/02_andon.md`, `brain/ai_harness/rules/andon_pull.md`.)
- **References are not analogies.** When the user hands you a URL or product name, it's the thing, not inspiration material. If your reading disagrees with the project model, the project model is probably wrong, not the reference. (`brain/ai_harness/rules/references_are_not_analogies.md`.)

## 6. Reflect and improve

The original line: "6) reflect and improve."

This grew into the close ritual. `~~finish_sprint` walks the closing sprint and asks:

- Did every card write its outcome section?
- Did the changelog entry get written from those bullets?
- Did the cards that changed contracts update the northstar docs they changed? (Silent contract drift is the slowest-acting bug in this brain.)
- Did the orientation surfaces (`brain_map.md`, `search_map.md`, `ai_harness/_readme.md`) stay current with what moved?
- Did the visible features get demoed in the zoo?

Reflection isn't optional and isn't post-hoc. The close flow is the reflection, structured. If a card didn't update the doc it should have, it's not actually done -- it bounces back rather than getting papered over from the flow.

There's also a per-sprint optional post-mortem (`s<N>_91_review.md`) for sprints that shipped material schema or contract changes. Footgun pass, smell pass, what was learned. Skippable for tight refactor sprints; recommended for anything that touched contracts.

## What the v2 doc names that the v1 didn't

Putting it in one place so the upgrades are visible:

1. **The brain is the durable artifact** -- rule, not advice.
2. **Northstar layer as the "truths" home** -- one page each, three families (philosophy / components / journeys).
3. **Lofting and progressive disclosure as one loop** -- and the four levels named.
4. **Triangulation as the correctness mechanism** -- code/tests/comments as three independent legs, reality as judge.
5. **Drift between layers is the signal**, not the rot. The structure that makes knowledge navigable is the same structure that detects its decay.
6. **AI rules are first-class brain content** -- live in `ai_harness/rules/`, not memory.
7. **Anchor discipline for agent-authored codebases** -- never derive more than one leg from the code in a single pass.
8. **Verification is observation** -- never re-derive and check your own math.
9. **References are the thing**, not analogies.
10. **Sprint-bounded handoffs and multi-agent CWC** -- the prune is the sprint boundary; the working set is rewritten on exit; in-flight slots prevent collision.
11. **Flows as callable workflows** (`~~name`) -- the loft loop applied to process, made executable.
12. **The close ritual as structured reflection** -- not "remember to reflect," a flow that catches the predictable misses.

## What the v1 had that the v2 should not lose

The voice. v1 reads like someone talking to themselves on a walk. "Resist the pile of crap." "Shit then get off the pot. Don't shit and smear." That register is part of how the brain works -- the warm prose is the bottom of the loft, and the bottom of the loft is where ideas land before they get formalized.

v2 should not feel like the v1 got sanded into consultant prose. It got more specific, not more polite.

## When to write a v3

When the brain has been built somewhere else (an AOP-style fork) and the lessons from that fork land back here. The AOP fork has already paid a few of those debts -- the verify rule, the references rule, the agent-collapse refinement. v2 incorporates them. v3 will exist when there's a second round of those, or when the molecule itself grows a piece (a third dimension to triangulation, a different disclosure surface, something the brain doesn't yet name).

Don't write v3 just to write it. Write it when the brain notices a tension v2 doesn't dissolve.
