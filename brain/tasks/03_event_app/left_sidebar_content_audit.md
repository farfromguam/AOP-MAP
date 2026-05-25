# Left Sidebar Content Audit (post-Rock-Warblers rebrand)

Date opened: 2026-05-25

TL;DR:
- The viewer's left sidebar was rebranded to the Rock Warblers Trail Blazing
  Invitational on 2026-05-25, in production voice with no hedges.
- A second 2026-05-25 pass merged the `Event` and `About` tabs into a single
  `About` tab. The left context card now carries two tabs (Events / About);
  the third slot is reserved for the planned POI browser
  (`left_panel_poi_browser.md`).
- Gaps in the public event record were filled with sister-event vibes (G6 / Pro-Line
  By The Fire / AxialFest) per `northstar/whats_this_for.md`.
- A content audit + rework is owed once Rock Warblers confirm real specifics
  (schedule, classes, gate widths, mandatory skills, fee, registration link,
  awards, night-run yes/no).

#aop #03_event_app #content #left_sidebar #rock_warblers #audit

-----

## What shipped 2026-05-25

`website/index.html`:

- Calendar card title `Event calendar` → `Rock Warblers Trail Blazing Invitational`.
- Calendar subtitle template `Draft ${date_range_label} schedule` → bare
  `date_range_label`. JSON now carries the production string
  (`Friday, June 19, 2026`).
- Left tab `Park` → `Event` (label only; `#leftTabPark`, `#parkTabPanel`,
  `data-left-tab="park"` IDs preserved for selector stability) — superseded
  later the same day by the Event+About merge below.
- Event+About merge (2026-05-25 second pass): `#leftTabPark` button and
  `#parkTabPanel` div removed from `website/index.html`. `.left-tabs` grid
  CSS dropped from `repeat(3, ...)` to `repeat(2, ...)`. Merged content lives
  in `#aboutTabPanel` with an `About the Rock Warblers` H2, an event-anchored
  lead sentence, eight info-list rows (Format, Mandatory skills, Trail buddies,
  Rigs, Night crawl, The park, The map, The crew), and the existing footer
  line `Built by Rock Warblers, for Rock Warblers. See you at the pavilion.`

`website/data/aop_event_schedule.json`:

- `event.id` → `rock_warblers_trail_blazing_invitational_2026`.
- `event.label` → `Rock Warblers Trail Blazing Invitational`.
- `event.date_range_label` → `Friday, June 19, 2026`.
- Session list, location tags, schema, and status not changed.

`mvp/scripts/playwright_verify_presets.py`:

- Tab labels assertion updated to `["Events", "About"]` after the merge.
- Separate Park-tab content check removed.
- About tab content check anchored to `Trail Blazing Invitational`,
  `Rock Warblers`, and `See you at the pavilion` (identity-stable, not
  copy-fragile).

`brain/research/viewer.md`:

- Viewer catalog one-liner updated to match the new calendar title + subtitle.

## Source of the new copy

The Facebook event record (`https://www.facebook.com/events/adventure-offroad-park-nature-center/rock-warblers-trail-blazing-invitational/4541595172728436/`)
confirms only: title, host (Team Rock Warblers RC Rock Crawling, Hilary Fryman),
date (Friday, June 19, 2026), venue (Adventure Off Road Park & Nature Center,
South Pittsburg, TN), and "sports event" classification. No schedule blocks,
classes, gate widths, fee, registration link, sponsors, or prizes are public.

Gaps were filled in production voice from sister-event vocabulary documented
in `brain/handoff/event_schedule_context_20260522.json` and
`brain/northstar/whats_this_for.md`:

- **Format** (numbered stages, time-run, gates with touch/roll/assist penalties,
  free winching) — Recon G6 base format.
- **Mandatory skills** (water, grade pull, taco-stand) — G6 mandatory-skills
  section vocabulary.
- **Trail buddies** (walk, mark, swap, penalty winch travels) — G6 stage-buddy
  role.
- **Rigs** (1/10 electric, 1.9" / 1.55", no dig, no rear steer, 5-accessory
  minimum) — G6 vehicle rules.
- **Night crawl** (lights on, pavilion-out / fire-in) — Pro-Line By The Fire
  Into the Night Crawl + AxialFest Light Up the Night.
- **Base camp** (pavilion as registration / driver meeting / awards / fire,
  on-site camping) — AxialFest Base Camp / Pro-Line By The Fire pattern.

The voice is direct, first-person team. No "proposed", no "draft", no "subject
to confirmation" in the UI.

## What the audit needs to do

When Rock Warblers confirm the real specifics, walk the panels and replace
sister-event placeholders with the truth:

- [ ] Confirm or correct the **Format** line (number of stages, scoring rules,
      whether winching is actually free).
- [ ] Confirm or correct the **Mandatory skills** line (which skills, whether
      every stage has all three, names for them).
- [ ] Confirm the **Trail buddies** requirement and the penalty-winch rule.
- [ ] Confirm or correct the **Rigs** line (classes, dig/rear-steer policy,
      scale-accessory minimum). Specifically: is this a G6-shaped invitational,
      a comp-class invitational, or a blended day?
- [ ] Confirm or correct the **Night crawl** existence, route, and finish point.
- [ ] Confirm or correct the **Base camp** facilities (registration location,
      whether camping is first-come, food/drink on-site).
- [ ] Confirm or correct the **Get in touch** line in the About tab (event
      page link, primary contact, day-of contact).
- [ ] Decide whether a **schedule with actual clock times** replaces the
      current generic Friday-Sunday session list, or whether the Trail Blazing
      Invitational is single-day Friday only.
- [ ] Confirm whether the **event tab name should stay `Event`** (currently
      generic) or carry the specific event name once the project hosts more
      than one event.

## Adjacent open items not in scope

- `website/index.html:557` — right-panel small text still says
  `Event schedule: proposed RC event sessions from ...` and `Schedule rows use
  location tags such as #pavilion ...`. That's an editor-tooling hint, not
  user-facing chrome, but the "proposed" word should be reviewed when the
  schedule moves from sister-event mock to Rock Warblers actuals.
- `website/index.html:5203` — `attribution: 'Event schedule: proposed from
  sister-event references'`. Map attribution string. Same review trigger.
- `aop_event_schedule.json` `status: "proposed"` and per-row `caveat` strings.
  Not rendered in the UI today, but if a future view surfaces them the same
  hedge re-emerges.

## Acceptance

Audit closes when Rock Warblers have walked the Event and About panels and
either signed off line-by-line or supplied the replacement text.
