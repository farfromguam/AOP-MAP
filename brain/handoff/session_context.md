# Session Handoff: MVP validation loop

Date: 202605201645

This session is continuing MVP work with context after invoking the CWC flow (`~~cwc`).

Archived copy: `brain/handoff/session_context_202605201517.md`

## What happened

 - The user asked to continue MVP work and begin testing the loop.
 - The CWC flow (`~~cwc`) was invoked to continue the session.
 - The current northstar promise is in `brain/northstar/map_northstar.md`.
 - The current build card is `brain/tasks/01_mvp/aop_south_pittsburg_map_build_card.md`.
- The MVP environment was launched successfully with `mvp/docker compose up -d`.
 - The database schema is initialized and the project tables exist, but all core tables were empty before this session.
 - A demo source and publishable sample features were inserted into `core.trail_centerlines`, `core.park_boundaries`, and `core.trailheads`.
 - A new MVP script was added at `mvp/scripts/export_publish_geojson.sh` to export `publish` views into `website/data/publish.geojson`.
 - `website/data/publish.geojson` was refreshed from the live `publish` views and the static viewer still renders the same demo GeoJSON.
 - The CWC smoke pass on 2026-05-20 confirmed the Docker/PostGIS MVP database is running.
 - `mvp/scripts/run_validation_loop_smoke.sh` was added and run successfully. It inserted one demo board-review source, captured observation id `1`, promoted it into `core.trail_centerlines` id `2`, and created provenance links in `source_register.feature_sources`.
 - `mvp/scripts/export_publish_geojson.sh` was hardened to write through a temporary file before replacing `website/data/publish.geojson`.
 - After export, `website/data/publish.geojson` contains 4 publishable demo features: 2 `trail_centerlines`, 1 `park_boundaries`, and 1 `trailheads`.
 - Verification performed: SQL counts/provenance checks passed; GeoJSON parsed successfully with Node. Browser-level Playwright verification was not rerun because `@playwright/test` is not installed in this repo.
 - Continued after the CWC pass and imported the first real source-backed AOP boundary slice from the Tennessee Comptroller Marion County parcel layer.
 - Added `mvp/scripts/import_aop_parcel_boundary.sh` and `mvp/scripts/import_aop_parcel_boundary.sql`.
 - The importer queries `Assessment_Data_58_ADDRESS = 'ELLIS COVE RD 1040'`, stores the raw feature in `raw.arcgis_feature_captures`, upserts parcel `110 008.00` into `core.parcels`, and publishes `AOP working parcel envelope - Ellis Cove Road 1040` through `core.park_boundaries`.
 - The imported parcel has `502.49725246` calculated acres and `483.46` deed acres, so the official 600+ acre AOP claim remains unreconciled.
 - Demo/smoke trail, trailhead, and boundary rows were moved to `publish_status = 'demo_hold'` and `permission = 'internal'` so they no longer export as public map data.
 - After export, `website/data/publish.geojson` contains 1 publishable feature: the candidate AOP parcel-derived boundary.
 - `website/index.html` now fetches GeoJSON directly, fits the map to exported data bounds, filters layers by the exported `layer` property, and includes boundary popups.
 - A local static preview server was started at `http://localhost:8001/`.
 - Continued again on 2026-05-20 and matched the connected parcel lead `058 093 03001 000 2026` to Tennessee Comptroller Marion assessment ID `093 030.01` / GIS parcel ID `058 093    03001 000 2023`.
 - The parcel importer now fetches both `ELLIS COVE RD 1040` and `093 030.01`, upserts both into `core.parcels`, and publishes the working envelope as `AOP working parcel envelope - included parcel candidates` with `MultiPolygon` geometry.
 - The imported candidate parcels total `592.31840466` calculated acres and `573.46` deed acres. `website/data/publish.geojson` was refreshed and now contains one publishable boundary feature whose bounds include the connected parcel.
 - Documented the current working bounds in `brain/research/aop_data_bounds.md` and `brain/output/aop_9_patch_data_bounds.geojson`: the center bounds are the exported bbox of the two-parcel candidate envelope, and the proposed 9-patch acquisition bounds expand that center cell one full cell in every direction for satellite/orthoimagery, topo, DEM, and lidar pulls. Trails stay inside the park working envelope unless AOP confirms otherwise.
 - User asked what the 9-patch means. Answer: it is a 3-by-3 data acquisition AOI around the current two-parcel working envelope; it is for raster/terrain/topo context only, not trail expansion or legal boundary claims.
 - User then asked to find lidar, satellite/imagery, and topographic data for the 9-patch.
 - Public GIS sources were queried against the full 9-patch bbox `-85.782935283, 35.067164188, -85.717154097, 35.117928496`.
 - Added `brain/output/aop_9_patch_data_acquisition_manifest.md` with concrete source links, query results, and recommended acquisition order.
 - Updated `brain/research/aop_data_bounds.md` with a short data acquisition findings section pointing to that manifest.
 - Best immediate imagery source found: TDOT / TNMap `https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer`; AOP point query returned Marion County `TN_Ortho_Year = 2022` and `NAIP_Year = 2021`. Treat exported imagery/licensing separately before publishing.
 - Best immediate elevation source found: USGS 3DEP 1-meter DEM `USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`, about `499,956,299` bytes, covering the full 9-patch.
 - Raw lidar source found: USGS 3DEP LAZ point cloud project `USGS_LPC_TN_27County_blk4_2015_LAS_2018`; 24 intersecting LAZ tiles totaling about `2,788,061,014` bytes. Use only if the 1-meter DEM/hillshade is not enough.
 - Topographic sources found: USGS contour GeoPackage `ELEV_Chattanooga_W_TN_1X1_GPKG.zip`, plus US Topo GeoPDFs for Orme, TN and South Pittsburg, TN from 2010, 2013, and 2016.
 - NAIP sources found: USGS NAIP ImageServer returned two 2021 downloadable 0.6 m, 4-band quarter-quads; USDA 2023 Tennessee image-date polygons intersect the AOI with acquisition date `2023-06-09`, but direct 2023 imagery download paths were not resolved in this pass.
 - USDA Geospatial Data Gateway was checked and is now retired as of 2026-03-31; USDA points many direct data downloads to Box paths including `https://nrcs.app.box.com/v/gateway/` and `https://nrcs.app.box.com/v/naip`.
 - No raster/lidar/topo products were downloaded locally in this pass; this was discovery and manifesting only.
 - Working tree at this CWC dump includes the new/modified acquisition docs plus pre-existing or unrelated untracked items visible in status: `brain/output/diagnose_viewer.png` and `brain/tasks/backlog/`. Do not assume those untracked items came from this dump.
 - Continued CWC on 2026-05-20 and found the host PostGIS connection docs were unsafe on this machine: local Postgres was already listening on `127.0.0.1:5432`, so `localhost:5432` reached the host database instead of `mvp-db-1`.
 - Updated the MVP Compose host port to default to `55432` via `AOP_DB_HOST_PORT`, while leaving the container-internal database port at `5432`.
 - Updated root/MVP spinup docs and QGIS notes to use `localhost:55432`.
 - Added a root `./cwc` helper and VS Code task for a non-mutating continuation check of Docker, Postgres, and `website/data/publish.geojson`.
 - Added durable runbook documentation at `brain/spinup/mvp_runbook.md` and routed related keywords through `brain/search_map.md`.
 - Current local static preview listener found during this pass is `http://localhost:8000/`.
 - Wired TNMap 2022 orthoimagery into the static viewer as a raster XYZ source: `https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer/tile/{z}/{y}/{x}`. Cached service (singleFusedMapCache) in Web Mercator with standard LODs, so XYZ access works directly with MapLibre.
 - Confirmed a 6-inch AOP tile fetch returns `image/jpeg` 200; treat as inspection-only and do not republish tiles.
 - Added a toggleable `Satellite imagery (TNMap 2022)` layer in `website/index.html`, initially hidden so the static viewer still opens cleanly without network.
 - Copied `brain/output/aop_9_patch_data_bounds.geojson` to `website/data/aop_9_patch.geojson` and added a toggleable `9-patch acquisition AOI` overlay with cell-code labels.
 - Added `mvp/scripts/playwright_verify_satellite.py`: exercises every toggle, verifies layer visibility through `window.map.getLayoutProperty`, captures 5 screenshots into `brain/output/playwright_satellite_*.png`, and asserts TNMap tile requests fire when satellite is enabled.
 - Run on 2026-05-20: 16 of 16 checks PASS, 96 TNMap tile requests, 0 console errors. Screenshots show TNMap 6-inch imagery rendering under the AOP parcel envelope and the dashed 9-patch grid around it.
 - Added `website/data/aop_lidar_tiles.geojson`: 24 USGS 3DEP LAZ tile footprints intersecting the 9-patch, sourced from the TNM products API. Each feature carries `tile_code`, `title`, `project`, `publication_date`, `size_bytes`, `size_mb`, `download_url`, `meta_url`, `source_name`, and `source_id`. Total raw payload still 2.79 GB; no LAZ tiles downloaded.
 - Added a toggleable `Lidar tile index (USGS 3DEP)` layer in `website/index.html` (fill + outline + `tile_code` labels + click popup with LAZ download link).
 - Added `mvp/scripts/playwright_verify_lidar_tiles.py`; on 2026-05-20 it reported 14 of 14 checks PASS, 0 console errors, and saved `brain/output/playwright_lidar_*.png`.
 - Documented the new layer in `brain/research/aop_data_bounds.md` under "Lidar Tile Index Layer".
 - User flagged interest in really high quality topography lines (lidar-grade contours) as the motivation. That work is not started; next session should scope contour interval, AOI, and output format (vector GeoJSON vs. raster tile overlay) before pulling the 1-meter DEM.
 - User followed up that they were not seeing lidar data, so the viewer was extended to actually visualize elevation, not just tile metadata.
 - Wired AWS Terrain Tiles (Terrarium-encoded raster-DEM) as a single `aws-terrain-dem` source feeding both a MapLibre `hillshade` layer and `map.setTerrain` 3D mode. In the AOP block the upstream elevation is USGS 3DEP, which is lidar-derived.
 - Added two new viewer toggles: `Lidar hillshade (USGS 3DEP)` and `3D terrain (AWS Terrarium / USGS 3DEP)`. The 3D toggle also calls `map.setSky(SKY_ATMOSPHERE)` and eases to pitch 60.
 - Strengthened the lidar tile-index styling (purple `#9b30ff` dashed outline at width 2.5, fill-opacity 0.16, 13px halo-2 labels) so it is unmissable against satellite imagery.
 - GDAL is not installed on this machine (`gdal_contour`, `gdalinfo`, `ogr2ogr`, Python `rasterio`/`osgeo` all missing). The local 1-meter-DEM contour pipeline therefore still requires a tooling decision (Docker `osgeo/gdal` vs `brew install gdal`) before download.
 - USGSShadedReliefOnly was probed and only caches to z=13 over this AOI, so the chosen path is the AWS Terrarium DEM client-side hillshade rather than the USGS shaded-relief tile cache.
 - Extended `mvp/scripts/playwright_verify_lidar_tiles.py` to toggle tile-index, hillshade, and 3D terrain, assert AWS Terrarium tile traffic, and capture six screenshots. On 2026-05-20 it reported 21 of 21 checks PASS, 109 AWS Terrarium tile requests, 0 console errors. Screenshots at `brain/output/playwright_lidar_*.png` show the AOP parcel with bold purple lidar tile-index, lidar-derived hillshade, and 3D tilt with sky atmosphere.
 - Captured the lidar-grade contour work as a backlog card at `brain/tasks/backlog/lidar_contour_pipeline.md` and added it to `brain/tasks/backlog/_readme.md`. The card sequences the GDAL toolchain decision, the 1-meter DEM clip, contour generation at a 5-foot first-pass interval over the full 9-patch, the GeoJSON-vs-PMTiles ship-format fork, the viewer wiring, and the Playwright verification. The contour pipeline is not started; pick it up from that card next session.
 - Imported `brain/import/community_trails/` into the viewer as layers. Build card: `brain/tasks/01_mvp/community_trails_import.md`.
 - Copied into `website/data/`: `osm_aop_9patch.geojson` (71 features), `osm_aop_named.geojson` (5 named), `sfwda_aop_trail_map.webp` (SFWDA 2015 paper map raster, internal/inspection only), and `sfwda_raster_alignment.json` (4 corner sidecar; defaults to OSM AOP polygon corners).
 - Extended `website/index.html` with toggles for OSM park polygon, OSM tracks (highway=track), OSM service roads, OSM named landmarks, and the SFWDA paper map. All default OFF. Click popups added for OSM tracks/service/named features.
 - SFWDA paper map is wired as a MapLibre `image` source. Opacity slider (0-100, default 70) and an in-viewer alignment editor: toggle `Edit alignment` to show 4 draggable NW/NE/SE/SW corner handles. Dragging rewrites the image source coordinates live. `Export alignment` downloads a JSON file that replaces `website/data/sfwda_raster_alignment.json`. `Reset` reverts to the OSM AOP polygon corners.
 - Default corners use the OSM `Adventure Off Road Park` polygon (way 1215497712); this is a placement seed, not a pixel-accurate georeference. Next session should drag the corners until the SFWDA trail centerlines overlap the OSM `highway=track` and `service` lines, then Export and commit the resulting JSON.
 - Added `mvp/scripts/playwright_verify_community_trails.py`. On 2026-05-20 it reported 11 of 11 checks PASS, 0 console errors. Screenshots at `brain/output/playwright_community_layers.png` (NW handle drag test) confirm the 4 corner handles render and the image source reprojects on drag.
 - The viewer file was edited by the user or a linter during this session to also add a `showRoads` toggle and a USGS National Map asphalt roads layer pulling `website/data/aop_roads.geojson` (sources: `usgs-roads`, layers `roads-local`, `roads-connecting`, `roads-controlled`, `roads-labels` with casing variants). That layer is default-ON.

## What the next session should do

1. Open the viewer at `http://localhost:8000/` and inspect the expanded candidate parcel boundary.
2. Optionally run `./cwc` from the repo root to verify Docker, Postgres, and the current publish export.
3. Connect QGIS to `localhost:55432` and inspect `raw.arcgis_feature_captures`, `core.parcels`, `core.park_boundaries`, and `source_register.feature_sources`.
4. Verify the `110 008.00` plus `093 030.01` envelope in QGIS and keep it labeled as parcel-reference context, not a legal survey.
5. Use `brain/research/aop_data_bounds.md` and `brain/output/aop_9_patch_data_bounds.geojson` for the 9-patch satellite/orthoimagery, topo, DEM, and lidar acquisition AOI.
6. Use `brain/output/aop_9_patch_data_acquisition_manifest.md` as the source list for data pulls.
7. In QGIS, add TNMap 2022 orthoimagery as an ArcGIS REST/WMTS inspection basemap.
8. Download the USGS 3DEP 1-meter DEM first, clip it to the 9-patch, then generate hillshade, slope, and print-friendly relief products.
9. Download the USGS contour GeoPackage and clip/filter it to the 9-patch.
10. Pull USGS US Topo GeoPDFs for Orme and South Pittsburg as archived references.
11. Hold raw LAZ downloads until the DEM-derived products are inspected; the full LAZ set is about 2.79 GB.
12. If newer NAIP than 2021 is needed, resolve 2023 NAIP direct download through USDA Box/AWS or another official USDA/USGS path; do not treat the 2023 date index as the imagery itself.
13. Replace demo/smoke trail and trailhead placeholders with actual AOP trail/observation data.
14. Attach each real feature to a source row in `source_register.sources` and preserve confidence/permission metadata.
15. Export the `publish` views to `website/data/publish.geojson` and verify the viewer renders the actual AOP map.
16. Execute the first real observation review, promotion, and verification pass after real trail data exists.
17. If the MVP stack is not ready, record the exact failure mode and update this handoff immediately.
18. Keep session-only notes in this folder; move stable promises to `northstar/` and source facts to `research/`.
19. Pending swap from the AWS terrarium DEM to AOP-specific tiles built from the USGS 3DEP 1m DEM. Full step list lives at `brain/tasks/01_mvp/_readme.md` item #10. Triggers: only worth doing once the 10m terrarium look has earned its keep, since the toolchain install + 500MB download + tile build is a half-day vs. zero today.
20. Open the viewer, enable `Satellite imagery (TNMap 2022)`, `OSM tracks (highway=track)`, and `SFWDA paper trail map`. Toggle `Edit alignment` and drag the NW/NE/SE/SW handles until the SFWDA trail centerlines roughly overlap the OSM tracks. Click `Export alignment` and replace `website/data/sfwda_raster_alignment.json` with the downloaded file, then commit. Re-run `python3 mvp/scripts/playwright_verify_community_trails.py` to confirm no regressions.
21. Decide whether the SFWDA raster needs true georeferencing (GDAL/QGIS, with ground control points and an affine/projective transform) before any of its trail content is promoted into `core.trail_centerlines`. The current image source is a 4-corner quadrilateral warp — fine for inspection, not for survey-grade work.
22. The OSM 9-patch features (47 tracks, 19 service, named landmarks) live in `raw zone` semantics only. Before any of them are promoted into publish layers, attach a row in `source_register.sources` per the rules in `northstar/source_register.md` (license: ODbL; confidence: medium; permission: community).

## Update: lidar contour pipeline (2026-05-20)

Continued this session and completed the backlog lidar contour card.

 - The card moved from `brain/tasks/backlog/` to `brain/tasks/01_mvp/lidar_contour_pipeline.md` and is marked DONE; its Outcome section has the full detail.
 - GDAL toolchain: Docker `ghcr.io/osgeo/gdal:ubuntu-small-latest`. Docker Hub `osgeo/gdal` is stale; `alpine-small` lacks GEOS (needed for `-simplify`). macOS blocks Docker from reading the repo under `~/Documents`, so GDAL work stages in `/private/tmp`. Pattern recorded in `brain/spinup/mvp_runbook.md`.
 - `mvp/scripts/build_contours.sh` is the reproducible pipeline: cache the 1m DEM, clip to the 9-patch, `gdal_contour` at 5 ft, attribute (`elev_ft` + `idx`), simplify, export.
 - `website/data/aop_contours.geojson` -- 6,376 contour lines, 605-1820 ft, ~5.0 MB. Shipped as GeoJSON (3 m Douglas-Peucker simplified); PMTiles not needed.
 - `website/index.html` has a `Lidar contours (5 ft, 1m DEM)` toggle (default OFF) with minor/index/label layers and a click popup.
 - Large derived artifacts are gitignored under `mvp/cache/` (full DEM, clipped `dem_9patch.tif`, full-res `aop_contours.gpkg`).
 - Verified: `mvp/scripts/playwright_verify_lidar_tiles.py` extended to cover contours; all checks PASS on 2026-05-20, 0 console errors.
 - Open follow-up: revisit a 2 ft interval only if 5 ft proves too coarse for RC-scale micro-terrain.

## Update: water / hydrography layer (2026-05-20)

User asked to review the 9-patch and find data for water/river layers.

 - Source: USGS National Hydrography Dataset (NHD) MapServer `https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer`, large-scale (high-resolution) layers 6/9/12/0.
 - `mvp/scripts/import_usgs_hydrography.sh` (mirrors `import_usgs_roads.sh`) writes `website/data/aop_water.geojson` — 94 water features: 55 streams, 30 artificial paths, 1 stream/river area, 3 lake/pond, 4 springs, 1 gage. Each feature tagged `water_kind` + `water_class` + NHD `ftype`/`fcode`.
 - Named streams in-AOI: Battle Creek (the main creek), Big Fiery Gizzard Creek, Kelly Cove Branch, Rogers Cove Branch, Sweden Creek, Tate Cove Creek. Named springs: Gilliam, Bible, Fish Trap.
 - `website/index.html` got two default-OFF toggles: `Streams & waterbodies (USGS NHD)` and `Springs & gages (USGS NHD)`, with popups carrying class, NHD ftype/fcode, length/area.
 - `mvp/scripts/playwright_verify_water.py` added: 28 of 28 checks PASS, 0 console errors. Screenshots `brain/output/playwright_water_*.png`.
 - Documented in `brain/research/aop_data_bounds.md` ("Hydrography / Water Layer") and `brain/output/aop_9_patch_data_acquisition_manifest.md` ("Hydrography / Water").
 - Not pulled: NHDPlus HR HUC4 `0602` geodatabase (bulk alternative) and USGS Watershed Boundary Dataset (HUC8/10/12 drainage basins). Listed in the manifest if a basin layer is wanted later.
 - All NHD water features are raw-zone context; attach a `source_register.sources` row (USGS NHD = public domain) before any promotion to publish layers.

## Update: map search (2026-05-20)

User asked for a search box that re-focuses the map on a named feature.

 - Added to `website/index.html` (no new files, no dependency, fully client-side over already-loaded GeoJSON — works offline).
 - `indexFeatures()` registers every named feature as each layer's data loads; `buildSearchGroups()` collapses multi-segment features into one result framed by its full extent. 127 named features indexed today (streams, waterbodies, springs, roads, OSM tracks/landmarks, publish features).
 - Trails are searchable: the publish `trail_centerlines` layer is indexed as kind `trail`. `searchDisplayName()` strips a trailing `(segment N)` suffix so a GPX-imported trail like `Saturday Afternoon Activity` collapses from its segment rows into one result. Real named AOP trails will be searchable automatically once loaded into `publish.geojson`.
 - OSM `highway=track` ways are wired for search too, but all 47 in the 9-patch are unnamed in OSM, so none surface today.
 - Search box at the top of the panel: substring match, dropdown of up to 8 results with a kind tag, arrow-key navigation, Enter selects, Escape clears.
 - On select: `fitBounds`/`flyTo` to the feature, auto-enables the feature's layer toggle if it was off, and flashes a yellow `search-highlight` layer (a ~2.6 s rAF pulse).
 - Verified with `mvp/scripts/playwright_verify_search.py` on 2026-05-20: 12 of 12 checks PASS, 0 console errors. Screenshots `brain/output/playwright_search_*.png`.

## Update: contour smoothing + crossing repair (2026-05-20 / 05-21)

User flagged the contour lines as jagged, then later spotted an 825 ft contour
overlapping the 820 ft line below it.

 - Jaggedness diagnosis: the raw 1 m lidar DEM carries micro-noise so the
   isolines crinkle, and Douglas-Peucker simplification only deletes vertices —
   it never adds curvature. Sampling finer would worsen it; the lever is to
   smooth the surface.
 - Smoothing fix: `build_contours.sh` now low-pass smooths the DEM — resamples
   the clipped DEM 1 m → 2 m with `gdalwarp -r cubicspline` before
   `gdal_contour`. Smoothed DEM cached at `mvp/cache/dem/dem_9patch_smooth.tif`.
 - Crossing diagnosis: a crossing detector found ~955 places where contours of
   different elevation intersect — impossible on a real surface. Cause: DP
   simplifies each line independently and pushes tightly-spaced contours across
   each other on steep ground. Raw `gdal_contour` output has 0 crossings; the
   count scales with DP tolerance (0.5 m→12, 1 m→216, 2 m→1281). Chaikin was
   *not* the cause (it slightly reduced crossings) and has been dropped.
 - Crossing fix: light 0.5 m DP, then new `mvp/scripts/repair_crossings.py`.
   Since DP only deletes vertices, a simplified line is an exact subsequence of
   its raw line; the repair detects crossings and restores the offending
   segments to raw geometry, iterating to zero. Last build: 14 → 0 in 4
   iterations, 130 vertices restored. `chaikin_smooth.py` was removed.
 - Result: `website/data/aop_contours.geojson` — 2,831 LineStrings, ~14 MB,
   605–1820 ft (501 indexed), 0 crossings (independent detector confirms).
 - Viewer needed no change — GeoJSON schema (`elev_m`/`elev_ft`/`idx`) unchanged.
   `playwright_verify_lidar_tiles.py` PASS, 0 console errors. Spot-checks:
   `brain/output/playwright_lidar_contours_z16.png`, `..._repair_spot.png`.
 - Tunables at the top of `build_contours.sh`: `SMOOTH_RES_M` (DEM low-pass) and
   `SIMPLIFY_M` (DP tolerance). The repair handles whatever crossings DP leaves.
 - Open follow-up: if the lines read slightly angular at high zoom (DP 0.5 m
   leaves ~16° median vertex turn), the long-term fix is shipping raw contours as
   PMTiles — keeps full smoothness with no crossings. Not done; not blocking.

## Update: cemeteries layer / the hole in the plot (2026-05-21)

User asked to review a USGenWeb cemetery record for "Ellis Cemetery" and
whether it is the hole in the AOP plot.

 - Confirmed: the AOP working-envelope polygon (`website/data/publish.geojson`)
   has an interior ring — a hole — in parcel `110 008.00`. A point query
   against the TN Comptroller Marion County parcel layer at the hole centroid
   returns parcel `110 008.04`, owner `BRYSON & ELLIS CEMETERY`, class
   `05 RELIGIOUS`, ~0.12 acre. The cemetery parcel geometry is bit-identical to
   the hole ring. It is an inholding excepted out of the deed when the Ellis
   land became the park. Full evidence: `brain/research/aop_ellis_cemetery.md`.
 - Added `mvp/scripts/import_marion_cemeteries.py` — pulls cemetery-class
   parcels (`OWNER LIKE '%CEMETERY%'`) from the 9-patch, joins a hand-curated
   burial roster, writes `website/data/aop_cemeteries.geojson` (4 cemeteries —
   Ellis, Gilliam, Bible, Tate; 8 features: a parcel polygon + a centroid
   marker each, tagged `geom_role`).
 - Wired a `Cemeteries (TN Comptroller parcels)` layer into `website/index.html`
   (default OFF): `cemetery-fill`, `cemetery-outline`, `cemetery-marker` (amber
   ring on the AOP inholding), `cemetery-label`, plus a click popup carrying
   parcel facts and the Ellis burial roster. Cemeteries are searchable; the
   county owner-of-record name is indexed as a search alias.
 - Added `mvp/scripts/playwright_verify_cemeteries.py`; on 2026-05-21 it
   reported 25 of 25 checks PASS, 0 console errors. Screenshots at
   `brain/output/playwright_cemeteries_*.png`.
 - Build card: `brain/tasks/01_mvp/cemeteries_layer.md` (DONE). Research:
   `brain/research/aop_ellis_cemetery.md`. Routed in `brain/search_map.md`.
 - Open follow-ups in the research doc: the `Bryson & Ellis` vs `Ellis`
   cemetery-name question, the cemetery-access easement (an AOP operational
   question), and a `source_register` decision before the USGenWeb burial
   roster ships beyond the inspection viewer.

## Update: forest land-cover layer + Muted Earth restyle (2026-05-21)

User asked to turn the satellite imagery into a vector layer and restyle the
viewer into a muted/pastel park-map palette.

 - Reframed: imagery cannot be vectorized directly — it becomes a
   classification source. Built a vector forest land-cover layer.
 - Imagery: USGS NAIP 2021, 4-band, 0.6 m, leaf-off (acquired 2021-11-07). Only
   no-auth 4-band source — 2023 leaf-on NAIP is behind an EarthExplorer login,
   the TNM products API no longer serves NAIP, TNMap is RGB-only. Cached
   gitignored at `mvp/cache/imagery/naip_2021_aop.tif`.
 - Pipeline: `mvp/scripts/build_landcover.sh` + `classify_landcover.py` +
   `smooth_landcover.py`. Forest classified as a neighbourhood-scale
   canopy-roughness field (NIR std-dev, low-pass, Otsu) then cleaned with
   morphological closing/opening. The first pixel-scale attempt produced
   unusable speckle; the user asked for "a more thorough conversion so it's not
   so blobby" — the field-scale + morphology approach is that fix.
 - Output: `website/data/aop_landcover.geojson` — 7 forest polygons, 63
   clearings as holes, 78% forest cover, clipped to the AOP boundary, ~152 KB.
 - Water dropped from land cover (leaf-off NIR confuses water with shadow; the
   NHD layer already handles hydrography). Open ground = paper background.
 - Viewer: `landcover-forest` layer at the base + `Forest land cover (NAIP)`
   toggle (default ON). Full "Muted Earth" palette restyle — paper background
   `#efe7d5`, every layer's paint retuned to the warm vintage palette.
 - Verified: `mvp/scripts/playwright_verify_landcover.py` 19/19 PASS, 0 console
   errors. Screenshots `brain/output/playwright_landcover_*.png`.
 - Build card `tasks/01_mvp/landcover_layer.md`; layer detail added to the
   viewer catalog `research/viewer.md`; routed in `search_map.md`.
 - Open follow-up: leaf-off imagery caps edge crispness (~15 m softness floor).

## Update: building footprints layer (2026-05-21)

User asked to review the 9-patch for accessible building layers and import what
we can use.

 - Checked FEMA USA Structures / ORNL, OSM `building=*`, and TNMap FEMA BLE
   building footprints.
 - FEMA USA Structures returned 202 polygon footprints in the 9-patch and was
   selected. OSM returned 11 building ways but was not imported to avoid a
   duplicate ODbL context layer. TNMap FEMA BLE returned 0 features in the AOI.
 - Added `mvp/scripts/import_fema_buildings.py`. It queries FEMA object ids over
   the 9-patch bbox, fetches those ids as GeoJSON chunks, normalizes fields, and
   writes `website/data/aop_buildings.geojson`.
 - Output count: 202 footprints. Class mix: 166 Residential, 24 Agriculture, 7
   Unclassified, 3 Assembly, 2 Government. Four footprint centroids fall inside
   the candidate AOP boundary: 1010, 1033, 665, and 880 Ellis Cove Road.
 - Wired `Building footprints (FEMA USA Structures)` into `website/index.html`,
   default OFF, with fill/outline layers and heavier outline for inside-AOP
   footprints. Addressed footprints are searchable.
 - Added `mvp/scripts/playwright_verify_buildings.py`; on 2026-05-21 it
   reported all checks PASS, 0 console errors. Screenshots:
   `brain/output/playwright_buildings_*.png`.
 - Build card: `brain/tasks/01_mvp/buildings_layer.md`. Viewer catalog and
   data-acquisition manifest were updated.

## Update: 9-patch forest land cover (2026-05-21)

User asked to extend the forest land-cover layer to the full 9-patch AOI, was
fine with the bounds being separate, and wanted to adjust opacity on the
non-park areas.

 - `classify_landcover.py` is now resolution-aware -- it rescales its texture
   and morphology window radii from the geotransform pixel size. Byte-identical
   at the 0.6 m park resolution, so the park build/layer was not touched.
 - New `mvp/scripts/build_landcover_9patch.sh` pulls one ~1.5 m NAIP export for
   the full 9-patch (the ImageServer caps exports at 4000 px, so 0.6 m would
   not fit), classifies, vectorizes, clips to the 9-patch rectangle.
 - `website/data/aop_landcover_9patch.geojson` -- 70 forest polygons, ~80%
   cover, ~1.7 MB, bbox = the full 9-patch.
 - Viewer: `landcover-9patch-forest` (+ `-outline`) layer at the base of the
   stack below the crisp park layer; toggle `Forest land cover — 9-patch
   (NAIP)` default ON; `9-patch forest opacity` slider default 55%. The park
   layer draws on top, so the slider fades only the non-park context. Full
   9-patch coverage, not park-cut-out.
 - `playwright_verify_landcover.py` extended for the new layer, base-of-stack
   order, and the slider; all checks PASS, 0 console errors. Screenshots
   `brain/output/playwright_landcover_9patch_*.png`.
 - Build card updated: `tasks/01_mvp/landcover_layer.md` ("Update: 9-patch
   extension"). Catalog updated: `research/viewer.md`.
 - Open follow-up unchanged: leaf-on 2023 NAIP (`tasks/backlog/leaf_on_landcover.md`)
   would sharpen both the park and 9-patch layers.

## Update: multi-shade land cover (2026-05-21)

User noted the land-cover layer was one green for all trees while the satellite
shows fields in different colours, and asked to support varied field colours
and darker tree shades. They chose to do the forest split and the field split
both now.

 - The land-cover layer went from binary forest/open to a five-class coverage:
   `forest_deciduous`, `forest_evergreen`, `open_grass`, `open_meadow`,
   `open_bare`. Open ground is now emitted as polygons (was paper background).
 - `classify_landcover.py` gained a stage 2: NDVI vigour smoothed within each
   zone. Forest split -- evergreen is the high-NDVI tail (top 20%); the weak
   scattered leaf-off conifer signal is consolidated into coherent stands by a
   stand-scale smooth + heavy morphology (the first attempt was dark-green
   confetti). Open split -- two Otsu cuts rank open ground bare/meadow/grass.
 - `smooth_landcover.py` keeps all five classes and no longer drops slivers/
   holes (would punch coverage gaps). Both build scripts emit all classes
   (`DN > 0`) and gained an `ogr2ogr -makevalid` pass (Chaikin can pinch thin
   polygons into self-intersections -> the GEOS clip threw TopologyException).
   The 9-patch build simplifies harder (3 m) since it is a dimmed context layer.
 - Viewer: fill colour is a MapLibre `match` on `class` with a same-family
   outline that bridges sub-pixel simplify slivers. Toggles relabelled `Land
   cover (NAIP)` / `Land cover — 9-patch (NAIP)`; layer ids kept.
 - Output: `aop_landcover.geojson` 631 polygons / ~920 KB;
   `aop_landcover_9patch.geojson` 6420 polygons / ~7.8 MB.
 - Verified: `playwright_verify_landcover.py` updated for the five classes --
   31 of 31 PASS, 0 console errors. Build card `tasks/01_mvp/landcover_layer.md`
   ("Update: multi-shade land cover"); catalog `research/viewer.md`.
 - Honest limit: leaf-off November is the ceiling. The conifer split is real
   but weak and only coherent after heavy consolidation; the open split is a
   relative vigour ranking, not crop ID. Leaf-on 2023 NAIP
   (`tasks/backlog/leaf_on_landcover.md`) would make both far more meaningful.

## Session note

This file is handoff context, not a durable policy document. Keep it live until the next session has read and acted on it.
