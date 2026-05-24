#!/usr/bin/env python3
"""Playwright verification for the on-map brand logos in the AOP viewer.

Covers Sprint 02 Bucket F: the AOP badge + Rock Warblers logo render as
MapLibre icons sourced from `website/data/aop_brand_logos.geojson`, sit in
the Publishable section under `showBrandLogos`, and consume the shared
drag-to-move primitive from `poi_editor_v2.md` (commit + persist across
reload via `aop_brand_logos_overrides_v1`).

Run after `python3 -m http.server 8001` is serving the `website/` dir.
Set WEBSITE_URL to override.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import (
    WEBSITE_URL,
    set_toggle,
    layer_visibility,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_brand_logos_initial.png",
    "off": "playwright_brand_logos_off.png",
    "panel": "playwright_brand_logos_panel.png",
    "moved": "playwright_brand_logos_moved.png",
}

LOGO_LAYER = "brand-logos-icons"
OVERRIDE_KEY = "aop_brand_logos_overrides_v1"


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def open_layer_editor(page, tune_key: str) -> None:
    page.evaluate(
        """(key) => {
          if (typeof toggleTunableExpansion === 'function') {
            toggleTunableExpansion(key);
          }
        }""",
        tune_key,
    )
    page.wait_for_timeout(250)


def feature_rows(page) -> list[dict]:
    return page.evaluate(
        """() => {
          const root = document.getElementById('featureList');
          if (!root || root.hidden) return [];
          return [...root.querySelectorAll('.feature-row')].map((r) => ({
            id: r.dataset.featureId,
            name: r.querySelector('.feature-name')?.textContent || '',
            hasMove: !!r.querySelector('.feature-move'),
            checked: !!r.querySelector('input[type=checkbox]')?.checked
          }));
        }"""
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, args=["--enable-unsafe-swiftshader"]
        )
        context = browser.new_context(viewport={"width": 1280, "height": 820})
        page = context.new_page()
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        # Clean override store so this run is deterministic.
        page.evaluate(f"() => localStorage.removeItem('{OVERRIDE_KEY}')")
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=45_000,
            polling=500,
        )
        page.wait_for_timeout(700)

        print("\n== Initial state ==")
        check(
            "showBrandLogos toggle present and on by default",
            page.locator("#showBrandLogos").count() == 1
            and page.locator("#showBrandLogos").is_checked(),
        )
        vis = layer_visibility(page, LOGO_LAYER)
        check(f"{LOGO_LAYER} visible at load", vis == "visible", f"visibility={vis}")

        data = page.evaluate(
            """async () => {
              const r = await fetch('./data/aop_brand_logos.geojson');
              if (!r.ok) return null;
              const d = await r.json();
              return {
                total: (d.features || []).length,
                ids: (d.features || []).map((f) => f.properties.logo_id),
                names: (d.features || []).map((f) => f.properties.name),
                icons: (d.features || []).map((f) => f.properties.icon_image)
              };
            }"""
        )
        check("brand logos GeoJSON loaded", data is not None)
        if data:
            check("two logos seeded", data["total"] == 2, str(data["ids"]))
            check("aop_badge present", "aop_badge" in data["ids"], str(data["ids"]))
            check("rock_warblers present", "rock_warblers" in data["ids"], str(data["ids"]))
            check(
                "icon_image names match map.addImage registration",
                set(data["icons"]) == {"brand-aop-badge", "brand-rock-warblers"},
                str(data["icons"]),
            )

        # The map should report the two icon images registered.
        images_known = page.evaluate(
            "() => ({aop: map.hasImage('brand-aop-badge'), rw: map.hasImage('brand-rock-warblers')})"
        )
        check("AOP badge icon registered via map.addImage", images_known.get("aop") is True)
        check("Rock Warblers icon registered via map.addImage", images_known.get("rw") is True)

        rendered_count = page.evaluate(
            "() => map.queryRenderedFeatures({ layers: ['brand-logos-icons'] }).length"
        )
        check("both logo icons render", rendered_count == 2, f"{rendered_count} rendered")

        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Toggle OFF ==")
        set_toggle(page, "showBrandLogos", False)
        check(
            f"{LOGO_LAYER} hidden when toggle is off",
            layer_visibility(page, LOGO_LAYER) == "none",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["off"]))
        set_toggle(page, "showBrandLogos", True)
        page.wait_for_timeout(200)

        print("\n== Feature list panel ==")
        open_layer_editor(page, "brandLogos")
        rows = feature_rows(page)
        check("feature list opens with 2 rows", len(rows) == 2, str(rows))
        ids = {r["id"] for r in rows}
        check(
            "rows expose both logo_ids",
            ids == {"aop_badge", "rock_warblers"},
            str(ids),
        )
        check("each row carries a ✋ move button", all(r["hasMove"] for r in rows), str(rows))
        check("each row defaults checked", all(r["checked"] for r in rows), str(rows))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["panel"]))

        print("\n== Drag-to-move commits and persists ==")
        target = "aop_badge"
        before = page.evaluate(
            "(id) => brandLogosData.features.find((f) => f.properties.logo_id === id).geometry.coordinates",
            target,
        )

        # Click ✋ on the AOP row to enter move mode.
        page.evaluate(
            """(id) => {
              const row = document.querySelector(`.feature-row[data-feature-id="${id}"]`);
              if (!row) throw new Error('row not found');
              row.querySelector('.feature-move').click();
            }""",
            target,
        )
        page.wait_for_timeout(150)

        canvas_box = page.locator(".maplibregl-canvas").bounding_box()
        commit_px = (640, 420)
        expected_ll = page.evaluate(
            "(p) => { const ll = map.unproject(p); return [ll.lng, ll.lat]; }",
            list(commit_px),
        )
        page.mouse.click(
            canvas_box["x"] + commit_px[0], canvas_box["y"] + commit_px[1]
        )
        page.wait_for_timeout(400)

        after = page.evaluate(
            "(id) => brandLogosData.features.find((f) => f.properties.logo_id === id).geometry.coordinates",
            target,
        )
        check(
            "AOP badge coordinates changed after commit",
            abs(after[0] - before[0]) > 1e-5 or abs(after[1] - before[1]) > 1e-5,
            f"before={before} after={after}",
        )
        check(
            "AOP badge lands at clicked map point",
            abs(after[0] - expected_ll[0]) < 1e-3
            and abs(after[1] - expected_ll[1]) < 1e-3,
            f"expected≈{expected_ll} got={after}",
        )

        override = page.evaluate(
            f"() => JSON.parse(localStorage.getItem('{OVERRIDE_KEY}') || '{{}}')"
        )
        check(
            "override store carries the moved logo",
            target in override and "geometry" in override[target],
            str(list(override.keys())),
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["moved"]))

        print("\n== Reload preserves the moved position ==")
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
            polling=500,
        )
        page.wait_for_timeout(500)
        post = page.evaluate(
            "(id) => brandLogosData.features.find((f) => f.properties.logo_id === id).geometry.coordinates",
            target,
        )
        check(
            "moved AOP badge survives reload",
            abs(post[0] - after[0]) < 1e-9 and abs(post[1] - after[1]) < 1e-9,
            f"after_commit={after} after_reload={post}",
        )

        print("\n== Console summary ==")
        # Filter benign "Failed to fetch" caused by camera-resize navigations
        # (same filter used by event_schedule + presets verifiers).
        meaningful = [e for e in console_errors if "Failed to fetch" not in e]
        check(
            "no console errors",
            len(meaningful) == 0,
            f"{len(meaningful)} error(s): {meaningful[:3]}",
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
