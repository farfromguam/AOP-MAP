#!/usr/bin/env python3
"""Re-bake every served feature collection into the Common Minimum Feature Schema.

Decision (2026-06-04, user): "re-bake the data entirely in our new format. keep
the raw we can refer back if needed. but our re-bake should have our fields."

Design (see brain/research/common_feature_schema.md):
  - Canonical fields (the CMFS) lead every feature's properties:
        id · name · description · kind · source · confidence · permission ·
        status · last_checked
    populated from each source's physical keys via the crosswalk below, enriched
    with the source-register provenance we know for that layer.
  - Re-bake is ADDITIVE: original physical keys are preserved after the canonical
    block, so the live index.html (which still reads old keys) keeps working and
    the map's paint/filter/label expressions are untouched. A clean "strip legacy
    keys" pass is a follow-up to run at the index->panel swap.
  - Pristine originals are archived to website/data/raw/ on first run; the re-bake
    always reads from that archive, so it is idempotent (re-run = re-bake clean).
  - MACHINE/coverage layers (landcover, contours, activity, synthetic) are not
    stamped per-feature with full provenance — they get id + kind only, and their
    provenance is recorded once at the LAYER level in _schema.json. This is the
    "minimum" reading: you don't edit an individual contour line, so stamping
    9 strings onto 2,831 lines is bloat for no editor benefit.

Run:  python3 mvp/scripts/rebake_canonical.py            (from repo root)
      python3 mvp/scripts/rebake_canonical.py --check     (report only, no write)
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "website", "data"))
RAW = os.path.join(DATA, "raw")

CANON_ORDER = ["id", "name", "description", "kind",
               "source", "confidence", "permission", "status", "last_checked"]

# --- The crosswalk: ordered physical keys to try for each canonical field ----
NAME_KEYS = ["name", "building_label", "facility_name", "label", "title", "track_name"]
DESC_KEYS = ["description", "blurb", "notes", "note"]
ID_KEYS = ["id", "uuid", "build_id", "parcel_id", "permanent_identifier", "osm_id",
           "ID", "edge_id", "logo_id", "source_id"]
SOURCE_KEYS = ["source", "source_name", "footprint_source", "source_type",
               "parcel_source", "burial_source", "attribution"]
CONF_KEYS = ["confidence", "number_confidence"]
PERM_KEYS = ["permission", "license_or_permission", "license", "burial_terms"]
STATUS_KEYS = ["status", "publish_status", "review_status"]
CHECKED_KEYS = ["last_checked", "retrieved_on", "validation_method", "image_date",
                "production_date", "publication_date", "generated_on"]


def first(props, keys):
    for k in keys:
        v = props.get(k)
        if v not in (None, "", []):
            return v
    return None


def compose(props, keys, sep=" · "):
    parts = [str(props[k]) for k in keys if props.get(k) not in (None, "", [])]
    return sep.join(parts) if parts else None


# name fallbacks where a source has no plain name key
def n_trail(p): return first(p, NAME_KEYS) or (f"Trail {p['trail_number']}" if p.get("trail_number") else None)
def n_marker(p): return first(p, NAME_KEYS) or (f"Marker · Trail {p['trail_number']}" if p.get("trail_number") else "Trail marker")
def n_cell(p): return f"Cell {p['cell_code']}" if p.get("cell_code") else "AOI cell"
def n_osm(p): return first(p, NAME_KEYS)  # often unnamed; left blank rather than faked
# publish: prefer an existing clean kind, else map its `layer` to one
_PUB_KIND = {"trail_centerlines": "trail", "park_boundaries": "boundary", "trailheads": "trailhead"}
def k_publish(p): return p.get("kind") or _PUB_KIND.get(p.get("layer"), p.get("layer"))


def k_osm(p):
    for k in ("highway", "leisure", "natural", "place"):
        if p.get(k):
            return f"osm_{p[k]}"
    return "osm_feature"


# Per-file config. prov = layer provenance defaults (literal) used to fill any
# canonical provenance field the feature itself doesn't carry. machine=True ->
# per-feature gets id+kind only; prov is recorded layer-level in the manifest.
CONFIG = {
    "publish.geojson": dict(kind=k_publish, name=None,
        prov=dict(source="AOP PostGIS publish view", last_checked=None)),
    "aop_9_patch.geojson": dict(kind="acquisition_aoi_cell", name=n_cell,
        prov=dict(source="AOP data-acquisition planning grid", confidence="planning",
                  permission="n/a — planning overlay", status="planning")),
    "aop_buildings.geojson": dict(kind="building", name=None,
        prov=dict(source="FEMA USA Structures (ORNL)", confidence="observed (footprint)",
                  permission="public domain (FEMA)", status="raw context")),
    "aop_cemeteries.geojson": dict(kind="cemetery", name=None, desc=["note"],
        prov=dict(source="TN Comptroller — Marion County parcels",
                  confidence="observed (county parcel)",
                  permission="parcel: public; burial roster: USGenWeb non-commercial",
                  status="raw context")),
    # name=None on trail_network/roads/water: `name` is a render key (label
    # layers filter/draw from it). Leaving blanks blank keeps the map identical;
    # auto-filling would spawn labels on unnamed features.
    "aop_trail_network.geojson": dict(kind="trail", name=None,
        prov=dict(source="SFWDA paper map (traced + merged)",
                  confidence="merged truth (traced)",
                  permission="SFWDA paper map — permission TBD", status="raw context")),
    "aop_visitor_context_callouts.geojson": dict(kind="visitor_callout", name=None,
        desc=lambda p: compose(p, ["direction", "services", "examples"]),
        prov=dict(source="AOP pages + Marion County tourism refs",
                  confidence="compiled", permission="context annotation",
                  status="context")),
    "aop_brand_logos.geojson": dict(kind="brand_logo", name=None,
        prov=dict(source="brand asset", confidence="n/a",
                  permission="brand owner", status="decorative")),
    "aop_editor_seed_pois.geojson": dict(kind=lambda p: p.get("category") or "poi", name=None,
        prov=dict(source="editor (first-party)", confidence="draft",
                  permission="first-party", status="draft")),
    "aop_lidar_tiles.geojson": dict(kind="lidar_tile", name=None,
        prov=dict(source="USGS 3DEP LAZ tile index", confidence="inventory metadata",
                  permission="public domain (USGS)", status="raw context")),
    "aop_roads.geojson": dict(kind="road", name=None,
        prov=dict(source="USGS National Map (transportation)", confidence="observed",
                  permission="public domain (USGS)", status="raw context")),
    "aop_water.geojson": dict(kind="water", name=None,
        prov=dict(source="USGS NHD", confidence="observed",
                  permission="public domain (USGS)", status="raw context")),
    "osm_aop_9patch.geojson": dict(kind=k_osm, name=n_osm,
        prov=dict(source="OpenStreetMap", confidence="community",
                  permission="ODbL", status="raw context")),
    "osm_aop_named.geojson": dict(kind=k_osm, name=n_osm,
        prov=dict(source="OpenStreetMap", confidence="community",
                  permission="ODbL", status="raw context")),
    "sfwda_traced_trails.geojson": dict(kind="trail", name=n_trail,
        prov=dict(source="SFWDA paper map (traced)",
                  permission="SFWDA paper map — permission TBD", status="raw context")),
    "sfwda_traced_markers.geojson": dict(kind="trail_marker", name=n_marker,
        prov=dict(source="SFWDA paper map (traced)",
                  permission="SFWDA paper map — permission TBD", status="raw context")),
    "sfwda_numbered_trails.geojson": dict(kind="trail", name=n_trail,
        prov=dict(source="SFWDA paper map (traced + numbered)",
                  permission="SFWDA paper map — permission TBD", status="raw context")),
    "sfwda_trails_edited.geojson": dict(kind="trail", name=n_trail,
        prov=dict(source="SFWDA paper map (traced + edited)",
                  permission="SFWDA paper map — permission TBD", status="raw context")),
    # --- MACHINE / coverage layers: id + kind per feature; prov is layer-level --
    "aop_landcover.geojson": dict(kind="landcover", machine=True,
        prov=dict(source="USDA NAIP 2023 + USGS 3DEP canopy-height model",
                  confidence="derived", permission="public domain",
                  status="raw context", last_checked="2023 imagery / 2015 lidar")),
    "aop_landcover_9patch.geojson": dict(kind="landcover", machine=True,
        prov=dict(source="USDA NAIP 2023 + USGS 3DEP canopy-height model",
                  confidence="derived", permission="public domain",
                  status="raw context", last_checked="2023 imagery / 2015 lidar")),
    "aop_contours.geojson": dict(kind="contour", machine=True,
        prov=dict(source="USGS 3DEP 1m DEM (lidar-derived)", confidence="derived",
                  permission="public domain (USGS)", status="raw context",
                  last_checked="2015 (DEM)")),
    "aop_activity_hotspots.geojson": dict(kind="activity_hotspot", machine=True,
        prov=dict(source="first-party Gaia GPX (dwell)", confidence="raw activity evidence",
                  permission="internal", status="hold")),
    "aop_synthetic_activity_hotspots.geojson": dict(kind="synthetic_activity_hotspot", machine=True,
        prov=dict(source="simulation", confidence="synthetic",
                  permission="internal", status="test data")),
    "aop_synthetic_activity_tracks.geojson": dict(kind="synthetic_activity_track", machine=True,
        prov=dict(source="simulation", confidence="synthetic",
                  permission="internal", status="test data")),
}


def resolve_kind(cfg, props):
    k = cfg.get("kind")
    if callable(k):
        return k(props)
    if k:
        return k
    return props.get("kind") or props.get("layer")


def resolve_name(cfg, props):
    nf = cfg.get("name")
    if callable(nf):
        return nf(props)
    return first(props, NAME_KEYS)


def resolve_desc(cfg, props):
    df = cfg.get("desc")
    if callable(df):
        return df(props)
    if isinstance(df, list):
        return first(props, df)
    return first(props, DESC_KEYS)


def canonical_props(cfg, props, stem="feature", idx=0):
    machine = cfg.get("machine", False)
    prov = cfg.get("prov", {})
    out = {}
    out["id"] = first(props, ID_KEYS)
    if out["id"] in (None, ""):
        out["id"] = f"{stem}-{idx}"          # never blank — used as an editor key
    if not machine:
        out["name"] = resolve_name(cfg, props)
        out["description"] = resolve_desc(cfg, props)
    out["kind"] = resolve_kind(cfg, props)
    if not machine:
        out["source"] = first(props, SOURCE_KEYS) or prov.get("source")
        out["confidence"] = first(props, CONF_KEYS) or prov.get("confidence")
        out["permission"] = first(props, PERM_KEYS) or prov.get("permission")
        out["status"] = first(props, STATUS_KEYS) or prov.get("status")
        out["last_checked"] = first(props, CHECKED_KEYS) or prov.get("last_checked")
    # canonical first, in order; then preserve every original key not already set
    ordered = {k: out[k] for k in CANON_ORDER if k in out}
    for k, v in props.items():
        if k not in ordered:
            ordered[k] = v
    return ordered


def rebake_file(fname, cfg, check=False):
    raw_path = os.path.join(RAW, fname)
    live_path = os.path.join(DATA, fname)
    # archive pristine original ONCE
    if not os.path.exists(raw_path):
        if not check:
            shutil.copy2(live_path, raw_path)
    src = raw_path if os.path.exists(raw_path) else live_path
    with open(src) as fh:
        doc = json.load(fh)
    feats = doc.get("features", [])
    n = len(feats)
    machine = cfg.get("machine", False)
    stem = fname.replace(".geojson", "")
    for i, ft in enumerate(feats):
        ft["properties"] = canonical_props(cfg, ft.get("properties") or {}, stem, i)
    if not check:
        with open(live_path, "w") as fh:
            json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    sample = feats[0]["properties"] if feats else {}
    return n, machine, sample


def write_manifest(results):
    manifest = {
        "schema": "aop-cmfs-v1",
        "updated_at": "2026-06-04",
        "purpose": "Common Minimum Feature Schema — the one data contract the right-panel editor reads. See brain/research/common_feature_schema.md.",
        "canonical_fields": {
            "id": "stable feature id (machine; never blank where derivable)",
            "name": "display name / title — the field the editor's Name input writes",
            "description": "human blurb / notes",
            "kind": "class of thing (trail, building, cemetery, poi, callout, road, water, contour, landcover, ...)",
            "source": "where it came from (source-register)",
            "confidence": "official / observed / inferred / derived / synthetic",
            "permission": "license or permission to publish",
            "status": "publish / review status",
            "last_checked": "date or method last verified",
        },
        "crosswalk": {
            "name": NAME_KEYS, "description": DESC_KEYS, "id": ID_KEYS,
            "source": SOURCE_KEYS, "confidence": CONF_KEYS, "permission": PERM_KEYS,
            "status": STATUS_KEYS, "last_checked": CHECKED_KEYS,
        },
        "rebake": {
            "mode": "additive (canonical fields prepended; original keys preserved)",
            "raw_archive": "website/data/raw/ (pristine pre-rebake originals)",
            "machine_layers": "id + kind per feature only; provenance is layer-level (below)",
        },
        "layers": {},
    }
    for fname, (n, machine, _sample) in results.items():
        entry = {"features": n, "kind": (CONFIG[fname].get("kind") if isinstance(CONFIG[fname].get("kind"), str) else "(per-feature)"), "machine": machine}
        if machine:
            entry["layer_provenance"] = CONFIG[fname].get("prov", {})
        manifest["layers"][fname] = entry
    with open(os.path.join(DATA, "_schema.json"), "w") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)


def main():
    check = "--check" in sys.argv
    if not check:
        os.makedirs(RAW, exist_ok=True)
    results = {}
    for fname, cfg in CONFIG.items():
        if not os.path.exists(os.path.join(DATA, fname)):
            print(f"  SKIP (missing): {fname}")
            continue
        n, machine, sample = rebake_file(fname, cfg, check=check)
        results[fname] = (n, machine, sample)
        tag = "MACHINE" if machine else "named  "
        canon = {k: sample.get(k) for k in CANON_ORDER if k in sample}
        print(f"  [{tag}] {fname:42s} {n:5d} feats  canon={json.dumps(canon, ensure_ascii=False)[:140]}")
    if not check:
        write_manifest(results)
        print(f"\nWrote {len(results)} re-baked files + _schema.json. Raw archived in {RAW}")
    else:
        print(f"\n--check: {len(results)} files would be re-baked (no write).")


if __name__ == "__main__":
    main()
