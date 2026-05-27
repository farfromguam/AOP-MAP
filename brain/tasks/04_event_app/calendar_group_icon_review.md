# Calendar Group Icon

TL;DR:
- The left-rail "Events / POI / About" group icon does not feel right to the
  user (misc_3.md item 16).
- A compare page with candidate icons is checked in at
  `website/calendar_group_icon_review.html`.
- The live viewer icon is unchanged — waiting on a pick.

#aop #04_event_app #icons #left_rail #pending_pick

-----

## Compare URL

`http://localhost:8000/calendar_group_icon_review.html` (load with the same
`python3 -m http.server 8000` you use for manual preview).

The page renders the current chip / tab strip alongside 2–3 candidate icons
in the same chip context so the pick is apples-to-apples, not a free-floating
glyph.

## What lands next

After the user picks a candidate:

1. Lift the chosen icon (inline SVG or unicode glyph) into the live calendar
   chip / tab strip in `website/index.html`. Match the warm-paper palette
   already in use; no new tokens.
2. Update any verifier that asserts the old icon (none known yet — check
   `mvp/scripts/playwright_verify_left_rail_drawer.py` and
   `mvp/scripts/playwright_verify_event_schedule.py` for icon assertions).
3. Retire `website/calendar_group_icon_review.html`. Part of the broader
   mockup-pruning chore (see `viewer_polish_followups.md` →
   "Mockup retirement").

## Source

Item 16 from `../03_event_app/misc_3.md`. Compare page produced by the
Bucket-D agent in the 2026-05-27 triage pass.
