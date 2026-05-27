#!/usr/bin/env python3
"""Playwright verification for the AOP viewer USGS NHD water layers.

Covers:
  - Streams & waterbodies (USGS NHD) GeoJSON overlay — flowlines, waterbody
    polygons, and the stream/river area polygon.
  - Springs & gages (USGS NHD) — NHD point features.

Confirms the toggles exist and start off, the layers are added hidden,
toggling makes the right layers visible, features render in the viewport,
and the GeoJSON carries the expected feature count. Captures screenshots
into brain/output/.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, set_toggle, layer_visibility, rendered_count


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_water_initial.png",
    "streams_on": "playwright_water_streams_on.png",
    "springs_on": "playwright_water_springs_on.png",
    "water_over_satellite": "playwright_water_over_satellite.png",
    "all_off": "playwright_water_all_off.png",
}

TOGGLE_IDS = {
    "water": "showWater",
    "springs": "showSprings",
    "satellite": "showSatellite",
}

WATER_LAYERS = ["water-area-fill", "waterbody-fill", "waterbody-outline", "streams", "stream-labels"]
SPRING_LAYERS = ["water-points", "water-point-labels"]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


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


def class_counts(page, url: str) -> dict:
    return page.evaluate(
        """async (u) => {
          const r = await fetch(u);
          if (!r.ok) return {};
          const d = await r.json();
          const out = {};
          for (const f of (d.features || [])) {
            const c = f.properties && f.properties.water_class;
            out[c] = (out[c] || 0) + 1;
          }
          return out;
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
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        print("\n== Initial state ==")
        check(
            "water toggle exists and starts ON (Bucket A2 default)",
            page.locator(f"#{TOGGLE_IDS['water']}").count() == 1
            and page.locator(f"#{TOGGLE_IDS['water']}").is_checked(),
        )
        check(
            "springs toggle exists and starts off",
            page.locator(f"#{TOGGLE_IDS['springs']}").count() == 1
            and not page.locator(f"#{TOGGLE_IDS['springs']}").is_checked(),
        )
        for layer in WATER_LAYERS:
            check(
                f"{layer} starts visible (Bucket A2)",
                layer_visibility(page, layer) == "visible",
            )
        for layer in SPRING_LAYERS:
            check(
                f"{layer} added with visibility=none",
                layer_visibility(page, layer) == "none",
            )
        count = feature_count(page, "./data/aop_water.geojson")
        check("aop_water.geojson has 94 features", count == 94, f"feature_count={count}")
        classes = class_counts(page, "./data/aop_water.geojson")
        check(
            "expected water classes present",
            classes.get("stream", 0) > 0
            and classes.get("spring", 0) > 0
            and classes.get("lake_pond", 0) > 0,
            str(classes),
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Streams & waterbodies ON ==")
        set_toggle(page, TOGGLE_IDS["water"], True)
        page.wait_for_timeout(700)
        for layer in WATER_LAYERS:
            vis = layer_visibility(page, layer)
            check(f"{layer} visible", vis == "visible", f"visibility={vis}")
        rendered = rendered_count(page, ["streams"])
        check("streams render in viewport", rendered > 0, f"{rendered} flowline features")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["streams_on"]))

        print("\n== Springs & gages ON ==")
        set_toggle(page, TOGGLE_IDS["springs"], True)
        page.wait_for_timeout(500)
        for layer in SPRING_LAYERS:
            vis = layer_visibility(page, layer)
            check(f"{layer} visible", vis == "visible", f"visibility={vis}")
        page.evaluate(
            "() => window.map.jumpTo({ center: [-85.74405784519145, 35.07065433778913], zoom: 15 })"
        )
        page.wait_for_timeout(300)
        rendered_pts = rendered_count(page, ["water-points"])
        check("water points render in viewport", rendered_pts > 0, f"{rendered_pts} points")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["springs_on"]))

        print("\n== Water over satellite imagery ==")
        set_toggle(page, TOGGLE_IDS["satellite"], True)
        page.wait_for_timeout(3500)
        check(
            "satellite visible under water layers",
            layer_visibility(page, "tnmap-satellite") == "visible",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["water_over_satellite"]))
        set_toggle(page, TOGGLE_IDS["satellite"], False)

        print("\n== Toggle everything OFF ==")
        set_toggle(page, TOGGLE_IDS["water"], False)
        set_toggle(page, TOGGLE_IDS["springs"], False)
        page.wait_for_timeout(400)
        for layer in WATER_LAYERS + SPRING_LAYERS:
            check(f"{layer} hidden again", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["all_off"]))

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
