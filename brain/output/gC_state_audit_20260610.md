# G_C (collapse identity forks) — state audit + canonical-id design — 2026-06-10

> Slice G_C of `tasks/06_going_gold/gold_slice6_backlog.md` (highest-risk: changes
> the IDENTITY published features match on). This doc is STATE-AUDIT FIRST: per
> finding, what is ALREADY done vs genuinely open, with live evidence (served files
> + `core.features` + the editor id-matching paths), then the canonical-id scheme,
> BEFORE any code change. Snapshot before any DB write:
> `/tmp/aop_db_snapshots/aop_map_pre_gC_selfsnapshot_20260610.sql`.

#aop #06_going_gold #G_C #identity #state_audit #design

-----

## Observed current state (the inputs, read 2026-06-10)

### Served `id` per layer (= `attrs->>'id'` for the 4 reference layers; F4 made publish id = source_key)

| layer | served `id` | unique? | DB `source_key` | host `spec.idField` | panel select `spec.key` | panel persist key |
|---|---|---|---|---|---|---|
| cemeteries | `parcel_id` (e.g. `093 001.02`) | **NO** (twin shares it; `093 001.02` ×2) | `cemeteries:<parcel_id>:<geom_role>` (8 distinct) | `parcel_id` | `p.name` | `props.id` |
| buildings | FEMA UUID `{a006e8…}` | yes (5) | `buildings:<build_id>` (e.g. `buildings:3396032`) | `build_id` | `p.build_id` | `props.id` |
| trails | `sfwda-N` load index | yes (120) | `trails:sfwda-N` | `__trail_row_id` (`n:<num>`/`name:<name>`) | (host derived) | `props.id` |
| visitor | `aop_badge` / `…-0` | yes (4) | `visitor:<id>` | split: `name` (callout) / `logo_id` (logo) | `p.name`\|`p.label` | `props.id` |
| publish | `<layer>:<source_key>` (e.g. `editorPois:aop-pavilion`) | yes (6) | `source_key` | n/a (publish-data node) | `p.id` | `p.id` |

The invariant the card wants: **`spec.idField == panel key == DB source_key`** for every layer.
Today they DIVERGE on every reference layer — the host reads `parcel_id`/`build_id`/`__trail_row_id`/`name`,
the panel persists on `props.id`, and the served `id` is a THIRD value (parcel_id / UUID / sfwda-N).

### The cemetery twin (verified)
`aop_cemeteries.geojson` = 8 features = 4 sites × (parcel Polygon + marker Point), each pair sharing one
`id`==`parcel_id`. `093 001.02` appears twice (Tate parcel + Tate marker) — the non-unique id. The host
dedupes by `parcel_id` keeping the FIRST (the parcel) → a star/edit on a cemetery resolves to the PARCEL twin,
while the destination LIST + panel surface the MARKER (geom_role filter). DB already stores them as TWO rows
with distinct `source_key` (`…:parcel` / `…:marker`), both `archived_at IS NULL`.

### Ellis cemetery across files (verified)
- `aop_cemeteries.geojson`: parcel_id `110 008.04` (parcel + marker, id `110 008.04`).
- `publish.geojson`: `park_boundaries:ellis-inholding` (name "Ellis Cemetery (inholding parcel)", kind `cemetery`)
  AND `editorPois:ellis-cemetery` (name "Ellis Cemetery", kind `cemetery`).
- So 4 representations, 3 distinct id namespaces; no surface links them.

### publish kind taxonomy (verified)
`publish.geojson` kinds: `editorPois:aop-pavilion` kind=`pavilion`, `editorPois:ellis-cemetery` kind=`cemetery`,
`park_boundaries:ellis-inholding` kind=`cemetery`. `pavilion`/`cemetery` are NOT in the controlled `kind` list.

### Both editor sinks (verified — Approach-C already unified)
- `apply_panel_overrides_to_core.py`: `POI_COL = {name,description,kind}` → COLUMNS.
- `apply_positioned_features_to_core.py`: `REF_COL = {name,description,kind}` → COLUMNS (identical), extras+highlight → attrs.
- `export_publish_geojson.sh`: ONE shared `SPINE_COLS="name description kind confidence permission status"`; both arms read the spine from COLUMNS (publish: explicit projection; reference: `attrs || SPINE_JSONB`).

-----

## Per-finding: already-done vs genuinely-open

| # | finding | status | evidence |
|---|---|---|---|
| 5 | `two-editor-sinks-opposite-homes` | **ALREADY DONE (Approach-C)** | `POI_COL` == `REF_COL` == columns; one `SPINE_COLS`; both bake arms read columns. Nothing to redo. |
| 4 | `buildings-served-id-is-attrs-businesskey-not-pk` | **OPEN** | served id = FEMA UUID, but source_key business key = `build_id`; the two ids disagree. Reference arm serves attrs.id (UUID), publish arm would serve source_key — two id semantics. (No building is in the publish gate today, so no live publish-arm building, but the SEMANTICS still fork.) |
| 1 | `served-id-heterogeneous-no-canonical-key` | **OPEN** | host idField ≠ panel key ≠ served id ≠ source_key on every reference layer. No single canonical `id`. |
| 2 | `cemetery-parcel-marker-twin-nonunique-id` | **OPEN** | served `id` non-unique (twin shares parcel_id); host resolves to parcel, list/panel to marker. |
| 3 | `ellis-cemetery-multi-id-across-files` | **OPEN (data/curation)** | 4 representations, no cross-link. |
| 6 | `publish-kind-taxonomy-fork` | **OPEN** | `pavilion`/`cemetery` off the controlled kind list in publish.geojson. |

Pre-existing known issue (G_meta flagged): `aop_buildings.geojson` is the lone `--check` DRIFT — **order-only**
(reference-arm SQL has no `ORDER BY`; same 5 ids, reordered). The card invites closing it here since we touch
buildings identity. Confirmed order-only: the unordered DB SELECT and the served file carry the same 5 UUIDs in
different order.

-----

## The canonical-id scheme (settled before touching code)

**Principle.** The DB `source_key` is ALREADY the canonical stable business key per layer
(`<layer>:<businesskey>[:<role>]`, UNIQUE-constrained, survives a fresh-volume PK renumber — F4 proved it for
publish). The served `id` must become the **business-key portion of that source_key** — i.e. the part the editor
keys on, equal across host idField / panel key / DB. We do NOT change `source_key` itself (it's the DB invariant
and the publish id). We make the SERVED `id` and the editor's `idField`/panel-key resolve to the same value.

Per layer, the canonical served `id` (and the value host+panel match on):

| layer | canonical served `id` | = source_key business part? | unique? |
|---|---|---|---|
| cemeteries | `<parcel_id>:<geom_role>` (e.g. `093 001.02:marker`) | YES (drops the `cemeteries:` layer prefix) | YES (8) |
| buildings | `<build_id>` (e.g. `3396032`) | YES | YES (5) |
| trails | `sfwda-N` (the existing load index) | YES | YES (120) |
| visitor | existing `id` (`aop_badge`/`…-0`) | YES (already == business key) | YES (4) |
| publish | `<layer>:<source_key>` (unchanged, F4) | YES | YES (6) |

Why these, against the card's literal targets:
- **trails: `sfwda-N`, NOT `trail_number`.** The card target says trail_number, but trail_number is NULL on 33
  of 120 edges and only 88 distinct — it CANNOT be a unique key. `sfwda-N` (the existing served id == source_key
  business part) is unique 120/120 and is already the DB source_key. The card's intent ("a stable business key
  per layer") is satisfied by sfwda-N; trail_number stays a Tier3 facet. (The host's `__trail_row_id` derive
  stays — it is the DEDUP key for collapsing multi-edge trails into one directory row, a separate concern from
  the per-feature canonical id. The canonical `id` field is added/kept on every feature; `__trail_row_id` is the
  list-dedup view over it. We leave the host trail machinery UNTOUCHED — changing it is out of scope and the
  highest-risk regression; the trail served id is already canonical.)
- **buildings: `build_id`, NOT the UUID and NOT the serial PK.** `build_id` is the source_key business key. The
  served id today is the UUID; we re-point the served `id` to `build_id` and align the host idField (already
  `build_id`) + panel key (already `build_id`). The UUID survives in attrs as `uuid`/`attrs.id`-equivalent
  (additive, nothing dropped).
- **cemeteries: `<parcel_id>:<geom_role>`.** This makes the served id UNIQUE per feature (collapses the twin
  non-uniqueness) while keeping both geometries served. The host idField moves from `parcel_id` → `id` so the
  host resolves the MARKER (matching the list/panel), and `geom_role` becomes a Tier3 facet + the list filter
  moves to the spec (already is `listPredicate`).

**The cemetery twin (finding 2): ARCHIVE not collapse-by-delete.** The card says collapse to ONE store-of-record
row (the marker) with the parcel as related geometry, ARCHIVE the redundant identity (`archived_at`), never
hard-delete. DECISION: the bake/render REQUIRES the parcel polygon (cemetery-fill/outline paint on it) AND the
marker point (cemetery-marker/label) — both must keep being SERVED. So the "one record" is achieved at the
EDITOR-IDENTITY level (host idField=`id`, the marker is the row-of-record, the parcel is its related geometry,
`geom_role` is a facet), NOT by removing the parcel from the served file. The redundant IDENTITY being archived
is the **non-unique shared id** — by giving the two rows DISTINCT canonical ids (`:parcel`/`:marker`) the twin
no longer shares one id. To honor the literal "archive the redundant identity row" with an `archived_at`
audit trail WITHOUT losing the served parcel geometry, we ARCHIVE the parcel row's editor-DESTINATION identity:
the parcel row stays in core.features and stays served (geometry), but is marked so it is not the
star/edit/list store-of-record — recorded via an additive `archived_at` stamp is NOT appropriate (that would
drop it from the bake's `archived_at IS NULL` gate and LOSE the served parcel geometry).

→ **Resolved approach (loss-free):** do NOT set `archived_at` on the parcel (that gate-drops its served
geometry — a loss). Instead the twin is collapsed at the IDENTITY layer: distinct canonical ids end the
non-unique-id bug; the host idField=`id`+marker-of-record makes the marker the single store-of-record row; the
parcel is "related geometry" (same site, served, paints the polygon). The `archived_at` mechanism is reserved
for a TRUE redundant row with no served purpose. Since both geometries are required on the map, neither is
redundant-to-drop. This is the honest reading of "collapse to one record with the parcel as related geometry":
one IDENTITY (the marker), two geometries (marker + related parcel), zero served loss. Flagged for the council.

**Ellis (finding 3):** cross-layer link is a DATA/curation fact, not a schema mechanism. The canonical link is
the shared real-world identity. Additive approach: stamp the publish Ellis representations + the cemeteries
Ellis with a shared `same_as` facet referencing the canonical cemetery id (`110 008.04:marker`), so a surface
CAN know they are one place, without minting/merging (which would drop a representation a layer needs). Never
hard-merge (each representation paints a different layer).

**publish kind (finding 6):** map known kinds to the controlled list at the bake, pass unknown through (C5/C6).
`pavilion` → `poi` (+ `category: pavilion` facet); `cemetery` → `poi` (+ `category: cemetery` facet) for the
poi-layer rows; the `park_boundaries` Ellis stays `cemetery` is its DOMAIN kind on a boundary — but kind on a
boundary layer is the layer kind; leave non-poi rows' kind as-is (pass through), map only the controlled set.
A KIND_MAP `{pavilion: poi, cemetery: poi}` applied where a controlled `kind` is expected, original preserved
as `category` facet. Never throw on an unknown kind.

-----

## Implementation plan (genuinely-open work only; finding 5 skipped — already done)

1. **Bake: serve a canonical `id` = source_key business key on the 4 reference layers** (finding 1+2+4).
   In `export_publish_geojson.sh` reference arm, OVERLAY `id` = the business-key portion of `source_key`
   (strip the `<layer>:` prefix) on top of attrs, so the served `id` is canonical and unique. This makes
   cemeteries `id`=`<parcel_id>:<geom_role>` (unique), buildings `id`=`<build_id>`, trails `id`=`sfwda-N`
   (unchanged), visitor `id` unchanged. Additive: the prior attrs id (UUID for buildings, bare parcel_id for
   cemeteries) is preserved under its own attrs key (`uuid`/`parcel_id`/`attrs.id` already present).
2. **Host: cemeteries idField `parcel_id` → `id`** (finding 2) so the host resolves the MARKER (the
   store-of-record), matching the list/panel; `geom_role` stays the list filter (already spec). Add the
   per-feature canonical id consistently. Keep buildings idField `build_id` (now == served id). Trails/visitor
   host untouched (already canonical).
3. **publish kind map** (finding 6): a KIND_MAP at the bake, known→poi+category facet, unknown passes through.
4. **Ellis same_as facet** (finding 3): additive cross-link facet on the publish Ellis rows + cemeteries Ellis.
5. **buildings deterministic ORDER BY** (closes the pre-existing order-only `--check` DRIFT) in the reference arm.
6. VERIFY BY OBSERVATION: live editor still resolves the RIGHT single feature for cemetery / building / trail /
   publish; star/edit one and confirm it lands on the correct single feature and round-trips (not the twin).
7. Loss-free semantic diff vs HEAD (only intended id/kind/geom_role-facet/same_as changes); `--check`.

-----

## WHAT WAS DONE (implemented + verified 2026-06-10)

**Code/data changes (all additive, loss-free):**
- `mvp/scripts/export_publish_geojson.sh`:
  - reference arm: overlay `id = regexp_replace(source_key,'^layer:','')` (canonical id == source_key business part) + `ORDER BY source_key` (closes the pre-existing buildings order-only `--check` DRIFT).
  - publish arm (Python wrapper): `POI_KIND_MAP={pavilion:poi,cemetery:poi}` maps `layer='poi'` rows' specific-class kind → `poi` + a `category` facet (known→map, unknown→pass through, C5/C6); `same_as` cross-link stamped on the two Ellis publish ids → the canonical cemetery marker `110 008.04:marker`.
- `website/js/main.js`: cemeteries `idField: 'parcel_id' → 'id'` (the canonical unique id), and the THREE cemetery map-click/search reveal bindings re-pointed from `props.parcel_id` → `<parcel_id>:marker` (the canonical marker id, the store-of-record row).
- `mvp/scripts/apply_positioned_features_to_core.py`: cemetery DB-door resolver handles the new canonical key (`source_key = 'cemeteries:'+fid` when fid has a `:role`; legacy bare parcel_id still falls back to the marker — no buffered ★ lost).
- DB (additive, +2 rows touched, 0 inserts/deletes/archives): reciprocal Ellis `same_as = editorPois:ellis-cemetery` on the 2 cemetery Ellis rows (bakes through the attrs overlay). Snapshot first; DB still 160/159.
- New verifier `mvp/scripts/playwright_verify_gC_identity.py`.

**Per-finding outcome:**
1. `served-id-heterogeneous-no-canonical-key` — DONE. Served `id` == DB source_key business part on all 4 reference layers (live-verified: per-layer served-id set == DB business-key set).
2. `cemetery-parcel-marker-twin-nonunique-id` — DONE. Served ids now UNIQUE (`<parcel_id>:<geom_role>`); host idField=`id` resolves the MARKER store-of-record. **Archive decision (loss-free, flagged for council):** the redundant *identity* (the shared non-unique id) is collapsed by giving parcel+marker DISTINCT ids — NOT by setting `archived_at` on the parcel, which would gate-drop its served polygon geometry (a real loss; the cemetery-fill/outline paint it). Both geometries stay served; the marker is the single identity-of-record, the parcel is its related geometry. No hard-delete, no geometry loss.
3. `ellis-cemetery-multi-id-across-files` — DONE. Bidirectional `same_as` links the 4 Ellis representations to the canonical cemetery marker / its publish poi. Additive; no hard-merge (each representation paints a different layer).
4. `buildings-served-id-is-attrs-businesskey-not-pk` — DONE. Served `id` UUID → `build_id` (== source_key business key, stable, not the serial PK); UUID preserved in `attrs.uuid`. Both bake arms + the editor now use one id semantics.
5. `two-editor-sinks-opposite-homes` — ALREADY DONE (Approach-C); verified, not redone (`POI_COL`==`REF_COL`==columns, one `SPINE_COLS`, both arms read columns).
6. `publish-kind-taxonomy-fork` — DONE. `pavilion`→`poi`+category facet; `cemetery` (poi-layer dup)→`poi`+category; unknown/other kinds pass through; never throws.

**Verifications (observed):**
- `playwright_verify_gC_identity.py`: ALL PASS — incl. the KEY live-editor test: a cemetery ★ lands on EXACTLY ONE store key `cemeteries:093 001.02:marker` (the marker, not the parcel twin — no smear); a building edit lands on `buildings:3397585` (canonical build_id); 0 console errors.
- Real DB-door round-trip: a star bundle with the canonical cemetery key resolved to the marker only (parcel untouched), building name edit landed in the COLUMN; then test mutations undone (DB back to 160/159, Ellis same_as kept).
- F4 verifier: PASS (publish.geojson still reproducible; the Ellis park_boundary still resolves in the editor by source_key; 0 errors).
- refbake verifier: the only FAIL is the pre-existing G_meta `+maturity` add (120 adds = the `maturity` key; HEAD lacks it) — NOT a G_C regression; all G_C-relevant assertions (eviction, `--check` NO REVERT, viewer counts, Launchpad/Pavilion, 0 errors) PASS.
- Loss-free semantic diff vs HEAD (matched on stable identity): only intended `id`/`kind`/`category`/`same_as` (+ G_meta `maturity`); 0 features missing/added, 0 geometry change, 0 unexpected key change.
- `export --check`: NO REVERT on all 6 files (pure function; buildings order-only drift now closed).
- `node --check` main.js + panel.js: OK.
