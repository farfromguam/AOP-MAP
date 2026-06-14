# Land-cover layer + Muted Earth restyle

Started: 2026-05-21
Status: DONE (2026-05-21)

Turn the viewer's satellite imagery into a vector land-cover layer (a forest
mass), and restyle the whole viewer into a muted, vintage park-map palette.

#aop #landcover #naip #vector #viewer #restyle #editor-is-the-viewer

-----

## Why now

The user asked to "take our satellite photos and download them so we can make
vector versions and make a layer that is vector" and wanted a
"stylized/muted/pastel park map palette."

Reframe: you cannot vectorize a photo directly. The imagery becomes a
*classification source*. The map was already almost entirely vector (roads,
water, contours, trails, parcels, cemeteries); the one missing piece for a
park-map look was the **land-cover mass** — forest vs. open ground — and a
unified palette.

Two decisions the user made when asked:
- Land cover: **auto-classify** the imagery (vs. hand-trace, vs. skip).
- Palette: **Muted Earth** — warm vintage kraft (forest `#b9c2a3`, paper
  `#efe7d5`, trail `#9a5a32`, contour `#ab9f7e`).
- Follow-up directive: "do a more thorough conversion so it's not so blobby."

## Imagery

NAIP 2021, 4-band (R/G/B/NIR), 0.6 m, acquired 2021-11-07, from the USGS NAIP
ImageServer (`USGSNAIPImagery`). This is the only no-auth 4-band source:
- 2023 NAIP (June, leaf-on — ideal) is behind an EarthExplorer login.
- The TNM products API no longer serves NAIP downloads (returns 0).
- TNMap 2022 ortho is RGB-only (no NIR) and also flown leaf-off.

The NIR band matters — it is what makes a clean forest classification possible.
The November acquisition is partial leaf-off; that is *worked with*, not around
(see below).

Download is the two-step ArcGIS pattern: a 12-megapixel mosaic will not stream
inline (`f=image` 500s), so the script requests `f=json` to trigger generation
and returns an `href`, then downloads the generated TIFF. Cached (gitignored)
at `mvp/cache/imagery/naip_2021_aop.tif` (~51 MB).

## Classification — forest as a neighbourhood-scale field

The hard part. Leaf-off deciduous canopy lets brown litter show between bare
branches, so a single 0.6 m pixel flips noisily between "rough" and "bare". A
naive pixel-scale classifier produced unusable salt-and-pepper speckle.

The working method (`mvp/scripts/classify_landcover.py`):
1. **Canopy roughness as a smooth field** — local NIR std-dev (texture), then a
   low-pass pass over that std-dev field. Forest is uniformly high, fields
   uniformly low. Texture is the forest signal because it survives leaf-off
   (bare canopy is still rough); NDVI does not (leaf-off forest NDVI collapses
   toward bare-ground values).
2. **Otsu threshold**, picked per-image so the pipeline adapts to exposure.
3. **Morphological cleanup** — a closing fills canopy-gap holes punched through
   the woods (leaf-off crowns), an opening drops forest specks stranded in
   fields. Closing fills holes *without* eroding real clearings or softening
   their edges — that is why it beats blur or a bigger modal filter.

Forest came out 57.6% raw -> 78.2% after morphology — realistic for a wooded
Cumberland Plateau cove.

Only **forest** is emitted. Open ground is left as the viewer's paper
background (in Muted Earth, clearing and paper are nearly the same warm tone).
**Water was deliberately dropped**: leaf-off NIR confuses water with shadow,
and the USGS NHD layer already carries hydrography properly.

Vectorizing (`mvp/scripts/build_landcover.sh`, `smooth_landcover.py`):
polygonize -> light 1.5 m vertex simplify -> Chaikin corner-cutting (de-
staircase) -> drop sliver polygons (<250 m²) and pinhole holes (<500 m², the
leaf-off-crown artefacts) -> clip to the AOP boundary (the Ellis cemetery hole
is respected). GDAL runs via Docker per `spinup/mvp_runbook.md`.

## What was added

- `website/data/aop_landcover.geojson` — 7 forest polygons, 63 interior holes
  (the real clearings), ~152 KB, clipped to the park boundary.
- `mvp/scripts/build_landcover.sh` — reproducible pipeline orchestrator.
- `mvp/scripts/classify_landcover.py` — NAIP -> forest class raster.
- `mvp/scripts/smooth_landcover.py` — Chaikin smooth + sliver/hole cleanup.
- `website/index.html`:
  - `landcover-forest` (fill) + `landcover-forest-outline` (line), added first
    so they sit at the base of the layer stack, above the paper background and
    below everything else.
  - Toggle `Forest land cover (NAIP)`, default ON — it is the base map.
  - **Muted Earth restyle** — paper background `#efe7d5`, and every existing
    layer's paint retuned into the warm vintage palette (water, contours,
    roads, trails, boundary, cemeteries, OSM, hillshade, POIs, search flash,
    text halos to warm off-white, panel accent).

## Verification

- `mvp/scripts/playwright_verify_landcover.py` — 19 checks, all PASS on
  2026-05-21, 0 console errors. Covers the toggle, base-of-stack layer order,
  the paper background colour, GeoJSON shape (forest-only, polygonal), render,
  toggle off/on, forest under satellite, forest under contours.
- Screenshots: `brain/output/playwright_landcover_*.png`.
- Classification preview eyeballed at `mvp/cache/landcover/preview.png` during
  tuning.

## Honest limitations / follow-ups

- Leaf-off November imagery is the real ceiling on quality. Texture
  classification has a ~15 m edge-softness floor; leaf-on 2023 NAIP would give
  crisper, NDVI-driven edges. Tracked in the backlog:
  `tasks/backlog/leaf_on_landcover.md`.
- No open/bare distinction — open ground is just paper. Parking lots and
  structures belong to the POI/footprint editor, not a land-cover class.
- Raw-zone layer. Before any promotion to `core`/`publish`, attach a
  `source_register` row (NAIP = USDA, public domain) per
  `northstar/source_register.md`.
- Tunables at the top of `classify_landcover.py` (`TEXTURE_RADIUS`,
  `CLOSE_RADIUS`, `OPEN_RADIUS`) and `smooth_landcover.py` (`MIN_HOLE_AREA`).

## Acceptance

- [x] NAIP 4-band ortho downloaded and cached.
- [x] `build_landcover.sh` runs and writes `aop_landcover.geojson`.
- [x] Forest reads as a coherent mass, not speckle (the "not blobby" ask).
- [x] Real clearings preserved as holes; leaf-off-crown dot-holes removed.
- [x] Viewer has a `Forest land cover` toggle, default ON, at the base.
- [x] Whole viewer restyled into the Muted Earth palette.
- [x] Playwright verification passes with 0 console errors.

## Update: 9-patch extension (2026-05-21)

The forest layer was extended to the full 9-patch acquisition AOI, not just
the park boundary. The user wanted forest data around the park, was fine with
the bounds being a separate layer, and wanted to dim the non-park areas.

- The NAIP ImageServer caps a single export at 4000 px. The 9-patch is ~6 km
  wide -- 0.6 m pixels would need ~10000 px -- so the 9-patch ortho is pulled
  at ~1.5 m: one 3996x3742 export covering the whole AOI. Coarser than the
  park layer by design; it ships under the crisp park layer at reduced
  opacity as context.
- `classify_landcover.py` was made resolution-aware: it reads the pixel size
  from the geotransform and rescales the texture/morphology window radii so
  the *metric* windows are held constant. At the 0.6 m reference size the
  scale is 1.0, so the park build stays byte-identical -- the park layer did
  not need rebuilding or re-verifying.
- New build script `mvp/scripts/build_landcover_9patch.sh` (sibling of
  `build_landcover.sh`): downloads the 9-patch NAIP, classifies, vectorizes,
  clips to the 9-patch rectangle. Output `website/data/aop_landcover_9patch.geojson`
  -- 70 forest polygons, ~80% cover, ~1.7 MB.
- Viewer: a separate `landcover-9patch-forest` layer at the very base of the
  stack (below the crisp park layer), toggle `Forest land cover — 9-patch
  (NAIP)` default ON, plus a 9-patch opacity control in that layer's edit
  drawer (default 55%).
  The park layer draws on top, so the control effectively fades only the
  non-park context. Full 9-patch coverage (not park-cut-out) so the layer is
  still complete if the park layer is toggled off.
- Verified: `playwright_verify_landcover.py` extended for the new layer, its
  base-of-stack order, and the drawer opacity control -- all checks PASS, 0
  console errors.
  Screenshots `brain/output/playwright_landcover_9patch_*.png`.
- Same leaf-off ceiling as the park layer, plus the coarser ~1.5 m resolution.
  Fine for a reduced-opacity context layer; the leaf-on backlog card
  (`tasks/backlog/leaf_on_landcover.md`) would lift both layers at once.

## Update: multi-shade land cover (2026-05-21)

The user noted the layer was a single green for all trees while the satellite
imagery shows fields in different colours, and asked to support varied field
colours and darker tree shades in some areas. They chose to do both the forest
and the field split now (rather than waiting for leaf-on imagery).

The layer went from binary forest/open to a **five-class coverage**:
`forest_deciduous`, `forest_evergreen`, `open_grass`, `open_meadow`,
`open_bare`. Every valid pixel now carries a class -- open ground is emitted as
polygons instead of being left as the paper background.

- `classify_landcover.py` gained a second stage. Stage 1 (forest vs open,
  canopy-roughness texture) is unchanged. Stage 2 sub-classifies by NDVI
  vigour, low-passed *within* each zone (a masked box mean) so the forest/open
  edge does not bleed across the split:
  - **Forest split** -- evergreen is the high-NDVI tail (top 20%, percentile,
    not Otsu: Otsu on leaf-off forest NDVI is not bimodal and split the woods
    ~50/50). Conifers keep their needles in November; bare hardwood canopy does
    not. The leaf-off conifer signal is weak and scattered, so the first
    attempt was dark-green confetti -- the fix is a stand-scale NDVI smooth
    (`FOREST_NDVI_RADIUS`) plus a heavy morphological consolidation
    (`FOREST_CLEAN_RADIUS`) that resolves the stipple into a few coherent
    stands. Park result: ~20% evergreen / ~80% deciduous.
  - **Open split** -- two Otsu cuts on within-open NDVI rank open ground into
    bare (low) / meadow (mid) / grass (high). Honest framing: this is a
    relative greenness ranking within one leaf-off image, not crop ID.
- `smooth_landcover.py` now keeps all five classes and no longer drops slivers
  or pinhole holes -- the layer is a coverage, so a dropped polygon would punch
  a gap and a dropped hole would overlap the class inside it. Speckle is
  handled upstream in the classifier instead. Chaikin still runs per ring; on a
  coverage it is near-topology-preserving (a shared edge is the same vertex run
  in both rings and Chaikin is local, so its interior smooths identically).
- Both build scripts changed `-where "DN = 1"` to `"DN > 0"` so every class
  vectorizes, and gained an `ogr2ogr -makevalid` pass: Chaikin can pinch a thin
  polygon into a self-intersection, which made the GEOS clip throw a
  TopologyException. The 9-patch build also simplifies harder (3 m, was 1.5 m)
  to keep its GeoJSON light -- it is a dimmed context layer.
- Viewer: the single-colour forest fill became a MapLibre `match` on `class`
  (one `LANDCOVER_FILL` expression reused by the park and 9-patch fills); each
  class gets a thin same-family outline that doubles as a hairline-gap bridge
  for the sub-pixel slivers independent vertex-simplify leaves on a coverage.
  Toggles relabelled `Land cover (NAIP)` / `Land cover — 9-patch (NAIP)`;
  9-patch opacity now lives in that layer's edit drawer. Layer ids kept
  (`landcover-forest` etc.) to avoid rippling the toggle map and verification
  script.
- Muted Earth class palette: `forest_deciduous` `#b9c2a3` (the existing sage),
  `forest_evergreen` `#7f8c66` (darker conifer green), `open_grass` `#cfd4b0`,
  `open_meadow` `#dccfa3`, `open_bare` `#cdba8f`.
- Output: `aop_landcover.geojson` 631 polygons / ~920 KB;
  `aop_landcover_9patch.geojson` 6420 polygons / ~7.8 MB.
- Verified: `playwright_verify_landcover.py` updated for the five classes --
  31 of 31 checks PASS, 0 console errors. Classification previews eyeballed at
  `mvp/cache/landcover/preview*.png` during tuning.
- Honest limit (unchanged): leaf-off November imagery is the ceiling. The
  evergreen/deciduous split is real but weak and only coherent after heavy
  consolidation; the open-ground split is a relative vigour ranking. Leaf-on
  2023 NAIP (`tasks/backlog/leaf_on_landcover.md`) would make both splits far
  more meaningful and crisp.
- Tunables added at the top of `classify_landcover.py`: `FOREST_NDVI_RADIUS`,
  `OPEN_NDVI_RADIUS`, `FOREST_CLEAN_RADIUS`, `OPEN_CLEAN_RADIUS`,
  `EVERGREEN_PERCENTILE`, and the `CLASS_RGB` preview palette.

## Update: lidar canopy-height rebuild (2026-05-21)

The user asked how the vector land-cover layer was being produced, said it was
"not quite right," and described the Illustrator workflow they would use:
threshold the trees off the fields, then posterise the remaining ground into
3-4 field colours. They added a new satellite dataset (USDA NAIP 2023) to
compare against. The layer was rebuilt around that workflow.

### What was found

- **Leaf-on imagery is better for the fields, worse for the tree mask.** The
  open-ground colour split (the user's step 2) automates cleanly on leaf-on
  imagery -- k-means colour quantisation, the field colours are real and
  separable. But the forest/open split (step 1) does **not** automate from
  leaf-on imagery. Four builds confirmed it:
  - Colour/brightness threshold fails -- leaf-on canopy in full sun is bright,
    not dark.
  - Texture (canopy roughness) fails -- leaf-on canopy is a smooth continuous
    blanket; its texture barely differs from a mown field, the histogram is
    unimodal, and Otsu lands in the tail (5-11% forest, should be ~80%).
  - The *old* pipeline only worked because it ran on leaf-**off** winter NAIP:
    bare branches make extreme texture, a clean separate mode. Leaf-on kills
    that signal.
- Separating leaf-on tree canopy from grass is a genuine remote-sensing limit
  from optical imagery alone. The fix is **tree height**: trees are tall,
  grass is not. The user chose the lidar canopy-height path.

### The new pipeline

- **`mvp/scripts/build_canopy_height.sh`** (new) -- builds a canopy-height
  model (CHM) from USGS 3DEP lidar. `build_canopy_height.sh [park|9patch]`:
  downloads the LAZ tiles (6 for the park, all 24 for the 9-patch, from
  `website/data/aop_lidar_tiles.geojson`), runs PDAL `filters.hag_delaunay`
  (height above a TIN of the ground-classified returns), grids the per-cell
  max height, mosaics, and warps onto the exact NAIP grid. Output cached at
  `mvp/cache/lidar/chm_aop.tif` / `chm_9patch.tif` (gitignored).
- **PDAL toolchain**: the `pdal/pdal` Docker image (PDAL 2.10 + GDAL 3.13).
  Same `/private/tmp` staging pattern as the GDAL work.
- **Vertical-datum gotcha**: the 3DEP lidar carries a compound CRS with a
  NAVD88 vertical component. GDAL 3.x, left to itself, reads the CHM raster as
  elevation data and applies a ~-30 m geoid shift to the pixel values. The
  warp forces `-s_srs EPSG:6576` (the 2D horizontal CRS) so the height-above-
  ground values pass through unchanged.
- **`classify_landcover.py`** stage 1 rewritten: forest = `CHM > 2.5 m`, a
  crisp per-pixel cut. The CHM is a stipple of crowns, so a morphological
  closing (radius 12) bridges inter-crown gaps into a coherent mass and an
  opening (radius 4) drops lone trees / specks. Closing preserves the outer
  boundary of a large object, so the forest edge stays crisp. Stage 2 is
  unchanged in spirit: evergreen = darkest canopy tail; open ground = k-means
  RGB colour quantisation into grass/meadow/bare, majority-voted into solids.
- **Imagery moved to USDA NAIP 2023** (`USDA_CONUS_PRIME` ImageServer): June,
  leaf-on, 4-band, 0.6 m, no-auth `exportImage`. Cached
  `mvp/cache/imagery/naip_2023_aop.tif` / `naip_2023_9patch.tif`.
- `build_landcover.sh` / `build_landcover_9patch.sh` updated: new NAIP source,
  and each now ensures its CHM exists (runs `build_canopy_height.sh`) and
  passes it to the classifier as a second input.

### Output

- `aop_landcover.geojson` -- park, 154 polygons / ~420 KB, ~81% forest. The
  forest mass is coherent with a crisp lidar-cut edge; the fields are clean
  k-means colour polygons. (Was 631 speckled polygons on the leaf-off build.)
- `aop_landcover_9patch.geojson` -- rebuilt from the 24-tile 9-patch CHM.
- Viewer: class ids/names unchanged, so `LANDCOVER_FILL`/`LANDCOVER_OUTLINE`
  and the toggles were untouched; only the attribution strings updated to
  "USDA NAIP 2023 + USGS 3DEP lidar".
- Verified: `playwright_verify_landcover.py` PASS, 0 console errors.

### Honest limits

- The 3DEP lidar is from 2015; canopy grown or cleared since is not captured
  (the NAIP imagery is 2023, so colour and canopy are 8 years apart).
- The CHM threshold catches any tall object -- a large barn reads as a small
  forest patch; the opening drops house-sized specks, big structures survive.
- The open-ground colour split is still a relative ranking within one image,
  not absolute crop ID.
- Tunables at the top of `classify_landcover.py`: `CANOPY_HEIGHT_M`,
  `CLOSE_RADIUS`, `OPEN_RADIUS`, plus the stage-2 radii and k-means settings.

-----

## Update: vegetation simplification (2026-06-14)

The user's call: the five-class ground cover (two greens, three browns) is too
busy. Combine the two greens into one **vegetation** layer and let every
non-tree area read as the base map paper.

- **Data mutation, not a paint trick.** `mvp/scripts/simplify_landcover_vegetation.py`
  reads the 5-class GeoJSON, keeps the two forest classes, dissolves them with a
  shapely `unary_union` (touching deciduous/evergreen merge into one shape),
  explodes the union back to polygons, re-tags every feature `class=vegetation`,
  and drops the three open classes. Top-level `name`/`_meta` preserved (group
  label kept so the panel grouping + data manifest are unaffected; maturity stays
  `derived`). Idempotent guard: refuses to write if no forest features are present.
- **Result.** Park `aop_landcover.geojson`: 154 → 18 features (435 KB → 105 KB).
  9-patch `aop_landcover_9patch.geojson`: 3430 → 165 features (4.5 MB → 891 KB).
  Both carry only `class=vegetation`.
- **Pipeline wired.** The simplify is the final step of `build_landcover.sh` and
  `build_landcover_9patch.sh`; the 5-class export is kept in the gitignored cache
  (`mvp/cache/landcover/*.5class.geojson`), so a rebuild stays simplified instead
  of reverting. The 5-class source is recoverable from git + the cache + the
  pipeline.
- **Viewer.** `viewer_core.js` land-cover paint collapsed from a 5-class
  `match` on `class` to a flat vegetation green per preset (`#b8c1a1` Park /
  `#c0c6ad` Topo; outlines `#a6af8d` / `#aeb499`). `main.js` / `panel.js` (editor
  host, mid-port) still carry the old `match`; with single-class data it falls
  through to the same green — cleanup owed when the editor ports into the read core.
- **Not limiting code.** This is a directed simplification of a *derived* layer.
  `ai_rules/no_limiting_code_mvp.md` defers the display call to the user ("we want
  everything to display for now" was *their* call; dropping non-tree here is too).
- **Verified by observation (2026-06-14).** `playwright_verify_landcover.py`
  updated to the vegetation contract (single class, retired sub-classes gone,
  flat-green fill, base-of-stack, render counts; editor-only sections guarded so
  it runs against the read viewer `index.html` or the editor host
  `old_index.html`). All substantive checks PASS on the live `:8001` read viewer
  (single `vegetation` class both files, flat green `#b8c1a1`, 9-patch at base of
  stack, 18/165 render). The verifier's own console-summary line did not flush
  under a temp-fs tail hang, so the council Witness re-ran a clean Playwright
  capture (`console.error` + `pageerror`) and observed **0 console errors**.
- **Owed (user's git gate):** commit. `sw.js` VERSION + `#appVersion` were bumped
  for the data change (a contributor advanced both to `v80`). NB the Warden
  flagged the Tier-0 clearance hash spans the whole `website`+`mvp` tree (other
  sessions' uncommitted work) — isolate this into its own commit (`git add -p`).
