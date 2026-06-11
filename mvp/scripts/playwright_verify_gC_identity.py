#!/usr/bin/env python3
"""G_C (gold slice 6) — collapse identity forks: the live editor still resolves
the RIGHT single feature after the canonical-id changes, and an edit/star lands
on that one feature (it does NOT smear or land on the cemetery twin).

Shadow-attribute audit ids this closes/exercises:
  - served-id-heterogeneous-no-canonical-key   (served id == DB source_key biz part)
  - cemetery-parcel-marker-twin-nonunique-id    (twin shares one id -> now distinct)
  - buildings-served-id-is-attrs-businesskey-not-pk (served id was UUID -> build_id)
  - publish-kind-taxonomy-fork                   (pavilion -> poi + category facet)
  - ellis-cemetery-multi-id-across-files         (same_as cross-link)

Tile-independent, lean (playwright_base, NO networkidle, NO queryRenderedFeatures).
The map DOES load on :8001 (basemap reachable there) -> wait for map._loaded +
__panelReady, then drive the right panel + the host bridges.

THE KEY OBSERVATION (the whole risk): a cemetery ★/edit must land on the MARKER
store-of-record, not the parcel twin. We call the live host bridge
window.AOP_HOST_SET_HIGHLIGHT('cemeteries', <marker props>, true) and read back
which feature got highlight=true in the host's own live data — exactly ONE, the
marker, never the parcel. We also confirm a building (build_id id), a trail
(sfwda id), and a published feature (poi/category) resolve + a name edit
round-trips through the one door.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "website", "data")
MVP = os.path.join(ROOT, "mvp")

FAILS = []


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    if not ok:
        FAILS.append(label)
    print(f"  [{mark}] {label}" + (f"  — {detail}" if detail else ""))


def psql(sql: str) -> str:
    out = subprocess.run(
        ["docker", "compose", "exec", "-T", "db", "psql", "-U", "aop", "-d", "aop_map",
         "-At", "-c", sql],
        cwd=MVP, capture_output=True, text=True,
    )
    return out.stdout.strip()


def served(fname: str) -> dict:
    with open(os.path.join(DATA, fname)) as fh:
        return json.load(fh)


def main() -> int:
    print("== G_C identity-fork verifier ==")

    # ---- 1) Served ids are canonical == DB source_key business part ------------
    cem = served("aop_cemeteries.geojson")
    cem_ids = [f["properties"]["id"] for f in cem["features"]]
    check("cemetery served ids are UNIQUE (twin no longer shares one id)",
          len(cem_ids) == len(set(cem_ids)) == 8, f"ids={cem_ids}")
    check("cemetery ids are '<parcel_id>:<geom_role>'",
          all(":marker" in i or ":parcel" in i for i in cem_ids))

    bld = served("aop_buildings.geojson")
    bld_ok = all(f["properties"]["id"] == str(f["properties"]["build_id"]) for f in bld["features"])
    uuid_ok = all(f["properties"].get("uuid", "").startswith("{") for f in bld["features"])
    check("building served id == build_id (was the FEMA UUID)", bld_ok)
    check("building UUID preserved in attrs.uuid (additive, no loss)", uuid_ok)

    tr = served("aop_trail_network.geojson")
    tr_ok = all(str(f["properties"]["id"]).startswith("sfwda-") for f in tr["features"])
    check("trail served id == 'sfwda-N' (== DB source_key biz part)", tr_ok)

    # served id == DB source_key business part, per layer
    for layer, fname in [("cemeteries", "aop_cemeteries.geojson"),
                         ("buildings", "aop_buildings.geojson"),
                         ("trails", "aop_trail_network.geojson"),
                         ("visitor", "aop_visitor_context_callouts.geojson")]:
        rows = psql(
            f"SELECT regexp_replace(source_key, '^' || layer || ':', '') "
            f"FROM core.features WHERE layer='{layer}' AND archived_at IS NULL ORDER BY 1;"
        ).splitlines()
        sids = sorted(str(f["properties"]["id"]) for f in served(fname)["features"])
        check(f"{layer}: served id set == DB source_key business-part set",
              sorted(rows) == sids, f"db={sorted(rows)[:3]}… served={sids[:3]}…")

    # ---- 2) publish kind from the controlled list + Ellis cross-link ----------
    pub = {f["properties"]["id"]: f["properties"] for f in served("publish.geojson")["features"]}
    pav = pub.get("editorPois:aop-pavilion", {})
    check("publish Pavilion kind mapped pavilion->poi",
          pav.get("kind") == "poi", f"kind={pav.get('kind')}")
    check("publish Pavilion class preserved as category facet",
          pav.get("category") == "pavilion", f"category={pav.get('category')}")
    ell_poi = pub.get("editorPois:ellis-cemetery", {})
    check("publish Ellis poi same_as -> canonical cemetery marker",
          ell_poi.get("same_as") == "110 008.04:marker", f"same_as={ell_poi.get('same_as')}")
    boundary = pub.get("park_boundaries:2", {})
    check("non-mapped publish kinds pass through (envelope unchanged)",
          "category" not in boundary and boundary.get("kind") in (None,),
          f"kind={boundary.get('kind')}")
    # reciprocal cemetery -> poi link
    cem_ellis = [f["properties"] for f in cem["features"] if f["properties"].get("parcel_id") == "110 008.04"]
    check("reciprocal: cemetery Ellis rows same_as -> publish poi",
          all(p.get("same_as") == "editorPois:ellis-cemetery" for p in cem_ellis))

    # ---- 3) LIVE editor: the cemetery ★ lands on the MARKER, not the twin -----
    errs = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function("() => window.map && window.map._loaded === true", timeout=25_000)
        page.wait_for_function("() => window.__panelReady === true", timeout=20_000)
        page.wait_for_timeout(500)

        # THE KEY TEST. Drive the host's own ★ bridge with the MARKER's props
        # (what the panel passes — it filters geom_role==='marker'). The bridge
        # resolves the feature via positionedFeatureIdFor -> props[idField=id] ->
        # findFeatureById, sets highlight on that ONE feature, and persists the
        # patch to the aop_positioned_features_v1 store keyed `cemeteries:<id>`.
        # The OBSERVABLE: the store key that gets written. Pre-G_C it would be the
        # bare/parcel `cemeteries:093 001.02`; post-G_C it MUST be the canonical
        # MARKER `cemeteries:093 001.02:marker` — proof the star landed on the
        # marker store-of-record by its unique id, not the twin.
        STORE = "aop_positioned_features_v1"
        result = page.evaluate(
            """(STORE) => {
              const marker = { parcel_id: '093 001.02', geom_role: 'marker',
                               id: '093 001.02:marker', name: 'Tate Cemetery' };
              localStorage.removeItem(STORE);                       // clean slate
              const ok = window.AOP_HOST_SET_HIGHLIGHT('cemeteries', marker, true);
              const store = JSON.parse(localStorage.getItem(STORE) || '{}');
              const keys = Object.keys(store);
              const starred = keys.filter(k => store[k] && store[k].highlight === true);
              // un-star to leave a clean buffer
              window.AOP_HOST_SET_HIGHLIGHT('cemeteries', marker, false);
              return { ok, keys, starred };
            }""",
            STORE,
        )

        # A building edit round-trips through the one door. The host bridge
        # resolves via props.build_id (idField) and persists the name edit; for a
        # served reference layer setFeatureProperty routes to savePositionedFeature,
        # keyed `buildings:<positionedFeatureIdFor>` = `buildings:<build_id>`. The
        # OBSERVABLE: the store key written — it must be `buildings:3397585` (the
        # canonical build_id == the served id now), proving the edit landed on the
        # one building resolved by its canonical id, not the old UUID.
        bld_rt = page.evaluate(
            """(STORE) => {
              const f = { build_id: 3397585, id: '3397585', name: 'Pavilion',
                          aop_facility: true };  // Pavilion props as the panel passes
              localStorage.removeItem(STORE);
              const ok = window.AOP_HOST_SET_FEATURE_PROPS('buildings', f, { name: 'Pavilion G_C test' });
              const store = JSON.parse(localStorage.getItem(STORE) || '{}');
              const keys = Object.keys(store);
              return { ok, keys, build_id: f.build_id };
            }""",
            STORE,
        )
        b.close()

    check("viewer + panel booted with 0 console errors", len(errs) == 0, f"errors={errs[:3]}")

    starred = result.get("starred") or []
    check("cemetery ★ bridge resolved + returned ok", result.get("ok") is True,
          f"keys={result.get('keys')}")
    check("EXACTLY ONE positioned-features store key took the star (no smear across the twin)",
          len(starred) == 1, f"starred={starred}")
    check("the star landed on the MARKER store-of-record id 'cemeteries:093 001.02:marker' "
          "(the unique canonical id — NOT the bare/parcel twin)",
          starred == ["cemeteries:093 001.02:marker"], f"starred={starred}")

    check("building edit bridge resolved + returned ok", bld_rt.get("ok") is True,
          f"keys={bld_rt.get('keys')}")
    bkeys = bld_rt.get("keys") or []
    check("building name edit landed on the ONE building keyed by its canonical id "
          "'buildings:3397585' (build_id == served id; was the UUID)",
          bkeys == ["buildings:3397585"], f"keys={bkeys}")

    print()
    if FAILS:
        print(f"RESULT: {len(FAILS)} FAIL(S): {FAILS}")
        return 1
    print("RESULT: ALL PASS — identity forks collapsed; the live editor resolves the right single feature.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
