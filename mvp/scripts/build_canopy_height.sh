#!/usr/bin/env bash
set -euo pipefail

# Build a lidar canopy-height model (CHM) for the AOP park.
#
# The land-cover classifier needs a crisp forest mask. Optical imagery cannot
# give one: leaf-off canopy texture works but blurs the edge, and leaf-on
# canopy is too smooth to threshold at all (see classify_landcover.py and
# tasks/01_mvp/landcover_layer.md). Tree height does it cleanly -- trees are
# tall, grass is not -- so this script turns the USGS 3DEP lidar point cloud
# into a canopy-height raster the classifier can threshold per-pixel.
#
# Pipeline: download/cache the LAZ tiles over the park -> PDAL computes height
# above ground per point (Delaunay TIN of the ground-classified returns) ->
# grid the max height per cell into a per-tile CHM -> mosaic -> warp onto the
# exact NAIP ortho grid so the classifier can read imagery and CHM together.
#
# Source: USGS 3DEP LPC, project USGS_LPC_TN_27County_blk4_2015_LAS_2018.
# The cloud is NAD83(2011) / Tennessee State Plane in US survey feet (EPSG
# 6576); height above ground is converted to metres in the PDAL pipeline.
#
# PDAL + GDAL run via the pdal/pdal Docker image. macOS blocks Docker from
# reading the repo under ~/Documents, so all work is staged in /private/tmp
# and the final raster is copied back with host cp. See spinup/mvp_runbook.md.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

PDAL_IMG="pdal/pdal:latest"

# The 6 USGS 3DEP LAZ tiles whose footprints intersect the park centre cell
# (from website/data/aop_lidar_tiles.geojson).
TILES=(2038269NE 2038269NW 2038269SE 2038269SW 2038277SE 2038277SW)
LAZ_BASE="https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/USGS_LPC_TN_27County_blk4_2015_LAS_2018/laz"

LIDAR_CACHE="$REPO_DIR/mvp/cache/lidar"
NAIP_REF="$REPO_DIR/mvp/cache/imagery/naip_2023_aop.tif"   # CHM is warped to this grid
OUT_CHM="$LIDAR_CACHE/chm_aop.tif"

WORK="/private/tmp/aop_chm"

echo "==> AOP canopy-height (CHM) build"

if [[ ! -f "$NAIP_REF" ]]; then
  echo "ERROR: NAIP reference ortho missing: $NAIP_REF" >&2
  echo "       run build_landcover.sh once first to cache it." >&2
  exit 1
fi

# 1. Cache the LAZ tiles ----------------------------------------------------
mkdir -p "$LIDAR_CACHE"
for t in "${TILES[@]}"; do
  f="$LIDAR_CACHE/USGS_LPC_TN_27County_blk4_2015_${t}_LAS_2018.laz"
  if [[ -f "$f" ]]; then
    echo "==> tile $t cached ($(du -h "$f" | cut -f1))"
  else
    echo "==> downloading tile $t"
    curl -fSL --retry 3 --max-time 600 -o "$f" \
      "$LAZ_BASE/USGS_LPC_TN_27County_blk4_2015_${t}_LAS_2018.laz"
  fi
done

# 2. Stage inputs where Docker can read them --------------------------------
echo "==> Staging inputs into $WORK"
rm -rf "$WORK"
mkdir -p "$WORK"
for t in "${TILES[@]}"; do
  cp "$LIDAR_CACHE/USGS_LPC_TN_27County_blk4_2015_${t}_LAS_2018.laz" "$WORK/${t}.laz"
done
cp "$NAIP_REF" "$WORK/naip_ref.tif"

# PDAL pipeline template. Per tile the in/out filenames are overridden on the
# CLI. filters.hag_delaunay adds HeightAboveGround (height over a TIN of the
# ground-classified returns); filters.assign converts ftUS -> metres;
# filters.range clamps negative noise and absurd highpoints; writers.gdal
# grids the per-cell max height at 3 ft (~0.9 m, a touch coarser than the
# lidar point spacing).
cat > "$WORK/chm_pipeline.json" <<'EOF'
[
  {"type":"readers.las","filename":"/data/in.laz"},
  {"type":"filters.hag_delaunay"},
  {"type":"filters.assign","value":"HeightAboveGround = HeightAboveGround * 0.3048006096"},
  {"type":"filters.range","limits":"HeightAboveGround[0:120]"},
  {"type":"writers.gdal","filename":"/data/out.tif","dimension":"HeightAboveGround",
   "output_type":"max","resolution":3.0,"nodata":-9999}
]
EOF

# 3. Read the NAIP reference grid (SRS, extent, pixel count) ----------------
# The CHM is warped onto exactly this grid so the classifier can read the
# ortho and the CHM as pixel-aligned arrays.
GRID="$(docker run --rm -v "$WORK:/data" "$PDAL_IMG" python3 -c "
import json, subprocess
d = json.loads(subprocess.check_output(['gdalinfo', '-json', '/data/naip_ref.tif']))
ul = d['cornerCoordinates']['upperLeft']
lr = d['cornerCoordinates']['lowerRight']
w, h = d['size']
print(ul[0], lr[1], lr[0], ul[1], w, h)
")"
read -r XMIN YMIN XMAX YMAX W H <<< "$GRID"
echo "==> NAIP grid: EPSG:26916  te=$XMIN $YMIN $XMAX $YMAX  ts=$W $H"

# 4. Per-tile CHM -> mosaic -> warp to the NAIP grid ------------------------
echo "==> Building canopy height (PDAL hag + grid, then warp to NAIP grid)"
docker run --rm -v "$WORK:/data" "$PDAL_IMG" sh -c "
set -e
for t in ${TILES[*]}; do
  echo \"    hag + grid: \$t\"
  pdal pipeline /data/chm_pipeline.json \
    --readers.las.filename=/data/\${t}.laz \
    --writers.gdal.filename=/data/chmtile_\${t}.tif
done

# mosaic the per-tile CHMs (all in EPSG:6576)
gdalbuildvrt -q -srcnodata -9999 -vrtnodata -9999 \
  /data/chm_mosaic.vrt /data/chmtile_*.tif

# warp onto the NAIP grid: same SRS, extent and pixel count
gdalwarp -q -overwrite -t_srs EPSG:26916 \
  -te $XMIN $YMIN $XMAX $YMAX -ts $W $H -r bilinear \
  -srcnodata -9999 -dstnodata -9999 -ot Float32 -co COMPRESS=LZW \
  /data/chm_mosaic.vrt /data/chm_aop.tif
gdalinfo -stats /data/chm_aop.tif | grep -E 'Size is|STATISTICS_M(IN|AX|EAN)'
"

# 5. Copy the CHM back into the cache ---------------------------------------
echo "==> Writing output"
cp "$WORK/chm_aop.tif" "$OUT_CHM"
echo "==> Done"
echo "    CHM (gitignored cache): $OUT_CHM ($(du -h "$OUT_CHM" | cut -f1))"
echo "    grid matches $NAIP_REF -- classify_landcover.py reads both."
