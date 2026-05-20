# Doc Style Guide

TL;DR:
- Voice is how it sounds. Style is how it is shaped and where it lives.
- Use `snake_case.md`, lowercase `_readme.md`, and numeric prefixes only when order matters.
- Standard header: H1, TL;DR, tags, `-----`, body.

#style #docs #authoring

-----

## File names

Default to `snake_case.md`.

Use `_readme.md` for branch entry docs.

Use `_extend.md` only when a branch needs authoring rules of its own.

Use numeric prefixes only when reading order matters, like `practices/01_apparent_answers_first.md`.

## Where docs go

- `northstar/` -- promises and contracts.
- `research/` -- facts, sources, evidence, caveats.
- `tasks/` -- cards, acceptance, verification, implementation notes.
- `practices/` -- reusable thinking methods.
- `flows/` -- reusable work procedures.
- `voice/` -- writing and structure rules.
- `ai_rules/` -- assistant collaboration rules.
- `output/` -- scratch artifacts waiting to be promoted or discarded.

If a doc could live in two places, put it where a reader would look first. Link from the other place only when useful.

## Standard header

```md
# Title

TL;DR:
- Useful summary.

#tag #tag #tag

-----
```

Then the body.

Rules:

- One H1.
- TL;DR for anything longer than a short note.
- Tags are routing, not taxonomy.
- Five dashes divide header from body.

## Branch entries

Branch `_readme.md` files use this shape:

```md
# Branch Name

TL;DR: What lives here.

Writing here: see `../voice/voice_guide.md` first.

Context chain:
- `_readme.md`
- `branch/_readme.md`

#tag #tag

-----
```

Do not restate the whole voice guide in every branch.

## Links

Use relative links inside this brain.

Use backticks for paths in prose: `northstar/map_northstar.md`.

Use markdown links only where a reader would click.

## Lists and tasks

Use `-` bullets.

Task checklists use bare brackets:

```md
[ ] Source register exists.
[X] Research source stack copied into the new brain.
```

Do not mix native Markdown task bullets with the project checklist style in the same doc.

## Markers

These are allowed and should stay visible:

- `???` unresolved question.
- `[ ]` incomplete thought or task.
- `TODO:` work to return to.

Do not polish uncertainty into fake certainty.
