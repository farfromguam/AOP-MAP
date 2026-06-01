#!/usr/bin/env python3
"""Playwright verification for the AOP viewer map search.

Covers:
  - Search box indexes named features across loaded layers.
  - Typing filters a result dropdown.
  - Selecting a result flies the map to it, turns its layer on if hidden,
    and flashes the search-highlight layers.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, layer_visibility, set_toggle


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "results": "playwright_search_results.png",
    "sweden_creek": "playwright_search_sweden_creek.png",
    "ellis_rd": "playwright_search_ellis_rd.png",
    "tag_pavilion": "playwright_search_tag_pavilion.png",
    "tag_registration": "playwright_search_tag_registration.png",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def map_view(page) -> dict:
    return page.evaluate(
        """() => ({
          lng: window.map.getCenter().lng,
          lat: window.map.getCenter().lat,
          zoom: window.map.getZoom()
        })"""
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(600)

        print("\n== Initial state ==")
        check("search input exists", page.locator("#searchInput").count() == 1)
        search_box = page.locator("#searchInput").bounding_box()
        panel_box = page.locator(".panel").bounding_box()
        check(
            "search input is left of the layer panel",
            bool(search_box and panel_box and search_box["x"] < panel_box["x"]),
            f"search={search_box}, panel={panel_box}",
        )
        registry = page.evaluate("() => (typeof searchIndex !== 'undefined') ? searchIndex.length : -1")
        check(
            "search index populated with named features",
            registry > 10,
            f"searchIndex entries={registry}",
        )
        check(
            "search-highlight-line layer added hidden",
            layer_visibility(page, "search-highlight-line") == "none",
        )
        # Water is default-on as of Sprint 02 A2 (views_and_defaults.md). Flip
        # it off so we can verify that selecting a Sweden Creek result actually
        # re-enables it through the search auto-toggle path — otherwise the
        # later "auto-enabled by search" assertion would be trivially true.
        if page.locator("#showWater").is_checked():
            set_toggle(page, "showWater", False)
        check(
            "water layer toggled off before search",
            not page.locator("#showWater").is_checked(),
        )

        print("\n== Type 'sweden' ==")
        page.locator("#searchInput").click()
        page.locator("#searchInput").fill("sweden")
        page.wait_for_timeout(300)
        items = page.locator(".search-item")
        n_items = items.count()
        check("result dropdown shows matches", n_items > 0, f"{n_items} items")
        texts = [items.nth(i).inner_text() for i in range(n_items)]
        check(
            "Sweden Creek is a result",
            any("Sweden Creek" in t for t in texts),
            f"results={texts}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["results"]))

        print("\n== Select Sweden Creek ==")
        before = map_view(page)
        page.locator(".search-item", has_text="Sweden Creek").first.click()
        page.wait_for_timeout(450)
        check("water layer auto-enabled by search", page.locator("#showWater").is_checked())
        check(
            "search-highlight visible during flash",
            layer_visibility(page, "search-highlight-line") == "visible",
        )
        page.wait_for_timeout(1400)
        after = map_view(page)
        moved = abs(after["lng"] - before["lng"]) + abs(after["lat"] - before["lat"])
        zoomed = abs(after["zoom"] - before["zoom"])
        check(
            "map re-focused on the result",
            moved > 0.001 or zoomed > 0.3,
            f"center delta={moved:.5f}, zoom delta={zoomed:.2f}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["sweden_creek"]))
        page.wait_for_timeout(1600)
        check(
            "search-highlight hides after the flash",
            layer_visibility(page, "search-highlight-line") == "none",
        )

        print("\n== Search a trail: 'saturday' ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("saturday")
        page.wait_for_timeout(300)
        trail_items = page.locator(".search-item")
        trail_texts = [trail_items.nth(i).inner_text() for i in range(trail_items.count())]
        check(
            "multi-segment trail collapses to one result",
            trail_items.count() == 1,
            f"results={trail_texts}",
        )
        check(
            "trail result tagged kind=trail",
            trail_items.count() == 1 and "trail" in trail_texts[0],
            f"results={trail_texts}",
        )
        before_t = map_view(page)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)
        after_t = map_view(page)
        moved_t = abs(after_t["lng"] - before_t["lng"]) + abs(after_t["lat"] - before_t["lat"])
        check(
            "trails are searchable and re-focus the map",
            page.locator("#showTrails").is_checked()
            and (moved_t > 0.0005 or abs(after_t["zoom"] - before_t["zoom"]) > 0.3),
            f"center delta={moved_t:.5f}",
        )

        print("\n== Search a road: 'ellis' ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("ellis")
        page.wait_for_timeout(300)
        road_items = page.locator(".search-item")
        check("road results found", road_items.count() > 0, f"{road_items.count()} items")
        before_r = map_view(page)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1500)
        after_r = map_view(page)
        moved_r = abs(after_r["lng"] - before_r["lng"]) + abs(after_r["lat"] - before_r["lat"])
        check("Enter selects first result and moves the map", moved_r > 0.0005, f"delta={moved_r:.5f}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["ellis_rd"]))

        print("\n== Tag search: '#pavilion' ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("#pavilion")
        page.wait_for_timeout(300)
        tag_items = page.locator(".search-item")
        tag_texts = [tag_items.nth(i).inner_text() for i in range(tag_items.count())]
        check(
            "#pavilion returns the pavilion anchor",
            any("Pavilion" in t for t in tag_texts),
            f"results={tag_texts}",
        )
        # The dropdown should not be flooded with every session that used
        # the #pavilion tag (sessions are not indexed by tag, anchors are).
        # Anchor count today: pavilion + observed-finish ("Observed trail
        # finish near pavilion") both contain "pavilion" — but only the
        # pavilion anchor carries `#pavilion` as an alias. Tag-only mode
        # therefore returns exactly one result.
        check(
            "#pavilion tag-only query stays tight (one anchor, not every session)",
            tag_items.count() == 1,
            f"count={tag_items.count()} results={tag_texts}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["tag_pavilion"]))

        print("\n== Tag search: '#registration' (alias_of #pavilion) ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("#registration")
        page.wait_for_timeout(300)
        reg_items = page.locator(".search-item")
        reg_texts = [reg_items.nth(i).inner_text() for i in range(reg_items.count())]
        check(
            "#registration returns the Registration Desk anchor",
            any("Registration" in t for t in reg_texts),
            f"results={reg_texts}",
        )
        check(
            "#registration tag-only query stays tight (one anchor)",
            reg_items.count() == 1,
            f"count={reg_items.count()} results={reg_texts}",
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["tag_registration"]))

        print("\n== Tag search: '#observed-trailhead' ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("#observed-trailhead")
        page.wait_for_timeout(300)
        oh_items = page.locator(".search-item")
        oh_texts = [oh_items.nth(i).inner_text() for i in range(oh_items.count())]
        check(
            "#observed-trailhead returns the trailhead anchor",
            any("Trailhead" in t for t in oh_texts),
            f"results={oh_texts}",
        )
        check(
            "#observed-trailhead tag-only query stays tight (one anchor)",
            oh_items.count() == 1,
            f"count={oh_items.count()} results={oh_texts}",
        )

        print("\n== Tag prefix: '#pav' ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("#pav")
        page.wait_for_timeout(300)
        pre_items = page.locator(".search-item")
        pre_texts = [pre_items.nth(i).inner_text() for i in range(pre_items.count())]
        check(
            "leading-# prefix substrings into aliases",
            any("Pavilion" in t for t in pre_texts),
            f"results={pre_texts}",
        )

        print("\n== Bare 'pavilion' still resolves the anchor (name path) ==")
        page.locator("#searchInput").fill("")
        page.locator("#searchInput").fill("pavilion")
        page.wait_for_timeout(300)
        bare_items = page.locator(".search-item")
        bare_texts = [bare_items.nth(i).inner_text() for i in range(bare_items.count())]
        check(
            "bare 'pavilion' surfaces the pavilion anchor by name",
            any("Pavilion" in t for t in bare_texts),
            f"results={bare_texts}",
        )

        print("\n== Tag-search lands on the pavilion (fly + auto-enable) ==")
        page.locator("#searchInput").fill("")
        # Ensure the event-schedule layer is off, so we can verify the
        # tag-search auto-enables it on landing.
        page.evaluate(
            """() => {
              const t = document.getElementById('showEventSchedule');
              if (t && t.checked) { t.checked = false; t.dispatchEvent(new Event('change')); }
            }"""
        )
        check(
            "event-schedule layer starts off before tag click",
            not page.locator("#showEventSchedule").is_checked(),
        )
        page.locator("#searchInput").fill("#pavilion")
        page.wait_for_timeout(300)
        before_tag = map_view(page)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1400)
        after_tag = map_view(page)
        moved_tag = abs(after_tag["lng"] - before_tag["lng"]) + abs(after_tag["lat"] - before_tag["lat"])
        zoomed_tag = abs(after_tag["zoom"] - before_tag["zoom"])
        check(
            "tag search re-focuses the map",
            moved_tag > 0.001 or zoomed_tag > 0.3,
            f"center delta={moved_tag:.5f}, zoom delta={zoomed_tag:.2f}",
        )
        check(
            "tag search auto-enabled the event-schedule layer",
            page.locator("#showEventSchedule").is_checked(),
        )

        print("\n== Trail-network search (find a trail by number / name) ==")
        n_trail = page.evaluate("() => searchIndex.filter(e => e.kind === 'trail').length")
        check("trail edges indexed for search", n_trail > 50, f"trail entries={n_trail}")

        def trail_results(query: str) -> list[str]:
            page.locator("#searchInput").fill("")
            page.wait_for_timeout(120)
            page.locator("#searchInput").click()
            page.locator("#searchInput").fill(query)
            page.wait_for_timeout(320)
            items = page.locator(".search-item")
            return [items.nth(i).inner_text() for i in range(items.count())]

        r32 = trail_results("32")
        check(
            "two-digit number '32' returns trail 32 as the top result",
            bool(r32) and r32[0].split("\n")[0] == "32" and "trail" in r32[0].lower(),
            f"results={r32[:4]}",
        )
        # Single digit is allowed through the 2-char floor, and relevance ranking
        # must float the exact trail above building addresses that contain the digit.
        r9 = trail_results("9")
        check(
            "single-digit '9' returns trail 9 as the top result (not a building address)",
            bool(r9) and r9[0].split("\n")[0] == "9" and "trail" in r9[0].lower(),
            f"results={r9[:4]}",
        )
        r_named = trail_results("riot")
        check(
            "string-named trail 'Riot Hill' is searchable",
            any("riot hill" in t.lower() for t in r_named),
            f"results={r_named[:4]}",
        )

        print("\n== Select a trail: flies there + turns the network layer on ==")
        # Earlier trail searches in this run ('saturday', '32', '9') already
        # auto-enabled the trail layer, so reset it OFF first — otherwise the
        # "was none -> visible" precondition is stale and trivially fails. This
        # mirrors the showWater / showEventSchedule resets done above before
        # their auto-enable assertions. The aop-trail-network layer is driven by
        # #showAopTrailNetwork (the aopTrailNetworkToggle), not #showTrails.
        set_toggle(page, "showAopTrailNetwork", False)
        net_before = layer_visibility(page, "aop-trail-network")
        before_t = map_view(page)
        trail_results("32")
        page.locator(".search-item", has_text="32").first.click()
        page.wait_for_timeout(450)
        check(
            "trail search auto-enabled the aop-trail-network layer",
            net_before == "none" and layer_visibility(page, "aop-trail-network") == "visible",
            f"{net_before} -> {layer_visibility(page, 'aop-trail-network')}",
        )
        check(
            "search-highlight visible during flash",
            layer_visibility(page, "search-highlight-line") == "visible",
        )
        page.wait_for_timeout(1300)
        after_t = map_view(page)
        moved_t = abs(after_t["lng"] - before_t["lng"]) + abs(after_t["lat"] - before_t["lat"])
        check(
            "map re-focused on the trail",
            moved_t > 0.001 or abs(after_t["zoom"] - before_t["zoom"]) > 0.3,
            f"center delta={moved_t:.5f}, zoom delta={abs(after_t['zoom'] - before_t['zoom']):.2f}",
        )

        print("\n== Slice 3: catalogued trail rows carry a description line ==")

        def desc_for(query: str, row_first_token: str):
            """Type `query`, find the row whose first line == row_first_token,
            and return (row_locator, desc_count, desc_text)."""
            page.locator("#searchInput").fill("")
            page.wait_for_timeout(120)
            page.locator("#searchInput").click()
            page.locator("#searchInput").fill(query)
            page.wait_for_timeout(320)
            items = page.locator(".search-item")
            for i in range(items.count()):
                row = items.nth(i)
                first = row.inner_text().split("\n", 1)[0].strip()
                if first == row_first_token:
                    desc = row.locator(".search-result-desc")
                    dc = desc.count()
                    return row, dc, (desc.inner_text() if dc else "")
            return None, 0, ""

        # Trail 96 is catalogued (description: "A short loop with many rock and
        # ledge obstacles…"). Its row must show a truncated, ellipsised desc.
        _, dc96, dtext96 = desc_for("96", "96")
        check(
            "catalogued trail 96 row shows a .search-result-desc",
            dc96 == 1,
            f"desc_count={dc96}",
        )
        check(
            "trail 96 desc carries the catalog text",
            "rock and ledge" in dtext96,
            f"desc={dtext96!r}",
        )
        check(
            "trail 96 desc is truncated (~80 chars + ellipsis)",
            dtext96.endswith("…") and len(dtext96) <= 82,
            f"len={len(dtext96)} desc={dtext96!r}",
        )

        # Trail 11 (Ground Control) is catalogued and "11x" is NOT. Querying
        # "11" surfaces both, so the same dropdown proves the positive and the
        # negative case: 11 has a desc line, 11x has none.
        _, dc11, dtext11 = desc_for("11", "11")
        check(
            "catalogued trail 11 row shows a description",
            dc11 == 1 and bool(dtext11),
            f"desc_count={dc11} desc={dtext11!r}",
        )
        _, dc11x, _ = desc_for("11", "11X")
        check(
            "un-catalogued trail 11X has NO description line",
            dc11x == 0,
            f"desc_count={dc11x}",
        )

        # A non-trail dropdown (roads/addresses) must stay single-line: no
        # .search-result-desc node anywhere in the results.
        page.locator("#searchInput").fill("")
        page.wait_for_timeout(120)
        page.locator("#searchInput").fill("ellis")
        page.wait_for_timeout(320)
        non_trail_descs = page.locator(".search-item .search-result-desc").count()
        check(
            "non-trail (road/address) rows carry no description line",
            non_trail_descs == 0,
            f"unexpected desc nodes={non_trail_descs}",
        )

        print("\n== Console summary ==")
        check(
            "no console errors",
            len(console_errors) == 0,
            f"{len(console_errors)} error(s): {console_errors[:3]}",
        )

        browser.close()

    print("\nScreenshots:")
    for name in SCREENSHOTS.values():
        print(f"  - {OUTPUT_DIR / name}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
