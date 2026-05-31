from playwright.sync_api import sync_playwright
import numpy as np, os
from PIL import Image
OUT="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/icon_audit/svgs"
os.makedirs(OUT,exist_ok=True)
DSF=6
# selector -> label ; screenshot the <svg> itself so we measure ART, not button bg/borders/dots
sels=[("#zoomRegion svg","z:Region"),("#zoomPark svg","z:Park"),("#zoomPavilion svg","z:Pavilion"),
      ("#presetTopo svg","p:Topo"),("#presetTrace svg","p:Trace"),("#presetSatellite svg","p:Tree"),
      ("#lrTabSearch svg","t:Search"),("#lrTabHot svg","t:Hot"),("#lrTabCal svg","t:Cal"),
      ("#locateBtn svg","u:Locate"),("#pwaInstallBtn svg","u:Install"),(".panel-fab-pencil svg","fab:Pencil")]
def measure(path):
    a=np.asarray(Image.open(path).convert("L"),float)
    bg=np.median(np.concatenate([a[0],a[-1],a[:,0],a[:,-1]]))
    ink=np.abs(a-bg)>60
    ys,xs=np.where(ink)
    if len(xs)==0: return None
    artw=xs.max()-xs.min()+1; arth=ys.max()-ys.min()+1
    art=max(artw,arth)
    runs=[]
    for line in list(ink)+list(ink.T):
        c=0
        for v in line:
            if v:c+=1
            else:
                if c:runs.append(c);c=0
        if c:runs.append(c)
    runs=np.array([r for r in runs if 1<=r<=art*0.5])
    vals,cnts=np.unique(runs,return_counts=True); stroke=float(vals[np.argmax(cnts)])
    rend=a.shape[0]
    return dict(rend=rend, artfrac=art/rend, stroke=stroke, optical=stroke/art)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={"width":1280,"height":900},device_scale_factor=DSF)
    try: pg.goto("http://localhost:8001/index.html",wait_until="domcontentloaded",timeout=15000)
    except Exception as e: print("warn",e)
    pg.wait_for_timeout(1200)
    pg.evaluate("""()=>{const i=document.getElementById('pwaInstallBtn'); if(i){i.hidden=false;i.removeAttribute('hidden');}
      const p=document.querySelector('.panel'); if(p)p.classList.add('collapsed');}""")
    pg.wait_for_timeout(300)
    print(f"{'icon':<12}{'artfill%':>9}{'stroke_px':>10}{'OPTICAL':>9}  (optical=stroke/art; higher=looks fatter)")
    rows=[]
    for sel,lab in sels:
        el=pg.query_selector(sel)
        if not el: print(f"{lab:<12} MISSING ({sel})"); continue
        try:
            f=os.path.join(OUT,lab.replace(':','_')+".png"); el.screenshot(path=f)
        except Exception as e: print(f"{lab:<12} shot-fail {e}"); continue
        m=measure(f)
        if not m: print(f"{lab:<12} no-ink"); continue
        rows.append((lab,m))
    for lab,m in sorted(rows,key=lambda r:r[1]['optical']):
        print(f"{lab:<12}{m['artfrac']*100:>8.0f}%{m['stroke']:>10.1f}{m['optical']:>9.3f}")
    b.close()
