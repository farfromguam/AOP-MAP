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

### From Sprint 04 triage (2026-05-30)

Sorted out of `../04_event_app/` during the sprint-04 review. Each card carries
its own "Deferred because" header. Reasons in brief:

- `event_crud_upload_loop.md` — the sprint's main future thrust; not started.
  Needs scoping decisions (accounts/invite, moderation owner, R2/S3, photo
  publishability, GPX timestamps, QGIS-review gate) and a storage baseline.
- `paper_map_trail_extraction.md` — **partial/active.** Extraction pipeline
  shipped and serving raw-zone data; promotion to `core`/`publish` + the open
  refinements await a user review pass. May belong on an active sprint if the
  edited-SVG loop continues — flagged in the triage report.
- `star_driven_poi_list.md` — bake-first SERVE slice shipped (split to
  `_done/bake_first_poi_serve_slice.md`); the AUTHOR half + pipeline forks await
  a user decision.
- `dev_db_snapshot_reseed.md` — POI dev-fixture shipped (in the same `_done`
  slice card); the full DB dump/restore mechanism is unbuilt, wants a stable
  `core` schema first.
- `data_integrity_publishability.md` — only the positioned-feature bake is done;
  the rest is gated on outside truth (real trail data, acreage, DEM, POI gaps).
  Owns the building-tag promotion routed out of misc_4.
- `brand_assets_and_permissions.md` — blocked on the brand-use permission
  decision + the default-on reconcile; asset cleanup follows.
- `calendar_placeholder_state.md` — blocked on a user variant pick.
- `park_bounds_icon_apply.md` — blocked on a user `PB1`–`PB9` icon pick.
- `rock_warblers_content_audit.md` — gated on Rock Warblers confirming real
  event details.
- `poi_editor_followups.md` — discretionary editor refinements; some wait for
  real app storage.
- `viewer_polish_followups.md` — standing polish + verifier-residue backlog;
  pull items into an active sprint as they earn priority.

## Promoted out

- `poi_editor_v2.md` → `../02_edit/poi_editor_v2.md` (2026-05-23). Scoped by user: POI list on the right, select to find, drag to move; shared positioning primitive reused by region callouts and (later) logos.

## Lifecycle

A card promotes out of here by getting moved into an active sprint directory with a real scope and an Acceptance section. A card that stops mattering gets a "Killed because" line and stays here as a record; it does not get deleted.
