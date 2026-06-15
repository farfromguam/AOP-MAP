#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that the ~13 MB lidar-
contour GeoJSON is NO LONGER fetched on the default (Park) load, and instead loads
lazily the first time the user presses the Topo preset.

User: the viewer "takes a long time to load on phones." Cause found:
`viewer_core.js` fetched `gold_aop_contours.geojson` (~12.9 MB) with a BLOCKING
`await` inside `map.on('load')`, even though contours are visibility:none in every
preset except Topo (default is Park). Every layer after it (water/roads/buildings/
trails/waypoints/parcel/schedule) was serialized BEHIND that 13 MB download+parse.

Fix: removed the eager fetch; added `ensureContours()` called from `applyPreset`
only when a preset (Topo) turns contours on. The SW already excludes contours from
precache, so nothing pulls the 13 MB until Topo is pressed.

Checks the REAL running app:
  - PARK (default): no network request to gold_aop_contours.geojson; the
    `aop-contours` source does NOT exist; yet park content (waypoints + buildings)
    IS loaded — proving it's no longer blocked behind contours.
  - TOPO press: the contour request now fires; the source + layers get added; the
    contours-index layer becomes visible.
  - No console errors throughout.

Run: python3 brain/output/verify_contours_lazy_load.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
CONTOUR_URL_FRAGMENT = "gold_aop_contours.geojson"


def log(m):
    print(m, flush=True)


def main():
    R = {}
    errors = []
    requests = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.set_default_timeout(8000)
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("request", lambda r: requests.append(r.url))
        log("goto (Park is the default preset)")
        page.goto(URL, wait_until="load")
        # Park content must be ready WITHOUT waiting on contours.
        page.wait_for_function(
            "() => window.AOPViewer && window.AOPViewer.map && window.AOPViewer.map.isStyleLoaded()"
            " && window.AOPViewer.map.getSource('aop-waypoints')"
            " && window.AOPViewer.map.getSource('fema-buildings')",
            timeout=45000)
        page.wait_for_timeout(1500)

        R["park"] = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            return {
                has_waypoints: !!m.getSource('aop-waypoints'),
                has_buildings: !!m.getSource('fema-buildings'),
                has_contours_source: !!m.getSource('aop-contours'),
                active_preset: document.querySelector('.preset-bar .active')?.dataset.preset || null
            };
        }""")
        R["park"]["contour_requests"] = [u for u in requests if CONTOUR_URL_FRAGMENT in u]
        log(f"PARK: {json.dumps(R['park'])}")

        # --- Press Topo: contours should lazy-load now ---
        n_before = len(requests)
        page.click("#presetTopo")
        page.wait_for_function(
            "() => { const m = window.AOPViewer.map;"
            " return m.getSource('aop-contours') && m.getLayer('contours-index'); }",
            timeout=30000)
        page.wait_for_timeout(800)
        R["topo"] = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            const vis = (id) => m.getLayer(id) ? m.getLayoutProperty(id, 'visibility') : 'absent';
            return {
                has_contours_source: !!m.getSource('aop-contours'),
                contours_index_visibility: vis('contours-index'),
                contours_minor_visibility: vis('contours-minor'),
                active_preset: document.querySelector('.preset-bar .active')?.dataset.preset || null
            };
        }""")
        R["topo"]["contour_requests_after"] = [u for u in requests if CONTOUR_URL_FRAGMENT in u]
        log(f"TOPO: {json.dumps(R['topo'])}")

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    park = R["park"]
    topo = R["topo"]
    # MapLibre reports a layer with no explicit visibility set as 'visible'; Topo's
    # showContours flips contours-index on, so 'visible' is the pass state.
    checks = {
        "PARK is the default preset": park["active_preset"] == "park",
        "PARK loads waypoints (park content present)": park["has_waypoints"] is True,
        "PARK loads buildings (park content present)": park["has_buildings"] is True,
        "PARK did NOT fetch the 13 MB contours": park["contour_requests"] == [],
        "PARK has NO contour source": park["has_contours_source"] is False,
        "TOPO lazy-fetched the contours (exactly once)": len(topo["contour_requests_after"]) == 1,
        "TOPO added the contour source": topo["has_contours_source"] is True,
        "TOPO shows contours-index": topo["contours_index_visibility"] == "visible",
        "No console errors": len(real_errors) == 0,
    }
    print(json.dumps(R, indent=2), flush=True)
    print("\n--- CHECKS ---", flush=True)
    allok = True
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}", flush=True)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}", flush=True)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
