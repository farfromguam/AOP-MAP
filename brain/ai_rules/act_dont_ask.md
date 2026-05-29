# Act, don't ask

TL;DR: Default to acting. If the next step is reversible, has clear precedent in the brain or the codebase, or is bounded by a card, do it. Save questions for true forks.

#ai_rules #pacing #questions

-----

The user has called out, more than once, that the assistant asks too many yes/no questions and then doubles back to confirm things that were never in doubt. That cadence makes it impossible to stay in flow and forces the user to babysit work that should already be moving.

## When to act without asking

- The brain already has the answer (search `search_map.md`, then read).
- The repo already has the convention (run the existing scripts, follow the existing port discipline, etc. — see `canonical_spinup_commands.md`).
- A current task card directs the work.
- The action is reversible (edit a file, run a verifier, take a screenshot, write to `brain/output/`).
- The change is bounded and small enough that showing the result is faster than describing it.

In those cases: do the thing. Surface the result. Let the user redirect after if needed.

## When asking is warranted

- The work has a real fork that changes scope or visible product behavior (two different design directions, two different data sources, two different schemas).
- The next step is destructive or hard to reverse (git history rewrites, deleting persisted data, dropping a layer, regenerating an export that the user has been editing by hand).
- The brain is silent or contradictory and the user is the only authority.

When asking, ask once, with one question, with the assistant's recommendation up front. Do not stack three yes/no questions in a row to confirm a single line of work.

## How to apply

- Before opening `AskUserQuestion`, check: is this a real fork, or am I confirming the obvious? If the latter, close the prompt and act.
- Strings like "should I", "want me to", "is it okay if" are warning signs. Replace them with the action itself and a short note about what just happened.
- Do not re-ask "what's next?" / "which item next?" after every unit of work. Pull the next card from `brain/tasks/` yourself and keep moving. Only surface a "what next" choice at sprint/bucket boundaries, or when two queued items genuinely conflict in priority. A transcript audit (2026-05-29) found this next-task polling, alongside "want me to?", was the dominant source of question fatigue.
- If a question is unavoidable, lead with the recommendation, not the menu. See `commit_in_prose.md`.

See also: `commit_in_prose.md` (recommend, don't menu), `move_slowly.md` (slow on core forks, not on routine work), `canonical_spinup_commands.md` (one set of defaults, not a question).
