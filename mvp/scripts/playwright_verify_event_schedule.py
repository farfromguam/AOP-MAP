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
    "narrow_jump": "playwright_event_schedule_jump_narrow.png",
    "calendar_narrow_default": "playwright_event_schedule_calendar_narrow_default.png",
    "calendar_search_icon": "playwright_event_schedule_search_icon.png",
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
        # `page.reload` aborts in-flight tile / sprite / data: requests; the
        # browser then logs them as `TypeError: Failed to fetch` (network) or
        # `AJAXError: Failed to fetch (0): ...` (MapLibre's loader). They are
        # navigation artifacts, not real failures, and the verifier reloads
        # several times for narrow / wide / persist passes. Filter both.
        def _record_error(msg):
            if msg.type != "error":
                return
            text = (msg.text or "").strip()
            if "Failed to fetch" in text:
                return
            console_errors.append(text)

        page.on("console", _record_error)

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        # Sprint 02 B4 added localStorage-backed calendar collapse state.
        # Clear it once so the auto-collapse default is testable from a known
        # initial state across local re-runs.
        page.evaluate(
            "() => { try { localStorage.removeItem('aop_calendar_collapsed_v1'); } catch (_) {} }"
        )
        page.reload(wait_until="load")
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

        print("\n== Narrow viewport popup placement ==")
        # Sprint 02 Bucket B1: on cramped viewports the calendar-row popup
        # was clipped by chrome. After fix, gotoEventSession must leave the
        # popup fully inside the unoccluded map slice (visibleMapRect).
        # 1024x640 keeps the desktop layout (above the 760px breakpoint) but
        # squeezes vertical space so the calendar card eats real popup room.
        page.set_viewport_size({"width": 1024, "height": 640})
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=45_000,
            polling=500,
        )
        page.wait_for_timeout(700)
        page.locator('[data-session-id="sat-g6-cove-rally"]').click()
        # Fly is 1000 ms; the in-view panBy is 240 ms; plus a 1200 ms safety
        # pan from gotoEventSession. Give the whole settle 1700 ms.
        page.wait_for_timeout(1700)
        narrow_geom = page.evaluate(
            """() => {
              const popup = document.querySelector('.maplibregl-popup');
              const container = window.map.getContainer().getBoundingClientRect();
              if (!popup) return { ok: false };
              const r = popup.getBoundingClientRect();
              const width = container.right - container.left;
              const fullWidth = (b) => (b.right - b.left) >= width * 0.7;
              let top = container.top;
              let bottom = container.bottom;
              let left = container.left;
              let right = container.right;
              for (const sel of ['.left-controls', '.panel']) {
                const el = document.querySelector(sel);
                if (!el) continue;
                const b = el.getBoundingClientRect();
                if (fullWidth(b)) {
                  if (sel === '.left-controls') top = Math.max(top, b.bottom);
                  else bottom = Math.min(bottom, b.top);
                } else {
                  if (sel === '.left-controls') left = Math.max(left, b.right);
                  else right = Math.min(right, b.left);
                }
              }
              const msg = document.querySelector('.message');
              if (msg) bottom = Math.min(bottom, msg.getBoundingClientRect().top);
              return {
                ok: true,
                popup: { top: r.top, bottom: r.bottom, left: r.left, right: r.right },
                vis: { top, bottom, left, right },
                container: { top: container.top, bottom: container.bottom, left: container.left, right: container.right }
              };
            }"""
        )
        check("narrow viewport popup exists", narrow_geom.get("ok") is True, str(narrow_geom))
        if narrow_geom.get("ok"):
            popup_rect = narrow_geom["popup"]
            vis_rect = narrow_geom["vis"]
            tol = 2  # one CSS pixel + sub-pixel rounding
            check(
                "popup top is below left-controls strip",
                popup_rect["top"] >= vis_rect["top"] - tol,
                f"popup.top={popup_rect['top']:.1f} vis.top={vis_rect['top']:.1f}",
            )
            check(
                "popup bottom is above message bar",
                popup_rect["bottom"] <= vis_rect["bottom"] + tol,
                f"popup.bottom={popup_rect['bottom']:.1f} vis.bottom={vis_rect['bottom']:.1f}",
            )
            check(
                "popup left is right of left-controls",
                popup_rect["left"] >= vis_rect["left"] - tol,
                f"popup.left={popup_rect['left']:.1f} vis.left={vis_rect['left']:.1f}",
            )
            check(
                "popup right is left of layer panel",
                popup_rect["right"] <= vis_rect["right"] + tol,
                f"popup.right={popup_rect['right']:.1f} vis.right={vis_rect['right']:.1f}",
            )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["narrow_jump"]))

        print("\n== Search magnifier icon (B2) ==")
        # Icon is an inline SVG inside .search; pointer-events:none keeps the
        # input clickable. Assert it renders with non-zero geometry and sits
        # to the left of the input edge.
        icon_geom = page.evaluate(
            """() => {
              const icon = document.querySelector('.search .search-icon');
              const input = document.getElementById('searchInput');
              if (!icon || !input) return { ok: false };
              const i = icon.getBoundingClientRect();
              const n = input.getBoundingClientRect();
              return {
                ok: true,
                width: i.width,
                height: i.height,
                left_of_input_edge: i.left < n.left + 32 && i.right < n.right,
                inside_input_bounds: i.top >= n.top - 2 && i.bottom <= n.bottom + 2
              };
            }"""
        )
        check("search magnifier icon present", icon_geom.get("ok") is True, str(icon_geom))
        if icon_geom.get("ok"):
            check("icon has non-zero size", icon_geom["width"] > 0 and icon_geom["height"] > 0, str(icon_geom))
            check("icon sits at the left edge of the input", icon_geom["left_of_input_edge"], str(icon_geom))
            check("icon is vertically inside the input", icon_geom["inside_input_bounds"], str(icon_geom))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["calendar_search_icon"]), clip={"x": 0, "y": 0, "width": 360, "height": 60})

        print("\n== Calendar collapse: time labels (B4) ==")
        # User dump line "calendar needs time": confirm every row that has a
        # time_label in JSON also has visible text in .calendar-time. The
        # existing rendered-text check (~line 130) already proves a couple
        # of labels reach the row; here we explicitly assert per-row.
        time_count = page.evaluate(
            """() => {
              const rows = Array.from(document.querySelectorAll('#calendarDays .calendar-row .calendar-time'));
              return {
                total: rows.length,
                non_empty: rows.filter((el) => el.textContent.trim().length > 0).length
              };
            }"""
        )
        check(
            "every calendar row has a time label",
            time_count.get("total", 0) == 12 and time_count.get("non_empty", 0) == 12,
            str(time_count),
        )

        print("\n== Calendar collapse: narrow viewport default (B4) ==")
        # Stale localStorage from the previous narrow pass would mask the
        # auto-collapse default. Clear it before reloading at 420×740.
        page.evaluate(
            "() => { try { localStorage.removeItem('aop_calendar_collapsed_v1'); } catch (_) {} }"
        )
        page.set_viewport_size({"width": 420, "height": 740})
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_timeout(700)
        narrow_default = page.evaluate(
            """() => ({
              has_collapsed: document.getElementById('calendarCard').classList.contains('collapsed'),
              aria_expanded: document.getElementById('calendarToggle').getAttribute('aria-expanded'),
              stored: localStorage.getItem('aop_calendar_collapsed_v1')
            })"""
        )
        check("calendar starts collapsed on narrow viewport", narrow_default.get("has_collapsed") is True, str(narrow_default))
        check("calendar aria-expanded reflects collapsed", narrow_default.get("aria_expanded") == "false", str(narrow_default))
        check("auto-collapse does not persist by itself", narrow_default.get("stored") is None, str(narrow_default))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["calendar_narrow_default"]))

        print("\n== Calendar collapse: manual expand persists (B4) ==")
        page.locator("#calendarToggle").click()
        page.wait_for_timeout(200)
        after_expand = page.evaluate(
            """() => ({
              has_collapsed: document.getElementById('calendarCard').classList.contains('collapsed'),
              stored: localStorage.getItem('aop_calendar_collapsed_v1')
            })"""
        )
        check("manual expand opens the card", after_expand.get("has_collapsed") is False, str(after_expand))
        check("manual expand persists to localStorage", after_expand.get("stored") == "0", str(after_expand))
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_timeout(500)
        post_reload = page.evaluate(
            "() => document.getElementById('calendarCard').classList.contains('collapsed')"
        )
        check("user-expanded calendar survives reload on narrow", post_reload is False, str(post_reload))

        print("\n== Calendar collapse: wide viewport default (B4) ==")
        # Clear localStorage so the wide-viewport default is observable.
        page.evaluate(
            "() => { try { localStorage.removeItem('aop_calendar_collapsed_v1'); } catch (_) {} }"
        )
        page.set_viewport_size({"width": 1280, "height": 820})
        page.goto(WEBSITE_URL, wait_until="load")
        page.wait_for_timeout(500)
        wide_default = page.evaluate(
            """() => ({
              has_collapsed: document.getElementById('calendarCard').classList.contains('collapsed'),
              stored: localStorage.getItem('aop_calendar_collapsed_v1')
            })"""
        )
        check("calendar starts expanded on wide viewport", wide_default.get("has_collapsed") is False, str(wide_default))
        check("auto-expand does not persist by itself", wide_default.get("stored") is None, str(wide_default))

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
