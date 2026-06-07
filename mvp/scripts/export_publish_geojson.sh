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
      FROM publish.features WHERE layer = 'poi'
    ) t
  ) foo
) TO STDOUT;
EOF
)

# Reference layers (going gold, slice 2+) bake to their OWN served file -- NOT
# publish.geojson -- because they carry non-'publish' permission (buildings are
# FEMA reference / private presence; the publish gate correctly excludes them).
# Each is `{type, features (properties = attrs verbatim), _meta}` -- the canonical
# served shape (rebake_canonical.py:240-254), with _meta carried forward from the
# live file. The bake is the sole writer the viewer reads. ST_AsGeoJSON at 9
# decimals (~0.1 mm) -- the source's 13 decimals are spurious FEMA precision.
# Card: brain/tasks/06_going_gold/gold_migration.md (slice 2).
#   layer-in-core | served file (relative to website/data)
REFERENCE_LAYERS="buildings|aop_buildings.geojson cemeteries|aop_cemeteries.geojson visitor|aop_visitor_context_callouts.geojson trails|aop_trail_network.geojson"

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

# --- Reference / map-source layers (own served file, no publish gate) ---------
for pair in $REFERENCE_LAYERS; do
  layer="${pair%%|*}"
  fname="${pair##*|}"
  out="$ROOT_DIR/website/data/$fname"
  feat_tmp="$(mktemp "${out}.feats.XXXXXX")"
  # Plain SELECT with -At (NOT `COPY ... TO STDOUT`): COPY's TEXT format escapes
  # backslashes, so a JSON string's `\n` (a newline inside an attr like a callout
  # `label`) becomes a literal `\\n` and the newline is corrupted. -At prints the
  # json value raw, preserving the escape. (The publish.geojson COPY above has the
  # same latent risk if a published feature ever carries a newline -- none does today.)
  layer_sql="SELECT coalesce(json_agg(json_build_object(
      'type', 'Feature',
      'geometry', ST_AsGeoJSON(geom, 9)::json,
      'properties', attrs
    )), '[]'::json)
    FROM core.features
    WHERE layer = '$layer' AND archived_at IS NULL;"
  echo "Exporting core.features layer '$layer' -> $out"
  docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map -At -c "$layer_sql" > "$feat_tmp"
  # Wrap as {type, features, _meta} minified; carry _meta forward from the live
  # file (rebake_canonical.py pattern) so the editor still badges the layer.
  FEATS="$feat_tmp" OUT="$out" python3 - <<'PY'
import json, os
feats = json.load(open(os.environ["FEATS"]))
out_path = os.environ["OUT"]
doc = {"type": "FeatureCollection", "features": feats}
try:
    with open(out_path) as fh:
        meta = json.load(fh).get("_meta")
    if isinstance(meta, dict):
        doc["_meta"] = meta
except (FileNotFoundError, ValueError):
    pass
tmp = out_path + ".tmp"
with open(tmp, "w") as fh:
    json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
os.replace(tmp, out_path)
os.chmod(out_path, 0o644)
print(f"  wrote {len(feats)} features to {out_path}")
PY
  rm -f "$feat_tmp"
done

echo "Reference-layer export complete."
