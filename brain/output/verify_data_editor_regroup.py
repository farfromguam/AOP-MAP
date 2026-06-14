#!/usr/bin/env python3
"""Verify by observation: data_editor.html (the data editor page) lists the
renamed data sources GROUPED by medallion tier (<optgroup> Gold/Silver/Bronze/
Delete), with tier-prefixed filenames. Run on :8001."""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/data_editor.html"


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_context(viewport={"width": 1200, "height": 800}).new_page()
        pg.set_default_timeout(8000)
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto(URL, wait_until="load")
        pg.wait_for_selector("#fileSel optgroup", state="attached", timeout=20000)
        pg.wait_for_timeout(800)
        groups = pg.evaluate("""() => [...document.querySelectorAll('#fileSel optgroup')].map(g => ({
            label: g.label,
            options: [...g.querySelectorAll('option')].map(o => o.value)
        }))""")
        try:
            b.close()
        except Exception:
            pass

    real_errors = [e for e in errors if "favicon" not in e.lower()]
    print("=== TIER GROUPS in the data-editor picker ===")
    for g in groups:
        print(f"  [{g['label']}] {len(g['options'])} files: {', '.join(g['options'][:3])}{'...' if len(g['options'])>3 else ''}")
    print("=== console errors ===", real_errors)

    labels = [g["label"] for g in groups]
    allfiles = [f for g in groups for f in g["options"]]
    checks = {
        "Picker is grouped (has optgroups)": len(groups) >= 2,
        "Gold group present": any("Gold" in l for l in labels),
        "Silver group present": any("Silver" in l for l in labels),
        "Bronze group present": any("Bronze" in l for l in labels),
        "Files are tier-prefixed": all(f.startswith(("gold_", "silver_", "bronze_", "delete_")) for f in allfiles) and len(allfiles) > 0,
        "gold_aop_trail_network present": "gold_aop_trail_network.geojson" in allfiles,
        "bronze_aop_cemeteries present": "bronze_aop_cemeteries.geojson" in allfiles,
        "silver_publish present": "silver_publish.geojson" in allfiles,
        "No console errors": len(real_errors) == 0,
    }
    print("\n--- CHECKS ---", flush=True)
    ok = True
    for n, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {n}", flush=True)
        ok = ok and v
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
