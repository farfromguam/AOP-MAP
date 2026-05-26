#!/usr/bin/env python3
"""Playwright verification for viewer session tools and pocket-map state.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import WEBSITE_URL


REPO_ROOT = Path(__file__).resolve().parents[2]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def clear_viewer_storage(page) -> None:
    page.evaluate(
        """() => {
          const keys = [
            'aop_calendar_height_v1',
            'aop_calendar_collapsed_v1',
            'aop_left_rail_drawer_v1',
            'aop_virtual_clock_v1',
            'aop_viewer_session_state_v1',
            'aop_viewer_preset_settings_v1',
            'aop_feature_visibility_v1',
            'aop_feature_tags_v1',
            'aop_feature_tags_seeded_v1',
            'aop_editor_pois_v1',
            'aop_visitor_context_overrides_v1',
            'aop_brand_logos_overrides_v1'
          ];
          for (const key of keys) {
            try { localStorage.removeItem(key); } catch (_) {}
          }
        }"""
    )


def wait_loaded(page) -> None:
    page.evaluate("window.map = map;")
    page.wait_for_function(
        "() => document.getElementById('message').textContent.includes('publish feature')",
        timeout=15_000,
    )
    page.wait_for_function(
        "() => document.querySelectorAll('#calendarDays .calendar-row').length === 12",
        timeout=15_000,
    )
    page.wait_for_timeout(500)


def open_session_tools(page) -> None:
    page.evaluate(
        """() => {
          const section = document.querySelector('section[data-section="session-tools"]');
          if (section && section.classList.contains('collapsed')) {
            section.querySelector('.section-toggle')?.click();
          }
        }"""
    )
    page.wait_for_timeout(150)


def session_state(page) -> dict:
    return page.evaluate(
        """() => {
          const rawSession = localStorage.getItem('aop_viewer_session_state_v1');
          const rawClock = localStorage.getItem('aop_virtual_clock_v1');
          return {
            activePreset: [...document.querySelectorAll('.preset-bar button[data-preset]')]
              .find((b) => b.classList.contains('active'))?.dataset.preset || null,
            activeTab: [...document.querySelectorAll('.left-tab[data-left-tab]')]
              .find((b) => b.getAttribute('aria-selected') === 'true')?.dataset.leftTab || null,
            searchValue: document.getElementById('searchInput')?.value || '',
            clockStatus: document.getElementById('virtualClockStatus')?.textContent || '',
            clockActive: document.getElementById('virtualClockStatus')?.dataset.clockActive || '',
            hotTitle: document.getElementById('hotButtonTitle')?.textContent || '',
            activeRows: [...document.querySelectorAll('.calendar-row.active')].map((r) => r.dataset.sessionId),
            popupText: [...document.querySelectorAll('.maplibregl-popup')].map((el) => el.innerText).join('\\n'),
            session: rawSession ? JSON.parse(rawSession) : null,
            clock: rawClock ? JSON.parse(rawClock) : null,
            storageKeys: Object.keys(localStorage).filter((key) => key.startsWith('aop_')).sort()
          };
        }"""
    )


def main() -> int:
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader"])
        context = browser.new_context(viewport={"width": 1280, "height": 840})
        page = context.new_page()

        def record_console(msg) -> None:
            if msg.type != "error":
                return
            text = msg.text
            ignored = (
                "AJAXError: Failed to fetch (0):" in text
                or text.strip().endswith("TypeError: Failed to fetch")
                or text.strip() == "TypeError: Failed to fetch"
            )
            if not ignored:
                console_errors.append(text)

        page.on("console", record_console)
        page.on("dialog", lambda dialog: dialog.accept())

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        clear_viewer_storage(page)
        page.reload(wait_until="load")
        wait_loaded(page)
        open_session_tools(page)

        print("\n== Virtual clock ==")
        page.locator("#virtualClockDate").fill("2026-06-20")
        page.locator("#virtualClockTime").fill("13:15")
        page.locator("#clockUseInputs").click()
        page.wait_for_timeout(350)
        state = session_state(page)
        first_ms = state["clock"]["ms"] if state["clock"] else None
        check("setting date/time activates the test clock", state["clockActive"] == "true" and "2026-06-20 13:15" in state["clockStatus"], str(state))
        check("test clock persists to localStorage", isinstance(first_ms, int), str(state.get("clock")))
        check("13:15 fixture makes Proving Grounds the imminent event", state["hotTitle"] == "Starting soon", str(state))

        page.locator("#clockPlusHour").click()
        page.wait_for_timeout(350)
        state = session_state(page)
        second_ms = state["clock"]["ms"] if state["clock"] else None
        check("+1h advances the stored clock", second_ms - first_ms == 60 * 60 * 1000, f"first={first_ms} second={second_ms}")
        check("+1h changes the hot lane to live event", state["hotTitle"] == "Live event", str(state))

        page.locator("#clockPlusDay").click()
        page.wait_for_timeout(150)
        state = session_state(page)
        third_ms = state["clock"]["ms"] if state["clock"] else None
        check("+1d advances the stored clock by one day", third_ms - second_ms == 24 * 60 * 60 * 1000, f"second={second_ms} third={third_ms}")
        page.locator("#clockClear").click()
        page.wait_for_timeout(250)
        state = session_state(page)
        check("clear returns to wall clock", state["clockActive"] == "false" and state["clock"] is None, str(state))

        print("\n== Pocket-map persistence ==")
        page.locator("#presetTopo").click()
        page.locator("#leftTabPoi").click()
        page.locator("#searchInput").fill("pavilion")
        page.wait_for_timeout(250)
        state = session_state(page)
        check("session state records active preset, tab, and search query",
              state["session"].get("active_preset") == "topo"
              and state["session"].get("active_left_tab") == "poi"
              and state["session"].get("search_query") == "pavilion",
              str(state.get("session")))

        page.reload(wait_until="load")
        wait_loaded(page)
        state = session_state(page)
        check("active preset survives reload", state["activePreset"] == "topo", str(state))
        check("active left tab survives reload", state["activeTab"] == "poi", str(state))
        check("search query survives reload", state["searchValue"] == "pavilion", str(state))

        print("\n== Selected calendar event persistence ==")
        page.locator("#leftTabEvents").click()
        page.locator('[data-session-id="sat-g6-cove-rally"]').click()
        page.wait_for_timeout(1500)
        state = session_state(page)
        check("calendar click records selected session", state["session"].get("active_event_session_id") == "sat-g6-cove-rally", str(state.get("session")))
        page.reload(wait_until="load")
        wait_loaded(page)
        state = session_state(page)
        check("selected calendar row survives reload", "sat-g6-cove-rally" in state["activeRows"], str(state))
        check("selected session popup reopens after reload", "G6 Cove Rally stages" in state["popupText"], state["popupText"])

        print("\n== Reset viewer ==")
        open_session_tools(page)
        page.evaluate(
            """() => {
              const jsonSeed = JSON.stringify({ schema: 'verifier-seed' });
              for (const key of [
                'aop_calendar_height_v1',
                'aop_calendar_collapsed_v1',
                'aop_left_rail_drawer_v1',
                'aop_virtual_clock_v1',
                'aop_viewer_session_state_v1',
                'aop_viewer_preset_settings_v1',
                'aop_feature_visibility_v1',
                'aop_feature_tags_v1',
                'aop_editor_pois_v1',
                'aop_visitor_context_overrides_v1',
                'aop_brand_logos_overrides_v1'
              ]) {
                localStorage.setItem(key, jsonSeed);
              }
              localStorage.setItem('aop_feature_tags_seeded_v1', '1');
            }"""
        )
        page.locator("#resetViewerState").click()
        page.wait_for_timeout(1200)
        state = session_state(page)
        owned_after_reset = [key for key in state["storageKeys"] if key in {
            "aop_calendar_height_v1",
            "aop_calendar_collapsed_v1",
            "aop_left_rail_drawer_v1",
            "aop_virtual_clock_v1",
            "aop_viewer_session_state_v1",
            "aop_viewer_preset_settings_v1",
            "aop_feature_visibility_v1",
            "aop_feature_tags_v1",
            "aop_feature_tags_seeded_v1",
            "aop_editor_pois_v1",
            "aop_visitor_context_overrides_v1",
            "aop_brand_logos_overrides_v1",
        }]
        check("reset clears viewer-owned localStorage", owned_after_reset == [], str(state["storageKeys"]))
        check("reset returns to Park preset", state["activePreset"] == "park", str(state))
        check("reset returns to Events tab", state["activeTab"] == "events", str(state))
        check("reset clears search query and virtual clock", state["searchValue"] == "" and state["clockActive"] == "false", str(state))

        if console_errors:
            print("\nConsole errors:")
            for text in console_errors:
                print("  " + text)
        check("no non-tile console errors", not console_errors)

        browser.close()

    return 1 if check.failed else 0  # type: ignore[attr-defined]


if __name__ == "__main__":
    sys.exit(main())
