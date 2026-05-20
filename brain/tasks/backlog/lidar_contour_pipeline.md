# Lidar Contour Pipeline

Generate lidar-grade contour lines for the AOP 9-patch from the USGS 3DEP 1-meter DEM and ship them as a viewer layer alongside the existing AWS Terrarium hillshade and 3D terrain. The hillshade gives shape; contours give the high-quality topography lines AOP riders and event planners actually read at scale.

The tooling fork is real -- GDAL is not on this machine today, and the DEM tile is roughly half a gigabyte. This card sequences the decision and the work so neither happens by accident.

#aop #tasks #backlog #lidar #contours #dem #gdal

-----

## Source

- `../../research/aop_data_bounds.md` -- 9-patch AOI, parcel envelope, and the existing lidar layers ("Lidar Tile Index Layer", "Lidar Hillshade and 3D Terrain Layers").
- `../../output/aop_9_patch_data_acquisition_manifest.md` -- exact USGS 1-meter DEM URL, size, and quad coverage.
- `../../handoff/session_context.md` -- entry from 2026-05-20 capturing why the viewer pivoted to AWS Terrarium hillshade and why contours were deferred.
- `../01_mvp/aop_south_pittsburg_map_build_card.md` -- stage 2 ("Base Map Assembly") names DEM hillshade and contours as deliverables; this card is the contours half.

Captured 2026-05-20.


## Scope

- AOI: full 9-patch bbox `-85.782935283, 35.067164188, -85.717154097, 35.117928496`. The user has confirmed full-patch coverage, not parcel-only.
- Vertical datum and interval: first pass at 5-foot interval with a 25-foot indexed (major) contour. Revisit 2-foot only if 5-foot proves too coarse for RC scale micro-terrain.
- Source elevation: USGS 3DEP 1-meter DEM tile `USGS_one_meter_x61y389_TN_27County_blk4_2015.tif` (~500 MB, one tile covers the 9-patch).
- Out of scope here: trail extraction, drainage modelling, viewshed work, raw LAZ point-cloud rendering. Those are downstream of this card.


## Decisions

### 1. GDAL toolchain?

**Suggested:** Docker `osgeo/gdal:alpine-small-latest` driven from `mvp/scripts/` wrappers.

**Why:** The MVP already runs in Docker (PostGIS via `mvp/docker-compose.yml`). A pinned GDAL image stays version-stable for everyone touching the pipeline, leaves zero host footprint, and matches the spinup runbook's "everything via Docker" shape. `brew install gdal` is faster per command but pulls a large dependency tree onto one developer's machine and drifts on every other contributor's.

**Alternatives:**
- **`brew install gdal` on macOS hosts:** Wins on speed and ergonomics in QGIS sidecar workflows. Loses on reproducibility across contributors and CI.

### 2. Ship format for the contour layer?

**Suggested:** Start with simplified GeoJSON at `website/data/aop_contours.geojson`. If the simplified file exceeds about 25 MB, pipeline through tippecanoe into PMTiles and serve via `pmtiles://` source in MapLibre.

**Why:** GeoJSON keeps the static viewer simple and matches the existing layer shape (`publish.geojson`, `aop_lidar_tiles.geojson`, `aop_9_patch.geojson`). PMTiles is the right escape hatch once payload becomes the bottleneck; the build card already names PMTiles as part of the long-term stack.

**Alternatives:**
- **PMTiles from day one:** Cleaner at scale, but adds tippecanoe to the toolchain before we know whether GeoJSON is actually too heavy.
- **Server-side raster tile rendering of contours:** Avoided -- the project promise is source-traceable vector data, not pre-rendered images.


## Open Questions

- Does the 1-meter DEM project file need reprojection before `gdal_contour`, or is its native CRS already compatible with the WGS84 9-patch bbox clip? Answer with `gdalinfo` after the toolchain decision lands.
- Should indexed-contour elevations be labeled in the viewer at higher zooms, or kept clean and only show in popups? Defer until the layer is live and we can judge legibility against the lidar hillshade and satellite layers.
- For 5-foot contours over ~34 km² of plateau-edge terrain, what is the simplified GeoJSON size in practice? This determines whether we stay on GeoJSON or jump to PMTiles.


## Acceptance

- [ ] **GDAL toolchain decision recorded** in `brain/spinup/mvp_runbook.md` with the exact invocation pattern (e.g. `docker run --rm -v <pwd>:/data osgeo/gdal:alpine-small-latest gdal_contour ...`).
- [ ] **DEM cache landed** outside the published repo tree (`mvp/cache/dem/USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`) with the cache directory in `.gitignore` and the SHA noted in the manifest.
- [ ] **Clipped DEM** for the 9-patch written next to the cache, with the clip bbox and CRS recorded.
- [ ] **Contours generated** at 5-foot interval, with an indexed-contour attribute (boolean or 25-foot remainder) on every line, output to GeoPackage.
- [ ] **Ship-format decision** recorded -- GeoJSON file size + simplification settings, or PMTiles build command + tile size budget.
- [ ] **Viewer layer wired** at `website/index.html` as a toggleable `Lidar contours (1m DEM)` layer with attribution and minor/indexed styling. Source provenance recorded in `core.sources` if it lands in PostGIS, otherwise documented in `brain/research/aop_data_bounds.md`.
- [ ] **Brain updates** -- new subsection in `brain/research/aop_data_bounds.md` describing the contour layer, plus a closing note in `brain/handoff/session_context.md` when the work happens.


## Verification

- Reproducible CLI:
  - `gdalinfo <clipped_dem>.tif` -- confirm CRS, pixel size 1 m, and extent fully covers the 9-patch bbox.
  - `ogrinfo -so <contours>.gpkg <layer>` -- confirm feature count, elevation field, and indexed-contour flag.
  - `du -h website/data/aop_contours.geojson` (or `pmtiles show <file>.pmtiles`) -- confirm payload is inside the ship-format budget chosen in Decision 2.
- Browser verification: extend `mvp/scripts/playwright_verify_lidar_tiles.py` to toggle the contour layer and assert either a non-zero rendered feature count (GeoJSON path) or a non-zero tile-network response (PMTiles path), and add a before/after screenshot pair under `brain/output/playwright_lidar_contours_*.png`.
- Spot-check at zoom 15 over the parcel envelope: indexed contours readable against the lidar hillshade, minor contours not visually noisy, sample elevation values match the AWS Terrarium 3D surface within expected datum drift.
