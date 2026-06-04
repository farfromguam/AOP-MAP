# Why This Brain Holds

TL;DR:
- The AOP spec is right about the molecule -- loft/disclose loop + triangulation + drift-as-signal, anchored to a spec -- and right that the mature home is here. This doc is the inside-the-house view: where the molecule actually lives in this brain, why those instances hold, and what it owes back.
- The thing that distinguishes soka from AOP isn't the framing of the molecule. It's that the molecule operates *on the brain itself.* `northstar/10_philosophy/` doesn't describe the pattern; it runs it. Every loft level is a real altitude in the runtime, not a folder bucket.
- One open problem soka now owns out loud: in an agent-authored codebase, the triangle collapses when code becomes the common ancestor of all three legs. The cure is anchor discipline -- code to behavior, tests to the northstar, comments to intent -- and it earns its own rule, not just an L&L footnote.

#prose #brain #progressive-disclosure #triangulation #meta #soka

-----

The AOP doc (`AOP MAP/brain/practices/progressive_disclosure_spec.md`) names the pattern well and points back at the soka northstar files as the mature articulation. Read it first if you haven't -- this doc assumes its frame.

What it doesn't do, because it's written portable for a talk, is walk through where the molecule lives in soka and why those instances hold. That's this doc.

## The molecule operating on itself

The AOP spec is meta-commentary about the brain's shape. Soka's `northstar/10_philosophy/04_progressive_disclosure.md` and `06_triangulation.md` are not commentary -- they are the brain practicing the pattern on itself, in the layer where the brain stores its contracts. The TL;DR-then-rule shape, the four levels of lofting, the seismology analogy, the drift-as-signal coupling: those docs *are* an instance of the thing they describe.

That's the load-bearing difference between this brain and most "agent context" briefs in the wild. The pattern is not a doc about how to write docs. It is the working spec, and every doc in `brain/` was written under it.

## Where the brain shows it works

A short inventory of soka-internal instances where the molecule visibly operates. None of these are coincidences; each one is the loft/disclose loop in a different domain.

- **`brain/northstar/` as the top of the loft.** Promises, philosophy, practices. Drifts slower than code by design. A code change that violates a northstar is loud the way a red test is loud -- which is the triangulation signal applied across the disclosure hierarchy.
- **`brain/deepdive/` as the next altitude down.** Mechanics beneath northstar contracts. The disclosure layer between "what we promise" and "what's in `lib/`." A reader stops here when they don't need the implementation; an author lofts here when an insight is too mechanical for northstar but too cross-cutting for a function comment.
- **`brain/brain_map.md` as a triage surface, not a territory map.** It has a "Before you ask, look here" failure-mode index. That index is AAF wired into the boot read -- the most common ways an agent gets confused, with the brain location that resolves each one. AOP's brain_map is purely territory. Soka's is territory plus a routing layer that catches predictable mistakes before they happen.
- **`brain/voice/culture-of-documentation/` as a corpus, not a guide.** The voice guide tells you the rules; the corpus is the training data. Voice corroboration without a corpus is one seismometer. With it, the voice has somewhere to ground.
- **`brain/ai_harness/rules/` as durable collaboration spec.** Lofted out of agent memory and into version-controlled docs. The rule "the brain is durable" applies to the rules about the brain. Same loop.
- **`brain/flows/*.md` wired to `~~name` invocation at the harness layer.** A flow is loft made operational: the user types `~~start_sprint` and the brain runs. Not just a doc that describes a process -- a doc that *is* the process trigger.
- **`brain/prose/lofting_and_comments_as_arbiter.md` and this doc.** Warm register at the bottom of the loft. The thinking visible. Self-correction in real time, `???` markers, the dialogue that produced the eventual contract. Both legs in the triangle: the prose is "intent then," the northstar is "rule now."

When the AOP doc asks "is there a third domain to prove the molecule isn't a two-is-coincidence," part of the answer is: it's already inside soka in more than two domains. The engine triangle (code/tests/comments) and the map triangle (authoritative/observed/human) are two; the brain-on-itself triangle (northstar/deepdive/prose) is a third; the voice triangle (rule/corpus/produced doc) is a fourth. The pattern survives every domain swap that's been tried so far. That's the evidence.

## The agent-authored-codebase problem soka now owns

The AOP spec's 2026-06-01 refinement is the most important honest thing in the doc, and it lands harder on soka than on AOP because soka has more agent-authored surface area. Restated:

The legs of the triangle corroborate only when they were *derived from independent sources of truth.* The risk in an AI-authored codebase is not that one agent wrote all three legs in one sitting. The risk is that **the code becomes the common ancestor of all three legs.** An agent that regenerates tests-from-code and comments-from-code in a single pass produces a triangle that is consistent by construction and worth nothing.

The cure the AOP spec names is already in this brain's architecture but it isn't currently a working rule. It should be one:

> **Anchor each leg to a different source of truth.**
> - Code is anchored to behavior (what the system actually does at runtime).
> - Tests are anchored to the northstar / spec (what we promised, not what the code currently does).
> - Comments are anchored to intent (what the author believed and why -- the prose register, the rationale, the rejected alternative).
>
> When you change one leg, hold the other two and verify. When you must regenerate more than one leg, re-derive each from its own anchor, never all three from the code.

That belongs as a discrete rule in `brain/ai_harness/rules/` -- proposed name `triangle_anchor_discipline.md` -- and it cross-links to `04_progressive_disclosure.md`, `06_triangulation.md`, and the prose origin. The residual question the AOP spec leaves open ("how do you *enforce* tests-trace-to-northstar when an agent can read both?") is a soka problem to solve, not a talk question to wave at.

## What soka can borrow back from AOP

AOP is a fork of this brain and it has solved a few things sharper than soka has. Worth borrowing back:

- **The "THE BAR" callout at the top of `AGENTS.md`.** A single declarative paragraph that names the failure mode (acting before the lofted truth is loaded, asking for permission instead of working) and the standard agents are judged on. Soka's current entry is `CLAUDE.md` → `brain/ai_harness/_readme.md`, which is correct but not arresting. THE BAR is more honest about what's actually being asked of the agent.
- **`verify_by_observation.md` as a discrete named rule.** Soka has the `verify` skill and an `andon_pull.md` rule, but no rule pinning "verification means observing the real running system, not re-deriving the expected result." Worth adding -- it's the single most common slip in an agent loop and it deserves a citable name.
- **`references_are_not_analogies.md`.** When the user hands a URL, product name, or example, treat it as the thing, not as an analogy. Soka doesn't have this and it would have prevented multiple past detours. Worth borrowing.
- **The split between `commit_in_prose.md` and `commit_dont_menu.md`.** Soka has the latter but the commit-voice rule is buried in the voice guide. Two citable rules is better.

What soka has that AOP doesn't, and shouldn't try to import back:
- A real voice corpus, not just a guide.
- Loft levels that match runtime concerns (`northstar/` vs `deepdive/` vs `flows/` are real altitudes; AOP collapsed them into sister branches).
- `~~name` flow invocation at the harness layer.

## What's actually new in this brain (lead with these when describing it)

1. **The molecule is the working spec, not a meta-doc.** Every northstar file is shaped by it. Every brain doc inherits the inverted pyramid. The pattern isn't proposed; it's already running.
2. **Loft altitudes match the runtime, not the topic.** `northstar/` is contracts; `deepdive/` is mechanics; `flows/` is execution; `tasks/` is the active card; `prose/` is the warm register. A reader narrows by altitude, not by category.
3. **brain_map as triage, not territory.** The map indexes failure modes, not just folders.
4. **Voice as a corpus, not a guide.** Examples are part of the contract. The voice triangulates against itself.
5. **AI collaboration rules are first-class brain content.** They're durable, version-controlled, and live next to the philosophy that justifies them. Not memory, not scratch.
6. **Anchor discipline as the agent-era cure for triangle collapse.** Pending as a rule; named above.

## Notes for future thinking, soka-side

- Find one in-soka instance where layer-drift was caught and one where it was missed silently. The AOP spec asks the same question portable; soka can answer it with its own git history.
- The voice corpus is itself a candidate fourth leg of a triangle (voice rule / corpus example / produced doc). Worth thinking about whether voice drift is detectable the way invariant drift is.
- The lineage section in the AOP spec (Knuth, Memory Bank, llms.txt, C4, Diataxis, Zettelkasten) is talk material. In soka it can collapse to a footnote: the atoms are old; what's new is the molecule operating on itself and the anchor-discipline cure for the agent collapse case. That's enough.

## Open

[x] `brain/ai_harness/rules/triangle_anchor_discipline.md` -- created 2026-06-01, cross-linked from `06_triangulation.md`.
[x] `brain/ai_harness/rules/verify_by_observation.md` and `brain/ai_harness/rules/references_are_not_analogies.md` -- borrowed from AOP 2026-06-01.
[x] THE BAR -- landed at the top of `brain/ai_harness/_readme.md` (the real boot read), not in `CLAUDE.md` (which stays a doormat).
[ ] Find the in-soka drift-caught vs drift-missed example for the AOP open item.
[x] CWC pattern landed 2026-06-01 -- `brain/flows/cwc.md` (sprint-bounded, multi-agent aware, per-sprint `_handoff.md` with rewritten working set + append-only log). `~~finish_sprint` archives the handoff with the sprint; `~~start_sprint` seeds an empty one. Prune is the sprint boundary by gravity, not a judgment call mid-sprint.
