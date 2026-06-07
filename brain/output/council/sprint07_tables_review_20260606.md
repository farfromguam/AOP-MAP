# Council review — Sprint 07 tables model (DESIGN), 2026-06-06

**Artifact reviewed:** `brain/tasks/07_tables/tables_model.md` (my read of the user's
`brain/tasks/07_tables/breif.md`). Brain-only, design/direction — no code. Same review
shape as the gold-migration plan review.

**Tier:** full six (sprint-spine architectural design — the next layer of the gold
migration). Chaired as Steward; five worker seats spawned fresh + adversarial,
prompted to refute.

**Result: FULL CLEAR (2 rounds).** No seat refuted the core model
(Where×When×What → one new `core.events` table soft-referencing `core.features`;
"abouts" are feature data, not a new store; sequence after gold; activity-catalog
fork held). All three andons were precision/grounding defects in *how the card stated
it*, each fixed and re-cleared.

## Round 1

| Seat | Verdict | Finding |
|------|---------|---------|
| Warden | clear | (nit) "one new table, not three" header vs "two tables, one new" body wording |
| Witness | **andon** | Card said `#pavilion` resolves to the 1010 building. It resolves to the seeded POI `aop_seed_pavilion` (rebound 2026-05-26 — `main.js:37-41`, `:7361`); the schedule JSON's prose `source` field is itself stale (`aop_event_schedule.json:19`). |
| Quartermaster | **andon** | (a) "list panel renders features independent of geometry" is false — the one list engine drops geom-less rows (`main.js:6287`, `:1264`), rows need a fly coord, bake emits `geometry:null`. (b) `core.events` under-credited — a schedule resolver engine already exists (`eventScheduleToGeojson`/`resolveEventLocation`, `main.js:6280-6357`); frame as *extending* it. |
| Mason | **andon** | "FK"/"foreign key" used without pinning it must NOT be an enforced Postgres `FOREIGN KEY` constraint (would reject unmatched rows — `23503`, the C5/R13 ban the gold contract carries, `gold_migration.md:38-44`,`:177-189`). |
| Scribe | clear | (nits) untracked file = user's git gate; town callouts are `kind=visitor_callout` not `brand_logo`. |

## Fixes applied to the card

- **Witness:** corrected `#pavilion` → seeded POI `aop_seed_pavilion` (migrated off
  the 1010 building 2026-05-26); flagged the schedule JSON's stale `source` prose.
- **Quartermaster (a):** dropped the false geom-independence premise; place-less
  "abouts" now ride the proven geometry-bearing row path via a **representative anchor
  point**, not `geom NULL`. Named the three drop sites as the reason.
- **Quartermaster (b):** reframed `core.events` as **extending** the existing
  `eventScheduleToGeojson`/`resolveEventLocation` resolver — the JSON becomes its bake
  output — not "wiring a hole from scratch."
- **Mason:** added a no-limiting-code note — `place_key`/`activity_key` are plain
  `text` **soft-reference** columns, NOT enforced FK constraints; an unmatched place is
  stored/resolved-later, never rejected. Tightened all implementation-spec "FK" → "reference."
- **Warden + Scribe nits:** clarified the one-new-table framing; corrected the callout
  `kind` labels.

## Round 2 (re-review by the three andon seats)

| Seat | Verdict |
|------|---------|
| Witness | **clear** — correction accurate against `main.js:37-41,7345,7361,7385`; resolver returns `aop_seed_pavilion`; stale JSON prose confirmed; no new unobserved claim. |
| Quartermaster | **clear** — false premise retracted, place-less abouts on the geometry-bearing row path; `core.events` framed as extending the resolver. C1=0, C2=1 collector, C6 clean (design-only baseline). |
| Mason | **clear** — note pins soft-reference / soft-join / NOT a Postgres FOREIGN KEY / stored-not-rejected, cites the gold ban + `23503`. Spec block unambiguous. |

**Steward clears the gate.** Every convened seat `clear`. Review touched only `brain/`
(no `website/`/`mvp/`), so the Tier-0 Stop hook does not self-fire and there is no
diff hash to write to `.claude/.council-cleared`. Nothing committed — the git gate is
the user's.

**The one fork that survives to the user** (not a defect — the genuine product
decision): does an activity (hill climb, RC rally) recur across *different* places, or
is each bound to one place? Bound-to-one-place → two tables, one new (recommended
start). Recurs-across-places → add a thin `core.activities` reference table. This is
the user's domain call; the card recommends starting bound-to-one-place.

-----

## Revision + re-review — 2026-06-06 (the user resolved the fork)

**User directive:** *"the events usually are at the same place sometimes they are
different. they are only tied to the place when the schedule says so for that occurance
and at the #location tagged."*

This resolves the fork toward **recurs-across-places**, with a sharpening: the place
binds on the **occurrence** (the schedule row), via the `#location` tag — never on the
activity. The card was revised to a **two-new-table** model:
- `core.activities` — the reusable, **place-agnostic** WHAT (CMFS shape minus geometry).
- `core.events` — the WHEN **junction**, one row per occurrence, soft-referencing both
  `activity_key` and `place_key` (the place per-occurrence). No default-place field.
- Place-attached "abouts" (rock warblers, to-town, about AOP) stay feature bodies.

**Re-review (Steward-chaired) of the delta** — the three seats whose lenses the change
touches; Witness's prior facts unchanged, Scribe's record/voice held by the chair:

| Seat | Verdict | Note |
|------|---------|------|
| Quartermaster | **clear** | `core.activities` is a reuse-safe sibling of `core.features` (CMFS minus geometry, one vocabulary); no second registry/list-builder/bake; resolving a 2nd ref in `eventScheduleToGeojson` is an extension. **Corroboration:** the schedule JSON already duplicates activity content inline (`fri-night-crawl` / `sat-night-crawl` are two copies of "Night Crawl") — `core.activities` de-duplicates exactly that. C1/C2/C6 at target. |
| Mason | **clear** | No-FK line held for *both* keys; two tables earned (can't store moving data on a fixed place); rejects a default-place field + a third content store; `activity_key UNIQUE` matches the cleared `source_key UNIQUE` precedent; no enum/CHECK on value columns. |
| Warden | **clear** | The promotion of `core.activities` from deferred to in-scope is the user's directive, not invented scope; the activities/abouts split matches the brief's own two clusters; stays design-only, off the git gate; event-CRUD §2–4 stay deferred. |

**Steward clears the revised model.** Two new tables, council-clean. Still design-only;
depends on gold `core.features` (slices 2–5). Nothing committed.
