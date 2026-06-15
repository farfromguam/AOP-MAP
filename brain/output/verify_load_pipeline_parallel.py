#!/usr/bin/env python3
"""Observe the viewer's data-load pipeline: concurrency + throttled wall-clock.

Loads index.html with the service worker BLOCKED (worst-case first online load,
every /data/ file hits the network) under a fixed simulated latency, then reads
the Resource Timing API to measure:

  * max concurrency  — how many /data/ requests are in flight at once.
                       Serial await chain -> ~1.  Parallel kickoff -> ~all.
  * data span (ms)   — first data request start -> last data response end.
                       This is the latency the user waits through.

Also asserts the map still renders every key layer and logs zero console errors,
so the speedup can't have quietly dropped a layer.

Run the AOP Playwright server first:  cd website && python3 -m http.server 8001
Usage: python3 brain/output/verify_load_pipeline_parallel.py
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"
LATENCY_MS = 120          # simulated per-request RTT (a phone on weak field signal)
THROUGHPUT = 8_000_000    # ~64 Mbps, so transfer time isn't the dominant term

# Layers that must exist once the chain has run (one per served data file in the
# load handler). If parallelizing dropped or mis-ordered a fetch, one goes missing.
REQUIRED_LAYERS = [
    "landcover-9patch-forest",   # gold_aop_landcover_9patch.geojson
    "landcover-forest",          # gold_aop_landcover.geojson
    "activity-hotspots-heat",    # gold_aop_activity_hotspots.geojson
    "streams",                   # gold_aop_water.geojson
    "roads-labels",              # gold_aop_roads.geojson
    "visitor-context-fill",      # gold_aop_visitor_context_callouts.geojson
    "building-footprint-fill",   # gold_aop_buildings.geojson
    "aop-facility-pin",          # buildings -> facility points
    "aop-trail-network",         # gold_aop_trail_network.geojson
    "aop-waypoints",             # gold_aop_waypoints_traced.geojson
    "publish-boundaries",        # gold_publish.geojson
    "event-session-routes",      # aop_event_schedule.json
]

TIMING_JS = r"""
() => {
  const ents = performance.getEntriesByType('resource')
    .filter(e => e.name.includes('/data/') &&
                 (e.name.endsWith('.geojson') || e.name.endsWith('.json')))
    .map(e => ({ name: e.name.split('/data/')[1],
                 start: e.startTime, end: e.responseEnd }));
  if (!ents.length) return { count: 0, maxConcurrency: 0, spanMs: 0, names: [] };
  // Max number of [start,end] intervals overlapping at any instant.
  const evs = [];
  for (const e of ents) { evs.push([e.start, 1]); evs.push([e.end, -1]); }
  evs.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  let cur = 0, max = 0;
  for (const [, d] of evs) { cur += d; if (cur > max) max = cur; }
  const span = Math.max(...ents.map(e => e.end)) - Math.min(...ents.map(e => e.start));
  return { count: ents.length, maxConcurrency: max, spanMs: Math.round(span),
           names: ents.map(e => e.name) };
}
"""


def run():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Block the SW so every /data/ file is a real network fetch (first-load).
        context = browser.new_context(service_workers="block")
        page = context.new_page()
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))

        # Throttle every request with a fixed RTT via CDP.
        client = context.new_cdp_session(page)
        client.send("Network.enable")
        client.send("Network.emulateNetworkConditions", {
            "offline": False, "latency": LATENCY_MS,
            "downloadThroughput": THROUGHPUT, "uploadThroughput": THROUGHPUT,
        })

        page.goto(URL, wait_until="domcontentloaded")
        # The event schedule is the LAST await in the load chain; when its rows
        # replace the spinner, the whole pipeline has resolved.
        page.wait_for_function(
            "() => { const d = document.getElementById('calendarDays');"
            " return d && !d.querySelector('.calendar-loading') && d.children.length > 0; }",
            timeout=30000,
        )

        timing = page.evaluate(TIMING_JS)
        layer_state = page.evaluate(
            "(ids) => { const m = window.AOPViewer && window.AOPViewer.map;"
            " if (!m) return null; const out = {}; for (const id of ids) out[id] = !!m.getLayer(id); return out; }",
            REQUIRED_LAYERS,
        )
        browser.close()

    print(f"\n=== Load pipeline observation (SW blocked, {LATENCY_MS}ms RTT) ===")
    print(f"data files fetched : {timing['count']}")
    print(f"max concurrency    : {timing['maxConcurrency']}  (1 == serial chain)")
    print(f"data span          : {timing['spanMs']} ms  (first start -> last end)")

    checks = []
    checks.append(("data files were fetched", timing["count"] >= 10))
    if layer_state is None:
        checks.append(("AOPViewer.map reachable", False))
    else:
        for lid in REQUIRED_LAYERS:
            checks.append((f"layer present: {lid}", layer_state.get(lid, False)))
    checks.append(("no console errors", len(errors) == 0))

    print("\n--- checks ---")
    passed = 0
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        passed += ok
    if errors:
        print("\nconsole errors:")
        for e in errors:
            print("   ", e)

    total = len(checks)
    print(f"\n{passed}/{total} checks pass")
    return passed == total


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
