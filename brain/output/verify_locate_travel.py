#!/usr/bin/env python3
"""Verify the Locate FAB's off-park travel notice (v80).

The map camera is leashed to the printed sheet (REGION_MAXBOUNDS), so a real GPS fix
from off-park lands outside maxBounds and the blue dot can't show — Locate looked dead
from home. Now the FAB reads the fix once: near the park it hands off to the normal
blue-dot follow flow; far away it shows a "<dist> to the park — <drive>" notice.

Observed by spoofing device geolocation (grant + set_geolocation) on the live :8001
viewer and reading the real #locateNotice DOM. Three fixes:
  - Chattanooga (~25 mi)   -> notice shows miles + a "min drive"
  - Nashville  (~94 mi)    -> notice shows miles + an "hr drive"
  - park pavilion (0 mi)   -> notice STAYS hidden; the GeolocateControl dot appears
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/index.html"
PARK = {"latitude": 35.090703, "longitude": -85.748268}
CHATTANOOGA = {"latitude": 35.0456, "longitude": -85.3097}
NASHVILLE = {"latitude": 36.1627, "longitude": -86.7816}

GL_NOISE = ("could not compile fragment shader", "could not compile vertex shader",
            "could not link program", "failed to create webgl", "webgl context")

def is_gl_noise(msg):
    m = (msg or "").lower()
    return any(s in m for s in GL_NOISE)

def load_at(page, geo, ctx):
    """Fresh page load at a spoofed fix, so getCurrentPosition's maximumAge cache
    (30 s, correct for the app) can't bleed the previous case's location in."""
    ctx.set_geolocation(geo)
    page.goto(URL)
    page.wait_for_function("window.AOPViewer && window.AOPViewer.map", timeout=15000)
    page.wait_for_timeout(800)

def locating(page):
    """The blue-dot path engaged: GeolocateControl is tracking (button lit) and/or
    the user-location marker exists."""
    active = page.eval_on_selector("#locateBtn", "el => el.classList.contains('active')")
    dot = page.query_selector(".maplibregl-user-location-dot, .maplibregl-user-location-accuracy-circle") is not None
    return active or dot

def click_locate_and_read(page):
    """Click the FAB, wait for the one-shot getCurrentPosition branch to settle,
    return (notice_visible, notice_text, dot_engaged)."""
    page.click("#locateBtn")
    page.wait_for_timeout(1800)
    notice = page.eval_on_selector(
        "#locateNotice",
        "el => ({hidden: el.hidden, text: el.innerText})",
    )
    return (not notice["hidden"], notice["text"].replace("\n", " "), locating(page))

def main():
    results = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1200, "height": 900},
            permissions=["geolocation"],
            geolocation=PARK,  # set per-case below
        )
        page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" and not is_gl_noise(m.text) else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        # --- far: Chattanooga -------------------------------------------------
        load_at(page, CHATTANOOGA, ctx)
        vis, text, dot = click_locate_and_read(page)
        results.append(("chattanooga_far", vis and ("mi to the park" in text) and ("min drive" in text), f"vis={vis} dot={dot} text={text!r}"))
        page.screenshot(path="brain/output/locate_travel_chattanooga.png")

        # --- very far: Nashville ---------------------------------------------
        load_at(page, NASHVILLE, ctx)
        vis, text, dot = click_locate_and_read(page)
        results.append(("nashville_veryfar", vis and ("mi to the park" in text) and (" hr" in text) and ("drive" in text), f"vis={vis} dot={dot} text={text!r}"))
        page.screenshot(path="brain/output/locate_travel_nashville.png")

        # --- at the park: notice stays hidden, blue-dot path engages ----------
        load_at(page, PARK, ctx)
        vis, text, dot = click_locate_and_read(page)
        page.wait_for_timeout(1200)
        dot = locating(page)
        results.append(("park_near_dot", (not vis) and dot, f"vis={vis} dot={dot} text={text!r}"))
        page.screenshot(path="brain/output/locate_travel_atpark.png")

        browser.close()

    print("=== Locate travel notice verification ===")
    ok = True
    for name, passed, detail in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {detail}")
        ok = ok and passed
    if errors:
        ok = False
        print(f"  [FAIL] {len(errors)} console/page error(s): {errors[:5]}")
    else:
        print("  [PASS] 0 non-GL console errors")
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
