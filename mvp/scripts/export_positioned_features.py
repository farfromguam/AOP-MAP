#!/usr/bin/env python3
"""Bake positioned brand-logo and visitor-context overrides into the seed GeoJSON.

Brand logos and visitor-context callouts both live in
`website/data/aop_visitor_context_callouts.geojson` (the brand logos were merged
in 2026-06-05 as kind=brand_logo point features) -- a file-based layer the static
viewer loads directly. It is NOT in PostGIS, so `export_publish_geojson.sh` never
touches it. Both override prefixes (brandLogos:<logo_id>, visitorContext:<name>)
bake into that one file, which is written minified to match its on-disk format.

When an editor drags or resizes one of these in the viewer, the new position is
written only to localStorage (`aop_positioned_features_v1`). A data reset /
"Reset viewer" wipes that store, so the features snap back to their seed
coordinates and the editor's placement work is lost.

This script closes that loop: it bakes the editor's overrides back into the seed
files on disk, so the updated locations survive a reset (the "won't lose
positions on data reset" requirement from tasks/04_event_app/misc_4.md).

Input is whatever the viewer's right-panel export produced:
  - "Export all"      -> schema `aop-viewer-preset-settings-v3` (key
                          `positioned_features`)
  - section "Copy"    -> schema `aop-section-state-v2` (key `positionedFeatures`)
  - or a bare object   mapping "<layer>:<id>" -> { geometry, icon_size, ... }

Only `geometry` (and `icon_size` for brand logos) is baked. Runtime-only flags
(`highlight`, `locked`) are session state, not authored data, and are ignored.

Usage:
  export_positioned_features.py overrides.json
  pbpaste | export_positioned_features.py -            # read from stdin
  export_positioned_features.py overrides.json --dry-run

Run order in the position-editing loop:
  drag/resize in the viewer -> right panel "Export all" (or section Copy)
  -> save the JSON -> export_positioned_features.py <that file> -> commit the
  two changed geojson files.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = REPO / "website" / "data"

# Coordinates in the seed files are stored to 5 decimals (~1.1 m). Match that so
# baked diffs stay clean and don't churn on full-precision browser geometry.
COORD_DECIMALS = 5

# layer override-key prefix -> (seed file, idField, bake icon_size?)
LAYERS = {
    # Brand logos + visitor-context callouts share one minified file (logos were
    # merged in 2026-06-05 as kind=brand_logo points). Both specs target it;
    # bake_layer reloads from disk per layer, so the two sequential writes don't
    # clobber each other. Written minified to match the served file's format.
    "brandLogos": {
        "file": DATA_DIR / "aop_visitor_context_callouts.geojson",
        "id_field": "logo_id",
        "bake_icon_size": True,
        "minify": True,
    },
    "visitorContext": {
        "file": DATA_DIR / "aop_visitor_context_callouts.geojson",
        "id_field": "name",
        "bake_icon_size": False,
        "minify": True,
    },
    # Curated park buildings (derived layer). Footprints are drag-adjustable in
    # the viewer because FEMA's polygons sit a little off; this bakes the moved
    # geometry back, keyed by build_id. The file is written by
    # import_fema_buildings.py with indent=1, so match that to keep diffs clean.
    "buildings": {
        "file": DATA_DIR / "aop_buildings.geojson",
        "id_field": "build_id",
        "bake_icon_size": False,
        "indent": 1,
    },
}


def load_json(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def read_input(arg: str) -> dict:
    if arg == "-":
        return json.load(sys.stdin)
    return load_json(Path(arg))


def extract_overrides(payload: dict) -> dict:
    """Pull the {"layer:id": {...}} map out of whatever export shape we got."""
    if not isinstance(payload, dict):
        raise SystemExit("Input JSON must be an object")
    for key in ("positioned_features", "positionedFeatures"):
        if isinstance(payload.get(key), dict):
            return payload[key]
    # Bare map fallback: looks like override keys ("<prefix>:<id>") at top level.
    if any(isinstance(k, str) and ":" in k for k in payload):
        return payload
    raise SystemExit(
        "No positioned-features found. Expected a 'positioned_features' / "
        "'positionedFeatures' key, or a bare '<layer>:<id>' map."
    )


def round_coords(coords):
    if isinstance(coords, (int, float)):
        return round(coords, COORD_DECIMALS)
    return [round_coords(c) for c in coords]


def geom_equal(a: dict, b: dict) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def bake_layer(prefix: str, spec: dict, overrides: dict, dry_run: bool) -> dict:
    path = spec["file"]
    id_field = spec["id_field"]
    if not path.exists():
        return {"file": path.name, "moved": 0, "resized": 0, "missing_seed": True}

    data = load_json(path)
    moved = 0
    resized = 0
    seen_ids = set()

    for feat in data.get("features", []):
        props = feat.get("properties", {}) or {}
        fid = props.get(id_field)
        if fid is None:
            continue
        seen_ids.add(str(fid))
        ov = overrides.get(f"{prefix}:{fid}")
        if not isinstance(ov, dict):
            continue

        geom = ov.get("geometry")
        if isinstance(geom, dict) and geom.get("coordinates") is not None:
            new_geom = {
                "type": geom["type"],
                "coordinates": round_coords(geom["coordinates"]),
            }
            if not geom_equal(feat.get("geometry", {}), new_geom):
                feat["geometry"] = new_geom
                moved += 1

        if spec["bake_icon_size"] and "icon_size" in ov:
            new_size = ov["icon_size"]
            if props.get("icon_size") != new_size:
                props["icon_size"] = new_size
                resized += 1
        feat["properties"] = props

    # Warn about overrides that name an id this seed file doesn't contain.
    orphans = sorted(
        k.split(":", 1)[1]
        for k in overrides
        if k.startswith(f"{prefix}:") and k.split(":", 1)[1] not in seen_ids
    )

    changed = moved + resized > 0
    if changed and not dry_run:
        meta = data.get("metadata")
        if isinstance(meta, dict):
            meta["generated"] = date.today().isoformat()
        with path.open("w") as fh:
            if spec.get("minify"):
                json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
            else:
                json.dump(data, fh, indent=spec.get("indent", 2), ensure_ascii=False)
                fh.write("\n")

    return {
        "file": path.name,
        "moved": moved,
        "resized": resized,
        "orphans": orphans,
        "changed": changed,
        "missing_seed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "input",
        help="Exported override JSON file, or '-' to read from stdin",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would change without writing the seed files",
    )
    args = ap.parse_args()

    overrides = extract_overrides(read_input(args.input))

    total_changes = 0
    for prefix, spec in LAYERS.items():
        result = bake_layer(prefix, spec, overrides, args.dry_run)
        if result.get("missing_seed"):
            print(f"  ! {result['file']}: seed file not found, skipped")
            continue
        verb = "would bake" if args.dry_run else "baked"
        print(
            f"  {result['file']}: {verb} "
            f"{result['moved']} moved, {result['resized']} resized"
        )
        for orphan in result.get("orphans", []):
            print(f"      (override for unknown {prefix} id, ignored: {orphan!r})")
        total_changes += result["moved"] + result["resized"]

    if total_changes == 0:
        print("No positioned-feature changes to bake.")
    elif args.dry_run:
        print(f"Dry run: {total_changes} change(s) NOT written.")
    else:
        print(f"Done: baked {total_changes} change(s). Commit the changed geojson.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
