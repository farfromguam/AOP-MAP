#!/usr/bin/env python3
"""Stage 6: build CONTIGUOUS numbered trails from the traced graph + markers.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

The vectorizer leaves trails as ~382 disconnected edge fragments with no number.
This step makes each trail whole:
  1. Tag edges with a trail number — for every marker sitting on an edge, match it
     to a hand-read number (trail_number_reads.json) by pixel centroid (<30 px).
  2. Connect, per number, the marker-bearing edges into one contiguous path by
     shortest-path through the skeleton graph, penalizing hops onto a *different*
     numbered trail (x6) so the path stays on its own ink across junctions.
  3. Warp to lng/lat and emit one feature per trail number.

A trail's number is labelled at several points along its route, so the markers of
trail N seed several fragments; this stitches the skeleton between them.

Inputs : brain/output/paper_trace/trail_graph.json        (from vectorize)
         brain/output/paper_trace/trail_number_reads.json (hand-read numbers)
Outputs: website/data/sfwda_numbered_trails.geojson  (one contiguous trail / number)
         + stamps trail_number onto directly-tagged edges in the traced-trails layers
"""
from __future__ import annotations
import heapq, json
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

import extract_paper_trails as ex
from paper_trace_warp import PaperWarp

REPO = Path(__file__).resolve().parents[2]
PT = REPO / "brain/output/paper_trace"
DATA = REPO / "website/data"
MATCH_PX = 30
OTHER_TRAIL_PENALTY = 6.0
BRIDGE_GAP_PX = 70       # max gap to rejoin two loose skeleton ends
BRIDGE_COS = 0.5         # ends must face each other within ~60 deg (colinear rejoin)
CONNECT_CAP_PX = 420     # max LOCAL skeleton-path length to connect two pieces of one trail
                         # (beyond this, pieces aren't adjacent on one trail -> leave a gap)


def build_bridges(edges, nodes):
    """Synthetic edges that rejoin degree-1 skeleton ends facing each other.

    A marker lifted off the line (or an ink gap) leaves two loose ends pointing
    across the gap. Reconnect the nearest such pair when the gap is small AND
    both ends' outward tangents align with the bridge direction (colinear), so we
    restore a cut trail without fusing trails that merely pass nearby.
    """
    deg = defaultdict(int)
    for e in edges.values():
        deg[e["a"]] += 1; deg[e["b"]] += 1
    ends = []   # (node_id, coord, outward_unit_tangent, edge_id)
    for e in edges.values():
        px = e["px"]
        if len(px) < 2:
            continue
        for node, p_end, p_in in ((e["a"], px[0], px[1]), (e["b"], px[-1], px[-2])):
            if deg[node] != 1:
                continue
            p0 = np.array(p_end, float); t = p0 - np.array(p_in, float)
            n = np.linalg.norm(t)
            if n > 1e-6:
                ends.append((node, p0, t / n, e["id"]))
    bridges, used, bid = [], set(), 0
    for ni, pi, ti, ei in ends:
        best, bestd = None, BRIDGE_GAP_PX
        for nj, pj, tj, ej in ends:
            if ej == ei or nj == ni:
                continue
            v = pj - pi; d = float(np.linalg.norm(v))
            if d < 1 or d > bestd:
                continue
            u = v / d
            if float(u @ ti) > BRIDGE_COS and float((-u) @ tj) > BRIDGE_COS:
                best, bestd = (ni, nj, pi, pj), d
        if best:
            a, b, pa, pb = best
            key = frozenset((a, b))
            if key in used:
                continue
            used.add(key); bid -= 1
            bridges.append({"id": bid, "a": a, "b": b,
                            "px": [[round(float(pa[0]), 1), round(float(pa[1]), 1)],
                                   [round(float(pb[0]), 1), round(float(pb[1]), 1)]],
                            "length_px": round(bestd, 1), "difficulty": None,
                            "marker_centroids": [], "bridge": True})
    return bridges


def main():
    g = json.loads((PT / "trail_graph.json").read_text())
    reads = [(r["centroid_px"][0], r["centroid_px"][1], r["number"])
             for r in json.loads((PT / "trail_number_reads.json").read_text())["reads"]]
    edges = {e["id"]: e for e in g["edges"]}

    # rejoin loose skeleton ends so cut trails become connected before pathfinding
    bridges = build_bridges(edges, g["nodes"])
    for b in bridges:
        edges[b["id"]] = b
    print(f"added {len(bridges)} colinear bridge edges (gap<={BRIDGE_GAP_PX}px)")

    # 1. tag each edge with a number from the markers sitting on it
    def num_for_centroid(mx, my):
        best, bd = None, MATCH_PX ** 2
        for rx, ry, num in reads:
            d = (rx - mx) ** 2 + (ry - my) ** 2
            if d < bd:
                bd, best = d, num
        return best
    enum = {}   # edge_id -> trail number (or None)
    for eid, e in edges.items():
        cand = [n for mc in e["marker_centroids"] if (n := num_for_centroid(*mc)) is not None]
        enum[eid] = Counter(cand).most_common(1)[0][0] if cand else None

    # 2. adjacency + per-number connect
    adj = defaultdict(list)
    for e in edges.values():
        adj[e["a"]].append((e["b"], e["id"]))
        adj[e["b"]].append((e["a"], e["id"]))
    elen = {eid: e["length_px"] for eid, e in edges.items()}

    def dijkstra(sources, n):
        dist = {s: 0.0 for s in sources}
        pred = {}
        h = [(0.0, s) for s in sources]
        heapq.heapify(h)
        while h:
            d, u = heapq.heappop(h)
            if d > dist.get(u, 1e18):
                continue
            for v, eid in adj[u]:
                w = elen[eid] * (OTHER_TRAIL_PENALTY if (enum[eid] is not None and enum[eid] != n) else 1.0)
                nd = d + w
                if nd < dist.get(v, 1e18):
                    dist[v], pred[v] = nd, (u, eid)
                    heapq.heappush(h, (nd, v))
        return dist, pred

    nodes = g["nodes"]
    numbers = sorted({n for n in enum.values() if n is not None})
    warp = PaperWarp()
    # canonical lng/lat per graph node so edges that share a node weld exactly in
    # linemerge (px endpoints can differ sub-pixel from the node coord otherwise).
    _nll = {}
    def node_ll(nid):
        if nid not in _nll:
            _nll[nid] = tuple(warp.pixel_to_lnglat(*nodes[nid]))
        return _nll[nid]
    def edge_line(eid):
        e = edges[eid]; px = e["px"]
        pts = [node_ll(e["a"])] + [tuple(warp.pixel_to_lnglat(x, y)) for x, y in px[1:-1]] + [node_ll(e["b"])]
        return LineString(pts)
    feats, stats = [], []
    edge_trailnum = {}   # edge_id -> number (for stamping the edges layer)
    extra_by_num = {}    # number -> straight connector segments (px) for overlay
    ov = cv2.imread(str(ex.SRC))          # debug overlay over the raster
    PAL = [(230,25,75),(60,180,75),(255,130,0),(0,130,255),(145,30,180),
           (70,240,240),(240,50,230),(0,128,128),(170,110,40),(128,0,0)]
    chosen_px = {}   # number -> list of edge ids (to draw)

    for n in numbers:
        seed = [eid for eid in edges if enum[eid] == n]
        # union-find seed edges into components by shared node
        parent = {}
        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        def union(a, b):
            parent[find(a)] = find(b)
        for eid in seed:
            union(edges[eid]["a"], edges[eid]["b"])
        comps = defaultdict(set)
        for eid in seed:
            comps[find(edges[eid]["a"])].update((edges[eid]["a"], edges[eid]["b"]))
        comps = list(comps.values())

        chosen = set(seed)
        extra_px = []          # bounded straight connectors for small true gaps
        dropped = 0            # components too far to connect honestly (left as gaps)
        seeds_n = len(comps)
        if len(comps) > 1:
            connected = set(comps[0])
            remaining = comps[1:]
            # connect a component ONLY through a short local path. Markers sit a few
            # hundred px apart along a trail; a path much longer than that means the
            # two pieces aren't adjacent on one trail (shared-skeleton over-reach) —
            # leave them as an honest gap rather than grab a map-spanning route.
            progress = True
            while remaining and progress:
                dist, pred = dijkstra(connected, n)
                pick = None     # (raw_len, node, comp, edge_ids)
                for comp in remaining:
                    nd = min(comp, key=lambda x: dist.get(x, 1e18))
                    if dist.get(nd, 1e18) >= 1e17:
                        continue
                    cur, raw, eids = nd, 0.0, []
                    while cur not in connected and cur in pred:
                        u, eid = pred[cur]; eids.append(eid); raw += elen[eid]; cur = u
                    if raw <= CONNECT_CAP_PX and (pick is None or raw < pick[0]):
                        pick = (raw, nd, comp, eids)
                if pick:
                    _, nd, comp, eids = pick
                    chosen.update(eids); connected |= comp; remaining.remove(comp)
                else:
                    progress = False
            # any still-disconnected component within a tiny straight gap: bridge it
            for comp in list(remaining):
                pair, pd = None, BRIDGE_GAP_PX
                for cn in connected:
                    cx, cy = nodes[cn]
                    for rn in comp:
                        rx, ry = nodes[rn]
                        d = ((cx - rx) ** 2 + (cy - ry) ** 2) ** 0.5
                        if d < pd:
                            pd, pair = d, (cn, rn)
                if pair:
                    extra_px.append([nodes[pair[0]], nodes[pair[1]]])
                    connected |= comp; remaining.remove(comp)
            dropped = len(remaining)

        for eid in chosen:
            edge_trailnum.setdefault(eid, n)   # first number to claim an edge wins
        chosen_px[n] = list(chosen)
        extra_by_num[n] = extra_px
        lines = [edge_line(eid) for eid in chosen]
        lines += [LineString([tuple(warp.pixel_to_lnglat(*p0)), tuple(warp.pixel_to_lnglat(*p1))]) for p0, p1 in extra_px]
        merged = linemerge(lines) if len(lines) > 1 else lines[0]
        if isinstance(merged, LineString):
            geom = {"type": "LineString", "coordinates": [list(c) for c in merged.coords]}
            parts = 1
        else:
            geom = {"type": "MultiLineString", "coordinates": [[list(c) for c in g.coords] for g in merged.geoms]}
            parts = len(merged.geoms)
        diffs = Counter(edges[eid]["difficulty"] for eid in seed if edges[eid]["difficulty"])
        feats.append({"type": "Feature", "geometry": geom, "properties": {
            "trail_number": n,
            "difficulty": diffs.most_common(1)[0][0] if diffs else None,
            "edge_count": len(chosen), "parts": parts,
            "stitched_gaps": len(extra_px),   # bounded straight connectors used (auditable)
            "unjoined_gaps": dropped,         # pieces left disconnected (too far to join honestly)
            "number_confidence": "high" if n >= 10 else "low",
            "source_name": "SFWDA AOP trail map 2015-03-11",
            "source_type": "community_raster",
            "review_status": "raster trace (2015 vintage); contiguous trail under hand-read markers; needs review before core/publish",
        }})
        stats.append((n, seeds_n, parts, len(chosen)))

    out = {"type": "FeatureCollection", "name": "sfwda_numbered_trails",
           "_meta": {"about": "Contiguous numbered trails stitched from the SFWDA raster trace + hand-read markers. One feature per trail number. Numbers/positions provisional (2015 vintage). Built by build_numbered_trails.py.",
                     "trails": len(feats)},
           "features": feats}
    (DATA / "sfwda_numbered_trails.geojson").write_text(json.dumps(out, indent=1))

    # stamp trail_number onto directly-tagged edges in the traced-trails layers
    for tgt in (DATA / "sfwda_traced_trails.geojson", PT / "sfwda_trails.geojson"):
        if not tgt.exists():
            continue
        fc = json.loads(tgt.read_text())
        for f in fc["features"]:
            eid = f["properties"].get("edge_id")
            if enum.get(eid) is not None:       # only edges that actually have a marker
                f["properties"]["trail_number"] = enum[eid]
        tgt.write_text(json.dumps(fc))

    # debug overlay: each number's contiguous trail in a palette colour + the number label
    for i, n in enumerate(numbers):
        col = PAL[i % len(PAL)]
        for eid in chosen_px[n]:
            pts = np.array(edges[eid]["px"], np.int32).reshape(-1, 1, 2)
            cv2.polylines(ov, [pts], False, col, 3)
        for (p0, p1) in extra_by_num.get(n, []):    # straight gap-connectors, dashed-ish
            cv2.line(ov, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), col, 2, cv2.LINE_AA)
        for eid in (e for e in chosen_px[n] if enum[e] == n):
            for mc in edges[eid]["marker_centroids"]:
                cv2.putText(ov, str(n), (int(mc[0]) + 4, int(mc[1]) - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)
                break
    cv2.imwrite(str(PT / "numbered_trails_overlay.png"), ov)

    multipart = [s for s in stats if s[2] > 1]
    print(f"built {len(feats)} contiguous numbered trails -> website/data/sfwda_numbered_trails.geojson")
    print(f"  fully contiguous (1 part): {sum(1 for s in stats if s[2]==1)}/{len(stats)}")
    if multipart:
        print(f"  still multi-part (gap in trace): {[ (s[0], s[2]) for s in multipart ]}")


if __name__ == "__main__":
    main()
