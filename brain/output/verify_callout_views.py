#!/usr/bin/env python3
"""Verify region callouts (visitor context) now persist across ALL read-core presets.

Change under test: viewer_core.js BUILT_IN_PRESETS — showVisitorContext flipped
on for `trace` and `satellite` (was Park/Topo only), plus a label-forward
visitor-context paint block added to the Satellite preset.

Targets the READ CORE (website/index.html → js/viewer_core.js, window.AOPViewer),
not the editor surface that playwright_verify_presets.py / _visitor_context.py
drive. Run after `cd website && python3 -m http.server 8001`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).resolve().parent
URL = os.environ.get("WEBSITE_URL", "http://localhost:8001/")

CALLOUT_LAYERS = ["visitor-context-fill", "visitor-context-outline", "visitor-context-labels"]
PRESETS = ["park", "topo", "trace", "satellite"]
SCREENSHOTS = {p: f"callout_views_{p}.png" for p in PRESETS}


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def visibility(page, layer_id: str):
    return page.evaluate(
        """(id) => {
          const m = window.map;
          if (!m || !m.getLayer || !m.getLayer(id)) return null;
          return m.getLayoutProperty(id, 'visibility') || 'visible';
        }""",
        layer_id,
    )


def rendered(page, layer_id: str) -> int:
    return page.evaluate(
        """(id) => {
          const m = window.map;
          if (!m || !m.getLayer || !m.getLayer(id)) return -1;
          return m.queryRenderedFeatures({ layers: [id] }).length;
        }""",
        layer_id,
    )


def main() -> int:
    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader"])
        context = browser.new_context(viewport={"width": 1280, "height": 840})
        page = context.new_page()

        def record(msg):
            if msg.type != "error":
                return
            t = msg.text
            ignored = (
                "tnmap.tn.gov" in t
                or "gis.apfo.usda.gov" in t
                or "Failed to load resource" in t
                or "AJAXError: Failed to fetch (0):" in t
                or t.strip().endswith("TypeError: Failed to fetch")
            )
            if not ignored:
                console_errors.append(t)

        page.on("console", record)

        print(f"Opening {URL}")
        page.goto(URL, wait_until="load")
        page.wait_for_function(
            """() => {
              const v = window.AOPViewer;
              return v && v.map && v.map.getLayer
                && v.map.getLayer('visitor-context-fill') && v.map.isStyleLoaded();
            }""",
            timeout=45_000,
            polling=500,
        )
        page.evaluate("() => { window.map = window.AOPViewer.map; }")
        page.wait_for_timeout(500)

        for preset in PRESETS:
            print(f"\n== {preset.title()} preset ==")
            page.locator(f"#preset{preset.title()}").click()
            page.wait_for_timeout(600)
            check(f"{preset} button active",
                  page.locator(f"#preset{preset.title()}").evaluate("el => el.classList.contains('active')"))
            for layer in CALLOUT_LAYERS:
                vis = visibility(page, layer)
                check(f"{preset}: {layer} visible", vis == "visible", f"visibility={vis}")
            # Frame the whole region so both edge-placed callouts are on screen,
            # then confirm the fill actually paints (camera-dependent) + shoot it.
            page.evaluate("() => { window.map.fitBounds(window.AOPViewer.regionBounds, { animate: false, padding: 20 }); }")
            page.wait_for_timeout(900)
            rc = rendered(page, "visitor-context-fill")
            check(f"{preset}: callout circles render in region view", rc > 0, f"{rc} rendered")
            page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS[preset]))

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
