#!/usr/bin/env python3
"""Playwright verification for the AOP viewer 3D-terrain toggle.

Loads the static viewer at http://localhost:8000/, toggles 3D terrain,
confirms the terrarium DEM source is registered, the sky layer becomes
visible, the map pitches, and AWS terrarium tile requests fire.

Run after `python3 -m http.server 8000` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = "http://localhost:8000/"
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "initial": "playwright_terrain_initial.png",
    "terrain_on": "playwright_terrain_on.png",
    "terrain_plus_satellite": "playwright_terrain_plus_satellite.png",
    "hillshade_only": "playwright_terrain_hillshade_only.png",
    "hillshade_plus_terrain": "playwright_terrain_hillshade_plus_terrain.png",
    "terrain_off": "playwright_terrain_off.png",
}

TOGGLE_IDS = {
    "terrain": "showTerrain",
    "hillshade": "showHillshade",
    "satellite": "showSatellite",
}

TERRARIUM_HOST = "elevation-tiles-prod"


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def set_toggle(page, toggle_id: str, target: bool) -> None:
    element = page.locator(f"#{toggle_id}")
    current = element.is_checked()
    if current != target:
        element.click()
    page.wait_for_timeout(150)


def layer_visibility(page, layer_id: str) -> str | None:
    return page.evaluate(
        """(id) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getLayoutProperty(id, 'visibility') || 'visible';
        }""",
        layer_id,
    )


def has_terrain(page) -> bool:
    return page.evaluate(
        """() => {
          if (!window.map || !window.map.getTerrain) return false;
          const t = window.map.getTerrain();
          return !!(t && t.source);
        }"""
    )


def has_sky(page) -> bool:
    return page.evaluate(
        """() => {
          if (!window.map || !window.map.getSky) return false;
          const s = window.map.getSky();
          return !!(s && Object.keys(s).length > 0);
        }"""
    )


def map_pitch(page) -> float:
    return page.evaluate("() => window.map ? window.map.getPitch() : -1")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []
    terrarium_requests: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error"
            else None,
        )
        page.on(
            "request",
            lambda req: terrarium_requests.append(req.url)
            if TERRARIUM_HOST in req.url
            else None,
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
            "terrain toggle exists and starts off",
            page.locator(f"#{TOGGLE_IDS['terrain']}").count() == 1
            and not page.locator(f"#{TOGGLE_IDS['terrain']}").is_checked(),
        )
        check(
            "aws-terrain-dem source registered",
            page.evaluate("() => !!window.map.getSource('aws-terrain-dem')"),
        )
        check(
            "lidar-hillshade layer added with visibility=none",
            layer_visibility(page, "lidar-hillshade") == "none",
        )
        check(
            "hillshade toggle starts off",
            page.locator(f"#{TOGGLE_IDS['hillshade']}").count() == 1
            and not page.locator(f"#{TOGGLE_IDS['hillshade']}").is_checked(),
        )
        check(
            "no sky atmosphere initially",
            not has_sky(page),
        )
        check(
            "no terrain bound initially",
            not has_terrain(page),
        )
        check(
            "no terrarium requests yet",
            len(terrarium_requests) == 0,
            f"requests={len(terrarium_requests)}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Toggle terrain ON ==")
        set_toggle(page, TOGGLE_IDS["terrain"], True)
        page.wait_for_timeout(3000)
        check("terrain bound to aws-terrain-dem", has_terrain(page))
        check("sky atmosphere applied", has_sky(page))
        pitch = map_pitch(page)
        check(
            "map pitched (>= 45 deg)",
            pitch >= 45,
            f"pitch={pitch:.1f}",
        )
        check(
            "terrarium tiles fetched",
            len(terrarium_requests) > 0,
            f"requests={len(terrarium_requests)}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["terrain_on"]))

        print("\n== Hillshade alone (2D + shaded relief) ==")
        # Drop terrain back to 2D, leave satellite off, turn hillshade on.
        set_toggle(page, TOGGLE_IDS["terrain"], False)
        page.wait_for_timeout(1000)
        set_toggle(page, TOGGLE_IDS["hillshade"], True)
        page.wait_for_timeout(2000)
        check(
            "lidar-hillshade visible",
            layer_visibility(page, "lidar-hillshade") == "visible",
        )
        check("terrain unbound while hillshade only", not has_terrain(page))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["hillshade_only"]))

        print("\n== Hillshade + terrain together ==")
        set_toggle(page, TOGGLE_IDS["terrain"], True)
        page.wait_for_timeout(2000)
        check("terrain bound", has_terrain(page))
        check(
            "lidar-hillshade still visible",
            layer_visibility(page, "lidar-hillshade") == "visible",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["hillshade_plus_terrain"]))
        # Reset hillshade off for the rest of the run.
        set_toggle(page, TOGGLE_IDS["hillshade"], False)
        page.wait_for_timeout(300)

        print("\n== Terrain + satellite together ==")
        set_toggle(page, TOGGLE_IDS["satellite"], True)
        page.wait_for_timeout(3000)
        check(
            "satellite visible",
            layer_visibility(page, "tnmap-satellite") == "visible",
        )
        check("terrain still bound", has_terrain(page))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["terrain_plus_satellite"]))

        print("\n== Toggle terrain OFF ==")
        set_toggle(page, TOGGLE_IDS["terrain"], False)
        page.wait_for_timeout(1000)
        check("terrain unbound", not has_terrain(page))
        check("sky atmosphere cleared", not has_sky(page))
        # Pitch eases back to 0 over 600ms; allow time + tolerance.
        page.wait_for_timeout(900)
        pitch = map_pitch(page)
        check(
            "map flattened (<= 5 deg)",
            pitch <= 5,
            f"pitch={pitch:.1f}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["terrain_off"]))

        print("\n== Console summary ==")
        check(
            "no console errors",
            len(console_errors) == 0,
            f"{len(console_errors)} error(s): {console_errors[:3]}",
        )

        browser.close()

    print("\nTerrarium tile requests:", len(terrarium_requests))
    print("Screenshots:")
    for name in SCREENSHOTS.values():
        print(f"  - {OUTPUT_DIR / name}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
