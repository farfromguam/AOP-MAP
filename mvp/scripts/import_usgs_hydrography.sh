#!/usr/bin/env bash
set -euo pipefail

# Pull USGS National Hydrography Dataset (NHD) water features for the AOP
# 9-patch and write them to website/data/aop_water.geojson.
#
# Mirrors import_usgs_roads.sh: query a USGS National Map MapServer over the
# 9-patch envelope, tag each feature with a class, atomic-write the GeoJSON.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
OUT_FILE="$REPO_DIR/website/data/aop_water.geojson"

SERVICE_URL="https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer"

# 9-patch acquisition envelope (WGS84 west,south,east,north)
BBOX_W="-85.782935283"
BBOX_S="35.067164188"
BBOX_E="-85.717154097"
BBOX_N="35.117928496"

# layer_id|water_kind|layer_name
# Large-scale (high-resolution) NHD layers — the right resolution for a park AOI.
LAYERS=(
  "6|flowline|Flowline - Large Scale"
  "9|water_area|Area - Large Scale"
  "12|waterbody|Waterbody - Large Scale"
  "0|point|Point"
)

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 1
fi

# Normalize NHD field-case differences and classify each feature.
# NHD ftype is the feature type; fcode refines it (e.g. perennial vs intermittent).
ENRICH='
.features
| map(
    (.properties | with_entries(.key |= ascii_downcase)) as $p
    | (($p.ftype // 0) | tonumber) as $ftype
    | (($p.fcode // 0) | tonumber) as $fcode
    | (
        if $water_kind == "flowline" then
          (if $ftype == 460 then
             (if $fcode == 46003 then "stream_intermittent"
              elif $fcode == 46007 then "stream_ephemeral"
              else "stream" end)
           elif $ftype == 558 then "artificial_path"
           elif $ftype == 336 then "canal_ditch"
           elif $ftype == 334 then "connector"
           elif $ftype == 428 then "pipeline"
           else "flowline_other" end)
        elif $water_kind == "water_area" then
          (if $ftype == 460 then "stream_river_area"
           elif $ftype == 484 then "wash"
           else "water_area_other" end)
        elif $water_kind == "waterbody" then
          (if $ftype == 390 then "lake_pond"
           elif $ftype == 436 then "reservoir"
           elif $ftype == 466 then "swamp_marsh"
           elif $ftype == 361 then "playa"
           else "waterbody_other" end)
        else
          (if $ftype == 458 then "spring"
           elif $ftype == 450 then "gage"
           elif $ftype == 343 then "dam_weir"
           elif $ftype == 431 then "rapids"
           else "water_point" end)
        end
      ) as $class
    | .properties = {
        name: ($p.gnis_name // null),
        gnis_id: ($p.gnis_id // null),
        fcode: $fcode,
        ftype: $ftype,
        water_kind: $water_kind,
        water_class: $class,
        lengthkm: $p.lengthkm,
        areasqkm: $p.areasqkm,
        elevation: $p.elevation,
        permanent_identifier: $p.permanent_identifier,
        nhd_layer_id: ($layer_id | tonumber),
        nhd_layer_name: $layer_name
      }
  )
'

TMP_FEATS="$(mktemp)"
TMP_OUT="$(mktemp)"
trap 'rm -f "$TMP_FEATS" "$TMP_OUT"' EXIT

TOTAL=0
for entry in "${LAYERS[@]}"; do
  IFS='|' read -r LAYER_ID WATER_KIND LAYER_NAME <<< "$entry"
  echo "Fetching NHD layer $LAYER_ID ($WATER_KIND)"

  RESP="$(
    curl -sS --get "$SERVICE_URL/$LAYER_ID/query" \
      --data-urlencode "geometry=$BBOX_W,$BBOX_S,$BBOX_E,$BBOX_N" \
      --data-urlencode "geometryType=esriGeometryEnvelope" \
      --data-urlencode "inSR=4326" \
      --data-urlencode "outSR=4326" \
      --data-urlencode "spatialRel=esriSpatialRelIntersects" \
      --data-urlencode "where=1=1" \
      --data-urlencode "outFields=*" \
      --data-urlencode "returnGeometry=true" \
      --data-urlencode "resultRecordCount=2000" \
      --data-urlencode "f=geojson"
  )"

  COUNT="$(echo "$RESP" | jq '.features | length' 2>/dev/null || echo "null")"
  if [ "$COUNT" = "null" ] || [ -z "$COUNT" ]; then
    echo "  no features returned (layer $LAYER_ID)" >&2
    continue
  fi
  echo "  $COUNT features"
  TOTAL=$((TOTAL + COUNT))

  if [ "$COUNT" -gt 0 ]; then
    echo "$RESP" | jq -c \
      --arg water_kind "$WATER_KIND" \
      --arg layer_id "$LAYER_ID" \
      --arg layer_name "$LAYER_NAME" \
      "$ENRICH | .[]" >> "$TMP_FEATS"
  fi
done

# Assemble one FeatureCollection from the per-layer feature lines.
jq -s '{type: "FeatureCollection", features: .}' "$TMP_FEATS" > "$TMP_OUT"

# Validate before replacing the live file.
if ! jq -e '.features | length' "$TMP_OUT" >/dev/null; then
  echo "Assembled GeoJSON is invalid; refusing to write $OUT_FILE" >&2
  cat "$TMP_OUT" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT_FILE")"
mv "$TMP_OUT" "$OUT_FILE"
chmod 644 "$OUT_FILE"
trap 'rm -f "$TMP_FEATS"' EXIT

echo "Wrote $TOTAL water features to $OUT_FILE"
echo "  by class:"
jq -r '.features | group_by(.properties.water_class)[]
  | "    \(length)\t\(.[0].properties.water_class)"' "$OUT_FILE"
echo "Source: $SERVICE_URL (USGS National Hydrography Dataset)"
