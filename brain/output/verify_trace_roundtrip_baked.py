#!/usr/bin/env python3
"""Verify the trail/point/polygon trace round-trip after the 2026-06-14 bakes:
  1. Export Waypoints layer now sources the SERVED waypoint gold (24), not the
     pre-trace stubs (1).
  2. Import no longer strips the baked "<number> <name>" ("1 Launchpad" survives).

NON-DESTRUCTIVE: drives the real export/import functions against a freshly-baked
SVG with the live served gold as the provenance baseline. Reads website/data
read-only; writes nothing there. (The generated export keeps data-fid/data-kind;
the real Affinity master strips data-* — that stripped-attr path is covered by
verify_waypoint_star_durability.py. This proves the export source + number-name.)
"""
import json, sys
from pathlib import Path
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "mvp/scripts"))
DATA = REPO / "website/data"
SVG = "{http://www.w3.org/2000/svg}"

from import_illustrator_trace import (
    load_meta, collect_layer, import_points, import_trails,
    preserve_unmatched_authored, _is_dropped_cemetery,
)

EXPORT_SVG = REPO / "brain/output/illustrator_trace/aop_satellite_trace.svg"

results = []
def check(label, cond, extra=""):
    results.append((bool(cond), label, extra))
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  -- {extra}" if extra else ""))

served_wp = json.loads((DATA / "gold_aop_waypoints_traced.geojson").read_text())["features"]
served_wp_names = {(f["properties"].get("name") or "").lower() for f in served_wp}
served_tn = json.loads((DATA / "gold_aop_trail_network.geojson").read_text())

root = ET.parse(EXPORT_SVG).getroot()
meta = load_meta(root, EXPORT_SVG)

# ---- 1. EXPORT: Waypoints layer reflects the served gold -------------------
print("\n== EXPORT Waypoints layer ==")
wlay = collect_layer(root, "Waypoints")
circles = [c for c in wlay.iter(f"{SVG}circle")]
svg_wp_names = set()
for c in circles:
    t = c.find(f"{SVG}title")
    if t is not None and t.text:
        svg_wp_names.add(t.text.lower())
check("Waypoints layer present", wlay is not None)
check("24 served waypoints exported (was 1 stub)", len(circles) == 24, f"{len(circles)} circles")
check("export waypoint names == served waypoint names", svg_wp_names == served_wp_names,
      f"missing={served_wp_names - svg_wp_names} extra={svg_wp_names - served_wp_names}")
check("Hot Rocks Comp Pad in export", "hot rocks comp pad" in svg_wp_names)
check("Gravity Gauntlet in export", "gravity gauntlet" in svg_wp_names)
check("AOP Pavilion NOT resurrected (user deleted it)", "aop pavilion" not in svg_wp_names)
check("off-park cemeteries absent from export",
      not any(n in svg_wp_names for n in ("tate cemetery", "bible cemetery", "gilliam cemetery")))
check("Ellis Cemetery present (in-park inholding)", "ellis cemetery" in svg_wp_names)

# ---- 2. ROUND-TRIP waypoints: nothing dropped, authored props carried ------
print("\n== ROUND-TRIP waypoints (import against served gold as prior) ==")
wp_by_name = {(f["properties"].get("name") or "").lower(): f for f in served_wp
              if f["properties"].get("name")}
pts, matched = import_points(meta, wlay, wp_by_name)
pts = [p for p in pts if not _is_dropped_cemetery(p["properties"].get("name"))]
preserved = preserve_unmatched_authored(served_wp, matched, _is_dropped_cemetery)
total = len(pts) + len(preserved)
check("all 24 re-imported (no waypoint dropped)", total == 24, f"{len(pts)} imported + {len(preserved)} preserved")
def find(name):
    for p in pts:
        if (p["properties"].get("name") or "").lower() == name:
            return p["properties"]
    return {}
hr = find("hot rocks comp pad")
gg = find("gravity gauntlet")
fp = find("firepit")
ellis = find("ellis cemetery")
check("Hot Rocks ★ carried", hr.get("highlight") is True)
check("Hot Rocks description carried", bool(hr.get("description")))
check("Hot Rocks kind carried (comp pad)", hr.get("kind") == "comp pad", repr(hr.get("kind")))
check("Gravity Gauntlet ★ carried", gg.get("highlight") is True)
check("Gravity Gauntlet location_tag carried", gg.get("location_tag") == "#gravity-gauntlet", repr(gg.get("location_tag")))
check("Firepit location_tag carried", fp.get("location_tag") == "#firepit", repr(fp.get("location_tag")))
check("Ellis description carried", bool(ellis.get("description")))
stars = sum(1 for p in pts if p["properties"].get("highlight") is True)
check("both ★ waypoints survive", stars == 2, f"{stars} starred")

# ---- 3. ROUND-TRIP trails: "1 Launchpad" survives (no number-strip) --------
print("\n== ROUND-TRIP trails (number-name no longer stripped) ==")
by_id, by_name, by_tn = {}, {}, {}
for f in served_tn["features"]:
    pp = f["properties"]
    if pp.get("id"): by_id[pp["id"]] = f
    if pp.get("name"): by_name[str(pp["name"]).lower()] = f
    if pp.get("trail_number") is not None: by_tn[pp["trail_number"]] = f
tlay = collect_layer(root, "Gold Trails")
tf = import_trails(meta, tlay, by_id, by_name, by_tn)
launch = next((f["properties"] for f in tf
               if (f["properties"].get("name") or "").lower().endswith("launchpad")), {})
check("Launchpad re-imports as '1 Launchpad' (NOT stripped)", launch.get("name") == "1 Launchpad", repr(launch.get("name")))
check("Launchpad trail_number carried (1)", launch.get("trail_number") == 1)
check("Launchpad gold provenance carried", launch.get("maturity") == "gold")
numname = sum(1 for f in tf if (lambda n, t: n and t is not None and n.split()[0].isdigit() and int(n.split()[0]) == t)(f["properties"].get("name"), f["properties"].get("trail_number")))
check("number-name preserved across the network (~80 trails)", numname >= 78, f"{numname} number-name trails")
carried = sum(1 for f in tf if f["properties"].get("maturity"))
check("trail provenance carried (120 gold)", carried == 120, f"{carried} carried")
check("130 trails total round-trip", len(tf) == 130, f"{len(tf)}")

# ---- guard: served gold untouched ------------------------------------------
print("\n== served gold untouched (read-only test) ==")
after = json.loads((DATA / "gold_aop_waypoints_traced.geojson").read_text())["features"]
check("served waypoint gold unchanged", len(after) == 24 and after == served_wp)

passed = sum(1 for ok, _, _ in results if ok)
print(f"\n{'='*60}\n{passed}/{len(results)} checks PASS")
sys.exit(0 if passed == len(results) else 1)
