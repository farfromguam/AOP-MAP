#!/usr/bin/env python3
"""The ONE store-of-record helper for served-file `_meta` + the `_schema.json`
manifest (gold slice 6, gMeta, 2026-06-10).

Three findings this closes (audit `tasks/09_editor_maturity/shadow_attributes_audit.md`):

  reference-bake-no-meta-on-fresh-volume  — the bake used to carry each served
      file's `_meta` (maturity badge + the trail gold block) + its owner-authored
      collection provenance forward from the LIVE served file. A FRESH volume has
      no prior file -> those are lost. The store of record is now `_schema.json`
      (COMMITTED, survives a fresh volume -- unlike the DB volume, F5/G_D). The bake
      reproduces every top-level served key (collection provenance + `_meta`) from
      the schema store, NOT from the prior served file.

  schema-manifest-stale  — `_schema.json` had no single writer; the export bake
      wrote 5 served files but never refreshed the manifest, so its per-layer
      `features` count + `updated_at` drifted. `regen_manifest()` below is invoked
      by the bake's LAST writer of the served files (export_publish_geojson.sh) and
      refreshes those DERIVED fields from the served truth, PRESERVING every curated
      field (maturity stamp, collection_meta, kind, machine, layer_provenance,
      crosswalk, facets, maturity_tiers). Maturity/`_meta` is INPUT (curated),
      counts/date are OUTPUT (regenerated) -- no circularity; one home, one writer (C6).

What lives in the schema store (additive, per layer under `layers.<file>`):
  - `maturity` / `group` / `locked` / `maturity_note`  — the maturity STAMP the
    editor reads from `_meta` (authored by stamp_maturity.py; mirrored here too so
    the schema is the single committed store of record).
  - `meta`  — the FULL `_meta` block VERBATIM (the maturity stamp AND, for the trail
    file, the rich self-describing gold block: about / crs / color_legend /
    difficulty_counts / review_flags / ...). Stored verbatim, not recomputed, so the
    served bytes are reproduced byte-IDENTICAL on a fresh volume. (A recompute from
    features would silently CHANGE stale derived fields, since the served HEAD block
    predates the current feature set; storing verbatim is the loss-free reproduction
    the finding asks for.)
  - `collection_meta`  — owner-authored TOP-LEVEL collection keys that have no DB
    home (`_source`, `_derived`, `_generated_by`, `_sources_checked`, the collection
    `name`, ...). Stored verbatim, reproduced so a fresh volume keeps them.

Usage:
  python3 mvp/scripts/regen_meta.py --capture    # served files -> _schema.json store
                                                  #   (idempotent promotion)
  python3 mvp/scripts/regen_meta.py --manifest   # served files -> refresh counts+date
  python3 mvp/scripts/regen_meta.py --check      # report only, no write

The export bake imports `served_top_meta` (schema store -> the file's top-level keys)
and `regen_manifest` directly; the CLI is for the one-time capture / a standalone
manifest refresh.
"""
from __future__ import annotations
import datetime
import json
import sys
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "website" / "data"
SCHEMA = DATA / "_schema.json"

# The maturity-stamp keys the editor reads from `_meta` (authored by
# stamp_maturity.py). Mirrored at the layer top level too (alongside the verbatim
# `meta`) so the existing `layers.<file>.maturity` contract stays intact.
STAMP_KEYS = ("maturity", "group", "locked", "maturity_note")

# Top-level keys that are the bake's own output (NOT stored collection provenance).
RESERVED_TOP = {"type", "features", "_meta"}

TRAIL_FILE = "aop_trail_network.geojson"


def _load_schema():
    try:
        return json.loads(SCHEMA.read_text())
    except (OSError, ValueError):
        return {}


# --- reproduce a served file's top-level keys from the store of record ---------
def served_top_meta(fname, schema=None):
    """Build a served file's top-level keys (collection provenance + `_meta`) from
    the store of record (`_schema.json`) -- WITHOUT the prior served file. Returns an
    ordered dict {key: value} to splice into the served doc (collection-provenance
    keys first, then `_meta` last, matching HEAD key order). Empty when the store has
    nothing for the file (a fresh volume before `--capture`): the bake then falls
    back to carrying the live file forward, and `--capture` promotes it.
    """
    schema = schema if schema is not None else _load_schema()
    layer = (schema.get("layers", {}) or {}).get(fname, {}) if isinstance(schema, dict) else {}
    out = OrderedDict()
    coll = layer.get("collection_meta")
    if isinstance(coll, dict):
        for k, v in coll.items():
            out[k] = v
    meta = layer.get("meta")
    if isinstance(meta, dict) and meta:
        out["_meta"] = meta
    return out


def has_store(fname, schema=None):
    """True iff the schema store has a `meta` for this file (the bake can reproduce
    the served `_meta` without the prior file)."""
    schema = schema if schema is not None else _load_schema()
    layer = (schema.get("layers", {}) or {}).get(fname, {}) if isinstance(schema, dict) else {}
    return isinstance(layer.get("meta"), dict) and bool(layer.get("meta"))


# --- capture: served files -> the store of record (idempotent) ----------------
def capture(check=False):
    """Promote the CURRENT served files' top-level keys (collection provenance +
    the full `_meta`) into `_schema.json` so the bake reproduces them without the
    prior file. Idempotent: re-running with unchanged served files writes the same
    store. Returns the number of layers whose store changed."""
    schema = _load_schema()
    if not isinstance(schema, dict) or "layers" not in schema:
        print("  ! _schema.json missing or has no `layers` — nothing captured")
        return 0
    captured = 0
    for fname, layer in schema["layers"].items():
        path = DATA / fname
        if not path.exists() or not isinstance(layer, dict):
            continue
        try:
            doc = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        changed = False
        # collection-level provenance: every top-level key except the reserved ones.
        coll = OrderedDict((k, v) for k, v in doc.items() if k not in RESERVED_TOP)
        if coll and layer.get("collection_meta") != coll:
            layer["collection_meta"] = coll
            changed = True
        # the FULL `_meta` block, verbatim.
        meta = doc.get("_meta")
        if isinstance(meta, dict) and meta:
            if layer.get("meta") != meta:
                layer["meta"] = meta
                changed = True
            # keep the flat stamp mirror in sync (the existing `layers.*.maturity`).
            for k in STAMP_KEYS:
                if k in meta and layer.get(k) != meta[k]:
                    layer[k] = meta[k]
                    changed = True
        if changed:
            captured += 1
    if captured and not check:
        SCHEMA.write_text(json.dumps(schema, ensure_ascii=False, indent=2))
    verb = "would update" if check else "updated"
    print(f"  capture: {verb} the store of record for {captured} layer(s)")
    return captured


# --- regen the DERIVED manifest fields from the served truth -------------------
def regen_manifest(check=False):
    """Refresh `_schema.json` per-layer `features` count + top-level `updated_at`
    from the served files. Preserves every curated field (maturity stamp, `meta`,
    collection_meta, ...). The export bake (the LAST writer of the served
    reference/publish files) calls this so the manifest can't go stale
    (schema-manifest-stale). Returns the number of layer counts refreshed."""
    schema = _load_schema()
    if not isinstance(schema, dict) or "layers" not in schema:
        print("  ! _schema.json missing or has no `layers` — manifest not regenerated")
        return 0
    refreshed = 0
    for fname, layer in schema["layers"].items():
        path = DATA / fname
        if not path.exists() or not isinstance(layer, dict):
            continue
        try:
            doc = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        n = len(doc.get("features", []))
        if layer.get("features") != n:
            layer["features"] = n
            refreshed += 1
    schema["updated_at"] = datetime.date.today().isoformat()
    if not check:
        SCHEMA.write_text(json.dumps(schema, ensure_ascii=False, indent=2))
    verb = "would refresh" if check else "refreshed"
    print(f"  manifest: {verb} {refreshed} layer count(s); updated_at -> {schema['updated_at']}")
    return refreshed


def main():
    check = "--check" in sys.argv[1:]
    did = False
    if "--capture" in sys.argv[1:]:
        capture(check=check); did = True
    if "--manifest" in sys.argv[1:]:
        regen_manifest(check=check); did = True
    if not did:
        capture(check=check)
        regen_manifest(check=check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
