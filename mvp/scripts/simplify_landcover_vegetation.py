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
holes (clearings). MapLibre tessellates `fill` per tile with earcut, and one
polygon that large+holey degenerates — chunks of the fill silently drop, which
showed as the whole 9-patch canopy rendering only as a central blob with empty
corners (the user: "satellite shows dense trees there ... all but top right have
un-natural rendering errors"). The v81 complexity cap (3976 verts / 47 holes in
one polygon) was NOT enough: a single fill polygon that big still collapses.

The real fix is to stop shipping the canopy as one giant fill polygon:

  1. Clean: drop interior holes below HOLE_MIN_DEG2 (noise clearings — filling
     them also reads truer to the dense canopy the imagery shows), then lightly
     simplify (SIMPLIFY_DEG, ~3 m) to thin the vertex count.
  2. Fill = SUBDIVIDE the cleaned mass against a fixed grid (GRID_DEG cells), so
     any polygon over SUBDIVIDE_VERTS becomes many small grid-clipped pieces.
     Small pieces tessellate reliably, so the fill draws everywhere — corners
     included. Adjacent pieces share exact edges (no overlap → no opacity seam).
  3. Outline = the dissolved boundary emitted as LineString features. Lines never
     hit the fill-tessellation failure (which is why the OLD outline always drew
     while the fill vanished), and emitting the TRUE boundary means the outline
     traces the canopy edge, not the subdivision grid.

The viewer's fill layers render only the polygons; its outline (`line`) layers
filter to LineString geometry, so they draw the boundary, never the grid edges.
Non-tree features are not carried. Top-level name/_meta are preserved; maturity
stays "derived".

Idempotent guard: if the input has no forest_* features it refuses to write,
so re-running on already-simplified data can't blow it away.

Usage: simplify_landcover_vegetation.py <input_5class.geojson> <output.geojson>
"""
import json
import math
import sys

from shapely.geometry import Polygon, MultiPolygon, box, mapping, shape
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
# Subdivision grid for the FILL. A polygon with more than SUBDIVIDE_VERTS vertices
# is clipped into GRID_DEG cells so every emitted fill piece is small enough that
# earcut never drops it. GRID_DEG ≈ 0.006° ≈ 550 m; SUBDIVIDE_VERTS 600 keeps even
# the cleaned ~4k-vertex 9-patch canopy split into pieces well under the limit.
GRID_DEG = 0.006
SUBDIVIDE_VERTS = 600


def deholed(poly):
    """Drop interior rings below HOLE_MIN_DEG2; keep the rest."""
    keep = [r for r in poly.interiors if Polygon(r).area >= HOLE_MIN_DEG2]
    return Polygon(poly.exterior, keep)


def poly_verts(p):
    return len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors)


def clean_parts(geom):
    """Dehole + light-simplify each polygon of the dissolved mass."""
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


def subdivided(poly):
    """Grid-clip a polygon into tessellation-friendly pieces. Polygons already
    under SUBDIVIDE_VERTS pass straight through (small ones render fine)."""
    if poly_verts(poly) <= SUBDIVIDE_VERTS:
        return [poly]
    minx, miny, maxx, maxy = poly.bounds
    out = []
    x0 = math.floor(minx / GRID_DEG) * GRID_DEG
    y0 = math.floor(miny / GRID_DEG) * GRID_DEG
    nx = int(math.ceil((maxx - x0) / GRID_DEG))
    ny = int(math.ceil((maxy - y0) / GRID_DEG))
    for ix in range(nx):
        for iy in range(ny):
            cell = box(x0 + ix * GRID_DEG, y0 + iy * GRID_DEG,
                       x0 + (ix + 1) * GRID_DEG, y0 + (iy + 1) * GRID_DEG)
            piece = poly.intersection(cell)
            if piece.is_empty or piece.area <= 0:
                continue
            piece = piece.buffer(0)
            geoms = piece.geoms if piece.geom_type == "MultiPolygon" else [piece]
            out.extend(g for g in geoms if g.geom_type == "Polygon" and not g.is_empty and g.area > 0)
    return out


def boundary_lines(parts):
    """The dissolved canopy edge (exteriors + kept holes) as a MultiLineString,
    for the viewer's outline layer — robust where the giant fill is not."""
    return unary_union([p.boundary for p in parts])


def vegetation_features(parts, kind="landcover"):
    """Cleaned canopy polygons -> the viewer's vegetation FeatureCollection body:
    grid-subdivided fill polygons (so earcut renders everywhere) plus one
    LineString outline (the true canopy edge). The single source of the viewer's
    landcover feature contract — shared by the 5-class bake (main) and the
    hand-edit re-import (import_landcover_svg.py). Returns (features, fill_pieces)."""
    fill_pieces = []
    for p in parts:
        fill_pieces.extend(subdivided(p))
    outline = boundary_lines(parts)
    feats = [
        {
            "type": "Feature",
            "properties": {"id": i + 1, "kind": kind, "class": "vegetation", "role": "fill"},
            "geometry": mapping(p),
        }
        for i, p in enumerate(fill_pieces)
    ]
    feats.append({
        "type": "Feature",
        "properties": {"id": len(fill_pieces) + 1, "kind": kind, "class": "vegetation", "role": "outline"},
        "geometry": mapping(outline),
    })
    return feats, fill_pieces


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
    parts = clean_parts(union)

    kind = forest[0]["properties"].get("kind", "landcover")
    out_features, fill_pieces = vegetation_features(parts, kind)

    meta = dict(fc.get("_meta", {}))
    meta["maturity_note"] = (
        "derived — machine output; forest classes dissolved into one vegetation "
        "layer, non-tree classes dropped (read as base map), small clearings "
        "filled. Fill is grid-subdivided into small polygons so earcut renders it "
        "everywhere (the giant single polygon dropped its corners); the canopy "
        "edge ships as a separate LineString outline. "
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

    # Report worst-case per-fill-piece complexity so a regression back toward the
    # tessellation-breaking shape is visible at build time.
    maxv = max((poly_verts(p) for p in fill_pieces), default=0)
    maxh = max((len(p.interiors) for p in fill_pieces), default=0)
    print(
        f"{in_path}: {len(feats)} features ({len(forest)} forest) "
        f"-> {out_path}: {len(fill_pieces)} fill pieces + 1 outline "
        f"(max {maxv} verts / {maxh} holes in one fill piece)"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
