# Slice 2 — Search ported into the clean core

TL;DR:
- Port the **feature search** into `viewer_core.js` + `viewer.html`: the search box, the client-side
  index over already-loaded GeoJSON, the results dropdown (rank/alias/trail-desc), Enter/click fly-to,
  the layer auto-unhide, and the highlight pulse.
- Same extraction discipline as slice 1: carry what's wired, **sever the editor seams** — `indexFeatures`'
  DOM-checkbox `toggleFor` and feature-list `featureListBindingFor`, and the session-persistence calls.
  "Turn the layer on" reuses the slice-1 `PRESET_LAYERS` registry, not a new one.
- Built alongside; `index.html`/`main.js` untouched. Verified by observation.

#aop #sprint #13 #viewer #search #slice

-----

## Why this slice next

Slice 1 proved the pattern and left search out (`indexFeatures` was one of the editor hooks stripped from
every layer add-site). Search is the next day-of read control on the slate (`_readme.md` item 2) and it's
self-contained: it reads the GeoJSON the layers already loaded, so it adds no new data sources — only the
one `search-highlight` overlay. It's a clean read of "what a real interactive read control costs."

## What to build

**`website/viewer.html`** — add the `.search-shell` block (search icon + `#searchInput` + `#searchResults`)
to `.left-controls`, below the pill-bar (from `index.html:111-120`). NOT the full left-rail drawer
(Search/Hot/Calendar tabs) — that two-column drawer is slices 3/5; slice 2 is the bare search box.

**`website/css/viewer.css`** — pull the search rules from `app.css` (`.search`, `.search input`,
`.search-icon`, `.search-results`, `.search-item`, `.search-kind`, `.search-result-*`, `.search-empty`,
`.search-shell`), each block citing its source line. Add the `--brown-soft` / `--brown-mid` tokens they use.

**`website/js/viewer_core.js`** — port from `main.js`:
- `search-highlight` source + `search-highlight-line`/`-point` layers (`main.js:9942`), added **last** so
  the pulse draws on top.
- `indexFeatures` (`main.js:9992`) — **rewritten signature** `(data, kindFor, layersFor, aliasesFor)`:
  drop `toggleFor` (no checkboxes) and `featureListBindingFor` (no editor feature list). `layersFor`
  returns the layer-id array to make visible on landing — reuse `PRESET_LAYERS` values.
- `searchDisplayName`, `buildSearchGroups` (minus the feature-list group fields), `searchGroupMatchesQuery`,
  `searchRank`, `renderSearchResults`, `positionSearchResults`, the pulse (`pulseHighlight` + constants),
  `clearSearchResults`, `gotoMatch` (toggle.checked → `setLayerVisibility`; drop feature-list +
  `persistViewerSessionState`), and the `searchInput` input/focus/keydown + document-click-to-clear
  listeners. `escapeHtml` helper.
- Call `indexFeatures` at each **carried** layer's add-site (water, roads, visitor-context, buildings
  facilities, gold trail network, brand logos, publish trails/boundaries/trailheads). Skip the
  dev-reference / later-slice index sites (OSM, event-schedule, cemeteries). `buildSearchGroups()` + the
  highlight layers at the end of `load`.

## Acceptance

- [x] `viewer.html` loads with the search box; **0 console/page errors**; `index.html` untouched.
- [x] Typing a known name (trail number, "ellis cove", "pavilion", "battle") surfaces ranked results;
      **Enter / click** flies to it, auto-unhides its layer, and **pulses the highlight** — observed.
- [x] Trail-number queries (bare digit) surface the trail family; alias queries ("trail 15", address
      aliases) land. (Trail-description second line: renders when a trail carries a baked `description`.)
- [x] No editor seam carried (no `featureListBindingFor`, no checkbox toggle, no session persistence).
- [x] Line-cost recorded under Verification.

## Verification

- `python3 -m http.server` from `website/`, open `viewer.html`.
- Playwright: type queries, assert the dropdown renders, Enter flies the camera (observe center/zoom or
  pixel change) and the highlight layer becomes visible, layer auto-unhide works (search a layer the
  current preset hides → it draws). Screenshot a result + highlight. 0 console errors.
### Done — 2026-06-13 (slice 2 shipped, verified by observation)

**Files (built alongside; `index.html`/`main.js` untouched — `git status` confirms):**
`viewer_core.js` 895 → **1249** (+354 for search) · `viewer.html` 63 → 75 (+12, the search box) ·
`viewer.css` 75 → 96 (+21, the search rules + `--brown-soft`).

**Verification (real running system).** `/tmp/verify_viewer_search.py`: **13/13 PASS, 0 console errors,
0 page errors.** Observed: `"pavilion"` → `['Pavilion facility','AOP Pavilion trailhead']`; `"15"` →
`['15 trail']`; `"battle"` → `['Battle Creek stream','Battlecreek Rd road']`; `"ellis cove"` →
`['Ellis Cove Rd road','Farmhouse facility','Front Office facility','Pavilion facility']` (the facility
rows match via their **address aliases** — alias search confirmed); `"zzzqqq"` → "No match". Enter
clears the dropdown, sets the input to the match name, and **moves the camera + draws the highlight**
(frame changed). **Layer auto-unhide observed:** in the Satellite preset (roads off) searching
`"ellis cove"` → Enter drew the road over the aerial — screenshots `viewer_search_after_enter_pulse.png`
(amber pulse on Battle Creek) and `viewer_search_satellite_after_road_search.png` (road unhidden + pulsed
over imagery) in `brain/output/`.

**Line-cost.** +354 lines in `viewer_core.js`: ~230 the search engine (`indexFeatures`,
`buildSearchGroups`, `searchGroupMatchesQuery`, `searchRank`, `renderSearchResults`,
`positionSearchResults`, `pulseHighlight` + constants, `clearSearchResults`, `gotoMatch`, `escapeHtml`);
~40 the `indexFeatures` calls at the 7 carried add-sites; ~18 the `search-highlight` source+layers; ~35
the input/keydown/mousedown/document-click/reposition listeners; ~10 DOM refs + state. This is the
calibration for "a real interactive read control": ~350 clean lines, **adding no new data source** — it
reads the GeoJSON the layers already loaded, only adding the one `search-highlight` overlay.

**What was severed (the editor seam, same axis as slice 1).** `indexFeatures` in `main.js` carries a DOM
`toggleFor` (a checkbox) and a `featureListBindingFor` (the editor's per-feature feature-list). Both are
dropped. The replacement: `indexFeatures(data, kindFor, layersFor, aliasesFor)` where `layersFor`
returns the **layer-ids to unhide on landing — reusing the slice-1 `PRESET_LAYERS` registry** (no second
registry). `gotoMatch`'s `match.toggle.checked = true; dispatchEvent('change')` becomes a direct
`setLayerVisibility(id, true)` loop; the `setFeatureVisible`/`renderFeatureList` feature-list unhide and
every `persistViewerSessionState` call are dropped. `main.js`'s broader `resyncViewport`/`map.resize`
viewport-health machinery was NOT carried (PWA slice 6) — only the dropdown's scroll/resize reposition,
which is all search needs.

**Scope lines.** Indexed only the **carried** layers (water/springs, roads, visitor-context, the 3
building facilities, the gold trail network, brand logos, publish trails/boundaries/trailheads). The
`main.js` index sites for dev-reference / later-slice layers (OSM, event-schedule, cemeteries) were not
ported — consistent with slice 1's carried-layer set.

**Owed / git gate.** UNCOMMITTED (the user's gate). `viewer.html` still not in `sw.js` `SHELL_ASSETS` →
**no `#appVersion` bump owed.** Next per the slate: **Calendar / Events** (slice 3) — needs the shared
`event_schedule_geojson.js` resolver + the `event-schedule` source.

## Notes

Built alongside; no commits without the user's git gate. `viewer.html` still not in `sw.js` → no
`#appVersion` bump owed. Next per the slate: Calendar / Events (slice 3).
