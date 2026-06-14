#!/usr/bin/env python3
"""Verify the index page stays at park zoom on load — no auto-peek jump to
region zoom and back. Samples map.getZoom() across the full former peek window."""
import sys, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"

def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1200, "height": 900})
        page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL, wait_until="domcontentloaded")

        # Wait for the map object + first framing to settle.
        page.wait_for_function("() => window.AOPViewer && window.AOPViewer.map", timeout=20000)
        page.wait_for_function(
            "() => { const m = window.AOPViewer.map; return m.isStyleLoaded() && m.getZoom() > 12.5; }",
            timeout=20000,
        )

        # Sample zoom every 150ms for ~7s — covers the old peek window
        # (idle -> 900ms fitBounds region -> 2000ms hold -> 1100ms easeTo home,
        # plus the 4500ms cap path). If the peek were still live we'd see a dip.
        trace = []
        t0 = time.time()
        while time.time() - t0 < 7.0:
            z = page.evaluate("() => window.AOPViewer.map.getZoom()")
            trace.append(round(z, 3))
            time.sleep(0.15)

        zmin, zmax = min(trace), max(trace)
        settled = trace[3:]  # drop first ~450ms in case framing still settling
        smin, smax = min(settled), max(settled)
        spread = round(smax - smin, 3)

        print(f"samples: {len(trace)}")
        print(f"zoom min/max (all):     {zmin} / {zmax}")
        print(f"zoom min/max (settled): {smin} / {smax}  spread={spread}")
        print(f"trace: {trace}")
        print(f"console errors: {len(errors)}")
        for e in errors[:10]:
            print("  ERR:", e)

        # PASS criteria: after settling, the camera holds park zoom — no region
        # peek. The peek dipped to ~11.5-12 (whole-region fitBounds) then back;
        # a held park view varies by <0.5 zoom.
        ok = spread < 0.5 and smin > 12.5 and len(errors) == 0
        print("RESULT:", "PASS — stays at park zoom, no load jump" if ok else "FAIL")

        # Screenshot the settled view for the record.
        page.screenshot(path="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/no_load_peek_settled.png")
        browser.close()
        return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
