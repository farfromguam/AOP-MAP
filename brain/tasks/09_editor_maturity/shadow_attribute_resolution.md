# Shadow-attribute resolution — the ralph-loop plan (Path A), Path B held

> **Sprint 09 resolution spine. Opened 2026-06-09.** Turns the council-cleared, **id-tagged** 45-finding
> catalog in [[shadow_attributes_audit]] (`shadow_attributes_audit.md` FINDINGS) into an executable, looped
> sequence. **Source of the findings + the two-path ruling:** the audit card + its receipt
> `../../output/council/shadow_attributes_audit_review_20260609.md`. This card does **not** re-list the
> findings — it sequences them. Each slice's `Closes:` cites findings by their **catalog `id`** (the
> backticked slug on each catalog bullet — grep the audit card for it; the ids are verbatim).

#aop #09_editor_maturity #shadow_attributes #cmfs #resolution #ralph_loop #db_first

> **COUNCIL: FULL SIX CLEAR (plan-review 2026-06-09; 2 andons folded → re-cleared).** Witness
> (verifiers must be live-DOM on `playwright_base.py`, never read-site re-derivation; A1's join machinery
> + label side-effect now named) + Scribe (catalog re-emitted id-tagged so `Closes:` ids grep-resolve; 3
> orphans homed; coverage total = 45) both pulled andons → folded → re-cleared. Quartermaster/Mason/Warden
> clear (Mason's additive-preserve note folded into the binding). Receipt:
> `../../output/council/shadow_attribute_resolution_plan_review_20260609.md`. **Ralph-loop-ready** — the
> loop prompt is below; the commit-pause + the `vNN` bump are the user's git gate; the loop runs in a fresh
> session.

-----

## The shape (Steward ruling, council-cleared 2026-06-09)

The cut+migrate splits into **two physical paths**, because the served reference files are baked by
`rebake_canonical.py` **from `data/raw/`**, not from `core.features`:

- **Path A — file / crosswalk / render (THIS loop).** Resolvable by completing the **additive** CMFS
  crosswalk + `_schema.json` + `rebake_canonical.py`, then pointing the viewer read sites at the
  canonical fields and deleting the runtime sidecar joins. **No DB-door pull needed.**
- **Path B — DB door / identity (gold slice 6, HELD — the user's pull).** The inherently DB/identity
  roots. The loop **STOPS at the Path A/B boundary**; Path B's findings are listed, tagged, and wait for
  the user to pull gold slice 6 (`../06_going_gold/gold_migration.md`).
- **Out of scope (events axis, re-homed):** the event-overlay findings — C3 scopes the `#tag`→coord axis
  off the visitor-list axis; both go to the event-overlay convergence (its own work).

### Coverage accounting (every one of the 45 findings is homed — total, visible)
**22 Path A** (A1=8 · A2=2 · A3=4 · A4=3 · A5=5) + **20 Path B** (held) + **2 out-of-scope** (events) +
**1 deferred-low** (no Path-A home) = **45**. No orphans. (Cross-checkable: every `id` below appears in
exactly one bucket.)

## Loop contract / gates

plan → **council the plan** (full six — done 2026-06-09; 2 andons folded, see banner) → user
**commit-pause** → **ralph-loop the Path A slices in a fresh session** (gold / sprint-08 cadence; this
producing session is context-heavy and the council's own principle is a fresh executor + fresh
verification).

Each iteration: read this card → do the **next incomplete Path A slice** (start at A1) → verify by its
**tile-independent observable acceptance** → **Record on green** (check the box + a DONE block) → **stop**.
**STOP at the Path A/B boundary** (do not start Path B — gold slice 6 is HELD). Do **NOT** commit or bump
`sw.js` / `#appVersion` — **report what's owed** (one bump covers the whole Path A batch at the user's
commit, not one per slice).

### Loop prompt (feed verbatim each iteration, fresh session)

> Read `brain/tasks/09_editor_maturity/shadow_attribute_resolution.md`. Obey its **Loop contract**. Do the
> **next incomplete Path A slice** (start at A1), verify it by its tile-independent **Observable
> acceptance**, **Record on green**, then stop. **STOP at the Path A/B boundary** (Path B = gold slice 6,
> HELD). Do **NOT** commit or bump `sw.js`/`#appVersion` — report what's owed. Convene the council
> done-review on the slice diff before declaring it done.

### Standing conditions the loop inherits (non-negotiable)

- **Mason (the binding):** every controlled-vocabulary target (`kind`/`confidence`/`status`/`difficulty`/
  `intensity_class`) is an **additive display mapping with a safe fallback** — map known values, pass an
  out-of-vocab value through as its own label (mirror `rebake_canonical.py` `_PUB_KIND.get(layer, layer)` /
  `category or "poi"` / `first(...) or prov.get(...)`). **Never** a CHECK/enum-reject/row-dropping
  filter/coerce-to-blank/throw (C5, R13). **A canonical field is a NEW derived field; the original physical
  key is preserved underneath** (mirror the re-bake's additive preserve) — never overwritten or dropped.
- **C1/C6 — converge, don't multiply.** Re-home into the ONE crosswalk + the ONE renderer + the ONE
  schema. No second catalog loader, second list engine, class hierarchy, or parallel editor surface.
- **Witness (the C4 gap the audit flagged) — verification is a LIVE observation, never a re-derivation.**
  Each convergence slice's verifier is a Playwright run on **`mvp/scripts/playwright_base.py`** that reads
  the **live DOM / feature-state** (tile-independent: no `networkidle`, no `queryRenderedFeatures`) and
  attaches the output. It must read the rendered left-list row text, the right-panel Name input *value*,
  and the map label feature's `name` — and assert they agree. **A slice may NOT be closed by tracing the
  read site** ("the row builder reads `p.name`, the bake set `p.name`, therefore they agree" is the exact
  re-derivation the Witness refutes). Plus a `grep` proving the sidecar join is **gone** at the read site.
- **Additive re-bake:** `rebake_canonical.py` always re-bakes from `data/raw/`, preserves original keys,
  idempotent (`--check`). A slice touching served data or shell assets owes a `sw.js`/`#appVersion` bump
  (cache invalidation) — reported, the user's gate.

-----

## Path A — the looped slices

### A1 — Crosswalk + `_schema.json` + re-bake population (foundational; do first)
Make the canonical fields REAL in the served data, **additively**, before any read site is repointed.
- **Closes:** `schema-json-missing-catalog-poi-index-and-tier3-crosswalk` ·
  `trail-difficulty-sidecar-and-uncrosswalked` · `building-status-holds-facility-role` ·
  `machine-layer-name-status-in-offcanonical-keys` · `publish-confidence-status-off-vocabulary` ·
  `cmfs-variability-table-stale` · `legacy-blurb-key-survives-in-served` · `schema-manifest-stale`.
- **BUILD (Witness — this is net-new machinery, not a config tweak):** today `rebake_canonical.py` reads
  **one file at a time from `data/raw/`** with **no cross-file join** and the two sidecars
  (`aop_trail_catalog.json`, `aop_poi_index.json`) are **not in `raw/` nor in `CONFIG`**. A1 must:
  (a) make the sidecars deterministic bake inputs (copy into `data/raw/` or read them by a fixed path);
  (b) add a **join primitive** to the re-bake (load the trail catalog by `number`→`trail_number`; the
  poi-index by its `match` fields); (c) register both sidecars + a `trail_number`→"Trail N" name fallback
  + a **Tier-3 `facets` block** (difficulty/category/occupancy/…) in `_schema.json`; (d) populate canonical
  `name`/`description` + facets from the join; map `confidence`/`status` as **display** values; building
  `status` = publish/review state with the facility role surfaced as a **facet**. **All additive:** the
  canonical field is a NEW derived field, every original physical key is preserved underneath (re-bake
  lines ~216-221); nothing dropped/overwritten/coerced (Mason binding).
- **SIDE EFFECT to observe (Witness):** the re-bake deliberately leaves trail-network `name=None` today
  ("auto-filling would spawn labels on unnamed features", `rebake_canonical.py:~98-101`). A1 inverts that
  for *catalog-named* trails, so the map label layer (`main.js` `text-field:['to-string',['get','name']]`,
  `filter:['to-boolean',['get','name']]`) will now **paint "Launchpad"** on those trails. This is intended,
  but A1's acceptance must **count labels** so a stray label on a still-unnamed edge is caught, not surprised.
- **Files:** `website/data/_schema.json`, `mvp/scripts/rebake_canonical.py`,
  `brain/research/common_feature_schema.md` (fix the stale variability table — it points at a non-existent
  `aop_brand_logos` file), `website/data/raw/` (sidecars as inputs).
- **Observable acceptance (tile-independent, artifacts attached):** run the re-bake, then `--check` clean
  → `jq` the served `aop_trail_network.geojson`: trail #1 carries canonical `name="Launchpad"` +
  `description` + `facets.difficulty="easy"`, **and its original `name="1"` key is still present**
  (additive); buildings/cemeteries/visitor carry non-null canonical `name`/`description` with originals
  preserved; `_schema.json` lists both sidecars + a facets block; **feature count == `data/raw/` count**
  (nothing dropped); **named-feature/label count** before vs after is the expected delta only (no stray
  labels); an out-of-vocab kind/status still present (no reject).
- **Owed:** `sw.js`/`#appVersion` bump (served data changed). Durable change = `_schema.json` + the script
  + the sidecar inputs; restore served files to HEAD after verifying if this iteration is verify-only.

### A2 — Trail read-site convergence (the Launchpad fix; do after A1)
Point every trail read site at the canonical `name`/`description`; delete the runtime catalog join.
- **Closes:** `trail-name-shadow-four-surface-fork` · `trail-listrow-status-revisitnote-source-fabricated`.
- **Files:** `website/js/main.js` (left list `rowLabel`/`listRow`, map label text-field, search index,
  popup — read canonical `name`/`description`; remove the `trailCatalogLookup` calls at the read sites —
  the join now lives in the bake), `website/js/panel.js` (`aopTrails` node label/key read canonical `name`).
- **Observable acceptance (Witness — LIVE DOM, not a read-site trace):** a new Playwright verifier on
  `mvp/scripts/playwright_base.py` that, for trail #1, reads the **rendered left-list row text**, the
  **right-panel editor Name input `value`**, the **map label feature `name`**, and the **search result** —
  and asserts all == "Launchpad" (not "1"/"Trail 1"); plus `grep` proving `trailCatalogLookup` is gone from
  the read sites (still defined is fine only if it has zero callers); `node --check`. Attach the verifier
  output. (This is the exact failure that opened the sprint.)
- **Owed:** `sw.js`/`#appVersion` bump.

### A3 — Building / cemetery / visitor name + subtitle convergence (do after A1)
Kill the `poiIndexLookup` cross-layer join; read canonical name/description.
- **Closes:** `poi-index-blurb-revisit-cross-layer-join` · `poi-index-dual-source-db-vs-sidecar` ·
  `visitor-name-label-description-three-source-fork` · `building-name-is-address-facility-name-shadow`.
- **Files:** `website/js/main.js` (building/cemetery/visitor list+popup read canonical `name`
  [building prefers `facility_name`; address → a facet] + `description`; remove `poiIndexLookup` at the
  read sites), `website/js/panel.js` (the matching node labels/Name fields).
- **Observable acceptance (LIVE DOM):** the A2-style Playwright verifier extended to the Pavilion/Front
  Office, a cemetery, and a visitor callout — **left-list row text == right-panel Name value == popup**
  on name + description; `grep` proves `poiIndexLookup` gone from the read sites; `node --check`. Attach output.
- **Owed:** bump.

### A4 — Render-derived display unification (do after A3)
One display-name helper; kind chips from canonical `kind`; baked source string.
- **Closes:** `poi-display-name-three-derivations` · `seed-poi-kind-is-propernoun-category`
  (`kind='poi'` safe-default, "Pavilion" → category facet) · `source-file-shown-as-derived-runtime-value`
  (bake a `source`/`source_file` attribute).
- **Files:** `website/js/main.js` + `website/js/panel.js` (display-name fallbacks),
  `mvp/scripts/rebake_canonical.py` + `_schema.json` (seed POI kind default; baked source attribute).
- **Observable acceptance (LIVE DOM):** Playwright verifier — a drawn POI shows ONE name across
  map/list/panel (read all three live); the seed POI kind chip reads "poi" with "Pavilion" as a category
  facet (and a feature with a real class set survives — Mason binding); the Source-tab File never reads
  "unknown" for a baked feature; `node --check`. Attach output.
- **Owed:** bump.

### A5 — Edge-dispatch → spec strategies (C1; do last in Path A)
Move the remaining per-layer call-site special-casing into declarative spec capabilities.
- **Closes:** `host-create-bridge-hardcodes-editorpois` · `visitor-list-source-chip-freestanding-map` ·
  `panel-userfeatures-source-special-casing` · `panel-explicit-host-toggle-map` ·
  `panel-positional-synthetic-index-identity`.
- **Files:** `website/js/main.js` (`spec.create` capability replacing the `editorPois` `!==` guard;
  `sourceChip` as a spec field — R10), `website/js/panel.js` (`node.hostToggle` / capability flags
  replacing `panel-explicit-host-toggle-map` + the `userFeatures` source branches; `spec.idField` for the
  positional-index identity).
- **Observable acceptance:** **structural** — the C1 region grep stays 0 non-comment `layerKey === '`,
  C6 stays 0 `class [A-Z]`, no new top-level registry; `node --check`. **Plus a LIVE behavior check** on
  the one layer whose user-facing behavior changes most (the `editorPois` **create** path): a Playwright
  run on `mvp/scripts/playwright_base.py` reads the DOM before/after a "+ POI" create and confirms the
  feature lands and is editable exactly as before. Attach output. (If a specific sub-change is structural
  only — e.g. `sourceChip` as a spec field — its acceptance may be grep + `node --check`, stated as such;
  do not narrate a DOM check that wasn't run.)
- **Owed:** bump.

> **— PATH A/B BOUNDARY. The loop STOPS here. —**

## Path B — HELD (gold slice 6, the user's pull; NOT looped here)

The DB-door / identity / bake-reproducibility / curation-as-data roots — the bounded list for
`../06_going_gold/gold_migration.md` slice 6. Tagged, **not sliced** (no `- [ ]` here):

- **Identity (6):** `served-id-heterogeneous-no-canonical-key` (F6 root) ·
  `cemetery-parcel-marker-twin-nonunique-id` · `ellis-cemetery-multi-id-across-files` ·
  `buildings-served-id-is-attrs-businesskey-not-pk` · `two-editor-sinks-opposite-homes` ·
  `publish-kind-taxonomy-fork` (its kind-*display* part rides A1/A4's controlled-vocab binding; the
  *one-id-per-real-feature* part is the DB-identity root held here).
- **localStorage-as-truth / C3 (7):** `served-features-edited-props-localstorage-only-no-db-door` ·
  `name-edit-two-store-fork-by-surface` · `panel-overrides-replayed-as-published-view` ·
  `highlight-two-store-by-surface` · `feature-visibility-paint-filter-as-curation` ·
  `visitor-file-two-kinds-one-orphaned-from-host-star` · `maturity-tier-derived-from-panel-tree-position`.
- **Bake reproducibility (7):** `publish-geojson-stale-not-reproducible` · `published-id-is-volatile-serial` ·
  `two-writers-same-five-files-rebake-vs-export` · `trail-human-name-not-in-db-bake-can-only-emit-number` ·
  `canonical-fields-duplicated-columns-vs-attrs-served-from-attrs` · `event-umbrella-metadata-hardcoded-in-bake` ·
  `reference-bake-no-meta-on-fresh-volume`.

> Symmetry: Path A makes the **served files** canonical via the re-bake (no DB pull); Path B makes the
> **DB** the reproducible store of record. A few bake-drift items (legacy `blurb` drop, manifest regen) are
> handled additively in A1; the reproducibility root itself stays Path B.

## Out of scope — events axis (re-homed to the event-overlay convergence)
- `event-anchor-position-from-localstorage-tag-binding` — coordinate-less anchor positioned from a
  per-browser `#tag` binding (C3 scopes the `#tag`→coord axis off the visitor-list axis).
- `event-overlay-two-divergent-resolvers` — host vs panel run two different resolvers; the events surface,
  not the reference-layer/CMFS axis. Both belong to the event-overlay convergence (its own card/work).

## Deferred — low, no Path-A home (stated, not silently dropped)
- `hotspot-twin-id-collision-offvocab-sort` (LOW, contract "none") — the cell/centroid twin-id is a latent
  identity quirk with no current user-facing break; its `intensity_class` *display/sort* is covered by
  A4's controlled-vocab binding (out-of-vocab sorts to a default bucket, never dropped). Left unsequenced;
  revisit if it surfaces a real bug.

## References (treat as the thing)
- [[shadow_attributes_audit]] — the id-tagged 45-finding catalog (this plan's source) + its council receipt.
- `../../research/common_feature_schema.md` — the CMFS + crosswalk + `_schema.json` (the migration target).
- `../../northstar/editor_architecture_contracts.md` — C1–C6 + R1–R14.
- `../../northstar/source_register.md` — Tier-2 provenance (required fields, NOT a closed enum — Mason).
- `../06_going_gold/gold_migration.md` slice 6 — Path B's home (HELD).
- `../../output/council/shadow_attributes_audit_review_20260609.md` — the Steward two-path ruling.
