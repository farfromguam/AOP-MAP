#!/usr/bin/env bash
set -euo pipefail

# Export the publish views from the MVP PostGIS database to the website viewer file.
# Run from the repository root or anywhere; the script resolves paths relative to itself.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
MVP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_FILE="$ROOT_DIR/website/data/publish.geojson"

# Construct SQL that produces a valid GeoJSON FeatureCollection.
SQL=$(cat <<'EOF'
COPY (
  SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', coalesce(json_agg(feature), '[]'::json)
  )
  FROM (
    SELECT json_build_object(
      'type', 'Feature',
      'geometry', ST_AsGeoJSON(geom)::json,
      'properties', to_jsonb(t) - 'geom'
    ) AS feature
    FROM (
      SELECT id, name, difficulty, NULL::text AS hazard_type, NULL::text AS severity, NULL::text AS kind, NULL::text AS blurb, status, confidence, permission, 'trail_centerlines' AS layer, geom
      FROM publish.trail_centerlines
      UNION ALL
      SELECT id, name, NULL::text AS difficulty, NULL::text AS hazard_type, NULL::text AS severity, NULL::text AS kind, NULL::text AS blurb, status, confidence, permission, 'park_boundaries' AS layer, geom
      FROM publish.park_boundaries
      UNION ALL
      SELECT id, name, NULL::text AS difficulty, NULL::text AS hazard_type, NULL::text AS severity, NULL::text AS kind, NULL::text AS blurb, status, confidence, permission, 'trailheads' AS layer, geom
      FROM publish.trailheads
      UNION ALL
      SELECT id, NULL::text AS name, NULL::text AS difficulty, hazard_type, severity, NULL::text AS kind, NULL::text AS blurb, status, confidence, permission, 'hazards' AS layer, geom
      FROM publish.hazards
      UNION ALL
      SELECT id, name, NULL::text AS difficulty, NULL::text AS hazard_type, NULL::text AS severity, kind, blurb, status, confidence, permission, 'poi' AS layer, geom
      FROM publish.pois
    ) t
  ) foo
) TO STDOUT;
EOF
)

mkdir -p "$(dirname "$OUTPUT_FILE")"
OUTPUT_TMP="$(mktemp "${OUTPUT_FILE}.tmp.XXXXXX")"
trap 'rm -f "$OUTPUT_TMP"' EXIT

echo "Exporting publish views to $OUTPUT_FILE"

# Same docker compose connection style as the import scripts.
cd "$MVP_DIR"
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map -At -c "$SQL" > "$OUTPUT_TMP"
mv "$OUTPUT_TMP" "$OUTPUT_FILE"
chmod 644 "$OUTPUT_FILE"
trap - EXIT

echo "Export complete: $OUTPUT_FILE"
