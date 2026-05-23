#!/usr/bin/env python3
"""Playwright verification for the feature list panel.

Covers the per-feature visibility primitive added 2026-05-23:
  - Cemeteries: Ellis pre-ticked, other three default-unhidden by user; only
    Ellis draws on layer-on; ticking Bible adds it to the rendered set.
  - Buildings: 4 in-park (Ellis Cove Rd) pre-ticked, 198 others collapsed and
    default-off; bulk-toggling the "Other" group makes them visible.
  - Persistence: per-feature visibility survives a page reload
    (localStorage `aop_feature_visibility_v1`).
  - Search auto-unhide: searching an unticked cemetery flips its row on.

The card this verifies: brain/tasks/02_edit/poi_editor_v2.md.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[2]
WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:8001/")
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "cemeteries_ellis_only": "playwright_feature_list_cemeteries_ellis_only.png",
    "cemeteries_panel_open": "playwright_feature_list_cemeteries_panel_open.png",
    "cemeteries_bible_on": "playwright_feature_list_cemeteries_bible_on.png",
    "buildings_in_park_only": "playwright_feature_list_buildings_in_park_only.png",
    "buildings_panel_open": "playwright_feature_list_buildings_panel_open.png",
    "buildings_all_on": "playwright_feature_list_buildings_all_on.png",
    "after_reload": "playwright_feature_list_after_reload.png",
}

CEMETERY_LAYERS = ["cemetery-fill", "cemetery-outline", "cemetery-marker", "cemetery-label"]
BUILDING_LAYERS = [
    "building-footprint-fill",
    "building-footprint-outline",
    "building-footprint-aop-outline",
]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def set_toggle(page, toggle_id: str, target: bool) -> None:
    element = page.locator(f"#{toggle_id}")
    if element.is_checked() != target:
        element.click()
    page.wait_for_timeout(250)


def visible_count_in_source(page, geojson_url: str, layer_id: str, id_field: str) -> int:
    """Count distinct feature IDs that pass `layer_id`'s current visibility
    filter. Fetches the GeoJSON afresh (works with MapLibre's actual layer
    filter rather than internal source plumbing). Looks specifically for the
    ['in', ['get', idField], ['literal', [...]]] visibility clause we compose
    in the viewer; any feature whose id is in that literal counts."""
    return page.evaluate(
        """async ({url, layerId, idField}) => {
          if (!window.map || !window.map.getLayer(layerId)) return -1;
          const r = await fetch(url);
          if (!r.ok) return -1;
          const data = await r.json();
          const filter = window.map.getFilter(layerId);
          function findInLiteral(f) {
            if (!Array.isArray(f)) return null;
            if (f[0] === 'in' && Array.isArray(f[1]) && f[1][0] === 'get' && f[1][1] === idField) {
              return Array.isArray(f[2]) && f[2][0] === 'literal' ? f[2][1] : [];
            }
            if (f[0] === 'all') {
              for (let i = 1; i < f.length; i++) {
                const inner = findInLiteral(f[i]);
                if (inner !== null) return inner;
              }
            }
            return null;
          }
          const literal = filter ? findInLiteral(filter) : null;
          const ids = new Set();
          for (const feat of data.features || []) {
            const id = feat.properties && feat.properties[idField];
            if (id == null) continue;
            // No literal means no per-feature filter applied — every feature
            // is drawable as far as visibility is concerned.
            if (literal === null || literal.includes(id)) ids.add(id);
          }
          return ids.size;
        }""",
        {"url": geojson_url, "layerId": layer_id, "idField": id_field},
    )


def open_layer_editor(page, tune_key: str) -> None:
    page.evaluate(
        """(key) => {
          if (typeof toggleTunableExpansion === 'function') {
            toggleTunableExpansion(key);
          }
        }""",
        tune_key,
    )
    page.wait_for_timeout(250)


def feature_list_summary(page) -> dict:
    return page.evaluate(
        """() => {
          const root = document.getElementById('featureList');
          if (!root || root.hidden) return { open: false };
          const headingText = root.querySelector('.feature-list-heading')?.innerText || '';
          const groups = [...root.querySelectorAll('.feature-list-group')].map((g) => ({
            id: g.dataset.groupId,
            label: g.querySelector('.group-name')?.textContent || null,
            count: g.querySelector('.group-count')?.textContent || null,
            rows: [...g.querySelectorAll('.feature-row')].map((r) => ({
              id: r.dataset.featureId,
              name: r.querySelector('.feature-name')?.textContent,
              checked: r.querySelector('input[type=checkbox]')?.checked
            }))
          }));
          return { open: true, headingText, groups };
        }"""
    )


def toggle_feature_row(page, feature_id: str) -> None:
    page.evaluate(
        """(fid) => {
          const row = document.querySelector(`.feature-row[data-feature-id="${fid}"]`);
          if (!row) throw new Error('row ' + fid + ' not found');
          row.querySelector('input[type=checkbox]').click();
        }""",
        feature_id,
    )
    page.wait_for_timeout(150)


def toggle_group_bulk(page, group_id: str) -> None:
    page.evaluate(
        """(gid) => {
          const head = document.querySelector(`.feature-list-group[data-group-id="${gid}"] .feature-list-group-head`);
          if (!head) throw new Error('group ' + gid + ' not found');
          head.querySelector('input[type=checkbox]').click();
        }""",
        group_id,
    )
    page.wait_for_timeout(250)


def localstorage_visibility(page) -> dict:
    raw = page.evaluate("() => localStorage.getItem('aop_feature_visibility_v1')")
    return json.loads(raw) if raw else {}


def search_and_enter(page, query: str) -> None:
    box = page.locator("#searchInput")
    box.click()
    box.fill("")
    box.fill(query)
    page.wait_for_timeout(300)
    box.press("Enter")
    page.wait_for_timeout(1200)


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

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        # Wipe any state from a prior run so defaults apply.
        page.evaluate("() => localStorage.removeItem('aop_feature_visibility_v1')")
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        # ---- Cemeteries: Ellis-only default ----
        print("\n== Cemeteries: only Ellis draws by default ==")
        set_toggle(page, "showCemeteries", True)
        page.wait_for_timeout(500)
        visible = visible_count_in_source(page, "./data/aop_cemeteries.geojson", "cemetery-marker", "parcel_id")
        check("only 1 cemetery (Ellis) draws when layer is on", visible == 1, f"{visible} drawable")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["cemeteries_ellis_only"]))

        # ---- Open the cemetery layer editor and verify the feature list ----
        print("\n== Cemeteries feature list panel ==")
        open_layer_editor(page, "cemeteries")
        summary = feature_list_summary(page)
        check("feature list panel is open on cemeteries", summary.get("open") is True)
        if summary.get("open"):
            all_rows = summary["groups"][0]["rows"] if summary["groups"] else []
            check("cemeteries list shows 4 rows", len(all_rows) == 4, str(len(all_rows)))
            ellis = next((r for r in all_rows if "Ellis" in (r["name"] or "")), None)
            check("Ellis row pre-ticked", bool(ellis and ellis["checked"]),
                  str(ellis) if ellis else "missing")
            bible = next((r for r in all_rows if "Bible" in (r["name"] or "")), None)
            check("Bible row unchecked by default", bool(bible and not bible["checked"]),
                  str(bible) if bible else "missing")
            gilliam = next((r for r in all_rows if "Gilliam" in (r["name"] or "")), None)
            check("Gilliam row unchecked by default",
                  bool(gilliam and not gilliam["checked"]),
                  str(gilliam) if gilliam else "missing")
            tate = next((r for r in all_rows if "Tate" in (r["name"] or "")), None)
            check("Tate row unchecked by default",
                  bool(tate and not tate["checked"]),
                  str(tate) if tate else "missing")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["cemeteries_panel_open"]))

        # ---- Tick Bible → it should draw ----
        print("\n== Cemeteries: tick Bible, expect 2 drawable ==")
        toggle_feature_row(page, "093 003.00")  # Bible
        visible = visible_count_in_source(page, "./data/aop_cemeteries.geojson", "cemetery-marker", "parcel_id")
        check("2 cemeteries draw after ticking Bible", visible == 2, f"{visible} drawable")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["cemeteries_bible_on"]))

        # ---- Buildings: in-park only ----
        print("\n== Buildings: only 4 in-park draw by default ==")
        # Close cemetery drawer to avoid confusion
        open_layer_editor(page, "cemeteries")  # toggle off
        page.wait_for_timeout(150)
        set_toggle(page, "showBuildings", True)
        page.wait_for_timeout(500)
        visible = visible_count_in_source(page, "./data/aop_buildings.geojson", "building-footprint-fill", "build_id")
        check("only 4 buildings (in-park) draw when layer is on", visible == 4,
              f"{visible} drawable")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["buildings_in_park_only"]))

        # ---- Open buildings list ----
        print("\n== Buildings feature list panel ==")
        open_layer_editor(page, "buildings")
        summary = feature_list_summary(page)
        check("feature list panel is open on buildings", summary.get("open") is True)
        if summary.get("open"):
            groups = {g["id"]: g for g in summary["groups"]}
            check("in_park group present and labeled",
                  "in_park" in groups and groups["in_park"]["label"] == "In park")
            check("other group present and labeled",
                  "other" in groups
                  and groups["other"]["label"] == "Other buildings in 9-patch")
            if "in_park" in groups:
                in_park_rows = groups["in_park"]["rows"]
                check("4 in-park rows", len(in_park_rows) == 4, str(len(in_park_rows)))
                check("all in-park rows pre-ticked",
                      all(r["checked"] for r in in_park_rows),
                      str([r["checked"] for r in in_park_rows]))
                names = " | ".join(r["name"] or "" for r in in_park_rows)
                check("1010 row annotated as pavilion", "pavilion" in names.lower(), names)
            if "other" in groups:
                check("198 other rows",
                      len(groups["other"]["rows"]) == 198,
                      str(len(groups["other"]["rows"])))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["buildings_panel_open"]))

        # ---- Bulk-toggle "Other" → all 202 visible ----
        print("\n== Buildings: bulk-toggle 'Other' group ==")
        toggle_group_bulk(page, "other")
        visible = visible_count_in_source(page, "./data/aop_buildings.geojson", "building-footprint-fill", "build_id")
        check("all 202 buildings drawable after bulk-on", visible == 202,
              f"{visible} drawable")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["buildings_all_on"]))

        # ---- Persistence across reload ----
        print("\n== Persistence: reload and confirm Bible + bulk-Other stick ==")
        store = localstorage_visibility(page)
        check("localStorage key written", "buildings" in store and "cemeteries" in store,
              ", ".join(store.keys()))
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)
        set_toggle(page, "showCemeteries", True)
        set_toggle(page, "showBuildings", True)
        page.wait_for_timeout(500)
        post_cemetery = visible_count_in_source(page, "./data/aop_cemeteries.geojson", "cemetery-marker", "parcel_id")
        check("Bible still drawable after reload (2 cemeteries)",
              post_cemetery == 2, f"{post_cemetery} drawable")
        post_building = visible_count_in_source(page, "./data/aop_buildings.geojson", "building-footprint-fill", "build_id")
        check("Other group still bulk-on after reload (202 buildings)",
              post_building == 202, f"{post_building} drawable")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["after_reload"]))

        # ---- Search auto-unhide ----
        print("\n== Search auto-unhide a hidden cemetery ==")
        # First, untick Bible via the list, confirm it drops back to 1.
        open_layer_editor(page, "cemeteries")
        toggle_feature_row(page, "093 003.00")  # Bible off
        visible = visible_count_in_source(page, "./data/aop_cemeteries.geojson", "cemetery-marker", "parcel_id")
        check("Bible can be unticked again (back to 1 drawable)",
              visible == 1, f"{visible} drawable")
        # Search for Bible → should auto-unhide.
        search_and_enter(page, "bible cemetery")
        page.wait_for_timeout(900)
        visible = visible_count_in_source(page, "./data/aop_cemeteries.geojson", "cemetery-marker", "parcel_id")
        check("search auto-unhid Bible cemetery", visible >= 2, f"{visible} drawable")

        # ---- Console summary ----
        print("\n== Console summary ==")
        check("no console errors", len(console_errors) == 0,
              f"{len(console_errors)} error(s): {console_errors[:3]}")

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
