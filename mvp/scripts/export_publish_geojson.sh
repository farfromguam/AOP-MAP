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
      -- All published map layers now live in the ONE converged core.features /
      -- publish.features gate -- the 2026-06-07 table cleanup folded the per-layer
      -- core.* tables (trail_centerlines, park_boundaries, trailheads, hazards,
      -- poi) into it. Domain columns read from attrs; kind/description come straight
      -- from core.features (poi carries them, the geo layers leave them NULL --
      -- the same property shape the per-view UNION emitted). `description` was
      -- renamed from `blurb` 2026-06-08 (07_tables/description_blurb_convergence.md).
      SELECT id, name,
             attrs->>'difficulty'  AS difficulty,
             attrs->>'hazard_type' AS hazard_type,
             attrs->>'severity'    AS severity,
             kind, description, status, confidence, permission, layer, geom
      FROM publish.features
      WHERE layer IN ('trail_centerlines','park_boundaries','trailheads','hazards','poi')
      ORDER BY CASE layer
                 WHEN 'trail_centerlines' THEN 1 WHEN 'park_boundaries' THEN 2
                 WHEN 'trailheads' THEN 3 WHEN 'hazards' THEN 4 WHEN 'poi' THEN 5
               END, id
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

# --- Event schedule (going gold, sprint 07 slice 1) ---------------------------
# The WHEN. A NEW emit arm in this one-writer bake (NOT a REFERENCE_LAYERS entry --
# the schedule is a {schema,event,locations{},sessions[]} document, not a GeoJSON
# FeatureCollection). sessions[] come from core.events; locations{} from
# core.features rows that carry attrs.event_location (the 6 'event' anchors + the
# annotated #pavilion POI), with coordinates resolved from each row's geom. Same
# served filename the viewer reads (main.js:8181) -> no main.js change, no shell
# bump. Card: brain/tasks/07_tables/tables_model.md (slice 1).
#
# OWED (flagged, not slice 1): the umbrella event/schema/status/updated_at wrapper
# is bake-config below, not yet a DB row -- it gets a core home when event CRUD
# lands (deferred V2). Until then it is the singular event's document metadata.
SCHED_OUT="$ROOT_DIR/website/data/aop_event_schedule.json"
EVENT_META=$(cat <<'EOF'
{
  "schema": "aop-event-schedule-v1",
  "updated_at": "2026-05-27",
  "status": "proposed",
  "event": {
    "id": "rock_warblers_trail_blazing_invitational_2026",
    "label": "Rock Warblers Trail Blazing Invitational",
    "date_range_label": "Friday, June 19, 2026",
    "end_date_label": "Sunday, June 21, 2026",
    "source_context": "brain/handoff/event_schedule_context_20260522.json",
    "source_summary": "Sister-event schedule vocabulary reviewed from Pro-Line By The Fire, RECON G6 / RG6, and AxialFest references.",
    "caveat": "Proposed planning context only; confirm final schedule, locations, staffing, facilities, and AOP permission before publishing as official."
  }
}
EOF
)
sched_sql="SELECT json_build_object(
  'locations', (
    SELECT coalesce(json_object_agg(
      attrs->'event_location'->>'tag',
      jsonb_strip_nulls(jsonb_build_object(
        'label',       attrs->'event_location'->>'label',
        'map_label',   attrs->'event_location'->>'map_label',
        'role',        attrs->'event_location'->>'role',
        'coordinates', ST_AsGeoJSON(geom, 9)::json->'coordinates',
        'source',      attrs->'event_location'->>'source',
        'confidence',  attrs->'event_location'->>'confidence',
        'caveat',      attrs->'event_location'->>'caveat'
      ))), '{}'::json)
    FROM core.features
    WHERE attrs ? 'event_location' AND archived_at IS NULL
  ),
  'sessions', (
    SELECT coalesce(json_agg(s ORDER BY so), '[]'::json) FROM (
      SELECT e.sort_order AS so, jsonb_strip_nulls(
        jsonb_build_object(
          'id', e.source_key, 'sort_order', e.sort_order, 'date_label', e.date_label,
          'start_local', e.start_local, 'time_label', e.time_label, 'title', e.title,
          'location_tag', e.place_key, 'status', e.status, 'inspired_by', e.attrs->'inspired_by'
        ) || CASE WHEN e.attrs ? 'route_tags'
                  THEN jsonb_build_object('route_tags', e.attrs->'route_tags')
                  ELSE '{}'::jsonb END
        -- The reusable WHAT, resolved (not copied) from core.activities. A
        -- not-yet-defined activity_key still carries its key (a.* NULL, stripped);
        -- a session with NULL activity_key gets no 'activity' field. Never dropped.
        || CASE WHEN e.activity_key IS NOT NULL THEN jsonb_build_object('activity',
                  jsonb_strip_nulls(jsonb_build_object(
                    'key', e.activity_key, 'name', a.name, 'kind', a.kind,
                    'description', a.description, 'attrs', a.attrs)))
                ELSE '{}'::jsonb END
      ) AS s
      FROM core.events e
      LEFT JOIN core.activities a ON a.activity_key = e.activity_key AND a.archived_at IS NULL
      WHERE e.archived_at IS NULL
    ) q
  )
);"
sched_tmp="$(mktemp "${SCHED_OUT}.body.XXXXXX")"
echo "Exporting core.events + event-place locations -> $SCHED_OUT"
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map -At -c "$sched_sql" > "$sched_tmp"
META="$EVENT_META" BODY="$sched_tmp" OUT="$SCHED_OUT" python3 - <<'PY'
import json, os
doc = json.loads(os.environ["META"])              # {schema, updated_at, status, event}
body = json.load(open(os.environ["BODY"]))         # {locations, sessions}
doc["locations"] = body["locations"]
doc["sessions"] = body["sessions"]
out_path = os.environ["OUT"]
tmp = out_path + ".tmp"
with open(tmp, "w") as fh:
    json.dump(doc, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
os.replace(tmp, out_path)
os.chmod(out_path, 0o644)
print(f"  wrote {len(body['sessions'])} sessions + {len(body['locations'])} locations to {out_path}")
PY
rm -f "$sched_tmp"

echo "Event-schedule export complete."
