#!/usr/bin/env bash
# Simple scaffold to import a GeoJSON file into PostGIS using ogr2ogr (GDAL).
# Usage: ./import_geojson.sh /path/to/file.geojson schema.table
# Example: ./import_geojson.sh ../website/data/publish.geojson publish.publish_features

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 /path/to/file.geojson schema.table"
  exit 2
fi

GEOJSON_FILE="$1"
TARGET_TABLE="$2"

PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-55432}"
PGUSER="${PGUSER:-aop}"
PGDATABASE="${PGDATABASE:-aop_map}"
PGPASSWORD="${PGPASSWORD:-aop}"

PG_CONN="PG:host=$PGHOST port=$PGPORT user=$PGUSER dbname=$PGDATABASE password=$PGPASSWORD"

if [ ! -f "$GEOJSON_FILE" ]; then
  echo "GeoJSON file not found: $GEOJSON_FILE"
  exit 1
fi

echo "Importing $GEOJSON_FILE -> $TARGET_TABLE on $PG_CONN"

# Import with ogr2ogr. This will create the table if missing; use -append to add.
ogr2ogr -f "PostgreSQL" \
  "$PG_CONN" \
  "$GEOJSON_FILE" \
  -nln "$TARGET_TABLE" \
  -append \
  -nlt PROMOTE_TO_MULTI \
  -lco GEOMETRY_NAME=geom \
  -t_srs "EPSG:4326"

echo "Import finished."
