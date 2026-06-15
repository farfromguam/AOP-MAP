#!/usr/bin/env python3
"""Verify by observation: the park-bounds border (publish-boundaries) is now a
faint tan — a tad darker than the publish-boundary-fill tint — instead of the old
dark brown edge, in BOTH presets that draw it (Park, Topo). The line layer is
kept (it stays in INTERACTIVE_POPUP_LAYERS as the click target) and renders with
no console errors. Trace/Satellite have showBoundaries:false so they don't draw
it. Run against the Playwright port (:8001).

    cd website && python3 -m http.server 8001   # if not already up
    python3 brain/output/verify_park_border_faint.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "mvp" / "scripts"))
from playwright_base import viewer_url, layer_visibility  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUTDIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]


def paint(page, prop):
    return page.evaluate(
        "([p]) => window.map.getPaintProperty('publish-boundaries', p)", [prop]
    )


def frame_park(page):
    # Fit the whole parcel so the border ring is in view.
    page.evaluate(
        """() => {
          const src = window.map.getSource('publish-data');
          const d = src && (src.serialize ? src.serialize().data : src._data);
          const b = {minx: 1e9, miny: 1e9, maxx: -1e9, maxy: -1e9};
          const walk = (c) => { if (typeof c[0] === 'number') {
              b.minx=Math.min(b.minx,c[0]); b.maxx=Math.max(b.maxx,c[0]);
              b.miny=Math.min(b.miny,c[1]); b.maxy=Math.max(b.maxy,c[1]); }
            else c.forEach(walk); };
          d.features.filter(f => (f.properties||{}).layer==='park_boundaries')
                    .forEach(f => walk(f.geometry.coordinates));
          window.map.fitBounds([[b.minx,b.miny],[b.maxx,b.maxy]],
            {padding: 80, duration: 0, bearing: 0});
        }"""
    )


def closeup_edge(page):
    # Center+zoom on one boundary vertex so the line is large in frame.
    page.evaluate(
        """() => {
          const src = window.map.getSource('publish-data');
          const d = src && (src.serialize ? src.serialize().data : src._data);
          const f = d.features.find(f => (f.properties||{}).layer==='park_boundaries');
          let c = f.geometry.coordinates;
          while (typeof c[0] !== 'number') c = c[Math.floor(c.length/2)];
          window.map.jumpTo({center: c, zoom: 17, bearing: 0, pitch: 0});
        }"""
    )


def main() -> int:
    checks, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="networkidle")
        page.wait_for_function(
            """() => { const m = window.AOPViewer && window.AOPViewer.map;
              if (!m || !m.isStyleLoaded || !m.isStyleLoaded()) return false;
              try { return !!m.getLayer('publish-boundaries'); } catch(e){ return false; } }""",
            timeout=20000,
        )
        page.evaluate("window.map = window.AOPViewer.map;")
        page.wait_for_timeout(1000)

        # --- Park (default) ---
        vis = layer_visibility(page, "publish-boundaries")
        checks.append(("Park: boundary line present + visible (click target)", vis == "visible", vis))
        pk = {k: paint(page, f"line-{k}") for k in ("color", "width", "opacity")}
        checks.append(("Park: line-color is the faint tan #c4b48c (not dark #6e5a3c)",
                       (pk["color"] or "").lower() in ("#c4b48c",), pk["color"]))
        checks.append(("Park: line-width thinned to 1.5 (was 2.5)", pk["width"] == 1.5, pk["width"]))
        checks.append(("Park: line-opacity dropped to 0.5 (was 1)", pk["opacity"] == 0.5, pk["opacity"]))
        frame_park(page); page.wait_for_timeout(500)
        page.screenshot(path=str(OUTDIR / "park_border_faint_park.png"))
        closeup_edge(page); page.wait_for_timeout(500)
        page.screenshot(path=str(OUTDIR / "park_border_faint_park_closeup.png"))

        # --- Topo ---
        page.click('.preset-bar button[data-preset="topo"]')
        page.wait_for_timeout(1200)
        vis = layer_visibility(page, "publish-boundaries")
        checks.append(("Topo: boundary line present + visible", vis == "visible", vis))
        tp = {k: paint(page, f"line-{k}") for k in ("color", "width", "opacity")}
        checks.append(("Topo: line-color is the faint gold #d4b974 (not dark #4d3928)",
                       (tp["color"] or "").lower() in ("#d4b974",), tp["color"]))
        checks.append(("Topo: line-width thinned to 1.5 (was 3)", tp["width"] == 1.5, tp["width"]))
        checks.append(("Topo: line-opacity dropped to 0.5 (was 1)", tp["opacity"] == 0.5, tp["opacity"]))
        frame_park(page); page.wait_for_timeout(500)
        page.screenshot(path=str(OUTDIR / "park_border_faint_topo.png"))
        closeup_edge(page); page.wait_for_timeout(500)
        page.screenshot(path=str(OUTDIR / "park_border_faint_topo_closeup.png"))

        browser.close()

    print("\nVERIFY park-bounds border is faint (a tad darker than the fill)\n" + "-" * 58)
    passed = 0
    for label, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}  — {detail}")
        passed += ok
    print("-" * 58)
    print(f"  {passed}/{len(checks)} PASS | console errors: {len(errors)}")
    for e in errors[:5]:
        print("    console-error:", e[:140])
    print("  screenshots: park_border_faint_{park,topo}[_closeup].png in brain/output/")
    return 0 if passed == len(checks) and not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
