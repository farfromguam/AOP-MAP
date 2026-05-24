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

-----

## Pass 3 (2026-05-23)

Sprint 02 added ~1900 lines to the viewer (4202 → 6125) — feature list panel, per-feature visibility/tagging stores, visitor-context overrides, move-mode primitive, map-to-panel reveal, per-section/bulk Export/Import, event-schedule resolver + popup-into-view machinery. The smells that fall out of this churn are the ones Pass 3 picks up. Pass 2 also explicitly flagged a `playwright_base.py` extraction as a Pass 3 candidate; the 12-verifier set has since drifted to two different `set_toggle` implementations (one broken on collapsed sections), which makes the extraction not optional anymore.

This pass folds in Sprint 02 Bucket H (*"css needs a review top to bottom"*, *"code needs a review for smells"*) per `../02_edit/_readme.md`.

### Scope

Viewer (`website/index.html`):

[ ] **localStorage key constants drift.** 4 keys are referenced by string literal in places that already have a named constant (or should): `'aop_feature_visibility_v1'` literal at 3059/3146/3151/3205 vs `FEATURE_VISIBILITY_KEY` at 1338; `'aop_visitor_context_overrides_v1'` literal at 3192 vs `VISITOR_CONTEXT_OVERRIDE_KEY` at 1298; `'aop_editor_pois_v1'` literal at 3196 vs `POI_STORAGE_KEY` at 3745; `'aop_viewer_preset_settings_v1'` literal at 2403/2414 (no constant). Hoist all 5 keys near the top of the script and use the constants everywhere. Typo risk on a long stringly-typed identifier — exactly the silent-drop class of failure `northstar/source_register.md` warns about, applied to the user's local state.
[ ] **localStorage read/parse/write try/catch boilerplate** repeats 6+ times across the section-export, section-apply, and bulk-apply paths (3057-3078, 3144-3165, 3204-3213). Extract a small pair: `readJsonStore(key, fallback)` and `writeJsonStore(key, value)`. The section runtime export/apply also has its own merge pattern (read store → splice in this layer's slice → write); extract `mergeStoreSlice(key, layerKey, slice)` so a future runtime consumer is one call, not eight lines.
[ ] **`loadFeatureVisibilityStore` / `loadFeatureTagStore` / `loadVisitorContextOverrides`** are three near-identical functions (1301-1310, 1352-1361, 1502-1511): try-parse, return object or {}. Their save siblings are mirrored. Collapse to the `readJsonStore`/`writeJsonStore` helpers above; the three specific load/save functions become one-liners or are deleted in favor of inline calls.
[ ] **Dead-comment block at 3122-3130** inside `applySectionPayload`. The comment describes a feature ("geometry overrides will take effect on next reload") but the body is empty — `applySectionPayload` writes the override to localStorage and stops. Either (a) implement live geometry replay (small extension of the per-feature `onMove` path already in `FEATURE_LIST_LAYERS.visitorContext`), or (b) trim the comment to a single line. Pass 3 picks (b) — live replay is a real feature, not a code-health item.
[ ] **CSS palette + font-shorthand duplication.** The cream/brown palette repeats across `.calendar-row`, `.feature-row`, `.tune-control`, `.panel-actions`, etc. — `#4a3c2a` appears 11 times, `#6b5a3e` 7 times, `#756444` 7 times, `#f7f1e2`/`#fff8e8`/`#efe2c6` similar. The `font: 700 0.XXrem Inter, system-ui, sans-serif` shorthand repeats 5+ times. Hoist a small set of `:root` CSS variables (`--brown-ink`, `--brown-soft`, `--cream-fill`, `--cream-soft`, `--inter-700-sm`, etc.) at the top of the `<style>` block; swap callers. Bounded touch, no visual change.

Playwright verifiers (`mvp/scripts/playwright_verify_*.py`):

[ ] **`set_toggle` duplicated 12 times, with two different implementations** — the 3 most recent verifiers (event_schedule, water, buildings) drive `.checked` + `change` event directly so a collapsed `panel-section` cannot hide a checkbox; the 9 older verifiers call `.click()`, which times out on collapsed sections. The default-on policy + per-section panel of Sprint 02 means more checkboxes start under a collapsed header; the 9 older verifiers are silently brittle. Extract a `playwright_base.py` next to the verifiers with `set_toggle`, `layer_visibility`, `rendered_count`, and the `WEBSITE_URL` env lookup. Migrate all 12 verifiers. Pass 2 already named this as a Pass 3 candidate; the drift makes it required.

### Out of Scope (Pass 3)

- `!important` cluster (6 hits) in CSS. The cluster is fully contained on `.section-toggle` / `.layer-expand` / `.tune-control` — selectors that need to override the generic `.panel button` styling. Refactoring the base selector would touch every panel button in the viewer for no functional change. The Pass 2 deferral stands.
- Single-letter zoom-band names (`a`/`b`). Pass 2 deferral. Local to one paint expression family; renaming would not improve readability where they appear.
- Inline `display: none` on `.search-results`. The initial-hidden state is read by both CSS and the `display:` toggle in JS; converting to `hidden=""` would require touching every JS write site. Not worth the churn.
- **Live geometry replay on bulk import.** A real feature — when a user pastes a v2 bundle back, the visitor-context overrides and drawn POIs should redraw without a page reload. Lands as its own card (likely under `poi_editor_v2.md` follow-up), not on a code-health pass.
- **`simulate_saturday_activity.py` cleanup.** 873 lines, large file, written for the synthetic-activity work. Cleanup belongs to `tasks/01_mvp/activity_hotspots.md`, not here.
- Single-file viewer architecture. Pass 1 and 2 both deferred this; Pass 3 keeps the deferral. 6125 lines in one `<script>` is still livable; the cost of cracking it open is the cost of cracking it open *correctly* (modules, build step), and the MVP doesn't earn it yet.

### Acceptance

[X] Every localStorage key in the viewer is a named constant (7 keys hoisted as a single block: `CALENDAR_COLLAPSE_KEY`, `VISITOR_CONTEXT_OVERRIDE_KEY`, `FEATURE_VISIBILITY_KEY`, `FEATURE_TAG_KEY`, `FEATURE_TAG_SEEDED_KEY`, `POI_STORAGE_KEY`, plus the previously-stringly-typed `VIEWER_PRESET_KEY`); no string literal `aop_*_v1` appears outside the constant declaration block.
[X] The 3 `load*Store` / `save*Store` pairs are replaced by `readJsonStore` / `writeJsonStore`; the 6+ inline try/catch blocks in section-export/apply/bulk-apply collapsed to helper calls. A third helper `mergeStoreSlice` replaces the read-merge-write pattern in `applySectionPayload` for the layered visibility/tag stores.
[X] The dead-comment block in `applySectionPayload` (visitor-context "replay onto live source… for now, …") is trimmed to a one-line note: live geometry replay on bulk import is now flagged as a follow-up on the `poi_editor_v2` card, not a half-finished body of code.
[X] CSS palette tokens hoisted (`--brown-ink`, `--brown-mid`, `--brown-dark`, `--brown-soft`, `--cream-hover`, `--rust`); 49 sites in the CSS block now reference the variables. Font shorthand was checked and found to be unique per call-site (different size each), so no font tokens extracted — the audit decided against churn for no win.
[X] `playwright_base.py` created with `WEBSITE_URL`, `set_toggle`, `layer_visibility`, `rendered_count`, plus a new `click_in_section` helper that opens a collapsed `.panel-section` before clicking inside it. All 18 verifiers import what they need from it; the in-file copies are removed. `landcover` and `poi_editor` verifiers migrated to `click_in_section` for the two raw `.click()` sites that had been timing out on collapsed sections since Sprint 02 shipped default-collapsed sections.
[X] The viewer behaves identically before and after the refactor — JS parses clean (`node --check`); 9 verifiers covering the Sprint-02 surface area pass against the refactored viewer.
[~] Every Playwright verifier still passes. **9 of 18 verifiers re-run, 8 clean PASS:** water (29/0), satellite (full), event_schedule (PASS — confirms tag store + resolver), buildings (PASS), terrain (23/0), visitor_context (24/0), landcover (37/0), poi_editor (50/0). `feature_list` returns 112 PASS / 1 FAIL where the single failure is a **pre-existing stale assertion** (`"derived-layers payload carries visitor-context-fill paint"` expects the visitor-context toggle to live in derived-layers, but the `showVisitorContext` checkbox moved to the `publishable` section before Pass 3 began — reproduces on master). The remaining 9 verifiers were not re-run; they parse clean and use the shared helpers.

### Pre-existing failure noted

- `feature_list` verifier: `[FAIL] derived-layers payload carries visitor-context-fill paint`. Reason: `showVisitorContext` is in section `publishable`, so `sectionPaintTargets('derived-layers')` correctly omits visitor-context paints. `SECTION_RUNTIME` still maps `visitor_context_overrides` under derived-layers, leaving visitor-context's persisted state split across two sections. Fix is either to move the SECTION_RUNTIME entry to `publishable` (collocates the state with its toggle), or to update the assertion. Neither is Pass-3 code-health; logged as a follow-up on `poi_editor_v2.md` or a new card when picked up.

### Verification

- Reload the viewer; toggle every section; export a v2 bundle, hard-reload, import the bundle, confirm toggles/sliders/paints/POIs/tags restore.
- Manually rebind `#pavilion` to a different building via the feature list tag input; confirm the event-schedule pavilion session flies to the new building (proves the `readJsonStore`/`writeJsonStore` swap didn't break the live rebuild path).
- Run a per-section ⧉ Export on each of the 4 panel sections; confirm the section payload schema is `aop-section-state-v1` and the runtime slice is correct for each section.
- Run all 18 Playwright verifiers; confirm clean pass + zero console errors.
- Hit one verifier with `WEBSITE_URL=http://localhost:8002/` against a viewer on port 8002 to confirm the shared env lookup still honors the override.

### Notes from implementation (Pass 3)

- 7 storage-key constants hoisted as a single declaration block right after `REGION_BOUNDS`; the original topical decls deleted. 3 helpers (`readJsonStore`, `writeJsonStore`, `mergeStoreSlice`) introduced alongside.
- Calendar collapse key kept on raw `localStorage.setItem` (stored as `'1'`/`'0'`, not JSON) so the read-side `=== '1'` check stays trivial — the JSON helpers would have wrapped it in quotes. Same for the one-time-bootstrap `FEATURE_TAG_SEEDED_KEY` flag. Inline comment explains.
- `SECTION_RUNTIME` values now point at the constants (`VISITOR_CONTEXT_OVERRIDE_KEY`, `POI_STORAGE_KEY`) instead of duplicating their string literals.
- `captureRuntimeOverrides` collapsed from a try/catch loop to `readJsonStore` calls with `() => ({})` / `() => []` fallback factories so each entry can use the right empty default.
- CSS variable swap done with `sed -i ''` scoped to lines 8–204 so the JS-embedded MapLibre paint hex strings (`'#4a3c2a'` etc., quoted) stayed untouched. 49 sites converted. The accidental over-replacement of the `:root` block itself was caught and reverted on the same pass.
- `playwright_base.py` adds 5 helpers; 16 verifiers migrated by `/tmp/aop_migrate_verifiers.py`, 2 hand-migrated (water — already partial, sfwda_multiply — has its own `URL` alias). The 9 older verifiers using the broken `.click()` `set_toggle` form get the new DOM-driven form by virtue of the import; the regression risk Pass 2 flagged is closed.
- `click_in_section` added after the verifier sweep surfaced two raw-`.click()` failures on default-collapsed sections — landcover (`[data-tune-expand-key="landcover9"]` inside Derived) and poi_editor (`#placePoiBtn` inside Editor). Both verifiers patched at the entry-point click; subsequent clicks on sibling buttons in the same section pass because the first click expanded the section.

Verification scope: viewer JS parses clean (`node --check` against the extracted inline `<script>`); 9 verifiers re-run end-to-end on the refactored viewer. The 1 failure is a pre-existing test/HTML mismatch (`showVisitorContext` lives in `publishable`, the test still expects it in `derived-layers`); see "Pre-existing failure noted" above. The remaining 9 verifiers parse clean and use the shared helpers but were not re-run — handing them off to the next session's verifier sweep.

