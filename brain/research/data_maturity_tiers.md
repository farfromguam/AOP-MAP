# Data maturity tiers (gold / silver / …)

TL;DR:
- Every served data file carries a **maturity tier** — a per-file review-state
  label that lives in its top-level `_meta` (`maturity` · `group` · `locked`).
- The tiers are `gold` · `silver` · `editor` · `derived` · `reference`. Only
  `gold` and `silver` are curated first-party data; they ship **locked** (unlock
  in the editor to change existing features; you can always *add* new ones).
- Maturity is a THIRD axis, orthogonal to provenance (`source`, a per-feature
  CMFS field) and to the source-register zones (`raw → core → publish`). Don't
  collapse the three.
- Stamped by `mvp/scripts/stamp_maturity.py` (runs LAST in the data pipeline);
  read by the right panel (`website/js/panel.js`) to group + badge the editor.

#aop #data #maturity #gold #silver #schema #editor #provenance

-----

## Why a tier at all (user, 2026-06-05)

> *"we have different data types. raw, baked, source, gold… we get things,
> mutate for our needs, cut, and produce a final data set. only current dataset
> that is gold is trails. region callouts are silver, pending text review. gold
> data is not un-editable — it's just locked. unlock it first. gold data should
> share a common schema; this should power our editor."*

The repo already had the maturity *spine* — it just wasn't named or generalized:
the trail network carried a self-describing gold `_meta` block
(`export_gold_trail_network.py`), `website/data/raw/` held pristine originals,
and `rebake_canonical.py` baked everything into the [[common-feature-schema]].
This doc names the missing axis and makes it uniform across files.

## The three axes (keep them separate)

The earlier instinct was a single ladder "raw → baked → source → gold." That
mixes three different things. They are orthogonal:

| Axis | Question | Where it lives |
| --- | --- | --- |
| **Maturity tier** | How reviewed/curated is this *file*? | file `_meta.maturity` (this doc) |
| **Provenance** | Where did this *feature* come from / how trusted? | per-feature CMFS `source`/`confidence`/`permission` |
| **Source-register zone** | Is it inspection (`raw`), edited (`core`), or publishable (`publish`)? | `northstar/source_register.md` |

`source` is **not** a rung on the maturity ladder — it is the provenance axis.
A `gold` file is still made of features that each carry their own `source`.

## The tiers — MEDALLION (user, 2026-06-14)

> *"rename all our data sources to bronze / silver / gold. ellis cemetery made it
> from bronze to gold. no other cemeteries did. same with park buildings — only 5
> made it. others did not."*

The earlier 6-rung ladder (`gold/silver/editor/derived/reference`) collapsed into
the industry-standard **medallion**: a promotion pipeline where data starts
**bronze** and earns **silver** then **gold** as it's curated and verified.
`delete` survives as an **orthogonal lifecycle flag** (the removal pen), NOT a
quality rung. The decisive question for a tier is *"did it make it to production?"*

| Tier | Meaning | Locked? |
| --- | --- | --- |
| `gold` | Curated/verified first-party AND accepted in production (incl. the machine-derived layers the read viewer renders — land cover, contours, water, roads — per the user's 2026-06-14 call). | yes |
| `silver` | First-party but pending review (text tightening, AOP confirmation, or placeholder-real data). | yes |
| `bronze` | Raw / inspection / not yet promoted to production. Absorbs the former editor + derived + reference + raw rungs. | no |
| `delete` | Lifecycle flag (not a medallion rung): staged for removal — held in the Delete group until the actual delete is approved (NOT auto-deleted). | no |

A FILE tier is the collection's overall state; a **mixed** file carries the
exception at the per-FEATURE `maturity` field, stamped by
`mvp/scripts/set_feature_maturity.py`: **Ellis Cemetery** features = gold while
Tate/Bible/Gilliam = bronze; the **5 ORNL park-building footprints** = gold while
the raw-trace **Shower House** = bronze.

**Production guard (task 4):** `website/js/viewer_core.js` `auditProductionTiers()`
runs once on map load and `console.warn`s the developer when any production-rendered
source carries bronze/silver data (currently: Park buildings → Shower House bronze;
Visitor context callouts → silver; Publishable layers → silver). Per
[[no-limiting-code-mvp]] it NEVER hides/filters — it only surfaces "production
should be gold" so leaks are visible, not enforced.

"Locked, not un-editable" (the user's words): a locked tier renders its existing
features read-only until you click the lock open. **Adding** a new feature is
never lock-gated — a new draw lands editable even inside a locked layer (the lock
protects existing curated data, not your new authoring). So "any gold file can
make new items" and "unlock first to edit" coexist.

## Current sort (2026-06-14, medallion re-tier — was the 2026-06-05 6-rung sort)

Stamped by `mvp/scripts/stamp_maturity.py` (file `_meta`; the `MATURITY` map is the
source of truth) + `mvp/scripts/set_feature_maturity.py` (per-feature for mixed
files). Counts: **gold=9, silver=2, bronze=11, delete=3**.

- **gold (9):** `aop_trail_network.geojson`; `aop_buildings.geojson` (5 ORNL
  footprints — Shower House is per-feature **bronze**); `aop_waypoints_traced.geojson`
  (camp POIs incl. the #firepit tag); and the accepted machine-derived production
  layers the read viewer renders — `aop_landcover.geojson`, `aop_landcover_9patch.geojson`,
  `aop_contours.geojson`, `aop_activity_hotspots.geojson`, `aop_roads.geojson`,
  `aop_water.geojson`. (User 2026-06-14: derived/reference layers that render in
  production are gold.)
- **silver (2):** `aop_visitor_context_callouts.geojson` (region callouts pending
  text review; also holds the 2 brand-logo points), `publish.geojson` (boundary ·
  trails · trailheads, pending).
- **bronze (11):** `aop_buildings_traced.geojson` (raw trace source),
  `aop_editor_seed_pois.geojson`, `aop_user_features.geojson`, `aop_9_patch.geojson`,
  `aop_cemeteries.geojson` (**Ellis is per-feature gold**; Tate/Bible/Gilliam bronze),
  `aop_lidar_tiles.geojson`, `osm_aop_9patch.geojson`, `osm_aop_named.geojson`,
  `sfwda_numbered_trails.geojson`, `sfwda_traced_markers.geojson`,
  `sfwda_trails_edited.geojson`. (SFWDA paper raster has no geojson `_meta`;
  `panel.js` node retag silver→bronze is owed — see Deferred.)
- **delete (3):** `aop_synthetic_activity_hotspots.geojson` +
  `aop_synthetic_activity_tracks.geojson` (the simulated-Saturday pair) and
  `sfwda_traced_trails.geojson`. Staged for removal in the **Delete** panel group
  (lifecycle flag, not a medallion rung).

**Editor (`panel.js`) re-group owed.** The editor tree still uses the pre-medallion
group layout (Gold / Silver / Derived / Reference / Delete sections with hardcoded
node `maturity:` tags). The chip renderer now knows `bronze` (`MATURITY_LABEL`), but
the buildings node (now gold) and SFWDA node (now bronze) still sit in their old
groups, and there is no Bronze section. A full editor re-group to the 3 medallion
buckets is deferred — the editor is a semi-retired surface and the read viewer +
data + production alert (the user's actual asks) are done. Not blocking.

**Delete group (user, 2026-06-05).** The user staged several do-NOT-gold layers
for removal — but as a *review pen*, not an immediate delete (they'd asked to drop
SFWDA traced trails before; it lingered, so now it sits visibly in a group until
the actual delete is approved). Members:
- **whole-file → stamped `delete`:** simulated Saturday activity (both synthetic
  files), SFWDA traced trails.
- **sub-layer → panel-only move (file keeps its tier):** **Springs & gages** is
  part of `aop_water.geojson` (the Streams node keeps that file); **OSM park
  polygon** is part of `osm_aop_9patch.geojson` (OSM tracks/service keep it).
  File-level deletion of these waits on splitting the layer out of its file.

Still **silver-pending** (not excluded forever): publishable trailheads and
event-schedule POIs (placeholder / proposed data that earns gold once real and
confirmed).

## How it's wired

**Data** — `mvp/scripts/stamp_maturity.py` merges `maturity`/`group`/`locked`
(+ a note) into each served file's `_meta`, preserving any existing `_meta` (the
trail gold block). It also records the tier per layer + a tier legend in
`website/data/_schema.json`. It is **additive + idempotent** and must run **LAST**
in the pipeline:

```
rebake_canonical.py            # machine refresh from data/raw/ (wipes _meta)
bake_panel_overrides.py        # human curation on top
export_gold_trail_network.py   # trail gold block
export_publish_geojson.sh      # ← going-gold bake from PostGIS core (slice 2+)
set_feature_maturity.py        # ← per-FEATURE medallion for mixed files (Ellis, Shower House)
stamp_maturity.py              # ← per-FILE maturity stamp, last
```

`rebake_canonical.py` now **carries a live `_meta` forward** (raw/ is pristine and
has none), so a re-bake no longer silently drops the stamp; re-running
`stamp_maturity.py` after any step is still the guaranteed-clean way to restore it.

**Going gold (slice 2+):** `export_publish_geojson.sh` is now the sole writer of a
reference layer's served file from PostGIS `core.features` (e.g. it rebuilds
`aop_buildings.geojson` from `core.features WHERE layer='buildings'`). Like
`rebake_canonical.py`, it **carries the live file's `_meta` forward** so the baked
output still badges its tier (buildings stay `silver`) — the editor reads
`_meta.maturity`, so the bake must never emit a tier-less file. Re-running
`stamp_maturity.py` after the bake remains the guaranteed-clean restore. (The
bake does NOT re-emit the original import provenance headers `_source`/
`_sources_checked`/`_derived`; per-feature provenance lives in `core.features.attrs`
+ `source_register`, which is the gold provenance home.)

**Editor** (`website/js/panel.js`) — the model groups the tree by maturity:
`Gold data` and `Silver — pending review` sit at the top, above the
provenance-grouped reference sections. Each editable group row shows a
**maturity chip** (`nodeMaturity()` → the node's declared `maturity`, falling
back to the loaded file's `_meta.maturity` captured in `META`). The feature
takeover's **Source tab** shows the served **File** + **Tier · locked/unlocked**.
Lock + unlock + add-new were already in the panel; the tier work is the data
stamp, the section layout, the badge, and the Source-tab fields. Verified by
observation (`/tmp/verify_maturity.py`, 23/23, standalone + embed, 0 console
errors); shots `brain/output/playwright_maturity_{tree,standalone,embed}.png`.

## Deferred (on purpose)

- **Strip legacy keys from gold/silver files.** The re-bake is additive (canonical
  block + original keys) so the live `index.html` keeps painting/filtering on the
  old keys. Stripping to a clean gold schema is gated on retiring `index.html`'s
  dependence on a layer's raw keys (the index→panel swap). Don't strip a file the
  live map still styles on. See [[common-feature-schema]] (save-path section).
- **Physical file renames** to match group names — current names are already good
  (`aop_trail_network.geojson` etc.); a rename touches `index.html`, `panel.js`
  `MAP_DATA`, and the `sw.js` cache manifest for little gain. Not done.
