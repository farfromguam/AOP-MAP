"""Shared parse / normalize contract for the panel-overrides export.

The web editor (website/js/panel.js) exports its edits as ONE JSON payload
(schema `aop-panel-overrides-v1`): `edits{}` (keyed "<source>:<canonical id>"),
`created[]` (whole drawn features), `deleted[]` (keys). This module is the ONE
parser for that payload. It has TWO sinks:

  - mvp/scripts/bake_panel_overrides.py        -> merges diffs into website/data/*.geojson
  - mvp/scripts/apply_panel_overrides_to_core.py -> upserts diffs into PostGIS core.*

Both import this module so there is a single source of truth for the schema, the
view-state key set, the "<source>:<id>" split, coordinate rounding, and the
drawn-feature normalization. The only thing that differs between the two callers
is the SINK (file vs DB). See brain/tasks/06_going_gold/gold_migration.md (slice 1).

`read_payload(strict=...)` is the one seam that differs by caller intent: the
file baker keeps the original strict behavior (reject a malformed/unknown-schema
payload); the core sink reads permissively (it must never reject -- C5/no-limiting
code: an unknown schema still upserts; the publish view is the only gate).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCHEMA = "aop-panel-overrides-v1"
COORD_DECIMALS = 5                      # match the served files (~1.1 m)
DEFAULT_CREATED_TARGET = "aop_user_features.geojson"

# Property keys the editor persists that are VIEW state or panel-internal, not
# authored data -- never written into a sink. `_src` is the home-source tag a
# created feature carries so a sink can route it; `_id` is its local pre-bake id.
VIEW_STATE_KEYS = {"highlight", "__locked", "__group", "_id", "_src"}
# Identity/facet keys the editor is allowed to write back onto a served feature.
# (the panel's pickEditable is the actual allowlist; this stays in sync with
# EDITABLE_SERVED_KEYS there, minus the view-state `highlight`.)
EDITABLE_KEYS = ["name", "description", "difficulty", "notes", "category", "tag"]


def load_json(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def read_payload(arg: str, strict: bool = True) -> dict:
    """Read the export payload from a path or '-' (stdin).

    strict=True  (the file baker): a non-object payload or an unexpected schema
                 is a hard error -- the original bake_panel_overrides.py behavior.
    strict=False (the core sink):  never reject. A non-object payload yields an
                 empty payload (nothing to apply); an unexpected schema is read
                 anyway (its edits/created/deleted still upsert). C5 -- the
                 publish view is the only gate, not this parser.
    """
    raw = json.load(sys.stdin) if arg == "-" else load_json(Path(arg))
    if not isinstance(raw, dict):
        if strict:
            raise SystemExit("Export payload must be a JSON object")
        return {}
    if raw.get("schema") != SCHEMA and strict:
        raise SystemExit(f"Unexpected schema {raw.get('schema')!r} (want {SCHEMA!r})")
    return raw


def split_key(key: str):
    """Split an export key "<source>:<canonical id>" on its FIRST colon.

    Returns (source, id). Mirrors the panel's `src + ':' + id` join and its
    replay split (main panel uses indexOf(':')); an id that itself contains a
    colon is preserved intact in the id half.
    """
    src, _, fid = str(key).partition(":")
    return src, fid


def round_coords(coords):
    if isinstance(coords, (int, float)):
        return round(coords, COORD_DECIMALS)
    return [round_coords(c) for c in coords]


def dumps_geom(g) -> str:
    return json.dumps(g, sort_keys=True)


def feature_by_id(features: list, fid: str):
    for feat in features:
        if str((feat.get("properties") or {}).get("id")) == str(fid):
            return feat
    return None


def geom_kind(geometry: dict) -> str:
    t = (geometry or {}).get("type")
    return {"Point": "poi", "LineString": "trail", "Polygon": "area"}.get(t, "poi")


def safe_geometry(geometry):
    """A clean geometry dict, or None if missing / partial / unparseable -- NEVER throws
    (R13). A drawn feature mid-draw or a non-geographic POI can carry geometry:null or a
    type without coordinates; it must land geom-less downstream (point_geom_sql -> NULL),
    not crash the whole batch. Behavior-preserving for a well-formed geometry: returns the
    same {type, coordinates: round_coords(coordinates)} the inline build used to."""
    if not isinstance(geometry, dict):
        return None
    gtype = geometry.get("type")
    coords = geometry.get("coordinates")
    if not gtype or coords is None:
        return None
    try:
        return {"type": gtype, "coordinates": round_coords(coords)}
    except Exception:
        return None


def build_created_feature(raw: dict, today: str):
    """A drawn feature -> a canonical-first served feature (or None if no id)."""
    props_in = dict(raw.get("properties") or {})
    canonical_id = props_in.get("_id") or props_in.get("id")
    if canonical_id is None:
        return None
    clean = {k: v for k, v in props_in.items() if k not in VIEW_STATE_KEYS}
    # canonical-first, editor provenance defaults (don't overwrite explicit values)
    out_props = {
        "id": str(canonical_id),
        "name": clean.get("name") or "Untitled",
        "description": clean.get("description", ""),
        "kind": clean.get("kind") or geom_kind(raw.get("geometry")),
        "source": clean.get("source") or "AOP editor (drawn)",
        "confidence": clean.get("confidence") or "observed",
        "permission": clean.get("permission") or "AOP first-party",
        "status": clean.get("status") or "core",
        "last_checked": clean.get("last_checked") or today,
    }
    for k, v in clean.items():            # carry any extra facet props (difficulty, notes…)
        out_props.setdefault(k, v)
    out_props.pop("id", None)             # avoid dup from the loop above
    return {
        "type": "Feature",
        "geometry": safe_geometry(raw.get("geometry")),  # null/partial geom -> None, never throws (R13)
        "properties": {"id": str(canonical_id), **out_props},
    }
