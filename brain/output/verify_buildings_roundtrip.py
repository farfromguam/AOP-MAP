#!/usr/bin/env python3
"""Verify the BUILDINGS (polygon) round-trip after wiring it into the served gold
(the full export->edit->re-upload loop now works for all three geometry types).

NON-DESTRUCTIVE: drives the real import_polys against the freshly-baked SVG with
the live served gold as the provenance baseline. Reads website/data read-only;
writes nothing there. (The end-to-end main() write path — _meta carry, served-file
write, all-three-types lossless — is exercised separately by the backup/restore
real run in the shell; this proves the per-feature logic + edit-tracking.)
"""
import copy, json, sys
from pathlib import Path
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "mvp/scripts"))
DATA = REPO / "website/data"
SVG = "{http://www.w3.org/2000/svg}"

from import_illustrator_trace import load_meta, collect_layer, import_polys
from import_fema_buildings import ring_centroid

EXPORT_SVG = REPO / "brain/output/illustrator_trace/aop_satellite_trace.svg"

results = []
def check(label, cond, extra=""):
    results.append((bool(cond), label, extra))
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  -- {extra}" if extra else ""))

served = json.loads((DATA / "gold_aop_buildings.geojson").read_text())
served_feats = served["features"]
prior_by_name = {(f["properties"].get("name") or "").lower(): f for f in served_feats
                 if f["properties"].get("name")}
served_names = set(prior_by_name)

root = ET.parse(EXPORT_SVG).getroot()
meta = load_meta(root, EXPORT_SVG)
blay = collect_layer(root, "Buildings")

# ---- 1. round-trip: all 6 carried, provenance preserved -------------------
print("\n== BUILDINGS round-trip (import_polys vs served gold) ==")
bf, matched = import_polys(meta, blay, prior_by_name)
check("Buildings layer present", blay is not None)
check("6 buildings re-imported", len(bf) == 6, f"{len(bf)}")
check("all matched by name (none thin/new)", matched == served_names,
      f"missing={served_names - matched} extra={matched - served_names}")
def find(name):
    for f in bf:
        if (f["properties"].get("name") or "").lower() == name:
            return f["properties"]
    return {}
fo = find("front office")
check("Front Office FEMA address carried", fo.get("address") == "880 Ellis Cove Road", repr(fo.get("address")))
check("Front Office aop_facility carried", fo.get("aop_facility") is True)
check("Front Office ★ highlight carried", fo.get("highlight") is True)
check("Front Office FEMA source/permission carried",
      fo.get("source") == "ORNL" and "FEMA" in (fo.get("permission") or ""))
check("Front Office occupancy provenance carried", bool(fo.get("primary_occupancy")))
facilities = sum(1 for f in bf if f["properties"].get("aop_facility") is True)
check("4 facilities carried (Front Office/Farmhouse/Pavilion/Shower House)", facilities == 4, f"{facilities}")
nthin = sum(1 for f in bf if f["properties"].get("source") == "illustrator_trace_new")
check("0 buildings flattened to thin/new", nthin == 0, f"{nthin}")

# ---- 2. unchanged footprints carried VERBATIM (no FEMA-area overwrite, no pin jump)
print("\n== unchanged footprints carried verbatim (re-import is a no-op) ==")
import math
def meters(dlng, dlat, lat):
    return math.hypot(dlng * 111320.0 * math.cos(math.radians(lat)), dlat * 110574.0)
# the fresh export reflects current gold, so EVERY building's footprint is unchanged
# -> each is carried verbatim: centroid + area + geometry must equal prior EXACTLY.
cent_exact = area_exact = geom_exact = 0
for f in bf:
    p = f["properties"]; nm = (p.get("name") or "").lower()
    pri = prior_by_name.get(nm, {})
    prip = pri.get("properties", {})
    if p.get("centroid_lng") == prip.get("centroid_lng") and p.get("centroid_lat") == prip.get("centroid_lat"):
        cent_exact += 1
    if p.get("area_sqm") == prip.get("area_sqm") and p.get("area_sqft") == prip.get("area_sqft"):
        area_exact += 1
    if f["geometry"] == pri.get("geometry"):
        geom_exact += 1
check("all 6 centroids preserved EXACTLY (pins do not move)", cent_exact == 6, f"{cent_exact}/6")
check("all 6 areas preserved EXACTLY (FEMA source area not overwritten)", area_exact == 6, f"{area_exact}/6")
check("all 6 geometries preserved EXACTLY (true no-op)", geom_exact == 6, f"{geom_exact}/6")
fo665 = find("665 ellis cove road")
check("FEMA source area verbatim (665 Ellis = 123.49 m², not the 110 re-measure)",
      fo665.get("area_sqm") == 123.49, f"{fo665.get('area_sqm')}")

# ---- 3. edit-tracking: move a footprint, centroid follows ------------------
print("\n== edit-tracking: a moved footprint moves its centroid (pin follows) ==")
# Build a synthetic edited Buildings layer: shift Front Office's path east by a
# large offset in the SVG frame, re-import, confirm the centroid tracks the move.
import re as _re
fo_path = None
for el in blay.iter(f"{SVG}path"):
    t = el.find(f"{SVG}title")
    if t is not None and t.text and t.text.lower() == "front office":
        fo_path = el
        break
check("found Front Office path to perturb", fo_path is not None)
if fo_path is not None:
    d = fo_path.get("d")
    # shift every "x,y" coord pair +50 metres east (frame units = UTM metres)
    def shift(m):
        x, y = m.group(1), m.group(2)
        return f"{float(x)+50:.2f},{y}"
    fo_path.set("d", _re.sub(r"(-?\d+\.?\d*),(-?\d+\.?\d*)", shift, d))
    bf2, _ = import_polys(meta, blay, prior_by_name)
    fo2 = next((f["properties"] for f in bf2 if (f["properties"].get("name") or "").lower() == "front office"), {})
    moved = meters(fo2["centroid_lng"] - fo["centroid_lng"], fo2["centroid_lat"] - fo["centroid_lat"], fo["centroid_lat"])
    check("moved footprint -> centroid tracks (~50 m east, pin follows)", 45 < moved < 55, f"{moved:.1f} m")
    check("edited building recomputes its area (no longer the verbatim FEMA value)",
          fo2.get("area_sqm") != fo.get("area_sqm"), f"edited={fo2.get('area_sqm')} vs verbatim={fo.get('area_sqm')}")
    check("edited building still keeps FEMA provenance (address/source/facility)",
          fo2.get("address") == "880 Ellis Cove Road" and fo2.get("aop_facility") is True)

# ---- 4. preserve unmatched: a building not in the SVG survives -------------
print("\n== preserve unmatched (a curated building absent from the SVG) ==")
# drop Pavilion from the prior index's match set by importing a layer missing it:
# simulate by removing Pavilion's path, re-import, confirm main()'s preserve step
# would keep it. (Here we replicate main()'s preserve logic.)
for el in list(blay):
    t = el.find(f"{SVG}title")
    if t is not None and t.text and t.text.lower() == "pavilion":
        blay.remove(el)
bf3, matched3 = import_polys(meta, blay, prior_by_name)
preserved = [f for f in served_feats if (f["properties"].get("name") or "").lower() not in matched3]
preserved_names = {(f["properties"].get("name") or "").lower() for f in preserved}
check("Pavilion dropped from SVG is NOT re-imported", "pavilion" not in matched3)
check("...but preserved from prior gold (non-destructive)", "pavilion" in preserved_names)
check("preserve carries Pavilion's full provenance",
      any(f["properties"].get("aop_facility") for f in preserved if (f["properties"].get("name") or "").lower()=="pavilion"))

# ---- guard: served gold untouched -----------------------------------------
print("\n== served gold untouched (read-only test) ==")
after = json.loads((DATA / "gold_aop_buildings.geojson").read_text())
check("served buildings gold unchanged", after == served)

passed = sum(1 for ok, _, _ in results if ok)
print(f"\n{'='*60}\n{passed}/{len(results)} checks PASS")
sys.exit(0 if passed == len(results) else 1)
