#!/usr/bin/env bash
set -euo pipefail

# Build lidar-grade contour lines for the AOP 9-patch from the USGS 3DEP 1m DEM.
#
# Pipeline: download/cache DEM -> clip to 9-patch -> low-pass smooth the DEM
# (1m -> 2m cubic spline, strips lidar micro-noise) -> gdal_contour at 5ft ->
# attribute (elev_ft + indexed flag) -> light Douglas-Peucker thin -> repair
# crossings -> WGS84 GeoJSON for the viewer.
#
# The DEM low-pass removes the noise that makes raw isolines crinkle. Vertices
# are then thinned with a light Douglas-Peucker pass for file size -- but DP
# treats each contour independently and can push tightly-spaced neighbours
# across each other on steep ground. Contours are isolines and cannot cross,
# so repair_crossings.py restores any crossed segment to its raw geometry.
#
# GDAL runs via Docker (host has no GDAL). macOS blocks Docker from reading the
# repo under ~/Documents, so all GDAL work is staged in /private/tmp and the
# final outputs are copied back with host cp. See brain/spinup/mvp_runbook.md.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

GDAL_IMG="ghcr.io/osgeo/gdal:ubuntu-small-latest"

DEM_NAME="USGS_one_meter_x61y389_TN_27County_blk4_2015.tif"
DEM_URL="https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/TN_27County_blk4_2015/TIFF/${DEM_NAME}"
DEM_CACHE="$REPO_DIR/mvp/cache/dem/$DEM_NAME"
CONTOUR_CACHE="$REPO_DIR/mvp/cache/contours"

# 9-patch acquisition envelope (WGS84 west,south,east,north)
BBOX_W="-85.782935283"
BBOX_S="35.067164188"
BBOX_E="-85.717154097"
BBOX_N="35.117928496"

CONTOUR_INTERVAL_M="1.524"   # 5 ft
INDEX_FT="25"                # indexed (major) contour every 25 ft
SMOOTH_RES_M="2"             # DEM low-pass: resample 1m -> this, cubic spline
SIMPLIFY_M="0.5"             # Douglas-Peucker tolerance (light, keeps crossings rare)
DEM_NODATA="-999999"

WORK="/private/tmp/aop_gdal"
# The full repaired contour set is the SILVER layer (medallion rename + curation,
# 2026-06-14); the served GOLD is the lean subset produced by curate_contours_gold.py
# below (all index lines 9-patch-wide + minor lines clipped to the park cell).
OUT_GEOJSON="$REPO_DIR/website/data/silver_aop_contours.geojson"
OUT_GOLD="$REPO_DIR/website/data/gold_aop_contours.geojson"
OUT_GPKG="$CONTOUR_CACHE/aop_contours.gpkg"
OUT_CLIP_DEM="$REPO_DIR/mvp/cache/dem/dem_9patch.tif"
OUT_SMOOTH_DEM="$REPO_DIR/mvp/cache/dem/dem_9patch_smooth.tif"

echo "==> AOP contour build"

# 1. Cache the DEM ----------------------------------------------------------
mkdir -p "$(dirname "$DEM_CACHE")" "$CONTOUR_CACHE"
if [[ ! -f "$DEM_CACHE" ]]; then
  echo "==> Downloading 1m DEM (~477 MB)"
  curl -fSL --retry 3 -o "$DEM_CACHE" "$DEM_URL"
else
  echo "==> DEM already cached: $DEM_CACHE"
fi

# 2. Stage inputs where Docker can read them --------------------------------
echo "==> Staging DEM and repair script into $WORK"
mkdir -p "$WORK"
cp "$DEM_CACHE" "$WORK/dem.tif"
cp "$SCRIPT_DIR/repair_crossings.py" "$WORK/repair_crossings.py"

# 3. Run the GDAL pipeline in one container pass ----------------------------
echo "==> Clipping, smoothing DEM, contouring, attributing, simplifying, repairing"
docker run --rm -v "$WORK:/data" "$GDAL_IMG" sh -c "
set -e

# clip to the 9-patch, keep the DEM's native CRS (UTM 16N), 1 m posting
rm -f /data/dem_9patch.tif
gdalwarp -te $BBOX_W $BBOX_S $BBOX_E $BBOX_N -te_srs EPSG:4326 \
  -of GTiff -co COMPRESS=LZW -co TILED=YES \
  /data/dem.tif /data/dem_9patch.tif

# low-pass smooth: resample 1m -> ${SMOOTH_RES_M}m with a cubic spline kernel.
# this strips lidar micro-noise (vegetation residue, scan texture) so the
# isolines flow instead of crinkling. kept light to preserve real micro-relief.
rm -f /data/dem_smooth.tif
gdalwarp -tr $SMOOTH_RES_M $SMOOTH_RES_M -r cubicspline \
  -of GTiff -co COMPRESS=LZW -co TILED=YES \
  /data/dem_9patch.tif /data/dem_smooth.tif

# 5ft contours from the smoothed DEM
rm -f /data/contours_raw.gpkg
gdal_contour -a elev_m -i $CONTOUR_INTERVAL_M -snodata $DEM_NODATA \
  -nln contour -f GPKG /data/dem_smooth.tif /data/contours_raw.gpkg

# full-resolution attributed GeoPackage (elev_ft + indexed flag), native CRS
rm -f /data/aop_contours.gpkg
ogr2ogr -f GPKG -nln contour -dialect SQLITE \
  -sql \"SELECT *, CAST(ROUND(elev_m/0.3048) AS INTEGER) AS elev_ft, \
    (CAST(ROUND(elev_m/0.3048) AS INTEGER) % $INDEX_FT = 0) AS idx FROM contour\" \
  /data/aop_contours.gpkg /data/contours_raw.gpkg

# thin vertices with Douglas-Peucker (native CRS, so tolerance is in metres)
rm -f /data/aop_contours_simplified.gpkg
ogr2ogr -f GPKG -nln contour -simplify $SIMPLIFY_M \
  /data/aop_contours_simplified.gpkg /data/aop_contours.gpkg

# reproject both the raw and the thinned contours to WGS84 GeoJSON. the raw
# copy is the non-crossing reference the repair pass restores segments from.
rm -f /data/aop_contours_raw.geojson /data/aop_contours_dp.geojson
ogr2ogr -f GeoJSON -t_srs EPSG:4326 -lco COORDINATE_PRECISION=6 \
  /data/aop_contours_raw.geojson /data/aop_contours.gpkg
ogr2ogr -f GeoJSON -t_srs EPSG:4326 -lco COORDINATE_PRECISION=6 \
  /data/aop_contours_dp.geojson /data/aop_contours_simplified.gpkg

# repair: DP can cross tightly-spaced contours; restore crossed segments to raw.
rm -f /data/aop_contours.geojson
python3 /data/repair_crossings.py \
  --raw /data/aop_contours_raw.geojson \
  --simplified /data/aop_contours_dp.geojson \
  --out /data/aop_contours.geojson
"

# 4. Copy outputs back into the repo ----------------------------------------
echo "==> Writing outputs"
cp "$WORK/aop_contours.geojson" "$OUT_GEOJSON"   # full set -> SILVER
cp "$WORK/aop_contours.gpkg" "$OUT_GPKG"
cp "$WORK/dem_9patch.tif" "$OUT_CLIP_DEM"
cp "$WORK/dem_smooth.tif" "$OUT_SMOOTH_DEM"

# Curate the lean served GOLD from the full SILVER set: all index lines across the
# 9-patch + minor lines clipped to the park center cell (~13 MB -> ~4 MB). Pure
# Python (shapely), no GDAL — this step runs on any machine even when the GDAL
# build above is skipped, as long as silver_aop_contours.geojson exists.
echo "==> Curating served gold (curate_contours_gold.py)"
python3 "$REPO_DIR/mvp/scripts/curate_contours_gold.py" --in "$OUT_GEOJSON" --out "$OUT_GOLD"

FEATURES="$(node -e 'const fs=require("fs");const d=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));console.log(d.features.length)' "$OUT_GEOJSON")"
GOLD_FEATURES="$(node -e 'const fs=require("fs");const d=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));console.log(d.features.length)' "$OUT_GOLD")"
echo "==> Done"
echo "    Silver (full)   : $OUT_GEOJSON ($(du -h "$OUT_GEOJSON" | cut -f1), $FEATURES features)"
echo "    Gold (served)   : $OUT_GOLD ($(du -h "$OUT_GOLD" | cut -f1), $GOLD_FEATURES features)"
echo "    GeoPackage (full-res, gitignored cache): $OUT_GPKG"
