# Sprint 02: Editor & Polish

Raw drop lives in `tasks.md` — captures the live punchlist after Sprint 01 (MVP) closed. This file triages it into buckets so each item lands on the right card or earns a new one, with recommended order. The dump stays verbatim; analysis lives here, not on top of the user's words.

Center of gravity: editing and curation. Getting AOP-specific named features into the map, tightening viewer chrome, and deciding what "default-on" means now that the layer set is ~25 toggles wide. Offline/PWA is in scope but waits until the layer set stabilizes.

-----

## Source

- `tasks.md` — raw user dump, kept verbatim.
- `../01_mvp/_readme.md` — what shipped in Sprint 01.
- `../01_mvp/poi_editor.md` — existing editor card; several Sprint 02 items extend it.
- `../01_mvp/buildings_layer.md`, `visitor_context_callouts.md`, `event_schedule_layer.md` — existing cards touched by Sprint 02 items.
- `../../northstar/whats_this_for.md` — view/persona work has to start here.

## Triage

Items keep the user's phrasing in quotes; the surrounding line is the triage note. Order inside a bucket is rough priority.

### A. Decisions blocking other work

These need answers before B/E can ship the right defaults; otherwise we re-do this work next sprint.

1. **Views / personas.** *"figure out who/what each view is for. tighten in on their needs."* Region / Park / Pavilion presets exist; this asks who each preset serves (driver picking a rig? event organizer? first-time visitor? marshal?) and what each one's layer payload should be. Gating decision for items A2 and A3.
2. **Default-on layer policy.** *"come up with a list of always on… buildings / water / road. sometimes… bottom layer / topo / trails / waypoints."* and *"one view needs trails by default."* Current default-on set (`showLandcover`, `showLandcover9`, `showVisitorContext`, `showRoads`, `showTrails`, `showBoundaries`, `showTrailheads`, `showEditorPois`) is wider than the proposed "always-on" list and missing buildings + water. Settle the global default-on set, then which preset overrides it for trails.
3. **Left-side hot button.** *"need a dedicated hot button on the left. fire icon???"* Action TBD — likely candidates: jump to the live event / current pavilion / "what's happening now." Pin down the action before drawing the icon.

### B. Viewer chrome (quick wins, no decisions needed)

Each is ~½ day or less. Group into one card if work happens together.

- *"magnifing glass on search"* — SVG search icon on `#searchInput` (`website/index.html:125`).
- *"make edit panel pop up from the bottom right. on mobile when collapsed its floating in the middle."* — restyle the POI editor panel's collapsed state; pin bottom-right on desktop, dock cleanly on mobile.
- *"collapse calendar on mobile / narrow widths automatically"* — media-query collapse of the event-schedule sidebar.
- *"calendar needs time"* — `aop_event_schedule.json` already carries `time_label`; verify the sidebar row renders it; fix if not.
- ~~*"our region circle callouts need to be positionable"*~~ — resolved 2026-05-23. The visitor-context callouts now consume the shared find + move primitive from `poi_editor_v2.md`. Override store: `aop_visitor_context_overrides_v1`.
- *"layers need text tweaking. currently trace has text hard to read."* — typography pass on label layers; trace label legibility first.
- *"when following a link from the calendar the item is selected and a tooltip pops up… overlap on some screens… scroll to make the tooltip in view"* (2026-05-23 addition to `tasks.md`) — on narrow viewports the `gotoEventSession` popup overflows the chrome. Fix: rect-aware visible-map slice + `panBy` after `moveend` to pull the popup inside. Lands in `viewer_chrome_polish.md` as B1.

### C. Search

- *"search should be able to search tags"* / *"ability to search tags"* — duplicated in the dump, signal of priority. Extend `searchIndex` (`website/index.html:461`) so POI tags (`#pavilion`, `#registration`, `#observed-trailhead`, etc.) resolve.

### D. Named-feature tagging (one card, content not code)

Data items, not features. Right home: a new card that uses the existing POI editor to enter and persist them. Some need source confirmation before they're publishable.

- *"see if we can get trail names"* — research step; check SFWDA paper map, OSM, RiderPlanet, ask AOP.
- *"tag cabins / campsites / pavillion bathrooms"*
- *"tag excavator hill / big log / jeep entrance / buggy entrance"*

### E. Buildings layer tweaks (extend `../01_mvp/buildings_layer.md`)

- *"make buildings show up by default"* — flip `showBuildings` to `checked` once Bucket A2 confirms it belongs in always-on.
- *"prune buildings outside of bounds ???"* — resolved 2026-05-23: not a hard prune. The Bucket G feature list panel renders the 4 in-park buildings as named rows pre-ticked, with the 198 outside-park buildings collapsed under a bulk-toggle row default-off. The data stays full; only what draws is filtered. See `poi_editor_v2.md`.

### F. Branding

- *"add aop logo"*
- *"add rock warblers logo"*
Needs an asset drop + placement decision (header? attribution corner? on-map?). Small card. If the logos land on the map (not in the chrome), they consume the shared "find + move" primitive from `poi_editor_v2.md` so placement is tuneable without code edits.

### G. Feature list panel — POI editor v2 + shared primitive

- *"we need a editor for points of intrest"* + user clarifications (2026-05-23):
  - POIs: *"poi editor needs a list of all pois on the right. selecting one allows us to find it and move it. same kinda move as the map region info. and same kinda move as future logos on map."*
  - Buildings: *"I kinda figured that we may have a list of all buildings on the right under the building layer and we could turn them on or off based on need."*
  - Cemeteries: *"I really only care about cemeteries in the park. there are extra."*
- Scope broadened from "POI list with drag" to a **feature list panel** that drops under any layer's right-panel row. Per-feature actions (visibility, fly-to, drag-to-move) are opted into per consumer. First three consumers: POIs (all three), Buildings (visibility + fly, grouped: 4 in-park named + 198 others collapsed bulk), Cemeteries (visibility + fly, 4 rows with Ellis pre-ticked). Region callouts (Bucket B) and on-map logos (Bucket F) consume the drag side later. Card: `poi_editor_v2.md`.

### H. Code / CSS health pass

- *"css needs a review top to bottom"*
- *"code needs a review for smells"*
Fold into a Pass 3 on the existing `../01_mvp/code_health_pass.md` (which already carries deferred cosmetic items). Do this after Buckets B/D/E land so the pass also cleans the new code.

### I. Performance & offline — deferred

Largest bucket; multi-phase; waits for a stable layer set so the measurement isn't against a moving target. Parked at `../03_deferred/offline_pwa.md`. Covers all four dump items: site weight measurement, reduction, caching, and PWA.

## Recommended order

1. **A1 → A2 → A3** decisions (otherwise B/E ship the wrong defaults).
2. **G** POI editor v2 + shared positioning primitive (early, because B's callout-positioning and F's optional on-map logos both consume it).
3. **B + C** in parallel (all small; B's callout item adopts the primitive from G).
4. **D** named-feature tagging (also unblocks the deferred offline card — measure against a populated map).
5. **E / F** — small dependent items.
6. **H** code/CSS pass after the above churn settles.

Bucket **I** is deferred to `../03_deferred/offline_pwa.md`; it re-enters the active sprint when the layer set stabilizes.

## Cards to spawn (in this sprint)

- `02_edit/views_and_defaults.md` — Buckets A1, A2, "trails by default."
- `02_edit/left_hot_button.md` — A3 (or fold into views card once personas are defined).
- `02_edit/poi_editor_v2.md` — Bucket G. **Written + shipped 2026-05-23.** Three consumers wired (POIs, buildings, cemeteries) plus the visitor-context drag consumer that closes Bucket B's positionable-callouts item.
- `02_edit/viewer_chrome_polish.md` — Bucket B. **Written 2026-05-23.** B1 (calendar popup scroll-into-view) in progress; B6 (region callouts positionable) closed via `poi_editor_v2.md`.
- `02_edit/search_tags.md` — Bucket C.
- `02_edit/named_feature_tagging.md` — Bucket D.
- Extend `../01_mvp/buildings_layer.md` in place — Bucket E.
- `02_edit/branding.md` — Bucket F. **Written; raw asset drop staged.**
- Bucket H folds into `../01_mvp/code_health_pass.md` Pass 3.

## Deferred (sister sprint)

- `../03_deferred/offline_pwa.md` — Bucket I.
