# Flows

TL;DR: Reusable workflows live here. Invoke one by name (`~~flow_name`) or, in Claude Code, via its `/flow` skill (`/cwc`, `/plan-task`, `/work-task`, `/research-flow`).

Writing here: see `../voice/voice_guide.md`.

Context chain:
- `_readme.md`
- `flows/_readme.md`

#aop #flows #workflow

-----

Active flows:

- `research_flow.md` -- produce a focused research brief.
- `plan_task.md` -- turn a request into a card that can be executed.
- `work_task.md` -- execute a prepared card and record what happened.
- `council_review.md` -- convene the review council over finished work before declaring it done.
- `cwc.md` -- continue MVP work with current handoff and validation loop context.

These flows are also exposed to Claude Code as thin skill pointers in `.claude/skills/<flow>/SKILL.md`. Those files hold no content of their own — they only point back to the flow doc here, which stays the single source of truth for every agent.

Flows are reusable process. Project facts belong in `northstar/`, `research/`, or `tasks/`.
