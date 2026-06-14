# Satellite 9-patch → Illustrator hand-trace export (+ round-trip)

Started: 2026-06-14
Status: SHIPPED + **first real Affinity round-trip ingested** (2026-06-14, verified
by observation — see "First real round-trip" below: 130 trails / 26 waypoints / 6
buildings, importer hardened for Affinity's export). Export + import originally
verified by observation. **Council-cleared**
(Witness · Quartermaster · Mason clear; Warden clear-in-isolation — the andon was
on a concurrent session's commingled tree, not this work; receipt
`brain/output/council/illustrator_trace_export.md`). Mason andon → fixed: the
importer now carries full gold props forward (provenance-preserving re-merge).
UNCOMMITTED — user's git gate; no `.council-cleared` marker written because the
tree is commingled with another session's unreviewed `website/`+`mvp/` changes.

The user wants to hand-trace the AOP satellite over the real imagery in Adobe
Illustrator, refining the gold trail network and placing waypoints/buildings, then
re-import — using the **layer names** as the truth. Their words:

> "make a export of the satellite map 9 patch for illustrator hand tracing.
> include gold trails / waypoints / buildings. I will edit and we will make gold.
> the names need to be the layer names. I will edit in illustrator and on
> re-import we use those."

This is the satellite + Illustrator sibling of the paper-map / Inkscape extraction
(`tasks/20_deferred/paper_map_trail_extraction.md`). Same round-trip idea, new
backdrop (NAIP satellite, not the SFWDA paper map) and a UTM frame instead of the
mesh warp.

## What ships

Two scripts, mirroring `export_trace_svg.py` / `import_trace_svg.py`:

- `mvp/scripts/export_illustrator_trace.py` → writes
  `brain/output/illustrator_trace/aop_satellite_trace.svg` (~9.2 MB) +
  `satellite_9patch.jpg` (standalone backdrop). Open the SVG in Illustrator. Each
  trail group also carries `data-fid` (its stable gold id) so re-import can
  re-merge provenance even after a rename.
- `mvp/scripts/import_illustrator_trace.py` → reads the edited SVG back to
  GeoJSON. Default writes `website/data/aop_trail_network.geojson` (the gold
  network); `--all` also emits `aop_waypoints_traced.geojson` +
  `aop_buildings_traced.geojson`. **Provenance-preserving:** each trail's edited
  geometry + name are the new truth, but its other gold props (`color`,
  `maturity`, `permission`, …) are carried forward from the prior gold feature it
  matches (by `data-fid`, then name) — a round-trip does NOT strip provenance.
  A user-drawn-new trail (no match) gets thin "needs review" provenance.

Run, edit, re-import:
```
python3 mvp/scripts/export_illustrator_trace.py
# … trace / refine / rename layers in Illustrator, save SVG …
python3 mvp/scripts/import_illustrator_trace.py path/to/edited.svg
python3 mvp/scripts/export_gold_trail_network.py   # re-stamp the gold _meta
```

## The SVG

Four `<g>` layers, top → bottom: **Satellite** (locked NAIP ortho), **Buildings**
(5 in-park footprints), **Waypoints** (5 named point POIs), **Gold Trails**
(120 lines, coloured by difficulty). The category layers are the ONLY groups.

**Each feature is ONE named geometry OBJECT — a `<path>` or `<circle>`, no wrapper
group, NO drawn text.** The name is the object name, written in every channel an
editor surfaces: `id` (Illustrator's `_xHH_` Layers-panel name + SVG round-trip),
`inkscape:label` (Inkscape), `serif:id` (Affinity), `<title>` child. So "Front
Office" is the polygon object itself, named — not a text item on the artboard
(the user's 2026-06-14 correction: *"the Front office should be a polygon named
correctly as a object name not a physical document object"*). Verified: the SVG
contains **0 `<text>`/`<tspan>` elements** and 0 wrapper groups inside the category
layers. Unnamed trails carry their feature id (`sfwda-N`) as the placeholder
object name to rename.

## Data sources

| Layer | File | Notes |
| --- | --- | --- |
| Satellite | `mvp/cache/imagery/naip_2023_9patch.tif` | NAIP 2023, 4-band, **EPSG:26916** (NAD83/UTM 16N), 3996×3742 px @ 1.525 m/px. Gitignored cache. |
| Gold Trails | `website/data/aop_trail_network.geojson` | 120 LineStrings, `maturity:gold`, `color`+`difficulty`+`name`/`trail_number`. |
| Buildings | `website/data/aop_buildings.geojson` | 5 in-park footprints (665, 889 Ellis Cove, Front Office, Farmhouse, Pavilion). |
| Waypoints | `publish.geojson` POIs + `aop_cemeteries.geojson` markers + `aop_editor_seed_pois.geojson` | deduped by name → AOP Pavilion, Ellis/Tate/Bible/Gilliam Cemetery. |

## Frame / projection (the load-bearing part)

The SVG frame **IS the raster's own CRS** — UTM 16N metres, origin at the raster
NW corner (read from the GeoTIFF `ModelPixelScale`/`ModelTiepoint`), `x = E − E₀`,
`y = N₀ − N`. Because the frame is the raster grid, vectors land 1:1 on the imagery
with **no raster resampling** (full pixel fidelity) and the `<image>` places at the
pixel box. Vector lng/lat → UTM is done with a self-contained transverse-Mercator
series (GRS80, lon₀ −87°, k₀ 0.9996) — **no GDAL/pyproj on this machine** (Docker
down too). The projection params live in the SVG `<metadata>` so import inverts in
lock-step. Datum note: vectors are WGS84, projected with NAD83/GRS80 params — the
~1 m CONUS datum slip is sub-pixel at 1.5 m/px and accepted.

**Shared frame (2026-06-14):** the raster-read + backdrop-embed + projection
`<metadata>` was extracted into a `RasterFrame` class in `export_illustrator_trace.py`
so the sibling vegetation exporter (`export_landcover_svg.py`,
`tasks/01_mvp/_done/landcover_layer.md`) reuses the exact same UTM-16N frame instead
of re-implementing it. This exporter's `main()` now calls `RasterFrame` too. The
refactor is **output-neutral**: the HEAD pre-refactor script and the refactored
script bake `aop_satellite_trace.svg` to the **identical md5** on the same inputs.
(A fresh bake differs from the *committed* SVG only because a concurrent session
edited this exporter's input `aop_trail_network.geojson` — independent of the
refactor; verified by the council Witness, 2026-06-14.)

## Verified by observation (2026-06-14)

- **Projection:** forward∘inverse round-trips sub-mm; the documented 9-patch bbox
  falls fully inside the raster frame (raster is slightly larger than the AOI).
- **Alignment:** building footprints sit on real structures and the pavilion
  marker in the staging field; the trail mass sits on the wooded park ridge
  (`brain/output/illustrator_trace/_verify_buildings_3x.png`, `_verify_overlay.png`).
  This is gross registration confirmed by eye — at 1.5 m/px a footprint is a few
  pixels, so "on the structure" is what the image proves, not pixel-exact rooftop
  registration.
- **Round-trip:** export → import (in memory, source file untouched) gives
  120/120 trails, 0 vertex-count mismatches, **max vertex error ~0.91 cm** (the
  2-decimal metre rounding in the path `d`), 100/120 names exact (the 20 are the
  genuinely-unnamed trails on their placeholder id), waypoints 5/5 and buildings
  5/5 names exact. **Provenance carry** re-verified after the council fix: all 120
  re-imported trails keep `maturity`/`color`/`permission` (props re-merged from the
  prior gold by `data-fid`). `ai_escape`/`ai_unescape` round-trips incl. spaces,
  digits, hyphens, `#`, `/`, and a leading-underscore name (`_15`).
- **SVG structure:** 4 layers, 1 embedded `<image>`, every feature group carries
  all three name channels (0 missing).

## First real round-trip — Affinity Designer (2026-06-14)

The user hand-traced in **Affinity Designer** and dropped the edited export at
`brain/import/trace_upload/aop_satellite_trace.svg` (+ the `.afdesign` master).
Affinity's SVG export differs hard from the generated one; the importer was
hardened to ingest it (the card's "confirm against the first real edited file"):

- **`<metadata>` stripped** → `load_meta` falls back to the original export's frame
  (deterministic: same raster + fixed UTM params). **Frame is intact — no rescale:**
  Affinity rounded the viewBox (`6092.6`→`6093`) but did NOT rescale geometry, so the
  frame applies 1:1. Evidence: the unedited originals reproject onto HEAD's committed
  geometry at the SVG's own quantization floor — the path `d` carries 2-decimal-metre
  coords, so a vertex returns within **~1–2.4 cm** of HEAD (sub-pixel at 1.5 m/px).
  Larger per-vertex deltas are the user's **real hand-edits**, not frame error (e.g.
  Ground Control moved ~1 m; trail 67 + two others changed vertex counts). *(The
  separate **0.7 cm** figure is the importer's in-memory self-round-trip — export→
  reimport without saving — NOT a measurement of the committed gold file; don't
  conflate them.)*
- **Names moved onto wrapper `<g>`s.** Affinity wraps every *moved/new* object in
  `<g transform=… serif:id="Name">` with the name on the wrapper, geometry (no name)
  inside. `walk` now carries an **inherited name** down to the leaf and composes the
  wrapper transform, so grouped features (Front Office, Shower House, all new
  waypoints) keep their names instead of importing as `None`.
- **Layer match.** `collect_layer` also matches `serif:id` + the dash-id (Affinity
  renamed `id="Gold-Trails"`, kept `serif:id="Gold Trails"`).
- **Provenance w/o `data-fid`** (Affinity strips `data-*`): match order is now
  data-fid → exact name → name-as-prior-id (unnamed `sfwda-N`) → **leading trail
  number** (carries gold lineage through a rename like `Launchpad`→`1 Launchpad`).
- **Number-prefix normalization.** The export names a trail by its plain name
  (`Launchpad`); the user re-prefixed the number for legibility (`1 Launchpad`).
  The viewer label already composes `<n> name`, so the importer strips a leading
  `<trail_number> ` → stored name reverts to `Launchpad`, label renders `1 Launchpad`
  (no `1 1 Launchpad`). Stable round-trip.
- **Stray-POI sweep.** Waypoint `<circle>`s are swept from **every** editable layer,
  so two entrance pins drawn into the Gold Trails layer (`Jeep Entrance`,
  `Buggy Entrance`) are ingested, not silently dropped.

**Ingested (verified by observation):** `aop_trail_network.geojson` = **130**
trails (120 gold-provenance carried incl. all 8 renamed, **10** new user-traced —
9 unnamed + the de-identified long-67), `aop_waypoints_traced.geojson` = **26**
named POIs, `aop_buildings_traced.geojson` = **6** (incl. moved Front Office +
new Shower House). The live viewer ingests all 130 and renders them with clean,
un-doubled labels, **0 fatal console errors** (`brain/output/verify_ingest_viewer.py`
PASS, 195 trail feats rendered); the satellite overlay shows correct registration +
sensible placement (`brain/output/illustrator_trace/_verify_ingest.png`,
`_verify_ingest_camp.png`).

**Trail 67:** the user split it — a short 14-vertex segment keeps `67` (gold), the
long 65-vertex original they de-named in Affinity → imports as a blank/unknown new
trail (their call: *"the short is 67 the long should be blank/unknown"*).

**Re-import is read-modify-write on `aop_trail_network.geojson`** (it reads the live
gold as the provenance baseline), so run it **once against the committed baseline** —
re-running on its own output drifts provenance. To redo: restore from HEAD first
(`git show HEAD:website/data/aop_trail_network.geojson > …`), then import once.

**Wired into the read viewer (2026-06-14, user: "I am not seeing it in the map"):**
The new POIs were INVISIBLE for two reasons — (1) the service worker precaches the
data files and only refreshes on a `VERSION` bump (so the cached app served the old
v83 data), and (2) the waypoints had **no layer**. Fixed:
- **Waypoints** → new `aop-waypoints` source + `aop-waypoints` (circle) +
  `aop-waypoints-labels` (symbol) layers in `viewer_core.js` (mirrors the
  trail-network/water-points pattern), reading `aop_waypoints_traced.geojson`,
  shown in every preset. Added to the `sw.js` `DATA_ASSETS` precache.
- **Shower House** → merged into the WIRED `aop_buildings.geojson` (NOT a swap — a
  swap would strip the existing 5 buildings' FEMA/ORNL address+facility provenance);
  added as one raw-zone feature (the other 5 untouched). The user's refined Front
  Office *geometry* was left for later (the existing footprint already renders).
- **Cache bump** `v83`→`v84` (`sw.js` `VERSION` + `index.html` `#appVersion`) so the
  new trail/waypoint/building data is served past the cache-first SW.
- **Verified by observation:** `brain/output/verify_waypoints_layer.py` PASS on
  `:8001` — `aop-waypoints` + labels exist, **26/26 render**, Shower House present
  (6 buildings), 0 fatal console errors; `_verify_waypoints_live.png`. `node --check`
  clean on `viewer_core.js`.

**Owed / next (left for the user's call):**
- **10 new trails need names + difficulty** (currently grey / needs-review).
- **Waypoints are a flat raw-zone marker layer** — richer POI-tab integration
  (blurbs, kinds/icons, grouping, search) is the next slice, gated by
  `northstar/source_register.md`. The trace `permission` is still "SFWDA — TBD".
- **Front Office** refined geometry from the trace not yet applied (cosmetic;
  existing FEMA footprint still renders).
- **The `v84` bump + commit are the user's git gate** (uncommitted).
- `AOP Pavilion` waypoint was deleted by the user (the Pavilion *building* stays).

## Open / next

- **The user edits, then we re-import.** `import_illustrator_trace.py` is built and
  self-round-trip-verified, AND now proven against the first real Affinity export
  (see above). The importer composes ancestor transforms, inherits wrapper names,
  and reduces curves to endpoints.
- **Raster choice.** NAIP 2023 (1.5 m/px, on-disk, offline) is the default. The
  viewer's sharper **TNMap 2022 6-inch** is online-tiles only (licensing =
  inspection, not republish) — swap in if the user wants more detail for tracing.
- **Waypoints are thin** (5). They're the only named point POIs that exist; the
  user will add/rename more by hand.
- **Promotion still owed** — same as the paper-map card: the trace is raw-zone,
  not `publish`; the gold network's `permission` is still "SFWDA paper map —
  permission TBD".

Sources/voice: `northstar/source_register.md`, `research/aop_data_bounds.md`,
`tasks/20_deferred/paper_map_trail_extraction.md`.
