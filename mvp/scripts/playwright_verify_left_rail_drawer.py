#!/usr/bin/env python3
"""Playwright verification for the left-rail two-column drawer.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def drawer_state(page) -> dict:
    return page.evaluate(
        """() => {
          const cards = ['search', 'hot', 'cal'];
          const tabId = { search: 'lrTabSearch', hot: 'lrTabHot', cal: 'lrTabCal' };
          const panelId = { search: 'lrPanelSearch', hot: 'lrPanelHot', cal: 'lrPanelCal' };
          const iconCol = document.getElementById('lrIconCol');
          const contentCol = document.getElementById('lrContentCol');
          const iconRect = iconCol.getBoundingClientRect();
          const contentRect = contentCol.getBoundingClientRect();
          const tabs = {};
          const panels = {};
          for (const c of cards) {
            const tab = document.getElementById(tabId[c]);
            const panel = document.getElementById(panelId[c]);
            const tr = tab.getBoundingClientRect();
            const pr = panel.getBoundingClientRect();
            tabs[c] = {
              open: tab.classList.contains('open'),
              pressed: tab.getAttribute('aria-pressed'),
              relTop: Math.round((tr.top - iconRect.top) * 10) / 10
            };
            panels[c] = {
              open: panel.classList.contains('open'),
              relTop: Math.round((pr.top - contentRect.top) * 10) / 10,
              height: Math.round(pr.height * 10) / 10
            };
          }
          let storage = null;
          try {
            const raw = localStorage.getItem('aop_left_rail_drawer_v1');
            storage = raw ? JSON.parse(raw) : null;
          } catch (_) {}
          return {
            tabs,
            panels,
            contentHidden: contentCol.hidden,
            standalone: iconCol.classList.contains('standalone'),
            col2Short: iconCol.classList.contains('col2-short'),
            hotControlHidden: document.getElementById('hotControl').hidden,
            storage
          };
        }"""
    )


def open_state(state: dict) -> dict[str, bool]:
    return {key: bool(value["open"]) for key, value in state["tabs"].items()}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader"])
        context = browser.new_context(viewport={"width": 1280, "height": 820})
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

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
        page.evaluate(
            """() => {
              try {
                localStorage.removeItem('aop_left_rail_drawer_v1');
                localStorage.removeItem('aop_virtual_clock_v1');
                localStorage.removeItem('aop_viewer_session_state_v1');
                localStorage.removeItem('aop_calendar_height_v1');
              } catch (_) {}
            }"""
        )
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_function(
            "() => !document.getElementById('hotControl').hidden",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        print("\n== Default + hot data arrival ==")
        state = drawer_state(page)
        check("drawer DOM is present", page.locator("#lrDrawer #lrTabSearch").count() == 1 and page.locator("#lrContentCol").count() == 1)
        check(
            "hot data auto-opens the Hot tab when no saved drawer state exists",
            open_state(state) == {"search": True, "hot": True, "cal": True}
            and state["hotControlHidden"] is False,
            str(state),
        )
        check(
            "Cal icon floats down to the Cal panel top when all cards are open",
            abs(state["tabs"]["cal"]["relTop"] - state["panels"]["cal"]["relTop"]) <= 2,
            str(state),
        )
        check(
            "tab order stays canonical top to bottom",
            state["tabs"]["search"]["relTop"] < state["tabs"]["hot"]["relTop"] < state["tabs"]["cal"]["relTop"],
            str(state["tabs"]),
        )
        check(
            "auto-open does not create saved drawer state by itself",
            state["storage"] is None,
            str(state.get("storage")),
        )

        print("\n== User close persists and suppresses later auto-open ==")
        page.locator("#lrTabHot").click()
        page.wait_for_timeout(250)
        state = drawer_state(page)
        check(
            "click toggles Hot closed",
            open_state(state) == {"search": True, "hot": False, "cal": True},
            str(state),
        )
        check(
            "manual Hot close persists",
            state["storage"] and state["storage"].get("open", {}).get("hot") is False,
            str(state.get("storage")),
        )
        page.evaluate("window.lrOpenCard('hot', { auto: true })")
        page.wait_for_timeout(150)
        state = drawer_state(page)
        check(
            "auto Hot open respects saved user-close state",
            open_state(state)["hot"] is False,
            str(state),
        )

        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_function(
            "() => !document.getElementById('hotControl').hidden",
            timeout=15_000,
        )
        page.wait_for_timeout(500)
        state = drawer_state(page)
        check(
            "saved Hot close survives reload even after data arrives",
            open_state(state) == {"search": True, "hot": False, "cal": True},
            str(state),
        )

        print("\n== All-closed standalone state ==")
        page.evaluate(
            """() => {
              window.lrCloseCard('search');
              window.lrCloseCard('hot');
              window.lrCloseCard('cal');
            }"""
        )
        page.wait_for_timeout(250)
        state = drawer_state(page)
        check(
            "all cards can close",
            open_state(state) == {"search": False, "hot": False, "cal": False},
            str(state),
        )
        check(
            "all-closed drawer hides content column and rounds icon column standalone",
            state["contentHidden"] is True and state["standalone"] is True,
            str(state),
        )

        if console_errors:
            print("\nConsole errors:")
            for text in console_errors:
                print("  " + text)
        check("no non-tile console errors", not console_errors)

        browser.close()

    return 1 if check.failed else 0  # type: ignore[attr-defined]


if __name__ == "__main__":
    sys.exit(main())
