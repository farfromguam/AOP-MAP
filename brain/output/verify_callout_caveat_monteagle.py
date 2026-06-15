#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) two region-callout changes.

User (2026-06-15):
  1. "review the region callouts and get rid of caveat. - people understand what
     they are getting"  -> the planning-estimate "Caveat" line (sourced from the
     callouts' drive_time_note via feature_display.js) must be GONE from BOTH
     region-callout popovers (South Pittsburg / Kimball AND Monteagle).
  2. "monteagle seems to duplicate some things ... extend as appropriate. it seems
     terser than it has been" + "clicking the poi goes to the poi with more
     information. its redundant to have the exact data in two places" -> the
     Monteagle popup/POI description must be the NEW, richer copy and must NOT
     simply restate the on-map label (no '~30 min northwest via I-24' echo).

Fix under test:
  - feature_display.js: dropped drive_time_note from the `caveat` pick-chain, so
    the planning note no longer surfaces as a visitor "Caveat".
  - gold_aop_visitor_context_callouts.geojson + aop_poi_index.json: new Monteagle
    description (richer; names venues; no drive-time/direction echo of the label).

Drives the REAL running reader: opens the POI tab, reads the two visitor-support
rows, then clicks the callout polygon on the map to open each popover and reads
its rendered HTML. No re-derivation.

Run: python3 brain/output/verify_callout_caveat_monteagle.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
NEW_MONTEAGLE = ("The plateau cluster up the mountain — a second base after the "
                 "South Pittsburg / Kimball run. Lodging at Smokehouse Lodge & Cabins "
                 "or the Monteagle hotels; food at the Mountain Goat Market, the "
                 "Smokehouse Restaurant, and High Point. Farther out, but a solid "
                 "fallback when the closer side books up for the event.")
OLD_ECHO = "~30 min northwest via I-24"          # the terse/duplicative phrasing, must be GONE
LABEL_LINES = ["MONTEAGLE", "~30 min", "I-24"]   # the on-map label teaser (unchanged)


def log(m):
    print(m, flush=True)


def open_callout_popover(page, name):
    """Click the callout's POI-tab row (deterministic) -> world popover via popupHtml."""
    page.evaluate("""(nm) => {
        const rows = Array.from(document.querySelectorAll('#poiList .poi-row'));
        const r = rows.find(x => ((x.querySelector('.poi-row-name')||{}).textContent||'').trim() === nm);
        if (r) r.click();
    }""", name)
    page.wait_for_selector(".maplibregl-popup .poi-popup-title", timeout=12000)
    page.wait_for_timeout(350)
    return page.evaluate("""() => {
        const pop = document.querySelector('.maplibregl-popup');
        if (!pop) return null;
        const dts = Array.from(pop.querySelectorAll('.poi-popup-meta dt')).map(d => d.textContent.trim());
        return {
            title: (pop.querySelector('.poi-popup-title')||{}).textContent || '',
            blurb: (pop.querySelector('.poi-popup-subtitle')||{}).textContent || '',
            meta_dt_labels: dts,
            html_has_Caveat: /<dt>\\s*Caveat\\s*<\\/dt>/.test(pop.innerHTML),
            innerHTML: pop.innerHTML
        };
    }""")


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
            "() => window.AOPViewer && window.AOPViewer.map && window.AOPViewer.map.isStyleLoaded()",
            timeout=45000)
        page.wait_for_timeout(1500)

        # The on-map label text actually served for the Monteagle callout feature.
        R["map_label"] = page.evaluate("""async () => {
            const r = await fetch('./data/gold_aop_visitor_context_callouts.geojson');
            const data = await r.json();
            const f = data.features.find(x => (x.properties||{}).name === 'Monteagle plateau services');
            return f ? (f.properties.label || '') : null;
        }""")
        log(f"map_label: {json.dumps(R['map_label'])}")

        # Open POI tab and wait for rows.
        page.click("#leftTabPoi")
        page.wait_for_function(
            "() => document.querySelectorAll('#poiList .poi-row').length > 0", timeout=20000)
        page.wait_for_timeout(400)

        R["monteagle"] = open_callout_popover(page, "Monteagle plateau services")
        log(f"monteagle popover: {json.dumps({k: v for k, v in R['monteagle'].items() if k != 'innerHTML'})}")
        # close popups before opening the next
        page.evaluate("() => document.querySelectorAll('.maplibregl-popup-close-button').forEach(b => b.click())")
        page.wait_for_timeout(250)

        R["south_pittsburg"] = open_callout_popover(page, "South Pittsburg / Kimball supply run")
        log(f"south pittsburg popover: {json.dumps({k: v for k, v in R['south_pittsburg'].items() if k != 'innerHTML'})}")

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    mt = R["monteagle"] or {}
    sp = R["south_pittsburg"] or {}
    label = R["map_label"] or ""
    mt_dt = {d.lower() for d in mt.get("meta_dt_labels", [])}
    sp_dt = {d.lower() for d in sp.get("meta_dt_labels", [])}
    checks = {
        "Monteagle popover opened (has title)": mt.get("title") == "Monteagle plateau services",
        "Monteagle popover has NO 'Caveat' meta": not mt.get("html_has_Caveat") and "caveat" not in mt_dt,
        "Monteagle blurb is the NEW richer copy": mt.get("blurb", "").strip() == NEW_MONTEAGLE,
        "Monteagle blurb does NOT echo the label drive-time": OLD_ECHO not in mt.get("blurb", ""),
        "Monteagle blurb names venues (more info than label)":
            all(v in mt.get("blurb", "") for v in ["Smokehouse Lodge", "Mountain Goat Market", "High Point"]),
        "Monteagle popover has NO meta list at all (caveat was the only one)": len(mt_dt) == 0,
        "on-map label teaser still terse (direction/time/I-24)": all(s in label for s in LABEL_LINES),
        "South Pittsburg popover opened": sp.get("title") == "South Pittsburg / Kimball supply run",
        "South Pittsburg popover has NO 'Caveat' meta": not sp.get("html_has_Caveat") and "caveat" not in sp_dt,
        "No console errors": len(real_errors) == 0,
    }
    print(json.dumps({k: v for k, v in R.items()
                      if k not in ("monteagle", "south_pittsburg")}, indent=2), flush=True)
    print("monteagle.blurb =", json.dumps(mt.get("blurb", "")), flush=True)
    print("south_pittsburg.meta_dt =", json.dumps(sp.get("meta_dt_labels", [])), flush=True)
    print("\n--- CHECKS ---", flush=True)
    allok = True
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}", flush=True)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}", flush=True)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
