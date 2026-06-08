#!/usr/bin/env python3
"""Apply reference-layer ★ (positioned-features `highlight`) into core.features.attrs.

Sprint 08 Slice A (brain/tasks/08_data_normalization/star_driven_poi_normalization.md):
the AUTHOR->STORE door for the four REFERENCE layers' star, so a curated ★ on a
building / cemetery / visitor callout / trail lands DURABLY in core.features and
bakes into the served artifact instead of living only in one browser's
localStorage.

  star in the editor -> "Export all" (aop-viewer-preset-settings-v3 bundle)
    -> apply_positioned_features_to_core.py <bundle.json>   (THIS script)
    -> export_publish_geojson.sh   (bake: emits attrs verbatim, so highlight rides)
    -> deploy

Why a NEW sibling script (not apply_panel_overrides_to_core.py): the reference ★
lives in a DIFFERENT store. `toggleFeatureHighlight` -> `savePositionedFeature`
writes `{highlight}` keyed `${layerKey}:${idField}` into `aop_positioned_features_v1`
(main.js:2982), round-tripped by the "Export all" bundle's `positioned_features`
map. apply_panel_overrides_to_core.py reads the panel-OVERRIDES export shape
(edits{}/created[]/deleted[]) and its VIEW_STATE_KEYS *strips* `highlight` -- the
one field this slice exists to carry. So that script is the wrong sink.

REUSE (do not re-implement -- the card's reuse line):
  * `split_key` from panel_overrides.py (the one "<layerKey>:<id>" splitter).
  * the `_applied` temp-table + count-back scaffold and `sql_str`/`run_psql`/
    `parse_count` from apply_panel_overrides_to_core.py.
NOT reused: that module's `read_payload` (parses the override shape, not the
positioned_features map) and `VIEW_STATE_KEYS` (strips `highlight`).

No-limiting code (C5 / gold's store-first discipline):
  * Curation/star axis ONLY. This sink writes `attrs.highlight` and nothing else.
    Geometry / icon_size overrides stay with the legacy file-baker
    (export_positioned_features.py) -- this script never touches them.
  * `attrs.highlight` is the SINGLE source of truth. The `is_destination` column
    is NOT written (the reference bake reads `attrs` verbatim and reads
    `is_destination` nowhere for these four layers -- a column write would have no
    consumer and drift).
  * An unresolved editor key (an orphan/stale key that matches no core row) is
    REPORTED loudly, never thrown on and never silently dropped. Resolution runs
    in the WHERE clause and every matched core row is recorded in `_applied`, so a
    zero-match is visible (the key prints under "unresolved"), not a silent no-op.
  * UPDATE-only: these reference rows ALWAYS pre-exist (gold migrated them). There
    is no stub to INSERT for an unmatched key (unlike the POI door), so this resolves
    to a source_key and UPDATEs it; the no-silent-zero-row guarantee is met by the
    `_applied` count-back + the unresolved report, not by an INSERT...ON CONFLICT arm.

Editor-layerKey -> core resolution (grounded 2026-06-08 against the live rows):
  buildings:<build_id>           -> source_key = the editor key (direct)
  cemeteries:<parcel_id>         -> attrs.parcel_id == <parcel_id> AND geom_role='marker'
  visitorContext:<name>          -> core layer 'visitor', coalesce(attrs.name,attrs.label)
                                    == <name>, kind <> 'brand_logo' (decision #3)
  trails:n:<num>                 -> attrs.trail_number == <num>
  trails:name:<name>             -> attrs.name == <name>
(brandLogos / editorPois are intentionally NOT carried here -- brand logos are
excluded by decision #3, and editorPois has its own DB door.)

Usage:
  apply_positioned_features_to_core.py aop-viewer-preset-settings.json
  pbpaste | apply_positioned_features_to_core.py -
  apply_positioned_features_to_core.py bundle.json --dry-run   # print SQL, run nothing
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from panel_overrides import split_key
from apply_panel_overrides_to_core import sql_str, run_psql, parse_count

# The four reference editor-layerKeys this sink carries, mapped to their core
# `layer` value. visitorContext -> 'visitor' (the gold-migration layer name).
LAYERKEY_TO_CORE_LAYER = {
    "buildings": "buildings",
    "cemeteries": "cemeteries",
    "visitorContext": "visitor",
    "trails": "trails",
}


def read_positioned_features(arg: str) -> dict:
    """Read the positioned_features map from a path or '-' (stdin). Permissive
    (C5): a non-object yields {} (nothing to apply); accepts either the full
    `aop-viewer-preset-settings-v3` bundle (carries `.positioned_features`) or a
    bare `${layerKey}:${id} -> {highlight,...}` slice."""
    raw = json.load(sys.stdin) if arg == "-" else json.loads(Path(arg).read_text())
    if not isinstance(raw, dict):
        return {}
    pf = raw.get("positioned_features")
    if isinstance(pf, dict):
        return pf
    return raw  # already a bare positioned_features map


def highlight_set_sql(value: bool) -> str:
    """SET clause for the resolved row. Mirrors applyPositionedFeatures (main.js
    :3021): write the flag when the store has an opinion (true OR false) so an
    un-star survives. Shallow jsonb `||` merge -- only `highlight` is touched,
    sibling attrs are preserved."""
    literal = "true" if value else "false"
    return (
        "SET attrs = coalesce(f.attrs, '{}'::jsonb) || "
        f"'{{\"highlight\":{literal}}}'::jsonb"
    )


def resolve_where(layerkey: str, fid: str) -> str | None:
    """The per-layer resolution predicate (Grounding #4). Returns None for an id
    shape we cannot resolve (e.g. a trail key with no n:/name: prefix) -- the
    caller reports it as unresolved, never throws."""
    core_layer = LAYERKEY_TO_CORE_LAYER[layerkey]
    base = f"f.layer = {sql_str(core_layer)}"
    if layerkey == "buildings":
        # editor key == core source_key (build_id == the key suffix).
        return f"{base} AND f.source_key = {sql_str(f'buildings:{fid}')}"
    if layerkey == "cemeteries":
        # the LIST surfaces the marker row (listPredicate geom_role==='marker').
        return (f"{base} AND f.attrs->>'parcel_id' = {sql_str(fid)} "
                f"AND f.attrs->>'geom_role' = 'marker'")
    if layerkey == "visitorContext":
        # the source_key '-N' suffix is a synthetic load index, not the name --
        # match on name (fall back to label); exclude brand logos (decision #3).
        return (f"{base} AND coalesce(f.attrs->>'name', f.attrs->>'label') = {sql_str(fid)} "
                f"AND coalesce(f.attrs->>'kind', '') <> 'brand_logo'")
    if layerkey == "trails":
        # `__trail_row_id` is `n:<num>` or `name:<name>` (main.js:9081). The
        # sfwda-<n> source_key suffix is a load index, NOT the trail number --
        # join on attrs.trail_number / attrs.name instead.
        kind, _, val = fid.partition(":")
        if kind == "n" and val != "":
            return f"{base} AND f.attrs->>'trail_number' = {sql_str(val)}"
        if kind == "name" and val != "":
            return f"{base} AND f.attrs->>'name' = {sql_str(val)}"
        return None  # unresolvable trail id shape -> reported, not thrown on
    return None


def entry_block(layerkey: str, fid: str, editor_key: str, highlight: bool) -> str | None:
    """One starred/un-starred entry -> resolve in the WHERE and UPDATE attrs.highlight,
    recording every matched core row in `_applied` so a zero-match is visible."""
    where = resolve_where(layerkey, fid)
    if where is None:
        return None
    return (
        "WITH up AS (\n"
        f"  UPDATE core.features f\n"
        f"  {highlight_set_sql(highlight)}\n"
        f"  WHERE {where}\n"
        f"  RETURNING f.source_key\n"
        ")\n"
        f"INSERT INTO _applied SELECT {sql_str(layerkey)}, {sql_str(editor_key)}, source_key FROM up;"
    )


def build_sql(pf: dict) -> tuple[str, list[str], list[str]]:
    """Returns (sql, in_scope_keys, unresolvable_keys). in_scope_keys = editor keys
    for the four reference layers that carry a `highlight` opinion; unresolvable =
    those whose id shape resolved to no predicate (reported, never thrown)."""
    parts: list[str] = ["BEGIN;"]
    parts.append("CREATE TEMP TABLE _applied(layerkey text, editor_key text, source_key text);")

    in_scope: list[str] = []
    unresolvable: list[str] = []
    for key, entry in pf.items():
        layerkey, fid = split_key(key)
        if layerkey not in LAYERKEY_TO_CORE_LAYER:
            continue  # not a reference layer (editorPois/brandLogos/parcels/...) -- skip
        if not isinstance(entry, dict) or "highlight" not in entry:
            continue  # no star opinion (e.g. a geometry-only override) -- not ours
        highlight = entry.get("highlight") is True
        block = entry_block(layerkey, fid, key, highlight)
        if block is None:
            unresolvable.append(key)
            continue
        in_scope.append(key)
        parts.append(block)

    # Machine-readable summary, read inside the txn before COMMIT.
    parts.append("SELECT 'APPLIED_ROWS=' || count(*) FROM _applied;")
    parts.append("SELECT 'APPLIED_KEYS=' || count(DISTINCT editor_key) FROM _applied;")
    parts.append("SELECT 'APPLIEDKEY=' || editor_key FROM (SELECT DISTINCT editor_key FROM _applied) s;")
    parts.append(
        "SELECT 'STARRED_TOTAL=' || count(*) FROM core.features "
        "WHERE layer IN ('buildings','cemeteries','visitor','trails') "
        "AND attrs->>'highlight' = 'true';"
    )
    parts.append("COMMIT;")
    return "\n".join(parts), in_scope, unresolvable


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Exported aop-viewer-preset-settings-v3 bundle (or a bare positioned_features map), or '-' for stdin")
    ap.add_argument("--dry-run", action="store_true", help="Print the SQL; run nothing")
    args = ap.parse_args()

    pf = read_positioned_features(args.input)
    sql, in_scope, unresolvable = build_sql(pf)

    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("apply-positioned-features: FAILED (psql error above; transaction rolled back)")
        return 1

    applied_rows = parse_count(out, "APPLIED_ROWS")
    applied_keys = parse_count(out, "APPLIED_KEYS")
    starred_total = parse_count(out, "STARRED_TOTAL")
    applied_set = {line.split("=", 1)[1] for line in out.splitlines() if line.startswith("APPLIEDKEY=")}
    # An in-scope key that resolved to no core row is unresolved (an orphan/stale
    # key) -- reported, never silently dropped (C5).
    unresolved = [k for k in in_scope if k not in applied_set] + unresolvable

    print("== applied reference-layer ★ to core.features.attrs.highlight ==")
    print(f"  in-scope star entries (4 reference layers): {len(in_scope) + len(unresolvable)}")
    print(f"  resolved keys: {applied_keys}   matched core rows: {applied_rows}")
    print(f"  core reference features now starred (attrs.highlight=true): {starred_total}")
    if unresolved:
        print(f"  UNRESOLVED (flagged, not applied -- no matching core row): {len(unresolved)}")
        for k in unresolved:
            print(f"    - {k}")

    # No silent zero-row write: every in-scope, resolvable key must have matched a
    # core row. A shortfall means a resolution predicate is wrong -- surfaced, not hidden.
    ok = all(k in applied_set for k in in_scope)
    if not ok:
        print("apply-positioned-features: NOTE -- some in-scope keys matched no core row (see UNRESOLVED).")
    print("apply-positioned-features: OK (attrs.highlight set on resolved rows; nothing dropped or thrown).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
