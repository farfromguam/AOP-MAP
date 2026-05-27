# Calendar loading placeholder

TL;DR:
- The left-rail calendar today flashes an ugly `<div>Loading…</div>` before content arrives.
- Four side-by-side mockup variants are checked in under `website/calendar_placeholder_*` for a pick.
- Nothing is wired into `website/index.html` yet — pick a variant first.

#aop #04_event_app #calendar #placeholder #mockups #pending_pick

-----

## Compare URL

`http://localhost:8000/calendar_placeholder_compare.html` (serves the four variants in iframes side-by-side; load with the same `python3 -m http.server 8000` you use for manual preview).

## Variants

- `calendar_placeholder_v1_skeleton.html` — shimmer skeleton row, title bar + meta line, content-row-shaped.
- `calendar_placeholder_v2_spinner.html` — single content row with "Loading events…" and a small subtle spinner glyph.
- `calendar_placeholder_v3_pulse.html` — softly pulsing cream-gradient row.
- `calendar_placeholder_v4_dotprogress.html` — calendar-row container with a dot-progress indicator.

Each variant copies the relevant `.calendar-card` / `.cal-row` / `.cal-time` / `.cal-title` tokens from `website/index.html` so it looks at home inside the real calendar card.

## What lands next

After the user picks a variant:

1. Lift the chosen variant's HTML/CSS into `website/index.html` at the calendar-loading slot (look for the current ugly placeholder render — probably in `#calendarLoading` or whatever renders before `renderCalendar()` populates).
2. Reuse the existing `.calendar-card` palette tokens; do not import the variant file's local copies.
3. Retire the other three variant files plus the compare page once the choice is in (`tasks_persist_to_brain.md` style — keep one mockup surface in the repo, retire experiments).

## Source

Item 13 from `tasks/03_event_app/misc_3.md`. Mockup compare pages produced by the Bucket-D agent in the 2026-05-27 triage pass; routing block on `misc_3.md` documents the dispatch.
