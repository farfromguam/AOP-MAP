#!/usr/bin/env python3
"""Re-import an edited trace SVG back to georeferenced GeoJSON.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

Reads the `traced_trails` layer from an SVG produced by export_trace_svg.py
(after you reconnect / clean trails in a graphics program), inverts the linear
metres->lng/lat projection recorded in the SVG <metadata> (NO mesh warp — the warp
was baked in at export), and writes normalized LineString GeoJSON. Trail number +
difficulty are carried from each path's id / data-* attributes.

Handles M/L/H/V/Z path commands (absolute + relative) and composes any
transform= on the path or its ancestor groups (Inkscape adds one when you move a
whole path). Curve commands (C/S/Q/T/A) are reduced to their endpoints.

Usage: python3 mvp/scripts/import_trace_svg.py [path/to/edited.svg]
Output: website/data/sfwda_trails_edited.geojson
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from paper_trace_warp import PaperWarp

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SVG = REPO / "brain/output/paper_trace/sfwda_trace_edit.svg"
OUT = REPO / "website/data/sfwda_trails_edited.geojson"
SVG_NS = "http://www.w3.org/2000/svg"
INK_NS = "http://www.inkscape.org/namespaces/inkscape"
SERIF_NS = "http://www.serif.com/"          # Affinity Designer object-name channel

NUM = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def parse_transform(s):
    """Return a 2x3 affine [a,b,c,d,e,f] for a transform attribute (matrix/translate/scale)."""
    m = [1, 0, 0, 1, 0, 0]
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", s or ""):
        v = [float(x) for x in NUM.findall(args)]
        if name == "matrix" and len(v) == 6:
            t = v
        elif name == "translate":
            t = [1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0]
        elif name == "scale":
            t = [v[0], 0, 0, (v[1] if len(v) > 1 else v[0]), 0, 0]
        else:
            continue
        a, b, c, d, e, f = m; a2, b2, c2, d2, e2, f2 = t      # m * t
        m = [a*a2 + c*b2, b*a2 + d*b2, a*c2 + c*d2, b*c2 + d*d2, a*e2 + c*f2 + e, b*e2 + d*f2 + f]
    return m


def apply(mat, x, y):
    a, b, c, d, e, f = mat
    return (a*x + c*y + e, b*x + d*y + f)


def path_points(d):
    """Tokenise an SVG path 'd' into a list of polylines (lists of (x,y)), absolute."""
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", d)
    polys, cur, x, y, start = [], [], 0.0, 0.0, None
    i, cmd = 0, None
    def nxt():
        nonlocal i
        val = float(tokens[i]); i += 1; return val
    while i < len(tokens):
        t = tokens[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t; i += 1
        rel = cmd.islower(); C = cmd.upper()
        if C == "M":
            nx, ny = nxt(), nxt()
            x, y = (x+nx, y+ny) if rel else (nx, ny)
            if cur: polys.append(cur)
            cur = [(x, y)]; start = (x, y); cmd = "l" if rel else "L"
        elif C == "L":
            nx, ny = nxt(), nxt(); x, y = (x+nx, y+ny) if rel else (nx, ny); cur.append((x, y))
        elif C == "H":
            nx = nxt(); x = x+nx if rel else nx; cur.append((x, y))
        elif C == "V":
            ny = nxt(); y = y+ny if rel else ny; cur.append((x, y))
        elif C in ("C", "S", "Q", "T"):                 # curve -> keep endpoint
            n = {"C": 6, "S": 4, "Q": 4, "T": 2}[C]; vals = [nxt() for _ in range(n)]
            ex, ey = vals[-2], vals[-1]; x, y = (x+ex, y+ey) if rel else (ex, ey); cur.append((x, y))
        elif C == "A":
            vals = [nxt() for _ in range(7)]; ex, ey = vals[-2], vals[-1]
            x, y = (x+ex, y+ey) if rel else (ex, ey); cur.append((x, y))
        elif C == "Z":
            if cur and start: cur.append(start)
        else:
            i += 1
    if cur: polys.append(cur)
    return polys


def main():
    svg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SVG
    tree = ET.parse(svg_path); root = tree.getroot()

    # Projection is recomputed from the alignment (deterministic) rather than trusting
    # the SVG <metadata>, which graphics editors strip. The inverse is proportional in
    # lng/lat over the viewBox, so any uniform rescale the editor applies cancels out.
    grid = np.array(PaperWarp().grid).reshape(-1, 2)
    lng_min, lng_max = float(grid[:, 0].min()), float(grid[:, 0].max())
    lat_min, lat_max = float(grid[:, 1].min()), float(grid[:, 1].max())
    vb = [float(x) for x in re.split(r"[ ,]+", (root.get("viewBox") or "").strip())]
    if len(vb) == 4:
        vbx, vby, vbw, vbh = vb
    else:                       # no viewBox: fall back to width/height
        vbx, vby = 0.0, 0.0
        vbw = float(re.findall(NUM, root.get("width") or "1")[0])
        vbh = float(re.findall(NUM, root.get("height") or "1")[0])

    def to_lnglat(x, y):
        fx = (x - vbx) / vbw; fy = (y - vby) / vbh
        return [round(lng_min + fx * (lng_max - lng_min), 7),
                round(lat_max - fy * (lat_max - lat_min), 7)]

    def extract(layer_id, source):
        layer = None
        for g in root.iter(f"{{{SVG_NS}}}g"):
            if g.get("id") == layer_id or g.get(f"{{{INK_NS}}}label") == layer_id:
                layer = g; break
        if layer is None:
            return []
        out = []
        def walk(el, mat):
            mat = compose(mat, parse_transform(el.get("transform")))
            tag = el.tag.split("}")[-1]
            if tag in ("path", "polyline"):
                if tag == "polyline":
                    pts = [tuple(map(float, p.split(","))) for p in
                           re.findall(r"[-+\d.eE]+,[-+\d.eE]+", el.get("points", ""))]
                    polys = [pts] if pts else []
                else:
                    polys = path_points(el.get("d", ""))
                # Name precedence: the human-editable object name wins (what the
                # user retypes in the editor's layers panel). A name is ANY string
                # now — "JW2", "Riot Hill", "GWT" — not just a number. Per the
                # user's rule, import every typed name EXCEPT the "?" placeholder.
                # Fall back to data-trail-number / id for un-relabelled files.
                name = _editable_name(el)
                if name is None:
                    fb = (el.get("data-trail-number") or _from_id(el.get("id")) or "").strip()
                    name = fb if fb and fb != "?" else None
                num = int(name) if (name or "").isdigit() else None
                # The colour the user HAND-SET in the editor is authoritative.
                # green/blue/black -> difficulty (Easy/Moderate/Difficult);
                # orange -> kind='road' (roads are not rated). reattach_from_markers
                # / number-band only fill what a trail was left uncoloured. Without
                # this the import threw the user's colours away and re-derived
                # everything from markers -> named trails went grey.
                cls = _stroke_class(el)
                is_road = cls == "road"
                diff = None if is_road else cls
                for poly in polys:
                    if len(poly) < 2:
                        continue
                    coords = [to_lnglat(*apply(mat, px, py)) for px, py in poly]
                    out.append({"type": "Feature",
                                "geometry": {"type": "LineString", "coordinates": coords},
                                "properties": {"trail_number": num,
                                               # name: the typed string ("JW2", "Riot Hill", "15")
                                               # or None. Carried straight through; numeric names
                                               # also populate trail_number above.
                                               "name": name,
                                               # kind: 'road' (orange) features sit off the difficulty
                                               # axis — no rating, no marker number inheritance.
                                               "kind": "road" if is_road else "trail",
                                               # _num_locked: an explicit human name is authoritative;
                                               # reattach_from_markers must not relabel it. Stripped below.
                                               "_num_locked": name is not None,
                                               "difficulty": diff, "source": source,
                                               "review_status": "hand-edited; normalized from SVG"}})
            for child in el:
                walk(child, mat)
        walk(layer, [1, 0, 0, 1, 0, 0])
        return out

    trails = extract("traced_trails", "sfwda_trace_edited")
    osm = extract("osm_tracks", "osm_edited")
    if not trails and not osm:
        sys.exit("no 'traced_trails' or 'osm_tracks' layer found in SVG")

    # Re-attach trail_number + difficulty from the (unchanged) markers by proximity —
    # graphics editors strip data-* and recolour strokes, so the markers are the
    # authority. Applied to BOTH sources so the merged network is numbered uniformly
    # at one level (an OSM track that runs under a trail's markers inherits its number).
    merged = trails + osm
    reattach_from_markers(merged, lat_min, lat_max)
    for i, f in enumerate(merged):
        p = f["properties"]
        p["id"] = f"{p['source'].split('_')[0]}-{i}"
        # Name precedence: a user-typed name (any string — "JW2", "Riot Hill")
        # wins; an unnamed numeric trail falls back to its number so the label
        # channel still carries something. None stays unnamed.
        p["name"] = p.get("name") or (str(p["trail_number"]) if p["trail_number"] is not None else None)
        p.pop("_num_locked", None)          # internal flag — not persisted
    assign_difficulty(merged)   # marker difficulty -> number-band fallback
    assign_colors(merged)       # green / blue / black by difficulty

    # the cleaned SFWDA-only trails (compat with the prior single-layer output)
    OUT.write_text(json.dumps({"type": "FeatureCollection", "name": "sfwda_trails_edited",
                               "features": trails}, indent=1))
    # the MERGED authoritative network — SFWDA trails + OSM tracks at one level
    NET = REPO / "website/data/aop_trail_network.geojson"
    NET.write_text(json.dumps({"type": "FeatureCollection", "name": "aop_trail_network",
        "_meta": {"about": "Merged authoritative AOP trail network: hand-cleaned SFWDA "
                  "traced trails + hand-cleaned OSM tracks, at one level, re-imported from "
                  + svg_path.name + ". Numbers/difficulty re-attached from the markers. "
                  "This is the new truth; re-export for further intersection cleanup.",
                  "sfwda_trails": len(trails), "osm_tracks": len(osm)},
        "features": merged}, indent=1))
    nnum = sum(1 for f in merged if f["properties"]["trail_number"] is not None)
    print(f"imported {len(trails)} SFWDA trails + {len(osm)} OSM tracks = {len(merged)} edges "
          f"({nnum} numbered) -> {NET.relative_to(REPO)}")


DIFF_COLOR = {"easy": "#1f9d3a", "moderate": "#2438c8", "difficult": "#111111"}
UNKNOWN_COLOR = "#888888"
ROAD_COLOR = "#f25e0d"           # orange — roads are not a difficulty, a separate kind

# RGB anchors for classifying a hand-set stroke colour. Nearest anchor wins, so a
# slightly-off pick from the editor still lands right. "road" (orange) is NOT a
# difficulty — it flags the feature as a road. None = grey = "still unknown".
_DIFF_ANCHORS = {
    "easy": (31, 157, 58),       # green  #1f9d3a
    "moderate": (36, 56, 200),   # blue   #2438c8
    "difficult": (17, 17, 17),   # black  #111111
    "road": (242, 94, 13),       # orange #f25e0d — roads (not rated)
    None: (136, 136, 136),       # grey   #888888
}
_NAMED_RGB = {"black": (0, 0, 0), "blue": (0, 0, 255), "green": (0, 128, 0),
              "red": (255, 0, 0), "orange": (255, 165, 0), "white": (255, 255, 255),
              "gray": (128, 128, 128), "grey": (128, 128, 128)}


def _parse_color(el):
    """RGB tuple of a path's stroke, or None. Reads both the SVG `stroke=` attr
    and a `style="...stroke:..."` declaration (Affinity writes the latter), in
    rgb(), #hex, and named-colour forms."""
    style = el.get("style") or ""
    m = re.search(r"stroke:\s*([^;]+)", style)
    raw = (m.group(1) if m else (el.get("stroke") or "")).strip().lower()
    if not raw or raw == "none":
        return None
    rm = re.match(r"rgb\(\s*(\d+)\D+(\d+)\D+(\d+)", raw)
    if rm:
        return tuple(int(x) for x in rm.groups())
    if raw.startswith("#"):
        h = raw[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            return tuple(int(h[i:i + 2], 16) for i in range(0, 6, 2))
    return _NAMED_RGB.get(raw)


def _stroke_class(el):
    """Classify a path's hand-set stroke colour to one of 'easy' / 'moderate' /
    'difficult' / 'road' / None (grey = still unknown), by nearest RGB anchor."""
    rgb = _parse_color(el)
    if rgb is None:
        return None
    return min(_DIFF_ANCHORS, key=lambda k: sum((a - b) ** 2 for a, b in zip(_DIFF_ANCHORS[k], rgb)))


def _norm_diff(d):
    return (d[0] if d else None) if isinstance(d, list) else d


def assign_difficulty(feats):
    """Best-guess difficulty for colouring, in confidence order:
      1. marker proximity (already filled by reattach_from_markers, <=22 m);
      2. number band, validated on the sheet — Easy 1-20, Moderate 21-39 & 80-99,
         Difficult 40-79.
    Non-numeric named trails (JW2, Riot Hill) with no nearby marker stay None and
    render grey for the human review pass — we do NOT guess difficulty from the
    digits inside a name."""
    def band(n):
        if n is None:
            return None
        if 1 <= n <= 20:
            return "easy"
        if (21 <= n <= 39) or (80 <= n <= 99):
            return "moderate"
        if 40 <= n <= 79:
            return "difficult"
        return None
    for f in feats:
        p = f["properties"]
        if p.get("kind") == "road":
            continue                            # roads are unrated — never band-guess
        p["difficulty"] = _norm_diff(p.get("difficulty")) or band(p.get("trail_number"))


def assign_colors(feats):
    """Colour each feature: roads orange; trails green Easy / blue Moderate /
    black Difficult, grey when still unknown (flagged for the review pass).
    Matches the hand-set colours the user edits in both the app layer and SVG."""
    for f in feats:
        p = f["properties"]
        if p.get("kind") == "road":
            p["color"] = ROAD_COLOR
        else:
            p["color"] = DIFF_COLOR.get(_norm_diff(p.get("difficulty")), UNKNOWN_COLOR)


def reattach_from_markers(feats, lat_min, lat_max, match_m=22.0):
    import math
    from collections import Counter
    mk_path = REPO / "website/data/sfwda_traced_markers.geojson"
    if not mk_path.exists():
        return
    lat0 = math.radians((lat_min + lat_max) / 2)
    mlat, mlng = 110540.0, 111320.0 * math.cos(lat0)
    def xy(lng, lat):
        return (lng * mlng, lat * mlat)
    markers = []
    for f in json.loads(mk_path.read_text())["features"]:
        p = f["properties"]; c = f["geometry"]["coordinates"]
        markers.append((xy(*c), p.get("trail_number"), p.get("difficulty")))

    def pt_seg(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        L = dx*dx + dy*dy
        t = 0.0 if L == 0 else max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / L))
        return math.hypot(px - (ax+t*dx), py - (ay+t*dy))

    for f in feats:
        if f["properties"].get("kind") == "road":
            continue                            # roads sit off the trail axis — no marker inheritance
        pts = [xy(*c) for c in f["geometry"]["coordinates"]]
        diffs = []
        for (mx, my), num, diff in markers:
            d = min(pt_seg(mx, my, *pts[i], *pts[i+1]) for i in range(len(pts)-1))
            if d <= match_m and diff:
                diffs.append(diff)
        # NUMBER/NAME: markers no longer assign a trail_number. The user hand-authors
        # every name in the editor's Objects panel, so the typed object-name is the
        # SOLE source of a trail's number/name (read in main() via _editable_name).
        # The old marker-proximity number-fill was a bootstrap that, once the user
        # was naming trails by hand, "renamed" UNNAMED neighbours of a marker cluster
        # to that marker's number — e.g. one typed "32" became three "32"s because the
        # #32 markers sat near two unnamed trails. Markers near an unnamed trail leave
        # it unnamed for the user to name; they never invent a number. (See card.)
        #
        # DIFFICULTY only: the user's hand-coloured stroke still wins; markers fill a
        # trail the user left uncoloured (a colour bootstrap, not a name/identity one).
        if diffs and not f["properties"].get("difficulty"):
            f["properties"]["difficulty"] = Counter(diffs).most_common(1)[0][0]


def compose(m, t):
    a, b, c, d, e, f = m; a2, b2, c2, d2, e2, f2 = t
    return [a*a2 + c*b2, b*a2 + d*b2, a*c2 + c*d2, b*c2 + d*d2, a*e2 + c*f2 + e, b*e2 + d*f2 + f]


def _editable_name(el):
    """The human-typed object name for a trail path, or None.

    Editors store the name a user types in the layers/objects panel in different
    attributes: Inkscape -> inkscape:label, Affinity Designer -> serif:id (and,
    for space-free names like "JW2"/"GWT", straight into the raw id). Our own
    export writes the name to both inkscape:label and serif:id. Read all three.
    A leading "_" (Affinity / export id prefix, e.g. "_15") is stripped. "?" is
    the not-yet-named placeholder and imports as no name."""
    nm = (el.get(f"{{{SERIF_NS}}}id") or el.get(f"{{{INK_NS}}}label")
          or el.get("id") or "").strip()
    if nm.startswith("_"):
        nm = nm[1:]
    if not nm or nm == "?":
        return None
    return nm


def _from_id(s):
    # export writes `<fid>_n<num>`; Affinity rewrites ids to `_<num>`.
    m = re.search(r"_n(\d+)", s or "") or re.fullmatch(r"_(\d+)", s or "")
    return m.group(1) if m else None


if __name__ == "__main__":
    main()
