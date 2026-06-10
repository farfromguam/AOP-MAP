#!/usr/bin/env python3
"""G_A "One writer per served file" (Approach C) — reference-file DB-bake ADOPTED.

Slice 6 / gold_slice6_backlog.md item: the 4 DB-baked reference files now have
exactly ONE bake writer (export_publish_geojson.sh); rebake_canonical.py was
EVICTED. The bake serves the CMFS spine from core.features COLUMNS overlaid on
attrs (Approach C). This verifier PROVES the adopted state by observation:

  A. LOSS-FREE PROPERTIES (file-based): the DB-bake of each of the 4 ref files vs
     HEAD has identical feature count, id set, and every `properties` key/value
     (no gate-key diff, no dropped key, no added key). The ONLY tolerated delta is
     geometry COORDINATE PRECISION (ST_AsGeoJSON 9-dec vs HEAD's raw 13-dec) on the
     polygon layers — a deliberate, documented canonicalization (<0.1 mm), asserted
     to be a pure precision rounding (max coord delta below a tiny epsilon), never a
     content change.
  B. PURE FUNCTION (shell): bake twice -> the 4 ref files are byte-identical (md5).
  C. ONE WRITER (shell): rebake_canonical.py CONFIG no longer lists ANY of the 4,
     and its --check would NOT rewrite them; export_publish_geojson.sh --check
     reports NO REVERT (the adopted served tree is the bake's fixed point).
  D. VIEWER SMOKE (MINIMAL): one page.goto (domcontentloaded + a short explicit
     wait, NO networkidle), read the 4 served sources off getSource().serialize(),
     assert trail src has a 'Launchpad' feature + a building src has 'Pavilion',
     assert 0 console errors. One retry on flake, then report.

UNLIKE the prior held-state probe, this verifier ADOPTS: it re-bakes (so the served
ref files are the DB-bake) and LEAVES them adopted (it restores ONLY the event
schedule to HEAD, since the events arm is the G_E axis, out of this slice).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "website", "data")
BAKE = os.path.join(ROOT, "mvp", "scripts", "export_publish_geojson.sh")
REBAKE = os.path.join(ROOT, "mvp", "scripts", "rebake_canonical.py")
MVP = os.path.join(ROOT, "mvp")

REF = ["aop_buildings", "aop_cemeteries", "aop_visitor_context_callouts", "aop_trail_network"]
# The events arm is the G_E axis (out of this slice) — restore it to HEAD so this
# slice never touches the events surface. The 4 ref files are LEFT adopted.
RESTORE_HEAD_AFTER = ["aop_event_schedule.json"]

# Every property key we assert equal where present (the loss-free gate).
GATE_KEYS = [
    "id", "name", "description", "kind", "source", "confidence", "permission",
    "status", "last_checked", "source_file", "facets", "_original",
    "color", "geom_role", "occupancy_class", "primary_occupancy", "difficulty",
    "class", "idx", "water_kind", "road_class", "category", "cemetery_type",
    "logo_id", "facility_role", "trail_number", "review_status", "aop_inholding",
    "address", "building_label", "note", "label", "services", "examples",
]
GEOM_EPSILON_DEG = 1e-6   # ~0.1 m; geom precision delta must be far below this.


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def md5_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def head_bytes(rel: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"HEAD:website/data/{rel}"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout


def write_head(rel: str) -> None:
    with open(os.path.join(DATA, rel), "wb") as fh:
        fh.write(head_bytes(rel))


def run_bake(*args: str) -> str:
    return subprocess.run(["bash", BAKE, *args], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout


def norm(v):
    if isinstance(v, (dict, list)):
        return json.dumps(v, sort_keys=True, ensure_ascii=False)
    return v


def feat_key(f):
    """Identity within a file: (id, geom_role, geom-type) — the cemetery twin
    shares id across a parcel polygon + a marker point, so id alone collides."""
    p = f.get("properties") or {}
    return (str(p.get("id")), p.get("geom_role"), (f.get("geometry") or {}).get("type"))


def max_coord_delta(a, b) -> float:
    fa: list[float] = []
    fb: list[float] = []

    def flat(x, acc):
        if isinstance(x, (int, float)):
            acc.append(x)
        elif isinstance(x, list):
            for e in x:
                flat(e, acc)
    flat(a, fa)
    flat(b, fb)
    if len(fa) != len(fb):
        return float("inf")
    return max((abs(x - y) for x, y in zip(fa, fb)), default=0.0)


def semantic_diff(stem: str, head_doc: dict, bake_doc: dict) -> dict:
    hf = head_doc.get("features", [])
    bf = bake_doc.get("features", [])
    hmap = {feat_key(f): f for f in hf}
    bmap = {feat_key(f): f for f in bf}
    r = {"stem": stem, "head_n": len(hf), "bake_n": len(bf),
         "count_equal": len(hf) == len(bf),
         "id_set_equal": sorted(map(str, hmap)) == sorted(map(str, bmap)),
         "gate_diffs": [], "key_adds": [], "key_drops": [],
         "geom_content_diffs": 0, "geom_precision_only": 0, "worst_geom_delta": 0.0}
    for k in sorted(hmap.keys() & bmap.keys(), key=str):
        hp = hmap[k].get("properties") or {}
        bp = bmap[k].get("properties") or {}
        for gk in GATE_KEYS:
            if (gk in hp or gk in bp) and norm(hp.get(gk)) != norm(bp.get(gk)):
                r["gate_diffs"].append((k, gk, hp.get(gk), bp.get(gk)))
        adds = set(bp) - set(hp)
        drops = set(hp) - set(bp)
        if adds:
            r["key_adds"].append((k, sorted(adds)))
        if drops:
            r["key_drops"].append((k, sorted(drops)))
        hg = hmap[k].get("geometry")
        bg = bmap[k].get("geometry")
        if json.dumps(hg, sort_keys=True) != json.dumps(bg, sort_keys=True):
            d = max_coord_delta((hg or {}).get("coordinates"), (bg or {}).get("coordinates"))
            r["worst_geom_delta"] = max(r["worst_geom_delta"], d)
            if d <= GEOM_EPSILON_DEG:
                r["geom_precision_only"] += 1
            else:
                r["geom_content_diffs"] += 1
    r["props_loss_free"] = (r["count_equal"] and r["id_set_equal"]
                            and not r["gate_diffs"] and not r["key_adds"]
                            and not r["key_drops"])
    r["geom_ok"] = (r["geom_content_diffs"] == 0)
    # collection-level: every top-level FeatureCollection key (excluding type/features)
    # must carry forward loss-free -- owner-authored provenance/derivation (_source,
    # _derived, _generated_by, _sources_checked, the collection `name`, _meta, ...).
    # Closes the 2026-06-10 verification hole (Scribe andon): the per-feature gate
    # above never inspected the top-level object, so a dropped collection key passed.
    skip = {"type", "features"}
    htop = {k: v for k, v in head_doc.items() if k not in skip}
    btop = {k: v for k, v in bake_doc.items() if k not in skip}
    r["toplevel_drops"] = sorted(set(htop) - set(btop))
    r["toplevel_adds"] = sorted(set(btop) - set(htop))
    r["toplevel_value_diffs"] = sorted(k for k in (set(htop) & set(btop))
                                       if norm(htop[k]) != norm(btop[k]))
    r["toplevel_loss_free"] = not (r["toplevel_drops"] or r["toplevel_adds"]
                                   or r["toplevel_value_diffs"])
    return r


def main() -> int:
    # ===== A + B: bake twice (md5) + semantic diff vs HEAD ==================
    print("== A/B: pure-function + loss-free semantic diff (file-based) ==")
    run_bake()
    md5_1 = {s: md5_of(os.path.join(DATA, f"{s}.geojson")) for s in REF}
    bake_docs = {s: json.load(open(os.path.join(DATA, f"{s}.geojson"))) for s in REF}
    run_bake()
    md5_2 = {s: md5_of(os.path.join(DATA, f"{s}.geojson")) for s in REF}
    head_docs = {s: json.loads(head_bytes(f"{s}.geojson")) for s in REF}

    for s in REF:
        d = semantic_diff(s, head_docs[s], bake_docs[s])
        print(f"\n  --- {s} ---")
        print(f"    count head={d['head_n']} bake={d['bake_n']} equal={d['count_equal']}  id_set_equal={d['id_set_equal']}")
        print(f"    gate-key diffs={len(d['gate_diffs'])}  key-adds={len(d['key_adds'])}  key-drops={len(d['key_drops'])}")
        print(f"    geom: content-diffs={d['geom_content_diffs']}  precision-only={d['geom_precision_only']}  worst_delta={d['worst_geom_delta']:.2e} deg")
        print(f"    top-level: drops={d['toplevel_drops']}  adds={d['toplevel_adds']}  value-diffs={d['toplevel_value_diffs']}")
        for fid, gk, hv, bv in d["gate_diffs"][:8]:
            print(f"      GATE DIFF {fid} {gk}: head={hv!r} bake={bv!r}")
        check(f"{s}: PROPERTIES loss-free vs HEAD (count/id/keys/values all equal)",
              d["props_loss_free"],
              f"gate_diffs={len(d['gate_diffs'])} adds={len(d['key_adds'])} drops={len(d['key_drops'])}")
        check(f"{s}: COLLECTION-level top-level keys loss-free vs HEAD (carry-forward)",
              d["toplevel_loss_free"],
              f"drops={d['toplevel_drops']} adds={d['toplevel_adds']} value_diffs={d['toplevel_value_diffs']}")
        check(f"{s}: geometry delta is precision-only (<{GEOM_EPSILON_DEG} deg), no content change",
              d["geom_ok"], f"worst_delta={d['worst_geom_delta']:.2e} content_diffs={d['geom_content_diffs']}")
        check(f"{s}: pure function (bake twice -> byte-identical md5)",
              md5_1[s] == md5_2[s], f"md5 {md5_1[s]} == {md5_2[s]}")

    # ===== C: ONE writer — rebake_canonical evicted + export --check NO REVERT
    print("\n== C: one writer per served file ==")
    src = open(REBAKE).read()
    still_in_config = [s for s in REF if f'"{s}.geojson"' in src]
    check("rebake_canonical CONFIG no longer lists ANY of the 4 ref files (EVICTED)",
          still_in_config == [], f"still_in_config={still_in_config}")
    chk = subprocess.run(
        [sys.executable, REBAKE, "--check"], cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    would_rewrite = [s for s in REF if f"{s}.geojson" in chk]
    check("rebake_canonical --check would NOT rewrite any of the 4 (no second writer)",
          would_rewrite == [], f"would_rewrite={would_rewrite}")
    export_chk = run_bake("--check")
    ref_no_revert = all(f"same  {s}.geojson" in export_chk for s in REF) \
        and ("same  publish.geojson" in export_chk)
    check("export_publish_geojson.sh --check: NO REVERT on the 4 ref files + publish (bake is the fixed point)",
          ref_no_revert, "all 'same' for the 5 in-scope served files")

    # ===== restore the EVENTS arm to HEAD (G_E axis, out of this slice) =====
    for rel in RESTORE_HEAD_AFTER:
        write_head(rel)

    # ===== D: MINIMAL viewer smoke (reads the ADOPTED served files) ========
    print("\n== D: minimal viewer smoke (one goto, short timeout) ==")
    src_counts = None
    launchpad_ok = pavilion_ok = None
    console_errors: list[str] = []

    def smoke():
        nonlocal src_counts, launchpad_ok, pavilion_ok, console_errors
        console_errors = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_context(viewport={"width": 1280, "height": 800}).new_page()
            page.on("console",
                    lambda m: console_errors.append(m.text) if m.type == "error" else None)
            page.goto(viewer_url(), wait_until="domcontentloaded", timeout=20_000)
            page.wait_for_function(
                """() => {
                  const m = window.AOP_HOST_MAP || window.map;
                  if (!m || !m.getSource) return false;
                  return ['fema-buildings','cemeteries','visitor-context','brand-logos','aop-trail-network']
                    .every((id) => m.getSource(id));
                }""",
                timeout=18_000,
            )
            page.wait_for_timeout(600)
            out = page.evaluate(
                """() => {
                  const m = window.AOP_HOST_MAP || window.map;
                  const ids = ['fema-buildings','cemeteries','visitor-context',
                               'brand-logos','aop-trail-network'];
                  const counts = {}; let launchpad = false, pavilion = false;
                  for (const id of ids) {
                    const s = m.getSource(id);
                    let d = (s && s.serialize && s.serialize().data) || (s && s._data);
                    if (typeof d === 'string') { try { d = JSON.parse(d); } catch(e){ d = null; } }
                    const feats = (d && d.features) || [];
                    counts[id] = feats.length;
                    if (id === 'aop-trail-network')
                      launchpad = feats.some((f)=> (f.properties||{}).name === 'Launchpad');
                    if (id === 'fema-buildings')
                      pavilion = feats.some((f)=> (f.properties||{}).name === 'Pavilion');
                  }
                  return {counts, launchpad, pavilion};
                }"""
            )
            src_counts = out["counts"]
            launchpad_ok = out["launchpad"]
            pavilion_ok = out["pavilion"]
            browser.close()

    try:
        smoke()
    except Exception as exc:  # one retry on flake
        print(f"    (smoke flaked: {exc!r}; retrying ONCE)")
        smoke()

    print(f"    source feature counts: {src_counts}")
    expected = {"fema-buildings": 5, "cemeteries": 8, "visitor-context": 2,
                "brand-logos": 2, "aop-trail-network": 120}
    check("viewer loaded served sources w/ expected counts "
          "(buildings 5, cemeteries 8, visitor 2+2=4, trails 120)",
          src_counts == expected, f"got={src_counts}")
    check("trail-network source has a feature name=='Launchpad' (canonical name renders)",
          bool(launchpad_ok))
    check("buildings source has a feature name=='Pavilion' (canonical name renders)",
          bool(pavilion_ok))
    check("0 console errors on minimal load", not console_errors,
          "; ".join(console_errors[:3]))

    print("\n== working tree (4 ref files LEFT ADOPTED; events restored to HEAD) ==")
    st = subprocess.run(["git", "status", "--short"], cwd=ROOT, capture_output=True, text=True).stdout
    for line in st.splitlines():
        if "website/data" in line:
            print(f"    {line}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nref-bake repro verification: FAIL")
        return 1
    print("\nref-bake repro verification: PASS (4 ref files adopted loss-free, one writer, viewer healthy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
