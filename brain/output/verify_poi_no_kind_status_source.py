#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) that Kind / Status /
Source are gone from BOTH the POI list and the world (feature) popovers.

User (2026-06-14): the POI tab shows Kind and Status as visible chips; we don't
need those in the POI list, and we don't need Kind/Status in the world popovers
either — and the world popover also carries a third field, Source, that also has
to go. Kind/Status/Source are provenance / dev-artifact metadata, not visitor copy.

Fix:
  - feature_display.js popupHtml: dropped the Kind/Status/Source <dt>/<dd> lines
    (the ONE shared popover renderer); only an author-facing Caveat may remain.
  - viewer_core.js renderPoiTab (reader): dropped the kind/status meta chips and
    the "kind · status" subtitle fallback; list shows blurb (then revisit note).
  - main.js renderPoiTab (editor): same — dropped kind/status chips and the
    "kind · source" subtitle fallback; kept the "info needed — revisit" chip.

This drives the REAL running reader: opens the POI tab, reads the rendered rows,
then clicks a row to open the world popover and reads its meta. No re-derivation.

Run: python3 brain/output/verify_poi_no_kind_status_source.py
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
BANNED = {"kind", "status", "source"}


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
            "() => window.AOPViewer && window.AOPViewer.map && window.AOPViewer.map.isStyleLoaded()",
            timeout=45000)
        page.wait_for_timeout(1500)

        # ---- Open the POI tab and wait for rows ----
        page.click("#leftTabPoi")
        page.wait_for_function(
            "() => document.querySelectorAll('#poiList .poi-row').length > 0", timeout=20000)
        page.wait_for_timeout(400)

        # ---- Read the rendered POI list ----
        R["poi_list"] = page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('#poiList .poi-row'));
            return {
                count: rows.length,
                // any .poi-row-meta span that is NOT the revisit placeholder
                kind_status_chip_count: rows.reduce((n, r) => n + Array.from(
                    r.querySelectorAll('.poi-row-meta span')).filter(
                        s => !s.classList.contains('poi-placeholder-chip')).length, 0),
                // subtitles must not contain the "x · y" kind/status/source pattern
                subtitles_with_dot_sep: rows.map(r => (r.querySelector('.poi-row-subtitle')||{}).textContent || '')
                    .filter(t => t.includes(' · ')),
                sample: rows.slice(0, 4).map(r => ({
                    name: (r.querySelector('.poi-row-name')||{}).textContent || '',
                    subtitle: (r.querySelector('.poi-row-subtitle')||{}).textContent || ''
                }))
            };
        }""")
        log(f"poi list: {json.dumps(R['poi_list'])}")

        # ---- Click the first POI row to open the world popover ----
        page.evaluate("() => document.querySelector('#poiList .poi-row').click()")
        page.wait_for_selector(".maplibregl-popup .poi-popup-title", timeout=12000)
        page.wait_for_timeout(400)

        # ---- Read the world popover meta ----
        R["popover"] = page.evaluate("""() => {
            const pop = document.querySelector('.maplibregl-popup');
            if (!pop) return null;
            const dts = Array.from(pop.querySelectorAll('.poi-popup-meta dt')).map(d => d.textContent.trim());
            return {
                title: (pop.querySelector('.poi-popup-title')||{}).textContent || '',
                meta_dt_labels: dts,
                html_has_Kind: /<dt>\\s*Kind\\s*<\\/dt>/.test(pop.innerHTML),
                html_has_Status: /<dt>\\s*Status\\s*<\\/dt>/.test(pop.innerHTML),
                html_has_Source: /<dt>\\s*Source\\s*<\\/dt>/.test(pop.innerHTML)
            };
        }""")
        log(f"popover: {json.dumps(R['popover'])}")

        real_errors = [e for e in errors if "favicon" not in e.lower()]
        R["console_errors"] = real_errors
        rc = print_verdict(R, real_errors)
        try:
            ctx.close(); browser.close()
        except Exception:
            pass
    return rc


def print_verdict(R, real_errors):
    lst = R["poi_list"]
    pop = R["popover"] or {}
    dt_lower = {d.lower() for d in pop.get("meta_dt_labels", [])}
    checks = {
        "POI list rendered rows": lst["count"] > 0,
        "POI list has NO kind/status chips": lst["kind_status_chip_count"] == 0,
        "POI list has NO 'x · y' kind/status subtitle": len(lst["subtitles_with_dot_sep"]) == 0,
        "world popover opened (has title)": bool(pop.get("title")),
        "popover has NO 'Kind' meta": not pop.get("html_has_Kind") and "kind" not in dt_lower,
        "popover has NO 'Status' meta": not pop.get("html_has_Status") and "status" not in dt_lower,
        "popover has NO 'Source' meta": not pop.get("html_has_Source") and "source" not in dt_lower,
        "any remaining popover meta is only Caveat": dt_lower.issubset({"caveat"}),
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
