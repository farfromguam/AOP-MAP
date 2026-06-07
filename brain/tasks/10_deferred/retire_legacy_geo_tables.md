# Retire the legacy per-layer geo tables (the "so many tables" cleanup)

> **Source:** council consult 2026-06-07 — the user, looking at the full table diagram, said
> *"how do we have so many tables… I am at a loss."* The council (Witness·Quartermaster·Mason,
> Steward-chaired) grounded the answer in live row counts. This card is the cleanup it surfaced.
> **Status: DEFERRED** — a safe, one-at-a-time drop, each gated on a content-migrated check.

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
