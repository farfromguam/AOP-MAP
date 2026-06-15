# Sprint 13 — Viewer extraction (pull the mature read view into a clean core)

TL;DR:
- The user (2026-06-13): *"I don't want to delete code I think is good. I want to copy code I know
  will be used in the viewer. It's a different activity… start with the core and see what gets moved
  over. When we have to move 1000 lines for a simple feature we can assess if it's truly needed."*
- The move is **extraction to a clean core, NOT subtraction from the tangled file.** Subtraction keeps
  everything you don't explicitly remove — all the viewer debt rides along by default. A clean core
  starts empty and only gains code you carry over on purpose. **The move itself is the audit.**
- This completes the convergence arc Sprint 11 pointed at (*"the website reverts to the read-only
  viewer the northstar promised"*) — but by **rebuild**, not by pruning `main.js`.

#aop #sprint #13 #viewer #extraction #read #clean_core #convergence

-----

## ✅ Sprint 13 status — SLATE COMPLETE (2026-06-14)

Every slice on the slate below shipped, was verified by observation, and is now in
`_done/`:

- **Slice 1 — core scaffold + presets/zoom/3D** → `_done/viewer_core_scaffold.md`
- **Slice 2 — search** → `_done/viewer_search.md`
- **Slice 3 — left-rail drawer + Calendar/Events** → `_done/viewer_drawer_schedule.md`
- **Slice 4 — POI popups + ★-destinations directory** → `_done/viewer_poi.md`
- **Slice 5 — Hot now (event + trails lanes)** → `_done/viewer_hot.md`
- **Slice 6 — Locate / Install / version / PWA + `?tester=1`** → `_done/viewer_locate_install_version.md`
  (carries the v80/v81 off-park travel notice; **council owed on the v81 follow-up diff**)
- **Slice 7 — the swap (viewer becomes `index.html`, old parked as `old_index.html`) + blue Locate FAB** → `_done/viewer_swap.md`
- **Slice 8 — off-edge decorative band merged into the read viewer** → `_done/viewer_band_merge.md`
- **Schedule loading spinner + single-number search review** → `_done/viewer_schedule_loading.md`

**Deferred (the one named future item):** the on-tester **edit FAB** waits on the
editor being ported into the read core — extracted to
`../../20_deferred/tester_edit_fab.md` so it isn't lost.

**Owed (the user's git gate):** the uncommitted viewer-extraction batch + its
`sw.js`/`#appVersion` bumps (the working tree rode v66→v81 across these slices; `cdcc918`
committed v80, the rest is uncommitted). The loop never commits or bumps
(`../../../ai_rules/no_commits.md`). The extraction's value still rides on the user's
commit gate. The committed verifiers under `mvp/scripts/playwright_verify_*.py` should
be re-pointed at `old_index.html` or rewritten as viewer verifiers (noted on
`_done/viewer_swap.md` Follow-ups).

-----

## Why extraction, not subtraction (the decision)

Last turn the assistant proposed subtracting the editor out of `main.js` and keeping the rest. The user
corrected it, and the correction is right: subtraction *keeps everything you don't remove*, so the
viewer's accumulated debt survives by default. Extraction inverts the default — **nothing crosses into
the new viewer unless you deliberately move it.** When a "simple feature" demands a thousand lines, that
is the andon: stop and decide whether the feature is real or the code is bloated. Subtraction never
gives you that moment; extraction forces it on every feature.

**The precedent is already in this repo.** `website/js/panel.js` is exactly this play, run once on the
*editor* half. Its own header: *"clean rebuild… ONE source of truth… Map layers are added to MapLibre
here, exactly as the live app does… ported verbatim from main.js so the toggles are genuinely wired, not
faked."* This sprint runs the same play on the *viewer* half. It is not a novel risk — it is the
established pattern applied to the other side.

## The debt this surfaces (grounded, 2026-06-13)

The "many generations of viewer code" is real, on a **different axis** than Sprint 11's C1=0 finding.
C1 measured per-layer behavior branches at call sites (none exist). It said nothing about superseded
paths, redundant styling, or layers of UI exploration fossilized in one file. Both are true. Observed:

- **82** `legacy / used-to / kept-working / superseded` marker-comments inside the live `js/main.js`
  (`grep -cniE "legacy|deprecated|superseded|used to|formerly|kept .* working|one-shot" js/main.js`).
- **38** `leftrail_*.html` + **21** right-panel/editor mockup variants on disk — literal generations.
- **50** `hidden`/`legacy` attrs in `index.html` itself (the `#legacyLayerToggles hidden` pattern) — old
  DOM carried only so newer code stays wired.

The clean core routes around all of it. What earns a move comes; the sediment stays behind in git.

## Why the READ view is the right candidate

The danger in any clean rebuild is the source moving under you while you copy (the second-system trap).
The read view is the user's own *"good / mature / settled"* surface — it has stopped changing, so it is
not a moving target. The editor kept churning, which is why *it* got the messier in-place treatment; the
viewer can be copied cleanly. The left controls are the day-of read surface (`index.html:52`,
`.left-controls`): pill-bar (zoom region/park/pavilion · presets park/topo/trace/satellite · 3D),
left-rail drawer (Search · Hot now · Calendar→Events/POI/About), Locate, Install, version.

## How it's done

1. **Build alongside, never gut.** A fresh `website/viewer.html` + a small `website/js/viewer_core.js`.
   `index.html` keeps working the entire time as the reference — never a broken state. Diff the new
   viewer against the old behavior at every step. When proven, the clean viewer **becomes** `index.html`
   (still one canonical viewer at the finish — honors `ai_rules/editor_is_the_viewer.md`, rebuilt
   instead of pruned).
2. **The clean core is its own usage oracle.** Wire the left controls one at a time; trace each DOM
   control → its handler → its real dependencies; only *that* crosses. Code the new viewer never calls
   is, by definition, dead — no guessing.
3. **The playwright verifiers are the contract.** They define "the viewer still does what it did." Green
   on the new core = the port dropped no behavior. Same safety net the data convergence leaned on.
4. **The published-vs-reference layer split falls out for free.** Port only the layers the read product
   shows (presets + publish trails/boundaries/trailheads, buildings, cemeteries, visitor context,
   schedule, trail network). The dev-reference pile (9-patch AOI, lidar tiles, NAIP, OSM service, SFWDA
   raster, synthetic activity) simply never gets carried. The data-normalization line is drawn by what
   you choose to bring.

## The slate (clean core first, then one control per slice — each green before the next)

1. **`viewer_core_scaffold.md` — SLICE 1.** Empty clean core: MapLibre map + published-layer style/sources
   + region/park bounds + bottom ⓘ + an empty left-control shell. First feature ported in: **map presets
   + zoom + 3D** (the map basics). Establishes the real line-cost-per-feature.
2. *(card when slice 1 proves the pattern)* **Search** — `searchInput` + `buildSearchGroups` /
   `renderSearchResults` (`main.js:10076`/`10206`).
3. *(card later)* **Calendar / Events** — `calendarCard`, `calendarDays`, the shared
   `event_schedule_geojson.js` resolver.
4. *(card later)* **POI tab + popups** — `renderPoiTab` / `gotoPoi` / `poiPopupHtml` / `fetchPoiIndex`
   (`main.js:1238`/`1317`/`1339`/`490`) and the ★-curated destinations.
5. *(card later)* **Hot now** — `hotControl` (event lane + trail-activity lane).
6. *(card later)* **Locate, Install/PWA, version** — geolocate, install button + iOS hint, `sw.js`
   precache, `manifest.json`.
7. *(card later, the swap)* **Promote the clean viewer to `index.html`** — once every control is green,
   the new viewer replaces the old page; the editor lives in `panel.js` + the standalone field tools
   (`schedule_editor.html`, `data_editor.html`) + QGIS. This is the deletion step, and it is the user's
   git gate.

## Forks (recommendations — surface, don't block)

1. **Approach** — extraction to a clean core, not subtraction. *Decided by the user 2026-06-13.*
2. **The published layer line** (how 4 above gets drawn) — which of the 40 `LAYER_TOGGLES` (`main.js:1661`)
   are "day-of public" vs dev reference is a curation/permission call the northstar reserves for the user
   (the publishability gap: 6 of 160 features pass the publish gate today). The default split above is a
   proposal; the user owns the line.
3. **Sequencing** — unlike the editor pull, the viewer rebuild is built *alongside*, so it does **not**
   wait on anything. The only step that deletes old code is the final swap-in (slice 7), behind the git
   gate.

## Loop contract

Slices 1–6 build a NEW file and never touch the live `index.html`/`main.js` — low blast radius, a good
ralph-loop candidate once slice 1 proves the line-cost. Slice 7 (the swap) is high-blast and gated. No
commits without the user's git gate (`no_commits.md`); the `sw.js`/`#appVersion` bump is the user's.
