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
