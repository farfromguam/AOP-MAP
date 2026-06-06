#!/usr/bin/env python3
"""Clip the heavy viewer data down to the park core for the topo+trail colour
comparison page (website/topo_trail_compare.html).

The comparison renders REAL data (not an SVG mockup) so the user can judge the
brown contour / orange trail colours against the actual map elements. The full
contour file is ~13 MB; loading it into several small maps is wasteful, so this
clips every layer the comparison needs to a tight bbox around the trail core and
writes minified copies to website/compare_data/.

A feature is kept when its own geometry bbox intersects the clip bbox (whole
features are preserved, so lines may run slightly past the edge — fine for a
review). Re-run after the source data changes. Output is reproducible.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "website", "data"))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "website", "compare_data"))

# Padded bbox around the trail network core (aop_trail_network spans
# lng[-85.7606,-85.7459] lat[35.0839,35.0977]); padded so the z15 compare view
# has no bare edges.  [minLng, minLat, maxLng, maxLat]
CLIP = (-85.770, 35.078, -85.737, 35.104)

# layer file -> nothing special; all clipped the same way.
FILES = [
    "aop_contours.geojson",
    "aop_trail_network.geojson",
    "aop_water.geojson",
    "aop_roads.geojson",
    "aop_landcover.geojson",
    "aop_buildings.geojson",
]


def geom_bbox(geom):
    minx = miny = 1e9
    maxx = maxy = -1e9

    def walk(c):
        nonlocal minx, miny, maxx, maxy
        if not c:
            return
        if isinstance(c[0], (int, float)):
            x, y = c[0], c[1]
            minx = min(minx, x); miny = min(miny, y)
            maxx = max(maxx, x); maxy = max(maxy, y)
        else:
            for p in c:
                walk(p)

    walk(geom.get("coordinates"))
    return minx, miny, maxx, maxy


def intersects(b):
    minx, miny, maxx, maxy = b
    return not (maxx < CLIP[0] or minx > CLIP[2] or maxy < CLIP[1] or miny > CLIP[3])


def in_bb(p):
    return CLIP[0] <= p[0] <= CLIP[2] and CLIP[1] <= p[1] <= CLIP[3]


def clip_line(coords):
    """Keep runs of segments where either endpoint is inside the clip bbox, so a
    long contour's far tails are dropped but anything crossing the park stays
    (with one vertex of overhang on each side). Returns a list of polylines."""
    segs = []
    cur = []
    for i in range(len(coords) - 1):
        a, b = coords[i], coords[i + 1]
        if in_bb(a) or in_bb(b):
            if not cur:
                cur = [a, b]
            else:
                cur.append(b)
        elif cur:
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    return segs


def clip_feature_lines(f):
    """For line geometries, trim coordinates to the clip bbox (returns possibly
    several features). Polygons/points are returned whole if they intersect."""
    g = f.get("geometry") or {}
    t = g.get("type")
    if t == "LineString":
        lines = clip_line(g["coordinates"])
    elif t == "MultiLineString":
        lines = []
        for ls in g["coordinates"]:
            lines.extend(clip_line(ls))
    else:
        return [f] if intersects(geom_bbox(g)) else []
    out = []
    for ls in lines:
        if len(ls) >= 2:
            out.append({"type": "Feature", "properties": f.get("properties", {}),
                        "geometry": {"type": "LineString", "coordinates": ls}})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    for fn in FILES:
        src = os.path.join(DATA, fn)
        if not os.path.exists(src):
            print(f"SKIP {fn} (missing)")
            continue
        fc = json.load(open(src))
        feats = fc.get("features", [])
        kept = []
        for f in feats:
            g = f.get("geometry") or {}
            if not g.get("coordinates"):
                continue
            if not intersects(geom_bbox(g)):
                continue
            kept.extend(clip_feature_lines(f))
        out = {"type": "FeatureCollection", "features": kept}
        dst = os.path.join(OUT, fn)
        with open(dst, "w") as fh:
            json.dump(out, fh, separators=(",", ":"))
        kb = os.path.getsize(dst) // 1024
        print(f"{fn}: {len(feats)} -> {len(kept)} features, {kb} KB")


if __name__ == "__main__":
    main()
