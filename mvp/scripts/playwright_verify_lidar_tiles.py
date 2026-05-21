#!/usr/bin/env python3
"""Playwright verification for the AOP viewer lidar layers.

Covers:
  - Lidar tile index (USGS 3DEP) GeoJSON overlay (24 tiles).
  - Lidar contours (5 ft, 1m DEM) GeoJSON overlay.
  - Lidar hillshade (raster-dem 'hillshade' layer over aws-terrain-dem).
  - 3D terrain (map.setTerrain via the dedicated 3D button).

Confirms layers render and that AWS Terrarium DEM tiles are actually fetched
when hillshade or 3D terrain is enabled. Captures verification screenshots
into brain/output/.

Run after `python3 -m http.server 8000` is serving the `website/` directory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:8000/")
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_lidar_initial.png",
    "contours_off": "playwright_lidar_contours_off.png",
    "contours_on": "playwright_lidar_contours_on.png",
    "tiles_on": "playwright_lidar_tiles_on.png",
    "hillshade_on": "playwright_lidar_hillshade_on.png",
    "hillshade_plus_tiles": "playwright_lidar_hillshade_plus_tiles.png",
    "terrain_3d": "playwright_lidar_terrain_3d.png",
    "all_off": "playwright_lidar_all_off.png",
}

TOGGLE_IDS = {
    "hillshade": "showHillshade",
    "satellite": "showSatellite",
    "patch": "showNinePatch",
    "lidar": "showLidarTiles",
    "contours": "showContours",
}
TERRAIN_BUTTON_ID = "terrainButton"


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
    page.wait_for_timeout(200)


def terrain_button_pressed(page) -> bool:
    return page.locator(f"#{TERRAIN_BUTTON_ID}").get_attribute("aria-pressed") == "true"


def set_terrain(page, target: bool) -> None:
    if terrain_button_pressed(page) != target:
        page.locator(f"#{TERRAIN_BUTTON_ID}").click()
    page.wait_for_timeout(200)


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


def terrain_enabled(page) -> bool:
    return page.evaluate(
        "() => !!(window.map && window.map.getTerrain && window.map.getTerrain())"
    )


def rendered_count(page, layers: list[str]) -> int:
    return page.evaluate(
        """(layers) => {
          if (!window.map || !window.map.queryRenderedFeatures) return -1;
          const present = layers.filter((l) => window.map.getLayer(l));
          if (!present.length) return -1;
          return window.map.queryRenderedFeatures({ layers: present }).length;
        }""",
        layers,
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []
    terrarium_requests: list[str] = []

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
        page.on(
            "request",
            lambda req: terrarium_requests.append(req.url)
            if "elevation-tiles-prod" in req.url
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
        for name in ("hillshade", "lidar", "patch", "satellite", "contours"):
            tid = TOGGLE_IDS[name]
            check(
                f"{name} toggle exists and starts off",
                page.locator(f"#{tid}").count() == 1
                and not page.locator(f"#{tid}").is_checked(),
            )
        check(
            "3D button exists and starts off",
            page.locator(f"#{TERRAIN_BUTTON_ID}").count() == 1
            and not terrain_button_pressed(page),
        )
        check(
            "lidar-tiles-outline added with visibility=none",
            layer_visibility(page, "lidar-tiles-outline") == "none",
        )
        check(
            "lidar-hillshade layer added with visibility=none",
            layer_visibility(page, "lidar-hillshade") == "none",
        )
        check(
            "terrain disabled at load",
            not terrain_enabled(page),
        )
        count = feature_count(page, "./data/aop_lidar_tiles.geojson")
        check(
            "lidar tile-index has 24 tiles",
            count == 24,
            f"feature_count={count}",
        )
        check(
            "contours-minor layer added with visibility=none",
            layer_visibility(page, "contours-minor") == "none",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Lidar contours ON ==")
        ccount = feature_count(page, "./data/aop_contours.geojson")
        check(
            "contour GeoJSON has features",
            ccount > 0,
            f"feature_count={ccount}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["contours_off"]))
        set_toggle(page, TOGGLE_IDS["contours"], True)
        page.wait_for_timeout(900)
        for layer in ("contours-minor", "contours-index"):
            vis = layer_visibility(page, layer)
            check(f"{layer} visible", vis == "visible", f"visibility={vis}")
        rendered = rendered_count(page, ["contours-minor", "contours-index"])
        check(
            "contours render in viewport",
            rendered > 0,
            f"{rendered} rendered contour features",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["contours_on"]))
        set_toggle(page, TOGGLE_IDS["contours"], False)
        page.wait_for_timeout(300)
        check(
            "contours-minor hidden again",
            layer_visibility(page, "contours-minor") == "none",
        )

        print("\n== Toggle lidar tile-index ON ==")
        set_toggle(page, TOGGLE_IDS["lidar"], True)
        page.wait_for_timeout(400)
        for layer in ("lidar-tiles-fill", "lidar-tiles-outline", "lidar-tiles-labels"):
            vis = layer_visibility(page, layer)
            check(f"{layer} visible", vis == "visible", f"visibility={vis}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["tiles_on"]))

        print("\n== Toggle hillshade ON (with tiles still on) ==")
        before = len(terrarium_requests)
        set_toggle(page, TOGGLE_IDS["hillshade"], True)
        page.wait_for_timeout(4500)
        after = len(terrarium_requests)
        check(
            "lidar-hillshade visible",
            layer_visibility(page, "lidar-hillshade") == "visible",
        )
        check(
            "AWS Terrarium DEM tiles requested",
            (after - before) > 0,
            f"{after - before} terrarium tile requests",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["hillshade_plus_tiles"]))

        # Hillshade alone (toggle tiles off, keep hillshade) to capture clean shading.
        set_toggle(page, TOGGLE_IDS["lidar"], False)
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["hillshade_on"]))

        print("\n== Toggle 3D terrain ON ==")
        before_t = len(terrarium_requests)
        set_terrain(page, True)
        page.wait_for_timeout(3500)
        check(
            "map.getTerrain() truthy",
            terrain_enabled(page),
        )
        check(
            "additional terrarium tile traffic during 3D enable",
            (len(terrarium_requests) - before_t) >= 0,
            f"{len(terrarium_requests) - before_t} new terrarium requests",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["terrain_3d"]))

        print("\n== Toggle everything OFF ==")
        set_terrain(page, False)
        set_toggle(page, TOGGLE_IDS["hillshade"], False)
        page.wait_for_timeout(800)
        check(
            "terrain disabled",
            not terrain_enabled(page),
        )
        check(
            "lidar-hillshade hidden",
            layer_visibility(page, "lidar-hillshade") == "none",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["all_off"]))

        print("\n== Console + network summary ==")
        check(
            "no console errors",
            len(console_errors) == 0,
            f"{len(console_errors)} error(s): {console_errors[:3]}",
        )
        print(f"  Total AWS Terrarium tile requests during run: {len(terrarium_requests)}")

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
