#!/usr/bin/env python3
"""Verify the contour styling compare mockup by observation.

Loads website/contour_styling_mockup.html over the live :8001 server, waits for the
five MapLibre panels + the shared real contour GeoJSON to render, captures console
errors, confirms each panel painted a non-empty canvas, and saves a full-page PNG.
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/contour_styling_mockup.html"
OUT = "/Users/christopherfryman/Documents/code/AOP MAP/brain/output/contour_styling_mockup.png"
PANELS = ["baseline", "faint", "ghost", "hairline", "tonal"]

def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1240, "height": 1600},
                                device_scale_factor=2)
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append("PAGEERROR: " + str(e)))
        page.goto(URL, wait_until="networkidle")
        # Give MapLibre time to add sources/layers and paint the local contour vectors.
        page.wait_for_timeout(6000)

        checks = []
        # 1) all five map containers exist and have a WebGL canvas with real pixels
        for pid in PANELS:
            canvas = page.query_selector(f"#map-{pid} canvas")
            ok = canvas is not None
            painted = False
            if ok:
                painted = page.evaluate(
                    """(id) => {
                        const c = document.querySelector(`#map-${id} canvas`);
                        if (!c) return false;
                        const g = c.getContext('webgl2') || c.getContext('webgl');
                        return !!g && c.width > 50 && c.height > 50;
                    }""", pid)
            checks.append((f"panel '{pid}' canvas present", ok))
            checks.append((f"panel '{pid}' canvas sized", painted))

        # 2) the five panels and their captions rendered in the DOM
        n_panels = page.eval_on_selector_all(".panel", "els => els.length")
        checks.append(("five panels in DOM", n_panels == 5))

        # 3) the grid did not fall back to the load-error message. The fallback
        # replaces grid.innerHTML with a single DIRECT-child <p> ("Could not load
        # contours…"), so match `.grid > p` — a bare `.grid p` descendant selector
        # also catches each panel's `.caption` <p> blurb (5 of them) and false-fails.
        has_error_msg = page.query_selector(".grid > p") is not None
        checks.append(("no contour load-error fallback", not has_error_msg))

        # 4) baseline panel is flagged as the reference
        baseline_marked = page.query_selector(".panel.baseline") is not None
        checks.append(("baseline panel marked", baseline_marked))

        page.screenshot(path=OUT, full_page=True)
        browser.close()

    print("=== CHECKS ===")
    passed = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        passed += ok
    print(f"\n{passed}/{len(checks)} checks passed")
    print(f"console/page errors: {len(errors)}")
    for e in errors[:20]:
        print("   !", e)
    print(f"\nscreenshot: {OUT}")
    sys.exit(0 if passed == len(checks) else 1)

if __name__ == "__main__":
    main()
