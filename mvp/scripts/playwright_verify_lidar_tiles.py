#!/usr/bin/env python3
"""Playwright verification for the AOP viewer lidar tile-index layer.

Loads the static viewer at http://localhost:8000/, toggles the lidar tile
index, confirms the layers render and that the GeoJSON contains the
expected 24 USGS 3DEP LAZ tile footprints intersecting the 9-patch.

Run after `python3 -m http.server 8000` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = "http://localhost:8000/"
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_lidar_initial.png",
    "lidar_on": "playwright_lidar_on.png",
    "lidar_plus_satellite": "playwright_lidar_plus_satellite.png",
    "lidar_off": "playwright_lidar_off.png",
}

TOGGLE_IDS = {
    "satellite": "showSatellite",
    "patch": "showNinePatch",
    "lidar": "showLidarTiles",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def set_toggle(page, toggle_id: str, target: bool) -> None:
    element = page.locator(f"#{toggle_id}")
    current = element.is_checked()
    if current != target:
        element.click()
    page.wait_for_timeout(150)


def layer_visibility(page, layer_id: str) -> str | None:
    return page.evaluate(
        """(id) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getLayoutProperty(id, 'visibility') || 'visible';
        }""",
        layer_id,
    )


def feature_count(page, url: str) -> int:
    return page.evaluate(
        """async (u) => {
          const r = await fetch(u);
          if (!r.ok) return -1;
          const d = await r.json();
          return (d && d.features) ? d.features.length : -1;
        }""",
        url,
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error"
            else None,
        )

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")

        page.evaluate("window.map = map;")

        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        print("\n== Initial state ==")
        check(
            "lidar toggle exists and starts off",
            page.locator(f"#{TOGGLE_IDS['lidar']}").count() == 1
            and not page.locator(f"#{TOGGLE_IDS['lidar']}").is_checked(),
        )
        check(
            "lidar-tiles-outline added with visibility=none",
            layer_visibility(page, "lidar-tiles-outline") == "none",
        )
        check(
            "lidar-tiles-fill added with visibility=none",
            layer_visibility(page, "lidar-tiles-fill") == "none",
        )
        check(
            "lidar-tiles-labels added with visibility=none",
            layer_visibility(page, "lidar-tiles-labels") == "none",
        )
        count = feature_count(page, "./data/aop_lidar_tiles.geojson")
        check(
            "lidar tile-index loaded 24 tiles",
            count == 24,
            f"feature_count={count}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Toggle lidar ON ==")
        set_toggle(page, TOGGLE_IDS["lidar"], True)
        page.wait_for_timeout(400)
        check(
            "lidar-tiles-outline visible",
            layer_visibility(page, "lidar-tiles-outline") == "visible",
        )
        check(
            "lidar-tiles-fill visible",
            layer_visibility(page, "lidar-tiles-fill") == "visible",
        )
        check(
            "lidar-tiles-labels visible",
            layer_visibility(page, "lidar-tiles-labels") == "visible",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["lidar_on"]))

        print("\n== Toggle lidar + satellite ON together ==")
        set_toggle(page, TOGGLE_IDS["satellite"], True)
        page.wait_for_timeout(3000)
        check(
            "satellite visible underneath",
            layer_visibility(page, "tnmap-satellite") == "visible",
        )
        check(
            "lidar still visible",
            layer_visibility(page, "lidar-tiles-outline") == "visible",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["lidar_plus_satellite"]))

        print("\n== Toggle lidar OFF ==")
        set_toggle(page, TOGGLE_IDS["lidar"], False)
        page.wait_for_timeout(300)
        for layer in (
            "lidar-tiles-outline",
            "lidar-tiles-fill",
            "lidar-tiles-labels",
        ):
            vis = layer_visibility(page, layer)
            check(f"{layer} hidden", vis == "none", f"visibility={vis}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["lidar_off"]))

        print("\n== Console summary ==")
        check(
            "no console errors",
            len(console_errors) == 0,
            f"{len(console_errors)} error(s): {console_errors[:3]}",
        )

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
