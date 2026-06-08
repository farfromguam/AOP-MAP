#!/usr/bin/env python3
"""One-time importer: a served GeoJSON layer -> PostGIS core.features (going gold).

This is the migration door for slices 2-5 of brain/tasks/06_going_gold/gold_migration.md.
ONE generic importer for every layer (buildings, cemeteries, visitor callouts,
trails): it lands each feature into the converged core.features table with the
CMFS spine in columns and the FULL original `properties` in JSONB `attrs` so
NOTHING is dropped, then the bake reconstructs the served file from core.

  website/data/<layer>.geojson  --import-->  core.features (layer='<layer>')
    --export_publish_geojson.sh-->  website/data/<layer>.geojson  (sole writer)

No-limiting-code (C5 / loop contract #3): this path ADDS rows. It never rejects a
value, never throws on an unknown/missing value, never skips a feature.
  * the full original `properties` go into `attrs` verbatim -- no key allowlist.
  * spine columns are read by their CMFS key if present, else left NULL (a safe
    default) -- never coerced (a building's reference permission stays verbatim,
    never forced to 'publish'; the publish view is the only gate).
  * a feature with no id for the source_key gets a generated key + a notes flag,
    never dropped.
  * UPSERT ON CONFLICT (source_key) -- re-running the same import is idempotent,
    never duplicates, and never silently zero-row-writes (count == input asserted).

Reference layers (buildings, cemeteries, ...) carry their TRUE non-'publish'
permission, so they are absent from publish.features (correct) and bake to their
OWN served file without the publish gate.

Usage (buildings, slice 2):
  import_layer_to_core_features.py website/data/aop_buildings.geojson \
    --layer buildings --id-field build_id \
    --source-name "FEMA USA Structures / ORNL (buildings)" \
    --source-permission "FEMA public data layer; no warranty; raw reference context"

  ... --dry-run       # print the SQL, run nothing
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO / "mvp" / "docker-compose.yml"

# CMFS spine: editor/served property key -> core.features column. Everything NOT
# here still lands in `attrs` (the full original properties), so nothing drops.
SPINE = {
    "name": "name",
    "kind": "kind",
    "status": "status",
    "confidence": "confidence",
    "permission": "permission",
    "publish_status": "publish_status",
}
# The description is read from 'description' OR 'blurb' in the SOURCE GeoJSON
# (CMFS crosswalk for heterogeneous external vocab); it is WRITTEN to the
# core.features.description column (renamed from `blurb` 2026-06-08).
BLURB_KEYS = ("description", "blurb")


def sql_str(value) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_jsonb(obj) -> str:
    return sql_str(json.dumps(obj, ensure_ascii=False, sort_keys=True)) + "::jsonb"


def sql_bool(value: bool) -> str:
    return "true" if value else "false"


def geom_sql(geometry) -> str:
    """ST_GeomFromGeoJSON for any geometry type (Polygon/Point/Line/...), SRID
    4326; NULL for a missing/invalid geometry (stored geom-less, never thrown)."""
    if isinstance(geometry, dict) and geometry.get("type") and geometry.get("coordinates") is not None:
        gj = json.dumps(geometry, ensure_ascii=False)
        return f"ST_SetSRID(ST_GeomFromGeoJSON({sql_str(gj)}), 4326)"
    return "NULL"


def source_key_for(props: dict, id_field: str, prefix: str, idx: int):
    """Build a stable, UNIQUE source_key '<prefix>:<v1>[:<v2>...]'. id_field may be
    a comma-separated list of property keys (e.g. 'parcel_id,geom_role') when no
    single property is unique per feature -- the values are joined so the marker
    and parcel rows of one cemetery get distinct keys. Missing values are skipped
    (flagged), never throw."""
    fields = [f.strip() for f in id_field.split(",") if f.strip()]
    parts = [str(props[f]) for f in fields if props.get(f) is not None]
    note = None
    if not parts:
        parts = [f"unkeyed-{idx}"]
        note = f"import: feature had no {id_field} value -- generated key"
    elif len(parts) < len(fields):
        note = f"import: feature missing part of {id_field} -- keyed on what was present"
    return f"{prefix}:" + ":".join(parts), note


def feature_block(feat: dict, layer: str, prefix: str, id_field: str,
                  is_destination: bool, idx: int) -> str:
    props = dict(feat.get("properties") or {})

    source_key, note = source_key_for(props, id_field, prefix, idx)

    cols = ["layer", "source_key", "is_destination", "attrs",
            "geom", "source_id", "last_verified"]
    vals = [
        sql_str(layer), sql_str(source_key), sql_bool(is_destination),
        sql_jsonb(props), geom_sql(feat.get("geometry")),
        "(SELECT id FROM source_register.sources WHERE name = :SRC_NAME)",
        "now()",
    ]

    # Spine columns (read by CMFS key if present; absent -> NULL, never coerced).
    for key, col in SPINE.items():
        if key in props:
            cols.append(col)
            vals.append(sql_str(props[key]))
    description = next((props[k] for k in BLURB_KEYS if k in props and props[k] is not None), None)
    if description is not None:
        cols.append("description")
        vals.append(sql_str(description))
    if note is not None:
        cols.append("notes")
        vals.append(sql_str(note))

    # ON CONFLICT: refresh the data columns (idempotent re-import); provenance and
    # source_key are stable. attrs is replaced wholesale (the file is the truth on
    # a one-time import).
    sets = [f"{c} = EXCLUDED.{c}" for c in cols
            if c not in ("source_key", "source_id", "last_verified")]
    sets.append("last_verified = now()")

    return (
        f"WITH up AS (\n"
        f"  INSERT INTO core.features ({', '.join(cols)})\n"
        f"  VALUES ({', '.join(vals)})\n"
        f"  ON CONFLICT (source_key) DO UPDATE SET {', '.join(sets)}\n"
        f"  RETURNING source_key, (xmax = 0) AS inserted\n"
        f")\n"
        f"INSERT INTO _imported SELECT source_key, inserted FROM up;"
    )


def build_sql(features: list, layer: str, prefix: str, id_field: str,
              is_destination: bool, source_name: str, source_permission: str) -> str:
    parts = ["BEGIN;",
             "CREATE TEMP TABLE _imported(source_key text, inserted boolean);"]
    # Provenance source row (idempotent). Reference import -> NOT publish.
    parts.append(
        "INSERT INTO source_register.sources\n"
        "  (name, source_type, url_or_contact, license_or_permission,\n"
        "   publish_status, confidence_default, notes)\n"
        f"SELECT {sql_str(source_name)}, 'import',\n"
        "  'mvp/scripts/import_layer_to_core_features.py',\n"
        f"  {sql_str(source_permission)},\n"
        "  'reference', 'mixed',\n"
        f"  'Layer {sql_str(layer)[1:-1]} imported from website/data into core.features (going gold).'\n"
        "WHERE NOT EXISTS (\n"
        f"  SELECT 1 FROM source_register.sources WHERE name = {sql_str(source_name)}\n"
        ");"
    )
    for i, feat in enumerate(features):
        block = feature_block(feat, layer, prefix, id_field, is_destination, i)
        block = block.replace(":SRC_NAME", sql_str(source_name))
        parts.append(block)
    parts.append(f"SELECT 'IMPORTED=' || count(*) FROM _imported;")
    parts.append(f"SELECT 'LAYER_TOTAL=' || count(*) FROM core.features WHERE layer = {sql_str(layer)} AND archived_at IS NULL;")
    parts.append("COMMIT;")
    return "\n".join(parts)


def run_psql(sql: str) -> str:
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), "exec", "-T", "db",
           "psql", "-U", "aop", "-d", "aop_map", "-v", "ON_ERROR_STOP=1", "-At", "-q"]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        return ""
    return proc.stdout


def parse_count(out: str, label: str) -> int:
    for line in out.splitlines():
        if line.startswith(label + "="):
            return int(line.split("=", 1)[1])
    return -1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("geojson", help="website/data/<layer>.geojson to import")
    ap.add_argument("--layer", required=True, help="core.features.layer value (buildings, cemeteries, ...)")
    ap.add_argument("--id-field", default="id",
                    help="property (or comma-separated properties) for the source_key. Use a "
                         "composite like 'parcel_id,geom_role' when no single property is unique "
                         "per feature (default: id)")
    ap.add_argument("--prefix", default=None, help="source_key prefix (default: the --layer value)")
    ap.add_argument("--is-destination", action="store_true", help="mark rows is_destination=true (default false)")
    ap.add_argument("--source-name", required=True, help="source_register.sources name for provenance")
    ap.add_argument("--source-permission", required=True, help="license_or_permission string for the source row")
    ap.add_argument("--dry-run", action="store_true", help="print the SQL; run nothing")
    args = ap.parse_args()

    doc = json.loads(Path(args.geojson).read_text())
    features = doc.get("features") or []
    prefix = args.prefix or args.layer

    sql = build_sql(features, args.layer, prefix, args.id_field, args.is_destination,
                    args.source_name, args.source_permission)
    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("import: FAILED (psql error above; transaction rolled back)")
        return 1
    imported = parse_count(out, "IMPORTED")
    total = parse_count(out, "LAYER_TOTAL")
    print(f"== imported {args.layer} into core.features ==")
    print(f"  features in file : {len(features)}")
    print(f"  upserted         : {imported}")
    print(f"  layer total (active): {total}")
    if imported != len(features):
        print("import: FAIL -- upserted count != feature count (a silent drop)")
        return 1
    print("import: OK (every feature upserted; nothing dropped)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
