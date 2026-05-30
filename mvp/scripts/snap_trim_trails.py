#!/usr/bin/env python3
"""Snap dangling trail ends onto their neighbours and trim short overshoots.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

Post-import topology cleanup on the merged network. "Ensure the trails end on
another": at a junction a trail end should land ON the trail it meets, sharing a
node. Two defects this fixes, conservatively (small tolerances; ambiguous cases
are left for the human review pass and reported):

  TRIM  — an end that overshoots past a crossing and dead-ends in a short stub:
          cut the line back to the crossing point.
  SNAP  — an end that stops just short of another trail (a gap): move the end
          onto the nearest point of that trail, and insert that point as a vertex
          on the target so the two share a node.

Only degree-1 ENDPOINTS are touched; interior vertices are left alone. Works in
local metres (equirectangular at the park latitude) so tolerances are real.

Usage:  python3 mvp/scripts/snap_trim_trails.py [in.geojson] [out.geojson]
        (defaults: website/data/aop_trail_network.geojson, in place)
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path

from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

REPO = Path(__file__).resolve().parents[2]
NET = REPO / "website/data/aop_trail_network.geojson"

SNAP_M = 18.0      # close a gap when an end is within this of another trail
TRIM_M = 18.0      # trim an overshoot stub no longer than this past a crossing
EPS_M = 0.5        # below this an end is already coincident — leave it
SELF_LOOP_M = 2.0  # an end this close to its own non-adjacent vertex is a loop, not a gap


def main():
    src = (Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else NET)
    out = (Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src)
    fc = json.loads(src.read_text())
    feats = fc["features"]

    # --- local-metres projection ---------------------------------------------
    pts = [c for f in feats if f["geometry"]["type"] == "LineString"
           for c in f["geometry"]["coordinates"]]
    lat0 = sum(p[1] for p in pts) / len(pts)
    lng0 = min(p[0] for p in pts)
    mlat = 110540.0
    mlng = 111320.0 * math.cos(math.radians(lat0))

    def to_m(lng, lat):
        return [(lng - lng0) * mlng, (lat - lat0) * mlat]

    def to_ll(x, y):
        return [round(lng0 + x / mlng, 7), round(lat0 + y / mlat, 7)]

    # working arrays in metres; non-LineStrings pass through untouched
    lines = []   # list of (feat_index, [[x,y],...]) for LineStrings >= 2 pts
    for i, f in enumerate(feats):
        g = f["geometry"]
        if g["type"] == "LineString" and len(g["coordinates"]) >= 2:
            lines.append([i, [to_m(*c) for c in g["coordinates"]]])

    arrs = {i: pts for i, pts in lines}        # feat_index -> metre points
    inserts = {}                                # feat_index -> list of points to weld in

    def shapely_for(skip):
        return {i: LineString(pts) for i, pts in arrs.items()
                if i != skip and len(pts) >= 2}

    def ends(pts):
        # (vertex_index_of_endpoint, neighbour_index) for both ends
        return [(0, 1), (len(pts) - 1, len(pts) - 2)]

    trimmed = snapped = 0

    # --- TRIM: cut short overshoots past a crossing --------------------------
    for i, pts in lines:
        others = shapely_for(i)
        for ei, ni in ends(pts):
            P = pts[ei]; V = pts[ni]
            seg = LineString([V, P])
            best = None  # (dist_to_P, point)
            for j, ln in others.items():
                inter = seg.intersection(ln)
                if inter.is_empty:
                    continue
                cands = [inter] if inter.geom_type == "Point" else (
                        list(inter.geoms) if inter.geom_type == "MultiPoint" else [])
                for pt in cands:
                    dP = math.dist((pt.x, pt.y), P)
                    dV = math.dist((pt.x, pt.y), V)
                    if dP <= TRIM_M and dV > EPS_M and (best is None or dP < best[0]):
                        best = (dP, [pt.x, pt.y], j)
            if best and best[0] > EPS_M:
                pts[ei] = best[1]               # move end back to the crossing
                inserts.setdefault(best[2], []).append(best[1])
                trimmed += 1

    # --- SNAP: close short gaps onto the nearest trail -----------------------
    # A free end is one >SNAP_M from any OTHER feature. Not every free end is a gap
    # to fix — classify, don't cry wolf (the old code counted all three the same):
    #   - SELF-LOOP: the end rejoins its OWN line (a lollipop / closed loop), so it
    #     coincides with a non-adjacent vertex of the same feature — touches itself,
    #     not nothing (e.g. trail "9" closes onto its own vertex at 0 m). Ignore.
    #   - ROAD END: a road that terminates in space (it usually joins the network at
    #     its other end). Roads legitimately dead-end at boundaries/lots — report,
    #     don't flag for fixing.
    #   - TRAIL DANGLER: a TRAIL end hanging >SNAP_M from anything and not a loop —
    #     the real review set (e.g. an unnamed trail 88 m off trail 50).
    self_loops = 0
    road_ends = []                              # [feat_index, end_label, gap, nearest_index]
    trail_danglers = []
    for i, pts in lines:
        others = shapely_for(i)
        if not others:
            continue
        kind = feats[i]["properties"].get("kind", "trail")
        for ei, _ in ends(pts):
            P = Point(pts[ei])
            j, q, gap = None, None, float("inf")
            for k, ln in others.items():
                d = P.distance(ln)
                if d < gap:
                    gap, j, q = d, k, nearest_points(P, ln)[1]
            if gap <= EPS_M:
                continue                        # already connected
            if gap <= SNAP_M:
                pts[ei] = [q.x, q.y]
                inserts.setdefault(j, []).append([q.x, q.y])
                snapped += 1
            elif any(math.dist(pts[ei], pts[v]) <= SELF_LOOP_M
                     for v in range(len(pts)) if abs(v - ei) > 2):
                self_loops += 1                 # end rejoins its own line — not a gap
            else:
                entry = [i, "start" if ei == 0 else "end", gap, j]
                (road_ends if kind == "road" else trail_danglers).append(entry)
    dangling = len(trail_danglers)

    # --- weld inserted points into target lines (collinear, shape-preserving) -
    for j, qs in inserts.items():
        pts = arrs[j]
        for q in qs:
            # find the segment q lies on; insert if not already a vertex
            if any(math.dist(q, v) <= EPS_M for v in pts):
                continue
            bk, bd = None, float("inf")
            for k in range(len(pts) - 1):
                d = _pt_seg(q, pts[k], pts[k + 1])
                if d < bd:
                    bd, bk = d, k
            if bk is not None:
                pts.insert(bk + 1, q)

    # --- project back + write ------------------------------------------------
    for i, pts in arrs.items():
        feats[i]["geometry"]["coordinates"] = [to_ll(x, y) for x, y in pts]

    out.write_text(json.dumps(fc, indent=1))

    def label(fi):
        p = feats[fi]["properties"]
        return f"{p.get('kind','trail')} \"{p.get('name')}\""

    try:
        shown = out.relative_to(REPO)
    except ValueError:
        shown = out
    print(f"snap/trim -> {shown}")
    print(f"  trimmed overshoots: {trimmed}")
    print(f"  snapped gaps:       {snapped}  (<= {SNAP_M:.0f} m)")
    print(f"  self-loops ignored: {self_loops}  (end rejoins its own line — not a gap)")
    print(f"  road dead-ends:     {len(road_ends)}  (roads terminate in space — expected, not a fix)")
    print(f"  TRAIL danglers:     {dangling}  (> {SNAP_M:.0f} m from anything — the review set)")
    for fi, end_label, gap, nj in trail_danglers:
        print(f"     - {label(fi)} {end_label} end: {gap:.0f} m from {label(nj) if nj is not None else '—'}")
    for fi, end_label, gap, nj in road_ends:
        print(f"     · (road) {label(fi)} {end_label} end: {gap:.0f} m from {label(nj) if nj is not None else '—'}")


def _pt_seg(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


if __name__ == "__main__":
    main()
