#!/usr/bin/env python3
"""Playwright verification for AOP viewer UI presets and layer tuning.

Run after `python3 -m http.server 8000` is serving the `website/` directory.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:8000/")
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "park": "playwright_presets_park.png",
    "topo": "playwright_presets_topo.png",
    "trace": "playwright_presets_trace.png",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def layer_visibility(page, layer_id: str) -> str | None:
    return page.evaluate(
        """(id) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getLayoutProperty(id, 'visibility') || 'visible';
        }""",
        layer_id,
    )


def paint(page, layer_id: str, prop: str):
    return page.evaluate(
        """([id, prop]) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getPaintProperty(id, prop);
        }""",
        [layer_id, prop],
    )


def is_checked(page, toggle_id: str) -> bool:
    return page.locator(f"#{toggle_id}").is_checked()


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 840})
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin=WEBSITE_URL.rstrip("/"))
        page = context.new_page()

        def record_console(msg) -> None:
            if msg.type != "error":
                return
            text = msg.text
            # Trace mode turns online imagery on. Tile-load failures are not
            # preset UI failures, and the viewer has separate imagery checks.
            ignored = (
                "gis.apfo.usda.gov" in text
                or "tnmap.tn.gov" in text
                or "Failed to load resource" in text
            )
            if not ignored:
                console_errors.append(text)

        page.on("console", record_console)

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(700)

        print("\n== Left controls ==")
        check("three top-left preset buttons exist", page.locator(".preset-bar button[data-preset]").count() == 3)
        check("dedicated 3D button exists", page.locator("#terrainButton").count() == 1)
        check("search input sits in the left control cluster", page.locator(".left-controls #searchInput").count() == 1)
        bar_box = page.locator(".left-controls").bounding_box()
        check(
            "left controls are in the top-left",
            bool(bar_box and bar_box["x"] <= 16 and bar_box["y"] <= 16),
            str(bar_box),
        )
        check("Park starts active", page.locator("#presetPark").evaluate("el => el.classList.contains('active')"))
        check("Park keeps land cover on", is_checked(page, "showLandcover"))
        check("Park keeps topo overlays off", not is_checked(page, "showHillshade") and not is_checked(page, "showContours"))
        check("Park background is Muted Earth", paint(page, "background", "background-color") == "#efe7d5")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["park"]))

        print("\n== Topo preset ==")
        page.locator("#presetTopo").click()
        page.wait_for_timeout(900)
        check("Topo button becomes active", page.locator("#presetTopo").evaluate("el => el.classList.contains('active')"))
        check("Topo turns hillshade on", is_checked(page, "showHillshade") and layer_visibility(page, "lidar-hillshade") == "visible")
        check("Topo turns contours on", is_checked(page, "showContours") and layer_visibility(page, "contours-index") == "visible")
        check("Topo turns water and springs on", is_checked(page, "showWater") and is_checked(page, "showSprings"))
        check("Topo changes background", paint(page, "background", "background-color") == "#e7ddc4")
        check("Topo restyles index contours", paint(page, "contours-index", "line-color") == "#5f4934")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["topo"]))

        print("\n== Zoom presets + contour fade ==")
        check("zoom bar has three view buttons",
              page.locator(".zoom-bar button[data-view]").count() == 3)
        minor_opacity = paint(page, "contours-minor", "line-opacity")
        index_opacity = paint(page, "contours-index", "line-opacity")
        check("fine 5 ft contours fade with zoom",
              isinstance(minor_opacity, list) and minor_opacity[0] == "interpolate",
              str(minor_opacity))
        check("index contours tier 50 ft vs 25 ft by zoom",
              isinstance(index_opacity, list)
              and index_opacity[0] == "interpolate"
              and "case" in json.dumps(index_opacity),
              str(index_opacity))

        page.locator("#zoomPavilion").click()
        page.wait_for_timeout(1500)
        pav = page.evaluate("() => ({ z: window.map.getZoom(), c: window.map.getCenter() })")
        check("Pavilion zooms in tight", pav["z"] >= 15.5, f"zoom={pav['z']:.2f}")
        check("Pavilion centers on the 1010 building",
              abs(pav["c"]["lng"] + 85.748268) < 0.01 and abs(pav["c"]["lat"] - 35.090703) < 0.01,
              str(pav["c"]))

        page.locator("#zoomRegion").click()
        page.wait_for_timeout(1500)
        region_zoom = page.evaluate("() => window.map.getZoom()")
        check("Region zooms out wide", region_zoom < pav["z"] - 2,
              f"region={region_zoom:.2f} pavilion={pav['z']:.2f}")

        page.evaluate("() => window.map.jumpTo({ center: [-85.45, 35.42], zoom: 7 })")
        page.wait_for_timeout(400)
        leashed = page.evaluate("() => ({ z: map.getZoom(), c: map.getCenter() })")
        check("camera is leashed to the 9-patch (cannot pan/zoom past it)",
              -85.81 < leashed["c"]["lng"] < -85.70
              and 35.05 < leashed["c"]["lat"] < 35.13
              and leashed["z"] >= region_zoom - 0.5,
              f"z={leashed['z']:.2f} c=({leashed['c']['lng']:.4f},{leashed['c']['lat']:.4f})")

        page.locator("#zoomPark").click()
        page.wait_for_timeout(1500)
        park_zoom = page.evaluate("() => window.map.getZoom()")
        check("Park zoom sits between region and pavilion",
              region_zoom < park_zoom < pav["z"], f"park={park_zoom:.2f}")

        print("\n== Inline layer tuning + snapshot ==")
        page.locator('[data-tune-key="trails"]').click(position={"x": 2, "y": 2})
        check("selecting a layer row does not expand the editor",
              page.locator("#layerEditor").evaluate("el => el.hidden"))
        page.locator('[data-tune-expand-key="trails"]').click()
        check("inline editor can expand trails", page.locator("#layerEditorTitle").inner_text() == "Trails")
        check(
            "editor sits under the expanded layer row",
            page.locator('[data-tune-key="trails"]').evaluate(
                "el => el.nextElementSibling && el.nextElementSibling.id === 'layerEditor'"
            ),
        )
        check("trail tuner reflects visible state", page.locator("#tuneVisible").is_checked())
        check("trail tuner reads current color",
              page.locator("#tuneColor").input_value() == paint(page, "publish-trails", "line-color"))
        check("trail tuner reads current width",
              abs(float(page.locator("#tuneWidth").input_value()) - float(paint(page, "publish-trails", "line-width"))) < 0.01)
        check("trail tuner reads current opacity",
              int(page.locator("#tuneOpacity").input_value()) == round(float(paint(page, "publish-trails", "line-opacity")) * 100))
        page.locator("#tuneColor").fill("#00a6a6")
        page.locator("#tuneWidth").evaluate(
            """el => {
              el.value = '5.2';
              el.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        page.locator("#tuneOpacity").evaluate(
            """el => {
              el.value = '63';
              el.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        page.wait_for_timeout(250)
        check("color knob updates selected layer", paint(page, "publish-trails", "line-color") == "#00a6a6")
        check("width knob updates selected layer", abs(float(paint(page, "publish-trails", "line-width")) - 5.2) < 0.01)
        check("opacity knob updates selected layer", abs(float(paint(page, "publish-trails", "line-opacity")) - 0.63) < 0.01)
        check("status shows unsaved preset modification", "modified" in page.locator("#presetStatus").inner_text())
        page.locator('[data-tune-expand-key="roads"]').click()
        check("roads exposes each configured tuning knob",
              page.locator("#tuneControls .tune-control").count() >= 14,
              f"count={page.locator('#tuneControls .tune-control').count()}")
        page.locator("#snapshotPreset").click()
        page.wait_for_timeout(250)
        saved = page.evaluate("JSON.parse(localStorage.getItem('aop_viewer_preset_settings_v1')).presets.topo")
        check("snapshot saves active preset to localStorage", bool(saved and saved["paints"]["publish-trails"]["line-color"] == "#00a6a6"))

        page.locator("#presetPark").click()
        page.wait_for_timeout(350)
        page.locator("#presetTopo").click()
        page.wait_for_timeout(500)
        check("snapshot persists when preset is re-applied", paint(page, "publish-trails", "line-color") == "#00a6a6")

        print("\n== Clipboard export ==")
        page.locator("#exportSettings").click()
        page.wait_for_timeout(500)
        text = page.evaluate("navigator.clipboard.readText()")
        payload = json.loads(text)
        check("export copied settings JSON", payload.get("schema") == "aop-viewer-preset-settings-v1")
        check("export includes all three presets", set(payload.get("presets", {}).keys()) == {"park", "topo", "trace"})
        check("export includes current state", payload.get("current_state", {}).get("toggles") is not None)

        print("\n== Trace preset ==")
        page.locator("#presetTrace").click()
        page.wait_for_timeout(900)
        check("Trace button becomes active", page.locator("#presetTrace").evaluate("el => el.classList.contains('active')"))
        check("Trace turns land cover off", not is_checked(page, "showLandcover") and layer_visibility(page, "landcover-forest") == "none")
        check("Trace turns imagery and tracing references on",
              is_checked(page, "showUsdaNaip") and is_checked(page, "showSfwda")
              and is_checked(page, "showOsmTracks") and is_checked(page, "showBuildings"))
        check("Trace applies high-contrast boundary color", paint(page, "publish-boundaries", "line-color") == "#fff0b8")
        page.locator('[data-tune-expand-key="sfwda"]').click()
        check("inline editor can expand SFWDA", page.locator("#layerEditorTitle").inner_text() == "SFWDA paper map")
        page.locator("#tuneOpacity").evaluate(
            """el => {
              el.value = '42';
              el.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        page.wait_for_timeout(250)
        check("SFWDA tuner drives the existing opacity slider", page.locator("#sfwdaOpacity").input_value() == "42")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["trace"]))

        print("\n== Mobile layout ==")
        page.set_viewport_size({"width": 500, "height": 760})
        page.wait_for_timeout(350)
        boxes = page.evaluate(
            """() => {
              const bar = document.querySelector('.left-controls').getBoundingClientRect();
              const panel = document.querySelector('.panel').getBoundingClientRect();
              return {
                bar: { x: bar.x, y: bar.y, width: bar.width, height: bar.height },
                panel: { x: panel.x, y: panel.y, width: panel.width, height: panel.height }
              };
            }"""
        )
        separated = boxes["bar"]["y"] + boxes["bar"]["height"] <= boxes["panel"]["y"]
        check("left controls do not overlap panel on narrow screens", separated, str(boxes))

        print("\n== Console summary ==")
        check("no non-tile console errors", len(console_errors) == 0,
              f"{len(console_errors)} error(s): {console_errors[:3]}")

        browser.close()

    print("\nScreenshots:")
    for name in SCREENSHOTS.values():
        print(f"  - {OUTPUT_DIR / name}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
