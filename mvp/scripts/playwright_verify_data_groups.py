#!/usr/bin/env python3
"""Verify the 2026-06-05 data-group reorganization renders in the live panel.

Serves website/ and loads the standalone right_panel.html (panel.js renders the
whole PANEL_MODEL tree). Asserts every move the user asked for, by observation.
"""
import http.server, socketserver, threading, functools, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/Users/christopherfryman/Documents/code/AOP MAP/website")
PORT = 8139

failed = False
def check(label, ok, detail=""):
    global failed
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok: failed = True

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        errors = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(str(e)))
        # Block the service worker so we always read fresh assets.
        page.add_init_script("delete window.navigator.__proto__.serviceWorker;")
        page.goto(f"http://127.0.0.1:{PORT}/right_panel.html", wait_until="networkidle")
        page.wait_for_selector(".panel-section .section-label", timeout=10000)

        # Read the rendered tree: ordered sections -> their node labels + tiers.
        tree = page.evaluate(r"""() => {
          const out = [];
          for (const sec of document.querySelectorAll('.panel-section')) {
            const label = sec.querySelector('.section-label');
            if (!label) continue;
            const nodes = [];
            for (const n of sec.querySelectorAll('.node-select')) {
              const lab = n.querySelector('.node-label');
              const badge = n.querySelector('.maturity-badge');
              if (lab) nodes.push({ label: lab.textContent.trim(), tier: badge ? badge.textContent.trim() : null });
            }
            out.push({ section: label.textContent.trim(), nodes });
          }
          return out;
        }""")

    sections = [s["section"] for s in tree]
    by_section = {s["section"]: s["nodes"] for s in tree}
    def labels(sec): return [n["label"] for n in by_section.get(sec, [])]
    def tier_of(sec, lab):
        for n in by_section.get(sec, []):
            if n["label"] == lab: return n["tier"]
        return "<absent>"
    all_labels = [n["label"] for s in tree for n in s["nodes"]]

    print("\nRendered sections:", sections, "\n")

    # --- Section set + order -------------------------------------------------
    expected_order = ["Gold data", "Silver — pending review", "Source layers",
                      "Derived layers", "External reference", "User submitted",
                      "Delete — staged for removal"]
    check("section order matches reorg", sections == expected_order, str(sections))
    check("Map editor group is GONE", "Map editor" not in sections)

    # --- Map editor retired: no draw groups / drawn POIs anywhere ------------
    for gone in ["Points (draw)", "Lines (draw)", "Polygons (draw)", "Drawn POIs"]:
        check(f"'{gone}' removed everywhere", gone not in all_labels)

    # --- Brand logos -> Silver ----------------------------------------------
    bl = next((l for l in labels("Silver — pending review") if l.startswith("Brand logos")), None)
    check("Brand logos in Silver", bl is not None)
    if bl: check("Brand logos chip = Silver", tier_of("Silver — pending review", bl) == "Silver",
                 tier_of("Silver — pending review", bl))

    # --- Paper trail map -> Silver ------------------------------------------
    check("SFWDA paper trail map in Silver", "SFWDA paper trail map" in labels("Silver — pending review"))
    check("paper map chip = Silver", tier_of("Silver — pending review", "SFWDA paper trail map") == "Silver")

    # --- Cemeteries -> External reference ------------------------------------
    check("Cemeteries in External reference", "Cemeteries (TN Comptroller)" in labels("External reference"))
    check("Cemeteries NOT in Source layers", "Cemeteries (TN Comptroller)" not in labels("Source layers"))

    # --- Activity hotspots (real) -> Derived ---------------------------------
    check("Activity hotspots in Derived", "Activity hotspots (GPX dwell)" in labels("Derived layers"))
    check("Activity hotspots NOT in User submitted", "Activity hotspots (GPX dwell)" not in labels("User submitted"))

    # --- Delete group members ------------------------------------------------
    dl = labels("Delete — staged for removal")
    for want in ["SFWDA traced trails (extracted)", "Springs & gages (USGS NHD)",
                 "Simulated Saturday activity", "OSM park polygon"]:
        check(f"Delete group has '{want}'", want in dl)
    for n in by_section.get("Delete — staged for removal", []):
        check(f"  chip = Delete for '{n['label']}'", n["tier"] == "Delete", str(n["tier"]))

    # --- Things that moved OUT of External reference -------------------------
    er = labels("External reference")
    for gone in ["Springs & gages (USGS NHD)", "OSM park polygon",
                 "SFWDA paper trail map", "SFWDA traced trails (extracted)"]:
        check(f"External ref no longer has '{gone}'", gone not in er)

    # --- Simulated Saturday out of Derived -----------------------------------
    check("Simulated Saturday NOT in Derived", "Simulated Saturday activity" not in labels("Derived layers"))

    check("0 console / page errors", not errors, "; ".join(errors[:5]))
finally:
    httpd.shutdown()

print("\nRESULT:", "FAIL" if failed else "PASS")
sys.exit(1 if failed else 0)
