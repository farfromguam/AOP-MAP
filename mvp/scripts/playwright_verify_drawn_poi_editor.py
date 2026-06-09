#!/usr/bin/env python3
"""Sprint 09 Slice 1 acceptance — drawn POIs are visible + editable in the right
panel, persisting to the ONE store of record (aop_editor_pois_v1), no twin-store.

Restores the retired Drawn POIs node (host-bridged: hostEdit:true / hostKey:'editorPois').
A panel edit must route through window.AOP_HOST_* into the host's aop_editor_pois_v1
array (not the panel OVERRIDES), so it survives reload and the map/list stay in sync.

Tile-independent (Witness conditions): wait on AOP_HOST_MAP.loaded() + the editor-poi
source carrying the injected POI; no networkidle/queryRenderedFeatures. Serve website/
on :8001.
"""
from __future__ import annotations
import json, sys
from playwright.sync_api import sync_playwright
from playwright_base import viewer_url, viewer_origin

POI = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [-85.7479, 35.0905]},
       "properties": {"id": "user_launchpad", "name": "Launchpad", "category": "staging",
                      "source": "editor (first-party)", "highlight": True}}


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
                   return d && d.features && d.features.some(f => (f.properties||{}).id === 'user_launchpad'); }""",
        timeout=25_000)
    page.wait_for_timeout(800)


def ls_poi(page, poi_id):
    return page.evaluate("""(id) => {
      const raw = localStorage.getItem('aop_editor_pois_v1'); if (!raw) return null;
      const f = (JSON.parse(raw)||[]).find(x => (x.properties||x).id === id);
      return f ? (f.properties || f) : null;
    }""", poi_id)


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(); page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_origin() + "/")
        page.evaluate("(v) => localStorage.setItem('aop_editor_pois_v1', v)", json.dumps([POI]))
        page.goto(viewer_url()); boot(page)

        # 1) The panel now HAS a Drawn POIs node that lists the drawn POI.
        page.wait_for_selector('[data-node-id="editorPois"]', timeout=15_000)
        check("right panel has a Drawn POIs (editorPois) node", True)

        # 2) Edit THROUGH THE PANEL UI (not the bridge directly): expand the node,
        #    click the item to open the editor, change the name field, commit. The
        #    edit must land in the ONE store (aop_editor_pois_v1) via commitChange ->
        #    AOP_HOST_SET_FEATURE_PROPS -> setFeatureProperty -> saveEditorPois.
        before = ls_poi(page, "user_launchpad")
        page.evaluate("""() => { const n=document.querySelector('[data-node-id="editorPois"]');
                                 const c=n&&n.querySelector('button[aria-expanded]'); if(c)c.click(); }""")
        page.wait_for_selector('[data-node-id="editorPois"] .item-select', timeout=8_000)
        page.evaluate("""() => { const b=[...document.querySelectorAll('[data-node-id="editorPois"] .item-select')]
                                 .find(x=>/Launchpad/.test(x.textContent)); if(b)b.click(); }""")
        page.wait_for_timeout(700)
        ed = page.evaluate("""() => {
          const inputs=[...document.querySelectorAll('.panel input')].filter(i=>(i.getAttribute('type')||'text')==='text');
          const named=inputs.find(i=>/launchpad/i.test(i.value));
          if(!named) return false;
          named.focus(); named.value='Launchpad EDITED';
          named.dispatchEvent(new Event('input',{bubbles:true}));
          named.dispatchEvent(new Event('change',{bubbles:true})); named.blur(); return true;
        }""")
        page.wait_for_timeout(500)
        after = ls_poi(page, "user_launchpad")
        check("panel UI opened the editor for the drawn POI (name field present)", ed is True)
        check("UI edit routed to the ONE store (aop_editor_pois_v1.name updated)",
              bool(after) and after.get("name") == "Launchpad EDITED",
              f"before={before and before.get('name')} after={after and after.get('name')}")

        # 2b) NO twin-store: the edit must NOT also land in the panel OVERRIDES
        #     (aop_panel_overrides_v1). An editor-poi entry there = the F6 desync.
        overrides_leak = page.evaluate("""() => {
          const raw = localStorage.getItem('aop_panel_overrides_v1'); if (!raw) return false;
          const o = JSON.parse(raw) || {}; const edits = o.edits || {};
          return Object.keys(edits).some(k => k.startsWith('editor-poi:')) ||
                 (o.created || []).some(f => ((f.properties||{}).id) === 'user_launchpad');
        }""")
        check("NO twin-store leak (aop_panel_overrides_v1 carries no editor-poi entry)",
              overrides_leak is False)

        # 3) The edit survives reload (durable in the one store).
        page.reload(); boot(page)
        reloaded = ls_poi(page, "user_launchpad")
        check("rename survives reload", bool(reloaded) and reloaded.get("name") == "Launchpad EDITED",
              f"name={reloaded and reloaded.get('name')}")
        # and the panel still lists it (now renamed)
        listed = page.evaluate("""() => {
          const p = document.querySelector('.panel'); return !!(p && p.textContent.includes('Launchpad EDITED'));
        }""")
        check("panel lists the renamed POI after reload", listed)

        # 4) Delete THROUGH THE PANEL UI (the 🗑 Delete action in the editor) —
        #    re-open the editor, click Delete, confirm it leaves the one store.
        page.wait_for_selector('[data-node-id="editorPois"]', timeout=10_000)  # node back after reload
        page.evaluate("""() => { const n=document.querySelector('[data-node-id="editorPois"]');
                                 const c=n&&n.querySelector('button[aria-expanded]');
                                 if(c && c.getAttribute('aria-expanded')!=='true') c.click(); }""")
        page.wait_for_timeout(300)  # let the expand rerender settle
        # state='attached' (not 'visible'): the row is clicked via page.evaluate (DOM
        # .click), which works regardless of a transient post-reload visibility race.
        page.wait_for_selector('[data-node-id="editorPois"] .item-select', timeout=8_000, state='attached')
        page.evaluate("""() => { const b=[...document.querySelectorAll('[data-node-id="editorPois"] .item-select')]
                                 .find(x=>/Launchpad/.test(x.textContent)); if(b)b.click(); }""")
        page.wait_for_timeout(600)
        page.on("dialog", lambda d: d.accept())  # accept any delete confirm
        deleted = page.evaluate("""() => {
          const btn=[...document.querySelectorAll('.panel button')].find(b=>/delete/i.test(b.textContent||''));
          if(!btn) return false; btn.click(); return true;
        }""")
        page.wait_for_timeout(500)
        check("panel UI Delete action present + clicked", deleted is True)
        check("UI delete removes it from the ONE store (aop_editor_pois_v1)",
              ls_poi(page, "user_launchpad") is None)

        check("no console errors", not errors, "; ".join(errors[:3]))
        b.close()
    if check.failed:
        print("drawn-POI-editor verification: FAIL"); return 1
    print("drawn-POI-editor verification: PASS"); return 0


if __name__ == "__main__":
    sys.exit(main())
