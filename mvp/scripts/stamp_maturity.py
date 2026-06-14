#!/usr/bin/env python3
"""Stamp the data-maturity tier onto every served collection's `_meta`.

Decision (2026-06-05, user): "we have different data types. raw, baked, source,
gold... only current dataset that is gold is trails. region callouts are silver,
pending text review. gold data is not un-editable, just locked — unlock first.
gold data should share a common schema; this should power our editor."

The maturity tier is the THIRD axis of the data (see brain/research/
data_maturity_tiers.md): orthogonal to provenance (`source`, a per-feature field
in the CMFS) and to the source-register zones (`raw -> core -> publish`). It is a
per-FILE review-state label that lives in `_meta`, exactly like the trail
network's existing self-describing gold block (export_gold_trail_network.py):

  gold      curated, reviewed, first-party, final. Locked (unlock to edit).
  silver    curated/real first-party but pending review (text, confirmation,
            or placeholder-real data). Locked.
  editor    first-party editor scratch (drawn / seed). Unlocked.
  derived   machine-computed reference (you don't edit a contour line). Unlocked.
  reference external raw context we trace against but don't own. Unlocked.

This writes `_meta.maturity` / `_meta.group` / `_meta.locked` (+ a short note)
onto each served GeoJSON, preserving any existing `_meta` (the trail gold block).
It also records the tier per layer in website/data/_schema.json so the contract
is self-describing.

IMPORTANT run order (mirrors bake_panel_overrides.py):
  rebake_canonical.py        # machine refresh from data/raw/ (wipes _meta)
  bake_panel_overrides.py    # human curation on top
  export_gold_trail_network.py   # trail gold block
  THIS                       # maturity stamp — must run LAST
rebake_canonical.py now carries a live `_meta` forward, so a re-bake no longer
silently drops the stamp; re-running this after any pipeline step is still the
safe, idempotent way to guarantee it.

Usage:
  python3 mvp/scripts/stamp_maturity.py            # stamp + update _schema.json
  python3 mvp/scripts/stamp_maturity.py --check    # report only, no write
"""
from __future__ import annotations
import json
import sys
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "website" / "data"
SCHEMA = DATA / "_schema.json"

# Tier legend (also written to _schema.json so the contract is self-describing).
# MEDALLION tiers (user, 2026-06-14): "rename all our data sources to bronze /
# silver / gold". gold = curated/verified first-party AND accepted in production;
# silver = first-party but pending review; bronze = raw / inspection / not yet
# promoted to production (the former editor + derived + reference + raw all read
# as un-promoted). `delete` is NOT a medallion quality tier — it is an orthogonal
# lifecycle flag (staged for removal), kept so the Delete review-pen still works.
TIERS = OrderedDict([
    ("gold", "Curated/verified first-party, accepted in production. Locked — unlock to edit."),
    ("silver", "First-party but pending review (text / confirmation / placeholder-real). Locked."),
    ("bronze", "Raw / inspection / not yet promoted to production. Unlocked."),
    ("delete", "Staged for removal — sits in the Delete group until the actual delete is approved. Unlocked."),
])
LOCKED_TIERS = {"gold", "silver"}

# filename -> (tier, group display name). The group name is the editor grouping
# this file lives under — "the group maps to the file it lives in" (user, 2026-06-05).
# filename -> (medallion tier, group display name). Tier = "did it make it to
# production?" — gold = curated/verified AND a layer the read viewer renders;
# silver = first-party pending review; bronze = not in production / not promoted.
# A FILE tier is the collection's overall state; a mixed file (e.g. buildings:
# 5 gold + Shower House bronze; cemeteries: Ellis gold + 3 bronze) carries the
# exception at the per-FEATURE `maturity` field (see set_feature_maturity.py).
MATURITY = OrderedDict([
    # -- gold: verified first-party + accepted production layers (user, 2026-06-14:
    #    "derived/reference layers that render in production are gold") --
    ("aop_trail_network.geojson",            ("gold",   "AOP trail network")),
    ("aop_buildings.geojson",                ("gold",   "Park buildings")),  # Shower House is per-feature bronze
    ("aop_waypoints_traced.geojson",         ("gold",   "Camp waypoints / POIs")),
    ("aop_landcover.geojson",                ("gold",   "Land cover (NAIP)")),
    ("aop_landcover_9patch.geojson",         ("gold",   "Land cover — 9-patch")),
    ("aop_contours.geojson",                 ("gold",   "Lidar contours")),
    ("aop_activity_hotspots.geojson",        ("gold",   "Activity hotspots (GPX dwell)")),
    ("aop_roads.geojson",                    ("gold",   "Asphalt roads (USGS National Map)")),
    ("aop_water.geojson",                    ("gold",   "Hydrography (USGS NHD)")),
    # -- gold: promoted from silver 2026-06-14 (user: context callouts + publish to gold) --
    ("aop_visitor_context_callouts.geojson", ("gold",   "Visitor context callouts")),
    ("publish.geojson",                      ("gold",   "Publishable (boundary · trails · trailheads)")),
    # -- bronze: raw / inspection / not yet promoted to production --
    ("aop_buildings_traced.geojson",         ("bronze", "Park buildings (raw hand-trace source)")),
    ("aop_editor_seed_pois.geojson",         ("bronze", "Drawn POIs (seed) — retired panel group")),
    ("aop_user_features.geojson",            ("bronze", "Drawn features — retired panel group")),
    ("aop_9_patch.geojson",                  ("bronze", "9-patch acquisition AOI")),
    ("aop_cemeteries.geojson",               ("bronze", "Cemeteries (TN Comptroller)")),  # Ellis is per-feature gold
    ("aop_lidar_tiles.geojson",              ("bronze", "Lidar tile index (USGS 3DEP)")),
    ("osm_aop_9patch.geojson",               ("bronze", "OSM cluster")),
    ("osm_aop_named.geojson",                ("bronze", "OSM named landmarks")),
    ("sfwda_numbered_trails.geojson",        ("bronze", "SFWDA numbered trails (extract)")),
    ("sfwda_traced_markers.geojson",         ("bronze", "SFWDA traced markers (extract)")),
    ("sfwda_trails_edited.geojson",          ("bronze", "SFWDA trails (edited extract)")),
    # -- delete: staged for removal (lifecycle flag, orthogonal to the medallion).
    #  Springs (part of aop_water.geojson) and OSM park polygon (part of
    #  osm_aop_9patch.geojson) are ALSO in the Delete panel group, but their files
    #  carry layers that stay, so the files keep their own tier — those are
    #  panel-only moves until the file is split. --
    ("aop_synthetic_activity_hotspots.geojson", ("delete", "Simulated Saturday activity (staged for removal)")),
    ("aop_synthetic_activity_tracks.geojson",   ("delete", "Simulated Saturday activity (staged for removal)")),
    ("sfwda_traced_trails.geojson",          ("delete", "SFWDA traced trails (staged for removal)")),
])

NOTES = {
    "gold": "gold — verified first-party, accepted in production; locked, unlock to edit",
    "silver": "silver — pending review; locked, unlock to edit",
    "bronze": "bronze — raw / inspection / not yet promoted to production; unlocked",
    "delete": "delete — staged for removal; in the Delete group until the actual delete is approved",
}


def stamp_file(path: Path, tier: str, group: str, check: bool) -> str:
    """Merge maturity fields into the file's top-level `_meta`. Returns status."""
    doc = json.loads(path.read_text())
    if doc.get("type") != "FeatureCollection":
        return "skip (not a FeatureCollection)"
    meta = doc.get("_meta")
    if not isinstance(meta, dict):
        meta = {}
    locked = tier in LOCKED_TIERS
    before = (meta.get("maturity"), meta.get("group"), meta.get("locked"))
    after = (tier, group, locked)
    # Preserve every existing _meta key (e.g. the trail gold block); only set ours.
    meta["maturity"] = tier
    meta["group"] = group
    meta["locked"] = locked
    meta["maturity_note"] = NOTES[tier]
    doc["_meta"] = meta
    if not check:
        # match the served files' compact formatting (no whitespace padding)
        path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
    return "unchanged" if before == after else f"{before[0] or '—'} -> {tier}"


def update_schema(stamped: dict, check: bool) -> None:
    if not SCHEMA.exists():
        print(f"  ! {SCHEMA.name} not found — skipping schema update")
        return
    schema = json.loads(SCHEMA.read_text())
    schema["maturity_tiers"] = dict(TIERS)
    layers = schema.get("layers", {})
    for fname, (tier, _group) in stamped.items():
        if fname in layers and isinstance(layers[fname], dict):
            layers[fname]["maturity"] = tier
    if not check:
        SCHEMA.write_text(json.dumps(schema, ensure_ascii=False, indent=2))


def main() -> int:
    check = "--check" in sys.argv[1:]
    print(f"{'CHECK' if check else 'STAMP'} data-maturity tiers in {DATA}\n")
    by_tier: dict[str, int] = {}
    missing = []
    for fname, (tier, group) in MATURITY.items():
        path = DATA / fname
        if not path.exists():
            missing.append(fname)
            continue
        status = stamp_file(path, tier, group, check)
        by_tier[tier] = by_tier.get(tier, 0) + 1
        print(f"  [{tier:9s}] {fname:42s} {group:42s} {status}")
    update_schema(MATURITY, check)
    # stamp_maturity authors the served files' `_meta`; promote it (and the
    # owner-authored collection provenance) into the COMMITTED store of record so the
    # bake can reproduce `_meta` on a fresh volume without the prior served file
    # (reference-bake-no-meta-on-fresh-volume). One store, captured by the same author.
    try:
        import regen_meta
        regen_meta.capture(check=check)
    except Exception as exc:  # never let the store sync break the stamp itself
        print(f"  ! regen_meta.capture skipped ({exc})")
    print("\nper tier: " + ", ".join(f"{t}={by_tier.get(t, 0)}" for t in TIERS))
    if missing:
        print("missing (not on disk, skipped): " + ", ".join(missing))
    print(("\n--check: no files written." if check
           else f"\nStamped {sum(by_tier.values())} files + updated {SCHEMA.name}."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
