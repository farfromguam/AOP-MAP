# Code Health Pass

A deep review of the MVP code (`website/index.html`, `mvp/init_db.sql`, the importers, the shell and Playwright scripts) turned up a set of smells. None block the MVP, but a few are landmines worth defusing before real AOP trail data lands.

The shape of the fix: tighten the schema so a typo can't silently drop a feature from publish, kill duplicated DDL and viewer boilerplate, and clean up the repo litter. One pass, verify as it goes.

#aop #tasks #mvp #code-health #cwc

-----

## Scope

Resolution checklist, grouped by where it bites.

Schema (`mvp/init_db.sql` and the SQL importers):

[ ] CHECK constraints on the status columns -- decided against for now (2026-05-20). The user wants everything to display while the data is still settling, so limiting code stays off. The exact-equality publish gate remains a known, accepted risk. See Open Questions.
[X] Fix `promote_gpx_to_trail.sql`: it set `field_tracks.publish_status = 'reference_publish'`, a source-register value, not a feature publish_status. Now `hold`.
[X] Remove the dead `ALTER TABLE core.parcels ADD COLUMN IF NOT EXISTS` block in `init_db.sql` -- the `CREATE TABLE` directly above already declares those columns.
[X] Move `raw.arcgis_feature_captures` DDL into `init_db.sql`. It was being created as a side effect of `import_aop_parcel_boundary.sql`.
[X] Drop the duplicate `publish.parcels` / `publish.park_boundaries` DDL and the dead parcels/geom migration from `import_aop_parcel_boundary.sql` so the importer only imports data.
[X] Add GIST indexes on every `geom` column, plus an index on `feature_sources(feature_schema, feature_table, feature_id)` -- the provenance lookup key.
[X] Add a `BEFORE UPDATE` trigger so `updated_at` maintains itself instead of every importer setting it by hand.

Viewer (`website/index.html`):

[X] Extract a `bindPopup` helper -- 8 near-identical `map.on('click', ...)` handlers now route through it.
[X] Extract a `fetchJson` helper -- 6 copies of the same fetch-try-catch block collapsed onto it.
[X] Make `updateLayerVisibility()` data-driven (a `LAYER_TOGGLES` table); `GRID_N` hoisted so the SFWDA loop is bounded by the real grid size, not a magic `12`.
[X] Register `map.on('error', ...)` at the top of the load handler so a publish load failure no longer skips it.

Housekeeping:

[X] Unify the DB connection style -- `export_publish_geojson.sh` now uses `docker compose exec -T db psql`, matching the import scripts. No more hardcoded `mvp-db-1`.
[X] `chmod 644` published GeoJSON -- the three scripts that `mv` a temp file into `website/data/` (`export_publish_geojson.sh`, `import_usgs_roads.sh`, `import_usgs_hydrography.sh`) now `chmod 644`; existing `0600` data files were corrected.
[ ] `import_geojson.sh` is a drifted unused scaffold (needs GDAL, points at non-existent table `publish.publish_features`). Wire it up or delete it -- needs a user call. It is documented in `mvp/scripts/README.md`, so deleting means editing that too.
[ ] `import_usgs_roads.sh` fetches `secondary` and `ramp` road classes the viewer never styles. Style them or stop fetching them -- needs a user call (a what-the-map-wants decision).
[X] README drift -- `website/README.md` now lists the current publishable + reference layer set.
[ ] Repo litter -- added `__pycache__/` + `*.pyc` to `.gitignore`. Still worth removing by hand: `mvp/db-data-broken-*` (broken Postgres data dir, gitignored), `mvp/website/data/publish.geojson` (a stale orphan -- the live viewer is the repo-root `website/`), and ~30 committed Playwright PNGs in `brain/output/`. Removing tracked files is git work, left to the user per `ai_rules/no_commits.md`.

## Context

The full review is in the session that opened this card. The driving worry is the publish gate: `publish.trail_centerlines` and friends are `WHERE permission = 'publish' AND publish_status = 'publish'`. Those columns are bare `text`. A clean-looking wrong value is exactly the failure mode `northstar/source_register.md` warns about -- except here it fails silent, not visible.

The `promote_gpx_to_trail.sql` bug is the proof the risk is real: a wrong status value already shipped. It was harmless only because no `publish.field_tracks` view exists yet.

## Open Questions

### 1. What are the locked vocabularies for the status columns?

**Suggested:** Lock these sets, drawn from current code usage, then constrain:

- `permission`: `publish`, `internal`, `unknown`
- `publish_status` (feature tables): `publish`, `hold`, `demo_hold`
- `confidence`: `low`, `medium`, `high`
- `status`: `candidate`, `observed`, `verified`, `promoted`, `rejected`, `demo`

**Why:** `review_status` is already locked by the build card section 5 (`raw, reviewed, verified, rejected, needs_field_check`). The other four are used but never enumerated anywhere in the brain. The sets above cover every value the current SQL writes; they need a deliberate yes before becoming a constraint, because a wrong allow-set blocks future imports.

**Alternative:**
- **Leave them free-text:** less safe, and the whole northstar promise is trustworthiness. Loses.

`source_register.sources.publish_status` is a separate column with its own values (`reference_publish`, `reference_only`, `publish`) -- constrain it separately or leave it, but do not fold it into the feature vocabulary.

**Decided (2026-05-20):** Skip the constraints. The user's call, verbatim: "skip any limiting code. we want everything to display for now." No `CHECK` constraints go in while MVP data is still settling. The silent-drop risk stays documented here as an accepted tradeoff, to revisit once real trail data and the vocabularies have settled.

## Out of Scope

- The single-file viewer architecture. 1000 lines in one `<script>` is fine for the MVP; revisit when the event layer lands.
- The polymorphic `feature_sources` association. Inherent to the design; an index is enough for now.
- Migrating the live database. Schema edits land in `init_db.sql`; re-run it (idempotent) or write a migration when ready.

## Acceptance

[ ] Out-of-vocabulary status values -- not enforced; `CHECK` constraints decided against (see Open Questions). Risk accepted and documented.
[X] `mvp/init_db.sql` is the single home for schema DDL; importers only move data.
[X] `init_db.sql` re-runs clean against an existing database (idempotent).
[X] The viewer behaves identically before and after the refactor -- same layers, toggles, popups.
[ ] No dead scaffold scripts and no committed build artifacts left ambiguous -- `import_geojson.sh` and the committed PNGs still pending a user call.

## Verification

- `psql` an out-of-vocabulary `publish_status` into `core.trail_centerlines` and confirm the insert is rejected.
- Re-run `mvp/init_db.sql` against the live DB; confirm no errors and the new indexes/trigger exist (`\di`, `\dy`).
- Run `mvp/scripts/run_validation_loop_smoke.sh` then `export_publish_geojson.sh`; confirm `publish.geojson` still exports the expected feature set.
- Serve `website/` and confirm every toggle, layer, and popup still works (Playwright scripts in `mvp/scripts/` once `playwright` is installed).

## Notes from implementation

First pass, this session:

- `promote_gpx_to_trail.sql` `reference_publish` -> `hold`.
- `init_db.sql`: removed the dead parcels ALTER; added `raw.arcgis_feature_captures`, GIST geometry indexes, the `feature_sources` lookup index, and a shared `set_updated_at()` trigger across every table with an `updated_at`.
- `import_aop_parcel_boundary.sql`: stripped all schema DDL (dead parcels ALTER, the park_boundaries geom migration + view rebuild, `raw.arcgis_feature_captures`, `publish.parcels`); it is now data-only.
- The importers still set `updated_at = now()` by hand. Harmless next to the trigger; clean up later if it bothers anyone.
- Found and fixed a latent bug along the way: `init_db.sql` was inconsistent on `updated_at` -- the live DB has it on every core table, so a fresh init now matches.

Verification: `init_db.sql` was run against a throwaway database in the live container. Clean on first run, idempotent on re-run, 9 indexes + 10 triggers created. The live `aop_map` database was not modified -- re-run `init_db.sql` against it to apply the indexes and trigger (safe, additive, idempotent). `import_aop_parcel_boundary.sql` was not re-run; the change was pure deletion of DDL now owned by `init_db.sql`.

Viewer refactor (`website/index.html`), this session:

- Added `fetchJson(url, label)` and `bindPopup(layers, titleFor, rowsFor, footerFor)` helpers near `detailRows`. The 6 overlay fetches and 8 popup click handlers now route through them. `bindPopup`'s optional `footerFor` carries the lidar-tile Download-LAZ link.
- `updateLayerVisibility()` is now a loop over a `LAYER_TOGGLES` table. `GRID_N` was hoisted to top-level scope so the SFWDA tile loop runs `GRID_N x GRID_N`, not the old `12 x 12` scan.
- `map.on('error', ...)` moved to the top of the load handler.
- Verified: JS syntax check, then the full Playwright suite (satellite, lidar, terrain, community_trails, sfwda_multiply) re-run against a pre-change baseline -- identical results, all green, zero console errors. The suite does not click features, so a throwaway popup check confirmed boundary, road, and lidar-tile popups (including the footer link) still render.

Housekeeping pass, this session: unified the export script's DB connection style; added `chmod 644` to the three scripts that publish a GeoJSON via `mktemp`+`mv` and corrected existing `0600` files; refreshed `website/README.md`; added a Python-cache `.gitignore` rule. Verified the rewritten `export_publish_geojson.sh` by running it -- valid GeoJSON, 3 features, perms `644`.

Still open, all needing a user call: whether to delete or wire up `import_geojson.sh`; whether to style or stop fetching the `secondary`/`ramp` road classes; and removing the repo litter (`mvp/db-data-broken-*`, `mvp/website/`, committed Playwright PNGs) -- the tracked-file removals are git work, left to the user.

The `CHECK` constraints stay decided against (see Open Questions).
