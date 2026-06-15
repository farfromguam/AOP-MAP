#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that the "The Gravity Gauntlet"
schedule session now LINKS to the proper point — the same map point as the #gravity-gauntlet
pin — following the existing #firepit / #pavilion example.

User: "make sure the schedule links to the proper point. there should be examples." The
session sat-gravity-gauntlet was tagged location_tag:"#trails" (coordinate-less, so clicking
its calendar row flew nowhere / opened no popup). Fix (data-only, mirroring #firepit):
  - aop_event_schedule.json: new `locations["#gravity-gauntlet"]` WITH coordinates
    [-85.7515, 35.09191] (identical to the gold waypoint), confidence high, source names the GPX.
  - the sat-gravity-gauntlet session retagged location_tag "#trails" -> "#gravity-gauntlet".

The eventScheduleToGeojson transform then emits an `event_anchor` Point at those coords and
gives the session a Point geometry there, so gotoEventSession flies to the point + opens the
session popup at it (viewer_core.js:1517-1555). "Proper point" = the schedule anchor coincides
with the pin. Drives the real DOM: clicks the calendar row, reads the live popup, and confirms
BOTH the waypoint pin AND the event anchor render at the same projected point.

Run: python3 brain/output/verify_gravity_gauntlet_schedule_link.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
TAG = "#gravity-gauntlet"
TITLE = "The Gravity Gauntlet"
SESSION_ID = "sat-gravity-gauntlet"
GG = [-85.7515, 35.09191]


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
            " && window.AOPViewer.map.getSource('event-schedule')"
            " && window.AOPViewer.map.getSource('aop-waypoints')",
            timeout=45000)
        page.wait_for_timeout(1000)

        # Park preset so the waypoint pin layer renders (event layers are selection-driven).
        page.evaluate("() => { const b=document.querySelector('[data-preset=\"park\"]'); if(b) b.click(); }")
        page.wait_for_timeout(500)

        # ---- The live schedule join: anchor + session Point at the GG coords ----
        R["join"] = page.evaluate("""(args) => {
            const [tag, sid] = args;
            const d = window.AOPViewer.map.getSource('event-schedule').serialize().data;
            const feats = d.features || [];
            const anchor = feats.find(f => (f.properties||{}).feature_kind === 'event_anchor'
                                        && f.properties.location_tag === tag);
            const sess = feats.find(f => (f.properties||{}).session_id === sid);
            return {
                anchor: anchor ? { tag: anchor.properties.location_tag,
                                   map_label: anchor.properties.map_label,
                                   coords: anchor.geometry && anchor.geometry.coordinates } : null,
                session: sess ? { tag: sess.properties.location_tag,
                                  location_label: sess.properties.location_label,
                                  geom_type: sess.geometry && sess.geometry.type,
                                  coords: sess.geometry && sess.geometry.coordinates } : null
            };
        }""", [TAG, SESSION_ID])
        log("join: " + json.dumps(R["join"]))

        # ---- Open Events tab, click the Gravity Gauntlet calendar row ----
        page.evaluate("() => { const b=document.querySelector('[data-left-tab=\"events\"]'); if(b) b.click(); }")
        page.wait_for_selector(f'.calendar-row[data-session-id="{SESSION_ID}"]', timeout=20000)
        center_before = page.evaluate("() => window.AOPViewer.map.getCenter()")
        page.click(f'.calendar-row[data-session-id="{SESSION_ID}"]')
        page.wait_for_selector(".maplibregl-popup-content strong", timeout=12000)
        page.wait_for_timeout(1400)  # let the flyTo settle

        # The popup body is detailRows() — plain "Label: value" lines joined by <br/>,
        # NOT a dt/dd table. Read the text and parse the "Label: value" pairs.
        R["popup"] = page.evaluate("""() => {
            const pop = document.querySelector('.maplibregl-popup-content');
            if (!pop) return null;
            const text = pop.innerText || '';
            const rows = {};
            text.split('\\n').forEach(line => {
                const i = line.indexOf(':');
                if (i > 0) rows[line.slice(0, i).trim()] = line.slice(i + 1).trim();
            });
            return { title: (pop.querySelector('strong')||{}).textContent || '', text, rows };
        }""")
        log("popup: " + json.dumps(R["popup"]))

        R["anchor_layer_visible"] = page.evaluate(
            "() => window.AOPViewer.map.getLayoutProperty('event-anchor-points','visibility') !== 'none'")
        center_after = page.evaluate("() => window.AOPViewer.map.getCenter()")
        R["camera_moved"] = (round(center_before["lng"], 5) != round(center_after["lng"], 5)
                             or round(center_before["lat"], 5) != round(center_after["lat"], 5))

        # ---- The schedule anchor coincides with the waypoint pin (same projected point) ----
        R["coincident"] = page.evaluate("""(gg) => {
            const m = window.AOPViewer.map;
            const pt = m.project({ lng: gg[0], lat: gg[1] });
            const box = [[pt.x - 8, pt.y - 8], [pt.x + 8, pt.y + 8]];
            const pin = m.queryRenderedFeatures(box, { layers: ['aop-waypoints'] })
                         .some(f => (f.properties||{}).name === 'Gravity Gauntlet');
            const anchor = m.queryRenderedFeatures(box, { layers: ['event-anchor-points'] })
                            .some(f => (f.properties||{}).location_tag === '#gravity-gauntlet');
            return { pin_at_point: pin, anchor_at_point: anchor };
        }""", GG)
        log("coincident: " + json.dumps(R["coincident"]))

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    join = R.get("join") or {}
    anchor = join.get("anchor") or {}
    sess = join.get("session") or {}
    pop = R.get("popup") or {}
    rows = pop.get("rows", {})
    coin = R.get("coincident") or {}
    checks = {
        "schedule join emits an event_anchor for #gravity-gauntlet": bool(anchor),
        "anchor sits at the waypoint coords [-85.7515, 35.09191]": anchor.get("coords") == GG,
        "session sat-gravity-gauntlet now has a Point geometry": sess.get("geom_type") == "Point",
        "session point is at the waypoint coords": sess.get("coords") == GG,
        "session retagged to #gravity-gauntlet": sess.get("tag") == TAG,
        "session location_label reads 'Gravity Gauntlet'": sess.get("location_label") == "Gravity Gauntlet",
        "calendar-row click opened the session popup": bool(pop.get("title")),
        "popup title is 'The Gravity Gauntlet'": pop.get("title", "").strip() == TITLE,
        "popup Location reads 'Gravity Gauntlet'": rows.get("Location") == "Gravity Gauntlet",
        "popup Tag reads '#gravity-gauntlet'": rows.get("Tag") == TAG,
        "event-anchor layer turned on by the selection": R.get("anchor_layer_visible") is True,
        "camera flew to the point": R.get("camera_moved") is True,
        "the waypoint PIN renders at the point": coin.get("pin_at_point") is True,
        "the schedule ANCHOR renders at the SAME point (links to it)": coin.get("anchor_at_point") is True,
        "No console errors": len(real_errors) == 0,
    }
    print(json.dumps(R, indent=2, ensure_ascii=False), flush=True)
    print("\n--- CHECKS ---", flush=True)
    allok = True
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}", flush=True)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}", flush=True)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
