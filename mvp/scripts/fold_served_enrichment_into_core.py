#!/usr/bin/env python3
"""Fold the SERVED-file canonical enrichment into PostGIS core.features (slice G_A
prerequisite: catch the DB up to the served reference files).

THE FINDING THIS FIXES. The A1/A4 canonical re-bake wrote a `facets` block
(difficulty / address / category / revisit_note ...) + a per-feature `source_file`
(and the rebake's `_original` preservation block) into the SERVED reference files
website/data/{aop_buildings,aop_cemeteries,aop_visitor_context_callouts,
aop_trail_network}.geojson -- but those enrichment keys never reached core.features.
DB coverage today: facets on 3 cemeteries only, source_file on 0 reference rows;
the served files carry source_file on ALL 137 reference rows and facets on 129.
Because export_publish_geojson.sh bakes reference layers `properties = attrs`
VERBATIM, a DB bake of these files is LOSSY right now (it would emit a feature with
no facets/source_file). This slice brings the DB attrs UP TO the served attrs so a
re-bake is a pure function of the store of record.

  website/data/aop_buildings.geojson                 --fold by source_key-->  core.features (buildings)
  website/data/aop_cemeteries.geojson                --fold by source_key-->  core.features (cemeteries)
  website/data/aop_visitor_context_callouts.geojson  --fold by source_key-->  core.features (visitor)
  website/data/aop_trail_network.geojson             --fold by source_key-->  core.features (trails)
    --export_publish_geojson.sh-->  served files (now reproducible from the DB, loss-free)

THE JOIN (the SAME business key import_layer_to_core_features.py used to mint
source_key -- this is the complete join; the slice-1 fold's trail_number join only
covered 87/120 trails, this covers all 137 reference rows):
  * buildings  -> source_key = 'buildings:'  + props.build_id
  * cemeteries -> source_key = 'cemeteries:' + props.parcel_id + ':' + props.geom_role
  * visitor    -> source_key = 'visitor:'    + props.id
  * trails     -> source_key = 'trails:'      + props.id
Each served feature is matched to ITS core.features row by source_key and the row's
attrs is UPDATEd additively.

ADDITIVE ONLY / IDEMPOTENT (C5 / Mason / loop contract):
  * Only ADD the served enrichment keys (`facets`, `source_file`, `_original`, and
    any other served property key absent from the DB attrs). Existing DB attrs keys
    are NEVER dropped and NEVER overwritten -- the merge is
    `served_additions || attrs`, so a DB value already present always WINS.
  * `facets` is merged at the SUBKEY level: served facet subkeys absent from the DB
    facets are added (e.g. parcel rows gain `address`); the DB's own facet subkeys
    (e.g. a marker row's `revisit_note` from the slice-1 fold) are preserved and win
    on collision. Built as `served_facets || db_facets`.
  * NEVER INSERT a new row (count stays 160), NEVER DELETE / archive, NEVER
    coerce-to-blank, NEVER reject. UPDATE only matched rows.
  * Re-run == byte-identical DB state: every add is guarded by "absent in attrs",
    every merge lets the existing value win, so a second pass changes nothing.
  * A served feature whose source_key matches NO DB row is REPORTED, never guessed,
    never inserted.

Reuses the connection + psql style of fold_sidecars_into_core_features.py /
import_layer_to_core_features.py (docker compose exec -T db psql, ON_ERROR_STOP,
-At -q, BEGIN/COMMIT, a TEMP table + summary). Writes the ONE sink (core.features).

Usage:
  fold_served_enrichment_into_core.py             # fold into the live DB
  fold_served_enrichment_into_core.py --dry-run   # print the SQL; run nothing
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO / "mvp" / "docker-compose.yml"
DATA = REPO / "website" / "data"

# Served reference files whose canonical enrichment must reach core.features, and
# how to rebuild each feature's source_key from its props -- the SAME recipe the
# gold import (import_layer_to_core_features.py --id-field ...) used per layer.
def _sk_buildings(p):
    bid = p.get("build_id")
    return f"buildings:{bid}" if bid is not None else None

def _sk_cemeteries(p):
    pid, role = p.get("parcel_id"), p.get("geom_role")
    if pid is None or role is None:
        return None
    return f"cemeteries:{pid}:{role}"

def _sk_visitor(p):
    fid = p.get("id")
    return f"visitor:{fid}" if fid is not None else None

def _sk_trails(p):
    fid = p.get("id")
    return f"trails:{fid}" if fid is not None else None

LAYERS = {
    "buildings":  ("aop_buildings.geojson",                _sk_buildings),
    "cemeteries": ("aop_cemeteries.geojson",               _sk_cemeteries),
    "visitor":    ("aop_visitor_context_callouts.geojson", _sk_visitor),
    "trails":     ("aop_trail_network.geojson",            _sk_trails),
}


def sql_str(value) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_jsonb(obj) -> str:
    return "'" + json.dumps(obj, ensure_ascii=False, sort_keys=True).replace("'", "''") + "'::jsonb"


def load_json(path: Path) -> dict:
    with open(path) as fh:
        return json.load(fh)


def fold_block(source_key: str, served_props: dict) -> str:
    """One served feature -> an additive UPDATE on its core.features row by source_key.

    The served enrichment that may be missing from the DB attrs: `facets`,
    `source_file`, `_original`, and (defensively) any other served property key. We
    apply it as `served_additions || attrs` so EXISTING attrs keys always win (never
    overwritten); `facets` is merged subkey-level as `served_facets || db_facets` so
    the DB's own facet subkeys (revisit_note) survive and win on collision.

    Idempotent: `served_additions || attrs` with a re-run finds every served key
    already in attrs, so the merge is a no-op; the facets sub-merge likewise yields
    the same object. Byte-stable across runs.
    """
    # The full served property bag becomes the "additions" layer; placing `attrs` to
    # its RIGHT makes every existing DB key (and value) win -> we only ever ADD keys
    # the DB lacks, never overwrite. This also subsumes facets/source_file/_original
    # plus any other served-only key, satisfying "any other canonical-block key".
    additions = sql_jsonb(served_props)

    # facets needs subkey merge (not whole-object), else the DB's revisit_note would
    # be lost when the served facets object replaces it. Compute the merged facets as
    # served_facets || db_facets (db wins on collision) and jsonb_set it back on top
    # of the keys-merge result. Only emitted when the served feature HAS facets.
    has_served_facets = isinstance(served_props.get("facets"), dict)

    # base = additions || COALESCE(attrs,'{}')  -> existing keys win, missing added.
    base = f"({additions} || COALESCE(attrs, '{{}}'::jsonb))"
    if has_served_facets:
        served_facets = sql_jsonb(served_props["facets"])
        # merged facets = served_facets || existing-db-facets (db subkeys win).
        merged_facets = (
            f"({served_facets} || COALESCE(attrs->'facets', '{{}}'::jsonb))"
        )
        attrs_expr = f"jsonb_set({base}, '{{facets}}', {merged_facets})"
    else:
        attrs_expr = base

    return (
        f"WITH up AS (\n"
        f"  UPDATE core.features\n"
        f"     SET attrs = {attrs_expr},\n"
        f"         last_verified = now()\n"
        f"   WHERE source_key = {sql_str(source_key)}\n"
        f"     AND archived_at IS NULL\n"
        f"  RETURNING source_key\n"
        f")\n"
        f"INSERT INTO _folded SELECT {sql_str(source_key)}, count(*) FROM up;"
    )


def build_sql(features_by_layer: dict) -> tuple[str, int]:
    parts = ["BEGIN;",
             "CREATE TEMP TABLE _folded(source_key text, matched bigint);"]
    total_served = 0
    for layer, (fn, skf) in LAYERS.items():
        for feat in features_by_layer[layer]:
            props = dict(feat.get("properties") or {})
            sk = skf(props)
            total_served += 1
            if sk is None:
                # No business key to rebuild source_key -> cannot match. Report it
                # (matched=0, source_key tagged), never guess, never insert.
                parts.append(
                    f"INSERT INTO _folded VALUES "
                    f"({sql_str('NOKEY:' + layer + ':' + str(props.get('id') or props.get('name')))}, 0);")
                continue
            parts.append(fold_block(sk, props))
    # Per-row matched counts (inside the txn) so we can name every served feature
    # that matched zero DB rows (reported, not dropped).
    parts.append(
        "SELECT 'ROW=' || source_key || '|' || matched FROM _folded ORDER BY source_key;")
    parts.append("SELECT 'MATCHED_ROWS=' || COALESCE(sum(matched),0) FROM _folded;")
    parts.append("SELECT 'TOTAL_ROWS=' || count(*) FROM core.features;")
    parts.append("COMMIT;")
    return "\n".join(parts), total_served


def run_psql(sql: str) -> str:
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE), "exec", "-T", "db",
           "psql", "-U", "aop", "-d", "aop_map", "-v", "ON_ERROR_STOP=1", "-At", "-q"]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        return ""
    return proc.stdout


def parse_one(out: str, label: str) -> str:
    for line in out.splitlines():
        if line.startswith(label + "="):
            return line.split("=", 1)[1]
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print the SQL; run nothing")
    args = ap.parse_args()

    features_by_layer = {}
    for layer, (fn, _skf) in LAYERS.items():
        doc = load_json(DATA / fn)
        features_by_layer[layer] = doc.get("features") or []

    sql, total_served = build_sql(features_by_layer)

    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("fold-served-enrichment: FAILED (psql error above; transaction rolled back)")
        return 1

    rows = [line[4:] for line in out.splitlines() if line.startswith("ROW=")]
    unmatched = []
    matched_features = 0
    for r in rows:
        sk, matched = r.rsplit("|", 1)
        if int(matched) == 0:
            unmatched.append(sk)
        else:
            matched_features += 1

    matched_rows = parse_one(out, "MATCHED_ROWS")
    total = parse_one(out, "TOTAL_ROWS")

    print("== folded served-file enrichment into core.features ==")
    print(f"  served reference features : {total_served}")
    print(f"  served features matched   : {matched_features} (DB rows updated: {matched_rows})")
    print(f"  core.features total rows  : {total}  (additive -- nothing inserted/dropped)")
    if unmatched:
        print("  REPORTED (served features that matched NO DB row -- NOT inserted, NOT guessed):")
        for u in unmatched:
            print(f"    - {u}")
    else:
        print("  every served feature matched a DB row (no fork)")
    print("fold-served-enrichment: OK (facets/source_file/_original + any served-only key "
          "added where absent; existing DB attrs never overwritten; idempotent)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
