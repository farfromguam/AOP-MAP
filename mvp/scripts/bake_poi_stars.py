#!/usr/bin/env python3
"""Bake the POI ★ curation into the served data model.

The star (``properties.highlight``) is the "this is a destination worth listing"
flag. It used to live ONLY in the editor's localStorage (verified: 0 highlight=true
features in the served files except the one seed POI), so the read viewer could not
see it — the directory had to side-join aop_poi_index.json at runtime. The user's
call (2026-06-13): *"STARS. if it's not in the data model we need to add it."* So
the star becomes a published, source-traceable field ON the feature.

This script SEEDS that field from the git-tracked curation record
``website/data/aop_poi_index.json`` (the hand-maintained list of which places are
destinations, with their group + blurb). For each index entry it finds the matching
served feature and stamps:
  - ``highlight = true``                       (the ★)
  - ``description``  = the entry blurb          (only if the feature has none yet —
                                                 so trails, which had no description,
                                                 gain their curated copy)
  - ``revisit_note`` = the entry revisit_note   (drives the "info needed — revisit"
                                                 placeholder), when present

After this seed, the served ``highlight`` field is the source of truth the viewer
reads; the editor toggles it and bake_panel_overrides.py publishes it (the file sink
no longer strips highlight — see panel_overrides.SERVED_SKIP_KEYS; the DB sink still
skips it via VIEW_STATE_KEYS until core gets a highlight column).

Idempotent: re-running is a no-op once baked. Runs AFTER rebake_canonical.py (a
machine refresh from raw/ drops served edits), same as bake_panel_overrides.py.

NOTE: publish.geojson is PostGIS-exported (export_publish_geojson.sh); a star baked
here is overwritten on the next export. To make a publish-layer star durable it must
also be carried into the publish view. The file-based layers (buildings, visitor,
cemeteries, editor seed, trail network) are safe.

Usage:
  bake_poi_stars.py            # apply
  bake_poi_stars.py --dry-run  # show what would change, write nothing
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "website" / "data"
INDEX = DATA / "aop_poi_index.json"

# Each index `source` -> (served file, matcher(props, match) -> bool).
SOURCES = {
    "buildings": (
        "aop_buildings.geojson",
        lambda p, m: p.get("address") == m.get("address") or p.get("building_label") == m.get("address"),
    ),
    "visitor_context": (
        "aop_visitor_context_callouts.geojson",
        lambda p, m: p.get("name") == m.get("name"),
    ),
    "publish": (
        "publish.geojson",
        lambda p, m: p.get("layer") == m.get("layer") and p.get("name") == m.get("name"),
    ),
    "cemeteries": (
        "aop_cemeteries.geojson",
        lambda p, m: p.get("geom_role") == m.get("geom_role") and p.get("parcel_id") == m.get("parcel_id"),
    ),
    # match has no key -> star every drawn feature (the seed is the only one today).
    "editor_pois": ("aop_editor_seed_pois.geojson", lambda p, m: True),
}


def load(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def write_fc(path: Path, data: dict) -> None:
    # Match the canonical served format (minified, one line) so the git diff is the
    # changed bytes, not a reformat.
    with path.open("w") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="stamp the export's <file>.check side files instead of the served "
                         "files (so export_publish_geojson.sh --check sees the ★ as part of "
                         "the bake's fixed point). Files without a .check are skipped.")
    args = ap.parse_args()
    suffix = ".check" if args.check else ""

    index = load(INDEX)
    entries = index.get("entries", [])
    # Group entries by their served file so each file is loaded/written once.
    by_file: dict[str, list] = {}
    unknown = []
    for entry in entries:
        match = entry.get("match") or {}
        src = match.get("source")
        spec = SOURCES.get(src)
        if not spec:
            unknown.append(src)
            continue
        by_file.setdefault(spec[0], []).append((entry, match, spec[1]))

    total_changes = 0
    for fname, items in by_file.items():
        path = DATA / (fname + suffix)
        if not path.exists():
            # In --check the export only wrote .check side files for its own arms;
            # a source with no side file (e.g. the editor seed) is simply skipped.
            if not args.check:
                print(f"  SKIP {fname}: not found")
            continue
        fc = load(path)
        feats = fc.get("features", [])
        file_changes = 0
        for entry, match, matcher in items:
            hits = [f for f in feats if matcher(f.get("properties") or {}, match)]
            if not hits:
                print(f"  MISS {fname}: no feature for {match}")
                continue
            for f in hits:
                p = f.setdefault("properties", {})
                changed = []
                if p.get("highlight") is not True:
                    p["highlight"] = True
                    changed.append("highlight")
                blurb = (entry.get("blurb") or "").strip()
                if blurb and not (str(p.get("description") or "").strip()):
                    p["description"] = blurb
                    changed.append("description")
                rev = (entry.get("revisit_note") or "")
                if rev and not p.get("revisit_note"):
                    p["revisit_note"] = rev
                    changed.append("revisit_note")
                if changed:
                    file_changes += 1
                    name = p.get("name") or p.get("building_label") or p.get("facility_name") or "(unnamed)"
                    print(f"  ★ {fname}: {name} +{','.join(changed)}")
        if file_changes and not args.dry_run:
            write_fc(path, fc)
        total_changes += file_changes

    if unknown:
        print(f"  (skipped entries with unknown source: {sorted(set(unknown))})")
    verb = "would change" if args.dry_run else "changed"
    print(f"\n{total_changes} feature(s) {verb}." + (" (dry run, nothing written)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
