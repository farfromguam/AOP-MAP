#!/usr/bin/env python3
"""Verify the curated GOLD contour layer: index (major) lines kept across the whole
9-patch, minor lines clipped to the park center cell; full set preserved as SILVER.

User: "the major lines for the whole 9 patch and the minor lines for just the park
bounds. our current data demoted to silver and this new bit our gold dataset."

Two layers of proof:
  (A) DATA invariants (read the files directly — deterministic):
      - silver = full set (2831 feats), maturity 'silver'
      - gold maturity 'gold'; ALL minor (idx==0) vertices inside the park cell;
        index (idx==1) lines present BOTH outside the cell (9-patch context) and
        inside (labels in the park); gold << silver in size.
  (B) LIVE render on :8001 (real running viewer, no JS change — it reads gold):
      - Park default: no contour fetch (lazy-load still holds).
      - Topo: the new gold loads (911 feats), contours-index + contours-minor
        layers visible, 0 console errors.

Run: python3 brain/output/verify_contours_curated_gold.py
"""
import json, os, sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
GOLD = "website/data/gold_aop_contours.geojson"
SILVER = "website/data/silver_aop_contours.geojson"
W, S, E, N = -85.761008221, 35.084085624, -85.739081159, 35.101007060
EPS = 1e-6  # bbox tolerance for clip rounding


def verts(g):
    t = g["type"]; c = g["coordinates"]
    if t == "LineString": return c
    if t == "MultiLineString": return [p for ln in c for p in ln]
    return []


def in_cell(p):
    return (W - EPS) <= p[0] <= (E + EPS) and (S - EPS) <= p[1] <= (N + EPS)


def log(m): print(m, flush=True)


def data_checks(R):
    gold = json.load(open(GOLD, encoding="utf-8"))
    silver = json.load(open(SILVER, encoding="utf-8"))
    gfeats = gold["features"]
    minor = [f for f in gfeats if f["properties"].get("idx") == 0]
    index = [f for f in gfeats if f["properties"].get("idx") == 1]
    minor_all_in_cell = all(in_cell(p) for f in minor for p in verts(f["geometry"]))
    index_outside = any(not in_cell(p) for f in index for p in verts(f["geometry"]))
    index_inside = any(in_cell(p) for f in index for p in verts(f["geometry"]))
    R["gold_size_mb"] = round(os.path.getsize(GOLD) / 1e6, 2)
    R["silver_size_mb"] = round(os.path.getsize(SILVER) / 1e6, 2)
    R["gold_features"] = len(gfeats)
    R["gold_minor"] = len(minor)
    R["gold_index"] = len(index)
    return {
        "silver is the full set (2831 feats)": len(silver["features"]) == 2831,
        "silver maturity == silver": silver.get("_meta", {}).get("maturity") == "silver",
        "gold maturity == gold": gold.get("_meta", {}).get("maturity") == "gold",
        "gold MINOR lines are ALL inside the park cell": bool(minor) and minor_all_in_cell,
        "gold INDEX lines reach OUTSIDE the cell (9-patch context)": index_outside,
        "gold INDEX lines also inside the park (labels there)": index_inside,
        "gold is much smaller than silver (>=60% cut)": os.path.getsize(GOLD) <= 0.4 * os.path.getsize(SILVER),
    }


def live_checks(R):
    errors = []
    requests = []
    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.set_default_timeout(8000)
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("request", lambda r: requests.append(r.url))
        page.goto(URL, wait_until="load")
        page.wait_for_function(
            "() => window.AOPViewer && window.AOPViewer.map && window.AOPViewer.map.isStyleLoaded()"
            " && window.AOPViewer.map.getSource('aop-waypoints')", timeout=45000)
        page.wait_for_timeout(1200)
        out["park_contour_requests"] = [u for u in requests if "gold_aop_contours" in u]
        page.click("#presetTopo")
        page.wait_for_function(
            "() => { const m=window.AOPViewer.map; return m.getSource('aop-contours') && m.getLayer('contours-index'); }",
            timeout=30000)
        page.wait_for_timeout(800)
        out["topo"] = page.evaluate("""() => {
            const m = window.AOPViewer.map;
            const data = m.getSource('aop-contours').serialize().data;
            const feats = (data && data.features) || [];
            const vis = (id) => m.getLayer(id) ? m.getLayoutProperty(id,'visibility') : 'absent';
            let idx0=0, idx1=0;
            for (const f of feats) { const i=(f.properties||{}).idx; if(i===0)idx0++; else if(i===1)idx1++; }
            return { feature_count: feats.length, minor: idx0, index: idx1,
                     contours_index_vis: vis('contours-index'), contours_minor_vis: vis('contours-minor') };
        }""")
        out["topo_contour_requests"] = [u for u in requests if "gold_aop_contours" in u]
        out["console_errors"] = [e for e in errors if "favicon" not in e.lower()]
        try: ctx.close(); browser.close()
        except Exception: pass
    R["live"] = out
    t = out["topo"]
    return {
        "PARK: no contour fetch (lazy-load holds)": out["park_contour_requests"] == [],
        "TOPO: loaded the curated gold (911 feats)": t["feature_count"] == 911,
        "TOPO: 501 index + 410 minor in the live source": t["index"] == 501 and t["minor"] == 410,
        "TOPO: contours-index visible": t["contours_index_vis"] == "visible",
        "TOPO: contours-minor visible": t["contours_minor_vis"] == "visible",
        "No console errors": len(out["console_errors"]) == 0,
    }


def main():
    R = {}
    checks = {}
    checks.update(data_checks(R))
    checks.update(live_checks(R))
    print(json.dumps(R, indent=2), flush=True)
    print("\n--- CHECKS ---", flush=True)
    allok = True
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}", flush=True)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}", flush=True)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
