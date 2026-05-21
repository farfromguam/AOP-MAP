#!/usr/bin/env python3
"""Playwright verification for the AOP viewer map search.

Covers:
  - Search box indexes named features across loaded layers.
  - Typing filters a result dropdown.
  - Selecting a result flies the map to it, turns its layer on if hidden,
    and flashes the search-highlight layers.

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
    "results": "playwright_search_results.png",
    "sweden_creek": "playwright_search_sweden_creek.png",
    "ellis_rd": "playwright_search_ellis_rd.png",
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


def map_view(page) -> dict:
    return page.evaluate(
        """() => ({
          lng: window.map.getCenter().lng,
          lat: window.map.getCenter().lat,
          zoom: window.map.getZoom()
        })"""
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

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(600)

        print("\n== Initial state ==")
        check("search input exists", page.locator("#searchInput").count() == 1)
        search_box = page.locator("#searchInput").bounding_box()
        panel_box = page.locator(".panel").bounding_box()
        check(
            "search input is left of the layer panel",
            bool(search_box and panel_box and search_box["x"] < panel_box["x"]),
            f"search={search_box}, panel={panel_box}",
        )
        registry = page.evaluate("() => (typeof searchIndex !== 'undefined') ? searchIndex.length : -1")
        check(
            "search index populated with named features",
            registry > 10,
            f"searchIndex entries={registry}",
        )
        check(
            "search-highlight-line layer added hidden",
            layer_visibility(page, "search-highlight-line") == "none",
        )
        check(
            "water layer starts off (so search must enable it)",
            not page.locator("#showWater").is_checked(),
        )

        print("\n== Type 'sweden' ==")
        page.locator("#searchInput").click()
        page.locator("#searchInput").fill("sweden")
        page.wait_for_timeout(300)
        items = page.locator(".search-item")
        n_items = items.count()
        check("result dropdown shows matches", n_items > 0, f"{n_items} items")
        texts = [items.nth(i).inner_text() for i in range(n_items)]
        check(
            "Sweden Creek is a result",
            any("Sweden Creek" in t for t in texts),
            f"results={texts}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["results"]))

        print("\n== Select Sweden Creek ==")
        before = map_view(page)
        page.locator(".search-item", has_text="Sweden Creek").first.click()
        page.wait_for_timeout(450)
        check("water layer auto-enabled by search", page.locator("#showWater").is_checked())
        check(
            "search-highlight visible during flash",
            layer_visibility(page, "search-highlight-line") == "visible",
        )
        page.wait_for_timeout(1400)
        after = map_view(page)
        moved = abs(after["lng"] - before["lng"]) + abs(after["lat"] - before["lat"])
        zoomed = abs(after["zoom"] - before["zoom"])
        check(
            "map re-focused on the result",
            moved > 0.001 or zoomed > 0.3,
            f"center delta={moved:.5f}, zoom delta={zoomed:.2f}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["sweden_creek"]))
        page.wait_for_timeout(1600)
        check(
            "search-highlight hides after the flash",
            layer_visibility(page, "search-highlight-line") == "none",
        )

        print("\n== Search a trail: 'saturday' ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("saturday")
        page.wait_for_timeout(300)
        trail_items = page.locator(".search-item")
        trail_texts = [trail_items.nth(i).inner_text() for i in range(trail_items.count())]
        check(
            "multi-segment trail collapses to one result",
            trail_items.count() == 1,
            f"results={trail_texts}",
        )
        check(
            "trail result tagged kind=trail",
            trail_items.count() == 1 and "trail" in trail_texts[0],
            f"results={trail_texts}",
        )
        before_t = map_view(page)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)
        after_t = map_view(page)
        moved_t = abs(after_t["lng"] - before_t["lng"]) + abs(after_t["lat"] - before_t["lat"])
        check(
            "trails are searchable and re-focus the map",
            page.locator("#showTrails").is_checked()
            and (moved_t > 0.0005 or abs(after_t["zoom"] - before_t["zoom"]) > 0.3),
            f"center delta={moved_t:.5f}",
        )

        print("\n== Search a road: 'ellis' ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("ellis")
        page.wait_for_timeout(300)
        road_items = page.locator(".search-item")
        check("road results found", road_items.count() > 0, f"{road_items.count()} items")
        before_r = map_view(page)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)
        after_r = map_view(page)
        moved_r = abs(after_r["lng"] - before_r["lng"]) + abs(after_r["lat"] - before_r["lat"])
        check("Enter selects first result and moves the map", moved_r > 0.0005, f"delta={moved_r:.5f}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["ellis_rd"]))

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
