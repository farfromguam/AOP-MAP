#!/usr/bin/env python3
"""F4 (gold slice 6) — publish.geojson is a reproducible pure function of the DB.

Shadow-attribute audit ids this closes:
  - publish-geojson-stale-not-reproducible   (served file != f(live DB + bake SQL))
  - published-id-is-volatile-serial          (served id was the serial PK; now source_key)

Five tile-independent observations (per playwright_base + C4 — NO networkidle,
NO queryRenderedFeatures):

  1. REPRODUCIBLE: run export_publish_geojson.sh TWICE -> the served
     publish.geojson is byte-identical (md5), AND its feature set == the live
     DB's publish-gated set (count + ids == the DB source_keys from psql).
  2. ID = SOURCE_KEY: every served `id` is the stable business key (source_key),
     not the volatile serial PK and not the stale 1-6.
  3. NO STALE KEYS: no `blurb` on any published feature; canonical name +
     description present.
  4. VIEWER HEALTHY + EDITOR MATCHES: load :8001, 0 console errors; a published
     feature (the Ellis inholding park_boundary) is selectable/editable in the
     right panel, the editor RESOLVES it (the Name input shows its canonical
     name read live from the DOM), and its served id == its DB source_key.
  5. GATE INTACT: an unpublishable candidate (Proving Grounds, unknown/candidate)
     is still excluded from the bake.

The deferred sibling reference/event files (buildings/cemeteries/visitor/
trail_network/aop_event_schedule) are restored to HEAD between bakes — this
slice owns publish.geojson + its viewer id-match only.
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
PUBLISH = os.path.join(ROOT, "website", "data", "publish.geojson")
BAKE = os.path.join(ROOT, "mvp", "scripts", "export_publish_geojson.sh")
MVP = os.path.join(ROOT, "mvp")
DEFERRED = [
    "aop_buildings.geojson", "aop_cemeteries.geojson", "aop_event_schedule.json",
    "aop_trail_network.geojson", "aop_visitor_context_callouts.geojson",
]
# The published feature we drive through the editor (a real publish-gated
# park_boundary, locked but selectable; reading its Name input value proves the
# panel resolved it by the served id == source_key).
EDIT_LABEL = "Ellis Cemetery (inholding parcel)"
EDIT_SOURCE_KEY = "park_boundaries:ellis-inholding"
EDIT_EXPECT_NAME = "Ellis Cemetery (inholding parcel)"
# The unpublishable candidate that MUST stay excluded by the gate.
EXCLUDED_SOURCE_KEY = "editorPois:proving-grounds-candidate"


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def md5_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def restore_head(rel: str) -> None:
    """Write HEAD bytes of website/data/<rel> back (a file write, not a git mutation)."""
    out = subprocess.run(
        ["git", "show", f"HEAD:website/data/{rel}"],
        cwd=ROOT, capture_output=True, check=True,
    )
    with open(os.path.join(ROOT, "website", "data", rel), "wb") as fh:
        fh.write(out.stdout)


def run_bake() -> None:
    subprocess.run(["bash", BAKE], cwd=ROOT, capture_output=True, check=True)


def psql(sql: str) -> str:
    out = subprocess.run(
        ["docker", "compose", "-f", os.path.join(MVP, "docker-compose.yml"),
         "exec", "-T", "db", "psql", "-U", "aop", "-d", "aop_map", "-At", "-c", sql],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return out.stdout.strip()


def db_publish_source_keys() -> list[str]:
    raw = psql(
        "SELECT source_key FROM core.features "
        "WHERE permission='publish' AND publish_status='publish' AND archived_at IS NULL "
        "ORDER BY source_key;"
    )
    return [r for r in raw.splitlines() if r]


def main() -> int:
    # --- 1. REPRODUCIBLE (byte-identical across two bakes) -------------------
    # Seed _meta from HEAD so the carry-forward is deterministic, then bake twice.
    restore_head("publish.geojson")
    run_bake()
    for rel in DEFERRED:
        restore_head(rel)
    md5_a = md5_of(PUBLISH)

    run_bake()
    for rel in DEFERRED:
        restore_head(rel)
    md5_b = md5_of(PUBLISH)

    check("publish.geojson is byte-identical across two bakes (reproducible)",
          md5_a == md5_b, f"md5 run1={md5_a} run2={md5_b}")

    doc = json.load(open(PUBLISH))
    feats = doc.get("features", [])
    served_ids = [f.get("properties", {}).get("id") for f in feats]
    db_keys = db_publish_source_keys()

    check("served feature COUNT == live DB publish-gated count",
          len(feats) == len(db_keys), f"served={len(feats)} db={len(db_keys)}")
    check("served ids == DB source_keys (set equality)",
          sorted(str(i) for i in served_ids) == sorted(db_keys),
          f"served={sorted(str(i) for i in served_ids)} db={sorted(db_keys)}")

    # --- 2. ID = SOURCE_KEY (stable business key, not serial PK, not 1-6) ----
    all_are_keys = all(isinstance(i, str) and ":" in i for i in served_ids)
    no_bare_serial = not any(str(i).isdigit() for i in served_ids)
    check("every served id is a source_key (contains ':'), not a bare serial",
          all_are_keys and no_bare_serial, f"ids={served_ids}")
    check("served ids are UNIQUE (the stale 1-6 had a colliding id=2)",
          len(served_ids) == len(set(served_ids)), f"ids={served_ids}")

    # --- 3. NO STALE KEYS (blurb gone; canonical name+description present) ---
    any_blurb = any("blurb" in (f.get("properties") or {}) for f in feats)
    all_named = all((f.get("properties") or {}).get("name") for f in feats)
    has_desc = all("description" in (f.get("properties") or {}) for f in feats)
    check("no `blurb` key on any published feature (canonical description only)",
          not any_blurb)
    check("canonical `name` present on every published feature", all_named)
    check("canonical `description` key present on every published feature", has_desc)

    # --- 5. GATE INTACT (unpublishable candidate excluded) ------------------
    check(f"gate excludes the unpublishable candidate ({EXCLUDED_SOURCE_KEY})",
          EXCLUDED_SOURCE_KEY not in served_ids)
    # And confirm that candidate really exists in the DB but off-gate (so the
    # exclusion is the gate doing work, not the row being absent).
    cand = psql(
        "SELECT permission || '/' || publish_status FROM core.features "
        f"WHERE source_key = '{EXCLUDED_SOURCE_KEY}';"
    )
    check("the excluded candidate IS in the DB but off-gate (gate, not absence)",
          cand not in ("", "publish/publish"), f"db gate state = {cand or '(absent)'}")

    # --- 4. VIEWER HEALTHY + EDITOR MATCHES ---------------------------------
    console_errors: list[str] = []
    name_value = None
    served_id_for_edit = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(viewport={"width": 1366, "height": 900}).new_page()
        page.on("console",
                lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message') && "
            "document.getElementById('message').textContent.includes('publish feature')",
            timeout=20_000,
        )
        # The embedded panel boots after the host's layers are up (whenHostReady);
        # __panelReady is its end-of-boot signal.
        page.wait_for_function("() => window.__panelReady === true", timeout=20_000)
        page.wait_for_timeout(500)

        # Read the served publish feature's id straight off the host map source
        # (tile-independent: no paint, no queryRenderedFeatures).
        served_id_for_edit = page.evaluate(
            """(label) => {
              const m = window.AOP_HOST_MAP;
              if (!m || !m.getSource) return null;
              const src = m.getSource('publish-data');
              if (!src) return null;
              // The exact feature set the source was fed (tile-independent). Prefer
              // serialize().data (a FeatureCollection); fall back to _data if it
              // happens to carry features.
              let d = (src.serialize && src.serialize().data) || src._data;
              if (typeof d === 'string') { try { d = JSON.parse(d); } catch (e) { d = null; } }
              if (!d || !d.features) return null;
              const f = d.features.find((ft) => (ft.properties || {}).name === label);
              return f ? (f.properties || {}).id : null;
            }""",
            EDIT_LABEL,
        )
        check("published feature loaded into the viewer's publish-data source "
              "with served id == DB source_key",
              served_id_for_edit == EDIT_SOURCE_KEY,
              f"served id={served_id_for_edit!r} source_key={EDIT_SOURCE_KEY!r}")

        # Open the published feature's editor in the right panel: open the panel,
        # expand the 'boundaries' node, then click its item row by label. The panel
        # resolves the item by `deriveItems(...).find(it.key === sel.key)` where the
        # key is now the served id (= source_key) — a populated Name input proves
        # the editor matched the published feature by that served id.
        page.evaluate(
            """() => {
              const c = document.getElementById('panelCollapse');
              if (c && c.getAttribute('aria-expanded') === 'false') c.click();
              const grp = document.querySelector('[data-node-id="boundaries"]');
              if (grp) { const ch = grp.querySelector('.node-chevron-btn'); if (ch) ch.click(); }
            }"""
        )
        page.wait_for_timeout(400)
        clicked = page.evaluate(
            """(label) => {
              const grp = document.querySelector('[data-node-id="boundaries"]');
              if (!grp) return false;
              const btn = [...grp.querySelectorAll('.item-select')]
                .find((b) => (b.textContent || '').trim() === label);
              if (!btn) return false;
              btn.click();
              return true;
            }""",
            EDIT_LABEL,
        )
        check("published park_boundary row is selectable in the right panel",
              clicked, f"label={EDIT_LABEL!r}")
        page.wait_for_timeout(400)

        name_value = page.evaluate(
            """() => {
              const inp = document.querySelector('.field-input[data-field="name"]');
              return inp ? inp.value : null;
            }"""
        )
        check("editor RESOLVED the published feature — Name input shows its "
              "canonical name (read live from the DOM)",
              name_value == EDIT_EXPECT_NAME,
              f"Name input value={name_value!r} expected={EDIT_EXPECT_NAME!r}")

        check("0 console errors on load + published-feature edit",
              not console_errors, "; ".join(console_errors[:3]))
        browser.close()

    print()
    print(f"  served ids: {served_ids}")
    print(f"  DB source_keys: {db_keys}")
    print(f"  edited feature served id == source_key: {served_id_for_edit!r}")
    print(f"  edited feature panel Name input value: {name_value!r}")

    if check.failed:  # type: ignore[attr-defined]
        print("\nF4 publish-repro verification: FAIL")
        return 1
    print("\nF4 publish-repro verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
