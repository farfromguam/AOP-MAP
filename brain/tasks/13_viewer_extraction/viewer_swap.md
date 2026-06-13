# Slice 7 — the swap (promote the clean viewer to index.html) + blue Locate FAB

TL;DR:
- The clean read view (`viewer.html`, slices 1–6) **becomes** `index.html`. The old tangled
  all-in-one page is parked at `old_index.html` (not deleted — honors the user's *"don't delete
  code I think is good"*). The editor lives on in `panel.js` + the standalone field tools
  (`schedule_editor.html`, `data_editor.html`) + QGIS.
- Same pass: the **Locate** control moved out of the left rail into a **blue crosshair FAB** in the
  bottom-right, styled like the editor's pencil FAB and parked in the slot *beside* it, so the future
  tester view can show Locate + Edit side by side (`brain/pages.md`).
- This is the git-gated deletion/rename step the sprint reserved for the user. Files are renamed in the
  working tree (plain `mv`, no `git mv`/`add`); the commit is the user's.

#aop #sprint #13 #viewer #extraction #swap #slice #pwa #locate

-----

## Trigger

`brain/pages.md` (the user's page map) plus: *"Do the blue locate tasks and ensure that the new page is
'fully ready' for action…. as far as index rename the old one old_index. its important that this new page
function as our 'front end'."* — 2026-06-13. This authorizes the slice-7 swap the `_readme.md` slate held
behind the git gate, and adds the blue Locate FAB.

## What was built

### Blue Locate FAB (`brain/pages.md` checkbox)

- **`index.html`** (the file that was `viewer.html`): `#locateBtn` removed from the `.left-controls`
  stack and re-added as a standalone bottom-right `button.locate-fab` (crosshair SVG kept). `id` is
  unchanged, so `viewer_core.js` wiring (`click → geolocate.trigger()`, `.active` lit on
  `trackuserlocationstart`) needed **no change**.
- **`css/viewer.css`**: new `--locate-blue`/`--locate-blue-dark` tokens (`#2b7cd3`/`#2367b4`) and a
  `.locate-fab` rule mirroring the editor pencil FAB (`app.css .panel.collapsed`): 56px circle, glow +
  cream ring, flat `bottom:18px` so it aligns with the bottom-left ⓘ. The old `.util-group.util-locate`
  rules were replaced by `.locate-fab`. Edit FAB is **not** shown on this read view.
  - **Position (user follow-up, 2026-06-13):** first parked at `right:80px` (the slot beside the edit
    FAB's `right:12px`), but the user noted that left a phantom margin where the absent edit button would
    be — *"the locate will always be there so make it the furthest to the right."* So Locate now anchors
    the far-right corner at **`right:12px`**. On the future tester view (where Locate + Edit both show),
    the edit FAB sits to its LEFT at `right:80px` (12 + 56 + 12).

### The swap

- **Rename (working tree):** `index.html` → `old_index.html`; `viewer.html` → `index.html`. Plain `mv`
  (no `git mv`/`add` — the user's git gate). No functional link in the site pointed at `viewer.html` and
  no `href` pointed at `index.html` (every match was prose in dev mockups), so the rename stranded
  nothing.
- **`sw.js`**: `VERSION` v63 → **v64**; added `./css/viewer.css` + `./js/viewer_core.js` to
  `SHELL_ASSETS` (the front end is now offline-first). `./js/main.js` + `./js/panel.js` +
  `./css/panel-embed.css` + `./css/app.css` were **kept** (additive, not pruned — `old_index.html` and
  the field editors still use them, so they stay offline-capable too). The navigation fallback already
  serves `./index.html`, which is now the viewer.
- **`index.html` `#appVersion`** v62 → **v64** (in sync with `sw.js`). `manifest.json` needed no change:
  `start_url`/`scope`/`id` are all `./`, which now resolves to the viewer.
- **`old_index.html`** left at `#appVersion` v63 — it is a frozen legacy page, not the version source.

## Acceptance

- [x] Locate is a blue crosshair FAB, 56×56, far-right corner (`right:12px`/`bottom:18px`), out of the
      left rail; click triggers the GeolocateControl and lights the FAB; the blue user-location dot
      renders. 0 errors. (First built at `right:80px`; moved to the corner per the user follow-up above —
      re-verified `rightGap:12`, clear of the bottom-left ⓘ, lights on click, 0 errors.)
- [x] `http://localhost:8000/` serves the clean viewer (no editor `.panel`); presets(4)/zooms(3)/search/
      calendar/hot/install all present; `#appVersion` reads **v64** folded into the ⓘ; service worker
      registers. **0 console errors.**
- [x] `http://localhost:8000/old_index.html` → **200**, still the full all-in-one editor page.
- [x] `node --check` clean on `sw.js` + `viewer_core.js`.

### Done — 2026-06-13 (verified by observation)

`/tmp/verify_locate_corner.py` (current state, after the right:12px follow-up): FAB `56×56`,
`rightGap:12 bottomGap:18`, `border-radius:50%`, `background rgb(43,124,211)` (=`#2b7cd3`),
`position:fixed`, `inLeftControls:false`, clear of the bottom-left ⓘ; click → `active:true`; **0 errors**
(`/tmp/locate_corner.png` shows the blue crosshair FAB flush in the corner). (The first build verified at
`rightGap:80` via `/tmp/verify_locate_fab.py`/`/tmp/locate_fab_corner.png` before the user's reposition.)
`/tmp/verify_swap.py`: root `/` → `isViewer:true`,
`hasMainJsPanel:false`, `presets:4 zooms:3`, search/calendar/hot/install all true, `version:v64`,
`versionFolded:true`, `service worker: registered`, locate `active:true` after click; `old_index.html`
→ `200`, `hasEditPanel:true`, `v63`; **0 errors** (`/tmp/swap_root.png`).

## Follow-ups (noted, not done — out of this card's scope)

- **Verifier re-pointing.** The committed `mvp/scripts/playwright_verify_*.py` target `index.html`
  expecting the OLD full page (editor + all dev-reference layers). They will now hit the viewer and fail
  on the intentionally-dropped surfaces. They should be re-pointed at `old_index.html`, or rewritten as
  viewer verifiers. Tracked here; not silently left implying coverage.
- **`old_index.html` registers `./sw.js` too** — harmless (same scope, same v64 SW), but it means a
  visit to the legacy page also warms the now-viewer shell cache. Fine.
- **tester.html** (a `brain/pages.md` future page) is where Locate + Edit both show — not built here.

## Git gate

All changes are in the working tree, UNCOMMITTED. The rename shows in `git status` as
`viewer.html` deleted + `index.html` modified + `old_index.html` added (git detects the rename on the
user's `git add`). The user commits.
