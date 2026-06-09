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
import datetime, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "website", "data"))
RAW = os.path.join(DATA, "raw")


def _today():
    return datetime.date.today().isoformat()

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
# buildings: the facility NAME ("Pavilion") is the display name, not the street
# address that fills `name`/`building_label`. Prefer it; address becomes a facet.
def n_building(p): return p.get("facility_name") or first(p, NAME_KEYS)


def k_osm(p):
    for k in ("highway", "leisure", "natural", "place"):
        if p.get(k):
            return f"osm_{p[k]}"
    return "osm_feature"


# --- Sidecar join inputs (authored catalogs, joined into the feature here) ----
# These two files are the curated text the viewer used to join at RENDER time —
# the "shadow attribute" the Sprint-09 audit named (a trail shows "Launchpad" on
# one surface and "1" on another because the name was a runtime catalog join, not
# a field). We fold them into the served features in the BAKE so the join lives in
# one place and every surface reads one field. Read by fixed path from
# website/data/ and never written here, so the bake stays idempotent while always
# picking up the latest authored catalog — unlike the pristine geometry archive in
# raw/, an actively-authored catalog must not go stale behind a one-time copy.
def _load_json(fname):
    path = os.path.join(DATA, fname)
    try:
        with open(path) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


# trail catalog: number -> {name, description, difficulty, ...}
TRAIL_CATALOG = {t["number"]: t
                 for t in _load_json("aop_trail_catalog.json").get("trails", [])
                 if t.get("number") is not None}
# poi index: [{match:{source, ...identifying}, blurb, revisit_note}, ...]
POI_INDEX = _load_json("aop_poi_index.json").get("entries", [])

# Recorded in _schema.json so the crosswalk shows where the joined values come from.
SIDECARS = {
    "aop_trail_catalog.json": "trail name + description + difficulty, joined by trail_number == number",
    "aop_poi_index.json": "building/cemetery/visitor description (blurb) + revisit_note, joined by match{} fields",
}


def poi_match(poi_source, props):
    """The poi-index entry whose match{} (minus its `source`) all equal these props."""
    for e in POI_INDEX:
        m = e.get("match", {})
        if m.get("source") != poi_source:
            continue
        if all(str(props.get(k)) == str(v) for k, v in m.items() if k != "source"):
            return e
    return None


def join_name_desc(cfg, props, name, desc):
    """Fold the render-time sidecar joins into the baked feature. Returns
    (name, desc, poi_entry). A joined value beats the stand-in (a real trail name
    beats the number, a curated blurb beats a blank/composed description); when the
    sidecar has nothing, the existing crosswalk value is kept. Original physical
    keys are preserved underneath by canonical_props (additive — Mason)."""
    poi = None
    if cfg.get("trail_join"):
        cat = TRAIL_CATALOG.get(props.get("trail_number"))
        if cat:
            if cat.get("name"):
                name = cat["name"]
            if cat.get("description"):
                desc = cat["description"]
    ps = cfg.get("poi_source")
    if ps:
        poi = poi_match(ps, props)
        if poi and poi.get("blurb"):
            desc = poi["blurb"]
    return name, desc, poi


def facets(cfg, props):
    """Tier-3 type-specific facets — additive, emitted only where a value exists.
    Reads declarative property keys (never a layerKey), so a facet is a NEW derived
    view and the original physical key is preserved underneath (Mason / CMFS)."""
    f = {}
    if cfg.get("trail_join"):
        cat = TRAIL_CATALOG.get(props.get("trail_number"))
        diff = props.get("difficulty") or (cat.get("difficulty") if cat else None)
        if diff:
            f["difficulty"] = diff
        # Fold the catalog's supplementary trail detail so the popup reads the
        # feature, not a runtime join (the join is deleted from the viewer in A2).
        if cat:
            if cat.get("length_mi") is not None:
                f["length_mi"] = cat["length_mi"]
            if cat.get("tr") is not None:
                f["onx_tr"] = cat["tr"]
            if cat.get("connects"):
                f["connects"] = cat["connects"]
    if props.get("category"):
        f["category"] = props["category"]          # POIs: proper-noun category as a facet
    if props.get("facility_role"):
        f["facility_role"] = props["facility_role"]  # buildings: role out of `status`
    if props.get("address"):
        f["address"] = props["address"]              # buildings: address out of `name`
    occ = props.get("occupancy_class") or props.get("primary_occupancy")
    if occ:
        f["occupancy"] = occ
    return f


# Per-file config. prov = layer provenance defaults (literal) used to fill any
# canonical provenance field the feature itself doesn't carry. machine=True ->
# per-feature gets id+kind only; prov is recorded layer-level in the manifest.
CONFIG = {
    # publish.geojson is intentionally NOT here: it is DB-baked by
    # export_publish_geojson.sh (the live publish view, currently 6 features),
    # while raw/publish.geojson is a stale 5-feature snapshot. Re-baking it from
    # raw/ would silently revert the DB-baked content — the "two writers, one file"
    # shadow-attribute finding. rebake_canonical must not co-own a DB-baked file.
    # (Collapsing the publish bake to one reproducible DB writer is gold slice 6.)
    "aop_9_patch.geojson": dict(kind="acquisition_aoi_cell", name=n_cell,
        prov=dict(source="AOP data-acquisition planning grid", confidence="planning",
                  permission="n/a — planning overlay", status="planning")),
    # poi_source: join the poi-index blurb into `description` by the index's
    # match{} fields. status="raw context": the FEMA footprint's own status key
    # holds the facility ROLE ("facility"/"presence_only"), not a publish state —
    # the role is surfaced as a facet (facility_role) instead (shadow-attribute
    # finding building-status-holds-facility-role); the raw key is preserved.
    "aop_buildings.geojson": dict(kind="building", name=n_building, poi_source="buildings",
        status="raw context",
        prov=dict(source="FEMA USA Structures (ORNL)", confidence="observed (footprint)",
                  permission="public domain (FEMA)", status="raw context")),
    "aop_cemeteries.geojson": dict(kind="cemetery", name=None, desc=["note"],
        poi_source="cemeteries",
        prov=dict(source="TN Comptroller — Marion County parcels",
                  confidence="observed (county parcel)",
                  permission="parcel: public; burial roster: USGenWeb non-commercial",
                  status="raw context")),
    # name=None on trail_network/roads/water: `name` is a render key (label
    # layers filter/draw from it). Leaving blanks blank keeps the map identical;
    # auto-filling would spawn labels on unnamed features. trail_join folds the
    # curated trail catalog (name/description/difficulty) in by trail_number, so a
    # catalogued trail bakes "Launchpad" in place of the "1" stand-in — the label
    # count is unchanged (those trails already carried the number as their name).
    "aop_trail_network.geojson": dict(kind="trail", name=None, trail_join=True,
        prov=dict(source="SFWDA paper map (traced + merged)",
                  confidence="merged truth (traced)",
                  permission="SFWDA paper map — permission TBD", status="raw context")),
    # Mixed-kind file: callout polygons (normalized to kind=visitor_callout)
    # plus the AOP + Rock Warblers brand-logo points (kind=brand_logo) merged in
    # here. Discriminate on logo_id presence — brand logos carry it, callouts do
    # not — so callout polygons still normalize their raw kind to visitor_callout.
    # The brand features are stored canonically (carrying their own source/
    # confidence/permission/status), so the callout `prov` defaults below only
    # ever fill the callout polygons — the logos keep "brand owner"/"decorative".
    "aop_visitor_context_callouts.geojson": dict(
        kind=lambda p: "brand_logo" if p.get("logo_id") else "visitor_callout",
        name=None, poi_source="visitor_context",
        desc=lambda p: compose(p, ["direction", "services", "examples"]),
        prov=dict(source="AOP pages + Marion County tourism refs",
                  confidence="compiled", permission="context annotation",
                  status="context")),
    # kind is the controlled CLASS of a drawn point of interest ("poi"), NOT the
    # proper-noun category ("Pavilion") — the seed-poi-kind-is-propernoun finding
    # (Sprint-09 A4). The category rides as a Tier-3 facet (facets() reads it).
    # `p.get("kind") or "poi"` is the Mason safe-default: a feature that carries a
    # real controlled `kind` keeps it; everything else defaults to "poi" (never a
    # reject/coerce). Raw seed carries kind=None -> "poi".
    "aop_editor_seed_pois.geojson": dict(kind=lambda p: p.get("kind") or "poi", name=None,
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


def resolve_status(cfg, props, prov):
    # A per-layer status override (const or callable) wins so a layer whose physical
    # `status` key holds something other than a publish/review state (FEMA buildings:
    # the facility role) can declare the real state; otherwise crosswalk then prov.
    s = cfg.get("status")
    if callable(s):
        return s(props)
    if s is not None:
        return s
    return first(props, STATUS_KEYS) or prov.get("status")


def canonical_props(cfg, props, stem="feature", idx=0):
    machine = cfg.get("machine", False)
    prov = cfg.get("prov", {})
    out = {}
    out["id"] = first(props, ID_KEYS)
    if out["id"] in (None, ""):
        out["id"] = f"{stem}-{idx}"          # never blank — used as an editor key
    name = resolve_name(cfg, props)
    desc = resolve_desc(cfg, props)
    name, desc, poi = join_name_desc(cfg, props, name, desc)
    out["kind"] = resolve_kind(cfg, props)
    if machine:
        # Machine/coverage layers stay lean (id + kind; provenance is layer-level),
        # but still crosswalk a name/status when the feature carries a physical key
        # (track_name, label, publish_status) — otherwise those are invisible to the
        # canonical editor. None of these layers have a label that paints `name`
        # (their symbol layers read `label`/raw keys), so this spawns no map labels.
        if name:
            out["name"] = name
        st = first(props, STATUS_KEYS)
        if st:
            out["status"] = st
    else:
        out["name"] = name
        out["description"] = desc
        out["source"] = first(props, SOURCE_KEYS) or prov.get("source")
        out["confidence"] = first(props, CONF_KEYS) or prov.get("confidence")
        out["permission"] = first(props, PERM_KEYS) or prov.get("permission")
        out["status"] = resolve_status(cfg, props, prov)
        out["last_checked"] = first(props, CHECKED_KEYS) or prov.get("last_checked")
        # Provenance: the served file this feature bakes to. The editor's Source-tab
        # "File" used to be reverse-mapped from the live MapLibre source id (and read
        # "unknown" when that lookup missed) — the source-file-shown-as-derived
        # finding (A4). Baked here it is read directly off the feature. Named layers
        # only: machine/coverage layers stay lean (no per-feature stamping bloat).
        out["source_file"] = f"{stem}.geojson"
    fc = facets(cfg, props)
    if poi and poi.get("revisit_note"):
        fc["revisit_note"] = poi["revisit_note"]
    # canonical first, in order; then the Tier-3 facets block; then preserve every
    # original physical key not already set (additive — nothing dropped/overwritten).
    ordered = {k: out[k] for k in CANON_ORDER if k in out}
    if "source_file" in out:
        ordered["source_file"] = out["source_file"]
    if fc:
        ordered["facets"] = fc
    # Most physical keys differ from the canonical field name and are preserved by
    # the loop below. But `name`/`description` COLLIDE with canonical fields, so when
    # a join overwrites them with a different value (trail name "1" -> "Launchpad"),
    # the original would be lost. Stash it under `_original` so the stand-in survives
    # (additive — Mason; and the bare trail number stays addressable).
    preserved = {k: props[k] for k in ("name", "description")
                 if k in props and props[k] not in (None, "") and ordered.get(k) != props[k]}
    if preserved:
        ordered["_original"] = preserved
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
    # Carry the curated top-level `_meta` additions forward from the LIVE file: the
    # maturity stamp (stamp_maturity.py) and the trail gold block
    # (export_gold_trail_network.py) live there. raw/ carries a PARTIAL `_meta`
    # (pristine, pre-stamp), so the old `if "_meta" not in doc` guard skipped the
    # carry-forward and silently wiped the stamps. Instead overlay every live-only
    # `_meta` key onto the doc's `_meta`: raw's pristine values are kept, the
    # post-bake curation (maturity/group/locked/gold block) survives. We only author
    # features here; `_meta` curation is theirs to keep.
    if os.path.exists(live_path):
        try:
            with open(live_path) as lf:
                live_meta = json.load(lf).get("_meta")
        except (OSError, ValueError):
            live_meta = None
        if isinstance(live_meta, dict):
            meta = doc.get("_meta") if isinstance(doc.get("_meta"), dict) else {}
            for k, v in live_meta.items():
                if k not in meta:
                    meta[k] = v
            doc["_meta"] = meta
    if not check:
        with open(live_path, "w") as fh:
            json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    sample = feats[0]["properties"] if feats else {}
    return n, machine, sample


def write_manifest(results):
    # Read the existing manifest so per-layer `maturity` (stamp_maturity.py) and the
    # `maturity_tiers` block survive a regen — they have no other writer, so a plain
    # rebuild was silently wiping them (the schema-manifest-stale finding). Counts
    # and the timestamp are always refreshed here so the manifest can't go stale.
    prior = _load_json("_schema.json")
    prior_layers = prior.get("layers", {}) if isinstance(prior, dict) else {}
    manifest = {
        "schema": "aop-cmfs-v1",
        "updated_at": _today(),
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
            "source_file": "the served file this feature bakes to — the editor Source tab reads it directly instead of reverse-mapping the live MapLibre source id (named layers only; machine/coverage layers stay lean)",
        },
        "facets": {
            "_note": "Tier-3, type-specific. Additive: emitted on a feature only where a value exists, alongside the preserved original key. Not every feature carries every facet.",
            "difficulty": "trails — easy / moderate / difficult (park-map color; catalog fills where the feature has none)",
            "category": "POIs — proper-noun category, e.g. Pavilion (machine coverage layers keep their sub-kind as the preserved `class` key, not stamped per feature)",
            "facility_role": "buildings — the facility role lifted out of `status` (Pavilion / Front office / ...)",
            "occupancy": "buildings — FEMA occupancy class",
            "revisit_note": "what info is still owed (from the poi-index), kept auditable on the feature",
        },
        "crosswalk": {
            "name": NAME_KEYS, "description": DESC_KEYS, "id": ID_KEYS,
            "source": SOURCE_KEYS, "confidence": CONF_KEYS, "permission": PERM_KEYS,
            "status": STATUS_KEYS, "last_checked": CHECKED_KEYS,
        },
        "sidecars": SIDECARS,
        "rebake": {
            "mode": "additive (canonical fields prepended; facets next; original keys preserved)",
            "raw_archive": "website/data/raw/ (pristine pre-rebake originals)",
            "machine_layers": "id + kind per feature (name/status crosswalked where a physical key exists); provenance is layer-level (below)",
            "sidecar_joins": "trail catalog + poi-index folded into name/description/facets at bake time (read live from website/data/, not raw/)",
            "not_owned": "publish.geojson is DB-baked by export_publish_geojson.sh and intentionally not re-baked here",
        },
        "layers": {},
    }
    for fname, (n, machine, _sample) in results.items():
        kind = CONFIG[fname].get("kind")
        entry = {"features": n, "kind": kind if isinstance(kind, str) else "(per-feature)", "machine": machine}
        if machine:
            entry["layer_provenance"] = CONFIG[fname].get("prov", {})
        if isinstance(prior_layers.get(fname), dict) and "maturity" in prior_layers[fname]:
            entry["maturity"] = prior_layers[fname]["maturity"]
        manifest["layers"][fname] = entry
    # Carry forward layers this re-bake does not process (e.g. publish.geojson is
    # DB-baked) so the manifest stays a complete catalog; refresh their live count.
    for fname, entry in prior_layers.items():
        if fname not in manifest["layers"]:
            live = _load_json(fname)
            if isinstance(live, dict) and "features" in live:
                entry = {**entry, "features": len(live.get("features", []))}
            manifest["layers"][fname] = entry
    if isinstance(prior.get("maturity_tiers"), dict):
        manifest["maturity_tiers"] = prior["maturity_tiers"]
    with open(os.path.join(DATA, "_schema.json"), "w") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)


def strip_legacy_publish_blurb(check=False):
    """Drop the retired `blurb` key from the served publish.geojson where canonical
    `description` carries the copy. The DB rename blurb->description (init_db.sql)
    never propagated to the served artifact; the current export SQL already emits
    `description`, so this matches a fresh DB bake without a DB round-trip. publish
    is DB-baked (not in CONFIG), so this operates on the served file in place.
    Idempotent: re-running finds no `blurb` to drop. Returns the number dropped."""
    path = os.path.join(DATA, "publish.geojson")
    doc = _load_json("publish.geojson")
    if not isinstance(doc, dict) or "features" not in doc:
        return 0
    dropped = 0
    for ft in doc["features"]:
        p = ft.get("properties") or {}
        # Drop the retired key when `description` already carries the copy, or when
        # `blurb` is empty anyway. The only case we keep it is blurb-content with no
        # description home — that would be content loss, so it is left to surface.
        if "blurb" in p and (p.get("description") not in (None, "") or p.get("blurb") in (None, "")):
            del p["blurb"]
            dropped += 1
    if dropped and not check:
        with open(path, "w") as fh:
            json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    return dropped


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
    dropped = strip_legacy_publish_blurb(check=check)
    if dropped:
        verb = "would drop" if check else "dropped"
        print(f"  [publish] {verb} legacy `blurb` from {dropped} served feature(s) (description is canonical)")
    if not check:
        write_manifest(results)
        print(f"\nWrote {len(results)} re-baked files + _schema.json. Raw archived in {RAW}")
    else:
        print(f"\n--check: {len(results)} files would be re-baked (no write).")


if __name__ == "__main__":
    main()
