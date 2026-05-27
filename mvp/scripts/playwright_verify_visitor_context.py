#!/usr/bin/env python3
"""Playwright verification for visitor context callouts in the AOP viewer.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
Set WEBSITE_URL to use a different preview URL.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, set_toggle, layer_visibility, rendered_count


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_visitor_context_initial.png",
    "off": "playwright_visitor_context_off.png",
    "search": "playwright_visitor_context_search.png",
    "monteagle": "playwright_visitor_context_monteagle.png",
}

CALLOUT_LAYERS = [
    "visitor-context-fill",
    "visitor-context-outline",
    "visitor-context-labels",
]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def callout_data(page) -> dict:
    return page.evaluate(
        """async () => {
          const r = await fetch('./data/aop_visitor_context_callouts.geojson');
          if (!r.ok) return null;
          const d = await r.json();
          return {
            total: (d.features || []).length,
            names: (d.features || []).map((f) => f.properties.name),
            labels: (d.features || []).map((f) => f.properties.label),
            foodUrls: (d.features || []).map((f) => f.properties.food_url),
            lodgingUrls: (d.features || []).map((f) => f.properties.lodging_url),
            sources: d._sources_checked || []
          };
        }"""
    )


def search_labels(page, query: str) -> list[str]:
    box = page.locator("#searchInput")
    box.click()
    box.fill("")
    box.fill(query)
    page.wait_for_timeout(350)
    items = page.locator("#searchResults .search-item")
    return [items.nth(i).inner_text().replace("\n", " ") for i in range(items.count())]


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        # --enable-unsafe-swiftshader: fall back to software WebGL when the
        # headless host has no usable GPU, otherwise MapLibre's shaders fail
        # to compile and the viewer never finishes loading.
        browser = p.chromium.launch(
            headless=True, args=["--enable-unsafe-swiftshader"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 820})
        page = context.new_page()
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        # polling=500: software WebGL keeps the main thread busy compiling
        # shaders, which starves the default requestAnimationFrame poll. Timer
        # polling and a generous timeout keep the wait reliable on a GPU-less
        # headless host.
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=45_000,
            polling=500,
        )
        page.wait_for_timeout(700)

        print("\n== Initial state ==")
        check(
            "visitor context toggle exists and starts on",
            page.locator("#showVisitorContext").count() == 1
            and page.locator("#showVisitorContext").is_checked(),
        )
        for layer in CALLOUT_LAYERS:
            vis = layer_visibility(page, layer)
            check(f"{layer} visible", vis == "visible", f"visibility={vis}")

        data = callout_data(page)
        check("callout GeoJSON loaded", data is not None)
        if data:
            check("two visitor context callouts exist", data["total"] == 2, str(data["names"]))
            check("South Pittsburg / Kimball callout present",
                  "South Pittsburg / Kimball supply run" in data["names"])
            check("Monteagle callout present", "Monteagle plateau services" in data["names"])
            check("source manifest carried in GeoJSON", len(data["sources"]) >= 4,
                  str([s.get("name") for s in data["sources"]]))
            check("labels include drive-time text",
                  any("10-15 min" in label for label in data["labels"])
                  and any("~30 min" in label for label in data["labels"]),
                  str(data["labels"]))
            check("SE callout label carries the Chattanooga regional anchor",
                  any("Chattanooga" in label and "mi" in label
                      for label in data["labels"]),
                  str(data["labels"]))
            check("food links deep-link to a per-town section, one per callout",
                  len(set(data["foodUrls"])) == len(data["foodUrls"])
                  and all("#:~:text=" in url for url in data["foodUrls"]),
                  str(data["foodUrls"]))
            check("lodging links deep-link to a per-town section, one per callout",
                  len(set(data["lodgingUrls"])) == len(data["lodgingUrls"])
                  and all("#:~:text=" in url for url in data["lodgingUrls"]),
                  str(data["lodgingUrls"]))
            se_idx = (data["names"].index("South Pittsburg / Kimball supply run")
                      if "South Pittsburg / Kimball supply run" in data["names"]
                      else None)
            if se_idx is not None:
                se_food = data["foodUrls"][se_idx]
                se_lodging = data["lodgingUrls"][se_idx]
                check("SE callout food/lodging links cover both South Pittsburg and Kimball",
                      all("South%20Pittsburg" in url and "Kimball" in url
                          for url in (se_food, se_lodging)),
                      str([se_food, se_lodging]))

        page.wait_for_function(
            """() => window.map && window.map.queryRenderedFeatures
              && window.map.queryRenderedFeatures({ layers: ['visitor-context-fill'] }).length > 0""",
            timeout=15_000,
            polling=500,
        )
        rendered = rendered_count(page, ["visitor-context-fill"])
        check("callout circles render in initial viewport", rendered > 0, f"{rendered} rendered")
        center = page.evaluate(
            """() => {
              const p = window.map.project([-85.7392, 35.0837]);
              return { x: p.x, y: p.y };
            }"""
        )
        page.mouse.click(center["x"], center["y"])
        page.wait_for_timeout(350)
        popup_links = page.evaluate(
            """() => [...document.querySelectorAll('.maplibregl-popup a')]
              .map((a) => ({ text: a.textContent.trim(), href: a.href }))"""
        )
        link_texts = [link["text"] for link in popup_links]
        check("popup exposes Directions, Food, Lodging, and Source links",
              {"Directions", "Food", "Lodging", "Source"}.issubset(set(link_texts)),
              str(popup_links))
        check("directions link points to Google Maps",
              any(link["text"] == "Directions" and "google.com/maps/dir" in link["href"]
                  for link in popup_links),
              str(popup_links))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Toggle OFF ==")
        set_toggle(page, "showVisitorContext", False)
        for layer in CALLOUT_LAYERS:
            check(f"{layer} hidden", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["off"]))

        print("\n== Search jump ==")
        labels = search_labels(page, "Monteagle")
        check("search finds the Monteagle context callout",
              any("Monteagle plateau services" in s for s in labels), str(labels))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["search"]))
        page.locator("#searchInput").press("Enter")
        page.wait_for_timeout(1600)
        check("search re-enabled visitor context",
              page.locator("#showVisitorContext").is_checked())
        check("Monteagle jump zooms to context circle",
              page.evaluate("() => window.map.getZoom()") > 14)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["monteagle"]))

        print("\n== Console summary ==")
        check("no console errors", len(console_errors) == 0,
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
