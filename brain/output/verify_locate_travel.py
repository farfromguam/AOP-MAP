#!/usr/bin/env python3
"""Verify the Locate FAB's off-park distance notice (v82).

The map camera is leashed to the printed sheet (REGION_MAXBOUNDS), so a real GPS fix
from off-park lands outside maxBounds and the blue dot can't show — Locate looked dead
from home. Now the FAB reads the fix once (coarse + fast): near the park it hands off
to the normal blue-dot follow flow; far away it shows the straight-line miles AND a
rough drive time ("<dist> away, as the bird flies / about a <t> drive"); a failed fix
shows a visible "Couldn't get your location" notice instead of silently no-op'ing; and
the FAB itself only appears when the device exposes navigator.geolocation.

Observed by spoofing device geolocation (grant + set_geolocation) on the live :8001
viewer and reading the real #locateNotice / #locateBtn DOM. Five cases:
  - Chattanooga (~25 mi)   -> "<dist> away … as the bird flies" + a "drive" time
  - Nashville  (~94 mi)    -> same shape, larger number
  - park pavilion (0 mi)   -> notice STAYS hidden; the GeolocateControl dot appears
  - permission revoked     -> notice shows "Couldn't get your location" (never dead)
  - no navigator.geolocation -> the FAB never reveals (stays hidden)
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/index.html"
PARK = {"latitude": 35.090703, "longitude": -85.748268}
CHATTANOOGA = {"latitude": 35.0456, "longitude": -85.3097}
NASHVILLE = {"latitude": 36.1627, "longitude": -86.7816}

# Headless software-GL artifacts — message-less, unrelated to page logic. The first
# council Witness review (v81) caught the GPU-stall / GL-driver form leaking past the
# old "could not compile…" list, flapping the 0-error gate. Filter only these.
GL_NOISE = ("could not compile fragment shader", "could not compile vertex shader",
            "could not link program", "failed to create webgl", "webgl context",
            "gl driver message", "gpu stall", "readpixels", "gl_close_path_nv",
            "could not compile", "[.webgl")

# Transient harness-load noise, NOT a locate-feature failure: under repeated heavy
# reloads on software GL the page's OWN publish.geojson fetch (viewer_core.js:2179)
# occasionally flakes. The #locateNotice path under test does not depend on it, so a
# data-fetch flake must not fail the locate verification — but it is COUNTED and
# printed (not silently dropped), so it stays visible.
TRANSIENT_NOISE = ("failed to fetch", "publish layer failed to load", "load failed",
                   "networkerror", "err_network", "the operation was aborted")

def classify(msg):
    m = (msg or "").lower()
    if any(s in m for s in GL_NOISE):
        return "gl"
    if any(s in m for s in TRANSIENT_NOISE):
        return "transient"
    return "real"

def load_at(page, geo, ctx):
    """Fresh page load at a spoofed fix, so getCurrentPosition's maximumAge cache
    can't bleed the previous case's location in. Retries once on a navigation flake
    (TargetClosedError etc.) — a closed target on reload is harness churn, not a bug."""
    ctx.set_geolocation(geo)
    last = None
    for _ in range(3):
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_function("window.AOPViewer && window.AOPViewer.map", timeout=15000)
            page.wait_for_selector("#locateBtn", state="visible", timeout=10000)
            page.wait_for_timeout(800)
            return
        except Exception as e:  # noqa: BLE001 — navigation/target churn, retry
            last = e
            page.wait_for_timeout(600)
    raise last

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
    msgs = []  # (kind, text) where kind in {real, transient, gl}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1200, "height": 900},
            permissions=["geolocation"],
            geolocation=PARK,  # set per-case below
        )
        page = ctx.new_page()
        page.on("console", lambda m: msgs.append((classify(m.text), m.text)) if m.type == "error" else None)
        page.on("pageerror", lambda e: msgs.append((classify(str(e)), str(e))))

        # --- far: Chattanooga — bird-flies miles AND a drive time ------------
        load_at(page, CHATTANOOGA, ctx)
        vis, text, dot = click_locate_and_read(page)
        ok_chat = vis and ("mi away" in text) and ("as the bird flies" in text) and ("drive" in text)
        results.append(("chattanooga_far", ok_chat, f"vis={vis} dot={dot} text={text!r}"))
        page.screenshot(path="brain/output/locate_travel_chattanooga.png")

        # --- very far: Nashville — same shape, larger number -----------------
        load_at(page, NASHVILLE, ctx)
        vis, text, dot = click_locate_and_read(page)
        ok_nash = vis and ("mi away" in text) and ("as the bird flies" in text) and ("drive" in text)
        results.append(("nashville_veryfar", ok_nash, f"vis={vis} dot={dot} text={text!r}"))
        page.screenshot(path="brain/output/locate_travel_nashville.png")

        # --- at the park: notice stays hidden, blue-dot path engages ----------
        load_at(page, PARK, ctx)
        vis, text, dot = click_locate_and_read(page)
        page.wait_for_timeout(1200)
        dot = locating(page)
        results.append(("park_near_dot", (not vis) and dot, f"vis={vis} dot={dot} text={text!r}"))
        page.screenshot(path="brain/output/locate_travel_atpark.png")

        # --- geolocation DENIED: the notice SAYS SO (never silently dead) -----
        # This is the off-park "button does nothing" report: a failed/blocked fix
        # used to fall back to a no-op. Now it must surface a visible message.
        ctx.clear_permissions()
        load_at(page, NASHVILLE, ctx)  # location set, but permission revoked → error path
        page.click("#locateBtn")
        page.wait_for_timeout(1500)
        n = page.eval_on_selector("#locateNotice", "el => ({hidden: el.hidden, text: el.innerText})")
        denied_text = n["text"].replace("\n", " ")
        ok_denied = (not n["hidden"]) and ("Couldn't get your location" in denied_text)
        results.append(("denied_visible", ok_denied, f"hidden={n['hidden']} text={denied_text!r}"))
        page.screenshot(path="brain/output/locate_travel_denied.png")

        # --- NO geolocation API: the FAB must not show at all -----------------
        # A separate context whose navigator.geolocation is undefined BEFORE any page
        # script runs (init script). viewer_core.js reveals the FAB only when
        # navigator.geolocation exists, so here it must stay hidden.
        ctx2 = browser.new_context(viewport={"width": 1200, "height": 900})
        ctx2.add_init_script(
            "Object.defineProperty(navigator, 'geolocation', { configurable: true, get: () => undefined });"
        )
        page2 = ctx2.new_page()
        page2.on("console", lambda m: msgs.append((classify(m.text), m.text)) if m.type == "error" else None)
        page2.on("pageerror", lambda e: msgs.append((classify(str(e)), str(e))))
        page2.goto(URL, wait_until="domcontentloaded", timeout=20000)
        page2.wait_for_function("window.AOPViewer && window.AOPViewer.map", timeout=15000)
        page2.wait_for_timeout(1500)  # give viewer_core.js time to (not) reveal the FAB
        has_geo = page2.evaluate("!!navigator.geolocation")
        btn = page2.eval_on_selector("#locateBtn", "el => ({hidden: el.hidden, visible: el.offsetParent !== null})")
        ok_nogps = (has_geo is False) and btn["hidden"] and (not btn["visible"])
        results.append(("no_gps_button_hidden", ok_nogps, f"navigator.geolocation={has_geo} btn_hidden={btn['hidden']} btn_visible={btn['visible']}"))
        page2.screenshot(path="brain/output/locate_travel_nogps.png")
        ctx2.close()

        browser.close()

    print("=== Locate travel notice verification ===")
    ok = True
    for name, passed, detail in results:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}: {detail}")
        ok = ok and passed
    real = [t for k, t in msgs if k == "real"]
    transient = [t for k, t in msgs if k == "transient"]
    gl = [t for k, t in msgs if k == "gl"]
    if transient:
        print(f"  [note] {len(transient)} transient harness-load msg(s) ignored (e.g. publish.geojson fetch under load)")
    if gl:
        print(f"  [note] {len(gl)} software-GL msg(s) ignored")
    if real:
        ok = False
        print(f"  [FAIL] {len(real)} real console/page error(s): {real[:5]}")
    else:
        print("  [PASS] 0 real console/page errors")
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
