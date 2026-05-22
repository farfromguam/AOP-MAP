#!/usr/bin/env python3
"""Playwright check for why trails do not appear on the AOP viewer.

Loads http://localhost:8001/, inspects window.map sources/layers, counts
features actually rendered by the publish-trails layer, and dumps a JSON
summary plus a zoomed screenshot to brain/output/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "brain" / "output"
WEBSITE_URL = "http://localhost:8001/"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary: dict = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(viewport={"width": 1280, "height": 800}).new_page()
        console_errors: list[str] = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)

        page.goto(WEBSITE_URL, wait_until="load")
        page.evaluate("window.map = map;")
        page.wait_for_function(
            "() => document.getElementById('message').textContent.includes('publish feature')",
            timeout=15_000,
        )
        page.wait_for_timeout(500)

        summary["message_text"] = page.locator("#message").inner_text()

        summary["publish_source_features"] = page.evaluate(
            """() => {
              const src = window.map.getSource('publish-data');
              if (!src) return null;
              const data = src._data;
              const feats = (data && data.features) || [];
              return feats.map(f => ({
                layer: f.properties && f.properties.layer,
                name:  f.properties && f.properties.name,
                geometry: f.geometry && f.geometry.type
              }));
            }"""
        )

        summary["layers_present"] = page.evaluate(
            """() => ['publish-trails','publish-boundaries','publish-boundary-fill','publish-trailheads']
                 .map(id => ({ id, present: !!window.map.getLayer(id),
                               visibility: window.map.getLayer(id) ? window.map.getLayoutProperty(id,'visibility') || 'visible' : null }))"""
        )

        summary["trails_rendered"] = page.evaluate(
            "() => window.map.queryRenderedFeatures({ layers: ['publish-trails'] }).length"
        )
        summary["boundaries_rendered"] = page.evaluate(
            "() => window.map.queryRenderedFeatures({ layers: ['publish-boundaries'] }).length"
        )
        summary["trailheads_rendered"] = page.evaluate(
            "() => window.map.queryRenderedFeatures({ layers: ['publish-trailheads'] }).length"
        )

        page.screenshot(path=str(OUTPUT_DIR / "playwright_trails_check.png"))
        summary["console_errors"] = console_errors

        browser.close()

    out_path = OUTPUT_DIR / "playwright_trails_check.json"
    out_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"\nScreenshot: {OUTPUT_DIR / 'playwright_trails_check.png'}")
    print(f"Summary:    {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
