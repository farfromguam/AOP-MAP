from playwright.sync_api import sync_playwright
import numpy as np, os
from PIL import Image
OUT="brain/output/icon_audit/cells"
DSF=5
ids = ["zoomRegion","zoomPark","zoomPavilion","presetPark","presetTopo","presetTrace","presetSatellite",
       "lrTabSearch","lrTabHot","lrTabCal"]
def stroke_px(path):
    im = Image.open(path).convert("L")
    a = np.asarray(im, float)
    h,w = a.shape
    # inset to drop the pill border/divider
    m = int(min(h,w)*0.16)
    a = a[m:h-m, m:w-m]
    # background = median of border ring
    bg = np.median(np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]))
    ink = (np.abs(a-bg) > 60)  # ink = far from bg (works for dark-on-light and light-on-dark)
    runs=[]
    for line in list(ink)+list(ink.T):
        c=0
        for v in line:
            if v: c+=1
            else:
                if c: runs.append(c); c=0
        if c: runs.append(c)
    runs=np.array([r for r in runs if 2<=r<=min(ink.shape)*0.45])
    if len(runs)==0: return None,0
    # mode via histogram of small runs = typical stroke thickness
    vals,counts=np.unique(runs,return_counts=True)
    mode=vals[np.argmax(counts)]
    return float(np.median(runs)), float(mode)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1280,"height":900},device_scale_factor=DSF)
    try: pg.goto("http://localhost:8001/index.html",wait_until="domcontentloaded",timeout=15000)
    except Exception as e: print("warn",e)
    pg.wait_for_timeout(1200)
    print(f"{'icon':<18}{'render_w':>9}{'median_px':>11}{'mode_px':>9}   (all at ~same display size)")
    for i in ids:
        el=pg.query_selector("#"+i)
        if not el: print(f"{i:<18} MISSING"); continue
        f=os.path.join(OUT,i+".png"); el.screenshot(path=f)
        bw=Image.open(f).size[0]
        med,mode=stroke_px(f)
        print(f"{i:<18}{bw:>9}{med:>11.1f}{mode:>9.1f}")
    b.close()
