#!/usr/bin/env python3
"""Smoke verifier for the app-code-review Group B fixes (H1, M12, M5, M4).

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

        # --- M5: visibility toggle updates counts IN PLACE (no subtree rebuild) ---
        # A rendered feature-list group existing at all also confirms M4 (its
        # geojson loaded via the warmed/memoized fetchJson). We tag the rows
        # container + a row with JS-property sentinels (not serialized to
        # innerHTML), toggle a row's visibility checkbox, then re-query: if a full
        # renderFeatureList ran it would wipe innerHTML and the sentinels would be
        # gone. In-place => sentinels survive AND the (captured) count node updates.
        m5 = page.evaluate(
            """() => {
                const groups = [...document.querySelectorAll('.feature-list-group')];
                let groupEl = null, countEl = null;
                for (const g of groups) {
                    const c = g.querySelector('.group-count');
                    const cb = g.querySelector('.feature-row input[type=checkbox]');
                    if (c && cb) { groupEl = g; countEl = c; break; }
                }
                if (!groupEl) return { ok: false, why: 'no rendered feature-list group on load' };
                const rows = groupEl.querySelector('.feature-list-rows') || groupEl;
                const row = groupEl.querySelector('.feature-row');
                rows.__m5probe = 'rows';
                row.__m5probe = 'row';
                const before = countEl.textContent;
                const cb = groupEl.querySelector('.feature-row input[type=checkbox]');
                cb.checked = !cb.checked;
                cb.dispatchEvent(new Event('change', { bubbles: true }));
                const after = countEl.textContent;            // captured node — updated only if in-place
                const rowsAfter = groupEl.querySelector('.feature-list-rows') || groupEl;
                const rowAfter = groupEl.querySelector('.feature-row');
                return {
                    ok: true, before, after,
                    countChanged: before !== after,
                    nodesReused: rowsAfter.__m5probe === 'rows' && !!rowAfter && rowAfter.__m5probe === 'row',
                };
            }"""
        )
        record("M5/M4: feature-list group rendered (geojson loaded)", bool(m5.get("ok")), m5.get("why", ""))
        if m5.get("ok"):
            record("M5: visibility toggle updates the group count", bool(m5.get("countChanged")),
                   f"{m5.get('before')} -> {m5.get('after')}")
            record("M5: rows updated in place, not rebuilt (DOM nodes reused)", bool(m5.get("nodesReused")),
                   f"nodesReused={m5.get('nodesReused')}")

        # --- M13: heavy default-off layers dropped from the install precache -----
        # The change is in the SERVED sw.js precache list; the cache-first /data/
        # fetch handler is unchanged, so the dropped layers still lazy-cache on
        # first view (offline-after-once). We assert the served SW excludes the two
        # heavy layers from precache yet keeps essentials + the /data/ cacheFirst
        # route, and that the SW actually activates at v25 (no parse error, bump took).
        m13 = page.evaluate(
            """async () => {
                const sw = await (await fetch('./sw.js', { cache: 'no-store' })).text();
                // Isolate the DATA_ASSETS precache literal so a URL mentioned in a
                // comment elsewhere can't fool the check.
                const m = sw.match(/const DATA_ASSETS = \\[([\\s\\S]*?)\\];/);
                const precache = m ? m[1] : '';
                const listed = (u) => new RegExp("['\\\"]" + u.replace(/[.]/g, '\\\\.') + "['\\\"]").test(precache);
                let active = null, cacheNames = [];
                try {
                    const reg = await navigator.serviceWorker.ready;
                    active = reg.active && reg.active.state;
                    cacheNames = await caches.keys();
                } catch (e) { active = 'ERR:' + e; }
                return {
                    contoursPrecached: listed('./data/aop_contours.geojson'),
                    synthTracksPrecached: listed('./data/aop_synthetic_activity_tracks.geojson'),
                    publishPrecached: listed('./data/publish.geojson'),
                    landcover9Precached: listed('./data/aop_landcover_9patch.geojson'),
                    dataCacheFirst: /\\/data\\/[\\s\\S]*?cacheFirst\\(request, DATA_CACHE\\)/.test(sw),
                    active, cacheNames,
                };
            }"""
        )
        record("M13: contours NOT in install precache", m13.get("contoursPrecached") is False)
        record("M13: synthetic-activity tracks NOT in install precache", m13.get("synthTracksPrecached") is False)
        record("M13: essentials still precached (publish + default-on landcover-9patch)",
               m13.get("publishPrecached") is True and m13.get("landcover9Precached") is True,
               f"publish={m13.get('publishPrecached')} landcover9={m13.get('landcover9Precached')}")
        record("M13: /data/ still cache-first (dropped layers lazy-cache on first view)",
               m13.get("dataCacheFirst") is True)
        record("M13: SW activates at v26 (bump took, no parse error)",
               m13.get("active") == "activated" and ("aop-data-v26" in (m13.get("cacheNames") or [])),
               f"state={m13.get('active')} caches={m13.get('cacheNames')}")

        browser.close()

    print("\n=== code-review Group B smoke (H1, M12, M5, M4, M13) ===")
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
