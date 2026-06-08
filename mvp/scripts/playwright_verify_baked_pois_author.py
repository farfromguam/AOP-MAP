#!/usr/bin/env python3
"""Slice-1 AUTHOR verifier: the viewer consumes the author-path edit (the baked
publish.geojson came from core.pois after apply_panel_overrides_to_core.py).

Tile-independent (per the Observable acceptance standard + C4): it does NOT wait
on `networkidle`, does NOT call `queryRenderedFeatures`, and does NOT read the
closure-private `publishDataCache`. It reuses the PROVEN star_collector harness
(`wait_loaded` gates on the "publish feature(s) loaded" message, which fires
independently of MapLibre `load`; `open_poi_tab`) and reads the
`published_destinations` DOM rows. The launch/wait harness is imported, not
re-implemented. Card: brain/tasks/06_going_gold/gold_migration.md (slice 1).

Two-state, so it stays green in the durable `playwright_verify_*` suite AND proves
the author path when the slice-1 export is applied. Always asserts on the served
bake (never a pre-bake source file):
  - the `published_destinations` rows render from the baked publish.geojson,
  - 0 console errors,
  - AND, when the slice-1 author export is applied (Pavilion edited to the
    author-test name), the EDITED value is served and the ARCHIVED POI is ABSENT
    (the round-trip proof); otherwise the baseline POIs (Pavilion + Ellis) are
    served (the serve path is sound on committed state).

Re-prove the author path on demand (mutates core, then restore). Use
`--require-author` (or AOP_REQUIRE_AUTHOR=1) so the run FAILS if the edit is NOT
present -- otherwise the verifier silently degrades to the baseline branch and a
"PASS" would not prove the round-trip reached the rendered DOM:
  python3 mvp/scripts/apply_panel_overrides_to_core.py <slice-1 export> \
    && bash mvp/scripts/export_publish_geojson.sh \
    && python3 mvp/scripts/playwright_verify_baked_pois_author.py --require-author

Run in the durable suite (viewer served on :8001) -- baseline-green, no flag:
  python3 mvp/scripts/playwright_verify_baked_pois_author.py
"""
from __future__ import annotations

import os
import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url
# Reuse the proven headless-safe harness -- do NOT re-implement boot/wait.
from playwright_verify_star_collector import wait_loaded, open_poi_tab

EDITED_NAME = "AOP Pavilion (author-test)"
EDITED_BLURB_MARK = "AUTHORPATH-OK"
ARCHIVED_NAME = "Ellis Cemetery"
# Baseline (committed/restored) destinations that the bake serves from core.pois.
BASELINE_NAMES = ["AOP Pavilion", "Ellis Cemetery"]
# When set, the author edit MUST be present -- the verifier cannot pass by
# silently falling back to the baseline branch (so a re-proof of the round-trip
# is real, not "it printed PASS"). Off by default so the durable suite stays
# green on committed/baseline state.
REQUIRE_AUTHOR = os.environ.get("AOP_REQUIRE_AUTHOR") == "1" or "--require-author" in sys.argv

# Slice 3 of the description convergence (07_tables/description_blurb_convergence.md):
# prove the renamed `description` reaches the rendered subtitle. A distinctive
# substring of the seeded Pavilion description; when REQUIRE_DESCRIPTION is set the
# run FAILS if it is absent from the DOM (so it cannot degrade to a "rows render"
# baseline pass -- the Witness condition).
DESCRIPTION_MARK = "campfire all happen here"
REQUIRE_DESCRIPTION = os.environ.get("AOP_REQUIRE_DESCRIPTION") == "1" or "--require-description" in sys.argv


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def main() -> int:
    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url())
        wait_loaded(page)
        open_poi_tab(page)

        # Read the Published-destinations rows: id + visible name + subtitle(blurb).
        rows = page.evaluate(
            """() => {
              const g = document.querySelector('.poi-list-group[data-group-id="published_destinations"]');
              if (!g) return null;
              return [...g.querySelectorAll('.poi-row')].map((b) => ({
                id: b.dataset.poiId,
                name: (b.querySelector('.poi-row-name') || {}).textContent || '',
                subtitle: (b.querySelector('.poi-row-subtitle') || {}).textContent || '',
              }));
            }"""
        )
        check("Published destinations group renders rows (from the baked core POIs)",
              bool(rows), f"rows={rows}")
        rows = rows or []
        names = [r["name"] for r in rows]

        edited = next((r for r in rows if r["name"] == EDITED_NAME), None)
        if edited is not None:
            # Author-path applied: prove the edited value is served + archived is gone.
            print("  [INFO] slice-1 author export is applied -- proving the round-trip.")
            check("edited POI blurb (new value) appears in its subtitle",
                  EDITED_BLURB_MARK in edited["subtitle"], f"subtitle={edited['subtitle']!r}")
            check("archived POI is ABSENT from the baked viewer (edit->core->bake->serve)",
                  ARCHIVED_NAME not in names, f"names={names}")
        elif REQUIRE_AUTHOR:
            # Author proof was demanded but the edit isn't served -- do NOT degrade
            # to baseline-PASS; that silent fallback is exactly what made an
            # earlier "PASS" fail to prove the round-trip.
            check("author edit REQUIRED (--require-author) and present in the baked viewer",
                  False, f"edit {EDITED_NAME!r} absent; apply the slice-1 export + bake first. names={names}")
        else:
            # Baseline / restored state: the serve path still carries core POIs.
            print("  [INFO] slice-1 author export NOT applied (committed state) -- "
                  "verifying the baseline serve path. Re-prove with apply + bake (see docstring).")
            for nm in BASELINE_NAMES:
                check(f"baseline destination {nm!r} served from core via the bake",
                      nm in names, f"names={names}")

        # Slice-3 positive assertion: the renamed `description` reached the rendered
        # subtitle (main.js reads props.description; the served bake emits description).
        if REQUIRE_DESCRIPTION:
            pav = next((r for r in rows if r["name"] == "AOP Pavilion"), None)
            check("published POI subtitle carries the DB description (props.description -> rendered DOM)",
                  pav is not None and DESCRIPTION_MARK in pav.get("subtitle", ""),
                  f"pavilion subtitle={pav['subtitle']!r}" if pav else f"no Pavilion row; names={names}")

        check("no console errors during POI render", not console_errors,
              "; ".join(console_errors[:3]))
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("baked-pois author verification: FAIL")
        return 1
    print("baked-pois author verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
