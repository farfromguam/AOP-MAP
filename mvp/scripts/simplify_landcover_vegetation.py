#!/usr/bin/env python3
"""Simplify a 5-class land-cover GeoJSON into a single dissolved vegetation layer.

The classified land cover ships five classes — two forest shades
(forest_deciduous, forest_evergreen) and three open-ground shades
(open_grass, open_meadow, open_bare). The user's simplification (2026-06-14):

  - combine the two greens into ONE vegetation layer, and
  - drop every non-tree class — those areas read as the base map paper.

This is a directed simplification of a *derived* layer, not limiting code:
the 5-class source is preserved (git history + the gitignored cache copy the
build scripts keep), and the build pipeline can regenerate it. See
brain/ai_rules/no_limiting_code_mvp.md ("the user's call ... what to display").

Transform: keep the two forest classes, dissolve them with a unary union so
touching deciduous/evergreen patches merge into one shape, explode the union
back to individual polygons, and re-tag every feature class=vegetation. Non-tree
features are not carried. Top-level name/_meta are preserved (group label kept so
the panel grouping and data manifest are unaffected); maturity stays "derived".

Idempotent guard: if the input has no forest_* features it refuses to write,
so re-running on already-simplified data can't blow it away.

Usage: simplify_landcover_vegetation.py <input_5class.geojson> <output.geojson>
"""
import json
import sys

from shapely.geometry import mapping, shape
from shapely.ops import unary_union
from shapely import set_precision

FOREST_CLASSES = {"forest_deciduous", "forest_evergreen"}
PRECISION = 1e-6  # matches the pipeline's COORDINATE_PRECISION=6 / xy_coordinate_resolution


def main(in_path, out_path):
    with open(in_path) as f:
        fc = json.load(f)

    feats = fc.get("features", [])
    forest = [ft for ft in feats if ft.get("properties", {}).get("class") in FOREST_CLASSES]

    if not forest:
        sys.exit(
            f"refusing to write: {in_path} has no forest_* features "
            f"(already simplified, or wrong input). Classes present: "
            f"{sorted({ft.get('properties', {}).get('class') for ft in feats})}"
        )

    # Dissolve the two forest classes into one geometry, then explode to polygons.
    union = unary_union([shape(ft["geometry"]) for ft in forest])
    union = set_precision(union, PRECISION)
    parts = list(union.geoms) if union.geom_type.startswith("Multi") else [union]
    parts = [p for p in parts if not p.is_empty and p.area > 0]

    kind = forest[0]["properties"].get("kind", "landcover")
    out_features = [
        {
            "type": "Feature",
            "properties": {"id": i + 1, "kind": kind, "class": "vegetation"},
            "geometry": mapping(p),
        }
        for i, p in enumerate(parts)
    ]

    meta = dict(fc.get("_meta", {}))
    meta["maturity_note"] = (
        "derived — machine output; forest classes dissolved into one vegetation "
        "layer, non-tree classes dropped (read as base map). "
        "Source: simplify_landcover_vegetation.py"
    )

    out = {
        "type": "FeatureCollection",
        "name": "vegetation",
        "xy_coordinate_resolution": fc.get("xy_coordinate_resolution", PRECISION),
        "features": out_features,
    }
    if meta:
        out["_meta"] = meta

    with open(out_path, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    print(
        f"{in_path}: {len(feats)} features ({len(forest)} forest) "
        f"-> {out_path}: {len(out_features)} vegetation features"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
