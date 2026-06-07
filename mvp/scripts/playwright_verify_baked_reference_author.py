#!/usr/bin/env python3
"""Going-gold REFERENCE-layer verifier (one generic verifier for slices 2-5).

A reference layer (buildings, cemeteries, visitor callouts, trails) bakes from
PostGIS core.features to its OWN served file and the viewer renders it as a
MapLibre source. This proves the viewer CONSUMES the baked layer, tile-independently
(per the corrected Observable acceptance standard + C4): paint is tile-bound and
blocked headless, so it reads the loaded source DATA, not the paint. It reuses the
proven star_collector `wait_loaded` gate ("publish feature(s) loaded", set inside
`map.on('load')`, which DOES fire headless) then reads
`window.AOP_HOST_MAP.getSource('<id>').serialize().data.features`. NO `networkidle`,
NO `queryRenderedFeatures`/`querySourceFeatures`, NO `publishDataCache`.
Card: brain/tasks/06_going_gold/gold_migration.md (slices 2-5).

ONE verifier, configured per layer in LAYERS (no per-layer copy -- Quartermaster).

Two-state, so it stays green in the durable suite (committed file) AND proves the
bake path:
  - baseline: the layer's features load with their attrs (a distinguishing attr
    value checked) -- the serve path is sound on committed/baked state.
  - --require-baked (AOP_REQUIRE_BAKED=1): a marker authored into core.features then
    baked MUST appear in the viewer's loaded source, so a "PASS" cannot come from a
    stale standalone file. FAILs if absent (cannot degrade to baseline-PASS).

Run (durable suite, viewer on :8001):
  python3 mvp/scripts/playwright_verify_baked_reference_author.py --layer buildings
  python3 mvp/scripts/playwright_verify_baked_reference_author.py --layer cemeteries
Re-prove the bake path (mutate core, bake, verify, restore -- see the slice runner):
  ... author _baked_marker into core.features + bash export_publish_geojson.sh ...
  python3 mvp/scripts/playwright_verify_baked_reference_author.py --layer buildings --require-baked
"""
from __future__ import annotations

import argparse
import os
import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url
# Reuse the proven headless-safe gate -- do NOT re-implement boot/wait.
from playwright_verify_star_collector import wait_loaded

# The generic marker the --require-baked round-trip authors into core then bakes.
MARKER_KEY = "_baked_marker"
MARKER_VAL = "BAKED-OK"

# Per-layer config. `source` = the MapLibre source id(s) the viewer registers (a
# string, or a LIST when the viewer splits one served file into several sources,
# e.g. visitor callouts -> 'visitor-context' + 'brand-logos'). `count` = features
# expected across those sources. `names` = the DISTINCT display names expected.
# `attr` = (matcher_props, field, value): a distinguishing attrs value that must
# survive core->bake->serve->viewer (not just feature count).
LAYERS = {
    "buildings": {
        "source": "fema-buildings",
        "count": 5,
        "names": ["880 Ellis Cove Road", "1010 Ellis Cove Road", "1033 Ellis Cove Road",
                  "665 Ellis Cove Road", "889 Ellis Cove Road"],
        "attr": ({"id": "{41014ca8-1baa-4dcc-8a6d-c544eb2a745c}"},
                 "facility_role", "Pavilion / G-Central — registration, awards, campfire"),
    },
    "cemeteries": {
        "source": "cemeteries",
        "count": 8,
        "names": ["Tate Cemetery", "Gilliam Cemetery", "Bible Cemetery", "Ellis Cemetery"],
        "attr": ({"parcel_id": "110 008.04", "geom_role": "marker"},
                 "burial_count", 12),
    },
    # The viewer splits the one served file by `kind` into two map sources.
    "visitor": {
        "source": ["visitor-context", "brand-logos"],
        "count": 4,
        "names": ["South Pittsburg / Kimball supply run", "Monteagle plateau services",
                  "AOP badge", "Rock Warblers"],
        "attr": ({"id": "aop_badge"}, "icon_image", "brand-aop-badge"),
    },
    # 120 LineStrings; `names` is a representative subset (issubset check, not all
    # 120). `attr` checks a trail's baked difficulty `color` (load-bearing: the
    # gold network is self-contained, each feature carries its own colour).
    "trails": {
        "source": "aop-trail-network",
        "count": 120,
        "names": ["15", "27"],
        "attr": ({"id": "sfwda-0"}, "color", "#1f9d3a"),
    },
}


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--layer", required=True, choices=sorted(LAYERS), help="reference layer to verify")
    ap.add_argument("--require-baked", action="store_true",
                    help="FAIL unless the baked marker is present (proves the bake path)")
    args = ap.parse_args()
    require_baked = args.require_baked or os.environ.get("AOP_REQUIRE_BAKED") == "1"
    cfg = LAYERS[args.layer]
    matcher, attr_field, attr_value = cfg["attr"]

    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url())
        wait_loaded(page)

        sources = cfg["source"] if isinstance(cfg["source"], list) else [cfg["source"]]
        feats = page.evaluate(
            """(sourceIds) => {
              const m = window.AOP_HOST_MAP;
              if (!m) return null;
              const out = [];
              for (const id of sourceIds) {
                const s = m.getSource(id);
                if (!s) continue;
                const data = s.serialize().data;
                for (const f of ((data && data.features) || [])) out.push(f.properties || {});
              }
              return out;
            }""",
            sources,
        )
        check(f"viewer loaded the '{args.layer}' source(s) ({', '.join(sources)}) tile-independently",
              bool(feats), f"features={None if feats is None else len(feats)}")
        feats = feats or []

        check(f"{cfg['count']} {args.layer} features present in the loaded source",
              len(feats) == cfg["count"], f"got {len(feats)}")
        names = {f.get("name") for f in feats}
        check(f"expected distinct {args.layer} names present",
              set(cfg["names"]).issubset(names), f"names={sorted(n for n in names if n)}")

        matched = next((f for f in feats
                        if all(f.get(k) == v for k, v in matcher.items())), None)
        check(f"distinguishing attr '{attr_field}' survived core->bake->serve->viewer",
              bool(matched) and matched.get(attr_field) == attr_value,
              f"{attr_field}={matched.get(attr_field)!r}" if matched else f"feature {matcher} absent")

        marked = next((f for f in feats if f.get(MARKER_KEY) == MARKER_VAL), None)
        if marked is not None:
            print(f"  [INFO] baked marker present -- the bake path is proven "
                  f"({MARKER_KEY}={MARKER_VAL} on {marked.get('name')!r}).")
        elif require_baked:
            check("baked marker REQUIRED (--require-baked) and present in the viewer source",
                  False, f"{MARKER_KEY}={MARKER_VAL} absent; author it into core.features + re-bake first")
        else:
            print("  [INFO] no baked marker (committed/baseline state) -- verifying the baseline "
                  "serve path. Re-prove with the marker round-trip (see docstring).")

        check(f"no console errors during {args.layer} load", not console_errors,
              "; ".join(console_errors[:3]))
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print(f"baked-{args.layer} author verification: FAIL")
        return 1
    print(f"baked-{args.layer} author verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
