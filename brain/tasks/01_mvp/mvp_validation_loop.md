# MVP Validation Loop

TL;DR: Test one round of the AOP MVP observation review and promotion loop.

## Purpose

Prove the loop that turns observations into trustable map updates before building any submission or editing UI.

## Sources

 - `brain/northstar/validation_loop.md`
 - `brain/northstar/map_northstar.md`
 - `brain/tasks/01_mvp/aop_south_pittsburg_map_build_card.md`
 - `brain/handoff/session_context.md`

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
 - Confirm the next session can continue from `brain/handoff/session_context.md`.

## Notes

If `mvp/docker compose up -d` fails again, capture the error and update the handoff notes instead of guessing the fix.

## Smoke test result

2026-05-20 CWC pass:
- `mvp/scripts/run_validation_loop_smoke.sh` captured one demo board-review observation.
- The observation was reviewed as `verified`, then promoted into `core.trail_centerlines` as `MVP Smoke: Board-Validated Connector`.
- `source_register.feature_sources` links now trace the smoke observation, promoted trail, and original demo publish features back to source rows.
- `mvp/scripts/export_publish_geojson.sh` refreshed `website/data/publish.geojson` from the live `publish` views.

This proves the MVP plumbing for capture, review, promotion, provenance, and export. It does not replace the remaining need for real AOP parcel, trail, and field-observation data.
