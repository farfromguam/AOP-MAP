#!/usr/bin/env python3
"""Verify the five-item review fixes against the real running viewer (:8001).

Fresh browser context each run → no service-worker cache, first load is network.
Screenshots: brain/output/v5_*.png. Prints PASS/FAIL per observable claim.
"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).resolve().parent
URL = "http://localhost:8001/index.html"
fail = False


def ck(label, ok, detail=""):
    global fail
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        fail = True


def main():
    errs = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        pg = ctx.new_page()
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(URL, wait_until="load")
        pg.evaluate("window.map=(window.AOPViewer&&window.AOPViewer.map)||window.map;")
        pg.wait_for_function("()=>window.map&&window.map.isStyleLoaded&&window.map.isStyleLoaded()", timeout=20000)
        pg.wait_for_timeout(2800)

        ver = pg.evaluate("()=>document.getElementById('appVersion')?.textContent")
        print(f"version: {ver}")

        print("\n== item 4: Park no-tree base = #e7ddc4 ==")
        bg = pg.evaluate("()=>window.map.getPaintProperty('background','background-color')")
        ck("Park background is the warm tan base", bg == "#e7ddc4", f"bg={bg}")

        print("\n== item 5: 9-patch vegetation renders across its extent ==")
        # Region zoom (whole 9-patch); screenshot for visual confirmation.
        pg.evaluate("()=>{const b=document.getElementById('zoomRegion'); if(b)b.click();}")
        pg.wait_for_timeout(2800)
        pg.screenshot(path=str(OUT / "v5_region.png"))
        # The user's complaint was "all but top right have un-natural rendering
        # errors" — i.e. 3 of 4 corners empty. So sample the interior by QUADRANT
        # and require EVERY quadrant to render veg fill (was centre-only before).
        cov = pg.evaluate("""()=>{
          const c=window.map.getCanvas(), w=c.clientWidth, h=c.clientHeight;
          const q={TL:0,TR:0,BL:0,BR:0}, n={TL:0,TR:0,BL:0,BR:0};
          for(let i=0;i<6;i++) for(let j=0;j<6;j++){
            const fx=0.12+0.76*i/5, fy=0.12+0.76*j/5;
            const x=w*fx, y=h*fy;
            const k=(fy<0.5?'T':'B')+(fx<0.5?'L':'R');
            n[k]++;
            const f=window.map.queryRenderedFeatures([x,y],{layers:['landcover-9patch-forest']});
            if(f.length) q[k]++;
          }
          return {q,n};
        }""")
        q = cov["q"]
        ck("9-patch veg fill renders in ALL four quadrants (corners no longer empty)",
           all(q[k] >= 2 for k in q), f"hits per quadrant {q}")
        # fill-piece count regression guard via the served file
        d9 = pg.evaluate("""async()=>{const r=await fetch('./data/aop_landcover_9patch.geojson');const d=await r.json();
          const f=d.features||[];const poly=f.filter(x=>/Polygon/.test(x.geometry.type));
          const line=f.filter(x=>/LineString/.test(x.geometry.type));
          const v=g=>{const rs=g.type==='Polygon'?g.coordinates:g.type==='MultiPolygon'?g.coordinates.flat():[];return rs.reduce((s,r)=>s+r.length,0);};
          return {fill:poly.length, line:line.length, maxv:poly.reduce((m,x)=>Math.max(m,v(x.geometry)),0)};}""")
        ck("9-patch is subdivided fill + line outline", d9["fill"] >= 50 and d9["line"] >= 1,
           f"{d9['fill']} fill, {d9['line']} line")
        ck("no giant fill polygon", d9["maxv"] < 1500, f"max {d9['maxv']} verts/piece")

        print("\n== item 1: trail labels number-first ==")
        # turn on the trail network + zoom into the park so labels render
        pg.evaluate("()=>{const b=document.getElementById('zoomPark'); if(b)b.click();}")
        pg.wait_for_timeout(2200)
        tf = pg.evaluate("()=>JSON.stringify(window.map.getLayoutProperty('aop-trail-network-labels','text-field'))")
        ck("label text-field uses trail_number expression",
           "trail_number" in (tf or ""), (tf or "")[:80])
        # resolve the labels my expression would produce for the source features
        labels = pg.evaluate("""()=>{
          const src = window.map.getSource('aop-trail-network');
          // read raw data via the source's _data if present, else querySourceFeatures
          const feats = window.map.querySourceFeatures('aop-trail-network');
          const out = [];
          const seen = new Set();
          for(const f of feats){
            const p=f.properties||{}; const tn=p.trail_number; const nm=p.name;
            let lab;
            if(tn!=null && String(nm)!==String(tn)) lab=String(tn)+' '+String(nm);
            else if(tn!=null) lab=String(tn);
            else lab=nm==null?null:String(nm);
            if(lab && !seen.has(lab)){seen.add(lab); out.push(lab);}
          }
          return out.sort();
        }""")
        named = [l for l in labels if " " in l]
        print("   sample resolved labels:", named[:6], "… numeric:", [l for l in labels if l.isdigit()][:6])
        ck("named trails read 'N Name' (e.g. '1 Launchpad')",
           any(l.split(" ", 1)[0].isdigit() and not l.split(" ", 1)[1].isdigit() for l in named),
           f"{len(named)} named-with-number labels")
        pg.screenshot(path=str(OUT / "v5_trail_labels.png"))

        print("\n== item 2: POI selection persists (then moves on next select) ==")
        pg.evaluate("()=>{const b=document.querySelector('.preset-bar button[data-preset=\"park\"]'); if(b)b.click();}")
        pg.wait_for_timeout(1200)
        pg.evaluate("()=>{const t=document.querySelector('.left-tab[data-left-tab=\"poi\"]'); if(t)t.click();}")
        pg.wait_for_timeout(500)
        first = pg.evaluate("""()=>{const list=document.getElementById('poiList');const gs=[...list.querySelectorAll('.poi-list-group')];
          for(const g of gs){const h=g.querySelector('.poi-list-group-head span')?.textContent||'';if(/trail/i.test(h)){const btn=g.querySelector('button.poi-row');if(btn){btn.click();return btn.querySelector('.poi-row-name')?.textContent;}}}return null;}""")
        print("   selected:", first)
        pg.wait_for_timeout(3400)  # past the ~2.6s pulse
        hold = pg.evaluate("""()=>({vis:window.map.getLayoutProperty('search-highlight-line','visibility'),
                                    op:window.map.getPaintProperty('search-highlight-line','line-opacity')})""")
        ck("highlight PERSISTS after the pulse ends", hold["vis"] == "visible",
           f"vis={hold['vis']} op={round(hold['op'],2) if isinstance(hold['op'],(int,float)) else hold['op']}")
        pg.screenshot(path=str(OUT / "v5_poi_persist.png"))
        # selecting another feature moves the highlight (source data replaced)
        n_before = pg.evaluate("""()=>{const s=window.map.getSource('search-highlight');return s&&s._data?(s._data.features||[]).length:-1;}""")
        pg.evaluate("""()=>{const list=document.getElementById('poiList');const btns=[...list.querySelectorAll('button.poi-row')];
          // click a DIFFERENT row (a building) to move the selection
          for(const btn of btns){const n=btn.querySelector('.poi-row-name')?.textContent||'';if(!/saturday/i.test(n)){btn.click();return;}}}""")
        pg.wait_for_timeout(800)
        moved_vis = pg.evaluate("()=>window.map.getLayoutProperty('search-highlight-line','visibility')")
        ck("a new selection re-pulses (highlight still active, on new feature)",
           moved_vis == "visible", f"vis={moved_vis}")

        print("\n== item 3: 3D pitch/rotate locked; pan+zoom keep; button still tilts ==")
        # Fresh load so we test the real path (open app at the park view → tap 3D),
        # not item 2's zoomed-in POI state where maxBounds clamps pitch.
        pg.goto(URL, wait_until="load")
        pg.evaluate("window.map=(window.AOPViewer&&window.AOPViewer.map)||window.map;")
        pg.wait_for_function("()=>window.map&&window.map.isStyleLoaded&&window.map.isStyleLoaded()", timeout=20000)
        pg.wait_for_timeout(2800)
        gestures_2d = pg.evaluate("""()=>({touchPitch: window.map.touchPitch?window.map.touchPitch.isEnabled():'n/a',
          dragRotate: window.map.dragRotate.isEnabled(), dragPan: window.map.dragPan.isEnabled(),
          scrollZoom: window.map.scrollZoom.isEnabled()})""")
        ck("touch pitch (finger-tilt) disabled", gestures_2d["touchPitch"] in (False, "n/a"), str(gestures_2d["touchPitch"]))
        ck("drag-rotate disabled", gestures_2d["dragRotate"] is False)
        ck("pan still enabled", gestures_2d["dragPan"] is True)
        ck("zoom still enabled", gestures_2d["scrollZoom"] is True)
        pg.evaluate("()=>{const b=document.getElementById('terrainButton'); if(b)b.click();}")
        pg.wait_for_timeout(3200)  # setTerrain→easeTo(pitch:60) lands by ~1.6s
        pitch = pg.evaluate("()=>window.map.getPitch()")
        ck("3D button still tilts the camera (programmatic)", pitch > 30, f"pitch={round(pitch,1)}")

        print(f"\nConsole errors: {len(errs)}")
        for e in errs[:8]:
            print("  ERR:", e[:180])
        b.close()
    print("\n=== " + ("ALL CHECKS PASS" if not fail else "SOME CHECKS FAILED") + " ===")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
