# Sprint 07 — Tables: wiring Where × When × What

> **Source:** the user's `breif.md` in this folder (raw thought, kept verbatim).
> This card is my read of it, written to be reviewed by the council before any code.
> **Status: DESIGN ONLY.** It depends on Sprint 06 (`core.features`) landing first —
> see "Sequencing" — so nothing here is executable yet.
> **Fork RESOLVED by the user, 2026-06-06:** *"the events usually are at the same place
> sometimes they are different. they are only tied to the place when the schedule says so
> for that occurance and at the #location tagged."* → the place binds on the **occurrence**
> (the schedule row), via the `#location` tag — never on the activity. So the activity
> catalog IS in scope. See "The resolved model."

TL;DR:
- The pattern you're feeling is real, and it's **relational normalization**: don't
  bake the "what" into each "when." Store each thing once, reference it.
- **WHERE is done** — the gold `core.features` table already gives every place a
  JSONB `attrs` bag. A place's own data is its feature's `attrs`.
- **WHAT-reusable is a new table: `core.activities`.** The hill climb, the RC rally,
  the rock-hard tour — reusable, **place-agnostic** content cited by the schedule.
  It does NOT own a location (that's the user's call: an activity is usually at the
  same place but sometimes moves).
- **WHEN is the junction table: `core.events`** (one occurrence per row). Each row
  binds `(time, activity-ref, place-ref via #location tag)`. **The place lives here,
  per occurrence** — set by the schedule, resolved through the `#tag`, never stored on
  the activity. Same hill climb Saturday at `#hillclimb`, Sunday elsewhere — just two
  rows. All references are **soft references by `source_key`/key — not copies, not
  enforced FK constraints** (see the no-limiting-code note).
- **WHAT-place-attached ("abouts": rock warblers, to-town, about AOP) is NOT a new
  table** — they're already features; the about is a richer body on the feature. The
  test: *does the schedule cite it (→ `core.activities`) or does a place own it
  (→ feature body)?*

#aop #sprint #07 #tables #events #schedule #postgis #normalization #ralph

-----

## Your three models, mapped to what already exists

You named them exactly right: **where**, **when**, **what**. Here's where each one
actually lives once the gold migration lands.

| Your model | Lives in | State |
|------------|----------|-------|
| **WHERE** — "where things are" | `core.features` (CMFS columns + JSONB `attrs`) | Being built now (Sprint 06 gold migration) |
| **WHAT** — "what things are about" (reusable activity, e.g. hill climb) | **`core.activities`** — CMFS shape, no geometry, place-agnostic | **New table.** The reusable content the schedule cites. |
| **WHAT** — place-attached "abouts" (rock warblers, to-town, about AOP) | `core.features` — a richer body on the feature | Already features; not a new table |
| **WHEN** — "when things are" | `aop_event_schedule.json` → promote to **`core.events`** (the occurrence/junction) | Half-built: a *proposed* side-JSON, 13 sessions, already keyed to places by `location_tag` |

So: **two new tables** — `core.events` (the junction) and `core.activities` (the
reusable what). `core.features` (where) is the gold migration's; place-attached abouts
ride it. The schedule resolver in the viewer is *extended*, not rebuilt.

## The hole isn't a missing table — it's a missing *join*

> "at 1:30pm is a hill climb at #hillclimb location and the hillclimb has this
> specific data... the hillclimb will be re-used and will not be tied to a singular
> event time."

That sentence is a JOIN across **three** things — and your follow-up ("usually same
place, sometimes different; only tied to the place when the schedule says so for that
occurrence at the `#location` tagged") tells me how they connect:

- **the hill climb + "its specific data"** → the **activity** (`core.activities`):
  the reusable what (grade, length, gate list, rules). It is **place-agnostic** —
  because you said it can move places. Edit the hill climb once → every occurrence
  that cites it updates. This is the reusable record you were reaching for.
- **`#hillclimb` for this occurrence** → a `#location` tag that resolves to a
  `core.features` row (the place). ✅ gold migration. The activity does **not** store
  this — the **occurrence** does, via the tag, "when the schedule says so."
- **at 1:30pm** → the **occurrence** (`core.events`): one row binding
  `(time, activity-ref, place-ref-via-#tag)`. Same hill climb, Saturday at
  `#hillclimb`, Sunday at `#north-technical` → two occurrence rows, one activity, no
  copies. **That occurrence is the hole** — the junction that ties when × what × where
  without baking the what into the when.

The reason the activity's data lives on the activity and **not** on the place: if it
lived on the `#hillclimb` feature, the hill climb couldn't move to another place
without leaving its data behind. Place-agnostic activity + per-occurrence place tag is
exactly what "usually same place, sometimes different" requires.

The schedule already gestures at this: every session today carries
`"location_tag": "#pavilion"` and `route_tags` (`aop_event_schedule.json`,
schema `aop-event-schedule-v1`, all 13 sessions carry a `location_tag`). And the
viewer **already has a resolver engine** that does exactly this join in the browser —
`resolveEventLocation` / `eventScheduleToGeojson` / `rebuildEventScheduleData` / the
`eventSchedule` spec on `FEATURE_LIST_LAYERS` (`website/js/main.js:6280-6357`,
`:469`, `:2729`). At runtime `#pavilion` resolves to the **seeded editor POI
`aop_seed_pavilion`** (the binding was migrated *off* the 1010 building on
2026-05-26 — `main.js:37-41`, `:7345`, `:7361`; the schedule JSON's prose `source`
field still says "1010 building" and is itself stale). So the join already exists as
a **string tag resolved in the browser, against a binding that lives in JS**. Sprint
7 doesn't *wire a hole from scratch* — it **extends that resolver**: the binding
moves into `core` (the soft reference), and the schedule JSON becomes the **bake output** of the
same `eventScheduleToGeojson` path, so the join survives the gold migration's
one-writer bake instead of living in browser state.

## The resolved model — two new tables

WHERE (`core.features`) lands in the gold migration; place-attached abouts ride it.
Sprint 7 adds **two** tables: the reusable WHAT (`core.activities`) and the WHEN
junction (`core.events`). The viewer's schedule resolver is *extended*, not rebuilt.

**`core.activities`** — the reusable, place-agnostic WHAT (hill climb, RC rally,
rock-hard tour):
- `id`, **`activity_key text UNIQUE`** (the stable name the schedule cites, e.g. `hill_climb`)
- `name`, `kind`, `description` — CMFS identity fields, same as a feature
- `attrs` JSONB — the "specific data" (grade, length, gate list, class rules, scale
  vocabulary). No allowlist, no enum.
- source-register provenance, `archived_at` — same contract as `core.features`.
- **No geometry, no place column.** An activity is not a place; it never owns a
  location. (This is the user's resolution: the place binds on the occurrence.)
- It is the **same CMFS shape as `core.features` minus geometry** — one vocabulary,
  not a second one. A sibling table, not a second engine.

**`core.events`** — the WHEN junction (one row per occurrence; call it sessions/occurrences):
- `id`, `event_id` (the umbrella event), `title`, `starts_at` / time label, `status`
- **`activity_key text` → soft-references `core.activities.activity_key`** — the WHAT
- **`place_key text` → soft-references `core.features.source_key`** — the WHERE, *for
  this occurrence*, = today's `location_tag` (`#hillclimb`). Per-occurrence, never on
  the activity.
- `attrs` JSONB — per-occurrence extras (`inspired_by`, `route_tags`, sort order).
  No allowlist, no enum.

**No-limiting-code note (the seat that pulled andon on this — Mason).** `activity_key`
and `place_key` are plain `text` reference columns that **soft-join** on
`core.activities.activity_key` / `core.features.source_key` at bake/render time. They
are **NOT** enforced Postgres `FOREIGN KEY ... REFERENCES` constraints. An enforced FK
would raise `23503` and **reject** any occurrence whose activity or place isn't yet in
`core` — the exact throw-on-unmatched / row-rejection the gold migration bans
(`gold_migration.md:38-44`, `:177-189`). Instead: an occurrence pointing at a
not-yet-present activity or place is **stored and resolved later**, never dropped —
same upsert-with-`notes`-flag posture as `apply_panel_overrides_to_core.py`. The
relational *idea* of a foreign key (point, don't copy) without the relational
*constraint* that limits.

Then the schedule JSON becomes **bake output, not source of truth** — exactly what
the deferred `event_crud_upload_loop.md` already wrote: *"Seed from
`aop_event_schedule.json` or generate that JSON from the database. Long term, the
JSON is output, not source of truth."* So WHEN rides the **same one-writer bake** as
every other layer in the gold migration. No new pipeline.

## The "abouts" — your real question, answered

> "we kinda have abouts circled around -- an about for aop / rock warblers / to town
> pittsburgh / to other town. I am not sure if this is the ~same things... or we
> should be storing this in the geojson."

Your brief mixed two kinds in one list, and they split by **one test: does the
schedule cite it, or does a place own it?**

- **Schedule-cited, place-agnostic** (RC rally, rock-hard adventure tour, hill climb)
  → `core.activities`. These ARE the new reusable WHAT — see the resolved model above.
- **Place-attached narrative** (rock warblers, to-town, about AOP) → **not a new
  entity; a richer body on the feature.** Every one is already a real feature:

- **rock warblers** + **about AOP** — already **point features** in
  `aop_visitor_context_callouts.geojson` (`id:"rock_warblers"`, `id:"aop_badge"`,
  both `kind:"brand_logo"`, Point geometry). An "about" for them is a richer
  `description` + `attrs.detail` body **on that feature.**
- **"to town pittsburgh" / "to other town"** — already point features in the same
  file (`kind:"visitor_callout"`: "South Pittsburg / Kimball supply run", "Monteagle
  plateau services"). Wayfinding content is again a feature's body.
- **genuinely place-less park-level content** (a general "About AOP" page with no
  obvious single dot) — give it a **representative anchor point** (the park centroid,
  or G-Central), `kind='about'`. **Do not give it null geometry.**

**Why not `geom NULL` (the seat that pulled andon — Quartermaster).** I first wrote
"a `geom NULL` row, the list panel renders features independent of geometry." That is
**false against the code.** The one list engine is geometry-required at every node:
`eventScheduleToGeojson` drops geom-less locations (`main.js:6287`
`if (location.hidden || !location.coordinates) continue;`), the anchor block of the
single collector `collectStarredDestinations` drops them (`main.js:1264`), every row
carries a `feature` + a fly button (`makeFlyButton`/`flyToFeature`,
`popupCoord: firstCoordinate(...)`), and the bake emits `"geometry": null`
(`export_publish_geojson.sh`) which MapLibre cannot add to a source. A geom-NULL
"about" would be a **new untested path**, not reuse. So the reuse-safe answer is: a
place-less about rides the **proven geometry-bearing row path** via a representative
anchor point. **That keeps it one feature engine — genuinely reused, not assumed.**

**So: place-attached abouts go in the feature (the geojson/`attrs`), not a separate
"abouts" table.** A general-purpose content store *on top of* both features and
activities would be a third list engine + a third bake — the duplication the gold
migration and the Quartermaster seat exist to prevent (C2/C6). The reusable WHAT earns
exactly one table (`core.activities`, the CMFS shape without geometry); place-attached
content stays feature data.

## The fork — RESOLVED by you (2026-06-06)

> *"the events usually are at the same place sometimes they are different. they are
> only tied to the place when the schedule says so for that occurance and at the
> #location tagged."*

This settled it: an activity **recurs across places** (usually the same, sometimes
not), and the tie to a place is made **at the occurrence**, by the schedule, through
the `#location` tag — never on the activity. So:

- The activity catalog (`core.activities`) **is in scope** — it's the only way one
  hill climb can move places without copying its data.
- The `place_key` lives on `core.events` (the occurrence), not on the activity.
- "Usually same place" needs **no default-place field** on the activity — most
  occurrences just reuse the same `#tag`. A default would be a value that goes stale;
  per-occurrence-explicit is both simpler and less-limiting (C5).

The thinnest **first slice** still starts small: stand up `core.events` against the
existing 13 schedule sessions (which already carry `location_tag`), prove the
occurrence→place join bakes, **then** introduce `core.activities` and the
`activity_key` on the same junction. Two slices, both inside this model.

## Sequencing (why this is design-only today)

Sprint 7 **depends on Sprint 06.** You cannot wire a `place_key` reference into
`core.features.source_key` until `core.features` exists and carries `source_key`.
Gold slice 1 (the `core.pois` author path) has closed; `core.features` arrives at
slice 2 and the layers migrate in across slices 2–5. The active gold-migration ralph
loop is building it now (the handoff's ▶ ACTIVE block runs it in a fresh session).

So the order is fixed:
1. Gold migration lands `core.features` + `source_key` (Sprint 06, slices 2–5).
2. **Then** sprint 7: add `core.events` (+ `core.activities`), the `place_key`/
   `activity_key` references, bake the schedule JSON from them. Same thin-slice,
   observe-don't-narrate, archive-not-delete contract as the gold migration — sprint 7
   is the *next layer of the same migration*, not a new project.

Starting sprint 7 code now would collide with the in-flight loop. This card is the
direction so it's ready to pull the moment gold lands.

## What this reuses (so the Quartermaster doesn't have to ask)

- `core.features` + `attrs` — the WHERE, plus place-attached abouts. Not rebuilt.
- The **CMFS shape** (`research/common_feature_schema.md`) — `core.activities` reuses
  it (minus geometry), so the editor reads an activity with the same frame it reads a
  feature. One vocabulary, not a second.
- The existing `aop_event_schedule.json` shape (`event` / `locations` / `sessions`)
  — it becomes the bake *output target*; its session fields are the `core.events`
  columns, its `locations` block is the `place_key` tags.
- The `location_tag` → place resolution that already runs in the viewer
  (`eventScheduleToGeojson`/`resolveEventLocation`) — it becomes a soft reference by
  `source_key`, baked instead of resolved in browser state.
- The one bake (`export_publish_geojson.sh`) — extended to emit the schedule, not a
  parallel pipeline.
- The deferred `event_crud_upload_loop.md` — sprint 7 is the **data-model half** of
  it (staff event CRUD §1), unblocked early; uploads/moderation/submissions (§2–4)
  stay deferred (northstar V2).

## Owed / not in scope

- No prod write-service, auth, moderation, or upload intake — that's V2, deferred.
- No separate content store for place-attached abouts — they're feature data.
- No default-place field on activities — the place is per-occurrence (user's call).
- `core.activities` reuses the CMFS shape; it is not a second vocabulary.
- File `breif.md` keeps the user's spelling; flag only.

-----

# Execution plan — slices (ready to pull)

> Added 2026-06-07 when the **dependency landed**. The design above is council-cleared
> (full six, 2 rounds). This section turns it into an executable, ralph-loopable spine —
> the gold-migration form: sequenced slices, **tile-independent acceptance**, a Loop
> contract, run commands. It inherits the gold council's standing conditions. **Still
> design/plan — no code or DB written yet.** Per the gold precedent, the next step is the
> user's: council-review this plan → commit pause → ralph loop.

## Dependency: SATISFIED (verified by observation, 2026-06-07)

Sprint 06 gold migration is COMPLETE, so Sprint 7 is now pullable. Confirmed against the
live DB (`mvp/docker-compose.yml`, db `aop_map` on `:55432`), not the card's word:
- `core.features` exists — full CMFS spine + `source_key text UNIQUE` + `attrs jsonb` +
  `archived_at` + `geom geometry(Geometry,4326)`. **141 rows** (buildings 5, cemeteries 8,
  poi 4 [3 active + 1 archived test], trails 120, visitor 4).
- `publish.features` view live; `core.pois` / `publish.pois` **dropped** (the 2026-06-07
  human-owed DROP). `core.features` is the sole feature/POI table.
- `#pavilion` resolves to the seeded editor POI `editorPois:aop-pavilion`
  (`core.features`, `layer='poi'`) — the binding the schedule resolver uses.
- Viewer resolver intact: `resolveEventLocation` (`main.js:6202`), `eventScheduleToGeojson`
  (`:6280`, drops geom-less at `:6287`), `rebuildEventScheduleData` (`:6360`),
  `collectStarredDestinations` (`:1152`, anchor-drop `:1261`). The schedule is loaded at
  `main.js:8181` (`fetchJson('./data/aop_event_schedule.json')`); 13 sessions, schema
  `aop-event-schedule-v1`.

## Review deltas found (flag-only — not edited; editing them owes a shell bump)

Following the gold loop's precedent of not triggering a `sw.js`/`#appVersion` bump for a
comment, these are recorded, not fixed:
1. **Stale `#pavilion` prose.** `main.js:6224` comment still says `#pavilion` "picks up the
   1010 building's representative point"; the binding moved to `editorPois:aop-pavilion` on
   2026-05-26 (`main.js:37`, `:2378`). The schedule JSON's `locations["#pavilion"].source`
   prose likewise still names "1010 building." Accurate as history; both are stale as fact.
2. **The tag→place wrinkle the design glossed.** Of the 7 location tags, **only `#pavilion`
   is feature-backed**; the other 6 (`#observed-trailhead`, `#observed-finish`,
   `#proving-grounds`, `#north-technical`, `#night-checkpoint`, `#photo-waypoint`) carry
   **inline `coordinates`** and have **no `core.features` row**. The card's "`place_key` →
   `core.features.source_key`" only holds for `#pavilion` as written. **Resolution
   (recommended, council to confirm): migrate the 6 anchors into `core.features`**
   (`layer='event'`, `kind` = their `role`, non-publish permission per their 'proposed'/
   observed confidence) so `place_key` resolves **uniformly** through `core.features.source_key`
   — reuses the gold spine, **adds no third table**, keeps the two-table model. The
   alternative (a `core.event_locations` tag registry) is viable but is a new surface; the
   anchor-migration is the reuse-first answer. Either way **no row is dropped** — the
   resolver already supports "explicit coords win, else bound feature."

## Slices

### Slice 1 — `core.events` + the 13 sessions; bake the schedule from the DB
The hole: the WHEN junction. Stand it up and prove the schedule JSON becomes **bake output**,
not hand-curated source — so it survives the gold one-writer bake.
- Migrate the 6 coordinate anchors → `core.features` (`layer='event'`; non-publish), so all
  7 tags resolve through `core.features.source_key`. (Per delta #2; council confirms.)
- DDL (additive, `init_db.sql` fresh-volume + applied by hand to the live volume, the gold
  pattern): `core.events` — `id`, `source_key text UNIQUE` (= session `id`, e.g.
  `fri-registration`), `event_id text`, `session_id text`, `sort_order int`, `title text`,
  `starts_at` / `start_local` / `time_label` / `date_label`, `status text`,
  **`place_key text`** (soft-ref `core.features.source_key`, = today's `location_tag`),
  `attrs jsonb` (`inspired_by`, `route_tags`, etc.), `archived_at`, `source_id`. **No
  CHECK/enum, no FK constraint** on `place_key` (`23503`-reject is the banned throw-on-
  unmatched — `no_limiting_code_mvp`, gold council Mason). Soft join at bake/render.
- New importer (sibling to `import_layer_to_core_features.py`, which is geometry-bearing →
  `core.features`; `core.events` is the geometry-less junction so it needs its own thin
  loader): upsert the 13 sessions `ON CONFLICT (source_key)`, **assert count==input**, never
  drop/skip/throw (gold Mason's standing condition — confirm against a live apply).
- Extend the **one bake** (`export_publish_geojson.sh`) with a **new schedule emit arm in
  the same one-writer script, sibling to the `REFERENCE_LAYERS` loop** (`:55`/`:73`) — NOT a
  new `REFERENCE_LAYERS` entry: the schedule is a `{schema, event, locations{}, sessions[]}`
  document, not a GeoJSON FeatureCollection, so the loop body can't emit it (Quartermaster).
  Emit `website/data/aop_event_schedule.json` (same filename, same `aop-event-schedule-v1`
  schema the viewer reads at `main.js:8181`) from `core.events`, resolving `place_key`
  against `core.features`. One writer, one bake script — not a parallel pipeline. **Same
  filename → no `main.js` change → no shell bump owed** (gold pattern).
- **Acceptance (tile-independent):**
  - (a) **Browserless**: baked `aop_event_schedule.json` is field-equivalent to committed
    HEAD's hand-curated file (13 sessions, location tags, labels, sort order, schema) — the
    gold "prop-equivalent to HEAD" check.
  - (b) **Observable, no tiles**: viewer loads, `getSource('event-schedule').serialize()
    .data.features` carries the 13 session features and the `#pavilion` session row resolves
    to the `editorPois:aop-pavilion` point. Add this as a **NEW tile-independent assertion**
    inside the existing `mvp/scripts/playwright_verify_event_schedule.py` (do **not** add a
    parallel verifier; Quartermaster) — but do **not** inherit that file's render-dependent
    pattern: it currently uses `queryRenderedFeatures` (`rendered_count`) and
    `wait_until="load"` (Witness). The proven tile-independent technique to copy is
    `getSource(...).serialize()` as used in `mvp/scripts/playwright_verify_baked_reference_author.py`
    (no `networkidle`, no render read). **Re-witness the REAL verifier output** before
    trusting green.
  - (c) `publish.features` carries no `event` rows (the anchors are reference/non-publish —
    gate holds).
- **Restore** served files byte-identical to HEAD after proving (production untouched);
  report what's owed. Record on green.

### Slice 2 — `core.activities` + `activity_key` on `core.events`
The reusable WHAT. The schedule JSON already duplicates activity content inline
(`fri-night-crawl` / `sat-night-crawl` are two copies of "Night Crawl" — Quartermaster
corroboration); this de-duplicates exactly that.
- DDL: `core.activities` — `id`, `activity_key text UNIQUE` (e.g. `hill_climb`), `name`,
  `kind`, `description`, `attrs jsonb` (grade, length, gate list, class rules), provenance,
  `archived_at`. **No geometry, no place column** (place binds on the occurrence — user's
  resolution). Same CMFS shape minus geometry — one vocabulary.
- Add `core.events.activity_key text` (soft-ref `core.activities.activity_key`; same no-FK
  posture). Backfill activity rows from the sessions' distinct activities; point each
  occurrence at its activity.
- Extend the bake so the session feature carries the activity's detail (resolved, not
  copied per row).
- **Acceptance (tile-independent):** browserless — one `core.activities` row drives N
  occurrences (edit the activity once → every citing session's baked detail changes);
  `count==input` on the import; the schedule still bakes field-equivalent for the
  session-level fields. Observable viewer check that the activity detail surfaces on the
  session. Record on green.

### Slice 3 — place-attached abouts (NOT a migration slice; folds into normal editing)
Per the design: rock warblers / to-town / about AOP are **feature bodies**, not a new
table — richer `description` + `attrs.detail` on the existing `aop_visitor_context_callouts`
features (`rock_warblers`, `aop_badge`, the two `visitor_callout` points). A place-less
"About AOP" gets a **representative anchor point** (park centroid / G-Central), `kind='about'`
— **never `geom NULL`** (the one list engine is geometry-required at every node;
`main.js:6287`/`:1261` — gold/Quartermaster). This is content authoring through the existing
editor→`core` path, not a schema slice; listed for completeness, do not build it as DDL.

## Loop contract (if the user runs this as a ralph loop)
- Do the **next incomplete slice** (start at Slice 1), verify by its **tile-independent
  acceptance**, **Record on green**, then **stop**. One slice per iteration; fresh executor.
- **Do NOT commit**, and do **not** bump `sw.js` / `#appVersion` — report what's owed. The
  bake reuses existing served filenames, so no shell asset should change; if one does, the
  bump is **owed to the user**, never performed (`no_commits.md`).
- Restore served files byte-identical to HEAD after each proof (production stays untouched
  until the user's git gate).
- Inherited gold conditions: **Witness** — re-witness the FIRST slice's REAL verifier output
  before trusting "green" (the schedule verifier exists but the bake-from-`core.events` path
  and the anchor migration are new). **Mason** — confirm the `count==input` acceptance runs
  against a live apply before Slice 1 closes; no CHECK/enum/FK introduced.

## Run commands
- DB up: `docker compose -f mvp/docker-compose.yml up -d db` (db `aop_map`, `:55432`).
- Bake: `mvp/scripts/export_publish_geojson.sh` (extended with the schedule arm).
- Verify: `python3 mvp/scripts/playwright_verify_event_schedule.py` against a clean serve on
  `:8001` (`cd website && python3 -m http.server 8001`); 0 console errors required.

## Sequencing note
Slices 1–2 are sequential (both stand up tables, slice 2 references slice 1's `core.events`).
Slice 3 is not a migration slice. No collision with any active loop — the gold loop is done.
