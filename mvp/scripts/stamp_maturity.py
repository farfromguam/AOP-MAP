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
TIERS = OrderedDict([
    ("gold", "Curated, reviewed, first-party, final. Locked — unlock to edit."),
    ("silver", "Curated first-party, pending review (text / confirmation / placeholder-real). Locked."),
    ("editor", "First-party editor scratch (drawn / seed). Unlocked."),
    ("derived", "Machine-computed reference (not hand-edited). Unlocked."),
    ("reference", "External raw context we trace against but don't own. Unlocked."),
    ("delete", "Staged for removal — sits in the Delete group until the actual delete is approved. Unlocked."),
])
LOCKED_TIERS = {"gold", "silver"}

# filename -> (tier, group display name). The group name is the editor grouping
# this file lives under — "the group maps to the file it lives in" (user, 2026-06-05).
MATURITY = OrderedDict([
    # -- gold: the only gold dataset today is the merged trail network --
    ("aop_trail_network.geojson",            ("gold",      "AOP trail network")),
    # -- silver: real first-party, pending review --
    ("aop_visitor_context_callouts.geojson", ("silver",    "Visitor context callouts")),
    ("aop_buildings.geojson",                ("silver",    "Park buildings")),
    ("publish.geojson",                      ("silver",    "Publishable (boundary · trails · trailheads)")),
    # -- editor scratch (first-party, unlocked) --
    # (aop_brand_logos.geojson retired 2026-06-05: the AOP + Rock Warblers logos
    #  were merged into aop_visitor_context_callouts.geojson as kind=brand_logo
    #  point features. They inherit that file's silver _meta. The "Map editor"
    #  panel group retired 2026-06-05; the Brand logos node moved up to Silver and
    #  now tags itself silver to match the file it lives in.)
    # These two editor-scratch files have no panel node anymore (the draw groups +
    #  Drawn POIs retired with the Map editor group); the host map still owns the
    #  sources. Left at editor tier — not staged for delete (user said "retiring,"
    #  not "delete"; nothing of value to stage — userFeatures is empty, editor-poi
    #  holds 1 seed POI).
    ("aop_editor_seed_pois.geojson",         ("editor",    "Drawn POIs (seed) — retired panel group")),
    ("aop_user_features.geojson",            ("editor",    "Drawn features — retired panel group")),
    # -- derived: machine outputs, never gold (do-not-gold list) --
    ("aop_landcover.geojson",                ("derived",   "Land cover (NAIP)")),
    ("aop_landcover_9patch.geojson",         ("derived",   "Land cover — 9-patch")),
    ("aop_contours.geojson",                 ("derived",   "Lidar contours")),
    ("aop_activity_hotspots.geojson",        ("derived",   "Activity hotspots (GPX dwell)")),
    # -- delete: staged for removal (user, 2026-06-05). Whole-file members only.
    #  Springs (part of aop_water.geojson) and OSM park polygon (part of
    #  osm_aop_9patch.geojson) are ALSO in the Delete panel group, but their files
    #  carry layers that stay, so the files keep their reference tier — those are
    #  panel-only moves until the file is split. --
    ("aop_synthetic_activity_hotspots.geojson", ("delete", "Simulated Saturday activity (staged for removal)")),
    ("aop_synthetic_activity_tracks.geojson",   ("delete", "Simulated Saturday activity (staged for removal)")),
    ("sfwda_traced_trails.geojson",          ("delete",    "SFWDA traced trails (staged for removal)")),
    # -- reference: external raw context (do-not-gold list) --
    ("aop_9_patch.geojson",                  ("reference", "9-patch acquisition AOI")),
    ("aop_cemeteries.geojson",               ("reference", "Cemeteries (TN Comptroller)")),
    ("aop_lidar_tiles.geojson",              ("reference", "Lidar tile index (USGS 3DEP)")),
    ("aop_roads.geojson",                    ("reference", "Asphalt roads (USGS National Map)")),
    ("aop_water.geojson",                    ("reference", "Hydrography (USGS NHD)")),
    ("osm_aop_9patch.geojson",               ("reference", "OSM cluster")),
    ("osm_aop_named.geojson",                ("reference", "OSM named landmarks")),
    ("sfwda_numbered_trails.geojson",        ("reference", "SFWDA numbered trails (extract)")),
    ("sfwda_traced_markers.geojson",         ("reference", "SFWDA traced markers (extract)")),
    ("sfwda_trails_edited.geojson",          ("reference", "SFWDA trails (edited extract)")),
])

NOTES = {
    "gold": "gold — reviewed first-party; locked, unlock to edit",
    "silver": "silver — pending review; locked, unlock to edit",
    "editor": "editor scratch — first-party, unlocked",
    "derived": "derived — machine output, not hand-edited",
    "reference": "reference — external raw context",
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
    print("\nper tier: " + ", ".join(f"{t}={by_tier.get(t, 0)}" for t in TIERS))
    if missing:
        print("missing (not on disk, skipped): " + ", ".join(missing))
    print(("\n--check: no files written." if check
           else f"\nStamped {sum(by_tier.values())} files + updated {SCHEMA.name}."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
