# The AOP Viewer

TL;DR:
- `website/index.html` is the static MapLibre viewer -- one file, vendored
  libraries, no build step, runs offline.
- It shows three publishable layers from `publish.geojson` plus ~15 toggleable
  reference layers, has a feature search box, and an in-map POI/footprint editor.
- This is the viewer's home doc: the layer catalog. Per-layer build detail that
  has its own task card is linked, not duplicated.

#aop #viewer #maplibre #layers #reference

-----

## What the viewer is

`website/index.html` is the Website V1 surface from the build card: a static
MapLibre map, read-only over `publish.geojson` plus an editing mode. It is a
single HTML file with an inline `<script>`, MapLibre and Terra Draw vendored
under `website/vendor/`, and no build step. It reads GeoJSON straight from
`website/data/` and works with no network -- a hard requirement, see
`[[project-offline-requirement]]`.

Editing is a mode inside this viewer, not a separate app -- see
`[[feedback-editor-is-the-viewer]]`. The POI editor and the SFWDA alignment
editor both live here.

Serve it with `python3 -m http.server` from `website/`; see
`spinup/mvp_runbook.md`.

When a layer is added, changed, or removed in `index.html`, update the inventory
and detail below in the same pass. This catalog is only useful while it matches
the file.

## Layer inventory

Default-ON layers are marked; everything else is OFF until toggled, so the
viewer opens cleanly with no network. "Detail" points to the doc that records
how the layer was built.

| Toggle label | Data / source | Default | Detail |
| --- | --- | --- | --- |
| Publishable trails | `publish.geojson` (`core` -> `publish` views) | on | build card; `northstar/source_register.md` |
| Publishable boundaries | `publish.geojson` | on | build card |
| Publishable trailheads | `publish.geojson` | on | build card |
| Drawn POIs | `localStorage` + editor export | on | `tasks/01_mvp/poi_editor.md` |
| Asphalt roads (USGS National Map) | `aop_roads.geojson` | on | "Asphalt Roads Layer" below |
| 3D terrain (AWS Terrarium / USGS 3DEP) | AWS Terrain Tiles | off | "Lidar Hillshade and 3D Terrain Layers" below |
| Lidar hillshade (USGS 3DEP) | AWS Terrain Tiles | off | "Lidar Hillshade and 3D Terrain Layers" below |
| Lidar contours (5 ft, 1m DEM) | `aop_contours.geojson` | off | `tasks/01_mvp/lidar_contour_pipeline.md`; "Lidar Contour Layer" below |
| Satellite imagery (TNMap 2022) | TNMap XYZ tiles | off | "Satellite Imagery" below |
| 9-patch acquisition AOI | `aop_9_patch.geojson` | off | "9-Patch Acquisition AOI Overlay" below |
| Lidar tile index (USGS 3DEP) | `aop_lidar_tiles.geojson` | off | "Lidar Tile Index Layer" below |
| Streams & waterbodies (USGS NHD) | `aop_water.geojson` | off | "Hydrography / Water Layer" below |
| Springs & gages (USGS NHD) | `aop_water.geojson` | off | "Hydrography / Water Layer" below |
| Cemeteries (TN Comptroller parcels) | `aop_cemeteries.geojson` | off | `tasks/01_mvp/cemeteries_layer.md`; "Cemeteries Layer" below |
| OSM park polygon | `osm_aop_9patch.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| OSM tracks (highway=track) | `osm_aop_9patch.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| OSM service roads | `osm_aop_9patch.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| OSM named landmarks | `osm_aop_named.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| SFWDA paper trail map | `sfwda_aop_trail_map.webp` + `sfwda_raster_alignment.json` | off | `tasks/01_mvp/community_trails_import.md` |

The viewer also has a feature search box and the POI/footprint editor -- see
"Viewer capabilities" below.

## Viewer capabilities

### Feature search

Added 2026-05-20. No new files, no dependency, fully client-side over the
already-loaded GeoJSON -- so it works offline.

- `indexFeatures()` registers every named feature as each layer's data loads;
  `buildSearchGroups()` collapses a multi-segment feature into one result framed
  by its full extent. ~127 named features index today.
- Trails are searchable: the publish `trail_centerlines` layer indexes as kind
  `trail`, and `searchDisplayName()` strips a trailing `(segment N)` suffix so a
  GPX-imported trail collapses to one result. Real named AOP trails become
  searchable automatically once they land in `publish.geojson`.
- OSM `highway=track` ways are wired for search, but all 47 in the 9-patch are
  unnamed in OSM so none surface yet.
- The box sits at the top of the panel: substring match, dropdown of up to 8
  results with a kind tag, arrow-key navigation, Enter selects, Escape clears.
- On select it `fitBounds`/`flyTo`s to the feature, auto-enables the feature's
  layer toggle if it was off, and flashes a yellow highlight pulse.
- Verified: `mvp/scripts/playwright_verify_search.py` -- 12/12 PASS on
  2026-05-20, 0 console errors.

### POI / footprint editor

The viewer can draw, label, persist (`localStorage`), and export point POIs and
polygon footprints -- pavilions, buildings, staging, gates, hazards. Full
record: `tasks/01_mvp/poi_editor.md`. PostGIS write-back is the open follow-up.

## Layer detail

### Publishable Layers

The three publishable layers -- trails, boundaries, trailheads -- come from
`website/data/publish.geojson`, exported from the PostGIS `publish` views by
`mvp/scripts/export_publish_geojson.sh`. Today the file holds one publishable
feature: the parcel-derived AOP working envelope. How features earn their way
into `publish` is the source-register contract -- see
`northstar/source_register.md`, `northstar/validation_loop.md`, and the build
card.

### Satellite Imagery (TNMap 2022)

Recorded on 2026-05-20:

- Source: TDOT / TNMap orthoimagery, wired as a raster XYZ source --
  `https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer/tile/{z}/{y}/{x}`.
  The service is a cached (`singleFusedMapCache`) Web Mercator map with standard
  LODs, so XYZ access works directly with MapLibre.
- TNMap says source imagery is 1 ft before 2022 and 6 in from 2022 onward; the
  AOP point query returns Marion County `TN_Ortho_Year = 2022`.
- A 6-inch AOP tile fetch returns `image/jpeg` 200. Treat as inspection-only --
  do not republish the tiles. Licensing must be settled separately before any
  imagery is exported.
- Toggle `Satellite imagery (TNMap 2022)`, default OFF so the viewer still opens
  with no network.
- Verified: `mvp/scripts/playwright_verify_satellite.py`.

### 9-Patch Acquisition AOI Overlay

Recorded on 2026-05-20:

- `website/data/aop_9_patch.geojson` is a copy of
  `brain/output/aop_9_patch_data_bounds.geojson` -- the 3-by-3 data-acquisition
  grid around the parcel envelope. The grid concept and cell coordinates live in
  `research/aop_data_bounds.md`.
- Toggle `9-patch acquisition AOI`, default OFF; the overlay draws the nine
  cells with their cell-code labels (`NW`, `N`, ... `C` ... `SE`).
- This is a data-acquisition planning overlay, not a trail or boundary claim.

### Lidar Tile Index Layer

Recorded on 2026-05-20:

- The 24 USGS 3DEP LAZ tile footprints are a viewer overlay at `website/data/aop_lidar_tiles.geojson`.
- Source: TNM products API query `datasets=Lidar Point Cloud (LPC)&prodFormats=LAZ&bbox=<9-patch>`.
- Each feature carries `tile_code`, `title`, `project`, `publication_date`, `size_bytes`, `size_mb`, `download_url`, `meta_url`, `source_name`, and `source_id`.
- Footprints come straight from each tile's `boundingBox`; they are inventory metadata, not measured coverage envelopes.
- The static viewer exposes the layer behind a toggle labeled `Lidar tile index (USGS 3DEP)` with fill, outline, and `tile_code` labels, plus a popup that links the LAZ download.

### Lidar Hillshade and 3D Terrain Layers

Recorded on 2026-05-20:

- The viewer renders a lidar-derived hillshade and a 3D terrain view directly from AWS Terrain Tiles (Terrarium-encoded raster-DEM). In the AOP block the upstream elevation is USGS 3DEP, which is lidar-derived; that is the closest "see the lidar" the viewer can show without downloading the LAZ tiles.
- Source: `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`, `encoding: 'terrarium'`, `maxzoom: 15`.
- 2D shading: MapLibre `hillshade` layer `lidar-hillshade`, toggle `Lidar hillshade (USGS 3DEP)`.
- 3D terrain: `map.setTerrain` with exaggeration 1.4 plus `map.setSky` atmosphere, toggle `3D terrain (AWS Terrarium / USGS 3DEP)`. Drag with right-click / two-finger to tilt and rotate.
- Attribution shown in the viewer credits AWS Terrain Tiles (USGS 3DEP, SRTM, GMTED, ETOPO1).
- Verified with `mvp/scripts/playwright_verify_lidar_tiles.py` on 2026-05-20: 21 of 21 checks PASS, 109 AWS Terrarium tile requests during the run, 0 console errors.
- The hillshade and 3D terrain are global-DEM derivatives, not the locally-derived 1-meter DEM lidar product. The locally-derived contour layer below is the lidar-grade product; swapping the hillshade onto AOP-specific 1 m DEM tiles is tracked at `tasks/01_mvp/_readme.md` item #10.

### Lidar Contour Layer

Recorded on 2026-05-20; updated 2026-05-21:

- The viewer has lidar-grade contour lines at `website/data/aop_contours.geojson`,
  generated from the USGS 3DEP 1-meter DEM (lidar-derived bare-earth elevation).
- Build pipeline: `mvp/scripts/build_contours.sh`. It caches the DEM, clips it to
  the 9-patch, low-pass smooths the DEM, runs `gdal_contour` at a 5-foot interval,
  attributes each line, thins with a light Douglas-Peucker pass, repairs any
  contour crossings, and exports a WGS84 GeoJSON. GDAL runs via Docker
  `ghcr.io/osgeo/gdal:ubuntu-small-latest` (see `brain/spinup/mvp_runbook.md` for
  the toolchain and the macOS file-access constraint).
- Source DEM: `USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`, native CRS
  `NAD83 / UTM zone 16N` (EPSG:26916), 1 m pixels. Clipped to the full 9-patch bbox
  `-85.782935283, 35.067164188, -85.717154097, 35.117928496`; the clipped DEM is
  cached at `mvp/cache/dem/dem_9patch.tif`.
- Contour interval: 5 ft (1.524 m). Indexed (major) contour every 25 ft.
- Smoothing (2026-05-20): raw 1 m lidar contours were jagged -- crinkle from lidar
  micro-noise plus angular corners from Douglas-Peucker. The DEM is low-pass
  smoothed first: resampled 1 m -> 2 m with a cubic-spline kernel
  (`gdalwarp -r cubicspline`), which strips the micro-noise before contouring. The
  smoothed DEM is cached at `mvp/cache/dem/dem_9patch_smooth.tif`. Sampling a
  *finer* interval would worsen the noise crinkle, not help -- smoothing the surface
  is the lever.
- Crossing repair (2026-05-21): contours are isolines and can never cross, but
  Douglas-Peucker simplifies each line independently and pushed tightly-spaced
  contours across each other on steep ground (~955 crossings at a 2 m tolerance).
  The fix: a light 0.5 m DP pass, then `mvp/scripts/repair_crossings.py`. Because
  DP only *deletes* vertices, a simplified line is an exact subsequence of its raw
  line; the repair detects crossings and restores the offending segments to raw
  (non-crossing) geometry, iterating until none remain. The last build repaired
  14 crossings to 0 in 4 iterations, restoring 130 vertices -- a negligible file
  cost. Tunable: `SIMPLIFY_M` at the top of `build_contours.sh`.
- Features: 2,831 LineStrings spanning 605-1820 ft (501 indexed). Each carries
  `elev_m` (metres), `elev_ft` (whole feet), and `idx` (1 = indexed/25-ft, 0 = minor/5-ft).
- Ship format: GeoJSON, ~14 MB. Under the ~25 MB threshold, so the layer ships as
  GeoJSON rather than PMTiles. The full-resolution attributed GeoPackage is cached
  at `mvp/cache/contours/aop_contours.gpkg` (gitignored, archival / QGIS use).
- Viewer: toggle `Lidar contours (5 ft, 1m DEM)`, default OFF. Layers `contours-minor`
  (thin), `contours-index` (bold 25-ft), and `contours-labels` (elevation labels on
  index lines). Clicking any contour shows its elevation.
- Verified with `mvp/scripts/playwright_verify_lidar_tiles.py` on 2026-05-21: all
  checks PASS, 0 console errors. An independent crossing detector confirms 0
  different-elevation crossings.

### Asphalt Roads Layer

Recorded on 2026-05-20:

- Source: USGS National Map Transportation MapServer `https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer`.
- Layers queried over the 9-patch bbox: `29` Controlled-access Highways (10 features), `30` Secondary Highways (0), `31` Local Connecting Roads (28), `32` Local Roads (76), `33` Ramps (0). Total `114` paved-network features.
- Excluded by design: layer `35` 4WD Roads, layer `36` Closed Roads, layer `37` Trails -- those would not be asphalt.
- Importer: `mvp/scripts/import_usgs_roads.sh` (curl + jq, atomic write).
- Output: `website/data/aop_roads.geojson` -- each feature tagged with `road_class` (`controlled_access`, `secondary`, `local_connecting`, `local`, `ramp`) plus `name`, `mtfcc_code`, `tnmfrc`, and route designators.
- Viewer: toggle `Asphalt roads (USGS National Map)`, default-on. Stacked layers `roads-local-casing` + `roads-local`, `roads-connecting-casing` + `roads-connecting`, `roads-controlled-casing` + `roads-controlled`, plus a `roads-labels` symbol layer along the line. Click any class for a popup with name, MTFCC, and route designators.
- Notable named features in-AOI: I-24, Ellis Cove Rd (the AOP access road), Ellis Rd, Battlecreek Rd, Fiery Gizzard Rd, Sweetens Cove Rd.
- Picked over TNMap MAJOR_ROADS (too sparse -- interstates and state highways only, misses county/park-access roads) and Overpass/OSM (would require per-way `surface=*` filtering and local TN ways are not reliably tagged for surface).

### Hydrography / Water Layer

Recorded on 2026-05-20:

- Source: USGS National Hydrography Dataset (NHD) `https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer`.
- Large-scale (high-resolution) NHD layers queried over the 9-patch bbox: `6` Flowline (85 features), `9` Area (1), `12` Waterbody (3), `0` Point (5). Total `94` water features.
- Importer: `mvp/scripts/import_usgs_hydrography.sh` (curl + jq, atomic write).
- Output: `website/data/aop_water.geojson` -- each feature tagged with `water_kind` (`flowline`, `water_area`, `waterbody`, `point`) and `water_class`, plus `name` (GNIS), `gnis_id`, `fcode`, `ftype`, `lengthkm`/`areasqkm`/`elevation`, `permanent_identifier`, and `nhd_layer_id`/`nhd_layer_name`.
- Class breakdown: `55` stream, `30` artificial_path (flow paths through wide water), `1` stream_river_area, `3` lake_pond, `4` spring, `1` gage.
- Named streams in-AOI: Battle Creek (the main creek through the AOP block, mostly modeled as artificial paths inside a 0.63 km² stream/river area polygon), Big Fiery Gizzard Creek, Kelly Cove Branch, Rogers Cove Branch, Sweden Creek, Tate Cove Creek. Named springs: Gilliam Spring, Bible Spring, Fish Trap Spring.
- Viewer: two toggles in `website/index.html`, both default-off. `Streams & waterbodies (USGS NHD)` drives `streams` + `stream-labels` + `waterbody-fill`/`waterbody-outline` + `water-area-fill`; `Springs & gages (USGS NHD)` drives `water-points` + `water-point-labels`. Click any stream/waterbody/point for a popup with class, NHD ftype/fcode, and length or area.
- Verified with `mvp/scripts/playwright_verify_water.py` on 2026-05-20: 28 of 28 checks PASS, 0 console errors.
- All NHD water features are raw-zone context. Before any are promoted into publish layers, attach a row in `source_register.sources` per `northstar/source_register.md` (USGS NHD is public domain; confidence: high for named perennial streams, lower for unnamed/intermittent; permission: public).
- The 1m-DEM lidar contour pipeline (`brain/tasks/01_mvp/lidar_contour_pipeline.md`) is the natural cross-check: where NHD flowlines and lidar drainage scars disagree, trust the lidar for micro-terrain.

### Cemeteries Layer

Recorded on 2026-05-21:

- Source: Tennessee Comptroller of the Treasury -- Marion County parcels, `TN_County_Parcel_Map` FeatureServer layer 35 (`Marion_Parcels`) -- the same service as the AOP boundary import.
- Importer: `mvp/scripts/import_marion_cemeteries.py` queries cemetery-owned parcels (`OWNER LIKE '%CEMETERY%'`) across the 9-patch bbox, normalizes each into a readable cemetery feature, joins a hand-curated burial roster where one is known, and writes `website/data/aop_cemeteries.geojson` -- 4 cemeteries, 8 features (one parcel polygon plus one centroid marker each, tagged `geom_role`).
- The four in-AOI cemeteries: Ellis (`110 008.04`, ~0.12 ac), Gilliam (`093 029.00`, ~2.91 ac), Bible (`093 003.00`, ~0.74 ac), Tate (`093 001.02`, ~0.70 ac). All class `05 RELIGIOUS`.
- Ellis Cemetery is the AOP inholding -- the interior ring (the hole) in the AOP working-envelope polygon, parcel `110 008.04` carved out of parent parcel `110 008.00`. Confirmed by point query and bit-identical geometry. Full evidence: `research/aop_ellis_cemetery.md`.
- Viewer: toggle `Cemeteries (TN Comptroller parcels)` in `website/index.html`, default off. Layers `cemetery-fill`, `cemetery-outline`, `cemetery-marker` (amber ring on the AOP inholding), `cemetery-label`. Cemeteries are searchable; the county owner-of-record name is indexed as an alias.
- Verified with `mvp/scripts/playwright_verify_cemeteries.py` on 2026-05-21: 25 of 25 checks PASS, 0 console errors.
- All cemetery features are raw-zone context. Before any promotion to publish layers, attach a `source_register.sources` row per `northstar/source_register.md`. The Ellis burial roster comes from a USGenWeb transcription with non-commercial terms -- keep it inspection-only until use is settled.

## Verification scripts

Viewer layers and capabilities have Playwright checks under `mvp/scripts/`
(`playwright_verify_*.py` -- satellite, lidar tiles, terrain, water, cemeteries,
community trails, SFWDA multiply, POI editor, search, trails). They drive the
real browser, exercise the toggles, assert layer visibility and network traffic,
capture screenshots into `brain/output/`, and fail on any console error. Run the
relevant one after touching `website/index.html`. `brain/output/playwright_eyes.md`
records why the viewer vendors its libraries instead of using a CDN.
