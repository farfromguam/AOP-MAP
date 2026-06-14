# Satellite 9-patch → Illustrator hand-trace export (+ round-trip)

Started: 2026-06-14
Status: SHIPPED (export + import, verified by observation). **Council-cleared**
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

## Open / next

- **The user edits, then we re-import.** `import_illustrator_trace.py` is built
  and self-round-trip-verified, but its real test is the user's *Illustrator-saved*
  SVG (Illustrator may rewrite `id`/transforms/curves — the importer composes
  ancestor transforms and reduces curves to endpoints like the paper-map importer,
  but confirm against the first real edited file).
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
