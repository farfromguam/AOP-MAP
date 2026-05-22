#!/usr/bin/env python3
"""Playwright verification for the editable event schedule sidebar.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
Set WEBSITE_URL to override the default.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:8001/")
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

EVENT_LAYERS = [
    "event-session-routes",
    "event-route-labels",
    "event-anchor-points",
    "event-anchor-labels",
]

SCREENSHOTS = {
    "initial": "playwright_event_schedule_initial.png",
    "jump": "playwright_event_schedule_jump.png",
    "off": "playwright_event_schedule_off.png",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
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


def set_toggle(page, toggle_id: str, target: bool) -> None:
    element = page.locator(f"#{toggle_id}")
    if element.is_checked() != target:
        element.click()
    page.wait_for_timeout(300)


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


def schedule_data(page) -> dict:
    return page.evaluate(
        """async () => {
          const response = await fetch('./data/aop_event_schedule.json');
          if (!response.ok) return { ok: false, status: response.status };
          const data = await response.json();
          const sessions = data.sessions || [];
          const locations = data.locations || {};
          return {
            ok: true,
            schema: data.schema,
            session_count: sessions.length,
            location_tags: Object.keys(locations).sort(),
            route_count: sessions.filter((s) => Array.isArray(s.route_tags)).length,
            sessions_have_coordinates: sessions.some((s) => Object.prototype.hasOwnProperty.call(s, 'coordinates')),
            pavilion_alias: locations['#pavillion'] && locations['#pavillion'].alias_of,
            g6: sessions.find((s) => s.id === 'sat-g6-cove-rally') || null
          };
        }"""
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader"])
        context = browser.new_context(viewport={"width": 1280, "height": 820})
        page = context.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=45_000,
            polling=500,
        )
        page.wait_for_timeout(700)

        print("\n== JSON source ==")
        data = schedule_data(page)
        check("schedule JSON loads", data.get("ok") is True, str(data))
        check("schema is event schedule v1", data.get("schema") == "aop-event-schedule-v1", str(data))
        check("twelve editable session rows", data.get("session_count") == 12, str(data))
        check("sessions reference tags, not coordinates", data.get("sessions_have_coordinates") is False, str(data))
        check("#pavilion tag is present", "#pavilion" in data.get("location_tags", []), str(data.get("location_tags")))
        check("#pavillion misspelling aliases to #pavilion", data.get("pavilion_alias") == "#pavilion", str(data))
        check("G6 row references location and route tags",
              data.get("g6", {}).get("location_tag") == "#observed-trailhead"
              and data.get("g6", {}).get("route_tags") == ["#observed-trailhead", "#north-technical"],
              str(data.get("g6")))

        print("\n== Sidebar initial state ==")
        rows = page.locator("#calendarDays .calendar-row")
        row_texts = rows.evaluate_all("els => els.map((el) => el.textContent.trim().replace(/\\s+/g, ' '))")
        check("calendar renders all JSON sessions", rows.count() == 12, str(row_texts))
        check("calendar rows show location tags", any("#pavilion" in text for text in row_texts), str(row_texts))
        check("G6 schedule row is present", any("G6 Cove Rally stages" in text for text in row_texts), str(row_texts))
        check(
            "event overlay toggle starts off",
            page.locator("#showEventSchedule").count() == 1
            and not page.locator("#showEventSchedule").is_checked(),
        )
        for layer in EVENT_LAYERS:
            check(f"{layer} hidden", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Schedule row jump ==")
        page.locator('[data-session-id="sat-g6-cove-rally"]').click()
        page.wait_for_timeout(1300)
        check("row click turns event overlay on", page.locator("#showEventSchedule").is_checked())
        for layer in EVENT_LAYERS:
            check(f"{layer} visible", layer_visibility(page, layer) == "visible")
        check(
            "clicked row is active",
            page.locator('[data-session-id="sat-g6-cove-rally"]').evaluate("el => el.classList.contains('active')"),
        )
        rendered_routes = rendered_count(page, ["event-session-routes"])
        check("event route renders after jump", rendered_routes > 0, f"{rendered_routes} rendered route features")
        popup_text = " | ".join(page.locator(".maplibregl-popup").all_inner_texts())
        check("popup shows session and tag", "G6 Cove Rally stages" in popup_text and "#observed-trailhead" in popup_text, popup_text)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["jump"]))

        print("\n== Toggle OFF ==")
        set_toggle(page, "showEventSchedule", False)
        for layer in EVENT_LAYERS:
            check(f"{layer} hidden again", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["off"]))

        print("\n== Console summary ==")
        check("no console errors", len(console_errors) == 0, f"{len(console_errors)} error(s): {console_errors[:3]}")

        browser.close()

    print("\nScreenshots:")
    for filename in SCREENSHOTS.values():
        print(f"  - {OUTPUT_DIR / filename}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
