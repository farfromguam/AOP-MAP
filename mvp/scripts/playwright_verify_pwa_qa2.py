#!/usr/bin/env python3
"""Playwright verification for the pwa_qa_2 viewer items.

Covers the headless-verifiable slices of brain/tasks/04_event_app/pwa_qa_2.md:

  item 1 — calendar open-event popup pins to a fixed `bottom` anchor (no
           mid-flight auto-anchor flip / jerk).
  item 2 — on a narrow viewport, picking a calendar event collapses the whole
           left drawer (search + hot + the calendar card itself).
  item 3 — the build version is folded into the bottom-left info ⓘ so the
           corner reads "ⓘ v18" (one container, version beside the control).
  items 4+5 — Trace preset drops park bounds + OSM park polygon + OSM tracks,
           keeps the SFWDA paper-map raster, turns the merged gold
           aop-trail-network ON (per-difficulty colour), and leaves the
           extracted SFWDA trace trails + legacy demo trails OFF.

The camera-settle smoothness (item 1) and the logo zoom-out overshoot (item 6)
are device/GL-only and are NOT asserted here — see the card.

Run after `cd website && python3 -m http.server 8001` is serving website/.
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, layer_visibility


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def paint(page, layer_id: str, prop: str):
    return page.evaluate(
        """([id, prop]) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getPaintProperty(id, prop);
        }""",
        [layer_id, prop],
    )


def wait_for_map(page) -> None:
    page.evaluate("window.map = map;")
    page.wait_for_function(
        "() => document.getElementById('message').textContent.includes('publish feature')",
        timeout=15_000,
    )
    page.wait_for_timeout(600)


def reset_storage(page) -> None:
    page.evaluate(
        """() => {
          try {
            localStorage.removeItem('aop_left_rail_drawer_v1');
            localStorage.removeItem('aop_virtual_clock_v1');
            localStorage.removeItem('aop_viewer_session_state_v1');
            localStorage.removeItem('aop_lr_card_height_v1');
          } catch (_) {}
        }"""
    )


def main() -> int:
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def record_console(msg) -> None:
            if msg.type != "error":
                return
            text = msg.text
            # Tile fetches over file/http in headless can 404; ignore those,
            # they are not app-logic errors (matches the other verifiers).
            if "Failed to fetch" in text or "ERR_" in text or "status of 4" in text:
                return
            console_errors.append(text)

        # ---- Desktop context: items 3, 4, 5, 1 -------------------------
        context = browser.new_context(viewport={"width": 1280, "height": 860})
        page = context.new_page()
        page.on("console", record_console)
        page.goto(viewer_url(), wait_until="load")
        reset_storage(page)
        page.reload(wait_until="load")
        wait_for_map(page)

        print("\n== Item 3 — build version folded into the bottom-left info ⓘ ==")
        ver = page.evaluate(
            """() => {
              const el = document.getElementById('appVersion');
              if (!el) return null;
              const bl = el.closest('.maplibregl-ctrl-bottom-left');
              return {
                text: el.textContent.trim(),
                inBottomLeft: !!bl,
                hasClass: !!bl && bl.classList.contains('attrib-with-version'),
                hasAttrib: !!bl && !!bl.querySelector('.maplibregl-ctrl-attrib'),
              };
            }"""
        )
        check("#appVersion exists", ver is not None)
        if ver:
            check("version text is v18", ver["text"] == "v18", ver["text"])
            check("version sits inside the bottom-left info control", ver["inBottomLeft"])
            check("bottom-left carries the attrib-with-version layout class", ver["hasClass"])
            check("the info ⓘ (attribution control) shares that container", ver["hasAttrib"])

        print("\n== Items 4+5 — Trace preset trail/reference layers ==")
        page.locator("#presetTrace").click()
        page.wait_for_timeout(500)
        check("Trace button becomes active",
              page.locator("#presetTrace").evaluate("el => el.classList.contains('active')"))
        # Disabled in Trace (item 4): park bounds, OSM park polygon, OSM tracks.
        check("park bounds (publish-boundaries) OFF in Trace",
              layer_visibility(page, "publish-boundaries") == "none",
              str(layer_visibility(page, "publish-boundaries")))
        check("OSM park polygon (osm-park-outline) OFF in Trace",
              layer_visibility(page, "osm-park-outline") == "none",
              str(layer_visibility(page, "osm-park-outline")))
        check("OSM tracks (osm-tracks) OFF in Trace",
              layer_visibility(page, "osm-tracks") == "none",
              str(layer_visibility(page, "osm-tracks")))
        # Kept (item 5): SFWDA paper-map raster + merged gold network ON.
        check("SFWDA paper trail map ON in Trace (showSfwda checked)",
              page.locator("#showSfwda").is_checked())
        check("merged aop-trail-network ON in Trace",
              layer_visibility(page, "aop-trail-network") == "visible",
              str(layer_visibility(page, "aop-trail-network")))
        check("aop-trail-network labels ON in Trace",
              layer_visibility(page, "aop-trail-network-labels") == "visible",
              str(layer_visibility(page, "aop-trail-network-labels")))
        # OFF (item 5): extracted SFWDA trace trails + legacy demo trails.
        check("extracted SFWDA trace trails OFF in Trace",
              page.locator("#showSfwdaTraceTrails").is_checked() is False)
        check("legacy demo trails (publish-trails) OFF in Trace",
              layer_visibility(page, "publish-trails") == "none",
              str(layer_visibility(page, "publish-trails")))
        # Merged network keeps its baked per-difficulty colour (coalesce expr),
        # not Topo's flat orange — confirm via Topo→Trace.
        page.locator("#presetTopo").click()
        page.wait_for_timeout(300)
        page.locator("#presetTrace").click()
        page.wait_for_timeout(400)
        trace_color = paint(page, "aop-trail-network", "line-color")
        check("Trace network keeps per-difficulty colour after Topo→Trace (not flat orange)",
              isinstance(trace_color, list),
              json_short(trace_color))

        print("\n== Regression — Park preset reference layers unchanged ==")
        page.locator("#presetPark").click()
        page.wait_for_timeout(400)
        check("Park: OSM park polygon still OFF",
              layer_visibility(page, "osm-park-outline") == "none")
        check("Park: park bounds still ON",
              layer_visibility(page, "publish-boundaries") == "visible",
              str(layer_visibility(page, "publish-boundaries")))
        check("Park: merged network still ON",
              layer_visibility(page, "aop-trail-network") == "visible")

        print("\n== Item 1 — calendar open-event popup uses a fixed bottom anchor ==")
        page.locator("#leftTabEvents").click()
        page.wait_for_timeout(200)
        row_count = page.locator(".calendar-row").count()
        if row_count == 0:
            check("calendar has selectable rows", False, "no .calendar-row rendered")
        else:
            page.locator(".calendar-row").first.click()
            page.wait_for_timeout(1400)  # let the flight settle + popup mount
            popup = page.evaluate(
                """() => {
                  const el = document.querySelector('.maplibregl-popup');
                  if (!el) return null;
                  return {
                    cls: el.className,
                    bottom: el.classList.contains('maplibregl-popup-anchor-bottom'),
                  };
                }"""
            )
            check("an event popup is shown", popup is not None)
            if popup:
                check("popup is pinned to the bottom anchor (no auto-flip)",
                      popup["bottom"], popup["cls"])
        context.close()

        # ---- Narrow context: item 2 -----------------------------------
        print("\n== Item 2 — mobile pick collapses the whole left drawer ==")
        narrow = browser.new_context(viewport={"width": 700, "height": 900})
        npage = narrow.new_page()
        npage.on("console", record_console)
        npage.goto(viewer_url(), wait_until="load")
        reset_storage(npage)
        npage.reload(wait_until="load")
        wait_for_map(npage)
        # On mobile the no-saved-state default is calendar-only open.
        cal_open_before = npage.locator("#lrPanelCal").evaluate("el => el.classList.contains('open')")
        check("calendar drawer starts open on mobile", cal_open_before)
        npage.locator("#leftTabEvents").click()
        npage.wait_for_timeout(200)
        if npage.locator(".calendar-row").count() == 0:
            check("calendar has selectable rows (mobile)", False, "no .calendar-row rendered")
        else:
            npage.locator(".calendar-row").first.click()
            npage.wait_for_timeout(500)
            cal_open_after = npage.locator("#lrPanelCal").evaluate("el => el.classList.contains('open')")
            check("calendar drawer collapses after picking an event", cal_open_after is False)
            search_open = npage.locator("#lrPanelSearch").evaluate("el => el.classList.contains('open')")
            hot_open = npage.locator("#lrPanelHot").evaluate("el => el.classList.contains('open')")
            check("search + hot drawers also collapsed", (search_open is False) and (hot_open is False))
        narrow.close()

        print("\n== Console ==")
        check("no app-logic console errors", len(console_errors) == 0,
              f"{len(console_errors)} error(s): {console_errors[:3]}")

        browser.close()

    print()
    if getattr(check, "failed", False):
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


def json_short(value) -> str:
    import json
    try:
        s = json.dumps(value)
    except Exception:
        s = str(value)
    return s[:80]


if __name__ == "__main__":
    sys.exit(main())
