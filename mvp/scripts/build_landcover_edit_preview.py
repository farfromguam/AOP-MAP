#!/usr/bin/env python3
"""Lightweight preview page for a hand-edited vegetation trace SVG.

Card: brain/tasks/01_mvp/_done/landcover_layer.md  (vegetation → editable SVG)

After the user resolves the vegetation polygons in Affinity/Illustrator and saves
the SVG, this builds a dead-simple standalone HTML page to SEE the result: their
edited tree-cover shapes laid straight back over the satellite, in the raster's own
frame (no georeferencing needed — the edited SVG's viewBox IS the satellite's
metre grid, so the shapes overlay 1:1).

Affinity strips the projection <metadata> and the embedded satellite on export, so
this does NOT depend on either: it pulls the raster frame from the viewBox and
re-attaches the satellite backdrop (brain/output/landcover_trace/satellite_9patch.jpg,
written by export_landcover_svg.py) by reference. The page has wheel-zoom + drag-pan
and toggles for the satellite, fill/outline, and vegetation opacity — enough to
judge the trace against the imagery.

Usage:  python3 mvp/scripts/build_landcover_edit_preview.py [edited.svg] [--backdrop NAME]
Default in:  brain/import/trace_upload/aop_landcover_trace.svg
Default out: brain/output/landcover_trace/landcover_edit_preview.html
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SVG = REPO / "brain/import/trace_upload/aop_landcover_trace.svg"
OUT_DIR = REPO / "brain/output/landcover_trace"


def extract(svg_text):
    """Pull the viewBox and the Vegetation <g>…</g> (paths only, one group)."""
    vb = re.search(r'viewBox="([^"]+)"', svg_text)
    if not vb:
        sys.exit("no viewBox in the SVG")
    w, h = (float(x) for x in vb.group(1).split()[2:4])
    g = re.search(r'(<g\b[^>]*id="Vegetation"[^>]*>.*?</g>)', svg_text, re.S)
    if not g:
        sys.exit("no <g id=\"Vegetation\"> layer in the SVG (editor renamed it?)")
    npaths = g.group(1).count("<path")
    return w, h, g.group(1), npaths


def main():
    argv = sys.argv[1:]
    backdrop = "satellite_9patch.jpg"
    if "--backdrop" in argv:
        i = argv.index("--backdrop"); backdrop = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    svg_path = Path(argv[0]) if argv else DEFAULT_SVG

    w, h, veg_group, npaths = extract(svg_path.read_text(errors="replace"))
    # give the group a hook class and drop Affinity's inline fill so the page's
    # CSS fully owns fill/stroke (lets the fill/outline toggle work).
    veg = re.sub(r'<g\b', '<g class="veg"', veg_group, count=1)
    veg = re.sub(r'\s*style="[^"]*fill:rgb\([^)]*\)[^"]*"', '', veg)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "landcover_edit_preview.html"
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>AOP land cover — hand-edited vegetation over NAIP 2023</title>
<style>
  :root {{ --green:#3f7a2f; --edge:#1f5613; }}
  * {{ box-sizing:border-box; }}
  html,body {{ margin:0; height:100%; background:#222; overflow:hidden;
    font:13px/1.4 -apple-system,Segoe UI,Roboto,sans-serif; color:#eee; }}
  #stage {{ width:100vw; height:100vh; display:block; cursor:grab; touch-action:none; }}
  #stage.drag {{ cursor:grabbing; }}
  #sat {{ image-rendering:auto; }}
  .veg path {{ fill:var(--green); fill-rule:evenodd; stroke:var(--edge);
    stroke-width:3; vector-effect:non-scaling-stroke; }}
  body.outline .veg path {{ fill:none !important; stroke-width:1.5; }}
  body.nosat #sat {{ display:none; }}
  #panel {{ position:fixed; top:12px; left:12px; background:#1b1b1bdd; backdrop-filter:blur(6px);
    border:1px solid #ffffff22; border-radius:10px; padding:12px 14px; min-width:210px;
    box-shadow:0 6px 20px #0007; }}
  #panel h1 {{ font-size:13px; margin:0 0 2px; font-weight:600; }}
  #panel .sub {{ color:#9bd07e; font-size:11px; margin-bottom:10px; }}
  .row {{ display:flex; align-items:center; gap:8px; margin:7px 0; }}
  .row label {{ flex:1; }}
  input[type=range] {{ width:96px; }}
  button {{ background:#2c2c2c; color:#eee; border:1px solid #ffffff22; border-radius:7px;
    padding:5px 9px; cursor:pointer; font-size:12px; }}
  button.on {{ background:var(--green); border-color:var(--green); color:#fff; }}
  .hint {{ color:#888; font-size:11px; margin-top:10px; }}
</style></head>
<body>
<svg id="stage" viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="xMidYMid meet">
  <g id="cam">
    <image id="sat" x="0" y="0" width="{w:.0f}" height="{h:.0f}"
           preserveAspectRatio="none" href="{backdrop}" />
    <g id="vegwrap" opacity="0.7">
      {veg}
    </g>
  </g>
</svg>
<div id="panel">
  <h1>Land cover — hand-edited</h1>
  <div class="sub">{npaths} vegetation shapes · {svg_path.name}</div>
  <div class="row"><label>Vegetation opacity</label>
    <input id="op" type="range" min="0" max="100" value="70"></div>
  <div class="row">
    <button id="bSat" class="on">Satellite</button>
    <button id="bFill" class="on">Fill</button>
  </div>
  <div class="hint">scroll = zoom · drag = pan · double-click = reset</div>
</div>
<script>
const stage=document.getElementById('stage'), cam=document.getElementById('cam');
let s=1,tx=0,ty=0;
function apply(){{ cam.setAttribute('transform',`translate(${{tx}} ${{ty}}) scale(${{s}})`); }}
function toSvg(e){{ const p=stage.createSVGPoint(); p.x=e.clientX; p.y=e.clientY;
  return p.matrixTransform(stage.getScreenCTM().inverse()); }}
stage.addEventListener('wheel',e=>{{ e.preventDefault();
  const m=toSvg(e), k=Math.exp(-e.deltaY*0.0015), ns=Math.min(40,Math.max(0.5,s*k));
  // keep cursor point fixed: tx' = m.x - (m.x - tx)*ns/s
  tx=m.x-(m.x-tx)*ns/s; ty=m.y-(m.y-ty)*ns/s; s=ns; apply(); }},{{passive:false}});
let dragging=false,lx=0,ly=0;
stage.addEventListener('pointerdown',e=>{{ dragging=true; lx=e.clientX; ly=e.clientY;
  stage.classList.add('drag'); stage.setPointerCapture(e.pointerId); }});
stage.addEventListener('pointermove',e=>{{ if(!dragging)return;
  const ctm=stage.getScreenCTM(); tx+=(e.clientX-lx)/ctm.a; ty+=(e.clientY-ly)/ctm.d;
  lx=e.clientX; ly=e.clientY; apply(); }});
stage.addEventListener('pointerup',e=>{{ dragging=false; stage.classList.remove('drag'); }});
stage.addEventListener('dblclick',()=>{{ s=1; tx=0; ty=0; apply(); }});
document.getElementById('op').addEventListener('input',e=>
  document.getElementById('vegwrap').setAttribute('opacity', e.target.value/100));
const bSat=document.getElementById('bSat'), bFill=document.getElementById('bFill');
bSat.onclick=()=>{{ document.body.classList.toggle('nosat'); bSat.classList.toggle('on'); }};
bFill.onclick=()=>{{ document.body.classList.toggle('outline'); bFill.classList.toggle('on');
  bFill.textContent=document.body.classList.contains('outline')?'Outline':'Fill'; }};
apply();
</script>
</body></html>"""
    out.write_text(html)
    print(f"wrote {out.relative_to(REPO)}  ({out.stat().st_size/1024:.0f} KB, {npaths} shapes)")
    print(f"  frame {w:.0f} x {h:.0f} (metres) · backdrop {backdrop}")
    print(f"  source {svg_path.relative_to(REPO) if svg_path.is_relative_to(REPO) else svg_path}")


if __name__ == "__main__":
    main()
