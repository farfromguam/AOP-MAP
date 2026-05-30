#!/usr/bin/env python3
"""Playwright verification for the field "where am I" GeolocateControl.

Fakes a GPS fix at the AOP park center (from publish.geojson) so the
maplibregl.GeolocateControl resolves a position without a real device,
then asserts the control button mounts, the blue user-location dot
renders, and the camera locks onto the faked coordinate.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
Set WEBSITE_URL to override the default.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

# Park center computed from website/data/publish.geojson.
PARK_LAT = 35.0888
PARK_LNG = -85.7434
SCREENSHOT = "playwright_geolocate_park.png"


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Grant geolocation up front and pin the fix to the park. The real
        # navigator.geolocation API then returns this to the control.
        context = browser.new_context(
            geolocation={"latitude": PARK_LAT, "longitude": PARK_LNG},
            permissions=["geolocation"],
        )
        page = context.new_page()
        page.goto(viewer_url(), wait_until="load")
        page.wait_for_timeout(1500)

        button = page.query_selector(".maplibregl-ctrl-geolocate")
        check("geolocate control mounted", button is not None)
        if button is None:
            browser.close()
            return 1

        button.click()
        page.wait_for_timeout(2500)

        dot = page.query_selector(".maplibregl-user-location-dot")
        check("user-location dot rendered at fake fix", dot is not None)

        center = page.evaluate(
            "() => { const c = map.getCenter(); return [c.lng, c.lat]; }"
        )
        off_lng = abs(center[0] - PARK_LNG)
        off_lat = abs(center[1] - PARK_LAT)
        # Loose tolerance: the park is ~2 km across, so "near the fix" is the
        # meaningful assertion, not pixel-exact camera easing.
        check(
            "camera locked near faked coordinate",
            off_lng < 0.02 and off_lat < 0.02,
            f"center={center} off={off_lng:.5f},{off_lat:.5f}",
        )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOT))
        print(f"  screenshot -> {OUTPUT_DIR / SCREENSHOT}")

        browser.close()

    return 1 if check.failed else 0  # type: ignore[attr-defined]


if __name__ == "__main__":
    sys.exit(main())
