#!/usr/bin/env python3
"""DIAGNOSTIC — dump exactly what the left POI list renders, on a CLEAN profile.

The user can't trace what the left POI list shows; it's supposed to be DB +
star attributes but isn't appearing to be. This drives the real viewer in a
fresh context (no localStorage = the production-default a visitor sees), opens
the POI tab, and prints every group + every row + its source chip + star state,
plus the localStorage star store (empty on a clean profile, by design — that is
the point: it shows what is left when per-browser stars are gone).

Reuses the playwright_verify_starred_poi_flip.py wait pattern (LOAD event via
window.AOP_HOST_MAP + the four reference sources carrying data). Tile-independent.

Serve website/ on :8001 first (cd website && python3 -m http.server 8001).
"""
from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url


def main() -> int:
    console_errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()  # fresh context = clean profile, no localStorage
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url())

        page.wait_for_function(
            "() => window.AOP_HOST_MAP && typeof window.AOP_HOST_MAP.loaded === 'function' "
            "&& window.AOP_HOST_MAP.loaded()",
            timeout=25_000,
        )
        page.wait_for_function(
            """() => {
              const m = window.AOP_HOST_MAP; if (!m) return false;
              const ids = ['cemeteries','fema-buildings','visitor-context','aop-trail-network'];
              return ids.every((id) => {
                const s = m.getSource(id);
                if (!s || typeof s.serialize !== 'function') return false;
                const d = s.serialize().data;
                return d && Array.isArray(d.features) && d.features.length > 0;
              });
            }""",
            timeout=25_000,
        )
        page.wait_for_timeout(1200)

        # Open the left POI tab.
        page.evaluate(
            """() => {
              const btn = [...document.querySelectorAll('.left-tab[data-left-tab]')]
                .find((b) => b.dataset.leftTab === 'poi');
              if (btn) btn.click();
            }"""
        )
        page.wait_for_timeout(600)

        dump = page.evaluate(
            """() => {
              const groups = [...document.querySelectorAll('.poi-list-group')].map((g) => {
                const head = g.querySelector('.poi-list-group-head');
                const label = head ? head.firstChild.textContent : g.dataset.groupId;
                const rows = [...g.querySelectorAll('.poi-row')].map((b) => ({
                  id: b.dataset.poiId,
                  name: (b.querySelector('.poi-row-name') || {}).textContent || '',
                  sub: (b.querySelector('.poi-row-subtitle') || {}).textContent || '',
                  meta: (b.querySelector('.poi-row-meta') || {}).textContent || '',
                }));
                return { groupId: g.dataset.groupId, label, count: rows.length, rows };
              });
              // localStorage star stores + drawn POIs, the per-browser sources.
              // For the two STAR stores, surface the actual highlight count (a
              // truncated preview hid the seed POI's highlight:true and made the
              // editor store look unfed — Witness catch, 2026-06-08).
              const ls = {};
              function starCount(raw) {
                if (!raw) return null;
                try {
                  const parsed = JSON.parse(raw);
                  const feats = Array.isArray(parsed) ? parsed
                    : Array.isArray(parsed.features) ? parsed.features : [];
                  const starred = feats.filter((f) => (f.properties || f).highlight === true);
                  return { features: feats.length, starred: starred.length,
                           starredIds: starred.map((f) => (f.properties || f).id) };
                } catch (e) { return { parseError: true }; }
              }
              ls.aop_positioned_features_v1 = { raw: window.localStorage.getItem('aop_positioned_features_v1') };
              ls.aop_editor_pois_v1 = starCount(window.localStorage.getItem('aop_editor_pois_v1'));
              for (const k of ['aop_feature_visibility_v1','aop_feature_tags_v1',
                               'aop_visitor_context_overrides_v1','aop_brand_logo_overrides_v1']) {
                const v = window.localStorage.getItem(k);
                ls[k] = v ? v.slice(0, 200) : null;
              }
              return { groups, ls };
            }"""
        )

        print("=" * 72)
        print("LEFT POI LIST — clean profile (what a fresh visitor / re-set browser sees)")
        print("=" * 72)
        total = 0
        for g in dump["groups"]:
            print(f"\n[{g['groupId']}]  '{g['label']}'  — {g['count']} row(s)")
            for r in g["rows"]:
                total += 1
                print(f"    • {r['name']}   id={r['id']}")
                if r["sub"]:
                    print(f"        sub: {r['sub'][:90]}")
                if r["meta"]:
                    print(f"        meta: {r['meta'][:90]}")
        print(f"\nTOTAL rows rendered: {total}")

        print("\n" + "=" * 72)
        print("PER-BROWSER localStorage stores (empty here = clean profile, by design)")
        print("=" * 72)
        for k, v in dump["ls"].items():
            print(f"  {k}: {v if v not in (None, {}) else '(absent)'}")

        print("\nconsole errors:", console_errors[:5] if console_errors else "none")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
