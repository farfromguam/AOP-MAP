#!/usr/bin/env python3
"""Shadow-attribute resolution A5 — edge-dispatch → spec strategies.

A5 moves the remaining per-layer call-site special-casing into declarative spec /
node capabilities (C1), naming no layerKey / source literal at the call site:

  * host-create-bridge-hardcodes-editorpois — AOP_HOST_CREATE_FEATURE dispatches
    through a `spec.create` capability (was `if layerKey !== 'editorPois'`). A
    layer opts in by declaring `create`; everything else returns null (safe
    default, no throw).
  * visitor-list-source-chip-freestanding-map — `sourceChip` is a co-located spec
    field (was the free-standing VISITOR_LIST_SOURCE_CHIP map).
  * panel-explicit-host-toggle-map — `node.hostToggle` is a declarative node field
    (was the EXPLICIT_HOST_TOGGLE id-keyed map).
  * panel-userfeatures-source-special-casing — one `usesUserFeatures(spec)`
    predicate + `USER_FEATURES_SOURCE` constant (was `=== 'userFeatures'` smeared
    across call sites).
  * panel-positional-synthetic-index-identity — deriveItems falls back to the
    canonical baked `id` before the positional load index (never identity = idx).

The CREATE path is the one with user-facing behavior, so it gets a LIVE check: a
"+ POI" create is driven through the SAME host bridge the panel's commitFeature
uses, and the DOM/source is read before/after to confirm the feature lands and is
editable exactly as before. The other four sub-changes are STRUCTURAL (the call
site reads a declarative capability; the dispatch map is gone) — asserted by
reading the shipped files, not by narrating a DOM check that the embedded viewer
can't surface (the ★ Visitor-list chip + SFWDA toggle render into main.js's
hidden #editorTree under panel-embed). Tile-independent. Run with a viewer on :8001.
"""

from __future__ import annotations

import os
import re
import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MAIN_JS = os.path.join(ROOT, "website", "js", "main.js")
PANEL_JS = os.path.join(ROOT, "website", "js", "panel.js")


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def structural_checks() -> None:
    print("\n== Structural: the dispatch maps are gone; call sites read a capability ==")
    main = open(MAIN_JS).read()
    panel = open(PANEL_JS).read()

    # C1: no non-comment `layerKey === '` branches in main.js.
    c1 = [i + 1 for i, l in enumerate(main.splitlines())
          if "layerKey === '" in l and not l.strip().startswith("//")]
    check("C1: 0 non-comment `layerKey === '` branches in main.js", c1 == [], str(c1))
    # C6: no class declarations.
    classes = re.findall(r"(?m)^\s*class [A-Z]", main) + re.findall(r"(?m)^\s*class [A-Z]", panel)
    check("C6: 0 class declarations", classes == [], str(classes))

    # host create → spec.create dispatch (no literal editorPois guard left in CODE;
    # a description of what it replaced survives in a comment, which is fine).
    guard = [i + 1 for i, l in enumerate(main.splitlines())
             if "!== 'editorPois'" in l and not l.strip().startswith("//")]
    check("create bridge dispatches through spec.create (no non-comment `!== 'editorPois'` guard)",
          "return spec.create(geometry, opts)" in main and guard == [], str(guard))
    check("editorPois spec declares the `create` capability", "create: (geometry, opts)" in main)

    # sourceChip is a spec field; the free-standing map is gone.
    check("VISITOR_LIST_SOURCE_CHIP dispatch map removed (no const decl)",
          "const VISITOR_LIST_SOURCE_CHIP" not in main)
    check("sourceChip read from the spec (`spec.sourceChip`)", "spec.sourceChip" in main)
    check("4 specs co-locate a `sourceChip` field", main.count("sourceChip: '") == 4,
          str(main.count("sourceChip: '")))

    # node.hostToggle replaces EXPLICIT_HOST_TOGGLE.
    check("EXPLICIT_HOST_TOGGLE map removed", "const EXPLICIT_HOST_TOGGLE" not in panel)
    check("bridge reads declarative `node.hostToggle`", "node.hostToggle" in panel)
    check("sfwda node declares `hostToggle: 'showSfwda'`", "hostToggle: 'showSfwda'" in panel)

    # userFeatures literal converged to one constant + predicate.
    lit = [i + 1 for i, l in enumerate(panel.splitlines())
           if "'userFeatures'" in l and "USER_FEATURES_SOURCE =" not in l and not l.strip().startswith("//")]
    check("no `'userFeatures'` literal left at a call site (converged to a constant/predicate)",
          lit == [], str(lit))
    check("usesUserFeatures predicate used at the dispatch sites", panel.count("usesUserFeatures") >= 4)

    # deriveItems prefers the canonical id before the positional index.
    check("deriveItems falls back to canonical `id` before positional `idx`",
          "props.id != null ? String(props.id) : String(idx)" in panel)


def main() -> int:
    console_errors: list[str] = []
    structural_checks()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(viewport={"width": 1366, "height": 900}).new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="load")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(700)

        print("\n== LIVE: editorPois create path through spec.create (before/after) ==")
        # Wait for the seed POI to feed the editor-poi source so the before-count is
        # stable (the seed feeds asynchronously after boot).
        page.wait_for_function(
            """() => {
              const s = window.AOP_HOST_MAP && window.AOP_HOST_MAP.getSource('editor-poi');
              const fc = s && s._data && (s._data.geojson || s._data);
              return fc && fc.features && fc.features.length >= 1;
            }""",
            timeout=10_000,
        )
        before = page.evaluate(
            """() => {
              const s = window.AOP_HOST_MAP.getSource('editor-poi');
              const fc = s._data && (s._data.geojson || s._data);
              return fc && fc.features ? fc.features.length : -1;
            }"""
        )
        # Drive the SAME bridge the panel's "+ POI" commit uses.
        new_id = page.evaluate(
            """() => window.AOP_HOST_CREATE_FEATURE('editorPois',
                   { type: 'Point', coordinates: [-85.7481, 35.0905] }, { category: 'Restroom' })"""
        )
        check("create returned a new feature id (spec.create dispatched)", bool(new_id), str(new_id))
        page.wait_for_timeout(300)
        after = page.evaluate(
            """(id) => {
              const s = window.AOP_HOST_MAP.getSource('editor-poi');
              const fc = s._data && (s._data.geojson || s._data);
              const feats = (fc && fc.features) || [];
              const f = feats.find(x => x.properties && String(x.properties.id) === String(id));
              return { count: feats.length, found: !!f,
                       name: f && f.properties.name, category: f && f.properties.category };
            }""",
            new_id,
        )
        check("the new feature LANDED in the editorPois store (found + count +1)",
              after["found"] and after["count"] == before + 1, f"{before} -> {after['count']}, found={after['found']}")
        check("created feature carries name == category == 'Restroom' (unchanged shape)",
              after["found"] and after["name"] == "Restroom" and after["category"] == "Restroom",
              str(after))

        # Safe default: a layer with no `create` capability returns null (no throw).
        non_creatable = page.evaluate(
            """() => window.AOP_HOST_CREATE_FEATURE('buildings',
                   { type: 'Point', coordinates: [-85.748, 35.090] }, {})"""
        )
        check("a non-creatable layer returns null (safe default, no throw — C1/R13)",
              non_creatable is None, str(non_creatable))

        # Editable exactly as before: edit the created feature through the SAME host
        # bridge the panel's commitChange uses for a hostEdit node
        # (AOP_HOST_SET_FEATURE_PROPS), then re-read the live source — the edit must
        # land on the store. Deterministic (no panel re-seed race: the bridge-created
        # feature shows in the panel only after the panel's own commitFeature
        # re-seeds, which the host-create bridge alone doesn't trigger).
        edited = page.evaluate(
            """(id) => {
              const s = window.AOP_HOST_MAP.getSource('editor-poi');
              const fc = s._data && (s._data.geojson || s._data);
              const f = fc.features.find(x => String(x.properties.id) === String(id));
              if (!f) return null;
              window.AOP_HOST_SET_FEATURE_PROPS('editorPois', f.properties, { name: 'Restroom (renamed)' });
              const fc2 = (window.AOP_HOST_MAP.getSource('editor-poi')._data) ;
              const g = (fc2.geojson || fc2).features.find(x => String(x.properties.id) === String(id));
              return g ? g.properties.name : null;
            }""",
            new_id,
        )
        check("the created feature is EDITABLE through the panel's edit bridge (name edit lands on the store)",
              edited == "Restroom (renamed)", str(edited))

        # And the panel's editorPois Name input is live-editable (the DOM the created
        # POI uses once the panel re-seeds) — proven on the always-present seed POI.
        page.evaluate(
            """() => { const c = document.getElementById('panelCollapse');
                       if (c && c.getAttribute('aria-expanded') === 'false') c.click(); }"""
        )
        page.wait_for_selector('[data-node-id="editorPois"]', state="attached", timeout=8000)
        page.evaluate(
            """() => {
              const grp = document.querySelector('[data-node-id="editorPois"]');
              if (grp && grp.querySelectorAll('.item-select').length === 0) {
                const ch = grp.querySelector('.node-chevron-btn'); if (ch) ch.click();
              }
            }"""
        )
        page.wait_for_timeout(500)
        name_val = page.evaluate(
            """() => {
              const grp = document.querySelector('[data-node-id="editorPois"]');
              const btn = grp && [...grp.querySelectorAll('.item-select')].find(b => b.textContent.includes('Pavilion'));
              if (btn) btn.click();
              const i = document.querySelector('.field-input[data-field="name"]');
              return i ? i.value : null;
            }"""
        )
        check("the panel editorPois Name input is live-editable (seed POI → 'AOP Pavilion')",
              name_val == "AOP Pavilion", str(name_val))

        print("\n== Health ==")
        check("no console errors", len(console_errors) == 0, f"{len(console_errors)}: {console_errors[:3]}")
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
