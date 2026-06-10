#!/usr/bin/env python3
"""Fold the authored SIDECAR text into PostGIS core.features (going gold, slice G_A).

THE STORE-OF-RECORD FOLD. The trail HUMAN names ("Launchpad"), difficulty, and
descriptions live ONLY in website/data/aop_trail_catalog.json, and the building/
cemetery/visitor/trail blurbs live ONLY in website/data/aop_poi_index.json. They
never entered the DB, so a bake from core.features can only emit name="1" for a
trail. Path A (rebake_canonical.py) folds these into the SERVED files; THIS slice
folds them into the DB so the bake is reproducible FROM the store of record.

  website/data/aop_trail_catalog.json   --fold by trail_number-->  core.features (trails)
  website/data/aop_poi_index.json       --fold by match{} keys -->  core.features (buildings/cemeteries/visitor/trail_centerlines)
    --export_publish_geojson.sh-->  served files (now emit "Launchpad", not "1")

The join keys (the sidecars' own match logic, mirrored against the DB):
  * trail_catalog.number      == core.features.attrs->>'trail_number'   (layer='trails')
  * poi_index buildings       == core.features.attrs->>'address'        (layer='buildings')
  * poi_index cemeteries      == attrs->>'parcel_id' + attrs->>'geom_role' (layer='cemeteries')
  * poi_index visitor_context == core.features.name                     (layer='visitor')
  * poi_index publish/trail   == core.features.name                     (layer='trail_centerlines')

ADDITIVE ONLY (C5 / Mason / loop contract):
  * UPDATE canonical columns/attrs on matched rows. Never DELETE, never hard-delete,
    never reject/skip/throw, never coerce-to-blank.
  * name is set ONLY where the catalog actually has a human name. A catalog entry
    with name=null (e.g. trail 96) NEVER blanks or stamps a name -- auto-naming an
    unnamed edge would later spawn a map label on it. description/difficulty likewise:
    a sidecar value is folded only where the sidecar HAS one.
  * The original physical value is PRESERVED, never dropped: the pre-fold canonical
    column value is stashed under attrs.original.<field> on the FIRST fold (the
    re-bake's additive-preserve pattern), so the bare trail number "1" stays
    addressable. The guard writes attrs.original.<field> only if it is not already
    present, so a re-run is byte-identical (idempotent).
  * Unmatched sidecar rows are REPORTED, not dropped (a catalog entry whose
    trail_number is not in the DB, a poi-index entry with no matching feature).
  * Idempotent: re-run == byte-identical DB state, no dupes (matched-by-key UPDATE,
    original-preserve guarded, attrs merged not replaced).

Reuses the connection + psql style of apply_panel_overrides_to_core.py /
import_layer_to_core_features.py (docker compose exec -T db psql, ON_ERROR_STOP,
-At -q, BEGIN/COMMIT, a TEMP table + parse_count summary). It writes the ONE sink
(core.features) -- no second store.

Usage:
  fold_sidecars_into_core_features.py                 # fold into the live DB
  fold_sidecars_into_core_features.py --dry-run       # print the SQL; run nothing
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPO / "mvp" / "docker-compose.yml"
DATA = REPO / "website" / "data"

TRAIL_CATALOG = DATA / "aop_trail_catalog.json"
POI_INDEX = DATA / "aop_poi_index.json"

# poi-index group -> the core.features layer it folds into, and how to read the
# DB match value(s) for each match{} key. A row matches an entry when EVERY
# (db-value == entry-match-value) for the entry's match keys (minus `source`).
# 'col:<name>'     reads a core.features column;
# 'attr:<key>'     reads core.features.attrs->><key>.
# A group not here (drawn_pois) carries no folded blurb -> reported, never written.
POI_GROUP_BINDING = {
    # source value in match{} -> (layer, {match_key: db_accessor})
    "buildings":       ("buildings",         {"address": "attr:address"}),
    "cemeteries":      ("cemeteries",        {"parcel_id": "attr:parcel_id",
                                              "geom_role": "attr:geom_role"}),
    "visitor_context": ("visitor",           {"name": "col:name"}),
    "publish":         ("trail_centerlines", {"name": "col:name"}),
}


def sql_str(value) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def sql_jsonb(obj) -> str:
    return sql_str(json.dumps(obj, ensure_ascii=False, sort_keys=True)) + "::jsonb"


def load_json(path: Path) -> dict:
    with open(path) as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# attrs merge helpers (the additive-preserve pattern, expressed in SQL)
# ---------------------------------------------------------------------------
# Both fold blocks build attrs in ONE jsonb expression with NO nesting of the
# running expression inside its own guards: Postgres evaluates every SET right-hand
# side against the OLD (pre-UPDATE) row, so each `original`-preserve guard reads the
# live `name`/`description`/`attrs` columns directly. We assemble `attrs` as:
#   COALESCE(attrs,'{}') merged with {original: <preserved>}  merged with facet sets.
# The `original` object is built from the OLD column values, only for fields not
# already stashed (idempotent: a re-run sees attrs.original.<field> present and
# keeps it via the `- 'already-present-keys'` removal below).

def original_merge_sql(fields: list[tuple[str, str, str]]) -> str:
    """jsonb expression merging {original:{...}} into COALESCE(attrs,'{}').
    `fields` = [(canonical_field_name, old_value_sql, present_test_sql), ...].
    For each field we add it to `original` ONLY when its old value exists AND it is
    not already stashed (so a re-run preserves the first-fold original, byte-stable).
    Returns a jsonb expression rooted on the live `attrs`."""
    # Build the new-original additions as a jsonb_build_object filtered per field.
    # jsonb_strip_nulls drops fields whose CASE yielded NULL (not-applicable / already
    # stashed), so the `||` merge adds only genuinely-new original keys.
    obj_parts = []
    for fld, old_sql, present in fields:
        obj_parts.append(
            f"'{fld}', CASE WHEN attrs #>> '{{original,{fld}}}' IS NULL AND ({present}) "
            f"THEN {old_sql} ELSE NULL END")
    new_original = f"jsonb_strip_nulls(jsonb_build_object({', '.join(obj_parts)}))"
    return (
        f"jsonb_set(COALESCE(attrs, '{{}}'::jsonb), '{{original}}', "
        f"COALESCE(attrs->'original','{{}}'::jsonb) || {new_original})"
    )


def canonical_attrs_set_sql(base_expr: str, pairs: list[tuple[str, str]]) -> str:
    """Write each (key -> value) into the canonical block INSIDE attrs, on top of
    base_expr. Reference layers (buildings/cemeteries/visitor/trails) are baked
    `properties = attrs` by export_publish_geojson.sh, so `attrs` carries the
    SERVED canonical block (attrs.name='1', attrs.description, attrs.difficulty was
    written by the import). The fold must update that served block too -- not just
    the spine columns -- or a bake from this row still emits the stand-in '1'. The
    pre-fold value is already stashed under attrs.original.<field> (additive). The
    spine COLUMN is set in the same UPDATE so the publish-gated bake arm (which reads
    the column) also emits the folded value: one fold, both homes, one original."""
    expr = base_expr
    for key, val in pairs:
        expr = f"jsonb_set({expr}, '{{{key}}}', to_jsonb({val}::text))"
    return expr


def trail_fold_block(number, name, description, difficulty) -> str:
    """One catalog trail -> an UPDATE on the matching trails row(s) by trail_number.
    name/description set only where the catalog HAS a value (never blank-coerce,
    never auto-name); difficulty folds into attrs.difficulty. The pre-fold column /
    attr value is stashed under attrs.original.<field> on first fold (guarded)."""
    set_cols = []
    preserve = []  # (field, old_value_sql, present_test)
    canon_attrs = []  # (attrs key, sql value) -- the served canonical block in attrs
    if name is not None and str(name).strip() != "":
        set_cols.append(f"name = {sql_str(name)}")
        preserve.append(("name", "to_jsonb(name)", "name IS NOT NULL"))
        canon_attrs.append(("name", sql_str(name)))
    if description is not None and str(description).strip() != "":
        set_cols.append(f"description = {sql_str(description)}")
        preserve.append(("description", "to_jsonb(description)", "description IS NOT NULL"))
        canon_attrs.append(("description", sql_str(description)))

    # attrs: original-preserve for any folded canonical field, then write the folded
    # values into the served canonical block (attrs.name/.description/.difficulty),
    # preserving the prior attrs.difficulty under original.difficulty.
    if difficulty is not None and str(difficulty).strip() != "":
        preserve.append(("difficulty", "attrs->'difficulty'", "attrs ? 'difficulty'"))
        canon_attrs.append(("difficulty", sql_str(difficulty)))
    attrs_expr = original_merge_sql(preserve) if preserve else "COALESCE(attrs, '{}'::jsonb)"
    attrs_expr = canonical_attrs_set_sql(attrs_expr, canon_attrs)

    if not set_cols and (difficulty is None or str(difficulty).strip() == ""):
        # Catalog entry with nothing foldable (name=null, no desc, no difficulty) ->
        # count the match for the report, write nothing.
        return (
            f"WITH up AS (\n"
            f"  SELECT source_key FROM core.features\n"
            f"  WHERE layer = 'trails' AND archived_at IS NULL\n"
            f"    AND attrs->>'trail_number' = {sql_str(number)}\n"
            f")\n"
            f"INSERT INTO _folded SELECT 'trail', {sql_str(number)}, count(*) FROM up;"
        )

    set_cols.append(f"attrs = {attrs_expr}")
    set_cols.append("last_verified = now()")
    return (
        f"WITH up AS (\n"
        f"  UPDATE core.features SET {', '.join(set_cols)}\n"
        f"  WHERE layer = 'trails' AND archived_at IS NULL\n"
        f"    AND attrs->>'trail_number' = {sql_str(number)}\n"
        f"  RETURNING source_key\n"
        f")\n"
        f"INSERT INTO _folded SELECT 'trail', {sql_str(number)}, count(*) FROM up;"
    )


def poi_fold_block(layer, match_pairs, blurb, revisit_note, tag) -> str:
    """One poi-index entry -> an UPDATE on the matching layer row(s). description set
    only where the entry HAS a blurb (a blurb=null entry folds only revisit_note);
    revisit_note folds into attrs.facets.revisit_note. The pre-fold description is
    stashed under attrs.original.description on first fold (guarded)."""
    where = [f"layer = {sql_str(layer)}", "archived_at IS NULL"]
    for key, accessor, val in match_pairs:
        if accessor.startswith("attr:"):
            where.append(f"attrs->>'{accessor[5:]}' = {sql_str(val)}")
        else:  # col:
            where.append(f"{accessor[4:]} = {sql_str(val)}")

    set_cols = []
    preserve = []
    canon_attrs = []
    if blurb is not None and str(blurb).strip() != "":
        set_cols.append(f"description = {sql_str(blurb)}")
        preserve.append(("description", "to_jsonb(description)", "description IS NOT NULL"))
        canon_attrs.append(("description", sql_str(blurb)))
    attrs_expr = original_merge_sql(preserve) if preserve else "COALESCE(attrs, '{}'::jsonb)"
    attrs_expr = canonical_attrs_set_sql(attrs_expr, canon_attrs)
    if revisit_note is not None and str(revisit_note).strip() != "":
        # revisit_note -> a Tier-3 facet (attrs.facets.revisit_note), additive.
        attrs_expr = (
            f"jsonb_set({attrs_expr}, '{{facets}}', "
            f"  COALESCE({attrs_expr}->'facets','{{}}'::jsonb) || "
            f"  jsonb_build_object('revisit_note', {sql_str(revisit_note)}::text))"
        )

    if not set_cols and (revisit_note is None or str(revisit_note).strip() == ""):
        # Nothing to fold (e.g. drawn_pois group, blurb=null + revisit_note=null).
        # Still count the match so the report is honest; no write.
        return (
            f"WITH up AS (\n"
            f"  SELECT source_key FROM core.features\n"
            f"  WHERE {' AND '.join(where)}\n"
            f")\n"
            f"INSERT INTO _folded SELECT 'poi-noop', {sql_str(tag)}, count(*) FROM up;"
        )

    set_cols.append(f"attrs = {attrs_expr}")
    set_cols.append("last_verified = now()")
    return (
        f"WITH up AS (\n"
        f"  UPDATE core.features SET {', '.join(set_cols)}\n"
        f"  WHERE {' AND '.join(where)}\n"
        f"  RETURNING source_key\n"
        f")\n"
        f"INSERT INTO _folded SELECT 'poi', {sql_str(tag)}, count(*) FROM up;"
    )


def build_sql(catalog: dict, poi_index: dict) -> tuple[str, list, list]:
    parts = ["BEGIN;",
             "CREATE TEMP TABLE _folded(kind text, tag text, matched bigint);"]

    trails = [t for t in catalog.get("trails", []) if t.get("number") is not None]
    for t in trails:
        parts.append(trail_fold_block(
            t["number"], t.get("name"), t.get("description"), t.get("difficulty")))

    poi_entries = poi_index.get("entries", [])
    for i, e in enumerate(poi_entries):
        m = e.get("match", {}) or {}
        src = m.get("source")
        binding = POI_GROUP_BINDING.get(src)
        tag = f"{src or '?'}:{i}"
        if binding is None:
            # No DB layer binding for this group (drawn_pois etc.) -- report, no write.
            parts.append(
                f"INSERT INTO _folded VALUES ('poi-unbound', {sql_str(tag)}, 0);")
            continue
        layer, key_accessors = binding
        match_pairs = []
        ok = True
        for key, accessor in key_accessors.items():
            if key not in m:
                ok = False
                break
            match_pairs.append((key, accessor, m[key]))
        if not ok:
            parts.append(
                f"INSERT INTO _folded VALUES ('poi-badmatch', {sql_str(tag)}, 0);")
            continue
        parts.append(poi_fold_block(
            layer, match_pairs, e.get("blurb"), e.get("revisit_note"), tag))

    # Per-row matched counts (read inside the txn, before COMMIT) so we can name
    # exactly which sidecar rows matched zero DB rows (reported, not dropped).
    parts.append(
        "SELECT 'ROW=' || kind || '|' || tag || '|' || matched FROM _folded ORDER BY kind, tag;")
    parts.append("SELECT 'TRAIL_MATCHED=' || COALESCE(sum(matched),0) FROM _folded WHERE kind='trail';")
    parts.append("SELECT 'POI_MATCHED=' || COALESCE(sum(matched),0) FROM _folded WHERE kind='poi';")
    parts.append("SELECT 'TOTAL_ROWS=' || count(*) FROM core.features;")
    parts.append("COMMIT;")
    return "\n".join(parts), trails, poi_entries


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

    catalog = load_json(TRAIL_CATALOG)
    poi_index = load_json(POI_INDEX)
    sql, trails, poi_entries = build_sql(catalog, poi_index)

    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("fold-sidecars: FAILED (psql error above; transaction rolled back)")
        return 1

    # Per-row report: every sidecar row, matched count -> name the unmatched ones.
    rows = [line[4:] for line in out.splitlines() if line.startswith("ROW=")]
    unmatched = []
    for r in rows:
        kind, tag, matched = r.split("|")
        if kind in ("trail", "poi") and int(matched) == 0:
            unmatched.append(f"{kind} {tag}")
        if kind in ("poi-noop", "poi-unbound", "poi-badmatch"):
            unmatched.append(f"{kind} {tag} ({matched} matched, nothing to fold)")

    trail_matched = parse_one(out, "TRAIL_MATCHED")
    poi_matched = parse_one(out, "POI_MATCHED")
    total = parse_one(out, "TOTAL_ROWS")

    print("== folded sidecars into core.features ==")
    print(f"  trail-catalog entries    : {len(trails)}  -> trail rows matched: {trail_matched}")
    print(f"  poi-index entries        : {len(poi_entries)} -> poi rows matched : {poi_matched}")
    print(f"  core.features total rows : {total}  (additive -- nothing dropped)")
    if unmatched:
        print("  REPORTED (unmatched / nothing-to-fold sidecar rows -- NOT dropped):")
        for u in unmatched:
            print(f"    - {u}")
    print("fold-sidecars: OK (matched rows updated; canonical name/description/difficulty"
          " folded; originals preserved under attrs.original; idempotent)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
