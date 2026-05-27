# Dev DB Snapshot + Reseed

Date: 2026-05-24

TL;DR:
- We need a repeatable way to dump configured PostGIS data to a file and reseed a fresh dev database.
- This is not production backup design. It is dev/pre-prod consistency and "don't lose the configured work."
- The seed should become clean enough that a new port spinup lands in the same known state.

#aop #03_event_app #database #seed #dev

-----

## Source

- `misc.md` user note, 2026-05-24.
- `../../northstar/source_register.md` for provenance discipline.
- `../../northstar/validation_loop.md` for observation -> review -> promote shape.
- `../../../mvp/init_db.sql` for the base schema.
- `../../../mvp/scripts/export_publish_geojson.sh` for current publish export.

## Job

Create a durable dev data snapshot path:

1. Export configured DB data to a file.
2. Restore that file into a fresh local DB after `init_db.sql` runs.
3. Export `website/data/publish.geojson`.
4. Verify the viewer sees the same dev/pre-prod state.

This gives the project a known state even if `mvp/db-data/` disappears.

It also gives future "new port" spinup a concrete consistency check: fresh DB,
seed import, publish export, viewer verifier.

## Scope

- Include `source_register`, `raw`, and `core` base tables.
- Do not dump `publish` views as source data; regenerate them from `core`.
- Prefer a reviewable seed file if the data size stays reasonable.
- Add an import/reseed command that starts from an initialized schema and
  replaces dev data intentionally.
- Run `export_publish_geojson.sh` after reseed so the static viewer file stays
  derived from the DB.
- Document which rows are dev fixtures, raw context, reviewed observations, and
  publishable map truth.

## Cleanup Before Dev Seed

The first dump may contain useful but messy state. Before it becomes the dev
seed, decide what earns a permanent row.

Examples already called out:

- FEMA houses may move from raw reference into a polygon/facility layer once
  tagged and reviewed.
- Tagged configured data should reseed to the same state, not depend on
  browser-local edits.
- Demo/smoke rows should be clearly named, retired, or excluded before the
  seed pretends to be pre-prod truth.

## Acceptance

- [ ] One export command writes a DB data snapshot file.
- [ ] One reseed command loads that file into a fresh initialized DB.
- [ ] Reseed is intentionally replacing dev data, not merging silently.
- [ ] `export_publish_geojson.sh` after reseed produces the expected layer
      counts.
- [ ] A new local spinup can run reseed + viewer verification and get the same
      state as current dev.
- [ ] The seed cleanup policy is documented before the file becomes pre-prod
      fixture data.

## Out Of Scope

- Cloud backup, PITR, production restore, or managed database policy.
- Public uploads and moderation storage. Those stay on
  `full_loop_crud_upload_audit.md`.
- Browser `localStorage` export/import. This card is database state.
