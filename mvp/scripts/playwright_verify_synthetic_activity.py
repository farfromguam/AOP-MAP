#!/usr/bin/env python3
"""Playwright verification for the simulated Saturday activity layer.

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

SYNTHETIC_LAYERS = [
    "synthetic-activity-tracks",
    "synthetic-activity-hotspots-heat",
    "synthetic-activity-hotspots-fill",
    "synthetic-activity-hotspots-outline",
    "synthetic-activity-hotspots-labels",
]

SCREENSHOTS = {
    "initial": "playwright_synthetic_activity_initial.png",
    "on": "playwright_synthetic_activity_on.png",
    "popup": "playwright_synthetic_activity_popup.png",
    "off": "playwright_synthetic_activity_off.png",
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def synthetic_summary(page) -> dict:
    return page.evaluate(
        """async () => {
          const [trackResponse, hotspotResponse, reportResponse, existingResponse] = await Promise.all([
            fetch('./data/aop_synthetic_activity_tracks.geojson'),
            fetch('./data/aop_synthetic_activity_hotspots.geojson'),
            fetch('./data/aop_synthetic_activity_report.json'),
            fetch('./data/aop_activity_hotspots.geojson')
          ]);
          if (![trackResponse, hotspotResponse, reportResponse, existingResponse].every((response) => response.ok)) {
            return {
              ok: false,
              statuses: [trackResponse.status, hotspotResponse.status, reportResponse.status, existingResponse.status]
            };
          }
          const [tracks, hotspots, report, existing] = await Promise.all([
            trackResponse.json(),
            hotspotResponse.json(),
            reportResponse.json(),
            existingResponse.json()
          ]);
          const cells = hotspots.features.filter((f) => f.geometry?.type === 'Polygon');
          const points = hotspots.features.filter((f) => f.geometry?.type === 'Point');
          const existingPoints = existing.features.filter((f) => f.geometry?.type === 'Point');
          const top = points.slice().sort((a, b) =>
            (b.properties.dwell_seconds || 0) - (a.properties.dwell_seconds || 0))[0];
          const top20 = points.slice().sort((a, b) =>
            (b.properties.dwell_seconds || 0) - (a.properties.dwell_seconds || 0)).slice(0, 20);
          const toRad = (value) => value * Math.PI / 180;
          const distanceM = (a, b) => {
            const R = 6371000;
            const lon1 = toRad(a[0]), lat1 = toRad(a[1]), lon2 = toRad(b[0]), lat2 = toRad(b[1]);
            const dlon = lon2 - lon1, dlat = lat2 - lat1;
            const h = Math.sin(dlat / 2) ** 2
              + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dlon / 2) ** 2;
            return 2 * R * Math.atan2(Math.sqrt(h), Math.sqrt(Math.max(0, 1 - h)));
          };
          const nearestExistingDistance = (coord) =>
            Math.min(...existingPoints.map((feature) => distanceM(coord, feature.geometry.coordinates)));
          const top20Overlap45m = top20
            .filter((feature) => nearestExistingDistance(feature.geometry.coordinates) <= 45)
            .length;
          const expectedStrong = (report.expected_hotspots || [])
            .filter((anchor) => (anchor.planned_dwell_minutes || 0) + (anchor.planned_crawl_minutes || 0) >= 80);
          const expectedCovered = expectedStrong.filter((anchor) =>
            Math.min(...points.map((feature) => distanceM(anchor.coordinates, feature.geometry.coordinates))) <= 45
          );
          const startAtPavilion = tracks.features.filter((feature) =>
            feature.properties?.start_anchor === '#pavilion'
          ).length;
          const tracksWithOsm = tracks.features.filter((feature) =>
            Number(feature.properties?.osm_route_count || 0) > 0
          ).length;
          const trackOsmKm = tracks.features.reduce((total, feature) =>
            total + Number(feature.properties?.osm_track_m || 0), 0) / 1000;
          return {
            ok: true,
            report_schema: report.schema,
            track_schema: tracks.metadata?.schema,
            hotspot_schema: hotspots.metadata?.schema,
            track_source: tracks.metadata?.source_type,
            hotspot_source: hotspots.metadata?.source_type,
            users: report.summary?.users,
            tracks_started_at_pavilion: report.summary?.tracks_started_at_pavilion,
            start_at_pavilion_features: startAtPavilion,
            track_features: tracks.features.length,
            hotspot_points: points.length,
            hotspot_cells: cells.length,
            hotspot_point_count: hotspots.metadata?.point_count,
            hotspot_segments: hotspots.metadata?.segment_count,
            hotspot_rank_by: hotspots.metadata?.rank_by,
            hotspot_min_stop_slow_seconds: hotspots.metadata?.min_stop_slow_seconds,
            hotspot_intensity_cap_seconds: hotspots.metadata?.intensity_cap_seconds,
            report_osm_track_km: report.summary?.osm_track_km,
            report_tracks_with_osm_route: report.summary?.tracks_with_osm_route,
            report_osm_route_count: report.summary?.osm_route_count,
            report_osm_way_ids_used: report.summary?.osm_way_ids_used?.length,
            track_osm_km: Math.round(trackOsmKm * 100) / 100,
            tracks_with_osm_features: tracksWithOsm,
            top_class: top?.properties?.intensity_class,
            top_minutes: top?.properties?.dwell_minutes,
            top_center: top?.geometry?.coordinates,
            top20_overlap_45m: top20Overlap45m,
            expected_strong_count: expectedStrong.length,
            expected_covered_count: expectedCovered.length,
            report_overlap_anchors: report.summary?.anchors_with_existing_hotspot_overlap_50m
          };
        }"""
    )


def click_top_hotspot(page, coords: list[float]) -> None:
    point = page.evaluate(
        """(coords) => {
          const p = window.map.project(coords);
          return { x: p.x, y: p.y };
        }""",
        coords,
    )
    page.mouse.click(point["x"], point["y"])
    page.wait_for_timeout(300)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        print(f"Opening {WEBSITE_URL}")
        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(900)

        print("\n== Initial state ==")
        check(
            "simulated activity toggle exists and starts off",
            page.locator("#showSyntheticActivity").count() == 1
            and not page.locator("#showSyntheticActivity").is_checked(),
        )
        for layer in SYNTHETIC_LAYERS:
            check(f"{layer} added hidden", layer_visibility(page, layer) == "none")
        summary = synthetic_summary(page)
        check("synthetic data files load", summary.get("ok") is True, str(summary))
        check("report schema is synthetic Saturday v1", summary.get("report_schema") == "aop-synthetic-saturday-activity-v1")
        check("hotspot schema reuses activity hotspots v1", summary.get("hotspot_schema") == "aop-activity-hotspots-v1")
        check("synthetic source type is preserved", summary.get("hotspot_source") == "synthetic_activity_gpx", str(summary))
        check("72 track features start at pavilion", summary.get("track_features") == 72 and summary.get("start_at_pavilion_features") == 72, str(summary))
        check("synthetic tracks follow OSM linework", summary.get("tracks_with_osm_features", 0) >= 60 and summary.get("track_osm_km", 0) >= 80, str(summary))
        check("OSM route summary is recorded", summary.get("report_tracks_with_osm_route", 0) >= 60 and summary.get("report_osm_way_ids_used", 0) >= 10, str(summary))
        check("hotspot extraction kept 72 synthetic sessions", summary.get("hotspot_segments") == 72, str(summary))
        check("synthetic extraction is focused on dwell/crawl cells", summary.get("hotspot_rank_by") == "stop_slow" and summary.get("hotspot_cells", 0) <= 30, str(summary))
        check("hotspot output has paired cell/centroid features", summary.get("hotspot_cells") == summary.get("hotspot_points") and summary.get("hotspot_cells", 0) >= 15, str(summary))
        check("top synthetic hotspot is peak intensity", summary.get("top_class") == "peak", str(summary))
        check("focused hotspots still overlap existing GPX heat", summary.get("top20_overlap_45m", 0) >= 8, str(summary))
        check("planned strong anchors were surfaced by extraction", summary.get("expected_covered_count", 0) >= 5, str(summary))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["initial"]))

        print("\n== Simulated activity ON ==")
        set_toggle(page, "showSyntheticActivity", True)
        page.wait_for_timeout(1000)
        for layer in SYNTHETIC_LAYERS:
            check(f"{layer} visible", layer_visibility(page, layer) == "visible")
        check("synthetic tracks render in viewport", rendered_count(page, ["synthetic-activity-tracks"]) > 0)
        rendered_cells = rendered_count(page, ["synthetic-activity-hotspots-fill"])
        check("synthetic hotspot cells render in viewport", rendered_cells > 0, f"{rendered_cells} rendered cells")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["on"]))

        print("\n== Hotspot popup ==")
        if summary.get("top_center"):
            click_top_hotspot(page, summary["top_center"])
            page.locator(".maplibregl-popup").first.wait_for(timeout=2_000)
            popup_texts = page.locator(".maplibregl-popup").all_inner_texts()
            detail = " || ".join(text.replace("\n", " | ") for text in popup_texts)
            check(
                "popup opens with synthetic dwell detail",
                any("Synthetic Saturday hotspot" in text and "Dwell" in text for text in popup_texts),
                detail,
            )
        else:
            check("top hotspot center available", False, str(summary))
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["popup"]))

        print("\n== Simulated activity OFF ==")
        set_toggle(page, "showSyntheticActivity", False)
        for layer in SYNTHETIC_LAYERS:
            check(f"{layer} hidden again", layer_visibility(page, layer) == "none")
        page.screenshot(path=str(OUTPUT_DIR / SCREENSHOTS["off"]))

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
