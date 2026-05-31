# Harness adapters are thin

TL;DR: Claude Code skills, hooks, and slash commands are POINTERS into the brain, never copies of it. They carry no durable content of their own. The brain is the single source of truth; the harness only routes to it.

#ai_rules #brain #harness #durability #pointers

-----

> Stated by the user, 2026-05-31: the skill/hook files "should point to the brain alone. It is the durable artifact. There are multiple agents and you cannot have differing input. So these need to be thin and minimal."

## Why

Multiple agents and harnesses read this repo (Claude, Codex, others). Each harness exposes its own slots — Claude Code reads `.claude/skills/`, `.claude/hooks/`, `.claude/commands/`; another agent reads none of them. If durable prose is written into a harness slot, it becomes a SECOND copy that drifts from the brain, and different agents act on different, conflicting input. The brain exists precisely so there is one artifact every agent reads.

## The rule

- A skill / command file = YAML frontmatter (name + a one-line router description so the harness can surface it) and a body that says, in one line, "read `brain/<path>` and follow it." Nothing else.
- A hook script = the minimal deterministic logic (or a pointer via `additionalContext`); it names the brain rule it enforces, it does not restate it.
- Any explanation, procedure, rule text, or narrative belongs in the brain — `northstar/`, `research/`, `tasks/`, `flows/`, `practices/`, or `ai_rules/` per `brain_is_durable.md`.

## How to apply

When you reach for a harness primitive, write the content in the brain first (or confirm it is already there), then add the thinnest possible pointer in the harness slot. If you catch yourself typing procedure into a `SKILL.md` or a hook, stop — that text goes in the brain, and the adapter links to it. See `brain_is_durable.md`, `extract_before_invent.md`.
