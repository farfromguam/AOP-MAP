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

        print("\n== Preset bar ==")
        check("three top-left preset buttons exist", page.locator(".preset-bar button").count() == 3)
        bar_box = page.locator(".preset-bar").bounding_box()
        check(
            "preset bar is in the top-left",
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

        print("\n== Layer tuning + snapshot ==")
        page.locator("#layerTuneSelect").select_option("trails")
        check("tuner can select trails", page.locator("#layerTuneSelect").input_value() == "trails")
        check("trail tuner reflects visible state", page.locator("#tuneVisible").is_checked())
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
        page.locator("#layerTuneSelect").select_option("sfwda")
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
              const bar = document.querySelector('.preset-bar').getBoundingClientRect();
              const panel = document.querySelector('.panel').getBoundingClientRect();
              return {
                bar: { x: bar.x, y: bar.y, width: bar.width, height: bar.height },
                panel: { x: panel.x, y: panel.y, width: panel.width, height: panel.height }
              };
            }"""
        )
        separated = boxes["bar"]["y"] + boxes["bar"]["height"] <= boxes["panel"]["y"]
        check("preset bar does not overlap panel on narrow screens", separated, str(boxes))

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
