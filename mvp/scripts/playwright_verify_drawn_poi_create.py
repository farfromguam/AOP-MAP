#!/usr/bin/env python3
"""Sprint 09 Slice 2 acceptance — the right panel's CREATE affordance lands a new
drawn POI in the ONE store of record (aop_editor_pois_v1), not the panel OVERRIDES.

Slice 1 restored drawn-POI *editing* over the one store; Slice 2 closes the matching
*create* leak. The panel captures the geometry (its own crosshair place-click) but
commitFeature routes a hostEdit node through window.AOP_HOST_CREATE_FEATURE ->
addDrawnPoi -> editorPois -> aop_editor_pois_v1 (the same builder the host's TerraDraw
`finish` handler uses). Before this fix a panel-created POI persisted to
aop_panel_overrides_v1 (the F6 twin-store desync).

Acceptance (card 09_editor_maturity/editor_completeness.md, Slice 2): create a POI ->
it appears in the restored editor, editable immediately, persisted to
aop_editor_pois_v1; NO twin-store leak; survives reload.

Tile-independent (Witness conditions): wait on AOP_HOST_MAP.loaded() + the editor-poi
source carrying the seed; drive create through the real panel UI; place via map.fire
(no networkidle/queryRenderedFeatures). Serve website/ on :8001.
"""
from __future__ import annotations
import json, sys
from playwright.sync_api import sync_playwright
from playwright_base import viewer_url, viewer_origin

# A seed POI so editor-poi exists + LOADED['editor-poi'] is populated (nodeCanCreate).
SEED = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-85.7479, 35.0905]},
        "properties": {"id": "seed_existing", "name": "Seed POI", "category": "Pavilion",
                       "layer": "editor_poi"}}
PLACE_AT = {"lng": -85.7466, "lat": 35.0888}   # somewhere inside the working envelope


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
        """() => { const s = window.AOP_HOST_MAP.getSource('editor-poi');
                   if (!s || !s.serialize) return false;
                   const d = s.serialize().data;
                   return d && d.features && d.features.some(f => (f.properties||{}).id === 'seed_existing'); }""",
        timeout=25_000)
    page.wait_for_timeout(800)


def store(page):
    """Return the aop_editor_pois_v1 features list (the ONE store of record)."""
    return page.evaluate("""() => {
      const raw = localStorage.getItem('aop_editor_pois_v1'); return raw ? (JSON.parse(raw)||[]) : [];
    }""")


def new_drawn(page):
    """The newest created drawn POI (id 'poi_…'), if any — distinct from the seed."""
    return page.evaluate("""() => {
      const raw = localStorage.getItem('aop_editor_pois_v1'); if (!raw) return null;
      const list = JSON.parse(raw) || [];
      const f = list.filter(x => String((x.properties||x).id||'').startsWith('poi_')).pop();
      return f ? (f.properties || f) : null;
    }""")


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(); page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_origin() + "/")
        page.evaluate("(v) => localStorage.setItem('aop_editor_pois_v1', v)", json.dumps([SEED]))
        page.goto(viewer_url()); boot(page)

        before = store(page)
        check("seeded one store (aop_editor_pois_v1 has the seed)", len(before) == 1)

        # 1) Select the Drawn POIs group → its edit area opens with the + add buttons.
        page.wait_for_selector('[data-node-id="editorPois"]', timeout=15_000)
        page.evaluate("""() => { const b=document.querySelector('[data-node-id="editorPois"] .node-select');
                                 if(b) b.click(); }""")
        page.wait_for_selector('button.add-type', timeout=8_000)
        has_add = page.evaluate("""() => !![...document.querySelectorAll('button.add-type')]
                                   .find(b=>/Add POI/i.test(b.title||''));""")
        check("panel exposes a '+ POI' create affordance on the Drawn POIs node", has_add)

        # 2) Click '+ POI' (startCreate → placing) then place via a map click.
        page.evaluate("""() => { const b=[...document.querySelectorAll('button.add-type')]
                                 .find(x=>/Add POI/i.test(x.title||'')); if(b) b.click(); }""")
        page.wait_for_timeout(300)
        page.evaluate("""(at) => { window.AOP_HOST_MAP.fire('click',
                          { lngLat:{lng:at.lng, lat:at.lat}, point:{x:220, y:220} }); }""", PLACE_AT)
        page.wait_for_timeout(700)

        # 3) The new POI landed in the ONE store (one more row, id 'poi_…').
        after = store(page)
        created = new_drawn(page)
        check("create added a row to the ONE store (aop_editor_pois_v1)", len(after) == len(before) + 1,
              f"before={len(before)} after={len(after)}")
        check("the new POI has a host drawn-POI id (poi_…) + layer editor_poi",
              bool(created) and created.get("layer") == "editor_poi",
              f"created={created}")

        # 4) NO twin-store leak — the panel OVERRIDES store must NOT carry the create.
        leak = page.evaluate("""() => {
          const raw = localStorage.getItem('aop_panel_overrides_v1'); if (!raw) return false;
          const o = JSON.parse(raw) || {};
          const created = o.created || [];
          return created.some(f => { const p=(f.properties||{});
            return String(p.id||'').startsWith('poi_') || p.layer==='editor_poi' || p.layer==='editor_trace'; })
            || Object.keys(o.edits||{}).some(k => k.startsWith('editor-poi:'));
        }""")
        check("NO twin-store leak (aop_panel_overrides_v1 carries no created drawn POI)", leak is False)

        # 5) Editable immediately — create auto-selects the new POI; the takeover
        #    editor opens with its Name field, and a rename persists to the one store.
        name_input = page.evaluate("""() => {
          const inputs=[...document.querySelectorAll('.panel input')].filter(i=>(i.getAttribute('type')||'text')==='text');
          const named=inputs.find(i=>/^other$/i.test((i.value||'').trim()));
          if(!named) return false;
          named.focus(); named.value='Created via panel';
          named.dispatchEvent(new Event('input',{bubbles:true}));
          named.dispatchEvent(new Event('change',{bubbles:true})); named.blur(); return true;
        }""")
        page.wait_for_timeout(500)
        renamed = new_drawn(page)
        check("new POI is editable immediately (Name field open in the editor)", name_input is True)
        check("rename persists to the ONE store (aop_editor_pois_v1.name updated)",
              bool(renamed) and renamed.get("name") == "Created via panel",
              f"name={renamed and renamed.get('name')}")

        # 6) Survives reload (durable in the one store), still no leak.
        new_id = (created or {}).get("id")
        page.reload(); boot(page)
        survived = page.evaluate("""(id) => {
          const raw = localStorage.getItem('aop_editor_pois_v1'); if (!raw) return null;
          const f = (JSON.parse(raw)||[]).find(x => (x.properties||x).id === id);
          return f ? (f.properties||f) : null;
        }""", new_id)
        check("created POI survives reload with its rename",
              bool(survived) and survived.get("name") == "Created via panel",
              f"survived={survived and survived.get('name')}")

        check("no console errors", not errors, "; ".join(errors[:3]))
        b.close()
    if check.failed:
        print("drawn-POI-create verification: FAIL"); return 1
    print("drawn-POI-create verification: PASS"); return 0


if __name__ == "__main__":
    sys.exit(main())
