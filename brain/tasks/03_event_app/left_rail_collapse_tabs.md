# Left Rail Collapse — Two-column Drawer

Date: 2026-05-25

TL;DR:
- Replaced the vertical stack of left-rail cards (search, hot, calendar) with
  a two-column drawer. Col1 is a 44px icon strip (3 tab buttons in canonical
  order: search, hot, cal). Col2 holds the open panels stacked from the top
  in tab order.
- Icons keep canonical order and float DOWN — never up, never reordered —
  to align with their panel's top in col2. Closed icons sit at canonical y.
- Click is a pure toggle (closed ↔ open). No "active" middle state, no rust
  accent on a primary panel.
- Landed in `website/index.html` 2026-05-25. Reference implementation lives
  at `website/leftrail_v5_hybrid.html`.

#aop #03_event_app #viewer #left_panel #collapse

-----

## Source

- User request, 2026-05-25: review the left sidebar; design a collapse for the
  search + hot + info-panel cards; each card gets a top-left icon that toggles
  only itself; "spin up agents for creative variations."
- Five HTML mockup variants explored (v1–v5). v5 was picked and iterated
  through several rounds (clip-path L → flex L → float-down icons → pure
  toggle) before landing.
- Builds on `left_panel_context_tabs.md` (Events / Park / About tabs shipped
  inside `#calendarCard`) and `left_sidebar_content_audit.md` (Rock Warblers
  rebrand of the tab labels). Composes with `left_panel_poi_browser.md`
  (POI tab inside the context card).
- Full work log: `brain/handoff/session_context_20260525.md`.

## What shipped (locked behavior)

The drawer is two flex columns with independent heights.

- **Col1 (.lr-icon-col).** 44px wide, `min-height: 132px` (= 3 × `--tab-h`).
  Three 44×44 tab buttons in canonical order: search, hot, cal. Closed tab =
  transparent over the cream icon-col background. Open tab = moss-soft fill.
  Adjacent tabs are separated by a 1px hairline.
- **Col2 (.lr-content-col).** Fills the rest of `.left-controls` width
  (responsive: 296–360 px depending on the existing `.left-controls` rule).
  Open panels stack from the top in tab order; closed panels are `display:
  none`. Adjacent open panels separated by a 1px hairline (general-sibling
  selector handles gaps when a middle panel is closed).
- **Icon float-down.** Each icon's y is
  `max(canonical_y, panel.offsetTop, previous_icon_bottom)`. Icons NEVER go
  up. The visible effect: when all three are open, the Cal icon drops from
  its canonical y=88 to align with the Cal panel's top (which sits below
  the taller Hot panel), leaving a cream gap between Hot and Cal in col1.
- **Click is a pure toggle.** Open → closed, closed → open. No "active"
  state, no rust accent on a primary panel.
- **L-shape outer corners.** Col1 rounds top-left + bottom-left always.
  Col2 rounds top-right + bottom-right always. When col2 ends above col1's
  bottom (e.g., only Search open, ~44px panel vs 132px icon strip),
  `render()` adds `.col2-short` to col1 to also round its bottom-right.
- **All closed.** Col2 is `hidden`. Col1 gets `.standalone` and rounds all
  four corners — drawer collapses to a 44px icon pill on the left.

## Mockup variants (historical)

All five variants explored the same problem with different visual treatments.
v5 was picked and iterated past its original description. The others are
preserved as reference and stay in the tree.

- `website/leftrail_v1_classic.html` — classic manilla folder treatment.
- `website/leftrail_v2_modern.html` — flat modern, "active" rust accent.
- `website/leftrail_v3_cabinet.html` — color-coded filing cabinet
  (SR / HT / CL filing codes, function-stripe per tab).
- `website/leftrail_v4_dynamic.html` — motion-led: spring overshoot, rotateY
  wobble, prefers-reduced-motion-aware.
- `website/leftrail_v5_hybrid.html` — **picked.** Iterated through several
  rounds into the two-column drawer with float-down icons and pure-toggle
  clicks. This file is the reference implementation; its README-style top
  comment documents the model.
- `website/leftrail_compare.html` — side-by-side review iframe page.
- `website/leftrail_collapse_mockups.html`,
  `website/leftrail_edge_dock_mockup.html` — round-one ASCII iteration.

## Integration details (website/index.html)

CSS — added to the existing stylesheet (no removals):

- New `:root` tokens: `--tab-h: 44px`, `--hairline: rgba(74,60,42,0.08)`,
  `--moss-tint-hover: #d6e0cb`, `--cream-wash-hover: #f1e8d2`.
- Namespaced classes to avoid the existing `.panel` / `.drawer` /
  `.tab` collisions in the rest of `index.html`: `.lr-drawer`,
  `.lr-icon-col` (+ `.standalone`, `.col2-short`), `.lr-content-col`,
  `.lr-tab` (+ `.open`), `.lr-panel` (+ `.open`), `.lr-live-dot`,
  `.lr-day-cap`.
- Scoped overrides on `.lr-panel .search-shell`, `.lr-panel .hot-control`,
  `.lr-panel .calendar-card` suppress the now-redundant standalone card
  chrome (border / radius / background / shadow). `.lr-panel .search-shell`
  is pinned to `height: var(--tab-h)` so the search row sits flush with
  one tab.

HTML — existing `.search-shell`, `#hotControl`, `#calendarCard` were
WRAPPED, not replaced. All internal markup and existing IDs preserved:

```
.left-controls
  .pill-bar (unchanged)
  .lr-drawer #lrDrawer
    .lr-icon-col #lrIconCol
      .lr-tab.open #lrTabSearch — search SVG
      .lr-tab #lrTabHot — flame SVG + .lr-live-dot
      .lr-tab.open #lrTabCal — calendar SVG
    .lr-content-col #lrContentCol
      .lr-panel.open #lrPanelSearch  → existing .search-shell
      .lr-panel     #lrPanelHot     → existing #hotControl
      .lr-panel.open #lrPanelCal     → existing #calendarCard
```

Initial state mirrors the prior layout: Search + Cal open, Hot closed
(because `#hotControl` historically started with `hidden` until an event
populated it).

JS — self-contained IIFE appended to the existing inline script:

- Reads `--tab-h` from CSS once at startup. If `:root` changes `--tab-h`
  at runtime the cached value won't follow without a reload.
- Tracks `lrOpen = { search, hot, cal }` and runs the float-down margin
  loop on each render.
- Exposes `window.lrOpenCard(c)` and `window.lrCloseCard(c)` so external
  code (e.g., the hot-control reveal logic) can drive the drawer.
  **Not wired yet** — see Still Open.

## Verification

Playwright smoke (inline, `http://localhost:8001/index.html`):

- All drawer DOM hooks present; all preserved IDs reachable (`#searchInput`,
  `#hotButton`, `#hotTrailButton`, `#calendarToggle`, `#calendarBody`).
- Initial state: Search + Cal open, Hot closed. Tab positions canonical
  (y = 59 / 103 / 147 from drawer top with 1px border offset).
- Click `#lrTabHot` → Hot panel opens; Cal icon shifts from y=147 to y=201
  to align with the new Cal panel top (Hot panel inserts ~98px between
  Search and Cal). Float-down confirmed.
- Close Search + Hot → only Cal open. `.col2-short` correctly false
  (icon-col and content-col both 466 px because Cal is the taller side).
- No JS errors. WebGL chatter from MapLibre is normal.

Session-only screenshots at `/tmp/lr_initial.png`, `/tmp/lr_hot_open.png`.

## Still open

- **Wire Hot tab to hot-control data arrival.** The existing logic that
  removes `hidden` from `#hotControl` when an event becomes live does NOT
  open the Hot tab. Add a call to `window.lrOpenCard('hot')` in that code
  path so users see hot updates without manually clicking the icon.
- **Mobile (≤760px).** Drawer fills the wider mobile rail without changes,
  but the visual treatment has not been audited. Likely needs the
  full-width override and possibly a smaller `--tab-h` on tiny screens.
- **Persistence.** Each card's open/closed state could persist via
  localStorage (one key per card; mirrors `aop_calendar_collapsed_v1`).
  Not implemented this pass.
- **Dedicated verifier.** No `playwright_verify_left_rail_drawer.py` yet.
  The smoke test was inline. A standalone verifier should cover the L
  shape, the float-down rule, and the all-closed standalone state.
- **Old `.left-tab` collision.** The real-app `.left-tab` (Events / POI /
  About inside `#calendarCard`) and the mockup's same-named class for
  calendar inner tabs collide name-wise but don't share a parent. Confirm
  no specificity surprises after the integration ships.

## Files touched

CSS + HTML + JS:
- `website/index.html` — tokens, lr-* classes, drawer scaffold around the
  three existing cards, IIFE for render/click logic.

Mockup polish (no behavior changes during integration):
- `website/leftrail_v5_hybrid.html` — title, top comment block, and JS
  leading comment updated to match the final model.

Card rewrite:
- `brain/tasks/03_event_app/left_rail_collapse_tabs.md` — this file.

The four other mockup variants (`v1` / `v2` / `v3` / `v4`) and the two
intermediate exploration files were left untouched as historical reference.
