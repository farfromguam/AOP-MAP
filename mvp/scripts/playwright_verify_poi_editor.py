#!/usr/bin/env python3
"""Playwright verification for the AOP viewer map editor (drawn POIs).

Covers the Terra Draw POI placement feature added to website/index.html:
  - Vendored Terra Draw + MapLibre adapter UMD bundles load.
  - editor-poi GeoJSON source and circle/label layers are created.
  - "Place POI" enters Terra Draw point mode; clicking the map commits a POI.
  - Placed POIs carry the selected category and persist to localStorage.
  - POIs survive a page reload (offline-safe persistence).
  - The "Drawn POIs" toggle hides/shows the editor layers.
  - Clicking a POI opens a rename/delete popup; delete removes the POI.

Run after `python3 -m http.server 8000` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = "http://localhost:8000/"
OUTPUT_DIR = REPO_ROOT / "brain" / "output"
POI_STORAGE_KEY = "aop_editor_pois_v1"

SCREENSHOTS = {
    "initial": "playwright_poi_initial.png",
    "placing": "playwright_poi_placing.png",
    "placed": "playwright_poi_placed.png",
    "reloaded": "playwright_poi_reloaded.png",
    "popup": "playwright_poi_popup.png",
    "hidden": "playwright_poi_hidden.png",
}

# Click points on the map canvas, kept clear of the top-right control panel.
PLACE_POINTS = [(380, 360), (520, 300), (300, 480)]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def wait_for_viewer(page) -> None:
    page.wait_for_function(
        "() => document.getElementById('message').textContent.includes('publish feature')",
        timeout=15_000,
    )
    page.wait_for_timeout(600)
    page.evaluate("window.map = map; window.draw = draw;")


def layer_visibility(page, layer_id: str) -> str | None:
    return page.evaluate(
        """(id) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getLayoutProperty(id, 'visibility') || 'visible';
        }""",
        layer_id,
    )


def poi_count(page) -> int:
    return page.evaluate("editorPois.length")


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
        # Start from a clean slate so counts are deterministic.
        page.evaluate(f"localStorage.removeItem('{POI_STORAGE_KEY}')")
        page.reload(wait_until="load")
        wait_for_viewer(page)

        print("\n== Initial state ==")
        check("title is AOP Map Viewer", page.title() == "AOP Map Viewer", page.title())
        check(
            "terra-draw UMD bundle loaded",
            page.evaluate("typeof window.terraDraw === 'object' && !!terraDraw.TerraDraw"),
        )
        check(
            "terra-draw maplibre adapter UMD bundle loaded",
            page.evaluate(
                "typeof window.terraDrawMaplibreGlAdapter === 'object'"
                " && !!terraDrawMaplibreGlAdapter.TerraDrawMapLibreGLAdapter"
            ),
        )
        check("Terra Draw instance created", page.evaluate("!!window.draw"))
        check(
            "Terra Draw starts in static mode",
            page.evaluate("draw.getMode()") == "static",
        )
        check(
            "editor-poi-circles layer exists",
            page.evaluate("!!map.getLayer('editor-poi-circles')"),
        )
        check(
            "editor-poi-labels layer exists",
            page.evaluate("!!map.getLayer('editor-poi-labels')"),
        )
        check("no POIs placed initially", poi_count(page) == 0, f"count={poi_count(page)}")
        check(
            "Place POI button present",
            page.locator("#placePoiBtn").count() == 1,
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Enter placing mode ==")
        page.locator("#placePoiBtn").click()
        page.wait_for_timeout(200)
        check("draw mode is 'point' after Place POI", page.evaluate("draw.getMode()") == "point")
        check(
            "Place POI button shows active state",
            "active" in (page.locator("#placePoiBtn").get_attribute("class") or ""),
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["placing"]))

        print("\n== Place POIs ==")
        # First two as Pavilion, third as Building, to prove the category sticks.
        page.select_option("#poiCategory", "Pavilion")
        for x, y in PLACE_POINTS[:2]:
            page.mouse.click(x, y)
            page.wait_for_timeout(350)
        page.select_option("#poiCategory", "Building")
        page.mouse.click(*PLACE_POINTS[2])
        page.wait_for_timeout(350)

        check("three POIs placed", poi_count(page) == 3, f"count={poi_count(page)}")
        categories = page.evaluate("editorPois.map((f) => f.properties.category)")
        check(
            "categories recorded (2 Pavilion, 1 Building)",
            categories.count("Pavilion") == 2 and categories.count("Building") == 1,
            str(categories),
        )
        check(
            "poiStatus text updated",
            "3 POIs placed" in (page.locator("#poiStatus").inner_text()),
            page.locator("#poiStatus").inner_text(),
        )
        check(
            "all POIs carry layer=editor_poi",
            page.evaluate("editorPois.every((f) => f.properties.layer === 'editor_poi')"),
        )
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        check("Escape exits placing mode", page.evaluate("draw.getMode()") == "static")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["placed"]))

        print("\n== localStorage persistence ==")
        stored = page.evaluate(f"localStorage.getItem('{POI_STORAGE_KEY}')")
        check("POIs written to localStorage", bool(stored) and stored != "[]")
        stored_count = page.evaluate(
            f"JSON.parse(localStorage.getItem('{POI_STORAGE_KEY}') || '[]').length"
        )
        check("localStorage holds 3 POIs", stored_count == 3, f"count={stored_count}")

        print("\n== Survive a reload ==")
        page.reload(wait_until="load")
        wait_for_viewer(page)
        check("3 POIs restored after reload", poi_count(page) == 3, f"count={poi_count(page)}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["reloaded"]))

        print("\n== POI popup: rename + delete ==")
        # Project the first POI to a screen pixel and click it.
        pixel = page.evaluate(
            "(() => { const c = editorPois[0].geometry.coordinates;"
            " const p = map.project(c); return [p.x, p.y]; })()"
        )
        page.mouse.click(pixel[0], pixel[1])
        page.wait_for_timeout(300)
        check("POI popup opened", page.locator(".poi-popup").count() == 1)
        check("popup has name input", page.locator("#poiNameInput").count() == 1)
        check("popup has Save + Delete buttons",
              page.locator("#poiSaveBtn").count() == 1
              and page.locator("#poiDeleteBtn").count() == 1)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["popup"]))
        page.locator("#poiDeleteBtn").click()
        page.wait_for_timeout(300)
        check("POI deleted via popup", poi_count(page) == 2, f"count={poi_count(page)}")
        check(
            "delete persisted to localStorage",
            page.evaluate(
                f"JSON.parse(localStorage.getItem('{POI_STORAGE_KEY}') || '[]').length"
            )
            == 2,
        )

        print("\n== Drawn POIs toggle ==")
        check(
            "editor layers visible by default",
            layer_visibility(page, "editor-poi-circles") == "visible"
            and layer_visibility(page, "editor-poi-labels") == "visible",
        )
        page.locator("#showEditorPois").click()
        page.wait_for_timeout(250)
        check(
            "editor layers hidden after toggle off",
            layer_visibility(page, "editor-poi-circles") == "none"
            and layer_visibility(page, "editor-poi-labels") == "none",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["hidden"]))
        page.locator("#showEditorPois").click()
        page.wait_for_timeout(250)
        check(
            "editor layers visible after toggle on",
            layer_visibility(page, "editor-poi-circles") == "visible",
        )

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
