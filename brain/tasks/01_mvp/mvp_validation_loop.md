# MVP Validation Loop

TL;DR: Test one round of the AOP MVP observation review and promotion loop.

## Purpose

Prove the loop that turns observations into trustable map updates before building any submission or editing UI.

## Sources

- `aop_brain/northstar/validation_loop.md`
- `aop_brain/northstar/map_northstar.md`
- `aop_brain/tasks/aop_south_pittsburg_map_build_card.md`
- `aop_brain/handoff/session_context.md`

## Scope

- Use the MVP environment to capture an observation or board/photo review.
- Record source, confidence, and review outcome.
- Promote the observation into the map only if validation criteria are met.
- Document what worked and what failed.

## Acceptance criteria

- One observation is captured and attached to a source.
- The review process is documented.
- The observation promotion path is traceable.
- Any MVP stack failure is recorded clearly.

## Verification

- Confirm the observation can answer: what, source, confidence, publishable, last checked.
- Confirm the promotion path from evidence to map update is documented.
- Confirm the next session can continue from `aop_brain/handoff/session_context.md`.

## Notes

If `mvp/docker compose up -d` fails again, capture the error and update the handoff notes instead of guessing the fix.
