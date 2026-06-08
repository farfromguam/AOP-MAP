#!/usr/bin/env bash
# Import a GPX field track into the AOP MAP database.
#
# Lands raw XML in raw.gpx_captures and parses segments into core.features
# (layer='field_tracks', status=candidate, publish_status=hold). Adds a source
# row and feature_sources links. See brain/northstar/source_register.md and
# validation_loop.md for the data-zone policy.
#
# Usage: ./import_gpx_track.sh /path/to/file.gpx
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MVP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SQL_FILE="$SCRIPT_DIR/import_gpx_track.sql"
PARSER="$SCRIPT_DIR/parse_gpx.py"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/file.gpx"
  exit 2
fi

GPX_FILE="$1"

if [ ! -f "$GPX_FILE" ]; then
  echo "GPX file not found: $GPX_FILE"
  exit 1
fi

if [ ! -f "$SQL_FILE" ]; then
  echo "Import SQL not found: $SQL_FILE"
  exit 1
fi

if [ ! -f "$PARSER" ]; then
  echo "GPX parser not found: $PARSER"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required"
  exit 1
fi

FILE_NAME="$(basename "$GPX_FILE")"

echo "Parsing $GPX_FILE"
PAYLOAD="$(python3 "$PARSER" "$GPX_FILE")"

SEG_COUNT="$(python3 -c 'import json,sys; print(len(json.loads(sys.stdin.read())["segments"]))' <<<"$PAYLOAD")"
PT_COUNT="$(python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["total_point_count"])' <<<"$PAYLOAD")"
echo "Parsed $SEG_COUNT segment(s), $PT_COUNT point(s)"

cd "$MVP_DIR"

docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map \
  -v gpx_payload="$PAYLOAD" \
  -v file_name="$FILE_NAME" \
  < "$SQL_FILE"
