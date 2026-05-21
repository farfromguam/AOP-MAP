# AOP 9-Patch Data Acquisition Manifest

Generated: 2026-05-20

AOI bbox, WGS84 west/south/east/north:

```text
-85.782935283, 35.067164188, -85.717154097, 35.117928496
```

This manifest records concrete public data found for the AOP 9-patch. Use it for raster, terrain, and topo context only. Trail claims still stay inside the current park working envelope unless AOP confirms otherwise.

## Best Immediate Stack

1. TDOT / TNMap 2022 orthoimagery for visual inspection.
2. USGS 3DEP 1-meter DEM for hillshade, slope, contours, and print terrain.
3. USGS 3DEP LAZ point cloud only if the 1-meter DEM is not enough.
4. USDA / USGS NAIP for downloadable aerial fallback and comparison.
5. USGS US Topo and contour GeoPackage for cartographic/topographic context.

## Imagery

### TDOT / TNMap Orthoimagery

- Service: `https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer`
- Layer: `Tennessee Ortho Index`
- AOP point query result: Marion County has `TN_Ortho_Year = 2022`, `NAIP_Year = 2021`.
- Use in QGIS as an ArcGIS REST service or WMTS inspection basemap.
- Notes: TNMap says source imagery is 1 ft before 2022 and 6 in from 2022 onward. Treat service use separately from redistribution; do not publish exported imagery unless licensing/permission is clear.

### USGS NAIP Image Service

- Service: `https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer`
- AOP bbox query returned two downloadable 2021 NAIP quarter-quads:

| Name | Year | Acquisition date | Resolution | Bands | Download |
| --- | ---: | --- | --- | ---: | --- |
| `m_3508558_ne_16_060_20211107` | 2021 | 2021-11-07 | 0.6 m | 4 | https://earthexplorer.usgs.gov/download/options/naip/3084501 |
| `m_3508559_nw_16_060_20211107` | 2021 | 2021-11-07 | 0.6 m | 4 | https://earthexplorer.usgs.gov/download/options/naip/3084506 |

### USDA 2023 NAIP Date Index

- ArcGIS item: `2023 Tennessee Image Dates`
- Item id: `089161fe29a94397b6ff995fdfa012b6`
- Service: `https://services.arcgis.com/LLVEmB8Lsae3Um4s/arcgis/rest/services/2023_Tennessee_Image_Dates/FeatureServer`
- AOP bbox intersects six 2023 acquisition-date polygons, all `2023-06-09`, natural color (`NC`), digital Leica Geosystems ContentMapper.
- This confirms newer NAIP coverage exists over the AOI, but the direct downloadable imagery link was not resolved in this pass.
- USDA Geospatial Data Gateway was retired on 2026-03-31. USDA now points many direct geospatial downloads to Box: `https://nrcs.app.box.com/v/gateway/`; direct NAIP folder: `https://nrcs.app.box.com/v/naip`.

### NAIP AWS

- Registry: `https://registry.opendata.aws/naip/`
- Buckets: `naip-analytic`, `naip-source`, `naip-visualization`
- Notes: public-domain-with-attribution NAIP on AWS is available in requester-pays buckets. Use for cloud-native access if the exact 2023 tile paths are resolved.

## Elevation / Lidar

### USGS 3DEP 1-Meter DEM

- Product: `USGS one meter x61y389 TN 27County blk4 2015`
- Publication date: 2020-03-30
- File last modified: 2026-02-14
- Approx size: 499,956,299 bytes
- Download: `https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/TN_27County_blk4_2015/TIFF/USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`
- Coverage bbox: `-85.7924866883, 35.0555407932, -85.684039456, 35.1469521929`
- Interpretation: one tile covers the full 9-patch.
- Downloaded 2026-05-20 to `mvp/cache/dem/` (gitignored). SHA-256:
  `f21b4dd6219e77d7d6b3c0f61416b02943202150bf84bc79f16c0406d568306a`
- Native CRS confirmed by `gdalinfo`: `NAD83 / UTM zone 16N` (EPSG:26916), 1 m pixels, 10012 x 10012.
- Used by `mvp/scripts/build_contours.sh` to generate the viewer's 5-foot lidar contour layer.

### USGS 3DEP Dynamic Elevation Service

- Service: `https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer`
- Use for quick hillshade, slope, aspect, elevation-tinted hillshade, and dynamic contour visualization.
- Notes: for production map derivatives, prefer the downloaded 1-meter DEM above and generate local hillshade/slope/contours in QGIS.

### USGS 3DEP LAZ Point Cloud

- Dataset: `USGS_LPC_TN_27County_blk4_2015_LAS_2018`
- Product count intersecting bbox: 24 LAZ tiles
- Total size: 2,788,061,014 bytes
- Use only if DEM-derived hillshade is insufficient for trail benching, drainage scars, or micro-terrain checks.

| Tile | Size bytes | Download |
| --- | ---: | --- |
| `2024261NE` | 85771165 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2024261NE_LAS_2018.laz |
| `2024269NE` | 102525809 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2024269NE_LAS_2018.laz |
| `2024269SE` | 109955777 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2024269SE_LAS_2018.laz |
| `2024277NE` | 126704123 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2024277NE_LAS_2018.laz |
| `2024277SE` | 110155558 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2024277SE_LAS_2018.laz |
| `2024285SE` | 104264076 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2024285SE_LAS_2018.laz |
| `2038261NE` | 103054258 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038261NE_LAS_2018.laz |
| `2038261NW` | 102346132 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038261NW_LAS_2018.laz |
| `2038269NE` | 121917464 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038269NE_LAS_2018.laz |
| `2038269NW` | 113214067 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038269NW_LAS_2018.laz |
| `2038269SE` | 110996544 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038269SE_LAS_2018.laz |
| `2038269SW` | 117415047 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038269SW_LAS_2018.laz |
| `2038277NE` | 126500126 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038277NE_LAS_2018.laz |
| `2038277NW` | 101844601 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038277NW_LAS_2018.laz |
| `2038277SE` | 114888371 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038277SE_LAS_2018.laz |
| `2038277SW` | 138799823 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038277SW_LAS_2018.laz |
| `2038285SE` | 129603391 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038285SE_LAS_2018.laz |
| `2038285SW` | 99647438 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2038285SW_LAS_2018.laz |
| `2052261NW` | 128928754 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2052261NW_LAS_2018.laz |
| `2052269NW` | 127707237 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2052269NW_LAS_2018.laz |
| `2052269SW` | 131669220 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2052269SW_LAS_2018.laz |
| `2052277NW` | 128828546 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2052277NW_LAS_2018.laz |
| `2052277SW` | 129553972 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2052277SW_LAS_2018.laz |
| `2052285SW` | 121769515 | https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz/USGS_LPC_TN_27County_blk4_2015_2052285SW_LAS_2018.laz |

## Topographic Data

### USGS Contours

- Product: `USGS NED 1/3 arc-second Contours for Chattanooga W, Tennessee 1 x 1 degree`
- Publication date: 2022-10-18
- Approx size: 209,543,596 bytes
- Download: `https://prd-tnm.s3.amazonaws.com/StagedProducts/Contours/GPKG/ELEV_Chattanooga_W_TN_1X1_GPKG.zip`
- Service: `https://carto.nationalmap.gov/arcgis/rest/services/contours/MapServer`

### USGS US Topo GeoPDFs

The 9-patch intersects the Orme and South Pittsburg 7.5-minute quadrangles.

| Quad | Year | Download |
| --- | ---: | --- |
| Orme, TN | 2016 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/PDF/TN/TN_Orme_20160414_TM_geo.pdf |
| Orme, TN | 2013 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/PDF/TN/TN_Orme_20130410_TM_geo.pdf |
| Orme, TN | 2010 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/PDF/TN/TN_Orme_20100504_TM_geo.pdf |
| South Pittsburg, TN | 2016 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/PDF/TN/TN_South_Pittsburg_20160414_TM_geo.pdf |
| South Pittsburg, TN | 2013 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/PDF/TN/TN_South_Pittsburg_20130410_TM_geo.pdf |
| South Pittsburg, TN | 2010 | https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/PDF/TN/TN_South_Pittsburg_20100504_TM_geo.pdf |

### TNMap USGS Topo Service

- Service: `https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/USGS_TOPO/MapServer`
- Use for quick topo overlay in QGIS. Download GeoPDFs above for archived local references.

## Transportation / Roads

### USGS National Map Transportation

- Service: `https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer`
- Paved-network layers used: `29` Controlled-access Highways, `30` Secondary Highways, `31` Local Connecting Roads, `32` Local Roads, `33` Ramps.
- Unpaved/closed layers explicitly excluded: `35` 4WD Roads, `36` Closed Roads, `37` Trails.
- AOP 9-patch counts (2026-05-20): 10 controlled-access (I-24), 0 secondary, 28 local connecting, 76 local, 0 ramps = **114 paved-network features**.
- Importer: `mvp/scripts/import_usgs_roads.sh` writes `website/data/aop_roads.geojson` with a `road_class` property per feature.
- Considered and rejected: TNMap `TRANSPORTATION/MAJOR_ROADS` (interstates + state highways only, no county/park-access roads); OSM via Overpass (119 ways but requires per-way `surface=*` filtering, locally inconsistent).

## Hydrography / Water

### USGS National Hydrography Dataset (NHD)

- Service: `https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer`
- Large-scale (high-resolution) layers — the right resolution for a park AOI:
  `6` Flowline, `9` Area, `12` Waterbody, `0` Point. (The `Small Scale` layers
  4/7/10 are continental-scale generalizations — too coarse here.)
- AOP 9-patch counts (2026-05-20): 85 flowlines (55 perennial stream/river, 30
  artificial path), 1 stream/river area polygon (0.63 km²), 3 lake/pond polygons
  (all small unnamed ponds), 5 points (4 springs, 1 gage) = **94 water features**.
- Named streams: Battle Creek (main creek, modeled as artificial path through the
  area polygon), Big Fiery Gizzard Creek, Kelly Cove Branch, Rogers Cove Branch,
  Sweden Creek, Tate Cove Creek. Named springs: Gilliam, Bible, Fish Trap.
- Importer: `mvp/scripts/import_usgs_hydrography.sh` writes `website/data/aop_water.geojson`
  with `water_kind` + `water_class` + NHD `ftype`/`fcode` per feature.
- Bulk alternative: NHD is also distributed as the National Hydrography Dataset
  Plus High Resolution (NHDPlus HR) by HUC4 (this AOI is HUC4 `0602` — Middle
  Tennessee-Hiwassee) as a downloadable geodatabase, if a full local copy is wanted
  later. The MapServer query is enough for the 9-patch.
- Watershed boundaries (HUC8/10/12) for the 9-patch can be pulled from the USGS
  Watershed Boundary Dataset service `https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer`
  if a drainage-basin layer is wanted; not pulled in this pass.

## Query References

- TNM product API: `https://tnmaccess.nationalmap.gov/api/v1/products`
- DEM query:
  `datasets=Digital Elevation Model (DEM) 1 meter`
- LAZ query:
  `datasets=Lidar Point Cloud (LPC)&prodFormats=LAZ`
- US Topo query:
  `datasets=US Topo&prodFormats=GeoPDF`
- Contour query:
  `datasets=National Elevation Dataset (NED) 1/3 arc-second - Contours&prodFormats=GeoPackage`
