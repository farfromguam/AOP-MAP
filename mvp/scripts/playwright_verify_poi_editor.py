#!/usr/bin/env python3
"""Playwright verification for the AOP viewer map editor.

Covers the Terra Draw editing feature added to website/index.html:
  - Vendored Terra Draw + MapLibre adapter UMD bundles load.
  - editor-poi GeoJSON source with point, polygon, and LineString render layers.
  - "Place POI" enters point mode; clicking the map commits a POI.
  - "Draw footprint" enters polygon mode; a multi-click polygon commits a footprint.
  - "Trace line" enters linestring mode; a multi-click line commits a raw trace
    with source/review metadata.
  - Drawn features carry the selected category and persist to localStorage.
  - Points, footprints, and traces survive a page reload (offline-safe persistence).
  - The "Drawn POIs" toggle hides/shows every editor layer.
  - Clicking a POI or a footprint opens a rename/delete popup; delete removes it.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import WEBSITE_URL, click_in_section, layer_visibility


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"
POI_STORAGE_KEY = "aop_editor_pois_v1"

SCREENSHOTS = {
    "initial": "playwright_poi_initial.png",
    "placing": "playwright_poi_placing.png",
    "placed": "playwright_poi_placed.png",
    "footprint": "playwright_poi_footprint.png",
    "trace": "playwright_poi_trace.png",
    "reloaded": "playwright_poi_reloaded.png",
    "popup": "playwright_poi_popup.png",
    "hidden": "playwright_poi_hidden.png",
}

EDITOR_LAYERS = [
    "editor-poi-fill",
    "editor-poi-outline",
    "editor-poi-lines",
    "editor-poi-circles",
    "editor-poi-labels",
    "editor-poi-fill-labels",
    "editor-poi-line-labels",
]

# Click points on the map canvas, kept clear of the top-right control panel.
PLACE_POINTS = [(380, 360), (520, 320), (300, 470)]
# A four-corner footprint; the run closes it by clicking the first corner again.
FOOTPRINT_CORNERS = [(360, 520), (560, 520), (560, 640), (360, 640)]
TRACE_POINTS = [(300, 285), (390, 260), (500, 290), (620, 345)]


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


def feature_count(page) -> int:
    return page.evaluate("editorPois.length")


def kind_count(page, geom_type: str) -> int:
    return page.evaluate(
        "(t) => editorPois.filter((f) => f.geometry.type === t).length", geom_type
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
        check(
            "point + polygon + linestring modes registered",
            page.evaluate("typeof terraDraw.TerraDrawPointMode === 'function'"
                          " && typeof terraDraw.TerraDrawPolygonMode === 'function'"
                          " && typeof terraDraw.TerraDrawLineStringMode === 'function'"),
        )
        check("Terra Draw starts in static mode", page.evaluate("draw.getMode()") == "static")
        for layer in EDITOR_LAYERS:
            check(f"{layer} layer exists", page.evaluate(f"!!map.getLayer('{layer}')"))
        check("no features placed initially", feature_count(page) == 0)
        check("Place POI button present", page.locator("#placePoiBtn").count() == 1)
        check("Draw footprint button present", page.locator("#drawFootprintBtn").count() == 1)
        check("Trace line button present", page.locator("#traceLineBtn").count() == 1)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Place POIs (point mode) ==")
        click_in_section(page, "#placePoiBtn")
        page.wait_for_timeout(200)
        check("draw mode is 'point' after Place POI", page.evaluate("draw.getMode()") == "point")
        check(
            "Place POI button shows active state",
            "active" in (page.locator("#placePoiBtn").get_attribute("class") or ""),
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["placing"]))

        page.select_option("#poiCategory", "Pavilion")
        for x, y in PLACE_POINTS[:2]:
            page.mouse.click(x, y)
            page.wait_for_timeout(350)
        page.select_option("#poiCategory", "Building")
        page.mouse.click(*PLACE_POINTS[2])
        page.wait_for_timeout(350)
        check("three POIs placed", kind_count(page, "Point") == 3, f"points={kind_count(page, 'Point')}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["placed"]))

        print("\n== Draw a footprint (polygon mode) ==")
        page.locator("#drawFootprintBtn").click()
        page.wait_for_timeout(200)
        check("draw mode is 'polygon' after Draw footprint",
              page.evaluate("draw.getMode()") == "polygon")
        check(
            "Draw footprint button shows active state",
            "active" in (page.locator("#drawFootprintBtn").get_attribute("class") or ""),
        )
        check(
            "Place POI button no longer active",
            "active" not in (page.locator("#placePoiBtn").get_attribute("class") or ""),
        )
        page.select_option("#poiCategory", "Building")
        # Click each corner, then click the first corner again to close the ring.
        for x, y in FOOTPRINT_CORNERS:
            page.mouse.click(x, y)
            page.wait_for_timeout(250)
        page.mouse.click(*FOOTPRINT_CORNERS[0])
        page.wait_for_timeout(500)
        check("one footprint polygon committed",
              kind_count(page, "Polygon") == 1, f"polygons={kind_count(page, 'Polygon')}")
        check("total feature count is 4", feature_count(page) == 4, f"count={feature_count(page)}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["footprint"]))

        print("\n== Trace a line (linestring mode) ==")
        page.locator("#traceLineBtn").click()
        page.wait_for_timeout(200)
        check("draw mode is 'linestring' after Trace line",
              page.evaluate("draw.getMode()") == "linestring")
        check(
            "Trace line button shows active state",
            "active" in (page.locator("#traceLineBtn").get_attribute("class") or ""),
        )
        page.select_option("#poiCategory", "Trail trace")
        for x, y in TRACE_POINTS:
            page.mouse.click(x, y)
            page.wait_for_timeout(220)
        page.keyboard.press("Enter")
        page.wait_for_timeout(500)
        check("one trace line committed",
              kind_count(page, "LineString") == 1,
              f"lines={kind_count(page, 'LineString')}")
        check("total feature count is 5", feature_count(page) == 5, f"count={feature_count(page)}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["trace"]))

        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        check("Escape exits drawing mode", page.evaluate("draw.getMode()") == "static")

        print("\n== Categories + properties ==")
        point_cats = page.evaluate(
            "editorPois.filter((f) => f.geometry.type === 'Point').map((f) => f.properties.category)"
        )
        poly_cat = page.evaluate(
            "editorPois.find((f) => f.geometry.type === 'Polygon').properties.category"
        )
        trace_props = page.evaluate(
            "editorPois.find((f) => f.geometry.type === 'LineString').properties"
        )
        check(
            "point categories recorded (2 Pavilion, 1 Building)",
            point_cats.count("Pavilion") == 2 and point_cats.count("Building") == 1,
            str(point_cats),
        )
        check("footprint category recorded (Building)", poly_cat == "Building", str(poly_cat))
        check(
            "point/polygon features carry layer=editor_poi",
            page.evaluate("editorPois.filter((f) => f.geometry.type !== 'LineString')"
                          ".every((f) => f.properties.layer === 'editor_poi')"),
        )
        check("trace category recorded (Trail trace)", trace_props["category"] == "Trail trace")
        check("trace carries layer=editor_trace", trace_props["layer"] == "editor_trace")
        check(
            "trace carries USDA NAIP source metadata",
            trace_props["source_name"] == "USDA NAIP public image service"
            and trace_props["source_year"] == "2023"
            and trace_props["confidence"] == "draft",
            str(trace_props),
        )
        check(
            "trace is explicitly marked raw/review-needed",
            "needs review" in trace_props["review_status"],
            trace_props["review_status"],
        )
        check(
            "status text reports points, footprints, and traces",
            page.locator("#poiStatus").inner_text() == "3 POIs, 1 footprint, 1 trace.",
            page.locator("#poiStatus").inner_text(),
        )

        print("\n== localStorage persistence ==")
        stored_count = page.evaluate(
            f"JSON.parse(localStorage.getItem('{POI_STORAGE_KEY}') || '[]').length"
        )
        check("localStorage holds 5 features", stored_count == 5, f"count={stored_count}")

        print("\n== Survive a reload ==")
        page.reload(wait_until="load")
        wait_for_viewer(page)
        check("5 features restored after reload", feature_count(page) == 5, f"count={feature_count(page)}")
        check("3 points + 1 polygon + 1 trace restored",
              kind_count(page, "Point") == 3
              and kind_count(page, "Polygon") == 1
              and kind_count(page, "LineString") == 1)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["reloaded"]))

        print("\n== Popup: delete a POI, then a footprint ==")
        point_pixel = page.evaluate(
            "(() => { const f = editorPois.find((x) => x.geometry.type === 'Point');"
            " const p = map.project(f.geometry.coordinates); return [p.x, p.y]; })()"
        )
        page.mouse.click(point_pixel[0], point_pixel[1])
        page.wait_for_timeout(300)
        check("POI popup opened", page.locator(".poi-popup").count() == 1)
        check("popup has name input + Save + Delete",
              page.locator("#poiNameInput").count() == 1
              and page.locator("#poiSaveBtn").count() == 1
              and page.locator("#poiDeleteBtn").count() == 1)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["popup"]))
        page.locator("#poiDeleteBtn").click()
        page.wait_for_timeout(300)
        check("POI deleted via popup", kind_count(page, "Point") == 2, f"points={kind_count(page, 'Point')}")

        # Click the footprint at its centroid and delete it too.
        poly_pixel = page.evaluate(
            "(() => { const f = editorPois.find((x) => x.geometry.type === 'Polygon');"
            " const r = f.geometry.coordinates[0]; const n = r.length - 1;"
            " let x = 0, y = 0; for (let i = 0; i < n; i++) { x += r[i][0]; y += r[i][1]; }"
            " const p = map.project([x / n, y / n]); return [p.x, p.y]; })()"
        )
        page.mouse.click(poly_pixel[0], poly_pixel[1])
        page.wait_for_timeout(300)
        check("footprint popup opened", page.locator(".poi-popup").count() == 1)
        page.locator("#poiDeleteBtn").click()
        page.wait_for_timeout(300)
        check("footprint deleted via popup", kind_count(page, "Polygon") == 0)
        check("two POIs and one trace remain", feature_count(page) == 3, f"count={feature_count(page)}")

        print("\n== Drawn POIs toggle ==")
        check(
            "editor layers visible by default",
            all(layer_visibility(page, lyr) == "visible" for lyr in EDITOR_LAYERS),
        )
        page.locator("#showEditorPois").click()
        page.wait_for_timeout(250)
        check(
            "all editor layers hidden after toggle off",
            all(layer_visibility(page, lyr) == "none" for lyr in EDITOR_LAYERS),
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["hidden"]))
        page.locator("#showEditorPois").click()
        page.wait_for_timeout(250)
        check(
            "all editor layers visible after toggle on",
            all(layer_visibility(page, lyr) == "visible" for lyr in EDITOR_LAYERS),
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
