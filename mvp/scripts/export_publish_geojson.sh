#!/usr/bin/env bash
set -euo pipefail

# Export the publish views from the MVP PostGIS database to the website viewer file.
# Run from the repository root or anywhere; the script resolves paths relative to itself.
#
# --check : NON-WRITING pure-function proof (Approach C, gold slice 6). Bakes every
#   served file to a side path, byte-compares it to the live served file, and writes
#   NOTHING. Exit 0 + "NO REVERT" iff every file is byte-identical (the bake is a pure
#   function of the DB + this script, so a re-run can't silently revert gold state);
#   exit 1 + a diff list if any file would change. Run it AFTER an adopt to prove the
#   served tree is the bake's fixed point.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
MVP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_FILE="$ROOT_DIR/website/data/publish.geojson"

# --check mode: every write goes to "<file>.check" and is diffed, never to the file.
CHECK=0
for arg in "$@"; do [ "$arg" = "--check" ] && CHECK=1; done
CHECK_FILES=()   # collected "<served>|<check>" pairs to diff at the end

# === THE ONE SHARED BAKE HELPER (Approach C, gold slice 6, 2026-06-10) ========
# Both arms of this bake -- the publish arm and the reference arm -- build a
# feature's `properties` the SAME way: the CMFS SPINE comes from core.features
# COLUMNS (the one home, C6), and domain/render extras come from attrs.
#
#   properties = {spine: columns} (+) {provenance with no column: attrs}
#                (+) {curated attrs extras}
#
# `SPINE_COLS` is the SINGLE source of truth for which CMFS fields live in
# columns: name/description/kind + the Tier-2 provenance confidence/permission/
# status. (`id` is the per-arm business key -- source_key for publish, attrs.id
# for reference -- handled per arm; `source`/`last_checked` have NO column and
# stay in attrs, see brain/output/approachC_field_inventory_20260610.md.)
#
# It is rendered two ways from that one list:
#   SPINE_JSONB  -> a jsonb_strip_nulls(jsonb_build_object(...)) the REFERENCE arm
#                   overlays on attrs (attrs || SPINE_JSONB) so the column wins for
#                   the spine while every attrs extra is preserved verbatim.
#   SPINE_SELECT -> the bare column list the PUBLISH arm projects (it already reads
#                   the spine from columns; this just names the shared set).
# Keeping ONE list means the publish and reference arms can never drift on which
# fields are spine-from-columns.
SPINE_COLS="name description kind confidence permission status"
SPINE_JSONB="jsonb_strip_nulls(jsonb_build_object($(
  first=1
  for c in $SPINE_COLS; do
    if [ $first -eq 1 ]; then first=0; else printf ", "; fi
    printf "'%s', %s" "$c" "$c"
  done
)))"

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
      --
      -- F4 (gold slice 6, 2026-06-09): the served `id` is the STABLE business key
      -- (`source_key`, the existing UNIQUE crosswalk identity), NOT the volatile
      -- serial PK -- a fresh-volume rebuild renumbers the PK but never the
      -- source_key, so the editor's per-feature match key (served id ==
      -- panel `<source>:<id>` -> DB upsert `ON CONFLICT (source_key)`) stays
      -- deterministic (audit `published-id-is-volatile-serial` /
      -- `publish-geojson-stale-not-reproducible`). We read core.features with the
      -- publish view's EXACT gate inline (so we can project source_key, which the
      -- fixed-column publish.features view does not expose) -- the GATE is
      -- unchanged, NOT weakened: same permission/publish_status/archived_at filter.
      -- Approach C (2026-06-10): the spine projected here -- name, kind,
      -- description, status, confidence, permission -- is the SAME spine-from-
      -- COLUMNS set the reference arm overlays via SPINE_COLS/SPINE_JSONB (the one
      -- shared bake-helper rule: spine from columns, domain extras from attrs).
      -- The publish arm reads it as an explicit projection (id=source_key business
      -- key + the publish-only domain facets difficulty/hazard_type/severity), the
      -- reference arm as an attrs overlay; both name the same columns as the home.
      SELECT source_key AS id, name,
             attrs->>'difficulty'  AS difficulty,
             attrs->>'hazard_type' AS hazard_type,
             attrs->>'severity'    AS severity,
             kind, description, status, confidence, permission, layer, geom
      FROM core.features
      WHERE permission = 'publish'
        AND publish_status = 'publish'
        AND archived_at IS NULL
        AND layer IN ('trail_centerlines','park_boundaries','trailheads','hazards','poi')
      ORDER BY CASE layer
                 WHEN 'trail_centerlines' THEN 1 WHEN 'park_boundaries' THEN 2
                 WHEN 'trailheads' THEN 3 WHEN 'hazards' THEN 4 WHEN 'poi' THEN 5
               END, source_key
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
# Wrap as {type, features, <top-level keys>} minified. The top-level keys (the
# publish layers' maturity badge / group label the editor reads from `_meta`, plus
# any owner-authored collection provenance) now come from the STORE OF RECORD --
# website/data/_schema.json (regen_meta.served_top_meta) -- NOT carried forward from
# the prior served file. _schema.json is COMMITTED, so a FRESH VOLUME (no prior
# served file) still reproduces `_meta` exactly: closes
# `reference-bake-no-meta-on-fresh-volume` (gold slice 6, 2026-06-10). When the
# store has nothing for the file yet (a fresh checkout before regen_meta.py
# --capture), the bake falls back to carrying the live file forward so it never
# emits a meta-less file; --capture then promotes it to the store.
# Per-feature `maturity` (the editor Tier chip's store of record): each published
# feature is stamped with the file's layer maturity from the store
# (`maturity-tier-derived-from-panel-tree-position`); panel.js reads
# props.maturity first, the node literal as a default.
# Python re-serialization (separators=(",", ":")) keeps the served bytes a
# deterministic pure function of the DB rows + this script + the schema store.
PUB_WRITE="$OUTPUT_FILE"; [ "$CHECK" -eq 1 ] && PUB_WRITE="${OUTPUT_FILE}.check"
BODY="$OUTPUT_TMP" OUT="$OUTPUT_FILE" WRITE="$PUB_WRITE" FNAME="publish.geojson" \
  SCRIPT_DIR="$SCRIPT_DIR" python3 - <<'PY'
import json, os, sys
sys.path.insert(0, os.environ["SCRIPT_DIR"])
import regen_meta as rm
body = json.load(open(os.environ["BODY"]))            # {type, features} from the COPY
out_path = os.environ["OUT"]                          # live file (carry-forward fallback)
write_path = os.environ.get("WRITE") or out_path      # --check: write to a side path
fname = os.environ["FNAME"]
feats = body.get("features", [])
schema = rm._load_schema()
# G_C (gold slice 6, 2026-06-10) -- publish `kind` from the controlled list
# (audit `publish-kind-taxonomy-fork`). The two `poi`-layer published features
# carry a specific-class proper-noun kind (`pavilion`, `cemetery`) where the
# controlled Tier-1 `kind` is `poi`; the specific class belongs in a Tier-3
# `category` facet (mirrors the A4 `seed-poi-kind-is-propernoun-category` fix).
# C5/C6 -- MAP KNOWN, PASS UNKNOWN THROUGH: only the controlled mapping below is
# rewritten; an unmapped kind renders as-is, never thrown on, never coerced to
# blank. Only `layer='poi'` rows are touched -- a `park_boundaries` row keeps its
# domain kind (e.g. the Ellis inholding boundary stays `cemetery`). The original
# class is preserved in `category` so nothing is dropped (additive).
POI_KIND_MAP = {"pavilion": "poi", "cemetery": "poi"}
# G_C (gold slice 6, 2026-06-10) -- Ellis cemetery is ONE real-world place
# represented across files/layers (audit `ellis-cemetery-multi-id-across-files`):
# `editorPois:ellis-cemetery` (poi) + `park_boundaries:ellis-inholding` (boundary)
# in publish.geojson, and `110 008.04:parcel`/`:marker` in aop_cemeteries.geojson.
# We do NOT hard-merge (each representation paints a different layer and is needed);
# instead an ADDITIVE `same_as` facet links every representation to the canonical
# site id (the cemetery MARKER, the store-of-record row) so a surface CAN know they
# are one place. Keyed by the published source_key (the served `id`). Permissive:
# only the known Ellis publish ids are linked; nothing else is touched.
ELLIS_CANONICAL_ID = "110 008.04:marker"   # the cemetery marker's canonical id
ELLIS_PUBLISH_IDS = {"editorPois:ellis-cemetery", "park_boundaries:ellis-inholding"}
for ft in feats:
    props = ft.get("properties")
    if not isinstance(props, dict):
        continue
    if props.get("layer") == "poi":
        k = props.get("kind")
        if k in POI_KIND_MAP and POI_KIND_MAP[k] != k:
            if "category" not in props or props.get("category") in (None, ""):
                props["category"] = k          # keep the specific class as a facet
            props["kind"] = POI_KIND_MAP[k]     # controlled Tier-1 kind
    if props.get("id") in ELLIS_PUBLISH_IDS and "same_as" not in props:
        props["same_as"] = ELLIS_CANONICAL_ID  # cross-link to the canonical cemetery
# Per-feature maturity (default = the file's layer maturity from the store).
layer_mat = (schema.get("layers", {}).get(fname, {}) or {}).get("maturity")
if layer_mat:
    for ft in feats:
        props = ft.get("properties")
        if isinstance(props, dict) and "maturity" not in props:
            props["maturity"] = layer_mat
doc = {"type": "FeatureCollection", "features": feats}
top = rm.served_top_meta(fname, schema)               # store of record -> top keys
if top:
    for k, v in top.items():
        doc[k] = v
else:
    # Fresh-volume fallback: carry the live file's top keys forward (no store yet).
    try:
        with open(out_path) as fh:
            prior = json.load(fh)
        for k, v in prior.items():
            if k not in ("type", "features"):
                doc[k] = v
    except (FileNotFoundError, ValueError):
        pass
tmp = write_path + ".tmp"
with open(tmp, "w") as fh:
    json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
os.replace(tmp, write_path)
os.chmod(write_path, 0o644)
print(f"  wrote {len(doc['features'])} publish features to {write_path}")
PY
[ "$CHECK" -eq 1 ] && CHECK_FILES+=("$OUTPUT_FILE|$PUB_WRITE")
rm -f "$OUTPUT_TMP"
trap - EXIT

echo "Export complete: $OUTPUT_FILE"

# --- Reference / map-source layers (own served file, no publish gate) ---------
# Approach C (2026-06-10): the CMFS SPINE is served from COLUMNS, not attrs. Each
# feature's `properties` = `attrs || SPINE_JSONB` -- the attrs carry the curated
# render/domain extras (color, difficulty, facets, trail_number, geom_role,
# icon_size, source, last_checked, _original, ...) and the spine columns
# (name/description/kind/confidence/permission/status) are overlaid ON TOP so the
# COLUMN is the one home (C6) and an editor edit that lands in a column actually
# appears in the served file. `source`/`last_checked` have no column and ride from
# attrs unchanged. The overlay is loss-free vs the prior attrs-verbatim bake
# because the columns were reconciled to equal the attrs spine values (buildings
# name/status promoted; the rest already matched) -- see
# brain/output/approachC_field_inventory_20260610.md. This is the SAME
# spine-from-columns rule the publish arm above uses (shared SPINE_COLS list).
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
  # G_C (gold slice 6, 2026-06-10): the served `id` is now the CANONICAL business
  # key -- the `source_key` minus its `<layer>:` prefix -- so `spec.idField ==
  # panel key == DB source_key` for every layer (audit
  # `served-id-heterogeneous-no-canonical-key`). It is overlaid ON TOP of attrs
  # (after $SPINE_JSONB) so the canonical id wins over whatever `attrs.id` carried:
  #   buildings  id = build_id          (was the FEMA UUID -- now matches source_key;
  #                                       the UUID survives in attrs.uuid/attrs.id,
  #                                       additive, audit `buildings-served-id-...-pk`)
  #   cemeteries id = '<parcel_id>:<geom_role>' (UNIQUE per feature -- collapses the
  #                                       twin's non-unique shared id; the parcel and
  #                                       marker now carry DISTINCT canonical ids,
  #                                       audit `cemetery-parcel-marker-twin-...`)
  #   trails     id = 'sfwda-N'         (unchanged -- already == source_key biz key)
  #   visitor    id = '<id>'            (unchanged -- already == source_key biz key)
  # `geom_role` stays an attrs facet (it already rides in attrs verbatim). The host
  # idField for cemeteries moves to `id` (js/main.js) so the editor resolves the
  # MARKER store-of-record, not the parcel twin. ORDER BY source_key makes the bake
  # deterministic (closes the pre-existing buildings order-only --check DRIFT).
  ID_OVERLAY="jsonb_build_object('id', regexp_replace(source_key, '^' || layer || ':', ''))"
  layer_sql="SELECT coalesce(json_agg(json_build_object(
      'type', 'Feature',
      'geometry', ST_AsGeoJSON(geom, 9)::json,
      'properties', attrs || $SPINE_JSONB || $ID_OVERLAY
    ) ORDER BY source_key), '[]'::json)
    FROM core.features
    WHERE layer = '$layer' AND archived_at IS NULL;"
  echo "Exporting core.features layer '$layer' -> $out"
  docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map -At -c "$layer_sql" > "$feat_tmp"
  ref_write="$out"; [ "$CHECK" -eq 1 ] && ref_write="${out}.check"
  # Wrap as {type, features, <top-level keys>} minified. The top-level keys -- the
  # owner-authored collection provenance (_source, _derived, _generated_by,
  # _retrieved_on, _aop_9_patch_bbox, _source_item, _source_service,
  # _sources_checked, _description, the collection `name`) AND the `_meta` block
  # (the editor's maturity badge + the trail self-describing GOLD BLOCK) -- now come
  # from the STORE OF RECORD, website/data/_schema.json (regen_meta.served_top_meta),
  # NOT carried forward from the prior served file. _schema.json is COMMITTED, so a
  # FRESH VOLUME with no prior served file reproduces every top-level key (and the
  # gold block) BYTE-IDENTICAL: closes `reference-bake-no-meta-on-fresh-volume`
  # (gold slice 6, 2026-06-10). Fresh-checkout fallback (no store yet): carry the
  # live file forward, then `regen_meta.py --capture` promotes it.
  # Per-feature `maturity` (the editor Tier chip's store of record): each reference
  # feature is stamped with the file's layer maturity from the store
  # (`maturity-tier-derived-from-panel-tree-position`); panel.js reads
  # props.maturity first, the node literal as a default.
  FEATS="$feat_tmp" OUT="$out" WRITE="$ref_write" FNAME="$fname" \
    SCRIPT_DIR="$SCRIPT_DIR" python3 - <<'PY'
import json, os, sys
sys.path.insert(0, os.environ["SCRIPT_DIR"])
import regen_meta as rm
feats = json.load(open(os.environ["FEATS"]))
out_path = os.environ["OUT"]                          # live file (carry-forward fallback)
write_path = os.environ.get("WRITE") or out_path      # --check: write to a side path
fname = os.environ["FNAME"]
schema = rm._load_schema()
layer_mat = (schema.get("layers", {}).get(fname, {}) or {}).get("maturity")
if layer_mat:
    for ft in feats:
        props = ft.get("properties")
        if isinstance(props, dict) and "maturity" not in props:
            props["maturity"] = layer_mat
doc = {"type": "FeatureCollection", "features": feats}
top = rm.served_top_meta(fname, schema)               # store of record -> top keys
if top:
    for k, v in top.items():
        doc[k] = v
else:
    try:
        with open(out_path) as fh:
            prior = json.load(fh)
        for k, v in prior.items():
            if k not in ("type", "features"):
                doc[k] = v
    except (FileNotFoundError, ValueError):
        pass
tmp = write_path + ".tmp"
with open(tmp, "w") as fh:
    json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
os.replace(tmp, write_path)
os.chmod(write_path, 0o644)
print(f"  wrote {len(feats)} features to {write_path}")
PY
  [ "$CHECK" -eq 1 ] && CHECK_FILES+=("$out|$ref_write")
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
# The umbrella event/schema/status/updated_at wrapper now lives in the store of
# record: core.event_meta (going gold G_E, 2026-06-10, audit
# `event-umbrella-metadata-hardcoded-in-bake`). The bake reads the umbrella row
# below and composes the document wrapper from DB truth. The heredoc here is now
# only the FALLBACK for a fresh/unseeded volume that has no core.event_meta row
# yet -- the bake never throws and never emits a broken document (C5). Seed it with
# mvp/scripts/seed_event_meta.py; init_db.sql carries the table DDL.
SCHED_OUT="$ROOT_DIR/website/data/aop_event_schedule.json"
EVENT_META_FALLBACK=$(cat <<'EOF'
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
# Read the umbrella row from core.event_meta and shape it back into the served
# `{schema, updated_at, status, event{...}}` wrapper. `json_build_object` (NOT
# jsonb) preserves the column ORDER below so the served `event{}` keys stay in the
# canonical id/label/date.../caveat order (jsonb sorts keys -> would churn the
# served bytes). The Python wrapper below merges any future `attrs` fields over
# this block so nothing a user adds later is dropped. Emits an empty string when no
# umbrella row exists -> the bake fallback is used. NULL columns are kept here (the
# Python wrapper strips them) to preserve key order deterministically.
event_meta_sql="SELECT coalesce((
  SELECT json_build_object(
    'schema', schema,
    'updated_at', schedule_updated_at,
    'status', status,
    'event', json_build_object(
      'id', event_id,
      'label', label,
      'date_range_label', date_range_label,
      'end_date_label', end_date_label,
      'source_context', source_context,
      'source_summary', source_summary,
      'caveat', caveat
    ),
    'attrs', attrs
  )::text
  FROM core.event_meta
  WHERE archived_at IS NULL
  ORDER BY id
  LIMIT 1
), '');"
EVENT_META_DB="$(docker compose exec -T db psql -v ON_ERROR_STOP=1 -U aop -d aop_map -At -c "$event_meta_sql")"
if [ -n "$EVENT_META_DB" ]; then
  EVENT_META="$EVENT_META_DB"
  echo "Event umbrella: read from core.event_meta (store of record)."
else
  EVENT_META="$EVENT_META_FALLBACK"
  echo "Event umbrella: no core.event_meta row -- using the bake fallback (unseeded volume)."
fi
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
sched_write="$SCHED_OUT"; [ "$CHECK" -eq 1 ] && sched_write="${SCHED_OUT}.check"
META="$EVENT_META" BODY="$sched_tmp" OUT="$sched_write" python3 - <<'PY'
import json, os
doc = json.loads(os.environ["META"])              # {schema, updated_at, status, event[, attrs]}
# DB path: core.event_meta carries a top-level `attrs` (future umbrella fields with
# no column) + NULL event values kept to preserve key order. Strip the NULLs and
# merge attrs OVER the event{} block so nothing a user adds later is dropped, then
# drop the top-level attrs key (it is not part of the served wrapper). The fallback
# heredoc path has no `attrs` key and no NULLs, so both branches are no-ops there.
event = doc.get("event") or {}
event = {k: v for k, v in event.items() if v is not None}
extra = doc.pop("attrs", None)
if isinstance(extra, dict):
    event.update(extra)
doc["event"] = event
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
[ "$CHECK" -eq 1 ] && CHECK_FILES+=("$SCHED_OUT|$sched_write")
rm -f "$sched_tmp"

echo "Event-schedule export complete."

# --- Re-apply the published POI ★ curation ------------------------------------
# The DB has no `highlight` column yet, so the SQL bake above emits features WITHOUT
# the star. bake_poi_stars.py stamps `properties.highlight` (the published ★; source
# of record website/data/aop_poi_index.json) back onto the freshly-baked files -- the
# same "machine refresh THEN re-apply human curation" order as
# rebake_canonical -> bake_panel_overrides. This makes the ★ part of THIS bake's fixed
# point, so a re-export never silently reverts the stars (--check stamps the .check
# side files too, so the byte-proof still holds). Carrying ★ into core.features.attrs
# so the SQL bake emits it directly is the eventual cleanup (then drop this step).
if [ "$CHECK" -eq 1 ]; then
  python3 "$SCRIPT_DIR/bake_poi_stars.py" --check
else
  python3 "$SCRIPT_DIR/bake_poi_stars.py"
fi

# --- Manifest regen (ONE writer of the served files owns _schema.json's DERIVED
#     fields) --------------------------------------------------------------------
# This export script is the LAST writer of the served reference/publish files, so it
# refreshes _schema.json's per-layer `features` count + top-level `updated_at` from
# the served truth -- closing `schema-manifest-stale` (the export bake used to write
# 5 files but never touch the manifest, so its counts/date drifted). The CURATED
# fields (maturity stamp, the verbatim `meta`, collection_meta, kind, machine,
# layer_provenance, crosswalk, facets, maturity_tiers) are PRESERVED -- maturity is
# INPUT, counts/date are OUTPUT, no circularity. In --check mode it reports only.
# Skipped under --check writes nothing (the side-file bake didn't change the served
# tree, so a manifest refresh there would be spurious).
if [ "$CHECK" -eq 0 ]; then
  echo "Regenerating _schema.json manifest counts (regen_meta.py --manifest)"
  python3 "$SCRIPT_DIR/regen_meta.py" --manifest
fi

# --- --check pure-function proof: byte-diff each freshly-baked side file against
#     the live served file, then delete the side files. NO REVERT iff all match.
if [ "$CHECK" -eq 1 ]; then
  echo ""
  echo "=== --check: byte-comparing fresh bake against the live served tree ==="
  drift=0
  for pair in "${CHECK_FILES[@]}"; do
    live="${pair%%|*}"
    fresh="${pair##*|}"
    if [ ! -f "$live" ]; then
      echo "  NEW   $(basename "$live") (no live file to compare)"; drift=1
    elif cmp -s "$live" "$fresh"; then
      echo "  same  $(basename "$live")"
    else
      echo "  DRIFT $(basename "$live") -- the bake would CHANGE this served file:"
      # `|| true` so a SIGPIPE from `head` closing the pipe early can't trip the
      # script's `set -euo pipefail` and skip the cleanup below.
      { diff <(python3 -m json.tool "$live" 2>/dev/null || cat "$live") \
             <(python3 -m json.tool "$fresh" 2>/dev/null || cat "$fresh") || true; } | head -40 || true
      drift=1
    fi
    rm -f "$fresh"
  done
  if [ "$drift" -eq 0 ]; then
    echo "--check: NO REVERT -- every served file is byte-identical to a fresh bake (pure function)."
    exit 0
  fi
  echo "--check: DRIFT DETECTED -- a re-bake would change the served tree (see above)."
  exit 1
fi
