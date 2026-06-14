#!/usr/bin/env python3
"""Standalone MapLibre test for the hand-edited vegetation, BEFORE viewer integration.

Card: brain/tasks/01_mvp/_done/landcover_layer.md  (vegetation → editable SVG)

The user resolved the 9-patch vegetation in Affinity (159 shapes) and wants to see it
rendered by the REAL engine (MapLibre) on a map — solid light-sage, no border, no
opacity — and specifically to check the high-vertex tessellation bug that bit us
before (one shape is a 3969-vertex / 48-subpath canopy mass; the same giant+holey
single fill polygon that made MapLibre's earcut drop chunks → empty corners).

So this renders BOTH forms and lets you flip between them:
  • RAW         — the 159 edited shapes as-is (the monster intact)  → expect the bug
  • SUBDIVIDED  — the proven viewer fix: union + grid-subdivide into small fill pieces
                  (simplify_landcover_vegetation.vegetation_features)  → expect clean

Affinity strips the projection <metadata>, so the frame is RECOVERED from the
9-patch raster (RasterFrame) — deterministic, the exact frame the export was written
in. Geometry is inverted to lng/lat with the existing import path; the satellite is a
local MapLibre image source (offline, no tiles). Test here first; integrate after
it renders clean.

Output: brain/output/landcover_trace/landcover_map_test.html
        + landcover_map_raw.geojson + landcover_map_subdivided.geojson
Run:    python3 mvp/scripts/build_landcover_map_test.py [edited.svg] [--target 9patch|park]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

from shapely.geometry import mapping
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_illustrator_trace import utm_to_geodetic
from export_landcover_svg import OUT_DIR, TARGETS, recover_frame   # shared frame recovery
from import_illustrator_trace import collect_layer
from import_landcover_svg import read_polys
from simplify_landcover_vegetation import vegetation_features

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SVG = REPO / "brain/import/trace_upload/aop_landcover_trace.svg"
SAGE = "#cfdabf"            # light sage — solid fill, no border, no opacity


def fc(features):
    return {"type": "FeatureCollection", "features": features}


def main():
    argv = sys.argv[1:]
    target = "9patch"
    if "--target" in argv:
        i = argv.index("--target"); target = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    svg_path = Path(argv[0]) if argv else DEFAULT_SVG
    if target not in TARGETS:
        sys.exit(f"unknown --target {target!r}; choose {list(TARGETS)}")

    F, meta = recover_frame(target)
    root = ET.parse(svg_path).getroot()
    layer = collect_layer(root, "Vegetation")
    if layer is None:
        sys.exit(f"no 'Vegetation' layer in {svg_path}")
    polys = read_polys(meta, layer)            # shapely polygons in lng/lat
    if not polys:
        sys.exit(f"no vegetation polygons read from {svg_path}")

    # RAW: the edited shapes exactly as drawn (the high-vertex monster intact).
    raw_feats = [{"type": "Feature", "properties": {"i": i}, "geometry": mapping(p)}
                 for i, p in enumerate(polys)]
    raw_max = max(len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors) for p in polys)

    # SUBDIVIDED: union + grid-subdivide (the viewer's fill contract). Fill only.
    union = unary_union(polys)
    parts = list(union.geoms) if union.geom_type == "MultiPolygon" else [union]
    veg_feats, fill_pieces = vegetation_features(parts, kind="landcover")
    sub_feats = [f for f in veg_feats if f["properties"]["role"] == "fill"]
    sub_max = max(len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors) for p in fill_pieces)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "landcover_map_raw.geojson").write_text(json.dumps(fc(raw_feats), separators=(",", ":")))
    (OUT_DIR / "landcover_map_subdivided.geojson").write_text(json.dumps(fc(sub_feats), separators=(",", ":")))

    # satellite image corners (lng/lat), MapLibre order TL,TR,BR,BL
    minE, maxN, w, h = F.minE, F.maxN, F.width_u, F.height_u
    def ll(e, n):
        lon, lat = utm_to_geodetic(e, n); return [float(lon), float(lat)]
    NW, NE, SE, SW = ll(minE, maxN), ll(minE + w, maxN), ll(minE + w, maxN - h), ll(minE, maxN - h)
    lons = [c[0] for c in (NW, NE, SE, SW)]; lats = [c[1] for c in (NW, NE, SE, SW)]
    bounds = [[min(lons), min(lats)], [max(lons), max(lats)]]

    out = OUT_DIR / "landcover_map_test.html"
    out.write_text(_HTML
                   .replace("__SAGE__", SAGE)
                   .replace("__CORNERS__", json.dumps([NW, NE, SE, SW]))
                   .replace("__BOUNDS__", json.dumps(bounds))
                   .replace("__RAWN__", str(len(raw_feats)))
                   .replace("__SUBN__", str(len(sub_feats)))
                   .replace("__RAWMAX__", str(raw_max))
                   .replace("__SUBMAX__", str(sub_max)))
    print(f"wrote {out.relative_to(REPO)}")
    print(f"  RAW  {len(raw_feats)} shapes, worst {raw_max} verts (the monster) -> landcover_map_raw.geojson")
    print(f"  SUB  {len(sub_feats)} fill pieces, worst {sub_max} verts -> landcover_map_subdivided.geojson")
    print(f"  serve from REPO ROOT, open /brain/output/landcover_trace/{out.name}")


_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AOP land cover — MapLibre render test (raw vs subdivided)</title>
<link href="/website/vendor/maplibre-gl.css" rel="stylesheet" />
<script src="/website/vendor/maplibre-gl.js"></script>
<style>
  html,body{margin:0;height:100%;font:13px/1.4 -apple-system,Segoe UI,Roboto,sans-serif}
  #map{position:absolute;inset:0}
  #panel{position:absolute;top:12px;left:12px;z-index:2;background:#1b1b1bdd;color:#eee;
    backdrop-filter:blur(6px);border:1px solid #ffffff22;border-radius:10px;padding:12px 14px;
    box-shadow:0 6px 20px #0007;min-width:230px}
  #panel h1{font-size:13px;margin:0 0 8px}
  .row{display:flex;gap:7px;margin:7px 0;flex-wrap:wrap}
  button{background:#2c2c2c;color:#eee;border:1px solid #ffffff22;border-radius:7px;
    padding:5px 10px;cursor:pointer;font-size:12px}
  button.on{background:#5b7a4a;border-color:#5b7a4a;color:#fff}
  .note{color:#9bd07e;font-size:11px;margin-top:8px}
  .warn{color:#ffb37a}
</style></head>
<body>
<div id="map"></div>
<div id="panel">
  <h1>Land cover — MapLibre render test</h1>
  <div class="row">
    <button id="bRaw">RAW (__RAWN__, worst __RAWMAX__v)</button>
    <button id="bSub" class="on">SUBDIVIDED (__SUBN__)</button>
  </div>
  <div class="row">
    <button id="bSat" class="on">Satellite</button>
  </div>
  <div class="note" id="msg">SUBDIVIDED — the integration-ready form.</div>
</div>
<script>
const SAGE="__SAGE__", CORNERS=__CORNERS__, BOUNDS=__BOUNDS__;
const map=new maplibregl.Map({container:'map', style:{version:8, sources:{}, layers:[
  {id:'bg', type:'background', paint:{'background-color':'#e7ddc4'}}
]}, bounds:BOUNDS, fitBoundsOptions:{padding:20}, attributionControl:false});
window.map=map; window._ready=false;
map.on('load', ()=>{
  map.addSource('sat',{type:'image', url:'./satellite_9patch.jpg', coordinates:CORNERS});
  map.addLayer({id:'sat', type:'raster', source:'sat', paint:{'raster-opacity':1}});
  map.addSource('raw',{type:'geojson', data:'./landcover_map_raw.geojson'});
  map.addSource('sub',{type:'geojson', data:'./landcover_map_subdivided.geojson'});
  // solid light sage, NO border (no fill-outline-color), NO opacity (fill-opacity 1)
  map.addLayer({id:'veg-raw', type:'fill', source:'raw',
    paint:{'fill-color':SAGE,'fill-opacity':1}, layout:{visibility:'none'}});
  map.addLayer({id:'veg-sub', type:'fill', source:'sub',
    paint:{'fill-color':SAGE,'fill-opacity':1}});
  window._ready=true;
});
const bRaw=document.getElementById('bRaw'), bSub=document.getElementById('bSub'),
      bSat=document.getElementById('bSat'), msg=document.getElementById('msg');
function show(which){
  if(!map.getLayer('veg-sub')) return;
  const raw=which==='raw';
  map.setLayoutProperty('veg-raw','visibility', raw?'visible':'none');
  map.setLayoutProperty('veg-sub','visibility', raw?'none':'visible');
  bRaw.classList.toggle('on',raw); bSub.classList.toggle('on',!raw);
  msg.innerHTML = raw
    ? '<span class="warn">RAW — one 3969-vertex shape. Watch for dropped chunks / missing canopy.</span>'
    : 'SUBDIVIDED — the integration-ready form.';
}
bRaw.onclick=()=>show('raw'); bSub.onclick=()=>show('sub');
bSat.onclick=()=>{ if(!map.getLayer('sat')) return;
  const v=map.getLayoutProperty('sat','visibility')!=='none';
  map.setLayoutProperty('sat','visibility', v?'none':'visible'); bSat.classList.toggle('on',!v);};
</script>
</body></html>"""


if __name__ == "__main__":
    main()
