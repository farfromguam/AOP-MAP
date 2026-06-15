#!/usr/bin/env python3
"""Verify the camp-waypoint ★ (and authored fields) survive an Affinity re-import.

User: "fix the star durability … it needs to survive a db export or a re-import.
save it to the gold data directly. no shortcuts." Findings:
  - DB export is a NON-threat: gold_aop_waypoints_traced.geojson is a FILE-based gold
    layer; no DB/canonical bake regenerates it (only publish.geojson is PostGIS-exported).
  - The real threat was import_illustrator_trace.py's import_points(): it rebuilt every
    waypoint from the SVG with bare {name, kind}, STRIPPING highlight/description/
    location_tag on a re-import.

Fix (no shortcut — the star stays ON the gold feature and the pipeline preserves it):
  1. import_points() is now provenance-preserving (mirrors import_trails): a waypoint's
     edited geometry + name are the new truth, but its authored gold props (highlight,
     description, location_tag, …) carry forward from the prior gold by name.
  2. preserve_unmatched_authored() keeps prior ★/#tag POIs that AREN'T in the SVG (e.g.
     Gravity Gauntlet, added from a GPX straight to gold), so a curated destination
     survives a re-import even when the trace master doesn't carry it.

This drives the REAL code path: a synthetic edited Waypoints SVG (Hot Rocks moved +
a brand-new POI; GG/Firepit intentionally absent) re-imported against the ACTUAL
current gold as the prior. No real master is run (the in-repo SVG is a stale stub that
would gut the gold), and the live gold file is NOT written — this is read-only.

Run: python3 brain/output/verify_waypoint_star_durability.py
"""
import json, sys
from pathlib import Path
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "mvp/scripts"))
import import_illustrator_trace as imp  # noqa: E402

GOLD = REPO / "website/data/gold_aop_waypoints_traced.geojson"

SYNTH_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">'
    '<g inkscape:label="Waypoints" id="Waypoints">'
    '<circle inkscape:label="Hot Rocks Comp Pad" data-kind="comp pad" cx="120" cy="140" r="9"/>'
    '<circle inkscape:label="Brand New Lookout" cx="300" cy="200" r="9"/>'
    '</g></svg>'
)


def log(m): print(m, flush=True)


def main():
    prior = json.loads(GOLD.read_text())
    prior_feats = prior["features"]
    by_name = {(f["properties"].get("name") or "").lower(): f
               for f in prior_feats if f["properties"].get("name")}

    root = ET.fromstring(SYNTH_SVG)
    meta = imp.load_meta(root)                 # falls back to the real frame
    layer = imp.collect_layer(root, "Waypoints")
    pts, matched = imp.import_points(meta, layer, by_name)
    preserved = imp.preserve_unmatched_authored(prior_feats, matched, imp._is_dropped_cemetery)

    out = {(f["properties"].get("name") or "").lower(): f for f in pts}
    pres = {(f["properties"].get("name") or "").lower(): f for f in preserved}
    R = {
        "imported": [f["properties"].get("name") for f in pts],
        "preserved": [f["properties"].get("name") for f in preserved],
        "hot_rocks_props": out.get("hot rocks comp pad", {}).get("properties"),
        "new_poi_props": out.get("brand new lookout", {}).get("properties"),
        "gg_preserved_props": pres.get("gravity gauntlet", {}).get("properties"),
    }
    log(json.dumps(R, indent=2))

    hr = out.get("hot rocks comp pad", {}).get("properties", {})
    nl = out.get("brand new lookout", {}).get("properties", {})
    gg = pres.get("gravity gauntlet", {}).get("properties", {})
    hr_geom = out.get("hot rocks comp pad", {}).get("geometry", {})
    # geometry must be the EDITED point, not the prior one
    prior_hr = by_name.get("hot rocks comp pad", {}).get("geometry", {}).get("coordinates")

    checks = {
        "Hot Rocks re-imported (was in the SVG)": "hot rocks comp pad" in out,
        "Hot Rocks keeps its ★ (highlight carried)": hr.get("highlight") is True,
        "Hot Rocks keeps its description (carried)": str(hr.get("description", "")).startswith("Purpose-built"),
        "Hot Rocks geometry is the EDITED point (new truth)": hr_geom.get("coordinates") not in (None, prior_hr),
        "Hot Rocks marked re-imported (provenance note)": "re-imported" in str(hr.get("review_status", "")),
        "brand-new POI has NO star (thin props)": "brand new lookout" in out and nl.get("highlight") is None,
        "brand-new POI is thin {name,kind}": set(nl.keys()) == {"name", "kind"},
        "Gravity Gauntlet PRESERVED (★/#tag, not in the SVG)": "gravity gauntlet" in pres,
        "Gravity Gauntlet keeps its ★": gg.get("highlight") is True,
        "Gravity Gauntlet keeps its #location_tag": gg.get("location_tag") == "#gravity-gauntlet",
        "Firepit anchor (#tag) also preserved": "firepit" in pres,
        "Hot Rocks NOT double-counted in preserved": "hot rocks comp pad" not in pres,
        "a non-authored absent waypoint (RV Site 1) is NOT preserved": "rv site 1" not in pres,
        "live gold file untouched by this read-only test": json.loads(GOLD.read_text()) == prior,
    }
    print("\n--- CHECKS ---", flush=True)
    allok = True
    for name, ok in checks.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}", flush=True)
        allok = allok and ok
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'}", flush=True)
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
