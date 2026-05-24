#!/usr/bin/env python3
"""Playwright verification for the editable event schedule sidebar.

Run after `python3 -m http.server 8001` is serving the `website/` directory.
Set WEBSITE_URL to override the default.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import WEBSITE_URL, set_toggle, layer_visibility, rendered_count


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"

EVENT_LAYERS = [
    "event-session-routes",
    "event-route-labels",
    "event-anchor-points",
    "event-anchor-labels",
]

SCREENSHOTS = {
    "initial": "playwright_event_schedule_initial.png",
    "jump": "playwright_event_schedule_jump.png",
    "off": "playwright_event_schedule_off.png",
    "narrow_jump": "playwright_event_schedule_jump_narrow.png",
    "calendar_narrow_default": "playwright_event_schedule_calendar_narrow_default.png",
    "calendar_search_icon": "playwright_event_schedule_search_icon.png",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def schedule_data(page) -> dict:
    return page.evaluate(
        """async () => {
          const response = await fetch('./data/aop_event_schedule.json');
          if (!response.ok) return { ok: false, status: response.status };
          const data = await response.json();
          const sessions = data.sessions || [];
          const locations = data.locations || {};
          return {
            ok: true,
            schema: data.schema,
            session_count: sessions.length,
            location_tags: Object.keys(locations).sort(),
            route_count: sessions.filter((s) => Array.isArray(s.route_tags)).length,
            sessions_have_coordinates: sessions.some((s) => Object.prototype.hasOwnProperty.call(s, 'coordinates')),
            pavilion_has_json_coordinates: Object.prototype.hasOwnProperty.call(locations['#pavilion'] || {}, 'coordinates'),
            pavilion_alias: locations['#pavillion'] && locations['#pavillion'].alias_of,
            g6: sessions.find((s) => s.id === 'sat-g6-cove-rally') || null
          };
        }"""
    )


def reset_tag_storage(page) -> None:
    """Clear tag store + seed flag + calendar-collapse so a re-run starts
    from the same first-load state as a fresh user."""
    page.evaluate(
        """() => {
          try {
            localStorage.removeItem('aop_feature_tags_v1');
            localStorage.removeItem('aop_feature_tags_seeded_v1');
            localStorage.removeItem('aop_calendar_collapsed_v1');
            localStorage.removeItem('aop_feature_visibility_v1');
          } catch (_) {}
        }"""
    )


def pavilion_building_coords(page) -> list[float] | None:
    """Look up the FEMA 1010 Ellis Cove Rd building's representative point
    (centroid for its polygon) from the loaded buildings layer. The viewer
    uses geometryCentroid on the same geometry, so coordinates should match
    to within ~1e-9 degrees."""
    return page.evaluate(
        """async () => {
          const response = await fetch('./data/aop_buildings.geojson');
          if (!response.ok) return null;
          const data = await response.json();
          const f = (data.features || []).find((feat) => {
            const a = (feat.properties || {}).address || '';
            return String(a).startsWith('1010 ');
          });
          if (!f || !f.geometry) return null;
          // Same centroid math as viewer geometryCentroid for Polygon.
          if (f.geometry.type !== 'Polygon') return null;
          const ring = (f.geometry.coordinates || [])[0] || [];
          const last = ring.length > 1 ? ring.length - 1 : ring.length;
          if (!last) return null;
          let sx = 0, sy = 0;
          for (let i = 0; i < last; i++) { sx += ring[i][0]; sy += ring[i][1]; }
          return [sx / last, sy / last];
        }"""
    )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--enable-unsafe-swiftshader"])
        context = browser.new_context(viewport={"width": 1280, "height": 820})
        page = context.new_page()
        # `page.reload` aborts in-flight tile / sprite / data: requests; the
        # browser then logs them as `TypeError: Failed to fetch` (network) or
        # `AJAXError: Failed to fetch (0): ...` (MapLibre's loader). They are
        # navigation artifacts, not real failures, and the verifier reloads
        # several times for narrow / wide / persist passes. Filter both.
        def _record_error(msg):
            if msg.type != "error":
                return
            text = (msg.text or "").strip()
            if "Failed to fetch" in text:
                return
            console_errors.append(text)

        page.on("console", _record_error)

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        # Sprint 02 B4 added localStorage-backed calendar collapse state and
        # Bucket D added the feature tag store + seed flag. Clear all of them
        # so the auto-collapse default + the pavilion-seed default are
        # observable from a known initial state across local re-runs.
        reset_tag_storage(page)
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=45_000,
            polling=500,
        )
        page.wait_for_timeout(700)

        print("\n== JSON source ==")
        data = schedule_data(page)
        check("schedule JSON loads", data.get("ok") is True, str(data))
        check("schema is event schedule v1", data.get("schema") == "aop-event-schedule-v1", str(data))
        check("twelve editable session rows", data.get("session_count") == 12, str(data))
        check("sessions reference tags, not coordinates", data.get("sessions_have_coordinates") is False, str(data))
        # Bucket D: #pavilion location entry no longer carries coordinates;
        # the viewer resolves them through the 1010 building binding instead.
        check("#pavilion location has no JSON coordinates", data.get("pavilion_has_json_coordinates") is False, str(data))
        check("#pavilion tag is present", "#pavilion" in data.get("location_tags", []), str(data.get("location_tags")))
        check("#pavillion misspelling aliases to #pavilion", data.get("pavilion_alias") == "#pavilion", str(data))
        check("G6 row references location and route tags",
              data.get("g6", {}).get("location_tag") == "#observed-trailhead"
              and data.get("g6", {}).get("route_tags") == ["#observed-trailhead", "#north-technical"],
              str(data.get("g6")))

        print("\n== Sidebar initial state ==")
        rows = page.locator("#calendarDays .calendar-row")
        row_texts = rows.evaluate_all("els => els.map((el) => el.textContent.trim().replace(/\\s+/g, ' '))")
        check("calendar renders all JSON sessions", rows.count() == 12, str(row_texts))
        check("calendar rows show location tags", any("#pavilion" in text for text in row_texts), str(row_texts))
        check("G6 schedule row is present", any("G6 Cove Rally stages" in text for text in row_texts), str(row_texts))
        check(
            "event overlay toggle starts off",
            page.locator("#showEventSchedule").count() == 1
            and not page.locator("#showEventSchedule").is_checked(),
        )
        for layer in EVENT_LAYERS:
            check(f"{layer} hidden", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Schedule row jump ==")
        page.locator('[data-session-id="sat-g6-cove-rally"]').click()
        page.wait_for_timeout(1300)
        check("row click turns event overlay on", page.locator("#showEventSchedule").is_checked())
        for layer in EVENT_LAYERS:
            check(f"{layer} visible", layer_visibility(page, layer) == "visible")
        check(
            "clicked row is active",
            page.locator('[data-session-id="sat-g6-cove-rally"]').evaluate("el => el.classList.contains('active')"),
        )
        rendered_routes = rendered_count(page, ["event-session-routes"])
        check("event route renders after jump", rendered_routes > 0, f"{rendered_routes} rendered route features")
        popup_text = " | ".join(page.locator(".maplibregl-popup").all_inner_texts())
        check("popup shows session and tag", "G6 Cove Rally stages" in popup_text and "#observed-trailhead" in popup_text, popup_text)
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["jump"]))

        print("\n== Toggle OFF ==")
        set_toggle(page, "showEventSchedule", False)
        for layer in EVENT_LAYERS:
            check(f"{layer} hidden again", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["off"]))

        print("\n== Narrow viewport popup placement ==")
        # Sprint 02 Bucket B1: on cramped viewports the calendar-row popup
        # was clipped by chrome. After fix, gotoEventSession must leave the
        # popup fully inside the unoccluded map slice (visibleMapRect).
        # 1024x640 keeps the desktop layout (above the 760px breakpoint) but
        # squeezes vertical space so the calendar card eats real popup room.
        page.set_viewport_size({"width": 1024, "height": 640})
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=45_000,
            polling=500,
        )
        page.wait_for_timeout(700)
        page.locator('[data-session-id="sat-g6-cove-rally"]').click()
        # Fly is 1000 ms; the in-view panBy is 240 ms; plus a 1200 ms safety
        # pan from gotoEventSession. Give the whole settle 1700 ms.
        page.wait_for_timeout(1700)
        narrow_geom = page.evaluate(
            """() => {
              const popup = document.querySelector('.maplibregl-popup');
              const container = window.map.getContainer().getBoundingClientRect();
              if (!popup) return { ok: false };
              const r = popup.getBoundingClientRect();
              const width = container.right - container.left;
              const fullWidth = (b) => (b.right - b.left) >= width * 0.7;
              let top = container.top;
              let bottom = container.bottom;
              let left = container.left;
              let right = container.right;
              for (const sel of ['.left-controls', '.panel']) {
                const el = document.querySelector(sel);
                if (!el) continue;
                const b = el.getBoundingClientRect();
                if (fullWidth(b)) {
                  if (sel === '.left-controls') top = Math.max(top, b.bottom);
                  else bottom = Math.min(bottom, b.top);
                } else {
                  if (sel === '.left-controls') left = Math.max(left, b.right);
                  else right = Math.min(right, b.left);
                }
              }
              const msg = document.querySelector('.message');
              if (msg) bottom = Math.min(bottom, msg.getBoundingClientRect().top);
              return {
                ok: true,
                popup: { top: r.top, bottom: r.bottom, left: r.left, right: r.right },
                vis: { top, bottom, left, right },
                container: { top: container.top, bottom: container.bottom, left: container.left, right: container.right }
              };
            }"""
        )
        check("narrow viewport popup exists", narrow_geom.get("ok") is True, str(narrow_geom))
        if narrow_geom.get("ok"):
            popup_rect = narrow_geom["popup"]
            vis_rect = narrow_geom["vis"]
            tol = 2  # one CSS pixel + sub-pixel rounding
            check(
                "popup top is below left-controls strip",
                popup_rect["top"] >= vis_rect["top"] - tol,
                f"popup.top={popup_rect['top']:.1f} vis.top={vis_rect['top']:.1f}",
            )
            check(
                "popup bottom is above message bar",
                popup_rect["bottom"] <= vis_rect["bottom"] + tol,
                f"popup.bottom={popup_rect['bottom']:.1f} vis.bottom={vis_rect['bottom']:.1f}",
            )
            check(
                "popup left is right of left-controls",
                popup_rect["left"] >= vis_rect["left"] - tol,
                f"popup.left={popup_rect['left']:.1f} vis.left={vis_rect['left']:.1f}",
            )
            check(
                "popup right is left of layer panel",
                popup_rect["right"] <= vis_rect["right"] + tol,
                f"popup.right={popup_rect['right']:.1f} vis.right={vis_rect['right']:.1f}",
            )
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["narrow_jump"]))

        print("\n== Search magnifier icon (B2) ==")
        # Icon is an inline SVG inside .search; pointer-events:none keeps the
        # input clickable. Assert it renders with non-zero geometry and sits
        # to the left of the input edge.
        icon_geom = page.evaluate(
            """() => {
              const icon = document.querySelector('.search .search-icon');
              const input = document.getElementById('searchInput');
              if (!icon || !input) return { ok: false };
              const i = icon.getBoundingClientRect();
              const n = input.getBoundingClientRect();
              return {
                ok: true,
                width: i.width,
                height: i.height,
                left_of_input_edge: i.left < n.left + 32 && i.right < n.right,
                inside_input_bounds: i.top >= n.top - 2 && i.bottom <= n.bottom + 2
              };
            }"""
        )
        check("search magnifier icon present", icon_geom.get("ok") is True, str(icon_geom))
        if icon_geom.get("ok"):
            check("icon has non-zero size", icon_geom["width"] > 0 and icon_geom["height"] > 0, str(icon_geom))
            check("icon sits at the left edge of the input", icon_geom["left_of_input_edge"], str(icon_geom))
            check("icon is vertically inside the input", icon_geom["inside_input_bounds"], str(icon_geom))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["calendar_search_icon"]), clip={"x": 0, "y": 0, "width": 360, "height": 60})

        print("\n== Calendar collapse: time labels (B4) ==")
        # User dump line "calendar needs time": confirm every row that has a
        # time_label in JSON also has visible text in .calendar-time. The
        # existing rendered-text check (~line 130) already proves a couple
        # of labels reach the row; here we explicitly assert per-row.
        time_count = page.evaluate(
            """() => {
              const rows = Array.from(document.querySelectorAll('#calendarDays .calendar-row .calendar-time'));
              return {
                total: rows.length,
                non_empty: rows.filter((el) => el.textContent.trim().length > 0).length
              };
            }"""
        )
        check(
            "every calendar row has a time label",
            time_count.get("total", 0) == 12 and time_count.get("non_empty", 0) == 12,
            str(time_count),
        )

        print("\n== Calendar collapse: narrow viewport default (B4) ==")
        # Stale localStorage from the previous narrow pass would mask the
        # auto-collapse default. Clear it before reloading at 420×740.
        page.evaluate(
            "() => { try { localStorage.removeItem('aop_calendar_collapsed_v1'); } catch (_) {} }"
        )
        page.set_viewport_size({"width": 420, "height": 740})
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_timeout(700)
        narrow_default = page.evaluate(
            """() => ({
              has_collapsed: document.getElementById('calendarCard').classList.contains('collapsed'),
              aria_expanded: document.getElementById('calendarToggle').getAttribute('aria-expanded'),
              stored: localStorage.getItem('aop_calendar_collapsed_v1')
            })"""
        )
        check("calendar starts collapsed on narrow viewport", narrow_default.get("has_collapsed") is True, str(narrow_default))
        check("calendar aria-expanded reflects collapsed", narrow_default.get("aria_expanded") == "false", str(narrow_default))
        check("auto-collapse does not persist by itself", narrow_default.get("stored") is None, str(narrow_default))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["calendar_narrow_default"]))

        print("\n== Calendar collapse: manual expand persists (B4) ==")
        page.locator("#calendarToggle").click()
        page.wait_for_timeout(200)
        after_expand = page.evaluate(
            """() => ({
              has_collapsed: document.getElementById('calendarCard').classList.contains('collapsed'),
              stored: localStorage.getItem('aop_calendar_collapsed_v1')
            })"""
        )
        check("manual expand opens the card", after_expand.get("has_collapsed") is False, str(after_expand))
        check("manual expand persists to localStorage", after_expand.get("stored") == "0", str(after_expand))
        page.reload(wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_timeout(500)
        post_reload = page.evaluate(
            "() => document.getElementById('calendarCard').classList.contains('collapsed')"
        )
        check("user-expanded calendar survives reload on narrow", post_reload is False, str(post_reload))

        print("\n== Calendar collapse: wide viewport default (B4) ==")
        # Clear localStorage so the wide-viewport default is observable.
        page.evaluate(
            "() => { try { localStorage.removeItem('aop_calendar_collapsed_v1'); } catch (_) {} }"
        )
        page.set_viewport_size({"width": 1280, "height": 820})
        page.goto(WEBSITE_URL, wait_until="load")
        page.wait_for_timeout(500)
        wide_default = page.evaluate(
            """() => ({
              has_collapsed: document.getElementById('calendarCard').classList.contains('collapsed'),
              stored: localStorage.getItem('aop_calendar_collapsed_v1')
            })"""
        )
        check("calendar starts expanded on wide viewport", wide_default.get("has_collapsed") is False, str(wide_default))
        check("auto-expand does not persist by itself", wide_default.get("stored") is None, str(wide_default))

        print("\n== Tag-driven location resolution (Bucket D) ==")
        # The wide-viewport reload just above already cleared localStorage via
        # the prior pages — but we cleared only the calendar-collapse key
        # before that goto. Reset the tag store + seed flag explicitly, then
        # reload so the maybeSeedFeatureTags path fires on this load with a
        # known starting state.
        reset_tag_storage(page)
        page.goto(WEBSITE_URL, wait_until="load")
        # The viewer's tag store + lookup + tunable-expansion helpers are
        # script-scoped consts. Expose them on window for the verifier to
        # inspect.
        page.evaluate(
            """() => {
              window.map = map;
              window.tagToFeature = tagToFeature;
              window.eventLocationByTag = eventLocationByTag;
              window.toggleTunableExpansion = toggleTunableExpansion;
            }"""
        )
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=45_000,
            polling=500,
        )
        page.wait_for_timeout(700)

        # The 1010 building's centroid is the truth source for #pavilion.
        building_coords = pavilion_building_coords(page)
        check("1010 Ellis Cove Rd building present in buildings geojson",
              building_coords is not None and len(building_coords) == 2,
              str(building_coords))

        # After load + auto-seed, the viewer should have #pavilion → 1010.
        seeded = page.evaluate(
            """() => {
              const raw = localStorage.getItem('aop_feature_tags_v1');
              const seed = localStorage.getItem('aop_feature_tags_seeded_v1');
              return { stored: raw ? JSON.parse(raw) : null, seed };
            }"""
        )
        check("seed flag set on first load", seeded.get("seed") == "1", str(seeded))
        check("aop_feature_tags_v1 has a #pavilion binding under buildings",
              isinstance(seeded.get("stored"), dict)
              and isinstance(seeded["stored"].get("buildings"), dict)
              and "#pavilion" in [str(v).lower() for v in seeded["stored"]["buildings"].values()],
              str(seeded))

        # The viewer's tag-to-feature lookup should mirror the same binding,
        # and the event schedule resolver should pick up those coords for
        # #pavilion even though the JSON no longer carries any.
        resolved = page.evaluate(
            """() => {
              const tagBinding = window.tagToFeature && window.tagToFeature.get
                ? window.tagToFeature.get('#pavilion')
                : null;
              const location = window.eventLocationByTag && window.eventLocationByTag.get
                ? window.eventLocationByTag.get('#pavilion')
                : null;
              return {
                bound: tagBinding ? {
                  layerKey: tagBinding.layerKey,
                  featureId: String(tagBinding.featureId),
                  coordinates: tagBinding.coordinates
                } : null,
                location: location ? {
                  tag: location.tag,
                  coordinates: location.coordinates,
                  bound_feature: location.bound_feature || null
                } : null
              };
            }"""
        )
        check("tagToFeature has #pavilion → buildings binding",
              resolved.get("bound") and resolved["bound"].get("layerKey") == "buildings",
              str(resolved))
        check("#pavilion location resolved to building coords",
              resolved.get("location") and resolved["location"].get("coordinates") is not None,
              str(resolved))
        if building_coords and resolved.get("location"):
            loc_coords = resolved["location"]["coordinates"]
            dist = abs(loc_coords[0] - building_coords[0]) + abs(loc_coords[1] - building_coords[1])
            check(
                "resolved #pavilion coords match 1010 building centroid",
                dist < 1e-7,
                f"loc={loc_coords} building={building_coords} dist={dist}",
            )

        # Click a pavilion-bound session row and confirm the camera flies to
        # somewhere close to the building. The Friday driver meeting is the
        # first pavilion-anchored session (location_tag = #pavilion).
        page.locator('[data-session-id="fri-driver-meeting"]').click()
        page.wait_for_timeout(1500)
        cam_center = page.evaluate("() => { const c = window.map.getCenter(); return [c.lng, c.lat]; }")
        if building_coords:
            cam_dist = abs(cam_center[0] - building_coords[0]) + abs(cam_center[1] - building_coords[1])
            check(
                "pavilion row flies camera near the 1010 building (within ~0.0005°)",
                cam_dist < 5e-4,
                f"camera={cam_center} building={building_coords} dist={cam_dist}",
            )
        # The popup should show the resolved location label and the tag.
        popup_text = " | ".join(page.locator(".maplibregl-popup").all_inner_texts())
        check("pavilion popup shows location label", "AOP Pavilion" in popup_text, popup_text)

        # Buildings drawer: expand it and confirm the tag input renders on
        # rows, with the 1010 row pre-bound to #pavilion. Then re-bind
        # #pavilion to a different building row and confirm the schedule
        # re-resolves live (no reload).
        page.evaluate("() => { try { document.querySelector('.maplibregl-popup-close-button')?.click(); } catch(_){} }")
        page.evaluate("() => window.toggleTunableExpansion && window.toggleTunableExpansion('buildings')")
        page.wait_for_timeout(400)
        tag_inputs = page.evaluate(
            """() => {
              const rows = Array.from(document.querySelectorAll('#featureList .feature-row'));
              return rows.map((r) => {
                const tag = r.querySelector('.feature-tag');
                const label = r.querySelector('.feature-name');
                return {
                  id: r.dataset.featureId,
                  label: label ? label.textContent : '',
                  has_tag_input: !!tag,
                  tag_value: tag ? tag.value : null
                };
              });
            }"""
        )
        check("buildings drawer renders feature-tag input on every row",
              len(tag_inputs) > 0 and all(r.get("has_tag_input") for r in tag_inputs),
              f"{sum(1 for r in tag_inputs if r.get('has_tag_input'))}/{len(tag_inputs)} rows have tag input")
        pavilion_rows = [r for r in tag_inputs if r.get("tag_value") == "#pavilion"]
        check("exactly one building row is pre-bound to #pavilion",
              len(pavilion_rows) == 1,
              f"rows tagged #pavilion: {[r.get('label') for r in pavilion_rows]}")
        pavilion_label = pavilion_rows[0]["label"] if pavilion_rows else ""
        check("the #pavilion-bound row is the 1010 Ellis Cove Rd building",
              "1010" in pavilion_label,
              pavilion_label)

        # Move the #pavilion tag to a different building row by typing into
        # its input and dispatching change. The resolved schedule coords
        # should follow without a reload.
        target_id = next((r["id"] for r in tag_inputs
                          if r["id"] != (pavilion_rows[0]["id"] if pavilion_rows else "")
                          and r.get("has_tag_input")), None)
        check("there is another building row to bind for the live re-resolve test",
              target_id is not None, "no second building row found")
        if target_id:
            new_coords = page.evaluate(
                """(targetId) => {
                  const row = document.querySelector(`.feature-row[data-feature-id="${targetId}"]`);
                  const input = row && row.querySelector('.feature-tag');
                  if (!input) return null;
                  input.focus();
                  input.value = '#pavilion';
                  input.dispatchEvent(new Event('change', { bubbles: true }));
                  // Pull the freshly-resolved location coords back out.
                  const location = window.eventLocationByTag.get('#pavilion');
                  const bound = window.tagToFeature.get('#pavilion');
                  return {
                    location_coords: location ? location.coordinates : null,
                    bound_layer: bound ? bound.layerKey : null,
                    bound_feature: bound ? String(bound.featureId) : null
                  };
                }""",
                target_id,
            )
            check("live re-bind: tagToFeature points at the new building row",
                  new_coords and new_coords.get("bound_feature") == str(target_id),
                  str(new_coords))
            check("live re-bind: schedule re-resolves to new coords (different from 1010)",
                  new_coords and new_coords.get("location_coords") is not None
                  and building_coords is not None
                  and (abs(new_coords["location_coords"][0] - building_coords[0])
                       + abs(new_coords["location_coords"][1] - building_coords[1])) > 1e-6,
                  str(new_coords))
            # Restore the binding so the rest of the run (and the screenshot)
            # leave a clean state. Bind back to the original row by ID.
            if pavilion_rows:
                original_id = pavilion_rows[0]["id"]
                page.evaluate(
                    """(origId) => {
                      const row = document.querySelector(`.feature-row[data-feature-id="${origId}"]`);
                      const input = row && row.querySelector('.feature-tag');
                      if (input) {
                        input.value = '#pavilion';
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                      }
                    }""",
                    original_id,
                )

        # Search for `#pavilion` should still surface the anchor (the
        # alias path from Bucket C continues to work because the anchor now
        # exists in the rebuilt searchIndex).
        page.locator("#searchInput").fill("#pavilion")
        page.wait_for_timeout(250)
        results_text = page.locator("#searchResults").inner_text()
        check("search for #pavilion surfaces the pavilion anchor",
              "AOP Pavilion" in results_text or "G-Central" in results_text,
              results_text)
        page.locator("#searchInput").fill("")

        # ----------------------------------------------------------------
        # Hot control (Sprint 02 Bucket A3 + two-lane follow-up)
        # ----------------------------------------------------------------
        # Three states driven by ?clock= fixtures so the same clock-override
        # contract the calendar uses also pins the button. The forward
        # anchor (eventScheduleAnchorForward) makes Mon-Fri "look ahead" to
        # the upcoming weekend, so a Monday fixture still yields coming-up
        # against the schedule's weekend template.

        def load_with_clock(clock: str) -> None:
            page.set_viewport_size({"width": 1280, "height": 820})
            page.goto(WEBSITE_URL + f"?clock={clock}", wait_until="load")
            page.evaluate(
                """() => {
                  window.map = map;
                  window.eventSessionById = eventSessionById;
                  window.eventLocationByTag = eventLocationByTag;
                  window.refreshHotButton = refreshHotButton;
                  window.computeHotButtonTarget = computeHotButtonTarget;
                }"""
            )
            page.wait_for_function(
                "() => document.getElementById('message').textContent.includes('publish feature')",
                timeout=45_000,
                polling=500,
            )
            page.wait_for_timeout(700)
            # Refresh once more after init settles — covers the case where
            # schedule/hotspots load order races the initial refresh.
            page.evaluate("() => window.refreshHotButton && window.refreshHotButton()")
            page.wait_for_timeout(150)

        def button_snapshot() -> dict:
            return page.evaluate(
                """() => {
                  const control = document.getElementById('hotControl');
                  const btn = document.getElementById('hotButton');
                  const trail = document.getElementById('hotTrailButton');
                  if (!control || !btn || !trail) return { present: false };
                  const buttonData = (el, titleId, detailId, glyphId) => ({
                    hidden: el.hidden,
                    disabled: el.disabled,
                    state: el.dataset.hotState || '',
                    selected: el.dataset.hotSelected || '',
                    targetSessionId: el.dataset.targetSessionId || '',
                    title: (document.getElementById(titleId) || {}).textContent || '',
                    detail: (document.getElementById(detailId) || {}).textContent || '',
                    glyph: (document.getElementById(glyphId) || {}).textContent || ''
                  });
                  const event = buttonData(btn, 'hotButtonTitle', 'hotButtonDetail', 'hotButtonGlyph');
                  const trails = buttonData(trail, 'hotTrailButtonTitle', 'hotTrailButtonDetail', 'hotTrailButtonGlyph');
                  return {
                    present: true,
                    hidden: control.hidden,
                    status: (document.getElementById('hotControlStatus') || {}).textContent || '',
                    event,
                    trails,
                    // Back-compat aliases for the Event lane.
                    state: event.state,
                    targetSessionId: event.targetSessionId,
                    title: event.title,
                    detail: event.detail,
                    glyph: event.glyph
                  };
                }"""
            )

        print("\n== Hot control: Event lane state=hot-now (live) ==")
        # 2026-05-23 13:45 sits inside sat-proving-grounds (13:30 + 90 min).
        load_with_clock("2026-05-23T13:45")
        snap = button_snapshot()
        check("hot button is present", snap.get("present") is True, str(snap))
        check("hot button is visible", snap.get("hidden") is False, str(snap))
        check("hot-now state on live fixture", snap.get("state") == "hot-now", str(snap))
        check("targets sat-proving-grounds", snap.get("targetSessionId") == "sat-proving-grounds", str(snap))
        check("event lane selected for live fixture", snap.get("event", {}).get("selected") == "true", str(snap))
        check("trail lane is available alongside live event", snap.get("trails", {}).get("disabled") is False, str(snap))
        check("title reads Live event", "Live event" in (snap.get("title") or ""), str(snap))
        check("detail mentions session title", "Proving Grounds" in (snap.get("detail") or ""), str(snap))

        # Click in hot-now should fly to the resolved session's location and
        # open its popup — identical to a calendar row click.
        page.locator("#hotButton").click()
        page.wait_for_timeout(1500)
        cam_after_live_click = page.evaluate("() => { const c = window.map.getCenter(); return [c.lng, c.lat]; }")
        proving_coords = page.evaluate(
            "() => { const l = window.eventLocationByTag.get('#proving-grounds'); return l ? l.coordinates : null; }"
        )
        check(
            "hot-now click flies the camera near #proving-grounds",
            proving_coords is not None
            and (abs(cam_after_live_click[0] - proving_coords[0])
                 + abs(cam_after_live_click[1] - proving_coords[1])) < 5e-4,
            f"camera={cam_after_live_click} target={proving_coords}",
        )
        live_popup = " | ".join(page.locator(".maplibregl-popup").all_inner_texts())
        check("hot-now click opens the session popup", "Proving Grounds" in live_popup, live_popup)

        print("\n== Hot control: Event lane state=hot-now (imminent, <=30 min) ==")
        # 13:15 puts the same session 15 min in the future (still imminent).
        load_with_clock("2026-05-23T13:15")
        snap = button_snapshot()
        check("hot-now state on imminent fixture", snap.get("state") == "hot-now", str(snap))
        check("targets sat-proving-grounds", snap.get("targetSessionId") == "sat-proving-grounds", str(snap))
        check("title reads starting soon", "starting soon" in (snap.get("title") or "").lower(), str(snap))
        check("event lane selected for imminent fixture", snap.get("event", {}).get("selected") == "true", str(snap))

        print("\n== Hot control: Event lane state=coming-up (same-day, >30 min) ==")
        # 19:45 sits between sat-awards (18:00 + 90m -> 19:30) and
        # sat-night-crawl (20:30) — 45 min until night crawl.
        load_with_clock("2026-05-23T19:45")
        snap = button_snapshot()
        check("event lane stays in coming-up state when no session is imminent", snap.get("state") == "coming-up", str(snap))
        check("targets sat-night-crawl", snap.get("targetSessionId") == "sat-night-crawl", str(snap))
        check("title reads Next event", "Next event" in (snap.get("title") or ""), str(snap))
        check("detail mentions countdown",
              "in " in (snap.get("detail") or "") and ("m" in (snap.get("detail") or "")),
              str(snap))
        check("trail lane selected by default when event is future",
              snap.get("trails", {}).get("selected") == "true", str(snap))

        # Trail-first users should not have to wait for an empty schedule. The
        # Trails lane is a direct action while the Event lane still points at
        # the next scheduled session.
        before_check = page.evaluate("() => document.getElementById('showActivityHotspots').checked")
        page.locator("#hotTrailButton").click()
        page.wait_for_timeout(1300)
        after_check = page.evaluate("() => document.getElementById('showActivityHotspots').checked")
        hotspots_vis = layer_visibility(page, "activity-hotspots-fill")
        snap_after_trail = button_snapshot()
        check("trail lane click turns activity-hotspots toggle on while schedule exists",
              before_check is False and after_check is True, f"before={before_check} after={after_check}")
        check("trail lane click makes activity-hotspots visible while schedule exists",
              hotspots_vis == "visible", f"visibility={hotspots_vis}")
        check("trail lane remains selected after trail click",
              snap_after_trail.get("trails", {}).get("selected") == "true", str(snap_after_trail))

        print("\n== Hot control: Event lane coming-up across days (Mon fixture) ==")
        # Forward anchor: a Monday clock should wrap the template to the
        # upcoming weekend (fri-registration ~4 days out). This proves the
        # "Friday should already light up for a Saturday evening session"
        # promise from the card.
        load_with_clock("2026-05-25T12:00")
        snap = button_snapshot()
        check("event lane coming-up state on Monday fixture", snap.get("state") == "coming-up", str(snap))
        check("Monday fixture targets first weekend session (fri-registration)",
              snap.get("targetSessionId") == "fri-registration", str(snap))
        check("trail lane selected on Monday when no event is imminent",
              snap.get("trails", {}).get("selected") == "true", str(snap))

        # Click in coming-up should also fly + popup, like a calendar row.
        page.locator("#hotButton").click()
        page.wait_for_timeout(1500)
        coming_popup = " | ".join(page.locator(".maplibregl-popup").all_inner_texts())
        check("coming-up click opens the upcoming session popup",
              "Registration" in coming_popup or "Wristband" in coming_popup or "wristband" in coming_popup.lower(),
              coming_popup)

        print("\n== Hot control: Trails lane when schedule is empty ==")
        # Forward-anchoring means a weekday-template schedule never goes
        # "all past"; with the two-lane control, clearing the schedule disables
        # Event but leaves Trails usable.
        load_with_clock("2026-05-23T13:45")
        page.evaluate(
            """() => {
              eventSessionById.clear();
              refreshHotButton();
            }"""
        )
        page.wait_for_timeout(150)
        snap = button_snapshot()
        check("event lane has no-event state when schedule is empty", snap.get("state") == "no-event", str(snap))
        check("event lane disabled when schedule is empty", snap.get("event", {}).get("disabled") is True, str(snap))
        check("trail lane selected when schedule is empty", snap.get("trails", {}).get("selected") == "true", str(snap))
        check("trail title reads Trail heat", "Trail heat" in (snap.get("trails", {}).get("title") or ""), str(snap))
        check("no session target in empty-schedule state", snap.get("targetSessionId") == "", str(snap))

        # Click in Trails should toggle activity hotspots on and fit to the
        # hotspot target.
        before_check = page.evaluate("() => document.getElementById('showActivityHotspots').checked")
        page.locator("#hotTrailButton").click()
        page.wait_for_timeout(1300)
        after_check = page.evaluate("() => document.getElementById('showActivityHotspots').checked")
        hotspots_vis = layer_visibility(page, "activity-hotspots-fill")
        check("empty-schedule Trails click turns activity-hotspots toggle on",
              before_check is False and after_check is True, f"before={before_check} after={after_check}")
        check("activity-hotspots layer becomes visible after fallback click",
              hotspots_vis == "visible", f"visibility={hotspots_vis}")

        print("\n== Console summary ==")
        check("no console errors", len(console_errors) == 0, f"{len(console_errors)} error(s): {console_errors[:3]}")

        browser.close()

    print("\nScreenshots:")
    for filename in SCREENSHOTS.values():
        print(f"  - {OUTPUT_DIR / filename}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
