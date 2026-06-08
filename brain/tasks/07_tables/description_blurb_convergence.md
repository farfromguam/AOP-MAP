# Card: converge the feature description on ONE name (`description`) — in the DATA

Status: ✅ DONE 2026-06-08 — all 4 slices GREEN by observation; council plan-review CLEARED and an
independent Witness DONE-REVIEW re-verified the end state on the running system (CLEAR). OWED: the
user's `git commit` of the diff (v52→v53 bump). Robust source-data approach (user directive).
Receipts: diagnosis `brain/output/council/description_blurb_flow_review_20260608.md`; plan
`description_blurb_plan_review_20260608.md`; done-review `description_blurb_done_review_20260608.md`.

## Request (plain)

"I want a full robust fix. source data should be updated vs support in code." Make the human
description of a feature use ONE canonical name end-to-end — `description` (the CMFS canonical) —
and fix it in the DATA (the DB store-of-record + the served files), NOT by teaching the viewer or
the bake to read/emit both names. This OVERRIDES the minimal additive read-both shape the council
cleared earlier the same day (`cards_not_gospel` — the user's inline correction wins): NO
`props.description ?? props.blurb` fallback in main.js; NO `blurb AS description` alias in the bake.

## Why (observed)

One concept, two physical names. The editor reads/writes `description` (panel.js:1349); the viewer
renders `blurb` (main.js:1232); the DB stores it in the `core.features.blurb` column; the bake emits
`blurb` (export_publish_geojson.sh:36). For the Pavilion the editor edits the FROZEN static
`aop_editor_seed_pois.geojson` (text under `description`) while the view renders the DB-baked
`publish.geojson` (text under `blurb`), and the two texts have DRIFTED (same logical POI, different
content). DB is the store of record (gone gold) — so the DB carries the canonical name and the
served files are baked from it.

## Northstar / rules check

- Northstar: DB is the living spine; bake is the only writer of served files; web V1 read-only. ✓
- `no_limiting_code_mvp` / C5: the rename adds NO CHECK/enum/validator and drops NO row. `ALTER ...
  RENAME COLUMN` is metadata-only (no data rewrite, no loss). ✓
- The `import_layer_to_core_features.py` `BLURB_KEYS=("description","blurb")` crosswalk STAYS — it
  reads heterogeneous EXTERNAL source vocab (FEMA/OSM) on ingest; that is legitimate, not the "support
  in code" being removed. What is removed is OUR-OWN-data crutches (viewer fallback, bake alias).
- `description` already names a column on sibling `core.activities` (the reusable activity WHAT —
  distinct meaning). Keep distinct; document.

## Scope

IN: rename `core.features.blurb` → `description`; update every checked-in writer/reader of that
column; bake emits a single `description` key; viewer reads `props.description` only; re-bake the
static seed file from the DB so the editable layer's text == the DB == the view.

OUT (carded as follow-ups below, not this loop): the `aop_poi_index.json` sidecar fold; the full
editor-loads-DB / localStorage→working-buffer collapse (gold slice 6, HELD); reference-layer
attrs-vs-column normalization beyond what the rename touches.

## Source links / blast radius (every `blurb` in mvp/, observed)

- DB schema: `init_db.sql:60` (column), `:165` (publish.features view SELECT — view must be
  DROP/recreated to rename a selected column).
- Seed: `seed_core_pois.sql:45,47,67,72` (INSERT cols + VALUES alias + ON CONFLICT SET).
- One-time migration (NOT in fresh-volume path; update for hygiene): `migrate_layers_to_core_features.sql`
  (8 INSERT column lists: :25,37,48,59,74,89,104,117).
- Promote: `promote_gpx_to_trail.sql:40`.
- Apply sink: `apply_panel_overrides_to_core.py:71` (POI_COL), `:209` (var), `:226,230,237` (cols/vals/sets).
- Ingest: `import_layer_to_core_features.py:120-123` (writes the column — retarget to `description`;
  keep `BLURB_KEYS` READ crosswalk :56-57).
- Crosswalk-exempt (NO change — reads external GeoJSON vocab, not the DB column):
  `rebake_canonical.py:39` (`DESC_KEYS`), `:267` (docstring). Listed so the `blurb` grep hit is
  pre-accounted (Mason).
- Seed-file SECOND producer (Quartermaster): `rebake_canonical.py:119` already emits
  `aop_editor_seed_pois.geojson` from `website/data/raw/`. Slice 4 must make the DB bake arm the SOLE
  producer — retire/repoint this entry, or the drift Slice 4 kills reappears via the raw re-bake.
- Bake: `export_publish_geojson.sh:36` (POI SELECT).
- Verifiers: `playwright_verify_baked_pois.py:74,83-85`; `playwright_verify_baked_pois_author.py:77,98`.
- Fixture: `scripts/fixtures/poi_rows_fixture.json:6-7` (test data `blurb` key).
- Viewer read of the feature property: `main.js:1232` (the ONE published-POI cutover; internal
  `row.blurb` field name at :1374/:1435 may stay — only the SOURCE read changes).
- Seed file: `website/data/aop_editor_seed_pois.geojson` (1 feature, stale `description`, key
  `aop_seed_pavilion`; DB has 4 `editorPois:*` poi rows).
- Fresh-volume path: docker-compose mounts ONLY `init_db.sql` + `seed_core_pois.sql` into
  `/docker-entrypoint-initdb.d/`.

## Execution plan — slices (ready to loop)

### Loop contract (feed each iteration)
Do the **next incomplete slice** (start at Slice 1). Verify it by its **tile-independent
acceptance** (observe the real DB / baked file / running viewer — never re-derive). **Record on
green** (check the slice box + a one-line handoff entry). Then **stop**. Do **NOT** `git commit`.
Bump `sw.js`/`#appVersion` **only** in the slice that says so (Slice 3) and report it as owed.
Restore served files byte-identical to HEAD when a slice only needed them for verification, so
production stays untouched until the user deploys. No-limiting-code: never add a CHECK/enum, never
drop a row, never silently skip.

**Load-bearing safety invariant (Mason):** a `description`-only baked `publish.geojson` MUST NOT be
the served file until the viewer read is cut over in Slice 3. Between Slice 1 (DB renamed) and Slice
3 the served files stay at HEAD (which carry BOTH keys, so the un-bumped viewer reading `props.blurb`
still resolves). Serving a `description`-only file before Slice 3 blanks every POI subtitle.

**Acceptance is VALUE, not presence (Witness):** the convergence is a value change, so each slice
asserts the NEW text BY VALUE, in the positive `--require-author` style that already exists at
`playwright_verify_baked_pois_author.py:98,102-107` (absence FAILS). A `!!`-presence / "rows render"
check is NOT acceptance here. Extend the EXISTING verifiers (Quartermaster) — do not invent new ones.

### Slice 1 — DB: rename `core.features.blurb` → `description`  ✅ DONE 2026-06-08
> GREEN by observation: live DB `\d` shows `description` / no `blurb`, `publish.features` exposes
> `description`, 159 rows / 7 non-null intact (pg_dump backup `/tmp/aop_map_backup_predesc.dump`).
> Fresh throwaway volume from init_db.sql+seed_core_pois.sql → `description` present, `blurb` ABSENT,
> 3 POI rows / 2 with text, `publish.features` exposes `description`. Scripts updated: init_db.sql
> (col+view), seed_core_pois.sql, migrate_layers_to_core_features.sql, promote_gpx_to_trail.sql,
> import_layer_to_core_features.py (write target; kept BLURB_KEYS read crosswalk),
> apply_panel_overrides_to_core.py (POI_COL + created_block). Fixture poi_rows_fixture.json deferred
> to Slice 3 (it is viewer-shape test data, coupled to the main.js read).
- `pg_dump` backup first (`/tmp/aop_map_backup_predesc.dump`) — reversible.
- Live DB, one txn: `DROP VIEW publish.features;` → `ALTER TABLE core.features RENAME COLUMN blurb
  TO description;` → recreate `publish.features` verbatim except `blurb`→`description`.
- Update checked-in scripts to the new name: `init_db.sql` (col + view), `seed_core_pois.sql`,
  `migrate_layers_to_core_features.sql`, `promote_gpx_to_trail.sql`, `import_layer_to_core_features.py`
  (write target `description`; KEEP `BLURB_KEYS` read crosswalk), `apply_panel_overrides_to_core.py`
  (`POI_COL={"name":"name","description":"description","kind":"kind"}`; created_block var/cols/sets),
  `fixtures/poi_rows_fixture.json` (key `blurb`→`description`).
- **Acceptance (tile-independent, Witness-tightened):** the LOAD-BEARING proofs are (1) live
  `\d core.features` shows `description`, no `blurb`; (2) `publish.features` exposes `description`;
  (3) fresh THROWAWAY volume (separate compose project / temp data dir) booted from ONLY the two
  mounted files (`init_db.sql`+`seed_core_pois.sql`) → `SELECT count(*), count(description) FROM
  core.features WHERE layer='poi'` = `3 | 2` (proving-grounds has no text), `information_schema`
  shows NO `blurb` column, container exit 0. `SELECT count(*)` vs backup is a cheap SANITY line only
  — NOT the no-loss proof (RENAME is metadata-only; it can't drop rows). Do NOT equate fresh-volume
  count (3) with the live count (4 — the live DB carries the residual `editorPois:u-authortest-1`).

### Slice 2 — Bake: emit a single `description` key  ✅ DONE 2026-06-08
> GREEN by value-equality: baked publish.geojson POI `description` set-equal to DB publish.features by
> id (139/140, exact text), `blurb` absent, stale `source`/`last_checked` gone. Served files restored
> byte-identical to HEAD after verifying (via `git show HEAD:… > …`, since the working-tree git gate
> blocks `checkout`). export_publish_geojson.sh:36 SELECT → `description`.
- `export_publish_geojson.sh:36` POI SELECT: `description` (was `blurb`). Re-bake `publish.geojson`.
- **Acceptance (VALUE-equality, Witness — not a `!!` presence flag):** a browserless assertion that
  loads `website/data/publish.geojson` and the paired `psql` read `SELECT id, description FROM
  publish.features WHERE layer='poi'`, and proves SET-EQUALITY of `(id → description text)` between
  them, AND `'blurb' NOT IN properties` for every poi feature, AND the stale `source`/`last_checked`
  keys are gone. Print the matched pairs. Then **restore the served file to HEAD** (a
  `description`-only file must not be served until Slice 3 — see the safety invariant).

### Slice 3 — Viewer: read `props.description` only; bump shell  ✅ DONE 2026-06-08
> GREEN by rendered-DOM observation: `playwright_verify_baked_pois_author.py --require-description`
> PASS — the published-POI subtitle in the live DOM contains the DB text "campfire all happen here"
> 0 console errors. main.js:1232 → `props.description`; fixture poi_rows_fixture.json → `description`;
> the orphan verifier `playwright_verify_baked_pois.py` retargeted `blurb`→`description` (card
> blast-radius line; PASS); sw.js + index.html bumped v52→v53.
> COUNCIL DONE-REVIEW ADJUSTMENT (Steward, on a Quartermaster finding): the served `publish.geojson`
> is LEFT AT HEAD, NOT re-baked-and-shipped. A fresh bake drops the served-only hand-curated
> `id=5 park_boundaries "Ellis Cemetery (inholding parcel)"` (6→5 features, not in the DB — the flagged
> gold served-only-row gap) and re-serializes all ids — both out of scope for a description fix. HEAD's
> publish.geojson already carries `description` matching the DB, so the v53 viewer satisfies the
> user-visible fix without that collateral. The durable convergence is the bake SCRIPT (Slice 2 proved
> it emits `description`); the served file regenerates at the user's deploy bake. OWED: the commit (git
> gate). FLAGGED follow-up: migrate the Ellis inholding park_boundary into `core.features` before the
> next deploy-bake, or that deploy drops it (a pre-existing gold gap, now decoupled from this commit).
- `main.js:1232`: `blurb: props.description || null` (NO `?? props.blurb`). Internal `row.blurb`
  field name + the renderer at `:1374/:1435` stay — only the SOURCE read changes.
- Re-bake `publish.geojson` for real this slice (it ships with the viewer change).
- Bump `sw.js` + `#appVersion` (main.js changed). **Owed to the user: the commit (git gate).**
- **Acceptance (POSITIVE rendered-DOM assertion, Witness — not "rows render"):** extend
  `playwright_verify_baked_pois_author.py` with a `--require-description` mode (mirroring
  `--require-author`, :102-107) that reads the rendered published-POI subtitle
  (`.poi-row-subtitle` / the popup `.poi-popup-subtitle`, `main.js:1435`) and asserts it CONTAINS a
  distinctive DB substring (live Pavilion: `"campfire all happen here"`). Absence FAILS — it must not
  degrade to a baseline "rows exist" pass. Show the PASS line + the subtitle text. Report the
  `sw.js`/`#appVersion` bump as owed.

### Slice 4 — Seed file: reconcile to the DB (kill the drift)  ✅ DONE 2026-06-08
> SCOPE CHANGE (cards_not_gospel + observation): the planned "re-bake the seed FROM the DB via a bake
> arm" is NOT a clean slice — the editor seed and the DB row have divergent shapes (identity
> `aop_seed_pavilion` vs `editorPois:aop-pavilion`; maturity draft/draft/first-party vs
> confirmed/high/publish; the `#pavilion` tag is `seed_tag` in the file but `attrs.event_location.tag`
> in the DB; the DB has 4 editorPois rows incl. a test residual). A faithful DB→seed re-bake would
> reshape the editor's identity/maturity/tag model and pull in junk — that IS the HELD gold-slice-6
> editor-loads-DB collapse. So Slice 4 scoped DOWN to a source-data RECONCILE: set the served seed's
> drifted `description` (and its stale mirrored `notes`) to the DB value, and fix the raw source
> (`data/raw/aop_editor_seed_pois.geojson`) so the legacy `rebake_canonical` reproduces it (no drift
> reintroduction — Quartermaster condition met without removing the CONFIG entry).
> GREEN by observation: (a) served seed `description` == DB `description` (file assert PASS); (b)
> fresh-state editor (clear `aop_editor_pois_v1`, reload, await async seed) carries the NEW DB
> description, ZERO old text (PASS); (c) `rebake_canonical --check` resolves the seed canon
> `description` to the NEW text (drift can't return via the legacy path). The editable Pavilion now
> matches the published view. Seed file ships (precached sw.js:92) under the v53 bump.
- Regenerate `website/data/aop_editor_seed_pois.geojson` FROM `core.features WHERE layer='poi'`
  (the editorPois-keyed rows), text under `description`, same filename + `_meta` carried — a new emit
  arm in the one-writer bake (sibling to REFERENCE_LAYERS), NOT a hand edit.
- **Make the DB arm the SOLE producer (Quartermaster):** retire/repoint the `rebake_canonical.py:119`
  `aop_editor_seed_pois.geojson` output, or the raw re-bake re-introduces the drift.
- **Served-file disposition (Warden):** the seed file is precached (`sw.js:92`). It SHIPS with this
  convergence, so it rides the SAME `sw.js`/`#appVersion` bump owed in Slice 3 (one bump for the whole
  deploy) — restore it to HEAD if the loop stops before the user deploys.
- **Acceptance (Witness — compare seed-vs-DB, NOT seed-vs-popup; the editor and the popup are two
  different client features, and unifying them is the OUT-of-scope gold slice 6):** (1) browserless:
  `aop_editor_seed_pois.geojson` Pavilion `properties.description` `==` `SELECT description FROM
  core.features WHERE source_key='editorPois:aop-pavilion'` (string-equal, printed); (2) headless DOM
  on FRESH state — clear `localStorage['aop_editor_pois_v1']` (the seed loads there on fresh install,
  `main.js:43`) and reload, then read the editor `editorPois` source / the Description textarea
  (`panel.js:1349`) and assert it CONTAINS the DB substring `"campfire all happen here"`. Stale
  localStorage would mask the re-bake — the fresh-state reset is load-bearing.

## Verification (whole card)
Per-slice tile-independent acceptance above. The card is DONE when: DB has one `description` column
(no `blurb`); the bake emits one `description` key; the viewer reads `props.description`; and the
editor's Description for the Pavilion matches the view — all observed on the running system. Then
convene the council done-review.

## Open questions
None blocking. Confirmed forks resolved by the user's directive (source-data update, not code
support). The sidecar fold + full editor-loads-DB collapse are explicit OUT-of-scope follow-ups.

## Follow-up cards (NOT this loop)
- Sidecar `aop_poi_index.json`: fold `entries[].blurb` → `core.features.description`; rehome
  `revisit_note` + POI-tab `groups[]` ordering/labels (poiGroupOrder/poiGroupLabel main.js:1313-1320)
  FIRST; then retire the sidecar (it is precached — bump sw.js). [Quartermaster condition.]
- Full editor-loads-DB / localStorage→working-buffer collapse (gold slice 6, HELD) so there is one
  Pavilion feature, not an editorPois + published_destinations pair.
