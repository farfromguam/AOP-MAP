#!/usr/bin/env python3
"""Verify the facility name pins + labels render in the live viewer.
Front Office / Farmhouse / Pavilion / Shower House each get a rust pin + name.
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
        page = b.new_context(viewport={"width": 1000, "height": 800}).new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function(
            "() => { try { return !!window.AOPViewer.map.getLayer('aop-facility-labels'); }"
            " catch(e){ return false; } }", timeout=20000)
        page.wait_for_timeout(9000)  # let the on-load park fit settle before zooming in
        info = page.evaluate("""async () => {
            const m = window.AOPViewer.map;
            const bd = await (await fetch('data/aop_buildings.geojson')).json();
            const fac = bd.features.filter(f => f.properties.aop_facility === true
                                                && f.properties.centroid_lng != null);
            const names = fac.map(f => f.properties.facility_name || f.properties.name);
            // frame the camp facilities and hold (zoom in past the z14 load-fit)
            m.jumpTo({ center: [-85.7472, 35.0902], zoom: 16.4 });
            await new Promise(r => setTimeout(r, 1800));
            return {
              hasPin: !!m.getLayer('aop-facility-pin'),
              hasLabels: !!m.getLayer('aop-facility-labels'),
              facilityCount: fac.length, names,
              renderedPins: m.queryRenderedFeatures({layers:['aop-facility-pin']}).length,
              renderedLabels: m.queryRenderedFeatures({layers:['aop-facility-labels']}).length,
              zoom: +m.getZoom().toFixed(2),
            };
        }""")
        page.screenshot(path="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/illustrator_trace/_verify_facility_labels.png")
        b.close()

    for k, v in info.items():
        print(f"  {k}: {v}")
    fatal = [e for e in errors if not is_noise(e)]
    print(f"  console errors: {len(errors)} (fatal={len(fatal)})")
    for e in fatal[:8]:
        print("   FATAL:", e)
    ok = (info["hasPin"] and info["hasLabels"] and info["facilityCount"] == 4
          and info["renderedPins"] == 4 and info["renderedLabels"] == 4 and not fatal)
    print("RESULT:", "PASS — 4 facility pins + 4 names render live, no fatal errors"
          if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
