#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that the new "Gravity Gauntlet"
race-course waypoint — sourced from brain/import/Wpt_5-16-26-144753_race_driver_position.gpx
— is now (a) a pin on the map and (b) a starred row in the reader's POI list, tagged
#gravity-gauntlet.

User: "add this to the map as a pin and star it to make it into the poi list as
#gravity-gauntlet make sure it ends up in the correct gold data source." Data-only change:
gold_aop_waypoints_traced.geojson gains one feature with highlight:true +
location_tag:"#gravity-gauntlet". The viewer wiring (aop-waypoints pin layer + the
'Camp POIs' ★-group) already exists from the Hot Rocks pass, so no JS change.

Camp POIs is ★-gated, so the group now holds EXACTLY the two starred pads
(Hot Rocks Comp Pad + Gravity Gauntlet). Pins are gated to Park/Topo (user 2026-06-14),
so the test selects the Park preset before reading rendered pins. Drives the real DOM:
opens the POI tab, reads the rendered group + rows, clicks the Gravity Gauntlet row,
reads the live popover.

Run: python3 brain/output/verify_gravity_gauntlet_in_poi_list.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
NAME = "Gravity Gauntlet"
TAG = "#gravity-gauntlet"


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

        # ---- The live waypoints source: both pads highlighted, GG carries the tag ----
        R["highlighted_waypoints"] = page.evaluate("""() => {
            const d = window.AOPViewer.map.getSource('aop-waypoints').serialize().data;
            return (d.features || []).filter(f => (f.properties||{}).highlight === true)
                                     .map(f => f.properties.name);
        }""")
        R["gg_feature"] = page.evaluate("""(tag) => {
            const d = window.AOPViewer.map.getSource('aop-waypoints').serialize().data;
            const f = (d.features || []).find(f => (f.properties||{}).location_tag === tag);
            if (!f) return null;
            return { name: f.properties.name, tag: f.properties.location_tag,
                     highlight: f.properties.highlight, coords: f.geometry.coordinates };
        }""", TAG)

        # ---- Select Park preset so pins render, then confirm GG is a drawn pin ----
        page.evaluate("""() => {
            const b = document.querySelector('[data-preset="park"]');
            if (b) b.click();
        }""")
        page.wait_for_timeout(800)
        R["pin_layer_visible"] = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            return m.getLayoutProperty('aop-waypoints', 'visibility') !== 'none';
        }""")
        R["gg_rendered_pin"] = page.evaluate("""(name) => {
            const m = window.AOPViewer.map;
            const feats = m.queryRenderedFeatures({ layers: ['aop-waypoints'] });
            return feats.some(f => (f.properties||{}).name === name);
        }""", NAME)

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

        # ---- Click the Gravity Gauntlet row -> world popover ----
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
    gg = R.get("gg_feature") or {}
    camp_names = sorted(r["name"].strip() for r in camp["rows"]) if camp else []
    dt_lower = {d.lower() for d in pop.get("dt_labels", [])}
    blurb_start = "The Gravity Gauntlet"
    checks = {
        "Gravity Gauntlet is highlighted in the live waypoints source":
            NAME in R.get("highlighted_waypoints", []),
        "Both pads (Hot Rocks + Gravity Gauntlet) highlighted, nothing else":
            sorted(R.get("highlighted_waypoints", [])) == ["Gravity Gauntlet", "Hot Rocks Comp Pad"],
        "GG feature carries location_tag #gravity-gauntlet + highlight:true":
            gg.get("tag") == TAG and gg.get("highlight") is True,
        "GG coords match the GPX (-85.7515, 35.09191)":
            gg.get("coords") == [-85.7515, 35.09191],
        "pin layer visible on Park preset": R.get("pin_layer_visible") is True,
        "Gravity Gauntlet renders as a pin on the map": R.get("gg_rendered_pin") is True,
        "'Camp POIs' group rendered in POI list": camp is not None,
        "Camp POIs group contains Gravity Gauntlet": NAME in camp_names,
        "Camp POIs holds exactly the two starred pads":
            camp_names == ["Gravity Gauntlet", "Hot Rocks Comp Pad"],
        "Camp POIs count badge reads 2": (camp or {}).get("count") == "2",
        "GG row shows its blurb (no kind/status chips)":
            bool(camp) and any(r["name"].strip() == NAME and r["subtitle"].startswith(blurb_start)
                               and r["meta_chips"] == 0 for r in camp["rows"]),
        "row click opened the world popover": R.get("row_clicked") is True and bool(pop.get("title")),
        "popover title is Gravity Gauntlet": pop.get("title", "").strip() == NAME,
        "popover shows the description blurb": pop.get("subtitle", "").startswith(blurb_start),
        "popover has no Kind/Status/Source meta": dt_lower.issubset({"caveat"}),
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
