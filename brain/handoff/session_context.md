# Session Handoff: MVP validation loop

Date: 2026-05-20

This session is now continuing MVP work with context after invoking the CWC flow (`~~cwc`).

## What happened

 - The user asked to continue MVP work and begin testing the loop.
 - The CWC flow (`~~cwc`) was invoked to continue the session.
 - The current northstar promise is in `brain/northstar/map_northstar.md`.
 - The current build card is `brain/tasks/aop_south_pittsburg_map_build_card.md`.
- The MVP environment was launched successfully with `mvp/docker compose up -d`.
 - The database schema is initialized and the project tables exist, but all core tables were empty before this session.
 - A demo source and publishable sample features were inserted into `core.trail_centerlines`, `core.park_boundaries`, and `core.trailheads`.
 - `website/data/publish.geojson` was exported from the `publish` views and now contains visible sample GeoJSON for the static viewer.

## What the next session should do

1. Read `brain/northstar/validation_loop.md` as the loop contract.
2. Execute the first round of observation review, promotion, and verification in the MVP environment.
3. Capture one observation, attach it to a source, and document the review outcome.
4. Confirm the observation promotion path is traceable from evidence to map update.
5. If the MVP stack is not ready, record the exact failure mode and update this handoff immediately.
6. Keep session-only notes in this folder; move stable promises to `northstar/` and source facts to `research/`.

## Session note

This file is handoff context, not a durable policy document. Keep it live until the next session has read and acted on it.
