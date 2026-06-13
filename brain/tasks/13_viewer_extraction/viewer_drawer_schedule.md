# Slice 3 — Left-rail drawer + Calendar/Events (schedule)

TL;DR:
- Stand up the **left-rail drawer** (the two-column icon+content shell) and port the **Calendar/Events
  schedule** into it: the clock-driven session state machine (LIVE / SOON / countdown), the row→fly+popup,
  the `event-schedule` source + 4 map layers, the shared `event_schedule_geojson.js` resolver, and the
  About tab. Search moves **into** the drawer.
- Same extraction discipline: sever the editor seams — the **virtual-clock Session-tools UI** (keep only
  the `?clock=` fixture + wall clock), the `event-schedule` checkbox toggle (drive layers via
  `setLayerVisibility`), all session-persistence (`persistViewerSessionState`), the drawer
  open/height localStorage, and the editor feature-list registration.
- Built alongside; `index.html`/`main.js` untouched. Verified by observation (with `?clock=` fixtures to
  exercise pre / live / post states).

#aop #sprint #13 #viewer #drawer #schedule #calendar #slice

-----

## Why this groups the drawer with the schedule

The drawer's main content **is** the schedule — there's no clean "drawer shell" to ship without it. And
the drawer is the shared chrome Hot (slice 5) and Search both sit in, so building it here moves Search in
and leaves Hot a drop-in next. The user's call (2026-06-13): implement hot & schedule **before** a styling
polish pass — because the drawer chrome is shared, so styling a bare search box now is throwaway.

## What to build

**`website/viewer.html`** — replace the bare `.search-shell` with the full `.lr-drawer` (icon-col +
content-col, from `index.html:84-197`): Search tab/panel (the search box moves in), Calendar tab/panel
(the `calendar-card` with Events + About sub-tabs). **Defer:** the Hot tab (slice 5), the POI sub-tab
(slice 4), and the per-card resize handles (polish). Load `./js/event_schedule_geojson.js` before
`viewer_core.js`.

**`website/css/viewer.css`** — pull the `lr-*` drawer rules + the calendar / left-tab / countdown / badge
/ info-panel rules from `app.css` (129-207, 276-293, 718-816), each block citing source lines; add the
tokens they use (`--brown-mid`, `--brown-dark`, `--cream-border`, `--hairline`, `--moss-soft`,
`--moss-tint-hover`, `--cream-wash-hover`, `--rust`, `--tab-h`).

**`website/js/viewer_core.js`** — port from `main.js`:
- the `?clock=` fixture (`parseLocalClockString`/`clockParamDate`) + `eventScheduleNow` reduced to
  `(urlClock || wall)`;
- the calendar clock machine (`parseEventAnchorFriday`→`resolveCalendarAnchorSat`,
  `eventScheduleStartFromAnchor`, `computeCalendarScheduleEdges`, `computeCalendarState`,
  `eventScheduleFormatMinutes`, `refreshEventScheduleSessionStates`, `ensureEventScheduleStateTicker`,
  `scrollCalendarCurrentRowIntoView`);
- `renderEventSchedule`, `detailRows`/`formatListProperty`, the popup-fit helpers
  (`visibleMapRect`/`visibleMapPadding`/`visibleCenterOffset`/`panPopupIntoView`/`closeAllMapPopups`/
  `firstCoordinate`/`sessionPopupHtml`), `gotoEventSession`, `setLeftTab`, `renderAbout`;
- the `event-schedule` source + the 4 layers (routes/route-labels/anchor-points/anchor-labels) via the
  shared `window.AOPEventSchedule.eventScheduleToGeojson(config)`; `indexFeatures` the anchors (search);
- the drawer reflow (`lrRender` floating-tab layout + tab click) with `LR_CARDS = ['search','cal']`.

**Sever:** virtual-clock UI + stored clock (keep `?clock=`), `persistViewerSessionState`, the
`eventScheduleToggle` checkbox (→ `setLayerVisibility` on the 4 event layers), drawer
open/height persistence, `registerFeatureListLayer`, and the `refreshHotButton` call (its
`typeof===function` guard already no-ops without Hot).

## Acceptance

- [x] Drawer renders; Search works inside it; Calendar tab shows the schedule rows; About tab renders.
- [x] `?clock=` fixtures exercise the states: a during-event clock shows a **LIVE** row; a pre-event clock
      shows the **countdown**; rows carry SOON badges. Observed.
- [x] Clicking a session row flies the camera, opens its popup, and pulses the highlight; the 4 event
      layers become visible.
- [x] **0 console/page errors**; `index.html` untouched; no editor seam carried.
- [x] Line-cost recorded.

## Verification

- Playwright with `?clock=2026-06-20T12:00` (during) and default (pre): assert a `data-session-state="happening"`
  row exists under the live clock, the countdown shows pre-event, row-click flies + opens a popup +
  highlight visible, drawer tabs switch. Screenshot. 0 console errors.
### Done — 2026-06-13 (slice 3 shipped, verified by observation)

**Files (built alongside; `index.html`/`main.js` untouched):** `viewer_core.js` 1249 → **1848** (+599) ·
`viewer.html` 75 → 135 (+60, the drawer) · `viewer.css` 96 → 175 (+79, drawer + calendar rules + tokens).
`viewer.html` now loads `./js/event_schedule_geojson.js` before `viewer_core.js`.

**Verification (real running system).** `/tmp/verify_viewer_schedule.py`, with `?clock=` fixtures:
**15/15 PASS, 0 console errors.** Observed — **pre-event** (default wall clock 2026-06-13): calendar
renders 13 rows, `data-calendar-state="pre"`, the **"GATES OPEN IN 6D 5H"** countdown shows. **During
event** (`?clock=2026-06-20T14:00`): `data-calendar-state="live"`, "Proving Grounds" (13:30) stamped
`happening` with a **LIVE** badge, "King of the Hill" (15:00) stamped `upcoming_next` with a SOON badge;
clicking the live row opens a map popup; About tab renders 1245 chars; drawer tabs toggle their panels.
Screenshots `viewer_schedule_{pre,live}.png` in `brain/output/` — the drawer's floating-tab reflow, the
calendar, the badges, the popup, and the event anchor pulse all render correctly.

**Line-cost.** +599 in `viewer_core.js`: ~140 the clock state machine
(`parseEventAnchorFriday`→`resolveCalendarAnchorSat`, `eventScheduleStartFromAnchor`,
`computeCalendarScheduleEdges`/`State`, `refreshEventScheduleSessionStates`, ticker, formatters), ~35
`renderEventSchedule`, ~110 the popup-fit helpers
(`visibleMapRect`/`visibleMapPadding`/`visibleCenterOffset`/`panPopupIntoView`/`closeAllMapPopups`/
`sessionPopupHtml`/`firstCoordinate`/`detailRows`/`formatListProperty`), ~55 `gotoEventSession`, ~15
`setLeftTab`, ~50 `renderAbout`, ~95 the `event-schedule` source + 4 layers + `indexFeatures` + the
load/auto-fly block, ~40 the drawer reflow + tab/calendar/About wiring. The drawer + schedule is the
heaviest control yet, but it's the read product's "what's on now" surface — load-bearing.

**What was severed (editor seam).** The Session-tools **virtual-clock UI + its localStorage** — kept only
the `?clock=` fixture; `eventScheduleNow` reduced to `(urlClock || wall)`. The **`eventScheduleToggle`
checkbox** — `gotoEventSession` now drives the 4 event layers via `setLayerVisibility` (selection-driven,
default-off, never preset-driven, so `PRESET_LAYERS` is untouched). **Every `persistViewerSessionState`**
(active session / left tab / search). The **drawer open + height localStorage** and the
`lrOpenCard`/`lrCloseCard` external hooks. The per-card **resize handles**. `registerFeatureListLayer`.
The `refreshHotButton()` call is kept verbatim behind its `typeof === 'function'` guard — a safe no-op
until Hot lands (slice 5).

**Reuse, not a second engine.** The document→GeoJSON transform is the **one shared resolver**
(`window.AOPEventSchedule.eventScheduleToGeojson`) — loaded as a `<script>`, not re-ported. The session
highlight reuses the slice-2 `search-highlight` source + `pulseHighlight`. Event-anchor search reuses
`indexFeatures` (its `layersFor` returns the 4 event layer ids).

**Scope deferred (documented):** the **Hot tab** (slice 5 — drops into the drawer's third icon + wires
the already-guarded `refreshHotButton`); the **POI sub-tab** (slice 4 — needs `poiPopupHtml`/the POI
index); the per-card **resize handles** + drawer **persistence** (polish). The drawer carries two cards
(Search, Calendar); `LR_CARDS = ['search','cal']`, icon column reserves 2 tab-heights.

**Owed / git gate.** UNCOMMITTED (the user's gate). `viewer.html` still not in `sw.js` → **no
`#appVersion` bump owed.** Next per the slate: **Hot** (slice 5), then POI (slice 4), then PWA/swap.

### Addendum — 2026-06-13 (deferred resize handles RESTORED into index.html)

User: *"review the old_index. there is a schedule/clipboard draggable area that we want to restore
into our newer lighter index viewer."* The deferred item above (the per-card **resize handles** + their
**height persistence**) — the draggable grip under the schedule "clipboard". Restored into the shipped
read viewer (now `index.html`, post-swap):

- **`index.html`** — the 3 handles back under each card body (`calendarResizeHandle` / `poiResizeHandle` /
  `aboutResizeHandle`), `role="separator"` + `aria-controls`/`aria-valuenow`, ported verbatim from
  `old_index.html`.
- **`viewer.css`** — `.lr-resize-handle` (+ `::before` grip, `:active`, `:focus-visible`) from
  `app.css:804-809`; the phone default `--lr-card-body-height: 160px` added to the `≤760px` media query
  (`app.css:868`).
- **`viewer_core.js`** — `initLrCardResize()` ported from `main.js:1370-1452`: pointer drag + keyboard
  (Arrow/Page/Home) drive the shared `--lr-card-body-height` var on `.lr-content-col`, so all three bodies
  stay equal across tab switches. **Reuse, not a second engine:** the existing `lrRender` reflow is exposed
  as `window.lrReflow` (the exact contract the ported code calls) instead of building a new reflow; reuses
  `scrollCalendarCurrentRowIntoView`. **Persistence kept** (localStorage `aop_lr_card_height_v1`, a tiny
  inline try/catch get/set) so a grown schedule survives reload — the one session pref the read core keeps,
  everything else stays stateless.

**Verified by observation** (`/tmp/verify_schedule_resize.py`, Playwright on `:8001`, **7/7 PASS, 0 console
errors**): handle visible; drag +160px grew `calendarBody` 240→**400px**; `aria-valuenow` + the CSS var
track to 400; POI + About bodies both read 400px and carry their own handle; **400px persisted across
reload**. Screenshots `brain/output/schedule_resize_{events,poi}.png`. `node --check` clean.

**Shell bump owed + done:** `index.html` + `viewer.css` + `viewer_core.js` are in `sw.js` `SHELL_ASSETS`,
so bumped **v66 → v67** (`sw.js` VERSION + `#appVersion`). **UNCOMMITTED** (the user's git gate).

## Notes

Built alongside; no commits without the user's git gate; `viewer.html` not in `sw.js` → no `#appVersion`
bump owed. Next: **Hot** (slice 5) drops into the drawer's third tab + wires `refreshHotButton`.
