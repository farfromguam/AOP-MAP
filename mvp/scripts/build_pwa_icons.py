#!/usr/bin/env python3
"""Bake the PWA launch icons from the Rock Warblers warbler mark.

White background, brand-blue shape. Source vector lives beside the output at
website/icons/warbler.svg (the bird + rocks + broken ring). The SVG paths carry
no fill, so a single `fill` on the root cascades to every path; the bird's
evenodd holes then read as white line-art against the blue.

Outputs (sizes + manifest/index.html wiring already point at these names):
  icon-192.png            192   purpose any
  icon-512.png            512   purpose any
  apple-touch-icon.png    180   index.html <link rel=apple-touch-icon>
  icon-maskable-512.png   512   purpose maskable (art kept inside the 80% safe zone)

Render is via Playwright/Chromium (the same engine the viewer verifiers use) so
the SVG rasterizes exactly as a browser draws it. Re-run after any logo change.
"""
import pathlib
from playwright.sync_api import sync_playwright

ICONS = pathlib.Path(__file__).resolve().parents[2] / "website" / "icons"
SVG_SRC = ICONS / "warbler.svg"
BRAND_BLUE = "#1668b4"   # sampled from website/assets/branding/rock-warblers.jpg
WHITE = "#ffffff"

# (filename, pixel size, svg-fill fraction of the canvas)
#   any/apple -> 1.0: the mark already carries ~7.5% built-in margin in its viewBox
#   maskable  -> 0.90: shrink so the mark sits inside the central 80% safe zone
SPECS = [
    ("icon-192.png", 192, 1.0),
    ("icon-512.png", 512, 1.0),
    ("apple-touch-icon.png", 180, 1.0),
    ("icon-maskable-512.png", 512, 0.90),
]


def inline_svg() -> str:
    raw = SVG_SRC.read_text()
    # drop the XML prolog / DOCTYPE so it embeds cleanly in HTML
    body = raw[raw.index("<svg"):]
    # cascade the brand fill onto the root <svg style="..."> (paths inherit it)
    needle = 'style="fill-rule:evenodd;'
    return body.replace(needle, f'style="fill:{BRAND_BLUE};fill-rule:evenodd;', 1)


def page_html(svg: str, size: int, frac: float) -> str:
    inner = round(size * frac)
    return (
        f'<!doctype html><html><head><meta charset="utf-8">'
        f'<style>html,body{{margin:0;padding:0}}'
        f'#f{{width:{size}px;height:{size}px;background:{WHITE};'
        f'display:flex;align-items:center;justify-content:center}}'
        f'#m{{width:{inner}px;height:{inner}px}}'
        f'#m svg{{width:100%;height:100%;display:block}}</style></head>'
        f'<body><div id="f"><div id="m">{svg}</div></div></body></html>'
    )


def main() -> None:
    svg = inline_svg()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, size, frac in SPECS:
            page = browser.new_page(device_scale_factor=1,
                                    viewport={"width": size, "height": size})
            page.set_content(page_html(svg, size, frac))
            page.locator("#f").screenshot(path=str(ICONS / name))
            page.close()
            print(f"baked {name}  {size}x{size}  fill={frac}")
        browser.close()


if __name__ == "__main__":
    main()
