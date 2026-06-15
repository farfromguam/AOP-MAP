#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that the starred "Hot Rocks
Comp Pad" camp waypoint now appears in the reader's POI list and opens correctly.

User: "Hot rock comp pad needs to be starred and show up in poi list." The POI list
(viewer_core.js buildPoiGroups) is ★-gated (properties.highlight===true) over the
STAR_GROUPS source set, which had buildings/trails/visitor-support but NO camp-
waypoints group — so starring a waypoint alone wouldn't surface it. Fix:
  - data: gold_aop_waypoints_traced.geojson — Hot Rocks Comp Pad gets highlight:true.
  - viewer_core.js: expose the loaded waypoints as module-scoped poiWaypointsData and
    add a { id:'waypoints', label:'Camp POIs', data:()=>poiWaypointsData } STAR_GROUP.

Only highlighted waypoints appear, so the Camp POIs group must contain EXACTLY the one
starred pad (RV sites / cabins / firepit etc. stay out). Drives the real DOM: opens the
POI tab, reads the rendered group + rows, clicks the row, reads the live popover.

Run: python3 brain/output/verify_hot_rocks_in_poi_list.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
NAME = "Hot Rocks Comp Pad"


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
            " && window.AOPViewer.map.getSource('aop-waypoints')",
            timeout=45000)
        page.wait_for_timeout(1200)

        # ---- Cross-check the live waypoints source: only Hot Rocks is highlighted ----
        R["highlighted_waypoints"] = page.evaluate("""() => {
            const d = window.AOPViewer.map.getSource('aop-waypoints').serialize().data;
            return (d.features || []).filter(f => (f.properties||{}).highlight === true)
                                     .map(f => f.properties.name);
        }""")

        # ---- Open POI tab, read the rendered groups ----
        page.click("#leftTabPoi")
        page.wait_for_function(
            "() => document.querySelectorAll('#poiList .poi-row').length > 0", timeout=20000)
        page.wait_for_timeout(400)
        R["groups"] = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('#poiList .poi-list-group')).map(g => {
                const head = g.querySelector('.poi-list-group-head');
                const label = head ? (head.querySelector('span') || {}).textContent : '';
                const count = head ? (head.querySelector('.poi-list-group-count')||{}).textContent : '';
                const rows = Array.from(g.querySelectorAll('.poi-row')).map(r => ({
                    name: (r.querySelector('.poi-row-name')||{}).textContent || '',
                    subtitle: (r.querySelector('.poi-row-subtitle')||{}).textContent || '',
                    meta_chips: r.querySelectorAll('.poi-row-meta span').length
                }));
                return { label, count, rows };
            });
        }""")
        log("groups: " + json.dumps(R["groups"], indent=2))

        camp = next((g for g in R["groups"] if g["label"] == "Camp POIs"), None)
        R["camp_group"] = camp

        # ---- Click the Hot Rocks row -> world popover ----
        clicked = page.evaluate("""(name) => {
            const row = Array.from(document.querySelectorAll('#poiList .poi-row'))
                .find(r => ((r.querySelector('.poi-row-name')||{}).textContent||'').trim() === name);
            if (row) { row.click(); return true; }
            return false;
        }""", NAME)
        R["row_clicked"] = clicked
        if clicked:
            page.wait_for_selector(".maplibregl-popup .poi-popup-title", timeout=12000)
            page.wait_for_timeout(400)
            R["popover"] = page.evaluate("""() => {
                const pop = document.querySelector('.maplibregl-popup');
                if (!pop) return null;
                return {
                    title: (pop.querySelector('.poi-popup-title')||{}).textContent || '',
                    subtitle: (pop.querySelector('.poi-popup-subtitle')||{}).textContent || '',
                    dt_labels: Array.from(pop.querySelectorAll('.poi-popup-meta dt')).map(d => d.textContent.trim())
                };
            }""")
            log("popover: " + json.dumps(R["popover"]))

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    camp = R.get("camp_group")
    pop = R.get("popover") or {}
    camp_names = [r["name"].strip() for r in camp["rows"]] if camp else []
    dt_lower = {d.lower() for d in pop.get("dt_labels", [])}
    checks = {
        "only Hot Rocks waypoint is highlighted in source": R["highlighted_waypoints"] == [NAME],
        "'Camp POIs' group rendered in POI list": camp is not None,
        "Camp POIs group contains Hot Rocks Comp Pad": NAME in camp_names,
        "Camp POIs group has EXACTLY the 1 starred pad": camp_names == [NAME],
        "Camp POIs count badge reads 1": (camp or {}).get("count") == "1",
        "Hot Rocks row shows its blurb (no kind/status chips)": bool(camp) and camp["rows"][0]["subtitle"].startswith("Purpose-built") and camp["rows"][0]["meta_chips"] == 0,
        "row click opened the world popover": R.get("row_clicked") is True and bool(pop.get("title")),
        "popover title is Hot Rocks Comp Pad": pop.get("title", "").strip() == NAME,
        "popover shows the description blurb": pop.get("subtitle", "").startswith("Purpose-built"),
        "popover has no Kind/Status/Source meta": dt_lower.issubset({"caveat"}),
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
