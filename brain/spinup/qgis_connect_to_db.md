# Connect QGIS to the AOP database — the real grip on the data

TL;DR:
- This closes the never-done MVP backlog item 3 ("connect QGIS to `localhost:55432`"). It is the tool
  the northstar always meant for editing the data — the in-browser editor was a workaround built because
  this was never set up.
- QGIS is a free desktop GIS that connects **straight to PostGIS** and edits it with a GUI — no code, no
  export/re-import. The browser can't write to a database directly (it edits a copy + a script folds it
  back in); QGIS writes to the source of truth itself.
- Connection (verified 2026-06-10 from the host with `psql`): host `localhost`, port `55432`, db
  `aop_map`, user `aop`, password `aop`, SSL disabled.

#aop #spinup #qgis #postgis #data #editing

-----

## Prerequisites

- The dev DB is up: `mvp-db-1` exposes `0.0.0.0:55432->5432`. Start it if needed:
  `docker compose -f mvp/docker-compose.yml up -d`.
- QGIS installed. It is NOT installed by default on this machine. Install (the user runs this — a Bash
  agent is permission-blocked from installing apps):

  ```
  brew install --cask qgis
  ```

  (~1.5 GB download; first launch is slow while it builds its index. No restart needed.)

## Connect — the 30-second path (import the prepared connection)

1. Open QGIS.
2. In the **Browser** panel (left), right-click **PostgreSQL** → **Load Connections…**
3. Pick `brain/spinup/assets/qgis/aop_postgis_connection.xml`.
4. A connection **"AOP map (local PostGIS)"** appears. Expand it → expand the **core** schema →
   double-click (or drag) **features** onto the map.

## Connect — the reliable manual path (if the import hiccups)

Browser panel → right-click **PostgreSQL** → **New Connection…**, then:

| field | value |
|---|---|
| Name | `AOP map (local PostGIS)` |
| Host | `localhost` |
| Port | `55432` |
| Database | `aop_map` |
| Authentication → Basic | username `aop`, password `aop` (tick "Store") |
| SSL mode | `disable` |

Tick **"Also list tables with no geometry"** (so `core.events` / `core.activities` /
`source_register.sources` show up too). **Test Connection** → **OK**. Expand the connection.

## What you'll see

- **`core.features`** — the converged spine, the store of record. ~159 live features across 12 layers
  (trails 120, cemeteries 8, event 6, buildings 5, visitor 4, trail_centerlines 4, park_boundaries 3,
  poi 3, …). This is the layer you edit.
- **`publish.features`** — the published-only view (read-through; edit `core.features`, not this).
- **`tiger.*`** — PostGIS's bundled US Census sample tables. **Not ours — ignore them.**

## Edit the data (this is "taking hold of it")

1. Click `core.features` in the Layers panel.
2. Toggle **Edit** (the yellow pencil in the toolbar).
3. Select a feature → edit its fields in the attribute form, or move/reshape its geometry on the map.
4. **Save** (Ctrl/Cmd+S, or the save-edits button). It writes **straight to the database** — no export,
   no bake step, no copy. The change is in the source of truth immediately.
5. Open the full table any time: right-click `core.features` → **Open Attribute Table**.

Note: `core.features.geom` is mixed-geometry (points, lines, polygons in one table), so QGIS loads it as
one layer. Existing features edit fine. To **add a new** feature of a specific type, either filter the
layer by geometry (right-click → Filter, e.g. `GeometryType(geom)='ST_Point'`) or add the typed sublayer.
This is a v1 nicety, not a blocker.

## Why this lets the browser editor retire

The website stays the **read-only viewer** the northstar promised. Curation/editing moves here, to QGIS
on the live DB — the intended design. Once you've confirmed QGIS gives you the grip you wanted, the
~3,000-line in-browser editor (`website/js/panel.js` + the editor regions of `main.js`) can be deleted
rather than maintained. See `tasks/_done/11_client_convergence/client_layer_registry.md`.

## Verification (reproducible)

From the host (proves the exact path QGIS uses):

```
PGPASSWORD=aop psql -h localhost -p 55432 -U aop -d aop_map -c "select layer, count(*) from core.features where archived_at is null group by layer order by 2 desc;"
```

2026-06-10: connected as `aop` to `aop_map`; `geometry_columns` lists `core.features` and
`publish.features` (SRID 4326); the per-layer counts above returned. The connection works; only the QGIS
install remains (the user's `brew` step).
