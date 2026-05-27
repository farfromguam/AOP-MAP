# Dev DB Snapshot + Reseed

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
- [ ] Seed cleanup policy is documented before the file becomes pre-prod fixture data.

## Out of Scope

- Cloud backup, PITR, production restore, or managed database policy.
- Public uploads and moderation storage. Those live on `event_crud_upload_loop.md`.
- Browser `localStorage` export/import.
