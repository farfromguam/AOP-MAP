#!/usr/bin/env python3
"""gMeta verifier (gold slice 6) — the per-feature maturity Tier chip reads the
BAKED feature attribute; the panel-node literal is now only a DEFAULT.

Closes `maturity-tier-derived-from-panel-tree-position` by OBSERVATION (C4,
tile-independent): opens a reference feature's editor in the STANDALONE panel and
reads the rendered Source-tab "Tier" chip from the live DOM.

Two decisive assertions per layer:
  (1) BAKED  — the first feature's served props.maturity equals the file's layer
      tier, and the rendered Tier chip shows that tier (the normal case still works).
  (2) FEATURE-WINS — mutate that feature's props.maturity in window.LOADED to a
      SENTINEL that is NOT the node literal, reopen its editor, and confirm the Tier
      chip shows the SENTINEL. A pre-fix panel.js (nodeMaturity only, the node
      literal `maturity:'gold'/'silver'`) IGNORES props.maturity and would still
      show the node tier — so this assertion would FAIL pre-fix. That is the proof
      the chip is driven by the feature attribute, not the panel-tree position.

DOM flow (no programmatic select API): for each layer, find its node group by
`[data-node-id]`, click the expand chevron, then click the first `.item-select`
row; the Source-tab Tier renders in `.fe-pane[data-pane="source"]`.

NO networkidle / NO queryRenderedFeatures (the 600s-stall traps).

Run (viewer on :8001):  python3 mvp/scripts/playwright_verify_gMeta_maturity.py
"""
from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_origin

STANDALONE_URL = viewer_origin() + "/right_panel.html"
SENTINEL = "reference"            # a real tier value that is NOT 'gold'/'silver'
SENTINEL_LABEL = "Reference"     # MATURITY_LABEL['reference']

# (panel node id, served MapLibre source id, expected baked tier, rendered label)
CASES = [
    ("aopTrails", "aop-trail-network", "gold", "Gold"),
    ("buildings", "fema-buildings", "silver", "Silver"),
    ("visitorContext", "visitor-context", "silver", "Silver"),
]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def set_all_maturity(page, source, value):
    """Read the first feature's served maturity, and (when value is not None) set
    EVERY feature's props.maturity to `value` in window.LOADED (== the panel's module
    LOADED, line 2308). Mutating all features means whichever row the DOM opens (the
    list is sorted by label, line 1319, so the first row != features[0]) carries the
    value. Returns the first feature's maturity AFTER the mutation, or a marker."""
    return page.evaluate(
        """({ src, value }) => {
          const fc = window.LOADED && window.LOADED[src];
          if (!fc || !fc.features || !fc.features.length) return '__no_loaded__';
          for (const f of fc.features) {
            f.properties = f.properties || {};
            if (value !== null) f.properties.maturity = value;
          }
          const m = fc.features[0].properties.maturity;
          return m == null ? null : m;
        }""",
        {"src": source, "value": value},
    )


def open_first_feature_editor(page, node_id):
    """Expand the node group `[data-node-id]` and click its first feature row.
    Returns True if a row was clicked."""
    ok = page.evaluate(
        """(nodeId) => {
          const group = document.querySelector('[data-node-id="' + nodeId + '"]');
          if (!group) return 'no-group';
          const chevron = group.querySelector('.node-chevron-btn');
          if (chevron && chevron.getAttribute('aria-expanded') !== 'true') chevron.click();
          return 'expanded';
        }""",
        node_id,
    )
    if ok != "expanded":
        return ok
    page.wait_for_timeout(150)
    clicked = page.evaluate(
        """(nodeId) => {
          const group = document.querySelector('[data-node-id="' + nodeId + '"]');
          if (!group) return 'no-group';
          const item = group.querySelector('.node-content .item-select')
                    || group.querySelector('.item-select');
          if (!item) return 'no-item';
          item.click();
          return 'clicked';
        }""",
        node_id,
    )
    page.wait_for_timeout(200)
    return clicked


def read_tier_from_dom(page):
    """Read the Source-tab Tier chip value from the open feature editor (DOM)."""
    return page.evaluate(
        """() => {
          const pane = document.querySelector('.fe-pane[data-pane="source"]')
                    || document.querySelector('[data-pane="source"]');
          if (!pane) return null;
          for (const f of pane.querySelectorAll('.field')) {
            const lab = f.querySelector('.field-label');
            const val = f.querySelector('.field-value');
            if (lab && val && lab.textContent.trim() === 'Tier') return val.textContent.trim();
          }
          return null;
        }"""
    )


def close_editor(page):
    """Return to the tree (click the back control) so the next case starts clean."""
    page.evaluate(
        """() => {
          const back = document.querySelector('.fe-back, .panel-back, [data-action="back"]');
          if (back) back.click();
        }"""
    )
    page.wait_for_timeout(120)


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        # Bypass the service worker so we always read the on-disk panel.js (a stale
        # cached asset would mask the fix). Same guard the gB verifier uses.
        page.add_init_script("delete window.navigator.__proto__.serviceWorker;")
        page.goto(STANDALONE_URL)
        page.wait_for_function("window.__panelReady === true", timeout=60000)

        for node_id, source, baked_tier, baked_label in CASES:
            # ---- (1) BAKED: open a feature unmutated, read its Tier ----
            served = set_all_maturity(page, source, None)
            if served == "__no_loaded__":
                check(f"[{node_id}] LOADED[{source}] present", False, "no loaded data")
                continue
            check(f"[{node_id}] features carry a baked maturity attr",
                  served == baked_tier, f"served maturity={served!r} (expected {baked_tier!r})")
            opened = open_first_feature_editor(page, node_id)
            check(f"[{node_id}] feature editor opened", opened == "clicked", f"open={opened!r}")
            tier = read_tier_from_dom(page)
            check(f"[{node_id}] Tier chip renders the baked tier ({baked_label})",
                  tier is not None and tier.startswith(baked_label),
                  f"rendered Tier={tier!r}")
            close_editor(page)

            # ---- (2) FEATURE-WINS: set EVERY feature's maturity to the sentinel,
            #         reopen any feature, read Tier. The sorted list (line 1319) makes
            #         the first row != features[0], so all-features mutation is what
            #         guarantees the opened row carries the sentinel. ----
            served2 = set_all_maturity(page, source, SENTINEL)
            check(f"[{node_id}] features' props.maturity mutated to '{SENTINEL}'",
                  served2 == SENTINEL, f"served maturity={served2!r}")
            opened2 = open_first_feature_editor(page, node_id)
            check(f"[{node_id}] feature editor reopened after mutation", opened2 == "clicked",
                  f"open={opened2!r}")
            tier2 = read_tier_from_dom(page)
            check(f"[{node_id}] Tier chip FOLLOWS props.maturity (feature wins over node literal '{baked_label}')",
                  tier2 is not None and tier2.startswith(SENTINEL_LABEL),
                  f"rendered Tier={tier2!r} — a pre-fix panel.js would show {baked_label!r}")
            close_editor(page)

        check("0 console / page errors", not errors, "; ".join(errors[:5]))
        browser.close()

    if check.failed:  # type: ignore[attr-defined]
        print("\ngMeta-maturity verification: FAIL")
        return 1
    print("\ngMeta-maturity verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
