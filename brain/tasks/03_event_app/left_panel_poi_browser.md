# Left Panel POI Browser

Date: 2026-05-25

TL;DR:
- New Sprint 03 card routed from `misc.md`.
- The viewer needs a browseable POI list in the left rail so a reader can scroll
  through locations, read a short context line, and click to fly the map to one.
- Reuse the existing `#calendarCard` `Park` tab footprint so the left rail does
  not grow.

#aop #03_event_app #viewer #left_panel #poi

-----

## Source

- `misc.md` 2026-05-24 loose bullet: *"need a poi viewer on the left side so
  that a user can browse locations and read about them. clicking will take them
  to the location on the map."*
- `left_panel_context_tabs.md` — the Events / Park / About tabs in
  `#calendarCard`. `Park` is currently a short copy block; this card replaces
  that copy with the POI browser.
- `../../research/viewer.md` — catalog of publishable POI layers (event-anchor,
  editor POIs, brand logos, visitor-context callouts, cemeteries, etc.).

## Job

Stand up a read-only POI browser inside the `Park` tab of the left context
card. Each row shows a short identity + caveat; click flies the map to the
POI and opens its popup (the same `bindPopup` path the click on the map
uses).

This is the read surface. CRUD, moderation, submissions all stay on
`full_loop_crud_upload_audit.md`.

## Scope (first cut)

- One scrollable list bound to a small set of `feature_kind`s: at minimum
  editor POIs, named-feature-tagged buildings (e.g. `#pavilion`), event
  anchors, and brand logos. Grouping convention should follow the feature-list
  panel in the right rail (`feature-list-group`).
- Each row: short name + optional kind/caveat line. Click flies the map; the
  click should also reveal the row's source layer in the right panel if it is
  hidden.
- Empty state when no layers are loaded.
- Mobile: list scrolls inside the card; left rail itself should not grow.
- localStorage: none. The browser is a derived view of layers already loaded.

## Out of scope

- POI editing, creation, deletion. Right-rail `Editor POIs` drawer still owns
  that surface.
- Submissions from non-staff visitors. Stays on
  `full_loop_crud_upload_audit.md`.
- New POI data sources. The list reads what the viewer already loads.

## Acceptance

- [ ] `Park` tab inside `#calendarCard` renders a scrollable POI list when at
      least one supported layer is loaded.
- [ ] Each row shows a name and a short context line; click flies the map and
      opens the bound popup.
- [ ] Empty state renders when no supported layers are loaded.
- [ ] Mobile width 360 px / 390 px keeps the left rail within the existing
      clear-of-panel height.
- [ ] A Playwright verifier (extend
      `mvp/scripts/playwright_verify_event_schedule.py` or new
      `playwright_verify_left_poi_browser.py`) asserts at least one row renders,
      click flies the camera, popup opens, and the source layer becomes visible.

## Verification

- Node inline-script parse: PASS.
- `python3 -m py_compile` the new/extended verifier.
- Run the verifier end-to-end against the 8001 viewer.
- Spot-check the viewer manually at desktop + 360 px + 390 px widths.

## Notes

This card is pending until prioritized. The misc.md routing block points
here so the loose user line has a home.
