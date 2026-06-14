#!/usr/bin/env python3
"""Verify the vegetation landcover SVG round-trips geometry losslessly.

Card: brain/tasks/01_mvp/_done/landcover_layer.md  (vegetation → editable SVG)

Observes the ACTUAL exported SVG files (not re-derived math): re-dissolves the
canopy from the 5-class cache the exporter used, parses the SVG's Vegetation layer
back through the real import path (walk_layer / _ring / path_points), inverts the
UTM-16N frame, and measures per-polygon Hausdorff displacement in metres + polygon
and ring-count parity + total canopy-area drift. The only expected error is the
2-decimal-metre rounding the exporter writes into the path `d` (≈1 cm ceiling).

Run after export_landcover_svg.py. Exits non-zero on any FAIL so it can gate.
Usage: python3 mvp/scripts/verify_landcover_svg_roundtrip.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from shapely.geometry import shape, Polygon as SP
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from simplify_landcover_vegetation import FOREST_CLASSES, clean_parts
from export_illustrator_trace import geodetic_to_utm
from import_illustrator_trace import walk_layer, collect_layer, _ring
from import_trace_svg import path_points
from import_landcover_svg import load_meta

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "mvp/cache/landcover"
OUT = REPO / "brain/output/landcover_trace"

# Acceptance thresholds. The path `d` is written at 2 dp of UTM metres, so the
# worst single-vertex displacement is bounded near sqrt(2)*0.005 m ≈ 0.71 cm; allow
# a small margin. Area drift is a derived check on the whole canopy.
MAX_HAUSDORFF_CM = 2.0
MAX_AREA_DRIFT_PCT = 0.01

TARGETS = [
    ("park", "aop_landcover.5class.geojson", "aop_landcover_trace.svg"),
    ("9patch", "aop_landcover_9patch.5class.geojson", "aop_landcover_9patch_trace.svg"),
]


def _conv(ring):
    a = np.array(ring); X, Y = geodetic_to_utm(a[:, 0], a[:, 1]); return np.c_[X, Y]


def _utm_from_shapely(p):
    return SP(_conv(list(p.exterior.coords)), [_conv(list(r.coords)) for r in p.interiors])


def _utm_from_rings(rings):
    return SP(_conv(rings[0]), [_conv(r) for r in rings[1:]]).buffer(0)


def orig_parts(cache):
    fc = json.loads((CACHE / cache).read_text())
    forest = [ft for ft in fc["features"] if ft["properties"].get("class") in FOREST_CLASSES]
    union = unary_union([shape(ft["geometry"]).buffer(0) for ft in forest])
    return clean_parts(union)


def svg_rings(svg):
    root = ET.parse(OUT / svg).getroot()
    meta = load_meta(root)
    layer = collect_layer(root, "Vegetation")
    out = []
    for el, m, _inh in walk_layer(layer):
        if not el.tag.endswith("path"):
            continue
        rings = [_ring(meta, m, sub) for sub in path_points(el.get("d", "")) if len(sub) >= 3]
        if rings:
            out.append(rings)
    return out


def main():
    overall_ok = True
    for name, cache, svg in TARGETS:
        if not (OUT / svg).exists():
            print(f"{name:7s} FAIL: {svg} missing — run export_landcover_svg.py first")
            overall_ok = False
            continue
        parts = orig_parts(cache)
        polys = svg_rings(svg)
        checks = []
        checks.append(("poly count parity", len(parts) == len(polys), f"{len(parts)} vs {len(polys)}"))
        max_hd = 0.0; area_o = 0.0; area_d = 0.0; ring_ok = True
        for p, rings in zip(parts, polys):
            if 1 + len(p.interiors) != len(rings):
                ring_ok = False
                continue
            uo = _utm_from_shapely(p); ur = _utm_from_rings(rings)
            max_hd = max(max_hd, uo.hausdorff_distance(ur))
            area_o += uo.area; area_d += abs(uo.area - ur.area)
        checks.append(("ring count parity", ring_ok, "exterior+holes match"))
        checks.append(("max Hausdorff", max_hd * 100 <= MAX_HAUSDORFF_CM, f"{max_hd*100:.3f} cm <= {MAX_HAUSDORFF_CM}"))
        drift_pct = 100 * area_d / area_o if area_o else 0.0
        checks.append(("area drift", drift_pct <= MAX_AREA_DRIFT_PCT, f"{drift_pct:.5f}% <= {MAX_AREA_DRIFT_PCT}"))
        ok = all(c[1] for c in checks)
        overall_ok = overall_ok and ok
        print(f"{name:7s} polys={len(parts):4d}  Hausdorff={max_hd*100:.3f}cm  "
              f"canopy={area_o/1e6:.3f}km^2 ({area_o/4046.86:.0f}ac)  drift={drift_pct:.5f}%  "
              f"-> {'PASS' if ok else 'FAIL'}")
        for label, good, detail in checks:
            if not good:
                print(f"        FAIL: {label} ({detail})")
    print("RESULT:", "PASS" if overall_ok else "FAIL")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
