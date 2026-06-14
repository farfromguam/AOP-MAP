#!/usr/bin/env python3
"""Rename served data-source files to carry their MEDALLION tier as a filename
prefix (user, 2026-06-14: "rename all our data sources to bronze_* silver_* or
gold_*"), and sweep the runtime references so nothing 404s.

  aop_trail_network.geojson      -> gold_aop_trail_network.geojson
  aop_cemeteries.geojson         -> bronze_aop_cemeteries.geojson
  publish.geojson                -> gold_publish.geojson
  aop_synthetic_activity_*.geojson -> delete_aop_synthetic_activity_*.geojson

Tier per file is the single source of truth in stamp_maturity.MATURITY (imported,
not duplicated). The bake/import pipeline keeps emitting CANONICAL names; this is a
FINAL step (like stamp_maturity) — re-run it after any data bake to re-prefix.

What it sweeps (full-filename string replace — collision-free, every name carries
`.geojson`): the runtime the live app loads + the served catalogs. It deliberately
does NOT rewrite the ~50 pipeline/verifier scripts (they read/write canonical
names; that consistency pass is a separate, Docker-gated follow-up).

Usage:
  python3 mvp/scripts/rename_data_medallion.py --check   # report, no writes
  python3 mvp/scripts/rename_data_medallion.py           # rename + sweep
"""
from __future__ import annotations
import sys
from pathlib import Path

import stamp_maturity  # the tier-per-file source of truth (MATURITY)

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "website" / "data"
WEB = REPO / "website"

# Files that reference served geojson by name and are loaded/served at RUNTIME.
SWEEP = [
    WEB / "js" / "viewer_core.js",
    WEB / "js" / "main.js",
    WEB / "js" / "panel.js",
    WEB / "js" / "data_editor_map.js",
    WEB / "sw.js",
    WEB / "index.html",
    WEB / "old_index.html",
    WEB / "right_panel.html",
    WEB / "data_editor.html",
    DATA / "_schema.json",
    DATA / "_data_manifest.json",
]

# canonical -> prefixed. Longest canonical first so a shorter name can never land
# inside a longer one mid-sweep (belt-and-suspenders; the names don't nest anyway).
RENAME = {f: f"{tier}_{f}" for f, (tier, _g) in stamp_maturity.MATURITY.items()}
ORDERED = sorted(RENAME.items(), key=lambda kv: -len(kv[0]))


def main() -> int:
    check = "--check" in sys.argv[1:]
    print(f"{'CHECK' if check else 'RENAME'} medallion data-source filenames\n")

    # 1) rename the files on disk
    renamed = skipped = 0
    for canonical, new in ORDERED:
        src, dst = DATA / canonical, DATA / new
        if src.exists():
            print(f"  {canonical}  ->  {new}")
            if not check:
                src.rename(dst)
            renamed += 1
        elif dst.exists():
            skipped += 1  # already renamed (idempotent)
        else:
            print(f"  ! {canonical} NOT FOUND (skipped)")
    print(f"\n  files: {renamed} renamed, {skipped} already-prefixed")

    # 2) sweep references (full-filename string replace)
    print("\n  sweeping references:")
    for path in SWEEP:
        if not path.exists():
            print(f"    - {path.name}: (missing)")
            continue
        text = path.read_text()
        hits = 0
        for canonical, new in ORDERED:
            n = text.count(canonical)
            if n:
                text = text.replace(canonical, new)
                hits += n
        if hits and not check:
            path.write_text(text)
        print(f"    - {path.relative_to(REPO)}: {hits} ref(s) {'(would update)' if check else 'updated'}")

    print("\n--check: no writes." if check else "\nDone. Re-run after any data bake (canonical -> prefixed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
