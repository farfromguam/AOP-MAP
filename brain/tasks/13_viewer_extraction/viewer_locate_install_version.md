# Slice 6 — Locate · Install · version (the bottom of the left stack + PWA chrome)

TL;DR:
- Port the last of the left-control stack: the **Locate** float button (drives the hidden MapLibre
  GeolocateControl), the **Install** button + iOS Add-to-Home-Screen hint, and the **version** chip that
  folds into the bottom-left ⓘ. Plus the head PWA meta (manifest, apple-touch-icon) and the
  install/service-worker scripts.
- **Deferred to the swap (slice 7):** adding `viewer.html` + its assets to `sw.js` `SHELL_ASSETS`, the
  `VERSION`/`#appVersion` bump, and the manifest `start_url` — those all still name `index.html`, so they
  reconcile when the viewer BECOMES `index.html`. So slice 6 owes **no version bump** (built alongside).

#aop #sprint #13 #viewer #pwa #locate #install #version #slice

-----

## What to build

**`viewer.html`** — `<head>`: add `<link rel="manifest">` + `apple-touch-icon`. `<body>` (in
`.left-controls`, after the drawer, from `index.html:199-241`): the `.util-locate` button, the
`#pwaInstallBtn` (self-hides until installable), the `#appVersion` chip, the `#pwaIosHint`. Scripts (from
`index.html:562-621`): the install-prompt handler (`beforeinstallprompt` / iOS fallback) and the
service-worker registration (the existing `./sw.js`, idempotent with index's registration; online it
serves the real page).

**`viewer.css`** — the `util-group`/`util-btn`/`util-locate`/`util-install`/`util-version`/`util-ios-hint`
rules + `.attrib-with-version` (the folded ⓘ state) + the top-right geolocate-control hide
(`app.css:209-274`).

**`viewer_core.js`** — port from `main.js`: the `GeolocateControl` (added top-right, hidden by CSS;
`main.js:186-192`), the `locateBtn` wiring (click → `geolocate.trigger()`, lit/dim on
`trackuserlocationstart`/`end`/`error`; `main.js:220-228`), and `foldVersionIntoInfoControl()` that
relocates `#appVersion` into the bottom-left ⓘ (`main.js:173-180`).

## Acceptance

- [x] Locate button renders; clicking it triggers the geolocate control (no console error); it lights when
      tracking. Version chip shows the build and is folded into the ⓘ ("ⓘ v62"). Install button present,
      hidden until installable; iOS hint present. **0 console/page errors**; `index.html` untouched.
- [x] `sw.js`/`#appVersion`/`SHELL_ASSETS` NOT changed (deferred to the swap) → no version bump owed.
- [x] Line-cost recorded.

### Done — 2026-06-13 (verified by observation)

`/tmp/verify_viewer_pwa.py`: **9/9 PASS, 0 console errors** (geolocation granted in the test context). The
version chip is folded into `.maplibregl-ctrl-bottom-left` reading **v62**; clicking **Locate** fires
`geolocate.trigger()` → the button lights + the blue location dot renders (screenshot `viewer_pwa.png`);
the default top-right geolocate control is hidden; **Install** is present + hidden-until-installable; the
iOS hint is present; the **service worker registers**. Files: `viewer.html` +75 (head PWA meta + the
util markup + the install/sw scripts), `viewer.css` +25 (`util-*` + version fold + geolocate hide),
`viewer_core.js` +33 (geolocate control + locate wiring + `foldVersionIntoInfoControl`). `index.html`,
`main.js`, **and `sw.js` untouched → no `#appVersion`/`VERSION` bump owed** (the precache + bump reconcile
at the swap). The viewer reuses the existing `manifest.json` + `./sw.js`; online it serves the real page.

**Deferred to slice 7 (the swap):** `viewer.html` + its assets into `SHELL_ASSETS`, the `VERSION`/
`#appVersion` bump, and the `manifest.json` `start_url` reconciliation — all land when `viewer.html`
becomes `index.html`. Until then offline a viewer navigation falls back to the cached `index.html` shell.

## Verification

- Playwright: load viewer.html → `#locateBtn` exists + click fires without error; `#appVersion` is inside
  `.maplibregl-ctrl-bottom-left` (folded) reading the version; `#pwaInstallBtn` hidden; service worker
  registers (no error). Screenshot the ⓘ + the locate group. 0 console errors.

## Notes

Full PWA coherence (offline-complete viewer, install opens the viewer, precache) lands at the **swap
(slice 7)** when `viewer.html` becomes `index.html` and its assets replace index's in `SHELL_ASSETS` +
the `VERSION`/`#appVersion` bump. Until then: online works; offline a viewer navigation falls back to the
cached `index.html` shell (acceptable, documented). Next: **slice 7 — the swap** (git-gated deletion step).

### Addendum — 2026-06-13 (bottom-left ⓘ: state 2 = combined bubble + longer loading credit)

User: *"our ⓘ callout bottom-left has three states. 1) loading (ⓘ Made by Rock Warblers vXX) 2) loaded (ⓘ)
vXX 3) open. I want the second state to look like the first state. currently it goes from a combined ⓘ
bubble to a separate ⓘ next to a vXX mark. also make the first state a bit longer, right now it's only like
half a second."*

The three states are MapLibre's compact `AttributionControl`: **(1) loading** = `maplibregl-compact-show`
present → one white pill "ⓘ Made by Rock Warblers · vNN"; **(2) loaded** = `-show` removed → bare ⓘ disc with
`#appVersion` ("vNN") rendered as a sibling *outside* the pill (the "separate mark"); **(3) open** = user taps
ⓘ → expanded again. Two fixes, both **viewer-only** (no editor, no data):

- **State 2 → one combined bubble (`viewer.css`).** Let the flex WRAPPER
  (`.maplibregl-ctrl-bottom-left.attrib-with-version`) carry the white `12px` pill background and drop the
  inner compact ⓘ's own background, so a single rounded fill spans the ⓘ + "vNN" → reads as one bubble like
  the loading credit. Scoped to the collapsed state with
  `:has(> .maplibregl-ctrl-attrib.maplibregl-compact:not(.maplibregl-compact-show))` — expanded (loading /
  open) keeps MapLibre's own pill untouched, and the existing `~ .attrib-version{display:none}` still hides
  the label there so they never double up. (`:has()` is iOS-Safari-15.4+/Chromium; graceful fallback = the
  old separate-mark look, no breakage.)
- **State 1 timing — tried longer, REVERTED to quick collapse (`viewer_core.js`).** First attempt held the
  credit up `ATTRIB_CREDIT_DWELL_MS = 2800` after first `sourcedata` so it was readable. User feedback
  (2026-06-13): *"make it not wait anymore, that's worse — I thought the flash would be 'Made by Rock
  Warblers' but it starts with that then gets joined by the other disclaimers overwhelming our simple message,
  then disappears."* Root cause: MapLibre's expanded attribution AGGREGATES every source's `attribution` as
  sources load, so a longer dwell only shows more of that pile-up. Reverted to the original immediate collapse
  on first `sourcedata` — the credit collapses before the layer disclaimers pile on, keeping the brief flash
  clean; the full disclaimers stay behind the ⓘ tap (state 3). A *readable* clean "Made by Rock Warblers"
  credit (branding separated from the source disclaimers) is a still-open design fork, not built here.

**Verified by observation** (`/tmp/shot_attrib.py` + `/tmp/probe_timing.py`, Playwright :8001): state 2 a
single white pill "ⓘ v68" (`brain/output/attrib_after_state2.png`, CSS unchanged by the revert); after the
revert the credit collapses on first `sourcedata` again (no artificial dwell). `node --check` clean,
0 functional console errors (only headless-GPU WebGL noise, outside this diff). Shell changed →
bumped **v67 → v68** (`sw.js` + `#appVersion`); this build carries the state-2 combined bubble + the
schedule-resize restore (the dwell was added then reverted within the same uncommitted v68). **UNCOMMITTED**
(user's git gate).
