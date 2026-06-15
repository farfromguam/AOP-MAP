#!/usr/bin/env python3
"""Observe the FULL 3D camera in the viewer (viewer_core.js v98): the user asked to
"enable the 3d features" after only being able to pivot (rotate) around a center
point. So pitch is no longer button-only — every camera gesture is live:

  * dragRotate.isEnabled()        -> True  (right-click / ctrl-drag)
  * touchZoomRotate.isEnabled()   -> True  (two-finger pinch + twist)
  * touchPitch.isEnabled()        -> True  (two-finger vertical-drag tilts) -- CHANGED
  * map.getMaxPitch()             -> 60    (MapLibre default; tilt ceiling unchanged)
  * pitchWithRotate (constructor) -> a VERTICAL right-drag now changes pitch -- NEW

Then drives REAL right-button drags across the canvas and observes, by reading the
live camera, that a horizontal drag rotates the bearing and a vertical drag UP tilts
the pitch UPWARD toward the ceiling (pitchWithRotate). Driving up (not down) proves
the headline — that you can now tilt INTO the 3D view by gesture — rather than just
nudging pitch toward the 0 floor. This is verify_by_observation, not re-derived math.

Run the AOP Playwright server first:  cd website && python3 -m http.server 8001
Usage: python3 brain/output/verify_spin_while_tilted.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/index.html"
PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 900, "height": 800})
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))

        page.goto(URL, wait_until="load")
        page.wait_for_function("() => window.AOPViewer && window.AOPViewer.map", timeout=15000)
        page.wait_for_function("() => window.AOPViewer.map.isStyleLoaded()", timeout=15000)
        page.wait_for_timeout(800)

        # ── 1. Live handler states (the real running config) ──────────────
        states = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            return {
                dragRotate: m.dragRotate && m.dragRotate.isEnabled(),
                touchZoomRotate: m.touchZoomRotate && m.touchZoomRotate.isEnabled(),
                touchPitch: m.touchPitch ? m.touchPitch.isEnabled() : null,
                maxPitch: m.getMaxPitch(),
            };
        }""")
        check("dragRotate enabled (desktop right-click spin)", states["dragRotate"] is True, str(states["dragRotate"]))
        check("touchZoomRotate enabled (two-finger spin/zoom)", states["touchZoomRotate"] is True, str(states["touchZoomRotate"]))
        check("touchPitch ENABLED (two-finger drag tilts now)", states["touchPitch"] is True, str(states["touchPitch"]))
        check("maxPitch at MapLibre default 60 (no raised ceiling)", abs((states["maxPitch"] or 0) - 60) < 0.01, str(states["maxPitch"]))

        # ── 2. Behavioral: horizontal right-drag ROTATES the bearing ──────
        page.evaluate("() => window.AOPViewer.map.easeTo({ pitch: 30, bearing: -90, duration: 0 })")
        page.wait_for_timeout(250)
        box = page.locator("#map canvas").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2

        before = page.evaluate("() => ({ b: AOPViewer.map.getBearing(), p: AOPViewer.map.getPitch() })")
        page.mouse.move(cx, cy)
        page.mouse.down(button="right")
        for dx in range(40, 201, 40):  # sweep RIGHT -> bearing
            page.mouse.move(cx + dx, cy)
            page.wait_for_timeout(15)
        page.mouse.up(button="right")
        page.wait_for_timeout(250)
        midd = page.evaluate("() => ({ b: AOPViewer.map.getBearing(), p: AOPViewer.map.getPitch() })")
        check("horizontal right-drag rotated the bearing", abs(midd["b"] - before["b"]) > 5,
              f"Δbearing={abs(midd['b'] - before['b']):.1f}°")

        # ── 3. Behavioral: vertical right-drag UP TILTS the pitch UPWARD (pitchWithRotate) ──
        # Start near-flat and drag UP, so we observe the camera tilt INTO the 3D view
        # (pitch climbing toward the 60° ceiling) — the headline feature — not a fall to
        # the 0 floor. A drag DOWN flattens; a drag UP lays the camera back. (Witness 2026-06-15.)
        page.evaluate("() => window.AOPViewer.map.easeTo({ pitch: 8, duration: 0 })")
        page.wait_for_timeout(250)
        p_before = page.evaluate("() => AOPViewer.map.getPitch()")
        page.mouse.move(cx, cy)
        page.mouse.down(button="right")
        for dy in range(40, 201, 40):  # sweep UP -> pitch climbs toward the ceiling
            page.mouse.move(cx, cy - dy)
            page.wait_for_timeout(15)
        page.mouse.up(button="right")
        page.wait_for_timeout(250)
        p_after = page.evaluate("() => AOPViewer.map.getPitch()")
        check("vertical right-drag UP tilted the pitch UPWARD (pitchWithRotate)", p_after - p_before > 5,
              f"pitch {p_before:.1f}->{p_after:.1f} (Δ={p_after - p_before:+.1f}°, ceiling 60)")

        # ── 4. No product console errors (headless-environment noise filtered) ──
        # Filtered as ENVIRONMENTAL (not product defects; the diff touches no
        # fetch/source/shader code):
        #   * tnmap.tn.gov / s3.amazonaws.com (elevation-tiles-prod) / favicon — external
        #     tiles + DEM are unreachable/blocked headless, surfacing as "Failed to fetch".
        #   * shader compile failures — the sky/atmosphere shader won't compile under
        #     headless software WebGL (SwiftShader); it throws regardless of this change.
        def is_env(e):
            return ("tnmap.tn.gov" in e or "favicon" in e
                    or "Failed to fetch" in e or "elevation-tiles-prod" in e
                    or "s3.amazonaws.com" in e or "amazonaws" in e
                    or "compile fragment shader" in e or "compile vertex shader" in e)
        real_errors = [e for e in errors if not is_env(e)]
        check("no product console errors (headless-env tile/shader noise filtered)",
              len(real_errors) == 0, "; ".join(real_errors[:3]))

        browser.close()

    print(f"\n{len(PASS)}/{len(PASS) + len(FAIL)} PASS")
    if FAIL:
        print("FAILED:", ", ".join(FAIL))
        sys.exit(1)


if __name__ == "__main__":
    main()
