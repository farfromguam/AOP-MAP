#!/usr/bin/env python3
"""Complete-reconciliation fold: sync core.features.attrs to the COUNCIL-CLEARED
served reference files so a DB-bake of them is loss-free (slice G_A "one writer").

THE SITUATION (verified by two prior agents, 2026-06-09/10). The 4 served reference
files are the A1-A4 council-cleared, committed canonical truth:
  website/data/{aop_buildings,aop_cemeteries,aop_visitor_context_callouts,
                aop_trail_network}.geojson
`export_publish_geojson.sh` bakes reference layers `properties = attrs` VERBATIM, so
the served file's properties ARE the DB attrs. But core.features.attrs is BEHIND the
served files:
  * buildings: attrs.name = the street ADDRESS ("880 Ellis Cove Road"), served name =
    the facility name ("Front Office"); attrs.status = the FEMA role
    ("facility"/"presence_only"), served status = "raw context".
  * trails: attrs.difficulty = "moderate" on sfwda-114 (Descension) / sfwda-98
    (Ascension) where the served file (AND attrs.facets.difficulty AND attrs.color
    = green #1f9d3a) say "easy". The served file is internally consistent (easy +
    green); the DB top-level difficulty is the lone contradiction.
  * all 4: the slice-1 sidecar fold left a STRAY top-level `original` key in attrs
    (the canonical convention is `_original`). The served files carry `_original`
    (e.g. {"name":"6"}); the DB additionally carries `original`
    (e.g. {"name":"6","difficulty":"easy","description":"..."}).

A DB-bake is therefore LOSSY today: it would regress the building name to the
address, the 2 trails' difficulty to "moderate", and emit a redundant `original`
block. This script does ONE thing: it SYNCS the DB attrs UP TO the served canonical
truth (per source_key), KEPT in the DB as an additive migration.

  served file feature.properties  --(served WINS)-->  core.features.attrs   (per source_key)

SCOPE — WHAT THIS SCRIPT DOES NOT DO (recorded 2026-06-10, after a council Mason andon):
it does NOT bake/adopt the served files and does NOT evict rebake_canonical. A first
run attempted that downstream half and it was REVERTED: the DB-bake still cannot
reproduce render-sensitive trail human-names ("Launchpad" stays a number/blank to
avoid spawning labels on unnamed edges), which is the columns-vs-attrs + trail-name
architectural fork (see `brain/tasks/06_going_gold/gold_slice6_backlog.md` "⛔ BLOCKED").
The 4 served reference files stay at HEAD and rebake_canonical remains their writer
until that fork is decided. This script's contribution is the DB attrs sync ONLY.

THE MERGE (a jsonb shallow merge, SERVED WINS):
  attrs := (COALESCE(attrs,'{}') || <served properties>) - 'original'
The served properties are placed to the RIGHT of attrs, so the served value WINS on
every key (name/status/difficulty/_original promoted to the served value). Any DB-only
attrs key is kept (additive) -- EXCEPT the stray `original`, explicitly dropped (the
canonical convention is `_original`, which the served props carry and the merge
installs). Verified pre-flight: the ONLY DB-only attrs key across all 4 layers is
`original`, so after the drop the merged attrs == exactly the served property set.

THE JOIN (the SAME business key import_layer_to_core_features.py minted as source_key,
matching fold_served_enrichment_into_core.py's recipe):
  * buildings  -> source_key = 'buildings:'  + props.build_id
  * cemeteries -> source_key = 'cemeteries:' + props.parcel_id + ':' + props.geom_role
  * visitor    -> source_key = 'visitor:'    + props.id
  * trails     -> source_key = 'trails:'      + props.id

ADDITIVE / IDEMPOTENT / BOUNDED (C5 / Mason / loop contract):
  * UPDATE only matched rows. NEVER INSERT, NEVER DELETE / archive, NEVER reject /
    coerce-to-blank / throw. Count stays 159 active (160 incl. the 1 archived row,
    which archived_at IS NULL excludes).
  * Re-run == byte-identical attrs (md5): the merge installs the served values and
    drops `original`; a second pass re-installs the same served values and finds no
    `original` to drop -> no change.
  * A served feature whose source_key matches NO DB row is REPORTED, never guessed,
    never inserted.

FLAG FOR THE USER (a curation call, not an engineering one): the 2-trail difficulty
is being SYNCED toward the deployed/served truth ("easy" -- which the served file's
facet + green color already agreed with); the DB import had said "moderate". The
served/catalog value wins here because these files are the committed canonical truth;
whether the real-world difficulty is easy or moderate is the user's curation call.

Reuses the connection + psql style of fold_served_enrichment_into_core.py /
import_layer_to_core_features.py (docker compose exec -T db psql, ON_ERROR_STOP,
-At -q, BEGIN/COMMIT, a TEMP table + summary). Writes the ONE sink (core.features).

Usage:
  fold_served_canonical_into_core.py             # fold into the live DB
  fold_served_canonical_into_core.py --dry-run   # print the SQL; run nothing
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO / "mvp" / "docker-compose.yml"
DATA = REPO / "website" / "data"


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
    """One served feature -> a reconciliation UPDATE on its core.features row.

    attrs := (COALESCE(attrs,'{}') || served) - 'original'
    The served bag to the RIGHT -> served WINS on every shared key (name/status/
    difficulty/_original become the served value); DB-only keys survive (additive)
    except the stray `original`, dropped here so the canonical `_original` (carried
    by served) is the only stash. Idempotent: a re-run installs the same served
    values and finds no `original`. Drops `original` whether or not the served bag
    carried one (it never does), so the result is always the served key set.
    """
    served = sql_jsonb(served_props)
    attrs_expr = f"((COALESCE(attrs, '{{}}'::jsonb) || {served}) - 'original')"
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
                parts.append(
                    f"INSERT INTO _folded VALUES "
                    f"({sql_str('NOKEY:' + layer + ':' + str(props.get('id') or props.get('name')))}, 0);")
                continue
            parts.append(fold_block(sk, props))
    parts.append(
        "SELECT 'ROW=' || source_key || '|' || matched FROM _folded ORDER BY source_key;")
    parts.append("SELECT 'MATCHED_ROWS=' || COALESCE(sum(matched),0) FROM _folded;")
    parts.append("SELECT 'ACTIVE_ROWS=' || count(*) FROM core.features WHERE archived_at IS NULL;")
    parts.append("SELECT 'TOTAL_ROWS=' || count(*) FROM core.features;")
    parts.append("SELECT 'STRAY_ORIGINAL=' || count(*) FROM core.features "
                 "WHERE archived_at IS NULL AND attrs ? 'original';")
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
        print("fold-served-canonical: FAILED (psql error above; transaction rolled back)")
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
    active = parse_one(out, "ACTIVE_ROWS")
    total = parse_one(out, "TOTAL_ROWS")
    stray = parse_one(out, "STRAY_ORIGINAL")

    print("== reconciled served canonical truth into core.features.attrs ==")
    print(f"  served reference features : {total_served}")
    print(f"  served features matched   : {matched_features} (DB rows updated: {matched_rows})")
    print(f"  core.features ACTIVE rows : {active}  (additive -- nothing inserted/dropped)")
    print(f"  core.features TOTAL rows  : {total}")
    print(f"  stray `original` keys left: {stray}  (dropped; canonical convention is `_original`)")
    if unmatched:
        print("  REPORTED (served features that matched NO DB row -- NOT inserted, NOT guessed):")
        for u in unmatched:
            print(f"    - {u}")
    else:
        print("  every served feature matched a DB row (no fork)")
    print("fold-served-canonical: OK (served name/status/difficulty/_original promoted "
          "as the canonical truth; stray `original` dropped; idempotent)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
