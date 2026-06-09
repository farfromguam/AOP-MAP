#!/usr/bin/env python3
"""Shadow-attribute resolution A1 — canonical re-bake population (observed).

A1 makes the sidecar joins REAL in the served data: the trail catalog folds into
aop_trail_network (name/description/difficulty), the poi-index folds into
building/cemetery/visitor descriptions, the building facility role moves to a
facet, the legacy `blurb` is dropped from the served publish.geojson, and the
maturity stamps survive the re-bake. A1 changes DATA, not read sites — so this
verifier OBSERVES the running viewer load the new served files cleanly and reads
the served bytes through the app's own origin (tile-independent: no networkidle,
no queryRenderedFeatures). The read-site convergence is A2/A3 (their own checks).

Run after a viewer is serving website/ on :8001 (the assistant's lane):
    python3 -m http.server 8001 --directory website
    python3 mvp/scripts/playwright_verify_shadow_a1_canonical.py
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def served(page) -> dict:
    """Read the served files through the running viewer's own origin."""
    return page.evaluate(
        """async () => {
          const get = async (f) => (await (await fetch('./data/' + f)).json());
          const tn = await get('aop_trail_network.geojson');
          const bld = await get('aop_buildings.geojson');
          const cem = await get('aop_cemeteries.geojson');
          const vis = await get('aop_visitor_context_callouts.geojson');
          const pub = await get('publish.geojson');
          const t1 = tn.features.map(f=>f.properties).find(p=>p.trail_number===1);
          const pav = bld.features.map(f=>f.properties).find(p=>p.facility_name==='Pavilion');
          const ellis = cem.features.map(f=>f.properties).find(p=>p.name==='Ellis Cemetery' && p.geom_role==='marker');
          const sp = vis.features.map(f=>f.properties).find(p=>(p.name||'').includes('Pittsburg'));
          const brand = vis.features.some(f=>f.properties.kind==='brand_logo');
          return {
            t1, pav, ellis, sp, brand,
            tn_meta_maturity: (tn._meta||{}).maturity,
            pub_count: pub.features.length,
            pub_has_blurb: pub.features.some(f=>('blurb' in (f.properties||{}))),
            pub_desc_count: pub.features.filter(f=>f.properties.description).length,
            has_trail_source: !!(window.map && window.map.getSource && window.map.getSource('aop-trail-network')),
          };
        }"""
    )


def main() -> int:
    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        d = served(page)

        print("\n== Trail catalog join (the Launchpad fix, baked) ==")
        check("trail #1 canonical name == 'Launchpad'", d["t1"]["name"] == "Launchpad", str(d["t1"]["name"]))
        check("trail #1 has a description", bool(d["t1"].get("description")))
        check("trail #1 facets.difficulty == 'easy'", (d["t1"].get("facets") or {}).get("difficulty") == "easy",
              str(d["t1"].get("facets")))
        check("trail #1 original name '1' preserved under _original (additive)",
              (d["t1"].get("_original") or {}).get("name") == "1", str(d["t1"].get("_original")))
        check("trail #1 trail_number key still present", d["t1"].get("trail_number") == 1)

        print("\n== poi-index join into description (baked) ==")
        check("Pavilion has a description (poi-index blurb)", bool(d["pav"].get("description")))
        check("Ellis cemetery marker has a description", bool(d["ellis"].get("description")))
        check("visitor (South Pittsburg) has a description", bool(d["sp"].get("description")))

        print("\n== Building facility role -> facet; status is a publish/review state ==")
        check("Pavilion facets.facility_role present", bool((d["pav"].get("facets") or {}).get("facility_role")),
              str(d["pav"].get("facets")))
        check("Pavilion status is not the role word ('raw context')", d["pav"].get("status") == "raw context",
              str(d["pav"].get("status")))

        print("\n== publish.geojson legacy blurb dropped, content intact ==")
        check("no `blurb` key left on any published feature", d["pub_has_blurb"] is False)
        check("publish still has 6 features (DB-baked, not reverted)", d["pub_count"] == 6, str(d["pub_count"]))
        check("published descriptions intact (3)", d["pub_desc_count"] == 3, str(d["pub_desc_count"]))

        print("\n== Non-limiting + maturity preserved + viewer healthy ==")
        check("out-of-vocab kind 'brand_logo' still served (no reject)", d["brand"] is True)
        check("trail-network _meta maturity preserved ('gold')", d["tn_meta_maturity"] == "gold",
              str(d["tn_meta_maturity"]))
        check("viewer consumed the trail-network source (data parsed + loaded)", d["has_trail_source"] is True)
        check("no console errors loading the re-baked data", len(console_errors) == 0,
              f"{len(console_errors)} error(s): {console_errors[:3]}")

        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
