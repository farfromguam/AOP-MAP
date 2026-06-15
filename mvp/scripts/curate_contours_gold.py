#!/usr/bin/env python3
"""Curate the lean GOLD contour layer from the full SILVER set.

Why: the full contour set is ~13 MB / ~560k vertices, and ~88% of those vertices
are the dense MINOR (idx==0) lines out in the 8 surrounding patches — county
hillside nobody reads on an RC-park map. But the INDEX (idx==1, labelled, every
50 ft) lines are useful context across the whole 9-patch.

So GOLD (what the viewer serves) keeps:
  - every INDEX line (idx==1) WHOLE, across the full 9-patch  (the readable context)
  - the MINOR lines (idx==0) only INSIDE the park center cell, clipped to it
    (the fine detail, where riders actually read topo at scale)

SILVER stays the full-detail, full-extent accepted set (the promote-from source).
The viewer reads `gold_aop_contours.geojson` and filters by `idx`, so no JS change:
`contours-index` still draws everywhere; `contours-minor` now only has park data.

Lineage: raw/aop_contours.geojson --(build_contours.sh)--> silver_aop_contours.geojson
         --(this script)--> gold_aop_contours.geojson (served).

Center cell (park working-envelope bbox) from research/aop_data_bounds.md.

Usage:
  python3 mvp/scripts/curate_contours_gold.py \
      --in website/data/silver_aop_contours.geojson \
      --out website/data/gold_aop_contours.geojson
"""
import argparse, json, sys
from shapely.geometry import shape, box, mapping, LineString, MultiLineString

# Park working-envelope bbox (the 9-patch CENTER cell): W, S, E, N.
# research/aop_data_bounds.md "Center Cell Bbox".
CELL_W, CELL_S, CELL_E, CELL_N = -85.761008221, 35.084085624, -85.739081159, 35.101007060
PRECISION = 6  # decimal places (~0.1 m) — matches the source; no visible loss


def round_coords(geom):
    """Round a (Multi)LineString's coords to PRECISION decimals to keep bytes lean."""
    def r(seq):
        return [[round(x, PRECISION), round(y, PRECISION)] for x, y in seq]
    if geom["type"] == "LineString":
        geom["coordinates"] = r(geom["coordinates"])
    elif geom["type"] == "MultiLineString":
        geom["coordinates"] = [r(line) for line in geom["coordinates"]]
    return geom


def clip_to_cell(geom):
    """Intersect a line geometry with the center cell; return GeoJSON geom or None."""
    clipped = shape(geom).intersection(box(CELL_W, CELL_S, CELL_E, CELL_N))
    if clipped.is_empty:
        return None
    # Keep only line parts (a corner-touch can yield a Point — drop it).
    if isinstance(clipped, LineString):
        return mapping(clipped)
    if isinstance(clipped, MultiLineString):
        return mapping(clipped)
    # GeometryCollection: keep the line members only.
    lines = [g for g in getattr(clipped, "geoms", []) if isinstance(g, (LineString, MultiLineString))]
    if not lines:
        return None
    merged = []
    for g in lines:
        if isinstance(g, LineString):
            merged.append(list(g.coords))
        else:
            merged.extend([list(p.coords) for p in g.geoms])
    return {"type": "MultiLineString", "coordinates": merged}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="website/data/silver_aop_contours.geojson")
    ap.add_argument("--out", dest="out", default="website/data/gold_aop_contours.geojson")
    args = ap.parse_args()

    d = json.load(open(args.inp, encoding="utf-8"))
    feats = d.get("features", [])
    out_feats = []
    kept_index = kept_minor = dropped_minor = 0
    for f in feats:
        idx = (f.get("properties") or {}).get("idx")
        geom = f.get("geometry") or {}
        if idx == 1:
            # Index/major line — keep whole, across the full 9-patch.
            out_feats.append({"type": "Feature", "properties": f["properties"],
                              "geometry": round_coords(geom)})
            kept_index += 1
        elif idx == 0:
            # Minor line — keep only the part inside the park cell.
            clipped = clip_to_cell(geom)
            if clipped is None:
                dropped_minor += 1
                continue
            out_feats.append({"type": "Feature", "properties": f["properties"],
                              "geometry": round_coords(clipped)})
            kept_minor += 1
        else:
            # Unknown idx — keep whole (permissive; don't silently drop).
            out_feats.append({"type": "Feature", "properties": f["properties"],
                              "geometry": round_coords(geom)})

    out = {
        "type": "FeatureCollection",
        "name": d.get("name", "aop_contours"),
        "features": out_feats,
        "_meta": {
            "maturity": "gold",
            "group": "Lidar contours",
            "locked": True,
            "maturity_note": ("gold — served production contour layer: ALL index (major) lines "
                              "across the 9-patch + minor lines clipped to the park center cell. "
                              "Full-detail set is silver_aop_contours.geojson. Regenerate via "
                              "mvp/scripts/curate_contours_gold.py."),
            "derived_from": "silver_aop_contours.geojson",
            "curate": {"minor_clip_bbox": [CELL_W, CELL_S, CELL_E, CELL_N], "precision": PRECISION}
        }
    }
    json.dump(out, open(args.out, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(f"wrote {args.out}: {len(out_feats):,} features "
          f"(index kept whole: {kept_index:,}; minor kept-in-park: {kept_minor:,}; "
          f"minor dropped-outside: {dropped_minor:,})", flush=True)


if __name__ == "__main__":
    sys.exit(main())
