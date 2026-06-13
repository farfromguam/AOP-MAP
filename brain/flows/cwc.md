# CWC

TL;DR: Continue MVP work with context by using the current handoff note, validation loop northstar, and build card.

This flow is the brain-level anchor for continuing the MVP without losing the session context.

## Use

- Invoke as `~~cwc` in conversation.
- Optional local helper: run `./cwc` from the repo root for a non-mutating MVP continuation check.
- For local spinup and troubleshooting, use `brain/spinup/mvp_runbook.md`.
- Use `brain/brain_map.md` to find the current active task card.
- Before claiming that card, check `brain/handoff/coord/` — if another session is live and claims it, take something else (concurrency axis; see its `_protocol.md`).
- If the active card carries a **Cursor** block, resume from it: read the goal + cursor + the one slice it names, not the whole handoff (depth axis; see `brain/ai_rules/coordination_axes.md`).
- Follow the current session handoff in `brain/handoff/session_context.md`.
- Respect the validation loop in `brain/northstar/validation_loop.md`.
- Do not hardcode the old Sprint 01 build card as the current work. It is a
  historical card under `_done/`; the active card moves with the sprint.

## Purpose

- Keep MVP work grounded in the documented validation loop.
- Avoid premature V2 intake or public submission work.
- Preserve source provenance, review status, and publish-safe export guidance.

## When to use

- When the user wants to continue MVP work from the existing context.
- When the session needs a handoff-safe restart point.
- When the MVP stack or database status should be checked before further changes.

#flow #cwc #mvp #handoff
