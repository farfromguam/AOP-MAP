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

## Session note

This file is handoff context, not a durable policy document. Keep it live until the next session has read and acted on it.
