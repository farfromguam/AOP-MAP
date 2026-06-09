#!/usr/bin/env python3
"""F2 (gold slice 6) — the drawn-POI DB door: aop_editor_pois_v1 -> core.features (layer='poi').

A hand-drawn POI lives in the editor's own store (`aop_editor_pois_v1`) — rendered on the
map and fed to the left collector — but had NO direct writer to `core.features` (spike audit
F2, `brain/output/council/spike_code_dbfirst_audit_20260608.md`). It reached core only via the
RIGHT panel's opt-in `created[]` export, so a drawn POI that never went through that panel
vanished on a browser reset and never published. This door makes `core.features (layer='poi')`
the store of record for drawn POIs — the C3 demotion gold slice 6 calls for.

  draw a POI (editor) -> "Copy all as GeoJSON"  (the aop_editor_pois_v1 FeatureCollection)
    -> apply_editor_pois_to_core.py <fc.json>     (THIS script)
    -> export_publish_geojson.sh                  (bake: POIs from publish.features WHERE layer='poi')
    -> deploy

REUSE (Quartermaster — ONE sink, two input shapes). This is a thin INPUT ADAPTER, not a second
apply path: it maps each drawn-POI feature to the panel-overrides `created[]` shape
(`_src='editorPois'`, so the `source_key` becomes `editorPois:<id>` — the same convention the
seed rows use, e.g. `editorPois:aop-pavilion`) and feeds the SAME
`apply_panel_overrides_to_core` machinery (`build_sql`/`run_psql`). The upsert-fold-archive,
the `source_register` provenance, and the no-drop / no-throw / no-silent-zero-row guarantees are
all INHERITED, never re-implemented. No second upsert path, no second store of record.

No-limiting code (C5 / the gold loop contract):
  * Every drawn POI UPSERTs `ON CONFLICT (source_key)` — idempotent (re-applying the same export
    updates the same row, never duplicates), never drops a row, never throws.
  * Safe defaults: a drawn POI is NOT publishable unless its own properties carry
    `permission='publish'` AND `publish_status='publish'` (the publish view is the only gate).
    A freshly drawn POI defaults to `permission='AOP first-party'` / `publish_status='candidate'`
    (NOT served) — curation through the editor is what promotes it.
  * Geometry is never a throw or a drop (R13): the shared `created_block` geom builder is
    point-tuned (a POI is a point), so a drawn FOOTPRINT/TRACE (polygon/line) upserts as a row
    but lands geom-less (a general geom builder is a follow-up, F1/F6 territory; the POI
    acceptance is points). A null / partial / unparseable geometry (a feature mid-draw, a
    non-geographic POI) ALSO upserts geom-less rather than crashing the batch — `safe_geometry`
    (panel_overrides.py) guards `build_created_feature` so nothing throws and nothing is dropped.

Usage:
  apply_editor_pois_to_core.py aop_editor_pois.geojson
  pbpaste | apply_editor_pois_to_core.py -          # the editor's "Copy all as GeoJSON" clipboard
  apply_editor_pois_to_core.py fc.json --dry-run    # print the SQL; run nothing
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from apply_panel_overrides_to_core import build_sql, run_psql, parse_count


def read_features(arg: str) -> list:
    """Read the drawn-POI features from a path or '-' (stdin). Permissive (C5): accepts
    a FeatureCollection ({features:[...]}, the "Copy all as GeoJSON" output), a bare
    features list, or the raw `aop_editor_pois_v1` array. A non-matching shape yields []
    (nothing to apply) — never an error."""
    raw = json.load(sys.stdin) if arg == "-" else json.loads(Path(arg).read_text())
    if isinstance(raw, dict) and isinstance(raw.get("features"), list):
        return raw["features"]
    if isinstance(raw, list):
        return raw
    return []


def to_created(feat: dict) -> dict:
    """Map one drawn-POI feature -> the panel-overrides `created[]` raw shape. `_src`
    namespaces the source_key to `editorPois:<id>` (the seed convention); the drawn
    store carries the canonical id in `properties.id`, which created_block reads."""
    props = dict((feat or {}).get("properties") or {})
    props["_src"] = "editorPois"
    return {"geometry": (feat or {}).get("geometry"), "properties": props}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Drawn-POI FeatureCollection / aop_editor_pois_v1 export, or '-' for stdin")
    ap.add_argument("--dry-run", action="store_true", help="Print the SQL; run nothing")
    args = ap.parse_args()

    feats = read_features(args.input)
    payload = {"edits": {}, "created": [to_created(f) for f in feats], "deleted": []}
    sql, _n_edits, n_created, _n_deleted = build_sql(payload)

    if args.dry_run:
        print(sql)
        return 0

    out = run_psql(sql)
    if not out:
        print("apply-editor-pois: FAILED (psql error above; transaction rolled back)")
        return 1

    created = parse_count(out, "CREATED_UPSERTED")
    total = parse_count(out, "POIS_TOTAL")
    active = parse_count(out, "POIS_ACTIVE")

    print("== applied drawn POIs to core.features (layer='poi') ==")
    print(f"  drawn POIs in input: {len(feats)}")
    print(f"  upserted into core.features (source_key editorPois:<id>): {created} / {n_created}")
    print(f"  core.features(poi) total: {total}  active(not archived): {active}")

    # No silent zero-row write: every input feature must have upserted exactly one row
    # (ON CONFLICT (source_key) guarantees insert-or-update). A shortfall = a silent
    # zero-row write, the failure mode a bare UPDATE hides.
    if created != n_created:
        print("apply-editor-pois: FAIL -- upserted count != input count (a silent zero-row write)")
        return 1
    print("apply-editor-pois: OK (drawn POIs are now in the DB store of record; nothing dropped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
