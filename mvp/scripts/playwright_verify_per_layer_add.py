#!/usr/bin/env python3
"""Sprint 09 Slice 4 acceptance — the generic draw group (Points/Lines/Polygons,
retired 7cd51fa) is cleanly retired because per-layer "+ add" covers authoring every
geometry type into a REAL (non-empty) source, persisting + editable (Fork #1).

Point is covered by Slices 2/3 (editorPois -> aop_editor_pois_v1; trailheads ->
publish-data). This verifier covers the other two geometry types:
  - LineString authored into aopTrails -> aop-trail-network (real, has trails)
  - Polygon authored into buildings   -> fema-buildings   (real, has buildings)
plus a structural check that the retired generic-draw nodes are absent.

Tile-independent: wait on AOP_HOST_MAP.loaded() + the two sources; drive the real
panel UI ("+ Line"/"+ Polygon" add buttons); place via map.fire click/dblclick.
Serve website/ on :8001.
"""
from __future__ import annotations
import sys
from playwright.sync_api import sync_playwright
from playwright_base import viewer_url, viewer_origin

LINE_PTS = [{"lng": -85.7470, "lat": 35.0900}, {"lng": -85.7455, "lat": 35.0890}]
POLY_PTS = [{"lng": -85.7480, "lat": 35.0905}, {"lng": -85.7465, "lat": 35.0905},
            {"lng": -85.7465, "lat": 35.0892}]


def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True
check.failed = False


def boot(page):
    page.wait_for_function(
        "() => window.AOP_HOST_MAP && window.AOP_HOST_MAP.loaded && window.AOP_HOST_MAP.loaded()",
        timeout=25_000)
    page.wait_for_function(
        """() => { const m=window.AOP_HOST_MAP;
                   return ['aop-trail-network','fema-buildings'].every(s => { const x=m.getSource(s); return x && x.serialize; }); }""",
        timeout=25_000)
    # Wait for the embedded panel itself to have rendered its nodes (a real node
    # present) — otherwise the structural check below is a false pass and the
    # select-click finds nothing.
    page.wait_for_selector('[data-node-id="aopTrails"]', timeout=15_000)
    page.wait_for_timeout(500)


def source_count(page, src):
    return page.evaluate("""(s) => { const x=window.AOP_HOST_MAP.getSource(s); if(!x||!x.serialize) return -1;
        const d=x.serialize().data; return d && d.features ? d.features.length : -1; }""", src)


def click_add(page, node_id, title_prefix):
    page.evaluate("""(nid) => { const b=document.querySelector('[data-node-id="'+nid+'"] .node-select'); if(b) b.click(); }""", node_id)
    page.wait_for_selector(f'[data-node-id="{node_id}"] button.add-type', timeout=8_000)
    return page.evaluate("""(args) => { const [nid,tp]=args;
        const b=[...document.querySelectorAll('[data-node-id="'+nid+'"] button.add-type')].find(x=>(x.title||'').startsWith(tp));
        if(!b) return false; b.click(); return true; }""", [node_id, title_prefix])


def fire(page, kind, pt):
    page.evaluate("""(a) => { const [kind,pt]=a; window.AOP_HOST_MAP.fire(kind,
                      { lngLat:{lng:pt.lng, lat:pt.lat}, point:{x:200, y:200} }); }""", [kind, pt])


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(); page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url()); boot(page)

        # 0) Structural — the panel rendered (real node present) AND the retired
        #    generic-draw nodes are absent from it (not a false pass on an empty panel).
        panel_rendered = page.evaluate("""() => !!document.querySelector('[data-node-id="aopTrails"]')""")
        check("panel rendered (aopTrails node present)", panel_rendered)
        generic = page.evaluate("""() => ['userPoints','userLines','userPolys','points','lines','polygons']
            .filter(id => !!document.querySelector('[data-node-id="'+id+'"]'));""")
        check("retired generic-draw nodes are absent from the panel", generic == [], f"present={generic}")

        # 1) LineString via aopTrails "+ Line" -> aop-trail-network (real source).
        before_l = source_count(page, "aop-trail-network")
        check("aop-trail-network is a real (non-empty) source", before_l > 0, f"count={before_l}")
        clicked = click_add(page, "aopTrails", "Add line")
        check("aopTrails exposes a '+ Line' add control", clicked is True)
        page.wait_for_timeout(250)
        fire(page, "click", LINE_PTS[0]); fire(page, "click", LINE_PTS[1])
        fire(page, "dblclick", LINE_PTS[1])
        page.wait_for_timeout(500)
        after_l = source_count(page, "aop-trail-network")
        check("authoring a Line lands in aop-trail-network (real source)", after_l == before_l + 1,
              f"before={before_l} after={after_l}")
        line_editable = page.evaluate("""() => {
          const inputs=[...document.querySelectorAll('.panel input')].filter(i=>(i.getAttribute('type')||'text')==='text');
          return !!inputs.find(i=>/^New trail/i.test((i.value||'').trim())); }""")
        check("the authored Line is editable (Name field open: 'New trail …')", line_editable)

        # Creating selects the new feature → full-panel takeover editor; return to
        # the layers tree (‹ Layers) before authoring the next geometry.
        page.evaluate("""() => { const b=[...document.querySelectorAll('.panel button')]
            .find(x=>/Layers/.test(x.textContent||'')); if(b) b.click(); }""")
        page.wait_for_selector('[data-node-id="buildings"]', timeout=8_000)

        # 2) Polygon via buildings "+ Polygon" -> fema-buildings (real source).
        before_p = source_count(page, "fema-buildings")
        check("fema-buildings is a real (non-empty) source", before_p > 0, f"count={before_p}")
        clicked = click_add(page, "buildings", "Add polygon")
        check("buildings exposes a '+ Polygon' add control", clicked is True)
        page.wait_for_timeout(250)
        for pt in POLY_PTS:
            fire(page, "click", pt)
        fire(page, "dblclick", POLY_PTS[-1])
        page.wait_for_timeout(500)
        after_p = source_count(page, "fema-buildings")
        check("authoring a Polygon lands in fema-buildings (real source)", after_p == before_p + 1,
              f"before={before_p} after={after_p}")
        poly_editable = page.evaluate("""() => {
          const inputs=[...document.querySelectorAll('.panel input')].filter(i=>(i.getAttribute('type')||'text')==='text');
          return !!inputs.find(i=>/^New building/i.test((i.value||'').trim())); }""")
        check("the authored Polygon is editable (Name field open: 'New building …')", poly_editable)

        check("no console errors", not errors, "; ".join(errors[:3]))
        b.close()
    if check.failed:
        print("per-layer-add verification: FAIL"); return 1
    print("per-layer-add verification: PASS"); return 0


if __name__ == "__main__":
    sys.exit(main())
