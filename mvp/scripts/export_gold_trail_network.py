#!/usr/bin/env python3
"""Stamp the served AOP trail network into its self-contained "gold" form.

Card: brain/tasks/04_event_app/paper_map_trail_extraction.md

`import_trace_svg.py` writes website/data/aop_trail_network.geojson with a thin
round-trip `_meta` ("re-imported from <svg>; this is the new truth"). The static
viewer loads that file DIRECTLY (layer aop-trail-network), with no DB, pipeline,
or localStorage in the path — so on a fresh checkout/install the file is the only
thing that has to be right. This script replaces the thin `_meta` with the full
self-describing gold block (crs, colour legend, difficulty band, counts, property
schema, band-mismatch review flags, provenance) computed deterministically from
the features, so the gold metadata is reproducible instead of hand-maintained.

The features themselves are NOT touched — geometry/number/difficulty/colour are
authored upstream (SVG round-trip + snap_trim). This only (re)writes `_meta`.

Run order:  import_trace_svg.py <svg>  ->  snap_trim_trails.py  ->  THIS
Usage:      python3 mvp/scripts/export_gold_trail_network.py [in/out.geojson] [--from SVG]
            (default file: website/data/aop_trail_network.geojson, in place)
"""
from __future__ import annotations
import json, sys
from collections import Counter, OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NET = REPO / "website/data/aop_trail_network.geojson"

# Colour -> difficulty legend, mirrored from import_trace_svg.assign_colors.
COLOR_LEGEND = OrderedDict([
    ("#1f9d3a", "easy"),
    ("#2438c8", "moderate"),
    ("#111111", "difficult"),
    ("#f25e0d", "road"),
    ("#888888", "unknown"),
])
PROPERTY_SCHEMA = ["id", "trail_number", "name", "kind", "difficulty",
                   "color", "source", "review_status"]


def band(n):
    """Difficulty implied by a trail number, per the validated sheet bands."""
    if n is None:
        return None
    if 1 <= n <= 20:
        return "easy"
    if (21 <= n <= 39) or (80 <= n <= 99):
        return "moderate"
    if 40 <= n <= 79:
        return "difficult"
    return None


def main():
    # provenance hint: --from <svg name> (else carried from the existing _meta)
    argv = sys.argv[1:]
    from_svg = None
    if "--from" in argv:
        i = argv.index("--from")
        from_svg = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    pos = [a for a in argv if not a.startswith("--")]
    src = Path(pos[0]) if pos else NET

    doc = json.loads(src.read_text())
    feats = doc["features"]
    props = [f["properties"] for f in feats]

    diff_counts = Counter(p.get("difficulty") for p in props if p.get("kind") != "road")
    color_counts = Counter(p.get("color") for p in props)
    roads = sum(1 for p in props if p.get("kind") == "road")
    grey = [p.get("name") for p in props
            if p.get("kind") != "road" and not p.get("difficulty")]

    # Review flags: a numbered trail whose hand-set difficulty contradicts its
    # number band. These are the rows a human should adjudicate — surfaced in the
    # file itself so the gold copy carries its own open questions.
    flags = []
    for p in props:
        if p.get("kind") == "road":
            continue
        n, d = p.get("trail_number"), p.get("difficulty")
        b = band(n)
        if n is not None and d and b and d != b:
            flags.append(f'name "{p.get("name")}": difficulty "{d}" vs number-band "{b}" (n={n})')
    if grey:
        flags.append(f"{len(grey)} non-road trails still have no difficulty (grey): "
                     + ", ".join(str(g) for g in grey))

    prev_from = (doc.get("_meta") or {}).get("generated_from", "")
    provenance = (from_svg + " round-trip; numbers/difficulty re-attached from markers"
                  if from_svg else (prev_from or "SVG round-trip"))

    doc["_meta"] = OrderedDict([
        ("about",
         "AOP merged trail network: hand-cleaned SFWDA traced trails + OSM tracks "
         "at one level. Authoritative truth, served directly by the static viewer "
         "(layer aop-trail-network). Self-contained: each feature carries its own "
         "difficulty colour, so it renders correctly on a fresh viewer load with no "
         "pipeline, DB, or localStorage dependency."),
        ("crs", "urn:ogc:def:crs:OGC:1.3:CRS84 (WGS84 lng/lat, RFC 7946 default)"),
        ("color_legend", dict(COLOR_LEGEND)),
        ("difficulty_band",
         "Easy 1-20 | Moderate 21-39 & 80-99 | Difficult 40-79 (park rating; onX may differ)"),
        ("feature_count", len(feats)),
        ("difficulty_counts", OrderedDict([
            ("easy", diff_counts.get("easy", 0)),
            ("moderate", diff_counts.get("moderate", 0)),
            ("difficult", diff_counts.get("difficult", 0)),
            ("road/none", roads + diff_counts.get(None, 0)),
        ])),
        ("color_counts", OrderedDict(
            (c, color_counts.get(c, 0)) for c in COLOR_LEGEND if color_counts.get(c))),
        ("named", sum(1 for p in props if p.get("name"))),
        ("numbered", sum(1 for p in props if p.get("trail_number") is not None)),
        ("property_schema", PROPERTY_SCHEMA),
        ("review_flags", flags),
        ("generated_from", provenance),
    ])

    # Re-key so _meta sits before features (cosmetic, matches the prior gold file).
    out = OrderedDict([("type", doc["type"]), ("name", doc.get("name", "aop_trail_network")),
                       ("_meta", doc["_meta"]), ("features", feats)])
    src.write_text(json.dumps(out, indent=1))
    print(f"gold _meta stamped -> {src.relative_to(REPO)}")
    print(f"  {len(feats)} features | "
          f"easy {diff_counts.get('easy',0)} / moderate {diff_counts.get('moderate',0)} / "
          f"difficult {diff_counts.get('difficult',0)} / road {roads} | "
          f"named {out['_meta']['named']} numbered {out['_meta']['numbered']}")
    if flags:
        print("  review flags:")
        for fl in flags:
            print("   -", fl)


if __name__ == "__main__":
    main()
