#!/usr/bin/env python3
"""Verify the live viewer ingests the re-imported gold trail network (130 feats,
incl. the 9 new traced trails, the renamed number-first names, and the 67 fix).
Observes the real running system on :8001 — not a re-derived check.
Card: brain/tasks/14_illustrator_trace/satellite_illustrator_export.md
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
GL_NOISE = ("WebGL", "GL_", "shader", "Program", "framebuffer", "texImage",
            "willReadFrequently", "Failed to load resource")


def is_noise(t):
    return any(k.lower() in t.lower() for k in GL_NOISE)


def main():
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_context(viewport={"width": 1200, "height": 900}).new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_function("() => window.AOPViewer && window.AOPViewer.map", timeout=20000)
        # the band streams ~50 layers async (isStyleLoaded stays false); gate on the
        # trail source existing. The viewer loads it by URL, so read the actual served
        # file via fetch() for counts — that IS the bytes the viewer ingested.
        page.wait_for_function(
            "() => { try { return !!window.AOPViewer.map.getSource('aop-trail-network'); }"
            " catch(e) { return false; } }", timeout=25000)
        page.wait_for_timeout(3000)
        info = page.evaluate("""async () => {
            const m = window.AOPViewer.map;
            const d = await (await fetch('data/aop_trail_network.geojson')).json();
            const fs = d.features;
            const names = fs.map(f => f.properties.name);
            // force the trail layer on and frame a new traced trail, then sample pixels
            const trailLayers = m.getStyle().layers.filter(l=>l.id.indexOf('aop-trail-network')===0).map(l=>l.id);
            trailLayers.forEach(id=>{ try{ m.setLayoutProperty(id,'visibility','visible'); }catch(e){} });
            // frame trail 1 (Launchpad) so its composed "<n> name" label paints,
            // to SEE that the number isn't doubled after name normalization.
            const lp = fs.find(f=>f.properties.name==='Launchpad');
            if (lp) { const cs = lp.geometry.coordinates;
                let m1=[180,90], m2=[-180,-90];
                cs.forEach(c=>{m1=[Math.min(m1[0],c[0]),Math.min(m1[1],c[1])];m2=[Math.max(m2[0],c[0]),Math.max(m2[1],c[1])];});
                m.fitBounds([m1,m2],{padding:200,duration:0,maxZoom:17}); }
            await new Promise(r=>setTimeout(r,1500));
            const rendered = m.queryRenderedFeatures({layers: trailLayers.filter(id=>m.getLayer(id))});
            // a name that re-embeds its own trail number would double in the label
            const doubled = fs.filter(f=>{const p=f.properties; const mm=/^(\d+)\s+/.exec(p.name||'');
                return mm && p.trail_number!=null && +mm[1]===p.trail_number;}).map(f=>f.properties.name);
            return {
              total: fs.length,
              named: names.filter(Boolean).length,
              gold: fs.filter(f=>f.properties.maturity==='gold').length,
              newTraced: fs.filter(f=>f.properties.source==='illustrator_trace_new').length,
              hasLaunchpad: names.includes('Launchpad'),
              hasGroundCtl: names.includes('Ground Control'),
              has67: fs.some(f=>f.properties.name==='67' && f.properties.trail_number===67),
              doubledNameTrails: doubled,
              renderedTrailFeatures: rendered.length,
              trailLayers,
            };
        }""")
        page.screenshot(path="/Users/christopherfryman/Documents/code/AOP MAP/brain/output/illustrator_trace/_verify_viewer.png")
        b.close()

    for k, v in info.items():
        print(f"  {k}: {v}")
    fatal = [e for e in errors if not is_noise(e)]
    print(f"  console errors: {len(errors)} (fatal={len(fatal)})")
    for e in fatal[:8]:
        print("   FATAL:", e)
    ok = (info["total"] == 130 and info["newTraced"] == 10 and info["hasLaunchpad"]
          and info["hasGroundCtl"] and info["has67"] and not info["doubledNameTrails"]
          and info["renderedTrailFeatures"] > 0 and not fatal)
    print("RESULT:", "PASS — live viewer ingests the 130-feature network, labels clean, no errors"
          if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
