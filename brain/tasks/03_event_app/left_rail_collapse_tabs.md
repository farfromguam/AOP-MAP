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

## Mockup variants

2026-05-26 — element-round picks landed in `website/index.html`:

- **Gates-open countdown**: G2 ticker style from `leftrail_gates_ticker.html`
  — slim hairline tier, no fill, rust live-dot before the value, tabular
  scoreboard digits. CSS swap on `.calendar-countdown*` only.
- **Next-event chip**: N1 close-mode chip from `leftrail_next_minimal.html`
  — rust outline on transparent, lowercase "in 47m", tabular numerals.
  Restyles existing `.cal-soon-badge`; JS text changed from
  `SOON · IN {X}` to `in {X}`. Class name preserved.
- Far-mode header ticker from N1 was NOT carried (header ticker that
  replaces the gates banner when next event > 1h). Skipped to keep
  the change small; current behavior keeps the chip on the row at all
  upcoming_next distances, which is a simpler superset of the close mode.
- Round-2 variants (`leftrail_tabs_*`, `leftrail_gates_dash|horizon|tag`,
  `leftrail_eventflow_*`) did not get carried. Compare page at
  `website/leftrail_compare_v2.html` keeps them available for reference.

The v1–v10 design-round mockups were retired 2026-05-25 after the drawer
shipped. The artifact stack went through two further rounds:

1. **Theme round (12 whole-rail variants)** — palette/surface/treatment
   forks of the now-live integrated layout. User picked variant #12
   (higher contrast) as the direction.
2. **Element round (12 element-focused variants)** — buttons,
   countdown banner, live/next rows, past/future rows. Each variant
   restyles only its target element; the rest stays at the new baseline.

Master baseline (post variant-#12 promotion):

- `website/leftrail_current.html` — extracts the live drawer from
  `index.html` (pill-bar + drawer + all three panels open) and carries
  the higher-contrast palette tokens promoted from the theme round
  (deeper browns, more saturated rust, slightly deeper hairline alpha;
  cream + moss surfaces unchanged). All element variants fork this file.

Round 1 — lineage redo on the live layout (5 variants):

- `website/leftrail_classic.html` — warm kraft-tan open-tab fill,
  papery hairlines, slightly heavier outer chrome.
- `website/leftrail_modern.html` — flatter radii (4px), near-zero
  drop shadow, cooler cream, rust as a thin accent stroke.
- `website/leftrail_cabinet.html` — per-tab accent (search/slate,
  hot/rust, cal/moss) with SR / HT / CL filing codes beneath each icon
  and a left-edge stripe on each panel. Adds one `<span>` child per tab
  to host the code; all JS hooks preserved.
- `website/leftrail_motion.html` — springy float-down + fade-rise
  panel reveal + live-dot glow. Wrapped in
  `@media (prefers-reduced-motion: no-preference)` with a defensive
  symmetric `reduce` kill block.
- `website/leftrail_hybrid.html` — closest to current. Hairlines tuned
  warmer, open tab grows a connecting hairline, inner top shadow on the
  panel, countdown reads like a notebook pull.

Round 2 — fresh themes for the now-live layout (4 variants):

- `website/leftrail_warm_paper.html` — warmer amber cream, ochre
  hairlines, softened shadow, asymmetric handed-paper radii, very-low-
  opacity paper grain.
- `website/leftrail_cool_utility.html` — pale stone surface, charcoal
  ink, crisper hairlines, terracotta rust.
- `website/leftrail_rust_accent.html` — open-tab fill becomes a soft
  peach-clay wash, glyph deepens to walnut-rust. Rust as signature
  without dyeing the whole drawer.
- `website/leftrail_ink_noir.html` — full dark-mode sibling: walnut
  substrate, cream ink, deeper moss open fill, slate/moss map backdrop.

Round 3 — palette-only swaps (3 variants, `:root` tokens only):

- `website/leftrail_palette_warmer.html` — cream/moss-soft/hairline
  pushed one step amber. Rust/moss/ink untouched.
- `website/leftrail_palette_stone.html` — cream pushed toward neutral
  cool stone, brown-ink nudged cooler for cohesion.
- `website/leftrail_palette_contrast.html` — deeper ink family + slightly
  more saturated rust + thicker hairline alpha. AA+ sibling.

Element round — buttons (3 variants):

- `website/leftrail_buttons_outline.html` — cream surface + colored
  border + colored title; glyph becomes a small filled chip in the
  state color.
- `website/leftrail_buttons_chip.html` — unified walnut surface for
  all lanes; state expressed only as a 4–8px colored left-edge stripe.
- `website/leftrail_buttons_segmented.html` — chunky pills: 12px
  radius, 72px tall, stronger glyph, inner sheen + drop shadow,
  tactile press.

Element round — gates open countdown (3 variants):

- `website/leftrail_gates_ribbon.html` — wider banner with stacked
  label/value, ochre gradient, rust left ribbon, folded-corner notch.
- `website/leftrail_gates_ticker.html` — minimal slim ticker: no fill,
  no stripe, tabular numerals, 1px bottom rule.
- `website/leftrail_gates_card.html` — boxed two-column card: value
  left, stacked small-caps label right, postage-stamp rust triangle
  in the top-right corner.

Element round — live + next calendar rows (3 variants):

- `website/leftrail_livenext_badge.html` — drop bg fill + inset
  stripe; lean on rounded LIVE/NEXT pill badges with soft outer rings.
- `website/leftrail_livenext_glow.html` — live row picks up soft rust
  outer glow + badge pulse (prefers-reduced-motion aware); next gets
  a thin amber underline.
- `website/leftrail_livenext_card.html` — elevated cards: live = 2px
  rust border + larger shadow; next = 1.5px brown-dark + smaller shadow.

Element round — past + future calendar rows (3 variants):

- `website/leftrail_pastfuture_faded.html` — past dims deeper (0.42)
  with name strikethrough; hover lifts back. Future gets a bolder time
  + small dot marker on the day chip.
- `website/leftrail_pastfuture_marker.html` — past rows pick up a ✓
  in the day cell, future rows get a ○. Pure CSS pseudo-elements.
- `website/leftrail_pastfuture_condensed.html` — past rows collapse
  to half-height single-line ledger entries (location hidden, time
  inline); future stays roomy.

Compare page:

- `website/leftrail_compare.html` — side-by-side iframe review,
  baseline pinned at the top in a rust banner, 12 element variants
  grouped by category, and an appendix linking the 11 unchosen theme
  variants for reference.

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

Theme exploration stack (2026-05-25, post-integration):
- `website/leftrail_current.html` — master baseline; updated to carry
  the higher-contrast palette after variant #12 was promoted.
- `website/leftrail_classic.html`, `leftrail_modern.html`,
  `leftrail_cabinet.html`, `leftrail_motion.html`, `leftrail_hybrid.html`
  — theme round, lineage redo.
- `website/leftrail_warm_paper.html`, `leftrail_cool_utility.html`,
  `leftrail_rust_accent.html`, `leftrail_ink_noir.html`
  — theme round, fresh themes.
- `website/leftrail_palette_warmer.html`, `leftrail_palette_stone.html`,
  `leftrail_palette_contrast.html` — theme round, palette-only swaps.
  (`palette_contrast` is byte-identical to the new baseline.)
- `website/leftrail_buttons_{outline,chip,segmented}.html`,
  `leftrail_gates_{ribbon,ticker,card}.html`,
  `leftrail_livenext_{badge,glow,card}.html`,
  `leftrail_pastfuture_{faded,marker,condensed}.html`
  — element round (12 variants).
- `website/leftrail_compare.html` — side-by-side iframe review.

Retired 2026-05-25 (deleted from tree): `leftrail_v{1..10}_*.html`,
the previous `leftrail_compare.html`, `leftrail_collapse_mockups.html`,
`leftrail_edge_dock_mockup.html`.

Card rewrite:
- `brain/tasks/03_event_app/left_rail_collapse_tabs.md` — this file.
