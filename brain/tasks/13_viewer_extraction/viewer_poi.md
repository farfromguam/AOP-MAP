# Slice 4 — POI: feature popups (4a) + the ★-destinations directory (4b)

TL;DR:
- **4a (done):** the normalized **feature click popup** — click any curated/published feature → its
  "what is this line, where did it come from?" card (name · blurb/revisit · Kind/Status/Source/Caveat),
  via the **one shared `window.AOPFeatureDisplay`** strategy. This is the northstar's core product test,
  and what slice 1 deferred when it dropped `bindPopup`.
- **4b (deferred):** the **POI-tab directory** in the drawer — `renderPoiTab` + `buildPoiGroups` (the
  `aop_poi_index.json` ↔ feature join) + the ★-curated destinations + `gotoPoi`. A bigger piece; next.

#aop #sprint #13 #viewer #poi #popups #slice

-----

## 4a — feature click popups (shipped)

Instead of porting `main.js`'s per-layer `bindPopup` calls (each with its own `detailRows`), the clean
core uses the **one text strategy** the user mandated (`feature_display.js`,
`normalize_feature_display.md`): a single map-click handler over the interactive layers reads the clicked
feature's props through `window.AOPFeatureDisplay.featureDisplay(props)` and renders
`window.AOPFeatureDisplay.popupHtml(model)`. Branch-free — every feature reads the same fallback chain;
the values live on the baked feature, not in per-layer code.

**Built:** `viewer.html` loads `./js/feature_display.js` before `viewer_core.js`. `viewer.css` carries the
`.poi-tab-popup .poi-popup-*` rules (app.css:748-754). `viewer_core.js` adds `INTERACTIVE_POPUP_LAYERS`
(the carried layers worth a popup) + a `map.on('click')` that queries the topmost rendered interactive
feature and opens the normalized popup (reusing `closeAllMapPopups` / `visibleMapRect` / `panPopupIntoView`
from the schedule slice), plus a `mousemove` pointer-cursor.

### Done — 2026-06-13 (verified by observation)

`/tmp/verify_viewer_popups.py`: **6/6 PASS, 0 console errors.** Click a **visitor callout** → popup with
the `.poi-popup-title` "South Pittsburg / Kimball supply run", the blurb, and the Kind/Status/Source meta
(screenshot `viewer_popup_callout.png`). Click a **building facility** (fresh page, Pavilion zoom →
click) → "Pavilion | Kind building · Status raw context · Source ORNL" — proving the one strategy works
across layers. `viewer_core.js` 2151 → **2187** (+36); `viewer.html` +3; `viewer.css` +8. `index.html`
untouched. (Note: the popup harness needs a fresh page per feature — a second click-interaction on the
same page is eaten by leftover popup/search state; a test artifact, not a viewer bug. MapLibre's
`closeOnClick` closes the popup when a click lands on empty map.)

**Reuse:** `feature_display.js` is loaded as a `<script>` (not re-ported), same as the schedule resolver;
the popup positioning reuses the schedule slice's `closeAllMapPopups`/`visibleMapRect`/`panPopupIntoView`.

## 4b — POI-tab directory (deferred, next)

The drawer's Calendar card has Events + About tabs (slice 3); the **POI** sub-tab is not yet wired. It
needs `fetchPoiIndex` (`aop_poi_index.json`), `buildPoiGroups` (join the index to the loaded layer
features — buildings, trails, cemeteries, visitor support, event anchors, ★-drawn POIs), `renderPoiTab`
(the grouped scrollable list with kind/status chips + revisit flags), and `gotoPoi` (fly + the same
normalized popup). Add the POI `<button>` back to `.left-tabs` and the `poiList` panel. Bigger than 4a;
its own pass.

## Owed / git gate

UNCOMMITTED (the user's gate). `viewer.html` still not in `sw.js` → no `#appVersion` bump owed. Remaining
slate after 4b: Locate / Install / version (slice 6), the swap to `index.html` (slice 7).
