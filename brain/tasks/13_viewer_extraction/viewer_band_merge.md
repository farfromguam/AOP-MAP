# Slice 8 — merge the off-edge decorative band into the clean viewer

TL;DR:
- The geolocated "printed neat-line" band is built and council-cleared, but it only lives on the proof
  page `website/viewer_banded.html`. This slice carries it into the real viewer (`index.html`).
- This is **extraction, not subtraction** (the sprint rule): carry ONLY the band. The proof page's
  scaffolding — the screen-space `#bandFrame` tiles, `viewer_band.css`, the proof HUD, the `?deco`
  compare rig, the constructor shim — does **not** cross. None of the editor/CRUD crosses either.
- The merge surface is 3 files + 1 already-in-place module. The one real fork is the camera leash
  (`maxBounds`).

#aop #sprint #13 #viewer #band #merge #extraction

-----

## What is already built (the thing that crosses)

`website/js/viewer_band.js` — the band, **rewritten 2026-06-13** from a screen-space HTML overlay to
real geolocated MapLibre layers. Verified by observation on `viewer_banded.html?frame=out`: it draws
**38 layers** — `band-mask` (paper donut hiding data spill outside the 9-patch), `band-keyline`
(neat-line), and a 6×6 grid of `band-art-*` draped raster tiles carrying the lettering + Rock Warblers
corner marks. It reads `window.AOPViewer = { map, regionBounds }`, uses zero CSS, and touches no DOM but
its own canvases. The centerline + label tuning is council-cleared (`band_centerline_council_receipt.md`,
`band_labels_council_receipt.md`). It drops in **unchanged**.

`website/assets/branding/rw-mark.svg` — the corner mark, already in the tree (v65), fetched at runtime
by `loadMark`.

## The seam (what the proof faked, the core must now own)

The proof page wraps `maplibregl.Map` in a constructor shim (`viewer_banded.html:190‑216`) to expose the
map + region and loosen the leash. In the real viewer, `viewer_core.js:36‑50` builds the map in an IIFE
with `maxBounds: REGION_BOUNDS` and exposes nothing. The seam becomes a few real lines in the core.

## The surgical diff (3 files)

1. **`website/js/viewer_core.js`** — after map construction (~line 50), expose the seam:
   `window.AOPViewer = { map, regionBounds: REGION_BOUNDS };` and pad `maxBounds` (see fork below).
   This is the ~3 lines the proof header promised. Nothing else in the core changes.
2. **`website/index.html`** — add `<script src="./js/viewer_band.js"></script>` immediately after the
   `viewer_core.js` tag (line ~262). Bump `#appVersion` (line 220).
3. **`website/sw.js`** — add `'./js/viewer_band.js'` and `'./assets/branding/rw-mark.svg'` to
   `SHELL_ASSETS` (so the band is offline-first; `addAll` is fail-hard and both files exist). Bump
   `VERSION` to match `#appVersion`. Do **not** add `viewer_band.css` (dead — see below).

`viewer_band.js` is already correct; it needs no edit.

## What does NOT cross (extraction discipline — the residual)

Confirmed dead/proof-only by reading + observation (`tileVisibleCount: 0` of the 8 old tiles):

- **`website/css/viewer_band.css`** — 100% dead for the feature. The geolocated band uses no CSS
  classes; every `#bandFrame`/`.band-tile`/`.band-label`/`?deco` rule styles nothing. Only the proof HUD
  rules survive, and those are proof-only. Not linked by `index.html`.
- **The screen-space frame** `<div id="bandFrame">` + 8 `.band-tile`/`.band-label` (proof page 34‑43) —
  fossil of the pre-rewrite approach. Never read by the new JS.
- **Proof scaffolding** — `#bandProofHud` + "Show me (auto-peek)" script, the `?deco`/`?frame=out`
  script, the constructor shim.
- **No CRUD / editor** — the merge touches none of `panel.js`, `data_editor*.html`, `data_editor_map.js`,
  `schedule_editor.html`, `main.js`. The read viewer stays read-only (user directive, 2026-06-13:
  *"be sure not to pull over the crud"*).

## Retire after the merge (spent scaffolding)

- `website/viewer_banded.html` (proof page) and `website/viewer_banded_compare.html` (now stale — its
  `?deco` iframes render identically because deco only styled the dead `#bandFrame`).
- `website/css/viewer_band.css`.
- Out of scope but adjacent: `old_index.html` (parked pre-swap monolith).

## The one fork — the camera leash (`maxBounds`)

`maxBounds` is currently the 9-patch exactly, so the band barely shows (thin letterbox slivers) and the
over-pull peek can't happen. The band's art frame extends ~0.12 of the region beyond the 9-patch.

**Recommendation:** pad `maxBounds` to ≈ the band's art frame (~0.13 out), so the leash becomes the edge
of the printed sheet — the whole frame seats, a gentle over-pull peek works, and users can't wander into
blank paper. The proof used a looser 0.6 pad for a dramatic demo; production wants the tighter, bounded
leash. The Region preset's `fitBounds` padding may want a small bump to seat the frame cleanly — tune by
observation during implementation.

Note the intended, visible consequence (this is the feature, not a regression): in satellite/topo/trace
presets the `band-mask` paints everything **outside** the 9-patch as paper, so imagery no longer spills
past the boundary. That is the "always a clean 9-patch" promise of the band.

## Verification (by observation, not re-derivation)

- Load `index.html` in real Chrome (Playwright), Region preset: screenshot shows the full lettered frame
  seated on the map; `getStyle().layers` reports `band-mask` + `band-keyline` + 36 `band-art-*`.
- Switch presets (park/topo/trace/satellite) and toggle 3D: the band drapes/conforms, stays on top
  (the `idle` raise), no data spill past the 9-patch, no console errors.
- Re-run the existing playwright viewer verifiers (search/presets/hot/poi/locate) — green = the port
  dropped no read-view behavior.

## Gate

Production fork + PWA version bump = the user's git gate (`no_commits.md`). The `maxBounds` pad amount is
the open decision above. Convene the council on the diff before declaring done (`council/`).

-----

## Implemented — 2026-06-13 (verified by observation, uncommitted)

The merge shipped on the user's "give it a shot." Files changed (all uncommitted, the user's git gate):

- **`website/js/viewer_core.js`** — band seam: padded camera leash `REGION_MAXBOUNDS` (`BAND_PAD = 0.13`,
  the 9-patch outset to the printed-sheet edge) now drives `maxBounds`; `window.AOPViewer = { map,
  regionBounds: REGION_BOUNDS }` exposed right after construction. Plus the **Region preset reframed**:
  `goToView('region')` used to inset the fit ~15% per side (filling the viewport with the data-rich
  centre, which cropped the band off every edge); it now **outsets ~7%** so the whole neat-line frame
  seats with a paper margin — matching the button's own label, "the full 9-patch region".
- **`website/index.html`** — `<script src="./js/viewer_band.js">` after `viewer_core.js`; `#appVersion`
  `v70 → v71`.
- **`website/sw.js`** — `./js/viewer_band.js` + `./assets/branding/rw-mark.svg` added to `SHELL_ASSETS`
  (offline-first); `VERSION` `v70 → v71`.
- **`website/js/viewer_band.js`** — z-order fix surfaced by the real viewer (the proof's tiny core hid
  it): the core adds ~50 layers async over ~8 s **after** the band is added, each landing on top, so the
  old idle-only raise left the band sunk under the data for the whole load. raiseBand now re-floats on
  every `styledata` (each core addLayer) + `idle`, coalesced one-per-frame (`queueRaise`), guarded by
  `bandIsOnTop()` so the band's own `moveLayer` doesn't loop. **This is the only change to the
  council-cleared band module, and it is robustness, not appearance.**

**Verified by observation** (real Chrome via Playwright on the clean `index.html`, not re-derived):
- Band renders as 38 geolocated layers (`band-mask` + `band-keyline` + 36 `band-art-*` draped tiles).
- Z-order poll: band reaches top at ~6 s and stays (`above=[]`) through the full load + preset switches —
  no sink (the pre-fix run sat under ~50 layers from ~1.5 s to ~9.8 s).
- PIL pixel sampling at the Region preset: all 8 perimeter points are paper `#e3d7bb`, centre is map —
  the frame seats cleanly. Satellite preset: corners paper, imagery contained inside the 9-patch (mask
  hides spill). 3D: lettering drapes/foreshortens on the pitched terrain.
- No console errors. `node --check` clean on all three JS files.
- **No CRUD leak:** `window.TerraDraw`/editor-panel selectors absent, Locate FAB present — read viewer
  stays read-only.
- `playwright_verify_presets.py`: all read-view assertions PASS (presets, 3D, search, calendar,
  Events/POI/About, POI rows, left-controls, Park active). The editor-tree / `#showLandcover` FAILs are
  **pre-existing** — that DOM does not exist in the post-extraction read viewer (the CRUD moved to
  `panel.js`), so they are structural to the clean viewer, not caused by this merge.

**Still owed (the user's call):** the git commit + version bump are the user's gate. Retire the spent
scaffolding when ready: `viewer_banded.html`, `viewer_banded_compare.html`, `css/viewer_band.css`
(+ adjacent `old_index.html`). Council review on the diff before "done".
