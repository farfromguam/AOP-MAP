#!/usr/bin/env python3
"""Observe that the 3D viewer can be SPUN (bearing rotated) while TILTED, and that
the pitch GESTURE stays disabled (pitch is button-only) — verify_by_observation
for the viewer_core.js rotate re-enable.

Reads the LIVE MapLibre handler states (not re-derived):
  * dragRotate.isEnabled()        -> True  (right-click / ctrl-drag spins)
  * touchZoomRotate rotation       -> True  (two-finger twist spins)
  * touchPitch.isEnabled()         -> False (no accidental finger-tilt)

Then drives a REAL right-button mouse drag across the canvas with the camera
pitched, and observes the bearing actually change while the pitch is preserved
(pitchWithRotate:false held — the spin did not also tilt).

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
        # Wait for the viewer to expose the map and finish first style load.
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
            };
        }""")
        check("dragRotate enabled (desktop right-click spin)", states["dragRotate"] is True, str(states["dragRotate"]))
        check("touchZoomRotate enabled (two-finger spin)", states["touchZoomRotate"] is True, str(states["touchZoomRotate"]))
        check("touchPitch DISABLED (pitch is button-only)", states["touchPitch"] is False, str(states["touchPitch"]))

        # ── 2. Behavioral: spin while tilted ──────────────────────────────
        # Tilt the camera the way the 3D toggle does (pitch 60), instantly.
        page.evaluate("() => window.AOPViewer.map.easeTo({ pitch: 58, bearing: -90, duration: 0 })")
        page.wait_for_timeout(300)
        before = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            return { bearing: m.getBearing(), pitch: m.getPitch() };
        }""")
        check("camera is tilted before spin", before["pitch"] > 45, f"pitch={before['pitch']:.1f}")

        # Drive a REAL right-button drag horizontally across the map canvas.
        box = page.locator("#map canvas").bounding_box()
        cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        page.mouse.move(cx, cy)
        page.mouse.down(button="right")
        for dx in range(20, 261, 20):  # sweep right -> rotates bearing
            page.mouse.move(cx + dx, cy)
            page.wait_for_timeout(10)
        page.mouse.up(button="right")
        page.wait_for_timeout(300)

        after = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            return { bearing: m.getBearing(), pitch: m.getPitch() };
        }""")
        d_bearing = abs(after["bearing"] - before["bearing"])
        d_pitch = abs(after["pitch"] - before["pitch"])
        check("right-drag SPUN the bearing while tilted", d_bearing > 5,
              f"Δbearing={d_bearing:.1f}° ({before['bearing']:.1f}->{after['bearing']:.1f})")
        check("pitch PRESERVED during spin (pitchWithRotate:false)", d_pitch < 5,
              f"Δpitch={d_pitch:.1f}° ({before['pitch']:.1f}->{after['pitch']:.1f})")

        # ── 3. No console errors ──────────────────────────────────────────
        # Filter known-ENVIRONMENTAL noise (not product defects, and provably not
        # caused by this rotate change — the diff touches no shaders/sky/fog):
        #   * tnmap.tn.gov / favicon — external tiles unreachable headless.
        #   * "Could not compile fragment shader" — the sky/atmosphere shader
        #     fails to compile under headless software WebGL (SwiftShader); it
        #     throws regardless of whether rotation is enabled.
        def is_env(e):
            return ("tnmap.tn.gov" in e or "favicon" in e
                    or "compile fragment shader" in e or "compile vertex shader" in e)
        real_errors = [e for e in errors if not is_env(e)]
        check("no product console errors (headless GL shader noise filtered)",
              len(real_errors) == 0, "; ".join(real_errors[:3]))

        browser.close()

    print(f"\n{len(PASS)}/{len(PASS) + len(FAIL)} PASS")
    if FAIL:
        print("FAILED:", ", ".join(FAIL))
        sys.exit(1)


if __name__ == "__main__":
    main()
