#!/usr/bin/env python3
"""Sprint 08 Slice C acceptance — the POI tab is ★-curated for the four reference layers.

After the listMode 'wholesale'->'starred' flip (cemeteries/buildings/visitorContext/
trails), in a CLEAN PROFILE the POI tab must show ONLY the ★-curated rows for those
layers — the durable ★ baked into core.features.attrs.highlight (Slice A->B), not
per-browser localStorage.

STAR-ONLY (2026-06-08): the two former wholesale unions — published `poi`
(publish.geojson) and event anchors (aop_event_schedule.json) — were removed from
collectStarredDestinations. The POI tab is now exactly the registry's ★-gated layers,
so those two groups must NOT appear at all (asserted below).

Clone of playwright_verify_star_collector.py, with the Witness conditions the card
inherits:
  * A fresh browser context = a clean profile (no aop_positioned_features_v1), so the
    SERVED `highlight` drives — exactly the durability the flip needs.
  * Wait on the map LOAD event via window.AOP_HOST_MAP (not window.map, a lexical
    const absent from page scope), and on the four reference sources actually carrying
    data — that proves the in-`map.on('load')` registerFeatureListLayer calls ran and
    seeded featureListRuntime. wait_loaded (publish message) fires PRE-load and does
    NOT prove that. Tile-independent: no networkidle, no queryRenderedFeatures.
  * Per-reference-group counts are asserted against the ACTUAL baked served files
    (the count of highlight===true features), not a hardcoded number, and against the
    wholesale-eligible total to prove the flip GATES (a group shows the starred subset,
    not every feature).

Run the bake first so the served files carry the curated ★ (Slice A apply -> Slice B
bake). Serve website/ on :8001 (playwright_base.viewer_url()).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url

DATA = Path(__file__).resolve().parents[2] / "website" / "data"

# Reference layer -> (served filename, POI-tab group id, wholesale-eligible predicate).
# `eligible` is the listPredicate the spec applies in wholesale mode; the starred set
# is `eligible AND highlight===true`. Comparing the two proves the flip actually gates.
REFERENCE_GROUPS = {
    "cemeteries": ("aop_cemeteries.geojson", "cemeteries",
                   lambda p: p.get("geom_role") == "marker"),
    "buildings": ("aop_buildings.geojson", "buildings",
                  lambda p: p.get("aop_facility") is True),
    "visitorContext": ("aop_visitor_context_callouts.geojson", "visitor_support",
                       lambda p: p.get("kind") != "brand_logo"),
    "trails": ("aop_trail_network.geojson", "trails",
               lambda p: p.get("trail_number") is not None or p.get("name") not in (None, "")),
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def served_counts(fname: str, eligible) -> tuple[int, int]:
    """(starred-eligible, wholesale-eligible) feature counts in a served file."""
    doc = json.loads((DATA / fname).read_text())
    feats = doc.get("features", [])
    elig = [f for f in feats if eligible((f.get("properties") or {}))]
    starred = [f for f in elig if (f.get("properties") or {}).get("highlight") is True]
    return len(starred), len(elig)


def main() -> int:
    # Expected per-group counts, read from the ACTUAL baked artifacts.
    expected = {}
    for key, (fname, group_id, eligible) in REFERENCE_GROUPS.items():
        starred, wholesale = served_counts(fname, eligible)
        expected[group_id] = (starred, wholesale, key)
    print("Expected from baked served files (starred / wholesale-eligible):")
    for group_id, (s, w, key) in expected.items():
        print(f"  {key:14s} group='{group_id}': starred={s}  wholesale={w}")

    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()  # fresh context = clean profile (no localStorage)
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url())

        # 1) Wait on the LOAD event (Witness condition), not the publish message.
        page.wait_for_function(
            "() => window.AOP_HOST_MAP && typeof window.AOP_HOST_MAP.loaded === 'function' "
            "&& window.AOP_HOST_MAP.loaded()",
            timeout=25_000,
        )
        # 2) Wait until all four reference sources carry data -> the in-load
        #    registerFeatureListLayer calls ran and seeded featureListRuntime.
        page.wait_for_function(
            """() => {
              const m = window.AOP_HOST_MAP; if (!m) return false;
              const ids = ['cemeteries','fema-buildings','visitor-context','aop-trail-network'];
              return ids.every((id) => {
                const s = m.getSource(id);
                if (!s || typeof s.serialize !== 'function') return false;
                const d = s.serialize().data;
                return d && Array.isArray(d.features) && d.features.length > 0;
              });
            }""",
            timeout=25_000,
        )
        page.wait_for_timeout(1200)  # settle the register -> POI-list refresh

        # Open the left POI tab.
        page.evaluate(
            """() => {
              const btn = [...document.querySelectorAll('.left-tab[data-left-tab]')]
                .find((b) => b.dataset.leftTab === 'poi');
              if (btn) btn.click();
            }"""
        )
        page.wait_for_timeout(500)

        def group_rows(group_id: str):
            return page.evaluate(
                """(gid) => {
                  const g = document.querySelector(`.poi-list-group[data-group-id="${gid}"]`);
                  if (!g) return null;
                  return [...g.querySelectorAll('.poi-row')].map((b) => b.dataset.poiId);
                }""",
                group_id,
            )

        # 3) Each reference group shows exactly its starred-eligible count, and fewer
        #    than its wholesale-eligible total (the flip GATES — unstarred rows hidden).
        for group_id, (starred, wholesale, key) in expected.items():
            rows = group_rows(group_id)
            count = len(rows) if rows else 0
            check(f"{key}: POI group shows the curated ★ set ({count} == {starred})",
                  count == starred, f"rows={rows}")
            if wholesale > starred:
                check(f"{key}: flip gates (curated {count} < wholesale-eligible {wholesale})",
                      count < wholesale)

        # 4) STAR-ONLY: the two wholesale unions were removed — neither the
        #    published `poi` group nor the event-anchors group may appear. The
        #    POI tab is now exactly the registry's ★-gated layers.
        pub = group_rows("published_destinations")
        check("published destinations group is GONE (star-only, no wholesale union)",
              pub is None, f"rows={pub}")
        ev = group_rows("event_anchors")
        check("event anchors group is GONE (schedule lives in the Events tab)",
              ev is None, f"rows={ev}")

        # 5) Curation fields render on a starred reference row (verify-first — the
        #    blurb/kind/status/revisit chip are produced by renderPoiTab already).
        #    Only meaningful when at least one reference feature is starred; against
        #    the production-default 0-star bake there is nothing to inspect (N/A).
        total_starred = sum(s for (s, _w, _k) in expected.values())
        if total_starred > 0:
            starred_row = page.evaluate(
                """() => {
                  const ids = ['cemeteries','buildings','visitor_support','trails'];
                  for (const gid of ids) {
                    const g = document.querySelector(`.poi-list-group[data-group-id="${gid}"]`);
                    const row = g && g.querySelector('.poi-row');
                    if (row) return { gid, html: row.innerHTML.length, hasName: !!row.querySelector('.poi-row-name, .poi-name, strong, b') || row.textContent.trim().length > 0 };
                  }
                  return null;
                }"""
            )
            check("a starred reference row renders with content", bool(starred_row and starred_row.get("hasName")),
                  f"{starred_row}")
        else:
            print("  [N/A ] starred reference row render check skipped (0 features starred in the bake)")

        check("no console errors during clean-profile POI render",
              not console_errors, "; ".join(console_errors[:3]))
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("starred-POI-flip verification: FAIL")
        return 1
    print("starred-POI-flip verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
