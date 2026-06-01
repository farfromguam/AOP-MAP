#!/usr/bin/env python3
"""Smoke verifier for the app-code-review Group B fixes (H1, M12).

Both are "on-device feel" fixes whose *feel* the user confirms on the iPhone
(per ai_rules/verify_by_observation.md), but the code paths are observable
headlessly — so this proves the mechanism, not just the absence of a parse error.

  H1  SFWDA multiply slider rebake is rAF-coalesced.
      A full rebake calls HTMLCanvasElement.toDataURL 36 times (one per tile).
      We monkey-patch toDataURL to count calls, then:
        - one `input` event  -> ~36 calls   (one bake; the per-bake baseline)
        - a synchronous BURST of N `input` events, measured BEFORE any frame
          -> 0 calls          (proves the rebake is deferred, not synchronous)
        - after one frame     -> ~36 calls  (ONE coalesced bake, NOT N bakes)
      Pre-fix behavior would be N*36 calls fired synchronously inside the burst.

  M12 PWA install button survives a dismissed prompt.
      Simulate Chromium's `beforeinstallprompt`, click the button, resolve
      userChoice as 'dismissed' -> button must STAY visible. Re-arm, resolve
      'accepted' -> button must hide.

Run: serve website/ on :8001 first, then `python3 this_file.py`.  Exit 0 = PASS.
"""
import sys
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8001/index.html?edit=1"


def main():
    errors = []
    results = []

    def record(label, ok, detail=""):
        results.append((label, ok, detail))

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1100, "height": 850})
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(f"PAGEERROR: {exc}"))

        page.goto(BASE, wait_until="domcontentloaded")
        page.wait_for_selector(".maplibregl-canvas", timeout=20000)
        # Let the map load chain finish so sfwdaImageEl is loaded and the install
        # IIFE has attached its listener.
        page.wait_for_timeout(5000)

        record("map canvas present", page.locator(".maplibregl-canvas").count() > 0)

        # --- H1: rAF-coalesced multiply-slider rebake ------------------------
        # Install the toDataURL counter.
        page.evaluate(
            """() => {
                window.__tdCount = 0;
                const proto = HTMLCanvasElement.prototype;
                if (!proto.__patched) {
                    const orig = proto.toDataURL;
                    proto.toDataURL = function (...a) { window.__tdCount++; return orig.apply(this, a); };
                    proto.__patched = true;
                }
            }"""
        )

        def fire_inputs(n, value):
            # Dispatch n synchronous 'input' events on the multiply slider in one
            # tick (no awaits between them) — mimics a drag's event storm.
            return page.evaluate(
                """({n, value}) => {
                    const s = document.getElementById('sfwdaMultiply');
                    window.__tdCount = 0;
                    for (let i = 0; i < n; i++) {
                        s.value = String(value + (i % 5));   // vary so it's not a no-op
                        s.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                    // Count BEFORE any animation frame has run.
                    return window.__tdCount;
                }""",
                {"n": n, "value": value},
            )

        # Baseline: one input -> one coalesced bake after a frame.
        fire_inputs(1, 30)
        page.wait_for_timeout(600)
        per_bake = page.evaluate("() => window.__tdCount")
        record("single slider input bakes once (toDataURL>0)", per_bake > 0,
               f"{per_bake} toDataURL calls")

        if per_bake > 0:
            burst = 12
            sync_count = fire_inputs(burst, 20)
            # Immediately after the synchronous burst, nothing should have baked yet.
            record("burst defers rebake (0 bakes before frame)", sync_count == 0,
                   f"{sync_count} toDataURL calls fired synchronously")
            page.wait_for_timeout(600)
            after = page.evaluate("() => window.__tdCount")
            # Coalesced: ~one bake (per_bake). Pre-fix: ~burst*per_bake.
            bakes = round(after / per_bake) if per_bake else 0
            record(f"{burst} inputs coalesce to one rebake", bakes <= 1,
                   f"{after} toDataURL calls = ~{bakes} bake(s) (expected ~1, pre-fix ~{burst})")
        else:
            record("H1 measurable (sfwda image loaded)", False,
                   "sfwdaImageEl not loaded headlessly — slider bake not observable")

        # --- M12: install button survives a dismissed prompt -----------------
        def simulate_prompt(outcome):
            return page.evaluate(
                """(outcome) => {
                    const btn = document.getElementById('pwaInstallBtn');
                    const ev = new Event('beforeinstallprompt');
                    ev.preventDefault = () => {};
                    ev.prompt = () => {};
                    ev.userChoice = Promise.resolve({ outcome });
                    window.dispatchEvent(ev);
                    return { armedVisible: !btn.hidden };
                }""",
                outcome,
            )

        def click_and_state():
            page.evaluate("() => document.getElementById('pwaInstallBtn').click()")
            page.wait_for_timeout(250)  # let the async userChoice microtask settle
            return page.evaluate("() => !document.getElementById('pwaInstallBtn').hidden")

        armed = simulate_prompt("dismissed")
        record("beforeinstallprompt reveals install button", armed.get("armedVisible") is True)
        visible_after_dismiss = click_and_state()
        record("install button STAYS visible after dismiss (M12)", visible_after_dismiss is True,
               "hidden" if not visible_after_dismiss else "visible")

        simulate_prompt("accepted")
        visible_after_accept = click_and_state()
        record("install button hides after accept", visible_after_accept is False,
               "visible" if visible_after_accept else "hidden")

        browser.close()

    print("\n=== code-review Group B smoke (H1, M12) ===")
    all_ok = True
    for label, ok, detail in results:
        if not ok:
            all_ok = False
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  ({detail})" if detail else ""))

    print(f"\nconsole errors / pageerrors: {len(errors)}")
    for e in errors[:15]:
        print(f"  ! {e}")
    if errors:
        all_ok = False

    print("\nRESULT:", "PASS" if all_ok else "FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
