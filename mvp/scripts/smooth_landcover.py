#!/usr/bin/env python3
"""Smooth polygonized land-cover before it ships to the viewer.

Reads the WGS84 GeoJSON that ogr2ogr produced from gdal_polygonize (the
raster was already vertex-simplified by ogr2ogr), runs Chaikin corner-cutting
so the pixel staircase reads as organic curves, and renames the raster DN
value to a human-readable `class` property.

The land-cover layer is a full coverage now -- five classes (two forest, three
open) that tile the whole AOI with no gaps. So this pass does NOT drop sliver
polygons or pinhole holes the way the old forest-only version did: a dropped
polygon would punch a hole through the coverage, and a dropped hole would
overlap whichever class actually sits inside it. Speckle is instead handled
upstream in classify_landcover.py (the NDVI field is low-passed and each
sub-class is morphologically tidied), so there is nothing to filter here.

Chaikin runs per ring. On a coverage that is *near* topology-preserving: a
shared edge between two adjacent polygons is the same run of vertices in both
rings, and Chaikin is a local operation (each output point comes from two
consecutive input points), so the interior of that run is smoothed identically
in both polygons regardless of traversal direction. Only the handful of
junction vertices where three or more polygons meet diverge, and only by a
sub-pixel amount; the viewer draws each class with a thin same-family outline
that bridges any such hairline gap.

Usage: smooth_landcover.py in.geojson out.geojson
"""
import json
import sys

# Raster DN -> land-cover class name. Must match classify_landcover.py.
CLASS_NAMES = {
    1: "forest_deciduous",
    2: "forest_evergreen",
    3: "open_grass",
    4: "open_meadow",
    5: "open_bare",
}
CHAIKIN_ITERS = 2


def chaikin(ring, iters):
    """Chaikin corner-cutting on a closed ring (first vertex repeated last)."""
    pts = ring[:-1]
    for _ in range(iters):
        if len(pts) < 3:
            break
        out = []
        n = len(pts)
        for i in range(n):
            px, py = pts[i]
            qx, qy = pts[(i + 1) % n]
            out.append((0.75 * px + 0.25 * qx, 0.75 * py + 0.25 * qy))
            out.append((0.25 * px + 0.75 * qx, 0.25 * py + 0.75 * qy))
        pts = out
    return [list(p) for p in pts] + [list(pts[0])]


def smooth_polygon(rings):
    """Chaikin-smooth every ring of one polygon (outer ring + holes)."""
    return [chaikin(ring, CHAIKIN_ITERS) for ring in rings]


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src) as fh:
        data = json.load(fh)

    out_features = []
    counts = {}
    for feat in data.get("features", []):
        geom = feat.get("geometry")
        if not geom:
            continue
        dn = feat.get("properties", {}).get("DN")
        name = CLASS_NAMES.get(int(dn)) if dn is not None else None
        if name is None:
            continue

        if geom["type"] == "Polygon":
            polys = [geom["coordinates"]]
        elif geom["type"] == "MultiPolygon":
            polys = geom["coordinates"]
        else:
            continue

        smoothed = [smooth_polygon(rings) for rings in polys]
        if len(smoothed) == 1:
            out_geom = {"type": "Polygon", "coordinates": smoothed[0]}
        else:
            out_geom = {"type": "MultiPolygon", "coordinates": smoothed}
        out_features.append({
            "type": "Feature",
            "properties": {"class": name},
            "geometry": out_geom,
        })
        counts[name] = counts.get(name, 0) + 1

    with open(dst, "w") as fh:
        json.dump({"type": "FeatureCollection", "features": out_features}, fh)
    print(f"==> smoothed {len(out_features)} land-cover polygons -> {dst}")
    for name in sorted(counts):
        print(f"    {name}: {counts[name]}")


if __name__ == "__main__":
    main()
