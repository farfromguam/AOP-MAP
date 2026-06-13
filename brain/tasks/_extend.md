# Task Card Shape

TL;DR:
- Lead with the gist in plain language.
- Put source links, scope, decisions, acceptance, and verification below the `-----` divider.
- Cards grow in passes. Do not pretend the first pass knows everything.

#tasks #style #cards

-----

## Spine

Above the divider:

```md
# Title

One to three sentences explaining what this card is and why it exists.

The problem and the shape of the fix.
```

Then:

```md
-----
```

Below the divider, use only the sections the card earns:

- `## Source`
- `## Scope`
- `## Context`
- `## Decisions`
- `## Open Questions`
- `## Out of Scope`
- `## Acceptance`
- `## Verification`
- `## Notes from implementation`

## Cursor — campaign cards only

Most cards don't need this. Add it only when a goal won't finish in one context window — a campaign (see `../ai_rules/coordination_axes.md`). It is the one-line "you are here" a fresh window reads to resume *without* re-reading the whole handoff. Put it at the very top of the card, right under the title:

```md
> **Cursor:** S2 — next: bake fields onto served features. Done: S1 (verified, 4/4 Playwright). Goal: <one line>.
```

Advance it at every slice checkpoint: when a slice lands (with its verification evidence in the Slices ledger below), move the cursor to the next slice and stop with margin. The cursor + the slice ledger are what let the next window page in cheap and trust what is already done.

## Decisions and questions

When a card has a real fork, suggested answer first:

```md
### 1. Question?

**Suggested:** One-line answer.

**Why:** Short rationale grounded in source docs, field evidence, or project constraints.

**Alternatives:**
- **Alternative:** Why it loses.
```

Do not invent weak alternatives to make the format look balanced. If there is one real answer, say that.

## Acceptance

Use checkbox lists for done conditions:

```md
[ ] Source register exists.
[ ] Publish exports filter disallowed material.
[ ] Print PDF can be generated from the same data spine as the web map.
```

## Verification

Verification should be reproducible.

Good:

- `ogrinfo <file>`
- Open the QGIS project and confirm PostGIS layers are editable.
- Export the print PDF and inspect date/version stamp.

Weak:

- "Verify the map works."

If the next person cannot run the check, the card is not done explaining itself.
