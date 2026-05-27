# Session 2026-05-27 — misc_4 pickup (incomplete)

Short handoff. Read this once, then go act. Don't re-run verifiers to "confirm" prior state — the diff already tells you everything.

## Where to start

Open `brain/tasks/04_event_app/misc_4.md`. User has been editing it live; trust it over this file.

## What is already in the working tree (uncommitted)

`website/index.html`:

- Items 1, 2, 3 of misc_4 done: `#showPastEventsBtn`, `#poiExpandAllBtn`, and the About `.tab-footer` "Event page" button are gone. About's Facebook URL is now an inline `<a>` wrapping "Trail Blazing Invitational" in the lead paragraph. `.tab-footer` / `.tab-footer-btn` CSS removed.
- Item 4 (resize handles): one shared `--lr-card-body-height` var on `.lr-content-col`. Each tab (Events / POI / About) has its own `.lr-resize-handle` sibling **outside** its scroll body. `setLrCardHeight` / `initializeLrCardResize` replace the old `setCalendarBodyHeight` chain. No min/max — drag to 0. Old `CALENDAR_MIN_BODY_HEIGHT`, `CALENDAR_MAX_BODY_HEIGHT`, `calendarResizeMaxHeight`, `calendarCurrentBodyHeight`, `setCalendarBodyHeight`, `initializeCalendarResize` all deleted. localStorage key bumped: `aop_calendar_height_v1` → `aop_lr_card_height_v1`. The old key is still in `VIEWER_OWNED_STORAGE_KEYS` for one sprint of Reset cleanup per `spinup/viewer_storage_migration.md`.
- Item 5 (Friday-of-week shim removed): new `parseEventAnchorFriday()` reads `eventScheduleConfig.event.date_range_label`. `resolveCalendarAnchorSat` returns the event Saturday; `eventScheduleAnchorForward` delegates to `eventScheduleStartFromAnchor` with that anchor. `CALENDAR_MONDAY_RESET_HOUR` and `mondayResetMs` deleted.
- Item 6 (sticky header scroll-with-events): **not touched** — user explicitly held it out.
- Tab restore fix: the event-session auto-restore (around line 7021) no longer force-calls `setLeftTab('events')` if `viewerSessionState.active_left_tab` is something other than `'events'`. POI/About reload now stays put. Verified by Playwright probe.

`mvp/scripts/playwright_verify_event_schedule.py`,
`mvp/scripts/playwright_verify_left_rail_drawer.py`,
`mvp/scripts/playwright_verify_presets.py`,
`mvp/scripts/playwright_verify_session_tools.py`:

- All four updated: `aop_calendar_height_v1` → `aop_lr_card_height_v1`.
- Event schedule verifier `?clock=` fixtures rebased to event-anchored dates (June 15 / June 20 / June 21, 2026). The "late-list Sunday fixture" was set to `2026-06-21T08:30` (sun-feedback-board, row 11/13) — not 10:30 — because 10:30 puts the active row at row 12/13 and the scroll-to-center lands at maxScrollTop, blowing the "safe scroll runway" math.

## What is still wrong (do this first)

**POI and About show ~62 px of empty cream between the handle and the bottom of the card.** Root cause: `.left-tab-panels { display: grid }` stretches every panel to the tallest. Events has `.calendar-heading` (~62 px) + body + handle; POI/About have only body + handle. The stack-to-tallest was added by `tasks/03_event_app/_done/misc.md` item 21 to eliminate tab-switch layout shift.

**Decision is made: take option A.** Drop the stretch-to-tallest. Each tab-panel sizes to its own content. Tab switches will shift ~62 px when going to/from Events. That shift is less bad than the dead cream space the user is staring at right now.

Edit at roughly `website/index.html:365-370`:

```css
.left-tab-panels { display: grid; }
.left-tab-panels .left-tab-panel { grid-area: 1 / 1; visibility: hidden; pointer-events: none; }
.left-tab-panels .left-tab-panel:not([hidden]) { visibility: visible; pointer-events: auto; }
.left-tab-panels .left-tab-panel[hidden] { display: block; }
```

Pull the grid stack out: just stack panels naturally (only the un-hidden one displays). Something like:

```css
.left-tab-panels { display: block; }
/* delete the grid-area / visibility / display:block-when-hidden rules */
```

Then load the viewer (`cd website && python3 -m http.server 8000`), open `http://localhost:8000/`, click each tab, verify the handle sits at the bottom of every card with no cream gap. Take a `brain/output/` screenshot.

## What to log after the A fix

Add to `brain/tasks/04_event_app/viewer_polish_followups.md`: "Verifier vs. behavior mismatch — `playwright_verify_event_schedule.py` Trail-lane click tests expect `#showActivityHotspots` to flip ON, but the button handler treats a click while the lane is already selected as toggle-OFF (`hotButtonFlyToHotspots` only called on the off→on edge). 6 pre-existing FAILs. Either rewrite the test to deselect first, or change the handler so a click on an already-selected trail lane re-runs `hotButtonFlyToHotspots` without flipping state. Not caused by misc_4."

## What to write to misc_4.md (per `ai_rules/preserve_card_directives.md`)

Under a `-----` divider, list:

- Items 1–5 shipped (per above).
- Item 6 held by user.
- Items "white space" + "current tab on reload" addressed: tab restore shipped; handle white space shipped via grid-stack drop.
- Items "1033 is the farmhouse" / "880 is the park offices" — these are building-tag bindings, not a misc_4 follow-up. Move them to a feature-tagging pass on the buildings drawer (or capture in `tasks/04_event_app/data_integrity_publishability.md` if owed by source verification).

## Things the user said in this session that bear on the next one

- "leave the last scrolling request out of the mix" — item 6 stays out.
- "stop" / "you are taking too long" / "are you slow" — pacing complaint. Concrete read: do not run all four Playwright verifiers for a CSS structural change. One quick browser screenshot of POI + About is enough to confirm the layout fix. Save verifier runs for the end, once.
- The user's diagnostic style is direct. Don't ask permission for a fix when the answer is one of two obvious options; just pick the better one and ship.

## Files I touched in this session

```text
M website/index.html
M mvp/scripts/playwright_verify_event_schedule.py
M mvp/scripts/playwright_verify_left_rail_drawer.py
M mvp/scripts/playwright_verify_presets.py
M mvp/scripts/playwright_verify_session_tools.py
```

User has also been editing `brain/tasks/04_event_app/misc_4.md` outside my context — that file is theirs, read it first.

## What is NOT done

- The empty-space fix (option A above). Apply it.
- The viewer_polish_followups.md note about the trail-button verifier mismatch.
- The misc_4.md "what shipped" block under the user's directives.
- No git commit. Per `ai_rules/no_commits.md`. Leave that to the user.
