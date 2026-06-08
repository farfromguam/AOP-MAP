#!/usr/bin/env python3
"""Apply right-panel editor edits into PostGIS core.features (layer='poi'), the DB SINK.

Retirement step (2026-06-06): core.pois was folded into the converged core.features
(layer='poi'); this sink now upserts core.features and the bake reads publish.features.
The match key (source_key) and all the no-limiting-code guarantees below are unchanged.

This is the AUTHOR->STORE link for "going gold": the web editor's export
(schema `aop-panel-overrides-v1`) is applied to `core` instead of baked into the
served files. `core` is the single source of truth; `export_publish_geojson.sh`
is the only writer of website/data/*.geojson. localStorage becomes a working
buffer. Card: brain/tasks/06_going_gold/gold_migration.md (slice 1).

    edit in the panel -> "Export edits" (aop_panel_overrides.json)
      -> apply_panel_overrides_to_core.py aop_panel_overrides.json   (THIS script)
      -> export_publish_geojson.sh   (bake core -> served files)
      -> deploy

ONE parser, TWO sinks: the schema/normalize contract lives in panel_overrides.py
and is shared with the FILE sink (bake_panel_overrides.py). The only difference
is this sink writes the DB, and it is PERMISSIVE where the file baker rejected:

  * No-limiting-code (C5 / loop contract #3): this path ADDS rows. It never
    rejects a value, never throws on an unknown/missing value, never skips a row.
    - unknown editor keys (no core.pois column) -> folded into `notes` (never dropped)
    - missing values -> a safe default (a stub edit / created row is NOT publishable
      by default; the publish view is the only gate)
    - an unparseable entry -> upserted with a `notes` flag, never dropped
  * edits[]/created[] UPSERT `ON CONFLICT (source_key)` -- never a bare UPDATE.
    A bare `UPDATE ... WHERE source_key` is BANNED: an unmatched key would be a
    silent zero-row no-op (a lost edit). Upsert => an edit to a not-yet-present
    key INSERTS a stub under its raw source_key (flagged in notes) instead of
    vanishing. We assert upserted-count == input-count to prove no silent drop.
  * deleted[] ARCHIVES (sets archived_at), never hard-deletes. There is no
    hard-delete of any core row anywhere here -- archive only. Archiving an
    absent key is a harmless no-op (logged, not an error).

Scope: the POI door of core.features (layer = 'poi'). The buildings/cemeteries/...
doors (other layers) are a future increment on this same script + module.

Usage:
  apply_panel_overrides_to_core.py aop_panel_overrides.json
  pbpaste | apply_panel_overrides_to_core.py -
  apply_panel_overrides_to_core.py aop_panel_overrides.json --dry-run   # print SQL, run nothing
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from panel_overrides import (
    VIEW_STATE_KEYS,
    read_payload,
    round_coords,
    build_created_feature,
    split_key,
)

REPO = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO / "mvp" / "docker-compose.yml"

# Provenance source for editor-authored / stub rows (mirrors seed_core_pois.sql).
APPLY_SOURCE_NAME = "AOP web editor (apply)"

# Editor editable key -> core.features column. Keys NOT here (and not view state)
# are folded into `notes` so nothing is dropped (C5). `highlight` is view state
# (VIEW_STATE_KEYS) -- never applied (a star is not a fact about the feature).
# `notes` is handled specially (it is both an editable key and the catch-all
# column), so it is intentionally absent from this direct map.
POI_COL = {"name": "name", "description": "description", "kind": "kind"}


def sql_str(value) -> str:
    """SQL literal for a text value (None -> NULL); single quotes doubled."""
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_bool(value, default: bool) -> str:
    if value is None:
        return "true" if default else "false"
    if isinstance(value, str):
        return "true" if value.strip().lower() in ("true", "t", "1", "yes") else "false"
    return "true" if value else "false"


def point_geom_sql(geometry) -> str:
    """ST_MakePoint for a Point geometry; NULL for anything else (a non-point in
    a POI context is stored geom-less + flagged, never thrown on)."""
    if isinstance(geometry, dict) and geometry.get("type") == "Point":
        coords = geometry.get("coordinates")
        if isinstance(coords, (list, tuple)) and len(coords) >= 2 \
           and all(isinstance(c, (int, float)) for c in coords[:2]):
            lng, lat = round_coords([coords[0], coords[1]])
            return f"ST_SetSRID(ST_MakePoint({lng}, {lat}), 4326)"
    return "NULL"


def attrs_marker(extras: dict) -> str:
    """A compact, idempotent notes tag carrying editor keys that have no core.pois
    column (so they are preserved as text, never dropped)."""
    if not extras:
        return ""
    body = "; ".join(f"{k}={extras[k]}" for k in sorted(extras))
    return f"[attrs: {body}]"


def edit_block(key: str, entry: dict, idx: int) -> str:
    """One edit -> an UPSERT that always touches exactly one row (no zero-row
    write). On INSERT (key absent) it lands a stub flagged in notes; on CONFLICT
    it patches only the edited columns (provenance is left intact)."""
    patch = entry.get("properties") or {}
    mapped: dict[str, object] = {}
    user_notes = None
    extras: dict[str, object] = {}
    for k, v in patch.items():
        if k in VIEW_STATE_KEYS or k == "id":
            pass  # view state (highlight, __locked, _id, _src, __group) / id -- not data
        elif k == "notes":
            user_notes = v
        elif k in POI_COL:
            mapped[POI_COL[k]] = v
        else:
            extras[k] = v  # unknown editor key -> preserved in notes, never dropped

    geom_sql = point_geom_sql(entry.get("geometry"))
    marker = attrs_marker(extras)

    insert_notes = user_notes if user_notes is not None \
        else "slice1 apply: edit to source_key not yet present -- inserted as stub"
    if marker:
        insert_notes = f"{insert_notes} {marker}".strip()

    # INSERT column/value lists (the absent-key path). layer='poi' -- the POI door
    # of the converged core.features (the Retirement step folded core.pois in).
    cols = ["layer", "source_key"]
    vals = ["'poi'", sql_str(key)]
    for col, val in mapped.items():
        cols.append(col)
        vals.append(sql_str(val))
    if geom_sql != "NULL":
        cols.append("geom")
        vals.append(geom_sql)
    cols += ["notes", "source_id", "is_destination", "last_verified"]
    vals += [
        sql_str(insert_notes),
        f"(SELECT id FROM source_register.sources WHERE name = {sql_str(APPLY_SOURCE_NAME)})",
        "true",
        "now()",
    ]

    # ON CONFLICT DO UPDATE: only the edited columns + last_verified (an edit IS a
    # check). Provenance/source_id are NOT touched. notes is set only when the
    # user edited it or there are extras to preserve (never clobbered by the stub).
    sets = [f"{col} = EXCLUDED.{col}" for col in mapped]
    if geom_sql != "NULL":
        sets.append("geom = EXCLUDED.geom")
    if user_notes is not None:
        sets.append(f"notes = {sql_str((user_notes + ' ' + marker).strip() if marker else user_notes)}")
    elif marker:
        # preserve any existing note, refresh the attrs marker idempotently
        sets.append(
            "notes = NULLIF(trim(regexp_replace(COALESCE(core.features.notes, ''), "
            f"'\\s*\\[attrs:[^\\]]*\\]', '', 'g')) || ' ' || {sql_str(marker)}, '')"
        )
    sets.append("last_verified = now()")

    return (
        f"WITH up AS (\n"
        f"  INSERT INTO core.features ({', '.join(cols)})\n"
        f"  VALUES ({', '.join(vals)})\n"
        f"  ON CONFLICT (source_key) DO UPDATE SET {', '.join(sets)}\n"
        f"  RETURNING source_key, (xmax = 0) AS inserted\n"
        f")\n"
        f"INSERT INTO _applied SELECT 'edit', source_key, inserted FROM up;"
    )


def created_block(raw: dict, idx: int) -> str:
    """One created feature -> an UPSERT (idempotent: re-running the same export
    updates the same source_key row, never duplicates)."""
    raw_props = dict(raw.get("properties") or {})
    src = raw_props.get("_src") or "userFeatures"
    local_id = raw_props.get("_id")
    if local_id is None:
        local_id = raw_props.get("id")

    note_flag = ""
    if local_id is None:
        # missing id -> generate a key, never drop (loop contract #3)
        local_id = f"unkeyed-{idx}"
        note_flag = "slice1 apply: created feature had no _id/id -- generated key"
    source_key = f"{src}:{local_id}"

    feat = build_created_feature(raw, "")  # today unused here (we stamp last_verified=now())
    if feat is None:
        # build_created_feature only returns None on a missing id, which we
        # already generated above; rebuild a minimal feature so nothing is dropped.
        feat = {
            "geometry": raw.get("geometry"),
            "properties": {"name": raw_props.get("name") or "Untitled"},
        }
        note_flag = (note_flag + " | unbuildable feature -- minimal row").strip(" |")
    fp = feat.get("properties") or {}

    name = fp.get("name") or "Untitled"
    description = fp.get("description", "")
    kind = fp.get("kind")
    status = fp.get("status") or "core"
    confidence = fp.get("confidence") or "observed"
    permission = fp.get("permission") or "AOP first-party"  # safe default: NOT publish
    publish_status = raw_props.get("publish_status") or "candidate"  # safe default: NOT published
    is_destination = sql_bool(raw_props.get("is_destination"), True)
    geom_sql = point_geom_sql(feat.get("geometry"))

    # extras = editor keys carried by build_created_feature that have no column.
    known = {"id", "name", "description", "kind", "source", "confidence",
             "permission", "status", "last_checked", "notes"}
    extras = {k: v for k, v in fp.items() if k not in known}
    base_notes = fp.get("notes")
    notes_parts = [p for p in (base_notes, note_flag or None, attrs_marker(extras) or None) if p]
    notes_val = " ".join(str(p) for p in notes_parts) if notes_parts else None

    cols = ["layer", "source_key", "name", "description", "kind", "is_destination", "status",
            "confidence", "permission", "publish_status", "geom", "notes",
            "source_id", "last_verified"]
    vals = [
        "'poi'", sql_str(source_key), sql_str(name), sql_str(description), sql_str(kind),
        is_destination, sql_str(status), sql_str(confidence), sql_str(permission),
        sql_str(publish_status), geom_sql, sql_str(notes_val),
        f"(SELECT id FROM source_register.sources WHERE name = {sql_str(APPLY_SOURCE_NAME)})",
        "now()",
    ]
    sets = [
        "name = EXCLUDED.name", "description = EXCLUDED.description", "kind = EXCLUDED.kind",
        "is_destination = EXCLUDED.is_destination", "status = EXCLUDED.status",
        "confidence = EXCLUDED.confidence", "permission = EXCLUDED.permission",
        "publish_status = EXCLUDED.publish_status",
        "geom = COALESCE(EXCLUDED.geom, core.features.geom)",
        "notes = EXCLUDED.notes", "last_verified = now()",
    ]
    return (
        f"WITH up AS (\n"
        f"  INSERT INTO core.features ({', '.join(cols)})\n"
        f"  VALUES ({', '.join(vals)})\n"
        f"  ON CONFLICT (source_key) DO UPDATE SET {', '.join(sets)}\n"
        f"  RETURNING source_key, (xmax = 0) AS inserted\n"
        f")\n"
        f"INSERT INTO _applied SELECT 'created', source_key, inserted FROM up;"
    )


def delete_block(key: str) -> str:
    """One delete -> ARCHIVE (set archived_at). Never DELETE. Archiving an absent
    key matches zero rows and is a harmless no-op."""
    return (
        f"WITH del AS (\n"
        f"  UPDATE core.features SET archived_at = now()\n"
        f"  WHERE source_key = {sql_str(key)} AND layer = 'poi' AND archived_at IS NULL\n"
        f"  RETURNING source_key\n"
        f")\n"
        f"INSERT INTO _applied SELECT 'delete', source_key, NULL FROM del;"
    )


def build_sql(payload: dict) -> tuple[str, int, int, int]:
    edits = payload.get("edits") or {}
    created = payload.get("created") or []
    deleted = payload.get("deleted") or []

    parts: list[str] = ["BEGIN;"]
    parts.append("CREATE TEMP TABLE _applied(kind text, source_key text, inserted boolean);")
    # Provenance row for editor-authored / stub rows (idempotent).
    parts.append(
        "INSERT INTO source_register.sources\n"
        "  (name, source_type, url_or_contact, license_or_permission,\n"
        "   publish_status, confidence_default, notes)\n"
        f"SELECT {sql_str(APPLY_SOURCE_NAME)}, 'derived',\n"
        "  'mvp/scripts/apply_panel_overrides_to_core.py',\n"
        "  'internal -- authored via the web editor, applied to core',\n"
        "  'publish', 'mixed',\n"
        "  'Rows authored in the web editor and applied to core.features layer=poi (going gold).'\n"
        "WHERE NOT EXISTS (\n"
        f"  SELECT 1 FROM source_register.sources WHERE name = {sql_str(APPLY_SOURCE_NAME)}\n"
        ");"
    )

    for i, (key, entry) in enumerate(edits.items()):
        parts.append(edit_block(key, entry, i))
    for i, raw in enumerate(created):
        parts.append(created_block(raw, i))
    for key in deleted:
        src, _ = split_key(key)  # validates the key shape; archive uses the whole key
        parts.append(delete_block(key))

    # Machine-readable summary (read inside the txn, before COMMIT).
    parts.append("SELECT 'EDITS_UPSERTED=' || count(*) FROM _applied WHERE kind = 'edit';")
    parts.append("SELECT 'CREATED_UPSERTED=' || count(*) FROM _applied WHERE kind = 'created';")
    parts.append("SELECT 'DELETED_ARCHIVED=' || count(*) FROM _applied WHERE kind = 'delete';")
    parts.append("SELECT 'POIS_TOTAL=' || count(*) FROM core.features WHERE layer = 'poi';")
    parts.append("SELECT 'POIS_ACTIVE=' || count(*) FROM core.features WHERE layer = 'poi' AND archived_at IS NULL;")
    parts.append("COMMIT;")
    return "\n".join(parts), len(edits), len(created), len(deleted)


def run_psql(sql: str) -> str:
    cmd = [
        "docker", "compose", "-f", str(COMPOSE_FILE), "exec", "-T", "db",
        "psql", "-U", "aop", "-d", "aop_map", "-v", "ON_ERROR_STOP=1", "-At", "-q",
    ]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        return ""  # caller treats empty/missing summary as failure (an honest error, not a silent drop)
    return proc.stdout


def parse_count(out: str, label: str) -> int:
    for line in out.splitlines():
        if line.startswith(label + "="):
            return int(line.split("=", 1)[1])
    return -1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Exported aop_panel_overrides.json, or '-' for stdin")
    ap.add_argument("--dry-run", action="store_true", help="Print the SQL; run nothing")
    args = ap.parse_args()

    # Permissive read (strict=False): an unexpected schema still upserts (C5).
    payload = read_payload(args.input, strict=False)
    sql, n_edits, n_created, n_deleted = build_sql(payload)

    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("apply-to-core: FAILED (psql error above; transaction rolled back)")
        return 1

    e = parse_count(out, "EDITS_UPSERTED")
    c = parse_count(out, "CREATED_UPSERTED")
    d = parse_count(out, "DELETED_ARCHIVED")
    total = parse_count(out, "POIS_TOTAL")
    active = parse_count(out, "POIS_ACTIVE")

    print("== applied panel overrides to core.features (layer='poi') ==")
    print(f"  edits     upserted: {e} / {n_edits} input")
    print(f"  created   upserted: {c} / {n_created} input")
    print(f"  deleted  archived : {d} / {n_deleted} input (absent keys are no-ops)")
    print(f"  core.features(poi) total: {total}  active(not archived): {active}")

    # No silent zero-row write: every edit/created upsert must touch exactly one
    # row (ON CONFLICT guarantees insert-or-update). If the counts fall short,
    # a write silently matched zero rows -- the failure mode a bare UPDATE hides.
    ok = (e == n_edits) and (c == n_created)
    if not ok:
        print("apply-to-core: FAIL -- upserted count != input count (a silent zero-row write)")
        return 1
    print("apply-to-core: OK (edits/created upserted 1 row each; deletes archived; nothing dropped)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
