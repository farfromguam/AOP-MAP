# Left Panel Context Tabs

Date: 2026-05-24

TL;DR:
- Reworked the viewer's left controls as a mobile-first stack.
- Added Events / Park / About tabs in the existing left context footprint.
- Kept the calendar behavior intact by making `#calendarCard` the tabbed context card.

#aop #03_event_app #viewer #left_panel #mobile

-----

## Source

- User request: review the left panel UI, buttons, and elements; use independent agents; add About Us and possibly About the Park; design mobile first.
- `../../northstar/whats_this_for.md` for scale RC / not-OHV language.
- `../../northstar/personas.md` for event-day left-panel priorities.
- `../../research/viewer.md` for the viewer catalog.

## Shipped

`website/index.html`:

- Left stack order is now search, `Hot now`, map presets, zoom shortcuts, then context.
- `Hot now` has the same cream surface treatment as the rest of the left chrome, while the two lane buttons remain visually distinct.
- Added three tabs to `#calendarCard`:
  - `Events` — default tab; contains the existing collapsible event calendar body.
  - `Park` — source-cautious AOP park context.
  - `About` — map-project posture and validation-loop copy.
- Preserved the existing stable IDs used by verifiers and users: `#searchInput`, `#hotControl`, `#hotButton`, `#hotTrailButton`, `#presetPark`, `#presetTopo`, `#presetTrace`, `#terrainButton`, `.zoom-bar button[data-view]`, `#calendarToggle`, `#calendarBody`, and `#calendarDays`.
- Mobile defaults no longer rely on internal scrolling of the whole left stack. At 360 px / 390 px width with `Hot now` loaded, the left stack clears the bottom panel.

`mvp/scripts/playwright_verify_presets.py`:

- Added checks for the Events / Park / About tabs.
- Added a mobile assertion that the left stack does not need internal scrolling.

`brain/research/viewer.md`:

- Updated the left-control capability description to match the new stack and context tabs.

## Verification

```text
node inline-script parse: PASS
python3 -m py_compile mvp/scripts/playwright_verify_presets.py: PASS
git diff --check -- website/index.html mvp/scripts/playwright_verify_presets.py: PASS
python3 -u mvp/scripts/playwright_verify_presets.py: RESULT PASS
python3 -u mvp/scripts/playwright_verify_event_schedule.py: RESULT PASS
phone-width geometry probe, 390 px and 360 px with Hot loaded: clear=true, no internal left-scroll
```

## Notes

The third review agent correctly caught a bad first shape where the calendar collapse state owned too much context and the first mobile CSS depended on scrolling the whole left rail. The shipped version keeps the tabs in the existing `#calendarCard` footprint while preserving the stable calendar body IDs and default mobile controls.
