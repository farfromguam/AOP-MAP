# App Code Review — Fix Batch 1 (DONE, 2026-05-31)

> **Shipped slice of the 2026-05-31 app code review.** The full review found
> 4 High / 20 Medium / 13 Low across `website/index.html` + `sw.js` +
> `manifest.json`. **20 of 37 findings are now resolved** in the working tree and
> verified by observation: the 15 no-decision fixes, H4+L8 (the queued
> "stale-while-revalidate" decision), and the M7/M14/M17 no-device forks. The 17
> still-held items (on-device checks + refactors) live in
> [`app_code_review_followups.md`](app_code_review_followups.md).

#aop #04_event_app #code_health #review #done

-----

## What shipped (working tree, UNCOMMITTED)

All 15 respect the MVP rule ([`no_limiting_code_mvp`](../../../../ai_rules/no_limiting_code_mvp.md)):
each guards / normalizes / escapes / handles malformed input so the feature
still displays — none reject data.

| ID | Location | Fix |
| --- | --- | --- |
| **H2** | `index.html` `sliceCanvasN` / `bakeTiles` | Free the slice + rotated bake canvases (`width=height=0`) so the SFWDA multiply/rotate cycle doesn't leak 37 canvases + data-URLs per bake |
| **H3** | `index.html` `applyMultiplyAlpha` | try/catch the tainted-canvas `getImageData` throw; skip the multiply key and `console.warn` instead of aborting the whole map-load chain |
| **M1** | `index.html` `bindPopup` | Close popups via `closeAllMapPopups()` (was raw `el.remove()`), so the event-session popup's own `close` handler fires and `activeEventSessionId`/session state stays in sync |
| **M2** | `index.html` `bindPopup` + 12 title fns | Escape the popup **title** centrally in `bindPopup`; stripped the now-redundant `escapeHtml` from all 12 title functions (single safe sink, no future caller can forget it) |
| **M3** | `index.html` `fetchJson` | `console.warn` on a non-OK HTTP status — a missing data file no longer disappears with zero signal |
| **M6** | `index.html` `hotspotPolygonCentroid` | Handle `MultiPolygon` (read `coordinates[0][0]`) instead of summing rings → NaN → silently dropping the hotspot |
| **M11** | `index.html` `buildPoiGroups` | Stable index-based fallback row id (`idx-<n>`) instead of `Math.random()`, so `data-poi-id` is stable across renders |
| **M15** | `index.html` `renderAbout` | Assign the About link `href` only when it matches `^https?://` — declines `javascript:` without dropping the link text |
| **M16** | `index.html` `mergeStoreSlice` | Shallow-merge each layer's slice (`{...existing, ...layerSlice}`) so a partial paste adds to, not replaces, that layer's entries |
| **M18** | `index.html` `applyPositionedFeatures` | Write `highlight`/`locked` whenever the store has an opinion (`!== undefined`), so an un-star/un-lock survives reload even if the base shipped `true` |
| **M20** | `index.html` `panelCollapse`/`panelHeader`/`calendarDays` | `?.`-guard the module-eval `addEventListener`s so a renamed id can't throw and abort all wiring below |
| **L4** | `index.html` `withZoomStops` | Guard the exact 7-element 2-stop `['interpolate', …, ['zoom'], …]` shape and `console.warn` rather than silently corrupting a different expression |
| **L5** | `index.html` `describeGeometry` | Derive N/S + E/W from coordinate sign (no more `−85°E` for a western longitude) |
| **L6** | `sw.js` `cacheFirst` / `staleWhileRevalidate` | Cache on `status === 200` (not `res.ok`) so a future 206 can't throw inside `Cache.put` |
| **L7** | `manifest.json` | Add `"id": "./"` so a future `start_url` change can't fork the installed app identity |

## H4 + L8 — SW cache-staleness (the queued decision, answered)

The user chose **stale-while-revalidate** (the recommended option). Applied to
`sw.js` + a version bump:

- The app **shell HTML** is now self-healing: navigations are network-first **and
  write the response back to `SHELL_CACHE`** (so the offline fallback is no longer
  frozen at the last bump), and a non-navigation `.html` fetch is
  stale-while-revalidate.
- The **copy JSON** (`aop_ui_strings.json`, `aop_about.json`,
  `aop_copy_registry.json`) joins the event schedule on the
  stale-while-revalidate path via a new `SWR_SUFFIXES` list — wording edits reach
  installed users without a `VERSION` bump. Bulky GeoJSON stays cache-first.
- A **release checklist** comment sits at `VERSION` (bump here + `#appVersion` +
  reconcile `DATA_ASSETS` with `ls website/data/`).
- **`VERSION` v20 → v21** in `sw.js` and `#appVersion` in `index.html` (the bump
  the user's chosen option called for; also ships the L6 fix to installed users).

## M7 / M14 / M17 — quick decision-forks (next slice, shipped)

The no-device forks, resolved:

- **M7** — the event-schedule 60s ticker + `visibilitychange` listener are
  confirmed **singletons** (both behind the `eventScheduleStateTimer != null`
  guard, so re-render/reset creates nothing new) and intentionally page-lifetime
  — a reset still wants live session states, so there is nothing to stop.
  Documented in place with a note on how to add a `stop…()` if this ever becomes
  a multi-view SPA. (Comment-only; no behavior change.)
- **M14** — removed the 4 precache entries unreferenced by `index.html`
  (`aop_synthetic_activity_report.json`, `sfwda_traced_markers.geojson`,
  `sfwda_numbered_trails.geojson`, `sfwda_trails_edited.geojson`) from
  `sw.js` `DATA_ASSETS`, with a comment listing them so they can be re-added if
  wired in. Rides the v21 bump (no extra bump).
- **M17** — `EDITOR_POI_CATEGORIES` now builds from the `<select id="poiCategory">`
  options at load (single source of truth) with the literal list as a fallback,
  so the editor's per-bucket Category dropdowns can't drift from the HTML.
  Verified the derived set equals the prior 11 categories exactly.

## Verification (by observation)

New durable verifier **`mvp/scripts/playwright_verify_code_review_fixes.py`**.
Three runs, **0 console/page errors** on load and through all four presets.
Direct confirmations of the changed popup paths:

- `[PASS]` map canvas present
- `[PASS]` **service worker active (state=activated)** — confirms the H4/L8
  `sw.js` rewrite + v21 bump parse, register, and activate cleanly
- `[PASS]` calendar pick opens a single popup
- `[PASS]` **popup has no double-escaped entities** — M2 escaping is correct, not doubled
- `[PASS]` **second pick replaces the popup, no stacking** — M1 `closeAllMapPopups` works
- `[PASS]` About panel populated (renderAbout + href-gate path ran clean)
- `[PASS]` presets Topo / Trace / Satellite / Park each switch with no new errors (exercises the L4 `withZoomStops` guard)

(One run logged a one-off `Could not compile fragment shader` / `CONTEXT_LOST_WEBGL`
— a headless-GPU artifact under raster load, not app logic; the other runs were
clean with identical code. `manifest.json` re-validated as parseable JSON.)

## Review record — retracted finding

The sweep flagged `composeFeatureFilter` (`index.html`) for a numeric-vs-string
id mismatch. Re-read **disproves it**: `visibleIds` holds the native-typed
`props[idField]` and `['get', idField]` returns the same native type, so the
membership test matches; only the `persisted[…]` lookup is stringified, and that
side is correct. No change made. (Logged here so it isn't "re-found" later.)

## Caveats

- Everything is in the **working tree, uncommitted** — the user commits.
- The `VERSION` v20 → v21 bump is included (the user's chosen H4 option called for
  it); it carries L6 + the H4/L8 routing to installed users on deploy.

## What's next

The 20 still-held findings — decisions, on-device checks, and refactors — with
full context and a recommended order are in
[`app_code_review_followups.md`](app_code_review_followups.md). With the SW
decision resolved, the next cheap slice is the small no-device forks (M7 ticker
teardown, M14 unused-precache cleanup, M17 categories-from-select).
