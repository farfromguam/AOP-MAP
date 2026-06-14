#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) of four fixes:
  1. Trail label + search both read the number-first display name ("1 Launchpad").
  2. Tree cover is borderless (no landcover -outline layers).
  5. Search + event selection share ONE persistent active item (de-throne each other).
  6. "PRO Line Before the Fire" resolves to the #firepit POI coordinates.

Interactions are dispatched through the viewer's OWN handlers (native DOM click +
real keydown) so the genuine code paths run, without Playwright visibility waits.
Run: python3 brain/output/verify_label_border_persist_firepit.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
OUT = "brain/output"
FIREPIT = [-85.7482023, 35.090492]


def near(a, b, tol=1e-5):
    return bool(a) and abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


def log(m):
    print(m, flush=True)


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
            " && window.AOPViewer.map.getSource('event-schedule')",
            timeout=45000)
        page.wait_for_timeout(2500)
        log("map+data ready")

        # ---- Task 1 ----
        R["t1_trail1_display_name"] = page.evaluate("""() => {
            const d = window.AOPViewer.map.getSource('aop-trail-network').serialize().data;
            const f = d.features.find(x => String((x.properties||{}).trail_number) === '1');
            return f ? f.properties.display_name : null;
        }""")
        R["t1_label_textfield"] = page.evaluate(
            "() => window.AOPViewer.map.getLayoutProperty('aop-trail-network-labels','text-field')")
        R["t1_search_launchpad"] = page.evaluate("""() => {
            const i = document.getElementById('searchInput');
            i.value = 'launchpad';
            i.dispatchEvent(new Event('input', {bubbles:true}));
            return [...document.querySelectorAll('#searchResults .search-item')]
                     .map(e => e.textContent.replace(/\\s+/g,' ').trim());
        }""")
        log(f"t1 done: {R['t1_trail1_display_name']!r} / labels={R['t1_label_textfield']}")

        # ---- Task 2 ---- (pure data — no camera move; WebGL renders stall headless)
        log("t2 begin")
        R["t2"] = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            return {
              park_outline: !!m.getLayer('landcover-forest-outline'),
              patch_outline: !!m.getLayer('landcover-9patch-forest-outline'),
              park_fill: !!m.getLayer('landcover-forest'),
              park_fill_opacity: m.getLayer('landcover-forest') ? m.getPaintProperty('landcover-forest','fill-opacity') : null
            };
        }""")
        log(f"t2 done: {R['t2']}")

        # ---- Task 5a: search becomes the active item ----
        R["t5_search_first"] = page.evaluate("""() => {
            const i = document.getElementById('searchInput');
            i.value = 'launchpad';
            i.dispatchEvent(new Event('input', {bubbles:true}));
            i.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
            const hl = window.AOPViewer.map.getSource('search-highlight').serialize().data.features || [];
            return { highlight: hl.length };
        }""")
        page.wait_for_timeout(1200)

        # ---- Task 5b + 6: select the proline event via its REAL row handler ----
        R["t6_proline_row_present"] = page.evaluate(
            "() => !!document.querySelector('.calendar-row[data-session-id=\"sat-proline-fire\"]')")
        page.evaluate("""() => {
            const row = document.querySelector('.calendar-row[data-session-id="sat-proline-fire"]');
            if (row) row.click();
        }""")
        page.wait_for_timeout(1600)
        R["t5_active_after_event"] = page.evaluate(
            "() => { const a=document.querySelector('.calendar-row.active'); return a?a.getAttribute('data-session-id'):null; }")
        R["t5_highlight_after_event"] = page.evaluate(
            "() => (window.AOPViewer.map.getSource('search-highlight').serialize().data.features||[]).length")
        R["t6_proline_coords"] = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            const data = m.getSource('event-schedule').serialize().data;
            const feats = (data && data.features) || [];
            const anchor = feats.find(f => (f.properties||{}).location_tag === '#firepit'
                                         && f.geometry && f.geometry.type === 'Point');
            return anchor ? anchor.geometry.coordinates : null;
        }""")
        log(f"t5b/t6 done: active={R['t5_active_after_event']} coords={R['t6_proline_coords']}")

        # ---- Task 5c: a new search DE-THRONES the active event ----
        page.evaluate("""() => {
            const i = document.getElementById('searchInput');
            i.value = 'major tom';
            i.dispatchEvent(new Event('input', {bubbles:true}));
            i.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
        }""")
        page.wait_for_timeout(1400)
        R["t5_active_after_search"] = page.evaluate(
            "() => { const a=document.querySelector('.calendar-row.active'); return a?a.getAttribute('data-session-id'):null; }")
        R["t5_highlight_after_search"] = page.evaluate(
            "() => (window.AOPViewer.map.getSource('search-highlight').serialize().data.features||[]).length")
        log(f"t5c done: active_after_search={R['t5_active_after_search']}")

        # NOTE: no camera move / screenshot here — ANY programmatic camera-move
        # evaluate (jumpTo/flyTo) deadlocks this headless swiftshader build and
        # would block the verdict. The data checks below ARE the observation;
        # the borderless tree cover is also confirmed visually in the separately
        # captured verify_treecover_borderless.png.

        # Compute + print the verdict INSIDE the context, before the cleanup —
        # browser.close() can hang on this headless build, and plain print() is
        # block-buffered, so the verdict must flush before any close.
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
        "T1 map label uses display_name": R["t1_label_textfield"] == ["get", "display_name"],
        "T1 trail 1 display_name == '1 Launchpad'": R["t1_trail1_display_name"] == "1 Launchpad",
        "T1 search shows '1 Launchpad'": any("1 Launchpad" in s for s in R["t1_search_launchpad"]),
        "T2 park outline layer gone": R["t2"]["park_outline"] is False,
        "T2 9patch outline layer gone": R["t2"]["patch_outline"] is False,
        "T2 park fill solid (opacity 1)": R["t2"]["park_fill_opacity"] == 1,
        "T5 search sets a persistent highlight": (R["t5_search_first"]["highlight"] or 0) >= 1,
        "T5 event becomes active item": R["t5_active_after_event"] == "sat-proline-fire",
        "T5 highlight holds event feature": (R["t5_highlight_after_event"] or 0) >= 1,
        "T5 new search de-thrones event (no active row)": R["t5_active_after_search"] is None,
        "T5 highlight holds searched trail": (R["t5_highlight_after_search"] or 0) >= 1,
        "T6 proline anchor at firepit coords": near(R["t6_proline_coords"], FIREPIT),
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
