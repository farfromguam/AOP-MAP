#!/usr/bin/env python3
"""Verify the reorg in EMBED mode (index.html, the real shipping app)."""
import http.server, socketserver, threading, functools, sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/Users/christopherfryman/Documents/code/AOP MAP/website")
PORT = 8141
failed = False
def check(label, ok, detail=""):
    global failed
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not ok: failed = True

# JS errors we care about vs network/tile noise we don't.
NOISE = re.compile(r"(Failed to (load|fetch)|net::|ERR_|tile|raster|terrarium|status of 4|status of 5|favicon)", re.I)

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
        page.add_init_script("delete window.navigator.__proto__.serviceWorker;")
        page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="domcontentloaded")
        # Embedded panel renders into #aopPanelMount once the host map is ready.
        page.wait_for_selector("#aopPanelMount .panel-section .section-label", timeout=25000)
        page.wait_for_timeout(800)

        tree = page.evaluate(r"""() => {
          const out = [];
          for (const sec of document.querySelectorAll('#aopPanelMount .panel-section')) {
            const label = sec.querySelector('.section-label');
            if (!label) continue;
            const nodes = [...sec.querySelectorAll('.node-select .node-label')].map(n => n.textContent.trim());
            out.push({ section: label.textContent.trim(), nodes });
          }
          return out;
        }""")
    sections = [s["section"] for s in tree]
    all_labels = [n for s in tree for n in s["nodes"]]
    print("\nEmbed sections:", sections, "\n")

    check("embed renders 7 sections incl Delete",
          sections == ["Gold data", "Silver — pending review", "Source layers",
                       "Derived layers", "External reference", "User submitted",
                       "Delete — staged for removal"], str(sections))
    check("embed: Map editor GONE", "Map editor" not in sections)
    for gone in ["Points (draw)", "Lines (draw)", "Polygons (draw)", "Drawn POIs"]:
        check(f"embed: '{gone}' gone", gone not in all_labels)
    check("embed: Brand logos present (in Silver)",
          any(l.startswith("Brand logos") for l in [n for s in tree if s["section"].startswith("Silver") for n in s["nodes"]]))
    js_errors = [e for e in errors if not NOISE.search(e)]
    check("0 JS (non-network) console errors", not js_errors, "; ".join(js_errors[:5]))
    if errors and not js_errors:
        print(f"     (ignored {len(errors)} network/tile console msgs)")
finally:
    httpd.shutdown()

print("\nRESULT:", "FAIL" if failed else "PASS")
sys.exit(1 if failed else 0)
