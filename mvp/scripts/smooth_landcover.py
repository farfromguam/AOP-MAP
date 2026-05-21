#!/usr/bin/env python3
"""Smooth and tidy polygonized land-cover before it ships to the viewer.

Reads the WGS84 GeoJSON that ogr2ogr produced from gdal_polygonize (the
raster was already vertex-simplified by ogr2ogr), then:
  - drops sliver polygons and pinhole rings below an area floor,
  - runs Chaikin corner-cutting so the pixel staircase reads as organic
    curves instead of blocky steps,
  - renames the raster DN value to a human-readable `class` property.

Chaikin is corner-cutting by linear interpolation, so it is unit-agnostic and
runs fine directly on lon/lat. It is applied per ring: land-cover polygons are
not a shared-edge coverage here (open ground is left as the map background, so
only forest / water / bare are emitted), so per-feature smoothing is safe.
Smoothing runs before the boundary clip, so the property line stays a crisp
cut while the natural class edges read soft.

Usage: smooth_landcover.py in.geojson out.geojson
"""
import json
import math
import sys

CLASS_NAMES = {1: "forest"}
CHAIKIN_ITERS = 2
MIN_POLY_AREA = 250.0   # m^2 - drop forest islands smaller than this
# Interior holes below this are dropped: in the leaf-off NAIP, bare deciduous
# crowns and small canopy gaps punch dot-holes through otherwise continuous
# forest. Real clearings are far larger, so a generous floor cleans the
# artefacts without filling any genuine opening.
MIN_HOLE_AREA = 500.0   # m^2

DEG_LAT_M = 110574.0   # metres per degree of latitude (mid-latitude mean)
DEG_LON_M = 111320.0   # metres per degree of longitude at the equator


def ring_area_m2(ring):
    """Absolute area of a closed lon/lat ring, converted to square metres."""
    s = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i]
        x1, y1 = ring[i + 1]
        s += x0 * y1 - x1 * y0
    deg2 = abs(s) / 2.0
    lat = sum(p[1] for p in ring) / len(ring)
    return deg2 * (DEG_LON_M * math.cos(math.radians(lat))) * DEG_LAT_M


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


def clean_polygon(rings):
    """Filter + smooth one polygon's rings. Returns a polygon or None."""
    if not rings or ring_area_m2(rings[0]) < MIN_POLY_AREA:
        return None
    out = [chaikin(rings[0], CHAIKIN_ITERS)]
    for hole in rings[1:]:
        if ring_area_m2(hole) >= MIN_HOLE_AREA:
            out.append(chaikin(hole, CHAIKIN_ITERS))
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    with open(src) as fh:
        data = json.load(fh)

    out_features = []
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

        cleaned = [p for p in (clean_polygon(rings) for rings in polys) if p]
        if not cleaned:
            continue

        if len(cleaned) == 1:
            out_geom = {"type": "Polygon", "coordinates": cleaned[0]}
        else:
            out_geom = {"type": "MultiPolygon", "coordinates": cleaned}
        out_features.append({
            "type": "Feature",
            "properties": {"class": name},
            "geometry": out_geom,
        })

    with open(dst, "w") as fh:
        json.dump({"type": "FeatureCollection", "features": out_features}, fh)
    print(f"==> smoothed {len(out_features)} land-cover polygons -> {dst}")


if __name__ == "__main__":
    main()
