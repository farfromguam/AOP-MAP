# Council receipt — "description in editor ≠ values in view" (DB→view flow)

Date: 20260608
Tier: design consult (Witness · Quartermaster · Mason, Steward-chaired). No diff —
the user asked the council to EXPLAIN the description→view flow and recommend the encoding.
Live DB up; all claims re-verified by observation.

## The question

User: "explain how the description goes from the db to the view. what I see in
description does not match the values in the view. how should this be saved/encoded?
what changes need to be made?"

## What is true (observed, all CONFIRMED by the Witness)

The descriptive text for a feature lives under TWO physical names for ONE concept:
- `blurb` — DB column `core.features.blurb` (init_db.sql:60); the bake emits it
  (export_publish_geojson.sh:36); the viewer renders `props.blurb` (main.js:1232,
  popup/list subtitle :1374/:1435); the sidecar `aop_poi_index.json` `entries[].blurb`.
- `description` — the editor field (panel.js:1349, reads/writes `props.description`;
  EDITABLE_SERVED_KEYS :84); the CMFS LOGICAL canonical (`_schema.json` canonical_fields,
  crosswalk folds blurb/notes/note→description); reference layers store it in
  `attrs->>'description'`; the (stale) served publish.geojson still carries a `description`
  key from an older writer.
- The apply-to-core sink BRIDGES them: `POI_COL={"description":"blurb"}`
  (apply_panel_overrides_to_core.py:71) — editor `description` → DB `blurb` column.

So on a full DB round-trip the text reconciles; in the LIVE browser and across the
two served files it does not.

## Why the user sees a mismatch (the sharpened diagnosis — Witness andon, resolved)

For "AOP Pavilion" there are TWO map features at the identical coordinate
[-85.7482512, 35.0907264], same logical key `editorPois:aop-pavilion`:
- EDITABLE feature ← static `aop_editor_seed_pois.geojson` (layer `editorPois`),
  text under `description` = "Main pavilion at 1010 Ellis Cove Road. G-Central…"
- RENDERED feature ← `publish.geojson` (layer `published_destinations`, baked READ-ONLY,
  main.js:1220/:1246), text under `blurb` = "AOP Pavilion / G-Central. Registration,
  driver meeting, awards…"

Three compounding causes, all observed:
1. NAMING split — editor reads/writes `description`; viewer renders `blurb`.
2. TWO homes for one POI on the client — the editor edits the frozen SEED FILE; the
   viewer renders the DB-baked publish file. Same place, two features, two files.
3. CONTENT drift — the seed file's `description` text differs from the DB's `blurb`
   text. Going gold made the DB the store of record, but the editor still loads the
   static seed, not the DB-baked POI (the gold slice-6 seed→DB convergence is HELD).
Plus: live in-browser edits land in a localStorage override store the popup never reads
(panel.js:147 OVERRIDES vs main.js:1224 publishDataCache) — an edit only shows after
Export→apply-to-core→bake→reload (the gold day-of loop, by design).

## Verdict

Steward REJECTS the opening "rename the `core.features.blurb` column to `description`"
proposal. Both Quartermaster and Mason pulled andon on it:
- Mason: a column rename is a flag-day with wide blast radius (init_db.sql, the
  publish.features VIEW must be dropped/recreated, migrate_layers_to_core_features.sql,
  seed_core_pois.sql, import_layer_to_core_features.py, promote_gpx_to_trail.sql,
  apply_…_to_core.py) — a miss hard-errors the bake — and it does NOT converge the
  reference layers (they store the concept in `attrs->>'description'`, untouched by a
  column rename). The codebase already has the right idiom: `BLURB_KEYS=("description",
  "blurb")` (import_layer_to_core_features.py:56) + the CMFS crosswalk.
- Quartermaster: `description` is the right canonical name (least churn — editor + CMFS
  already use it), but `description` ALSO already exists as a physical column on the
  sibling `core.activities` table (distinct meaning) — document, don't conflate. The
  `aop_poi_index.json` sidecar is NOT a clean delete: it also carries `revisit_note`
  (no column/canonical home) and POI-tab `groups[]` ordering+labels (poiGroupOrder/
  poiGroupLabel main.js:1313-1320). Fold `blurb`→`description`, but rehome those FIRST.

## Accepted shape (CLEARED)

Converge the READ/OUTPUT name on the CMFS canonical `description`, ADDITIVELY
(read-both, write-canonical) — keep `blurb` as the physical DB spine column.

Minimal now (round-trip reconcile, no DB migration, no view rebuild, nothing dropped):
1. export_publish_geojson.sh:36 — emit `blurb AS description` (canonical) alongside
   `blurb` (transition alias).
2. main.js:1232 — `blurb: props.description ?? props.blurb ?? null` (read-both).
   Editor unchanged (already `description`); apply-to-core crosswalk KEPT (it is the
   crosswalk, not a violation).
3. Touches main.js (a shell asset) → owes a `sw.js`/`#appVersion` bump. Commit is the
   user's git gate.

Follow-up cards (NOT this minimal fix):
- Collapse the static `aop_editor_seed_pois.geojson` into the DB-baked POIs so the
  editor edits the live feature, not a frozen seed (the gold slice-6 seed→DB
  convergence). This is what makes content drift impossible.
- Fold sidecar `entries[].blurb`→`core.features.description`; rehome `revisit_note` +
  `groups[]` first; then retire the sidecar (bump sw.js — it's precached, sw.js:70).
- Reference layers: populate the spine `blurb`/`description` column at import for
  uniformity (card note, not a gate — C5, attrs.description displaying today is fine).
- Drop the bake's `blurb` transition alias one cycle after the viewer fallback is
  confirmed dead.

Seats resumable: Witness a23aae1dad31eb954 · Quartermaster a033501b8028de989 ·
Mason aa8afe0445ee1524d.
