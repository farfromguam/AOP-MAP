#!/usr/bin/env python3
"""gMeta bake-side verifier (gold slice 6) — browserless, baked-file assertions.

Closes (by observation, not re-derivation) two findings:

  reference-bake-no-meta-on-fresh-volume — the served file's top-level keys (`_meta`
      = maturity badge + the trail GOLD BLOCK, plus owner-authored collection
      provenance) are reproduced from the COMMITTED store of record (_schema.json),
      NOT carried forward from the prior served file. Proven by FRESH-VOLUME
      SIMULATION: strip a served file to {type, features}, reproduce its top keys from
      the store ALONE (regen_meta.served_top_meta), and assert byte-identical to HEAD.

  schema-manifest-stale — _schema.json's per-layer `features` count + `updated_at`
      are regenerated from the served truth by ONE writer (the export bake), while
      the curated fields survive. Proven by mutating a count, running the regen, and
      asserting the count is corrected and the curated store is preserved.

Plus a LOSS-FREE assertion: every served reference/publish file vs HEAD has ONLY
the additive per-feature `maturity` key added (no top-level drop/add/value-diff, no
per-feature key dropped or changed). This is the slice's "exactly the intended
additive change" proof.

This reads files + subprocess `git show HEAD:` (read-only). No DB, no browser.

Run:  python3 mvp/scripts/verify_gMeta_bake.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import regen_meta as rm  # noqa: E402

REPO = HERE.parents[1]
DATA = REPO / "website" / "data"
REF_FILES = [
    "aop_buildings.geojson", "aop_cemeteries.geojson",
    "aop_visitor_context_callouts.geojson", "aop_trail_network.geojson",
    "publish.geojson",
]


def check(label, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def head_json(rel):
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True, cwd=str(REPO))
    return json.loads(out.stdout)


def live_json(rel):
    return json.loads((REPO / rel).read_text())


def jdump(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def main():
    schema = rm._load_schema()

    # --- Finding 1: fresh-volume reproduction from the store ALONE ---------------
    print("Finding 1 — _meta reproduced from the store of record (fresh-volume):")
    for fn in REF_FILES:
        rel = f"website/data/{fn}"
        head = head_json(rel)
        # HEAD's top-level keys (the truth to reproduce), key order preserved.
        head_top_keys = [k for k in head if k not in ("type", "features")]
        head_top = {k: head[k] for k in head_top_keys}
        # Reproduce from the store ONLY (no prior served file is read here).
        repro = rm.served_top_meta(fn, schema)
        repro_keys = list(repro.keys())
        keys_ok = repro_keys == head_top_keys
        vals_ok = jdump(dict(repro)) == jdump(head_top)
        check(f"{fn}: top keys reproduced from store ALONE, byte-identical to HEAD "
              f"(order + values)", keys_ok and vals_ok,
              "" if (keys_ok and vals_ok) else f"keyorder={repro_keys} vs {head_top_keys}")
    # the trail gold block specifically (the rich self-describing block)
    trail_meta = rm.served_top_meta("aop_trail_network.geojson", schema).get("_meta", {})
    gold_keys = ("about", "crs", "color_legend", "difficulty_band", "feature_count",
                 "difficulty_counts", "color_counts", "named", "numbered",
                 "property_schema", "review_flags", "generated_from")
    check("trail GOLD BLOCK fully present in the store reproduction",
          all(k in trail_meta for k in gold_keys),
          f"missing={[k for k in gold_keys if k not in trail_meta]}")

    # --- Finding 1 (end-to-end): the LIVE served file actually carries _meta ----
    print("\nFinding 1 — the live baked served files carry the reproduced _meta:")
    for fn in REF_FILES:
        live = live_json(f"website/data/{fn}")
        meta = live.get("_meta")
        check(f"{fn}: served _meta present + matches HEAD",
              isinstance(meta, dict) and jdump(meta) == jdump(head_json(f"website/data/{fn}").get("_meta")),
              "" if isinstance(meta, dict) else "no _meta")

    # --- Finding 2: the manifest is regenerated (counts) + curated preserved -----
    print("\nFinding 2 — manifest counts regenerate, curated fields preserved:")
    schema_path = DATA / "_schema.json"
    before = json.loads(schema_path.read_text())
    # Corrupt one count + the date, run the regen, assert it self-heals.
    corrupt = json.loads(schema_path.read_text())
    corrupt["layers"]["aop_buildings.geojson"]["features"] = 999
    corrupt["updated_at"] = "1999-01-01"
    schema_path.write_text(json.dumps(corrupt, ensure_ascii=False, indent=2))
    rm.regen_manifest(check=False)
    after = json.loads(schema_path.read_text())
    check("manifest regen corrects a drifted per-layer count (999 -> live)",
          after["layers"]["aop_buildings.geojson"]["features"]
          == len(live_json("website/data/aop_buildings.geojson")["features"]),
          f"got {after['layers']['aop_buildings.geojson']['features']}")
    check("manifest regen refreshes updated_at off the stale 1999 date",
          after["updated_at"] != "1999-01-01", f"updated_at={after['updated_at']}")
    # curated fields (maturity stamp, the verbatim `meta`, collection_meta, tiers)
    # are PRESERVED across the regen (maturity is INPUT, counts/date are OUTPUT).
    bl = before["layers"]["aop_trail_network.geojson"]
    al = after["layers"]["aop_trail_network.geojson"]
    check("manifest regen PRESERVES the curated maturity stamp + verbatim meta + collection_meta",
          al.get("maturity") == bl.get("maturity") and jdump(al.get("meta")) == jdump(bl.get("meta"))
          and jdump(al.get("collection_meta")) == jdump(bl.get("collection_meta")),
          "")
    check("manifest regen PRESERVES maturity_tiers", jdump(after.get("maturity_tiers")) == jdump(before.get("maturity_tiers")))
    # restore the manifest exactly as it was before this test.
    schema_path.write_text(json.dumps(before, ensure_ascii=False, indent=2))

    # --- Loss-free: only the additive per-feature `maturity` key changed vs HEAD --
    print("\nLoss-free — served files vs HEAD: ONLY per-feature `maturity` added:")
    for fn in REF_FILES:
        rel = f"website/data/{fn}"
        h, l = head_json(rel), live_json(rel)
        hk = {k for k in h if k not in ("type", "features")}
        lk = {k for k in l if k not in ("type", "features")}
        top_ok = hk == lk and all(jdump(h[k]) == jdump(l[k]) for k in hk)

        def byid(d):
            m = {}
            for ft in d["features"]:
                pr = ft.get("properties") or {}
                m[pr.get("id")] = pr
            return m
        hb, lb = byid(h), byid(l)
        added, dropped, valdiff, missing = set(), set(), set(), 0
        for fid, hp in hb.items():
            lp = lb.get(fid)
            if lp is None:
                missing += 1
                continue
            added |= set(lp) - set(hp)
            dropped |= set(hp) - set(lp)
            for k in set(hp) & set(lp):
                if jdump(hp[k]) != jdump(lp[k]):
                    valdiff.add(k)
        ok = top_ok and added == {"maturity"} and not dropped and not valdiff and not missing
        check(f"{fn}: loss-free, only `maturity` added", ok,
              f"top_identical={top_ok} added={added or '-'} dropped={dropped or '-'} "
              f"valdiff={valdiff or '-'} missing={missing}")
        # the added maturity equals the file's layer tier
        layer_mat = (schema.get("layers", {}).get(fn, {}) or {}).get("maturity")
        mats = {(ft.get("properties") or {}).get("maturity") for ft in l["features"]}
        check(f"{fn}: every feature's baked maturity == layer tier '{layer_mat}'",
              mats == {layer_mat}, f"values={mats}")

    if check.failed:  # type: ignore[attr-defined]
        print("\ngMeta-bake verification: FAIL")
        return 1
    print("\ngMeta-bake verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
