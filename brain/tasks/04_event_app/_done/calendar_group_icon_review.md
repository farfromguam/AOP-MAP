# Calendar Group Icon — Resolved

TL;DR:
- The left-rail "Events / POI / About" group icon was reviewed against 2–3
  candidates (misc_3.md item 16).
- **Pick (2026-05-29):** Candidate A — Clipboard with ruled lines. Reads as
  "event list / schedule" rather than a date.
- Lifted into `website/index.html` `#lrTabCal` SVG.
- Compare page `website/calendar_group_icon_review.html` retired.

#aop #04_event_app #icons #left_rail #done

-----

## What landed

Inline SVG on the `#lrTabCal` button: 14×15 rounded board, top clip arc, three
ruled horizontal strokes (the bottom stroke shorter, the way a clipboard
schedule line wraps). Stroke widths 1.5 / 1.3 / 1.2 to mirror the other
left-rail tab glyphs. Uses `currentColor` so the moss / cream `lr-tab.open` and
hover states keep working unchanged.

No new tokens, no new CSS — pure SVG path swap.

## Verifier impact

None. `mvp/scripts/playwright_verify_left_rail_drawer.py` only references the
button ID (`lrTabCal`), not the SVG content. `playwright_verify_event_schedule.py`
takes a screenshot of the top-left strip that now shows the new glyph; if it
asserts pixel-perfect, refresh the baseline.

## Source

Item 16 from `../03_event_app/misc_3.md`. Compare page produced by the
Bucket-D agent in the 2026-05-27 triage pass.
