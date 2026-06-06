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
   (DOM/cache read or `node -c`/grep) — never on a `queryRenderedFeatures`/map-render check
   (external tiles are blocked headless, so `map.on('load')` never fires).
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
   "publish feature(s) loaded" message (it fires independently of `map.on('load')`) and reads the
   `published_destinations` DOM rows (`.poi-list-group[data-group-id="published_destinations"]`).
   **NO** `wait_until="networkidle"`, **NO** `queryRenderedFeatures`, **NO** `publishDataCache`
   (it is a module-local `let` at `main.js:457`, not a global — `page.evaluate` cannot reach it).

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
- [ ] `panel_overrides.py` extracted; `bake_panel_overrides.py` imports it; the fixture-export diff (pre vs post refactor) is byte-identical (behavior preserved — there is no baker unit test, the diff IS the check).
- [ ] `apply_panel_overrides_to_core.py` upserts `edits[]`/`created[]`/`deleted[]` into `core.pois` `ON CONFLICT (source_key)`; idempotent (re-run = no new rows).
- [ ] `deleted[]` sets `archived_at`; `publish.pois` excludes archived; **no `DELETE` statement** in the apply script (grep clean).
- [ ] Core sink drops nothing: grep the apply path for `raise`/`continue`/`return None` row-drops → none (unknown→text, missing→default, unparseable→`notes` flag).
- [ ] No silent zero-row writes: `edits[]`/`created[]` UPSERT (`ON CONFLICT (source_key)`), never a bare `UPDATE`; assert matched-or-inserted count == input count (the grep can't see a zero-row UPDATE, so count it).
- [ ] **Baked-file assertion:** after apply→bake, `website/data/publish.geojson` carries the applied edit's **new value** (changed `name`/`blurb`) on the right `layer='poi'` feature; an archived row is absent. (Browserless Python check.)
- [ ] **Viewer assertion:** new `playwright_verify_baked_pois_author.py` (star_collector pattern — gates on the "publish feature(s) loaded" message; no `networkidle`/`queryRenderedFeatures`/`publishDataCache`) shows the edited value in the `published_destinations` DOM rows after reload. **PASS, 0 console errors.**
- [ ] No CHECK/enum/JSONB-allowlist introduced (Mason re-grep); a `source_register.sources` row exists for editor-authored rows.

**Record on green:** tick the boxes above with the verifier output named; append a
`handoff/session_context.md` line ("slice 1 closed: POI author path; owed: v-bump for any shell
asset touched"). Report the owed version bump; do not perform it.

-----

## Slice 2 — `core.features` + buildings as the first migrated layer

- Create `core.features` (CMFS columns + JSONB `attrs` + `source_key UNIQUE` + `archived_at`) +
  `publish.features` view (CMFS gate `permission='publish' AND publish_status='publish' AND
  archived_at IS NULL`). One-time import the 5 curated buildings from
  `website/data/aop_buildings.geojson` → `core.features` with `source_register` rows; per-domain
  keys (`facility_role`, `build_id`, …) go into `attrs`.
- Extend `export_publish_geojson.sh` (the one bake — do not add a parallel bake) to emit
  `publish.features`; the viewer reads the baked output for buildings; teach
  `apply_panel_overrides_to_core.py` the buildings door (same module, `layer='buildings'`).
- **Observable acceptance (per the standard — buildings register at map-load, so a render check
  CANNOT pass headless; the existing `playwright_verify_buildings.py` reads the pre-bake source
  file, so it does NOT prove the bake):**
  - [ ] **Baked-file assertion:** `website/data/publish.geojson` carries the 5 curated buildings under `layer='buildings'` with their `attrs` (`facility_role`, `build_id`, …). (Browserless.)
  - [ ] **Viewer assertion:** NEW `playwright_verify_baked_buildings_author.py` (star_collector pattern) confirms the viewer renders the baked buildings via the tile-independent surface. PASS, 0 console errors.
- **Record on green** (as slice 1).

-----

## Slices 3–5 — migrate the remaining destination layers (one layer per slice)

Same recipe as slice 2, **one layer per iteration**, each with its own named source file and a
NEW headless-safe author verifier (per the Observable acceptance standard — **not** the existing
render-bound verifier in the last column, which is listed only to show what NOT to reuse):

| Slice | Layer | Source file | NEW author verifier (write this) | Existing render-bound verifier — do NOT reuse for the green-stop |
|------|-------|-------------|----------------------------------|------------------------------------------------------------------|
| 3 | cemeteries | `website/data/aop_cemeteries.geojson` | `playwright_verify_baked_cemeteries_author.py` | `playwright_verify_cemeteries.py` (`wait_until="load"`+`queryRenderedFeatures`) |
| 4 | visitor callouts | `website/data/aop_visitor_context_callouts.geojson` | `playwright_verify_baked_visitor_author.py` | `playwright_verify_visitor_context.py` |
| 5 | trails | `website/data/aop_trail_network.geojson` | `playwright_verify_baked_trails_author.py` | `playwright_verify_trails.py` / `playwright_verify_sfwda_trace.py` |

Per slice: import the current file data → `core.features` (+ `source_register` rows; domain
keys → `attrs`) → extend `export_publish_geojson.sh` to bake that layer from `publish.features` →
green-stop on the TWO standard observations: **(a)** baked-file assertion (`publish.geojson`
carries the layer's features + `attrs`, browserless) and **(b)** the NEW author verifier
(star_collector pattern). **Record on green.** Do NOT fold the `core.pois` retire into these — it
is its own step below.

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
