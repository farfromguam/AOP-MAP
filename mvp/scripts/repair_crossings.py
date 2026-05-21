#!/usr/bin/env python3
"""Repair contour-crossing artifacts in simplified contour GeoJSON.

Contours are isolines of one surface and can never cross. gdal_contour output
is topologically clean, but per-line Douglas-Peucker simplification (run for
file size) treats each contour independently and can push tightly-spaced
neighbours across each other on steep ground.

Because Douglas-Peucker only DELETES vertices, a simplified line is an exact
ordered subsequence of its raw line. So this pass detects the crossings and
restores the offending simplified segments to their raw (non-crossing)
geometry. Restoring a segment can expose a neighbouring crossing, so it
iterates until none remain. The restored spans are tiny -- only the steepest
spots -- so the file barely grows.

Pure stdlib: runs inside the ghcr.io/osgeo/gdal container.

Usage:
  repair_crossings.py --raw RAW.geojson --simplified DP.geojson --out OUT.geojson
"""
import argparse
import json

CELL = 0.0005       # spatial-hash cell, degrees (~45 m)
MAX_ITERS = 12


def parts_of(geom):
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return geom["coordinates"]
    return []


def seg_cross(p1, p2, p3, p4):
    """True if open segments p1-p2 and p3-p4 properly cross (not at a shared end)."""
    d = (p2[0]-p1[0])*(p4[1]-p3[1]) - (p2[1]-p1[1])*(p4[0]-p3[0])
    if d == 0:
        return False
    t = ((p3[0]-p1[0])*(p4[1]-p3[1]) - (p3[1]-p1[1])*(p4[0]-p3[0])) / d
    u = ((p3[0]-p1[0])*(p2[1]-p1[1]) - (p3[1]-p1[1])*(p2[0]-p1[0])) / d
    return 1e-9 < t < 1-1e-9 and 1e-9 < u < 1-1e-9


def detect(parts):
    """Find crossings between parts of different elevation.

    Returns ({part_index: set(segment_index)}, crossing_count).
    """
    grid = {}
    for li, pt in enumerate(parts):
        c = pt["work"]
        for si in range(len(c) - 1):
            a, b = c[si], c[si+1]
            for cx in range(int(min(a[0], b[0])//CELL), int(max(a[0], b[0])//CELL)+1):
                for cy in range(int(min(a[1], b[1])//CELL), int(max(a[1], b[1])//CELL)+1):
                    grid.setdefault((cx, cy), []).append((li, si))
    hits = {}
    seen = set()
    for bucket in grid.values():
        for i in range(len(bucket)):
            la, sa = bucket[i]
            for j in range(i+1, len(bucket)):
                lb, sb = bucket[j]
                if la == lb or parts[la]["elev"] == parts[lb]["elev"]:
                    continue
                ca, cb = parts[la]["work"], parts[lb]["work"]
                if not seg_cross(ca[sa], ca[sa+1], cb[sb], cb[sb+1]):
                    continue
                key = ((la, sa), (lb, sb)) if (la, sa) < (lb, sb) else ((lb, sb), (la, sa))
                if key in seen:
                    continue
                seen.add(key)
                hits.setdefault(la, set()).add(sa)
                hits.setdefault(lb, set()).add(sb)
    return hits, len(seen)


def _same(a, b):
    return abs(a[0]-b[0]) <= 1e-9 and abs(a[1]-b[1]) <= 1e-9


def raw_index_map(work, raw):
    """work is an ordered subsequence of raw -> index of each work vertex in raw."""
    idx = []
    j = 0
    for v in work:
        while j < len(raw) and not _same(raw[j], v):
            j += 1
        if j >= len(raw):
            return None
        idx.append(j)
        j += 1
    return idx


def restore(work, raw, ridx, flagged):
    """Rebuild work, expanding each flagged segment back to its raw vertices."""
    out = []
    for k in range(len(work) - 1):
        out.append(work[k])
        if k in flagged:
            out.extend(raw[ridx[k]+1:ridx[k+1]])
    out.append(work[-1])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--simplified", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.raw) as fh:
        raw_fc = json.load(fh)
    with open(args.simplified) as fh:
        dp_fc = json.load(fh)

    rf, df = raw_fc["features"], dp_fc["features"]
    if len(rf) != len(df):
        raise SystemExit("feature count mismatch: raw %d vs simplified %d"
                          % (len(rf), len(df)))

    # Flatten to parts; each part keeps its raw counterpart and a back-reference.
    parts = []
    feat_parts = []
    for fi in range(len(df)):
        rparts = parts_of(rf[fi]["geometry"])
        dparts = parts_of(df[fi]["geometry"])
        if len(rparts) != len(dparts):
            feat_parts.append(None)            # unexpected; leave feature as-is
            continue
        elev = df[fi]["properties"].get("elev_ft")
        idxs = []
        for pi in range(len(dparts)):
            parts.append({"elev": elev, "work": dparts[pi], "raw": rparts[pi]})
            idxs.append(len(parts) - 1)
        feat_parts.append(idxs)

    v_before = sum(len(p["work"]) for p in parts)
    initial = iters = 0
    for it in range(MAX_ITERS):
        hits, nc = detect(parts)
        if it == 0:
            initial = nc
        if not hits:
            break
        iters = it + 1
        for li, segs in hits.items():
            pt = parts[li]
            ridx = raw_index_map(pt["work"], pt["raw"])
            if ridx is None:
                continue
            pt["work"] = restore(pt["work"], pt["raw"], ridx, segs)

    _, final = detect(parts)
    v_after = sum(len(p["work"]) for p in parts)

    for fi, idxs in enumerate(feat_parts):
        if idxs is None:
            continue
        new = [parts[i]["work"] for i in idxs]
        geom = df[fi]["geometry"]
        geom["coordinates"] = new[0] if geom["type"] == "LineString" else new

    with open(args.out, "w") as fh:
        json.dump(dp_fc, fh)

    print("    repair: %d crossings -> %d (%d iterations); "
          "%d vertices restored to raw"
          % (initial, final, iters, v_after - v_before))
    if final:
        print("    WARNING: %d crossings remain after %d iterations"
              % (final, MAX_ITERS))


if __name__ == "__main__":
    main()
