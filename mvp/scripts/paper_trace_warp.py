#!/usr/bin/env python3
"""Pixel -> lng/lat for the SFWDA paper map, replicating the viewer's warp.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

The viewer (website/index.html) georeferences the raster by:
  1. rotating the image by `orientation_cw_degrees` into a display canvas
     (rotateToCanvas), then
  2. slicing that canvas row-major into an N x N tile mesh and binding each
     tile's 4 corners to the `grid_NxN` control points, bilinear within a cell
     (sliceCanvasN + tileCornerCoords + the image source's 4-corner interp).

This module reproduces that exact transform so a traced pixel coordinate lands
where the viewer would draw it -- the alignment JSON stays the single authority;
we do NOT fit a new transform. Used to warp detected markers and (later) the
vectorized trail polylines into the same world coordinates.

CLI: python3 mvp/scripts/paper_trace_warp.py
     -> reads brain/output/paper_trace/markers.json
     -> writes brain/output/paper_trace/sfwda_markers.geojson  (+ self-check)
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ALIGN = REPO / "website/data/sfwda_raster_alignment.json"
OUT = REPO / "brain/output/paper_trace"


class PaperWarp:
    def __init__(self, align_path: Path = ALIGN):
        data = json.loads(Path(align_path).read_text())
        self.W, self.H = data["image_pixel_size"]            # [2500, 1817]
        self.cw = int(data.get("orientation_cw_degrees", 0)) % 360
        n = None
        for k in data:
            if k.startswith("grid_") and "x" in k:
                n = int(k.split("_")[1].split("x")[0])
        if n is None:
            raise ValueError("no grid_NxN in alignment json")
        self.n = n
        self.grid = data[f"grid_{n}x{n}"]                    # (n+1)x(n+1) [lng,lat]

    def _to_canvas(self, px, py):
        """Image pixel -> rotated display-canvas coords + canvas dims."""
        W, H, cw = self.W, self.H, self.cw
        if cw == 0:
            return px, py, W, H
        if cw == 90:
            return H - py, px, H, W
        if cw == 180:
            return W - px, H - py, W, H
        if cw == 270:
            return py, W - px, H, W
        raise ValueError(f"unsupported orientation {cw}")

    def pixel_to_lnglat(self, px, py):
        Xc, Yc, Wc, Hc = self._to_canvas(px, py)
        n, g = self.n, self.grid
        u = min(max(Xc / Wc, 0.0), 1.0)
        v = min(max(Yc / Hc, 0.0), 1.0)
        gc = min(n - 1, int(u * n))
        gr = min(n - 1, int(v * n))
        lu = u * n - gc
        lv = v * n - gr
        p00, p10 = g[gr][gc], g[gr][gc + 1]
        p11, p01 = g[gr + 1][gc + 1], g[gr + 1][gc]
        lng = (1-lu)*(1-lv)*p00[0] + lu*(1-lv)*p10[0] + lu*lv*p11[0] + (1-lu)*lv*p01[0]
        lat = (1-lu)*(1-lv)*p00[1] + lu*(1-lv)*p10[1] + lu*lv*p11[1] + (1-lu)*lv*p01[1]
        return [round(lng, 7), round(lat, 7)]


def _self_check(warp: PaperWarp):
    """Image corners must land on the alignment NW/NE/SE/SW control points."""
    W, H, g, n = warp.W, warp.H, warp.grid, warp.n
    named = {"NW": g[0][0], "NE": g[0][n], "SE": g[n][n], "SW": g[n][0]}
    corners = {
        "TL(0,0)": warp.pixel_to_lnglat(0, 0),
        "TR(W,0)": warp.pixel_to_lnglat(W, 0),
        "BR(W,H)": warp.pixel_to_lnglat(W, H),
        "BL(0,H)": warp.pixel_to_lnglat(0, H),
    }
    print("self-check (image corner -> lng/lat):")
    for k, v in corners.items():
        match = next((nm for nm, p in named.items()
                      if abs(p[0]-v[0]) < 1e-4 and abs(p[1]-v[1]) < 1e-4), "??")
        print(f"  {k} -> {v}  == grid {match}")


def main():
    warp = PaperWarp()
    _self_check(warp)
    summary = json.loads((OUT / "markers.json").read_text())
    feats = []
    for m in summary["markers"]:
        px, py = m["centroid_px"]
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": warp.pixel_to_lnglat(px, py)},
            "properties": {
                "marker_type": m["type"],
                "difficulty": m["difficulty"],
                "trail_number": None,     # OCR + human-verify pass, deferred
                "source_name": "SFWDA AOP trail map 2015-03-11",
                "source_type": "community_raster",
                "confidence": "position high (mapping-system export); number pending",
                "review_status": "raster marker; number unread; needs review before core/publish",
                "centroid_px": [px, py],
            },
        })
    fc = {"type": "FeatureCollection",
          "name": "sfwda_paper_markers",
          "features": feats}
    out = OUT / "sfwda_markers.geojson"
    out.write_text(json.dumps(fc))
    print(f"\nwrote {len(feats)} georeferenced markers -> {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
