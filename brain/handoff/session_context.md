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

## What the next session should do

1. Open the viewer at `http://localhost:8001/` and inspect the expanded candidate parcel boundary.
2. Connect QGIS to `localhost:5432` and inspect `raw.arcgis_feature_captures`, `core.parcels`, `core.park_boundaries`, and `source_register.feature_sources`.
3. Verify the `110 008.00` plus `093 030.01` envelope in QGIS and keep it labeled as parcel-reference context, not a legal survey.
4. Use `brain/research/aop_data_bounds.md` and `brain/output/aop_9_patch_data_bounds.geojson` for the 9-patch satellite/orthoimagery, topo, DEM, and lidar acquisition AOI.
5. Use `brain/output/aop_9_patch_data_acquisition_manifest.md` as the source list for data pulls.
6. In QGIS, add TNMap 2022 orthoimagery as an ArcGIS REST/WMTS inspection basemap.
7. Download the USGS 3DEP 1-meter DEM first, clip it to the 9-patch, then generate hillshade, slope, and print-friendly relief products.
8. Download the USGS contour GeoPackage and clip/filter it to the 9-patch.
9. Pull USGS US Topo GeoPDFs for Orme and South Pittsburg as archived references.
10. Hold raw LAZ downloads until the DEM-derived products are inspected; the full LAZ set is about 2.79 GB.
11. If newer NAIP than 2021 is needed, resolve 2023 NAIP direct download through USDA Box/AWS or another official USDA/USGS path; do not treat the 2023 date index as the imagery itself.
12. Replace demo/smoke trail and trailhead placeholders with actual AOP trail/observation data.
13. Attach each real feature to a source row in `source_register.sources` and preserve confidence/permission metadata.
14. Export the `publish` views to `website/data/publish.geojson` and verify the viewer renders the actual AOP map.
15. Execute the first real observation review, promotion, and verification pass after real trail data exists.
16. If the MVP stack is not ready, record the exact failure mode and update this handoff immediately.
17. Keep session-only notes in this folder; move stable promises to `northstar/` and source facts to `research/`.

## Session note

This file is handoff context, not a durable policy document. Keep it live until the next session has read and acted on it.
