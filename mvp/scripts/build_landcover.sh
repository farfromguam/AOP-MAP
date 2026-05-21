#!/usr/bin/env bash
set -euo pipefail

# Build the AOP vector land-cover layer from NAIP aerial imagery.
#
# Pipeline: download/cache a 4-band NAIP ortho clipped to the park ->
# classify into five land-cover classes (canopy-roughness field for forest vs
# open, then NDVI vigour for the sub-classes) -> polygonize every class ->
# light vertex simplify -> Chaikin smooth -> clip to the AOP boundary ->
# WGS84 GeoJSON for the viewer.
#
# The layer is a full coverage: forest_deciduous, forest_evergreen,
# open_grass, open_meadow, open_bare tile the whole park. Water/hydrography is
# still carried by the separate USGS NHD layer (website/data/aop_water.geojson).
#
# GDAL runs via Docker (host has no GDAL). macOS blocks Docker from reading the
# repo under ~/Documents, so all GDAL work is staged in /private/tmp and the
# final outputs are copied back with host cp. See brain/spinup/mvp_runbook.md.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

GDAL_IMG="ghcr.io/osgeo/gdal:ubuntu-small-latest"

# NAIP 2021 (acquired 2021-11-07), 0.6 m, 4-band, from the USGS NAIP ImageServer.
# bbox is the AOP parcel-envelope centre cell padded ~100 m so the texture
# window has clean context up to the true boundary; the pad is clipped off.
NAIP_BBOX="-85.762008221,35.083085624,-85.738081159,35.102007060"
NAIP_SIZE="3633,3487"   # ~0.6 m pixels in EPSG:26916
NAIP_EXPORT="https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer/exportImage?bbox=${NAIP_BBOX}&bboxSR=4326&imageSR=26916&size=${NAIP_SIZE}&format=tiff&pixelType=U8&interpolation=RSP_NearestNeighbor"

NAIP_CACHE="$REPO_DIR/mvp/cache/imagery/naip_2021_aop.tif"
LC_CACHE="$REPO_DIR/mvp/cache/landcover"
BOUNDARY="$REPO_DIR/website/data/publish.geojson"

WORK="/private/tmp/aop_lc"
OUT_GEOJSON="$REPO_DIR/website/data/aop_landcover.geojson"

echo "==> AOP land-cover build"

# 1. Cache the NAIP ortho ---------------------------------------------------
mkdir -p "$(dirname "$NAIP_CACHE")" "$LC_CACHE"
if [[ ! -f "$NAIP_CACHE" ]]; then
  echo "==> Downloading NAIP 2021 4-band ortho (ImageServer export)"
  # A 12-megapixel mosaic export will not stream inline. The robust path is
  # the two-step ArcGIS pattern: request f=json to trigger generation and
  # return an href, then download the generated TIFF from that href.
  href="$(curl -fsSL --max-time 180 "${NAIP_EXPORT}&f=json" \
    | python3 -c 'import sys,json; print(json.load(sys.stdin)["href"])')"
  curl -fSL --retry 3 --max-time 300 -o "$NAIP_CACHE" "$href"
else
  echo "==> NAIP ortho already cached: $NAIP_CACHE"
fi
echo "    $(du -h "$NAIP_CACHE" | cut -f1)  $NAIP_CACHE"

# 2. Stage inputs where Docker can read them --------------------------------
echo "==> Staging inputs into $WORK"
mkdir -p "$WORK"
cp "$NAIP_CACHE" "$WORK/naip.tif"
cp "$SCRIPT_DIR/classify_landcover.py" "$WORK/classify_landcover.py"
cp "$SCRIPT_DIR/smooth_landcover.py" "$WORK/smooth_landcover.py"

# clip source: just the park-boundary polygon (publish.geojson also carries
# trail lines, which would corrupt an -clipsrc union)
node -e '
const d = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
const b = d.features.filter(f => f.properties && f.properties.layer === "park_boundaries");
if (!b.length) { console.error("no park_boundaries feature in publish.geojson"); process.exit(1); }
require("fs").writeFileSync(process.argv[2],
  JSON.stringify({type: "FeatureCollection", features: b}));
' "$BOUNDARY" "$WORK/boundary.geojson"

# 3. Classify -> polygonize -> simplify -> smooth -> clip -------------------
echo "==> Classifying and vectorizing"
docker run --rm -v "$WORK:/data" "$GDAL_IMG" sh -c "
set -e

# pixel classification -> single-band 5-class coverage raster
python3 /data/classify_landcover.py /data/naip.tif /data/class.tif /data/preview.png

# polygonize connected class regions (class 0 = nodata is skipped)
rm -f /data/class.gpkg
gdal_polygonize.py /data/class.tif -b 1 -f GPKG /data/class.gpkg lc DN

# light vertex simplify (1.5 m, ~2.5 px) + keep every land-cover class
# (DN > 0; only nodata is dropped); stays in EPSG:26916 so the simplify
# tolerance is metric
rm -f /data/class_simpl.gpkg
ogr2ogr -f GPKG -simplify 1.5 -where \"DN > 0\" \
  /data/class_simpl.gpkg /data/class.gpkg lc

# reproject to WGS84 for the smoothing pass
rm -f /data/class_simpl.geojson
ogr2ogr -f GeoJSON -t_srs EPSG:4326 \
  /data/class_simpl.geojson /data/class_simpl.gpkg

# Chaikin smooth + rename DN -> class
python3 /data/smooth_landcover.py /data/class_simpl.geojson /data/class_smooth.geojson

# repair any self-intersections Chaikin can pinch into thin polygons, so the
# boundary clip's GEOS overlay gets only valid input
rm -f /data/class_valid.geojson
ogr2ogr -f GeoJSON -makevalid -nlt PROMOTE_TO_MULTI \
  /data/class_valid.geojson /data/class_smooth.geojson

# clip to the AOP boundary (hole at the Ellis cemetery is respected)
rm -f /data/aop_landcover.geojson
ogr2ogr -f GeoJSON -clipsrc /data/boundary.geojson \
  -lco COORDINATE_PRECISION=6 \
  /data/aop_landcover.geojson /data/class_valid.geojson
"

# 4. Copy outputs back into the repo ----------------------------------------
echo "==> Writing outputs"
cp "$WORK/aop_landcover.geojson" "$OUT_GEOJSON"
cp "$WORK/class.tif" "$LC_CACHE/class.tif"
cp "$WORK/preview.png" "$LC_CACHE/preview.png"

FEATURES="$(node -e 'const d=JSON.parse(require("fs").readFileSync(process.argv[1],"utf8"));const c={};for(const f of d.features){const k=f.properties.class;c[k]=(c[k]||0)+1;}console.log(d.features.length+" features "+JSON.stringify(c))' "$OUT_GEOJSON")"
echo "==> Done"
echo "    GeoJSON : $OUT_GEOJSON ($(du -h "$OUT_GEOJSON" | cut -f1), $FEATURES)"
echo "    Class raster + preview (gitignored cache): $LC_CACHE"
