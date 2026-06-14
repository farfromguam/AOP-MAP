#!/usr/bin/env python3
"""One-off observation pass for the five-item review (2026-06-14).

Captures the real running viewer (served on :8001) so the fixes are designed
from observed pixels, not theory. Screenshots land in brain/output/obs5_*.png.

Items observed:
  1 trail labels (number-first) — captured in default + network-on shots
  2 POI trail selection persistence — before / during / after the pulse
  3 3D pan/tilt gestures — reports handler enabled-state with 3D on
  4 Park vs Topo vs Trace base colours — preset screenshots + bg sample
  5 vegetation corner render — Region-zoom screenshot + corner pixel sample
"""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).resolve().parent
URL = "http://localhost:8001/index.html"


def grab(page, name):
    page.screenshot(path=str(OUT / f"obs5_{name}.png"))
    print(f"  shot: obs5_{name}.png")


def main():
    errs = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800},
                                  device_scale_factor=2)
        page = ctx.new_page()
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.goto(URL, wait_until="load")
        page.evaluate("window.map = (window.AOPViewer && window.AOPViewer.map) || window.map;")
        page.wait_for_function("() => window.map && window.map.isStyleLoaded && window.map.isStyleLoaded()", timeout=20000)
        page.wait_for_timeout(2500)  # let async layers + presets settle

        print("== item 4/5: default Park view ==")
        grab(page, "01_park_default")
        bg = page.evaluate("() => window.map.getPaintProperty('background','background-color')")
        print("  background:", bg)

        # Layer presence + visibility snapshot
        for lid in ["landcover-9patch-forest", "landcover-forest",
                    "aop-trail-network", "aop-trail-network-labels", "publish-trails"]:
            has = page.evaluate(f"() => !!window.map.getLayer('{lid}')")
            vis = page.evaluate(f"() => window.map.getLayer('{lid}') ? window.map.getLayoutProperty('{lid}','visibility') : 'NO LAYER'")
            print(f"  layer {lid}: present={has} visibility={vis}")

        print("\n== item 5: Region zoom (whole 9-patch) + corner pixels ==")
        page.evaluate("""() => {
            const b = document.querySelector('[data-view=\"region\"]') || document.getElementById('zoomRegion');
            if (b) b.click();
        }""")
        page.wait_for_timeout(2600)
        grab(page, "02_region")
        # sample the rendered fill at the 4 corners via queryRenderedFeatures
        corners = page.evaluate("""() => {
            const c = window.map.getCanvas();
            const w = c.clientWidth, h = c.clientHeight, m = 60;
            const pts = {TL:[m,m], TR:[w-m,m], BL:[m,h-m], BR:[w-m,h-m], C:[w/2,h/2]};
            const out = {};
            for (const k in pts) {
                const f = window.map.queryRenderedFeatures(pts[k], {layers:['landcover-9patch-forest','landcover-forest']});
                out[k] = f.length;
            }
            return out;
        }""")
        print("  queryRenderedFeatures veg-layer hits per corner:", corners)

        print("\n== item 4: Topo + Trace ==")
        page.evaluate("() => { const b=document.querySelector('.preset-bar button[data-preset=\"topo\"]'); if(b) b.click(); }")
        page.wait_for_timeout(2200)
        grab(page, "03_topo")
        topo_bg = page.evaluate("() => window.map.getPaintProperty('background','background-color')")
        page.evaluate("() => { const b=document.querySelector('.preset-bar button[data-preset=\"trace\"]'); if(b) b.click(); }")
        page.wait_for_timeout(2200)
        grab(page, "04_trace")
        trace_bg = page.evaluate("() => window.map.getPaintProperty('background','background-color')")
        print("  topo bg:", topo_bg, " trace bg:", trace_bg)

        # back to Park for the POI test
        page.evaluate("() => { const b=document.querySelector('.preset-bar button[data-preset=\"park\"]'); if(b) b.click(); }")
        page.wait_for_timeout(1500)

        print("\n== item 2: POI trail selection persistence ==")
        # open the POI tab
        page.evaluate("""() => {
            const t = document.querySelector('.left-tab[data-left-tab=\"poi\"]');
            if (t) t.click();
            const drawer = document.querySelector('.lr-icon[data-drawer], .lr-icon-col button');
        }""")
        page.wait_for_timeout(600)
        # ensure the POI panel is visible; click first trail row
        rows = page.evaluate("""() => {
            const list = document.getElementById('poiList');
            if (!list) return {ok:false, why:'no #poiList'};
            const btns = [...list.querySelectorAll('button.poi-row')];
            return {ok:true, count: btns.length, names: btns.slice(0,8).map(b=>b.querySelector('.poi-row-name')?.textContent)};
        }""")
        print("  POI rows:", rows)
        # find a trail row and click it
        clicked = page.evaluate("""() => {
            const list = document.getElementById('poiList');
            if (!list) return null;
            const groups = [...list.querySelectorAll('.poi-list-group')];
            for (const g of groups) {
                const head = g.querySelector('.poi-list-group-head span')?.textContent || '';
                if (/trail/i.test(head)) {
                    const b = g.querySelector('button.poi-row');
                    if (b) { b.click(); return head + ' :: ' + (b.querySelector('.poi-row-name')?.textContent||''); }
                }
            }
            // fallback: first row
            const b = list.querySelector('button.poi-row'); if (b){ b.click(); return 'FALLBACK first row'; }
            return null;
        }""")
        print("  clicked POI row:", clicked)
        page.wait_for_timeout(700)
        grab(page, "05_poi_during_pulse")
        hl_during = page.evaluate("() => ({line: window.map.getLayoutProperty('search-highlight-line','visibility'), pt: window.map.getLayoutProperty('search-highlight-point','visibility')})")
        print("  highlight during pulse:", hl_during)
        page.wait_for_timeout(3200)  # pulse is ~2.6s; this lands after it ends
        grab(page, "06_poi_after_pulse")
        hl_after = page.evaluate("() => ({line: window.map.getLayoutProperty('search-highlight-line','visibility'), pt: window.map.getLayoutProperty('search-highlight-point','visibility')})")
        print("  highlight after pulse:", hl_after)
        # is the backing publish-trails layer visible?
        pt_vis = page.evaluate("() => window.map.getLayer('publish-trails') ? window.map.getLayoutProperty('publish-trails','visibility') : 'NO LAYER'")
        print("  publish-trails visibility after select:", pt_vis)

        print("\n== item 3: 3D gestures ==")
        page.evaluate("() => { const b=document.getElementById('terrainButton'); if(b) b.click(); }")
        page.wait_for_timeout(2500)
        grab(page, "07_3d")
        gestures = page.evaluate("""() => ({
            dragPan: window.map.dragPan.isEnabled(),
            dragRotate: window.map.dragRotate.isEnabled(),
            touchZoomRotate: window.map.touchZoomRotate.isEnabled(),
            touchPitch: window.map.touchPitch ? window.map.touchPitch.isEnabled() : 'n/a',
            pitch: window.map.getPitch(),
            terrain: !!window.map.getTerrain && !!window.map.getTerrain()
        })""")
        print("  gesture handlers (3D on):", gestures)

        print("\nConsole errors:", len(errs))
        for e in errs[:10]:
            print("  ERR:", e[:200])
        browser.close()


if __name__ == "__main__":
    main()
