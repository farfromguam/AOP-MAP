# Left Rail Collapse — Manilla Tab Drawer

Date: 2026-05-25

TL;DR:
- Replace the current vertical stack of left-rail cards (search, hot, calendar)
  with a unified "manilla tab drawer" where each card has its own icon tab and
  its own independent toggle. No global collapse.
- Open cards scoot up to absorb collapsed cards' rows above; the bottom card
  also extends down. Closed cards become icon "islands" inside the next open
  card's segment.
- Five HTML mockup variants live under `website/leftrail_v*.html`, indexed by
  `website/leftrail_compare.html`. Nothing is wired into `website/index.html`
  yet — variant pick is the open decision.

#aop #03_event_app #viewer #left_panel #collapse #design

-----

## Source

- User request, 2026-05-25: review the left sidebar; design a collapse for the
  search + hot + info-panel cards; each card gets a top-left icon that toggles
  only itself; "spin up agents for creative variations."
- Locked behavior arrived at through several rounds of ASCII iteration with the
  user. Full work log: `brain/handoff/session_context_20260525.md`.
- Builds on `left_panel_context_tabs.md` (Events / Park / About tabs shipped
  inside `#calendarCard`) and `left_sidebar_content_audit.md` (Rock Warblers
  rebrand of the tab labels). The collapse work is structural; those two are
  content. They overlap on the same `#calendarCard` DOM but do not conflict.
- Adjacent pending: `left_panel_poi_browser.md` (adds a POI tab inside the
  context card). The collapse drawer wraps the context card from outside, so
  the POI work and the collapse work compose.

## Locked behavior

The drawer is one unified rectangle, not three independent pills.

- Left column: 44px wide, always shows three icons in fixed row positions —
  search (row 1), hot (row 2), calendar (row 3) — with horizontal hairline
  dividers between them.
- Right column: 360px wide, segmented by which cards are open.
- Per-card icon click toggles only that card. No global collapse button.
- **Upward absorption**: each open card's right-column segment extends UP to
  swallow any contiguous closed cards' rows above it. The closed card's icon
  stays in its row as an "island" sitting in front of the open segment.
- **Downward absorption (E1, bottom edge case)**: if the bottom card is closed
  and an open card sits above it, the open card extends DOWN through the
  closed bottom row.
- Divider rule: the seam between rows N and N+1 is icon-column-only (44px,
  short) when both rows belong to the same open segment; otherwise full-width
  (404px) across both columns.
- All three closed → the drawer shrinks to just the 44px icon strip on the
  left. No empty right column floats next to the map.

## Mockup variants

All built on the same locked behavior. They differ only in visual treatment.

- `website/leftrail_v1_classic.html` — classic manilla folder: rounded outer
  tab corners, slightly darker spine behind the icon strip, open tab "pulled
  out" with `translateX(-2px)` + deeper drop shadow. Most skeuomorphic.
- `website/leftrail_v2_modern.html` — flat modern: no shadows, no special tab
  shapes, color-only state (closed = transparent on the cream drawer, open =
  moss-soft fill), single 2px rust accent on the "active" segment.
- `website/leftrail_v3_cabinet.html` — color-coded filing cabinet: each tab
  has a function stripe on its inner edge (search = moss, hot = rust, calendar
  = brown-dark) + a 2-letter filing code (SR / HT / CL). Open tab fills with
  a 12% wash of its stripe color. Provenance fingerprint at the chrome level.
- `website/leftrail_v4_dynamic.html` — motion-led: open shifts the icon left
  3px on a slight-overshoot spring; close snaps back with a 150ms rotateY
  wobble; hover gives a 1px "pull-me" telegraph. Respects
  `prefers-reduced-motion`. No paper textures — depth comes from timing.
- `website/leftrail_v5_hybrid.html` — v1's content-aware JS layout engine
  (segments size to their natural content height instead of being clipped to
  fixed grid rows) wearing v2's flat skin. Carries v2's "active" model:
  clicking an open inactive tab promotes it; clicking the active tab closes
  it; rust accent migrates to whichever open tab is left.
- `website/leftrail_compare.html` — side-by-side review of all five with
  iframes you can click through.

Earlier exploration that stays in the tree as reference:

- `website/leftrail_collapse_mockups.html` — round-one ASCII review (edge dock,
  accordion, map-room metaphor, power-user).
- `website/leftrail_edge_dock_mockup.html` — intermediate per-card mockup; the
  unified-drawer behavior came from this iteration.

## Open

- **Variant pick.** v1 / v2 / v3 / v4 / v5. The hybrid v5 is the most likely
  pickup but the user hasn't committed.
- **Integration into `website/index.html`.** None of the five mockups have
  touched the real viewer yet. Integration replaces the current
  `.search-shell`, `.hot-control`, `.calendar-card` standalone shells with the
  unified-drawer layout; the inside chrome of each card stays intact.
- **Mobile (≤760px).** Locked behavior is desktop-only at the moment. Mobile
  still has the `.left-controls { left: 8px; right: 8px }` full-width override
  from `website/index.html:277` plus the bottom-anchored panel. The drawer
  needs a mobile story — likely per-card collapse still works but the drawer
  fills viewport width; the icon column stays 44px regardless.
- **"Active" vs "open" model.** v2 and v5 carry an "active" concept where one
  open segment shows the rust accent and clicking an open-but-inactive tab
  promotes it without closing anything. Drop this if the second click target
  is one subtlety too many; keep it if the accent stripe is doing useful work.
- **Verifier strategy.** Existing Playwright verifiers hit `#searchInput`,
  `#hotButton`, `#hotTrailButton`, `#calendarToggle`, `#calendarBody`. The
  drawer rewrite must preserve those IDs or the verifier suite breaks.
  Carryover from `left_panel_context_tabs.md` — same ID-stability rule.
- **Persistence.** Should each card's open/closed state persist across reloads
  in localStorage? Calendar already persists via `aop_calendar_collapsed_v1`
  (see `viewer_polish_carryover.md` Lane 2). Probably yes, one key per card.

## Files touched

Nothing in `website/index.html`. All new files:

- `website/leftrail_v1_classic.html`
- `website/leftrail_v2_modern.html`
- `website/leftrail_v3_cabinet.html`
- `website/leftrail_v4_dynamic.html`
- `website/leftrail_v5_hybrid.html`
- `website/leftrail_compare.html`
- `website/leftrail_edge_dock_mockup.html` (intermediate)
- `website/leftrail_collapse_mockups.html` (intermediate)

## Verification

Design-only this session. No `index.html` changes, no verifier runs. Each
mockup was clicked through the 8 open/closed permutations and the absorption
math + divider rules confirmed against the locked behavior.
