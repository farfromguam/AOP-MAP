# Progressive Disclosure Spec

TL;DR:
- This is the L&L synthesis + outside-in prior-art check for a pattern that already lives, fully articulated, in the Soka brain. Read the sources there first; this doc names the molecule and tests it against the field.
- The pattern: lofting and progressive disclosure are one loop in two directions (author lofts knowledge up to the level of highest leverage; reader discloses down only as far as needed), triangulation (code / tests / comments as three independent arbiters, reality as judge) is the correctness mechanism, and drift between disclosure layers *is* the triangulation signal -- which is the andon pull.
- The author's working name: "north-star triangles + progressive disclosure." The "triangle" is triangulation, not the inverted-pyramid header.
- Verdict for the talk: the atoms are old, the molecule is defensibly novel. Say "synthesis," lead with the parts that fight the orthodoxy.

#practice #spec #progressive-disclosure #lofting #triangulation #l-and-l #portable

-----

A meta doc. Not about the map -- about the shape of the brain the map is built on, written portable so it can travel and get argued with.

## Sources (the mature home is Soka, not here)

The original articulation is already written, in the warm and the formal register both:

- `soka/brain/northstar/10_philosophy/04_progressive_disclosure.md` -- "Progressive Disclosure: The Inverse of Lofting." The four-level hierarchy (repo docs / module headers / function comments / code body) and the loft-up/disclose-down loop.
- `soka/brain/northstar/10_philosophy/06_triangulation.md` -- "Comments, Code, and Tests as Arbiters of Truth." The three-leg model, the temporal-independence argument, the seismology trilateration analogy.
- `soka/brain/prose/lofting_and_comments_as_arbiter.md` -- the original thinking, warmest register. The L&L's narrative spine probably lives here.

This AOP brain carries the same triangulation idea in a different domain: `practices/02_triangulation.md` triangulates map facts (authoritative records / observed artifacts / human reality). Same shape, different legs. That the triangle survives a domain swap -- engine vs map -- is itself evidence it's a real abstraction, not a one-off. Use that in the talk.

## What the pattern actually is

Three pieces, already coupled in the sources:

**Lofting and progressive disclosure -- one loop, opposite directions.** The author lofts knowledge to where it has the highest leverage: code body, to function comment, to module header, to repo docs, to the brain. The reader discloses downward, reading only as deep as the question needs. Four levels, each answering a different question, each a claim about the level below. The inverted-pyramid header on every brain doc (`TL;DR` then `-----` then detail) is this same move at the document scale. The discipline is choosing what rises: loft nothing and everyone excavates from scratch; loft everything and the top is noise.

**Triangulation -- three independent arbiters, reality as judge.** Code says what the system does, tests say what we enforce, comments say what was intended. Agreement is alignment, not correctness -- three legs can share one wrong assumption and line up perfectly. The value is in disagreement: when they diverge you don't have a bug, you have a missing fact, and the question becomes which leg is lying. The legs must be *independent* -- the temporal gap (comments record intent *then*, code runs *now*) is exactly what makes the comment leg load-bearing rather than redundant. Seismology: one seismometer gives a circle, three intersect at a point. Enough instruments, spread apart, turns redundancy into resolution.

**The coupling -- drift between disclosure layers is the triangulation signal.** This is the move that makes it one pattern instead of two. A module header claims an invariant the code no longer holds: that's the comments/code/tests triangle applied to the disclosure hierarchy itself. The structure that makes knowledge navigable is the same structure that detects its own decay. Drift isn't rot -- it's signal, and the signal is an andon pull: stop, name which leg lied, re-loft, continue.

The **northstar** is both ends of this. It's the top of the loft (where cross-cutting principle lands, and principle drifts slower than code, so a violation is loud) and the external arbiter the triangle is checked against. That's the sense in which it's "spec-first": the spec is where lofted truth comes to rest and what correctness is measured against.

## The honest read on novelty

Old atoms. Progressive disclosure is Nielsen. Inverted pyramid is journalism. Spec-first is RFCs and design docs. Comments-as-first-class-narrative is Knuth's literate programming, 1984.

What's uncommon, and worth standing on:
- **Comments as an independent arbiter, defended on purpose.** The modern orthodoxy -- self-documenting code, "comments are a smell," tests-as-docs -- says drop them. The sources argue the opposite from the temporal-independence angle and win the argument. A well-argued contrarian stance is a better talk than a novel one.
- **Lofting and disclosure as a single bidirectional loop**, not two separate practices.
- **Drift-as-signal coupling** -- navigation structure doubling as decay detector, wired to andon.

Closest single ancestor is literate programming, and it has no triangulation or drift mechanism. So the molecule -- loft/disclose loop + triangulation + drift-as-signal, anchored to a spec, run as a development discipline -- is defensibly novel *as a synthesis*. Don't claim the atoms. Claim the molecule, and name every atom you borrowed. The engineer in the room who's used Cline's Memory Bank or read Knuth will trust you more for it, not less.

## Who's close (name these or get caught)

The orthodoxy it fights:
- **"Self-documenting code / comments are a smell"** (Martin et al.). Name the opponent early; the talk sharpens against it.

Comments-as-layer ancestor:
- **Knuth, literate programming** (WEB, 1984) -- code and prose interleaved in narrative order. The direct ancestor of the comment hierarchy. No triangulation, no drift signal.

Spec-first lineage:
- **GitHub Spec Kit** (`/specify` then `/plan` then `/tasks`) and **Amazon Kiro** (requirements/design/tasks + steering files) -- the closest named methodologies.
- **Amazon Working Backwards / PR-FAQ** -- press release + FAQ before code. Northstar is the press release; the context doc is the FAQ. Steal the analogy.
- **README-Driven Development, RFCs, ADRs** -- the older "spec before code" culture.

Agent-context cousins:
- **Cline "Memory Bank"** -- nearest living analog: fixed markdown a stateless agent re-reads each session (projectbrief ~ northstar, activeContext ~ handoff, progress ~ cards). Differentiate out loud.
- **`llms.txt`** (Jeremy Howard, 2024) -- progressive disclosure for LLMs. The AGENTS.md + search_map routing layer.
- **AGENTS.md / CLAUDE.md / Cursor rules** -- the open conventions this builds on.

Information-architecture cousins:
- **C4 model** (Simon Brown) -- zoomable architecture docs, the structural twin of the cross-doc zoom.
- **Diataxis** -- docs split by purpose, a different axis (intent, not zoom).
- **Zettelkasten / Obsidian** -- atomic notes + `[[links]]`, the lineage of the cross-links.

## What's actually yours (lead with these)

1. **The loft/disclose loop** -- one mechanism, two directions, not two practices bolted together.
2. **Comments as the undervalued independent leg** -- temporal independence reframed as a feature, against the grain of current practice.
3. **Drift-as-signal coupling** -- the navigation surface is the decay detector; divergence pulls andon.
4. **Domain-polymorphism** -- the same triangle is code/tests/comments in the engine and authoritative/observed/human in the map. One pattern, two domains. Strong evidence it's a real abstraction.
5. **Boot order as the bar** -- spec-first as a gated ritual (read the lofted spec in order, before acting, judged on it), not a hope that someone reads the doc.

## The L&L spine

Open on the seismology analogy -- it's the author's own and it lands cold: three seismometers locate an earthquake nobody felt; three artifacts locate a bug nobody can see.

Three acts:
1. The failure mode -- one seismometer (code only) tells you something's wrong, not where. Stateless agents and drifting specs fail the same way: acting before the lofted truth is loaded.
2. The loop -- loft up, disclose down. Walk one real query top-down, live, so the room feels the narrowing.
3. The coupling -- drift between a module header and its code is the same signal as a red test. Show andon firing on a divergence.

Pre-empt the objection on purpose: one slide with Knuth, Memory Bank, and the "comments are a smell" orthodoxy; the next slide, the molecule. Early, not in Q&A.

## Open, for the mature brain to push on

[ ] Does drift-as-signal hold at scale, or decay into a cord nobody pulls? Find one real instance where layer-drift got caught vs. one where it got missed silently.
Is the comment leg's independence real in an AI-authored codebase? Refined 2026-06-01 -- this is no longer a blanket threat, and the refinement is itself an L&L beat:

- Independence isn't about who wrote the legs or whether it was one sitting. It's *derivational*: two legs corroborate only if neither was derived from the other. The real failure is when **the code becomes the common ancestor of all three legs.**
- A behavior-preserving refactor is the safe case, even single-agent: code moves, tests are held fixed by definition, so passing tests on changed code is genuine corroboration -- the refactor manufactures the temporal gap that was missing at creation. (Caveat that is the whole game: if the agent edited the tests to fit the new code, it re-collided, and passing proves nothing.)
- A feature change is the threat: all legs legitimately move, and an agent that regenerates the set in one pass fits tests and comments to the new code. Consistency by construction. Worthless.
- The cure is already in the architecture: anchor each leg to a *different* source of truth -- code to behavior, tests to the northstar/spec, comments to intent -- never all three to the code. That keeps a one-agent triangle non-degenerate. It's also the source's own KEEP/DELETE rule restated: mechanics-comments drift (derived from code, not independent); intent-comments hold (derived from the spec).
- Agent discipline that falls out: change one leg, hold the others, verify. If you must regenerate, re-derive each leg from its own anchor, never all three from the code.

Residual ??? : how do you *enforce* "tests trace to the northstar, not the code" when an agent can read both? The anchor discipline is sound in theory; the mechanism that keeps an agent honest about it is still open.
[ ] The triangle is domain-polymorphic (engine vs map). Is there a third domain to prove it, or two-is-coincidence?
[ ] Naming. "North-star triangles + progressive disclosure" is three nouns; the talk needs one handle. "Loft" is the strongest single word the author already owns. ???
