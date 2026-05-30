#!/usr/bin/env python3
"""Export the trace layers to a single, pre-aligned, editable SVG.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

The 6x6 mesh warp is BAKED IN here so the graphics-program editor needs no manual
warping: the paper-map raster is rectified into the same local-meters frame as the
(already-georeferenced) vector layers, and everything is written as named SVG
layers. Edit the trails, then round-trip back with import_trace_svg.py.

Coordinate frame: local equirectangular metres, origin at the NW of the data
bounds, +x east, +y south (SVG convention). Re-import inverts this linear map —
no mesh warp on the way back. The exact projection params live in the SVG
<metadata> so import stays in lock-step.

Layers (Inkscape-labelled <g>):
  paper_map      rectified reference raster (embedded PNG; --paper) [lock; reference]
  osm_tracks     OSM highway=track/service lines              [reference]
  traced_trails  SFWDA extracted trail edges (edit these)     [EDIT]
  traced_markers difficulty markers + trail numbers           [reference]

Trail NUMBER is editable: every trail path carries `inkscape:label="<number>"`
(and a child <title>), so each trail shows in Inkscape's Objects panel named by
its number. Retype the label there to correct a number ("?" = none guessed yet);
import_trace_svg.py reads the label back as the authoritative trail number.

Output: brain/output/paper_trace/sfwda_trace_edit.svg
Run:    python3 mvp/scripts/export_trace_svg.py
"""
from __future__ import annotations
import base64, json, math
from pathlib import Path

import cv2
import numpy as np
from scipy.interpolate import griddata

from paper_trace_warp import PaperWarp

REPO = Path(__file__).resolve().parents[2]
PT = REPO / "brain/output/paper_trace"
DATA = REPO / "website/data"
SRC_PNG = REPO / "brain/import/community_trails/sfwda_aop_trail_map_2015-03-11.png"
OUT_SVG = PT / "sfwda_trace_edit.svg"
SAMPLE_STEP = 6        # source-pixel sampling stride for rectification
TARGET_W = 2200        # rectified raster width in px (resolution of the backdrop)

DIFF_COLOR = {"easy": "#1f9d3a", "moderate": "#2438c8", "difficult": "#111111",
              "extreme": "#f25e0d"}


def _xml_attr(s):
    """Escape a trail name for safe use inside an XML attribute value."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def norm_diff(d):
    """difficulty may be a string, a list (mixed edge), or None."""
    if isinstance(d, list):
        return d[0] if d else None
    return d


def vec_pixel_to_lnglat(warp, px, py):
    """Vectorised copy of PaperWarp.pixel_to_lnglat for numpy arrays."""
    W, H, n, cw = warp.W, warp.H, warp.n, warp.cw
    if cw == 270:
        Xc, Yc, Wc, Hc = py, W - px, H, W
    elif cw == 0:
        Xc, Yc, Wc, Hc = px, py, W, H
    elif cw == 90:
        Xc, Yc, Wc, Hc = H - py, px, H, W
    else:  # 180
        Xc, Yc, Wc, Hc = W - px, H - py, W, H
    u = np.clip(Xc / Wc, 0, 1.0); v = np.clip(Yc / Hc, 0, 1.0)
    gc = np.minimum(n - 1, (u * n).astype(int)); gr = np.minimum(n - 1, (v * n).astype(int))
    lu = u * n - gc; lv = v * n - gr
    g = np.array(warp.grid)            # (n+1, n+1, 2)
    p00 = g[gr, gc]; p10 = g[gr, gc + 1]; p11 = g[gr + 1, gc + 1]; p01 = g[gr + 1, gc]
    w00 = (1 - lu) * (1 - lv); w10 = lu * (1 - lv); w11 = lu * lv; w01 = (1 - lu) * lv
    lng = w00 * p00[..., 0] + w10 * p10[..., 0] + w11 * p11[..., 0] + w01 * p01[..., 0]
    lat = w00 * p00[..., 1] + w10 * p10[..., 1] + w11 * p11[..., 1] + w01 * p01[..., 1]
    return lng, lat


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Export trace layers to an editable, pre-aligned SVG.")
    ap.add_argument("--trails", default="sfwda_traced_trails.geojson", help="trail layer geojson in website/data")
    ap.add_argument("--osm", default="osm_aop_9patch.geojson", help="OSM geojson, or 'none' to omit the layer")
    ap.add_argument("--color", choices=["difficulty", "feature"], default="difficulty",
                    help="'feature' uses each trail's baked-in `color` (distinct per trail)")
    ap.add_argument("--paper", default=str(SRC_PNG),
                    help="reference raster to rectify as the backdrop. Any size: sampling is "
                         "scaled proportionally into the warp frame, so a newer render of the "
                         "same map (e.g. aop_official_trail_map_2025-11.png) drops in directly.")
    ap.add_argument("--out", default=str(OUT_SVG), help="output SVG path")
    args = ap.parse_args()
    warp = PaperWarp()
    g = np.array(warp.grid).reshape(-1, 2)
    lng_min, lng_max = g[:, 0].min(), g[:, 0].max()
    lat_min, lat_max = g[:, 1].min(), g[:, 1].max()
    lat0 = (lat_min + lat_max) / 2
    M_PER_DEG_LAT = 110540.0
    M_PER_DEG_LNG = 111320.0 * math.cos(math.radians(lat0))

    def to_m(lng, lat):                       # lng/lat -> local metres (x east, y south)
        return ((lng - lng_min) * M_PER_DEG_LNG, (lat_max - lat) * M_PER_DEG_LAT)
    width_m = (lng_max - lng_min) * M_PER_DEG_LNG
    height_m = (lat_max - lat_min) * M_PER_DEG_LAT
    PXM = TARGET_W / width_m                   # px per metre for the raster
    outW, outH = int(round(width_m * PXM)), int(round(height_m * PXM))

    # --- rectify the raster: backward-map output px -> source px via griddata ---
    # Sample in the warp's own pixel frame (so the normalised mesh applies), but scatter
    # the corresponding PAPER-image pixel coords. When the paper raster is a different size
    # than the alignment's image_pixel_size, this proportional scale lets a newer render of
    # the same map reuse the warp verbatim; when sizes match it is the identity.
    src = cv2.imread(str(args.paper))
    img_h, img_w = src.shape[:2]
    ys, xs = np.mgrid[0:warp.H:SAMPLE_STEP, 0:warp.W:SAMPLE_STEP]
    sx = xs.ravel().astype(float); sy = ys.ravel().astype(float)
    lng, lat = vec_pixel_to_lnglat(warp, sx, sy)
    mx, my = to_m(lng, lat)
    opx, opy = mx * PXM, my * PXM              # source samples placed in output px
    sx_img = sx / warp.W * img_w               # warp-frame px -> paper-image px
    sy_img = sy / warp.H * img_h
    grid_x, grid_y = np.meshgrid(np.arange(outW), np.arange(outH))
    map_x = griddata((opx, opy), sx_img, (grid_x, grid_y), method="linear").astype(np.float32)
    map_y = griddata((opx, opy), sy_img, (grid_x, grid_y), method="linear").astype(np.float32)
    map_x = np.nan_to_num(map_x, nan=-1); map_y = np.nan_to_num(map_y, nan=-1)
    rect = cv2.remap(src, map_x, map_y, cv2.INTER_LINEAR,
                     borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
    ok, buf = cv2.imencode(".png", rect)
    raster_b64 = base64.b64encode(buf).decode()

    # --- vector layers (already in lng/lat) -> metres ---
    def load(fn):
        p = DATA / fn
        return json.loads(p.read_text()) if p.exists() else {"features": []}
    osm = load(args.osm) if args.osm != "none" else {"features": []}
    trails = load(args.trails)
    markers = load("sfwda_traced_markers.geojson")

    def path_d(coords):
        pts = [to_m(x, y) for x, y in coords]
        return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts)

    def lines_of(fc, want=None):
        out = []
        for f in fc["features"]:
            gtype = f["geometry"]["type"]; props = f["properties"]
            if want and props.get("highway") not in want and "highway" in props:
                continue
            if gtype == "LineString":
                out.append((f["geometry"]["coordinates"], props))
            elif gtype == "MultiLineString":
                for part in f["geometry"]["coordinates"]:
                    out.append((part, props))
        return out

    osm_paths = []
    for coords, p in lines_of(osm, want={"track", "service", "unclassified"}):
        if p.get("highway") in (None,):  # skip the boundary polygon / unrelated
            continue
        osm_paths.append(f'<path class="osm" d="{path_d(coords)}" />')

    trail_paths = []
    for coords, p in lines_of(trails):
        # The baked `color` is authoritative — import bakes it from the user's
        # hand-set strokes (incl. orange roads, which sit off the difficulty axis),
        # so re-export round-trips the colours. Fall back to difficulty for raw
        # layers that carry no baked colour.
        if p.get("color") and (args.color == "feature" or p.get("kind") == "road"):
            col = p["color"]
        else:
            col = DIFF_COLOR.get(norm_diff(p.get("difficulty")), "#888888")
        tn = p.get("trail_number")
        fid = p.get("id") or f"trail_e{p.get('edge_id')}"
        # The trail NAME is the editable handle — ANY string now ("JW2",
        # "Riot Hill", "15"), not just a number. It rides on BOTH inkscape:label
        # (Inkscape's Objects panel) and serif:id (Affinity Designer's name
        # channel) plus a child <title>, so each trail shows named in whichever
        # editor the user opens — double-click the row to retype it.
        # import_trace_svg.py reads those channels back as authoritative; "?" =
        # not yet named. (data-* / id kept as a fallback for un-edited files.)
        name = p.get("name") or (str(tn) if tn is not None else "?")
        label = _xml_attr(name)
        trail_paths.append(
            f'<path class="trail" id="{fid}_n{tn if tn is not None else ""}" '
            f'inkscape:label="{label}" serif:id="{label}" '
            f'stroke="{col}" data-difficulty="{norm_diff(p.get("difficulty")) or ""}" '
            f'data-trail-number="{tn if tn is not None else ""}" d="{path_d(coords)}">'
            f'<title>{label}</title></path>')

    marker_els = []
    for f in markers["features"]:
        p = f["properties"]; lngc, latc = f["geometry"]["coordinates"]
        x, y = to_m(lngc, latc); col = DIFF_COLOR.get(norm_diff(p.get("difficulty")), "#888")
        tn = p.get("trail_number"); d = norm_diff(p.get("difficulty"))
        r = 9
        if d == "easy":
            shape = f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}" />'
        elif d == "moderate":
            shape = f'<rect x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" fill="{col}" />'
        else:
            shape = (f'<polygon points="{x:.1f},{y-r:.1f} {x-r:.1f},{y+r:.1f} {x+r:.1f},{y+r:.1f}" '
                     f'fill="{col}" />')
        label = (f'<text x="{x:.1f}" y="{y+3:.1f}" text-anchor="middle" font-size="10" '
                 f'fill="#fff">{tn}</text>' if tn is not None else "")
        marker_els.append(f'<g class="marker" data-trail-number="{tn if tn is not None else ""}" '
                          f'data-difficulty="{d or ""}">{shape}{label}</g>')

    meta = {"projection": "local_equirectangular_metres",
            "lng_min": lng_min, "lat_max": lat_max,
            "m_per_deg_lng": M_PER_DEG_LNG, "m_per_deg_lat": M_PER_DEG_LAT,
            "width_m": width_m, "height_m": height_m,
            "note": "SVG user units = metres. import_trace_svg.py inverts this linear map (no mesh warp)."}

    INK = ('xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           'xmlns:serif="http://www.serif.com/"')
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" {INK}
     width="{width_m:.1f}" height="{height_m:.1f}" viewBox="0 0 {width_m:.2f} {height_m:.2f}">
<metadata id="aop_proj">{json.dumps(meta)}</metadata>
<style>
 .osm {{ fill:none; stroke:#b07a2a; stroke-width:1.2; opacity:0.7; }}
 .trail {{ fill:none; stroke-width:2.2; }}
</style>
<g inkscape:groupmode="layer" inkscape:label="paper_map" sodipodi:insensitive="true"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd">
  <image x="0" y="0" width="{width_m:.2f}" height="{height_m:.2f}" preserveAspectRatio="none"
         xlink:href="data:image/png;base64,{raster_b64}" />
</g>
<g inkscape:groupmode="layer" inkscape:label="osm_tracks">
  {"".join(osm_paths)}
</g>
<g inkscape:groupmode="layer" inkscape:label="traced_trails">
  {"".join(trail_paths)}
</g>
<g inkscape:groupmode="layer" inkscape:label="traced_markers">
  {"".join(marker_els)}
</g>
</svg>'''
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = REPO / out_path
    out_path.write_text(svg)
    print(f"wrote {out_path}")
    print(f"  paper {Path(args.paper).name} ({img_w}x{img_h}px)")
    print(f"  frame {width_m:.0f} x {height_m:.0f} m | raster {outW}x{outH}px | "
          f"osm {len(osm_paths)} trails {len(trail_paths)} markers {len(marker_els)}")


if __name__ == "__main__":
    main()
