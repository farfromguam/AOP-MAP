# AOP database diagram — all tables + relationships

TL;DR: Four schemas, **8 objects** (7 tables + 1 view) after the 2026-06-07 table
cleanup. `raw` captures unprocessed source data; `core` is the store of record
(**one** `core.features` for every geo layer, plus `core.events` + `core.activities`
for the Where/When/What event model); `publish` is the single read-only gate the
website bakes from (`publish.features`); `source_register` is the provenance hub
**every** `core.*` and `raw.*` table FK's into. The eight per-layer `core.*` tables
(trail_centerlines, park_boundaries, trailheads, parcels, hazards, observations,
field_tracks, print_annotations) and their five `publish.*` views were **folded into
`core.features`** — every row moved (domain fields → `attrs`), nothing lost. Every
cross-link between Where/When/What is a **soft reference** (plain `text`, no FK, no
CHECK); the only enforced FK anywhere is `source_id` → `source_register.sources`
(`no_limiting_code_mvp`).

#aop #sprint #07 #tables #er #diagram #schema

-----

## The cleanup (2026-06-07) — 21 objects → 8

The user looked at the old 21-object diagram and said: *"we should not have so many
tables… it needs to be moved or removed… figure out the minimum and migrate data into
that shape."* (This overrode a prior consult that argued for keeping the per-layer
"source-led spine" — *"there is data there"* is not a reason to keep a table; the data
moves.) So the gold convergence that already collapsed the **display** layers into
`core.features` was extended to the **source** layers too:

- The 8 per-layer `core.*` tables held **12 rows total**; all 12 moved into
  `core.features` (each table's domain columns + JSONB side-bag → `core.features.attrs`,
  `layer` = the old table name). `migrate_layers_to_core_features.sql` is the one-shot.
- The 5 per-layer `publish.*` views were retired; the bake reads every published map
  layer from the one `publish.features` gate, filtered by `layer`.
- The validation-loop pipeline (`import_gpx_track` → `promote_gpx_to_trail`, the parcel
  import, the smoke test) was **rewritten onto `core.features`** — the northstar loop
  (capture → field track → review → promote → publish) is unchanged in shape, it just
  runs on one table now. Proven end-to-end on a fresh volume.
- All 15 `feature_sources` provenance links were re-pointed to `core.features`.

**What stays (and why it earns its place):** `core.events`/`core.activities` (the
When/What model — geometry-less, a different entity than a place), `source_register`
×2 (the provenance hub / the one enforced FK), `raw` ×2 (the unprocessed capture zone),
and `publish.features` (the gate). Folding any of those in would undo Where/When/What or
the capture/provenance zones. So **8 is the honest minimum.**

## Schema zones — the flow

```
 raw  (capture, unprocessed)         core  (store of record)              publish  (gate → website)
 ┌──────────────────────┐            ┌──────────────────────────────┐     ┌──────────────────────────┐
 │ gpx_captures         │  promote   │ features   (WHERE / all geo) │ gate│ features                 │
 │ arcgis_feature_capt. │ ─────────► │ events     (WHEN, junction)  │ ───►│  (the ONE view; layers   │
 └──────────┬───────────┘            │ activities (WHAT, reusable)  │     │   filtered by `layer`)   │
            │                        └──────────────┬───────────────┘     └────────────┬─────────────┘
            │ source_id                             │                        ▲ gate: permission='publish'
            │                                       │                        │  AND publish_status='publish'
            ▼                                       │                        │  AND archived_at IS NULL
 ┌──────────────────────────────────────────────────────────────────────────┘
 │ source_register
 │   sources           ◄──── source_id  (real FK)  from EVERY core.* and raw.* table
 │   feature_sources   ──── (feature_schema, feature_table='features', feature_id) = soft ref → a core.features row
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────
```

The validation loop runs inside `core.features`: a GPX ride lands as
`layer='field_tracks'` (held), review **promotes** it to `layer='trail_centerlines'`
(publish) — observations never overwrite trails directly, review promotes them
(`northstar/validation_loop`). Promotion is a re-layer within one table, traced through
`source_register` at every hop.

## `core.features` — the converged geo table

```
features  id PK · layer · name · kind · blurb · is_destination · status · confidence
          · permission · publish_status · source_key UNIQUE · archived_at
          · source_id FK→sources · geom geometry(Geometry,4326) · attrs jsonb
          · notes · last_verified · created_at · updated_at
```

`layer` values in use (live, 2026-06-07): `buildings`, `cemeteries`, `visitor`,
`trails`, `poi`, `event` (the gold/display + event-anchor layers) plus the folded-in
`trail_centerlines`, `park_boundaries`, `trailheads`, `parcels`, `observations`,
`field_tracks` (and `hazards` / `print_annotations`, defined, 0 rows today).
`attrs` carries each layer's domain data with **no allowlist, no CHECK** — e.g. a
trail's `difficulty`, a parcel's `parcel_id`/`owner`/`land_area` + assessment metadata,
a field track's `segment_index`/`recorded_*`, an observation's `review_status`.

## The Sprint 07 event model — Where × When × What

```
        WHERE — a place                  WHEN — an occurrence              WHAT — reusable
┌──────────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────┐
│ core.features            │     │ core.events  (junction)  │     │ core.activities          │
│ geom + attrs             │     │ place_key (soft→#tag) ───┼──┐  │ activity_key UNIQUE      │
│  └ event_location        │ ◄───┤ activity_key (soft) ─────┼──┼──► name, kind, description   │
│    {tag,label,role,…}    │     │ sort_order,title,status  │  │  │ attrs (grade/length/…)    │
│ source_id FK             │     │ date_label,time_label    │  │  │ (NO geom, NO place col)  │
└──────────────────────────┘     │ archived_at, source_id FK│  │  │ source_id FK             │
                                  └──────────────────────────┘  └──────────────────────────┘
```

The place binds on the **occurrence** (`place_key`, a `#tag` resolved against
`core.features.attrs->'event_location'->>'tag'`), never on the activity — one activity
(Night Crawl) is cited by many occurrences and can move places.

## Every table — columns

### source_register  (provenance hub)
```
sources           id PK · name · source_type · url_or_contact · retrieved_on · license_or_permission
                  · publish_status · confidence_default · notes · timestamps
feature_sources   id PK · feature_schema · feature_table · feature_id  ← soft ref to a core.features row
                  · source_id FK→sources · claim · confidence · last_checked · review_status · notes · timestamps
```

### core  (store of record)
```
features    (above) — every geo layer
events      id PK · source_key UNIQUE · event_id (soft) · sort_order · title · date_label · start_local
            · time_label · status · place_key (SOFT→features #tag) · activity_key (SOFT→activities)
            · attrs jsonb · archived_at · source_id FK→sources · notes · timestamps
activities  id PK · activity_key UNIQUE · name · kind · description · attrs jsonb
            · source_id FK→sources · archived_at · notes · timestamps   (NO geom)
```

### publish  (the one read-only view over core — the gate the website bakes from)
```
features    VIEW of core.features    gate: permission='publish' AND publish_status='publish'
                                          AND archived_at IS NULL  (selects attrs explicitly)
```
The bake (`export_publish_geojson.sh`) reads the published map layers
(`poi`, `trail_centerlines`, `park_boundaries`, `trailheads`, `hazards`) from
`publish.features` filtered by `layer`; reference layers (buildings/cemeteries/visitor/
trails) bake to their own served files from `core.features` (non-publish permission);
the schedule bakes from `core.events` + `core.activities` + the event-anchor features.

### raw  (capture zone, unprocessed)
```
gpx_captures            id PK · source_id FK→sources · file_name · track_name · creator · recorded_at
                        · segment_count · point_count · raw_xml · captured_at · notes
                        · CONSTRAINT gpx_captures_file_recorded_uniq UNIQUE(file_name,recorded_at)
arcgis_feature_captures id PK · source_id FK→sources · source_url · query_where · fetched_at
                        · feature_json jsonb · notes
```

## Relationships — complete

| From | column(s) | → To | matches on | type |
|------|-----------|------|-----------|------|
| `core.events` | `place_key` (a `#tag`) | `core.features` | `attrs->'event_location'->>'tag'` | **soft** (no FK) |
| `core.events` | `activity_key` | `core.activities` | `activity_key` | **soft** (no FK) |
| `core.events` | `event_id` | umbrella event | bake-config today (no table yet) | **soft** |
| `core.features` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.events` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.activities` | `source_id` | `source_register.sources` | `id` | **FK** |
| `raw.gpx_captures` | `source_id` | `source_register.sources` | `id` | **FK** |
| `raw.arcgis_feature_captures` | `source_id` | `source_register.sources` | `id` | **FK** |
| `source_register.feature_sources` | `source_id` | `source_register.sources` | `id` | **FK** |
| `source_register.feature_sources` | `feature_schema`,`feature_table`,`feature_id` | a `core.features` row | soft (`feature_table='features'`) | **soft** |
| `publish.features` | view | `core.features` | publish gate | view |

## Rules the diagram encodes

- **Soft reference** = plain `text` (or polymorphic key) resolved by match at
  bake/render. **No `FOREIGN KEY`, no `CHECK`, no enum** — a reference at a not-yet-present
  target is stored and resolved later, never rejected (`no_limiting_code_mvp`; the bake uses
  LEFT joins).
- **FK** = the one enforced kind: `source_id` → `source_register.sources`, on every `core.*`
  and `raw.*` table (provenance is always populated by the importer; a link, not a data gate).
- **`publish.features`** is a view, not a table — the read-only gate. A typo in `permission`
  silently drops a row from publish (the accepted MVP failure mode), it never errors.
- **One geo table, one publish view.** Per-domain shape lives in `attrs`, not in a
  per-geometry-type table. Adding a new layer = a new `layer` value, not a new table.
- **Generated from the live DB** (`aop_map`) on 2026-06-07 after the table cleanup.
  Source of truth: `mvp/init_db.sql`. Fresh-volume reproducible (init_db → 8 objects).
```
