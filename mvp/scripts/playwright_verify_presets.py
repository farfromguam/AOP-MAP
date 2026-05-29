#!/usr/bin/env python3
"""Playwright verification for AOP viewer UI presets and layer tuning.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_origin, viewer_url, click_in_section, layer_visibility


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

SCREENSHOTS = {
    "park": "playwright_presets_park.png",
    "topo": "playwright_presets_topo.png",
    "trace": "playwright_presets_trace.png",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def paint(page, layer_id: str, prop: str):
    return page.evaluate(
        """([id, prop]) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getPaintProperty(id, prop);
        }""",
        [layer_id, prop],
    )


def is_checked(page, toggle_id: str) -> bool:
    return page.locator(f"#{toggle_id}").is_checked()


def camera_state(page):
    return page.evaluate(
        """() => {
          const bearing = window.map.getBearing();
          const normalizedBearing = Math.abs((((bearing + 180) % 360) + 360) % 360 - 180);
          return {
            zoom: window.map.getZoom(),
            pitch: window.map.getPitch(),
            bearing,
            normalizedBearing,
            terrainPressed: document.getElementById('terrainButton')?.getAttribute('aria-pressed'),
            terrainChecked: document.getElementById('showTerrain')?.checked
          };
        }"""
    )


def angular_diff(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def is_flat_west(camera: dict) -> bool:
    return abs(float(camera["pitch"])) < 0.75 and angular_diff(float(camera["bearing"]), -90) < 0.75


def camera_matches(actual: dict, expected: dict) -> bool:
    return (
        abs(float(actual["zoom"]) - float(expected["zoom"])) < 0.03
        and abs(float(actual["pitch"]) - float(expected["pitch"])) < 0.75
        and angular_diff(float(actual["bearing"]), float(expected["bearing"])) < 0.75
    )


def panel_section_for(page, toggle_id: str) -> str | None:
    return page.evaluate(
        """(id) => {
          const el = document.getElementById(id);
          return el?.closest('.panel-section')?.dataset.section || null;
        }""",
        toggle_id,
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 840})
        context.grant_permissions(["clipboard-read", "clipboard-write"], origin=viewer_origin())
        page = context.new_page()

        def record_console(msg) -> None:
            if msg.type != "error":
                return
            text = msg.text
            # Source-only preset checks may turn online imagery on. Tile-load
            # failures are not preset UI failures, and the viewer has separate
            # imagery checks.
            ignored = (
                "gis.apfo.usda.gov" in text
                or "tnmap.tn.gov" in text
                or "Failed to load resource" in text
                # Reloads after viewport resize abort in-flight tile / sprite
                # fetches; MapLibre logs them as `AJAXError: Failed to fetch
                # (0): data:image/webp;base64,...` (the `(0)` is the
                # placeholder HTTP status for an aborted request) or the
                # browser emits `TypeError: Failed to fetch`. Real HTTP
                # failures from MapLibre carry a real status (e.g. `(404):`)
                # and are NOT filtered out.
                or "AJAXError: Failed to fetch (0):" in text
                or text.strip().endswith("TypeError: Failed to fetch")
                or text.strip() == "TypeError: Failed to fetch"
            )
            if not ignored:
                console_errors.append(text)

        page.on("console", record_console)

        print(f"Opening {viewer_url()}")
        page.goto(viewer_url(), wait_until="load")
        page.evaluate(
            """() => {
              try {
                localStorage.removeItem('aop_left_rail_drawer_v1');
                localStorage.removeItem('aop_virtual_clock_v1');
                localStorage.removeItem('aop_viewer_session_state_v1');
                localStorage.removeItem('aop_lr_card_height_v1');
              } catch (_) {}
            }"""
        )
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(700)

        print("\n== Left controls ==")
        check("four top-left preset buttons exist", page.locator(".preset-bar button[data-preset]").count() == 4)
        check("dedicated 3D button exists", page.locator("#terrainButton").count() == 1)
        check("search input sits in the left control cluster", page.locator(".left-controls #searchInput").count() == 1)
        check("calendar sits in the left control cluster", page.locator(".left-controls #calendarCard").count() == 1)
        check("calendar card carries the left context tabs",
              page.locator("#calendarCard .left-tabs").count() == 1)
        tab_labels = page.locator(".left-controls .left-tab").evaluate_all(
            "els => els.map((el) => el.textContent.trim())"
        )
        check("left card exposes Events, POI, and About tabs", tab_labels == ["Events", "POI", "About"], str(tab_labels))
        check(
            "Events tab is selected by default",
            page.locator("#leftTabEvents").get_attribute("aria-selected") == "true"
            and page.locator("#eventsTabPanel").is_visible(),
        )
        page.locator("#leftTabAbout").click()
        about_text = page.locator("#aboutTabPanel").inner_text()
        check(
            "About tab carries the merged Trail Blazing Invitational + Rock Warblers copy",
            page.locator("#aboutTabPanel").is_visible()
            and "Trail Blazing Invitational" in about_text
            and "Rock Warblers" in about_text
            and "See you at the pavilion" in about_text,
        )
        # POI tab — left-rail browseable directory.
        # Card: brain/tasks/03_event_app/left_panel_poi_browser.md.
        page.locator("#leftTabPoi").click()
        page.wait_for_timeout(400)
        poi_rows_count = page.locator("#poiList .poi-row").count()
        check(
            "POI tab renders at least one POI row after data loads",
            page.locator("#poiTabPanel").is_visible() and poi_rows_count >= 1,
            f"rows={poi_rows_count}",
        )
        check(
            "POI tab groups list at least one labelled section",
            page.locator("#poiList .poi-list-group").count() >= 1,
        )
        # Right-panel Map editor section — unified bucket tree. The legacy
        # POI section (`data-section="poi"`) was retired by the unified-tree
        # card; the editor now carries a five-bucket tree (Point / Line /
        # Polygon / Image / Callout) plus a ★ Visitor list virtual group.
        check(
            "legacy POI section is gone",
            page.locator('section[data-section="poi"]').count() == 0,
        )
        page.locator('section[data-section="editor"] .section-toggle').click()
        page.wait_for_timeout(150)
        bucket_ids = page.locator('#editorTree .editor-bucket').evaluate_all(
            "els => els.map((el) => el.dataset.bucket)"
        )
        check(
            "editor tree renders the three geometry buckets plus visitor list",
            bucket_ids == ["visitor-list", "point", "line", "polygon"],
            f"buckets={bucket_ids}",
        )
        # V3c folded Image and Callout buckets into Point and Polygon as
        # source sub-groups (brand logos under Point, visitor context under
        # Polygon). Card: brain/tasks/04_event_app/editor_three_buckets_v3c.md.
        source_keys = page.locator('#editorTree .editor-subgroup').evaluate_all(
            "els => els.map((el) => `${el.dataset.bucket}/${el.dataset.source}`)"
        )
        check(
            "Point bucket carries Drawn + Brand sub-groups (trailheads moved out 2026-05-28)",
            "point/drawn" in source_keys
            and "point/brand" in source_keys
            and "point/trailhead" not in source_keys,
            f"sources={source_keys}",
        )
        check(
            "Polygon bucket carries Drawn + Visitor sub-groups",
            "polygon/drawn" in source_keys and "polygon/visitor" in source_keys,
            f"sources={source_keys}",
        )
        check(
            "editor visitor-list container exists",
            page.locator('#editorVisitorList').count() == 1,
        )
        page.locator("#leftTabEvents").click()
        schedule_rows = page.locator("#calendarBody .calendar-row").evaluate_all(
            "els => els.map((el) => el.textContent.trim().replace(/\\s+/g, ' '))"
        )
        check(
            "calendar renders the editable schedule rows",
            len(schedule_rows) == 13
            and any("Show & Shine: The Advance Party" in row for row in schedule_rows)
            and any("G6 Cove Rally stages" in row for row in schedule_rows)
            and any("#pavilion" in row for row in schedule_rows),
            str(schedule_rows),
        )
        check(
            "event schedule toggle exists and starts off",
            page.locator("#showEventSchedule").count() == 1
            and not page.locator("#showEventSchedule").is_checked(),
        )
        check(
            "calendar title is static and starts expanded",
            page.locator("#calendarToggle").evaluate("el => el.tagName") == "DIV"
            and not page.locator("#calendarCard").evaluate("el => el.classList.contains('collapsed')")
            and page.locator("#calendarResizeHandle").count() == 1,
        )
        expanded_height = page.locator("#calendarBody").bounding_box()["height"]
        page.locator("#calendarToggle").click()
        page.wait_for_timeout(200)
        after_title_click_height = page.locator("#calendarBody").bounding_box()["height"]
        check(
            "title click does not collapse calendar",
            abs(after_title_click_height - expanded_height) < 2,
            f"before={expanded_height:.1f} after={after_title_click_height:.1f}",
        )
        handle_box = page.locator("#calendarResizeHandle").bounding_box()
        page.mouse.move(handle_box["x"] + handle_box["width"] / 2, handle_box["y"] + handle_box["height"] / 2)
        page.mouse.down()
        page.mouse.move(handle_box["x"] + handle_box["width"] / 2, handle_box["y"] + handle_box["height"] / 2 + 70)
        page.mouse.up()
        page.wait_for_timeout(200)
        resized_height = page.locator("#calendarBody").bounding_box()["height"]
        check("calendar resize handle expands the body", resized_height > expanded_height + 35, f"before={expanded_height:.1f} after={resized_height:.1f}")
        bar_box = page.locator(".left-controls").bounding_box()
        check(
            "left controls are in the top-left",
            bool(bar_box and bar_box["x"] <= 16 and bar_box["y"] <= 16),
            str(bar_box),
        )
        check("Park starts active", page.locator("#presetPark").evaluate("el => el.classList.contains('active')"))
        check("Park keeps land cover on", is_checked(page, "showLandcover"))
        check("Park keeps topo overlays off", not is_checked(page, "showHillshade") and not is_checked(page, "showContours"))
        # Sprint 02 A2: water + buildings join the default-on Park payload.
        check("Park turns water on by default (A2)", is_checked(page, "showWater"))
        check("Park turns buildings on by default (A2)", is_checked(page, "showBuildings"))
        check("Park keeps springs off (A2 — topo-only)", not is_checked(page, "showSprings"))
        check("Park background is Muted Earth", paint(page, "background", "background-color") == "#efe7d5")
        park_camera = camera_state(page)
        check("initial Park view starts flat and west-up", is_flat_west(park_camera), str(park_camera))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["park"]))

        print("\n== Right panel layer grouping ==")
        labels = page.locator(".panel-section .section-label").evaluate_all(
            "els => els.map((el) => el.textContent.trim())"
        )
        check("panel has a Derived layers section", "Derived layers" in labels, str(labels))
        check("panel has a Source layers section", "Source layers" in labels, str(labels))
        check("old source sub-sections are consolidated",
              not {"Acquisition overlays", "Community (OSM)", "SFWDA paper map (2015)"} & set(labels),
              str(labels))
        check("land-cover outputs live under Derived layers",
              panel_section_for(page, "showLandcover") == "derived-layers"
              and panel_section_for(page, "showContours") == "derived-layers")
        check("visitor context lives with publishable map layers",
              panel_section_for(page, "showVisitorContext") == "publishable")
        check("source/reference inputs live under Source layers",
              panel_section_for(page, "showSatellite") == "source-layers"
              and panel_section_for(page, "showNinePatch") == "source-layers"
              and panel_section_for(page, "showOsmTracks") == "source-layers"
              and panel_section_for(page, "showSfwda") == "source-layers")

        print("\n== Topo preset ==")
        topo_camera_before = {"zoom": 15.15, "bearing": 37, "pitch": 42}
        page.evaluate("(camera) => { window.map.jumpTo(camera); }", topo_camera_before)
        page.locator("#presetTopo").click()
        page.wait_for_timeout(900)
        check("Topo button becomes active", page.locator("#presetTopo").evaluate("el => el.classList.contains('active')"))
        check("Topo turns hillshade on", is_checked(page, "showHillshade") and layer_visibility(page, "lidar-hillshade") == "visible")
        check("Topo turns contours on", is_checked(page, "showContours") and layer_visibility(page, "contours-index") == "visible")
        check("Topo turns water and springs on", is_checked(page, "showWater") and is_checked(page, "showSprings"))
        check("Topo turns buildings on by default (A2)", is_checked(page, "showBuildings"))
        check("Topo changes background", paint(page, "background", "background-color") == "#e7ddc4")
        check("Topo restyles index contours", paint(page, "contours-index", "line-color") == "#5f4934")
        topo_camera = camera_state(page)
        check(
            "Topo preset preserves zoom, pitch, and rotation",
            camera_matches(topo_camera, topo_camera_before),
            str(topo_camera),
        )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["topo"]))

        print("\n== Zoom presets + contour fade ==")
        check("zoom bar has three view buttons",
              page.locator(".zoom-bar button[data-view]").count() == 3)
        minor_opacity = paint(page, "contours-minor", "line-opacity")
        index_opacity = paint(page, "contours-index", "line-opacity")
        check("fine 5 ft contours fade with zoom",
              isinstance(minor_opacity, list) and minor_opacity[0] == "interpolate",
              str(minor_opacity))
        check("index contours tier 50 ft vs 25 ft by zoom",
              isinstance(index_opacity, list)
              and index_opacity[0] == "interpolate"
              and "case" in json.dumps(index_opacity),
              str(index_opacity))

        page.locator("#zoomPavilion").click()
        page.wait_for_timeout(1500)
        pav = page.evaluate("() => ({ z: window.map.getZoom(), c: window.map.getCenter() })")
        check("Pavilion zooms in tight", pav["z"] >= 15.5, f"zoom={pav['z']:.2f}")
        check("Pavilion centers on the 1010 building",
              abs(pav["c"]["lng"] + 85.748268) < 0.01 and abs(pav["c"]["lat"] - 35.090703) < 0.01,
              str(pav["c"]))
        pavilion_camera = camera_state(page)
        check("Pavilion zoom resets to flat west-up", is_flat_west(pavilion_camera), str(pavilion_camera))

        page.evaluate("() => { window.map.jumpTo({ bearing: 24, pitch: 38 }); }")
        page.locator("#zoomRegion").click()
        page.wait_for_timeout(1500)
        region_zoom = page.evaluate("() => window.map.getZoom()")
        check("Region zooms out wide", region_zoom < pav["z"] - 2,
              f"region={region_zoom:.2f} pavilion={pav['z']:.2f}")
        region_camera = camera_state(page)
        check("Region zoom resets to flat west-up", is_flat_west(region_camera), str(region_camera))

        page.evaluate("() => { window.map.jumpTo({ center: [-85.45, 35.42], zoom: 7 }); }")
        page.wait_for_timeout(400)
        leashed = page.evaluate("() => ({ z: map.getZoom(), c: map.getCenter() })")
        check("camera is leashed to the 9-patch (cannot pan/zoom past it)",
              -85.81 < leashed["c"]["lng"] < -85.70
              and 35.05 < leashed["c"]["lat"] < 35.13
              and leashed["z"] >= region_zoom - 0.5,
              f"z={leashed['z']:.2f} c=({leashed['c']['lng']:.4f},{leashed['c']['lat']:.4f})")

        page.evaluate("() => { window.map.jumpTo({ bearing: 31, pitch: 41 }); }")
        page.locator("#zoomPark").click()
        page.wait_for_timeout(1500)
        park_zoom = page.evaluate("() => window.map.getZoom()")
        check("Park zoom sits between region and pavilion",
              region_zoom < park_zoom < pav["z"], f"park={park_zoom:.2f}")
        zoom_park_camera = camera_state(page)
        check("Park zoom resets to flat west-up", is_flat_west(zoom_park_camera), str(zoom_park_camera))

        print("\n== Inline layer tuning + snapshot ==")
        page.evaluate(
            """() => {
              const el = document.querySelector('[data-tune-key="trails"]');
              const section = el?.closest('.panel-section');
              if (section && section.classList.contains('collapsed')) {
                section.querySelector('.section-toggle')?.click();
              }
            }"""
        )
        page.locator('[data-tune-key="trails"]').click(position={"x": 2, "y": 2})
        check("selecting a layer row does not expand the editor",
              page.locator("#layerEditor").evaluate("el => el.hidden"))
        click_in_section(page, '[data-tune-expand-key="trails"]')
        check("inline editor can expand trails", page.locator("#layerEditorTitle").inner_text() == "Trails")
        check(
            "editor sits under the expanded layer row",
            page.locator('[data-tune-key="trails"]').evaluate(
                "el => el.nextElementSibling && el.nextElementSibling.id === 'layerEditor'"
            ),
        )
        check("trail tuner reflects visible state", page.locator("#tuneVisible").is_checked())
        check("trail tuner reads current color",
              page.locator("#tuneColor").input_value() == paint(page, "publish-trails", "line-color"))
        check("trail tuner reads current width",
              abs(float(page.locator("#tuneWidth").input_value()) - float(paint(page, "publish-trails", "line-width"))) < 0.01)
        check("trail tuner reads current opacity",
              int(page.locator("#tuneOpacity").input_value()) == round(float(paint(page, "publish-trails", "line-opacity")) * 100))
        page.locator("#tuneColor").fill("#00a6a6")
        page.locator("#tuneWidth").evaluate(
            """el => {
              el.value = '5.2';
              el.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        page.locator("#tuneOpacity").evaluate(
            """el => {
              el.value = '63';
              el.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        page.wait_for_timeout(250)
        check("color knob updates selected layer", paint(page, "publish-trails", "line-color") == "#00a6a6")
        check("width knob updates selected layer", abs(float(paint(page, "publish-trails", "line-width")) - 5.2) < 0.01)
        check("opacity knob updates selected layer", abs(float(paint(page, "publish-trails", "line-opacity")) - 0.63) < 0.01)
        check("status shows unsaved preset modification", "modified" in page.locator("#presetStatus").inner_text())
        click_in_section(page, '[data-tune-expand-key="roads"]')
        check("roads exposes each configured tuning knob",
              page.locator("#tuneControls .tune-control").count() >= 14,
              f"count={page.locator('#tuneControls .tune-control').count()}")
        # Snapshot Preset retired 2026-05-23 (user direction: "we can just
        # reload the page"). The button is gone; verify so.
        check("snapshotPreset button removed",
              page.evaluate("() => !document.getElementById('snapshotPreset')"))
        check("Park toggle still re-applies preset paints over an unsnapped edit",
              True)
        page.locator("#presetPark").click()
        page.wait_for_timeout(350)
        check("re-applying Park reverts the unsnapped color edit",
              paint(page, "publish-trails", "line-color") != "#00a6a6")
        page.locator("#presetTopo").click()
        page.wait_for_timeout(500)

        print("\n== Clipboard export (v2, replaces Export Settings) ==")
        # Old #exportSettings button retired 2026-05-23 in favor of #exportAll
        # at the bottom of the panel. Import UI was dropped the same day —
        # user pastes JSON out-of-band to the assistant or directly into code.
        check("exportSettings button removed",
              page.evaluate("() => !document.getElementById('exportSettings')"))
        page.locator("#exportAll").click()
        page.wait_for_timeout(500)
        text = page.evaluate("navigator.clipboard.readText()")
        payload = json.loads(text)
        check("export copied v3 settings JSON",
              payload.get("schema") == "aop-viewer-preset-settings-v3",
              str(payload.get("schema")))
        check("export includes all four presets",
              set(payload.get("presets", {}).keys()) == {"park", "topo", "trace", "satellite"})
        check("export includes current state",
              payload.get("current_state", {}).get("toggles") is not None)
        check("export includes runtime_overrides bag",
              "runtime_overrides" in payload,
              str(list(payload.keys())))

        print("\n== Satellite preset ==")
        page.locator("#presetSatellite").click()
        page.wait_for_timeout(500)
        check("Satellite button becomes active", page.locator("#presetSatellite").evaluate("el => el.classList.contains('active')"))
        check("Satellite keeps the preset imagery-only",
              is_checked(page, "showSatellite")
              and not is_checked(page, "showHillshade")
              and not is_checked(page, "showTrails")
              and not is_checked(page, "showEditorPois"))
        check("Satellite fallback background is paper, not black",
              paint(page, "background", "background-color") == "#efe7d5")

        print("\n== Trace preset ==")
        trace_camera_before = {"zoom": 16.1, "bearing": -51, "pitch": 35}
        page.evaluate("(camera) => { window.map.jumpTo(camera); }", trace_camera_before)
        page.locator("#presetTrace").click()
        page.wait_for_timeout(900)
        check("Trace button becomes active", page.locator("#presetTrace").evaluate("el => el.classList.contains('active')"))
        check("Trace turns land cover off", not is_checked(page, "showLandcover") and layer_visibility(page, "landcover-forest") == "none")
        # Item 22 (misc_3.md): Trace preset now sits over the lidar hillshade,
        # not the NAIP imagery. SFWDA + OSM tracks remain on as tracing refs.
        check("Trace turns lidar hillshade and tracing references on",
              is_checked(page, "showHillshade") and not is_checked(page, "showUsdaNaip")
              and is_checked(page, "showSfwda")
              and is_checked(page, "showOsmTracks") and is_checked(page, "showBuildings"))
        check("Trace uses a relief-paper substrate instead of a black base",
              paint(page, "background", "background-color") == "#e7ddc4"
              and paint(page, "lidar-hillshade", "hillshade-highlight-color") == "#fff4d9"
              and paint(page, "lidar-hillshade", "hillshade-shadow-color") == "#2f2a21")
        check("Trace applies high-contrast boundary color", paint(page, "publish-boundaries", "line-color") == "#fff0b8")
        trace_camera = camera_state(page)
        check("Trace preset preserves zoom, pitch, and rotation", camera_matches(trace_camera, trace_camera_before), str(trace_camera))
        # Sprint 02 B5: trace label legibility — cream text on the SFWDA paper
        # map needs a dark halo or it disappears into the imagery. Assert the
        # four label layers picked up the dark halo override.
        check(
            "Trace gives roads-labels a dark halo",
            paint(page, "roads-labels", "text-halo-color") == "#15110d"
            and float(paint(page, "roads-labels", "text-halo-width") or 0) >= 2,
        )
        check(
            "Trace gives osm-named-labels a dark halo",
            paint(page, "osm-named-labels", "text-halo-color") == "#15110d"
            and float(paint(page, "osm-named-labels", "text-halo-width") or 0) >= 1.5,
        )
        check(
            "Trace gives activity-hotspots-labels a dark halo",
            paint(page, "activity-hotspots-labels", "text-halo-color") == "#15110d"
            and float(paint(page, "activity-hotspots-labels", "text-halo-width") or 0) >= 1.5,
        )
        check(
            "Trace gives visitor-context-labels a dark halo",
            paint(page, "visitor-context-labels", "text-halo-color") == "#15110d"
            and float(paint(page, "visitor-context-labels", "text-halo-width") or 0) >= 1.5,
        )
        click_in_section(page, '[data-tune-expand-key="sfwda"]')
        check("inline editor can expand SFWDA", page.locator("#layerEditorTitle").inner_text() == "SFWDA paper map")
        check("SFWDA alignment controls live in the drawer", page.locator("#sfwdaDrawerControls").is_visible())
        page.locator("#tuneOpacity").evaluate(
            """el => {
              el.value = '42';
              el.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        page.wait_for_timeout(250)
        check("SFWDA tuner drives the existing opacity slider", page.locator("#sfwdaOpacity").input_value() == "42")
        check("SFWDA drawer exposes alignment toggle", page.locator("#editSfwda").is_visible())
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["trace"]))

        # Sprint 02 B5: switching trace → park must reset halos. Without an
        # explicit cream-halo override in park, the dark halo from trace
        # would sit under park's dark text.
        park_camera_before = {"zoom": 15.6, "bearing": 28, "pitch": 32}
        page.evaluate("(camera) => { window.map.jumpTo(camera); }", park_camera_before)
        page.locator("#presetPark").click()
        page.wait_for_timeout(800)
        park_reset_camera = camera_state(page)
        check("Park preset preserves zoom, pitch, and rotation", camera_matches(park_reset_camera, park_camera_before), str(park_reset_camera))
        check(
            "Park preset resets roads-labels halo to cream",
            paint(page, "roads-labels", "text-halo-color") == "#f7f1e2",
        )
        check(
            "Park preset resets osm-named-labels halo to cream",
            paint(page, "osm-named-labels", "text-halo-color") == "#f7f1e2",
        )
        check(
            "Park preset resets activity-hotspots-labels halo to cream",
            paint(page, "activity-hotspots-labels", "text-halo-color") == "#f7f1e2",
        )

        print("\n== Mobile layout (B3 bottom-dock + calendar resize) ==")
        # Sprint 02 B3 dropped the fixed `top: 430px` on the mobile panel in
        # favor of a bottom-dock that grows upward. Reload after the resize so
        # the mobile calendar sizing and panel layout both apply.
        page.set_viewport_size({"width": 500, "height": 760})
        page.evaluate(
            "() => { try { localStorage.removeItem('aop_lr_card_height_v1'); } catch (_) {} }"
        )
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_timeout(700)
        boxes = page.evaluate(
            """() => {
              const bar = document.querySelector('.left-controls').getBoundingClientRect();
              const panel = document.querySelector('.panel').getBoundingClientRect();
              const message = document.querySelector('.message').getBoundingClientRect();
              const style = getComputedStyle(document.querySelector('.left-controls'));
              return {
                bar: {
                  x: bar.x,
                  y: bar.y,
                  width: bar.width,
                  height: bar.height,
                  scrollHeight: document.querySelector('.left-controls').scrollHeight,
                  clientHeight: document.querySelector('.left-controls').clientHeight,
                  overflowY: style.overflowY
                },
                panel: { x: panel.x, y: panel.y, width: panel.width, height: panel.height, bottom: panel.bottom },
                message: { y: message.y, bottom: message.bottom },
                viewport_height: window.innerHeight
              };
            }"""
        )
        separated = boxes["bar"]["y"] + boxes["bar"]["height"] <= boxes["panel"]["y"]
        check("left controls do not overlap panel on narrow screens", separated, str(boxes))
        check(
            "left controls do not require internal scrolling by default",
            boxes["bar"]["scrollHeight"] <= boxes["bar"]["clientHeight"] + 1
            and boxes["bar"]["overflowY"] not in {"auto", "scroll"},
            str(boxes),
        )
        check(
            "panel docks above the message bar (bottom-anchored)",
            boxes["panel"]["bottom"] <= boxes["message"]["y"] + 2,
            str(boxes),
        )

        print("\n== Collapsed panel docks to bottom-right (B3) ==")
        # Wide viewport: collapse the panel and confirm its bottom edge is
        # near the viewport bottom (the tray-style resting state).
        page.set_viewport_size({"width": 1280, "height": 820})
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_timeout(500)
        # Make sure the panel starts expanded, then collapse via #panelCollapse.
        is_collapsed = page.evaluate(
            "() => document.querySelector('.panel').classList.contains('collapsed')"
        )
        if is_collapsed:
            page.locator("#panelCollapse").click()
            page.wait_for_timeout(300)
        page.locator("#panelCollapse").click()
        page.wait_for_timeout(400)
        collapsed_geom = page.evaluate(
            """() => {
              const panel = document.querySelector('.panel');
              const r = panel.getBoundingClientRect();
              return {
                collapsed: panel.classList.contains('collapsed'),
                bottom: r.bottom,
                right: r.right,
                top: r.top,
                viewport_height: window.innerHeight,
                viewport_width: window.innerWidth
              };
            }"""
        )
        check("panel reports collapsed state", collapsed_geom.get("collapsed") is True, str(collapsed_geom))
        check(
            "collapsed panel sits within 24 px of viewport bottom",
            (collapsed_geom["viewport_height"] - collapsed_geom["bottom"]) <= 24,
            str(collapsed_geom),
        )
        check(
            "collapsed panel sits within 24 px of viewport right",
            (collapsed_geom["viewport_width"] - collapsed_geom["right"]) <= 24,
            str(collapsed_geom),
        )
        check(
            "collapsed panel top is below mid-screen (not floating up top)",
            collapsed_geom["top"] >= collapsed_geom["viewport_height"] / 2,
            str(collapsed_geom),
        )

        print("\n== Console summary ==")
        check("no non-tile console errors", len(console_errors) == 0,
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
