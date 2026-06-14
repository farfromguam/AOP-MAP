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
- **Committed.** The user committed this pass as **`da5d032 v79`** (the data
  files, `simplify_landcover_vegetation.py`, the `viewer_core.js` flat-green
  paint, the verifier update, and this card addendum). Not owed — it shipped.

-----

## Update: corner rendering fix (2026-06-14)

The user reported the vegetation showed empty top-right / bottom-right /
bottom-left corners and patches "popping" at different zooms — and that the
**satellite shows dense trees in those areas**. It was a real rendering bug, not
open ground:

- **Root cause.** The first pass dissolved all forest with `unary_union`, which
  merged the near-continuous mountain canopy into a single polygon of ~28,000
  vertices and ~282 interior holes. MapLibre's `fill` tessellation silently drops
  chunks of a polygon that complex, so large parts of the canopy never rendered —
  the empty corners. (Verified: forest *area* was present in all four quadrants of
  the data, so geometry wasn't missing — it wasn't being drawn.)
- **Fix (data only).** `simplify_landcover_vegetation.py` now, after the union,
  caps per-polygon complexity: drop interior holes below ~5000 m² (`HOLE_MIN_DEG2`
  — small noise clearings; filling them also reads truer to the dense canopy the
  imagery shows) and lightly Douglas-Peucker simplify the edge (`SIMPLIFY_DEG`
  ~3 m). Worst-case polygon went 28107 verts / 282 holes → **3976 verts / 47
  holes** (9-patch) and 3228/10 → **187/0** (park) — back in the range that always
  rendered (the open classes peaked at 2343/46). Coverage unchanged (±0.1% area).
  The script prints the worst-case verts/holes each build so a regression toward
  the tessellation-breaking shape is visible.
- **Verified by observation (2026-06-14).** A fresh render agent drove the live
  `:8001` viewer (Region preset + z12.4/13/14/15, `window.AOPViewer.map`): the
  previously-empty TR/BR/BL corners now fill with green, the canopy reads as one
  continuous mass (not a central blob with bites), coverage is stable across zoom
  (no blink-out), **0 console errors**. Before/after shots:
  `brain/output/diag_veg_region_preset.png` (broken) vs
  `brain/output/veg_fixed_region_preset.png` + `veg_fixed_z124_lite.png` (fixed);
  receipt `brain/output/council/witness_vegetation_render.md`.
- **Committed** as **`692464b v81`** (HEAD carries the 3976/47 data; working tree
  is clean against it). `sw.js`/`#appVersion` now `v82` (later contributor bumps).
  No outline/viewer change was needed — the fix keeps the natural forest edge, so
  the existing outline still traces it.

## Update: corner rendering fix, part 2 — subdivide the fill (v83, 2026-06-14)

The v81 complexity cap was **not enough**. The user reported the same empty
corners again ("all but top right have un-natural rendering errors ... satellite
confirms there are trees here"). Observed on the live `:8001` viewer at the Region
zoom: the whole 9-patch canopy rendered as only a **central blob** (the small
park-clipped `landcover-forest`), while the wide `landcover-9patch-forest` —
still one ~3976-vertex / 47-hole polygon after the v81 cap — drew almost nothing.

- **Real root cause.** A *single* fill polygon that large+holey still degenerates
  in MapLibre's per-tile earcut tessellation (lines never hit this — which is why
  the OLD outline always drew while the fill vanished). Capping vertex count alone
  doesn't fix it; you have to stop shipping the canopy as one giant fill polygon.
- **Fix (data, `simplify_landcover_vegetation.py`).** After the union + dehole +
  simplify, the cleaned mass is now **grid-subdivided** for the fill: any polygon
  over `SUBDIVIDE_VERTS` (600) is clipped into `GRID_DEG` (~0.006° ≈ 550 m) cells,
  so every emitted fill piece is small. The dissolved canopy **edge** is emitted
  separately as `role:"outline"` LineString features. 9-patch: 1 giant → **324
  fill pieces + 1 outline, worst piece 202 verts / 3 holes**; park unchanged
  (18 pieces, ≤187 verts — under the threshold, not subdivided). Adjacent pieces
  share exact edges (no overlap → no opacity seam).
- **Viewer (`viewer_core.js` + `main.js`).** The two fill layers filter to
  `['==',['geometry-type'],'Polygon']`; the two `-outline` line layers filter to
  `['==',['geometry-type'],'LineString']` — so the outline traces the true canopy
  edge, NOT the subdivision grid. Both hosts updated (same files feed both).
- **Verified by observation (v83, 2026-06-14).** `:8001`, fresh SW-cold context:
  the 9-patch fill renders in **all four quadrants** (was centre-only) — quadrant
  hit-counts TL/TR/BL/BR all ≥3; **354 features render across the AOI**; render is
  fast (fitBounds 1.0 s, screenshot 0.5 s — no slow/hung tessellation); **0 console
  errors**. Region screenshot `brain/output/v5_region.png` shows continuous canopy
  to every corner. Canonical `playwright_verify_landcover.py` updated to the new
  contract (polygons + a line outline; "no giant fill polygon" + "subdivided into
  small pieces" guards) → **23 PASS, RESULT: PASS** (also fixed two pre-existing
  Map-serialization hangs in that verifier — `fitBounds`/`zoomTo` arrows returned
  the Map). `sw.js`/`#appVersion` v82→**v83**. **UNCOMMITTED** (user's git gate).

## Update: vegetation → editable SVG round-trip (2026-06-14)

The user: *"I need the landcover exported to a svg so I can edit it. there are
some polygons that need to be manually resolved. we have been working towards a
single green for treecover."* They want to hand-resolve the tree-cover polygons in
a vector editor (Illustrator/Inkscape/Affinity) against the satellite.

- **What gets edited is the dissolved canopy, NOT the shipped GeoJSON.** The viewer
  `aop_landcover*.geojson` is grid-subdivided into many small fill pieces purely so
  MapLibre's earcut renders the canopy everywhere (the corner-fix, above) — a render
  workaround, not an editable shape (nobody hand-edits 324 grid cells). The editable
  "single green for tree cover" is the **dissolved canopy mass**: the forest classes
  unioned, clearings as holes — exactly what `simplify_landcover_vegetation.clean_parts()`
  builds *before* it subdivides.
- **`mvp/scripts/export_landcover_svg.py` (new).** Re-dissolves from the gitignored
  5-class cache (`mvp/cache/landcover/*.5class.geojson`), and writes each canopy
  polygon as ONE named, filled, editable compound `<path>` (exterior + holes,
  `fill-rule:evenodd`) in a **Vegetation** layer over a locked **Satellite** backdrop.
  `python3 export_landcover_svg.py [park|9patch|both]` → `brain/output/landcover_trace/`.
  Park `aop_landcover_trace.svg` (6.4 MB, **18 polys**, ≤187 verts); 9-patch
  `aop_landcover_9patch_trace.svg` (9.3 MB, **165 polys**).
- **Reuse, not a second pipeline.** The projection + satellite-backdrop machinery
  was extracted from `export_illustrator_trace.py` into a shared `RasterFrame` class
  (the raster's own **UTM 16N** grid, JPEG backdrop, round-trip `<metadata>`); the
  trail-trace exporter now calls it too. The dissolve/clean comes from
  `simplify_landcover_vegetation` (`FOREST_CLASSES`, `clean_parts`); the viewer
  feature contract (grid-subdivide fill + LineString outline) was extracted there
  into a shared `vegetation_features()` used by both the 5-class bake and the
  re-import.
- **Both refactors are output-neutral (verified, precise framing).** Running the
  refactored script vs the HEAD pre-refactor script on the **same current inputs**
  produces byte-identical output: `simplify_landcover_vegetation` re-bakes the
  committed `website/data/aop_landcover*.geojson` byte-for-byte, and
  `export_illustrator_trace` bakes the trail-trace SVG to the identical md5 under
  both versions. **Caveat (council Witness, 2026-06-14):** a *fresh* trail-trace
  bake no longer matches the **committed** `aop_satellite_trace.svg` — but the cause
  is a **concurrent session editing that exporter's input** (`aop_trail_network.geojson`),
  **not** this refactor (proven: HEAD and refactored scripts bake the identical md5
  to each other on the live input). "Behavior-preserving" here means
  refactored-equals-predecessor, which is what was checked.
- **`mvp/scripts/import_landcover_svg.py` (new)** closes the loop: reads the edited
  Vegetation layer back, inverts the UTM frame from the SVG `<metadata>` (no warp),
  unions the hand-resolved polygons, and re-bakes the viewer file via
  `vegetation_features()` (target park vs 9-patch read from the SVG meta). It reads
  its OWN metadata (does **not** fall back to the trail-trace frame like the trail
  importer — that frame is the 9-patch raster and would mis-place a park edit).
- **Verified by observation (2026-06-14).** Durable verifier
  `mvp/scripts/verify_landcover_svg_roundtrip.py` (not transcript-only — a re-runnable
  script that exits non-zero on regression; uncommitted per the user's git gate)
  observes the actual SVG files: poly + ring-count
  parity, **max Hausdorff 0.912 cm** (the 2-dp-metre path-rounding ceiling, same as
  the trail trace), canopy area drift **~0%** (park 2.117 km²/523 ac, 9-patch
  28.1 km²/6944 ac) → **RESULT: PASS**. Export→import of the *unedited* SVG
  reproduces the viewer contract (park 18 fill + 1 outline = live 19; 9-patch 323
  fill + 1 outline vs live's 324 — a one-grid-cell difference from the cm-level
  rounding, not a content change). Rendered the park SVG (Playwright): the green
  overlays the forest canopy, the cleared park staging area + fields read as bare
  satellite, the stroke traces the canopy edge — `brain/output/landcover_trace/_render_park_{full,crop}.png`.
- **Next: the user edits in Illustrator, then `import_landcover_svg.py` re-bakes the
  viewer file** (importer is self-round-trip-verified; its real test is the first
  editor-saved SVG, exactly as with the trail trace). **UNCOMMITTED** (user's git gate).

### Update: first hand-edit ingested + lightweight preview page (2026-06-14)

The user resolved the **9-patch** vegetation by hand in **Affinity Designer** and
dropped it back at `brain/import/trace_upload/aop_landcover_trace.svg` (+ the
`.afdesign` master): **165 → 159 polygons** (merged/deleted ~6 by hand). Affinity's
export keeps the `Vegetation` layer + per-shape names (`serif:id="Vegetation N"`) but
**strips the projection `<metadata>` and the embedded satellite** — and adds a
near-identity layer transform — exactly like its trail-trace export. The edited SVG's
viewBox (`0 0 6093 5706`) **is** the 9-patch raster's metre grid, so the shapes still
register 1:1 on the satellite with no georeferencing.

The user asked for "a dedicated lightweight page that uses this … I want to see what
it does." Built `mvp/scripts/build_landcover_edit_preview.py`: pulls the `Vegetation`
group + frame from the edited SVG and writes a **self-contained, dependency-free**
page (`brain/output/landcover_trace/landcover_edit_preview.html`) that re-attaches the
satellite backdrop (`satellite_9patch.jpg`, by reference — does NOT need the stripped
metadata/raster) and overlays the edited shapes, with wheel-zoom + drag-pan and
toggles for satellite / fill-vs-outline / opacity. **Extraction assumption (council
Mason):** the generator pulls the one flat `<g id="Vegetation">` group as raw markup
(Affinity emits paths-only, no nesting). If a future editor exports *nested* groups,
re-flatten the Vegetation layer before previewing rather than expecting the
non-greedy group grab to capture nested children. **Verified by observation:**
rendered at `:8002`, the green tracks the canopy and pulls off the cleared
fields/staging, edges hold at 23× zoom, **0 console errors**
(`brain/output/landcover_trace/_preview_{default,outline,zoom}.png`). This is a
*preview*, not the viewer re-bake — wiring the edit back into the viewer still goes
through `import_landcover_svg.py` (which needs the stripped frame recovered from the
9-patch target; owed when the user wants it in the map). **UNCOMMITTED** (git gate).

### Update: standalone MapLibre render test — raw vs subdivided (2026-06-14)

The user: *"test it in a map. no opacity no borders. make the color a light sagey
color. the past time we put a high vertex image into the map it caused rendering
issues. we test it separately first. then integrate after success."* Right instinct:
**158 of their 159 edited shapes are tiny (<50 verts), but one is the 3969-vertex /
48-subpath canopy mass** my export handed them — the same giant+holey single fill
polygon the v79→v83 saga blamed for MapLibre earcut dropping the corners.

Built `mvp/scripts/build_landcover_map_test.py`: recovers the stripped 9-patch frame
(`RasterFrame`), inverts the edited SVG to lng/lat (reuses `import_landcover_svg.read_polys`),
and emits TWO geojsons + a standalone MapLibre page (`brain/output/landcover_trace/landcover_map_test.html`,
local vendored maplibre, satellite as an offline `image` source) that flips between
**RAW** (the 159 shapes, monster intact) and **SUBDIVIDED** (union + grid-subdivide via
the shared `vegetation_features` → 317 small fill pieces, worst 202 verts). Fill is
**solid light sage `#cfdabf`, no `fill-outline-color`, `fill-opacity:1`** — per the ask.

**Verified by observation (`:8003`, 0 console errors):** SUBDIVIDED renders the full
canopy across all four quadrants — clean, the integration-ready form
(`_maptest_sub_nosat.png`, `_maptest_sub_sat.png` over imagery). **Notable:** in this
isolated single-layer test the **RAW 3969-vert monster also rendered fully** — overview,
z13, z14, and the historically-empty TR/BL corners all filled, no dropped chunks
(`_maptest_raw_nosat.png`, `_rawzoom_*.png`). So the old bug did **not** reproduce here
(it may need the live viewer's two-layer + maxBounds + Region-preset state). **Recommendation
for integration: ship the SUBDIVIDED form regardless** — it's the proven, de-risked shape
(what the viewer already bakes, verified across zooms in v83) and renders identically
clean; betting on the raw monster because one isolated test passed isn't worth it.
**Next (on the user's go): integrate** — teach `import_landcover_svg.py` to recover the
9-patch frame (same `RasterFrame` recovery this test uses), bake → `aop_landcover_9patch.geojson`,
bump `sw.js`/`#appVersion`. Sage tone is one constant (`SAGE`) — trivial to retune.
**Factor-forward (council Quartermaster):** `build_landcover_map_test.recover_frame()` and
`import_landcover_svg.load_meta()` are the two halves of one frame-recovery decision —
at integration, expose ONE shared recovery (a `recover_frame(target)` both call) instead
of `load_meta` re-implementing the raster fallback it currently `sys.exit`s on.
**Council-reviewed:** this map-test delta cleared all four seats (Witness · Warden ·
Mason · Quartermaster), 2026-06-14. **UNCOMMITTED** (git gate).

### Update: INTEGRATED into the viewer — subdivided + `#D1D2B8` (2026-06-14)

The user: *"integrate it, ship the subdivided form. make the green this color: D1D2B8."*

- **Data baked.** `import_landcover_svg.py brain/import/trace_upload/aop_landcover_trace.svg
  --target 9patch` recovered the Affinity-stripped frame and re-baked
  `website/data/aop_landcover_9patch.geojson` → **318 features (317 fill + 1 outline)**,
  `_meta.maturity = hand-resolved`, replacing the machine bake (was 325). The park layer
  (`aop_landcover.geojson`) is **unchanged** — the user only hand-edited the 9-patch; the
  crisp park canopy still draws on top of it in the park area (same green, so it reads as
  one mass; a park-layer edit is a separate future ask).
- **Shared frame recovery (Quartermaster's factor-forward, done).** `recover_frame(target)`
  now lives once in `export_landcover_svg.py`; `import_landcover_svg.load_meta(root, target)`
  calls it when the SVG metadata is stripped (new `--target` flag), and
  `build_landcover_map_test.py` imports it instead of its own copy. No duplicate recovery.
- **Colour.** All four landcover paint constants in `viewer_core.js`
  (`LANDCOVER_{MUTED,RELIEF}_{FILL,OUTLINE}`) set to **`#D1D2B8`** — one light-sage green,
  fill == outline so there's no contrasting border (the outline still bridges sub-pixel
  grid slivers, invisibly). `node --check` clean.
- **Opacity unchanged (a noted fork).** The viewer composites vegetation at its existing
  per-preset opacity (9-patch 0.55 / park 0.9 in Park; 0.38 / 0.62 in Topo), so `#D1D2B8`
  reads as a soft wash — fainter than the solid (opacity-1) map test the user approved.
  Left as-is because the ask was data+colour, not opacity; flagged to the user to crank
  solid if they want the test's punchier look.
- **Version.** A concurrent session bumped the shared `sw.js`/`#appVersion` to **v86**
  (its facility-label work) *after* these edits landed in the same files, so v86 ships the
  landcover changes too — no separate bump.
- **Verified by observation (`:8001`, SW-cold).** `getPaintProperty` → both landcover fills
  `#D1D2B8`; the 9-patch fill renders across the full AOI (sage canopy, tan fields/clearings
  cut out, no dropped corners — `brain/output/landcover_trace/_integrate_aoi.png`); **0
  console errors**. The canonical `playwright_verify_landcover.py` has stale hard counts
  (expects the old 324-piece bake) → owed a count refresh to 317.
- **Commingled tree / git gate.** `viewer_core.js` + `sw.js` + `index.html` are shared with
  the concurrent illustrator-trace/waypoints session; my landcover hunks were the colour
  constants + the data file (`aop_landcover_9patch.geojson`) + the three scripts. The user
  has since **committed** the whole `website/`+`mvp/` tree — the `#D1D2B8` constants landed
  in **v84** (`59e4686`) and v86 carries them forward; `git status` for `website`/`mvp` is
  clean. What is still **UNCOMMITTED** is this brain record (the card + `handoff/session_context.md`
  + the `brain/output/landcover_trace/` PNGs) — the brain's own write, the user's git gate.
- **No tessellation bug in the REAL viewer (the user's actual worry).** The earlier map
  test was isolated/single-layer; the council Witness independently drove the real
  two-layer viewer (`:8001`, SW-cold) and confirmed the high-vertex shape renders fully:
  `querySourceFeatures('aop-landcover-9patch')` = 822 loaded, `queryRenderedFeatures`
  non-zero in **every** quadrant + both tight corners, screenshots show sage to every
  edge with clearings cut out — **no dropped corners/chunks**, 0 console errors. The
  v83 empty-corner bug did **not** appear with the subdivided form in the live viewer.
- **Council: all five seats clear** (Witness · Warden · Quartermaster · Mason · Scribe),
  2026-06-14. Scribe pulled one andon — the card's earlier "UNCOMMITTED" line was false
  (the tree was already committed as v84) — corrected in place (this block).

### Update: opacity iteration — solid → "slight on the non-park" (2026-06-14)

After the committed `#D1D2B8` integration, the user iterated the compositing:

1. *"probably no opacity — I calculated the color with none accounted for."* → set all
   landcover fill-opacity to **1 (solid)** so `#D1D2B8` renders as the true value (Park +
   Topo presets, both park + 9-patch layers; slider defaults 100; initial paints 1).
   `sw.js`/`#appVersion` **v86→v87**. UNCOMMITTED.
2. *"there should be some opacity for the non-park areas … just slight … enough so we don't
   have to make a border. make some mockups."* → the **park layer stays solid**; the
   **9-patch (non-park) opacity** is the variable, and the opacity step at the park
   boundary becomes the separator (no drawn border). Built an interactive chooser
   `brain/output/landcover_trace/mockups/compare.html` (standalone MapLibre — the full
   viewer hangs headlessly on `setPaintProperty`, and live flipping is better for "I'll
   choose styles"): park solid `#D1D2B8`, non-park opacity preset buttons 100→60 + slider,
   paper/satellite backdrop. Served `:8005`, 0 console errors.
- **Finding (durable): grid-subdivided fill shows opacity SEAMS at <100%.** MapLibre
  antialiases each fill piece's shared edge, so adjacent subdivided pieces double their
  edge alpha when transparent → a faint ~550 m grid appears at <100% (verified: visible at
  70%, near-gone at 95%, absent at 100%). **Fix: `fill-antialias: false`** on the fill
  layers — pieces then tile seamlessly at any opacity (verified clean at 70% in the
  chooser). This must go into `viewer_core.js` when the non-park opacity drops below 100%.
- **Pending the user's pick.** When the user names a non-park %, set
  `landcover-9patch-forest` fill-opacity to it (park stays 1) + `fill-antialias:false` on
  both landcover fills, in Park + Topo, bump version, verify. The live viewer (`:8001`)
  currently shows the non-park **solid** (step 1) — the intermediate state until the pick.
- **Council (opacity delta, 2026-06-14): Witness · Mason · Scribe clear** (viewer renders
  solid `#D1D2B8` at opacity 1 both layers; chooser + `fill-antialias:false` seam-fix
  verified; record honest). **Warden andon — commingled tree:** the uncommitted
  `viewer_core.js` bundles the concurrent session's unrelated work (trail `display_name`
  unification, event-selection change, popup-close) + modified `aop_waypoints_traced.geojson`
  / `aop_event_schedule.json`. That session also **removed the landcover outline layers +
  `LANDCOVER_*_OUTLINE` consts** — it edits the same landcover paint as this work (the
  removal aligns with the no-border direction, but it isn't this task's change). My
  landcover-opacity hunks (fill-opacity→1, slider→100, v87) are gate-ready on their own;
  the rest belongs to the other session and should be committed separately (`git add -p`).
  **No `.council-cleared`** — the Tier-0 hash spans all of `website/`+`mvp/`, i.e. the
  commingled tree, so stamping it would falsely certify the other session's code.
