#!/usr/bin/env python3
"""Re-import the hand-edited vegetation SVG back to the viewer's landcover GeoJSON.

Card: brain/tasks/01_mvp/_done/landcover_layer.md  (vegetation simplification)

Companion to export_landcover_svg.py. After the user resolves the green polygons
on the satellite, this reads the Vegetation layer back, inverts the UTM-16N frame
recorded in the SVG <metadata> (no warp), unions the edited polygons, and re-bakes
the viewer file the SAME way the 5-class bake does: clearings kept as holes, the
fill grid-subdivided so MapLibre renders it everywhere, and the canopy edge
emitted as a separate LineString outline.

Reuse, not re-implementation:
  - path/transform parsing  <- import_trace_svg (path_points)
  - frame walk + inversion  <- import_illustrator_trace (walk/load_meta/_ring/collect_layer)
  - subdivide + outline + the viewer feature contract
                            <- simplify_landcover_vegetation (vegetation_features)

The edited polygons are taken as already-resolved: they are unioned (so adjacent
hand-drawn pieces merge) but NOT re-deholed/re-simplified — that would undo the
user's manual work. The output target (park vs 9-patch) is read from the SVG meta
`target`, so the right viewer file is re-baked.

Usage:  python3 mvp/scripts/import_landcover_svg.py [edited.svg] [--out FILE] [--target park|9patch]
Default in:  brain/output/landcover_trace/aop_landcover_trace.svg
Default out: website/data/aop_landcover.geojson   (or _9patch per the SVG/--target)
--target recovers the frame when an editor (Affinity) stripped the <metadata>.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_trace_svg import path_points                          # path parser
from import_illustrator_trace import walk_layer, collect_layer, _ring  # frame inversion
from simplify_landcover_vegetation import vegetation_features     # viewer contract
from export_landcover_svg import recover_frame                    # shared frame recovery

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "website/data"
DEFAULT_SVG = REPO / "brain/output/landcover_trace/aop_landcover_trace.svg"
SVG_NS = "{http://www.w3.org/2000/svg}"
OUT_BY_TARGET = {"park": "aop_landcover.geojson", "9patch": "aop_landcover_9patch.geojson"}


def load_meta(root, target=None):
    """Read the UTM-16N frame from this SVG's own <metadata>. If an editor stripped
    it (Affinity does), recover the frame from --target's raster — the same
    deterministic frame the export was written in — via the shared
    export_landcover_svg.recover_frame (NOT the trail importer's fallback, whose frame
    is always the 9-patch and would mis-place a park edit). Without either, refuse."""
    md = root.find(f"{SVG_NS}metadata")
    txt = (md.text or "").strip() if md is not None and md.text else ""
    if txt:
        meta = json.loads(txt)
        assert meta.get("epsg") == 26916, f"unexpected frame {meta.get('epsg')}"
        return meta
    if target:
        _F, meta = recover_frame(target)
        return meta
    sys.exit("SVG carries no <metadata> frame (editor stripped it). Re-export with "
             "export_landcover_svg.py, or pass --target park|9patch to recover the frame.")


def read_polys(meta, layer):
    """Every <path> in the Vegetation layer -> a shapely Polygon in lng/lat. The
    first subpath is the exterior, the rest are holes (the compound-path order the
    exporter writes; a hand-split path keeps that convention)."""
    polys = []
    for el, m, _inh in walk_layer(layer):
        if not el.tag.endswith("path"):
            continue
        rings = []
        for sub in path_points(el.get("d", "")):
            if len(sub) < 3:
                continue
            ring = _ring(meta, m, sub)              # -> [[lon,lat], ...]
            if ring[0] != ring[-1]:
                ring.append(ring[0])
            rings.append(ring)
        if not rings:
            continue
        poly = Polygon(rings[0], rings[1:]).buffer(0)   # buffer(0) fixes any self-touch
        if poly.is_empty or poly.area <= 0:
            continue
        polys.append(poly)
    return polys


def main():
    argv = sys.argv[1:]
    out_override = None
    target_arg = None
    if "--out" in argv:
        i = argv.index("--out")
        out_override = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if "--target" in argv:
        i = argv.index("--target")
        target_arg = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    svg_path = Path(argv[0]) if argv else DEFAULT_SVG

    root = ET.parse(svg_path).getroot()
    meta = load_meta(root, target_arg)
    layer = collect_layer(root, "Vegetation")
    if layer is None:
        sys.exit(f"no 'Vegetation' layer in {svg_path}")

    polys = read_polys(meta, layer)
    if not polys:
        sys.exit(f"no vegetation polygons read from {svg_path}")

    union = unary_union(polys)
    parts = list(union.geoms) if union.geom_type == "MultiPolygon" else [union]
    out_features, fill_pieces = vegetation_features(parts, kind="landcover")

    target = meta.get("target", "park")
    out_path = Path(out_override) if out_override else DATA / OUT_BY_TARGET.get(target, "aop_landcover.geojson")
    out = {
        "type": "FeatureCollection",
        "name": "vegetation",
        "xy_coordinate_resolution": 1e-6,
        "features": out_features,
        "_meta": {
            "maturity": "hand-resolved",
            "maturity_note": (
                "vegetation polygons hand-resolved in Illustrator/Inkscape over the "
                "satellite and re-imported by import_landcover_svg.py; unioned, then "
                "grid-subdivided for fill + a LineString outline (viewer contract via "
                "simplify_landcover_vegetation.vegetation_features)."),
            "generated_from": svg_path.name,
        },
    }
    out_path.write_text(json.dumps(out, separators=(",", ":")))
    shown = out_path.relative_to(REPO) if out_path.resolve().is_relative_to(REPO) else out_path
    print(f"{svg_path.name}: {len(polys)} edited polygons -> {shown}  "
          f"({len(fill_pieces)} fill pieces + 1 outline, target={target})")


if __name__ == "__main__":
    main()
