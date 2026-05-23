#!/usr/bin/env python3
"""Playwright verification for the AOP viewer cemetery layer.

Covers:
  - Cemeteries (TN Comptroller parcels) GeoJSON overlay — parcel polygons and
    centroid markers for the four cemetery-class parcels in the 9-patch.
  - Ellis Cemetery (parcel 110 008.04) flagged as the AOP inholding — the
    interior parcel carved out of the park boundary polygon.
  - Map search: the cemetery and its county owner-of-record name ("Bryson &
    Ellis Cemetery") both resolve and a search jump turns the layer on.

Confirms the toggle exists and starts off, the layers are added hidden,
toggling makes them visible, features render, the GeoJSON carries the expected
counts and the inholding flag + burial roster, and search lands on the
cemetery. Captures screenshots into brain/output/.

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
    "initial": "playwright_cemeteries_initial.png",
    "cemeteries_on": "playwright_cemeteries_on.png",
    "search_results": "playwright_cemeteries_search.png",
    "ellis_inholding": "playwright_cemeteries_ellis.png",
    "all_off": "playwright_cemeteries_all_off.png",
}

CEMETERY_LAYERS = ["cemetery-fill", "cemetery-outline", "cemetery-marker", "cemetery-label"]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def set_toggle(page, toggle_id: str, target: bool) -> None:
    element = page.locator(f"#{toggle_id}")
    if element.is_checked() != target:
        element.click()
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


def cemetery_data(page) -> dict:
    return page.evaluate(
        """async () => {
          const r = await fetch('./data/aop_cemeteries.geojson');
          if (!r.ok) return null;
          const d = await r.json();
          const parcels = (d.features || []).filter(
            (f) => f.properties.geom_role === 'parcel');
          const ellis = parcels.find((f) => f.properties.name === 'Ellis Cemetery');
          return {
            total: (d.features || []).length,
            parcels: parcels.length,
            names: parcels.map((f) => f.properties.name).sort(),
            ellis: ellis ? {
              parcel_id: ellis.properties.parcel_id,
              aop_inholding: ellis.properties.aop_inholding,
              burial_count: ellis.properties.burial_count,
              named_burial_count: ellis.properties.named_burial_count,
              aka: ellis.properties.aka
            } : null
          };
        }"""
    )


def search_labels(page, query: str) -> list[str]:
    """Type into the search box and return the dropdown result labels."""
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
            "cemeteries toggle exists and starts off",
            page.locator("#showCemeteries").count() == 1
            and not page.locator("#showCemeteries").is_checked(),
        )
        for layer in CEMETERY_LAYERS:
            check(
                f"{layer} added with visibility=none",
                layer_visibility(page, layer) == "none",
            )

        data = cemetery_data(page)
        check("aop_cemeteries.geojson loaded", data is not None)
        if data:
            check("8 features (4 parcels + 4 markers)",
                  data["total"] == 8 and data["parcels"] == 4,
                  f"total={data['total']} parcels={data['parcels']}")
            check("expected cemetery names",
                  data["names"] == ["Bible Cemetery", "Ellis Cemetery",
                                    "Gilliam Cemetery", "Tate Cemetery"],
                  str(data["names"]))
            ellis = data["ellis"] or {}
            check("Ellis Cemetery is parcel 110 008.04",
                  ellis.get("parcel_id") == "110 008.04", str(ellis.get("parcel_id")))
            check("Ellis Cemetery flagged as AOP inholding",
                  ellis.get("aop_inholding") is True, str(ellis.get("aop_inholding")))
            check("Ellis Cemetery carries 12 burials (9 named)",
                  ellis.get("burial_count") == 12 and ellis.get("named_burial_count") == 9,
                  f"burials={ellis.get('burial_count')} named={ellis.get('named_burial_count')}")
            check("Ellis Cemetery carries county aka name",
                  ellis.get("aka") == "Bryson & Ellis Cemetery", str(ellis.get("aka")))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Cemeteries ON ==")
        set_toggle(page, "showCemeteries", True)
        page.wait_for_timeout(600)
        for layer in CEMETERY_LAYERS:
            vis = layer_visibility(page, layer)
            check(f"{layer} visible", vis == "visible", f"visibility={vis}")
        rendered = rendered_count(page, ["cemetery-fill", "cemetery-marker"])
        check("cemetery features render in viewport", rendered > 0,
              f"{rendered} rendered")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["cemeteries_on"]))

        print("\n== Search: by cemetery name ==")
        labels = search_labels(page, "ellis cemetery")
        check("search box finds 'Ellis Cemetery'",
              any("Ellis Cemetery" in s for s in labels), str(labels))
        check("Ellis result tagged as a cemetery",
              any("cemetery" in s.lower() for s in labels), str(labels))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["search_results"]))

        print("\n== Search: by county owner-of-record name ==")
        aka_labels = search_labels(page, "bryson")
        check("search box finds 'Bryson & Ellis Cemetery'",
              any("Bryson" in s for s in aka_labels), str(aka_labels))

        print("\n== Search jump lands on Ellis Cemetery ==")
        # Turn the layer back off first, to prove the search jump re-enables it.
        set_toggle(page, "showCemeteries", False)
        search_labels(page, "ellis cemetery")
        page.locator("#searchInput").press("Enter")
        page.wait_for_timeout(1800)
        check("search jump re-enabled the cemeteries layer",
              page.locator("#showCemeteries").is_checked())
        zoom = page.evaluate("() => window.map.getZoom()")
        check("search jump zoomed in on the cemetery", zoom > 14, f"zoom={zoom:.2f}")
        center = page.evaluate("() => window.map.getCenter()")
        check("search jump centered near parcel 110 008.04",
              abs(center["lng"] + 85.7439) < 0.01 and abs(center["lat"] - 35.0895) < 0.01,
              f"center=({center['lng']:.4f}, {center['lat']:.4f})")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["ellis_inholding"]))

        print("\n== Toggle OFF ==")
        set_toggle(page, "showCemeteries", False)
        page.wait_for_timeout(400)
        for layer in CEMETERY_LAYERS:
            check(f"{layer} hidden again", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["all_off"]))

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
