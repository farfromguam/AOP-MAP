import sys, time
from playwright.sync_api import sync_playwright

def log(*a): print(*a); sys.stdout.flush()

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_context(viewport={"width": 1280, "height": 800}).new_page()
    pg.goto("http://localhost:8001/index.html", wait_until="load")
    pg.evaluate("window.map=(window.AOPViewer&&window.AOPViewer.map)||window.map;")
    pg.wait_for_function("()=>window.map&&window.map.isStyleLoaded&&window.map.isStyleLoaded()", timeout=20000)
    pg.wait_for_timeout(2500)
    t0 = time.time()
    # SAFE fitBounds — return undefined, do not serialize the Map (the verifier's
    # bug: its arrow returns the Map → circular serialize → hang).
    pg.evaluate("() => { window.map.fitBounds([[-85.782935,35.067164],[-85.717154,35.117928]],{padding:20,duration:0}); }")
    pg.wait_for_timeout(900)
    log("fitBounds+wait: %.1fs" % (time.time() - t0))
    t1 = time.time()
    rendered = pg.evaluate("""() => {
      const c=window.map.getCanvas();
      return window.map.queryRenderedFeatures(
        [[0,0],[c.clientWidth,c.clientHeight]],{layers:['landcover-9patch-forest']}).length;
    }""")
    log("rendered9 count: %d  (query %.1fs)" % (rendered, time.time() - t1))
    t2 = time.time()
    pg.screenshot(path="/tmp/widerender.png")
    log("screenshot: %.1fs" % (time.time() - t2))
    # Now reproduce the verifier's exact (buggy) call with a short timeout to prove the hang.
    try:
        pg.set_default_timeout(8000)
        pg.evaluate("() => window.map.fitBounds([[-85.782935,35.067164],[-85.717154,35.117928]],{padding:20,duration:0})")
        log("BUGGY return-the-map evaluate: returned OK (no hang)")
    except Exception as e:
        log("BUGGY return-the-map evaluate: raised/timed out -> %s" % str(e)[:120])
    b.close()
log("DONE")
