# Left Hot Button (Sprint 02 Bucket A3)

TL;DR:
- A single button on the left chrome that answers "what's hot right now?" without the user reading the calendar.
- Three states: **hot-now**, **coming-up**, **heatmap-fallback**. The button always has an action; the state and icon change with the schedule.
- Spec is locked, build is not started. Card written 2026-05-23 from the personas.md decision; A3 originally deferred while H (code-health Pass 3) is in flight.

#aop #tasks #02_edit #left_hot_button #views

-----

## Source chain

- `personas.md` — "Left hot button" row carries the locked decision.
- `_readme.md` — Bucket A3 triage.
- `tasks.md` — original line: *"need a dedicated hot button on the left. fire icon???"*
- `../01_mvp/event_schedule_layer.md` — schedule data shape + resolver.
- `named_feature_tagging.md` — tag-resolved location lookup (`#pavilion` etc.).
- `../01_mvp/activity_hotspots.md` — heatmap fallback source.

## The decision (locked 2026-05-23)

The user direction across three follow-ups:

1. *"if an event is about to happen then thats hot otherwise the trail spots are heatmap hot"*
2. *"we should be able to see a saturday hot evening item coming up if one were scheduled"* — look-ahead across days.
3. *"imminent is 30 minutes"* — threshold.

Plus the demo correction: today is Saturday (brain date 2026-05-23).

That gives three states:

| State | Trigger | Action | Visual |
| --- | --- | --- | --- |
| **Hot-now** | A session is live, OR starts within 30 minutes | Fly to that session's tag-resolved location; open its popup; calendar row highlighted | Button glows; icon = live/hot |
| **Coming-up** | No session imminent, but one is on the schedule somewhere in the future (today or any later day) | Fly to the next session's tag-resolved location; open its popup; chrome shows a countdown ("Saturday 6:00 PM — in 4h 12m") | Button is colored but not glowing; icon = clock / soft hot |
| **Heatmap-fallback** | Schedule empty, OR every session is in the past | Fly to / highlight the activity-hotspots layer; force `showActivityHotspots = true` and `showActivityHotspotsLabels = true`; bound the view to the densest hotspot cluster | Button is neutral; icon = heatmap / dotted region |

`imminent_window = 30 minutes`. No other thresholds carry meaning — "coming up" extends across days, bounded only by the schedule itself.

## Why three states, not two

A two-state model ("event or nothing") goes dead the moment there is no live session. A 30-minute window is short — most of any day sits outside it. So the button needs a default that still does something useful, hence heatmap-fallback.

But the coming-up middle state matters because the button is for **people on the property right now**. If it's Friday evening and the next session is Saturday morning, the button shouldn't pretend nothing is happening — it should already be pointing at the right place with the right countdown. That's the *"we should be able to see a saturday hot evening item coming up if one were scheduled"* clarification.

## Scope

### What it does

- Live read on `window.eventSchedule` (the schedule JSON the existing sidebar consumes) every 60 seconds or on visibility-change.
- Resolves the active/next session through the existing `resolveEventLocation` path so the tag-binding system (`aop_feature_tags_v1`) is honored. If `#pavilion` is rebound to a different building, the button follows.
- Click action:
  - hot-now / coming-up: same as a calendar row click — `gotoEventSession(...)` plus open popup (see B1 in `viewer_chrome_polish.md` for the popup-into-view nudge — already shipped).
  - heatmap-fallback: enable the activity-hotspots layer set, fit the view to the densest cluster bbox.
- Countdown rendered in the chrome (tooltip or inline label), updating every 60 s.

### What it does not do

- Does not replace the calendar.
- Does not auto-trigger on schedule change — it only acts on click.
- Does not pretend to be a wayfinder ("turn-by-turn"). It's a teleport, same as a calendar row.
- Does not need a new schedule schema — `aop_event_schedule.json` carries `time_label` (day-part) and, as of 2026-05-24, per-session `start_local` (`HH:MM` 24h local). `start_local` is what the "imminent ≤ 30 min" rule reads. The viewer already exposes both on `props` (`window` is the composed `"5:00 PM · Evening"`, `start_local` is the raw clock value). See `../01_mvp/event_schedule_layer.md`.

### Out of scope for this card

- Audio/visual nag for hot-now (no sounds, no flash).
- Multiple hot buttons (one for events, one for heatmap). Single button, three states.
- Personalization (driver vs spectator). The button is the same for everyone on the property.
- Offline. Folds into `../03_deferred/offline_pwa.md` when that lands.

## Placement

- **Left chrome.** The triage line said "left." `personas.md` puts it at the bottom of the user list because it serves everyone on-site during an event.
- Below the existing preset bar / search shell / calendar card stack (`.left-controls` in `website/index.html`).
- Single round/large button, ~44×44 px minimum touch target. Same chrome palette as the preset bar.
- Icon swap by state (see Visual table above). The fire icon the user originally suggested only fits hot-now; coming-up and heatmap-fallback need their own glyphs.

## Acceptance

- [ ] Button renders on first viewer load in whichever state matches the schedule.
- [ ] State recomputes every 60 s and on `visibilitychange`.
- [ ] Click in hot-now or coming-up flies to the resolved session location and opens its popup, identical to the calendar-row path.
- [ ] Click in heatmap-fallback toggles `showActivityHotspots` + `showActivityHotspotsLabels` on and fits to the densest cluster bbox.
- [ ] Countdown chrome reads the same `time_label` the calendar uses.
- [ ] Editing a `#tag` binding for the resolved session re-routes the button without a reload.
- [ ] Demo posture: with today simulated as Saturday 2026-05-23, the default test session is the live/imminent path; with today simulated as Friday, the upcoming-Saturday case kicks in.

## Verification

- Playwright: extend `playwright_verify_event_schedule.py` with three fixture clocks — one inside the 30-minute window of a session, one outside but before any future session, one after the schedule's last entry. Assert the button state and click action for each.
- Manual: load with the live system clock, then with `?clock=2026-05-23T18:00` (a query-param time override the verifier can use), confirm transitions visibly.
- Manual: rebind `#pavilion` to a different building via the feature list tag input; confirm the button's next click flies to the new location.

## Open questions

- **Look-ahead horizon.** Decided: "next scheduled session regardless of day." If the next session is two weeks out, the button is still in coming-up. If the user later wants a soft "no event this week → heatmap" rule, it lands as a refinement.
- **Icon set.** Three icons needed. Fire is the user's suggestion for hot-now; coming-up and heatmap-fallback open. Punt to a sketch pass once the logic ships.
- **Heatmap-fallback target.** "Densest cluster bbox" needs a concrete query against `activity_hotspots.geojson`. The data already ranks by `stop_slow`; we just need a top-K helper. Folds into the build.

## State at write time

Card written 2026-05-23 while H (code-health Pass 3) is the active executable. A3 is unblocked and ready to pick up next; build cost is ~half-day if the schedule resolver and gotoEventSession path stay in their current shape.

Update 2026-05-24: schedule now carries per-session `start_local`. The "imminent ≤ 30 min" rule has a real anchor; the countdown chrome example ("Saturday 6:00 PM — in 4h 12m") can read straight off `start_local` instead of guessing from `time_label`. No remaining schema blocker.
