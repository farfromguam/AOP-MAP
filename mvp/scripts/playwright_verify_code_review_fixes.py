#!/usr/bin/env python3
"""Smoke verifier for the 2026-05-31 code-review fix batch.

Covers the changed code paths in website/index.html + sw.js:
  - Zero console errors / pageerrors on load (catches any parse breakage from
    the bindPopup central-escape strip, the nested-template row id, the
    hotspot-centroid rewrite, the withZoomStops guard, etc.).
  - renderAbout runs and populates #aboutInfoPanel (About href-gate path).
  - Every preset switches clean (applyPreset -> withZoomStops paint apply).
  - A calendar pick opens exactly one popup with no double-escaped entities
    (M1 closeAllMapPopups + M2 central title escape canary).

Run: serve website/ on :8001 first, then `python3 this_file.py`.
Exit 0 = PASS.
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8001/index.html?edit=1"
DOUBLE_ESCAPE_CANARIES = ["&amp;", "&#039;", "&lt;", "&gt;", "&quot;"]


def main():
    errors = []        # console.error + pageerror -> hard fail
    warnings = []      # console.warning -> informational
    results = []       # (label, ok, detail)

    def record(label, ok, detail=""):
        results.append((label, ok, detail))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1100, "height": 850})

        def on_console(msg):
            if msg.type == "error":
                errors.append(msg.text)
            elif msg.type == "warning":
                warnings.append(msg.text)

        page.on("console", on_console)
        page.on("pageerror", lambda exc: errors.append(f"PAGEERROR: {exc}"))

        page.goto(BASE, wait_until="domcontentloaded")
        # Map + data settle.
        page.wait_for_selector(".maplibregl-canvas", timeout=20000)
        page.wait_for_timeout(4500)

        # 1) Map canvas rendered.
        record("map canvas present", page.locator(".maplibregl-canvas").count() > 0)

        # 1b) Service worker registers + activates cleanly (catches any sw.js
        #     parse/registration failure from the H4/L8 cache-strategy edits).
        try:
            sw = page.evaluate(
                """async () => {
                    if (!('serviceWorker' in navigator)) return {ok:false, why:'no SW API'};
                    const reg = await navigator.serviceWorker.ready;
                    const w = reg.active;
                    return {ok: !!w, state: w && w.state};
                }""")
            record("service worker active", bool(sw.get("ok")), f"state={sw.get('state')}")
        except Exception as e:
            record("service worker active", False, str(e))

        # 2) Calendar pick -> exactly one popup, no double-escaped entities.
        #    The event calendar lives in the default-active Events tab, so do
        #    this BEFORE switching to About.
        try:
            page.click("#leftTabEvents", timeout=4000)
            page.wait_for_timeout(500)
            rows = page.locator(".calendar-row")
            rows.first.wait_for(state="visible", timeout=6000)
            if rows.count() > 0:
                rows.first.click(timeout=5000)
                page.wait_for_timeout(1600)
                popups = page.locator(".maplibregl-popup")
                npop = popups.count()
                html = popups.first.inner_html() if npop else ""
                doubled = [c for c in DOUBLE_ESCAPE_CANARIES if c in html]
                record("calendar pick opens single popup", npop == 1, f"{npop} popups")
                record("popup has no double-escaped entities", not doubled, str(doubled))
                # Pick a second row -> still exactly one popup (closeAllMapPopups).
                if rows.count() > 1:
                    rows.nth(1).click(timeout=5000)
                    page.wait_for_timeout(1300)
                    record("second pick replaces popup (no stacking)",
                           page.locator(".maplibregl-popup").count() == 1,
                           f"{page.locator('.maplibregl-popup').count()} popups")
            else:
                record("calendar rows present", False, "0 rows")
        except Exception as e:
            record("calendar/popup path", False, str(e))

        # 3) About tab -> renderAbout populates the panel.
        try:
            page.click("#leftTabAbout", timeout=5000)
            page.wait_for_timeout(800)
            about_children = page.eval_on_selector(
                "#aboutInfoPanel", "el => el.children.length")
            record("About panel populated (renderAbout)", about_children > 0,
                   f"{about_children} child nodes")
        except Exception as e:
            record("About panel populated (renderAbout)", False, str(e))

        # 4) Presets switch clean (withZoomStops runs during paint apply).
        for pid in ("presetTopo", "presetTrace", "presetSatellite", "presetPark"):
            before = len(errors)
            try:
                page.click(f"#{pid}", timeout=5000)
                page.wait_for_timeout(1200)
                record(f"preset {pid} no new errors", len(errors) == before)
            except Exception as e:
                record(f"preset {pid} clicked", False, str(e))

        browser.close()

    # ---- report ----
    print("\n=== code-review fix smoke ===")
    all_ok = True
    for label, ok, detail in results:
        flag = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  [{flag}] {label}" + (f"  ({detail})" if detail else ""))

    print(f"\nconsole errors / pageerrors: {len(errors)}")
    for e in errors[:15]:
        print(f"  ! {e}")
    print(f"console warnings: {len(warnings)} (informational)")
    for w in warnings[:8]:
        print(f"  ~ {w}")

    if errors:
        all_ok = False

    print("\nRESULT:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
