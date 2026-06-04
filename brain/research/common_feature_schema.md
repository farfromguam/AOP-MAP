# Common Minimum Feature Schema (CMFS)

TL;DR:
- The right panel already has ONE renderer. What it did **not** have is one
  data contract underneath it — every source named the same concepts with
  different property keys, so the editor could not offer one consistent field set.
- The fix is a **Common Minimum Feature Schema**: a tiny set of fields every
  feature carries (`id` · `name` · `description` · `kind`, plus the
  source-register provenance block), populated by a per-source **crosswalk**.
- The schema is not invented here — it is the northstar's six product-test
  questions turned into fields.

> **DECISION (2026-06-04, user):** *"no preference on the vocabulary, go with
> what is common. I would not have a half rebuild. I want to re-bake the data
> entirely in our new format. keep the raw we can refer back if needed. but our
> re-bake should have our fields."* → Vocabulary set to the names that already
> dominate the data and GeoJSON convention (`name`/`description`/`kind`, the
> publish-view's own vocabulary). Implementation is a **full data re-bake**, not
> a render-time adapter: every served feature is rewritten to carry the canonical
> fields; the pristine originals are archived to `website/data/raw/`. See
> "Implementation — the re-bake" below.

#aop #schema #data #editor #provenance #right_panel

-----

## The problem, stated by the user

> *"The variability of the data and its sources … each one has a different
> schema to it. We need a common minimum dataset. I should be able to edit a
> trail description the same way I edit the pavilion text, because the schema is
> similar and the editor is consistent."* — 2026-06-04

The editor (`website/js/panel.js`) is already the *"singular massive JSON object
+ singular renderer"* the rebuild promised — `PANEL_MODEL` → `renderPanel`. So
the inconsistency the user feels is **not** in the renderer. It is in the data:
the same human concept ("the name", "the description", "what kind of thing this
is", "where it came from") lives under a *different property key in almost every
source file*. The renderer can only be as consistent as the contract beneath it,
and right now there is no contract.

## Evidence — the variability is real (observed 2026-06-04)

Property keys read directly from every file in `website/data/`. The "name" and
"description" concepts alone scatter across ~10 different keys:

| Source file | "name" lives in | "description" lives in |
| --- | --- | --- |
| `publish.geojson` (trails/boundary) | `name` | `blurb` |
| `aop_trail_network.geojson` | `name` (often empty), `trail_number` | — none — |
| `sfwda_traced_trails` / `_markers` / `numbered` | `trail_number` only | — none — |
| `aop_buildings.geojson` (the pavilion) | `building_label`, `name`, `facility_name` | — none — |
| `aop_cemeteries.geojson` | `name` | `note` |
| `aop_editor_seed_pois` / drawn POIs | `name` | `notes` |
| `aop_visitor_context_callouts` | `name`, `label` | `services` + `examples` + `source_summary` (3 keys) |
| `aop_brand_logos` | `name`, `logo_id` | — none — |
| `aop_roads` / `aop_water` / OSM | `name` | — none — |
| `aop_lidar_tiles` | `title`, `tile_code` | — none — |
| `aop_activity_hotspots` / synthetic | `label` / `track_name` | — none — |
| `aop_contours`, `aop_landcover` | — NONE — (`ID`/`elev_ft`; `class`) | — none — |

The user's own example is the cleanest illustration: a **trail's** display name
is `name` (or, in the SFWDA sources, nonexistent — only `trail_number`), while
the **pavilion's** is `building_label`. Same concept, different key. The editor
cannot offer one "edit the title" field because there is no one title field.

The proof that this is the real friction is already in the code: `panel.js`
carries a hand-written **`PROVENANCE_KEYS`** alias list (14 entries —
`source`/`source_name`/`footprint_source` all → "Source", etc.) whose *entire
job* is to make the read-only provenance block look uniform across sources.
Someone already solved this problem once, for the read-only half, by hand. The
editable half (`title`/`description`/`kind`) has the same problem and has **not**
been solved — instead `itemFields()` falls back to geometry-derived fields for
user-drawn features and a bare `note` + read-only static for everything else.
That fork (user feature vs. reference feature) is the schema gap showing through.

## The schema is the northstar's product tests

`northstar/map_northstar.md` says a usable map must let a reader answer six
questions. Those questions *are* the schema — turn each into a field:

| Product-test question | Logical field |
| --- | --- |
| What is this line? | `kind` + `title` |
| Where did it come from? | `source` |
| Official, observed, inferred, or guessed? | `confidence` |
| Can we publish it? | `permission` + `publish_status` |
| When was it last checked? | `last_checked` |
| What would close the uncertainty? | `review_status` (+ `description`) |

`northstar/source_register.md` already mandates the provenance half
(`source_type`, `license_or_permission`, `publish_status`, `confidence`, …). The
CMFS just adds the **identity** half (`title`, `description`, `kind`) that the
editor needs, and unifies the naming so one renderer can read both.

## Proposed Common Minimum Feature Schema

Three tiers. "Minimum" means: **only Tier 1 is required of every feature**; Tier
2 travels with anything aiming for publish; Tier 3 is machine-managed.

**Tier 1 — Identity (human-authored, always editable):**
- `id` — stable feature id (machine; never blank).
- `title` — the display name. *This is the field the user wants consistent.*
- `description` — the human blurb/notes.
- `kind` — what class of thing this is (trail · building · cemetery · poi ·
  callout · water · road · contour · hotspot · logo · boundary · …). Drives
  which optional facets appear and how it renders.

**Tier 2 — Provenance (the source-register contract; read-only until promotion):**
- `source` — where it came from.
- `confidence` — official / observed / inferred / guessed.
- `permission` — license or permission to publish.
- `status` — publish/review status.
- `last_checked` — date/method last verified.

**Tier 3 — Optional facets (only where the `kind` needs them):**
- `difficulty` (trails), `category` (POIs), `occupancy` (buildings), etc.
- These are the legitimately type-specific fields. The CMFS does not flatten
  them away — it just keeps Tier 1+2 common so the *frame* is identical and the
  facets slot in underneath.

## The crosswalk (logical field ← physical keys, per the audit)

This is the adapter table. It is the whole mechanism — declare it once, and
every source reads/writes through the same logical names.

| Logical | Physical keys seen in the data |
| --- | --- |
| `id` | `id` · `uuid` · `build_id` · `parcel_id` · `osm_id` · `permanent_identifier` · `ID` · `edge_id` · `logo_id` |
| `title` | `name` · `building_label` · `facility_name` · `label` · `title` · `track_name` · `trail_number`→"Trail N" · `tile_code` · `cell_code` · (fallback: by `kind`) |
| `description` | `blurb` · `notes` · `note` · `description` · (visitor: compose `services`+`examples`+`source_summary`) |
| `kind` | `kind` · `layer` · `category` · `water_kind` · `road_class` · `cemetery_type` · `marker_type` · `feature_kind` · (fallback: source layer id) |
| `source` | `source` · `source_name` · `footprint_source` · `source_type` · `parcel_source` · `burial_source` · `nhd_layer_name` |
| `confidence` | `confidence` · `number_confidence` |
| `permission` | `license_or_permission` · `permission` · `burial_terms` · `license` |
| `status` | `status` · `publish_status` · `review_status` |
| `last_checked` | `retrieved_on` · `production_date` · `image_date` · `publication_date` · `validation_method` · `generated_on` |

`PROVENANCE_KEYS` in `panel.js` is already the bottom five rows of this table —
the CMFS generalizes that one good idea to the whole feature, including the
editable identity fields.

## What it buys the editor

With the crosswalk in place, `itemFields()` stops branching on geometry / user
vs. reference. **Every** feature gets the same logical editor:

```
[ Title          ]  ← text, writes back through the crosswalk
[ Description     ]  ← note/textarea
  Kind: trail        ← read-only or select
[ Difficulty ▾  ]    ← facet, only if kind needs it
  — Source ─────     ← provenance block (read-only until promotion)
  Source / Confidence / Permission / Status / Last checked
[ Fly · Copy · Move · Delete ]   ← gated by lock
```

That is precisely *"edit a trail description the same way I edit the pavilion
text."* A trail and the pavilion differ only in their Tier-3 facets and in which
physical keys the crosswalk reads — the *frame the user touches* is identical.

## Recommended rollout (non-destructive first)

1. **Adapter in `panel.js` (cheap, reversible, recommended first).** Add a
   `FIELD_MAP` (the crosswalk above) and `readField(props, logical)` /
   `writeField(props, logical, val)` helpers. Refactor `itemFields()` to emit the
   one common field set, reading/writing through the crosswalk. **No data file
   changes, no importer changes.** Fits `ai_rules/no_limiting_code_mvp.md`: it
   *adds* a reading lens, it never rejects or drops a feature whose keys don't
   match — unmapped keys just fall through to the existing static read-out.
2. **Normalize at the source, opportunistically (later).** As each importer in
   `mvp/scripts/import_*.py` is next touched, have it *also* emit the canonical
   keys (keep the originals — additive, not a rename, so nothing is dropped). The
   crosswalk then has less work to do, but never stops working.
3. **Lift into the source register when settled.** Once the vocabulary holds,
   record the Tier-1 identity fields alongside the Tier-2 provenance fields in
   `northstar/source_register.md` so the contract is locked, not just adapted.

Phase 1 alone delivers the user's ask; 2 and 3 are hardening, not prerequisites.

## The one genuine fork for the user

The **canonical vocabulary** is a naming/taxonomy call, and per
`ai_rules/...work_within_users_pattern` that is the user's axis to set, not mine
to impose. My proposed defaults — `title` / `description` / `kind` — are a
suggestion. The real decision is only: do we say `title` or keep `name`?
`description` or `blurb`? and what is the controlled `kind` list? The mechanism
(crosswalk adapter) is unaffected by the answer; only the labels change.

Recommendation: adopt `title` / `description` / `kind` as the logical names
(they read as plain English in the editor and don't collide with the many
existing physical `name` keys), build the Phase-1 adapter, and adjust the words
if they aren't the user's axis.

## Implementation — the re-bake (SHIPPED 2026-06-04, UNCOMMITTED)

Built and verified in one pass after the user chose a full re-bake over an adapter.

**Phase 1 — data re-bake (`mvp/scripts/rebake_canonical.py`).** Reads every served
feature collection, archives the pristine original to `website/data/raw/` once,
and rewrites each feature with the canonical block leading its properties,
populated via the crosswalk + per-layer source-register provenance defaults.
- **Additive** — original physical keys are preserved after the canonical block,
  so the map's paint/filter/label expressions (which read `class`, `idx`,
  `elev_ft`, `water_kind`, `road_class`, `geom_role`, `occupancy_class`, `color`,
  `difficulty`, …) are untouched and the live `index.html` keeps working.
- **`name` is render-sensitive** on trail-network / roads / water (label layers
  read it), so blank names are left blank there — auto-filling would spawn labels
  on unnamed features. Synthetic name fallbacks are applied only where nothing
  paints from `name` (9-patch cells, SFWDA trails).
- **Machine/coverage layers** (landcover, contours, activity, synthetic) get
  `id` + `kind` per feature only; their provenance is recorded once at the layer
  level in `website/data/_schema.json` — no point stamping 9 strings onto 2,831
  contour lines you never edit. Files did not balloon (contours 14.3→13.2 MB).
- Idempotent: always re-bakes from `data/raw/`, so re-running is safe. Run with
  `--check` for a no-write dry run. `_schema.json` is the manifest (canonical
  field defs + crosswalk + per-machine-layer provenance).

**Phase 2 — editor reads canonical (`website/js/panel.js`).** `itemFields()` no
longer forks user-vs-reference or branches on geometry: every feature gets the
one frame — `Name · Description · Kind · (Details/Difficulty facet) · provenance
· actions`. `PROVENANCE_KEYS` collapsed from a 14-entry hand alias list to the
five canonical fields. Dead `userFeatureFields` / `renderNoteField` removed.

**Verified by observation** (served :8077, headless, 0 console errors):
- Map still renders every default-on layer post-re-bake (buildings 3, streams 87,
  roads 84, landcover 123 + 2169, boundary 1, trails 2, visitor 6, both brand
  logos, trail-network 120). Shot: `brain/output/playwright_rebake_verify.png`.
- A building and a trail now show the **same** editor frame, both with live
  Name + Description inputs; differences are only the facet tier (trail =
  Difficulty, building = Last checked). Throwaway verifier:
  `/tmp/verify_canonical_editor.py`.

**Owed / decisions for the user (git gate):**
- `website/data/raw/` (~20 MB, pristine originals) is untracked. The same
  originals are also recoverable from git history (pre-re-bake HEAD), so the dir
  can be committed for convenience or `.gitignore`d — user's call.
- A **clean strip-legacy-keys** pass (drop the preserved original keys, leaving
  only canonical + render facets) is deferred to the index→panel swap, when
  `index.html` no longer reads the old keys.
- In-editor edits to Name/Description are in-memory (persistence is the rebuild's
  separate owed item).

## Pointers

- Renderer + current field logic: `website/js/panel.js`
  (`itemFields`, `PROVENANCE_KEYS`, `provenanceFields`, `renderField`).
- Active card: `tasks/04_event_app/right_panel_rebuild.md`.
- Provenance contract this extends: `northstar/source_register.md`.
- Product tests this implements: `northstar/map_northstar.md`.
- Layer/data catalog: `research/viewer.md`.
- Audit screenshot: `brain/output/playwright_schema_audit_panel.png`.
</content>
</invoke>
