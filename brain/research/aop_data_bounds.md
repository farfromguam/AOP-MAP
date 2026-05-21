# AOP Data Bounds

TL;DR:
- The current park working bounds are a candidate parcel envelope assembled from two Tennessee Comptroller Marion County parcels.
- Use that current exported boundary bbox as the center cell of a 3-by-3 data acquisition patch.
- Pull satellite/orthoimagery, topo, DEM, hillshade, contours, and lidar for the full 9-patch. Keep trail data inside the park working envelope unless AOP confirms otherwise.

#aop #bounds #aoi #parcels #imagery #lidar

-----

## Current Working Bounds

Current published boundary feature:
- Name: `AOP working parcel envelope - included parcel candidates`
- Source layer: Tennessee Comptroller `TN_County_Parcel_Map` FeatureServer layer `35` / `Marion_Parcels`
- Import script: `mvp/scripts/import_aop_parcel_boundary.sh`
- Import SQL: `mvp/scripts/import_aop_parcel_boundary.sql`
- Export checked from: `website/data/publish.geojson`
- GIS concept artifact: `brain/output/aop_9_patch_data_bounds.geojson`
- Date recorded: 2026-05-20

The current boundary was assembled from two parcel features:

| Parcel | Assessment parcel ID | Address field | Calculated acres | Deed acres |
| --- | --- | --- | ---: | ---: |
| `110 008.00` | `058 110    00800 000 2023` | `ELLIS COVE RD 1040` | `502.49725246` | `483.46` |
| `093 030.01` | `058 093    03001 000 2023` | `ELLIS RD` | `89.8211522` | `90` |

Combined parcel reference totals:
- Calculated acres: `592.31840466`
- Deed acres: `573.46`

How it was assembled:
1. The importer queried the Comptroller ArcGIS FeatureServer with:
   `Assessment_Data_58_ADDRESS = 'ELLIS COVE RD 1040' OR Assessment_Data_58_ID = '093 030.01'`.
2. It required exactly the two expected parcel assessment IDs: `110 008.00` and `093 030.01`.
3. It stored raw ArcGIS features in `raw.arcgis_feature_captures`.
4. It upserted both parcel rows into `core.parcels`.
5. It built the publishable working envelope by collecting and unary-unioning the two parcel geometries into a `MultiPolygon`.

Interpretation:
- This is source-backed parcel-reference context, not a legal survey.
- It is a candidate AOP working envelope with medium confidence.
- It gets close to the official 600+ acre AOP claim but does not fully reconcile it.

## Center Cell Bbox

Use the exported boundary bbox as the center cell for data acquisition planning.

Bbox order: west, south, east, north.

```text
-85.761008221, 35.084085624, -85.739081159, 35.101007060
```

Approximate center-cell span at this latitude:
- East-west: `1,999 m`
- North-south: `1,877 m`

## 9-Patch Data Bounds Concept

The data acquisition patch is a 3-by-3 grid where the current boundary bbox is the center cell.

Use this for:
- TDOT / TNMap orthoimagery and imagery date checks.
- NAIP fallback imagery.
- USGS topo and historical topo reference.
- USGS 3DEP DEM, hillshade, slope, contours, and drainage.
- Tennessee / USGS lidar availability and point cloud pulls if needed.

Do not use this as a trail expansion area. Trails stay in the park working envelope. If a trail claim appears outside the current parcel envelope, treat it as a discrepancy or adjacent-context lead until AOP confirms the land/trail relationship.

Full 9-patch bbox:

```text
-85.782935283, 35.067164188, -85.717154097, 35.117928496
```

Approximate full span:
- East-west: `5,998 m`
- North-south: `5,632 m`

## Patch Cells

Each cell uses the same lon/lat span as the current center bbox. Coordinates are WGS84 lon/lat and should be reprojected in QGIS for measured work.

| Cell | Role | West | South | East | North |
| --- | --- | ---: | ---: | ---: | ---: |
| `NW` | raster / terrain context | `-85.782935283` | `35.101007060` | `-85.761008221` | `35.117928496` |
| `N` | raster / terrain context | `-85.761008221` | `35.101007060` | `-85.739081159` | `35.117928496` |
| `NE` | raster / terrain context | `-85.739081159` | `35.101007060` | `-85.717154097` | `35.117928496` |
| `W` | raster / terrain context | `-85.782935283` | `35.084085624` | `-85.761008221` | `35.101007060` |
| `C` | current parcel-envelope bounds | `-85.761008221` | `35.084085624` | `-85.739081159` | `35.101007060` |
| `E` | raster / terrain context | `-85.739081159` | `35.084085624` | `-85.717154097` | `35.101007060` |
| `SW` | raster / terrain context | `-85.782935283` | `35.067164188` | `-85.761008221` | `35.084085624` |
| `S` | raster / terrain context | `-85.761008221` | `35.067164188` | `-85.739081159` | `35.084085624` |
| `SE` | raster / terrain context | `-85.739081159` | `35.067164188` | `-85.717154097` | `35.084085624` |

## Implementation Notes

The concept cells are also written as GeoJSON at `brain/output/aop_9_patch_data_bounds.geojson` so they can be loaded into QGIS. If this becomes a database layer, suggested fields are:
- `cell_code`
- `role`
- `west`
- `south`
- `east`
- `north`
- `source`
- `generated_on`
- `notes`

Use WGS84 bbox coordinates for service queries and downloads. Use a projected CRS in QGIS for measurement, raster processing, buffering, or print layout.

## Data Acquisition Findings

Recorded on 2026-05-20:

- Concrete imagery, DEM, lidar, contour, and US Topo products for the full 9-patch are listed in `brain/output/aop_9_patch_data_acquisition_manifest.md`.
- Best immediate imagery source: TDOT / TNMap `IMAGERY_WEB_MERCATOR`; the AOP point query returned Marion County `TN_Ortho_Year = 2022`.
- Best immediate elevation source: USGS 3DEP 1-meter DEM tile `USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`, which covers the full 9-patch.
- Raw lidar is available from USGS as 24 LAZ tiles totaling about 2.79 GB. Use it only if the 1-meter DEM and derived hillshade are not enough.
- USGS contour GeoPackage `ELEV_Chattanooga_W_TN_1X1_GPKG.zip` covers the AOI.
- Current US Topo GeoPDF coverage crosses the Orme, TN and South Pittsburg, TN quadrangles.

## Lidar Tile Index Layer

Recorded on 2026-05-20:

- The 24 USGS 3DEP LAZ tile footprints are now a viewer overlay at `website/data/aop_lidar_tiles.geojson`.
- Source: TNM products API query `datasets=Lidar Point Cloud (LPC)&prodFormats=LAZ&bbox=<9-patch>`.
- Each feature carries `tile_code`, `title`, `project`, `publication_date`, `size_bytes`, `size_mb`, `download_url`, `meta_url`, `source_name`, and `source_id`.
- Footprints come straight from each tile's `boundingBox`; they are inventory metadata, not measured coverage envelopes.
- The static viewer exposes the layer behind a toggle labeled `Lidar tile index (USGS 3DEP)` with fill, outline, and `tile_code` labels, plus a popup that links the LAZ download.

## Lidar Hillshade and 3D Terrain Layers

Recorded on 2026-05-20:

- The viewer now renders a lidar-derived hillshade and a 3D terrain view directly from AWS Terrain Tiles (Terrarium-encoded raster-DEM). In the AOP block the upstream elevation is USGS 3DEP, which is lidar-derived; that is the closest "see the lidar" the viewer can show without downloading the LAZ tiles.
- Source: `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`, `encoding: 'terrarium'`, `maxzoom: 15`.
- 2D shading: MapLibre `hillshade` layer `lidar-hillshade`, toggle `Lidar hillshade (USGS 3DEP)`.
- 3D terrain: `map.setTerrain` with exaggeration 1.4 plus `map.setSky` atmosphere, toggle `3D terrain (AWS Terrarium / USGS 3DEP)`. Drag with right-click / two-finger to tilt and rotate.
- Attribution shown in the viewer credits AWS Terrain Tiles (USGS 3DEP, SRTM, GMTED, ETOPO1).
- Verified with `mvp/scripts/playwright_verify_lidar_tiles.py` on 2026-05-20: 21 of 21 checks PASS, 109 AWS Terrarium tile requests during the run, 0 console errors. Screenshots: `brain/output/playwright_lidar_initial.png`, `playwright_lidar_tiles_on.png`, `playwright_lidar_hillshade_on.png`, `playwright_lidar_hillshade_plus_tiles.png`, `playwright_lidar_terrain_3d.png`, `playwright_lidar_all_off.png`.
- The hillshade and 3D terrain are global-DEM derivatives, not the locally-derived 1-meter DEM lidar product. For lidar-grade contour lines clipped to the 9-patch, install a GDAL toolchain (Docker `osgeo/gdal` or `brew install gdal`) and clip/contour `USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`; that path remains open.

## Asphalt Roads Layer

Recorded on 2026-05-20:

- Source: USGS National Map Transportation MapServer `https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer`.
- Layers queried over the 9-patch bbox: `29` Controlled-access Highways (10 features), `30` Secondary Highways (0), `31` Local Connecting Roads (28), `32` Local Roads (76), `33` Ramps (0). Total `114` paved-network features.
- Excluded by design: layer `35` 4WD Roads, layer `36` Closed Roads, layer `37` Trails — those would not be asphalt.
- Importer: `mvp/scripts/import_usgs_roads.sh` (curl + jq, atomic write).
- Output: `website/data/aop_roads.geojson` — each feature tagged with `road_class` (`controlled_access`, `secondary`, `local_connecting`, `local`, `ramp`) plus `name`, `mtfcc_code`, `tnmfrc`, and route designators.
- Viewer: toggle `Asphalt roads (USGS National Map)`, default-on. Stacked layers `roads-local-casing` + `roads-local`, `roads-connecting-casing` + `roads-connecting`, `roads-controlled-casing` + `roads-controlled`, plus a `roads-labels` symbol layer along the line. Click any class for a popup with name, MTFCC, and route designators.
- Notable named features in-AOI: I-24, Ellis Cove Rd (the AOP access road), Ellis Rd, Battlecreek Rd, Fiery Gizzard Rd, Sweetens Cove Rd.
- Picked over TNMap MAJOR_ROADS (too sparse — interstates and state highways only, misses county/park-access roads) and Overpass/OSM (would require per-way `surface=*` filtering and local TN ways are not reliably tagged for surface).
