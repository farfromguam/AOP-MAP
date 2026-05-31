# Working PWA CSS — known-good snapshot

TL;DR:
- This is the **locked, working** iOS-PWA (installed / `display-mode: standalone`)
  layout for `website/index.html`. Captured the moment it read right on-device.
- **Marker:** build **`v13-dbg`**, 2026-05-30. Device: iPhone 375×812pt @3x
  (`screenH 812`, `safe T50 B34`), iOS **26.2+**. Served straight to the phone.
- If the PWA layout ever regresses, diff against the verbatim blocks below — they
  are the source of truth for the full-bleed map + safe-area chrome + bottom bar.
- Phase 2 (iOS **Safari tab**, non-standalone) is a SEPARATE problem — do not edit
  these `@media (display-mode: standalone)` / PWA rules to chase a Safari-tab bug
  without re-confirming the PWA still reads right on-device.

#aop #pwa #ios #css #reference #locked

-----

## What "working" means here (the bar this snapshot cleared)

On an installed iOS PWA, verified from the device screenshot (not Playwright):

- **No red band.** `#map` paints edge-to-edge incl. under the status bar + home
  indicator. (`html,body{background:#ff0033}` is a live diagnostic — red would mean
  body bleed-through. None showed.)
- **Bottom bar aligned.** The ⓘ attribution (bottom-left) and the pencil edit FAB
  (bottom-right) share one baseline: **both 18px off the true viewport bottom.**
- **Chrome clears the notch / home indicator / rounded corners** via
  `env(safe-area-inset-*)` padding on the controls.

On-device dbg readout at lock (the `#dbgOverlay`): `standalone:true`, `innerH 812`,
`clientH 762`, `screenH 812`, `#map t0 b812 h812`, `canvas h812`, `safe T50 B34`,
`ⓘ fromBot 18  ✎ fromBot 18`.

> ⚠️ Line numbers below are a 2026-05-30 snapshot and WILL drift. Match on the
> selector / rule text, not the line number.

-----

## 1. `<head>` — meta + edit-gate (index.html ~4-27)

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
<link rel="manifest" href="./manifest.json" />
<meta name="theme-color" content="#a85020" />
<link rel="apple-touch-icon" href="./icons/apple-touch-icon.png" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="AOP Map" />
```

`viewport-fit=cover` + `black-translucent` are load-bearing: they put the web view
under the status bar / home indicator so the map can be full-bleed. The edit-gate
script (sets `html.editor-off` from `?edit=0`) runs in `<head>` to avoid a FAB flash.

`manifest.json`: `"display": "standalone"`, `background_color #F5EFE0`,
`theme_color #a85020`, `start_url "./"`, `scope "./"`.

## 2. Safe-area inset tokens (index.html ~57-71)

```css
--sa-top:    env(safe-area-inset-top, 0px);
--sa-bottom: env(safe-area-inset-bottom, 0px);
--sa-left:   env(safe-area-inset-left, 0px);
--sa-right:  env(safe-area-inset-right, 0px);
/* Width the bottom-right edit FAB occupies; the bottom-left ⓘ caps short of it. */
--edit-fab-reserve: 76px;   /* html.editor-off zeroes this */
```

To FAKE insets on desktop for testing: override these in DevTools (e.g.
`--sa-top: 50px`). They default to `0` so desktop layout is unchanged.

## 3. Height split + full-bleed map (index.html ~83-100) — THE red-band fix

```css
body, html { margin: 0; padding: 0; height: 100dvh; overflow: hidden; font-family: Inter, system-ui, sans-serif; }
#map { position: fixed; top: 0; left: 0; width: 100vw; height: 100dvh; }
@media (display-mode: standalone) {
  html, body, #map { height: 100vh; }
}
```

- **Browser tab → `100dvh`**: respects the collapsing address bar (`100vh` runs too
  tall in a tab).
- **Installed PWA → `100vh`**: no toolbar, and unlike `100dvh` it is correct on cold
  start. This is what closes the iOS bottom band.
- **NEVER `height:100%`** — with `viewport-fit=cover` + `black-translucent` a
  PERCENTAGE height makes Safari silently DROP cover layout, returning
  `screenH − statusBar` (762 on an 812 screen) and dumping the lost ~50px as a dead
  band at the bottom (the "red bar"). Documented dead end.
- **NEVER the negative-inset hack** `#map{ top:calc(-1*--sa-top); bottom:calc(-1*--sa-bottom) }`
  — a fixed element cannot paint into the off-viewport band a % height created.

## 4. Corner controls clear the insets (index.html ~101-114)

```css
.maplibregl-ctrl-top-left    { margin-top: var(--sa-top); margin-left: var(--sa-left); }
.maplibregl-ctrl-top-right   { margin-top: var(--sa-top); margin-right: var(--sa-right); }
.maplibregl-ctrl-bottom-left { margin: 0; }
.maplibregl-ctrl-bottom-left .maplibregl-ctrl-attrib { margin: 0 0 18px 16px; max-width: calc(100vw - 24px - var(--sa-left) - var(--sa-right) - var(--edit-fab-reserve)); }
.maplibregl-ctrl-bottom-right{ margin-bottom: var(--sa-bottom); margin-right: var(--sa-right); }
```

The ⓘ baseline is `18px` bottom / `16px` left (nudged from 12/12 on 2026-05-30
"up + right a bit"). Target the **attrib's own margin**, not the corner container's
— MapLibre also puts a 10px margin on `.maplibregl-ctrl` which otherwise stacks to
~22px.

## 5. Edit panel + collapsed pencil FAB (index.html ~287-320) — THE baseline fix

```css
/* position:FIXED, not absolute — see rule 5a below for why. */
.panel { position: fixed; right: calc(12px + var(--sa-right)); bottom: max(12px, var(--sa-bottom)); top: auto; background: rgba(255,255,255,0.94); padding: 14px; border-radius: 12px; box-shadow: 0 10px 35px rgba(0,0,0,0.15); width: 380px; max-width: calc(100vw - 24px - var(--sa-left) - var(--sa-right)); max-height: calc(100vh - 24px - var(--sa-top) - var(--sa-bottom)); overflow-y: auto; z-index: 2; box-sizing: border-box; }
.panel-fab-pencil { display: none; } /* shown only as the collapsed FAB */
.panel.collapsed {
  left: auto; right: 12px; bottom: 18px;
  width: 56px; height: 56px; min-width: 0; padding: 0;
  max-width: none; max-height: none;
  border-radius: 50%;
  background: var(--rust);
  box-shadow: 0 8px 22px rgba(120,52,18,0.42), 0 0 0 4px rgba(255,253,245,0.55);
  overflow: hidden;
}
.panel.collapsed .panel-header { height: 100%; justify-content: center; gap: 0; }
.panel.collapsed .panel-header h1,
.panel.collapsed #exportAll,
.panel.collapsed #panelCollapse { display: none; }
.panel.collapsed .panel-fab-pencil { display: grid; place-items: center; color: #fff7e9; }
.panel.collapsed .panel-fab-pencil svg { width: 24px; height: 24px; }
html.editor-off .panel { display: none; }
html.editor-off { --edit-fab-reserve: 0px; }
```

### 5a. WHY `position: fixed` (the 50px gremlin)

On iOS, a `position:absolute` `.panel` anchors to the `<html>` content box, which the
device measures as **762px** on an 812px screen (`innerH 812 / clientH 762`, the 50px
top safe area). So `bottom:12px` landed the FAB at `762−12 = 750` from top = **62px**
off the true bottom. The ⓘ lives INSIDE the `position:fixed` `#map` (true 812px
viewport), so its `bottom:12px` landed at 12px. Same value, two contexts → 50px split
(`62−12 = 50` = the top safe area). **`position:fixed` makes the panel resolve against
the same viewport as the ⓘ**, so the two bottoms actually align on-device. Inert on
desktop (body has no scroll, `overflow:hidden`).

## 6. Narrow-viewport overrides (index.html ~776-790)

```css
@media (max-width: 760px) {
  .left-controls { left: calc(8px + var(--sa-left)); right: calc(8px + var(--sa-right)); top: calc(8px + var(--sa-top)); width: auto; max-width: none; gap: 6px; }
  /* …pill/tab/hot sizing… */
  .panel { left: calc(8px + var(--sa-left)); right: calc(8px + var(--sa-right)); top: auto; bottom: calc(8px + var(--sa-bottom)); width: auto; max-width: none; max-height: clamp(220px, calc(100vh - 360px - var(--sa-top) - var(--sa-bottom)), 420px); }
}
```

(`.panel.collapsed`'s 0,2,0 specificity beats the `.panel` media rule, so the FAB
keeps `right:12px; bottom:18px` even here.) `.left-controls` base anchors top-left
with `calc(12px + var(--sa-*))`.

## 7. JS — attribution placement + viewport resync (index.html ~1342-1379, ~9823-9875)

```js
new maplibregl.Map({ /* … */ attributionControl: false });
map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-left');
// collapseAttribOnce(): on first `sourcedata`, strip `maplibregl-compact-show` +
//   `open` so the compact bar starts as the ⓘ (it defaults to EXPANDED), then unbind.
// resyncViewport(): map.resize() + updateDbgOverlay() on resize / orientationchange /
//   pageshow / visualViewport resize — iOS finalizes standalone height late, and
//   MapLibre's ResizeObserver on a fixed container doesn't always catch it.
```

## 8. Service worker version sync (`website/sw.js`)

`const VERSION = 'v13';` — **keep in lockstep with `#appVersion`** in index.html
(`v13-dbg`). Bumping VERSION busts `aop-shell-${VERSION}` / `aop-data-${VERSION}` so
the phone pulls the new build on reload. `aop-tiles` is unversioned on purpose.

-----

## STILL-LIVE DIAGNOSTICS (this snapshot includes them; strip at closeout)

This is a `-**dbg**` build — the following are scaffolding, NOT durable layout:

1. ~~`html, body { background: #ff0033; }` red bleed-through probe~~ — **RETIRED**
   (`#ff0033` red → `#F5EFE0` cream in v14 → **`#000` black in v15**). The body bg is
   invisible in the PWA (the fixed map covers it) but in a SAFARI TAB iOS samples it to
   tint the status bar + bottom toolbar — black makes those chrome strips read as the
   device bezel/notch and "disappear." Safari samples the BODY bg here, NOT the rust
   `theme-color` (proven: red bands despite theme-color=#a85020). Keep it black (or a
   deliberate map-toned neutral), never a debug color. Does not affect PWA layout.
2. Blue map background-layer paint `#1e66ff` (in the JS layer setup). **Still live.**
3. `#dbgOverlay` div (markup ~799) + `updateDbgOverlay()` / its resync wiring —
   **including the `ⓘ fromBot N  ✎ fromBot N` baseline line** added this session.
4. The `-dbg` suffix on `#appVersion` + the matching `sw.js VERSION`.

Closeout = strip 1-4, set neutral body bg, drop `-dbg`, then commit. The layout
rules in §1-§8 stay.

-----

## The five hard-won rules (don't re-litigate)

1. **`height:100%` is forbidden** under `viewport-fit=cover` + `black-translucent` —
   it drops cover layout and creates the bottom dead band.
2. **PWA = `100vh`, browser tab = `100dvh`** (split on `display-mode: standalone`).
3. **Anchor bottom chrome with `position: fixed`**, not absolute — absolute resolves
   against the 762px `<html>` box and floats 50px high on iOS.
4. **Playwright (desktop) cannot reproduce this class of bug** — no safe area, so
   `env(safe-area-inset-*)=0` and absolute≡fixed. It reported the misaligned icons as
   aligned. Ground truth = device screenshot (measure: 1pt = 3px @3x) + `#dbgOverlay`.
5. **iOS 26.1 had a PWA status-bar regression** (WebKit 301994, fixed in 26.2). The
   lock device is 26.2+, unaffected. Don't blame the OS.

See `brain/handoff/session_context.md` (2026-05-30 blocks) for the full build log.
