#!/usr/bin/env python3
"""Sprint 09 Slice 3 acceptance — the curated visibility-only `trailheads` layer
(F7) is now spec-complete: an editable feature list, authorable, with safe
key/label fallbacks so an unnamed trailhead still renders a row.

Trailheads is a publishable layer awaiting data — there are 0 trailhead features in
publish.geojson today. Slice 3 gives the panel node `items` (refItems('publish-data',
filter layer==='trailheads', fallbacks)) + create (geom Point, createDefaults stamps
layer:'trailheads' so an authored trailhead round-trips list→map→bake).

Acceptance (card 09_editor_maturity/editor_completeness.md, Slice 3): trailheads
drills to an editable list; a trailhead can be authored/renamed; an unnamed trailhead
still renders a row.

Tile-independent: wait on AOP_HOST_MAP.loaded() + publish-data source; drive the real
panel UI; place via map.fire. The unnamed-fallback case injects an unnamed SERVED
trailhead (no _id, no name) into the publish.geojson response via page.route — that
exercises deriveItems' spec.label path (the fallback this slice adds), not the
user-feature 'Untitled' path. No file mutation. Serve website/ on :8001.
"""
from __future__ import annotations
import json, sys
from playwright.sync_api import sync_playwright
from playwright_base import viewer_url, viewer_origin

# A SERVED unnamed trailhead — no _id (so deriveItems uses the node's spec.label,
# i.e. the fallback this slice adds), no name (so the fallback actually fires).
SERVED_UNNAMED = {"type": "Feature",
                  "geometry": {"type": "Point", "coordinates": [-85.7490, 35.0912]},
                  "properties": {"layer": "trailheads"}}
PLACE_AT = {"lng": -85.7466, "lat": 35.0888}


def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True
check.failed = False


def inject_unnamed_trailhead(route):
    resp = route.fetch()
    try:
        data = resp.json()
        if isinstance(data, dict) and data.get("type") == "FeatureCollection":
            data.setdefault("features", []).append(SERVED_UNNAMED)
        route.fulfill(status=200, content_type="application/json", body=json.dumps(data))
    except Exception:
        route.fulfill(response=resp)


def boot(page):
    page.wait_for_function(
        "() => window.AOP_HOST_MAP && window.AOP_HOST_MAP.loaded && window.AOP_HOST_MAP.loaded()",
        timeout=25_000)
    page.wait_for_function(
        "() => { const s = window.AOP_HOST_MAP.getSource('publish-data'); return !!(s && s.serialize); }",
        timeout=25_000)
    page.wait_for_timeout(800)


def trailheads_in_source(page):
    return page.evaluate("""() => {
      const s = window.AOP_HOST_MAP.getSource('publish-data'); if (!s || !s.serialize) return [];
      const d = s.serialize().data;
      return (d && d.features ? d.features : []).filter(f => (f.properties||{}).layer === 'trailheads')
              .map(f => f.properties);
    }""")


def main():
    errors = []
    with sync_playwright() as p:
        # Block the service worker so the publish.geojson route below actually fires
        # (a registered SW would serve it from cache and bypass page.route).
        b = p.chromium.launch(); ctx = b.new_context(service_workers="block"); page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        import re as _re
        page.route(_re.compile(r"publish\.geojson"), inject_unnamed_trailhead)
        page.goto(viewer_origin() + "/")
        page.goto(viewer_url()); boot(page)

        # 1) The trailheads node is now DRILLABLE (has items → a chevron + count).
        page.wait_for_selector('[data-node-id="trailheads"]', timeout=15_000)
        drillable = page.evaluate("""() => !!document.querySelector('[data-node-id="trailheads"] .node-chevron-btn')""")
        check("trailheads node drills to a feature list (chevron present)", drillable)

        # 2) The injected UNNAMED SERVED trailhead renders a row labeled "Trailhead"
        #    (spec.label fallback, never undefined) — expand the node, read the rows.
        page.evaluate("""() => { const c=document.querySelector('[data-node-id="trailheads"] .node-chevron-btn');
                                 if(c && c.getAttribute('aria-expanded')!=='true') c.click(); }""")
        page.wait_for_timeout(400)
        rows = page.evaluate("""() => [...document.querySelectorAll('[data-node-id="trailheads"] .item-select')]
                                .map(b => (b.textContent||'').trim());""")
        check("unnamed served trailhead renders a row with the fallback label 'Trailhead'",
              any(r == "Trailhead" for r in rows), f"rows={rows}")
        check("no 'undefined' label leaked from a missing name",
              not any("undefined" in r.lower() for r in rows), f"rows={rows}")

        # 3) Author a trailhead through the real UI: select group → "+ trailhead"
        #    (the Point add button) → map click. It must land in publish-data tagged
        #    layer:'trailheads' (createDefaults) so it shows in the list + on the map.
        before = len(trailheads_in_source(page))
        page.evaluate("""() => { const b=document.querySelector('[data-node-id="trailheads"] .node-select');
                                 if(b) b.click(); }""")
        page.wait_for_selector('[data-node-id="trailheads"] button.add-type', timeout=8_000)
        page.evaluate("""() => { const b=[...document.querySelectorAll('[data-node-id="trailheads"] button.add-type')]
                                 .find(x=>/Add POI/i.test(x.title||'')); if(b) b.click(); }""")
        page.wait_for_timeout(300)
        page.evaluate("""(at) => { window.AOP_HOST_MAP.fire('click',
                          { lngLat:{lng:at.lng, lat:at.lat}, point:{x:240, y:240} }); }""", PLACE_AT)
        page.wait_for_timeout(700)
        after = trailheads_in_source(page)
        check("authoring adds a trailhead to publish-data tagged layer:'trailheads'",
              len(after) == before + 1, f"before={before} after={len(after)}")
        authored = next((p for p in after if str(p.get("name", "")).startswith("New trailhead")), None)
        check("the authored trailhead carries a name + layer:'trailheads'",
              bool(authored) and authored.get("layer") == "trailheads",
              f"authored={authored}")

        # 4) The authored trailhead is editable — rename persists onto the feature.
        renamed_ok = page.evaluate("""() => {
          const inputs=[...document.querySelectorAll('.panel input')].filter(i=>(i.getAttribute('type')||'text')==='text');
          const named=inputs.find(i=>/^New trailhead/i.test((i.value||'').trim()));
          if(!named) return false;
          named.focus(); named.value='Main Gate Trailhead';
          named.dispatchEvent(new Event('input',{bubbles:true}));
          named.dispatchEvent(new Event('change',{bubbles:true})); named.blur(); return true;
        }""")
        page.wait_for_timeout(400)
        now = trailheads_in_source(page)
        check("authored trailhead is editable (Name field open)", renamed_ok is True)
        check("rename persists onto the trailhead feature",
              any(p.get("name") == "Main Gate Trailhead" for p in now),
              f"names={[p.get('name') for p in now]}")

        check("no console errors", not errors, "; ".join(errors[:3]))
        b.close()
    if check.failed:
        print("trailheads-editable verification: FAIL"); return 1
    print("trailheads-editable verification: PASS"); return 0


if __name__ == "__main__":
    sys.exit(main())
