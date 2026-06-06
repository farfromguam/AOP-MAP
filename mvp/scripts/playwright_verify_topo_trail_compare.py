#!/usr/bin/env python3
"""Verify the topo+trail colour comparison pages render real park-core data.

Two sibling review pages (linked from the index.html Review section):
  * topo_trail_compare.html        — fade-topo / pop-trail schemes (5 cards)
  * topo_trail_orange_compare.html — orange variations on the chosen V1
                                     background (8 cards)

Each card is one real MapLibre map of the clipped park-core data (compare_data/)
so the user can pick a scheme to wire into the Topo preset. This asserts the
right number of real map canvases + table rows and no console errors, and writes
a full-page screenshot per page.

The small maps render progressively as the AWS DEM tiles + geojson sources
resolve (8 maps each parse the ~3 MB contour clip), so this scrolls each map
into view and waits before the screenshot — an early shot caught maps mid-render
in development (not a product bug).

Run (server on the assistant's port 8001):
    cd website && python3 -m http.server 8001 &
    python3 mvp/scripts/playwright_verify_topo_trail_compare.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright_base import viewer_origin  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUTDIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "brain", "output")
)
PAGES = [
    ("topo_trail_compare.html", 5, "playwright_topo_trail_compare.png"),
    ("topo_trail_orange_compare.html", 8, "playwright_topo_trail_orange_compare.png"),
]


def check_page(pg, path, expected):
    errors = []
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append("PAGEERROR: " + str(e)))
    pg.goto(viewer_origin() + "/" + path, wait_until="networkidle")
    time.sleep(4)
    # force each map to paint by scrolling it into view, then settle
    n = pg.eval_on_selector_all(".card .map", "els => els.length")
    for i in range(n):
        pg.eval_on_selector_all(
            ".card .map", "(els, i) => els[i] && els[i].scrollIntoView()", i
        )
        time.sleep(1.2)
    time.sleep(3)
    return errors


def main():
    all_ok = True
    with sync_playwright() as p:
        b = p.chromium.launch()
        for path, expected, shot in PAGES:
            pg = b.new_page(viewport={"width": 1400, "height": 2600})
            errors = check_page(pg, path, expected)
            cards = pg.eval_on_selector_all(".card", "e => e.length")
            canv = pg.eval_on_selector_all(".maplibregl-canvas", "e => e.length")
            rows = pg.eval_on_selector_all("#attrs tbody tr", "e => e.length")
            pg.screenshot(path=os.path.join(OUTDIR, shot), full_page=True)
            ok = (cards == expected and canv == expected and rows == expected and not errors)
            all_ok = all_ok and ok
            print(f"[{path}] cards={cards} canvases={canv} rows={rows} "
                  f"(expected {expected}) console_errors={len(errors)} -> "
                  f"{'PASS' if ok else 'FAIL'}")
            for e in errors[:15]:
                print("   ERR:", e[:180])
            pg.close()
        b.close()
    print("RESULT:", "PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
