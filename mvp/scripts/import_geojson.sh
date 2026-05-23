#!/usr/bin/env bash
# Generic GeoJSON -> PostGIS importer (ogr2ogr wrapper, GDAL required).
#
# This is the ad-hoc ingest path for one-off GeoJSON files that do not yet
# have a dedicated importer. Properties in the source file get mapped to
# matching columns in the target table; unmapped properties are dropped.
# Source provenance is NOT set automatically -- see the hint after import.
#
# Usage:
#   ./import_geojson.sh /path/to/file.geojson schema.table
#
# Example (drop a generic point/line/polygon dataset into the observations
# bucket where it can be reviewed before promotion):
#   ./import_geojson.sh ../../website/data/aop_buildings.geojson core.observations
#
# Unlike the schema-specific importers (import_aop_parcel_boundary,
# import_gpx_track, import_fema_buildings, import_marion_cemeteries), this
# script does not write a `source_register.sources` row or a
# `feature_sources` link. Run it for prototyping; promote to a dedicated
# importer before the data is treated as truth.

set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 /path/to/file.geojson schema.table" >&2
  exit 2
fi

if ! command -v ogr2ogr >/dev/null 2>&1; then
  echo "ogr2ogr (GDAL) is required but not found on PATH." >&2
  echo "Install GDAL or use one of the dedicated importers in this folder." >&2
  exit 1
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
  echo "GeoJSON file not found: $GEOJSON_FILE" >&2
  exit 1
fi

echo "Importing $GEOJSON_FILE -> $TARGET_TABLE"

# Import with ogr2ogr. -append maps to an existing table; remove if you want
# ogr2ogr to create one from scratch.
ogr2ogr -f "PostgreSQL" \
  "$PG_CONN" \
  "$GEOJSON_FILE" \
  -nln "$TARGET_TABLE" \
  -append \
  -nlt PROMOTE_TO_MULTI \
  -lco GEOMETRY_NAME=geom \
  -t_srs "EPSG:4326"

echo "Import finished."
echo
echo "Provenance is not set. To link these rows to a source, run:"
echo "  INSERT INTO source_register.sources (name, source_type, ...) ... RETURNING id;"
echo "  UPDATE $TARGET_TABLE SET source_id = <id> WHERE source_id IS NULL;"
