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

## The tiers

| Tier | Meaning | Locked? | Editor section |
| --- | --- | --- | --- |
| `gold` | Curated, reviewed, first-party, final. | yes | **Gold data** |
| `silver` | Real first-party but pending review (text tightening, AOP confirmation, or placeholder-real data). | yes | **Silver — pending review** |
| `editor` | First-party editor scratch (drawn / seed). | no | _(retired 2026-06-05 — the Map editor panel group is gone; these files keep an editor `_meta` but have no panel node)_ |
| `derived` | Machine-computed reference (you don't hand-edit a contour line). | no | Derived layers |
| `reference` | External raw context we trace against but don't own. | no | Source / External reference |
| `delete` | Staged for removal — held in the Delete group until the actual delete is approved (NOT auto-deleted). | no | **Delete — staged for removal** |

"Locked, not un-editable" (the user's words): a locked tier renders its existing
features read-only until you click the lock open. **Adding** a new feature is
never lock-gated — a new draw lands editable even inside a locked layer (the lock
protects existing curated data, not your new authoring). So "any gold file can
make new items" and "unlock first to edit" coexist.

## Current sort (2026-06-05, after the group reorganization)

Stamped by `mvp/scripts/stamp_maturity.py` (the `MATURITY` map is the source of
truth; mirror any change into the `panel.js` node `maturity:` tags). The user
reorganized the right-panel groups on 2026-06-05 — the moves are folded in below.

- **gold (1):** `aop_trail_network.geojson` — the merged trail network. ~120
  edges; still may need edits.
- **silver (3 files):** `aop_visitor_context_callouts.geojson` (region callouts —
  pending text review; also holds the 2 brand-logo points), `aop_buildings.geojson`
  (curated park buildings), `publish.geojson` (boundary · submitted trails ·
  trailheads). The **Silver panel group** additionally shows two nodes relocated
  here on 2026-06-05: **Brand logos** (the callout file's logo points — chip now
  reads Silver, matching the file) and **SFWDA paper trail map** (a raster overlay
  with no geojson `_meta`; node-tagged `silver`).
- **editor (2):** `aop_editor_seed_pois.geojson` (1 seed POI),
  `aop_user_features.geojson` (empty). The **Map editor panel group RETIRED
  2026-06-05** — the three draw groups (Points / Lines / Polygons) and Drawn POIs
  were dropped. These files keep their editor `_meta` and the host map still owns
  the sources, but they have no panel node. (The former `aop_brand_logos.geojson`
  was merged into the silver callout file on 2026-06-05 as `kind=brand_logo`
  points; that node now lives in Silver.)
- **derived (4):** land cover (×2), contours, **activity hotspots** (real
  GPX-dwell — moved into Derived from the old User-submitted group 2026-06-05).
- **reference (10):** 9-patch, **cemeteries** (now shown in the External-reference
  panel group, moved from Source layers 2026-06-05), lidar tiles, roads, water,
  OSM (×2), SFWDA extracts (numbered / traced-markers / edited).
- **delete (3):** `aop_synthetic_activity_hotspots.geojson` +
  `aop_synthetic_activity_tracks.geojson` (the simulated-Saturday pair) and
  `sfwda_traced_trails.geojson`. Staged for removal in the **Delete** panel group.

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
stamp_maturity.py              # ← maturity stamp, last
```

`rebake_canonical.py` now **carries a live `_meta` forward** (raw/ is pristine and
has none), so a re-bake no longer silently drops the stamp; re-running
`stamp_maturity.py` after any step is still the guaranteed-clean way to restore it.

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
