#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MVP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SQL_FILE="$SCRIPT_DIR/import_aop_parcel_boundary.sql"

PARCEL_SERVICE_URL="https://services.arcgis.com/rD2ylXRs80UroD90/arcgis/rest/services/TN_County_Parcel_Map/FeatureServer/35"
OFFICIAL_AOP_URL="https://adventureoffroadpark.com/"
QUERY_WHERE="Assessment_Data_58_ADDRESS = 'ELLIS COVE RD 1040' OR Assessment_Data_58_ID = '093 030.01'"
EXPECTED_PARCEL_IDS='["093 030.01","110 008.00"]'
OUT_FIELDS="OBJECTID,Parcels_GISLINK,Parcels_CALC_ACRE,Assessment_Data_58_PARCELID,Assessment_Data_58_ADDRESS,Assessment_Data_58_CLASS,Assessment_Data_58_DEEDAC,Assessment_Data_58_OWNER,Assessment_Data_58_OWNER2,Assessment_Data_58_LANDUSE,Assessment_Data_58_ID,GlobalID"

if [ ! -f "$SQL_FILE" ]; then
  echo "Import SQL not found: $SQL_FILE"
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required"
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required"
  exit 1
fi

TMP_GEOJSON="$(mktemp)"
trap 'rm -f "$TMP_GEOJSON"' EXIT

echo "Fetching AOP parcel candidates from Tennessee Comptroller Marion_Parcels layer"

curl -sS --get "$PARCEL_SERVICE_URL/query" \
  --data-urlencode "f=geojson" \
  --data-urlencode "where=$QUERY_WHERE" \
  --data-urlencode "outFields=$OUT_FIELDS" \
  --data-urlencode "outSR=4326" \
  > "$TMP_GEOJSON"

FEATURE_COUNT="$(jq '.features | length' "$TMP_GEOJSON")"
MISSING_IDS="$(
  jq -r --argjson expected "$EXPECTED_PARCEL_IDS" '
    [ $expected[] as $id
      | select([.features[].properties.Assessment_Data_58_ID] | index($id) | not)
      | $id
    ] | join(", ")
  ' "$TMP_GEOJSON"
)"

if [ "$FEATURE_COUNT" != "2" ]; then
  echo "Expected exactly 2 parcel features for: $QUERY_WHERE"
  echo "Got: $FEATURE_COUNT"
  jq '{error, features: (.features | length)}' "$TMP_GEOJSON"
  exit 1
fi

if [ -n "$MISSING_IDS" ]; then
  echo "Missing expected parcel id(s): $MISSING_IDS"
  jq -r '.features[].properties.Assessment_Data_58_ID' "$TMP_GEOJSON"
  exit 1
fi

PARCEL_FEATURES="$(jq -c '.features' "$TMP_GEOJSON")"

echo "Fetched parcels:"
jq -r '.features[]
  | "  - \(.properties.Assessment_Data_58_ID) / \(.properties.Assessment_Data_58_PARCELID): \(.properties.Parcels_CALC_ACRE) calculated acres, \(.properties.Assessment_Data_58_DEEDAC) deed acres, \(.properties.Assessment_Data_58_ADDRESS)"' "$TMP_GEOJSON"

cd "$MVP_DIR"

docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map \
  -v parcel_features="$PARCEL_FEATURES" \
  -v parcel_service_url="$PARCEL_SERVICE_URL" \
  -v official_aop_url="$OFFICIAL_AOP_URL" \
  -v query_where="$QUERY_WHERE" \
  < "$SQL_FILE"
