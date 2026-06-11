# Data source inventory — the x-ray of what's under the hood

The user asked to *see* every data source: which are real, which are paper mache, what shape each one
is. This card ships a reproducible inventory — generated from the live DB and the served files, never
from memory — and a browser page to read it.

**✅ SHIPPED + VERIFIED (2026-06-10).**

-----

## What shipped

- **`mvp/scripts/build_data_manifest.py`** — introspects the live PostGIS store (same
  `docker compose exec … psql` idiom as the bake) and scans `website/data/*.{geojson,json}`, emitting
  **`website/data/_data_manifest.json`** (schema `aop-data-manifest-v1`). Classifies each served file by
  origin: `core-backed` / `sidecar` / `runtime-buffer` / `raw-pipeline` / `served-other`. It is
  documentation, not a gate — an unrecognized file is inventoried as `served-other`, never dropped
  (C5/`no_limiting_code_mvp`). If the DB is down, the db section is marked unreachable and the served
  inventory still builds (honest partial, not a crash).
- **`website/data_sources.html`** — a self-contained inspector (no build step). Three sections: ① the
  PostGIS spine (tables, roles, columns, the `core.features` layer breakdown), ② served files grouped by
  origin with a "view real rows" button that lazy-fetches the actual file, ③ the CMFS crosswalk from
  `_schema.json` (how the legacy field names reconcile to canonical fields). A legend names the three
  layers of reality honestly, including that the client is the real debt.

## Scope

In: the inventory generator, the manifest, the viewer page. Out: fixing the client sprawl (that is
`client_layer_registry.md`); converging sidecars into core (earned later).

## Acceptance

[x] `build_data_manifest.py` runs clean and writes `_data_manifest.json` (db reachable: 8 tables;
    served: 31 files).
[x] `data_sources.html` renders all three sections from the manifest.
[x] Clicking a served file fetches the real file and renders its real feature rows.
[x] Origin classification is correct (6 core-backed, 6 sidecar, 1 runtime-buffer, 18 raw-pipeline).

## Verification (reproducible)

- `python3 mvp/scripts/build_data_manifest.py` → prints `db: reachable (8 tables)` / `served: 31 files`.
- `cd website && python3 -m http.server 8000`, open `http://localhost:8000/data_sources.html`.
- Headless observation (2026-06-10): a Playwright drive loaded the page, found the 3 section headers,
  40 cards, the stat strip (`8 DB tables · 160 rows in core.features · 31 served files · 6 core-backed ·
  18 raw/derived`), expanded `aop_buildings.geojson`, clicked **View real rows**, and rendered **5 real
  feature rows** from the fetched file. No console errors, no page errors. Screenshot at
  `/tmp/aop_data_sources.png` (not durable).

## Notes from implementation

- The manifest's `ORIGINS` and `CLIENT_LAYER` maps are maintained best-effort provenance — edit them
  when the bake changes. They are clearly labeled as such in the script; they classify, they never
  reject.
- `_schema.json` and `_data_manifest.json` are skipped by the served scan (leading `_` = meta, not a
  source).
- Re-run the generator after any bake or schema change to keep the x-ray honest.
