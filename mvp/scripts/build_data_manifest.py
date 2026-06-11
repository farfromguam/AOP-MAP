#!/usr/bin/env python3
"""Build website/data/_data_manifest.json — the ground-truth inventory of every
AOP data source, so a human can SEE what is actually under the hood.

Three layers of reality, kept distinct because they are in very different states:

  1. db        — the PostGIS store of record (core.features + siblings). The
                 converged, normalized spine. Introspected live via psql.
  2. served    — the files in website/data/ the viewer actually loads. Each is
                 classified by where it came from: a core-backed bake, a raw
                 pipeline output that never touches core, an authored sidecar,
                 or a runtime buffer.
  3. (the client itself is NOT inventoried here — it is code, not data. Its
     per-layer adapter sprawl is the separate debt, tracked on its own card.)

This is documentation, not a gate: an unrecognized served file is still
inventoried (classified `served-other`), never dropped (C5/no_limiting_code_mvp).
Re-run after any bake or schema change:

    python3 mvp/scripts/build_data_manifest.py

Reads the live DB with the same `docker compose exec ... psql` idiom the bake
uses. If the DB is down, the db section is marked unreachable and the served
inventory still builds — an honest partial, not a crash.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = REPO / "website" / "data"
COMPOSE_FILE = REPO / "mvp" / "docker-compose.yml"
OUTPUT = DATA_DIR / "_data_manifest.json"

# Best-effort provenance for each served file: where it came from in the
# pipeline. This is a maintained map, not a validator — edit it when the bake
# changes. Anything not listed falls through to `served-other` (never dropped).
#   core-backed   : baked from core.features / siblings through the publish path
#   raw-pipeline  : a processing script's output (imagery/terrain/derived); by
#                   design it never passes through the publish gate
#   sidecar       : human-authored copy joined in at bake time
#   runtime-buffer: a working buffer the editor writes; not a store of record
ORIGINS = {
    # core-backed bakes (export_publish_geojson.sh + the apply_*_to_core path)
    "publish.geojson": ("core-backed", "publish.features view (the one publish gate)"),
    "aop_buildings.geojson": ("core-backed", "core.features WHERE layer='buildings'"),
    "aop_cemeteries.geojson": ("core-backed", "core.features WHERE layer='cemeteries'"),
    "aop_trail_network.geojson": ("core-backed", "core.features WHERE layer='trails'"),
    "aop_visitor_context_callouts.geojson": ("core-backed", "core.features WHERE layer='visitor'"),
    "aop_event_schedule.json": ("core-backed", "core.events + core.activities + core.event_meta"),
    # authored sidecars (copy joined in at bake; source geojson stays clean)
    "aop_about.json": ("sidecar", "authored About copy"),
    "aop_poi_index.json": ("sidecar", "authored POI blurbs + revisit notes"),
    "aop_trail_catalog.json": ("sidecar", "authored trail name/description/difficulty"),
    "aop_copy_registry.json": ("sidecar", "authored copy registry"),
    "aop_ui_strings.json": ("sidecar", "authored UI strings"),
    "aop_editor_seed_pois.geojson": ("sidecar", "seed POI installed on fresh/reset"),
    # runtime buffer (editor-written, not a store of record)
    "aop_user_features.geojson": ("runtime-buffer", "editor working buffer"),
    # raw / derived pipeline outputs (no publish gate, by northstar design)
    "aop_contours.geojson": ("raw-pipeline", "lidar/DEM contour pipeline"),
    "aop_landcover.geojson": ("raw-pipeline", "landcover classification"),
    "aop_landcover_9patch.geojson": ("raw-pipeline", "landcover, 9-patch AOI"),
    "aop_water.geojson": ("raw-pipeline", "USGS hydrography import"),
    "aop_roads.geojson": ("raw-pipeline", "USGS roads import"),
    "aop_lidar_tiles.geojson": ("raw-pipeline", "lidar tile index"),
    "aop_9_patch.geojson": ("raw-pipeline", "9-patch data-acquisition AOI"),
    "aop_activity_hotspots.geojson": ("raw-pipeline", "activity hotspot build"),
    "aop_synthetic_activity_hotspots.geojson": ("raw-pipeline", "simulated Saturday activity"),
    "aop_synthetic_activity_tracks.geojson": ("raw-pipeline", "simulated Saturday activity"),
    "aop_synthetic_activity_report.json": ("raw-pipeline", "simulated activity report"),
    "osm_aop_9patch.geojson": ("raw-pipeline", "OSM extract, 9-patch AOI"),
    "osm_aop_named.geojson": ("raw-pipeline", "OSM named features"),
    "sfwda_numbered_trails.geojson": ("raw-pipeline", "SFWDA paper-map trace"),
    "sfwda_traced_markers.geojson": ("raw-pipeline", "SFWDA paper-map trace"),
    "sfwda_traced_trails.geojson": ("raw-pipeline", "SFWDA paper-map trace"),
    "sfwda_trails_edited.geojson": ("raw-pipeline", "SFWDA paper-map trace, hand-edited"),
    "sfwda_raster_alignment.json": ("raw-pipeline", "SFWDA raster 4-corner warp"),
}

# Which served files the client actually loads as an interactive layer, and how.
# Documentation of the file -> live-layer binding; edit alongside the registries
# in website/js/main.js (TUNABLE_LAYERS / FEATURE_LIST_LAYERS).
CLIENT_LAYER = {
    "publish.geojson": "publish (bounds + published map features)",
    "aop_buildings.geojson": "buildings (FEATURE_LIST_LAYERS, editable)",
    "aop_cemeteries.geojson": "cemeteries (FEATURE_LIST_LAYERS, editable)",
    "aop_trail_network.geojson": "trails (FEATURE_LIST_LAYERS, editable)",
    "aop_visitor_context_callouts.geojson": "visitorContext / brandLogos",
    "aop_event_schedule.json": "eventSchedule",
    "aop_poi_index.json": "POI tab index",
    "aop_about.json": "About tab",
    "aop_ui_strings.json": "UI strings",
    "aop_editor_seed_pois.geojson": "editorPois seed",
}

# psql column-introspection for the four store-of-record tables, with the
# breakdown that actually answers "what is in here".
DB_TABLES = [
    ("core", "features", "store-of-record",
     "The ONE converged geo table — CMFS spine + JSONB attrs, one row shape for every layer.",
     "SELECT layer || '|' || count(*) || '|' || "
     "count(*) FILTER (WHERE archived_at IS NULL) || '|' || "
     "count(*) FILTER (WHERE permission='publish' AND publish_status='publish' AND archived_at IS NULL) "
     "FROM core.features GROUP BY layer ORDER BY count(*) DESC;",
     ("layer", "rows", "live", "published")),
    ("core", "events", "store-of-record",
     "The WHEN — one row per event occurrence/session.", None, None),
    ("core", "activities", "store-of-record",
     "The reusable WHAT — place-agnostic activities, no geometry.", None, None),
    ("core", "event_meta", "store-of-record",
     "The umbrella EVENT metadata — the WHO/WHEN banner.", None, None),
    ("source_register", "sources", "provenance",
     "The source register — where every claim comes from.", None, None),
    ("source_register", "feature_sources", "provenance",
     "Feature -> source provenance links.", None, None),
    ("raw", "gpx_captures", "raw-capture",
     "Pristine GPX captures (raw zone).", None, None),
    ("raw", "arcgis_feature_captures", "raw-capture",
     "Pristine ArcGIS feature captures (raw zone).", None, None),
]


def run_psql(sql: str) -> tuple[str, bool]:
    cmd = [
        "docker", "compose", "-f", str(COMPOSE_FILE), "exec", "-T", "db",
        "psql", "-U", "aop", "-d", "aop_map", "-v", "ON_ERROR_STOP=1", "-At", "-q",
    ]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if proc.returncode != 0:
        return (proc.stderr.strip(), False)
    return (proc.stdout, True)


def db_section() -> dict:
    ok, _ = run_psql("SELECT 1;")
    if not _:
        return {"reachable": False, "error": ok, "tables": []}
    tables = []
    for schema, table, role, note, breakdown_sql, breakdown_cols in DB_TABLES:
        cols_out, ok = run_psql(
            f"SELECT column_name || '|' || data_type FROM information_schema.columns "
            f"WHERE table_schema='{schema}' AND table_name='{table}' ORDER BY ordinal_position;")
        columns = [{"name": p.split("|")[0], "type": p.split("|")[1]}
                   for p in cols_out.splitlines() if "|" in p]
        count_out, _ = run_psql(f"SELECT count(*) FROM {schema}.{table};")
        try:
            row_count = int(count_out.strip())
        except ValueError:
            row_count = None
        entry = {
            "schema": schema, "table": table, "role": role, "note": note,
            "row_count": row_count, "columns": columns,
        }
        if breakdown_sql:
            b_out, _ = run_psql(breakdown_sql)
            rows = []
            for line in b_out.splitlines():
                if "|" not in line:
                    continue
                vals = line.split("|")
                rows.append(dict(zip(breakdown_cols, vals)))
            entry["breakdown"] = {"columns": list(breakdown_cols), "rows": rows}
        tables.append(entry)
    return {"reachable": True, "tables": tables}


def geometry_summary(features: list) -> dict:
    types: dict[str, int] = {}
    for f in features:
        g = (f or {}).get("geometry") or {}
        t = g.get("type", "—")
        types[t] = types.get(t, 0) + 1
    return types


def property_keys(features: list, cap: int = 3000) -> list:
    keys: dict[str, int] = {}
    for f in features[:cap]:
        for k in ((f or {}).get("properties") or {}).keys():
            keys[k] = keys.get(k, 0) + 1
    # most-common first so the page leads with the load-bearing fields
    return [k for k, _ in sorted(keys.items(), key=lambda kv: -kv[1])]


def served_entry(path: Path) -> dict:
    name = path.name
    origin, origin_note = ORIGINS.get(name, ("served-other", "unclassified — add to ORIGINS"))
    entry = {
        "file": name,
        "bytes": path.stat().st_size,
        "origin": origin,
        "origin_note": origin_note,
        "client_layer": CLIENT_LAYER.get(name),
    }
    try:
        doc = json.loads(path.read_text())
    except Exception as exc:  # an unreadable file is reported, not skipped
        entry["error"] = f"unreadable: {exc}"
        return entry
    if isinstance(doc, dict) and doc.get("type") == "FeatureCollection":
        feats = doc.get("features") or []
        entry["kind"] = "geojson"
        entry["feature_count"] = len(feats)
        entry["geometry_types"] = geometry_summary(feats)
        entry["property_keys"] = property_keys(feats)
        entry["sample"] = (feats[0].get("properties") if feats else None)
    else:
        entry["kind"] = "json"
        if isinstance(doc, dict):
            entry["top_keys"] = list(doc.keys())
        elif isinstance(doc, list):
            entry["top_keys"] = [f"[list of {len(doc)}]"]
    return entry


def served_section() -> list:
    out = []
    for path in sorted(DATA_DIR.glob("*.geojson")) + sorted(DATA_DIR.glob("*.json")):
        if path.name.startswith("_"):  # _schema.json, _data_manifest.json are meta, not sources
            continue
        out.append(served_entry(path))
    return out


def main() -> int:
    manifest = {
        "schema": "aop-data-manifest-v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "purpose": "Ground-truth inventory of every AOP data source. Open website/data_sources.html to browse it.",
        "layers_of_reality": {
            "db": "PostGIS store of record — the converged, normalized spine.",
            "served": "Files website/ loads — classified by origin (core-backed / raw-pipeline / sidecar / runtime-buffer).",
        },
        "db": db_section(),
        "served": served_section(),
    }
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")
    db = manifest["db"]
    n_db = len(db["tables"]) if db["reachable"] else 0
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    print(f"  db: {'reachable' if db['reachable'] else 'UNREACHABLE'} ({n_db} tables)")
    print(f"  served: {len(manifest['served'])} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
