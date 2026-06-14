#!/usr/bin/env python3
"""Simplify a 5-class land-cover GeoJSON into a single vegetation layer.

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
touching deciduous/evergreen patches merge into one mass. The raw classifier
forest is one near-continuous polygon with ~30k vertices and ~280 small interior
holes (clearings) — MapLibre's `fill` tessellation drops chunks of a polygon that
complex, which showed as missing fill at the map corners (the user: "satellite
shows dense trees there"). So after the union we REDUCE per-polygon complexity to
a level MapLibre renders reliably: drop interior holes below HOLE_MIN_DEG2 (noise
clearings — filling them also reads truer to the dense canopy the imagery shows),
then lightly simplify (SIMPLIFY_DEG, ~3 m) to thin the vertex count. The natural
forest edge is kept (so the layer's outline still traces it), and every output
polygon lands well under the tessellation limit. Non-tree features are not
carried. Top-level name/_meta are preserved (group label kept so the panel
grouping and data manifest are unaffected); maturity stays "derived".

Idempotent guard: if the input has no forest_* features it refuses to write,
so re-running on already-simplified data can't blow it away.

Usage: simplify_landcover_vegetation.py <input_5class.geojson> <output.geojson>
"""
import json
import sys

from shapely.geometry import Polygon, MultiPolygon, mapping, shape
from shapely.ops import unary_union

FOREST_CLASSES = {"forest_deciduous", "forest_evergreen"}
# Drop interior holes (clearings) smaller than this in deg^2. ~5e-7 deg^2 ≈ 5000 m².
# Small holes inflate the hole count that breaks MapLibre's polygon tessellation
# (the raw forest had 284 holes → fill failed); this keeps only genuinely large
# clearings (fields/meadows ≥ ~0.5 ha, up to the 0.1–0.4 km² ones) and fills the
# rest — which also reads truer to the dense canopy the imagery shows.
HOLE_MIN_DEG2 = 5e-7
# Light Douglas-Peucker tolerance in degrees (~3 m at this latitude). Thins the
# ~30k-vertex forest outline without visibly moving the edge at viewer zooms.
SIMPLIFY_DEG = 3e-5


def deholed(poly):
    """Drop interior rings below HOLE_MIN_DEG2; keep the rest."""
    keep = [r for r in poly.interiors if Polygon(r).area >= HOLE_MIN_DEG2]
    return Polygon(poly.exterior, keep)


def simplify_geom(geom):
    polys = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]
    out = []
    for p in polys:
        if p.is_empty or p.area <= 0:
            continue
        p = deholed(p)
        p = p.simplify(SIMPLIFY_DEG, preserve_topology=True)
        if p.is_empty or p.area <= 0:
            continue
        if p.geom_type == "Polygon":
            out.append(p)
        elif p.geom_type == "MultiPolygon":
            out.extend(g for g in p.geoms if not g.is_empty and g.area > 0)
    return out


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

    union = unary_union([shape(ft["geometry"]).buffer(0) for ft in forest])
    parts = simplify_geom(union)

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
        "layer, non-tree classes dropped (read as base map), small clearings "
        "filled and edge lightly simplified for reliable fill rendering. "
        "Source: simplify_landcover_vegetation.py"
    )

    out = {
        "type": "FeatureCollection",
        "name": "vegetation",
        "xy_coordinate_resolution": fc.get("xy_coordinate_resolution", 1e-6),
        "features": out_features,
    }
    if meta:
        out["_meta"] = meta

    with open(out_path, "w") as f:
        json.dump(out, f, separators=(",", ":"))

    # Report worst-case per-polygon complexity so a regression back toward the
    # tessellation-breaking shape is visible at build time.
    maxv = maxh = 0
    for p in parts:
        v = len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors)
        maxv = max(maxv, v)
        maxh = max(maxh, len(p.interiors))
    print(
        f"{in_path}: {len(feats)} features ({len(forest)} forest) "
        f"-> {out_path}: {len(out_features)} vegetation polygons "
        f"(max {maxv} verts / {maxh} holes in one polygon)"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
