#!/usr/bin/env python3
"""Observe the collapsed edit-panel pencil FAB through a map-click selection.

Reproduces (and, after the fix, guards) the bug where the edit pencil
disappears: clicking a map feature while the right edit panel is COLLAPSED
makes panel.js add `.aop-feature-editing` (the feature-editor takeover) without
expanding the panel. The takeover CSS (`panel-embed.css`) hides `.panel-header`
with `display:none !important`, and the pencil FAB lives inside that header — so
the collapsed 56px FAB becomes an empty rust circle with no pencil and no way
back into the editor.

Drives the REAL `map.on('click')` → `revealAtPoint` path (not a forced class)
and reads the rendered pencil's box, so this is observation, not re-derivation.

Run against a viewer served on 8001 (see brain/spinup/mvp_runbook.md):
    cd website && python3 -m http.server 8001
    python3 mvp/scripts/playwright_verify_collapsed_fab_pencil.py
"""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


# Pencil is "visible" only if its own box has size AND it has an offsetParent
# (null when any ancestor is display:none — exactly the bug: a display:none
# .panel-header zeroes the child even though .panel.collapsed says display:grid).
PENCIL_STATE_JS = """
() => {
  const panel = document.querySelector('.panel');
  const pencil = document.querySelector('.panel-fab-pencil');
  if (!panel || !pencil) return { found: false };
  const r = pencil.getBoundingClientRect();
  const cs = getComputedStyle(pencil);
  return {
    found: true,
    collapsed: panel.classList.contains('collapsed'),
    editing: panel.classList.contains('aop-feature-editing'),
    headerDisplay: getComputedStyle(document.getElementById('panelHeader')).display,
    pencilDisplay: cs.display,
    hasOffsetParent: pencil.offsetParent !== null,
    boxW: Math.round(r.width),
    boxH: Math.round(r.height),
    visible: pencil.offsetParent !== null && r.width > 0 && r.height > 0,
  };
}
"""

# For each reveal-eligible layer (a panel node with both `items` and `mapLayers`,
# the set revealAtPoint() clicks against), return ONE viewport pixel on a rendered
# feature so page.mouse.click drives the real handler. One candidate per layer so
# we can find which layers strand the user (panel.js selects but nothing expands).
FIND_FEATURES_JS = """
() => {
  const map = window.AOP_HOST_MAP;
  const model = window.PANEL_MODEL;
  if (!map || !model) return [];
  const layerIds = [];
  const walk = (n) => {
    if (n.items && n.mapLayers) layerIds.push(...n.mapLayers);
    (n.children || []).forEach(walk);
  };
  for (const s of model.sections) for (const n of s.nodes) walk(n);
  const coordOf = (g) => {
    if (g.type === 'Point') return g.coordinates;
    if (g.type === 'LineString') return g.coordinates[Math.floor(g.coordinates.length / 2)];
    if (g.type === 'MultiLineString') return g.coordinates[0][Math.floor(g.coordinates[0].length / 2)];
    if (g.type === 'Polygon') return g.coordinates[0][0];
    if (g.type === 'MultiPolygon') return g.coordinates[0][0][0];
    return null;
  };
  const out = [];
  const seen = new Set();
  for (const id of layerIds) {
    if (seen.has(id) || !map.getLayer(id)) continue;
    if ((map.getLayoutProperty(id, 'visibility') || 'visible') === 'none') continue;
    seen.add(id);
    const feats = map.queryRenderedFeatures({ layers: [id] });
    for (const f of feats) {
      const c = coordOf(f.geometry);
      if (!c) continue;
      const p = map.project(c);
      if (p.x > 360 && p.x < 1240 && p.y > 40 && p.y < 760) {  // clear of left/right chrome
        out.push({ x: p.x, y: p.y, layer: id, gtype: f.geometry.type });
        break;
      }
    }
  }
  return out;
}
"""


def boot(page) -> None:
    page.wait_for_function("() => window.__panelReady === true", timeout=20_000)
    page.wait_for_function(
        "() => window.AOP_HOST_MAP && window.AOP_HOST_MAP.isStyleLoaded()", timeout=20_000
    )
    page.wait_for_timeout(1200)  # let gold layers paint so they are queryable


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        url = viewer_url()
        print(f"Opening {url}")
        page.goto(url, wait_until="load")
        boot(page)

        print("\n== Initial state (panel ships collapsed) ==")
        before = page.evaluate(PENCIL_STATE_JS)
        print(f"  {before}")
        check("pencil FAB found in DOM", before.get("found", False))
        check("panel starts collapsed", before.get("collapsed", False))
        check("pencil FAB visible at start", before.get("visible", False))

        candidates = page.evaluate(FIND_FEATURES_JS)
        if not candidates:
            check("found reveal-eligible rendered features to click", False,
                  "no feature rendered in the clickable area")
            browser.close()
            return 1
        print(f"\n== Clicking {len(candidates)} reveal-eligible layers, each from a "
              f"fresh (collapsed) reload ==")

        stranded_layers: list[str] = []
        for c in candidates:
            page.goto(url, wait_until="load")   # reset: panel collapsed, selection cleared
            boot(page)
            page.mouse.click(c["x"], c["y"])
            page.wait_for_timeout(350)
            st = page.evaluate(PENCIL_STATE_JS)
            if not st.get("editing"):
                print(f"  · {c['layer']:<26} ({c['gtype']}) — no selection (skip)")
                continue
            stranded = st.get("collapsed") and not st.get("visible")
            tag = "STRANDED (pencil hidden)" if stranded else (
                "ok — expanded" if not st.get("collapsed") else "ok — pencil visible")
            print(f"  · {c['layer']:<26} ({c['gtype']}) — collapsed={st.get('collapsed')} "
                  f"editing={st.get('editing')} pencilVisible={st.get('visible')} → {tag}")
            if stranded:
                stranded_layers.append(c["layer"])

        print()
        check("no reveal-eligible layer strands the pencil FAB", not stranded_layers,
              ("BUG reproduced on: " + ", ".join(stranded_layers)) if stranded_layers else "")

        # CSS safety net (independent of the expand behaviour): force the panel
        # into collapsed + aop-feature-editing directly and confirm the pencil
        # still shows, so any future path that lands in that state can't strand.
        print("\n== CSS safety net: forced collapsed + .aop-feature-editing ==")
        page.goto(url, wait_until="load")
        boot(page)
        forced = page.evaluate("""() => {
          const panel = document.querySelector('.panel');
          panel.classList.add('collapsed');
          panel.classList.add('aop-feature-editing');
          const pencil = document.querySelector('.panel-fab-pencil');
          const r = pencil.getBoundingClientRect();
          return { visible: pencil.offsetParent !== null && r.width > 0 && r.height > 0,
                   pencilDisplay: getComputedStyle(pencil).display };
        }""")
        print(f"  {forced}")
        check("pencil FAB stays visible when collapsed + editing", forced.get("visible", False),
              f"pencilDisplay={forced.get('pencilDisplay')}")

        browser.close()

    print("\n" + ("FAILED" if check.failed else "PASSED"))  # type: ignore[attr-defined]
    return 1 if check.failed else 0  # type: ignore[attr-defined]


if __name__ == "__main__":
    sys.exit(main())
