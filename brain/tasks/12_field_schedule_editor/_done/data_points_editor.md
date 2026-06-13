# Data points editor — the spreadsheet for points + tags

Sibling to the schedule editor (times). The user, adrift and asking for the *simplest* thing — *"I would
be happy with a spreadsheet editor for these data points… it does not need to be much"* — gets exactly
that: a static, offline, file-based grid editor for the point data (names, tags, coords). No database, no
server, no framework. Same proven pattern as `schedule_editor.html` (council-cleared this session).

**✅ SHIPPED + VERIFIED (2026-06-11).**

-----

## What shipped — `website/data_editor.html`

- A spreadsheet grid: a file dropdown (populated from `data/_data_manifest.json` — every served GeoJSON
  with features, 22 files), one row per feature, columns **Name · Tag · Kind · Lat · Lng · Description**.
- Edit cells inline; **＋ Add point** (new Point at park centre); delete row (confirm); **⤓ Export file**
  (downloads the edited GeoJSON to replace the served file → deploy); **↺ Reset** to published.
- **Round-trip safe:** edits only the shown fields in place on the parsed FeatureCollection; every other
  property + the geometry of non-points round-trips untouched (`getVal`/`setVal` preserve, never rebuild).
  Tag writes back to `category` if that's the key the feature already uses, else `tag` (non-limiting).
- **Lat/Lng editable only for Point features**; for polygons/lines the coord cells are read-only (greyed)
  — "geometry edited on the map, not here" — so a grid edit can't mangle a shape.
- **Auto-saves every keystroke** to `localStorage['aop_dataedit::<file>']` (debounced 250 ms) + a
  `pagehide`/`visibilitychange` flush (the field-hardening carried from the schedule editor) so no edit
  is lost on close. Per-file override; switching files keeps each file's edits separate.
- Static, offline (reads PWA-cached files), no server. Does NOT touch `main.js`/`panel.js`.

## Fits the user's actual workflow (files are the truth, DB optional)

Edit locally → Export the file → drop into `website/data/` → bake/deploy. No DB round-trip required (per
the 2026-06-11 "files are the truth, the database is an optional tool" decision in this session). The DB
stays available for the heavy normalization/spatial work; hand-authored points/tags/times now have small
direct-to-file editors.

## Acceptance

[x] Loads any served feature file via the manifest dropdown (22 files); renders features as an editable
    grid; default `publish.geojson`.
[x] Edit a cell → auto-saves → **survives reload**; Add point → +1 row; switch file → loads it; Reset.
[x] Round-trip preserves unshown properties + non-point geometry; Lat/Lng read-only for non-points.

## Verification

- `cd website && python3 -m http.server 8000`, open `http://localhost:8000/data_editor.html`.
- Headless (2026-06-11): 22 files in dropdown; default `publish.geojson` (6 rows); edited a Name →
  auto-saved to `localStorage` → **reload persisted** (src "your edits"); Add → 7 rows; switched to
  `aop_cemeteries.geojson` → 8 rows; no console/page errors. PASS. Screenshot `/tmp/aop_data_editor.png`.

## Council done-review (2026-06-11) — CLEAR (5 seats)

Witness/Quartermaster/Warden/Scribe clear. Mason andon was a dead-code-only finding (two unused vars in
`addPoint`) — FIXED + re-verified (add-point still adds a row and focuses the new Name cell). Mason
confirmed all the real risks pass: round-trip preserves every unshown property + non-Point geometry; the
`tag`/`category` write-back is lossless in all cases; lat/lng `setVal` is a confirmed no-op on
polygons/lines; no row-dropping filter / validator / throw; Export serializes the full FeatureCollection.
Quartermaster: not a third editor (no map/viewer coupling, manifest reuse, shared pattern is acceptable
self-contained copy — no module system to share into). Receipt: this card + handoff.

## Owed (same as the schedule editor)

- PWA precache (add `./data_editor.html` to `sw.js` SHELL_ASSETS) + the user's VERSION bump, once the
  shape is confirmed. UNCOMMITTED (user's git gate).
