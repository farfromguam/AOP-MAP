#!/usr/bin/env bash
set -euo pipefail

# Build the AOP forest land-cover layer for the FULL 9-patch acquisition AOI.
#
# This is the wide-area sibling of build_landcover.sh. That script classifies
# the park-boundary cell at 0.6 m and clips to the AOP boundary; this one
# covers all nine cells (the 3x3 grid in research/aop_data_bounds.md) so the
# viewer has land-cover context around the park, not just inside it.
#
# The NAIP ImageServer caps a single export at 4000 x 4000 px, and the 9-patch
# is ~6 km wide -- 0.6 m pixels would need ~10000 px. So the 9-patch ortho is
# pulled at ~1.5 m: one 3996 x 3742 export covering the whole AOI. That is
# coarser than the park layer by design -- the 9-patch layer ships under the
# crisp park layer at reduced opacity as surrounding context. classify_land-
# cover.py is resolution-aware (it rescales its windows from the geotransform),
# so the same classifier handles both the 0.6 m and the ~1.5 m ortho.
#
# Pipeline: download/cache the leaf-on 4-band NAIP ortho for the 9-patch,
# build (or reuse) the 9-patch lidar canopy-height model -> classify into five
# land-cover classes -> polygonize -> light vertex simplify -> Chaikin smooth
# -> clip to the 9-patch rectangle -> WGS84 GeoJSON.
#
# The layer is a full coverage (forest_deciduous, forest_evergreen,
# open_grass, open_meadow, open_bare) tiling the whole 9-patch rectangle.
#
# GDAL runs via Docker (host has no GDAL). macOS blocks Docker from reading the
# repo under ~/Documents, so all GDAL work is staged in /private/tmp and the
# final outputs are copied back with host cp. See brain/spinup/mvp_runbook.md.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

GDAL_IMG="ghcr.io/osgeo/gdal:ubuntu-small-latest"

# Full 9-patch bbox (west,south,east,north) from research/aop_data_bounds.md.
NINE_PATCH_W="-85.782935283"
NINE_PATCH_S="35.067164188"
NINE_PATCH_E="-85.717154097"
NINE_PATCH_N="35.117928496"

# NAIP 2023 (acquired June, leaf-on), 4-band, from the USDA NAIP public
# ImageServer (USDA_CONUS_PRIME). 3996 x 3742 keeps both axes under the
# 4000 px export cap; over the ~6.0 x 5.6 km AOI that lands at ~1.5 m pixels.
NAIP_BBOX="${NINE_PATCH_W},${NINE_PATCH_S},${NINE_PATCH_E},${NINE_PATCH_N}"
NAIP_SIZE="3996,3742"
NAIP_EXPORT="https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/exportImage?bbox=${NAIP_BBOX}&bboxSR=4326&imageSR=26916&size=${NAIP_SIZE}&format=tiff&pixelType=U8&interpolation=RSP_NearestNeighbor"

NAIP_CACHE="$REPO_DIR/mvp/cache/imagery/naip_2023_9patch.tif"
CHM_CACHE="$REPO_DIR/mvp/cache/lidar/chm_9patch.tif"
LC_CACHE="$REPO_DIR/mvp/cache/landcover"

WORK="/private/tmp/aop_lc9"
OUT_GEOJSON="$REPO_DIR/website/data/aop_landcover_9patch.geojson"

echo "==> AOP 9-patch land-cover build"

# 1. Cache the NAIP ortho ---------------------------------------------------
mkdir -p "$(dirname "$NAIP_CACHE")" "$LC_CACHE"
if [[ ! -f "$NAIP_CACHE" ]]; then
  echo "==> Downloading NAIP 2023 leaf-on 4-band ortho for the 9-patch (USDA ImageServer)"
  # A 15-megapixel mosaic export will not stream inline. The robust path is
  # the two-step ArcGIS pattern: request f=json to trigger generation and
  # return an href, then download the generated TIFF from that href.
  href="$(curl -fsSL --max-time 240 "${NAIP_EXPORT}&f=json" \
    | python3 -c 'import sys,json; print(json.load(sys.stdin)["href"])')"
  curl -fSL --retry 3 --max-time 420 -o "$NAIP_CACHE" "$href"
else
  echo "==> NAIP 9-patch ortho already cached: $NAIP_CACHE"
fi
echo "    $(du -h "$NAIP_CACHE" | cut -f1)  $NAIP_CACHE"

# 1b. Ensure the 9-patch lidar canopy-height model exists -------------------
# Stage 1 of the classifier (forest vs open) thresholds tree height; the
# 9-patch CHM is built from all 24 USGS 3DEP LAZ tiles. Reuse if present.
if [[ ! -f "$CHM_CACHE" ]]; then
  echo "==> 9-patch CHM missing -- running build_canopy_height.sh 9patch"
  bash "$SCRIPT_DIR/build_canopy_height.sh" 9patch
else
  echo "==> 9-patch CHM already cached: $CHM_CACHE"
fi

# 2. Stage inputs where Docker can read them --------------------------------
echo "==> Staging inputs into $WORK"
mkdir -p "$WORK"
cp "$NAIP_CACHE" "$WORK/naip.tif"
cp "$CHM_CACHE" "$WORK/chm.tif"
cp "$SCRIPT_DIR/classify_landcover.py" "$WORK/classify_landcover.py"
cp "$SCRIPT_DIR/smooth_landcover.py" "$WORK/smooth_landcover.py"

# 3. Classify -> polygonize -> simplify -> smooth -> clip -------------------
echo "==> Classifying and vectorizing"
docker run --rm -v "$WORK:/data" "$GDAL_IMG" sh -c "
set -e

# pixel classification -> single-band class raster (classifier rescales its
# windows to the ~1.5 m pixel size read from the geotransform)
python3 /data/classify_landcover.py /data/naip.tif /data/chm.tif /data/class.tif /data/preview.png

# polygonize connected class regions (class 0 = nodata is skipped)
rm -f /data/class.gpkg
gdal_polygonize.py /data/class.tif -b 1 -f GPKG /data/class.gpkg lc DN

# vertex simplify + keep every land-cover class (DN > 0; only nodata is
# dropped); stays in EPSG:26916 so the tolerance is metric. The 9-patch is a
# dimmed wide-area context layer, so it is simplified harder than the crisp
# park build to keep the GeoJSON light.
rm -f /data/class_simpl.gpkg
ogr2ogr -f GPKG -simplify 3.0 -where \"DN > 0\" \
  /data/class_simpl.gpkg /data/class.gpkg lc

# reproject to WGS84 for the smoothing pass
rm -f /data/class_simpl.geojson
ogr2ogr -f GeoJSON -t_srs EPSG:4326 \
  /data/class_simpl.geojson /data/class_simpl.gpkg

# Chaikin smooth + rename DN -> class
python3 /data/smooth_landcover.py /data/class_simpl.geojson /data/class_smooth.geojson

# repair any self-intersections Chaikin can pinch into thin polygons, so the
# rectangle clip's GEOS overlay gets only valid input
rm -f /data/class_valid.geojson
ogr2ogr -f GeoJSON -makevalid -nlt PROMOTE_TO_MULTI \
  /data/class_valid.geojson /data/class_smooth.geojson

# clip to the 9-patch rectangle so the layer has clean rectangular edges
rm -f /data/aop_landcover_9patch.geojson
ogr2ogr -f GeoJSON \
  -clipsrc $NINE_PATCH_W $NINE_PATCH_S $NINE_PATCH_E $NINE_PATCH_N \
  -lco COORDINATE_PRECISION=6 \
  /data/aop_landcover_9patch.geojson /data/class_valid.geojson
"

# 4. Copy outputs back into the repo ----------------------------------------
echo "==> Writing outputs"
cp "$WORK/aop_landcover_9patch.geojson" "$OUT_GEOJSON"
cp "$WORK/class.tif" "$LC_CACHE/class_9patch.tif"
cp "$WORK/preview.png" "$LC_CACHE/preview_9patch.png"

FEATURES="$(node -e 'const d=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));const c={};for(const f of d.features){const k=f.properties.class;c[k]=(c[k]||0)+1;}console.log(d.features.length+" features "+JSON.stringify(c))' "$OUT_GEOJSON")"
echo "==> Done"
echo "    GeoJSON : $OUT_GEOJSON ($(du -h "$OUT_GEOJSON" | cut -f1), $FEATURES)"
echo "    Class raster + preview (gitignored cache): $LC_CACHE"
