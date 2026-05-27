load animations.

on load the page resets the view.

assuming everything was open on the left side.

1) page loads
2) search button blinks. 
3) search extends
4) hot blinks
5) hot extends
6) cal blinks
7) active cal tab extends.

8) user finds action in calendar.
If mobile

9) search button blinks. 
10) search collapses
11) hot blinks
12) hot collapses
13) cal blinks
14) active cal tab collapses.

if desktop 
9) nothing collapses

15) event in world pops up


by pulsing the buttons the user learns what they do.

## Review artifact

Created 2026-05-26:

- `website/load_animations.html`
- Backlog card: `brain/tasks/backlog/load_animation_intro.md`

The review page keeps this as a standalone mockup, not a live
`website/index.html` integration. It preserves the current left-rail chrome
and adds three named load-sequence variations:

- LA1 Pulse Ladder - direct pulse/open/collapse read of the card.
- LA2 Scout Sweep - same order, but the icon cue is a light sweep.
- LA3 Quiet Beacon - one soft flash per icon, quicker intro, faster mobile close.

The page supports desktop and mobile review:

- Desktop leaves Search, Hot, and Calendar open before the world popup.
- Mobile blinks and collapses Search, Hot, and Calendar together before the world popup.
- Six timing knobs are exposed in the review page for the selected variant:
  view reset, tab flash, open speed, step hold, mobile close, and popup delay.

Verification:

- JS syntax extracted from the page passes `node --check`.
- Headless Playwright smoke passed for desktop and mobile end states.

## Production decision

Pulled from the live viewer on 2026-05-26.

The animation felt good in isolation, but the runtime fought the real map
startup path: MapLibre loaded, the drawer restored default or saved state, hot
data could auto-open, then the intro collapsed the left rail and replayed the
sequence. That made the app feel unstable.

Keep the prototype. Do not wire it back into `website/index.html` until the
backlog guardrails in `brain/tasks/backlog/load_animation_intro.md` are met.
