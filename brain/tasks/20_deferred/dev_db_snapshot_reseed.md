# Dev DB Snapshot + Reseed

> **Deferred — Sprint 04 triage (2026-05-30).** The POI dev-fixture-in-fresh-DB
> piece shipped 2026-05-29 (recorded in the "Wired 2026-05-29" block below and
> split to `_done/bake_first_poi_serve_slice.md`). The card's main promise — a
> reviewable DB-data export + reseed-into-fresh-DB mechanism — is **deferred
> because** it is still unbuilt and wants a stable `core` schema baseline first.

Carry Sprint 03's dev/pre-prod data dump need into Sprint 04.

This is not production backup design. It is a repeatable way to keep configured
PostGIS state from vanishing when local containers or ports churn.

#aop #04_event_app #database #seed #dev

-----

## Source

- `../03_event_app/_done/dev_db_snapshot_reseed.md`
- `../03_event_app/_done/misc.md`
- `../../northstar/source_register.md`
- `../../../mvp/init_db.sql`
- `../../../mvp/scripts/export_publish_geojson.sh`

## Scope

Create a durable dev snapshot path:

1. Export configured DB data to a reviewable file.
2. Restore that file into a fresh local DB after `init_db.sql` runs.
3. Regenerate `website/data/publish.geojson`.
4. Verify the viewer sees the same dev/pre-prod state.

Include `source_register`, `raw`, and `core` base tables. Do not dump
`publish` views as source data; regenerate them from `core`.

## Cleanup Before Seed

Do not bless messy local state as pre-prod truth.

- Mark demo/smoke rows clearly or exclude them.
- Decide what FEMA building/house rows, visitor context, tags, and editor seeds
  earn as durable fixtures.
- Keep publishable map truth, reviewed observations, raw context, and dev
  fixtures visibly distinct.

## Acceptance

- [ ] One export command writes a DB data snapshot file.
- [ ] One reseed command loads that file into a fresh initialized DB.
- [ ] Reseed replaces dev data intentionally instead of merging silently.
- [ ] `export_publish_geojson.sh` after reseed produces expected layer counts.
- [ ] A new local spinup can run reseed + viewer verification and match current dev state.
- [x] Seed cleanup policy is documented before the file becomes pre-prod fixture data. *(POI fixture only — see below.)*

## Wired 2026-05-29 — POI dev fixture in fresh-DB bring-up

First concrete piece of this card, landed alongside the bake-first POI slice
(`star_driven_poi_list.md`). The full dump/restore mechanism is still unbuilt;
this only covers the destination-POI fixture.

- `mvp/scripts/seed_core_pois.sql` is now mounted into the db container's
  `/docker-entrypoint-initdb.d/` (`docker-compose.yml`). The PostGIS entrypoint
  runs `*.sql` in sorted order on a **fresh data volume**, and `init_db.sql`
  (schema) sorts before `seed_core_pois.sql` (data), so a brand-new dev DB comes
  up with the destination POIs already seeded — no manual seed step.
- **Verified** (2026-05-29) in a throwaway PostGIS container with a fresh
  volume: init runs schema → seed, leaving `core.pois`=3 rows and `publish.pois`
  exposing 2 (Pavilion, Ellis Cemetery); the unpublished candidate is gated out.
  (macOS note: ad-hoc `docker run -v file:file` init mounts hit "Operation not
  permitted"; mount the *directory* as initdb.d to reproduce.)
- Only affects **fresh** volumes. An existing `db-data` volume is untouched —
  apply the seed to a running DB by hand:
  `docker compose exec -T db psql -U aop -d aop_map < mvp/scripts/seed_core_pois.sql`.

### Seed cleanup policy (POI fixture)

- `seed_core_pois.sql` is **dev fixture data, not pre-prod truth.** Every row it
  writes is owned by the `source_register.sources` row named
  `'AOP bake-first POI seed'`; the script deletes rows by that `source_id` before
  re-inserting, so it is idempotent and never merges silently.
- Rows are derived one-time from `website/data/*` files and carry honest
  provenance (`permission`/`publish_status`/`confidence`). The unpublished
  candidate row is intentional — it exercises the `publish.pois` gate.
- When real authoring lands (the AUTHOR half), retire this seed or demote it to a
  smoke-only fixture; do not let hand-seeded rows masquerade as authored truth.

## Out of Scope

- Cloud backup, PITR, production restore, or managed database policy.
- Public uploads and moderation storage. Those live on `event_crud_upload_loop.md`.
- Browser `localStorage` export/import.
