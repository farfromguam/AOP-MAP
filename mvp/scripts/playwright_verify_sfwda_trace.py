#!/usr/bin/env python3
"""Verify the SFWDA traced-trail/marker review layers load and toggle.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

Confirms the two extracted review layers wire into the viewer cleanly:
  - both sources + layers exist on the map,
  - they default OFF (visibility 'none'),
  - flipping each toggle makes the layer visible and renders features,
  - switching presets does NOT force them (they are in no preset object),
  - no console errors during the run.

Captures a screenshot with both layers on over the Trace preset.

Run after `cd website && python3 -m http.server 8001`.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, set_toggle, layer_visibility, rendered_count

OUT = Path(__file__).resolve().parents[2] / "brain/output"
LAYERS = ["sfwda-trace-trails", "sfwda-trace-markers"]
TOGGLES = {"sfwda-trace-trails": "showSfwdaTraceTrails",
           "sfwda-trace-markers": "showSfwdaTraceMarkers"}


def main() -> int:
    failures, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")  # `map` is a global lexical binding
        page.wait_for_function(
            "() => document.getElementById('message')?.textContent?.includes('publish feature')",
            timeout=30000,   # full headless load (rectified imagery + all layers) runs ~10s; 15s was too tight under load
        )
        page.wait_for_timeout(600)

        # both layers (+ the marker-number label layer) present + default OFF
        for lid in LAYERS + ["sfwda-trace-marker-labels"]:
            vis = layer_visibility(page, lid)
            if vis is None:
                failures.append(f"{lid}: layer not on map")
            elif vis != "none":
                failures.append(f"{lid}: default visibility {vis!r}, expected 'none'")

        # toggle each on -> visible + renders features (after framing the park)
        page.evaluate("() => document.querySelector('[data-preset=\"trace\"]')?.click()")
        page.wait_for_timeout(400)
        for lid, tid in TOGGLES.items():
            set_toggle(page, tid, True)
        page.wait_for_timeout(400)
        for lid in LAYERS:
            if layer_visibility(page, lid) != "visible":
                failures.append(f"{lid}: not visible after toggle on")
        n = rendered_count(page, LAYERS)
        if n <= 0:
            failures.append(f"layers rendered {n} features (expected > 0)")
        # the marker-number labels show with the markers toggle
        if layer_visibility(page, "sfwda-trace-marker-labels") != "visible":
            failures.append("sfwda-trace-marker-labels: not visible after markers toggle on")
        if rendered_count(page, ["sfwda-trace-marker-labels"]) <= 0:
            failures.append("sfwda-trace-marker-labels: rendered 0 trail-number labels")
        # merged AOP trail network (the cleaned truth) loads + renders
        set_toggle(page, "showAopTrailNetwork", True)
        page.wait_for_timeout(400)
        if layer_visibility(page, "aop-trail-network") != "visible":
            failures.append("aop-trail-network: not visible after toggle on")
        if rendered_count(page, ["aop-trail-network"]) <= 0:
            failures.append("aop-trail-network: rendered 0 edges")

        # presets must not force these off (not in any preset object)
        page.evaluate("() => document.querySelector('[data-preset=\"park\"]')?.click()")
        page.wait_for_timeout(400)
        for lid in LAYERS:
            if layer_visibility(page, lid) != "visible":
                failures.append(f"{lid}: preset switch wrongly forced it off")

        OUT.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUT / "playwright_sfwda_trace.png"))
        browser.close()

    if errors:
        failures.append(f"{len(errors)} console error(s): {errors[:3]}")
    if failures:
        print("FAIL")
        for f in failures:
            print("  -", f)
        return 1
    print(f"PASS — both trace layers load, toggle, render ({n} features), survive preset switch")
    return 0


if __name__ == "__main__":
    sys.exit(main())
