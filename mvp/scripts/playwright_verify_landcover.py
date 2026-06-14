#!/usr/bin/env python3
"""Playwright verification for the AOP viewer land-cover layers.

Covers:
  - Land cover (NAIP) — the dissolved single-class vegetation coverage
    (forest greens merged, non-tree dropped to base map), clipped to the AOP
    park boundary. See simplify_landcover_vegetation.py.
  - Land cover, 9-patch — the wide-area vegetation context across the full
    3x3 acquisition AOI, with its own toggle and drawer opacity control,
    drawn below the park layer.
  - The Muted Earth restyle — the paper background and palette retune.

Confirms the toggles exist and start on, the 9-patch layer sits at the base of
the stack below the park layer, both GeoJSONs carry the single `vegetation`
class (the former forest/open sub-classes are gone), the drawer opacity
control drives the 9-patch fill, toggling hides/shows the layers, the paper
background colour is applied, and there are no console errors. Captures
screenshots into brain/output/.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import (
    viewer_url,
    click_in_section,
    layer_visibility,
    rendered_count,
    set_toggle,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_landcover_initial.png",
    "ninepatch_wide": "playwright_landcover_9patch_wide.png",
    "ninepatch_off": "playwright_landcover_9patch_off.png",
    "forest_off": "playwright_landcover_forest_off.png",
    "satellite": "playwright_landcover_over_satellite.png",
    "contours": "playwright_landcover_with_contours.png",
    "zoom": "playwright_landcover_zoom.png",
}

FOREST_LAYERS = ["landcover-forest", "landcover-forest-outline"]
NINE_PATCH_LAYERS = ["landcover-9patch-forest", "landcover-9patch-forest-outline"]

# The land cover ships a single dissolved class after
# simplify_landcover_vegetation.py: forest greens merged into `vegetation`, the
# three open/non-tree classes dropped to the base map.
LANDCOVER_CLASSES = ["vegetation"]
RETIRED_CLASSES = {
    "forest_deciduous", "forest_evergreen",
    "open_grass", "open_meadow", "open_bare",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def geojson_summary(page, url: str) -> dict | None:
    return page.evaluate(
        """async (url) => {
          const r = await fetch(url);
          if (!r.ok) return null;
          const d = await r.json();
          const feats = d.features || [];
          return {
            total: feats.length,
            classes: [...new Set(feats.map((f) => f.properties.class))].sort(),
            types: [...new Set(feats.map((f) => f.geometry.type))].sort()
          };
        }""",
        url,
    )


def landcover_data(page) -> dict | None:
    return geojson_summary(page, "./data/aop_landcover.geojson")


def landcover9_data(page) -> dict | None:
    return geojson_summary(page, "./data/aop_landcover_9patch.geojson")


def layer_opacity(page, layer_id: str) -> float | None:
    return page.evaluate(
        """(id) => {
          if (!window.map || !window.map.getLayer(id)) return null;
          return window.map.getPaintProperty(id, 'fill-opacity');
        }""",
        layer_id,
    )


def layer_below(page, lower: str, upper: str) -> bool:
    """True when `lower` is drawn beneath `upper` in the style layer order."""
    return page.evaluate(
        """([lower, upper]) => {
          const ids = (window.map.getStyle().layers || []).map((l) => l.id);
          const li = ids.indexOf(lower), ui = ids.indexOf(upper);
          return li !== -1 && ui !== -1 && li < ui;
        }""",
        [lower, upper],
    )


def first_layer_id(page) -> str | None:
    """The id of the lowest non-background layer in the style."""
    return page.evaluate(
        """() => {
          const layers = window.map.getStyle().layers || [];
          const drawn = layers.filter((l) => l.type !== 'background');
          return drawn.length ? drawn[0].id : null;
        }"""
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
        # Real map handle: the extracted read viewer (index.html) exposes
        # window.AOPViewer.map; the editor host (old_index.html) exposes a global
        # lexical `map`. Normalise both to window.map for the helpers below.
        page.evaluate(
            "window.map = (window.AOPViewer && window.AOPViewer.map)"
            " || (typeof map !== 'undefined' ? map : window.map);"
        )
        page.wait_for_function(
            "() => window.map && typeof window.map.getPaintProperty === 'function'",
            timeout=15_000,
        )
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(700)

        # The editor host carries layer checkboxes + the opacity drawer; the read
        # viewer drives the same layers via presets. Editor-only checks are guarded.
        editor = page.locator("#showLandcover").count() == 1

        print("\n== Initial state (Muted Earth, vegetation on) ==")
        if editor:
            check("land-cover toggle exists and starts on",
                  page.locator("#showLandcover").is_checked())
        for layer in FOREST_LAYERS:
            check(f"{layer} visible", layer_visibility(page, layer) == "visible")
        veg_fill = page.evaluate(
            "() => window.map.getPaintProperty('landcover-forest', 'fill-color')"
        )
        check("vegetation renders as one flat green fill",
              veg_fill == "#b8c1a1", f"fill-color={veg_fill}")

        bg = page.evaluate(
            "() => window.map.getPaintProperty('background', 'background-color')"
        )
        check("paper background colour applied", bg == "#efe7d5", f"background={bg}")

        bottom = first_layer_id(page)
        check("9-patch forest renders at the base of the layer stack",
              bottom == "landcover-9patch-forest", f"lowest drawn layer={bottom}")

        data = landcover_data(page)
        check("aop_landcover.geojson loaded", data is not None)
        if data:
            check("vegetation polygons present", data["total"] >= 1,
                  f"{data['total']} features")
            check("layer carries the single dissolved vegetation class",
                  data["classes"] == LANDCOVER_CLASSES, str(data["classes"]))
            check("retired forest/open sub-classes are gone",
                  not (RETIRED_CLASSES & set(data["classes"])),
                  str(data["classes"]))
            check("geometry is polygonal",
                  set(data["types"]) <= {"Polygon", "MultiPolygon"},
                  str(data["types"]))

        rendered = rendered_count(page, ["landcover-forest"])
        check("forest features render in viewport", rendered > 0,
              f"{rendered} rendered")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== 9-patch land cover ==")
        if editor:
            check("9-patch toggle exists and starts on",
                  page.locator("#showLandcover9").count() == 1
                  and page.locator("#showLandcover9").is_checked())
        for layer in NINE_PATCH_LAYERS:
            check(f"{layer} visible", layer_visibility(page, layer) == "visible")
        check("9-patch forest sits below the park forest layer",
              layer_below(page, "landcover-9patch-forest", "landcover-forest"))

        d9 = landcover9_data(page)
        check("aop_landcover_9patch.geojson loaded", d9 is not None)
        if d9:
            check("9-patch vegetation polygons present", d9["total"] >= 1,
                  f"{d9['total']} features")
            check("9-patch layer carries the single dissolved vegetation class",
                  d9["classes"] == LANDCOVER_CLASSES, str(d9["classes"]))
            check("9-patch retired forest/open sub-classes are gone",
                  not (RETIRED_CLASSES & set(d9["classes"])),
                  str(d9["classes"]))
            check("9-patch geometry is polygonal",
                  set(d9["types"]) <= {"Polygon", "MultiPolygon"},
                  str(d9["types"]))

        # wide view so the 9-patch context around the park is in frame
        page.evaluate(
            "() => window.map.fitBounds("
            "[[-85.782935, 35.067164], [-85.717154, 35.117928]], "
            "{ padding: 20, duration: 0 })"
        )
        page.wait_for_timeout(900)
        rendered9 = rendered_count(page, ["landcover-9patch-forest"])
        check("9-patch forest renders across the AOI", rendered9 > 0,
              f"{rendered9} rendered")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["ninepatch_wide"]))

        if editor:
            print("\n== 9-patch opacity drawer ==")
            check("opacity state slider exists", page.locator("#landcover9Opacity").count() == 1)
            check("opacity state slider is no longer visible inline",
                  page.locator("#landcover9Opacity").evaluate("el => el.hidden"))
            click_in_section(page, '[data-tune-expand-key="landcover9"]')
            page.wait_for_timeout(250)
            check("9-patch land cover drawer opens",
                  page.locator("#layerEditorTitle").inner_text() == "9-patch land cover")
            check("9-patch opacity control is in the drawer",
                  page.locator("#tuneOpacity").is_visible())
            op_before = layer_opacity(page, "landcover-9patch-forest")
            page.locator("#tuneOpacity").evaluate(
                """el => {
                  el.value = '100';
                  el.dispatchEvent(new Event('input', { bubbles: true }));
                }"""
            )
            page.wait_for_timeout(300)
            op_after = layer_opacity(page, "landcover-9patch-forest")
            check("drawer opacity drives 9-patch fill-opacity",
                  op_after is not None and abs(op_after - 1.0) < 0.01
                  and op_after != op_before,
                  f"{op_before} -> {op_after}")
            page.locator("#tuneOpacity").evaluate(
                """el => {
                  el.value = '55';
                  el.dispatchEvent(new Event('input', { bubbles: true }));
                }"""
            )
            page.wait_for_timeout(200)

            print("\n== 9-patch OFF ==")
            set_toggle(page, "showLandcover9", False)
            page.wait_for_timeout(400)
            for layer in NINE_PATCH_LAYERS:
                check(f"{layer} hidden", layer_visibility(page, layer) == "none")
            page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["ninepatch_off"]))
            set_toggle(page, "showLandcover9", True)
            page.wait_for_timeout(300)
            for layer in NINE_PATCH_LAYERS:
                check(f"{layer} visible again", layer_visibility(page, layer) == "visible")

            print("\n== Forest OFF ==")
            set_toggle(page, "showLandcover", False)
            page.wait_for_timeout(400)
            for layer in FOREST_LAYERS:
                check(f"{layer} hidden", layer_visibility(page, layer) == "none")
            page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["forest_off"]))

            print("\n== Forest back ON ==")
            set_toggle(page, "showLandcover", True)
            page.wait_for_timeout(400)
            for layer in FOREST_LAYERS:
                check(f"{layer} visible again", layer_visibility(page, layer) == "visible")

            print("\n== Forest under satellite imagery ==")
            set_toggle(page, "showSatellite", True)
            page.wait_for_timeout(1500)
            check("satellite layer visible over forest",
                  layer_visibility(page, "tnmap-satellite") == "visible")
            page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["satellite"]))
            set_toggle(page, "showSatellite", False)
            page.wait_for_timeout(400)

            print("\n== Forest with contours ==")
            set_toggle(page, "showContours", True)
            page.wait_for_timeout(800)
            check("contours visible over forest",
                  layer_visibility(page, "contours-index") == "visible")
            page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["contours"]))
            set_toggle(page, "showContours", False)

        print("\n== Zoomed in ==")
        page.evaluate("() => window.map.zoomTo(15.2, { duration: 0 })")
        page.wait_for_timeout(900)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["zoom"]))

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
