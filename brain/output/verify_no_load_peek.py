#!/usr/bin/env python3
"""Verify the index page opens at park zoom and HOLDS it on load — no auto-peek
reveal, and no region-wide → park climb. Samples the camera from the first frame the
map exists (an init script + requestAnimationFrame, NO zoom gate) so a slow data load
can't hide an early wide-frame state. Deterministic: the old >12.5 pre-sample gate
raced the load and flapped PASS/FAIL (council Witness, v76); this version has no gate.
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"

# Record (t_ms, zoom) from the moment window.AOPViewer.map appears, every frame.
INIT = """
window.__camlog = [];
(function poll() {
  if (window.AOPViewer && window.AOPViewer.map) {
    var m = window.AOPViewer.map, t0 = performance.now();
    (function tick() {
      window.__camlog.push([Math.round(performance.now() - t0), +m.getZoom().toFixed(3)]);
      requestAnimationFrame(tick);
    })();
    return;
  }
  requestAnimationFrame(poll);
})();
"""

# Known headless-Chromium GL artifacts — intermittent, message-less, and unrelated to
# page logic (they appear only on the software-GL fallback path under load, while the
# camera + band still render correctly). The council Witness (v76 re-review) caught the
# verifier flapping PASS/FAIL purely because these tripped a strict 0-error gate. We
# filter ONLY these; any real page error still fails the run.
GL_NOISE = ("could not compile fragment shader", "could not compile vertex shader",
            "could not link program", "failed to create webgl", "webgl context")

def is_gl_noise(msg):
    m = (msg or "").lower()
    return any(s in m for s in GL_NOISE)

def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1200, "height": 900})
        page = ctx.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.add_init_script(INIT)
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("() => window.__camlog && window.__camlog.length > 0", timeout=20000)
        page.wait_for_timeout(6000)   # outlast the ~4.4s data-load fit
        log = page.evaluate("() => window.__camlog")
        band_layers = page.evaluate(
            "() => window.AOPViewer.map.getStyle().layers.filter(l => l.id.indexOf('band')===0 || l.id.indexOf('art-')===0).length"
        )
        page.screenshot(path="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/no_load_peek_settled.png")
        browser.close()

    zooms = [r[1] for r in log]
    z0, zf = zooms[0], zooms[-1]
    zmin, zmax = min(zooms), max(zooms)
    span = round(zmax - zmin, 3)

    print(f"frames: {len(log)}")
    print(f"open zoom z0={z0}  final zoom={zf}  min/max={zmin}/{zmax}  span={span}")
    print(f"band layers: {band_layers}")
    fatal = [e for e in errors if not is_gl_noise(e)]
    gl_noise = [e for e in errors if is_gl_noise(e)]
    print(f"console errors: {len(errors)} (fatal={len(fatal)}, headless-GL noise filtered={len(gl_noise)})")
    for e in fatal[:10]:
        print("  FATAL:", e)

    # PASS: opens at park zoom (z0 >= 13.9), never moves more than 0.3 zoom across the
    # whole load (no region peek, no 12.5->14 climb), band renders, no *page* error
    # (headless-GL shader-compile flakes are filtered — see GL_NOISE).
    ok = z0 >= 13.9 and span < 0.3 and band_layers >= 30 and len(fatal) == 0
    print("RESULT:", "PASS — opens at park zoom and holds, no load jump" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
