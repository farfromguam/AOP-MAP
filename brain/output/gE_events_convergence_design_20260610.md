# G_E — Events overlay convergence: design (design-FIRST, before code)

> Slice: `brain/tasks/06_going_gold/gold_slice6_backlog.md` G_E + the G_A item
> "Event umbrella metadata → core.events row". Findings (verbatim catalog in
> `tasks/09_editor_maturity/shadow_attributes_audit.md`):
> `event-overlay-two-divergent-resolvers` (C1/C6), `event-anchor-position-from-localstorage-tag-binding`
> (Tier1 geom + Tier3 tag), `event-umbrella-metadata-hardcoded-in-bake` (Tier1/2).
> Authored 2026-06-10 by the G_E agent BEFORE touching code (the prior slices stalled
> on incomplete consumer maps — this is exhaustive).

#aop #06_going_gold #gE #events #convergence #design

-----

## 1. The exhaustive consumer map (BOTH resolvers, BOTH panel.js modes)

The served file `website/data/aop_event_schedule.json` is a `{schema,updated_at,status,event,locations{},sessions[]}`
**document** (NOT a FeatureCollection). Two transforms parse it.

### Resolver A — `eventScheduleToGeojson(config)` (main.js:6366) — the RICH, live one
Helpers: `resolveEventLocation` (6288), `buildEventLocationIndex` (6322), `eventRouteCoordinates` (6356),
`normalizeLocationTag` (6282), `composeEventWindowLabel`/`formatEventStartLocal`/`eventDayShort`.
Module-scoped state it reads/writes: `eventLocationByTag` (Map), `tagToFeature` (Map, the
localStorage `aop_feature_tags_v1` working buffer), `eventSessionById` (Map, side-effect).
Emits anchor **Points** (`feature_kind:'event_anchor'`, full props: name/map_label/role/source/confidence/caveat)
AND session **LineString|Point** features (`feature_kind:'event_session'`, props: title/day/window/
location_label/route_tags/route_labels/poi_role/status/inspired_by/caveat) + a top-level `metadata{schema,updated_at,status,event}` block.

**Consumers of Resolver A (the real viewer — index.html, where both main.js + panel.js load):**
1. Map source `event-schedule` (main.js:8339) → 4 layers: `event-session-routes`, `event-route-labels`,
   `event-anchor-points`, `event-anchor-labels` (8345-8405).
2. Popups (`bindPopup` 8407/8416) — read `name`/`location_tag`/`role`/`confidence`/`source`/`caveat`
   (anchor) and `title`/`day`/`window`/`location_label`/`route_tags`/`status` (route).
3. Calendar `renderEventSchedule(config, data)` (main.js:7183) — reads the **document** (`config.sessions`,
   `config.event.date_range_label`/`end_date_label`) for the 13 rows + state machine + countdown banner;
   reads `data` for the resolved location label per row.
4. Search index `indexFeatures(data, …)` (8426) — anchors searchable by `#tag` alias, sessions by title.
5. Feature-list CRUD runtime `registerFeatureListLayer('eventSchedule', data)` (8435) — the right-panel
   editor list of event features.
6. Hot button `computeHotButtonTarget`/`refreshHotButton` — reads `eventSessionById` + `eventLocationByTag`.
7. Tag-rebind live path `rebuildEventScheduleData` (6446) — re-runs A on a `#tag` edit, pushes to all of the above.

### Resolver B — `resolveEventSchedule(json)` (panel.js:335) — the STRIPPED reimplementation
Plus `roleForTag` (panel.js:327, a string-match heuristic; unmatched → `'pavilion'`).
Reads ONLY `json.locations`; emits anchor Points for tags that carry inline `coordinates`;
`name`=`map_label`=tag-without-#; **IGNORES `sessions[]` entirely** (no routes, no session points);
coordinate-less tags (#pavilion) **do not draw at all** ("simply don't draw here", panel.js:326).

**Where Resolver B is actually LIVE:**
- **Standalone** (right_panel.html — ONLY panel.js loads): `bootStandalone` (panel.js:2197) calls
  `fetchAllData` → `set.resolve = resolveEventSchedule` (panel.js:516) → `LOADED['event-schedule']` →
  `map.addSource('event-schedule', …)` (2211) + the 4 layers (panel.js:518-522). **This is the only place
  Resolver B's GeoJSON reaches a map.**
- **Embedded** (index.html — main.js + panel.js): `bootEmbedded` (panel.js:2227) does NOT add the
  `event-schedule` source/layers (only `userFeatures` + draft). `fetchAllData` STILL runs
  `resolveEventSchedule` into `LOADED['event-schedule']`, but `seedLoadedFromHost` (panel.js:2005) then
  overwrites `LOADED` from the host's live sources, and the `eventSchedule` PANEL_MODEL node (panel.js:690)
  has **NO `items` accessor** — so Resolver B's output is dead in embedded mode. **CONFIRMED by reading the code.**

**Net:** Resolver B is a stripped duplicate whose only live effect is the standalone right_panel.html map
(anchors only, wrong names, sessions missing, #pavilion absent). It diverges from A on every axis the finding names.

## 2. The ONE canonical transform + the single resolve path

**Decision: one shared pure function `eventScheduleToGeojson(config, opts)` in a NEW
`website/js/event_schedule_geojson.js`, loaded by BOTH index.html and right_panel.html.** Both surfaces
call the SAME function. As shipped: `roleForTag` and the stripped `resolveEventSchedule` body are DELETED
from panel.js; `resolveEventSchedule` survives only as a one-line delegating wrapper
(`return window.AOPEventSchedule.eventScheduleToGeojson(json).geojson`). This is "one
transform, no two functions that can drift" (C1) and is NOT a new registry / class / parallel editor surface
(C6 forbids a new editor *bundle*; a shared pure resolver module is the convergence the contract wants).

Why a shared module, not "panel calls main.js's function": in standalone mode main.js is NOT loaded, so the
function must live somewhere both pages reach. Why not factor the existing one OUT of main.js wholesale: it
is entangled with module-scoped `eventLocationByTag`/`tagToFeature`/`eventSessionById` and the search/calendar
plumbing — pulling it out risks the live viewer (the slice forbids regressing it). Instead the shared module
exposes a **pure** `eventScheduleToGeojson(config, { resolveTagCoords })`:

```
window.AOPEventSchedule.eventScheduleToGeojson(config, opts) -> { geojson, locationByTag, sessionById }
  opts.resolveTagCoords(normalizedTag) -> [lng,lat] | null   // OPTIONAL working-buffer override hook
```

- It bakes the canonical shape (anchors + sessions + metadata) — byte-for-byte the logic of today's
  main.js `eventScheduleToGeojson`, including alias resolution, route coords, window labels.
- Coordinate priority: **explicit `location.coordinates` in the served doc win** (now always present after
  item 2's bake). When absent AND `resolveTagCoords` is supplied, fall back to it (the host's localStorage
  `tagToFeature` buffer). The panel passes NO hook → it relies purely on baked coordinates. This makes
  localStorage an override/working-buffer, not the source of an anchor's position (`event-anchor-position-…` target).
- main.js's wrapper keeps the SAME name/signature (`eventScheduleToGeojson(config)`), now delegating to the
  shared fn with `resolveTagCoords: (tag) => tagToFeature.get(tag)?.coordinates || null`, and re-populating
  its module maps from the returned `locationByTag`/`sessionById`. ZERO change to main.js's downstream
  consumers (calendar/search/CRUD/hot button/rebind) — they read the same `eventScheduleData` + maps.
- panel.js's standalone `event-schedule` source uses `set.resolve = (json) =>
  window.AOPEventSchedule.eventScheduleToGeojson(json).geojson` → now draws anchors (correct names) AND
  session routes/points, with #pavilion present (baked coords). The 4 standalone layers already match the
  host's filters/paint, so they light up unchanged.

**The document shape stays a document.** The calendar/hot-button/state-machine consume `config.sessions[]` +
`config.event.*` directly — that is NOT collapsed. "One baked event feature collection" = the ONE GeoJSON the
shared transform emits from that document, read identically by both maps. Both the document (served file) and
its transform (shared fn) are now single-home.

## 3. Item 2 — coordinate-less anchors get baked geometry

Root state (observed in the live DB, 2026-06-10): the `#pavilion` event-place row
(`core.features` `source_key='editorPois:aop-pavilion'`, layer `poi`) **already carries a geom**
`[-85.7482512, 35.0907264]` (the pavilion building point). All 7 event-place rows have geom. The served
HEAD file omits `#pavilion.coordinates` ONLY because it is stale (predates the geom). The bake already does
`'coordinates', ST_AsGeoJSON(geom,9)::json->'coordinates'`, so **re-baking emits #pavilion coordinates with
no script change** — the served file becomes self-sufficient. `#tag` is already a baked facet
(`attrs.event_location->>'tag'` → the locations key). localStorage `tagToFeature` becomes the optional
`resolveTagCoords` override only.

Verified pre-existing FAIL (HEAD, empty localStorage, `--baked`): "a #pavilion session resolves to the baked
pavilion place point" = coords=None; "baked event-place anchors carry their names" missing AOP Pavilion.
After adopt these go GREEN with no localStorage — the self-sufficiency proof.

## 4. Item 3 — event umbrella metadata → DB store of record

Today: a hardcoded `EVENT_META` heredoc in `export_publish_geojson.sh` (lines ~258-273) supplies
`{schema, updated_at, status, event{id,label,date_range_label,end_date_label,source_context,source_summary,caveat}}`.

**Home: a NEW additive table `core.event_meta`** (idempotent, follows the `core.events`/`core.activities`
pattern — soft text keys, `attrs` jsonb, `archived_at`, updated_at trigger). One row per umbrella event,
keyed `event_id`. Columns map CMFS: `event_id` (= the umbrella id), `label` (Tier1 name), `status` (Tier2),
`schema`, `date_range_label`, `end_date_label`, `description`/`source_summary`, `source_context`, `caveat`,
`updated_at`, plus `attrs` for any future field (no allowlist). The bake composes the document wrapper from
this row instead of the heredoc.

Why a dedicated table, not a `core.events` umbrella row: `core.events` rows are sessions (sort_order/place_key/
activity_key) — an umbrella row there is a malformed session. The card explicitly allows "a dedicated umbrella
row/table … additive." A table is the clean CMFS home and keeps the sessions table pure.

Sync: add the table DDL to `mvp/init_db.sql` (DDL only — no seed INSERT there) and seed the umbrella row
with an idempotent script `mvp/scripts/seed_event_meta.py` (mirrors `import_event_schedule_to_core.py`'s style)
that upserts the current umbrella values from the served file's `event`/`schema`/`status`/`updated_at`. The
bake reads the row; if the row is absent it FALLS BACK to the prior heredoc constants (C5 — never throw,
never emit a broken file on a fresh volume that hasn't seeded).

## 5. Files to change

- NEW `website/js/event_schedule_geojson.js` — the ONE shared transform (`window.AOPEventSchedule`).
- `website/index.html` — load the shared module before main.js.
- `website/right_panel.html` — load the shared module before panel.js.
- `website/js/main.js` — `eventScheduleToGeojson` delegates to the shared fn (keep name/maps).
- `website/js/panel.js` — DELETE `roleForTag` + the stripped body; reduce `resolveEventSchedule` to a one-line delegating wrapper → shared fn.
- `mvp/init_db.sql` — `core.event_meta` table DDL + trigger (no seed INSERT; the row is seeded by `seed_event_meta.py`).
- `mvp/scripts/seed_event_meta.py` — NEW idempotent umbrella upsert.
- `mvp/scripts/export_publish_geojson.sh` — read umbrella from `core.event_meta` (fallback to heredoc).
- `website/data/aop_event_schedule.json` — ADOPT the re-baked file (gains #pavilion coords + session activity blocks).
- `mvp/scripts/playwright_verify_event_schedule.py` — extend with convergence assertions.

## 6. Verification plan (by observation)

(a) live index.html on :8001: calendar renders 13 sessions; map renders anchors + session routes; search
finds `#pavilion`; 0 console errors; **#pavilion anchor renders on FRESH localStorage** (clear it) —
`--baked` mode's two pre-existing FAILs go GREEN. (b) standalone right_panel.html renders the event layer
WITH session routes + #pavilion + correct names. (c) `export --check` = `same` on aop_event_schedule.json.
(d) DB row count unchanged except the +1 additive `core.event_meta` row. (e) extend + run
`playwright_verify_event_schedule.py` green; pre-existing fails noted separately.

## 7. Pre-existing baseline (stash/replay proof these predate me)

Against HEAD, `playwright_verify_event_schedule.py --baked` (empty localStorage) = 2 FAIL:
- "a #pavilion session resolves to the baked pavilion place point" (coords=None — no baked #pavilion coords)
- "baked event-place anchors carry their names" (AOP Pavilion anchor absent)
Both are the EXACT symptom item 2 fixes; they go green after adopt. No other fails in `--baked`.
