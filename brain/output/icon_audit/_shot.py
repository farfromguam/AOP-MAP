from playwright.sync_api import sync_playwright
import os
OUT = "brain/output/icon_audit"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":1280,"height":900}, device_scale_factor=3)
    try:
        pg.goto("http://localhost:8001/index.html", wait_until="domcontentloaded", timeout=15000)
    except Exception as e:
        print("goto warn:", e)
    pg.wait_for_timeout(1500)
    def shot(sel, name):
        try:
            el = pg.query_selector(sel)
            if not el: print("MISSING", sel); return
            el.screenshot(path=os.path.join(OUT, name))
            print("ok", name, sel)
        except Exception as e:
            print("shot warn", sel, e)
    shot(".pill-bar", "01_pillbar.png")
    shot(".left-controls", "02_leftrail.png")
    # force hot control + hot-now state visible for the flame glyph
    pg.evaluate("""() => {
      const hc = document.getElementById('hotControl'); if (hc) hc.hidden = false;
    }""")
    pg.wait_for_timeout(300)
    shot("#hotControl", "03_hotcontrol.png")
    # also a tight shot of just the preset group (buttons 4-7 incl my tree)
    shot(".preset-bar", "04_presets.png")
    b.close()
print("done")
