#!/usr/bin/env python3
"""Regression guard — a LIVE-authored ★ links to the left POI tab, for all four
reference layers, and survives a reload.

This covers the path playwright_verify_starred_poi_flip.py does NOT: that one tests
the CLEAN-PROFILE baked ★ (core.features.attrs.highlight -> served file). This one
tests the author loop in the user's own browser — star a feature, the host's
left-rail POI tab (#poiList, listMode 'starred' since sprint08) must surface it
immediately AND after reload (localStorage durability).

Why it exists: after the sprint08 flip the four reference layers show ONLY ★ rows,
but the live author->link wiring was incomplete — cemeteries' ★ landed on the
deduped parcel twin while the POI collector reads the marker twin, and trails had
no panel->host bridge and no applyPositionedFeatures replay. Both are fixed; this
guards against silent regression.

We drive the host bridge window.AOP_HOST_SET_HIGHLIGHT(layerKey, props, on) — the
exact call js/panel.js's ★ gesture makes for a node with spec.hostKey — using a
real feature pulled from each live source. For trails we pass STAMP-LESS served
props (no __trail_row_id) to prove the host's trailRowId derivation, since the
panel hands over its own served copy without the load-time stamp.

Tile-independent (per playwright_base + the Witness conditions): waits on the map
LOAD event via window.AOP_HOST_MAP and on the four reference sources carrying data;
no networkidle, no queryRenderedFeatures. Serve website/ on :8001.
"""
from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from playwright_base import viewer_url

# host layerKey -> (live source id, POI-tab group id, JS picker predicate)
LAYERS = {
    "buildings":      ("fema-buildings",   "buildings",       "p => p.aop_facility === true"),
    "cemeteries":     ("cemeteries",       "cemeteries",      "p => p.geom_role === 'marker'"),
    "visitorContext": ("visitor-context",  "visitor_support", "p => p.kind !== 'brand_logo'"),
    "trails":         ("aop-trail-network","trails",          "p => p.trail_number != null"),
}

WAIT_LOADED = ("() => window.AOP_HOST_MAP && typeof window.AOP_HOST_MAP.loaded === 'function' "
               "&& window.AOP_HOST_MAP.loaded()")
WAIT_SOURCES = """() => {
  const m = window.AOP_HOST_MAP; if (!m) return false;
  return ['cemeteries','fema-buildings','visitor-context','aop-trail-network'].every(id => {
    const s = m.getSource(id); if (!s || typeof s.serialize !== 'function') return false;
    const d = s.serialize().data; return d && Array.isArray(d.features) && d.features.length > 0;
  });
}"""


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def settle(page) -> None:
    page.wait_for_function(WAIT_LOADED, timeout=25_000)
    page.wait_for_function(WAIT_SOURCES, timeout=25_000)
    page.wait_for_timeout(1200)
    page.evaluate("""() => { const b=[...document.querySelectorAll('.left-tab[data-left-tab]')]
                              .find(x => x.dataset.leftTab === 'poi'); if (b) b.click(); }""")
    page.wait_for_timeout(400)


def group_count(page, gid: str) -> int:
    return page.evaluate(
        """(gid) => { const g = document.querySelector(`.poi-list-group[data-group-id="${gid}"]`);
                      return g ? g.querySelectorAll('.poi-row').length : 0; }""", gid)


def main() -> int:
    console_errors: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context()                 # persists localStorage across the reload
        page = ctx.new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url())
        settle(page)

        check("host ★ bridge present (AOP_HOST_SET_HIGHLIGHT)",
              page.evaluate("() => typeof window.AOP_HOST_SET_HIGHLIGHT") == "function")

        # 1) Each reference layer: a freshly authored ★ surfaces in its POI group live.
        for host_key, (src_id, gid, pred) in LAYERS.items():
            before = group_count(page, gid)
            # Trails: strip __trail_row_id to reproduce the panel's stamp-less props.
            strip = "true" if host_key == "trails" else "false"
            res = page.evaluate(
                """(a) => {
                  const [srcId, predSrc, hostKey, strip] = a;
                  const feats = window.AOP_HOST_MAP.getSource(srcId).serialize().data.features;
                  const f = feats.find(ff => eval(predSrc)(ff.properties || {}));
                  if (!f) return { picked: false };
                  let props = f.properties;
                  if (strip === 'true') { props = Object.assign({}, props); delete props.__trail_row_id; }
                  return { picked: true, ret: window.AOP_HOST_SET_HIGHLIGHT(hostKey, props, true) };
                }""", [src_id, pred, host_key, strip])
            page.wait_for_timeout(300)
            after = group_count(page, gid)
            check(f"{host_key}: live ★ surfaces in POI tab (rows {before} -> {after})",
                  bool(res.get("picked")) and res.get("ret") is True and after > before,
                  f"bridgeReturn={res.get('ret')}")

        # 2) Reload (same context = localStorage survives): the stars must persist.
        page.reload()
        settle(page)
        for host_key, (_src, gid, _pred) in LAYERS.items():
            check(f"{host_key}: ★ survives reload (POI group still populated)",
                  group_count(page, gid) >= 1)

        check("no console errors during live ★ author + reload",
              not console_errors, "; ".join(console_errors[:3]))
        ctx.close()
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("live-star-link verification: FAIL")
        return 1
    print("live-star-link verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
