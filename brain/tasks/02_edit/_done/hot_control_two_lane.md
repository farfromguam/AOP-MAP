# Two-Lane Hot Control

Date: 2026-05-24

TL;DR:
- Replace the single "event unless empty, then heatmap" hot button with a two-lane control: **Event** and **Trails**.
- Event hot and trail heat are different jobs. Both should be directly reachable when both data sources exist.
- Default selection follows urgency, but user selection wins until they choose another lane.

#aop #02_edit #hot_button #heatmap #personas #implementation

-----

## Source chain

- `../../northstar/personas.md`
- `hot_button_heatmap_review.md`
- `_done/left_hot_button.md`
- `../01_mvp/_done/activity_hotspots.md`
- `tasks.md` user line: "need a dedicated hot button on the left. fire icon???"

## Product decision

"Hot" has two meanings:

1. **Event hot:** something scheduled is live, starting soon, or next.
2. **Trail hot:** activity evidence shows where rigs spent time on trail.

The old single-button model forced trails to be a fallback only when the
schedule was empty. That makes trail-first users fight the event schedule.

New model: a shared **Hot now** control with two lanes:

| Lane | Job | Action |
| --- | --- | --- |
| Event | "What scheduled thing needs me?" | Selects the calendar session, opens the popup, and flies to the tag-resolved event location. |
| Trails | "Where is the trail activity?" | Turns on activity hotspots and flies to the hotspot target. |

## Selection rule

- If an event is live or starts within 30 minutes, Event is selected by default.
- If no event is live/imminent and hotspots exist, Trails is selected by default.
- If hotspots do not exist but a future event exists, Event is selected.
- If the user chooses a lane, keep that lane selected while it remains available.
- If Trails is selected and an event becomes live, badge/highlight Event, but do not steal selection.

## Placement

Left chrome, below the map/zoom presets and above the calendar.

Reason: the control is an on-map action surface, not a right-panel layer
configuration. It should remain visible even when the calendar is collapsed.

## Copy

- Header: `Hot now`
- Event live: `Live event`
- Event imminent: `Starting soon`
- Event future: `Next event`
- Event unavailable: `No event`
- Trail lane: `Trail activity` (originally shipped as `Trail heat`;
  renamed 2026-05-24 per critique-C item in
  `../../03_event_app/sprint_02_critique_followups.md`)
- Trail detail: `Where rigs spent time` (originally `Activity evidence`)

Avoid "heat" / "live heat" wording until the data is recent, aggregated, and
privacy-reviewed.

## Acceptance

- [x] Event lane shows live/imminent/next/no-event state.
- [x] Trails lane is visible and clickable when activity hotspots are loaded,
      even while an event schedule exists.
- [x] Live/imminent Event is selected by default.
- [x] Same-day or cross-day future Event does not force selection away from
      Trails when hotspots are available.
- [x] Clicking Event runs the existing `gotoEventSession` path.
- [x] Clicking Trails turns on `showActivityHotspots` and flies to hotspots.
- [x] Clearing schedule leaves Trails usable instead of hiding the hot control.
- [x] Verifier covers both lanes.

## Implementation notes

- Keep `#hotButton` as the Event lane so existing event verifier intent remains
  recognizable.
- Add `#hotTrailButton` as the Trail lane.
- Keep using the existing schedule tick and visibility-change refresh.
- Keep `computeHotButtonTarget()` for the event target decision.
- Track a short-lived preferred lane in JS; do not persist it yet.

## Shipped 2026-05-24

Implemented in `../../../website/index.html`.

- `#hotControl` now sits in the left chrome below zoom presets and above the
  calendar.
- `#hotButton` is the Event lane. It shows `Live event`, `Starting soon`,
  `Next event`, or `No event`; clicks still use `gotoEventSession`.
- `#hotTrailButton` is the Trails lane. It is available whenever activity
  hotspots are loaded; clicks turn on `showActivityHotspots` and fit to the
  hotspot target.
- Selection follows the card rule: Event for live/imminent, Trails for
  non-imminent future schedules when hotspots exist, and user choice wins while
  that lane remains available.

Verification:

```text
node inline-script parse: PASS
python3 -m py_compile mvp/scripts/playwright_verify_event_schedule.py: PASS
python3 mvp/scripts/playwright_verify_event_schedule.py: RESULT PASS
```

The Playwright pass covered live, imminent, same-day future, cross-day future,
direct Trails click while a schedule exists, empty-schedule Trails behavior, and
0 console errors.
