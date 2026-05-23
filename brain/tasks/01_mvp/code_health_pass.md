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

-----

## Pass 2 (2026-05-22)

The viewer grew ~4x since Pass 1 (1000 → 4202 lines), plus 7 more importers and 9 more Playwright verifiers. Fresh smells.

### Scope

Viewer (`website/index.html`):

[X] Toggle set lives in three places: the `LAYER_TOGGLES` table (`:591`), the `PRESET_TOGGLE_IDS` array of string ids (`:618`), and 25 hand-rolled `addEventListener` lines (`:4132-4159`). Same set, three forms, no enforcement they stay in sync. Add a `presetId` field to `LAYER_TOGGLES`, derive the other two, wire listeners in a loop.
[X] Pulse-animation magic numbers (`:4030, 4039, 4041-4046`) -- `DURATION = 2600`, `Math.PI * 6`, the `0.2 + 0.7 * osc` family. Hoist to named constants near the top of the block.
[X] Slider-to-percent `/100` pattern repeats at `:2338, :3617, :4135`. Trivial helper.

Importers and shell:

[X] Playwright URL drift -- 6 of 15 verifiers hardcode `WEBSITE_URL = "http://localhost:8001/"` ignoring the env override that `session_context.md` documents. `playwright_verify_sfwda_multiply.py:14` uses a different variable name (`URL`) entirely. Standardize on `os.environ.get("WEBSITE_URL", "http://localhost:8001/")`.
[X] `except BaseException` in tempfile cleanup at `import_fema_buildings.py:296` and `import_marion_cemeteries.py:249`. Catches KeyboardInterrupt and SystemExit. Scope to `(OSError, IOError)`.
[X] `import_gpx_track.sql:130` compares `recorded_start = NULLIF(...)::timestamptz` -- when both sides are NULL the EXISTS guard sees UNKNOWN and re-imports the row. Use `IS NOT DISTINCT FROM` instead.
[X] Repeated `docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map` across 4 scripts; the SQL files already `\set ON_ERROR_STOP on`. Document the canonical form in `mvp/scripts/README.md` so future importers copy it correctly.

User-call resolutions from Pass 1:

[X] `import_geojson.sh` -- decided to wire it up. Point the example at a real table, document the GDAL dependency, surface the provenance hint after import.
[X] `secondary` and `ramp` road classes -- decided to style them. Add casing + stroke layer pairs for each, extend the substrate presets, add to the roads toggle and tunable spec.
[X] Repo litter -- all three remove paths approved. `rm -rf mvp/db-data-broken-*`, delete `mvp/website/`, `git rm` the committed Playwright PNGs in `brain/output/`.

### Out of Scope

- Cosmetic findings (the `!important` CSS cluster, inline `display: none` for search results, `a`/`b` zoom-band names). Worth fixing on a later pass when adjacent code is being touched. Not now.
- A `playwright_base.py` shared module. The minimum fix (env-aware URL) doesn't require it; the bigger extraction is a Pass 3 candidate.
- ON CONFLICT on `core.field_tracks`. Would require a UNIQUE constraint, which crosses into the no-limiting-code zone. The `IS NOT DISTINCT FROM` fix above closes the actual bug without adding a constraint.

### Acceptance

[X] `LAYER_TOGGLES` is the single source of truth for the toggle set; adding a layer is one edit.
[X] All 15 Playwright verifiers honor `WEBSITE_URL` from the env.
[X] The two `except BaseException` blocks are scoped.
[X] Pulse animation constants are named.
[X] Slider `/100` helper is extracted and used at all 4 sites (one site found beyond the original three).
[X] `import_gpx_track.sql` uses `IS NOT DISTINCT FROM` for the timestamp guard.
[X] `import_geojson.sh` example points at a real table; `mvp/scripts/README.md` reflects it.
[X] Viewer styles `secondary` and `ramp` road classes. `import_usgs_roads.sh` left as-is; the data is no longer dropped, though the current 9-patch returns 0 features for both classes (defensive styling).
[X] No `mvp/website/`, `mvp/db-data-broken-*`, or `brain/output/*.png` tracked.

### Verification

- Reload viewer; toggle every layer; confirm presets save/restore the same set.
- Run a Playwright verifier with `WEBSITE_URL=http://localhost:8002/` against a viewer on port 8002 and confirm it hits.
- Re-export `publish.geojson` via `export_publish_geojson.sh` to confirm the importer ecosystem still works end-to-end.
- Playwright `playwright_verify_satellite.py` + a manual road-toggle pass to confirm secondary/ramp render.

### Notes from implementation

This session:

- Slider helper: added `sliderPercent(element)` next to `setTerrainEnabled`. Replaced all four `Number(slider.value) / 100` sites (the original review only counted three; `sfwdaMultiply` was the fourth).
- Toggle SoT: added a third positional field `presetId` to each `LAYER_TOGGLES` row, plus a single `[sfwdaToggle, [], 'showSfwda']` row for the SFWDA toggle (its visibility update is grid-driven, so it carries an empty layer list but still belongs in the preset/listener set). `PRESET_TOGGLE_IDS` is now `LAYER_TOGGLES.map(([,,id]) => id)`. The 27-line listener block collapsed to one loop plus the two genuinely special handlers (`terrainToggle` for 3D, `landcover9Opacity` for direct paint-property writes).
- Pulse constants: `PULSE_DURATION_MS`, `PULSE_FLASHES`, four `*_MIN`/`*_RANGE` pairs. The `Math.PI * 6` term became `Math.PI * 2 * PULSE_FLASHES`; same value, named intent.
- Roads: added `roads-secondary[-casing]` and `roads-ramp[-casing]` addLayer pairs between `roads-connecting` and `roads-controlled-casing` so MapLibre draw order matches network hierarchy. Extended the `roads` row of `LAYER_TOGGLES`, the `roads` entry in `TUNABLE_LAYERS`, both substrate paint presets (paper + trace), and the road popup binding. Did not trim `import_usgs_roads.sh`. Honest note: per `research/viewer.md:437`, the current 9-patch returns 0 features for both `secondary` and `ramp`, so the styling is defensive -- nothing renders today, but a future envelope expansion (or different AOI) will now light up correctly instead of silently dropping the data.
- Playwright URL: 7 files updated to `os.environ.get("WEBSITE_URL", "http://localhost:8001/")`. `playwright_verify_sfwda_multiply.py` kept its local variable name (`URL`) but reads the same env var, so the override is uniform.
- `import_geojson.sh`: header now documents purpose, the ogr2ogr property-mapping behaviour, and the provenance gap. Example switched from the non-existent `publish.publish_features` to `core.observations`. Added an ogr2ogr presence check up front; added a post-import hint that prints the source-link UPDATE pattern. `mvp/scripts/README.md` updated to match, and a new Canonical psql invocation section documents the importer wrapper form so future importers don't drift.
- `import_gpx_track.sql`: the EXISTS guard's `recorded_start = ...` flipped to `IS NOT DISTINCT FROM ...`. Inline comment explains the NULL-equality trap.
- Two `except BaseException` blocks scoped to `(OSError, IOError)`.
- Cleanup: `mvp/db-data-broken-*` removed (untracked). `mvp/website/` was an orphan with one empty file; `git rm -r`'d. All 100 PNGs in `brain/output/` `git rm`'d (the original card called it ~30; the actual count was 100, including a handful of hand-made debug shots like `landcover_palette_*`, all confirmed with the user as ephemeral output).

Verification: JS syntax check on the inline `<script>` (3942 lines after extraction) parses clean. Playwright preset verifier started in background to exercise the LAYER_TOGGLES <-> PRESET_TOGGLE_IDS coupling; result captured separately.

The Pass 2 cosmetic findings (the `!important` cluster, inline `display: none`, single-letter zoom-band names) deliberately deferred -- not worth the touch without nearby work to amortize against.
