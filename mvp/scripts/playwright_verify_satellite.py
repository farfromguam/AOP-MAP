#!/usr/bin/env python3
"""Playwright verification for the AOP viewer imagery + 9-patch layers.

Loads the static viewer at http://localhost:8000/, exercises every toggle,
confirms the TNMap and USDA NAIP tile networks are hit when their imagery
layers are enabled, and captures screenshots into brain/output/.

Run after `python3 -m http.server 8000` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:8000/")
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_satellite_initial.png",
    "satellite_on": "playwright_satellite_on.png",
    "usda_naip_on": "playwright_usda_naip_on.png",
    "satellite_plus_patch": "playwright_satellite_plus_patch.png",
    "patch_only": "playwright_patch_only.png",
    "all_off": "playwright_all_off.png",
}

TOGGLE_IDS = {
    "satellite": "showSatellite",
    "usda_naip": "showUsdaNaip",
    "patch": "showNinePatch",
    "trails": "showTrails",
    "boundaries": "showBoundaries",
    "trailheads": "showTrailheads",
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


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []
    tnmap_tile_requests: list[str] = []
    usda_tile_requests: list[str] = []

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
            lambda req: tnmap_tile_requests.append(req.url)
            if "tnmap.tn.gov" in req.url
            else None,
        )
        page.on(
            "request",
            lambda req: usda_tile_requests.append(req.url)
            if "gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME" in req.url
            else None,
        )

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")

        # Expose the map on window so we can introspect layer state.
        page.evaluate("window.map = map;")

        # Wait for the publish layer to load (message text changes).
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        print(f"\n== Initial state ==")
        check(
            "title is AOP Map Viewer",
            page.title() == "AOP Map Viewer",
            page.title(),
        )
        check(
            "satellite toggle exists and starts off",
            page.locator(f"#{TOGGLE_IDS['satellite']}").count() == 1
            and not page.locator(f"#{TOGGLE_IDS['satellite']}").is_checked(),
        )
        check(
            "USDA NAIP toggle exists and starts off",
            page.locator(f"#{TOGGLE_IDS['usda_naip']}").count() == 1
            and not page.locator(f"#{TOGGLE_IDS['usda_naip']}").is_checked(),
        )
        check(
            "9-patch toggle exists and starts off",
            page.locator(f"#{TOGGLE_IDS['patch']}").count() == 1
            and not page.locator(f"#{TOGGLE_IDS['patch']}").is_checked(),
        )
        check(
            "tnmap-satellite layer added with visibility=none",
            layer_visibility(page, "tnmap-satellite") == "none",
        )
        check(
            "usda-naip-satellite layer added with visibility=none",
            layer_visibility(page, "usda-naip-satellite") == "none",
        )
        check(
            "nine-patch-outline layer added with visibility=none",
            layer_visibility(page, "nine-patch-outline") == "none",
        )
        check(
            "publish-boundaries visible by default",
            layer_visibility(page, "publish-boundaries") == "visible",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print(f"\n== Toggle satellite ON ==")
        before_tile_count = len(tnmap_tile_requests)
        set_toggle(page, TOGGLE_IDS["satellite"], True)
        # Wait for tiles. Tile requests are network-dependent; allow some time.
        page.wait_for_timeout(4000)
        new_tnmap = len(tnmap_tile_requests) - before_tile_count
        check(
            "satellite layer visible after toggle",
            layer_visibility(page, "tnmap-satellite") == "visible",
        )
        check(
            "TNMap tiles requested",
            new_tnmap > 0,
            f"{new_tnmap} requests to tnmap.tn.gov after enabling satellite",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["satellite_on"]))

        print(f"\n== Toggle USDA NAIP ON ==")
        set_toggle(page, TOGGLE_IDS["satellite"], False)
        before_usda_count = len(usda_tile_requests)
        set_toggle(page, TOGGLE_IDS["usda_naip"], True)
        page.wait_for_timeout(4000)
        new_usda = len(usda_tile_requests) - before_usda_count
        check(
            "USDA NAIP layer visible after toggle",
            layer_visibility(page, "usda-naip-satellite") == "visible",
        )
        check(
            "USDA NAIP tiles requested",
            new_usda > 0,
            f"{new_usda} requests to gis.apfo.usda.gov after enabling NAIP",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["usda_naip_on"]))

        print(f"\n== Toggle 9-patch ON ==")
        set_toggle(page, TOGGLE_IDS["patch"], True)
        page.wait_for_timeout(500)
        check(
            "nine-patch-outline visible",
            layer_visibility(page, "nine-patch-outline") == "visible",
        )
        check(
            "nine-patch-fill visible",
            layer_visibility(page, "nine-patch-fill") == "visible",
        )
        check(
            "nine-patch-labels visible",
            layer_visibility(page, "nine-patch-labels") == "visible",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["satellite_plus_patch"]))

        print(f"\n== Toggle satellite OFF, keep patch ON ==")
        set_toggle(page, TOGGLE_IDS["satellite"], False)
        set_toggle(page, TOGGLE_IDS["usda_naip"], False)
        page.wait_for_timeout(300)
        check(
            "satellite layer hidden",
            layer_visibility(page, "tnmap-satellite") == "none",
        )
        check(
            "USDA NAIP layer hidden",
            layer_visibility(page, "usda-naip-satellite") == "none",
        )
        check(
            "nine-patch still visible",
            layer_visibility(page, "nine-patch-outline") == "visible",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["patch_only"]))

        print(f"\n== Toggle every layer OFF ==")
        for key in ("patch", "usda_naip", "trails", "boundaries", "trailheads"):
            set_toggle(page, TOGGLE_IDS[key], False)
        page.wait_for_timeout(300)
        for layer in (
            "tnmap-satellite",
            "usda-naip-satellite",
            "nine-patch-outline",
            "publish-trails",
            "publish-boundaries",
            "publish-boundary-fill",
            "publish-trailheads",
        ):
            vis = layer_visibility(page, layer)
            check(f"{layer} hidden", vis == "none", f"visibility={vis}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["all_off"]))

        print(f"\n== Console / network summary ==")
        check(
            "no console errors",
            len(console_errors) == 0,
            f"{len(console_errors)} error(s): {console_errors[:3]}",
        )
        print(f"  Total TNMap tile requests during run: {len(tnmap_tile_requests)}")
        print(f"  Total USDA NAIP tile requests during run: {len(usda_tile_requests)}")

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
