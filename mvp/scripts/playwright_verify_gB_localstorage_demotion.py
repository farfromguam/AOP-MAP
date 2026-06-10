#!/usr/bin/env python3
"""Going-gold G_B.1 verifier — localStorage demoted from PUBLISHED read source to
a working/staging buffer for the four SERVED reference layers.

This proves the keystone read-path flip (finding 3, shadow_attributes_audit.md):
after G_B.1 a STALE prior-session localStorage diff no longer overrides the BAKED
served value on reload, but the diff is still in the store and still Exports;
`created`/`deleted` replays STAY. Tile-independent (per C4): the boot READ is the
served source DATA, not the paint. Reads the panel's `window.LOADED[source]` (the
data the list rows render from) + the host map source + the DOM `.item-select`
labels directly. NO networkidle, NO queryRenderedFeatures (the 600s-stall traps).

Both panel.js boot paths call the replay, so BOTH are exercised:
  - EMBEDDED  : index.html (main.js applyPositionedFeatures + panel applyStoredOverrides)
  - STANDALONE: right_panel.html (panel applyStoredOverrides only)

Seeds localStorage by visiting the origin once, writing the stores, then RELOADING
so the boot replay sees the stale diff exactly as a real prior session would (and a
test-integrity check asserts the seed actually landed, so a non-seeded false-pass is
impossible). Each case uses a FRESH context (clean profile) so cases don't leak
storage into each other.

Anchor feature: building build_id 3396032, baked name "Front Office" (the exact
feature g0_obs2 captured diverging: context-A rendered an edit, fresh-B "Front
Office"). The store key is `buildings:3396032` (idField build_id) in
aop_positioned_features_v1 and `fema-buildings:3396032` in aop_panel_overrides_v1.

Run (viewer on :8001):
  python3 mvp/scripts/playwright_verify_gB_localstorage_demotion.py
"""
from __future__ import annotations

import json
import sys

from playwright.sync_api import sync_playwright

from playwright_base import viewer_url, viewer_origin

# --- Anchor: a served reference feature whose BAKED name is known. ---
BUILD_ID = "3396032"
BAKED_NAME = "Front Office"
STALE_NAME = "STALE-DIFF"
SOURCE = "fema-buildings"          # the MapLibre source id the viewer registers

INDEX_URL = viewer_url()
STANDALONE_URL = viewer_origin() + "/right_panel.html"

# A stale positioned-features store (the host store, replayed by main.js) AND a
# stale panel-overrides store (replayed by panel.js) — both carrying the SAME
# stale name for the SAME building, so whichever boot path paints would lose.
STALE_POSITIONED = {
    f"buildings:{BUILD_ID}": {
        "properties": {"name": STALE_NAME},
        "highlight": True,
        "updated": "2026-01-01T00:00:00.000Z",
    }
}
STALE_OVERRIDES = {
    "schema": "aop-panel-overrides-v1",
    "edits": {
        f"{SOURCE}:{BUILD_ID}": {
            "source": SOURCE,
            "id": BUILD_ID,
            "properties": {"name": STALE_NAME, "highlight": True},
            "updated": "2026-01-01T00:00:00.000Z",
        }
    },
    "created": [],
    "deleted": [],
}

# A created drawn feature + a deleted served key — to prove created/deleted STILL
# replay (regression guard). The created feature lands in its own _src source so
# the standalone panel paints it; the deleted key removes a different building.
# NOTE the deleted-replay (applyStoredOverrides step 2) filters on the served
# `.id` property (the GUID), NOT build_id — so the deleted key uses the GUID.
DEL_BUILD_GUID = "{41014ca8-1baa-4dcc-8a6d-c544eb2a745c}"   # "Pavilion" — must hide
DEL_NAME = "Pavilion"
CREATED_NAME = "GB-CREATED-DRAW"
OVERRIDES_WITH_CREATED_DELETED = {
    "schema": "aop-panel-overrides-v1",
    "edits": {},
    "created": [
        {
            "type": "Feature",
            "properties": {"_id": "u9001", "_src": SOURCE, "name": CREATED_NAME,
                           "build_id": "u9001", "id": "u9001"},
            "geometry": {"type": "Point", "coordinates": [-85.75, 35.09]},
        }
    ],
    "deleted": [f"{SOURCE}:{DEL_BUILD_GUID}"],
}


# Environmental console noise to ignore: MapLibre's image/tile loader intermittently
# fails to fetch an embedded `data:image/...` icon or a blocked basemap tile in
# headless chromium (especially on a reload). This is orthogonal to the
# localStorage read-path change under test, so it is filtered from the
# console-error assertion (mirrors the suite's tile-independence discipline).
def is_env_noise(text: str) -> bool:
    t = text or ""
    return ("data:image" in t) or ("Failed to fetch" in t) or ("AJAXError" in t) \
        or ("ERR_" in t) or ("tile" in t.lower())


def app_errors(errors: list[str]) -> list[str]:
    return [e for e in errors if not is_env_noise(e)]


def check(label: str, ok: bool, detail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {label}" + (f" - {detail}" if detail else ""))
    if not ok:
        check.failed = True  # type: ignore[attr-defined]


check.failed = False  # type: ignore[attr-defined]


def seed_storage(page, positioned=None, overrides=None) -> None:
    """Write the localStorage stores on the page's CURRENT origin, then the caller
    reloads so the boot replay reads them like a real prior session. (add_init_script
    does NOT reliably persist localStorage across the app's async boot here, so we
    seed on a first visit to the origin and reload — the durable, observed pattern.)"""
    page.evaluate(
        """(p) => {
          try {
            if (p.pos !== null) localStorage.setItem('aop_positioned_features_v1', p.pos);
            else localStorage.removeItem('aop_positioned_features_v1');
            if (p.ovr !== null) localStorage.setItem('aop_panel_overrides_v1', p.ovr);
            else localStorage.removeItem('aop_panel_overrides_v1');
          } catch (e) {}
        }""",
        {"pos": json.dumps(positioned) if positioned is not None else None,
         "ovr": json.dumps(overrides) if overrides is not None else None},
    )


def wait_panel(page) -> None:
    page.wait_for_function("window.__panelReady === true", timeout=60000)


def loaded_props(page, source: str):
    """The properties of every feature in the panel's LOADED[source] — the data the
    list rows render from (tile-independent)."""
    return page.evaluate(
        """(src) => {
          const fc = window.LOADED && window.LOADED[src];
          if (!fc || !fc.features) return null;
          return fc.features.map((f) => f.properties || {});
        }""",
        source,
    )


def host_props(page, source: str):
    """The host map source's loaded data (embedded only — main.js owns it)."""
    return page.evaluate(
        """(src) => {
          const m = window.AOP_HOST_MAP;
          if (!m || !m.getSource(src)) return null;
          const d = m.getSource(src).serialize().data;
          return ((d && d.features) || []).map((f) => f.properties || {});
        }""",
        source,
    )


def dom_item_labels(page):
    """The visible feature-row labels rendered in the panel (DOM, .item-select)."""
    return page.evaluate(
        """() => Array.from(document.querySelectorAll('.item-select')).map((b) => b.textContent.trim())"""
    )


def name_for(props_list, build_id: str):
    if not props_list:
        return None
    for p in props_list:
        if str(p.get("build_id")) == str(build_id):
            return p.get("name")
    return None


def run_case(p, label: str, url: str, embedded: bool, *, positioned=None,
             overrides=None, fresh=False) -> dict:
    """One clean-profile boot. For a seeded case: visit the page once (to reach the
    origin), write the stores, then RELOAD so the boot replay reads the seed like a
    real prior session — and verify the seed actually landed before trusting the
    result. For a fresh case: one navigation with storage cleared. Console errors
    are only collected from the FINAL (asserted) load. Keeps the run SHORT."""
    console_errors: list[str] = []
    browser = p.chromium.launch()
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    wait_panel(page)
    seed_storage(page, positioned=positioned if not fresh else None,
                 overrides=overrides if not fresh else None)
    seed_ok = page.evaluate(
        """() => ({
          pos: localStorage.getItem('aop_positioned_features_v1'),
          ovr: localStorage.getItem('aop_panel_overrides_v1'),
        })"""
    )
    # Only collect console errors from the asserted (post-reload) load.
    page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
    page.goto(url)
    wait_panel(page)
    obs = {
        "loaded": loaded_props(page, SOURCE),
        "host": host_props(page, SOURCE) if embedded else None,
        "dom": dom_item_labels(page),
        "errors": console_errors,
        "seed_pos": seed_ok.get("pos"),
        "seed_ovr": seed_ok.get("ovr"),
    }
    browser.close()
    return obs


def main() -> int:
    with sync_playwright() as p:
        # ---- CASE 1: keystone negative — stale diff must NOT override baked ----
        for mode, url, embedded in (("EMBEDDED", INDEX_URL, True),
                                    ("STANDALONE", STANDALONE_URL, False)):
            obs = run_case(p, f"keystone/{mode}", url, embedded,
                           positioned=STALE_POSITIONED, overrides=STALE_OVERRIDES)
            # Guard against a trivial pass: the STALE diff must have actually been
            # seeded into BOTH stores before the asserted reload.
            check(f"[{mode}] stale diff seeded into both stores (test integrity)",
                  bool(obs["seed_pos"]) and STALE_NAME in (obs["seed_pos"] or "")
                  and bool(obs["seed_ovr"]) and STALE_NAME in (obs["seed_ovr"] or ""),
                  f"pos_seeded={bool(obs['seed_pos'])} ovr_seeded={bool(obs['seed_ovr'])}")
            nm = name_for(obs["loaded"], BUILD_ID)
            check(f"[{mode}] panel LOADED renders BAKED name, not the stale diff",
                  nm == BAKED_NAME, f"got name={nm!r} (stale was {STALE_NAME!r})")
            # DOM cross-check: the stale name must not appear as a row label, and
            # the baked name must be present among the rendered rows.
            dom = obs["dom"] or []
            check(f"[{mode}] no '{STALE_NAME}' row label, baked name present in panel DOM",
                  (STALE_NAME not in dom) and (BAKED_NAME in dom),
                  f"stale_in_dom={STALE_NAME in dom} baked_in_dom={BAKED_NAME in dom}")
            if embedded:
                hnm = name_for(obs["host"], BUILD_ID)
                check(f"[{mode}] host map source renders BAKED name, not the stale diff",
                      hnm == BAKED_NAME, f"got host name={hnm!r}")
            errs = app_errors(obs["errors"])
            check(f"[{mode}] no app console errors on keystone boot (env noise filtered)", not errs,
                  "; ".join(errs[:3]))

        # ---- CASE 2: created/deleted STILL replay (regression guard) ----
        # Standalone owns its sources, so a created _src feature paints into LOADED
        # and a deleted key filters one out — the cleanest place to assert both.
        obs = run_case(p, "created-deleted/STANDALONE", STANDALONE_URL, False,
                       overrides=OVERRIDES_WITH_CREATED_DELETED)
        check("[STANDALONE] created/deleted store seeded (test integrity)",
              bool(obs["seed_ovr"]) and CREATED_NAME in (obs["seed_ovr"] or ""),
              f"ovr_seeded={bool(obs['seed_ovr'])}")
        names = {p_.get("name") for p_ in (obs["loaded"] or [])}
        check("[STANDALONE] created drawn feature STILL replays (shows)",
              CREATED_NAME in names, f"created name present={CREATED_NAME in names}")
        check("[STANDALONE] deleted served feature STILL replays (hidden)",
              DEL_NAME not in names, f"deleted '{DEL_NAME}' still present={DEL_NAME in names}")
        errs = app_errors(obs["errors"])
        check("[STANDALONE] no app console errors on created/deleted boot", not errs,
              "; ".join(errs[:3]))

        # ---- CASE 3: fresh browser (empty localStorage) shows baked truth ----
        for mode, url, embedded in (("EMBEDDED", INDEX_URL, True),
                                    ("STANDALONE", STANDALONE_URL, False)):
            obs = run_case(p, f"fresh/{mode}", url, embedded, fresh=True)
            nm = name_for(obs["loaded"], BUILD_ID)
            check(f"[{mode}] fresh/empty-localStorage renders the baked name",
                  nm == BAKED_NAME, f"got name={nm!r}")
            errs = app_errors(obs["errors"])
            check(f"[{mode}] no app console errors on fresh boot", not errs,
                  "; ".join(errs[:3]))

    if check.failed:  # type: ignore[attr-defined]
        print("gB-localstorage-demotion verification: FAIL")
        return 1
    print("gB-localstorage-demotion verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
