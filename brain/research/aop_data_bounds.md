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
