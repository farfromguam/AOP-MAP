#!/usr/bin/env python3
"""Stamp the per-FEATURE medallion tier where a file is MIXED.

stamp_maturity.py sets the per-FILE `_meta.maturity` (the collection's overall
state). A few served files are mixed — some features made it to gold while their
siblings did not — so the exception rides on each feature's own `maturity` field
(user, 2026-06-14):

  - Cemeteries: "ellis cemetery made it from bronze to gold. no other cemeteries
    did." -> Ellis Cemetery features = gold; Tate / Bible / Gilliam = bronze.
  - Park buildings: "only 5 made it. others did not." -> the 5 curated ORNL
    footprints = gold; the raw-trace Shower House = bronze.

Medallion tiers: gold = curated/verified + accepted in production; silver =
pending review; bronze = not yet promoted. Idempotent — re-run any time.

Usage:
  python3 mvp/scripts/set_feature_maturity.py            # write
  python3 mvp/scripts/set_feature_maturity.py --check    # report only
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "website" / "data"

# file -> (gold_predicate, bronze tier for everything else). The predicate gets a
# feature's properties dict and returns True when that feature is gold.
RULES = {
    "aop_cemeteries.geojson": lambda p: "ellis" in str(p.get("name", "")).lower(),
    # The 5 curated ORNL footprints are gold; the raw Affinity hand-trace
    # (Shower House) is bronze until it's confirmed.
    "aop_buildings.geojson": lambda p: str(p.get("source", "")).strip().upper() == "ORNL",
}


def stamp(fname: str, is_gold, check: bool) -> str:
    path = DATA / fname
    if not path.exists():
        return f"{fname}: MISSING"
    doc = json.loads(path.read_text())
    changed = 0
    counts = {"gold": 0, "bronze": 0}
    for feat in doc.get("features", []):
        props = feat.setdefault("properties", {})
        tier = "gold" if is_gold(props) else "bronze"
        counts[tier] += 1
        if props.get("maturity") != tier:
            props["maturity"] = tier
            changed += 1
    if not check and changed:
        path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
    return f"{fname}: gold={counts['gold']} bronze={counts['bronze']} ({changed} changed)"


def main() -> int:
    check = "--check" in sys.argv[1:]
    print(f"{'CHECK' if check else 'SET'} per-feature medallion tiers\n")
    for fname, pred in RULES.items():
        print("  " + stamp(fname, pred, check))
    print("\n--check: no files written." if check else "\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
