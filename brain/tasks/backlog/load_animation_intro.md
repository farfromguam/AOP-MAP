# Load Animation Intro Backlog

Date: 2026-05-26

TL;DR:
- Keep the loading-animation prototype as a review artifact, not live viewer behavior.
- The live integration was pulled because it fought MapLibre startup, drawer restore, and pocket-map persistence.
- Motion can come back only if it is state-aware, pre-paint or explicitly user-started, and incapable of making the app feel unstable.

#aop #backlog #viewer #motion #left_rail #maplibre

-----

## Fit

**V1 fit:** Out.

**V2 fit:** Maybe, if it teaches without delaying or destabilizing the map.

**Internal fit:** Good as a design review artifact and timing lab.

## Source

- User observation, 2026-05-26: the map loads with the left side extended, then the left rail collapses, then the animation runs.
- Original task note: `brain/tasks/03_event_app/_done/load animations.md`.
- Prototype: `website/load_animations.html`.

## Decision

The load intro is not live behavior.

It should not run on normal viewer startup, and Playwright should not need an
`intro=0` escape hatch. The map should feel steady before it feels clever.

The standalone prototype stays because the interaction idea still has value:
pulse Search, Hot, and Calendar so a new user understands the left drawer.
But the production viewer is currently a persisted pocket map. That means
saved preset, saved tab, saved search, selected event, hot-data auto-open, and
MapLibre layer readiness all matter more than a choreographed teaching moment.

## What Went Wrong

The live runtime ran after the app had already started doing real work:

- MapLibre loaded layers and sources.
- The drawer rendered default or saved card state.
- Hot could auto-open when event or activity data arrived.
- Pocket-map state could restore preset, left tab, search, and selected event.
- Then the intro closed Search / Hot / Calendar, reset the camera, reopened
  the cards, and opened an event popup.

That created a visible state reversal: app appears, app collapses, intro runs,
map moves again. The result reads as jank even when the individual animations
are polished.

## Guardrails

Future animation work must satisfy these before touching `website/index.html`:

- Do not override saved viewer state.
- Do not collapse UI that is already visibly open.
- Do not reset the camera after the map has visibly settled.
- Do not require verifier-only query params to make tests stable.
- Do respect `prefers-reduced-motion`.
- Do keep mobile map space stable after first paint.
- Do prove the animation does not race MapLibre `load`, data fetches, hot-card
  auto-open, or pocket-map restore.

## Future Shapes

### Explicit Tour

Put the teaching sequence behind a user-started action, likely in About or
Session tools. It can be richer because the user asked for it, and it can
temporarily drive the drawer without pretending to be normal startup.

### Passive Hints

After the drawer is stable, use a small icon cue or badge treatment. No card
open/close choreography, no camera reset, no popup. This is the safest path if
the goal is discovery rather than drama.

### Pre-Paint Intro

Only viable if the viewer can know the intended initial drawer/camera state
before first visible paint. If that requires delaying the map or hiding useful
content, drop it.

## Acceptance Bar

- Normal load has one stable drawer state.
- Saved preset, left tab, search text, and selected event restore without being
  displaced by animation.
- Hot-data auto-open does not trigger a visible collapse/reopen cycle.
- The map camera does not run a second fit/fly after initial settled state
  unless the user or restored selected event requested it.
- Mobile does not briefly give space to controls and then take it away.
- A focused Playwright check can prove no startup collapse, no second camera
  reset, and no intro-specific query escape hatch.

## Artifacts

- `website/load_animations.html` remains the timing and variant review page.
- `brain/tasks/03_event_app/_done/load animations.md` remains the original concept
  note and points here for the production decision.
