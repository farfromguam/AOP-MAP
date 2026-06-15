#!/usr/bin/env python3
"""Verify by observation (not re-derivation): the AOP trail network renders as a
gold line layer on the default Park preset, AND the data the live viewer loaded
now carries permission='publish' on every trail (was 'SFWDA paper map — permission
TBD' on 120 + missing on 10). Run against the Playwright port (:8001).

    cd website && python3 -m http.server 8001   # if not already up
    python3 brain/output/verify_trails_gold_publish_permission.py
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "mvp" / "scripts"))
from playwright_base import viewer_url, layer_visibility, rendered_count  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = Path(__file__).resolve().parent / "trails_gold_publish_permission.png"


def main() -> int:
    checks, errors = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="networkidle")
        # The MapLibre instance lives in a closure, exposed as window.AOPViewer.map
        # (window.map is the <div id="map"> element). Re-point window.map at the real
        # instance so the shared playwright_base helpers work.
        page.wait_for_function(
            """() => {
              const m = window.AOPViewer && window.AOPViewer.map;
              if (!m || !m.isStyleLoaded || !m.isStyleLoaded()) return false;
              try { return !!m.getLayer('aop-trail-network'); } catch (e) { return false; }
            }""",
            timeout=20000,
        )
        page.evaluate("window.map = window.AOPViewer.map;")
        page.wait_for_timeout(1200)

        vis = layer_visibility(page, "aop-trail-network")
        checks.append(("trail layer present + visible (Park default)", vis == "visible", vis))

        n = rendered_count(page, ["aop-trail-network"])
        checks.append(("trails rendered on the map", n > 0, f"{n} rendered features"))

        # Read the data the LIVE viewer actually fetched/holds for the trail source.
        perm = page.evaluate(
            """() => {
              const src = window.map.getSource('aop-trail-network');
              if (!src) return null;
              let d = null;
              if (typeof src.serialize === 'function') d = src.serialize().data;
              if (!d || !d.features) d = src._data || (src._options && src._options.data);
              if (!d || !d.features) return null;
              const c = {};
              for (const f of d.features) {
                const v = (f.properties || {}).permission ?? '(missing)';
                c[v] = (c[v] || 0) + 1;
              }
              return { total: d.features.length, counts: c };
            }"""
        )
        ok_perm = bool(perm) and perm["counts"].get("publish") == perm["total"]
        checks.append(("every loaded trail reads permission='publish'", ok_perm, perm))
        no_tbd = bool(perm) and not any("TBD" in k for k in perm["counts"])
        checks.append(("no 'permission TBD' left in loaded trail data", no_tbd, list(perm["counts"]) if perm else None))

        page.screenshot(path=str(OUT))
        browser.close()

    print("\nVERIFY trails render gold + permission=publish\n" + "-" * 52)
    passed = 0
    for label, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}  — {detail}")
        passed += ok
    print("-" * 52)
    print(f"  {passed}/{len(checks)} PASS | console errors: {len(errors)}")
    if errors:
        for e in errors[:5]:
            print("    console-error:", e[:140])
    print(f"  screenshot: {OUT.relative_to(Path(__file__).resolve().parents[2])}")
    return 0 if passed == len(checks) and not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
