# Going Gold — PostGIS is the store of record; the bake is production; the edit path survives

> **User direction, 2026-06-06:** *"we are going gold. going to the db. and baking the
> output for production. still these things may need tweaks from now to day of. so I have
> been trying to preserve edit paths."* This is the decision, not a proposal.
>
> **Hardened by a full council review, 2026-06-06 (round 1: all six seats pulled andon;
> every grounded issue folded in below).** This card is written to be executed by an
> **autonomous ralph loop** — a fresh agent re-reading THIS card each iteration with no
> access to the conversation that produced it. So it must be self-contained, per-slice
> bounded, and observable. Read the **Loop contract** before doing anything.

TL;DR:
- `core` in PostGIS becomes the **single source of truth**. The **bake** (`core` →
  `publish` views → static `website/data/*.geojson`) is the **only** writer of the served
  files. Prod stays static + read-only (northstar V1).
- **The edit path is preserved by redirecting it, not removing it.** The web editor already
  exports its edits as a diff (`aop-panel-overrides-v1`). Today that diff bakes into the
  *files* (`bake_panel_overrides.py`) and fights the DB bake. We point it at **`core`**
  instead, reusing the **same parser**. localStorage drops to a **working buffer** (C3).
- **Day-of loop:** `edit → Export → apply-to-core → bake → deploy` — fast, auditable. No
  prod write-service, no auth, no moderation (V2 stays deferred — that's *why* this is doable).

#aop #sprint #06 #gold #postgis #bake #pipeline #northstar #editor_is_the_viewer #ralph

-----

## Loop contract (the autonomous executor MUST obey these — they are not optional)

1. **Do ONE slice per iteration, in order. Stop at the Retirement step.** Slice 6 is HELD
   (out of loop scope) until a human pulls it — see its section. If the current slice's
   acceptance is already green, move to the next; never re-do a green slice.
2. **Never commit, never `git` anything mutating, never bump `sw.js`/`#appVersion`.** The
   commit and the version bump are the **user's git gate** (`no_commits.md`). When a shell
   asset (`index.html`/`js/*.js`/css/`sw.js`) changes, **report the owed bump** in the
   handoff — do not perform it.
3. **No limiting code (C5).** The apply/import paths **add rows; they never reject a value,
   never throw on an unknown/missing value, and never skip a row.** No `CHECK`, no enum, no
   `NOT NULL` on value columns, no row-dropping filter, no JSONB-key allowlist. Unknown
   values land as text; missing values take a safe default; an unparseable row is upserted
   with a `notes` flag, never dropped (R13). The **publish view is the only gate.**
4. **Deletes ARCHIVE, never hard-delete.** `deleted[]` sets `core.pois.archived_at`
   (or `core.features.archived_at`); the publish view excludes archived rows. Never
   `DELETE FROM core.*`. Never repurpose `is_destination`/`publish_status` to mean "deleted."
5. **Observe, don't narrate (C4).** A slice closes only on a **tile-independent** verifier
   (DOM/cache read, `map.getSource(...).serialize().data` read, or `node -c`/grep) — never on a
   `queryRenderedFeatures`/paint/map-render check.
   > **CORRECTED 2026-06-06 (council Witness andon, slice 2, observed on :8001):** the original
   > parenthetical "external tiles are blocked headless, so `map.on('load')` never fires" is **FALSE**.
   > `map.on('load')` DOES fire headless — the "publish feature(s) loaded" message is set INSIDE that
   > block (`main.js:9937`), and `window.AOP_HOST_MAP` is a global. What tiles block is **paint /
   > `queryRenderedFeatures` / `map.loaded()`**, NOT the `load` event or `addSource`/`addLayer`. So a
   > map-source's loaded data IS readable tile-independently via
   > `window.AOP_HOST_MAP.getSource('<id>').serialize().data.features` (observed: returns the 5 baked
   > buildings, `loaded:false`, 0 console errors). Use `serialize().data.features` — NOT
   > `querySourceFeatures` (it split a feature → 6) and NOT `queryRenderedFeatures` (paint-bound → 3).
   > This correction propagates to the Observable acceptance standard below and slices 3–5. (The
   > slice-1 "what's already built" caveat is accurate as written — it is about
   > `queryRenderedFeatures`/`networkidle` being paint-bound + blocked headless, NOT the `load` event —
   > so it needs no change.)
6. **Record on green** (every slice — see each slice's "Record on green" line). Tick the
   slice's boxes here with the observed artifact named, and append a one-line
   `brain/handoff/session_context.md` entry: which slice closed, what's owed (incl. the bump).
7. **Stay on the farm.** Only the directed slice; dev-time authoring + bake only; no prod
   write-service / auth / moderation (that is northstar V2, deferred).

## Why it kept slipping (named, so we don't repeat it)

The served files have **three writers** with a fragile ordering dep
(`bake_panel_overrides.py`'s docstring warns: run `rebake_canonical.py` after it and the panel
edits are discarded): `rebake_canonical.py` (from `raw/`), `bake_panel_overrides.py` (browser
edits), `export_publish_geojson.sh` (the DB). Three masters → every "go to the DB" attempt
fought the file edits or got abandoned to preserve them. The fix is **one upstream**: the DB.

## The one loop (the target)

```
  AUTHOR (3 doors, all write core)        STORE            BAKE                 SERVE/PROD
  ──────────────────────────────         ──────           ────                 ──────────
  1. web editor → Export → apply ─┐                  export_publish_geojson.sh   static viewer
  2. QGIS / SQL  ─────────────────┼──►  core.*  ──►  reads publish.* views  ──►  reads ONLY the
  3. localStorage = scratch,      │     (PostGIS)     writes website/data/        baked files.
     "commit" via door 1 ─────────┘     ONE truth     *.geojson (CMFS shape)      read-only.
```

One writer to the served files: the bake. Three doors INTO core, ranked: (1) **web editor**
(quick/day-of — the path we preserve); (2) **QGIS / SQL** (heavy authoritative cartography +
the `source_register` stack); (3) **localStorage** (scratch, committed through door 1 — C3).

## What's already built (verified by the council, 2026-06-06)

- **SERVE path runs end-to-end for POIs, with one caveat:** `core.pois` table
  (`mvp/init_db.sql:171`) + `publish.pois` view (`:249`) + `seed_core_pois.sql` +
  `export_publish_geojson.sh` UNION (`:38`) → `website/data/publish.geojson` already holds
  exactly the 2 gated POIs. **Caveat (Witness):** `playwright_verify_baked_pois.py` is **not**
  fully headless — its `rendered_count(['publish-pois'])==2` check (`:95`) uses
  `queryRenderedFeatures` and `wait_until="networkidle"`, which depend on map-load (blocked
  headless). The **DOM/cache** half of that script is observable; the render check is not.
  Slice 1's verifier follows the **`playwright_verify_star_collector.py`** pattern instead
  (no `networkidle`, no `queryRenderedFeatures`; reads `publishDataCache` + the
  `published_destinations` DOM rows) — see `mvp/scripts/playwright_verify_star_collector.py:4-8,40-48`.
- **The edit export exists:** `website/js/panel.js` writes `aop-panel-overrides-v1` diffs
  (`edits[]`/`created[]`/`deleted[]`, keyed `<source>:<canonical id>`; `:84,89,232`);
  `bake_panel_overrides.py` already parses it (it just writes files).
- **The shape contract exists:** CMFS (`website/data/_schema.json` `aop-cmfs-v1` +
  `research/common_feature_schema.md`), guarded by `schema_conformance_audit.md`.
- **`apply_panel_overrides_to_core.py` does NOT exist yet** — slice 1 builds it (by extension, see below).

## Schema decisions (the gold answer to "too many schemas")

**Converge destination layers onto ONE `core.features` table** — CMFS columns
(`id, layer, name, kind, geom, source_id, status, confidence, permission, publish_status, blurb,
is_destination, notes, last_verified`) **+ JSONB `attrs`** for per-domain extras (a trail's
`difficulty`, a cemetery's `burial_count`, a building's `facility_role`). ONE row shape, domain
specifics co-located, the bake becomes one SELECT. **`attrs` is free-form JSONB — no key
allowlist, no jsonschema CHECK; unknown domain keys are stored, never rejected** (mirrors the
existing permissive `jsonb` columns like `core.parcels.metadata`). All value columns open
`text`; the publish view is the only gate (C5).

**Two new columns the author path needs (named here so the user re-confirms them at the commit
pause — the loop does not invent schema):**
- `source_key text UNIQUE` on `core.pois` (and later `core.features`) — the stable external
  identity = the export's `<source>:<canonical id>` string. The apply path upserts
  `ON CONFLICT (source_key)`, so matching is deterministic and idempotent regardless of the serial.
- `archived_at timestamptz` on `core.pois` (and later `core.features`) — soft-delete; the
  publish view gains `AND archived_at IS NULL`.

**Sequencing guard:** prove the AUTHOR loop on the EXISTING `core.pois` first (slice 1), then
converge onto `core.features` as layers come in (slices 2–5), migrating pois into it and
retiring `core.pois` at the explicit Retirement step. Thin slices, each green before the next.

-----

## Observable acceptance standard (read before writing ANY slice verifier)

Every "the bake carries X" / "the edit shows" acceptance uses TWO tile-independent observations,
and NEVER a map-render or closure read:

1. **Baked-file assertion (browserless, strongest):** assert directly on the baked
   `website/data/publish.geojson` — load it in Python/`jq` and confirm the feature / `attrs` /
   edited value is present and archived rows are absent. No browser, no tiles, no map at all.
2. **Viewer-consumes-it assertion (star_collector pattern):** a NEW
   `playwright_verify_baked_<layer>_author.py` that gates on the tile-independent
   "publish feature(s) loaded" message (it is set inside `map.on('load')`, which **does** fire headless
   — see the correction in Loop contract #5). Then read the loaded data **tile-independently** by ONE of:
   - **Destination layers** (POIs and anything that surfaces in the ★ list): the
     `published_destinations` DOM rows (`.poi-list-group[data-group-id="published_destinations"]`).
   - **Reference / map-source layers** (buildings, cemeteries footprints, trail lines — they render as
     MapLibre sources, not ★ rows): `window.AOP_HOST_MAP.getSource('<source-id>').serialize().data.features`
     (observed working: 5 baked buildings, `loaded:false`, 0 errors). This reads the exact feature set the
     viewer fetched and fed to the source — no paint, no tiles.
   **NO** `wait_until="networkidle"`, **NO** `queryRenderedFeatures`/`querySourceFeatures` (paint-bound /
   feature-splitting), **NO** `publishDataCache` (module-local `let` at `main.js:457`, not a global).

**Do NOT reuse the existing render-bound verifiers** for a slice's green-stop —
`playwright_verify_{buildings,cemeteries,visitor_context,trails,sfwda_trace}.py` all use
`wait_until="load"` + `queryRenderedFeatures` (so they never pass headless), and some read the
**pre-bake source file**, not the bake. Model each new author verifier on
`mvp/scripts/playwright_verify_star_collector.py` (the proven headless-safe pattern).

Each `*_author.py` **imports `playwright_base`** and reuses star_collector's `wait_loaded` gate
(the "publish feature(s) loaded" message) — it must **not** re-implement the launch/wait harness
(no second copy of the boot/wait code across the five new verifiers).

-----

## Slice 1 — POI AUTHOR path (prove the whole loop on the proven layer)  · START HERE

Build the missing AUTHOR→STORE link for `core.pois` and prove the round-trip by observation.

**Reuse, don't duplicate (Quartermaster).** Do NOT write a second copy of the payload parser.
First **extract** the parse/validate/normalize contract from `bake_panel_overrides.py` into an
importable module `mvp/scripts/panel_overrides.py` (`read_payload`, `SCHEMA`, `VIEW_STATE_KEYS`,
`EDITABLE_KEYS`, the `<source>:<id>` split, `build_created_feature`, `round_coords`,
`feature_by_id`), refactor `bake_panel_overrides.py` to a thin CLI that imports it, THEN add the
core sink as **`apply_panel_overrides_to_core.py` importing the same module** (or, equivalently, a
`--target core` mode on the one script). One parser, two sinks (file vs DB). The only differing
seam is the sink. **There is no existing baker unit test** — prove the refactor is
behavior-preserving by running `bake_panel_overrides.py` against a fixture export
**before and after** the extraction and diffing the emitted file (byte-identical). That diff IS
the check; do not cite a non-existent "verifier."

**The `--target core` sink MUST NOT inherit the file-baker's silent drops (Mason).** The shared
module keeps file-path behavior, but the core sink replaces the parser's drop branches —
`raise SystemExit` on unknown schema (`bake_panel_overrides.py:82,84`),
`-- skipped; continue` on an unmatched source (`:127,268`), `return None` on a missing id
(`:178`) — with: malformed schema still upserts, an unmatched source upserts under its raw
`source_key`, a missing id gets a generated key — all flagged in `notes`. **Nothing on the core
path drops a row.**

**DDL (slice-1, additive):** add `source_key text UNIQUE` + `archived_at timestamptz` to
`core.pois`; add `AND archived_at IS NULL` to the `publish.pois` view. Update `seed_core_pois.sql`
to set `source_key` on its 3 rows.

**The match rule (Scribe — exact, no guessing). All three branches UPSERT — never a bare
`UPDATE` (Mason):**
- `edits[]`: the export key `<source>:<id>` IS the `source_key`. **Upsert** —
  `INSERT … ON CONFLICT (source_key) DO UPDATE` (apply changed identity/facet props + moved geom;
  never `highlight` — a star is view state, C3). A bare `UPDATE … WHERE source_key` is **banned**:
  if the key matches no row it is a silent zero-row no-op — a lost edit, the SQL twin of the
  parser's `:139` `missing += 1; continue`. So an edit to a not-yet-present key INSERTS the
  feature under its raw `source_key` with a `notes` flag instead of vanishing.
- `created[]`: `INSERT … ON CONFLICT (source_key) DO UPDATE` with `source_key` = the export key,
  editor-seed provenance (a `source_register.sources` row, mirror `seed_core_pois.sql`),
  `is_destination`/`permission`/`publish_status` from the payload or safe defaults. Idempotent:
  re-running the same export upserts, never duplicates.
- `deleted[]`: `UPDATE … SET archived_at = now() WHERE source_key = :key` (never `DELETE`). A
  delete of an absent key is a harmless no-op (nothing to lose) — log it, don't error.
- **Never throw, never skip, never silently no-op (Mason/R13):** an unknown `kind`/`status` lands
  as text; a missing value takes a safe default; an unparseable row is upserted with a `notes`
  flag — never dropped, and `edits[]`/`created[]` never resolve to a zero-row write.

**Run it (slice 1) — literal, from the repo root:**
```bash
# 1. DB up + ready
docker compose -f mvp/docker-compose.yml up -d db
until docker compose -f mvp/docker-compose.yml exec -T db pg_isready -U aop -d aop_map; do sleep 1; done
# 2. (fresh volume only) schema+seed run via initdb; for an existing volume, apply the slice-1 DDL + reseed by hand:
docker compose -f mvp/docker-compose.yml exec -T db psql -U aop -d aop_map < mvp/scripts/seed_core_pois.sql
# 3. apply a panel export into core (the export JSON = the panel "Export edits" download)
python3 mvp/scripts/apply_panel_overrides_to_core.py path/to/aop_panel_overrides.json
# 4. bake core -> served files
bash mvp/scripts/export_publish_geojson.sh
# 5. serve + verify by observation (tile-independent)
python3 -m http.server 8001 --directory website &
python3 mvp/scripts/playwright_verify_baked_pois_author.py   # the new headless-safe verifier (slice 1 writes it)
```

**Observable acceptance (tile-independent — per the Observable acceptance standard above):**
- [x] `panel_overrides.py` extracted; `bake_panel_overrides.py` imports it; the fixture-export diff (pre vs post refactor) is byte-identical (behavior preserved — there is no baker unit test, the diff IS the check). — *observed 2026-06-06: same fixture (`/tmp/aop_fixture_export.json`) baked before vs after the extraction → identical sha256 `8702a446…78301d`.*
- [x] `apply_panel_overrides_to_core.py` upserts `edits[]`/`created[]`/`deleted[]` into `core.pois` `ON CONFLICT (source_key)`; idempotent (re-run = no new rows). — *observed: run 1 then run 2 of the same export → `core.pois` stayed 4 rows, ids `1,2,3,5` unchanged.*
- [x] `deleted[]` sets `archived_at`; `publish.pois` excludes archived; **no `DELETE` statement** in the apply script (grep clean). — *observed: Ellis (`editorPois:ellis-cemetery`) archived → dropped from `publish.pois`/`publish.geojson`; `grep -E "DELETE[[:space:]]+FROM"` on the apply script = 0.*
- [x] Core sink drops nothing: grep the apply path for `raise`/`continue`/`return None` row-drops → none (unknown→text, missing→default, unparseable→`notes` flag). — *observed: `grep -E '\b(raise|continue)\b|return None'` on `apply_panel_overrides_to_core.py` = 0.*
- [x] No silent zero-row writes: `edits[]`/`created[]` UPSERT (`ON CONFLICT (source_key)`), never a bare `UPDATE`; assert matched-or-inserted count == input count (the grep can't see a zero-row UPDATE, so count it). — *observed (live apply, `_applied` temp-table count): edits 1/1, created 1/1 both runs; script gates on `count==input`.*
- [x] **Baked-file assertion:** after apply→bake, `website/data/publish.geojson` carries the applied edit's **new value** (changed `name`/`blurb`) on the right `layer='poi'` feature; an archived row is absent. (Browserless Python check.) — *observed: `poi` id 1 = `"AOP Pavilion (author-test)"` + blurb `AUTHORPATH-OK…`; Ellis (archived) + the non-publishable created POI both absent (gate works).*
- [x] **Viewer assertion:** new `playwright_verify_baked_pois_author.py` (star_collector pattern — gates on the "publish feature(s) loaded" message; no `networkidle`/`queryRenderedFeatures`/`publishDataCache`) shows the edited value in the `published_destinations` DOM rows after reload. **PASS, 0 console errors.** — *observed: `published_destinations` row `pubpoi:1` name+subtitle carry the edited values; Ellis absent; 0 console errors → PASS. Re-witnessed by a fresh council Witness on its own apply→bake→verify run. Verifier hardened with a `--require-author` mode (FAILs if the edit is absent, so it can't silently degrade to baseline-PASS); default no-flag run stays baseline-green for the durable suite.*
- [x] No CHECK/enum/JSONB-allowlist introduced (Mason re-grep); a `source_register.sources` row exists for editor-authored rows. — *observed: `core.pois` constraints = PK + `pois_source_key_key` UNIQUE + FK only (no CHECK); `source_register.sources` id 7 `'AOP web editor (apply)'`.*

**Record on green:** tick the boxes above with the verifier output named; append a
`handoff/session_context.md` line ("slice 1 closed: POI author path; owed: v-bump for any shell
asset touched"). Report the owed version bump; do not perform it.

> **SLICE 1 CLOSED — 2026-06-06.** All eight boxes green by observation (artifacts named inline).
> Files: new `mvp/scripts/{panel_overrides.py, apply_panel_overrides_to_core.py,
> playwright_verify_baked_pois_author.py}`; edited `mvp/scripts/bake_panel_overrides.py` (thin
> importer), `mvp/scripts/seed_core_pois.sql` (+`source_key`), `mvp/init_db.sql`
> (`core.pois` +`source_key UNIQUE`/`archived_at`; `publish.pois` +`archived_at IS NULL`). DB
> (existing volume) carries the same DDL applied by hand + the 3 seed rows keyed.
> **No shell asset touched → NO `sw.js`/`#appVersion` bump owed.** `website/data/publish.geojson`
> restored byte-identical to committed HEAD (production untouched).
> **⚠ Blocking finding for the bake-is-sole-writer goal (NOT slice-1 scope):** re-running
> `export_publish_geojson.sh` **drops** the hand-curated `park_boundaries` feature
> "Ellis Cemetery (inholding parcel)" (served id 5) because it exists ONLY in `publish.geojson`,
> not in `core.park_boundaries`. The DB bake cannot yet be the sole writer for boundaries until
> that polygon is migrated into `core` — fold into the slices that converge `core.features`
> (the same "served-only feature" risk applies to any layer with hand-curated served rows).
> **Residue:** one archived, non-publishable test row remains in `core.pois`
> (id 5 `editorPois:u-authortest-1` "Author Test Overlook") — left archived, not hard-deleted,
> per the no-`DELETE FROM core` rule; a human can purge it if desired.
>
> **Council: FULL CLEAR (full six, 2026-06-06).** Witness pulled one andon (the STATE B viewer
> proof rested on producer narration + the verifier could silently degrade to baseline-PASS);
> resolved by hardening the verifier with `--require-author` and a fresh Witness re-witnessing the
> author round-trip on its own apply→bake→verify run, then confirming production byte-identical to
> HEAD. Warden/Quartermaster/Mason/Scribe cleared first pass. Receipts:
> `../../output/council/gold_migration_slice1_review_20260606.md`.

-----

## Slice 2 — `core.features` + buildings as the first migrated layer

> **AMENDED 2026-06-06 (council design consult, full six; Witness/Quartermaster/Mason andon).** The
> original slice-2 text — its directives summarized here; the verbatim pre-amendment version is in git
> history (commit `bf41eb5`) — said the bake should emit `publish.features` so that **`publish.geojson`**
> carries the 5 buildings, and to teach `apply_panel_overrides_to_core.py` the buildings door. That
> **drifted from the data + the northstar** and is corrected here. WHY
> (all observed): the 5 buildings carry `permission='FEMA public data layer; no warranty; raw
> reference context'` (3 facilities) / `'Private structure … not published as a destination'` (2
> private), `publish_status='facility'`/`'presence_only'`, `_meta.maturity='silver'` — **NONE has
> `permission='publish'`**, so the publish gate (correctly) yields **zero** buildings. Forcing them
> into `publish.geojson` would inject FEMA "no warranty" / "not a destination" data into the publish
> zone — a direct northstar violation (`map_northstar.md`: "every line carries whether it can be
> published"). Buildings are a **reference layer** the viewer already reads from its **own** served
> file (`main.js:8766` → `fetchJson('./data/aop_buildings.geojson')` → `map.addSource('fema-buildings')`).
> The same holds for ALL of slices 3–5 (see the note after slice 5) — see also the corrected
> per-layer note below. The original text was a 4-round council FULL CLEAR; the council that wrote it
> reviewed plan structure, not the per-feature permission values, so the data conflict was missed.

**Corrected plan:**
- Create `core.features` (CMFS columns + JSONB `attrs` + `source_key UNIQUE` + `archived_at` +
  mixed `geometry(Geometry,4326)` like `core.observations`/`core.print_annotations`) +
  `publish.features` view (CMFS gate `permission='publish' AND publish_status='publish' AND
  archived_at IS NULL`, **and it MUST `SELECT attrs` explicitly** — the existing publish views emit
  fixed column lists and would drop `attrs` by omission, Mason). One-time import the 5 curated
  buildings from `website/data/aop_buildings.geojson` → `core.features` with a **reference-tier**
  `source_register.sources` row (license = the FEMA no-warranty string, publish_status non-publish —
  none exists today). Keep each building's **TRUE** permission/publish_status (never coerce to
  'publish'). Store the **full original `properties`** in `attrs` (so nothing is dropped); also
  populate the spine columns for query/gate. Reusable generic importer
  `import_layer_to_core_features.py` (serves slices 3–5 too).
- Extend `export_publish_geojson.sh` (the **one** bake — do not add a parallel script) to ALSO emit
  the **reference served file the viewer already reads** — `website/data/aop_buildings.geojson` —
  from `core.features WHERE layer='buildings' AND archived_at IS NULL`. **No publish gate** on a
  reference layer (the gate is publish-zone-only); the served file keeps its `_meta` wrapper so the
  editor still badges it `silver` (run `stamp_maturity.py` after, per the existing pipeline).
  Reconstruct properties = `attrs` overlaid with the editable spine columns under their original key
  names (so future edits win; with zero edits the output is prop-faithful). Because the bake writes
  the **same filename the viewer already reads**, there is **no `main.js` change → no `sw.js`/
  `#appVersion` bump owed** for slice 2.
- **Quartermaster condition (owed-note, NOT in this slice's diff):** `aop_buildings.geojson` already
  has 3 dormant legacy writers (`import_fema_buildings.py`, the `rebake_canonical.py` CONFIG entry,
  the `export_positioned_features.py` buildings branch). None runs in the day-of loop, so the bake is
  the sole writer **in the loop** — but they must be **retired** so a hand-run can't clobber. The
  `export_positioned_features.py` buildings branch is a working drag-edit path; it can only be retired
  AFTER the buildings apply-door exists (`apply_panel_overrides_to_core.py` `layer='buildings'` with a
  **layer-aware geom builder** — slice-1's `point_geom_sql` NULLs polygons, Mason). Carry the
  apply-door + the 3-writer retirement as the next increment; slice 2 proves the **serve** path.
- **Observable acceptance (per the corrected standard — `map.on('load')` DOES fire headless; tiles
  block only paint/`queryRenderedFeatures`):**
  - [x] **Baked-file assertion (browserless):** the regenerated `website/data/aop_buildings.geojson`
    carries the 5 buildings (`kind='building'`), prop-by-prop equivalent to the committed file
    (modulo provenance), AND a specific `attrs` **value** survives the round-trip (e.g. a facility's
    `facility_role`, an `occupancy_class`) — not just feature count (Mason). — *observed 2026-06-06:
    baked vs `git show HEAD:` → 5/5 features, id sets equal, **PROP+GEOM EQUIVALENCE PASS** (key sets +
    values identical; geom maxdelta < 1e-6 at 9-decimal precision), `1010`'s `facility_role` =
    "Pavilion / G-Central…" survived.*
  - [x] **Viewer assertion:** `playwright_verify_baked_reference_author.py --layer buildings`
    (star_collector pattern; generic across reference layers — generalized in slice 3 from the
    original `playwright_verify_baked_buildings_author.py`) reads
    `window.AOP_HOST_MAP.getSource('fema-buildings').serialize().data.features` and
    asserts the 5 baked buildings + a distinguishing `attrs` value are present, 0 console errors. —
    *observed: baseline PASS (5 buildings + facility_role, 0 errors); `--require-baked` marker
    round-trip PASS — a `_slice2_marker=BAKED-OK` authored into `core.features` then baked appeared in
    the viewer's loaded source on `1010`, proving edit→core→bake→serve→viewer (re-witnessed on the REAL
    verifier output, the standing Witness condition). Marker removed + served files restored to HEAD.*
  - [x] **Gate works:** `publish.features` returns **zero** buildings (they are reference, not
    publish) — `publish.geojson` is unchanged by this slice. (Browserless SQL/file check.) — *observed:
    `SELECT count(*) FROM publish.features WHERE layer='buildings'` = 0; `website/data/publish.geojson`
    restored byte-identical to HEAD (`git status` clean for `website/`).*
- **Record on green** (as slice 1). Re-witness on the REAL verifier output before trusting green
  (standing Witness condition). **Done 2026-06-06** — see the SLICE 2 CLOSED block below.

> **SLICE 2 CLOSED — 2026-06-06.** `core.features` + `publish.features` stood up; the 5 curated
> buildings migrated into `core.features` (true reference permission; full original `properties` in
> `attrs` so nothing dropped; `source_register` row id 9, reference tier); the bake regenerates the
> served `aop_buildings.geojson` from `core.features` (sole writer the viewer reads — same filename, so
> **NO `main.js` change → NO `sw.js`/`#appVersion` bump owed**). All three boxes green by observation
> (artifacts inline). Slice-1 POI verifier unregressed (PASS). Files: new
> `mvp/scripts/{import_layer_to_core_features.py, playwright_verify_baked_reference_author.py}` (the
> verifier was generic from slice 3 on; in slice 2 it shipped as `playwright_verify_baked_buildings_author.py`); edited
> `mvp/init_db.sql` (`core.features` table + `publish.features` view selecting `attrs` + index + trigger),
> `mvp/scripts/export_publish_geojson.sh` (reference-layer bake loop). DB (existing volume) carries the
> same DDL + the 5 building rows + source row 9. Served files restored byte-identical to HEAD (production
> untouched — the user's git gate decides whether to adopt the baked `aop_buildings.geojson`).
> **OWED (Quartermaster, next increment — NOT this slice):** 3 dormant legacy writers of
> `aop_buildings.geojson` (`import_fema_buildings.py`, the `rebake_canonical.py` CONFIG entry, the
> `export_positioned_features.py` buildings branch) must be retired so a hand-run can't clobber; the
> `export_positioned_features.py` branch is a working drag-edit path, so it can only go once the
> buildings apply-door exists (`apply_panel_overrides_to_core.py` `layer='buildings'` + a layer-aware
> geom builder — slice-1's `point_geom_sql` NULLs polygons). None runs in the day-of loop, so the bake
> is the sole writer in the loop today.

-----

## Slices 3–5 — migrate the remaining destination layers (one layer per slice)

Same recipe as slice 2, **one layer per iteration**, each with its own named source file and a
NEW headless-safe author verifier (per the Observable acceptance standard — **not** the existing
render-bound verifier in the last column, which is listed only to show what NOT to reuse):

> **Verifier (slice 3+): ONE generic `playwright_verify_baked_reference_author.py --layer <name>`** —
> add a `LAYERS` config row (source id, expected count, distinct names, a distinguishing `attrs` value),
> NOT a new per-layer file. (Slice 3 generalized the slice-2 buildings verifier into it.)

| Slice | Layer | Source file | Generic verifier invocation | Existing render-bound verifier — do NOT reuse for the green-stop |
|------|-------|-------------|----------------------------------|------------------------------------------------------------------|
| 3 | cemeteries | `website/data/aop_cemeteries.geojson` | `…reference_author.py --layer cemeteries` | `playwright_verify_cemeteries.py` (`wait_until="load"`+`queryRenderedFeatures`) |
| 4 | visitor callouts | `website/data/aop_visitor_context_callouts.geojson` | `…reference_author.py --layer visitor` | `playwright_verify_visitor_context.py` |
| 5 | trails | `website/data/aop_trail_network.geojson` | `…reference_author.py --layer trails` | `playwright_verify_trails.py` / `playwright_verify_sfwda_trace.py` |

> **AMENDED 2026-06-06 (same council consult as slice 2).** Like buildings, **none** of these layers
> pass the publish gate (observed): cemeteries `permission='parcel: public; burial roster: USGenWeb
> non-commercial'` (+ the burial roster is **non-commercial-licensed — it must NEVER enter the publish
> zone**), visitor callouts `'context annotation'`/`'brand owner'`, trail network `'SFWDA paper map —
> permission TBD'` ×120 (`TBD` = non-publishable per the northstar). So each bakes to its **own served
> file** (`aop_cemeteries.geojson`, `aop_visitor_context_callouts.geojson`, `aop_trail_network.geojson`
> — the files the viewer already reads), NOT `publish.geojson`. `publish.features` keeps the gate and
> stays buildings/reference-free.

Per slice: import the current file data → `core.features` (+ a `source_register` row; **full original
`properties` → `attrs`** so nothing drops) → extend `export_publish_geojson.sh` to bake that layer
**from `core.features WHERE layer='<layer>'` to its own served file** (reference layers have no publish
gate; carry the `_meta` wrapper) → green-stop on the TWO standard observations: **(a)** baked-file
assertion (the layer's **own served file** carries its features + a specific `attrs` value, browserless)
and **(b)** the NEW author verifier (star_collector pattern, reading the layer's map source via
`getSource(...).serialize().data.features`, or the ★ rows for destination layers). **Record on green.**
Do NOT fold the `core.pois` retire into these — it is its own step below. The cemetery slice MUST keep
the non-commercial burial roster out of any publish-gated output.

**Green-stop hygiene (Witness, slice 3):** the bake rewrites the served files in place, so the slice's
LAST action MUST restore production to HEAD and ASSERT clean — `git show HEAD:<path> > <path>` for every
served file the bake touched (`publish.geojson` + each reference file) and confirm `git status --short
website/` is empty. The marker round-trip mutates `core.features` + `attrs` — remove the marker too. The
slice is not green until production is byte-identical to HEAD (the user's git gate decides adoption).
**The producer does the authoritative restore AFTER the council** — parallel review seats that re-bake
can leave transient working-tree dirt; judge production state by `git show HEAD:` content, not raw
`git status` mtime, and trust the producer's final restore+assert.

> **⚠ PRODUCTION ADOPTION — two things the user/loop MUST know before adopting any baked output:**
> 1. **`publish.geojson` is NOT yet bake-safe.** A full `export_publish_geojson.sh` regenerates
>    `publish.geojson` from `core`, which **drops the hand-curated `park_boundaries` "Ellis Cemetery
>    (inholding parcel)"** (served id 5) — it lives only in the served file, not in
>    `core.park_boundaries` (the slice-1 finding, now triggered by every bake). Until that polygon is
>    migrated into `core`, `publish.geojson` MUST be restored to HEAD after a bake; do **not** commit the
>    bake's leaner `publish.geojson`. (This is why each slice restores it.) The reference layers
>    (buildings/cemeteries/visitor) have no such gap — their core data is complete.
> 2. **The reference files re-serialize.** The bake emits a **minified** `{type, features, _meta}` that
>    is **semantically equal but byte-different** from the hand-curated HEAD files (different
>    whitespace/key order; the top-level `_source`/`_sources_checked` import-provenance blocks are not
>    re-emitted — per-feature provenance lives in `attrs` + `source_register`). "Restored byte-identical
>    to HEAD" in each slice means the slice LEFT production at HEAD (proven, not adopted); ADOPTING the
>    baked serialization is the user's git-gate choice and will change those files' bytes (not their
>    meaning).

### Slices 3–5 progress

- [x] **Slice 3 — cemeteries.** Done 2026-06-06; council CLEAR. See the SLICE 3 CLOSED block below.
- [x] **Slice 4 — visitor callouts.** Done 2026-06-06; council CLEAR. See the SLICE 4 CLOSED block below.
- [x] **Slice 5 — trails.** Done 2026-06-06; council CLEAR. See the SLICE 5 CLOSED block below.

> **SLICE 3 CLOSED — 2026-06-06.** 8 cemetery features (4 cemeteries × parcel-polygon + marker-point)
> migrated into `core.features` (`layer='cemeteries'`, true reference permission; full original
> `properties` → `attrs` incl. the burial roster fields; `source_register` row id 10, reference tier).
> The cemetery feature keys are NOT unique on `parcel_id` (2 rows share each), so the generic importer
> gained a **composite `--id-field` (`parcel_id,geom_role`)** → 8 distinct `source_key`s. The bake
> regenerates the served `aop_cemeteries.geojson` from `core.features` (added to the `REFERENCE_LAYERS`
> loop). **Verifier consolidated (Quartermaster):** the slice-2 `playwright_verify_baked_buildings_author.py`
> was generalized into ONE `playwright_verify_baked_reference_author.py --layer <buildings|cemeteries>`
> (LAYERS config) so slices 4–5 add config, not copies; the buildings-specific file was retired and its
> slice-2 references updated. **Observed:** baked `aop_cemeteries.geojson` prop+geom equivalent to HEAD
> (8/8, key sets+values identical, geom maxdelta<1e-6), `_meta` `reference` carried; Ellis
> `burial_count=12`/`named_burial_count=9` survived in `attrs`. Viewer: `--layer cemeteries` baseline
> PASS + `--require-baked` marker round-trip PASS (a `_baked_marker` authored into core→baked→appeared on
> Ellis in the viewer's loaded source), 0 console errors. **Roster stays out of publish (the northstar
> condition):** `publish.features WHERE layer='cemeteries'` = 0; the non-commercial roster lives only in
> the reference served file (status quo — the bake is a faithful round-trip, adds/removes nothing) +
> `core.features.attrs`, never the publish zone. Slices 1+2 verifiers unregressed. Served files restored
> byte-identical to HEAD (production untouched). **NO shell asset touched → NO `sw.js`/`#appVersion` bump
> owed.** Files: edited `mvp/scripts/import_layer_to_core_features.py` (composite key),
> `mvp/scripts/export_publish_geojson.sh` (+cemeteries), new
> `mvp/scripts/playwright_verify_baked_reference_author.py` (generic; replaces the buildings-specific one),
> `brain/research/data_maturity_tiers.md` already noted the bake `_meta`-carry. DB carries the 8 rows +
> source row 10. **OWED:** same as slice 2 (legacy-writer retirement is per-layer; cemeteries' served
> file also has the `rebake_canonical.py`/`export_positioned_features.py` writers — dormant, out of the
> day-of loop). The commit is the user's git gate. **NEXT (loop):** slice 4 — visitor callouts.

> **SLICE 4 CLOSED — 2026-06-06.** 4 visitor-context features (2 `visitor_callout` polygons + 2
> `brand_logo` points) migrated into `core.features` (`layer='visitor'`, true reference permission
> 'context annotation'/'brand owner'; full `properties` → `attrs`; `source_register` row id 11). The
> served file's `id` is unique across both kinds, so a single `--id-field id` keyed all 4. The viewer
> splits the ONE served file by `kind` into TWO map sources (`visitor-context` + `brand-logos`), so the
> generic verifier's `LAYERS['visitor'].source` is a **list** — `getSource(...).serialize()` summed
> across both = 4 features (verifier extended to accept multiple sources per layer). **Real bug found +
> fixed (the baked-file assertion earned its keep):** a callout `label` carries embedded newlines; the
> reference bake's `COPY … TO STDOUT` applied TEXT-format backslash escaping, turning the JSON `\n` into
> a literal `\\n` (newline corrupted). Fixed by switching the reference-layer bake from `COPY … TO
> STDOUT` to a plain `SELECT` with `-At` (psql prints the json raw, no escaping). Buildings + cemeteries
> re-verified prop-faithful after the change. **The pre-existing `publish.geojson` `COPY` has the same
> latent risk** — noted in the bake script; no published feature carries a newline today (a finding, not
> slice-4 scope). **Observed:** baked `aop_visitor_context_callouts.geojson` prop+geom equivalent to HEAD
> (4/4, newline preserved), `_meta` `silver` carried; viewer `--layer visitor` baseline PASS +
> `--require-baked` round-trip PASS (marker authored into core→baked→appeared on the AOP-badge logo in
> the viewer's loaded source), 0 console errors; `publish.features WHERE layer='visitor'` = 0; slices
> 1–3 unregressed. Served files restored byte-identical to HEAD. **NO shell asset touched → NO bump
> owed.** Files: edited `mvp/scripts/export_publish_geojson.sh` (+visitor; `COPY`→`SELECT` newline fix),
> `mvp/scripts/playwright_verify_baked_reference_author.py` (multi-source `visitor` config). DB carries
> 4 rows + source row 11. **OWED:** per-layer legacy-writer retirement (same as slice 2/3). The commit
> is the user's git gate. **NEXT (loop):** slice 5 — trails (120 features, `permission TBD`).

> **SLICE 5 CLOSED — 2026-06-06.** All 120 trail-network LineStrings migrated into `core.features`
> (`layer='trails'`, true reference permission `'SFWDA paper map — permission TBD'`; full `properties` →
> `attrs` incl. each trail's load-bearing `color`/`difficulty`/`trail_number`; `source_register` row id
> 12). Unique `id` (`sfwda-N`) → single `--id-field id`, 120 distinct keys. The bake regenerates the
> served `aop_trail_network.geojson` from `core.features` (added to `REFERENCE_LAYERS`), carrying the
> rich **gold** `_meta` (the `about`/`color_legend`/`difficulty_band` block) forward. **Observed:** baked
> file prop+geom equivalent to HEAD (**120/120**, key sets+values identical, **max geom delta 0**),
> `_meta` gold + `about` carried; viewer `--layer trails` baseline PASS (`getSource('aop-trail-network')
> .serialize()` = 120, all trail names present, `sfwda-0` `color='#1f9d3a'` survived) + `--require-baked`
> round-trip PASS (marker authored into core→baked→appeared on trail '15' in the viewer's loaded source),
> 0 console errors; `publish.features WHERE layer='trails'` = 0; slices 1–4 unregressed. Served files
> restored byte-identical to HEAD (authoritative producer restore after the council; see the PRODUCTION
> ADOPTION warning). **NO shell asset touched → NO bump owed.** Files: edited
> `mvp/scripts/export_publish_geojson.sh` (+trails), `mvp/scripts/playwright_verify_baked_reference_author.py`
> (trails config). DB carries 120 rows + source row 12. `core.features` now holds all four reference
> layers (buildings 5 + cemeteries 8 + visitor 4 + trails 120 = 137). **OWED:** per-layer legacy-writer
> retirement (same as slices 2–4). The commit is the user's git gate. **NEXT (loop):** the Retirement
> step — collapse `core.pois` into `core.features`, then STOP (slice 6 HELD).

-----

## Retirement step (after slice 5 is green — the loop's LAST action, then STOP)

Collapse `core.pois` into `core.features` and prove it, so the transitional two-table duplicate
(Quartermaster) does not linger:
- Migrate the `core.pois` rows into `core.features` (`layer='poi'`), preserving `source_key`.
- Drop `publish.pois` from `export_publish_geojson.sh`'s UNION; POIs now bake from `publish.features`.
- **Observable acceptance:** a verifier asserts (a) **zero `core.pois` rows are unmirrored in
  `core.features`**, (b) `publish.pois` no longer appears in `export_publish_geojson.sh`, (c) the
  slice-1 author verifier passes **reading POIs from `publish.features`**. PASS.
- **Record on green**, then **STOP** — slice 6 is held for a human.

> **RETIREMENT CLOSED — 2026-06-06.** `core.pois` collapsed into `core.features` (`layer='poi'`).
> **Critical correctness point handled:** dropping `publish.pois` from the bake while leaving the apply
> path writing `core.pois` would have BROKEN the POI edit path (edits landing where the bake no longer
> reads). So the collapse also **rewired the apply path + the seed** to `core.features`, not just the
> bake. **Shipped:** (1) mirrored the 4 `core.pois` rows → `core.features` (`layer='poi'`, ON CONFLICT
> (source_key), **no DELETE** per loop contract #4 — the `core.pois` rows STAY, deprecated); (2) rewired
> `apply_panel_overrides_to_core.py` to upsert `core.features` (`layer='poi'`; delete scoped `AND
> layer='poi'`); (3) `export_publish_geojson.sh` POI arm `FROM publish.pois` → `FROM publish.features
> WHERE layer='poi'`; (4) rewrote `seed_core_pois.sql` to seed `core.features` via `ON CONFLICT` (no
> `DELETE FROM core`, fresh-volume reproducible); (5) deprecation comments on `core.pois` + `publish.pois`
> in `init_db.sql` (kept, not dropped — a DROP is a destructive op left to the user).
> **Observable acceptance — all green:** (a) **zero `core.pois` rows unmirrored** in `core.features`
> (observed: `count = 0`); (b) `publish.pois` **no longer in** `export_publish_geojson.sh` (grep: only
> `publish.features WHERE layer='poi'`); (c) the slice-1 author verifier **PASS reading POIs from
> `publish.features`** — baseline PASS AND `--require-author` PASS (an edit to Pavilion + a delete of
> Ellis applied via the rewired apply → bake → the viewer's `published_destinations` showed the edited
> name+blurb as `pubpoi:139` [the core.features serial, proving the new source] and Ellis absent, 0
> console errors). Then core POIs re-migrated to faithful state + served files restored byte-identical to
> HEAD. **NO shell asset touched → NO bump owed.** `core.features` now holds **141 features** (buildings
> 5 + cemeteries 8 + visitor 4 + trails 120 + poi 4). **OWED (human, NOT the loop):** ~~DROP the deprecated
> `core.pois` table + `publish.pois` view once confirmed unused (destructive — the user's call)~~ → **DONE
> 2026-06-07** (drop-tested, then dropped from the DB + `init_db.sql`; see the DROP COMPLETE block below);
> retire the dormant per-layer legacy writers (slices 2–5 OWED). **The loop STOPS here — slice 6 is HELD.**

> **DEPRECATED POI OBJECTS DROPPED — 2026-06-07 (human pulled the retirement's OWED item; DB +
> `mvp/init_db.sql`, UNCOMMITTED, NO bump owed; verified by observation throughout).** The user pulled the
> one destructive item the loop held back. Proven safe FIRST, then dropped, then re-proven for fresh volumes:
> - **Drop-safety (observed before touching anything):** every `core.pois` row mirrored into `core.features`
>   (`unmirrored = 0`); served-set parity identical (old `publish.pois` gate = **2**, new `publish.features
>   WHERE layer='poi'` gate = **2**, symmetric diff **0**); **no FK** points at `core.pois`; only `publish.pois`
>   depended on it (no other view). **One latent gate delta logged:** `publish.features` dropped the
>   `is_destination = true` clause that `publish.pois` carried — **0 rows differ today** (all 4 POIs are
>   destinations), but a future `is_destination=false` *published* POI would serve under the new gate where the
>   old one excluded it. Not a blocker; recorded so it isn't a surprise.
> - **Rename-and-reverify drop test (reversible proof nothing reads them by name):** `ALTER ... RENAME` both
>   objects out of the way → ran the bake (exit 0, **no** missing-object error) → `publish.geojson` still
>   carried both POIs (browserless assert) → `playwright_verify_baked_pois_author.py` **PASS, 0 console
>   errors**, viewer rendered `pubpoi:139/140` (the `core.features` serials — proves the serve reads
>   `core.features`, not `core.pois`). Served files then restored **byte-identical to HEAD**.
> - **The drop:** `DROP VIEW publish.pois; DROP TABLE core.pois;` on the live volume (the renamed objects);
>   `core.features` intact (141 rows, 4 poi). `mvp/init_db.sql` edited to remove the `core.pois` table, the
>   `publish.pois` view, the `pois_geom_gix` index, the trigger-loop array entry, and the now-stale
>   `core.features` comment. **Fresh-volume reproducibility proven:** ran the edited `init_db.sql` against a
>   throwaway DB → exit 0, `core.pois`/`publish.pois` absent, `core.features`/`publish.features` present.
> **NO shell asset touched (only `mvp/init_db.sql`) → NO `sw.js`/`#appVersion` bump owed.**
> **Cosmetic doc-debt left (historical comments only, not in any code path):** provenance comments in
> `website/js/main.js:1219,9536`, `website/data/aop_poi_index.json`, and the verifier/seed docstrings still
> name `core.pois → publish.pois` as the POI origin — accurate as *history*, harmless, deliberately not
> edited to avoid forcing a shell-asset version bump for a comment. **OWED (still human):** retire the
> dormant per-layer legacy writers (slices 2–5). **The commit is the user's git gate.**

-----

## Slice 6 — HELD (out of loop scope until a human pulls it)

**Do not execute in the loop.** Reframed per the council: most of the C2 collapse already
shipped in Sprint 05 (one `collectStarredDestinations` at `main.js:1152`, zero `pushRow(`,
`buildPoiGroups` is already a thin renderer) — **do not re-open `buildPoiGroups`**. The real
remaining work is **C3**: demote the parallel `aop-*-v*` localStorage stores to working-buffers
now that `core` is the store of record. When a human pulls this, it must come back **bounded**:
each named store to demote as its own `- [ ]` line, with an observable close = the C1/C2/C6
enforcement greps still at target (`editor_architecture_contracts.md` enforcement commands) **and**
the full `playwright_verify_*` suite green. Until then: out of scope.

## Guardrails (every slice) — see the Loop contract up top; in brief

- **No prod write-service / auth / moderation** (northstar V2, deferred). Dev-time bake + deploy only.
- **No limiting code (C5/Mason):** add rows, never reject/throw/skip/validate; deletes archive.
- **Provenance travels (source_register):** every authored/imported row carries its source stack; the publish view is the permission+confidence gate.
- **Shape is audited (Witness):** `schema_conformance_audit.md` proves each baked output conforms to CMFS.
- **Observable acceptance (C4):** each slice closes only on a tile-independent verifier PASS — never a map-render check.
- **Git gate is the user's:** the loop never commits, never bumps `sw.js`/`#appVersion`; it reports the owed bump.

## Council sign-off — FULL CLEAR (2026-06-06, 4 rounds)

Direction set by the user. **Reviewed, hardened, and CLEARED by the full council** over four
rounds — every seat ran fresh + adversarial. Round 1: all six pulled andon. The plan was rewritten
and tightened until every seat cleared (Warden + Scribe R2; Quartermaster + Witness R3; Mason R4;
Steward chairs). Receipts + the round-by-round record: `../../output/council/gold_migration_review_20260606.md`.
Shape vetted by the earlier schema consult (`../10_deferred/star_driven_poi_list.md`).

**Two standing conditions the executing loop inherits (from the seats' NEXTs):**
- **Witness:** the apply script + the five `playwright_verify_baked_*_author.py` do not exist yet
  — the loop writes them to the star_collector pattern. **Re-witness on the FIRST slice's real
  verifier output before trusting any "green"** ("the script printed PASS" ≠ observation).
- **Mason:** confirm the `count == input` (no silent zero-row write) acceptance actually executes
  against a live apply before slice-1 green.
