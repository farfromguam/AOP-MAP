import sys
from playwright.sync_api import sync_playwright

def log(*a):
    print(*a); sys.stdout.flush()

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_context(viewport={"width": 1100, "height": 800}).new_page()
    errs = []
    pg.on("console", lambda m: errs.append(m.type + ":" + m.text[:160]))
    pg.goto("http://localhost:8001/index.html", wait_until="load")
    pg.evaluate("window.map=(window.AOPViewer&&window.AOPViewer.map)||window.map;")
    pg.wait_for_function("()=>window.map&&window.map.isStyleLoaded&&window.map.isStyleLoaded()", timeout=20000)
    pg.wait_for_timeout(2800)
    log("dem source present:", pg.evaluate("()=>!!window.map.getSource('aws-terrain-dem')"))
    log("maxPitch:", pg.evaluate("()=>window.map.transform.maxPitch"))
    pg.evaluate("()=>{ window.map.easeTo({pitch:60,duration:0}); }")
    pg.wait_for_timeout(400)
    log("after DIRECT easeTo pitch:", pg.evaluate("()=>window.map.getPitch()"))
    log("touchPitch enabled:", pg.evaluate("()=>window.map.touchPitch&&window.map.touchPitch.isEnabled()"))
    log("dragRotate enabled:", pg.evaluate("()=>window.map.dragRotate.isEnabled()"))
    pg.evaluate("()=>{ window.map.easeTo({pitch:0,duration:0}); }")
    pg.wait_for_timeout(300)
    pg.evaluate("()=>{const b=document.getElementById('terrainButton'); if(b)b.click();}")
    pg.wait_for_timeout(400)
    log("button t=400 pitch=%.2f terrain=%s" % (pg.evaluate("()=>window.map.getPitch()"), pg.evaluate("()=>!!window.map.getTerrain()")))
    pg.wait_for_timeout(1200)
    log("button t=1600 pitch=%.2f" % pg.evaluate("()=>window.map.getPitch()"))
    pg.wait_for_timeout(1400)
    log("button t=3000 pitch=%.2f" % pg.evaluate("()=>window.map.getPitch()"))
    log("errs:", errs[:6])
    b.close()
