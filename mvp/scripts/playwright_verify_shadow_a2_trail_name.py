#!/usr/bin/env python3
"""Shadow-attribute resolution A2 — trail read-site convergence (the Launchpad fix).

The bug that opened Sprint 09: trail #1 showed "Launchpad" on the left, "Trail 1"
on the right, "1" on the map — because the name was a RUNTIME catalog join, not a
field. A1 baked the canonical name; A2 points every read site at it and DELETES the
runtime join. This verifier OBSERVES the agreement LIVE (tile-independent: it reads
the source feature, the rendered search DOM, the rendered panel row text, and the
right-panel Name input VALUE — never a re-derivation of the read site) and asserts
they all say "Launchpad". Plus a number still finds the trail (AOP IDs by number).

Run with a viewer serving website/ on :8001:
    python3 -m http.server 8001 --directory website
    python3 mvp/scripts/playwright_verify_shadow_a2_trail_name.py
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

        # --- Surface 1: the MAP LABEL source (text-field reads ['get','name']) -----
        # Read the live source's GeoJSON object where exposed, else the served file
        # the source was loaded from — either way it is the exact data the label layer
        # paints `['to-string',['get','name']]` from (not a re-derived join).
        label = page.evaluate(
            """async () => {
              const s = window.map.getSource('aop-trail-network');
              let d = s && (s._data || (s.serialize && s.serialize().data));
              if (typeof d === 'string' || !d || !d.features) {
                d = await (await fetch('./data/aop_trail_network.geojson')).json();
              }
              const f = d.features.find(x => (x.properties||{}).trail_number === 1);
              const p = f ? f.properties : {};
              return { name: p.name, desc: !!p.description, diff: (p.facets||{}).difficulty,
                       len: (p.facets||{}).length_mi };
            }"""
        )
        print("\n== Surface 1: map label source feature ==")
        check("map label trail #1 name == 'Launchpad'", label["name"] == "Launchpad", str(label["name"]))
        check("trail #1 description baked", label["desc"] is True)
        check("trail #1 facets.difficulty == 'easy'", label["diff"] == "easy", str(label["diff"]))

        # --- Surface 2: SEARCH DOM (index built from canonical name + description) -
        print("\n== Surface 2: search results (rendered DOM) ==")
        box = page.locator("#searchInput")
        box.click(); box.fill(""); box.fill("Launchpad"); page.wait_for_timeout(400)
        items = page.locator("#searchResults .search-item")
        texts = [items.nth(i).inner_text().replace("\n", " ") for i in range(items.count())]
        check("search 'Launchpad' returns a result naming Launchpad",
              any("Launchpad" in t for t in texts), str(texts[:4]))
        desc_text = page.locator("#searchResults .search-result-desc").first
        has_desc = desc_text.count() > 0 and len((desc_text.inner_text() or "").strip()) > 0
        check("search result shows the baked description (muted line)", has_desc)
        # number still finds it (AOP identifies trails by number)
        box.fill(""); box.fill("1"); page.wait_for_timeout(400)
        n_items = page.locator("#searchResults .search-item")
        n_texts = [n_items.nth(i).inner_text().replace("\n", " ") for i in range(n_items.count())]
        check("search '1' still finds a trail (number alias works)",
              any("trail" in t.lower() for t in n_texts), str(n_texts[:4]))

        # --- Surface 3: PANEL tree row + right-panel Name input VALUE -------------
        print("\n== Surface 3: panel row text + Name input value ==")
        # Ensure the panel is open, then expand the aopTrails node and read its rows.
        page.evaluate(
            """() => {
              const c = document.getElementById('panelCollapse');
              if (c && c.getAttribute('aria-expanded') === 'false') c.click();
              const grp = document.querySelector('[data-node-id="aopTrails"]');
              if (grp) { const ch = grp.querySelector('.node-chevron-btn'); if (ch) ch.click(); }
            }"""
        )
        page.wait_for_timeout(400)
        row_info = page.evaluate(
            """() => {
              const grp = document.querySelector('[data-node-id="aopTrails"]');
              if (!grp) return { found: false };
              const rows = [...grp.querySelectorAll('.item-select')].map(b => b.textContent.trim());
              const launch = rows.find(t => t.startsWith('Launchpad'));
              const t15 = rows.find(t => t.startsWith('Trail 15'));
              return { found: true, launch, t15, count: rows.length, sample: rows.slice(0, 4) };
            }"""
        )
        check("panel aopTrails node lists trail #1 as 'Launchpad' (not 'Trail Launchpad'/'1')",
              bool(row_info.get("launch")) and not str(row_info.get("launch")).startswith("Trail Launchpad"),
              str(row_info.get("launch")))
        check("panel regression: non-catalogued trail #15 still reads 'Trail 15'",
              bool(row_info.get("t15")), str(row_info.get("t15")))
        # Select trail #1's row -> the editor opens -> read the Name input value.
        page.evaluate(
            """() => {
              const grp = document.querySelector('[data-node-id="aopTrails"]');
              const btn = [...grp.querySelectorAll('.item-select')].find(b => b.textContent.trim().startsWith('Launchpad'));
              if (btn) btn.click();
            }"""
        )
        page.wait_for_timeout(400)
        name_val = page.evaluate(
            """() => {
              const inp = document.querySelector('.field-input[data-field="name"]');
              return inp ? inp.value : null;
            }"""
        )
        check("right-panel editor Name input value == 'Launchpad'", name_val == "Launchpad", str(name_val))

        print("\n== Convergence + health ==")
        check("ALL surfaces agree on 'Launchpad' (map label == search == panel row == Name input)",
              label["name"] == "Launchpad"
              and any("Launchpad" in t for t in texts)
              and str(row_info.get("launch", "")).startswith("Launchpad")
              and name_val == "Launchpad")
        check("no console errors", len(console_errors) == 0,
              f"{len(console_errors)}: {console_errors[:3]}")

        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
