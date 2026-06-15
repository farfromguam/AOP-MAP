#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that the event-schedule
calendar rows no longer show the raw internal #tag in front of the human label.

Bug the user reported: each schedule row's location read "#pavilion - Pavilion
(base camp)" — the internal foreign-key tag (#pavilion) printed right in front of
its own human name, which is redundant noise. The fix drops the "${tag} - " prefix
in BOTH calendar renders (viewer_core.js renderEventCalendar + main.js's editor
copy), leaving just the human location label.

This reads the LIVE rendered .calendar-location spans (the running app's real DOM
output), and confirms:
  - no row's location text contains a raw '#' tag,
  - the pavilion rows render their human label ("Pavilion (base camp)"),
  - the row count is unchanged (no rows dropped),
  - no console errors.

Run: python3 brain/output/verify_schedule_no_tag_prefix.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"


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
        # calendar rows render from the schedule source on load (even while collapsed)
        page.wait_for_function(
            "() => document.querySelectorAll('.calendar-row').length > 0", timeout=20000)
        page.wait_for_timeout(800)
        log("map + calendar rows ready")

        # ---- Read the live rendered calendar rows ----
        R["rows"] = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.calendar-row')).map(r => ({
                id: r.getAttribute('data-session-id'),
                name: (r.querySelector('.calendar-name')||{}).textContent || '',
                location: (r.querySelector('.calendar-location')||{}).textContent || ''
            }));
        }""")
        # ---- Cross-check against the resolver: every session's location_tag ----
        R["session_tags"] = page.evaluate("""() => {
            const data = window.AOPViewer.map.getSource('event-schedule').serialize().data;
            const out = {};
            for (const f of ((data && data.features) || [])) {
                const p = f.properties || {};
                if (p.feature_kind === 'event_session')
                    out[p.session_id] = { tag: p.location_tag, label: p.location_label };
            }
            return out;
        }""")
        log(f"{len(R['rows'])} rows rendered")
        for row in R["rows"]:
            log(f"  {row['id']:18} loc={row['location']!r}")

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    rows = R["rows"]
    tags = R["session_tags"]
    locs = [r["location"] for r in rows]
    pav_rows = [r for r in rows if (tags.get(r["id"]) or {}).get("tag") == "#pavilion"]
    fire_rows = [r for r in rows if (tags.get(r["id"]) or {}).get("tag") == "#firepit"]

    checks = {
        "calendar rendered rows": len(rows) > 0,
        "session count matches resolver": len(rows) == len(tags),
        "NO row location contains a raw '#' tag": all("#" not in loc for loc in locs),
        "NO row location starts with the tag-dash prefix": all(" - " not in loc or not loc.lstrip().startswith("#") for loc in locs),
        "every row location is non-empty": all(loc.strip() for loc in locs),
        "pavilion rows show 'Pavilion (base camp)'": bool(pav_rows) and all(r["location"].strip() == "Pavilion (base camp)" for r in pav_rows),
        "firepit rows show 'Firepit'": bool(fire_rows) and all(r["location"].strip() == "Firepit" for r in fire_rows),
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
