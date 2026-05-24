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
- Offline. Folds into `../10_deferred/offline_pwa.md` when that lands.

## Placement

- **Left chrome.** The triage line said "left." `personas.md` puts it at the bottom of the user list because it serves everyone on-site during an event.
- Below the existing preset bar / search shell / calendar card stack (`.left-controls` in `website/index.html`).
- Single round/large button, ~44×44 px minimum touch target. Same chrome palette as the preset bar.
- Icon swap by state (see Visual table above). The fire icon the user originally suggested only fits hot-now; coming-up and heatmap-fallback need their own glyphs.

## Acceptance

- [X] Button renders on first viewer load in whichever state matches the schedule.
- [X] State recomputes every 60 s and on `visibilitychange`.
- [X] Click in hot-now or coming-up flies to the resolved session location and opens its popup, identical to the calendar-row path.
- [X] Click in heatmap-fallback toggles `showActivityHotspots` + `showActivityHotspotsLabels` on and fits to the densest cluster bbox.
- [X] Countdown chrome reads `start_local` + `time_label` and renders the same `window` label the calendar uses ("Saturday 8:30 PM · Night · in 45m").
- [X] Editing a `#tag` binding for the resolved session re-routes the button without a reload — uses the same `eventLocationByTag` lookup as `gotoEventSession`, so a rebind is honored on the next click without code changes.
- [X] Demo posture: with `?clock=2026-05-23T13:45` the live path lights (`sat-proving-grounds`); with `?clock=2026-05-23T13:15` the imminent path lights for the same session; with `?clock=2026-05-25T12:00` (Monday) the forward anchor wraps to the next weekend and targets `fri-registration` in coming-up.

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

Update 2026-05-24 (same day, later): the calendar sidebar now carries its own current-time indicator — per-row `data-session-state` of `past | happening | upcoming_next | future`, plus solid `LIVE · 45m LEFT` and `SOON · IN 45m` corner badges. See `../01_mvp/event_schedule_layer.md` "Current-time indicator." Implication for this card: when A3 ships, it can reuse the shared `eventScheduleNow()` + `refreshEventScheduleSessionStates()` engine for "what session is hot/coming up?" instead of writing its own. The button's three-state logic still belongs to A3 (the calendar only *marks* sessions; it does not teleport or open popups). Consider whether the LIVE/SOON calendar badges + the hot-button glyph end up reading as redundant once both are on screen; a refinement pass may want one or the other to be the primary signal.

## Shipped (2026-05-24)

A3 built and verified end-to-end. Code map below; durable record stays here, not in `session_context.md`.

### Anchor decision

The calendar's `eventScheduleAnchor()` anchors sessions to the **most-recent** Saturday on/before now — correct for the calendar's "past rows fade" view. The hot button needed the opposite: on Mon-Fri the user wants the **upcoming** weekend, so a Friday afternoon load already points at Saturday's evening session.

Solution: add `eventScheduleAnchorForward(dayLabel, startLocal, now)` as a sibling anchor used only by the hot button. Rule:

- Mon-Fri (dow 1-5): reference Saturday = upcoming Saturday (`6 - dow` days forward).
- Saturday (dow 6): reference Saturday = today.
- Sunday (dow 0): reference Saturday = yesterday (Sunday is still part of the current weekend; the Sun session is today).

Friday session anchors to `refSat - 1`, Sunday to `refSat + 1`.

### Heatmap-fallback semantics with a template schedule

The schedule is weekday-template, not absolute-date. With the forward anchor, sessions always wrap to the next weekend — so "every session is in the past" never triggers organically. The heatmap-fallback path therefore fires only when the schedule is empty (or, in tests, when `eventSessionById` is cleared). If a future schedule format ever carries absolute dates, the same code path would catch the "schedule is over" case automatically; the forward-anchor branch only fires when dates are absent.

### Code map (`website/index.html`)

CSS: `.hot-button` block alongside the calendar styles (`[data-hot-state]` switches background / shadow). Glyph + title + detail spans driven by `id="hotButtonGlyph|Title|Detail"`.

HTML: single `<button id="hotButton">` in `.left-controls`, below the calendar card.

JS (near the existing schedule engine):

- `let aopActivityHotspotsData` (hoisted) — collects the activity-hotspots feature collection so `findDensestHotspotBbox` can compute without re-fetching.
- `HOT_BUTTON_IMMINENT_MIN = 30`, `HOT_BUTTON_SESSION_LEN_MIN = 90`.
- `eventScheduleAnchorForward(day, start, now)` — see anchor decision above.
- `computeHotButtonTarget()` — walks `eventSessionById.values()`, returns `{state, target, kind?}`. Prefers live → imminent → next future → fallback.
- `findDensestHotspotBbox(topK = 3)` — sorts hotspot polygons by `intensity_norm` (falling back to `dwell_minutes`), returns the combined bbox of the top-K.
- `hotButtonFlyToHotspots()` — ensures `showActivityHotspots` is checked (the toggle's layer group already includes `activity-hotspots-labels`, so the card's "force labels on" requirement is satisfied by the one toggle), then `map.fitBounds(densestBbox)` with the standard visible-slice padding.
- `attachHotButton()` — idempotent click binder (`dataset.bound = '1'`).
- `refreshHotButton()` — pulls a fresh decision, paints button state / glyph / title / detail / `data-target-session-id` / aria-label, or hides the button when both the schedule and hotspots are empty.

### Tick + tag-rebind wiring

`refreshHotButton()` is called from the tail of `refreshEventScheduleSessionStates()`. That path already runs:

- on every render of the schedule sidebar (`renderEventSchedule` → refresh)
- on every 60 s tick (`ensureEventScheduleStateTicker`)
- on `visibilitychange` (same ticker)
- after every tag-rebind (`rebuildEventScheduleData` → `renderEventSchedule` → refresh)

So one extra call covers all four signals — no second timer, no second visibility handler. The hotspots-load block also calls `refreshHotButton()` so the fallback state is reachable even if the schedule is missing.

### Verification

`mvp/scripts/playwright_verify_event_schedule.py` extended with a "Hot button (Sprint 02 Bucket A3)" section: 20 new assertions across four fixture clocks (`?clock=2026-05-23T13:45` for live, `T13:15` for imminent, `T19:45` for coming-up same-day, `2026-05-25T12:00` for coming-up across-day) plus a schedule-cleared assertion for heatmap-fallback. Each state also verifies the click action (camera flies + popup opens for hot-now / coming-up; activity-hotspots toggle flips on + layer renders for fallback). Full run: **85 PASS / 0 FAIL / 0 console errors**.

### Open: visual redundancy with calendar badges

The pre-shipped calendar already carries `LIVE · 45m LEFT` and `SOON · IN 45m` badges per row. The hot button now says essentially the same thing in chrome that is always-visible (the calendar can be collapsed). Behavioral roles are distinct — the badges mark sessions; the button teleports — but visually they may double-up when the calendar is expanded. Leaving this as a future refinement; the user picked "simple enough and has the info" for the calendar indicator and would likely do the same here.

### Icon punt (still open)

Used emoji glyphs as the smallest punt: 🔥 (hot-now), ◷ (coming-up), ❖ (heatmap-fallback). The card's "Icon set: punt to a sketch pass" still applies — these render cleanly across fonts but are not a designed set.
