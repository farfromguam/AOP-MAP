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
  - POIs (third consumer, Slice 1 of poi_editor_v2.md): list renders with
    category-then-name sort; toggle composes the paint filter and persists;
    fly-to row click moves the camera. POI drawing UX itself is covered by
    playwright_verify_poi_editor.py — here we exercise only the list panel.

The card this verifies: brain/tasks/02_edit/poi_editor_v2.md.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, set_toggle


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "cemeteries_ellis_only": "playwright_feature_list_cemeteries_ellis_only.png",
    "cemeteries_panel_open": "playwright_feature_list_cemeteries_panel_open.png",
    "cemeteries_bible_on": "playwright_feature_list_cemeteries_bible_on.png",
    "buildings_in_park_only": "playwright_feature_list_buildings_in_park_only.png",
    "buildings_panel_open": "playwright_feature_list_buildings_panel_open.png",
    "buildings_all_on": "playwright_feature_list_buildings_all_on.png",
    "after_reload": "playwright_feature_list_after_reload.png",
    "pois_panel_open": "playwright_feature_list_pois_panel_open.png",
    "pois_one_off": "playwright_feature_list_pois_one_off.png",
    "pois_after_reload": "playwright_feature_list_pois_after_reload.png",
    "pois_move_banner": "playwright_feature_list_pois_move_banner.png",
    "pois_move_committed": "playwright_feature_list_pois_move_committed.png",
    "visitor_context_panel": "playwright_feature_list_visitor_context_panel.png",
    "visitor_context_moved": "playwright_feature_list_visitor_context_moved.png",
    "reveal_building_other": "playwright_feature_list_reveal_building_other.png",
    "reveal_via_map_click": "playwright_feature_list_reveal_via_map_click.png",
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
    # Editor POIs render into their own inline target inside the Map editor
    # section, not into the drawer's #featureList. Make sure that section
    # is expanded so the inline list is visible and its innerText is
    # readable (the move banner is a hidden-text read). For all other
    # tune_keys, expand the drawer the old way.
    if tune_key == "editorPois":
        page.evaluate(
            """() => {
              const section = document.querySelector('section[data-section="editor"]');
              if (section && section.classList.contains('collapsed')) {
                const btn = section.querySelector('.section-toggle');
                if (btn) btn.click();
              }
            }"""
        )
    else:
        page.evaluate(
            """(key) => {
              if (typeof toggleTunableExpansion === 'function') {
                toggleTunableExpansion(key);
              }
            }""",
            tune_key,
        )
    page.wait_for_timeout(250)


def feature_list_summary(page, tune_key: str = None) -> dict:
    # editorPois lives in #editorPoiList; everything else lives in the
    # shared drawer #featureList. Helper picks the right container so
    # call sites can stay schema-agnostic.
    container_id = "editorPoiList" if tune_key == "editorPois" else "featureList"
    return page.evaluate(
        """(rootId) => {
          const root = document.getElementById(rootId);
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
        }""",
        container_id,
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

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
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

        # ---- POIs: feature list consumer (Slice 1 of poi_editor_v2.md) ----
        # POIs are the third feature list consumer. They differ from buildings
        # and cemeteries: data is mutable (the user draws/deletes), so the
        # runtime re-registers through `refreshEditorSource()` on every change.
        # We push three POIs via page.evaluate (the drawing UX is exercised in
        # playwright_verify_poi_editor.py — here we only test the list panel).
        print("\n== POIs feature list panel (mutable data) ==")
        # Wipe POI + visibility state so this run is deterministic. POI
        # storage gets an explicit empty array (not removed outright) so
        # the editorPois seed loader's "fresh-install" gate stays closed
        # — the verifier owns its own three-POI push below and doesn't
        # want the seeded pavilion in the mix.
        page.evaluate(
            """() => {
              localStorage.setItem('aop_editor_pois_v1', '[]');
              localStorage.removeItem('aop_feature_visibility_v1');
            }"""
        )
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)
        # Confirm an empty editorPois starts the panel empty.
        set_toggle(page, "showEditorPois", True)
        open_layer_editor(page, "editorPois")
        empty_summary = feature_list_summary(page, "editorPois")
        check("editorPois panel opens (empty)", empty_summary.get("open") is True)
        check(
            "empty editorPois panel has 0 rows",
            sum(len(g["rows"]) for g in empty_summary.get("groups", [])) == 0,
        )
        # Inject three POIs of two categories so we can check the category-then-name sort.
        page.evaluate(
            """() => {
              const samples = [
                { id: 'poi_test_a', category: 'Pavilion', name: 'Pavilion A', coord: [-85.7515, 35.0905] },
                { id: 'poi_test_b', category: 'Pavilion', name: 'Pavilion B', coord: [-85.7525, 35.0915] },
                { id: 'poi_test_c', category: 'Landmark', name: 'Landmark Z', coord: [-85.7535, 35.0925] }
              ];
              for (const s of samples) {
                editorPois.push({
                  type: 'Feature',
                  geometry: { type: 'Point', coordinates: s.coord },
                  properties: {
                    id: s.id, layer: 'editor_poi', category: s.category,
                    name: s.name, created: new Date().toISOString()
                  }
                });
              }
              saveEditorPois();
              refreshEditorSource();
            }"""
        )
        page.wait_for_timeout(250)
        summary = feature_list_summary(page, "editorPois")
        check("editorPois panel is open", summary.get("open") is True)
        rows = summary["groups"][0]["rows"] if summary.get("groups") else []
        check("editorPois list shows 3 rows", len(rows) == 3, str(len(rows)))
        check("all 3 POI rows pre-ticked (default-visible)",
              all(r["checked"] for r in rows),
              str([r["checked"] for r in rows]))
        # Sort: Landmark < Pavilion by category, then Pavilion A < Pavilion B.
        names = [r["name"] for r in rows]
        check("rows sort by category then name",
              names == ["Landmark — Landmark Z", "Pavilion — Pavilion A", "Pavilion — Pavilion B"],
              str(names))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["pois_panel_open"]))

        # Untick one POI; confirm the visibility filter on editor-poi-circles
        # drops to 2 ids.
        toggle_feature_row(page, "poi_test_b")
        page.wait_for_timeout(200)
        circle_visible = page.evaluate(
            """() => {
              const f = window.map.getFilter('editor-poi-circles');
              function findIn(arr) {
                if (!Array.isArray(arr)) return null;
                if (arr[0] === 'in' && Array.isArray(arr[1]) && arr[1][1] === 'id') return arr[2][1];
                if (arr[0] === 'all') {
                  for (let i = 1; i < arr.length; i++) {
                    const inner = findIn(arr[i]);
                    if (inner !== null) return inner;
                  }
                }
                return null;
              }
              const literal = findIn(f);
              return literal ? literal.length : -1;
            }"""
        )
        check("editor-poi-circles filter drops to 2 visible ids", circle_visible == 2,
              f"{circle_visible} ids")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["pois_one_off"]))

        # Reload; confirm the untick persists.
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)
        set_toggle(page, "showEditorPois", True)
        open_layer_editor(page, "editorPois")
        post = feature_list_summary(page, "editorPois")
        post_rows = post["groups"][0]["rows"] if post.get("groups") else []
        check("3 POIs survive reload", len(post_rows) == 3, str(len(post_rows)))
        b = next((r for r in post_rows if r["id"] == "poi_test_b"), None)
        check("unticked POI stays unticked after reload",
              bool(b and b["checked"] is False),
              str(b))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["pois_after_reload"]))

        # Fly-to: click the row name, expect camera center to move toward the POI.
        before_center = page.evaluate("[map.getCenter().lng, map.getCenter().lat]")
        page.evaluate(
            """() => {
              const row = document.querySelector('.feature-row[data-feature-id="poi_test_a"]');
              row.querySelector('.feature-name').click();
            }"""
        )
        page.wait_for_timeout(1100)
        after_center = page.evaluate("[map.getCenter().lng, map.getCenter().lat]")
        # POI A is at [-85.7515, 35.0905]; after fly-to the center should be
        # near that. We accept any shift > 1e-5 deg as "the fly fired."
        dlon = abs(after_center[0] - before_center[0])
        dlat = abs(after_center[1] - before_center[1])
        check("fly-to row click moved the camera",
              dlon > 1e-5 or dlat > 1e-5,
              f"before={before_center} after={after_center}")

        # ---- POIs: drag-to-move primitive (Slice 2 of poi_editor_v2.md) ----
        # ✋ button on a row enters move mode; banner appears; next map click
        # commits new coordinates. Esc and the inline Cancel button both abort
        # without changing geometry. Mobile long-press is covered indirectly —
        # it triggers the same enterMoveMode() path the ✋ button hits.
        print("\n== POIs drag-to-move ==")

        def click_move_button(row_id: str) -> None:
            page.evaluate(
                """(fid) => {
                  const row = document.querySelector(`.feature-row[data-feature-id="${fid}"]`);
                  if (!row) throw new Error('row ' + fid + ' not found');
                  const btn = row.querySelector('.feature-move');
                  if (!btn) throw new Error('move button missing for ' + fid);
                  btn.click();
                }""",
                row_id,
            )
            page.wait_for_timeout(150)

        def banner_text():
            return page.evaluate(
                """() => {
                  const b = document.querySelector('.feature-list-move-banner');
                  return b ? b.innerText : null;
                }"""
            )

        def feature_coord(feature_id: str):
            return page.evaluate(
                "(fid) => editorPois.find((f) => f.properties.id === fid).geometry.coordinates",
                feature_id,
            )

        # Sanity: editorPois rows are visible in the inline list (the Map
        # editor section). The list now lives there, not in the drawer.
        summary = feature_list_summary(page, "editorPois")
        check("editorPois panel open before move tests",
              summary.get("open") is True)

        # --- 1) Move a POI by clicking ✋ then clicking the map ---
        before = feature_coord("poi_test_a")
        click_move_button("poi_test_a")
        check("move banner visible after ✋ click",
              "Move mode" in (banner_text() or ""),
              str(banner_text()))
        # The move-target row should be highlighted.
        check("move-target row has highlight class",
              page.evaluate(
                  "!!document.querySelector('.feature-row[data-feature-id=\"poi_test_a\"].move-target')"
              ))
        # MapLibre crosshair cursor.
        check("map cursor is crosshair while staged",
              page.evaluate("map.getCanvas().style.cursor") == "crosshair")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["pois_move_banner"]))

        # Click the map at a known pixel; convert back via map.unproject so we
        # can assert the new coord without baking projection math into the test.
        commit_pixel = (640, 400)
        expected_ll = page.evaluate(
            "(p) => { const ll = map.unproject(p); return [ll.lng, ll.lat]; }",
            list(commit_pixel),
        )
        # Click the actual canvas, not a div on top — bbox-relative coordinates.
        canvas_box = page.locator(".maplibregl-canvas").bounding_box()
        page.mouse.click(canvas_box["x"] + commit_pixel[0],
                         canvas_box["y"] + commit_pixel[1])
        page.wait_for_timeout(300)

        after = feature_coord("poi_test_a")
        check("POI coord changed after commit",
              after != before, f"before={before} after={after}")
        # Allow ~1e-3 deg slop because the canvas may scroll/zoom slightly.
        check("POI coord landed at clicked map point",
              abs(after[0] - expected_ll[0]) < 1e-3
              and abs(after[1] - expected_ll[1]) < 1e-3,
              f"expected≈{expected_ll} got={after}")
        check("move banner gone after commit", banner_text() is None,
              str(banner_text()))
        check("map cursor cleared after commit",
              page.evaluate("map.getCanvas().style.cursor") != "crosshair",
              page.evaluate("map.getCanvas().style.cursor"))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["pois_move_committed"]))

        # Reload; the moved coord should persist (editorPois is in localStorage).
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)
        post_move = page.evaluate(
            "() => editorPois.find((f) => f.properties.id === 'poi_test_a').geometry.coordinates"
        )
        check("moved coord persisted across reload",
              abs(post_move[0] - after[0]) < 1e-9
              and abs(post_move[1] - after[1]) < 1e-9,
              f"persisted={post_move} expected={after}")

        # --- 2) Esc cancels without changing the geometry ---
        open_layer_editor(page, "editorPois")
        before_esc = feature_coord("poi_test_b")
        click_move_button("poi_test_b")
        check("banner up before Esc",
              "Move mode" in (banner_text() or ""))
        page.keyboard.press("Escape")
        page.wait_for_timeout(200)
        check("Esc cleared the move banner", banner_text() is None,
              str(banner_text()))
        check("POI_B coord unchanged after Esc cancel",
              feature_coord("poi_test_b") == before_esc,
              str(feature_coord("poi_test_b")))

        # --- 3) Inline Cancel button cancels without changing geometry ---
        before_btn = feature_coord("poi_test_c")
        click_move_button("poi_test_c")
        check("banner up before Cancel-button",
              "Move mode" in (banner_text() or ""))
        page.evaluate(
            """() => document.querySelector('.feature-list-move-banner .move-cancel').click()"""
        )
        page.wait_for_timeout(200)
        check("Cancel button cleared the move banner",
              banner_text() is None, str(banner_text()))
        check("POI_C coord unchanged after Cancel-button",
              feature_coord("poi_test_c") == before_btn,
              str(feature_coord("poi_test_c")))

        # ---- Visitor context: second drag consumer (Slice 3 of poi_editor_v2.md) ----
        # Same move primitive, different consumer. Geometry override lands in
        # `aop_visitor_context_overrides_v1` localStorage and is replayed on
        # next page load, so a moved callout survives a reload without
        # touching the source geojson on disk.
        print("\n== Visitor-context drag (second consumer) ==")
        # Clean slate for the override store so this run is deterministic.
        page.evaluate(
            "() => localStorage.removeItem('aop_visitor_context_overrides_v1')"
        )
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)
        set_toggle(page, "showVisitorContext", True)
        open_layer_editor(page, "visitorContext")
        vc_summary = feature_list_summary(page)
        check("visitor-context panel opens", vc_summary.get("open") is True)
        vc_rows = vc_summary["groups"][0]["rows"] if vc_summary.get("groups") else []
        check("visitor-context list shows 2 rows", len(vc_rows) == 2, str(len(vc_rows)))
        names = sorted([r["name"] for r in vc_rows])
        check("rows are the two known callouts",
              names == sorted(["Monteagle plateau services",
                              "South Pittsburg / Kimball supply run"]),
              str(names))
        # The move button should exist on visitor-context rows.
        has_move_btn = page.evaluate(
            "!!document.querySelector('.feature-row[data-feature-id=\"Monteagle plateau services\"] .feature-move')"
        )
        check("✋ button present on visitor-context rows", has_move_btn is True)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["visitor_context_panel"]))

        # Read the original centroid of the Monteagle callout so we can assert
        # the move actually shifted it. We project, then take the average.
        target_name = "Monteagle plateau services"
        before_centroid = page.evaluate(
            """(name) => {
              const f = visitorContextData.features.find((x) => x.properties.name === name);
              const ring = f.geometry.coordinates[0];
              const last = ring.length > 1 ? ring.length - 1 : ring.length;
              let sx = 0, sy = 0;
              for (let i = 0; i < last; i++) { sx += ring[i][0]; sy += ring[i][1]; }
              return [sx / last, sy / last];
            }""",
            target_name,
        )

        # Click ✋ on the Monteagle row, then click the map at a known pixel.
        page.evaluate(
            """(name) => {
              const row = document.querySelector(`.feature-row[data-feature-id="${name}"]`);
              row.querySelector('.feature-move').click();
            }""",
            target_name,
        )
        page.wait_for_timeout(150)
        check("visitor-context banner up after ✋",
              "Move mode" in (banner_text() or ""),
              str(banner_text()))

        vc_commit_pixel = (700, 350)
        vc_expected_ll = page.evaluate(
            "(p) => { const ll = map.unproject(p); return [ll.lng, ll.lat]; }",
            list(vc_commit_pixel),
        )
        canvas_box = page.locator(".maplibregl-canvas").bounding_box()
        page.mouse.click(canvas_box["x"] + vc_commit_pixel[0],
                         canvas_box["y"] + vc_commit_pixel[1])
        page.wait_for_timeout(400)

        after_centroid = page.evaluate(
            """(name) => {
              const f = visitorContextData.features.find((x) => x.properties.name === name);
              const ring = f.geometry.coordinates[0];
              const last = ring.length > 1 ? ring.length - 1 : ring.length;
              let sx = 0, sy = 0;
              for (let i = 0; i < last; i++) { sx += ring[i][0]; sy += ring[i][1]; }
              return [sx / last, sy / last];
            }""",
            target_name,
        )
        check("visitor-context centroid shifted after commit",
              abs(after_centroid[0] - before_centroid[0]) > 1e-5
              or abs(after_centroid[1] - before_centroid[1]) > 1e-5,
              f"before={before_centroid} after={after_centroid}")
        # The centroid should now be near the clicked lngLat (allow 1e-3 slop).
        check("visitor-context centroid lands at clicked map point",
              abs(after_centroid[0] - vc_expected_ll[0]) < 1e-3
              and abs(after_centroid[1] - vc_expected_ll[1]) < 1e-3,
              f"expected≈{vc_expected_ll} got={after_centroid}")
        # Override store should now hold the moved entry.
        override = page.evaluate(
            "() => JSON.parse(localStorage.getItem('aop_visitor_context_overrides_v1') || '{}')"
        )
        check("override store has the moved callout",
              target_name in override and "geometry" in override[target_name],
              str(list(override.keys())))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["visitor_context_moved"]))

        # Reload; the moved centroid should reappear.
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)
        post_centroid = page.evaluate(
            """(name) => {
              const f = visitorContextData.features.find((x) => x.properties.name === name);
              const ring = f.geometry.coordinates[0];
              const last = ring.length > 1 ? ring.length - 1 : ring.length;
              let sx = 0, sy = 0;
              for (let i = 0; i < last; i++) { sx += ring[i][0]; sy += ring[i][1]; }
              return [sx / last, sy / last];
            }""",
            target_name,
        )
        check("moved visitor-context centroid survives reload",
              abs(post_centroid[0] - after_centroid[0]) < 1e-9
              and abs(post_centroid[1] - after_centroid[1]) < 1e-9,
              f"persisted={post_centroid} after_commit={after_centroid}")

        # ---- Map-click → panel reveal (user request 2026-05-23) ----
        # Clicking a feature on the map should expand its right-panel drawer,
        # expand the containing group if collapsed (buildings "Other"), scroll
        # the row into view, and flash it briefly. Existing popups stay.
        print("\n== Map-click → right-panel reveal ==")

        def reveal_state():
            return page.evaluate(
                """() => ({
                    expanded: expandedTuneKey,
                    revealedIds: [...document.querySelectorAll('.feature-row.revealed')]
                      .map((r) => r.dataset.featureId)
                  })"""
            )

        def close_any_drawer():
            page.evaluate(
                "() => { if (expandedTuneKey) toggleTunableExpansion(expandedTuneKey); }"
            )
            page.wait_for_timeout(120)

        # --- 1) revealFeatureInPanel directly: in-park building ---
        close_any_drawer()
        # Pick the 1010 Ellis Cove Road building (the in-park pavilion).
        pavilion_id = page.evaluate(
            """async () => {
              const r = await fetch('./data/aop_buildings.geojson');
              const d = await r.json();
              const f = d.features.find((x) =>
                String((x.properties || {}).address || '').startsWith('1010 '));
              return f && f.properties.build_id;
            }"""
        )
        check("pavilion build_id resolved", pavilion_id is not None,
              str(pavilion_id))
        page.evaluate("(id) => revealFeatureInPanel('buildings', id)", pavilion_id)
        page.wait_for_timeout(250)
        state = reveal_state()
        check("buildings drawer expanded after pavilion reveal",
              state["expanded"] == "buildings", str(state))
        check("pavilion row flashed (.revealed)",
              str(pavilion_id) in state["revealedIds"],
              str(state["revealedIds"]))

        # --- 2) revealFeatureInPanel auto-expands a collapsed group ---
        # Drop into the "Other" group: pick a building NOT in the in-park set.
        other_id = page.evaluate(
            """async () => {
              const r = await fetch('./data/aop_buildings.geojson');
              const d = await r.json();
              const f = d.features.find((x) =>
                (x.properties || {}).inside_aop_boundary !== true);
              return f && f.properties.build_id;
            }"""
        )
        check("non-in-park building build_id resolved", other_id is not None,
              str(other_id))
        # Re-render fresh so the "Other" group is in its default collapsed state.
        close_any_drawer()
        # Open buildings drawer to seed the collapsed default, then close again
        # so reveal has to handle a cold-start re-expansion.
        page.evaluate("() => toggleTunableExpansion('buildings')")
        page.wait_for_timeout(150)
        # Confirm "Other" is collapsed by default.
        other_collapsed = page.evaluate(
            "() => featureListRuntime.buildings.collapsed.other"
        )
        check("'Other' group collapsed by default",
              other_collapsed is True, str(other_collapsed))
        # Now ask the reveal to surface a row from the collapsed group.
        page.evaluate("(id) => revealFeatureInPanel('buildings', id)", other_id)
        page.wait_for_timeout(250)
        post_collapsed = page.evaluate(
            "() => featureListRuntime.buildings.collapsed.other"
        )
        check("reveal expanded the 'Other' group", post_collapsed is False,
              str(post_collapsed))
        # The other-id row should now exist in the DOM.
        row_present = page.evaluate(
            """(id) => !!document.querySelector(`.feature-row[data-feature-id="${id}"]`)""",
            other_id,
        )
        check("non-in-park row visible after reveal", row_present is True)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["reveal_building_other"]))

        # --- 3) revealFeatureInPanel for cemetery + visitor-context + POI ---
        close_any_drawer()
        page.evaluate("() => revealFeatureInPanel('cemeteries', '110 008.04')")  # Ellis
        page.wait_for_timeout(200)
        state = reveal_state()
        check("cemeteries drawer expanded after cemetery reveal",
              state["expanded"] == "cemeteries", str(state))
        check("Ellis row flashed", "110 008.04" in state["revealedIds"],
              str(state["revealedIds"]))

        close_any_drawer()
        page.evaluate(
            "() => revealFeatureInPanel('visitorContext', 'Monteagle plateau services')"
        )
        page.wait_for_timeout(200)
        state = reveal_state()
        check("visitor-context drawer expanded after callout reveal",
              state["expanded"] == "visitorContext", str(state))
        check("Monteagle row flashed",
              "Monteagle plateau services" in state["revealedIds"],
              str(state["revealedIds"]))

        close_any_drawer()
        # Collapse the Map editor section so we can prove reveal re-opens it.
        page.evaluate(
            """() => {
              const section = document.querySelector('section[data-section="editor"]');
              if (section && !section.classList.contains('collapsed')) {
                section.querySelector('.section-toggle')?.click();
              }
            }"""
        )
        page.wait_for_timeout(120)
        page.evaluate("() => revealFeatureInPanel('editorPois', 'poi_test_a')")
        page.wait_for_timeout(200)
        state = reveal_state()
        # Editor POIs render into the Map editor section, not the drawer, so
        # reveal opens that section instead of toggling expandedTuneKey.
        editor_section_open = page.evaluate(
            """() => {
              const section = document.querySelector('section[data-section="editor"]');
              return !!section && !section.classList.contains('collapsed');
            }"""
        )
        check("Map editor section opened after POI reveal",
              editor_section_open is True, str(editor_section_open))
        check("poi_test_a row flashed",
              "poi_test_a" in state["revealedIds"],
              str(state["revealedIds"]))

        # --- 4) Real map click → reveal (binding wiring, end-to-end) ---
        # Visitor-context polygons are large and easy to hit-test deterministically.
        # Click on Monteagle's centroid; both popup and panel reveal should fire.
        close_any_drawer()
        # Make sure the visitor-context layer is drawing.
        set_toggle(page, "showVisitorContext", True)
        page.wait_for_timeout(200)
        monteagle_pixel = page.evaluate(
            """() => {
              const f = visitorContextData.features.find((x) =>
                x.properties.name === 'Monteagle plateau services');
              const ring = f.geometry.coordinates[0];
              const last = ring.length > 1 ? ring.length - 1 : ring.length;
              let sx = 0, sy = 0;
              for (let i = 0; i < last; i++) { sx += ring[i][0]; sy += ring[i][1]; }
              const p = map.project([sx / last, sy / last]);
              return [p.x, p.y];
            }"""
        )
        canvas_box = page.locator(".maplibregl-canvas").bounding_box()
        page.mouse.click(canvas_box["x"] + monteagle_pixel[0],
                         canvas_box["y"] + monteagle_pixel[1])
        page.wait_for_timeout(400)
        state = reveal_state()
        check("clicking the callout on the map opened its drawer",
              state["expanded"] == "visitorContext", str(state))
        check("clicking the callout flashed its row",
              "Monteagle plateau services" in state["revealedIds"],
              str(state["revealedIds"]))
        # Popup should still fire alongside the reveal.
        popup_count = page.evaluate(
            "() => document.querySelectorAll('.maplibregl-popup').length"
        )
        check("popup still appears alongside reveal", popup_count >= 1,
              f"popup_count={popup_count}")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["reveal_via_map_click"]))

        # --- 5) Move mode suppresses panel reveal ---
        # Closing the popup first so the next click is unambiguous.
        page.evaluate(
            "() => document.querySelectorAll('.maplibregl-popup-close-button').forEach((b) => b.click())"
        )
        page.wait_for_timeout(150)
        # The visitor-context drawer is already open from the previous reveal;
        # only open it if it isn't (avoid the toggle-closes-it footgun).
        page.evaluate(
            "() => { if (expandedTuneKey !== 'visitorContext') toggleTunableExpansion('visitorContext'); }"
        )
        page.wait_for_timeout(150)
        page.evaluate(
            """() => {
              const row = document.querySelector('.feature-row[data-feature-id="South Pittsburg / Kimball supply run"]');
              row.querySelector('.feature-move').click();
            }"""
        )
        page.wait_for_timeout(150)
        check("move banner appeared in move-suppression test",
              "Move mode" in (banner_text() or ""))
        # While staged, click the OTHER callout. Reveal must NOT switch drawers
        # (we never leave visitorContext anyway, but the row should not flash
        # because the click is the move-commit, not a reveal).
        before_revealed = page.evaluate(
            "() => [...document.querySelectorAll('.feature-row.revealed')].map((r) => r.dataset.featureId)"
        )
        page.mouse.click(canvas_box["x"] + monteagle_pixel[0],
                         canvas_box["y"] + monteagle_pixel[1])
        page.wait_for_timeout(300)
        after_revealed = page.evaluate(
            "() => [...document.querySelectorAll('.feature-row.revealed')].map((r) => r.dataset.featureId)"
        )
        # No NEW reveal flash should have been added by this click.
        new_reveals = [r for r in after_revealed if r not in before_revealed]
        check("no new reveal flash during move commit",
              len(new_reveals) == 0,
              f"new_reveals={new_reveals}")

        # ---- Export Settings v2: payload carries runtime overrides ----
        # At this point in the run we have: a moved Monteagle callout in
        # localStorage, three test POIs, and several per-feature visibility
        # entries. A v2 export should round-trip every one of those.
        print("\n== Export Settings v2 (runtime overrides round-trip) ==")
        payload = page.evaluate("() => buildExportPayload()")
        check("schema bumped to v2",
              payload.get("schema") == "aop-viewer-preset-settings-v2",
              str(payload.get("schema")))
        check("runtime_overrides key present",
              "runtime_overrides" in payload, str(list(payload.keys())))
        overrides = payload.get("runtime_overrides", {}) or {}
        check("visitor_context_overrides key present",
              "visitor_context_overrides" in overrides)
        check("editor_pois key present",
              "editor_pois" in overrides)
        check("feature_visibility key present",
              "feature_visibility" in overrides)
        # The moved Monteagle entry should be there with a geometry block.
        vc = overrides.get("visitor_context_overrides", {}) or {}
        check("Monteagle override round-trips in export",
              "Monteagle plateau services" in vc
              and "geometry" in (vc.get("Monteagle plateau services") or {}),
              str(list(vc.keys())))
        # The three test POIs should round-trip.
        poi_ids = [
            f.get("properties", {}).get("id")
            for f in (overrides.get("editor_pois", []) or [])
        ]
        check("all three test POIs round-trip in export",
              all(p in poi_ids for p in ["poi_test_a", "poi_test_b", "poi_test_c"]),
              str(poi_ids))
        # Per-feature visibility for visitor-context should be in the bag too.
        fv = overrides.get("feature_visibility", {}) or {}
        check("feature_visibility carries visitorContext entries",
              "visitorContext" in fv,
              str(list(fv.keys())))

        # ---- Per-section Export/Import (user direction 2026-05-23) ----
        # The three target sections (derived-layers, source-layers, editor)
        # each get their own ↑/↓ in their header. A small export carries
        # only that section's toggles/sliders/paints/runtime. An import
        # only touches that section.
        print("\n== Per-section Export / Import ==")
        # Every targeted section header carries the export-only ↑ button.
        # Import is intentionally not exposed in the UI per user direction
        # 2026-05-23 ("I will pass to you or put directly in code") — the
        # apply functions still exist for code-level use.
        # Publishable joined the per-section export set on 2026-05-25
        # (right_panel_editor_consistency build card). POI section is still
        # excluded — its toggles are derived bindings of `show*` IDs that
        # sectionInputs does not collect.
        for sid in ("derived-layers", "source-layers", "editor", "publishable"):
            exp = page.evaluate(
                """(sid) => !!document.querySelector(`[data-section-export="${sid}"]`)""",
                sid,
            )
            check(f"{sid}: ↑ Export button present", exp is True)
        # Per-section import buttons were retired — none should exist.
        any_import_btn = page.evaluate(
            "() => !!document.querySelector('[data-section-import]')"
        )
        check("no per-section ↓ Import buttons", any_import_btn is False)
        # POI + Notes sections do NOT get export.
        no_poi = page.evaluate(
            "!!document.querySelector('[data-section-export=\"poi\"]') === false"
        )
        check("poi section has no export button", no_poi is True)

        # --- editor section round-trip ---
        # Snapshot the editor payload, mutate, then restore.
        editor_before = page.evaluate("() => buildSectionPayload('editor')")
        check("editor payload schema is aop-section-state-v1",
              editor_before.get("schema") == "aop-section-state-v1",
              str(editor_before.get("schema")))
        check("editor payload tagged with section",
              editor_before.get("section") == "editor",
              str(editor_before.get("section")))
        check("editor payload carries showEditorPois toggle",
              "showEditorPois" in (editor_before.get("toggles") or {}),
              str(list((editor_before.get("toggles") or {}).keys())))
        editor_pois_before = editor_before.get("runtime", {}).get("editor_pois") or []
        check("editor payload carries the 3 test POIs",
              len(editor_pois_before) == 3,
              f"{len(editor_pois_before)} POIs")

        # Wipe the editor data, confirm everything's gone, then import the snapshot.
        page.evaluate(
            """() => {
              editorPois.length = 0;
              saveEditorPois();
              refreshEditorSource();
            }"""
        )
        page.wait_for_timeout(150)
        cleared = page.evaluate("() => editorPois.length")
        check("editor POIs cleared before import", cleared == 0,
              f"editorPois.length={cleared}")
        page.evaluate("(payload) => applySectionPayload(payload)", editor_before)
        page.wait_for_timeout(200)
        restored = page.evaluate("() => editorPois.length")
        check("editor section import restored 3 POIs", restored == 3,
              f"editorPois.length={restored}")

        # --- source-layers section round-trip ---
        source_payload = page.evaluate("() => buildSectionPayload('source-layers')")
        check("source-layers payload has cemeteries visibility",
              "cemeteries" in (source_payload.get("runtime", {}).get("feature_visibility") or {}),
              str((source_payload.get("runtime", {}) or {}).get("feature_visibility", {})))
        check("source-layers payload has buildings visibility",
              "buildings" in (source_payload.get("runtime", {}).get("feature_visibility") or {}))
        # Source-layers payload should NOT include visitor-context overrides
        # (the runtime + toggle live together in the publishable section now).
        check("source-layers payload does NOT carry visitor-context overrides",
              "visitor_context_overrides" not in (source_payload.get("runtime") or {}))

        # --- publishable section round-trip ---
        # The #showVisitorContext toggle lives in the publishable section, so
        # the visitor-context override + per-feature visibility slice live here
        # too. No per-section export *button* is exposed for publishable, but
        # buildSectionPayload still works for code-level round-trips.
        publishable_payload = page.evaluate("() => buildSectionPayload('publishable')")
        check("publishable payload carries visitor_context_overrides",
              "visitor_context_overrides" in (publishable_payload.get("runtime") or {}),
              str(list((publishable_payload.get("runtime") or {}).keys())))
        check("publishable payload carries visitor-context-fill paint",
              "visitor-context-fill" in (publishable_payload.get("paints") or {}),
              str(list((publishable_payload.get("paints") or {}).keys()))[:200])

        # --- derived-layers section round-trip ---
        # After the SECTION_RUNTIME move, derived-layers no longer carries any
        # visitor-context state; the background paint stays under derived.
        derived_payload = page.evaluate("() => buildSectionPayload('derived-layers')")
        check("derived-layers payload does NOT carry visitor_context_overrides",
              "visitor_context_overrides" not in (derived_payload.get("runtime") or {}))
        check("derived-layers payload still carries background paint",
              "background" in (derived_payload.get("paints") or {}),
              str(list((derived_payload.get("paints") or {}).keys()))[:200])

        # --- Wrong-section guard: an editor payload pasted into source-layers fails ---
        rejected = page.evaluate(
            """(payload) => {
              try { applySectionPayload({ ...payload, section: 'editor' }); return null; }
              catch (err) { return err.message; }
            }""",
            {"schema": "aop-section-state-v1", "section": "editor",
             "toggles": {}, "sliders": {}, "paints": {}, "runtime": {}},
        )
        # applySectionPayload itself doesn't check the section/button mismatch —
        # that's the importSectionFromPrompt wrapper's job. Verify the data path
        # is sound:
        check("applySectionPayload accepts a well-formed editor payload",
              rejected is None,
              str(rejected))
        bad_schema = page.evaluate(
            """() => {
              try { applySectionPayload({ schema: 'wrong', section: 'editor' }); return null; }
              catch (err) { return err.message; }
            }"""
        )
        check("applySectionPayload rejects wrong schema",
              "aop-section-state-v1" in (bad_schema or ""),
              str(bad_schema))

        # --- Snapshot Preset / Export Settings / Import-all buttons retired ---
        no_snapshot = page.evaluate(
            "() => !document.getElementById('snapshotPreset')"
        )
        check("snapshotPreset button removed", no_snapshot is True)
        no_export_settings = page.evaluate(
            "() => !document.getElementById('exportSettings')"
        )
        check("exportSettings button removed", no_export_settings is True)
        no_import_all = page.evaluate(
            "() => !document.getElementById('importAll')"
        )
        check("importAll button removed", no_import_all is True)
        export_all_present = page.evaluate(
            "() => !!document.getElementById('exportAll')"
        )
        check("Export-all button still present", export_all_present is True)

        # --- Per-feature copy button: drop-in GeoJSON Feature ---
        # Re-open the visitor-context drawer; each row should now carry an ↑
        # button next to fly/move. Triggering it should leave the clipboard
        # with a flat geojson Feature (type/properties/geometry) — paste-ready
        # for website/data/*.geojson.
        print("\n== Per-feature copy → drop-in GeoJSON Feature ==")
        # Grant clipboard read so we can verify what was copied.
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        page.evaluate(
            "() => { if (expandedTuneKey !== 'visitorContext') toggleTunableExpansion('visitorContext'); }"
        )
        page.wait_for_timeout(150)
        has_copy_btn = page.evaluate(
            """() => !!document.querySelector(
              '.feature-row[data-feature-id="Monteagle plateau services"] .feature-copy'
            )"""
        )
        check("per-feature ↑ copy button present on visitor-context row",
              has_copy_btn is True)
        page.evaluate(
            """() => document.querySelector(
              '.feature-row[data-feature-id="Monteagle plateau services"] .feature-copy'
            ).click()"""
        )
        page.wait_for_timeout(400)
        copied = page.evaluate("() => navigator.clipboard.readText()")
        try:
            feature_payload = json.loads(copied)
        except Exception as err:
            feature_payload = None
            check("clipboard holds valid JSON", False, f"{err}: {copied[:120]}")
        if feature_payload is not None:
            check("per-feature copy emits a GeoJSON Feature",
                  feature_payload.get("type") == "Feature",
                  str(feature_payload.get("type")))
            check("copied Feature carries Monteagle properties",
                  feature_payload.get("properties", {}).get("name")
                  == "Monteagle plateau services",
                  str(feature_payload.get("properties", {}).get("name")))
            check("copied Feature carries a Polygon geometry",
                  feature_payload.get("geometry", {}).get("type") == "Polygon",
                  str(feature_payload.get("geometry", {}).get("type")))
            # The geometry should reflect the just-moved centroid from the
            # earlier visitor-context drag, not the source-file default.
            ring = feature_payload.get("geometry", {}).get("coordinates", [[]])[0]
            n = max(len(ring) - 1, 1)
            cx = sum(p[0] for p in ring[:n]) / n
            cy = sum(p[1] for p in ring[:n]) / n
            check("copied geometry centroid matches the moved position",
                  abs(cx - vc_expected_ll[0]) < 1e-3
                  and abs(cy - vc_expected_ll[1]) < 1e-3,
                  f"copied≈({cx},{cy}) expected≈{vc_expected_ll}")

        # Same path for a POI row — must emit a Point Feature. editorPois
        # uses the inline accordion editor, so `⧉ Copy GeoJSON` lives inside
        # the per-leaf editor pane (.feature-row-editor .editor-action),
        # not on the row itself. Expand the leaf first, then click the
        # action labeled "⧉ Copy GeoJSON".
        page.evaluate(
            "() => { const s = document.querySelector('.panel-section[data-section=\"editor\"]');"
            " if (s && s.classList.contains('collapsed')) s.querySelector('.section-toggle').click(); }"
        )
        page.wait_for_timeout(120)
        page.evaluate(
            "() => toggleFeatureEditor('editorPois', 'poi_test_a')"
        )
        page.wait_for_timeout(200)
        page.evaluate(
            """() => {
              const editor = document.querySelector(
                '.feature-row-editor[data-feature-id="poi_test_a"]'
              );
              const btn = [...editor.querySelectorAll('.editor-action')]
                .find((b) => b.textContent.includes('Copy GeoJSON'));
              btn.click();
            }"""
        )
        page.wait_for_timeout(300)
        poi_copied = page.evaluate("() => navigator.clipboard.readText()")
        try:
            poi_payload = json.loads(poi_copied)
        except Exception:
            poi_payload = None
        if poi_payload is not None:
            check("POI copy emits a GeoJSON Feature",
                  poi_payload.get("type") == "Feature")
            check("POI copy carries Point geometry",
                  poi_payload.get("geometry", {}).get("type") == "Point",
                  str(poi_payload.get("geometry", {}).get("type")))
            check("POI copy carries the POI id",
                  poi_payload.get("properties", {}).get("id") == "poi_test_a",
                  str(poi_payload.get("properties", {}).get("id")))

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
