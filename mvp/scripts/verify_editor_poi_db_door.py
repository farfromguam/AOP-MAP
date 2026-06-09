#!/usr/bin/env python3
"""Gold slice 6 / F2 acceptance — the drawn-POI DB door (aop_editor_pois_v1 ->
core.features layer='poi'), verified BY OBSERVATION, browserless (the gold "baked-file
assertion" standard #1: assert directly on the DB + the baked publish.geojson — no tiles,
no map).

Acceptance (Sprint 09 editor_completeness Slice 5 / F2): draw+star a POI -> apply -> bake
-> it publishes; a browser reset does NOT lose it (it is in core.features, the store of
record); the publish gate still holds (a candidate drawn POI does NOT leak into publish).

Flow: apply a test drawn-POI FeatureCollection (one publishable, one candidate) via
apply_editor_pois_to_core.py -> assert both land active in core.features (survives reset)
-> bake -> assert publish.geojson carries the publishable POI and NOT the candidate (gate)
-> re-apply (idempotent, no dup) -> CLEANUP: restore served files to HEAD (git show) and
remove the test rows so the verifier is re-runnable and production is untouched.

Run from repo root with the DB up (docker compose -f mvp/docker-compose.yml up -d db).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COMPOSE = REPO / "mvp" / "docker-compose.yml"
SCRIPTS = REPO / "mvp" / "scripts"
PUBLISH = REPO / "website" / "data" / "publish.geojson"

PUB_KEY = "editorPois:f2-pub-test"
CAND_KEY = "editorPois:f2-candidate-test"
NULL_KEY = "editorPois:f2-nullgeom-test"
TEST_FC = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-85.7466, 35.0888]},
         "properties": {"id": "f2-pub-test", "name": "F2 Publishable POI",
                        "description": "drawn-POI DB door test", "category": "Landmark",
                        "layer": "editor_poi", "permission": "publish",
                        "publish_status": "publish", "is_destination": True}},
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-85.7470, 35.0895]},
         "properties": {"id": "f2-candidate-test", "name": "F2 Candidate POI",
                        "description": "should NOT publish", "category": "Other",
                        "layer": "editor_poi"}},
        # R13 no-throw / no-drop: a feature mid-draw can carry geometry:null. It must
        # upsert geom-less, never crash the batch (the Mason andon, folded).
        {"type": "Feature", "geometry": None,
         "properties": {"id": "f2-nullgeom-test", "name": "F2 Null-geom POI",
                        "category": "Other", "layer": "editor_poi"}},
    ],
}


def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True
check.failed = False


def psql(sql: str) -> str:
    cmd = ["docker", "compose", "-f", str(COMPOSE), "exec", "-T", "db",
           "psql", "-U", "aop", "-d", "aop_map", "-At", "-q", "-v", "ON_ERROR_STOP=1"]
    p = subprocess.run(cmd, input=sql, text=True, capture_output=True)
    if p.returncode != 0:
        print(p.stdout, p.stderr)
        raise SystemExit("psql failed")
    return p.stdout.strip()


def core_poi(source_key: str) -> dict | None:
    out = psql(
        "SELECT json_build_object('name',name,'permission',permission,"
        "'publish_status',publish_status,'archived',archived_at IS NOT NULL,"
        "'has_geom',geom IS NOT NULL) "
        f"FROM core.features WHERE layer='poi' AND source_key='{source_key}';")
    return json.loads(out) if out else None


def baked_poi_names() -> list:
    if not PUBLISH.exists():
        return []
    fc = json.loads(PUBLISH.read_text())
    return [ (f.get("properties") or {}).get("name")
             for f in fc.get("features", []) if (f.get("properties") or {}).get("layer") == "poi" ]


def restore_served_to_head():
    """Restore every served file the bake touched back to HEAD (read-only git show +
    write — never git checkout/restore). The durable change is in the DB + the script."""
    changed = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "website/data"],
                             text=True, capture_output=True).stdout.splitlines()
    for line in changed:
        path = line[3:].strip()
        if not path:
            continue
        head = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{path}"],
                              text=True, capture_output=True)
        if head.returncode == 0:
            (REPO / path).write_text(head.stdout)


def main() -> int:
    fc_path = Path("/tmp/aop_f2_test_drawn_pois.json")
    fc_path.write_text(json.dumps(TEST_FC))

    try:
        # 1) Apply the drawn-POI FC into core via the F2 door.
        r = subprocess.run([sys.executable, str(SCRIPTS / "apply_editor_pois_to_core.py"), str(fc_path)],
                           text=True, capture_output=True)
        print(r.stdout.strip())
        check("apply_editor_pois_to_core.py succeeded", r.returncode == 0 and "OK" in r.stdout)

        # 2) Both POIs are in core.features, active (the store of record → survives a
        #    browser reset, which clears localStorage but not the DB).
        pub = core_poi(PUB_KEY); cand = core_poi(CAND_KEY)
        check("publishable drawn POI is in core.features, active, with geom",
              bool(pub) and not pub["archived"] and pub["has_geom"]
              and pub["permission"] == "publish" and pub["publish_status"] == "publish",
              f"{pub}")
        check("candidate drawn POI is in core.features, active (NOT publish-gated)",
              bool(cand) and not cand["archived"] and cand["publish_status"] != "publish",
              f"{cand}")
        # R13: the null-geometry POI upserted geom-less (no throw, no drop — Mason andon).
        nullg = core_poi(NULL_KEY)
        check("null-geometry drawn POI upserts geom-less (no throw, not dropped)",
              bool(nullg) and not nullg["archived"] and not nullg["has_geom"],
              f"{nullg}")

        # 3) Bake core → served files.
        b = subprocess.run(["bash", str(SCRIPTS / "export_publish_geojson.sh")],
                           text=True, capture_output=True)
        check("bake (export_publish_geojson.sh) succeeded", b.returncode == 0,
              (b.stderr or "")[-200:])

        # 4) publish.geojson carries the publishable POI and NOT the candidate (gate).
        names = baked_poi_names()
        check("publishable drawn POI is in publish.geojson (it publishes)",
              "F2 Publishable POI" in names, f"poi names={names}")
        check("candidate drawn POI is GATED OUT of publish.geojson",
              "F2 Candidate POI" not in names, f"poi names={names}")

        # 5) Idempotent re-apply — no duplicate rows.
        before = int(psql("SELECT count(*) FROM core.features WHERE layer='poi';"))
        subprocess.run([sys.executable, str(SCRIPTS / "apply_editor_pois_to_core.py"), str(fc_path)],
                       text=True, capture_output=True)
        after = int(psql("SELECT count(*) FROM core.features WHERE layer='poi';"))
        check("re-apply is idempotent (no duplicate core rows)", before == after,
              f"before={before} after={after}")

    finally:
        # CLEANUP — restore production + remove the test rows (test scaffolding, not the
        # production apply path; the script itself never deletes — loop contract #4).
        restore_served_to_head()
        psql(f"DELETE FROM core.features WHERE source_key IN ('{PUB_KEY}','{CAND_KEY}','{NULL_KEY}');")

    # 6) Cleanup assertions: test rows gone, served files clean vs HEAD.
    check("test rows removed from core.features (cleanup)",
          core_poi(PUB_KEY) is None and core_poi(CAND_KEY) is None and core_poi(NULL_KEY) is None)
    dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain", "website/data"],
                           text=True, capture_output=True).stdout.strip()
    check("served files restored byte-identical to HEAD (production untouched)", dirty == "",
          f"dirty={dirty[:200]}")

    if check.failed:
        print("editor-poi-db-door verification: FAIL"); return 1
    print("editor-poi-db-door verification: PASS"); return 0


if __name__ == "__main__":
    sys.exit(main())
