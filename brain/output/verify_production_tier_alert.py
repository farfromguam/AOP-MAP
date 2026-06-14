#!/usr/bin/env python3
"""Verify by observation (real running viewer on :8001) of the task-4 production
data-tier alert: bronze/silver data live in production warns the developer in the
console; gold layers stay quiet; nothing is hidden (no-limiting-code).
Run: python3 brain/output/verify_production_tier_alert.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"


def main():
    warnings, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_context(viewport={"width": 1200, "height": 800}).new_page()
        page.set_default_timeout(8000)
        page.on("console", lambda m: (warnings if m.type == "warning" else errors).append(m.text)
                if m.type in ("warning", "error") else None)
        page.goto(URL, wait_until="load")
        page.wait_for_function(
            "() => window.AOPViewer && window.AOPViewer.map && window.AOPViewer.map.isStyleLoaded()"
            " && window.AOPViewer.map.getSource('fema-buildings')", timeout=45000)
        page.wait_for_timeout(3000)  # let all production sources load + audit run
        alert = next((w for w in warnings if "PRODUCTION DATA TIER ALERT" in w), None)
        print("=== ALERT TEXT ===")
        print(alert or "(no alert fired)")
        print("=== other warnings ===", [w[:80] for w in warnings if w is not alert])
        real_errors = [e for e in errors if "favicon" not in e.lower()]
        print("=== console errors ===", real_errors)
        try:
            browser.close()
        except Exception:
            pass

    a = alert or ""
    checks = {
        "Alert fired": bool(alert),
        "Flags Park buildings bronze (Shower House)": "Park buildings" in a and "bronze" in a,
        "Flags Visitor context callouts (silver)": "Visitor context callouts" in a,
        "Flags Publishable layers (silver)": "Publishable layers" in a,
        "GOLD quiet: Land cover NOT flagged": "Land cover" not in a,
        "GOLD quiet: Lidar contours NOT flagged": "Lidar contours" not in a,
        "GOLD quiet: Hydrography NOT flagged": "Hydrography" not in a,
        "GOLD quiet: Roads NOT flagged": "Roads" not in a,
        "GOLD quiet: AOP trail network NOT flagged": "AOP trail network" not in a,
        "GOLD quiet: Camp waypoints NOT flagged": "Camp waypoints" not in a,
        "No console errors": len(real_errors) == 0,
    }
    print("\n--- CHECKS ---", flush=True)
    allok = True
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}", flush=True)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}", flush=True)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
