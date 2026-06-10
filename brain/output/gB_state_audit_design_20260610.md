# G_B state audit + convergence design — demote localStorage to a working buffer

> **Read-only state audit.** No code, DB, or served-data change was made producing this doc.
> Slice: gold slice 6 **G_B** (Root 1 / C3 / F1) — `tasks/06_going_gold/gold_slice6_backlog.md`.
> Findings catalog: `tasks/09_editor_maturity/shadow_attributes_audit.md` (6 ids).
> Predecessors already landed: star path (`tasks/08_data_normalization/star_driven_poi_normalization.md`,
> council-cleared 2026-06-08) and **Approach-C** (2026-06-10) — the COLUMN home + one shared bake helper +
> both editor sinks column-aligned. This audit establishes the TRUE per-finding state on the CURRENT tree
> (line numbers verified post-Approach-C, which shifted them off the audit's pre-Approach-C cites) so the
> next agent implements only the genuinely-open gaps.

#aop #06_going_gold #slice6 #G_B #localStorage #C3 #state_audit #design

-----

## ✅ SHIPPED 2026-06-10 — the HIGH trio landed, COUNCIL FULL-SIX CLEAR

This was the design; it has since been implemented and council-cleared. So the per-finding statuses below now read as: **finding 3 (keystone) OPEN → DONE (G_B.1)** — the boot `edits`/property/geometry replay is demoted to staging-only in both `applyStoredOverrides` (panel.js) and `applyPositionedFeatures` (main.js, via an `opts.boot` gate on `BAKED_REFERENCE_LAYERS`), `created`/`deleted` kept; **finding 1 GAP A → DONE (G_B.3)** — `notes`→`description` fold + widened door eligibility (additive); **findings 2 + 4 (embedded) → DONE (G_B.2)** — reference panel edits + standalone ★ bridge through the existing `AOP_HOST_SET_FEATURE_PROPS` door (one store, one door). **GAP B (reference-geometry DB door) + findings 5 (visibility) / 6 (maturity) remain DEFERRED** (§4). Verified by observation: `mvp/scripts/playwright_verify_gB_localstorage_demotion.py` 17/17. Receipts: `council/gB_localstorage_demotion_20260610.md`. Read the rest of this doc as the original pre-implementation audit.

-----

## TL;DR for the next agent

- The **home exists** (Approach-C): CMFS spine lives in `core.features` COLUMNS; `export_publish_geojson.sh`
  reference arm serves `attrs || SPINE_JSONB` (columns win for the spine). Both apply scripts write spine→columns.
- The **write doors are mostly built**: `apply_positioned_features_to_core.py` already routes name/description/kind
  edits → columns AND highlight → attrs (Approach-C — its docstring lines 30-37 are STALE; the live code at
  lines 81-89/116-143/197-228 supersedes it). So **finding 1 is PARTIAL, not OPEN** — the write SINK is wired;
  what's open is `category`/`notes` mapping + the boot READ.
- The **keystone is still OPEN**: both boot replays — panel.js `applyStoredOverrides` (191-248, called 2208/2227)
  and main.js `applyPositionedFeatures` (3007-3030, called 8609/8679/8798/9110) — replay the localStorage diff
  over the served file at boot, so the published render = served file + per-browser diff. **This is the one real
  G_B job:** flip the boot READ to trust the baked file, demote the `edits`/`properties` replay to staging-only,
  KEEP `created`/`deleted` replay.
- **One genuine still-two-store gap:** the right-panel STANDALONE path and the right-panel reference-feature
  property edit still land in `aop_panel_overrides_v1`, which has **no reference DB door**
  (`apply_panel_overrides_to_core.py` writes `layer='poi'` ONLY). The embedded path is already unified
  (host bridge → positioned-features → DB).

-----

## 1. Per-finding status table

Each row: id · severity · **status** · code evidence (CURRENT tree) · what remains.

### Finding 1 — `served-features-edited-props-localstorage-only-no-db-door` · HIGH · **PARTIAL**

The orchestrator's question is answered: the read side + main() **DO** now pass name/notes/category/geometry
through to `set_clause` — but with two real gaps.

- **Write SINK = DONE.** `apply_positioned_features_to_core.py`:
  - `read_positioned_features` (92-103) reads the `positioned_features` map incl. `entry.properties`.
  - `build_sql` (197-239) detects `has_spine_edit = any(k in props for k in REF_COL)` (218) — a name/description/kind
    edit is in-scope **even with no star** (was star-only before Approach-C).
  - `entry_block`/`set_clause` (116-194) route `REF_COL = {name, description, kind}` → COLUMNS (124-127) and
    `highlight` + every other prop → `attrs` merge (129-142).
  - So a left-dock or panel name/description edit on a reference feature, exported in the bundle, **reaches the
    `name`/`description` COLUMN** and bakes through (`export_publish_geojson.sh` reference arm overlays SPINE_JSONB).
- **GAP A — `notes` and `category` are not mapped to columns.** The audit target is "Tier1 name/description
  (notes folds into description) + Tier3 category facet." But:
  - main.js writes the key `notes` (4691: `setFeatureProperty(layerKey, item.id, 'notes', ...)`) and `category`
    (Tier3 facet) into `positioned_features[...].properties`.
  - `REF_COL` only maps `name`/`description`/`kind`. So `notes`/`category` fall into the **attrs** merge (138),
    NOT the `description` column / a `category` facet column. They survive (additive, C5) but `notes` does not
    fold into `description`, and `category` is an attrs extra (acceptable per CMFS Tier3 = attrs facet, but the
    fold of `notes`→`description` the audit asks for is not done).
- **GAP B — geometry/icon_size are out of this sink by design.** Docstring 30-33 + `build_sql` 219 skip
  geometry/icon_size-only entries; they stay with the legacy file-baker `export_positioned_features.py`. The
  audit's "geometry" target for reference features is therefore NOT carried by this DB door.
- **GAP C (the real keystone) — the boot READ still replays.** Even with the sink wired, `applyPositionedFeatures`
  (main.js 3007-3030) replays `entry.properties` (3026 `Object.assign`) + geometry (3015) over served data at boot.
  So the edit's published truth is STILL the localStorage diff, not the baked column. Closing GAP C is finding 3.

**Remains:** map `category`→a Tier3 facet column or accept attrs; fold `notes`→`description`; decide geometry door
(reference geometry edits have no DB sink today); and the boot-read flip (finding 3).

### Finding 2 — `name-edit-two-store-fork-by-surface` · HIGH · **PARTIAL**

The two-store fork is **column-aligned but not single-door**. There are still two localStorage stores and two
DB doors, with one path that has NO reference DB door.

- **Left dock** (`main.js`): name → `setFeatureProperty('name')` (4664) → `persistFeaturePropertyChange` default
  (4900-4905) → `savePositionedFeature({properties:{name}})` → `aop_positioned_features_v1` →
  DB via `apply_positioned_features_to_core.py` (name→column). **Has a DB door now.**
- **Right panel EMBEDDED, reference layer:** `commitChange` (panel.js 145-171). The four reference nodes declare
  `hostKey` but **NOT `hostEdit`** (only editorPois has `hostEdit: true`, panel.js 756). So a reference name edit
  does NOT take the host-bridge branch (152) — it falls to `OVERRIDES.edits` (160-170) → `aop_panel_overrides_v1`.
  `apply_panel_overrides_to_core.py` writes `layer='poi'` ONLY (its docstring line 38: "Scope: the POI door").
  **So a panel-edited reference name has NO DB door — it stays browser-local.** ← still open.
- **Right panel STANDALONE (`!EMBEDDED`):** same `OVERRIDES.edits` path; same dead end.
- **Right-panel STAR is the exception that IS unified:** `toggleItemStar` → `hostHighlight` (panel.js 895-900)
  routes the four reference layers (embedded) through `AOP_HOST_SET_HIGHLIGHT` → positioned-features → DB.
  But standalone star still falls to `commitChange` → panel-overrides → dead end (see finding 4).

**Remains:** make the panel reference-feature property edit write through ONE door that reaches the DB. Either
(a) give the four reference nodes a `hostEdit`-equivalent bridge that routes name/description through
`AOP_HOST_SET_FEATURE_PROPS` (today that bridge calls `setFeatureProperty` → positioned-features, which DOES have
the DB door), or (b) teach `apply_panel_overrides_to_core.py` to write the reference layers. Path (a) reuses the
already-wired positioned-features door and collapses to one store of record per attribute — preferred (C6).

### Finding 3 — `panel-overrides-replayed-as-published-view` · HIGH · **OPEN** (the keystone)

Both boot replays are live and unchanged.

- **panel.js `applyStoredOverrides`** (191-248), called at boot 2208 (standalone) + 2227 (embedded). It:
  1. replays `created` into their source (211-224),
  2. replays `deleted` by filtering features out (227-235),
  3. replays `edits` — geometry (243) + `Object.assign(feat.properties, entry.properties)` (244) — over served
     features, then `s.setData(LOADED[src])` (247). The store comment (71-84) still says "no DB in prod… every
     value served from JSON… edit→localStorage diff→Export→baker."
- **main.js `applyPositionedFeatures`** (3007-3030) is the host-side twin: replays geometry (3015), highlight
  (3019), icon_size (3021), and `Object.assign` properties (3026) over each served reference collection at boot
  (called 8609/8679/8798/9110 inside `map.on('load')`). Same disease, host side.
- **Runtime debt discharged:** G0 observed the two-browser divergence live (`brain/output/g0_obs2_contextA_after_reload.png`
  vs `g0_obs2_contextB_fresh.png` — A renders "DIVERGENCE-TEST-EDIT", fresh B renders "Front Office"). Confirmed
  present on disk; no re-observation needed.

**Remains (the G_B core):** flip the boot READ so the served/baked file is the published source. The `edits`
(panel) / `entry.properties` + `entry.geometry` (main) replay must demote to **staging-for-export only** — kept
in the store and surfaced in the editor's own session, but NOT painted over the served `setData`/source at load.
`created` and `deleted` replays STAY (a drawn-not-yet-baked feature must show; an archived-not-yet-baked feature
must hide — there is no served-file truth for those until the next bake). See §3.

### Finding 4 — `highlight-two-store-by-surface` · MEDIUM · **PARTIAL** (embedded done, standalone open)

- **Embedded** (the production author path): the four reference layers route the ★ through
  `AOP_HOST_SET_HIGHLIGHT` (panel.js 895-900 → main.js 3736) → `setFeatureHighlight` →
  `savePositionedFeature({highlight})` → `aop_positioned_features_v1` → DB via
  `apply_positioned_features_to_core.py` (highlight→`attrs.highlight`). Left-dock ★ (`toggleFeatureHighlight`
  main.js 3701) uses the same store. **One store, one door — closed for the embedded/host case.** This is the
  star_driven_poi_normalization work (2026-06-08), and it bakes (`attrs.highlight` rides `attrs || SPINE_JSONB`).
- **Standalone / brand-logo**: `hostHighlight` returns false when `!EMBEDDED` (896) or no `hostKey`; the star
  then falls to `commitChange` → `OVERRIDES.edits` → `aop_panel_overrides_v1` (panel.js 919), which has no
  reference DB door and whose `applyStoredOverrides` replays its own copy (231-244 path replays `highlight`).
  Two browsers using the standalone panel disagree. (Brand logos are off the POI-tab axis by decision #3.)

**Remains:** the standalone reference ★ should route to the same positioned-features store, OR the panel-overrides
star for reference layers should reach the DB. Lower urgency than 1-3 because the production author flow is embedded
(the editor is the viewer); fold into the same one-door fix as finding 2.

### Finding 5 — `feature-visibility-paint-filter-as-curation` · LOW · **OPEN**

Unchanged from the audit (line numbers shifted: now 3287-3378).

- `buildFeatureListState` (3287-3318) overlays the per-id boolean from `aop_feature_visibility_v1` (3306-3310)
  on top of `group.defaultVisible(props)` — the default is a **code** default, not a baked attribute.
- `composeFeatureFilter` (3325-3333) builds `['in', idField, [...visibleIds]]` → `applyFeatureListFilters`
  (3353-3362) `map.setFilter`.
- `persistFeatureVisibility` (3367-3378) stores per-id booleans.
- No `core.features` column or attr holds default visibility; `is_destination` (DEFAULT false, init_db.sql:61)
  is a different axis (it's the curated-destination flag, not paint visibility).

**Remains:** a baked default-visibility attribute (a Tier3 `hidden`/`visible` facet in `attrs`, or reuse Tier2
`status`) so two browsers paint the same default set; transient un-ticks may stay a working buffer. Defer (LOW).

### Finding 6 — `maturity-tier-derived-from-panel-tree-position` · MEDIUM · **OPEN**

Unchanged (line numbers shifted ~).

- `nodeMaturity(node)` (panel.js 837-840) returns the panel NODE's `maturity` literal first (per-node literals at
  595/626/640/653/669/679/685/692), falling back to file `_meta.maturity` (840) — never a per-feature attribute.
- Read by the tier chip (1170) and the Source-tab Tier value (1457). So every feature under a node shows that
  node's single tier; it cannot vary per feature.
- No `core.features` column/attr for per-feature maturity; the served `_meta.maturity` is collection-level (carried
  forward by the bake, no DB home yet — the deferred `reference-bake-no-meta-on-fresh-volume` item).

**Remains:** a per-feature baked maturity attribute (Tier2 `status`/`confidence`, or a Tier3 `maturity` facet in
`attrs`); the node literal becomes a default. Defer (MEDIUM) — couples to the deferred `_meta`-on-fresh-volume item.

-----

## 2. Exhaustive store + flow map

Every localStorage store that touches a SERVED reference feature (buildings/cemeteries/visitor/trails). The four
served files are now baked from `core.features` COLUMNS+attrs (Approach-C); `rebake_canonical` no longer writes
them (evicted — `rebake_canonical.py:132-133` notes the four files are "NO LONGER re-baked here").

### Store A — `aop_positioned_features_v1` (main.js host store)

- **Key def:** `POSITIONED_FEATURES_KEY` (main.js:34). Map keyed `${layerKey}:${idField-value}`.
- **Carries:** `geometry`, `highlight`, `locked`, `icon_size`, and `properties:{name,label,notes,category,...}`
  (savePositionedFeature 2980-3002).
- **Writers (host surfaces):**
  - Left-dock name → `setFeatureProperty('name')` (4664) → default `persistFeaturePropertyChange` (4903) →
    `savePositionedFeature({properties:{name}})`.
  - Left-dock notes (4691) and any property field (4596/4603) → same default path.
  - Star → `toggleFeatureHighlight` (3701) → `savePositionedFeature({highlight})`.
  - Geometry move / lock / icon_size → `persistFeatureFlagChange` default (3851-3855) → savePositionedFeature.
  - **Embedded panel bridge writes here too:** `AOP_HOST_SET_HIGHLIGHT` (3736), `AOP_HOST_SET_FEATURE_PROPS`
    (3777 → setFeatureProperty → default → savePositionedFeature) for any `hostKey` layer — but in practice only
    editorPois calls SET_FEATURE_PROPS (it's the only `hostEdit` node); the four reference layers only call
    SET_HIGHLIGHT (star).
- **Boot read/replay:** `applyPositionedFeatures(layerKey, data)` (3007-3030), called per reference layer at
  8609/8679/8798/9110 inside `map.on('load')` — replays geometry + highlight + icon_size + properties over the
  freshly-fetched served collection, in place.
- **DB door:** `apply_positioned_features_to_core.py` (the "Export all" bundle's `positioned_features`):
  name/description/kind → COLUMNS, highlight + extras → `attrs`. **Exists, Approach-C.** Geometry/icon_size NOT
  carried (stays with legacy `export_positioned_features.py`).
- **Store-of-record column?** name/description/kind → COLUMNS yes; highlight → `attrs.highlight` yes; geometry →
  `geom` column exists but no DB door from this store; notes/category → fold to `attrs` only (no column mapping).

### Store B — `aop_panel_overrides_v1` (panel.js standalone/right-panel store)

- **Key def:** `OVERRIDES_KEY` (panel.js:85). Shape `{schema, edits:{}, created:[], deleted:[]}` keyed `source:id`.
- **Carries (edits):** `EDITABLE_SERVED_KEYS = [name, description, difficulty, notes, category, tag, highlight]`
  (panel.js:90) via `pickEditable` (117-121), plus optional `geometry`.
- **Writers:**
  - `commitChange` (145-171): a reference (non-hostEdit) feature edit → `OVERRIDES.edits[src:id]` (160-170).
  - editorPois (hostEdit) → bridges to host (152-158), NOT this store.
  - User-drawn features → `created` via `syncCreated` (128-142).
  - `toggleItemStar` standalone / no-hostKey → `commitChange` (919) → edits store.
  - `persistDelete` (172-187) → `OVERRIDES.deleted`.
- **Boot read/replay:** `applyStoredOverrides` (191-248), called 2208 (standalone) / 2227 (embedded) — replays
  created (211-224), deleted (227-235), edits properties+geometry (237-246), then `setData`.
- **DB door:** `apply_panel_overrides_to_core.py` — but **`layer='poi'` ONLY** (docstring:38). So `created` POIs +
  POI edits reach the DB; **reference-layer edits in this store reach NO DB door.** This is the finding-2 dead end.
- **Store-of-record column?** For POI rows: name/description/kind → POI_COL columns. For reference rows in this
  store: none (no reference door).

### Store C — `aop_feature_visibility_v1` (main.js host store)

- **Key def:** `FEATURE_VISIBILITY_KEY` (main.js:35). Map `layerKey → {idValue: boolean}`.
- **Writer:** `persistFeatureVisibility` (3367-3378).
- **Boot read:** `buildFeatureListState` (3287-3318) overlays per-id boolean on `group.defaultVisible(props)`;
  `composeFeatureFilter` (3325) builds the paint filter; `applyFeatureListFilters` (3353) applies it.
- **Bake carries:** nothing — there is no served default-visibility attribute. (`is_destination` is a separate
  curation axis.)
- **DB store-of-record column?** None. Default visibility lives only in code (`group.defaultVisible`). OPEN (finding 5).

### Store D — `aop_feature_tags_v1` (main.js host store) — context only, NOT a G_B finding

- **Key def:** `FEATURE_TAG_KEY` (main.js:36). Per-feature `#tag` bindings.
- **Status post-G_E (2026-06-10):** demoted to an **override** — `hostResolveTagCoords` (main.js 6299-6302) fills
  a tag's coordinate ONLY when the baked document has none; baked coordinates WIN (comment 6292-6298). The event
  anchor (#pavilion) now carries baked geometry. So this store is already a working buffer, not published truth —
  the audit's `event-anchor-position-from-localstorage-tag-binding` is CLOSED by G_E, not part of G_B's six.
  Mention only so the next agent does not re-touch it.

### Panel reference rows read the SERVED file

`refItems(...)` nodes (panel.js 604/643/656/...) derive list rows from `LOADED[source]` — the fetched served
collection — AFTER `applyStoredOverrides` mutates it. So the panel render is served-file-plus-replay, exactly the
finding-3 symptom.

-----

## 3. The convergence design

### One store of record per attribute (the home)

| Attribute | Home (store of record) | How it bakes |
|---|---|---|
| name | `core.features.name` COLUMN | SPINE_JSONB overlay (reference arm) / projection (publish arm) — DONE |
| description (incl. folded notes) | `core.features.description` COLUMN | same — DONE for description; **notes→description fold is the open bit** |
| kind | `core.features.kind` COLUMN | same — DONE |
| category (Tier3 facet) | `core.features.attrs.category` | rides `attrs` verbatim — works as attrs today |
| highlight (★) | `core.features.attrs.highlight` | rides `attrs` verbatim — DONE (star_driven) |
| geometry | `core.features.geom` COLUMN | served via `ST_AsGeoJSON(geom)` — **but no DB door from the editor for reference geometry** |
| default visibility | NEW: `core.features.attrs.<hidden|visible>` (Tier3) OR reuse `status` | needs a bake/attr add — DEFER (finding 5) |
| maturity tier | NEW: `core.features.attrs.maturity` (Tier3) OR `status`/`confidence` | needs a bake/attr add — DEFER (finding 6) |

The spine home is already COLUMNS (Approach-C). No new column is needed for the HIGH trio — name/description/kind
columns exist and bake. `category` already works as an `attrs` facet. The only NEW `core.features` additions are
for the DEFERRED low/medium pair (visibility-default, maturity).

### One write door per attribute

- **Spine (name/description/kind) + star:** ONE door = `apply_positioned_features_to_core.py` (already routes
  spine→columns, star→attrs). The convergence move is to make the **right-panel reference edit feed this same
  store** instead of `aop_panel_overrides_v1`. Concretely: give the four reference nodes a host bridge for
  property edits (route through `AOP_HOST_SET_FEATURE_PROPS`, which already lands in positioned-features → the
  one door), mirroring how the ★ already bridges via `AOP_HOST_SET_HIGHLIGHT`. That collapses Store B's
  reference-edit role into Store A and closes findings 2 + 4. (Standalone panel, with no host, keeps a local
  buffer that exports through the positioned-features bundle, not a second DB door.)
- **POI features:** keep `apply_panel_overrides_to_core.py` (`layer='poi'`). Unchanged.

### The boot-read flip (the keystone — finding 3)

The published READ must be the baked served file; localStorage becomes a staging-only export diff.

- **main.js `applyPositionedFeatures` (3007-3030):** at boot, STOP replaying `entry.geometry` (3015) and
  `entry.properties` (3026) over the served data for the four reference layers. KEEP replaying nothing that
  represents an attribute the bake now owns. The store still holds the diff (for "Export all" → the DB door) and
  the editor's own in-session edit still mutates the live feature (the editor IS the viewer — an edit-in-progress
  shows for the author), but a STALE diff from a prior session must not override the baked truth on load.
  - Practically: gate the property/geometry replay so it does not fire at boot for served reference layers (the
    served file is now authoritative), while the live edit path (setFeatureProperty mutating the in-memory
    feature) continues to update the current session. `highlight`/`locked`/`icon_size` replay: `highlight` is now
    baked too (attrs.highlight) so it also should read from the served file, not the store; `locked`/`icon_size`
    are pure view-state with no DB home and may stay buffer-replayed.
- **panel.js `applyStoredOverrides` (191-248):**
  - **DEMOTE to staging:** step 3, the `edits` replay (237-246) — properties + geometry on SERVED features. Do
    not `Object.assign`/`setData` these over the served collection at boot. The store keeps them for "Export
    edits"; the editor surfaces them only in the active editing session.
  - **KEEP:** step 1 `created` (211-224) — a drawn feature not yet baked has no served truth, must still show.
  - **KEEP:** step 2 `deleted` (227-235) — an archived feature not yet re-baked must still hide.
- **main.js equivalents that STAY:** the editorPois store (`aop_editor_pois_v1`) is the host's own
  source-of-record for drawn POIs (not a served-reference replay) — out of scope, unchanged. The
  `created`/`deleted` equivalents for drawn features stay.

### New columns/attrs needed (deferred sub-slice)

- **visibility-default (finding 5):** add an `attrs` facet (e.g. `attrs.published_default` / a Tier3 `hidden`
  boolean) baked into the served file; `group.defaultVisible` reads `props.<facet>` instead of a code literal.
  Transient un-ticks may remain a working buffer.
- **maturity (finding 6):** add a per-feature `attrs.maturity` (or promote to `status`/`confidence`); the bake
  emits it; `nodeMaturity` reads the feature value first, node literal as fallback. Couples to the deferred
  `reference-bake-no-meta-on-fresh-volume` item (the `_meta` DB home).

-----

## 4. Recommended sub-slice boundary

**First G_B slice (council-reviewable) — the HIGH trio, read-path-first:**

1. **G_B.1 — the keystone read-path flip (finding 3).** Demote the boot `edits`/`properties`/`geometry` replay in
   BOTH `applyStoredOverrides` (panel.js 237-246) and `applyPositionedFeatures` (main.js 3015/3026 for served
   reference layers) to staging-only; KEEP `created`/`deleted`. This alone makes the published render trust the
   baked file. **Do this FIRST** — it is the slice's reason to exist and it is the one with a live observed symptom
   (g0_obs2). It is additive in spirit (C5): no row dropped, the diff still exports.
2. **G_B.2 — one write door for reference name/description (findings 2 + 4 standalone).** Bridge the four reference
   nodes' property edits + standalone ★ through the host's positioned-features door (the one that already reaches
   the DB), so a panel rename no longer dead-ends in `aop_panel_overrides_v1`. Reuses the existing bridge pattern
   (`AOP_HOST_SET_FEATURE_PROPS` / `AOP_HOST_SET_HIGHLIGHT`) — no new store, no second door (C6).
3. **G_B.3 — finish the spine fold in the door (finding 1 GAP A).** Fold `notes`→`description` and decide
   `category` (attrs facet is acceptable per CMFS Tier3; if a column is wanted, add it additively). Small.

**Dependency order:** G_B.1 → G_B.2 → G_B.3. G_B.1 is independent and highest-value; G_B.2 depends on nothing but is
cleaner to verify after G_B.1 (so the verifier proves "panel rename now bakes AND a stale diff no longer overrides").
G_B.3 is a small follow-on to the door touched in G_B.2.

**Defer to a follow-up G_B slice:**
- **finding 5 (visibility-default, LOW)** — needs a new bake attr; on the working-buffer-vs-truth boundary; F1 kept
  it as a paint filter intentionally.
- **finding 6 (maturity, MEDIUM)** — needs a per-feature attr + couples to the deferred `_meta`-on-fresh-volume
  (G_A's open `reference-bake-no-meta-on-fresh-volume` item). Do it WITH that item.

**Keep additive (C5) / one-home-one-writer (C6).** No CHECK/enum/validator; an unknown key still renders; the diff
still exports.

**Irreversible/destructive flags for the user's gate:**
- The DB is **down (docker daemon)** and `core.features` carries **~153 live-only rows** (F5 / G_D). G_B is a
  CODE+read-path change — it should NOT require a `down -v` or a fresh-volume rebuild. **Flag:** do NOT run G_D's
  fresh-volume teardown as part of G_B. Snapshot the DB before any apply round-trip (mirror the Approach-C
  caution). The boot-read flip itself is reversible (it's a JS gate); the only owed user gate is the standard
  `vNN` bump + commit for the shell-asset/served-data change.
- No hard-delete anywhere; `deleted` replay stays and the DB door archives (`archived_at`), never DROPs.

-----

## 5. Verification plan (by observation, lean — no networkidle)

Tile-independent DOM on `mvp/scripts/playwright_base.py` against the local server (:8001), psql, and
`export_publish_geojson.sh --check`. Prove the published render no longer depends on localStorage.

1. **Baked edit shows on a FRESH browser (positive).** Apply a name edit to a reference feature via the DB door
   (`apply_positioned_features_to_core.py` on a one-entry bundle) → `export_publish_geojson.sh` → bake. Open the
   viewer in a **clean profile (empty localStorage)** and assert via live DOM that the reference feature's row
   label / dock title reads the baked name (e.g. the trail shows "Launchpad"), with 0 console errors. This proves
   the published READ is the served file, not a per-browser store. Restore the served files to HEAD after
   (read-only `git show HEAD:… > …`) and revert the DB test row (snapshot restore), per the star_driven Slice-B
   discipline.
2. **Stale localStorage diff no longer overrides the baked truth (negative — the keystone).** Seed a clean
   profile's `aop_positioned_features_v1` (and `aop_panel_overrides_v1`) with a STALE edit for a reference feature
   (e.g. name "STALE-DIFF") whose served value is the baked truth. Reload. After G_B.1, assert the DOM renders the
   **baked** name, NOT "STALE-DIFF" — the boot replay no longer paints the diff over the served file. (Before
   G_B.1 this is the g0_obs2 divergence; after, it must be gone.) Do this for BOTH panel.js modes (embedded via
   index.html and standalone via right_panel.html) since both call the replay (2208/2227).
3. **`created`/`deleted` still replay (regression guard).** With a stale-diff store that ALSO carries a `created`
   drawn feature and a `deleted` key, assert the created feature still shows and the deleted one is still hidden —
   confirming we demoted only the `edits` replay, not the created/deleted ones.
4. **Two-browser agreement (closes the F1 symptom).** Edit→bake→deploy locally; open two clean profiles; assert
   both render the same reference name/★ for the same feature/URL — the divergence g0_obs2 captured is gone.
5. **Bake purity unchanged.** `export_publish_geojson.sh --check` → "NO REVERT" (every served file byte-identical
   to a fresh bake) after the round-trip, proving the column-as-home bake still a pure function and no served file
   silently drifted. (Note the pre-existing exit-1-only-on-events drift is resolved post-G_E; expect clean.)
6. **psql store-of-record check.** After the apply, `SELECT name, attrs->>'highlight' FROM core.features WHERE
   source_key=…` shows the edit in the COLUMN and the star in attrs — the one home, the one door.

Keep the Playwright runs SHORT (one viewer smoke, hook `window.AOP_HOST_MAP` + the load event, assert DOM row
labels directly — no `networkidle`, no `queryRenderedFeatures`); three prior Approach-C agents hit the 600s stall
on heavy runs.

-----

## References (treat as the thing)

- `tasks/06_going_gold/gold_slice6_backlog.md` — G_B section + the Approach-C/G_E status log.
- `tasks/09_editor_maturity/shadow_attributes_audit.md` — the 6 finding ids (verbatim entries lines 150-159).
- `tasks/08_data_normalization/star_driven_poi_normalization.md` — what the star path already did (finding 4 embedded).
- `northstar/editor_architecture_contracts.md` — C3 (curation is data), C5 (no limiting), C6 (one home/one writer).
- `research/common_feature_schema.md` — CMFS Tier1 (id/title/description/kind) / Tier2 (provenance) / Tier3 (facets).
- `mvp/scripts/apply_positioned_features_to_core.py` · `apply_panel_overrides_to_core.py` · `export_publish_geojson.sh`
  — the two doors + the one bake (Approach-C state).
- `website/js/main.js` (3007 applyPositionedFeatures · 3287-3378 visibility · 3736-3831 host bridges · 4900 default
  property sink) · `website/js/panel.js` (191-248 applyStoredOverrides · 145-171 commitChange · 837-840 nodeMaturity).
- `brain/output/g0_obs2_*` — the observed two-browser divergence (C4 debt discharged).
