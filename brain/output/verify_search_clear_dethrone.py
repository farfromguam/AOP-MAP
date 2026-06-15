#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that clearing the search
bar drops the held highlight and de-thrones the active item.

  A. Backspace-to-empty (input event, empty value) empties search-highlight.
  B. Escape clears the input value, empties search-highlight, AND de-thrones the
     active event row (no .calendar-row.active remains).
  Baseline: a search still SETS a persistent highlight (so A/B prove removal, not
  that the highlight never appeared).

Interactions go through the viewer's OWN handlers (native input/keydown events) so
the real code paths run. No programmatic camera move (jumpTo/flyTo via evaluate
deadlocks this headless swiftshader build) — the search-highlight source data IS
the observation.
Run: python3 brain/output/verify_search_clear_dethrone.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"


def log(m):
    print(m, flush=True)


def hl_count(page):
    return page.evaluate(
        "() => (window.AOPViewer.map.getSource('search-highlight')"
        ".serialize().data.features || []).length")


def main():
    R = {}
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.set_default_timeout(8000)
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        log("goto")
        page.goto(URL, wait_until="load")
        page.wait_for_function(
            "() => window.AOPViewer && window.AOPViewer.map && window.AOPViewer.map.isStyleLoaded()"
            " && window.AOPViewer.map.getSource('aop-trail-network')"
            " && window.AOPViewer.map.getSource('event-schedule')"
            " && window.AOPViewer.map.getSource('search-highlight')",
            timeout=45000)
        page.wait_for_timeout(2500)
        log("map+data ready")

        # ---- A: search sets a highlight, backspace-to-empty removes it ----
        page.evaluate("""() => {
            const i = document.getElementById('searchInput');
            i.value = 'major tom';
            i.dispatchEvent(new Event('input', {bubbles:true}));
            i.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
        }""")
        page.wait_for_timeout(1200)
        R["A_hl_after_search"] = hl_count(page)
        page.evaluate("""() => {
            const i = document.getElementById('searchInput');
            i.value = '';                                  // user backspaced to empty
            i.dispatchEvent(new Event('input', {bubbles:true}));
        }""")
        page.wait_for_timeout(300)
        R["A_hl_after_clear"] = hl_count(page)
        log(f"A done: after_search={R['A_hl_after_search']} after_clear={R['A_hl_after_clear']}")

        # ---- B: search + select event (active row), Escape clears + de-thrones ----
        page.evaluate("""() => {
            const i = document.getElementById('searchInput');
            i.value = 'launchpad';
            i.dispatchEvent(new Event('input', {bubbles:true}));
            i.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
        }""")
        page.wait_for_timeout(1200)
        page.evaluate("""() => {
            const row = document.querySelector('.calendar-row[data-session-id="sat-proline-fire"]');
            if (row) row.click();
        }""")
        page.wait_for_timeout(1600)
        R["B_active_before"] = page.evaluate(
            "() => { const a=document.querySelector('.calendar-row.active'); return a?a.getAttribute('data-session-id'):null; }")
        R["B_hl_before"] = hl_count(page)
        page.evaluate("""() => {
            const i = document.getElementById('searchInput');
            i.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', bubbles:true}));
        }""")
        page.wait_for_timeout(400)
        R["B_input_value_after"] = page.evaluate("() => document.getElementById('searchInput').value")
        R["B_hl_after"] = hl_count(page)
        R["B_active_after"] = page.evaluate(
            "() => { const a=document.querySelector('.calendar-row.active'); return a?a.getAttribute('data-session-id'):null; }")
        log(f"B done: active_before={R['B_active_before']} active_after={R['B_active_after']}")

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    checks = {
        "A baseline: search sets a highlight": (R["A_hl_after_search"] or 0) >= 1,
        "A backspace-to-empty clears highlight": R["A_hl_after_clear"] == 0,
        "B event is active before Escape": R["B_active_before"] == "sat-proline-fire",
        "B highlight held before Escape": (R["B_hl_before"] or 0) >= 1,
        "B Escape empties the input value": R["B_input_value_after"] == "",
        "B Escape clears the highlight": R["B_hl_after"] == 0,
        "B Escape de-thrones the active event row": R["B_active_after"] is None,
        "No console errors": len(real_errors) == 0,
    }
    print(json.dumps(R, indent=2), flush=True)
    print("\n--- CHECKS ---", flush=True)
    allok = True
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}", flush=True)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}", flush=True)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
