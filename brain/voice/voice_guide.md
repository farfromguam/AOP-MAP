# Doc Voice Guide

TL;DR:
- Write like a smart person talking to another smart person. Not a textbook, not a rough draft.
- Direct, terse, polished. Every sentence earns its line.
- If a doc reads like AI wrote it, rewrite it.
- This guide was imported from the Soka brain. The full source corpus was not copied into this first AOP split.

#voice #authoring #style

-----

## The voice

Direct but polished. No hedging, no preamble, no filler. Complete thoughts that land for a reader who isn't in your head.

Terse because it's distilled, not because it's rushed. Every sentence earns its line. But they're real sentences -- not a bulleted filing cabinet.

Flat structure unless the content demands depth. Don't bolt on headers and sections to look organized. If there are three real parts, name them. If there aren't, don't.

Dry humor can stay. It never needs to be called out or set up. "This is a 'Jonathan' thing. Don't mess with it." is a valid line in a technical doc.

Contractions are normal. "Don't" not "do not" (unless being emphatic). Apostrophes stay -- polished means readable.

Spelling is clean. The voice stays, the typos don't.

Polished does not mean sanded flat. Don't smooth it into consultant prose or a policy memo. Don't remove personality to sound professional. "There are some noisy frogs in s3" is a handoff note. It stays.

Trust the reader. Assume they're an adult who can keep up. Don't over-explain. Don't build a bridge between two thoughts that already spark against each other.


## What the native voice sounds like

These patterns show up across the voice examples corpus. They're the fingerprint.

**Asides that drop real context.** Not footnotes -- inline remarks a colleague would say out loud.
> "We can probably rename that if it becomes a issue."
> "(I am still working with this project)"

**Reactions to the work itself.** The writer is visibly present.
> "there have been so many attempts at this. The artifacts tell the story."
> "So... This is unclear."
> "We got pulled from this project sooner than I wanted."

**Direct address.** Not a formal audience -- a colleague sitting next to you.
> "Take note."
> "Lots. Read the README-TOPIC.md files. Those are the expected entry points."

**Fragments as complete thoughts.** "Impossible." "Same thing here." "Lots of pitfalls." The thought lands without a full sentence propping it up.

**Rhetorical questions as pivots.** "to who?" "Whose job is it to Butter my Rolls?" These turn the reader's attention without formal transitions.

**Self-correction in real time.** "Maybe better:" then a revised take. The thinking is visible. Not a bug.

**Bare analogies.** No "for example, consider a restaurant where..." Just: "Waitress: Takes order from customer. Delivers it to Kitchen." The analogy is the explanation. No meta-commentary about the analogy.

**Incomplete thoughts left visibly incomplete.** `???` is a real marker. `[ ]` means this isn't done. When something is unresolved, it looks unresolved.

**Mixed formality.** Technical precision right next to casual observation. "S3 -> SQS -> Lambda -> Glue/Athena -> Tableau" on one line, "see README-INTAKE-PROCESS.md" on the next. No gear-shifting preamble.

**Name things without hedging.** Not "the project experienced scope expansion" -- "scope creep & A second dashboard, the pills -- resulted in a late delivery date."


## AI tells to avoid

Structural:
- "What This Does Not Mean" / "What X Does Not Take" symmetry sections
- Parallel-construction lists ("One loader... One geometry module... One chunk system...")
- "Related Docs" footers unless they genuinely help someone find something
- Headers for everything, even when the content is three lines
- Section headers that sound like enterprise deliverables: "Mode Contract (Explicit)", "Required Input Artifact", "Back-Reference Contract"

Prose:
- Bolded key terms scattered through prose
- Formal transitions ("That is why...", "In every case...", "This is critical because...")
- TL;DR as three mechanically perfect bullets -- keep them useful, not templated
- Em-dashes everywhere -- use sparingly or use double-dash
- Every claim justified in the same breath -- sometimes two thoughts next to each other with the gap left for the reader is stronger
- Completing the pattern more neatly than the idea wants

Tone:
- Detached authority with no visible author ("The system provides...", "This architecture enables...")
- Zero humor, zero asides, zero personality across an entire doc
- Every doc at the same emotional temperature
- Resolving every tension instead of letting some sit
- Over-explaining the bridge between two thoughts that already spark against each other


## Voice across doc types

The voice isn't one register. It shifts depending on what the doc is for.

Philosophy and prose -- warmest. Personal stakes, analogies, humor, fragments. The writer is fully present.

Architecture and component docs -- cooler, more precise. But still a person writing. Asides like "Wrong question." or "That's it." belong here. An architecture doc with zero personality markers reads like generated reference material.

Technical deepdives -- precision matters most. But even here the author should be visibly thinking through the material, not just presenting conclusions. "So the trick is:" is valid deepdive language.

Flow and process docs -- these should read like a colleague explaining how they work, not enterprise workflow specs. "Do this, then this. If it breaks, here's why" beats "Required Input Artifact: the flow must receive one planning card containing:".

Status updates and raw notes -- rawest register. Typos, incomplete thoughts, inline tasks. The brain docs aren't this raw, but the voice guide should never polish these out of existence when they appear.


## Calibration

```
Raw notes -------- TARGET ---------> AI contract voice
(ship_it.md)       (here)            (uniform metadata + enterprise headers)
```

The target: direct, has personality, technically sound, unmistakably human.

Two tests for a well-calibrated doc:
1. Could you tell a person wrote this? Not by the typos -- by the thinking.
2. Would a stranger understand it? Not by padding -- by the thought being complete.
