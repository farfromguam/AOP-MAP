#!/usr/bin/env python3
"""Playwright verification for the AOP viewer building-footprint layer.

Covers:
  - FEMA USA Structures building footprints imported into aop_buildings.geojson.
  - Default-off viewer toggle and layer visibility.
  - Search jump by address, which re-enables the building layer.

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
          const facilities = features.filter((f) => f.properties.aop_facility === true);
          const boxes = features.filter((f) => f.properties.aop_structure_box === true);
          return {
            total: features.length,
            inside: inside.length,
            classes,
            selectedSource: (d._sources_checked || []).find((s) => s.selected)?.name || '',
            insideLabels: inside.map((f) => f.properties.building_label).sort(),
            facilityNames: facilities.map((f) => f.properties.facility_name).sort(),
            facilityAddrs: facilities.map((f) => f.properties.address).sort(),
            boxAddrs: boxes.map((f) => f.properties.address).sort()
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
            # Curated/derived set only: the ~197 raw 9-patch context footprints
            # are dropped on purpose (owner decision 2026-06-03). The served
            # layer is the 5 owner-chosen AOP buildings (3 facilities + 2 private
            # boxes), all Residential. See import_fema_buildings.py CURATED_ADDRESSES.
            check("5 curated AOP buildings served (raw context dropped)",
                  data["total"] == 5, str(data["total"]))
            check("4 footprints tagged inside the AOP boundary",
                  data["inside"] == 4, str(data["inside"]))
            check("selected source is FEMA USA Structures",
                  data["selectedSource"] == "FEMA USA Structures", data["selectedSource"])
            check("curated set is all Residential",
                  data["classes"].get("Residential") == 5
                  and len(data["classes"]) == 1,
                  str(data["classes"]))
            check("inside-AOP labels include Ellis Cove Road addresses",
                  all("Ellis Cove Road" in label for label in data["insideLabels"]),
                  str(data["insideLabels"]))
            check("3 public facilities tagged (Pavilion / Farmhouse / Front Office)",
                  data["facilityNames"] == ["Farmhouse", "Front Office", "Pavilion"],
                  str(data["facilityNames"]))
            check("facility addresses are 880 / 1010 / 1033 Ellis Cove",
                  data["facilityAddrs"] == ["1010 Ellis Cove Road", "1033 Ellis Cove Road",
                                            "880 Ellis Cove Road"],
                  str(data["facilityAddrs"]))
            check("2 private structure boxes tagged (665 / 889)",
                  data["boxAddrs"] == ["665 Ellis Cove Road", "889 Ellis Cove Road"],
                  str(data["boxAddrs"]))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Private structure black-box layer ==")
        check("building-structure-box layer is present and visible",
              layer_visibility(page, "building-structure-box") == "visible",
              layer_visibility(page, "building-structure-box"))
        box_rendered = rendered_count(page, ["building-structure-box"])
        check("private boxes render (presence markers)", box_rendered > 0,
              f"{box_rendered} rendered")

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

        print("\n== Search: public facilities only ==")
        set_toggle(page, "showBuildings", False)
        check("search by name finds the Pavilion",
              any("Pavilion" in s for s in search_labels(page, "pavilion")),
              str(search_labels(page, "pavilion")))
        check("search by name finds the Farmhouse",
              any("Farmhouse" in s for s in search_labels(page, "farmhouse")),
              str(search_labels(page, "farmhouse")))
        check("search by name finds the Front Office",
              any("Front Office" in s for s in search_labels(page, "front office")),
              str(search_labels(page, "front office")))
        check("facility is searchable by street address (alias)",
              any("Pavilion" in s for s in search_labels(page, "1010 ellis")),
              str(search_labels(page, "1010 ellis")))

        print("\n== Search: private boxes + region excluded ==")
        check("private box 665 Ellis is NOT searchable",
              not any("665" in s for s in search_labels(page, "665 ellis")),
              str(search_labels(page, "665 ellis")))
        check("private box 889 Ellis is NOT searchable",
              not any("889" in s for s in search_labels(page, "889 ellis")),
              str(search_labels(page, "889 ellis")))
        check("region building 383 Ellis is NOT searchable",
              not any("383" in s for s in search_labels(page, "383 ellis")),
              str(search_labels(page, "383 ellis")))

        print("\n== Search jump (Pavilion) ==")
        search_labels(page, "pavilion")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["search"]))
        page.locator("#searchInput").press("Enter")
        page.wait_for_timeout(1800)
        check("search jump re-enabled the buildings layer",
              page.locator("#showBuildings").is_checked())
        zoom = page.evaluate("() => window.map.getZoom()")
        check("search jump zoomed in on the facility", zoom > 15, f"zoom={zoom:.2f}")
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
