# Viewer chrome polish — Sprint 02 Bucket B

Small, mostly independent viewer-chrome tweaks. Each is roughly ½ day or less.
They share a card so adjacent work can land in one pass — but every item ships
behind its own acceptance and verifier so a single line can close without
holding the rest.

#aop #tasks #02_edit #chrome #polish

-----

## Source

- `_readme.md` — Bucket B in the Sprint 02 triage.
- `tasks.md` — original dump plus the new "calendar popup overflow on narrow
  screens" line at the bottom.
- `../01_mvp/poi_editor.md` — owns the editor panel that needs a polished
  collapsed state.
- `../01_mvp/event_schedule_layer.md` — owns the calendar sidebar and the
  `gotoEventSession` jump that drops the session popup.

## Scope

In:

- One umbrella card. Items below carry their own acceptance.
- Code changes confined to `website/index.html` (CSS + JS) and the matching
  Playwright verifiers under `mvp/scripts/`.

Out:

- Buckets A (decisions) and E (buildings default-on) — those wait on the
  views-and-defaults card.
- Bucket C (search tags + magnifier icon) — sister card, lands separately.
- Bucket H (full CSS/JS smell pass) — folds into `../01_mvp/code_health_pass.md`
  Pass 3 once Bucket B + D land.

## Items

### B1. Calendar popup scrolls into view on narrow screens — **shipped 2026-05-23**

Symptom (user, 2026-05-23): clicking a calendar row fires `gotoEventSession`,
which `fitBounds`/`flyTo`s the session and drops a popup. On narrow viewports
the popup overflows the visible map slice (overlapped by the left-controls
strip up top, or by the bottom-pinned message bar) and is partially hidden.

Approach:

1. Replace the `visibleMapPadding` constant top/bottom (80/60) with rect-based
   occlusion derived from `.left-controls`, `.panel`, and `.message`. On wide
   screens the left strip is a column → `left` pad grows. On narrow screens
   the strip spans width → `top` pad grows. The right panel below 760 px sits
   at the bottom → `bottom` pad grows.
2. Add `visibleMapRect()` returning the unoccluded map slice as a viewport
   rect, and `panPopupIntoView(popup, margin)` that on `moveend` measures the
   popup element vs. that rect and `map.panBy([dx, dy])` if any edge is
   outside.
3. Call `panPopupIntoView` from `gotoEventSession` after the popup is
   `addTo(map)` — inside `map.once('moveend', ...)` so the fly has settled.

Acceptance:

- [x] On a 1024 × 640 viewport (calendar expanded, layer panel docked
      right), clicking the G6 Cove Rally row leaves the session popup fully
      inside `visibleMapRect()` — verified at `popup.right=590, vis.right=604`
      and `popup.top=178, vis.top=0`.
- [x] On the existing 1280 × 820 verifier pass, the G6 popup still shows
      the session text and tag.
- [x] No regression on `playwright_verify_event_schedule.py` — existing G6
      jump assertion still passes; new narrow-viewport assertions pass too.
- [x] Pre-existing FAILs in `playwright_verify_search.py` ("multi-segment
      trail collapses to one result") confirmed unrelated to this change —
      they fail identically on master before the diff.

Notes:

- The fix also tightens `Popup.maxWidth` to the unoccluded slice width
  (clamped to [200, 280] px). On cramped layouts the default 280 px popup
  was wider than the available map slice, so pan alone could not bring it
  fully in view.
- Other popups (search, drawn POIs, layer click popups) still use the
  default maxWidth and no in-view pan. They have not been reported as
  problems; if they are, the helper is layered and can be applied at those
  call sites without further refactor.

Verifier: `mvp/scripts/playwright_verify_event_schedule.py` — extended with
a narrow-viewport pass (`SCREENSHOTS["narrow_jump"]`) and four rect
assertions against `visibleMapRect()` inlined into the verifier.

### B2. Search input — magnifier icon — **shipped 2026-05-23**

User dump: *"magnifing glass on search"*. Inline SVG inside the search shell
(`.search > .search-icon`), positioned absolutely on the left edge of
`#searchInput`. `pointer-events: none` keeps the input clickable through it;
`#searchInput` gained `padding-left: 30px` so the placeholder clears the glyph.

Acceptance:

- [x] SVG magnifier sits at the left of the search input, vertically centered,
      not clipping the placeholder.
- [x] Focus outline still visible (no change to `.search input:focus`).
- [x] Verifier asserts geometry: 14×14 px, inside the input's vertical bounds,
      left of the input's text edge.

Verifier: B2 section of `playwright_verify_event_schedule.py`. Screenshot at
`brain/output/playwright_event_schedule_search_icon.png`.

### B3. Edit panel collapsed state pinned bottom-right (desktop) + clean dock (mobile) — **shipped 2026-05-23**

User dump: *"make edit panel pop up from the bottom right. on mobile when
collapsed its floating in the middle."*

Read the request as "the panel lives at the bottom-right as a tray that
pops up when expanded." Implementation: the panel anchor flipped from
`top: 12px` to `bottom: 12px` on both desktop and mobile, with
`box-sizing: border-box` so `max-height` includes padding (was overflowing
by 28 px otherwise). Mobile reserve bumped to `calc(100vh - 280px)` so
the docked panel never overlaps the auto-collapsed calendar strip above
it. Mobile panel also gets `width: auto` so the right anchor wins over
the desktop `width: 380px`.

Acceptance:

- [x] Desktop: collapsed editor pins to bottom-right (`bottom <= viewport - 24`,
      `right <= viewport - 24`, `top >= viewport/2`). Verified at 1280×820:
      `top=752, bottom=808, right=1268`.
- [x] Mobile (500×760): panel `top=224` clears the auto-collapsed calendar
      bar (`bar.bottom=212`) and panel `bottom=704` sits 7 px above the
      message bar (`message.top=711`).
- [x] Toggling collapse / expand keeps the same horizontal anchor (right
      column on desktop, full width on mobile).

Verifier: `mvp/scripts/playwright_verify_presets.py` — extended the mobile
layout section to reload after resize (so the B4 auto-collapse kicks in),
added a wide-viewport collapsed-dock section with four geometry checks.

Caveat: with the calendar manually expanded on mobile, the bar grows to
~380 px and the panel top floats up into it. The user can scroll the
panel internally; the visual overlap is small and the alternative
(constraining the panel to ~200 px tall at all times) would be worse for
the layer-toggle workflow. Captured here in case a Pass 3 wants to
revisit.

### B4. Calendar sidebar — auto-collapse on mobile + time row check — **shipped 2026-05-23**

User dump: *"collapse calendar on mobile / narrow widths automatically"* and
*"calendar needs time"*.

Implementation:

- New init IIFE reads `aop_calendar_collapsed_v1`; if present uses the stored
  state without persisting; otherwise defaults to collapsed when
  `matchMedia('(max-width: 760px)').matches`, expanded otherwise.
- `setCalendarCollapsed(collapsed, persist=true)` writes the key when the
  caller is a user click; init passes `persist=false` so auto-defaults stay
  off until the user makes a choice.
- Removed the leftover unconditional `setCalendarCollapsed(false)` at the
  end of the calendar wiring block — it was clobbering the new init and
  persisting `'0'` on every load.
- Verified `props.window = session.time_label || ''` flows through the row
  template `<span class="calendar-time">…</span>` and that `.calendar-time`
  has weight 700 + color #756444 in the chrome CSS.

Acceptance:

- [x] At ≤ 760 px viewport on first load, the calendar card starts collapsed
      (verifier: `narrow_default`).
- [x] Manual expand persists (`stored: '0'`) and survives reload at the
      narrow viewport (verifier: `manual expand` + post-reload check).
- [x] On a wide viewport with no stored value, the calendar starts expanded
      and the auto-default does not persist.
- [x] `time_label` renders in all 12 calendar rows (verifier: per-row
      non-empty `.calendar-time` count).

### B5. Label typography pass — trace legibility first — **shipped 2026-05-23**

User dump: *"layers need text tweaking. currently trace has text hard to
read."*

Diagnosis: trace draws cream/yellow text (`#fff0b8`, `#fff4cf`) on the
SFWDA paper-map underlay, which is busy and varies tan→dark. The default
cream halo (`#f7f1e2`) provided no contrast in trace mode — text blended
into the underlay. Park / topo do not have this problem because they use
dark text on light backgrounds; the cream halo carries them.

Fix: in the trace preset paints, add a dark halo (`#15110d`) to the four
label layers that read cream/yellow text in trace:

- `roads-labels` — halo width 2.2 (matches the heavier road weights)
- `osm-named-labels` — halo width 2
- `activity-hotspots-labels` — halo width 1.8
- `visitor-context-labels` — halo width 2

Park and topo presets get explicit cream halo overrides for those same
layers so a `trace → park` switch reverts cleanly. Without the reset the
dark halo would persist under park's dark text and look terrible.

Acceptance:

- [x] Trace label layers readable against SFWDA paper-map underlay
      (verified visually in `brain/output/playwright_presets_trace.png` —
      "Park Entrance" and "Pavilion" callouts crisp against the busy map).
- [x] Park / topo reset the halo back to cream when re-entered.
- [x] Verifier asserts trace sets dark halo and park resets it on three
      label layers (roads, osm-named, activity-hotspots).

Verifier: `mvp/scripts/playwright_verify_presets.py` Trace section gains
4 dark-halo assertions; new `Park preset resets …` section asserts 3
revert paths.

Out of scope for this pass: weight / size tweaks on labels still using a
cream halo on a cream background in trace (none identified after this
pass — the four covered layers were the legibility hot-spots). A Pass 3
typography review can revisit if a new label layer lands.

### B6. Region callouts positionable — **closed 2026-05-23**

Closed via the visitor-context drag consumer of the find/move primitive in
`poi_editor_v2.md`. Kept in this card for the breadcrumb.

## Order

1. **B1** — in progress. Smallest user-visible bug; uses the same geometry
   helper everyone else will lean on.
2. **B4 + B2** — both touch the chrome surfaces above the map; group the diff.
3. **B3** — editor panel restyle.
4. **B5** — typography pass, last so it runs against settled chrome.

## Verification

- B1: `python3 mvp/scripts/playwright_verify_event_schedule.py` (server on
  8001). Extended with a narrow-viewport pass.
- B2 / B3 / B4: extend `playwright_verify_presets.py` or its sister scripts
  to capture the relevant layout screenshots; no new verifier scaffolding
  needed.

## Related work

- `_readme.md` Bucket B — triage source.
- `../01_mvp/event_schedule_layer.md` — owns the calendar sidebar.
- `../01_mvp/poi_editor.md` — owns the editor panel.
- `02_edit/poi_editor_v2.md` — shipped find/move primitive; B6 closes through
  it.
