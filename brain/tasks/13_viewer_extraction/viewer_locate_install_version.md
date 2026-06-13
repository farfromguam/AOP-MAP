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
