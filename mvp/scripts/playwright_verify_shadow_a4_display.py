#!/usr/bin/env python3
"""Shadow-attribute resolution A4 — render-derived display unification.

A4 converges the last render-derived display shadows onto canonical / baked
fields:

  * poi-display-name-three-derivations — one `poiDisplayName` helper (main.js)
    feeds the left list, the edit-dock row, and the panel item; the map-label
    symbol expression mirrors it (coalesce name,category,'POI'). A drawn POI
    shows ONE name on the map, the list, and the panel.
  * seed-poi-kind-is-propernoun-category — the seed POI bakes the controlled
    kind="poi" (Mason safe default: a feature carrying a real `kind` keeps it);
    the proper-noun "Pavilion" rides as a Tier-3 `facets.category`.
  * source-file-shown-as-derived-runtime-value — the re-bake stamps a
    `source_file` provenance attribute; the Source-tab File reads it directly
    and never says "unknown" for a baked feature.
  * publish-confidence-status-off-vocabulary (re-homed A1->A4) — the panel
    confidence/status chips relabel KNOWN source-register values and pass an
    out-of-vocabulary value through as its own label (Mason binding); the raw
    value is untouched.

Everything below is OBSERVED on the live running app (served data, the map
source feature, the rendered POI-tab row, the panel item row + Name input + the
Source-tab static fields) — never a read-site re-derivation. Tile-independent
(no networkidle, no queryRenderedFeatures). Run with a viewer on :8001.
"""

from __future__ import annotations

import os
import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def mason_bake_check() -> None:
    """Observe the SHIPPED bake function: the seed-POI kind strategy defaults to
    'poi' but a feature carrying a real controlled `kind` survives (never coerced
    to 'poi'). This reads the live rebake_canonical.CONFIG, not a re-derivation."""
    print("\n== Mason binding: real class survives, else 'poi' (shipped bake fn) ==")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import rebake_canonical  # noqa: E402  (module import after sys.path tweak)

    kind_fn = rebake_canonical.CONFIG["aop_editor_seed_pois.geojson"]["kind"]
    check("seed POI with no kind defaults to 'poi'", kind_fn({"category": "Pavilion"}) == "poi",
          str(kind_fn({"category": "Pavilion"})))
    check("seed POI carrying a real controlled kind survives (not coerced)",
          kind_fn({"kind": "trailhead", "category": "Pavilion"}) == "trailhead",
          str(kind_fn({"kind": "trailhead", "category": "Pavilion"})))


def open_node(page, node_id: str) -> None:
    page.evaluate(
        """() => { const c = document.getElementById('panelCollapse');
                   if (c && c.getAttribute('aria-expanded') === 'false') c.click(); }"""
    )
    page.wait_for_selector(f'[data-node-id="{node_id}"]', state="attached", timeout=8000)
    # Idempotent expand: click the chevron ONLY when the node has no rows yet, so
    # re-opening an already-open node never toggles it shut (which would leave the
    # previous feature's detail on screen).
    page.evaluate(
        """(nodeId) => {
          const grp = document.querySelector('[data-node-id="' + nodeId + '"]');
          if (grp && grp.querySelectorAll('.item-select').length === 0) {
            const ch = grp.querySelector('.node-chevron-btn'); if (ch) ch.click();
          }
        }""",
        node_id,
    )
    page.wait_for_timeout(400)


def go_back(page) -> None:
    """Return from a feature-detail takeover to the layer tree (the ‹ Layers bar)."""
    page.evaluate("() => { const b = document.querySelector('.fe-back'); if (b) b.click(); }")
    page.wait_for_timeout(400)


def select_row(page, node_id: str, starts_with: str) -> None:
    page.evaluate(
        """({ nodeId, prefix }) => {
          const grp = document.querySelector('[data-node-id="' + nodeId + '"]');
          if (!grp) return;
          const btn = [...grp.querySelectorAll('.item-select')].find(b => b.textContent.trim().startsWith(prefix));
          if (btn) btn.click();
        }""",
        {"nodeId": node_id, "prefix": starts_with},
    )
    page.wait_for_timeout(400)


def static_fields(page) -> dict:
    """All currently-rendered Source/Identify static fields as {label: value}."""
    return page.evaluate(
        """() => {
          const out = {};
          for (const f of document.querySelectorAll('.field-static')) {
            const l = f.querySelector('.field-label'); const v = f.querySelector('.field-value');
            if (l) out[l.textContent.trim()] = v ? v.textContent.trim() : '';
          }
          return out;
        }"""
    )


def main() -> int:
    console_errors: list[str] = []
    mason_bake_check()
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

        # --- Surface 1: served / baked fields ------------------------------------
        data = page.evaluate(
            """async () => {
              const get = async (f) => (await (await fetch('./data/' + f)).json());
              const sp = (await get('aop_editor_seed_pois.geojson')).features[0].properties;
              const bld = (await get('aop_buildings.geojson')).features[0].properties;
              const t1 = (await get('aop_trail_network.geojson')).features
                          .map(f => f.properties).find(p => p.trail_number === 1) || {};
              return {
                seed_kind: sp.kind, seed_cat: (sp.facets || {}).category, seed_file: sp.source_file,
                bld_file: bld.source_file, t1_name: t1.name,
              };
            }"""
        )
        print("\n== Surface 1: baked fields (served) ==")
        check("seed POI kind == 'poi' (controlled class, not the proper noun)",
              data["seed_kind"] == "poi", str(data["seed_kind"]))
        check("seed POI 'Pavilion' rides as facets.category",
              data["seed_cat"] == "Pavilion", str(data["seed_cat"]))
        check("seed POI carries baked source_file", data["seed_file"] == "aop_editor_seed_pois.geojson",
              str(data["seed_file"]))
        check("building carries baked source_file", data["bld_file"] == "aop_buildings.geojson",
              str(data["bld_file"]))
        check("trail #1 still 'Launchpad' (A2 not regressed)", data["t1_name"] == "Launchpad",
              str(data["t1_name"]))

        # --- Surface 2: drawn-POI ONE name across map / list / panel -------------
        print("\n== Surface 2: drawn POI — one name across map / list / panel ==")
        # map: the editor-poi SOURCE feature the label symbol expression reads.
        map_name = page.evaluate(
            """() => {
              const s = window.AOP_HOST_MAP && window.AOP_HOST_MAP.getSource('editor-poi');
              const fc = s && s._data && (s._data.geojson || s._data);
              const f = fc && fc.features && fc.features.find(x => x.properties && x.properties.id === 'aop_seed_pavilion');
              return f ? (f.properties.name || f.properties.category || 'POI') : null;
            }"""
        )
        check("map: editor-poi source feature name == 'AOP Pavilion'",
              map_name == "AOP Pavilion", str(map_name))

        # list: star the seed POI through the host bridge so it surfaces in the
        # left POI tab, whose row name is the collector's listRow.name (poiDisplayName).
        page.evaluate(
            """() => {
              const s = window.AOP_HOST_MAP.getSource('editor-poi');
              const fc = s._data && (s._data.geojson || s._data);
              const f = fc.features.find(x => x.properties.id === 'aop_seed_pavilion');
              if (f) window.AOP_HOST_SET_HIGHLIGHT('editorPois', f.properties, true);
            }"""
        )
        page.wait_for_timeout(300)
        page.evaluate("() => { const b = document.getElementById('leftTabPoi'); if (b) b.click(); }")
        page.wait_for_timeout(500)
        list_name = page.evaluate(
            """() => {
              const rows = [...document.querySelectorAll('#poiList .poi-row-name')].map(n => n.textContent.trim());
              return rows.find(t => t.includes('Pavilion')) || (rows.length ? rows[0] : null);
            }"""
        )
        check("list (left POI tab row) name == 'AOP Pavilion' (poiDisplayName, not 'Pavilion — AOP Pavilion')",
              list_name == "AOP Pavilion", str(list_name))

        # panel: the editorPois node item row + the right-panel Name input value.
        open_node(page, "editorPois")
        panel_row = page.evaluate(
            """() => {
              const grp = document.querySelector('[data-node-id="editorPois"]');
              if (!grp) return null;
              const r = [...grp.querySelectorAll('.item-select')].map(b => b.textContent.trim());
              return r.find(t => t.includes('Pavilion')) || (r.length ? r[0] : null);
            }"""
        )
        check("panel: editorPois item row == 'AOP Pavilion'", panel_row == "AOP Pavilion", str(panel_row))
        select_row(page, "editorPois", "AOP Pavilion")
        name_val = page.evaluate(
            """() => { const i = document.querySelector('.field-input[data-field="name"]'); return i ? i.value : null; }"""
        )
        check("panel: right-panel Name input value == 'AOP Pavilion'", name_val == "AOP Pavilion", str(name_val))
        check("ONE name agrees across map / list / panel-row / Name input",
              map_name == "AOP Pavilion" and list_name == "AOP Pavilion"
              and panel_row == "AOP Pavilion" and name_val == "AOP Pavilion")

        # --- Surface 3: seed POI kind chip + category facet (the selected POI) ----
        print("\n== Surface 3: seed POI kind chip + category facet ==")
        sp_fields = static_fields(page)
        check("panel Kind chip reads 'poi'", sp_fields.get("Kind") == "poi", str(sp_fields.get("Kind")))
        check("panel Details reads the 'Pavilion' category facet",
              sp_fields.get("Details") == "Pavilion", str(sp_fields.get("Details")))

        # --- Surface 4: Source-tab File (baked) + confidence/status relabel -------
        print("\n== Surface 4: Source-tab File + confidence/status display map ==")
        go_back(page)  # leave the editorPois detail takeover, back to the tree
        open_node(page, "buildings")
        select_row(page, "buildings", "Pavilion")
        bf = static_fields(page)
        check("building Pavilion is the selected feature (Kind == 'building')",
              bf.get("Kind") == "building", str(bf.get("Kind")))
        check("Source-tab File reads the baked file (never 'unknown')",
              bf.get("File") == "aop_buildings.geojson", str(bf.get("File")))
        check("Status chip relabels known 'raw context' -> 'Raw context'",
              bf.get("Status") == "Raw context", str(bf.get("Status")))
        check("Confidence chip passes off-vocab 'medium' through (Mason: never dropped/blanked)",
              bf.get("Confidence") == "medium", str(bf.get("Confidence")))

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
