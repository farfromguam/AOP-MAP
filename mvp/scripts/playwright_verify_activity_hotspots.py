#!/usr/bin/env python3
"""Playwright verification for the AOP activity hotspot layer.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
Set WEBSITE_URL to override the default.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, set_toggle, layer_visibility, rendered_count


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

HOTSPOT_LAYERS = [
    "activity-hotspots-heat",
    "activity-hotspots-fill",
    "activity-hotspots-outline",
    "activity-hotspots-labels",
]

SCREENSHOTS = {
    "initial": "playwright_activity_hotspots_initial.png",
    "on": "playwright_activity_hotspots_on.png",
    "popup": "playwright_activity_hotspots_popup.png",
    "off": "playwright_activity_hotspots_off.png",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def hotspot_summary(page) -> dict:
    return page.evaluate(
        """async () => {
          const response = await fetch('./data/aop_activity_hotspots.geojson');
          if (!response.ok) return { ok: false, status: response.status };
          const data = await response.json();
          const features = data.features || [];
          const cells = features.filter((f) => f.geometry && f.geometry.type === 'Polygon');
          const points = features.filter((f) => f.geometry && f.geometry.type === 'Point');
          const top = cells.slice().sort((a, b) =>
            (b.properties.dwell_seconds || 0) - (a.properties.dwell_seconds || 0))[0];
          return {
            ok: true,
            schema: data.metadata && data.metadata.schema,
            features: features.length,
            cells: cells.length,
            points: points.length,
            point_count: data.metadata && data.metadata.point_count,
            top_minutes: top && top.properties.dwell_minutes,
            top_class: top && top.properties.intensity_class,
            classes: [...new Set(cells.map((f) => f.properties.intensity_class))].sort(),
            top_center: points.slice().sort((a, b) =>
              (b.properties.dwell_seconds || 0) - (a.properties.dwell_seconds || 0))[0]?.geometry.coordinates
          };
        }"""
    )


def click_top_hotspot(page, coords: list[float]) -> None:
    point = page.evaluate(
        """(coords) => {
          const p = window.map.project(coords);
          return { x: p.x, y: p.y };
        }""",
        coords,
    )
    page.mouse.click(point["x"], point["y"])
    page.wait_for_timeout(300)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(700)

        print("\n== Initial state ==")
        check(
            "activity hotspot toggle exists and starts off",
            page.locator("#showActivityHotspots").count() == 1
            and not page.locator("#showActivityHotspots").is_checked(),
        )
        for layer in HOTSPOT_LAYERS:
            check(f"{layer} added hidden", layer_visibility(page, layer) == "none")
        summary = hotspot_summary(page)
        check("hotspot GeoJSON loads", summary.get("ok") is True, str(summary))
        check("schema is activity hotspots v1", summary.get("schema") == "aop-activity-hotspots-v1")
        check("polygon and point feature pairs present", summary.get("cells") == summary.get("points") and summary.get("cells", 0) > 0, str(summary))
        check("expected GPX point count preserved in metadata", summary.get("point_count") == 368, str(summary))
        check("top hotspot is peak intensity", summary.get("top_class") == "peak", str(summary))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Hotspots ON ==")
        set_toggle(page, "showActivityHotspots", True)
        page.wait_for_timeout(900)
        for layer in HOTSPOT_LAYERS:
            check(f"{layer} visible", layer_visibility(page, layer) == "visible")
        rendered = rendered_count(page, ["activity-hotspots-fill"])
        check("hotspot cells render in viewport", rendered > 0, f"{rendered} rendered cells")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["on"]))

        print("\n== Hotspot popup ==")
        if summary.get("top_center"):
            click_top_hotspot(page, summary["top_center"])
            page.locator(".maplibregl-popup").first.wait_for(timeout=2_000)
            popup_texts = page.locator(".maplibregl-popup").all_inner_texts()
            activity_popups = [text for text in popup_texts if "Activity hotspot" in text]
            detail = " || ".join(text.replace("\n", " | ") for text in popup_texts)
            check(
                "popup opens with dwell detail",
                any("Dwell" in text for text in activity_popups),
                detail,
            )
        else:
            check("top hotspot center available", False, str(summary))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["popup"]))

        print("\n== Hotspots OFF ==")
        set_toggle(page, "showActivityHotspots", False)
        for layer in HOTSPOT_LAYERS:
            check(f"{layer} hidden again", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["off"]))

        print("\n== Console summary ==")
        check("no console errors", len(console_errors) == 0, f"{len(console_errors)} error(s): {console_errors[:3]}")

        browser.close()

    print("\nScreenshots:")
    for filename in SCREENSHOTS.values():
        print(f"  - {OUTPUT_DIR / filename}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
