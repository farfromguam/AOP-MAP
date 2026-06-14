import sys
from playwright.sync_api import sync_playwright

def log(*a): print(*a); sys.stdout.flush()

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_context(viewport={"width": 1000, "height": 700}, device_scale_factor=2).new_page()
    pg.goto("http://localhost:8001/index.html", wait_until="load")
    pg.evaluate("window.map=(window.AOPViewer&&window.AOPViewer.map)||window.map;")
    pg.wait_for_function("()=>window.map&&window.map.isStyleLoaded&&window.map.isStyleLoaded()", timeout=20000)
    pg.wait_for_timeout(2500)
    # ensure the trail network + labels are visible
    pg.evaluate("()=>{ window.map.setLayoutProperty('aop-trail-network','visibility','visible'); window.map.setLayoutProperty('aop-trail-network-labels','visibility','visible'); }")
    # find the centroid of a known named trail (Launchpad / trail_number 1) and zoom there
    target = pg.evaluate("""() => {
      const feats = window.map.querySourceFeatures('aop-trail-network');
      for (const f of feats) {
        const p = f.properties || {};
        if (String(p.name).toLowerCase().includes('launchpad') || p.trail_number === 1 || p.trail_number === '1') {
          const g = f.geometry;
          const cs = g.type === 'LineString' ? g.coordinates : (g.coordinates[0] || []);
          const mid = cs[Math.floor(cs.length/2)];
          return mid;
        }
      }
      return null;
    }""")
    log("Launchpad mid:", target)
    if target:
        pg.evaluate("(c)=>{ window.map.jumpTo({center:c, zoom:17}); }", target)
    else:
        pg.evaluate("()=>{ window.map.jumpTo({zoom:16.5}); }")
    pg.wait_for_timeout(1500)
    pg.screenshot(path="/tmp/label_zoom.png")
    log("saved /tmp/label_zoom.png")
    b.close()
log("DONE")
