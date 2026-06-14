#!/usr/bin/env python3
"""Verify the new camp-waypoints layer + Shower House render in the live viewer.
Observes :8001 directly. Card: brain/tasks/14_illustrator_trace/satellite_illustrator_export.md
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
NOISE = ("WebGL", "GL_", "shader", "Program", "framebuffer", "texImage",
         "willReadFrequently", "Failed to load resource")


def is_noise(t):
    return any(k.lower() in t.lower() for k in NOISE)


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_context(viewport={"width": 1200, "height": 900}).new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("() => window.AOPViewer && window.AOPViewer.map", timeout=20000)
        page.wait_for_function(
            "() => { try { return !!window.AOPViewer.map.getLayer('aop-waypoints'); }"
            " catch(e){ return false; } }", timeout=25000)
        info = page.evaluate("""async () => {
            const m = window.AOPViewer.map;
            const wp = await (await fetch('data/aop_waypoints_traced.geojson')).json();
            const bd = await (await fetch('data/aop_buildings.geojson')).json();
            // frame the camp cluster (mean of waypoint coords) so the markers paint
            let sx=0, sy=0; wp.features.forEach(f=>{const c=f.geometry.coordinates; sx+=c[0]; sy+=c[1];});
            const cx=sx/wp.features.length, cy=sy/wp.features.length;
            m.jumpTo({center:[cx,cy], zoom:16});
            await new Promise(r=>setTimeout(r,1500));
            const rendered = m.queryRenderedFeatures({layers:['aop-waypoints']});
            const labels = m.queryRenderedFeatures({layers:['aop-waypoints-labels']});
            return {
              hasLayer: !!m.getLayer('aop-waypoints'),
              hasLabels: !!m.getLayer('aop-waypoints-labels'),
              wpCount: wp.features.length,
              wpNamed: wp.features.filter(f=>f.properties.name).length,
              renderedWaypoints: rendered.length,
              renderedLabels: labels.length,
              buildingCount: bd.features.length,
              hasShowerHouse: bd.features.some(f=>f.properties.name==='Shower House'),
            };
        }""")
        page.screenshot(path="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/illustrator_trace/_verify_waypoints_live.png")
        b.close()

    for k, v in info.items():
        print(f"  {k}: {v}")
    fatal = [e for e in errors if not is_noise(e)]
    print(f"  console errors: {len(errors)} (fatal={len(fatal)})")
    for e in fatal[:8]:
        print("   FATAL:", e)
    ok = (info["hasLayer"] and info["hasLabels"] and info["wpCount"] == 26
          and info["renderedWaypoints"] > 0 and info["hasShowerHouse"]
          and info["buildingCount"] == 6 and not fatal)
    print("RESULT:", "PASS — waypoints layer + Shower House render live, no fatal errors"
          if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
