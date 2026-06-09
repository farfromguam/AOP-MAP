#!/usr/bin/env python3
"""Shadow-attribute resolution A3 — building / cemetery / visitor convergence.

A3 deletes the runtime `poiIndexLookup` blurb join and points building / cemetery /
visitor read sites at the canonical fields A1/A3 baked: the building NAME is now the
facility name ("Pavilion", not the street address — address moved to facets.address),
and descriptions come from the feature's `description` (folded from the poi-index).
This verifier OBSERVES the convergence LIVE — the building Pavilion reads "Pavilion"
on the panel row, the panel Name input value, and search; descriptions are present —
never a re-derivation. The per-feature poi-index join is gone (grep, separate).

Run with a viewer serving website/ on :8001.
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


def main() -> int:
    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(viewport={"width": 1366, "height": 900}).new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        # --- Surface 1: served canonical fields (what every site now reads) -------
        data = page.evaluate(
            """async () => {
              const get = async (f) => (await (await fetch('./data/' + f)).json());
              const bld = (await get('aop_buildings.geojson')).features.map(f => f.properties);
              const cem = (await get('aop_cemeteries.geojson')).features.map(f => f.properties);
              const vis = (await get('aop_visitor_context_callouts.geojson')).features.map(f => f.properties);
              const pav = bld.find(p => p.facility_name === 'Pavilion');
              const ellis = cem.find(p => p.name === 'Ellis Cemetery' && p.geom_role === 'marker');
              const sp = vis.find(p => (p.name||'').includes('Pittsburg'));
              return {
                pav_name: pav.name, pav_addr: (pav.facets||{}).address, pav_desc: !!pav.description,
                ellis_desc: !!ellis.description, sp_desc: !!sp.description,
              };
            }"""
        )
        print("\n== Surface 1: served canonical fields ==")
        check("building canonical name == 'Pavilion' (facility name, not the address)",
              data["pav_name"] == "Pavilion", str(data["pav_name"]))
        check("building street address moved to facets.address",
              data["pav_addr"] == "1010 Ellis Cove Road", str(data["pav_addr"]))
        check("Pavilion description baked (from poi-index)", data["pav_desc"] is True)
        check("Ellis cemetery marker description baked", data["ellis_desc"] is True)
        check("visitor (South Pittsburg) description baked", data["sp_desc"] is True)

        # --- Surface 2: search DOM ------------------------------------------------
        print("\n== Surface 2: search (rendered DOM) ==")
        box = page.locator("#searchInput")
        box.click(); box.fill(""); box.fill("pavilion"); page.wait_for_timeout(400)
        items = page.locator("#searchResults .search-item")
        texts = [items.nth(i).inner_text().replace("\n", " ") for i in range(items.count())]
        check("search 'pavilion' returns 'Pavilion'", any("Pavilion" in t for t in texts), str(texts[:4]))
        box.fill(""); box.fill("1010 ellis"); page.wait_for_timeout(400)
        a_items = page.locator("#searchResults .search-item")
        a_texts = [a_items.nth(i).inner_text().replace("\n", " ") for i in range(a_items.count())]
        check("search by street address '1010 ellis' still finds the Pavilion (address alias)",
              any("Pavilion" in t for t in a_texts), str(a_texts[:4]))

        # --- Surface 3: panel building row + Name input value --------------------
        print("\n== Surface 3: panel building row + Name input value ==")
        page.evaluate(
            """() => {
              const c = document.getElementById('panelCollapse');
              if (c && c.getAttribute('aria-expanded') === 'false') c.click();
              const grp = document.querySelector('[data-node-id="buildings"]');
              if (grp) { const ch = grp.querySelector('.node-chevron-btn'); if (ch) ch.click(); }
            }"""
        )
        page.wait_for_timeout(400)
        rows = page.evaluate(
            """() => {
              const grp = document.querySelector('[data-node-id="buildings"]');
              if (!grp) return { found: false };
              const r = [...grp.querySelectorAll('.item-select')].map(b => b.textContent.trim());
              return { found: true, pavilion: r.find(t => t.startsWith('Pavilion')),
                       address_only: r.some(t => t.startsWith('1010 Ellis')), sample: r.slice(0, 5) };
            }"""
        )
        check("panel building row reads 'Pavilion' (canonical name, not the address)",
              bool(rows.get("pavilion")), str(rows.get("sample")))
        check("panel building row is NOT the bare street address",
              rows.get("address_only") is False)
        page.evaluate(
            """() => {
              const grp = document.querySelector('[data-node-id="buildings"]');
              const btn = [...grp.querySelectorAll('.item-select')].find(b => b.textContent.trim().startsWith('Pavilion'));
              if (btn) btn.click();
            }"""
        )
        page.wait_for_timeout(400)
        name_val = page.evaluate(
            """() => { const i = document.querySelector('.field-input[data-field="name"]'); return i ? i.value : null; }"""
        )
        check("right-panel editor Name input value == 'Pavilion'", name_val == "Pavilion", str(name_val))

        print("\n== Convergence + health ==")
        check("building name agrees across served / search / panel row / Name input",
              data["pav_name"] == "Pavilion"
              and any("Pavilion" in t for t in texts)
              and str(rows.get("pavilion", "")).startswith("Pavilion")
              and name_val == "Pavilion")
        check("no console errors", len(console_errors) == 0, f"{len(console_errors)}: {console_errors[:3]}")
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
