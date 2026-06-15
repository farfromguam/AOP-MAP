# Views And Defaults

TL;DR:
- Park should open as the useful visitor/driver map: trails, roads, boundary, land cover, visitor context, in-park buildings, and water.
- Topo should be the same map plus relief: hillshade, contours, streams, springs, and buildings.
- Trace stays the workbench: imagery, SFWDA, OSM, buildings, and raw references.

#aop #views #defaults #layers #02_edit

-----

## Source

- `../../../../northstar/personas.md`
- `_readme.md` Bucket A
- `../../research/viewer.md`
- `../01_mvp/buildings_layer.md`
- `../01_mvp/visitor_context_callouts.md`
- `../01_mvp/event_schedule_layer.md`
- `../backlog/rc_event_mapping_backlog.md`

## Current state

The built-in `Park` preset is also the fresh-load default. Current default-on:

| Layer | Fresh HTML | Park | Topo | Trace | Read |
| --- | --- | --- | --- | --- | --- |
| Land cover | on | on | on | off | good |
| 9-patch land cover | on | on | on | off | good for region context |
| Roads | on | on | on | on | good |
| Visitor context callouts | on | on | on | off | good |
| Publishable trails | on | on | on | on | good; this is the driver map |
| Publishable boundary | on | on | on | on | good |
| Publishable trailheads | on | on | on | on | good |
| Drawn POIs | on | on | on | on | good while POIs are the working facility layer |
| Streams/waterbodies | off | off | on | off | mismatch for visitor utility |
| Springs/gages | off | off | on | off | fine; topo-specific for now |
| Building footprints | off | off | off | on | mismatch after feature-list work |
| Event schedule POIs/routes | off | off | off | off | correct; time-bound |
| Cemeteries | off | off | off | off | correct; searchable/special-case |
| Raw source layers | off | off | mostly off | on | correct |

Two mismatches matter:

- **Buildings are useful now.** The layer is raw FEMA context, but the feature
  list already limits the normal view to the four in-park footprints by default.
  The 198 outside-park buildings stay collapsed and unchecked.
- **Water is utility/safety context.** Drivers, marshals, visitors, and stage
  designers all care about creeks and water crossings. The data is raw NHD, but
  public-domain and useful enough to draw lightly in Park.

## Target defaults

| Layer group | Fresh / Park | Topo | Trace | Why |
| --- | --- | --- | --- | --- |
| Boundary, roads, land cover | on | on | roads on; land cover off | orientation |
| Trails and trailheads | on | on | on | driver map first |
| Drawn POIs | on | on | on | current bridge for facilities, gates, hazards |
| Visitor context callouts | on | on | off | region support context, not tracing evidence |
| Buildings | on | on | on | pavilion/facility orientation; per-feature filter controls noise |
| Streams/waterbodies | on | on | off | useful in Park; relief-critical in Topo |
| Springs/gages | off | on | off | too specialist for Park, useful in Topo |
| Event schedule POIs/routes | off | off | off | selecting calendar/search turns it on |
| Cemeteries | off | off | off | special context; search/panel can reveal it |
| Activity/synthetic activity | off | off | off | evidence/test layers |
| Satellite/NAIP/SFWDA/OSM/acquisition indexes | off | off | on where relevant | source/reference workbench only |

## Exact code changes

In `website/index.html`:

- Fresh HTML checkboxes:
  - set `#showWater` to `checked`
  - set `#showBuildings` to `checked`
- `BUILT_IN_PRESETS.park.toggles`:
  - `showWater: true`
  - `showBuildings: true`
  - leave `showSprings: false`
- `BUILT_IN_PRESETS.topo.toggles`:
  - `showBuildings: true`
  - keep `showWater: true`
  - keep `showSprings: true`
- `BUILT_IN_PRESETS.trace.toggles`:
  - no change

Do not change the zoom buttons yet. `Region`, `Park`, and `Pavilion` are camera
presets today. Wiring them to layer changes would be surprising unless we
rename the control model. If Region feels too cluttered after Park gets water
and buildings, add a separate `Approach` / `Region` layer preset later.

## Docs to update with the code

- `../../research/viewer.md`
  - inventory defaults for `Streams & waterbodies` and `Building footprints`
  - UI preset summary for Park and Topo
- `../01_mvp/buildings_layer.md`
  - outcome line from "default OFF" to "default ON in Park/Topo, filtered by
    feature-list visibility"
- `../../../../northstar/personas.md`
  - optional: change "Candidate policy" to "Proposed policy" once shipped

## Verification

Run with a clean viewer profile or clear `aop_viewer_preset_settings_v1`.
Saved custom presets override built-ins and can hide whether the built-in
defaults changed.

- `python3 mvp/scripts/playwright_verify_presets.py`
- `python3 mvp/scripts/playwright_verify_buildings.py`
- `python3 mvp/scripts/playwright_verify_water.py`
- Optional smoke: load the viewer fresh and confirm the Park preset draws the
  four in-park building footprints plus streams/waterbodies without enabling
  springs or outside-park buildings.

## Acceptance

[x] Fresh load / Park preset shows water and in-park buildings.
[x] Topo preset shows buildings in addition to hillshade, contours, streams,
    and springs.
[x] Trace preset still shows the tracing workbench and does not inherit Park's
    visitor-context defaults.
[x] Event schedule remains default-off until a calendar row, search result, or
    toggle turns it on.
[x] Cemeteries remain default-off, but search and panel reveal still work.
[x] Viewer catalog matches the shipped defaults.

## Shipped 2026-05-23

`website/index.html`:

- Fresh HTML `#showWater` + `#showBuildings` flipped to `checked`.
- `BUILT_IN_PRESETS.park.toggles`: `showWater: true`, `showBuildings: true`,
  `showSprings: false`.
- `BUILT_IN_PRESETS.topo.toggles`: `showBuildings: true` (water/springs
  already on).
- `BUILT_IN_PRESETS.trace.toggles`: unchanged.

Verifiers:

- `mvp/scripts/playwright_verify_water.py` — PASS, 0 console errors.
  Initial-state assertions now check water toggle starts ON and water layers
  start visible; springs stays off. `set_toggle` adopted the .checked +
  change-event pattern from `playwright_verify_event_schedule.py` so the
  collapsed `panel-section` no longer blocks the spring-toggle click.
- `mvp/scripts/playwright_verify_buildings.py` — PASS, 0 console errors. Same
  initial-state flip + same `set_toggle` patch (was timing out clicking
  `#showBuildings` while the Source-layers section stayed collapsed).
- `mvp/scripts/playwright_verify_presets.py` — A2 assertions PASS (Park
  defaults water + buildings ON, springs OFF; Topo defaults buildings ON).
  Pre-existing FAIL ("land-cover outputs live under Derived layers" — the
  assertion lists `showVisitorContext` which now lives under `publishable`)
  and pre-existing timeout at the trails inline-tuning step are unchanged by
  this card.

Bucket E (`../_readme.md`) closes through this card — buildings default-on
plus the in-park feature-list filter is the resolution. The "outside-park
prune" worry resolved earlier through `poi_editor_v2.md`.
