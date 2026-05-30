#!/usr/bin/env python3
"""Stage C/D/E: vectorize the isolated trail mask into georeferenced polylines.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

Pipeline (runs extract_paper_trails first for the mask + markers):
  C. Gap-bridge: close the small breaks the lifted markers left in the lines.
  D. Skeletonize to 1 px centerlines, walk the skeleton into a graph
     (nodes = endpoints + junctions, edges = the degree-2 chains between them),
     simplify each edge (Douglas-Peucker via shapely).
  E. Associate each detected marker with its nearest edge -> the edge inherits
     {trail_number(None yet), difficulty}.
  F. Warp every vertex to lng/lat with paper_trace_warp.PaperWarp.

Output: brain/output/paper_trace/sfwda_trails.geojson  (LineStrings, raw zone).
Debug:  brain/output/paper_trace/skeleton.png, trails_vector_overlay.png

Run: python3 mvp/scripts/vectorize_paper_trails.py
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
from skimage.morphology import skeletonize
from shapely.geometry import LineString, Point

import extract_paper_trails as ex
from paper_trace_warp import PaperWarp

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "brain/output/paper_trace"

SIMPLIFY_PX = 2.0       # Douglas-Peucker tolerance in pixels
MIN_EDGE_PX = 12        # drop chains shorter than this (specks / stubs)
BRIDGE_PX = 19          # close kernel to bridge marker-sized gaps


def build_trail_mask():
    """Re-run the extract stage and return (trail mask, markers, image size)."""
    bgr = cv2.imread(str(ex.SRC))
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    chrome = ex.chrome_mask(bgr.shape)
    gmask, greens = ex.detect_color_markers(hsv, chrome, "green")
    bmask, blues = ex.detect_color_markers(hsv, chrome, "blue")
    color = cv2.bitwise_or(gmask, bmask)
    tmask, tris = ex.detect_triangles(gray, chrome, color)
    marker_mask = cv2.bitwise_or(color, tmask)
    trails, _boundary, _dark = ex.isolate_trails(gray, chrome, marker_mask)
    return trails, greens + blues + tris, bgr.shape[1], bgr.shape[0], bgr


def neighbors(y, x, h, w):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                yield ny, nx


def walk_skeleton(skel):
    """Return list of edges; each edge is a list of (x, y) pixel points.

    Nodes are skeleton pixels whose neighbor-count != 2 (endpoints / junctions).
    Edges are the degree-2 chains connecting them. Pure loops (no node) are
    emitted as closed chains.
    """
    h, w = skel.shape
    ys, xs = np.where(skel)
    pts = set(zip(ys.tolist(), xs.tolist()))
    deg = {}
    for (y, x) in pts:
        deg[(y, x)] = sum(1 for n in neighbors(y, x, h, w) if n in pts)
    nodes = {p for p in pts if deg[p] != 2}

    edges = []
    visited_edge = set()  # frozenset of the two pixels of a traversed step

    def trace_from(node, first):
        path = [node, first]
        visited_edge.add(frozenset((node, first)))
        prev, cur = node, first
        while cur not in nodes:
            nxt = None
            for n in neighbors(cur[0], cur[1], h, w):
                if n in pts and n != prev and frozenset((cur, n)) not in visited_edge:
                    nxt = n
                    break
            if nxt is None:
                break
            visited_edge.add(frozenset((cur, nxt)))
            path.append(nxt)
            prev, cur = cur, nxt
        return path

    for node in nodes:
        for n in neighbors(node[0], node[1], h, w):
            if n in pts and frozenset((node, n)) not in visited_edge:
                path = trace_from(node, n)
                edges.append(path)

    # closed loops with no node: walk any unvisited degree-2 pixel
    for p in pts:
        if deg[p] != 2:
            continue
        started = [n for n in neighbors(p[0], p[1], h, w)
                   if n in pts and frozenset((p, n)) not in visited_edge]
        if started:
            edges.append(trace_from(p, started[0]))

    # convert (y,x) -> (x,y)
    return [[(x, y) for (y, x) in e] for e in edges]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    trails, markers, W, H, bgr = build_trail_mask()

    bridged = cv2.morphologyEx(
        trails, cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (BRIDGE_PX, BRIDGE_PX)))
    skel = skeletonize(bridged > 0)
    cv2.imwrite(str(OUT / "skeleton.png"), (skel * 255).astype(np.uint8))

    edges = walk_skeleton(skel)

    # simplify in pixel space, drop stubs
    polylines_px = []
    for e in edges:
        if len(e) < 2:
            continue
        ls = LineString(e)
        if ls.length < MIN_EDGE_PX:
            continue
        s = ls.simplify(SIMPLIFY_PX, preserve_topology=False)
        coords = list(s.coords)
        if len(coords) >= 2:
            polylines_px.append(coords)

    # marker -> nearest edge association
    def nearest_edge_idx(mx, my):
        best, bi = 1e18, -1
        for i, coords in enumerate(polylines_px):
            d = LineString(coords).distance(Point(mx, my))
            if d < best:
                best, bi = d, i
        return bi, best
    edge_markers = {i: [] for i in range(len(polylines_px))}
    for m in markers:
        mx, my = m["centroid_px"]
        bi, dist = nearest_edge_idx(mx, my)
        if bi >= 0 and dist <= 40:   # within ~40 px of the line
            edge_markers[bi].append(m)

    # dump the pixel graph so the contiguous-trail builder (build_numbered_trails.py)
    # can walk edge connectivity without re-skeletonizing. Nodes = snapped edge
    # endpoints; each edge records its endpoints, pixel polyline, difficulty, and
    # the centroids of markers sitting on it (used to inherit trail numbers).
    node_ids = {}
    def node_id(x, y):
        key = (int(round(x)), int(round(y)))
        if key not in node_ids:
            node_ids[key] = len(node_ids)
        return node_ids[key]
    graph_edges = []
    for i, coords in enumerate(polylines_px):
        a = node_id(*coords[0]); b = node_id(*coords[-1])
        ms = edge_markers[i]
        graph_edges.append({
            "id": i, "a": a, "b": b,
            "px": [[round(x, 1), round(y, 1)] for (x, y) in coords],
            "length_px": round(LineString(coords).length, 1),
            "difficulty": (sorted({m["difficulty"] for m in ms}) or [None])[0]
                          if len({m["difficulty"] for m in ms}) <= 1 else None,
            "marker_centroids": [[round(m["centroid_px"][0], 1), round(m["centroid_px"][1], 1)] for m in ms],
        })
    nodes_xy = [None] * len(node_ids)
    for (x, y), nid in node_ids.items():
        nodes_xy[nid] = [x, y]
    (OUT / "trail_graph.json").write_text(json.dumps({
        "image_px": [W, H], "nodes": nodes_xy, "edges": graph_edges}))

    # warp -> GeoJSON
    warp = PaperWarp()
    feats = []
    for i, coords in enumerate(polylines_px):
        ll = [warp.pixel_to_lnglat(x, y) for (x, y) in coords]
        ms = edge_markers[i]
        diffs = sorted({m["difficulty"] for m in ms})
        feats.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": ll},
            "properties": {
                "edge_id": i,
                "difficulty": diffs[0] if len(diffs) == 1 else (diffs or None),
                "marker_count": len(ms),
                "trail_number": None,           # OCR + human-verify, deferred
                "source_name": "SFWDA AOP trail map 2015-03-11",
                "source_type": "community_raster",
                "confidence": "position high (mapping-system export)",
                "review_status": "raster trace (2015 vintage); needs review before core/publish",
            },
        })
    fc = {"type": "FeatureCollection", "name": "sfwda_paper_trails", "features": feats}
    (OUT / "sfwda_trails.geojson").write_text(json.dumps(fc))

    # debug overlay: vectorized lines in magenta + simplify vertices
    ov = bgr.copy()
    for coords in polylines_px:
        pts = np.array(coords, np.int32).reshape(-1, 1, 2)
        cv2.polylines(ov, [pts], False, (255, 0, 255), 2)
    cv2.imwrite(str(OUT / "trails_vector_overlay.png"), ov)

    total_verts = sum(len(c) for c in polylines_px)
    print(json.dumps({
        "edges": len(polylines_px),
        "vertices": total_verts,
        "markers_assigned": sum(len(v) for v in edge_markers.values()),
        "markers_total": len(markers),
    }, indent=2))
    print(f"-> {(OUT / 'sfwda_trails.geojson').relative_to(REPO)}")


if __name__ == "__main__":
    main()
