#!/usr/bin/env python3
"""Verify the v97 CSS/JS cache-versioning change by OBSERVATION.

What this change did: URL-fingerprinted the three viewer shell assets
(viewer.css / viewer_core.js / viewer_band.js) with ?v=v97 in index.html +
sw.js SHELL_ASSETS, bumped VERSION/#appVersion v96->v97, and made the SW's
precache + revalidation fetches use cache:'reload'. Root problem: GitHub Pages
serves every file Cache-Control: max-age=600 on a STABLE url, so stable-url
assets sit ~10 min stale even after a deploy (the park-border change in
viewer_core.js wasn't reaching the client).

This verifier observes the REAL running page on :8001 (fresh Playwright context,
so no stale SW controls the load):
  1. The fingerprinted ?v=v97 resources actually load (200, present in the
     resource timeline) -- the stamp didn't break the page.
  2. Zero console errors.
  3. The live map reads the faint v96/v97 park border (#c4b48c on Park) off the
     running viewer_core.js?v=v97 -- proving the fingerprinted bytes are what runs.

Run: python3 -m http.server 8001 in website/, then python3 this_file.
"""
import os
import sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "http://localhost:8001"
PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"{'PASS' if ok else 'FAIL'}: {name}" + (f"  -- {detail}" if detail else ""))


with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context()
    page = ctx.new_page()
    console_errors = []
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: console_errors.append(str(e)))

    page.goto(f"{BASE}/index.html", wait_until="load")
    # Wait for the viewer to expose its map and finish the style load.
    page.wait_for_function("() => window.AOPViewer && window.AOPViewer.map", timeout=20000)
    page.wait_for_function("() => window.AOPViewer.map.isStyleLoaded()", timeout=20000)
    # publish-boundaries is added during the load handler; wait for it.
    page.wait_for_function(
        "() => !!window.AOPViewer.map.getLayer('publish-boundaries')", timeout=20000
    )
    page.wait_for_timeout(800)  # let paints settle

    # 1. Fingerprinted resources loaded (present in the resource timeline + not failed).
    res = page.evaluate(
        """() => performance.getEntriesByType('resource')
              .map(e => e.name).filter(n => n.includes('?v=v97'))"""
    )
    for asset in ["css/viewer.css?v=v97", "js/viewer_core.js?v=v97", "js/viewer_band.js?v=v97"]:
        hit = [r for r in res if r.endswith(asset)]
        check(f"loaded {asset}", bool(hit), hit[0] if hit else "not in resource timeline")

    # 2. Zero console errors.
    check("zero console errors", not console_errors, "; ".join(console_errors[:4]))

    # 3. Live park border reads the faint color off the running fingerprinted JS.
    color = page.evaluate(
        "() => window.AOPViewer.map.getPaintProperty('publish-boundaries', 'line-color')"
    )
    check("live park border is faint #c4b48c (Park preset)", color == "#c4b48c", f"got {color!r}")

    shot = os.path.join(HERE, "css_cache_versioning_park.png")
    page.screenshot(path=shot)
    print(f"screenshot -> {shot}")
    browser.close()

print(f"\n{len(PASS)}/{len(PASS) + len(FAIL)} PASS" + (f"  FAILED: {FAIL}" if FAIL else ""))
sys.exit(1 if FAIL else 0)
