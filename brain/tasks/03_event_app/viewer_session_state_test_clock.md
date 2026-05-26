# Viewer Session State + Test Clock

Date: 2026-05-26

TL;DR:
- Route `misc_2.md` into an executable viewer-polish card.
- Add a staff/test clock control for event-state styling, a reset-to-new-user
  affordance, and pocket-map persistence for the viewer's current context.
- Keep this as static-viewer state. It is not the Sprint 03 CRUD/upload app.

#aop #03_event_app #viewer #state #clock #hot

-----

## Source

- `misc_2.md`, 2026-05-26.
- Existing event schedule clock hook in `website/index.html`:
  `?clock=YYYY-MM-DDTHH:MM`.
- Existing localStorage keys centralized near the top of the viewer script.
- `left_rail_collapse_tabs.md` for the left-rail drawer and calendar-height
  persistence pattern.

## Shipped 2026-05-26

- Right panel now has a `Session tools` section with date/time inputs, `-1d`,
  `+1d`, `-1h`, `+1h`, `Set`, `Now`, `Clear`, and `Reset viewer` controls.
- The virtual clock uses the same runtime path as `?clock=YYYY-MM-DDTHH:MM`,
  persists in `aop_virtual_clock_v1`, and labels the UI as `Test clock ...`
  whenever wall time is overridden.
- Pocket-map state persists in `aop_viewer_session_state_v1`: active preset,
  active left tab, search query, and selected event session. Existing drawer
  and calendar-height keys continue owning those surfaces.
- `Reset viewer` clears every viewer-owned localStorage key, closes transient
  popups/highlights, resets Park/default view/default left tab/default drawer,
  and returns the clock to wall time.
- Landmark-hot decision recorded: keep landmarks in the POI/search context for
  now, not as a permanent third Hot lane. Event urgency and trail activity stay
  the two hot meanings until there is a specific "hot landmark now" rule.

Verification:

- `node -e ... new Function(script)` inline script parse.
- `python3 -m py_compile mvp/scripts/playwright_verify_session_tools.py mvp/scripts/playwright_verify_left_rail_drawer.py mvp/scripts/playwright_verify_event_schedule.py mvp/scripts/playwright_verify_presets.py`
- `git diff --check`
- `python3 mvp/scripts/playwright_verify_session_tools.py`
- `python3 mvp/scripts/playwright_verify_left_rail_drawer.py`
- `python3 mvp/scripts/playwright_verify_event_schedule.py`
- `python3 mvp/scripts/playwright_verify_presets.py`

## Job

Make the static viewer behave like a folded paper map pulled out of a pocket:
the user should come back to the same useful context after a reload, and staff
should be able to advance virtual time while testing live calendar and hot
states.

## Scope

### 1. Virtual Time Control

Add a right-panel staff/testing control that drives the same runtime path as
the current `?clock=` fixture.

Minimum useful shape:

- Date input.
- Time input or hour stepper.
- Buttons for `-1d`, `+1d`, `-1h`, `+1h`, and `Now`.
- Clear/test-clock reset back to wall clock.
- Refresh calendar row states, countdown, and hot lanes immediately after a
  change.

Persisting test time is optional. If it persists, make the UI visibly say it is
using a test clock so nobody mistakes it for wall time.

### 2. Reset New-User Experience

Add a bottom-right or panel-level reset affordance that clears viewer-owned
localStorage and returns the viewer to first-run defaults.

Known keys today:

- `aop_calendar_height_v1`
- `aop_calendar_collapsed_v1` (legacy cleanup)
- `aop_left_rail_drawer_v1`
- `aop_virtual_clock_v1`
- `aop_viewer_session_state_v1`
- `aop_visitor_context_overrides_v1`
- `aop_brand_logos_overrides_v1`
- `aop_feature_visibility_v1`
- `aop_feature_tags_v1`
- `aop_feature_tags_seeded_v1`
- `aop_editor_pois_v1`
- `aop_viewer_preset_settings_v1`

The reset should then apply the default Park preset, default camera, default
left tab, default drawer cards, and clear any selected calendar row / popup.

### 3. Pocket-Map Persistence

Persist the viewer context that users reasonably expect to survive a reload:

- active map preset (`park`, `topo`, `trace`)
- left drawer cards open/closed
- active left context tab (`Events`, `POI`, `About`)
- calendar body height
- selected calendar event, when the session still exists
- search panel open state and maybe query/results if that proves useful

Do not persist transient animation or pointer state.

### 4. Third Hot Target: Landmarks

Decide whether "landmarks" is:

- a third hot lane beside Event and Trail activity, or
- a shortcut into the existing POI tab / landmark search group.

Suggested first answer: make it a POI/landmark shortcut, not a permanent third
hot lane. The current two-lane hot control has clear meanings: event urgency
and trail activity. Landmarks are browse/navigation context and probably belong
with the POI tab unless a specific "hot landmark now" rule appears.

## Acceptance

- [x] Staff can set a virtual date/time from the right panel and the calendar
      live/upcoming/past styling updates without reloading.
- [x] Staff can advance virtual time by days and hours.
- [x] Staff can clear the virtual clock and return to wall time.
- [x] Reset-to-new-user clears every viewer-owned localStorage key and returns
      the visible viewer to first-run defaults.
- [x] Active preset, active left tab, drawer open/closed state, calendar
      height, and selected calendar row survive reload when appropriate.
- [x] Landmark-hot decision is recorded and either implemented or explicitly
      deferred.

## Out Of Scope

- Event CRUD, upload intake, moderation, or contributor identity.
- Offline/PWA persistence.
- Server-side account preferences.
