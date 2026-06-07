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
