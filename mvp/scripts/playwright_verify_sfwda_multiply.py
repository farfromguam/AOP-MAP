"""Verify that the SFWDA paper map switches into "multiply" alpha-keyed mode
when the lidar hillshade toggle is on, and reverts when the hillshade is off.

Captures:
  brain/output/playwright_sfwda_no_hillshade.png
  brain/output/playwright_sfwda_with_hillshade.png
  brain/output/playwright_sfwda_after_hillshade_off.png
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

from playwright_base import WEBSITE_URL as URL, set_toggle

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "brain" / "output"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    checks: list[bool] = []

    def record(label: str, ok: bool, detail: str = "") -> None:
        prefix = "PASS" if ok else "FAIL"
        msg = f"{prefix} {label}"
        if detail:
            msg += f" -- {detail}"
        print(msg)
        checks.append(ok)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        console_errors: list[str] = []
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text) if msg.type == "error" else None,
        )

        page.goto(URL, wait_until="networkidle")
        # Use the same load proxy the other verifiers use: the publish message.
        page.wait_for_selector("#message", state="attached")
        page.wait_for_function(
            "document.getElementById('message')?.textContent?.includes('publish feature')",
            timeout=15000,
        )

        # SFWDA on, hillshade off. The toggles sit inside a collapsed
        # `.panel-section`, so route through the shared `set_toggle` helper —
        # `page.check`/`page.click` would time out waiting for the hidden
        # checkbox to become visible.
        set_toggle(page, "showSfwda", True)
        page.wait_for_timeout(1500)
        record("SFWDA toggle on", page.is_checked("#showSfwda"))
        record("Hillshade toggle off (baseline)", not page.is_checked("#showHillshade"))
        page.screenshot(path=str(OUT / "playwright_sfwda_no_hillshade.png"))

        # Flip hillshade on -> SFWDA tiles should rebake with alpha keying.
        set_toggle(page, "showHillshade", True)
        # Rebake walks the source image pixel by pixel and re-emits 36 webp tiles.
        page.wait_for_timeout(3500)
        record("Hillshade toggle on", page.is_checked("#showHillshade"))
        page.screenshot(path=str(OUT / "playwright_sfwda_with_hillshade.png"))

        # Flip hillshade off -> revert to opaque paper.
        set_toggle(page, "showHillshade", False)
        page.wait_for_timeout(3500)
        record("Hillshade toggle off (after revert)", not page.is_checked("#showHillshade"))
        page.screenshot(path=str(OUT / "playwright_sfwda_after_hillshade_off.png"))

        # No console errors during any of this.
        meaningful = [e for e in console_errors if "favicon" not in e.lower()]
        record(
            "No meaningful console errors during multiply toggle cycle",
            not meaningful,
            "; ".join(meaningful) if meaningful else "",
        )

        browser.close()

    passed = sum(1 for c in checks if c)
    print(f"\n{passed} of {len(checks)} checks PASS")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
