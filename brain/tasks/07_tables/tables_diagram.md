# AOP database diagram — all tables + relationships

TL;DR: Four schemas. `raw` captures unprocessed source data; `core` is the store of record;
`publish` is the read-only gate the website bakes from; `source_register` is the provenance hub
**every** `core.*` and `raw.*` table FK's into. Sprint 07 added the event model
(`core.events` + `core.activities`) on top of the gold `core.features`. Every cross-link between
Where/When/What is a **soft reference** (plain `text`, no FK, no CHECK); the only enforced FK
anywhere is `source_id` → `source_register.sources` (`no_limiting_code_mvp`).

#aop #sprint #07 #tables #er #diagram #schema

-----

## Why it looks like a lot (live vs legacy — council consult 2026-06-07)

21 objects, but the live product runs on ~**5 tables**. The count breaks down by *job*, not by
duplication (grounded in live row counts):

- **6 `publish.*` are VIEWS**, not storage — read-only gates 1:1 over a core table.
- **2 `source_register`** = provenance hub; **2 `raw`** = capture/staging.
- **3 gold-spine tables carry the product**: `core.features` (147 rows, all layers),
  `core.events` (13), `core.activities` (12).
- **8 `core.*` per-layer tables are LEGACY** — the old rigid one-table-per-geometry-type MVP
  schema (`trail_centerlines` 4 demo rows, `trailheads` 1, `park_boundaries` 2, `parcels` 2,
  `hazards` 0, `observations` 1, `field_tracks` 2, `print_annotations` 0). The gold migration
  replaced all of them with the single flexible `core.features`; they now hold stale/demo data,
  not the live data (the 120 real trails live in `core.features`, not `trail_centerlines`).
  **They are retirement candidates — see `../10_deferred/retire_legacy_geo_tables.md`.**

So: not duplication, layering — plus old furniture not yet carried out. The trend is *shrinking*
(gold collapsed 5 layers + POIs into `core.features` and dropped `core.pois` outright).

-----

## Schema zones — the flow

```
 raw  (capture, unprocessed)         core  (store of record)              publish  (read-only gate → website)
 ┌──────────────────────┐            ┌──────────────────────────────┐     ┌──────────────────────────┐
 │ gpx_captures         │  promote   │ EVENT MODEL (sprint 06–07)   │ gate│ features                 │
 │ arcgis_feature_capt. │ ─────────► │  features · events · activities ──►│ trail_centerlines        │
 └──────────┬───────────┘            │ GEOGRAPHIC LAYERS            │     │ trailheads · hazards     │
            │                        │  trail_centerlines · trailheads    │ parcels · park_boundaries│
            │ source_id              │  park_boundaries · parcels   │     └────────────┬─────────────┘
            │                        │  hazards · observations      │      ▲ gate: permission='publish'
            │                        │  field_tracks · print_annot. │      │   AND publish_status='publish'
            ▼                        └──────────────┬───────────────┘      │   (+ archived_at IS NULL on
 ┌───────────────────────────────────────────────────────────────────────┘    publish.features)
 │ source_register
 │   sources           ◄──── source_id  (real FK)  from EVERY core.* and raw.* table below
 │   feature_sources   ──── (feature_schema, feature_table, feature_id) = polymorphic SOFT ref → any core feature
 └───────────────────────────────────────────────────────────────────────────────────────────────────────────
```

## The Sprint 07 event model — Where × When × What (detail)

```
        WHERE — a place                  WHEN — an occurrence              WHAT — reusable
┌──────────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────┐
│ core.features            │     │ core.events  (junction)  │     │ core.activities          │
│ ──────────────────────── │     │ ──────────────────────── │     │ ──────────────────────── │
│ id              PK       │     │ id              PK       │     │ id              PK       │
│ source_key      UNIQUE   │     │ source_key      UNIQUE   │     │ activity_key    UNIQUE   │
│ geom geometry(Geom,4326) │     │ event_id     (soft→umb.) │     │ name, kind, description   │
│ attrs jsonb              │     │ place_key    (soft) ─────┼──┐  │ attrs jsonb (grade/      │
│  └ event_location        │     │ activity_key (soft) ─────┼──┼──► length/gate list…)       │
│    {tag,label,map_label, │ ┌───┤ sort_order,title,status  │  │  │ (NO geom, NO place col)  │
│     role,source,conf,    │ │   │ date_label,start_local,  │  │  │ source_id  FK            │
│     caveat}              │ │   │ time_label, attrs jsonb  │  │  └──────────────────────────┘
│ layer,name,kind,blurb    │ │   │  └ inspired_by,route_tags│  │
│ permission,publish_status│ │   │ archived_at, source_id FK│  │   place_key (a #tag) matches
│ is_destination,confidence│ │   └──────────────────────────┘  │   core.features.attrs
│ archived_at, source_id FK│ │      ▲ soft: by #tag            │   ->'event_location'->>'tag'
└──────────────────────────┘ └──────┘                          │   activity_key matches
                                                                └─  core.activities.activity_key
```

The place binds on the **occurrence** (`place_key`), never on the activity — so one activity
(Night Crawl) is cited by many occurrences (Fri + Sat) and can move places.

## Every table — columns (PK / UNIQUE / FK / soft marked)

### source_register  (provenance hub)
```
sources           id PK · name · source_type · url_or_contact · retrieved_on · license_or_permission
                  · publish_status · confidence_default · notes · created_at · updated_at
feature_sources   id PK · feature_schema · feature_table · feature_id  ← polymorphic SOFT ref to any core feature
                  · source_id FK→sources · claim · confidence · last_checked · review_status · notes · timestamps
```

### core  (store of record)
```
features          id PK · source_key UNIQUE · layer · name · kind · blurb · is_destination
   (WHERE / gold)  · status · confidence · permission · publish_status · geom geometry(Geometry,4326)
                  · attrs jsonb (└ event_location for the 7 schedule places) · source_id FK→sources
                  · archived_at · notes · last_verified · created_at · updated_at
events            id PK · source_key UNIQUE · event_id (soft→umbrella) · sort_order · title
   (WHEN)          · date_label · start_local · time_label · status · place_key (SOFT→features)
                  · activity_key (SOFT→activities) · attrs jsonb (inspired_by, route_tags)
                  · archived_at · source_id FK→sources · notes · created_at · updated_at
activities        id PK · activity_key UNIQUE · name · kind · description · attrs jsonb
   (WHAT)          · source_id FK→sources · archived_at · notes · created_at · updated_at   (NO geom)
trail_centerlines id PK · name · difficulty · status · confidence · permission · publish_status
                  · source_id FK→sources · geom geometry(LineString,4326) · notes · last_verified · timestamps
trailheads        id PK · name · status · confidence · permission · publish_status · source_id FK→sources
                  · geom geometry(Point,4326) · notes · created_at · updated_at
park_boundaries   id PK · name · status · confidence · permission · publish_status · source_id FK→sources
                  · geom geometry(MultiPolygon,4326) · notes · last_verified · timestamps
parcels           id PK · parcel_id · owner · land_area numeric · status · confidence · permission
                  · publish_status · source_id FK→sources · geom geometry(Polygon,4326) · metadata jsonb
                  · notes · last_verified · timestamps
hazards           id PK · hazard_type · severity · status · confidence · permission · publish_status
                  · source_id FK→sources · geom geometry(Point,4326) · notes · timestamps
observations      id PK · observation_type · status · confidence · review_status · measured_at
                  · source_id FK→sources · geom geometry(Point,4326) · metadata jsonb · notes · timestamps
field_tracks      id PK · track_name · segment_index · point_count · recorded_start · recorded_end
                  · status · confidence · permission · publish_status · source_id FK→sources
                  · geom geometry(LineString,4326) · metadata jsonb · notes · last_verified · timestamps
print_annotations id PK · annotation_type · status · source_id FK→sources
                  · geom geometry(Geometry,4326) · notes · created_at · updated_at
```

### publish  (read-only views over core — the gate the website bakes from)
```
features          VIEW of core.features        gate: permission='publish' AND publish_status='publish'
                                                     AND archived_at IS NULL   (selects attrs explicitly)
trail_centerlines VIEW of core.trail_centerlines  gate: permission='publish' AND publish_status='publish'
trailheads        VIEW of core.trailheads          gate: (same)
park_boundaries   VIEW of core.park_boundaries     gate: (same)
parcels           VIEW of core.parcels             gate: (same)
hazards           VIEW of core.hazards             gate: (same)
```
(No `publish` view for `events` / `activities` / `observations` / `field_tracks` /
`print_annotations` — events/activities bake via `export_publish_geojson.sh`'s schedule arm
straight from `core`; the rest are not published.)

### raw  (capture zone, unprocessed)
```
gpx_captures            id PK · source_id FK→sources · file_name · track_name · creator · recorded_at
                        · segment_count · point_count · raw_xml · captured_at · notes   UNIQUE(file_name,recorded_at)
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
| `core.trail_centerlines` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.trailheads` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.park_boundaries` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.parcels` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.hazards` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.observations` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.field_tracks` | `source_id` | `source_register.sources` | `id` | **FK** |
| `core.print_annotations` | `source_id` | `source_register.sources` | `id` | **FK** |
| `raw.gpx_captures` | `source_id` | `source_register.sources` | `id` | **FK** |
| `raw.arcgis_feature_captures` | `source_id` | `source_register.sources` | `id` | **FK** |
| `source_register.feature_sources` | `source_id` | `source_register.sources` | `id` | **FK** |
| `source_register.feature_sources` | `feature_schema`,`feature_table`,`feature_id` | any `core.*` row | polymorphic | **soft** |
| `publish.features` | view | `core.features` | publish gate | view |
| `publish.trail_centerlines` | view | `core.trail_centerlines` | publish gate | view |
| `publish.trailheads` | view | `core.trailheads` | publish gate | view |
| `publish.park_boundaries` | view | `core.park_boundaries` | publish gate | view |
| `publish.parcels` | view | `core.parcels` | publish gate | view |
| `publish.hazards` | view | `core.hazards` | publish gate | view |

## Rules the diagram encodes

- **Soft reference** = plain `text` (or polymorphic key) resolved by match at bake/render. **No
  `FOREIGN KEY`, no `CHECK`, no enum** — an occurrence/feature pointing at a not-yet-present
  target is stored and resolved later, never rejected (`no_limiting_code_mvp`; the bake uses LEFT
  joins). The Sprint-07 Where/When/What links and `feature_sources`' polymorphic link are all soft.
- **FK** = the one enforced kind: `source_id` → `source_register.sources`, on every `core.*` and
  `raw.*` table (provenance is always populated by the importer; it's a link, not a data gate).
- **`publish.*`** are views, not tables — the read-only gate. A typo in `permission` silently drops
  a row from publish (the accepted MVP failure mode), it never errors.
- **Generated from the live DB** (`aop_map`) on 2026-06-07. Source of truth: `mvp/init_db.sql`.
```
