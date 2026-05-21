#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_FILE="$REPO_DIR/website/data/aop_roads.geojson"

SERVICE_URL="https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer"

# 9-patch acquisition envelope (WGS84 west,south,east,north)
BBOX_W="-85.782935283"
BBOX_S="35.067164188"
BBOX_E="-85.717154097"
BBOX_N="35.117928496"

OUT_FIELDS="name,mtfcc_code,tnmfrc,interstate,us_route,state_route,county_route"

# layer_id|road_class
LAYERS=(
  "29|controlled_access"
  "30|secondary"
  "31|local_connecting"
  "32|local"
  "33|ramp"
)

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 1
fi

TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_OUT"' EXIT

echo '{"type":"FeatureCollection","features":[' > "$TMP_OUT"

FIRST=1
TOTAL=0
for entry in "${LAYERS[@]}"; do
  LAYER_ID="${entry%%|*}"
  ROAD_CLASS="${entry##*|}"
  echo "Fetching USGS Transportation layer $LAYER_ID ($ROAD_CLASS)"

  RESP="$(
    curl -sS --get "$SERVICE_URL/$LAYER_ID/query" \
      --data-urlencode "geometry=$BBOX_W,$BBOX_S,$BBOX_E,$BBOX_N" \
      --data-urlencode "geometryType=esriGeometryEnvelope" \
      --data-urlencode "inSR=4326" \
      --data-urlencode "outSR=4326" \
      --data-urlencode "spatialRel=esriSpatialRelIntersects" \
      --data-urlencode "outFields=$OUT_FIELDS" \
      --data-urlencode "returnGeometry=true" \
      --data-urlencode "resultRecordCount=2000" \
      --data-urlencode "f=geojson"
  )"

  COUNT="$(echo "$RESP" | jq '.features | length')"
  if [ "$COUNT" = "null" ] || [ -z "$COUNT" ]; then
    echo "  no features returned (layer $LAYER_ID)" >&2
    continue
  fi
  echo "  $COUNT features"
  TOTAL=$((TOTAL + COUNT))

  if [ "$COUNT" -gt 0 ]; then
    FEATS="$(
      echo "$RESP" | jq -c --arg road_class "$ROAD_CLASS" --arg layer_id "$LAYER_ID" '
        .features[] | .properties.road_class = $road_class | .properties.usgs_layer_id = $layer_id
      '
    )"
    while IFS= read -r feat; do
      if [ "$FIRST" -eq 1 ]; then
        FIRST=0
      else
        printf ',\n' >> "$TMP_OUT"
      fi
      printf '%s' "$feat" >> "$TMP_OUT"
    done <<< "$FEATS"
  fi
done

printf '\n]}\n' >> "$TMP_OUT"

# Validate the assembled GeoJSON before replacing the live file
if ! jq -e '.features | length' "$TMP_OUT" >/dev/null; then
  echo "Assembled GeoJSON is invalid; refusing to write $OUT_FILE" >&2
  cat "$TMP_OUT" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT_FILE")"
mv "$TMP_OUT" "$OUT_FILE"
trap - EXIT

echo "Wrote $TOTAL road features to $OUT_FILE"
echo "Source: $SERVICE_URL (USGS National Map Transportation)"
