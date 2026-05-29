#!/usr/bin/env python3
"""Playwright verification for the bake-first POI pipeline.

Proves the SERVE end of the one pipeline (card:
brain/tasks/04_event_app/star_driven_poi_list.md):

    core.pois  ->  publish.pois (gate)  ->  export_publish_geojson.sh
               ->  website/data/publish.geojson `poi` features
               ->  map `publish-pois` layer + POI tab "Published destinations".

Preconditions:
  - DB seeded:  psql < mvp/scripts/seed_core_pois.sql
  - Baked:      bash mvp/scripts/export_publish_geojson.sh
  - Serving:    python3 -m http.server 8001 --directory website

The seed loads three core.pois rows; the publish gate must let exactly two
through (AOP Pavilion, Ellis Cemetery) and exclude the unpublished
"Proving Grounds (candidate)" row.
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, rendered_count


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def wait_loaded(page) -> None:
    page.evaluate("window.map = map;")
    page.wait_for_function(
        "() => document.getElementById('message').textContent.includes('publish feature')",
        timeout=15_000,
    )
    page.wait_for_timeout(500)


def open_poi_tab(page) -> None:
    page.evaluate(
        """() => {
          const btn = [...document.querySelectorAll('.left-tab[data-left-tab]')]
            .find((b) => b.dataset.leftTab === 'poi');
          if (btn) btn.click();
        }"""
    )
    page.wait_for_timeout(300)


def main() -> int:
    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="networkidle")
        wait_loaded(page)

        # 1. The bake gate: exactly the two published POIs reach the file.
        baked = page.evaluate(
            """() => ((typeof publishDataCache !== 'undefined' && publishDataCache
                       ? publishDataCache.features : []) || [])
                 .filter((f) => f.properties?.layer === 'poi')
                 .map((f) => ({ name: f.properties.name, blurb: !!f.properties.blurb }))"""
        )
        baked_names = sorted(f["name"] for f in baked)
        check(
            "publish.geojson carries exactly the 2 published POIs",
            baked_names == ["AOP Pavilion", "Ellis Cemetery"],
            f"got {baked_names}",
        )
        check(
            "baked POIs carry their DB blurb",
            all(f["blurb"] for f in baked),
            f"blurb flags {[f['blurb'] for f in baked]}",
        )
        check(
            "the unpublished candidate is excluded by the gate",
            "Proving Grounds (candidate)" not in baked_names,
            f"got {baked_names}",
        )

        # 2. The map renders the baked POI layer.
        check(
            "map publish-pois layer renders 2 features",
            rendered_count(page, ["publish-pois"]) == 2,
            f"rendered={rendered_count(page, ['publish-pois'])}",
        )

        # 3. The POI tab shows the baked group fed from the file.
        open_poi_tab(page)
        group = page.evaluate(
            """() => {
              const g = document.querySelector('.poi-list-group[data-group-id="published_destinations"]');
              if (!g) return null;
              return {
                label: g.querySelector('.poi-list-group-head span')?.textContent || '',
                rows: [...g.querySelectorAll('.poi-row .poi-row-name')].map((n) => n.textContent),
              };
            }"""
        )
        check("POI tab has a Published destinations group", group is not None,
              "" if group is not None else "group not found")
        if group:
            check(
                "group renders both baked destinations",
                sorted(group["rows"]) == ["AOP Pavilion", "Ellis Cemetery"],
                f"rows={group['rows']}",
            )

        check("no console errors", not console_errors,
              "; ".join(console_errors[:3]))
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("baked-POI verification: FAIL")
        return 1
    print("baked-POI verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
