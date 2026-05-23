# Sprint 03: Deferred

Sister sprint to the active one. Parking lot for cards explicitly deferred out of an active sprint — work that has a known shape but is waiting on a gating decision, a stable surface, or a larger chunk of focus than it can get inside the current sprint.

Nothing in here is abandoned. Each card carries a "Deferred because" section so the reason is visible the next time someone scans the brain.

#aop #sprint #deferred

-----

## What lands here

- Cards from an active sprint that depend on something not yet decided or shipped.
- Multi-phase work that wants a stable layer set, schema, or data baseline first.
- Items that need a scoping conversation before they earn an implementation card.

## What does not land here

- Backlog research and feature-review notes — those live in `../backlog/`.
- Hard-blocked work with no path forward — kill it in the card it lives in, don't warehouse it here.
- Session-only TODOs — those don't belong in the brain at all.

## Current contents

- `offline_pwa.md` — deferred from `../02_edit/_readme.md` Bucket I. Waits for a stable layer set so the measurement isn't against a moving target.

## Promoted out

- `poi_editor_v2.md` → `../02_edit/poi_editor_v2.md` (2026-05-23). Scoped by user: POI list on the right, select to find, drag to move; shared positioning primitive reused by region callouts and (later) logos.

## Lifecycle

A card promotes out of here by getting moved into an active sprint directory with a real scope and an Acceptance section. A card that stops mattering gets a "Killed because" line and stays here as a record; it does not get deleted.
