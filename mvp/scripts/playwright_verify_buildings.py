#!/usr/bin/env python3
"""Playwright verification for the AOP viewer building-footprint layer.

Covers:
  - FEMA USA Structures building footprints imported into aop_buildings.geojson.
  - Default-off viewer toggle and layer visibility.
  - Search jump by address, which re-enables the building layer.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:8001/")
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_buildings_initial.png",
    "buildings_on": "playwright_buildings_on.png",
    "search": "playwright_buildings_search.png",
    "address_jump": "playwright_buildings_address_jump.png",
    "off": "playwright_buildings_off.png",
}

BUILDING_LAYERS = [
    "building-footprint-fill",
    "building-footprint-outline",
    "building-footprint-aop-outline",
]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def set_toggle(page, toggle_id: str, target: bool) -> None:
    # Drive .checked + change directly so a collapsed `.panel-section` cannot
    # hide the checkbox from a UI click — matches the Sprint 02 D fix in
    # playwright_verify_event_schedule.py.
    page.evaluate(
        """({ id, target }) => {
          const el = document.getElementById(id);
          if (!el) return;
          if (el.checked !== target) {
            el.checked = target;
            el.dispatchEvent(new Event('change', { bubbles: true }));
          }
        }""",
        {"id": toggle_id, "target": target},
    )
    page.wait_for_timeout(250)


def layer_visibility(page, layer_id: str) -> str | None:
    return page.evaluate(
        """(id) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getLayoutProperty(id, 'visibility') || 'visible';
        }""",
        layer_id,
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


def building_data(page) -> dict:
    return page.evaluate(
        """async () => {
          const r = await fetch('./data/aop_buildings.geojson');
          if (!r.ok) return null;
          const d = await r.json();
          const features = d.features || [];
          const classes = {};
          for (const f of features) {
            const cls = f.properties.occupancy_class || 'unknown';
            classes[cls] = (classes[cls] || 0) + 1;
          }
          const inside = features.filter((f) => f.properties.inside_aop_boundary);
          return {
            total: features.length,
            inside: inside.length,
            classes,
            selectedSource: (d._sources_checked || []).find((s) => s.selected)?.name || '',
            insideLabels: inside.map((f) => f.properties.building_label).sort()
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
        page.wait_for_timeout(500)

        print("\n== Initial state ==")
        check(
            "buildings toggle exists and starts ON (Bucket A2 default)",
            page.locator("#showBuildings").count() == 1
            and page.locator("#showBuildings").is_checked(),
        )
        for layer in BUILDING_LAYERS:
            check(
                f"{layer} starts visible (Bucket A2)",
                layer_visibility(page, layer) == "visible",
            )

        data = building_data(page)
        check("aop_buildings.geojson loaded", data is not None)
        if data:
            check("202 FEMA footprints imported", data["total"] == 202, str(data["total"]))
            check("4 footprints tagged inside the AOP boundary",
                  data["inside"] == 4, str(data["inside"]))
            check("selected source is FEMA USA Structures",
                  data["selectedSource"] == "FEMA USA Structures", data["selectedSource"])
            check("expected class mix",
                  data["classes"].get("Residential") == 166
                  and data["classes"].get("Agriculture") == 24,
                  str(data["classes"]))
            check("inside-AOP labels include Ellis Cove Road addresses",
                  all("Ellis Cove Road" in label for label in data["insideLabels"]),
                  str(data["insideLabels"]))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Buildings ON ==")
        set_toggle(page, "showBuildings", True)
        page.wait_for_timeout(600)
        for layer in BUILDING_LAYERS:
            vis = layer_visibility(page, layer)
            check(f"{layer} visible", vis == "visible", f"visibility={vis}")
        rendered = rendered_count(page, BUILDING_LAYERS)
        check("building footprints render in viewport", rendered > 0,
              f"{rendered} rendered")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["buildings_on"]))

        print("\n== Search by building address ==")
        set_toggle(page, "showBuildings", False)
        labels = search_labels(page, "1010 ellis")
        check("search finds the 1010 Ellis Cove Road footprint",
              any("1010 Ellis Cove Road" in s for s in labels), str(labels))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["search"]))
        page.locator("#searchInput").press("Enter")
        page.wait_for_timeout(1800)
        check("search jump re-enabled the buildings layer",
              page.locator("#showBuildings").is_checked())
        zoom = page.evaluate("() => window.map.getZoom()")
        check("search jump zoomed in on the building", zoom > 15, f"zoom={zoom:.2f}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["address_jump"]))

        print("\n== Toggle OFF ==")
        set_toggle(page, "showBuildings", False)
        for layer in BUILDING_LAYERS:
            check(f"{layer} hidden again", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["off"]))

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
