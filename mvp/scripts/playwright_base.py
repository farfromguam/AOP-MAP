"""Shared helpers for the Playwright viewer verifiers.

Pass 3 (code_health_pass.md) extraction: every verifier used to carry its
own copy of `set_toggle`, `layer_visibility`, `rendered_count`, and the
`WEBSITE_URL` env lookup. By Sprint 02 the `set_toggle` implementations
had drifted into two variants (the older `.click()` form silently times
out when a checkbox sits inside a collapsed `.panel-section`), so the
shared file is now the single source of truth.

Import what you need:

    from playwright_base import viewer_url, set_toggle, layer_visibility, rendered_count

Verifiers that do not flip toggles, query layer visibility, or count
rendered features only need to import `viewer_url`.
"""

from __future__ import annotations

import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# Default points at the Playwright-only port from the handoff. The env
# override lets a verifier hit a viewer running on a different port (e.g.
# WEBSITE_URL=http://localhost:8002/ python3 mvp/scripts/playwright_verify_water.py).
WEBSITE_URL = os.environ.get("WEBSITE_URL", "http://localhost:8001/")


def viewer_url(**params: str) -> str:
    """Return the verifier URL, merging optional query params."""
    parts = urlsplit(WEBSITE_URL)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({key: str(value) for key, value in params.items() if value is not None})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def viewer_origin() -> str:
    parts = urlsplit(WEBSITE_URL)
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def set_toggle(page, toggle_id: str, target: bool) -> None:
    """Flip a panel-section checkbox by `id` to the target state.

    Drives `.checked` + a bubbling `change` event directly so the checkbox
    can sit inside a collapsed `.panel-section` (display:none) and still
    fire the same handlers a real click would. The pre-Pass-3 `.click()`
    form would time out waiting for the element to be visible.
    """
    page.evaluate(
        """({ id, target }) => {
          const el = document.getElementById(id);
          if (!el) return;
          if (el.checked !== target) {
            el.checked = target;
            el.dispatchEvent(new Event('change', { bubbles: true }));
          }
        }""",
        {"id": toggle_id, "target": target},
    )
    # MapLibre paint updates are async; let one frame settle before the
    # caller reads visibility / queryRenderedFeatures.
    page.wait_for_timeout(250)


def layer_visibility(page, layer_id: str) -> str | None:
    """Return MapLibre's `visibility` layout property for `layer_id`.

    Yields 'visible' when the layer is rendered (the spec default), the
    explicit value when one is set, or None when the layer is not on the
    map at all.
    """
    return page.evaluate(
        """(id) => {
          if (!window.map || !window.map.getLayer || !window.map.getLayer(id)) return null;
          return window.map.getLayoutProperty(id, 'visibility') || 'visible';
        }""",
        layer_id,
    )


def rendered_count(page, layers: list[str]) -> int:
    """Count features currently rendered across the given layer ids.

    Returns -1 when no listed layer exists on the map (so an assertion
    can distinguish "rendered 0 features" from "asked the wrong layer").
    """
    return page.evaluate(
        """(layers) => {
          if (!window.map || !window.map.queryRenderedFeatures) return -1;
          const present = layers.filter((l) => window.map.getLayer(l));
          if (!present.length) return -1;
          return window.map.queryRenderedFeatures({ layers: present }).length;
        }""",
        layers,
    )


def click_in_section(page, selector: str) -> None:
    """Click `selector`, expanding its containing `.panel-section` first.

    Sprint 02 made panel sections default-collapsed, so a button inside
    one (Place POI, a layer's tune-expand chevron, etc.) is not hit by a
    plain `.click()` until its section is open. Since the v25 full-bleed
    map, a *second* problem also bites: the `position:fixed` #map canvas
    covers the right panel's coordinates in the headless viewport, so even
    a visible button's centre point fails Playwright's hit-test (the canvas
    or the sticky #panelHeader "intercepts pointer events" and the click
    retries until it times out). So this helper opens the section and then
    fires the element's own `click()` via JS — the same dispatch `set_toggle`
    uses, for the same reason. The real click handler still runs; only the
    synthetic-mouse hit-test is bypassed, which is a headless-geometry
    artifact (on device the panel sits above the map), not a product bug.
    """
    page.evaluate(
        """(sel) => {
          const el = document.querySelector(sel);
          if (!el) return;
          const section = el.closest('.panel-section');
          if (section && section.classList.contains('collapsed')) {
            const toggle = section.querySelector('.section-toggle');
            if (toggle) toggle.click();
          }
          el.click();
        }""",
        selector,
    )
    # Let the section-expand + click handlers settle before the caller reads
    # DOM/map state (mirrors set_toggle; the old locator click auto-waited).
    page.wait_for_timeout(150)
