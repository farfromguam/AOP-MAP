#!/usr/bin/env python3
"""Export the vegetation (tree-cover) land cover as an EDITABLE SVG for hand-
resolving polygons in Illustrator / Inkscape / Affinity, over the satellite.

Card: brain/tasks/01_mvp/_done/landcover_layer.md  (vegetation simplification)

Why this is not just the shipped GeoJSON: aop_landcover*.geojson is GRID-
SUBDIVIDED into many small fill pieces purely so MapLibre's earcut renders the
canopy everywhere (the giant single polygon dropped its corners). That is a
render workaround, NOT an editable shape — nobody wants to hand-edit 324 grid
cells. For hand work we want the TRUE tree mass: the forest classes dissolved
into one green per area, with clearings as holes. So this re-dissolves from the
5-class cache (the same `clean_parts` step simplify_landcover_vegetation.py runs
internally) and emits each canopy polygon as ONE named, filled, editable
compound <path> (exterior + holes, fill-rule evenodd). The user resolves the
green against the imagery, then import_landcover_svg.py reads the edited polygons
back and re-bakes the viewer's aop_landcover*.geojson.

Frame + backdrop + projection are REUSED from export_illustrator_trace.RasterFrame
(the satellite raster's own UTM-16N grid), so the green sits 1:1 on the imagery
and the importer inverts it with no warp. The exact projection params live in the
SVG <metadata> so the importer stays in lock-step.

Targets (the 5-class cache must exist — build_landcover*.sh keeps it):
  park    crisp 0.6 m park layer   -> aop_landcover_trace.svg         (default)
  9patch  full AOI ~1.5 m context  -> aop_landcover_9patch_trace.svg

Output dir: brain/output/landcover_trace/
Run:    python3 mvp/scripts/export_landcover_svg.py [park|9patch|both]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_illustrator_trace import RasterFrame, ai_escape, _xml  # frame + name channels
from simplify_landcover_vegetation import FOREST_CLASSES, clean_parts  # dissolve + clean

REPO = Path(__file__).resolve().parents[2]
CACHE = REPO / "mvp/cache/landcover"
IMAGERY = REPO / "mvp/cache/imagery"
OUT_DIR = REPO / "brain/output/landcover_trace"

TARGETS = {
    "park": dict(
        cache="aop_landcover.5class.geojson", tif="naip_2023_aop.tif",
        jpg="satellite_park.jpg", svg="aop_landcover_trace.svg"),
    "9patch": dict(
        cache="aop_landcover_9patch.5class.geojson", tif="naip_2023_9patch.tif",
        jpg="satellite_9patch.jpg", svg="aop_landcover_9patch_trace.svg"),
}


def recover_frame(target):
    """Rebuild a target's UTM-16N frame + projection meta from its raster, for an
    editor export that DROPPED the <metadata> (Affinity does). Deterministic — same
    raster + fixed UTM params as the original export, so geometry inverts to the exact
    lng/lat it came from. The single home for frame recovery: shared by
    import_landcover_svg.py (re-bake) and build_landcover_map_test.py. Returns (F, meta)."""
    cfg = TARGETS[target]
    F = RasterFrame(IMAGERY / cfg["tif"], OUT_DIR / cfg["jpg"])
    meta = F.meta(note="recovered frame (editor stripped metadata)",
                  extra={"layer_target": "vegetation", "target": target})
    return F, meta


def dissolve_canopy(cache_path):
    """Forest classes -> one dissolved, deholed, lightly-simplified canopy mass
    (the editable 'single green for tree cover'). Same transform the viewer bake
    runs before it grid-subdivides for rendering; here we stop at the clean mass."""
    fc = json.loads(cache_path.read_text())
    forest = [ft for ft in fc["features"]
              if ft.get("properties", {}).get("class") in FOREST_CLASSES]
    if not forest:
        sys.exit(f"no forest_* features in {cache_path} (wrong input?)")
    union = unary_union([shape(ft["geometry"]).buffer(0) for ft in forest])
    return clean_parts(union)


def name_attrs(nm):
    """The feature name as the OBJECT name in every editor's name channel — on the
    geometry element itself (no wrapper group, no drawn text). Mirrors
    export_illustrator_trace.name_attrs so the same importer channels read it."""
    eid = ai_escape(nm); lab = _xml(nm)
    return f'id="{eid}" inkscape:label="{lab}" serif:id="{lab}"', f'<title>{lab}</title>'


def poly_path_d(poly, F):
    """One canopy polygon -> a compound SVG path: exterior + each hole as a closed
    subpath, projected into the raster's UTM frame. fill-rule evenodd punches the
    holes (clearings)."""
    rings = [poly.exterior.coords] + [r.coords for r in poly.interiors]
    subpaths = []
    for ring in rings:
        lon = np.array([c[0] for c in ring]); lat = np.array([c[1] for c in ring])
        xs, ys = F.to_frame(lon, lat)
        subpaths.append("M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in zip(xs, ys)) + " Z")
    return " ".join(subpaths)


def build(name, cfg):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    parts = dissolve_canopy(CACHE / cfg["cache"])
    F = RasterFrame(IMAGERY / cfg["tif"], OUT_DIR / cfg["jpg"])

    veg_els = []
    for i, poly in enumerate(parts, 1):
        attrs, title = name_attrs(f"Vegetation {i}")
        veg_els.append(
            f'<path {attrs} class="veg" data-fid="vegetation_{i}" '
            f'd="{poly_path_d(poly, F)}">{title}</path>')

    meta = F.meta(
        note=("SVG user units = UTM 16N metres; x=E-origin_E, y=origin_N-N. "
              "import_landcover_svg.py inverts this (no warp). Edit the green in "
              "the Vegetation layer against the satellite; each path is one canopy "
              "polygon (exterior + holes, fill-rule evenodd)."),
        extra={"layer_target": "vegetation", "target": name})

    INK = ('xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           'xmlns:serif="http://www.serif.com/"')
    w, h = F.width_u, F.height_u
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" {INK}
     width="{w:.1f}" height="{h:.1f}" viewBox="0 0 {w:.2f} {h:.2f}">
<metadata id="aop_proj">{json.dumps(meta)}</metadata>
<style>
 .veg {{ fill:#5a8f3c; fill-opacity:0.32; fill-rule:evenodd;
         stroke:#2f6d1e; stroke-width:2.5; }}
</style>
<g inkscape:groupmode="layer" inkscape:label="Satellite" id="Satellite"
   sodipodi:insensitive="true"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.0.dtd">
  <image x="0" y="0" width="{w:.2f}" height="{h:.2f}" preserveAspectRatio="none"
         xlink:href="data:image/jpeg;base64,{F.raster_b64}" />
</g>
<g inkscape:groupmode="layer" inkscape:label="Vegetation" id="Vegetation">
  {"".join(veg_els)}
</g>
</svg>'''
    out_svg = OUT_DIR / cfg["svg"]
    out_svg.write_text(svg)

    nw, se = meta["bbox_lnglat_nw"], meta["bbox_lnglat_se"]
    maxv = max((len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors)
                for p in parts), default=0)
    print(f"wrote {out_svg.relative_to(REPO)}  ({out_svg.stat().st_size/1e6:.1f} MB)")
    print(f"  backdrop {(OUT_DIR / cfg['jpg']).relative_to(REPO)}  "
          f"({F.img_w}x{F.img_h}px, {F.px[0]:.3f} m/px)")
    print(f"  Vegetation: {len(veg_els)} canopy polygons (max {maxv} verts)  "
          f"frame {w:.0f}x{h:.0f} m  UTM16N origin E{F.minE:.1f} N{F.maxN:.1f}")
    print(f"  raster NW lng/lat {nw[0]:.6f},{nw[1]:.6f}  SE {se[0]:.6f},{se[1]:.6f}")


def main():
    which = (sys.argv[1] if len(sys.argv) > 1 else "park").lower()
    names = list(TARGETS) if which == "both" else [which]
    for nm in names:
        if nm not in TARGETS:
            sys.exit(f"unknown target {nm!r}; choose park | 9patch | both")
        build(nm, TARGETS[nm])


if __name__ == "__main__":
    main()
