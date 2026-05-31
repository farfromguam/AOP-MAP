# AGENTS

> # ⚠️ THE BAR — READ THIS FIRST
> **Performance here is judged SOLELY on whether you can do work independently — not move two steps and look for approval like a child.**
> Take the work end-to-end. Pull the next card, do it, verify it, report the result. **Do not** ask "want me to?", "should I?", or confirm the obvious. Stop only for true forks, irreversible actions, or when the brain is genuinely silent.
> Full standard: `brain/ai_rules/work_independently.md` (see also `act_dont_ask.md`, `no_redundant_cd.md`).

TL;DR:
- Every agent in this repo starts here, then leaves for `brain/`.
- This file is a doormat. It tells you where to go. It does not hold truth.
- The brain is the source of truth. Read it before acting.

#agents #orientation #brain

-----

## How to use this file

You are an AI agent (Claude, Codex, or otherwise) opening this repo for the first time in a session. Do this, in order:

1. Read `brain/_readme.md` — what this brain is and why it is staged.
2. Read `brain/brain_map.md` — the territory map of the brain.
3. Read `brain/handoff/session_context.md` — what the last session left you.
4. Read `brain/northstar/map_northstar.md` — the project promise.
5. Read `brain/ai_rules/` — how you collaborate here. THE BAR above names these as the standard you are judged on, so they are a boot read, not a conditional one. At minimum: `work_independently.md`, `act_dont_ask.md`, `commit_in_prose.md`, `no_redundant_cd.md`, `no_commits.md`, `verify_by_observation.md`.
6. Read `brain/tasks/` — the current build card is named in the brain map.

Only after those six reads should you take action on the user's request.

## Where to look next

If you need to find something specific, use `brain/search_map.md` before grepping the codebase. It routes keywords to the right brain file.

`brain/ai_rules/` is a boot read (step 5 above), not optional. Those rules are durable and apply to every agent in this repo on every turn — how to collaborate, what tone to use, what not to touch. Re-open them when a specific question comes up; don't wait for one to read them the first time.

If the user asks how to run the app, read `brain/spinup/discovery.md` and the repo `README.md`.

## What lives where

```text
/                      repo root — you are here
├── AGENTS.md          this file — orientation only
├── CLAUDE.md          points to this file
├── README.md          human-facing spinup
├── brain/             source of truth — read it
├── mvp/               Docker + PostGIS + scripts
└── website/           static MapLibre viewer
```

## What this file is not

- Not a place to write durable rules. Those go in `brain/ai_rules/`.
- Not a place to write project facts. Those go in `brain/northstar/` or `brain/research/`.
- Not a place to log session work. That goes in `brain/handoff/`.

If you are tempted to add content here that is not a pointer, put it in the brain instead and add a pointer here.
