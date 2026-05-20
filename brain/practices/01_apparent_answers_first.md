# Apparent Answers First

TL;DR:
- Most "open questions" are closed questions that have not been checked against existing material.
- Try to dissolve the question before treating it as open.
- If it survives, write the suggested answer first and show the tradeoffs.

#practice #aaf #decisions

-----

When a design choice surfaces, the easy move is to write it up as an open question with a few options.

Sometimes that is right. More often the answer is already apparent if you look in the right places.

For AOP map work, check these before opening a question:

- **Northstar.** Does `northstar/map_northstar.md` or `northstar/source_register.md` already settle it?
- **Request.** Did the user already say the intent in plain language?
- **Research.** Does `research/` already contain the source fact or caveat?
- **Logic.** Do the constraints force one answer?
- **Field reality.** Would the map be unsafe, misleading, or unpublishable under one option?
- **Future path.** Does the task card already name the staged direction?

If the answer dissolves, write the conclusion and cite the source. Do not preserve fake uncertainty.

If the question remains open, use the task-card picker:

```md
### 1. Question?

**Suggested:** The most likely answer.

**Why:** Evidence and tradeoff.

**Alternatives:**
- **Other answer:** Why it loses or what it buys.
```

Suggested is first because the reader should not have to reverse-engineer your recommendation.
