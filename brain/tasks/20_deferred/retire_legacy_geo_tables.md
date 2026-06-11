# Retire the legacy per-layer geo tables (the "so many tables" cleanup)

> **✅ DONE 2026-06-07 — FULL FOLD executed (DB + scripts + init_db.sql, UNCOMMITTED). 21 objects → 8.**
> The earlier "DO NOT RETIRE — they're the source-led spine" correction was **overridden by the user**:
> *"we should not have so many tables. attempts to remove the extraneous resulted in andon pulls 'there
> is data there' well it needs to be moved or removed. figure out the minimum and migrate data into that
> shape."* (`cards_not_gospel` — the user's inline correction wins.) The user chose **full fold** + **rewrite
> the validation-loop pipeline onto `core.features`**. Done and verified by observation:
>
> - **Migrated** all 12 rows from the 8 per-layer `core.*` tables into `core.features` (domain fields →
>   `attrs`, `layer`=old table name; `migrate_layers_to_core_features.sql`). count==input (147→159).
>   All 15 `feature_sources` re-pointed to `core.features` (0 dangling).
> - **Bake rewired** (`export_publish_geojson.sh`): `publish.geojson` now reads every published layer
>   from the one `publish.features` gate. Output feature-equivalent to the prior bake (only the
>   geo-layer `id`s shifted to `core.features` serials — the gold-precedent change); POI DOM rows
>   observed rendering; served files restored byte-identical to HEAD.
> - **Pipeline rewritten** onto `core.features` (`import_gpx_track`, `promote_gpx_to_trail`,
>   `import_aop_parcel_boundary`, `validation_loop_smoke_test`) — proven end-to-end on a fresh volume
>   (all exit 0; field_tracks→promote→publish; parcels+envelope; observation→promote; 10/10 provenance
>   links → features). The northstar validation loop is re-homed on one table, not deleted.
> - **Dropped** the 8 per-layer tables + 5 per-layer publish views on the live DB. `init_db.sql`
>   updated (8 objects); fresh-volume repro exit 0. Also fixed a pre-existing drift: named the
>   `gpx_captures` UNIQUE constraint so `import_gpx_track.sql`'s `ON CONFLICT ON CONSTRAINT` resolves
>   on a fresh volume.
> - **Final shape (the honest minimum):** `core.features` + `core.events` + `core.activities` +
>   `source_register.sources`/`feature_sources` + `raw.gpx_captures`/`arcgis_feature_captures` +
>   `publish.features` = 7 tables + 1 view. See `../07_tables/tables_diagram.md`.
> - **Owed (the user's git gate):** the commit. **Flagged (pre-existing, NOT this card):** the served
>   `publish.geojson` carries a served-only park_boundary ("Ellis Cemetery (inholding parcel)") that no
>   table holds, so the bake drops it on next deploy — the gold "served-only hand-curated row" gap,
>   unrelated to this fold. Same class: HEAD's served file also carries extra keys
>   (`description`/`source`/`last_checked`) from an older writer the current `attrs`-verbatim bake won't
>   reproduce (non-breaking — the viewer reads `blurb`). Both surface only on the next real deploy.
> - **Council 2026-06-07: FULL CLEAR (full six).** Witness andon'd the rewritten parcel import (it threw
>   a unique-violation on a duplicate-parcel batch — a C5 reject); fixed with `ON CONFLICT (source_key)
>   DO NOTHING`, re-witnessed CLEAR; Warden/Quartermaster/Mason/Scribe clear.
>
> Everything below is the **superseded** original plan + the (now-overridden) keep-it correction, kept
> as the record of how the framing evolved.

> **Source:** council consult 2026-06-07 — the user, looking at the full table diagram, said
> *"how do we have so many tables… I am at a loss."* This card is the cleanup it surfaced.
> **Status: ~~DEFERRED~~ ~~WITHDRAWN~~ DONE (full fold; see the DONE block above).**

TL;DR:
- The live product runs on ~**5 tables** (`core.features` 147, `core.events` 13, `core.activities`
  12, `source_register.sources`/`feature_sources`). The high object count is mostly **views + the
  old per-layer MVP schema** sitting next to the new flexible one.
- The gold migration replaced 8 rigid per-geometry-type tables with ONE
  `core.features` (mixed `geometry(Geometry)` + `attrs`). The 8 originals are now **legacy
  leftovers holding stale/demo rows**, not the live data — but nobody has carried them out.
- This card retires them the **proven safe way** (the `core.pois` rename-and-reverify drop,
  `06_going_gold/gold_migration.md` DROP COMPLETE) — **one at a time, each drop-checked.**

#aop #cleanup #gold #postgis #legacy #deferred #schema

-----

## The finding (live counts, 2026-06-07)

| Legacy core table | rows | real successor | publish view |
|---|---|---|---|
| `core.trail_centerlines` | 4 (demo: "Demo Ridge Trail", "MVP Smoke…") | 120 real trails in `core.features` (layer='trails') | `publish.trail_centerlines` (2) |
| `core.trailheads` | 1 | — | `publish.trailheads` (0) |
| `core.park_boundaries` | 2 | (boundary render — **check first**) | `publish.park_boundaries` (1) |
| `core.parcels` | 2 | (parcel polygons — **check first**) | `publish.parcels` (0) |
| `core.hazards` | 0 | — | `publish.hazards` (0) |
| `core.observations` | 1 | — | (no view) |
| `core.field_tracks` | 2 | — | (no view) |
| `core.print_annotations` | 0 | — | (no view) |

The real data was imported into `core.features` **from the served `.geojson` files**, never from
these tables (`import_layer_to_core_features.py`) — so these were never the gold source; they hold
stale Sprint-01 MVP scaffolding. Only `hazards` + `print_annotations` are truly empty.

## Why this is NOT a redesign

The architecture is already right (Quartermaster + Mason): one flexible `core.features` beat eight
rigid per-geometry tables; `events`/`activities` are minimal Where/When/What normalization. This is
**dead furniture removal**, not a model change. Dropping these 8 (+ their views) takes the visible
count from 21 → ~13 without touching the live product.

## Plan (deferred — pull when the user wants the cleanup)

Per table, in this safety order, using the `core.pois` drop precedent:
1. **Confirm migrated/unused**: prove the table's content is either dead demo data OR already in
   `core.features` (and that the bake/website reads `features`, not the table). For
   `park_boundaries`/`parcels` this is the **gating check** — they may still back a curated polygon
   (the gold migration flagged the "Ellis Cemetery inholding" served-only gap) or a live render.
2. **Rename-and-reverify**: `ALTER … RENAME` the table + its publish view away → bake exit 0, no
   missing-object error, website renders identically (by observation) → restore byte-identical.
3. **Drop for real**: `DROP VIEW publish.<x>; DROP TABLE core.<x>;`; remove from `init_db.sql`
   (table + view + indexes + trigger-array entry); prove fresh-volume reproducibility.
4. Record per table; the commit + any owed are the user's git gate.

## Owed / not in scope
- Do **not** drop `park_boundaries`/`parcels` blind — each needs the step-1 content check first.
- `source_register`, `raw`, the 3 gold-spine tables, and the `publish.features` view all **stay** —
  they earn their place (provenance, capture, the live store of record, the publish gate).
- No `no_limiting_code` concern (this removes tables, adds no constraint).
