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
**22 Path A** (A1=7 · A2=2 · A3=4 · A4=4 · A5=5) + **20 Path B** (held) + **2 out-of-scope** (events) +
**1 deferred-low** (no Path-A home) = **45**. No orphans. (Cross-checkable: every `id` below appears in
exactly one bucket. `publish-confidence-status-off-vocabulary` re-homed A1→A4 on 2026-06-09 — A1 closes 7,
A4 closes 4; total Path A unchanged at 22.)

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
- **Closes (7):** `schema-json-missing-catalog-poi-index-and-tier3-crosswalk` ·
  `trail-difficulty-sidecar-and-uncrosswalked` · `building-status-holds-facility-role` ·
  `machine-layer-name-status-in-offcanonical-keys` · `cmfs-variability-table-stale` ·
  `legacy-blurb-key-survives-in-served` · `schema-manifest-stale`.
  (`publish-confidence-status-off-vocabulary` **re-homed A1→A4, 2026-06-09** — a read-site display relabel;
  publish.geojson is DB-baked, not Path-A re-baked, so the bake can't own it.)
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

> **A1 DONE — VERIFIED + COUNCIL FULL SIX CLEAR (2026-06-09).** Witness·Warden·Quartermaster·Mason·Steward
> clear; Scribe clear after a folded andon (handoff line added + this receipt written so the clear is
> artifact-backed). Receipt: `../../output/council/shadow_a1_canonical_rebake_20260609.md`.
>
> **Shipped (`mvp/scripts/rebake_canonical.py`):**
> - **Sidecar join primitives.** Trail catalog folds into `name`/`description` + `facets.difficulty` by
>   `trail_number → number`; poi-index folds into `description` (blurb) + `facets.revisit_note` by its
>   `match{}` fields. Read by **fixed path from `website/data/`** (not copied into `raw/`): the bake never
>   writes them so it stays idempotent, and an actively-authored catalog must not go stale behind a one-time
>   copy. (The plan offered "copy to `raw/` OR read by fixed path" — chose the latter.)
> - **Tier-3 `facets` block**, additive, emitted only where a value exists: `difficulty` (trails),
>   `category` (POIs), `facility_role` + `occupancy` (buildings), `revisit_note`. Registered in
>   `_schema.json` (new `facets` + `sidecars` blocks).
> - **Building `status` → publish/review state** ("raw context"); the facility role moved to
>   `facets.facility_role` (the raw `facility_role`/`publish_status` keys preserved underneath).
> - **Machine-layer name/status crosswalk** where a physical key exists (activity/synthetic: name←`label`/
>   `track_name`, status←`publish_status`/`review_status`) — applied as a uniform rule, no layerKey. Verified
>   no label spawns (those symbol layers read `label`/raw keys; none read canonical `name`).
> - **Additive-preserve fix.** `name`/`description` collide with the canonical field name, so a join that
>   overwrites them (trail "1"→"Launchpad") would drop the original. Now stashed under `_original` — nothing
>   lost (Mason binding honoured for the collision case the join introduces).
> - **`_meta` + manifest maturity preservation.** The old `if "_meta" not in doc` guard silently wiped the
>   `stamp_maturity.py` stamps on every re-bake (raw/ carries a partial `_meta`). Now overlays live-only
>   `_meta` keys; `write_manifest` carries per-layer `maturity` + `maturity_tiers` forward and refreshes
>   counts + `updated_at` (`schema-manifest-stale` closed).
> - **`common_feature_schema.md`** variability table fixed (dropped the non-existent `aop_brand_logos` row;
>   added a currency note pointing live divergence at the read sites = this sprint).
>
> **Observable acceptance — PASS (tile-independent).** Re-bake runs + `--check` clean (non-writing,
> confirmed); idempotent (2nd run byte-identical); every baked file's feature count == `raw/` count;
> trail-network named/label count **100→100** (8 catalog trails already carried the number → label text
> changes, count unchanged, **no stray labels**); out-of-vocab `brand_logo` kept (no reject). Live-DOM
> verifier `mvp/scripts/playwright_verify_shadow_a1_canonical.py` (on `playwright_base.py`): viewer boots
> over the new data with **0 console errors**, trail #1 = `name="Launchpad"` + description +
> `facets.difficulty="easy"` + `_original.name="1"`, Pavilion/Ellis-marker/visitor descriptions populated,
> Pavilion `facets.facility_role` set + `status="raw context"`, publish has **no `blurb` key** + still 6
> features (DB-baked, not reverted) — all observed through the running app. **RESULT: PASS.**
>
> **Two scope rulings folded into A1 (Steward-confirmed in the receipt):**
> 1. **`publish.geojson` removed from the re-bake `CONFIG`.** It is DB-baked by `export_publish_geojson.sh`
>    (6 features); `raw/publish.geojson` is a stale 5-feature snapshot, so the unmodified re-bake was
>    *reverting* publish 6→5 (the two-writers regression). rebake_canonical must not co-own a DB-baked file.
>    Its manifest entry is carried forward (count refreshed). The full DB-reproducibility collapse stays
>    **Path B / gold slice 6**.
> 2. **`legacy-blurb-key-survives-in-served` — DONE** via an idempotent in-place strip on the served
>    `publish.geojson` (drops the retired `blurb` where canonical `description` carries the copy; the current
>    export SQL already emits `description`, so this matches a fresh DB bake without a DB pull).
>    **`publish-confidence-status-off-vocabulary` — RE-HOMED to A4** (a display relabel belongs at the read
>    site; mapping `'medium'`→a source_register confidence is a curation call, not a bake guess). Flagged for
>    the Steward like the events re-home; the audit catalog id is annotated.
>
> **Owed (user's git gate):** the commit (`rebake_canonical.py` + `_schema.json` + 9 served `*.geojson` +
> the new verifier + brain) **with one `sw.js`/`#appVersion` bump** covering the whole Path A batch (one bump
> per deploy, not per slice). Not committed; not bumped — reported.

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

> **A2 DONE — VERIFIED + COUNCIL FULL SIX CLEAR (2026-06-09).** Receipt:
> `../../output/council/shadow_a2_trail_name_20260609.md`.
>
> **Shipped:**
> - **The runtime catalog join is GONE.** `trailCatalogLookup` + `fetchTrailCatalog` + the `trailCatalog`
>   Map are deleted from `main.js` (grep: **0 references**). Every trail read site now reads the canonical
>   field baked by A1: `rowLabel` + `listRow` (the one collector), the map label (already A1), the popup
>   title/body, the search index + result, and the `panel.js` `aopTrails` node label.
> - **The four-surface fork is closed.** Left list, right panel Name input, map label, search, and popup
>   all read `feature.properties.name` → "Launchpad" for trail #1 (was "Launchpad"/"Trail 1"/"1"/unsearchable).
>   `panel.js` no longer prefixes "Trail " onto a real name (no "Trail Launchpad").
> - **listRow de-fabricated** (`trail-listrow-status-revisitnote-source-fabricated`): `status` reads the
>   canonical `props.status` (not difficulty), `source` reads `props.source` (not a hardcoded string),
>   `blurb`/`revisitNote` read canonical `description`/`facets.revisit_note`.
> - **Number-search preserved.** Catalogued trails are still findable by number (AOP IDs by number on the
>   map): the search alias now carries both the name and the `trail_number`. Verified: searching "1" still
>   returns trails.
> - **Catalog enrichment baked (so the join could be fully deleted).** `rebake_canonical.facets()` now folds
>   the catalog's `length_mi`/`tr`→`onx_tr`/`connects` as trail facets; the popup reads them from the feature.
>   The always-empty onX-license footer (0 trails carried `license_on_text`) was dropped. The authoring
>   catalog file still feeds the bake + the copy-review page; only the render-time join was removed.
>
> **Observable acceptance — PASS (LIVE DOM, tile-independent).** `mvp/scripts/playwright_verify_shadow_a2_trail_name.py`
> (on `playwright_base.py`): for trail #1, the map-label source feature `name`, the rendered search result,
> the panel row text, and the **right-panel Name input value** ALL == "Launchpad"; the search shows the
> baked description; "1" still finds a trail; the uncatalogued trail #15 still reads "Trail 15"; **0 console
> errors**. `grep` proves the join is gone. `node --check` clean on both files. A1 verifier still PASS
> (no data regression). **RESULT: PASS.** (Noted, not mine: `playwright_verify_feature_list.py` fails on
> the drawn-POI **Move** flow — confirmed PRE-EXISTING by running it against committed-HEAD JS; not an A2
> regression, separate cleanup.)
>
> **Owed (user's git gate):** rides the same single `sw.js`/`#appVersion` bump + one commit as the rest of
> the Path A batch (`main.js` + `panel.js` + `rebake_canonical.py` + `aop_trail_network.geojson` + the new
> A2 verifier + brain). Not committed; not bumped — reported.

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

> **A3 DONE — VERIFIED + COUNCIL FULL SIX CLEAR (2026-06-09).** Receipt:
> `../../output/council/shadow_a3_poi_name_20260609.md`.
>
> **Shipped:**
> - **The per-feature `poiIndexLookup` blurb join is GONE** (3 callers removed; function deleted — 0
>   callers). Building/cemetery/visitor `listRow`s read canonical `description` + `facets.revisit_note`
>   (folded by A1's poi-index join). `fetchPoiIndex`/`poiIndex` stay ONLY for the POI-tab group taxonomy
>   (labels + order) — config, not a per-feature shadow attribute.
> - **Building name un-shadowed** (`building-name-is-address-facility-name-shadow`): `rebake_canonical`
>   now bakes canonical `name` = the facility name ("Pavilion", via `n_building` = `facility_name or
>   first(NAME_KEYS)`), and the street address moves to `facets.address`. Every surface — listRow, rowLabel,
>   panel row label, panel Name input, search — reads the one canonical `name`. Private structures with no
>   facility name keep the address as their name (fallback).
> - **Visitor fork closed**: description reads canonical (composed at bake where there's no blurb); kind is
>   the canonical `visitor_callout`. Cemetery description reads canonical (Ellis blurb; the three
>   outside-envelope cemeteries legitimately have none — revisit_note rides as a facet).
>
> **Observable acceptance — PASS (LIVE DOM, tile-independent).** `mvp/scripts/playwright_verify_shadow_a3_poi_name.py`
> (on `playwright_base.py`): the Pavilion reads "Pavilion" on the served feature, the rendered search
> result, the panel row, AND the right-panel **Name input value** — all agree; the address is searchable as
> an alias (`1010 ellis` → Pavilion) and shows as the panel detail; Pavilion/Ellis-marker/visitor
> descriptions are baked; **0 console errors**. `grep`: `poiIndexLookup` 0 callers. `node --check` clean on
> both files. A1 + A2 verifiers still PASS. **RESULT: PASS.**
>
> **Owed (user's git gate):** rides the same single `sw.js`/`#appVersion` bump + one commit as the Path A
> batch (`main.js` + `panel.js` + `rebake_canonical.py` + `aop_buildings.geojson` + `aop_cemeteries.geojson`
> + `aop_visitor_context_callouts.geojson` + the new A3 verifier + brain). Not committed; not bumped.

### A4 — Render-derived display unification (do after A3)
One display-name helper; kind chips from canonical `kind`; baked source string.
- **Closes:** `poi-display-name-three-derivations` · `seed-poi-kind-is-propernoun-category`
  (`kind='poi'` safe-default, "Pavilion" → category facet) · `source-file-shown-as-derived-runtime-value`
  (bake a `source`/`source_file` attribute) · `publish-confidence-status-off-vocabulary`
  (**re-homed from A1, 2026-06-09:** an additive display relabel of `confidence`/`status` at the chip
  read site — map known source_register values, pass an out-of-vocab value through as its own label; the
  raw value survives. The bake can't own it — publish.geojson is DB-baked, not Path-A re-baked. NB: the
  `'medium'`→source_register-confidence mapping is a curation call surfaced for the user).
- **Files:** `website/js/main.js` + `website/js/panel.js` (display-name fallbacks),
  `mvp/scripts/rebake_canonical.py` + `_schema.json` (seed POI kind default; baked source attribute).
- **Observable acceptance (LIVE DOM):** Playwright verifier — a drawn POI shows ONE name across
  map/list/panel (read all three live); the seed POI kind chip reads "poi" with "Pavilion" as a category
  facet (and a feature with a real class set survives — Mason binding); the Source-tab File never reads
  "unknown" for a baked feature; `node --check`. Attach output.
- **Owed:** bump.

> **A4 DONE — VERIFIED + COUNCIL FULL SIX CLEAR (2026-06-09).** Receipt:
> `../../output/council/shadow_a4_display_20260609.md`.
>
> **Shipped:**
> - **One drawn-POI display name (`poi-display-name-three-derivations`).** New `poiDisplayName(props)`
>   helper in `main.js` (`name.trim() || category || 'POI'`) is the SINGLE derivation the editorPois
>   `listRow.name` + `rowLabel` both read; the three `editor-poi-*labels` map symbol `text-field`s
>   (main.js + the panel.js MAP_DATA mirror) became `coalesce(name, category, 'POI')` to mirror it (a
>   style expression can't call JS). The old three-way fork is gone — the dock row no longer derives
>   `category — name`, the map no longer coalesces a different fallback. The category stays a Tier-3 facet
>   shown in the Category field / panel Details, never smuggled into the title.
> - **Seed POI kind un-shadowed (`seed-poi-kind-is-propernoun-category`).** `rebake_canonical` seed config
>   is now `kind=lambda p: p.get("kind") or "poi"` — the controlled class "poi", not the proper-noun
>   category. "Pavilion" rides as `facets.category` (the raw `category` key preserved). **Mason safe
>   default:** a feature carrying a real controlled `kind` survives (`{'kind':'trailhead'}`→'trailhead');
>   nothing is coerced or rejected.
> - **Source-tab File reads a baked attribute (`source-file-shown-as-derived-runtime-value`).** The
>   re-bake stamps a per-feature `source_file` on **named (non-machine) layers only** (machine/coverage
>   layers stay lean — no per-feature bloat); `panel.js fileForItem` prefers `item.props.source_file`,
>   falling back to the old source→file map. The File never reads "unknown" for a baked feature.
>   `_schema.json` documents the field.
> - **Confidence/status display relabel (`publish-confidence-status-off-vocabulary`, re-homed A1→A4).**
>   `panel.js` gains additive `CONFIDENCE_DISPLAY`/`STATUS_DISPLAY` maps + `vocabDisplay(v, map)` =
>   `map[key] || String(value)`, wired into the ONE `provenanceFields`/`PROVENANCE_KEYS` renderer (the
>   optional 3rd tuple slot). A known value gets its canonical label; an **out-of-vocab value passes
>   through as its own label** — never dropped/blanked/coerced/thrown (C5/R13). The raw value is untouched
>   on the feature. The `'medium'`→source-register-confidence mapping is left a **curation call surfaced
>   for the user** (publish trails carry `confidence='medium'`/`status='observed'`; they pass through
>   visibly, not silently rewritten).
>
> **Observable acceptance — PASS (LIVE DOM, tile-independent).** New
> `mvp/scripts/playwright_verify_shadow_a4_display.py` (on `playwright_base.py`): for the seed Pavilion
> (a drawn editorPois feature), the editor-poi **map source feature name**, the rendered **left POI-tab
> row**, the **panel editorPois item row**, and the right-panel **Name input value** ALL == "AOP Pavilion"
> (the old `Pavilion — AOP Pavilion` dock-row fork is gone); the **Kind chip** == "poi" with **Details**
> == "Pavilion" (category facet); the building Pavilion's **Source-tab File** == "aop_buildings.geojson"
> (never "unknown"), **Status** relabels `raw context`→"Raw context", **Confidence** passes off-vocab
> "medium" through; **0 console errors**. A Mason-binding assertion calls the shipped `rebake_canonical`
> kind lambda live (real class survives, else "poi"). Bake idempotent (proven by **byte-identical
> re-bake** — note: `--check` is a non-writing dry run, not itself an idempotency gate); feature counts
> unchanged; machine layers carry no `source_file`; trail #1 still "Launchpad". A1+A2+A3 verifiers still
> PASS (no regression); `node --check` clean; C1=0 non-comment `layerKey === '` branches; C6=0 `class`.
> **RESULT: PASS.**
>
> **Owed (user's git gate):** rides the same single `sw.js`/`#appVersion` bump + one commit as the Path A
> batch (`main.js` + `panel.js` + `rebake_canonical.py` + `_schema.json` + the named served `*.geojson`
> that gained `source_file` + the new A4 verifier + brain). Not committed; not bumped — reported.

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

> **A5 DONE — VERIFIED + COUNCIL FULL SIX CLEAR (2026-06-09).** Receipt:
> `../../output/council/shadow_a5_dispatch_20260609.md`. Pure-JS slice (no data change).
>
> **Shipped — five edge-dispatch sites converged onto declarative spec/node capabilities (C1):**
> - **`host-create-bridge-hardcodes-editorpois`.** `AOP_HOST_CREATE_FEATURE` dispatches through a
>   `spec.create` capability on `FEATURE_LIST_LAYERS` (was `if (layerKey !== 'editorPois') return null`).
>   editorPois declares `create: (geometry, opts) => addDrawnPoi(...)`; a layer without it returns null
>   (safe default, no throw — C1/R13). A future host-owned creatable layer just adds its own `create`.
> - **`visitor-list-source-chip-freestanding-map`.** `sourceChip` is a co-located spec field (R10) on the
>   four destination specs (editorPois→'drawn', brandLogos→'brand', visitorContext→'visitor', trails→
>   'trail'), read as `(spec && spec.sourceChip) || layerKey`; the free-standing `VISITOR_LIST_SOURCE_CHIP`
>   map is deleted.
> - **`panel-explicit-host-toggle-map`.** The sfwda node declares `hostToggle: 'showSfwda'`; the visibility
>   bridge reads `node.hostToggle` (safe default); the `EXPLICIT_HOST_TOGGLE` id-keyed map is deleted.
> - **`panel-userfeatures-source-special-casing`.** One `USER_FEATURES_SOURCE` constant + one
>   `usesUserFeatures(spec)` predicate replace the `=== 'userFeatures'` literal smeared across the
>   deriveItems reassignment skip / assign-into guard / `reassignable` / source-collect / bootEmbedded
>   add / syncCreated default / the MAP_DATA source decl. No call site names the literal.
> - **`panel-positional-synthetic-index-identity`.** `deriveItems` falls back to the canonical baked `id`
>   before the positional load `idx` (which survives only as a last-resort R13 default — no current
>   items-node reaches it, every one declares a `key`, so this is defensive hardening, not a live change).
>
> **Observable acceptance — PASS.** **Structural** (reading the shipped files): C1 = 0 non-comment
> `layerKey === '` branches, C6 = 0 `class`, the three dispatch maps gone, the capabilities present;
> `node --check` clean on both JS. **LIVE** (`mvp/scripts/playwright_verify_shadow_a5_dispatch.py` on
> `playwright_base.py`, **deterministic — 5/5 runs**): a "+ POI" create driven through the SAME host
> bridge the panel's commitFeature uses dispatches via `spec.create`, the feature LANDS in the editor-poi
> store (count 1→2, found, name==category=='Restroom'), a **non-creatable** layer ('buildings') returns
> null (safe default, no throw), the created feature is EDITABLE through the panel's edit bridge
> (`AOP_HOST_SET_FEATURE_PROPS` → the live source reflects the rename), and the panel editorPois Name input
> is live-editable (seed POI); 0 console errors. (The ★ Visitor-list chip + SFWDA toggle + userFeatures
> reassignment render into main.js's hidden `#editorTree` under embed, so those sub-changes are
> structural-only, stated as such — no narrated DOM check.) A1+A2+A3+A4 verifiers still PASS (no
> regression). A Witness flakiness andon (the original verifier's panel-select-of-bridge-created-feature
> step was a re-seed race) was folded: that step is replaced by the two deterministic editability checks
> above; Witness re-confirmed 5/5. **RESULT: PASS.**
>
> **Owed (user's git gate):** the LAST Path-A slice rides the same single `sw.js`/`#appVersion` bump + one
> commit as the whole batch (`main.js` + `panel.js` + the A1–A4 data/script + the 5 verifiers + brain).
> Not committed; not bumped — reported. **The loop is now at the Path A/B boundary; Path B (gold slice 6)
> is HELD for the user's pull.**

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
