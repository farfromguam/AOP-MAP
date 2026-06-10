# Approach-C field inventory — the 4 served reference files (2026-06-10)

> Built FIRST, before any bake change, per the gold-slice-6 Approach-C spec
> ("field-inventory FIRST — this is what stalled the 3 prior agents"). Enumerates
> every `properties` key in the 4 served reference files **at HEAD**, classifies
> each as CMFS spine-column vs attrs-extra, and records the COLUMN-vs-attrs-vs-served
> reconciliation that the loss-free DB-bake depends on.
>
> Source of truth for the spine: `research/common_feature_schema.md` (Tier1 id·name·
> description·kind + Tier2 provenance source·confidence·permission·status·last_checked).
> `northstar/editor_architecture_contracts.md` C6 (one home). The home = COLUMNS.

#aop #06_going_gold #slice6 #approachC #field_inventory #shadow_attributes

-----

## Method

- HEAD files: `git show HEAD:website/data/<file>` for trails / buildings / cemeteries / visitor.
- DB: `core.features` (160 rows; 159 active). The current `attrs`-verbatim bake
  reproduces HEAD's **per-feature `properties`** loss-free (semantic diff = IDENTICAL
  on all 4), i.e. `attrs == served properties` for every key — the prior folds synced
  the DB `attrs` to served canonical. (This is **per-feature** loss-free; the
  **collection-level** top-level keys are a separate carry-forward — see the
  "Collection-level (top-level) keys" section below, added after the 2026-06-10
  council Scribe andon caught them.) So the inventory's job is: where does each spine key
  live as a **column**, and where does the column diverge from `attrs`/served.

## The CMFS spine (Tier1 + Tier2) — classification

| Spine field | Real `core.features` column? | Home decision | Why |
| --- | --- | --- | --- |
| `id` | `source_key` (UNIQUE business key); served `id` = `attrs.id` (per-layer) | COLUMN→served `id` keeps the existing per-layer served `id` (= `attrs.id`); F4/G_C own canonical-id unification | not this slice's fork |
| `name` | `name` ✅ | COLUMN (after promotion) | buildings col held the ADDRESS — promoted to display name |
| `description` | `description` ✅ | COLUMN | already == served everywhere |
| `kind` | `kind` ✅ | COLUMN | already == served everywhere |
| `confidence` | `confidence` ✅ | COLUMN | already == served everywhere |
| `permission` | `permission` ✅ | COLUMN | already == served everywhere |
| `status` | `status` ✅ | COLUMN (after promotion) | buildings col held the facility ROLE — promoted to "raw context" |
| `source` | **NO column** (only `source_id` FK, finer-grained mismatch) | ATTRS | `source_id`→sources.name is a coarser per-layer label, NOT the served `source`; deriving from the FK is lossy. `source` is open-vocab provenance (source_register) → stays in attrs |
| `last_checked` | **NO column** (`last_verified` is a different timestamp semantic) | ATTRS | served `last_checked` carries strings like "Automated"/dates; `last_verified` is the edit-stamp. Open-vocab → attrs |

**Result: 6 spine fields read from COLUMNS** (id via source-side `id`, name, description,
kind, confidence, permission, status) **+ 2 spine fields read from ATTRS** (source,
last_checked — no column home; open-vocabulary provenance). All remaining keys are
attrs-extras served verbatim.

## COLUMN-vs-served divergences found (the DB-side promotion this slice does)

The `attrs`-verbatim bake matched served 100%. Reading the spine from COLUMNS instead
exposed exactly these column gaps (everything else: column already == served):

1. **buildings `name`** — 3 of 5 rows: column = street address (`880/1010/1033 Ellis Cove
   Road`), served/attrs = display name (`Front Office`/`Pavilion`/`Farmhouse`). The import
   put the address in `name`; the curated display name lived only in `attrs.name`.
   → **Promote `attrs.name` into the `name` column** for buildings. Address preserved in
   `attrs.address` (and `attrs.building_label`).
2. **buildings `status`** — all 5 rows: column = `facility` (the FEMA facility ROLE),
   served/attrs = `raw context` (the publish-state stand-in). The role is preserved as a
   facet (`attrs.facility_role`/`attrs.status` already carries "raw context").
   → **Promote `attrs.status` ("raw context") into the `status` column** for buildings.
   (Role survives in `attrs.facility_role`.)
3. **`source` column = NULL on ALL 4 layers** — `source` is not a column; it lives in
   `attrs.source`. Confirmed `source_id`→`sources.name` is a coarser label that does NOT
   equal the served `source` string. → read `source` from ATTRS (no DB change).
4. **`last_checked` column = NULL on ALL 4 layers** — not a column. → read from ATTRS.
5. **trails / cemeteries / visitor**: `name`/`description`/`kind`/`confidence`/`permission`/
   `status` columns already == served. No promotion needed. (trail `name` column already
   carries "Launchpad"/"15"/NULL identically to served — see Blocker-2 below.)

## Blocker-2 (unnamed trails) — HEAD reality, matched exactly

HEAD `aop_trail_network.geojson` trail `name` distribution (120 trails):
- **21 human-named** (Launchpad, GWT, 89X, JW3, …)
- **79 numeric** (`name` == the trail number as a string: "15", "27", …)
- **20 null/blank**

The DB **column `name` already equals served `name` for ALL 120 trails (0 mismatches)** —
including the numeric ones and the 20 NULLs. So reading `name` from the COLUMN reproduces
HEAD's label behavior exactly (the 20 already-NULL trails stay label-less; numeric and
human names render as today). **No name nulling is applied** — HEAD already serves numeric
names, and the Blocker-2 rule ("do not STORE the number as name where HEAD had none") is
already satisfied: the column was populated by the same sidecar fold that produced HEAD, so
column == served. `trail_number` is preserved in `attrs.trail_number` regardless.

## Per-file `properties` key inventory (HEAD)

### aop_trail_network.geojson — 120 features, has `_meta`
spine: `id`(120) `name`(120) `description`(120) `kind`(120) `confidence`(120) `permission`(120)
`status`(120) `source`(120) `last_checked`(120) · attrs-extras: `color`(120) `difficulty`(120)
`facets`(116) `review_status`(120) `source_file`(120) `trail_number`(120) `_original`(8)

### aop_buildings.geojson — 5 features, has `_meta`
spine: `id`(5) `name`(5) `description`(5) `kind`(5) `confidence`(5) `permission`(5) `status`(5)
`source`(5) `last_checked`(5) · attrs-extras: `address` `aop_facility`(3) `aop_private`(2)
`aop_structure_box`(2) `area_sqft` `area_sqm` `build_id` `building_label` `centroid_lat`
`centroid_lng` `city` `county` `facets` `facility_name`(3) `facility_role`(3) `footprint_source`
`height_m` `image_date` `image_name` `inside_aop_boundary` `license_or_permission`
`occupancy_class` `outbuilding` `primary_occupancy` `production_date` `publish_status`
`secondary_occupancy` `source_file` `source_item_url` `source_name` `source_object_id`
`source_service_url` `state` `uuid` `validation_method` `zip` `_original`(3)

### aop_cemeteries.geojson — 8 features (4 ids × parcel+marker twin), has `_meta`
spine: `id`(8) `name`(8) `description`(8) `kind`(8) `confidence`(8) `permission`(8) `status`(8)
`source`(8) `last_checked`(— not present; cemeteries carry no last_checked) · attrs-extras:
`acres` `address` `aka`(2) `aop_inholding` `burial_count` `burial_source` `burial_terms`
`burials` `cemetery_type` `facets` `geom_role` `named_burial_count` `note` `parcel_class`
`parcel_gislink` `parcel_id` `parcel_owner` `parcel_source`

### aop_visitor_context_callouts.geojson — 4 features, has `_meta`
spine: `id`(4) `name`(4) `description`(4) `kind`(4) `confidence`(4) `permission`(4) `status`(4)
`source`(4) `last_checked`(4) · attrs-extras: `attribution`(2) `direction`(2) `directions_url`(2)
`distance_note`(2) `drive_time_note`(2) `examples`(2) `food_url`(2) `icon_image`(2) `icon_size`(2)
`label`(2) `lodging_url`(2) `logo_id`(2) `services`(2) `source_file`(4) `source_summary`(2)
`source_url`(4)

## The loss-free contract for the bake

`properties = SPINE(columns: id,name,description,kind,confidence,permission,status)
            ⊕ SPINE(attrs: source,last_checked)
            ⊕ ALL remaining attrs keys verbatim`

Because attrs already == served for every key, and the only column/served gaps are
buildings `name`/`status` (fixed by promotion) and the two no-column fields source/
last_checked (read from attrs), the merged output is **loss-free vs HEAD by construction**.
The merge must not drop any attrs key — every render key (`color`, `difficulty`, `facets`,
`trail_number`, `geom_role`, `icon_size`, `_original`, …) survives.

## Collection-level (top-level) keys — added after the 2026-06-10 council Scribe andon

The per-feature inventory above is **not** the whole file. Each served reference file is a
GeoJSON FeatureCollection that also carries **top-level** (collection-level) keys besides
`type`/`features`/`_meta` — owner-authored provenance/derivation with no per-feature home.
The first cut of the bake carried forward **only `_meta`**, silently dropping the rest. The
council Witness/orchestrator loss-free checks compared only `features[]`, so the drop passed
unseen until the **Scribe** seat inspected the top-level object. The dropped keys at HEAD:

| File | Top-level keys HEAD ships (besides type/features/_meta) |
| --- | --- |
| `aop_buildings` | `_source` `_source_item` `_source_service` `_generated_by` `_retrieved_on` `_aop_9_patch_bbox` `_sources_checked` `_derived` (incl. "~197 raw FEMA footprints dropped per owner decision") |
| `aop_cemeteries` | `_source` `_generated_by` |
| `aop_trail_network` | `name` (the collection name "aop_trail_network") |
| `aop_visitor_context_callouts` | `name` `_description` `_sources_checked` |

**Fix:** `export_publish_geojson.sh` now carries forward **every** top-level key from the
live served file (both arms), not just `_meta` — the same stopgap `_meta` already used. So the
adopted bake is loss-free at **both** levels (per-feature AND collection). The verifier
`playwright_verify_shadow_refbake_repro.py` gained a `COLLECTION-level top-level keys
loss-free` assertion so this class can never slip through again. Like `_meta`, the durable
DB home for collection-level provenance is the deferred `reference-bake-no-meta-on-fresh-volume`
item — carry-forward keeps it loss-free until then.
