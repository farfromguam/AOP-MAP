# AGENTS

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
5. Read `brain/tasks/` — the current build card is named in the brain map.

Only after those five reads should you take action on the user's request.

## Where to look next

If you need to find something specific, use `brain/search_map.md` before grepping the codebase. It routes keywords to the right brain file.

If the user asks you how to collaborate, what tone to use, or what not to touch, read `brain/ai_rules/`. Those rules are durable and apply to every agent in this repo.

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
