# Spike-code audit — the move to DB-first

Date: 2026-06-08
Trigger: user — *"there is so much spike code in the app. We are moving to a db first and need to
begin cleaning up these edge cases. review audit. do all the things. convene the council."*
Mode: BRAIN ONLY, read-only audit (no `website/`/`mvp/` change), UNCOMMITTED. Grounded in observation
(live code read, live served files, `init_db.sql`/compose mounts, the apply scripts). Four read-only
Explore sweeps + my own verification of every load-bearing claim.

-----

## What "db-first" means here (so we audit the right thing)

The codification already exists — it's the editor contracts ([[editor_architecture_contracts]],
`northstar/editor_architecture_contracts.md`, locked 2026-06-06) plus the **HELD gold slice 6**
([[gold_migration]], `tasks/06_going_gold/gold_migration.md`). The relevant
contract is **C3 — curation is data, not browser state**: the ★/`highlight`, blurb/description, status, and
any curation decision are attributes on the feature row that travel **store-of-record → bake → served
artifact**; localStorage may be a *working buffer* only, never the source of truth for what publishes.
"Moving to db first" = finish demoting `localStorage` from source-of-truth to buffer, and make the served
artifact a pure function of `core.features`.

## What is already CLEAN — do not re-litigate

The Sprint-05 universal refactor and the gold spine **landed**. Verified by observation, not by the cards' word:

- **C1 — 0** non-comment `layerKey === '...'` branches in `main.js` AND `panel.js` (the region grep). Behavior
  lives in the `FEATURE_LIST_LAYERS` spec registry (`main.js:2209`). The contract's old line numbers
  (4096/4168/4180/4215/4583/4328/4427) are **stale** — those branches are gone.
- **C6 — 0** `class [A-Z]` declarations in `main.js`; single vanilla-JS IIFE; no second registry.
- **C2 — one collector.** `collectStarredDestinations()` (`main.js:1173`) is the single destination-row
  engine; `buildPoiGroups`/`renderPoiTab` (left, grouped) and the right ★ list are thin renderers over it;
  the `highlight === true` star gate is applied **once** (`main.js:1181`). No second `pushRow` engine, no
  hardcoded `VISITOR_LIST_LAYERS` (retired, comment-only at `:593`/`:1065`).
- No dead `buildInlineEditor` (deleted as the contract directed); no live `?? blurb` / `?? description`
  read-both crutch in the viewer.

So the spike is **not** the per-layer-branch slop the contracts were written against. That war was won.
The remaining spike is one axis down: **curation + identity still partly live in the browser and in
served files, not in the DB** — exactly the db-first gap. Eight findings, ranked.

-----

## The spike inventory (evidence-grounded)

### F1 — Curation stranded in browser localStorage (the core C3 gap) · HIGH

`aop_positioned_features_v1` (`main.js:savePositionedFeature` / `applyPositionedFeatures` ~`:3000-3060`)
carries FOUR kinds of edit per feature: `highlight` (★), `geometry`, `icon_size`, `locked`. Only **one** of
the four has a DB door:

- **★ `highlight`** → `apply_positioned_features_to_core.py` → `core.features.attrs.highlight` → bake emits
  `attrs` verbatim → served. **Migrated** (Sprint 08, the four reference layers).
- **geometry + icon_size** → only `export_positioned_features.py`, which bakes into served `.geojson` files
  directly. **Stranded file-only** — never reaches `core.features`. A drag-to-move or resize is a per-browser
  edit with no store-of-record. This is a live C3 violation: two browsers can disagree on where a building sits.
- **`locked`** → working-buffer only (fine).

Other `aop_*` keys, classified:
- **Legitimately VIEW state (keep in localStorage):** `aop-viewer-preset-settings-v3`, `aop-section-state-v2`,
  `aop_left_rail_drawer_v1`, `aop_virtual_clock_v1`, `aop_viewer_session_state_v1`, `aop_calendar_*`,
  `aop_lr_card_height_v1`, `aop_feature_visibility_v1` (paint filter, not publish truth),
  `aop_feature_tags_v1` (#tag→coord resolver — a separate axis, C3 explicitly scopes it out).
- **Curation that belongs in the DB:** `aop_positioned_features_v1` (above), `aop_editor_pois_v1` (F2),
  `aop-panel-overrides-v1` (F3). Legacy `aop_visitor_context_overrides_v1` / `aop_brand_logos_overrides_v1`
  are now folded into positioned-features and survive only as forward-migration/clear-list keys
  (`main.js:88-89`) — harmless, but worth a deletion note.

### F2 — Hand-drawn POIs have no direct DB door · HIGH

The editor's own draw store `aop_editor_pois_v1` (`main.js:7370` load, `:7477` register) is the source for
on-map POI rendering AND feeds the collector (`:2449` listRow, the seed Pavilion star). But it has **no
direct writer to `core.features`**. `apply_positioned_features_to_core.py` **intentionally skips editorPois**
(docstring `:54-55`: *"editorPois has its own DB door"*) — yet that door is really the *panel's*
`apply_panel_overrides_to_core.py` `created[]` path, which only fires if the user opens the right panel and
exports. A drawn, starred POI that never goes through the panel **vanishes on browser reset and never
publishes**. The store-of-record for a drawn POI should be `core.features (layer='poi')`, not a localStorage
array with an opt-in export.

### F3 — The legacy FILE-bakers still sit beside the DB path · MEDIUM

**Correction folded from the Quartermaster andon:** the *two apply scripts* are **not** duplication — they are
a deliberate, council-confirmed **two-sink split** (Sprint 08): `apply_panel_overrides_to_core.py` ←
`aop-panel-overrides-v1` writes POI identity/description/geometry (`layer='poi'`);
`apply_positioned_features_to_core.py` ← the `positioned_features` map writes `attrs.highlight` for the four
reference layers. One parser, two stores, no column overlap, by design (they even split reuse — `split_key`/
`sql_str` shared, `read_payload`/`VIEW_STATE_KEYS` deliberately NOT, because the stores differ). The
convergence db-first wants is **one DB store of record**, not one script. Leave the split.

The **real** duplication is the legacy **file-bakers** still in the tree, writing a *different* sink than the
DB path: `bake_panel_overrides.py` (file twin of the panel apply) and `export_positioned_features.py` (bakes
geometry/icon_size into served `.geojson` directly — orphaned since the 2026-06-08 attrs-verbatim bake;
verified by the Witness: it exists, nothing invokes it). Both are callable; a hand-run clobbers the served
files behind the DB's back. **This is already a standing gold OWED** — `gold_migration.md:310-317` / `:355-361`
name exactly this retirement (`export_positioned_features.py` + the `rebake_canonical.py` CONFIG entry +
`import_fema_buildings.py`) as the next increment after the apply-doors exist. The audit doesn't re-card it;
it credits and points at that OWED. Db-first close = the bake is the **sole** writer of served files.

### F4 — Served `publish.geojson` drifts from the DB bake · MEDIUM

The committed `website/data/publish.geojson` (6 features) carries **`blurb`, `last_checked`, `source`** keys
on every feature **in addition to** `description` — verified by reading the file. The current bake
(`export_publish_geojson.sh`) emits only `description` (the convergence, commit `5b5fcdd`). So the committed
served file is a **pre-convergence artifact the bake will not reproduce**; it serves both the old `blurb` and
the new `description`. This is the same "served file is hand-state, not a bake output" class the gold sessions
kept flagging. Non-breaking today (the viewer reads `description`), but it means the served file is not yet a
pure function of the DB. The reference-layer served files (`aop_buildings.geojson` etc.) similarly carry the
full upstream `attrs` verbatim (FEMA/ORNL source fields) — correct by design, but worth a one-line note that
reference served-shape ≠ the POI CMFS spine.

### F5 — A fresh DB volume does NOT reproduce the live map · HIGH (db-first integrity)

This is the sharpest db-first gap. The compose file mounts only `init_db.sql` + `seed_core_pois.sql` +
`seed_core_park_boundaries.sql` (verified, `mvp/docker-compose.yml:15-17`). **Measured against the live DB**
(`docker exec mvp-db-1 psql -U aop -d aop_map -c "select layer, count(*) from core.features group by layer"`,
as of 2026-06-08 — the Witness corrected my first-pass estimates): live `core.features` = **160 rows** (trails
120, cemeteries 8, event 6, buildings 5, visitor 4, poi 4, trail_centerlines 4, park_boundaries 3, field_tracks
2, parcels 2, trailheads 1, observations 1); a fresh-volume seed = **7 rows** (`seed_core_pois.sql` → poi 4 +
`seed_core_park_boundaries.sql` → park_boundaries 3); **live-only = 153 rows**. Everything else (buildings,
cemeteries, visitor, trails, events, parcels, …) arrived via **one-time, unmounted** imports
(`import_fema_buildings.py`, `import_marion_cemeteries.py`, `import_event_schedule_to_core.py`,
`migrate_layers_to_core_features.sql`, …). **A fresh `docker compose up` produces a DB that bakes nearly-empty
reference files.** If the DB is the source of truth, the source of truth is not reproducible from the repo —
the live volume is the only copy of those 153 rows. (This is *correct minimal-dev behavior* if intended, but it
collides head-on with "we are moving to db first.") The fork: seed/mount the imports so a fresh volume == the
publishable map, or declare fresh-volume a deliberately-minimal dev env and document it.

### F6 — Identity is resolved differently per layer (the bugfix generator) · MEDIUM

The last several sessions each patched ONE id-identity edge case (cemetery ★ landing on the parcel twin not
the marker; trails resolving via stamp-less panel props; trail missing `hostKey`). The root is that feature
**identity has multiple resolution paths**: plain `idField`, the derived `spec.idFor`/`trailRowId(props)`
(trails recompute from `trail_number`/`name` because the panel loads served props *without* the load-time
`__trail_row_id` stamp), `findFeatureById` over deduped state (parcel twin) vs `collectStarredDestinations`
reading raw `runtime.data` filtered to `geom_role==='marker'` (marker twin). The v55→v56 fix
(`persistFeatureFlagChange` re-runs `applyPositionedFeatures` so a live ★ lands on both twins) is correct and
idempotent but **symptom-treats** the fork — the next layer with a twin or a stamp-less load will reproduce
the bug. Db-first lets us collapse this: resolve identity from a stable DB key, store the marker as the row of
record, stop carrying parcel+marker twins through the runtime.

### F7 — Registered layers with no list spec (latent footguns) · LOW–MEDIUM

`registerFeatureListLayer('trailheads', …)` is called (`main.js:9608`) but `trailheads` has **no entry in
`FEATURE_LIST_LAYERS`** (it lives only in the preset/toggle config at `:2030`). It's harmless today (the
collector skips any spec without a `listRow`), but the registration call implies a spec that isn't there — the
moment someone makes trailheads starrable, the save silently no-ops with no reload persistence.
`eventSchedule`, `activityHotspots`, `syntheticActivity` are likewise registered without `listRow`/`listMode`/
`highlightable` — they never surface as destinations. Either intended (add a one-line "not a destination layer"
note) or incomplete (add the spec). None is wired to `applyPositionedFeatures` on load, so if any becomes
editable, its overrides die on reload.

### F8 — The `blurb`/`description` naming crosswalk persists · LOW

The DB column is `description` (renamed `5b5fcdd`), but the collector's **row shape** still names the subtitle
field `blurb` (`row.blurb`, the renderers read it at `:1318`/`:1378`), and the reference-layer subtitles are
sourced from `entry.blurb` — the `aop_poi_index.json` **sidecar**, not the DB `description`. So a cemetery's
list subtitle comes from a localStorage/sidecar `blurb`, not from `core.features.description`. Cosmetic +
a third source of subtitle text. Fold the sidecar `blurb` into the DB `description` and rename the row field.

### F9 (housekeeping) — Prototype HTML clutter · LOW

~**81** design-spike HTML files in `website/` (`leftrail_*` ×38, `bottombar_*` ×9, `editor_unified_*` ×8,
`right_sidebar_*` ×8, `add_any_type_*` ×5, `floatgroup_*` ×5, `poi_crud_*` ×4, `calendar_placeholder_*` ×4,
misc). **None** are loaded by `index.html`/`main.js`/`panel.js`, and **`sw.js` precaches none of them**
(verified). Pure design history — archival candidates (a few `*_compare.html` are linked from index as design
notes; keep those). No code cleanup, just tree weight.

-----

## Where this work lives — the bounded breakdown HELD gold slice 6 asked for (Quartermaster fold)

**This audit does NOT mint a "Sprint 09."** The Quartermaster pulled andon on the first draft for standing up a
second planning surface, and it's right: [[gold_migration]] **slice 6 is HELD precisely waiting for this** —
`gold_migration.md:570-574` says *"the real remaining work is C3: demote the parallel `aop-*-v*` localStorage
stores to working-buffers now that core is the store of record. When a human pulls this, it must come back
**bounded**: each named store to demote as its own `- [ ]` line."* The audit **is** that bounded list. So the
findings re-home onto the gold card, not a new sprint:

- **F1** (`aop_positioned_features_v1` geometry/icon_size → core) · **F2** (`aop_editor_pois_v1` drawn-POI →
  core) · **F8** (fold the `aop_poi_index.json` `blurb` sidecar into DB `description`) — the named-store
  `- [ ]` lines gold slice 6 wants. The curation/star axis of these already shipped (Sprint 08); this is the
  geometry/body/subtitle axis of the **same** demotion.
- **F3** (retire the legacy file-bakers `export_positioned_features.py` / `bake_panel_overrides.py`) — already
  the **standing gold OWED** at `gold_migration.md:310-317` / `:355-361`. Fold into it; don't re-card.
- **F5** (fresh-volume parity) + **F4** (re-bake `publish.geojson` from the DB) — the Retirement-step gaps the
  gold sessions already logged (served-only rows, unmounted imports). Reference, don't re-derive.
- **F6** (collapse identity / marker-as-record) — C3 convergence, **highest risk, do last** (the standing
  bugfix root). **F7** (spec-complete the registered-but-spec-less layers) + **F9** (archive 81 prototype HTML)
  — housekeeping notes on the same card.

**Pulling gold slice 6 off HOLD is the USER's call** — it's held "until a human pulls it" (`preserve_card_directives`;
the audit annotates the card to point here, it does not un-hold it). When pulled, the order by leverage:

1. **Fresh-volume parity (F5)** — the foundation; db-first means nothing if the DB isn't reproducible.
   Acceptance: fresh-volume row counts == live (160); bake diff == 0. **Mason note:** seed from a **captured
   snapshot / SQL dump**, NOT by re-running the live network importers inside initdb — `import_fema_buildings.py`
   et al. carry `raise` on geometry drift + a deliberate FEMA 197→5 curation drop, so mounting the live
   importers could `raise` and abort a fresh `docker compose up`. Those throws are import-side raw→curated, not
   display-path — record them as an intentional note, don't move them into the seed path.
2. **geometry/icon_size into core (F1)** — extend `apply_positioned_features_to_core.py` (the existing sink,
   don't invent a second), then F3's `export_positioned_features.py` retirement can land. Acceptance: move a
   building, apply, bake, observe the new position in the served file from the DB.
3. **drawn-POI DB door (F2)** — a direct editor→`core.features (layer='poi')` writer so a drawn POI has a
   store-of-record without the panel detour. **Mason note:** reuse the `apply_panel_overrides_to_core.py`
   upsert-fold-archive pattern (and `panel_overrides.py`) — NO category/status allowlist on the new sink.
   Acceptance: draw+star a POI, apply, bake, it publishes; browser reset doesn't lose it.
4. **bake = sole writer / retire the file-bakers (F3)** — the standing gold OWED. Acceptance: grep shows one
   author→DB→bake path; the file-bakers are gone or `_legacy/`.
5. **re-bake served truth (F4)** — re-bake `publish.geojson` from the DB so the committed served file == bake
   output. **Mason note:** this is a **column projection** (drop stale `blurb`/`last_checked`/`source`), NOT a
   row filter — the accepted exact-string publish-equality stays a note, never "fixed" with a validator.
   Acceptance: `git diff` after a fresh bake == 0. (Touches the served file the user hand-holds — **user's git gate**.)
6. **collapse identity (F6) + spec-complete (F7) + housekeeping (F9)** — do last; highest risk. **Mason note:**
   F7's fix stays a `listRow`/`highlightable` addition with R13 safe defaults — never a registration-time throw.

### The genuine forks (user decisions, not mine to make)

- **Un-hold gold slice 6?** It's HELD for a human pull. *Rec: pull it scoped to this bounded list — db-first is
  the user's stated direction and the breakdown gold slice 6 required now exists.*
- **F5:** fresh-volume == live (seed a snapshot), or fresh-volume = deliberate minimal dev env?
  *Rec: seed it — "db-first" implies the DB is reproducible from the repo.*
- **F3:** delete the legacy file-bakers, or keep them as a documented file-only fallback? *Rec: `_legacy/` them;
  one path. (This is the existing gold OWED's own recommendation.)*
- **F9:** delete the 81 prototypes, move to `website/_archive/`, or a design-spike branch? *Rec: `website/_archive/`.*
- **F4:** re-baking `publish.geojson` overwrites a file the user has been hand-editing — **user's git gate.**

-----

## Council consult — Steward-chaired, full six

Convened over this audit (the artifact, not a narration), each seat fresh + adversarial, prompted to refute.
**Round 1: 3 andon + 2 clear.** All three andons real, grounded, folded into the revisions above; affected
seats re-reviewed.

- **Warden — CLEAR (R1).** Boundary-clean: the scope read is right (audit + council + sliced plan, NOT a blind
  refactor of 10.7k lines — "do all the things" is bounded by *review/begin/convene*, and the work is decisive,
  not timid). Git gate untouched (verified: nothing staged, audit is the newest file, prior dirty tree from
  earlier sessions left entirely alone — noticed, not adopted). HELD gold slice 6 respected; no card directive
  deleted; F4 re-bake correctly flagged as the user's gate.
- **Mason — CLEAR (R1), with card notes (folded).** Seed target `core.features` is non-limiting by construction
  (no CHECK/enum/domain-NOT-NULL; `init_db.sql:47-75`). Notes carried into the slices above: (1) F5 seed from a
  snapshot, not live importers (they `raise`/curate-drop import-side); (2) F2/F3 reuse the upsert-fold-archive
  sink, no allowlist; (3) F4 is column projection only; (4) F7 stays safe-default spec, no registration throw.
  No new constraint/validator/row-dropping filter anywhere in the plan.
- **Witness — ANDON → folded.** F5's row counts were stated as fact but were estimates *and wrong* — the DB was
  up and queryable. Corrected to the **measured** values (live `core.features` **160**, fresh seed **7**,
  live-only **153**) with the query shown and date-anchored. Everything else the audit asserted independently
  re-observed CLEAN (C1/C6 greps = 0; `publish.geojson` carries blurb+description+last_checked+source on all 6;
  the compose mounts; `trailheads` registered w/o spec; `export_positioned_features.py` orphaned; editorPois
  skipped). **Re-review:** numbers now match the Witness's own measurement → clears.
- **Quartermaster — ANDON → folded.** The first draft minted "a sprint, sliced thin" = a second planning
  surface for work [[gold_migration]] slice 6 (HELD) already owns, and mis-framed the deliberate two-sink apply
  split as duplication. Re-homed onto gold slice 6's bounded `- [ ]` lines + the standing OWED (F3 file-bakers)
  + the Retirement-step gaps (F4/F5); F3's "two apply scripts = duplication" framing struck. **Re-review:** one
  planning surface, the split preserved → clears.
- **Scribe — ANDON → folded.** The outcome wasn't durably recorded where the next session looks: handoff not
  updated, the plan parked only in a receipt (not a card home), no `[[wikilinks]]`, council section stubbed.
  Fixed: same-turn handoff entry added; the durable home is **gold slice 6** (annotated to point here as its
  bounded breakdown — not a new card, per the Quartermaster); wikilinks added; this section filled. **Re-review:**
  recorded, homed, linked → clears.
- **Steward — CLEARS the gate.** Full six clear after one round + folds. The audit's *findings* held up under
  the Witness's independent re-observation (only the F5 numbers needed correction; the argument survived). The
  *plan* converged onto the one surface the brain already holds (gold slice 6), staying on the farm and off the
  user's git gate. Definition-of-Done met for a brain-only audit: observed (not narrated), on the farm,
  non-limiting, recorded. **What's owed is the user's:** pull gold slice 6 off HOLD (or not), decide the four
  forks, and the git commit. Nothing here is committed; no `website/`/`mvp/` file was touched.

**Receipts:** the five worker verdicts are summarized above; full seat reasoning is in this turn's transcript.
**Owed (user's gate):** the gold-slice-6 pull + fork decisions + any commit. The pre-existing dirty working
tree (prior sessions' `main.js`/`panel.js`/`sw.js` + the four untracked `mvp/scripts/*.py`) is unrelated to
this audit and stays the user's to review.
