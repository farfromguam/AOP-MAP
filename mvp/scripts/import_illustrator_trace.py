#!/usr/bin/env python3
"""Re-import the hand-edited satellite trace SVG back to georeferenced GeoJSON.

Card: brain/tasks/14_illustrator_trace/satellite_illustrator_export.md

Companion to export_illustrator_trace.py. After the user traces / refines on the
satellite in Illustrator (or Inkscape / Affinity) and renames layers, this reads
each edited layer back, inverts the UTM-16N frame recorded in the SVG <metadata>
(no warp), and writes GeoJSON. The layer NAME is the truth — read from whichever
channel the editor kept: inkscape:label, serif:id, <title>, or the `_xHH_`-escaped
group id (Illustrator's round-trip channel).

Path/transform parsing and the projection are reused, not re-implemented:
  - path_points / parse_transform / apply  <- import_trace_svg
  - geodetic_to_utm / utm_to_geodetic      <- export_illustrator_trace

Layers handled: "Gold Trails" -> LineString, "Waypoints" -> Point,
"Buildings" -> Polygon. By default only the trails are written back (the gold
network is the edit target); pass --all to also emit waypoints/buildings.

Provenance-preserving: a trail's EDITED geometry + name are the new truth, but the
rest of its gold props (color, maturity, permission, …) are carried forward from
the prior gold feature it matches — by `data-fid` (the stable id the export
embeds), falling back to name. So a round-trip does not strip gold provenance (a
trail the user draws fresh, with no match, gets thin "needs review" provenance).
The top-level `_meta` is left a thin stub for export_gold_trail_network.py to
re-stamp as the next step.

Usage:  python3 mvp/scripts/import_illustrator_trace.py [edited.svg] [--all]
Output: website/data/aop_trail_network.geojson  (geometry+name updated, props
        carried; run export_gold_trail_network.py next to re-stamp _meta)
"""
from __future__ import annotations
import copy, json, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_trace_svg import path_points, parse_transform, apply  # reuse parsers
from export_illustrator_trace import utm_to_geodetic, ai_escape   # reuse projection

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SVG = REPO / "brain/output/illustrator_trace/aop_satellite_trace.svg"
DATA = REPO / "website/data"
SVG = "{http://www.w3.org/2000/svg}"
INK = "{http://www.inkscape.org/namespaces/inkscape}"
SERIF = "{http://www.serif.com/}"


def ai_unescape(s):
    """Inverse of export_illustrator_trace.ai_escape. Order matters: strip the
    digit-guard `_` BEFORE decoding `_xHH_`, so a genuine leading-underscore name
    (escaped as `_x5F_…`, which starts with `_x`, not `_<digit>`) is not mistaken
    for the guard."""
    if s is None:
        return None
    # the export prepends a bare "_" only when the escaped id leads with a digit;
    # a content underscore escapes to "_x5F_" (next char 'x'), so this is unambiguous.
    if len(s) > 1 and s[0] == "_" and s[1].isdigit():
        s = s[1:]
    return re.sub(r"_x([0-9A-Fa-f]+)_", lambda m: chr(int(m.group(1), 16)), s)


def feature_name(el):
    """Read the name from the richest channel an editor preserved."""
    for getter in (lambda e: e.get(f"{INK}label"),
                   lambda e: e.get(f"{SERIF}id"),
                   lambda e: (e.find(f"{SVG}title").text if e.find(f"{SVG}title") is not None else None),
                   lambda e: ai_unescape(e.get("id"))):
        v = getter(el)
        if v not in (None, ""):
            return v
    return None


def load_meta(root, svg_path=None):
    """Read the UTM-16N frame from the SVG <metadata>. Affinity/Illustrator drop
    <metadata> on export, so when it's missing recover the frame from the original
    exported trace (DEFAULT_SVG) — the frame is deterministic (same raster + fixed
    UTM params), so it is exactly the frame the edited file was traced over."""
    md = root.find(f"{SVG}metadata")
    txt = (md.text or "").strip() if md is not None and md.text else ""
    if not txt:
        fb_root = ET.parse(DEFAULT_SVG).getroot()
        fb = fb_root.find(f"{SVG}metadata")
        txt = (fb.text or "").strip() if fb is not None else ""
        src = "uploaded SVG" if svg_path is None else Path(svg_path).name
        print(f"  [meta] {src} carries no projection metadata "
              f"(editor stripped it); recovered frame from {DEFAULT_SVG.name}")
    meta = json.loads(txt)
    assert meta.get("epsg") == 26916, f"unexpected frame {meta.get('epsg')}"
    return meta


def frame_to_lnglat(meta, xs, ys):
    E = np.asarray(xs) + meta["frame_origin_easting"]
    N = meta["frame_origin_northing"] - np.asarray(ys)
    lon, lat = utm_to_geodetic(E, N)
    return np.atleast_1d(lon), np.atleast_1d(lat)


def walk(el, mat, inherited=None):
    """Yield (element, composed_matrix, inherited_name) for el and all descendants.
    inherited_name is the name of the nearest *ancestor* that carried one: editors
    (Affinity) wrap a moved/new object in a <g transform=...> and put the object
    NAME on that wrapper, not on the leaf geometry, so a leaf must recover its name
    from above."""
    here = parse_transform(el.get("transform"))
    # compose mat * here
    a, b, c, d, e, f = mat; a2, b2, c2, d2, e2, f2 = here
    m = [a*a2+c*b2, b*a2+d*b2, a*c2+c*d2, b*c2+d*d2, a*e2+c*f2+e, b*e2+d*f2+f]
    yield el, m, inherited
    child_inh = feature_name(el) or inherited
    for child in el:
        yield from walk(child, m, child_inh)


def walk_layer(layer):
    """Walk a category layer's contents, composing transforms, WITHOUT letting the
    layer group's own name ("Gold Trails" etc.) leak down as a feature name — only
    names on wrapping <g>s *inside* the layer are inherited by their leaves."""
    base = parse_transform(layer.get("transform"))
    for child in layer:
        yield from walk(child, base, None)


def _lead_num(name):
    """Leading integer of a name ("11 Ground Control" -> 11), else None."""
    m = re.match(r"\s*(\d+)\b", name or "")
    return int(m.group(1)) if m else None


def collect_layer(root, label):
    """Find a category layer by any name channel an editor may have kept. Affinity
    renames the id ("Gold Trails" -> id="Gold-Trails") but preserves serif:id, and
    drops inkscape:label; Illustrator keeps the `_x20_`-escaped id. Search the whole
    tree (iter) so a layer nested under an editor's wrapper group is still found."""
    esc = ai_escape(label); dash = label.replace(" ", "-")
    for g in root.iter(f"{SVG}g"):
        if (g.get(f"{INK}label") == label or g.get(f"{SERIF}id") == label
                or g.get("id") in (esc, dash, label)):
            return g
    return None


def _ring(meta, m, poly):
    pts = [apply(m, x, y) for x, y in poly]
    lon, lat = frame_to_lnglat(meta, [p[0] for p in pts], [p[1] for p in pts])
    return [[round(float(a), 7), round(float(b), 7)] for a, b in zip(lon, lat)]


def import_trails(meta, layer, prior_by_id=None, prior_by_name=None, prior_by_tn=None):
    """Re-import the Gold Trails layer. Each trail is ONE named <path> object (the
    name may sit on the path or on an editor wrapper <g> above it). Its edited
    geometry + name are the new truth; the rest of its gold props
    (color/maturity/permission/…) are carried forward from the matching prior
    feature so a round-trip does NOT strip provenance. Match order:
    data-fid (Illustrator keeps it; Affinity strips), exact name, name-as-prior-id
    (unnamed trails export their `sfwda-N` id as the object name), then the leading
    trail number (a rename like "Launchpad" -> "1 Launchpad" still carries gold
    lineage). No match -> user-drawn-new, thin "needs review" provenance."""
    prior_by_id = prior_by_id or {}
    prior_by_name = prior_by_name or {}
    prior_by_tn = prior_by_tn or {}
    feats = []
    for el, m, inh in walk_layer(layer):
        if not el.tag.endswith("path"):
            continue
        name = feature_name(el) or inh
        fid = el.get("data-fid") or None
        prior = (prior_by_id.get(fid)
                 or (prior_by_name.get(name.lower()) if name else None)
                 or (prior_by_id.get(name) if name else None)
                 or (prior_by_tn.get(_lead_num(name)) if name else None))
        tn = el.get("data-trail-number") or None
        lines = [_ring(meta, m, poly) for poly in path_points(el.get("d", "")) if len(poly) >= 2]
        if not lines:
            continue
        geom = ({"type": "LineString", "coordinates": lines[0]} if len(lines) == 1
                else {"type": "MultiLineString", "coordinates": lines})
        if prior is not None:                       # carry full gold props
            props = copy.deepcopy(prior["properties"])
            props["review_status"] = "re-imported from Illustrator SVG (geometry/name updated)"
        else:                                       # user-drawn new trail
            props = {"trail_number": int(tn) if tn and tn.isdigit() else None,
                     "difficulty": el.get("data-difficulty") or None,
                     "source": "illustrator_trace_new",
                     "review_status": "new trail from Illustrator SVG; needs review"}
        # The export writes a named trail's object as just its name ("Launchpad").
        # A user may re-prefix the trail number for legibility while tracing
        # ("Launchpad" -> "1 Launchpad"); the viewer label already composes
        # "<number> <name>", so strip a leading "<trail_number> " to avoid a doubled
        # "1 1 Launchpad" (round-trips stably: export name -> edit -> import strips).
        tnum = props.get("trail_number")
        if name and tnum is not None:
            mm = re.match(r"\s*(\d+)\s+(.+)$", name)
            if mm and int(mm.group(1)) == tnum:
                name = mm.group(2).strip()
        props["name"] = name                        # the edited name wins
        feats.append({"type": "Feature", "properties": props, "geometry": geom})
    return feats


def import_points(meta, layer):
    feats = []
    for el, m, inh in walk_layer(layer):
        if not el.tag.endswith("circle"):
            continue
        x, y = apply(m, float(el.get("cx", 0)), float(el.get("cy", 0)))
        lon, lat = frame_to_lnglat(meta, [x], [y])
        feats.append({"type": "Feature",
                      "properties": {"name": feature_name(el) or inh, "kind": el.get("data-kind") or "poi"},
                      "geometry": {"type": "Point",
                                   "coordinates": [round(float(lon[0]), 7), round(float(lat[0]), 7)]}})
    return feats


def import_polys(meta, layer):
    feats = []
    for el, m, inh in walk_layer(layer):
        if not el.tag.endswith("path"):
            continue
        rings = []
        for poly in path_points(el.get("d", "")):
            if len(poly) < 3:
                continue
            ring = _ring(meta, m, poly)
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            rings.append(ring)
        if rings:
            feats.append({"type": "Feature",
                          "properties": {"name": feature_name(el) or inh, "kind": "building"},
                          "geometry": {"type": "Polygon", "coordinates": rings}})
    return feats


def main():
    argv = [a for a in sys.argv[1:]]
    want_all = "--all" in argv
    argv = [a for a in argv if not a.startswith("--")]
    svg_path = Path(argv[0]) if argv else DEFAULT_SVG
    root = ET.parse(svg_path).getroot()
    meta = load_meta(root, svg_path)

    # index the CURRENT gold network so each edited trail carries its full props
    # forward (provenance-preserving re-merge by stable id, then name, then number).
    dest = DATA / "aop_trail_network.geojson"
    prior = json.loads(dest.read_text()) if dest.exists() else {"features": []}
    by_id, by_name, by_tn = {}, {}, {}
    for f in prior.get("features", []):
        pp = f.get("properties", {})
        if pp.get("id"):
            by_id[pp["id"]] = f
        if pp.get("name"):
            by_name[str(pp["name"]).lower()] = f
        if pp.get("trail_number") is not None:
            by_tn[pp["trail_number"]] = f

    trails = collect_layer(root, "Gold Trails")
    tf = import_trails(meta, trails, by_id, by_name, by_tn) if trails is not None else []
    carried = sum(1 for f in tf if f["properties"].get("maturity"))
    newt = sum(1 for f in tf if f["properties"].get("source") == "illustrator_trace_new")
    out = {"type": "FeatureCollection", "name": "aop_trail_network",
           "_meta": {"generated_from": f"{svg_path.name} (Illustrator round-trip); "
                     "_meta re-stamped by export_gold_trail_network.py"},
           "features": tf}
    dest.write_text(json.dumps(out, indent=1))
    print(f"trails: {len(tf)} -> {dest.relative_to(REPO)}  "
          f"({carried} carried full gold props, {newt} user-drawn new)")

    if want_all:
        blay = collect_layer(root, "Buildings")
        bf = import_polys(meta, blay) if blay is not None else []
        (DATA / "aop_buildings_traced.geojson").write_text(json.dumps(
            {"type": "FeatureCollection", "name": "aop_buildings_traced", "features": bf}, indent=1))
        print(f"buildings: {len(bf)} -> website/data/aop_buildings_traced.geojson")

        # Waypoints: sweep <circle>s from EVERY editable layer, not just Waypoints.
        # A POI drawn into the wrong layer (e.g. an entrance dropped in Gold Trails)
        # is still a named point — ingest it, don't silently drop it.
        wf, strays = [], []
        for lname in ("Waypoints", "Gold Trails", "Buildings"):
            lay = collect_layer(root, lname)
            if lay is None:
                continue
            for feat in import_points(meta, lay):
                wf.append(feat)
                if lname != "Waypoints":
                    strays.append((feat["properties"].get("name"), lname))
        (DATA / "aop_waypoints_traced.geojson").write_text(json.dumps(
            {"type": "FeatureCollection", "name": "aop_waypoints_traced", "features": wf}, indent=1))
        print(f"waypoints: {len(wf)} -> website/data/aop_waypoints_traced.geojson")
        if strays:
            print(f"  swept {len(strays)} stray point POI(s) from non-Waypoints layers: "
                  + ", ".join(f"{n!r}<-{l}" for n, l in strays))


if __name__ == "__main__":
    main()
