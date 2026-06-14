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

### Addendum — 2026-06-13 (drawer OPEN/CLOSE persistence restored — the last deferred drawer piece)

User on the shipped read viewer: *"on load it seems search and clipboard is open on the left side. Can we
make it so that the open/close state is saved in a session/local storage? … localstorage is fine. also
persist the drawer height of the clipboard."* The drawer **open/close** state was the one piece still
severed — the addendum above restored the resize handles + their height; open/close stayed stateless, so
every reload snapped back to the hardcoded `{search:true, hot:false, cal:true}`. Now restored in
`viewer_core.js` **only**:

- Ported the lean form of `main.js`'s `LEFT_RAIL_DRAWER_KEY` logic into the read core's drawer block.
  `aop_left_rail_drawer_v1` stores `{search,hot,cal}` booleans; read on init (`readDrawerOpen` — tolerant
  of the old viewer's `{ open: {…} }` envelope on the **same** key, else falls to the existing default
  `{search:true, hot:false, cal:true}`), written on every tab click (`writeDrawerOpen`). Same inline
  try/catch get/set shape as the `aop_lr_card_height_v1` height pref right below it — **no** JSON-store
  helpers pulled in, and a first-time visitor's default layout is unchanged.
- **Clipboard height** was already persisting (`aop_lr_card_height_v1`, restored in the addendum above);
  this pass **verified it end-to-end** rather than re-asserting it.

**Verified by observation** (`verify_drawer_persist.py`, Playwright `:8001`, **18/18 PASS, 0 console/page
errors**): clean load shows the defaults (Search open, Hot closed, Clipboard open, no drawer key yet);
closing Search + opening Hot writes `{"search":false,"hot":true,"cal":true}`; keyboard-resizing the
clipboard handle grew `calendarBody` 240→**432px** and wrote `aop_lr_card_height_v1=432`; **after reload
both survived** — Search stayed closed, Hot stayed open, Clipboard stayed open and 432px tall. Screenshot
`brain/output/drawer_persist.png`. `node --check` clean.

**Shell bump owed + done:** `viewer_core.js` is in `sw.js` `SHELL_ASSETS` (served stale-while-revalidate),
bumped **v69 → v70** (`sw.js` VERSION + `#appVersion`). **UNCOMMITTED** (the user's git gate). This closes
the deferred "drawer persistence (polish)" item — open/close **and** height now persist.

### Addendum — 2026-06-13 (left-controls overlay ate map drags over its empty regions)

User: *"there is a draggable area where the user can pan and zoom the map. up top where the
search/hot/clipboard would be if it was expanded is not draggable. the Hand in the main field turns to a
pointer in the 'empty' area where it should still be handable."* Confirmed by observation, not reasoning.

**Root cause.** `.left-controls` is a fixed **340px-wide** `position:absolute` grid floating over the map,
and it (plus its grid gaps and the `.lr-drawer` row) had **default `pointer-events`** — so it intercepted
map pan/zoom drags over every *empty* part of its box and showed the arrow cursor (`auto`) instead of the
map's `grab` hand. Two empty regions in particular:
- **Collapsed drawer:** `lrContentCol.hidden=true`, but the `.lr-drawer` grid item still **stretches to the
  full 340px** while the visible icon column is only ~44px. The empty ~296px to the right of the icons was
  caught by `div#lrDrawer` (`cur=auto`) — exactly the "where the drawer would be if expanded" dead zone.
- **Pill-bar + grid gaps:** the 8px gaps between the three pills and the 8px grid gap between the pill-bar
  and the drawer were caught by `.left-controls` / `.pill-bar`, not the map.

Measured before the fix (Playwright `elementFromPoint` sweep over the box): only **29 / 986** probe points
reached the map; the rest hit overlay containers, many visibly empty with `cur=auto`.

**Fix (CSS only, `viewer.css`).** The standard MapLibre overlay pass-through: make the container
click-through and re-arm only the visible interactive cards —
`.left-controls { pointer-events:none }` + `pointer-events:auto` on `.pill`, `.lr-icon-col`,
`.lr-content-col`, `.util-install`, `.util-ios-hint` (leaf controls inherit `auto` from those cards;
search-results dropdown rides under `.lr-content-col`). The transparent gaps and the stretched-but-empty
drawer row now fall through to the map; the cream cards stay solid (a drag on the calendar can't pan the
map underneath). No JS, no markup, no `limiting code`.

**Verified by observation** (Playwright `:8001`): collapsed — all six right-of-icon points (200,120)…
(300,180) now return `canvas.maplibregl-canvas` `cur=grab`; expanded — pill-bar gaps (138,30)/(308,30) and
the pill↔drawer grid gap (100,55) now reach the map with `grab`. Controls unbroken: zoom/preset/3D pills
click, search input focuses, Events/POI/About tabs switch, the three drawer tabs toggle open/closed, and
the icon card stays a solid control (no drag leak). **Shell bump:** `viewer.css` rides `sw.js`
`SHELL_ASSETS` (SWR), bumped **v71 → v72** (`sw.js` VERSION + `#appVersion`). **UNCOMMITTED** (user's git gate).

## Notes

Built alongside; no commits without the user's git gate; `viewer.html` not in `sw.js` → no `#appVersion`
bump owed. Next: **Hot** (slice 5) drops into the drawer's third tab + wires `refreshHotButton`.
