#!/usr/bin/env python3
"""Re-bake right-panel editor edits back into the served GeoJSON.

There is no DB in prod -- every value the viewer shows is served from a static
GeoJSON file in website/data/. The right-panel editor (website/js/panel.js)
saves edits to localStorage as DIFFS and exports them as one JSON payload
(schema `aop-panel-overrides-v1`). This script is the other half of that loop:
it merges those diffs back into the on-disk GeoJSON so the edits become committed
authored data.

    edit in the panel -> "Export edits" (downloads aop_panel_overrides.json)
      -> bake_panel_overrides.py aop_panel_overrides.json
      -> review the git diff, commit -> in the panel hit "Clear"

DIFFS, not full-file replace (user decision 2026-06-04): the payload carries only
what changed, keyed "<source>:<canonical id>", so the git diff stays small and
the raw->core->publish zones survive. See brain/research/common_feature_schema.md
(the save-path section).

What it does, per the payload:
  - edits[]   : find the feature by canonical `properties.id` in its source file,
                apply the changed identity/facet props (name/description/
                difficulty/notes/category) and any moved geometry. View state
                (`highlight`) is NOT baked -- a star is not a fact about the
                feature. `last_checked` is stamped to today (an edit IS a check).
  - created[] : drawn features -> appended to the file of their HOME source.
                Each created feature carries `_src` (the layer it was drawn into),
                so a building drawn in the panel bakes into aop_buildings.geojson
                and a plain draw into aop_user_features.geojson (the default when
                `_src` is absent). `_id` promoted to canonical `id`, panel-internal
                keys dropped, editor provenance stamped. Replace-by-id so
                re-running the same export never duplicates.
  - deleted[] : remove the named features from their source file (logged loudly).

Idempotent: re-running the same payload is a no-op once baked.

IMPORTANT interaction with rebake_canonical.py: that script re-bakes the served
files FROM website/data/raw/ (pristine upstream), so running it AFTER this would
discard these panel edits. Order is: rebake_canonical.py first (machine refresh),
THEN bake_panel_overrides.py (human curation on top). Drawn features bake to their
OWN file, which rebake_canonical.py never touches, so draws are always safe.

Usage:
  bake_panel_overrides.py aop_panel_overrides.json
  pbpaste | bake_panel_overrides.py -            # read the export from stdin
  bake_panel_overrides.py aop_panel_overrides.json --dry-run
  bake_panel_overrides.py aop_panel_overrides.json --no-stamp   # don't touch last_checked
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

# One parser, two sinks: the schema/normalize contract lives in panel_overrides;
# this file is the FILE sink, apply_panel_overrides_to_core.py is the DB sink.
from panel_overrides import (
    DEFAULT_CREATED_TARGET,
    VIEW_STATE_KEYS,
    load_json,
    read_payload,
    round_coords,
    dumps_geom,
    feature_by_id,
    build_created_feature,
)

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = REPO / "website" / "data"


def write_fc(path: Path, data: dict) -> None:
    # Match the canonical served format exactly (rebake_canonical.py writes every
    # feature collection minified: compact separators, one line, no trailing
    # newline). Writing the same way keeps a bake's git diff to the changed bytes
    # instead of reformatting the whole file from minified to pretty-printed.
    meta = data.get("metadata")
    if isinstance(meta, dict):
        meta["generated"] = date.today().isoformat()
    with path.open("w") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))


def bake_edits(payload: dict, stamp: bool, today: str):
    """Apply edits[] grouped by file. Returns (per_file_changes, warnings)."""
    sources = payload.get("sources") or {}
    edits = payload.get("edits") or {}
    by_file: dict[str, list] = {}
    warnings: list[str] = []
    for key, entry in edits.items():
        src = entry.get("source")
        fname = sources.get(src)
        if not fname:
            warnings.append(f"edit {key}: source {src!r} has no file in payload.sources -- skipped")
            continue
        by_file.setdefault(fname, []).append(entry)
    return by_file, warnings


def apply_file_edits(path: Path, entries: list, stamp: bool, today: str, dry: bool):
    data = load_json(path)
    feats = data.get("features", [])
    changed_props = changed_geom = missing = 0
    for entry in entries:
        feat = feature_by_id(feats, entry.get("id"))
        if feat is None:
            missing += 1
            continue
        props = feat.setdefault("properties", {})
        # identity / facet props (skip view state + id)
        patch = entry.get("properties") or {}
        touched = False
        for k, v in patch.items():
            if k in VIEW_STATE_KEYS or k == "id":
                continue
            if props.get(k) != v:
                props[k] = v
                touched = True
        # moved geometry
        geom = entry.get("geometry")
        if isinstance(geom, dict) and geom.get("coordinates") is not None:
            new_geom = {"type": geom["type"], "coordinates": round_coords(geom["coordinates"])}
            if dumps_geom(feat.get("geometry")) != dumps_geom(new_geom):
                feat["geometry"] = new_geom
                changed_geom += 1
                touched = True
        if touched:
            changed_props += 1
            if stamp:
                props["last_checked"] = today
    if (changed_props or changed_geom) and not dry:
        write_fc(path, data)
    return {"file": path.name, "edited": changed_props, "moved": changed_geom, "missing": missing}


def created_target_file(props: dict, sources: dict, default_file: str) -> str:
    """A created feature carries `_src` (its home source); route it to that
    source's file. Drawn features (source userFeatures) and any legacy feature
    without `_src` fall back to the default created target."""
    src = props.get("_src")
    if src and sources.get(src):
        return sources[src]
    return default_file


def bake_created(payload: dict, today: str, dry: bool):
    """Append/replace each drawn feature into ITS layer's file (source-aware).
    A building drawn in the panel bakes into aop_buildings.geojson; a plain draw
    into aop_user_features.geojson. Returns a per-file result list."""
    created = payload.get("created") or []
    sources = payload.get("sources") or {}
    default_file = payload.get("created_target") or DEFAULT_CREATED_TARGET
    by_file: dict[str, list] = {}
    for raw in created:
        fname = created_target_file(raw.get("properties") or {}, sources, default_file)
        by_file.setdefault(fname, []).append(raw)

    results = []
    for fname, raws in by_file.items():
        path = DATA_DIR / fname
        existed = path.exists()
        if existed:
            data = load_json(path)
        else:
            data = {"type": "FeatureCollection",
                    "metadata": {"name": "AOP user-drawn features",
                                 "source": "AOP editor (drawn)", "confidence": "observed",
                                 "permission": "AOP first-party", "status": "core"},
                    "features": []}
        feats = data.setdefault("features", [])
        added = replaced = 0
        for raw in raws:
            feature = build_created_feature(raw, today)
            if feature is None:
                continue
            canonical_id = feature["properties"]["id"]
            existing = feature_by_id(feats, canonical_id)
            if existing is not None:
                if json.dumps(existing, sort_keys=True) == json.dumps(feature, sort_keys=True):
                    continue                  # already baked, identical -> true no-op
                feats[feats.index(existing)] = feature
                replaced += 1
            else:
                feats.append(feature)
                added += 1
        if (added or replaced) and not dry:
            write_fc(path, data)
        results.append({"file": fname, "added": added, "replaced": replaced})
    return results


def bake_deletes(payload: dict, dry: bool):
    sources = payload.get("sources") or {}
    deleted = payload.get("deleted") or []
    by_file: dict[str, list] = {}
    warnings: list[str] = []
    for key in deleted:
        src, _, fid = key.partition(":")
        fname = sources.get(src)
        if not fname:
            warnings.append(f"delete {key}: source {src!r} has no file -- skipped")
            continue
        by_file.setdefault(fname, []).append(fid)
    results = []
    for fname, ids in by_file.items():
        path = DATA_DIR / fname
        if not path.exists():
            continue
        data = load_json(path)
        feats = data.get("features", [])
        keep = [f for f in feats if str((f.get("properties") or {}).get("id")) not in set(map(str, ids))]
        removed = len(feats) - len(keep)
        if removed and not dry:
            data["features"] = keep
            write_fc(path, data)
        results.append({"file": fname, "removed": removed})
    return results, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Exported aop_panel_overrides.json, or '-' for stdin")
    ap.add_argument("--dry-run", action="store_true", help="Report what would change; write nothing")
    ap.add_argument("--no-stamp", action="store_true", help="Do not stamp last_checked on edited features")
    args = ap.parse_args()

    payload = read_payload(args.input)
    today = date.today().isoformat()
    dry = args.dry_run

    by_file, warn_edits = bake_edits(payload, not args.no_stamp, today)
    edit_results = [apply_file_edits(DATA_DIR / fname, entries, not args.no_stamp, today, dry)
                    for fname, entries in by_file.items()]
    created_results = bake_created(payload, today, dry)
    delete_results, warn_dels = bake_deletes(payload, dry)

    verb = "would bake" if dry else "baked"
    total = 0
    print(f"== {verb} panel overrides ==")
    for r in edit_results:
        print(f"  {r['file']}: {r['edited']} edited, {r['moved']} moved"
              + (f"  (! {r['missing']} id(s) not found)" if r["missing"] else ""))
        total += r["edited"]
    for cr in created_results:
        if cr["added"] or cr["replaced"]:
            print(f"  {cr['file']}: {cr['added']} added, {cr['replaced']} replaced (drawn)")
            total += cr["added"] + cr["replaced"]
    for r in delete_results:
        if r["removed"]:
            print(f"  {r['file']}: {r['removed']} DELETED")
            total += r["removed"]
    for w in warn_edits + warn_dels:
        print(f"  ! {w}")

    if total == 0:
        print("Nothing to bake (already up to date).")
    elif dry:
        print(f"Dry run: {total} change(s) NOT written.")
    else:
        print(f"Done: {total} change(s) written. Review the git diff, commit, "
              "then hit 'Clear' in the panel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
