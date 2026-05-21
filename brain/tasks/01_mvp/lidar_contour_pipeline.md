# Lidar Contour Pipeline

Generate lidar-grade contour lines for the AOP 9-patch from the USGS 3DEP 1-meter DEM and ship them as a viewer layer alongside the existing AWS Terrarium hillshade and 3D terrain. The hillshade gives shape; contours give the high-quality topography lines AOP riders and event planners actually read at scale.

The tooling fork is real -- GDAL is not on this machine today, and the DEM tile is roughly half a gigabyte. This card sequences the decision and the work so neither happens by accident.

#aop #tasks #mvp #lidar #contours #dem #gdal

-----

**Status: DONE (2026-05-20; smoothing + crossing repair 2026-05-21).** Picked up
from the backlog and completed this session. Contours are live in the viewer; see
the Outcome section, then the 2026-05-21 Update section, for the current state.

## Source

- `../../research/aop_data_bounds.md` -- 9-patch AOI and parcel envelope.
- `../../research/viewer.md` -- the viewer's layer catalog, including the existing lidar layers ("Lidar Tile Index Layer", "Lidar Hillshade and 3D Terrain Layers").
- `../../output/aop_9_patch_data_acquisition_manifest.md` -- exact USGS 1-meter DEM URL, size, and quad coverage.
- `../../handoff/session_context.md` -- entry from 2026-05-20 capturing why the viewer pivoted to AWS Terrarium hillshade and why contours were deferred.
- `aop_south_pittsburg_map_build_card.md` -- stage 2 ("Base Map Assembly") names DEM hillshade and contours as deliverables; this card is the contours half.

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

**Decided:** Docker, but `ghcr.io/osgeo/gdal:ubuntu-small-latest`, not `alpine-small`.
Two corrections to the suggestion: (1) Docker Hub `osgeo/gdal` is stale (newest tag
is 3.6.3) -- the project now publishes current images to GitHub Container Registry.
(2) `alpine-small` ships without GEOS, so `ogr2ogr -simplify` fails; `ubuntu-small`
includes GEOS. macOS also blocks Docker from reading the repo under `~/Documents`, so
the pipeline stages all GDAL work in `/private/tmp`. Full pattern in `brain/spinup/mvp_runbook.md`.

### 2. Ship format for the contour layer?

**Suggested:** Start with simplified GeoJSON at `website/data/aop_contours.geojson`. If the simplified file exceeds about 25 MB, pipeline through tippecanoe into PMTiles and serve via `pmtiles://` source in MapLibre.

**Why:** GeoJSON keeps the static viewer simple and matches the existing layer shape (`publish.geojson`, `aop_lidar_tiles.geojson`, `aop_9_patch.geojson`). PMTiles is the right escape hatch once payload becomes the bottleneck; the build card already names PMTiles as part of the long-term stack.

**Alternatives:**
- **PMTiles from day one:** Cleaner at scale, but adds tippecanoe to the toolchain before we know whether GeoJSON is actually too heavy.
- **Server-side raster tile rendering of contours:** Avoided -- the project promise is source-traceable vector data, not pre-rendered images.

**Decided:** GeoJSON. Unsimplified the file was 160 MB, but a 3 m Douglas-Peucker
simplification brought it to ~5.0 MB -- far under the ~25 MB threshold -- so no
tippecanoe/PMTiles step was needed. (Later revised: the smoothing + crossing-repair
pass moved the ship setting to a 0.5 m simplification; the shipped file is ~14 MB,
still under the threshold. See the Update section below.)


## Resolved Questions

- **Reprojection before `gdal_contour`?** No. `gdalinfo` showed the DEM is
  `NAD83 / UTM zone 16N` (EPSG:26916), 1 m pixels. Contours are generated in that
  native CRS; the clip accepts the WGS84 9-patch bbox via `gdalwarp -te_srs EPSG:4326`,
  and the final GeoJSON is reprojected to EPSG:4326 with `ogr2ogr -t_srs`.
- **Label indexed contours?** Yes. Index (25 ft) lines carry an `elev_ft` label in
  the viewer (MapLibre collision-culls overlaps); every contour also answers a click
  popup. Minor lines stay unlabeled.
- **Simplified GeoJSON size?** Unsimplified: 160 MB. At 1.5 m / 3 m / 6 m
  Douglas-Peucker the file first shipped at 3 m (~5.0 MB) -- GeoJSON, no PMTiles
  needed. Superseded by the crossing-repair pass (0.5 m DP, ~14 MB) -- see the
  Update section below.


## Acceptance

- [x] **GDAL toolchain decision recorded** in `brain/spinup/mvp_runbook.md` with the exact invocation pattern (e.g. `docker run --rm -v <pwd>:/data osgeo/gdal:alpine-small-latest gdal_contour ...`).
- [x] **DEM cache landed** outside the published repo tree (`mvp/cache/dem/USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`) with the cache directory in `.gitignore` and the SHA noted in the manifest.
- [x] **Clipped DEM** for the 9-patch written next to the cache, with the clip bbox and CRS recorded.
- [x] **Contours generated** at 5-foot interval, with an indexed-contour attribute (boolean or 25-foot remainder) on every line, output to GeoPackage.
- [x] **Ship-format decision** recorded -- GeoJSON file size + simplification settings, or PMTiles build command + tile size budget.
- [x] **Viewer layer wired** at `website/index.html` as a toggleable `Lidar contours (1m DEM)` layer with attribution and minor/indexed styling. Source provenance recorded in `core.sources` if it lands in PostGIS, otherwise documented in `brain/research/viewer.md`.
- [x] **Brain updates** -- new subsection in `brain/research/aop_data_bounds.md` describing the contour layer, plus a closing note in `brain/handoff/session_context.md` when the work happens.


## Verification

- Reproducible CLI:
  - `gdalinfo <clipped_dem>.tif` -- confirm CRS, pixel size 1 m, and extent fully covers the 9-patch bbox.
  - `ogrinfo -so <contours>.gpkg <layer>` -- confirm feature count, elevation field, and indexed-contour flag.
  - `du -h website/data/aop_contours.geojson` (or `pmtiles show <file>.pmtiles`) -- confirm payload is inside the ship-format budget chosen in Decision 2.
- Browser verification: extend `mvp/scripts/playwright_verify_lidar_tiles.py` to toggle the contour layer and assert either a non-zero rendered feature count (GeoJSON path) or a non-zero tile-network response (PMTiles path), and add a before/after screenshot pair under `brain/output/playwright_lidar_contours_*.png`.
- Spot-check at zoom 15 over the parcel envelope: indexed contours readable against the lidar hillshade, minor contours not visually noisy, sample elevation values match the AWS Terrarium 3D surface within expected datum drift.


## Outcome

Completed 2026-05-20.

- `mvp/scripts/build_contours.sh` -- reproducible pipeline: cache DEM, clip to the
  9-patch, `gdal_contour` at 5 ft, attribute (`elev_ft` + `idx`), simplify, export.
- `website/data/aop_contours.geojson` -- 6,376 contour LineStrings, 605-1820 ft,
  ~5.0 MB. Properties `elev_m`, `elev_ft`, `idx` (1 = indexed 25-ft line).
- `mvp/cache/contours/aop_contours.gpkg` -- full-resolution attributed GeoPackage
  (gitignored archival / QGIS product). `mvp/cache/dem/dem_9patch.tif` -- clipped DEM.
- `website/index.html` -- `Lidar contours (5 ft, 1m DEM)` toggle, layers
  `contours-minor` / `contours-index` / `contours-labels`, click popup with elevation.
- `mvp/scripts/playwright_verify_lidar_tiles.py` extended to cover contours; the
  2026-05-20 run reported all checks PASS with 4,170 contours rendered in-viewport
  and 0 console errors. Screenshots: `brain/output/playwright_lidar_contours_off.png`,
  `playwright_lidar_contours_on.png`, `playwright_lidar_contours_satellite.png`.
- Brain: `brain/research/viewer.md` "Lidar Contour Layer"; GDAL toolchain in
  `brain/spinup/mvp_runbook.md`; DEM SHA in `brain/output/aop_9_patch_data_acquisition_manifest.md`.

Follow-ups (not blocking): revisit a 2-foot interval if 5 ft proves too coarse for
RC-scale micro-terrain; the contour layer is a candidate to swap onto AOP-specific
1 m DEM tiles alongside the hillshade (`brain/tasks/01_mvp/_readme.md` item #10).


## Update: smoothing and crossing repair (2026-05-21)

The first-pass contours (above) read as jagged, and a later check found ~955
places where contours of different elevation crossed -- impossible on a real
surface. Two fixes folded into `build_contours.sh`:

- **Smoothing.** The clipped DEM is low-pass smoothed (resampled 1 m -> 2 m with
  `gdalwarp -r cubicspline`) before `gdal_contour`, stripping the lidar
  micro-noise that crinkled the isolines.
- **Crossing repair.** Simplification dropped to a light 0.5 m Douglas-Peucker
  pass, then `mvp/scripts/repair_crossings.py` restores any crossing segments to
  raw geometry, iterating to zero.

Current shipped file: `website/data/aop_contours.geojson` -- 2,831 LineStrings,
605-1820 ft (501 indexed), ~14 MB, 0 crossings. Still GeoJSON, still under the
~25 MB threshold. The viewer schema (`elev_m` / `elev_ft` / `idx`) did not change.
Full detail in `brain/research/viewer.md` ("Lidar Contour Layer") and
`brain/handoff/session_context.md`.
