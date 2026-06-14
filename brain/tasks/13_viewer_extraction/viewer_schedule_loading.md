# Schedule loading spinner + single-number search review

TL;DR:
- **Schedule loading status (thread 2, BUILT + verified).** The viewer's Events tab showed a bare
  `Loading schedule...` text until the event-schedule JSON resolved. Replaced it with the designed
  **spinner row** from `website/calendar_placeholder_v2_spinner.html` ("V2"): a spinning ring +
  **"Loading events…" / "Schedule arriving shortly"**, inside the existing calendar card. It shows only
  while the schedule is actually loading — `viewer_core.js` already swaps `calendarDays.innerHTML` to the
  real rows the moment the JSON resolves (the user's "only if it's actually loading").
- **Search (thread 1, verify-only — no change owed).** Reviewed how `old_index.html` returns a whole
  family for a bare number ("1" → trail 1 **and** 1X). Verified the extracted viewer already matches it
  exactly. Left untouched per the user's "dont change yet" hold (concurrent editor session).

#aop #sprint #13 #viewer #schedule #loading #spinner #search

-----

## Thread 2 — schedule loading spinner (what shipped)

**Mockup:** `website/calendar_placeholder_v2_spinner.html` (113 lines, "V2 — Spinner row"). Single
design, no variant fork.

**The gap:** `index.html` rendered `<li class="calendar-empty">Loading schedule...</li>` as the calendar's
initial state. `viewer_core.js` replaces `calendarDays.innerHTML` with the real session rows once
`aop_event_schedule.json` resolves (`viewer_core.js:1139`; `:1136` "No schedule rows.", `:2275`
"Schedule unavailable."). So the placeholder is the genuine loading state already — it just looked like
bare text.

**The change (2 files, +24/-1, no JS touched):**
- `website/index.html:176` — the placeholder `<li>` becomes the mockup's spinner row markup
  (`.loading-row` → `.loading-glyph` `.spinner-ring` + `.loading-text` `<strong>Loading events…</strong>`
  / "Schedule arriving shortly").
- `website/css/viewer.css` (after `.calendar-empty`, :266) — ported the mockup's spinner block:
  `@keyframes calLoadSpin` (namespaced to avoid collision), `.loading-row` (44px glyph column lines up
  with `.calendar-row`'s day/time column), `.loading-glyph`, `.spinner-ring` (18px, `--cream-border`
  ring, `--brown-soft` top, 0.9s linear spin), `.loading-text` + `strong`. All tokens already in
  `viewer.css`.

No JS change — the existing `innerHTML` swap removes the spinner when data lands, so "show only while
loading" is automatic. Faithful to the mockup (no reduced-motion override added — not in the mockup;
report if wanted, don't invent).

**Verified by observation** (`/tmp/verify_schedule_spinner.py`, SW blocked so edited CSS/HTML served
fresh; schedule JSON delayed 1.8–3s to make the loading window real). **11/11 PASS, 0 console/page
errors:**
- During load: `#calendarDays .spinner-ring` present; text reads "Loading events…"; computed style
  `animation-name: calLoadSpin`, `0.9s`, `18px`, `border-radius 50%`, ring top `rgb(90,72,40)`
  (= `--brown-soft`).
- After load: **13** real `li[data-session-day]` rows render; the spinner is gone.
- Rendered pixels confirmed: `brain/output/schedule_spinner_leftrail.png` — the ring + "Loading events…
  / Schedule arriving shortly" under the "ROCK WARBLERS TRAIL BLAZING INVITATIONAL · Fri Jun 19 – Sun Jun
  21, 2026" header, in the real Events tab. (`schedule_spinner_loading.png`, `schedule_loaded_rows.png`.)

**Scope held:** only the SCHEDULE placeholder. The sibling `poi-empty` "Loading places…" and the About
"loading…" copy were left as-is (not asked) — noted, not done.

**Bug found after first ship — "only text, no spinner" (user, 2026-06-14).** Root cause: the first pass
changed shell assets (`index.html`, `viewer.css`) but did **not** bump the SW `VERSION`/`#appVersion`. In
`sw.js`, navigations are **network-first** (so the new `index.html` markup *did* reach the user) but
`./css/viewer.css` is **stale-while-revalidate** (`sw.js:263-265`) — the browser served the **old cached
viewer.css with no `.spinner-ring` rules**, so the spinner markup rendered unstyled (0×0, invisible) while
"Loading events…" showed as plain text. The earlier verification missed it because it ran with
`service_workers="block"` — testing a condition the user is not in. Fix: **`VERSION` v73→v74 (`sw.js`) +
`#appVersion` v73→v74 (`index.html:234`)** so the new SW re-precaches the fresh `viewer.css`.

**Re-verified WITH the SW active** (`/tmp/verify_spinner_sw.py`, service workers ALLOWED, one context
across two loads): the reload is SW-controlled (`controller.scriptURL = …/sw.js`), `#appVersion` reads
`v74`, the SW-served `viewer.css` applies the spinner (`getComputedStyle` → `animationName: calLoadSpin`,
`18px`, `50%`, `rgb(90,72,40)`), old "Loading schedule..." text gone, 0 errors. Screenshot
`brain/output/schedule_spinner_sw_active.png` (ring visible in the Events tab, "v74" in the corner).

## Thread 1 — single-number search (reviewed, no change)

How `old_index.html` returns the family for a bare number, confirmed identical in the extracted viewer:
- `renderSearchResults` allows a lone digit past the 2-char floor, widens the dropdown cap to 12 for
  digit queries; `searchGroupMatchesQuery` substring-matches the trail **name** OR an **alias**
  (`String(trail_number)`, `"trail N"`); `searchRank` floats trails above building addresses.
- In the data: trail `#1`'s `name` is **"Launchpad"** (matches "1" via its `"1"` alias); **"1X"** is a
  separate feature (matches by name-substring). No bare `name:"1"`.

**Verified by observation** (`/tmp/verify_search_compare.py`, read-only vs the running `:8001`): query
"1" returns the **same 12 rows** on `index.html` and `old_index.html` — `10·12·14·15·16·17·18·1X·
Launchpad(#1)·21·41·61`, 0 errors, `has '1x': True`, `has 'launchpad': True` on both. **No change owed.**
Nuance (preserved from the old page, not regressed): trail #1's row reads "Launchpad", not "1".

## Acceptance

- [x] Schedule loading shows the spinner row (ring + "Loading events…"); replaced by real rows on load;
      0 errors. Observed (Playwright 11/11 + screenshot).
- [x] Search single-number family behavior verified identical old vs new; no change.
- [x] **SW `VERSION`/`#appVersion` bumped v73→v74** so installed users get the fresh `viewer.css` (this
      is what makes the spinner actually appear — see the bug note above). Verified SW-active.
- [ ] **Owed (user's git gate):** the commit. UNCOMMITTED — `sw.js` + `index.html` + `viewer.css`.

## Notes

The `load_animations.html` entrance-choreography mockup was an early misread of "loading status" — NOT
this task. That exploration was reverted (no stray change). If the entrance choreography is ever wanted,
the mockup still stands on its own.
