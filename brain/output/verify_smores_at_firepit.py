#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that the "Fire + s'mores"
sessions now resolve to the #firepit POI, not #pavilion.

Bug: the v87 batch tagged the "PRO Line Before the Fire" race to #firepit but left
both "Fire + s'mores" sessions (fri-fire, sat-fire) pointing at #pavilion. The
source copy (brain/import/TBI.copy) says the crew "head to the fire pit for some
smores", so the s'mores belong at the firepit.

Checks the live event-schedule GeoJSON source (the running resolver's real output),
then drives the Saturday s'mores calendar row through its OWN handler and confirms
it becomes the active item. No direct camera-move evaluate (that deadlocks the
headless swiftshader build); the row click's internal fly is the app's own path.

Run: python3 brain/output/verify_smores_at_firepit.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
FIREPIT = [-85.7482023, 35.090492]
PAVILION = [-85.7482512, 35.0907264]


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
            " && window.AOPViewer.map.getSource('event-schedule')",
            timeout=45000)
        page.wait_for_timeout(2000)
        log("map+schedule ready")

        # ---- Read the live resolver output for each session feature ----
        R["sessions"] = page.evaluate("""() => {
            const data = window.AOPViewer.map.getSource('event-schedule').serialize().data;
            const feats = (data && data.features) || [];
            const out = {};
            for (const id of ['fri-fire','sat-fire','sat-proline-fire']) {
                const f = feats.find(x => (x.properties||{}).session_id === id);
                out[id] = f ? { tag: f.properties.location_tag,
                                coords: f.geometry && f.geometry.coordinates } : null;
            }
            // firepit anchor present?
            const anchor = feats.find(f => (f.properties||{}).feature_kind === 'event_anchor'
                                         && f.properties.location_tag === '#firepit');
            out['_firepit_anchor'] = anchor ? anchor.geometry.coordinates : null;
            return out;
        }""")
        log(f"sessions: {R['sessions']}")

        # ---- Drive the Saturday s'mores calendar row through its own handler ----
        R["sat_fire_row_present"] = page.evaluate(
            "() => !!document.querySelector('.calendar-row[data-session-id=\"sat-fire\"]')")
        page.evaluate("""() => {
            const row = document.querySelector('.calendar-row[data-session-id="sat-fire"]');
            if (row) row.click();
        }""")
        page.wait_for_timeout(1600)
        R["active_after_click"] = page.evaluate(
            "() => { const a=document.querySelector('.calendar-row.active'); return a?a.getAttribute('data-session-id'):null; }")
        R["highlight_after_click"] = page.evaluate(
            "() => (window.AOPViewer.map.getSource('search-highlight').serialize().data.features||[]).length")
        log(f"row drive: active={R['active_after_click']} highlight={R['highlight_after_click']}")

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    s = R["sessions"]
    checks = {
        "fri-fire tagged #firepit": s.get("fri-fire", {}).get("tag") == "#firepit",
        "fri-fire at firepit coords": near((s.get("fri-fire") or {}).get("coords"), FIREPIT),
        "fri-fire NOT at pavilion": not near((s.get("fri-fire") or {}).get("coords"), PAVILION),
        "sat-fire tagged #firepit": s.get("sat-fire", {}).get("tag") == "#firepit",
        "sat-fire at firepit coords": near((s.get("sat-fire") or {}).get("coords"), FIREPIT),
        "sat-fire NOT at pavilion": not near((s.get("sat-fire") or {}).get("coords"), PAVILION),
        "PRO Line still at firepit (regression)": near((s.get("sat-proline-fire") or {}).get("coords"), FIREPIT),
        "firepit anchor renders at firepit coords": near(s.get("_firepit_anchor"), FIREPIT),
        "sat s'mores row present": R["sat_fire_row_present"] is True,
        "sat s'mores row becomes active item": R["active_after_click"] == "sat-fire",
        "click sets a map highlight": (R["highlight_after_click"] or 0) >= 1,
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
