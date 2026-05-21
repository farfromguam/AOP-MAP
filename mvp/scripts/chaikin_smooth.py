#!/usr/bin/env python3
"""Chaikin corner-cutting smoother for contour GeoJSON.

The AOP contour pipeline traces isolines from a lidar DEM, then thins them with
Douglas-Peucker. DP only deletes vertices -- it never adds curvature, so the
thinned lines meet at hard corners that read as "jagged". This pass cuts those
corners into flowing curves (Chaikin corner-cutting, which converges to a
quadratic B-spline), then drops the colinear vertices Chaikin leaves on straight
runs so the payload stays small.

Pure stdlib: runs inside the ghcr.io/osgeo/gdal container with no extra deps.

Usage:
  chaikin_smooth.py [--iterations N] [--colinear-eps-m M] SRC.geojson DST.geojson
"""
import argparse
import json
import math


def _chaikin_open(pts):
    """One Chaikin pass on an open polyline; endpoints are pinned."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for i in range(len(pts) - 1):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        out.append((0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by))
        out.append((0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by))
    out.append(pts[-1])
    return out


def _chaikin_closed(pts):
    """One Chaikin pass on a closed ring (last point repeats the first)."""
    ring = pts[:-1]
    if len(ring) < 3:
        return pts
    out = []
    n = len(ring)
    for i in range(n):
        (ax, ay), (bx, by) = ring[i], ring[(i + 1) % n]
        out.append((0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by))
        out.append((0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by))
    out.append(out[0])
    return out


def smooth_line(pts, iterations):
    pts = [(float(p[0]), float(p[1])) for p in pts]
    closed = len(pts) > 3 and pts[0] == pts[-1]
    for _ in range(iterations):
        pts = _chaikin_closed(pts) if closed else _chaikin_open(pts)
    return pts


def _perp_dist_m(a, b, c):
    """Perpendicular distance of b from segment a-c, in metres (local scale)."""
    mx = 111320.0 * math.cos(math.radians(b[1]))
    my = 110540.0
    ax, ay = a[0] * mx, a[1] * my
    bx, by = b[0] * mx, b[1] * my
    cx, cy = c[0] * mx, c[1] * my
    dx, dy = cx - ax, cy - ay
    seg = math.hypot(dx, dy)
    if seg == 0:
        return math.hypot(bx - ax, by - ay)
    return abs(dx * (ay - by) - (ax - bx) * dy) / seg


def drop_colinear(pts, eps_m):
    """Drop vertices that sit within eps_m of the line through their neighbours.

    Chaikin adds points along straight runs; this strips that clutter while
    leaving curved sections untouched.
    """
    if eps_m <= 0 or len(pts) < 3:
        return pts
    closed = pts[0] == pts[-1]
    keep = [pts[0]]
    for i in range(1, len(pts) - 1):
        if _perp_dist_m(keep[-1], pts[i], pts[i + 1]) >= eps_m:
            keep.append(pts[i])
    keep.append(pts[-1])
    min_len = 4 if closed else 2
    return keep if len(keep) >= min_len else pts


def _round(pts, ndigits=6):
    return [[round(x, ndigits), round(y, ndigits)] for x, y in pts]


def _count(geom):
    t = geom["type"]
    if t == "LineString":
        return len(geom["coordinates"])
    if t == "MultiLineString":
        return sum(len(line) for line in geom["coordinates"])
    return 0


def process_geometry(geom, iterations, eps_m):
    t = geom["type"]
    if t == "LineString":
        geom["coordinates"] = _round(
            drop_colinear(smooth_line(geom["coordinates"], iterations), eps_m))
    elif t == "MultiLineString":
        geom["coordinates"] = [
            _round(drop_colinear(smooth_line(line, iterations), eps_m))
            for line in geom["coordinates"]
        ]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--iterations", type=int, default=2,
                    help="Chaikin passes (default 2)")
    ap.add_argument("--colinear-eps-m", type=float, default=0.5,
                    help="drop vertices within this many metres of straight")
    args = ap.parse_args()

    with open(args.src) as fh:
        fc = json.load(fh)

    v_in = v_out = 0
    for feat in fc.get("features", []):
        geom = feat.get("geometry")
        if not geom:
            continue
        v_in += _count(geom)
        process_geometry(geom, args.iterations, args.colinear_eps_m)
        v_out += _count(geom)

    with open(args.dst, "w") as fh:
        json.dump(fc, fh)

    print("    chaikin: %d -> %d vertices "
          "(%d iterations, colinear eps %.2f m)"
          % (v_in, v_out, args.iterations, args.colinear_eps_m))


if __name__ == "__main__":
    main()
