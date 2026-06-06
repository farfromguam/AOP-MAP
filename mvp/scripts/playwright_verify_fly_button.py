#!/usr/bin/env python3
"""Sprint 05 card 08 DOM-level verification — the one makeFlyButton gesture.

Proves by observation that the centralized makeFlyButton(feature, className)
helper still fires flyToFeature on click. flyToFeature is closure-private but
operates on the closure `map`, which is also exposed as window.AOP_HOST_MAP —
so we wrap that object's camera methods (flyTo + fitBounds, the two flyToFeature
calls), click a REAL fly button, and confirm the camera moved.

Tile-independent: the per-feature list rows (renderFeatureListInto → the
`.feature-fly` button) and the dock head (buildEditDock → the `.dock-ico` 🎯
button) both render headless without a basemap. The third call site
(renderVisitorListGroup → `.vrow-fly`) needs starred features that only
populate at map-load; it is the SAME helper, so the two surfaces exercised here
prove the gesture for all three.
"""
from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]

WRAP_CAMERA = """() => {
  const m = window.AOP_HOST_MAP;
  if (!m) return false;
  window.__flyCalls = 0;
  for (const fn of ['flyTo', 'fitBounds']) {
    const orig = m[fn] ? m[fn].bind(m) : null;
    m[fn] = function (...args) { window.__flyCalls++; try { return orig && orig(...args); } catch (e) { return null; } };
  }
  return true;
}"""


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.goto(viewer_url(), wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        page.evaluate(
            """() => { document.querySelectorAll('.section-toggle').forEach(t => {
                 const s = t.closest('.panel-section'); if (s && s.classList.contains('collapsed')) t.click(); });
               document.querySelectorAll('[data-editor-bucket-body]').forEach(b => { b.hidden = false; }); }"""
        )
        page.wait_for_timeout(300)

        wrapped = page.evaluate(WRAP_CAMERA)
        check("window.AOP_HOST_MAP camera methods wrapped (flyTo/fitBounds)", wrapped)

        n_feature_fly = page.evaluate("() => document.querySelectorAll('.feature-fly').length")
        print(f"  [INFO] {n_feature_fly} .feature-fly buttons rendered headless (renderFeatureListInto)")

        # 1) per-feature list fly button
        page.evaluate("() => { window.__flyCalls = 0; const b = document.querySelector('.feature-fly'); if (b) b.click(); }")
        page.wait_for_timeout(150)
        calls_feature = page.evaluate("() => window.__flyCalls")
        check(".feature-fly click fires flyToFeature (camera moved)", calls_feature and calls_feature > 0, f"camera calls={calls_feature}")

        # 2) dock head fly button (.dock-ico 🎯) — open a dock first
        page.evaluate("() => { const c = document.querySelector('.feature-row-expand'); if (c) c.click(); }")
        page.wait_for_timeout(150)
        n_dock_ico = page.evaluate("() => document.querySelectorAll('#editDock .dock-ico').length")
        print(f"  [INFO] {n_dock_ico} .dock-ico fly button(s) in the open dock head (buildEditDock)")
        page.evaluate("() => { window.__flyCalls = 0; const b = document.querySelector('#editDock .dock-ico'); if (b) b.click(); }")
        page.wait_for_timeout(150)
        calls_dock = page.evaluate("() => window.__flyCalls")
        check(".dock-ico (dock head 🎯) click fires flyToFeature (camera moved)", calls_dock and calls_dock > 0, f"camera calls={calls_dock}")

        check("no console errors during fly-button clicks", not errors, f"errors={errors[:4]}")
        browser.close()

    print("fly-button verification:", "FAIL" if check.failed else "PASS")  # type: ignore[attr-defined]
    sys.exit(1 if check.failed else 0)  # type: ignore[attr-defined]


if __name__ == "__main__":
    main()
