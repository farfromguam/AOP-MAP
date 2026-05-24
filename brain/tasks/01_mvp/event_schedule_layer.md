# Event Schedule Layer

Status: DONE

Date: 2026-05-22

## Purpose

Move the sister-event schedule proposal out of loose handoff text and into the
viewer sidebar without baking coordinates into every row.

The schedule remains proposed planning context. It is not an official AOP event
calendar until AOP confirms dates, locations, staffing, route choices, and
facility use.

## Source

- `brain/handoff/event_schedule_context_20260522.json`
- `brain/northstar/whats_this_for.md`
- `brain/tasks/backlog/rc_event_mapping_backlog.md`
- Sister-event vocabulary references captured in the handoff: Pro-Line By The
  Fire, RECON G6 / RG6, and AxialFest.

## Implementation

- Added `website/data/aop_event_schedule.json` as the editable source object.
- The JSON has:
  - `locations`: tag dictionary for reusable locations such as `#pavilion`,
    `#registration`, `#observed-trailhead`, `#north-technical`, and
    `#photo-waypoint`.
  - `sessions`: schedule rows with `date_label`, `time_label`, `title`,
    `location_tag`, and optional `route_tags`. As of 2026-05-24 each session
    also carries `start_local` (24h `HH:MM` local time). The viewer formats
    it as 12-hour clock time and composes the calendar row's `window` as
    `"5:00 PM · Evening"` (clock · day-part). `time_label` stays as the
    day-part vocabulary the sister-event research produced; `start_local`
    unblocks the Sprint 02 Bucket A3 left-hot-button "imminent ≤ 30 min"
    rule (see `../02_edit/left_hot_button.md`). Helpers:
    `formatEventStartLocal()` + `composeEventWindowLabel()` in
    `website/index.html` next to `eventScheduleToGeojson`.

## Current-time indicator (2026-05-24)

The calendar sidebar now classifies each session row against "now" and
tints the two active rows. Picked from a 4×4 spawn of style variations
(`B4-info`, the badges-carry-timing variant).

- **Clock source.** `eventScheduleNow()` reads `?clock=YYYY-MM-DDTHH:MM`
  as a local datetime when present (test fixture / Playwright verifier);
  otherwise the system wall clock. A fixed-clock URL is the contract the
  upcoming left-hot-button verifier already plans to use.
- **Date anchor.** Each session's `date_label` ("Friday"/"Saturday"/
  "Sunday") is anchored against the most-recent Saturday on/before now
  (Fri = Sat−1, Sun = Sat+1). Sessions assume a 90-minute default duration
  because the schema has no `end_local` field.
- **Classification.** Each `<li>` carries `data-session-state` of
  `past` | `happening` | `upcoming_next` | `future`. Exactly one row is
  `upcoming_next` (the earliest session with `session_start > now`).
- **Treatment.** Happening row: sage `#dde2cf` background, 3px rust
  inset left bar, bold title, top-right `LIVE · 45m LEFT` badge
  (solid rust, cream text, time-remaining updates every 60s). Upcoming-
  next row: sand `#ecd9b1` background, 3px brown-dark inset left bar,
  top-right `SOON · IN 45m` badge (solid brown-dark, cream text,
  countdown updates every 60s). Past rows: opacity 0.5. No countdown
  banner, no blur/glow, no animations.
- **Tick.** Recompute every 60s and on `visibilitychange`.
- **Code.** CSS at lines 188-199, JS engine (`eventScheduleNow`,
  `eventScheduleAnchor`, `eventScheduleFormatMinutes`,
  `refreshEventScheduleSessionStates`, `ensureEventScheduleStateTicker`)
  at lines 3545-3650 in `website/index.html`; render hook in
  `renderEventSchedule` emits `data-session-day` + `data-session-start`
  per `<li>` and calls the refresh after innerHTML swap.
- **Demo posture.** At `?clock=2026-05-23T14:15`, `sat-proving-grounds`
  (13:30) is `happening` showing `LIVE · 45m LEFT`; `sat-king-of-hill`
  (15:00) is `upcoming_next` showing `SOON · IN 45m`. Fri × 3 + Sat 8 AM
  + Sat 9 AM are `past`.
- **Status.** Shipped as "simple enough and has the info" — the user
  flagged it may not be 100% the final aesthetic; revisits acceptable
  if the look needs tuning. Hot-button (A3) overlap noted in
  `../02_edit/left_hot_button.md`.
  - aliases: `#registration` resolves to `#pavilion`; `#pavillion` is accepted
    as a misspelling alias for `#pavilion`.
- A location's `coordinates` field is optional as of Sprint 02 Bucket D
  (2026-05-23). When absent, the viewer resolves coordinates from a
  per-feature `#tag` binding in the shared feature list panel
  (`aop_feature_tags_v1`). Explicit JSON `coordinates` still win when
  present. The `#pavilion` entry now ships with no coordinates and resolves
  through the 1010 Ellis Cove Rd building footprint (seeded on first load).
  See `brain/tasks/02_edit/named_feature_tagging.md`.
- `website/index.html` now fetches that JSON, resolves tags into an in-memory
  GeoJSON source, and renders:
  - sidebar schedule rows from the JSON sessions,
  - `event-session-routes`,
  - `event-route-labels`,
  - `event-anchor-points`,
  - `event-anchor-labels`.
- Selecting a schedule row turns on the default-off `Event schedule POIs`
  overlay, flies to the tagged point/route, flashes the highlight layer, and
  opens a popup. Before the popup opens the helper `closeAllMapPopups()` runs
  every existing popup's native close button so a schedule jump leaves the
  viewer with one fresh popup, not a stack of stale ones.
- The fly/fitBounds path uses `visibleMapPadding()` + `visibleCenterOffset()`
  to bias the camera toward the visible slice of the map (the strip between
  `.left-controls` and the right `.panel`). Without it, a schedule jump
  centered the target geographically — which placed the popup under the
  layer panel, so the "expanded item" was clipped. The helpers read the
  overlay widths from the DOM so the math survives layout changes.

## Verification

- Added `mvp/scripts/playwright_verify_event_schedule.py`.
- Updated `mvp/scripts/playwright_verify_presets.py` so the preset smoke check
  expects the JSON-driven schedule rows instead of the older three broad
  windows.

## Caveats

- Activity hotspots and observed trail references are raw evidence, not official
  route authority.
- The pavilion anchor is user-confirmed, but the underlying FEMA footprint is
  still raw reference context.
- Do not promote these event features into publishable layers without a source
  register decision and AOP confirmation.
