# Star-driven POI list — one authoring pipeline, not file reconciliation

> **Deferred — Sprint 04 triage (2026-05-30).** The bake-first SERVE slice
> shipped and was split to `../_done/04_edit/_done/bake_first_poi_serve_slice.md`.
> What remains here is **deferred because** it needs a user decision: the AUTHOR
> half (who writes the POI rows — web editor vs QGIS vs both) and the open
> pipeline forks (localStorage's role, bake artifact shape, dev-time-only vs
> prod write path) are unresolved. No code until those are picked.

> **⚠ COUNCIL READINESS VERDICT — 2026-06-08 (full six, Steward-chaired).** Read
> this first; the body below predates the gold migration + Sprint 05/07 and is
> stale in places (it still names dropped `core.pois`/`publish.pois`, pre-rename
> `blurb`, and old `index.html:NNNN` line numbers — the JS moved to
> `website/js/main.js`). What the council resolved by observation:
>
> - **Most forks are CLOSED, not open.** Authoring surface (for POIs/editorPois:
>   `apply_panel_overrides_to_core.py` → `core.features` → bake), bake artifact
>   shape (one `publish.geojson`), dev-time-only write, the **structural**
>   two-engines→one-collector convergence (shipped as
>   `../_done/05_special_operation/_done/06_one_star_driven_collector.md`), and the
>   store of record (`core.features`; `core.pois`/`publish.pois` dropped) ALL
>   shipped. The "Open forks — the real ones now" section near the bottom is no
>   longer a fork list — see the annotation there.
> - **STILL genuinely open:** (1) durable curation for the four **reference**
>   layers (cemeteries/buildings/visitor/trails) — no author→DB ★ path exists for
>   them (gold **slice 6, HELD**); (2) the user-visible flip itself (decisions
>   #1/#2).
> - **The executable slice (council-corrected):** (a) **add `highlightable: true`
>   to cemeteries + buildings** — Mason andon: they have no ★ control today, so
>   flipping them to starred without it is a banned **C5** row-dropping filter;
>   (b) flip `listMode: 'wholesale'`→`'starred'` on cemeteries, buildings,
>   visitorContext, trails (`main.js` ~2274/2345/2653/2860); (c) **published
>   POIs stay wholesale** — the bake is their curation gate, never retrofit
>   `'starred'` onto the baked `layer==='poi'` union; (d) render the left-tab
>   curation fields — mostly already present (the `info needed — revisit` chip is
>   live at `main.js:1396`); (e) tile-independent acceptance: clone
>   `playwright_verify_star_collector.py` — assert `pubpoi:1`/`pubpoi:2` still
>   render and the four wholesale groups are empty in a clean profile.
> - **Blocking caveat:** in the deployed read-only viewer (no localStorage author
>   session) the four reference groups would be **permanently empty** until gold
>   slice 6's author→DB ★ path lands — their ★ never reaches the bake. So the flip
>   delivers decision #2 (start empty/curated) but **not** #1/#5 *in production*
>   for those layers. editorPois + baked POIs already curate end-to-end.
> - **The user-decision fork is RESOLVED (2026-06-08):** the user picked **build the
>   ★ path first, then flip** (decisions #1 + #5 both met before any visible change).
>   See `../../output/council/star_driven_poi_list_consult_20260608.md`.
> - **The executable plan now lives in Sprint 08** —
>   `../_done/08_data_normalization/star_driven_poi_normalization.md`. This card stays the
>   design + council record; do NOT un-defer it whole (Quartermaster: its
>   engine/storage halves duplicate shipped work) and do NOT execute the flip
>   autonomously (user-visible end) — run it via the Sprint 08 loop contract.

Date: 2026-05-29

TL;DR:
- The left POI tab and the right ★ Visitor list are two lists built two
  different ways; they only coincide for drawn POIs. The ★ was bolted on per
  layer with no single rule.
- Locked principle: **★ is the one curation gate. The starred set _is_ the POI
  list.** Same data, two views — right rail = author's editable preview, left
  tab = reader's browse-and-read surface.
- **Do not design this against the current files.** The seed GeoJSON, the POI
  index, the localStorage stores, and the `highlight` overrides are *prototype
  scaffolding* — parallel mini-databases the static viewer grew because the
  real spine was never wired into the web loop. This card's job is to collapse
  them onto **one pipeline**, not to reconcile them.
- This is exploratory / direction-setting. **Nothing here is a locked
  implementation.** We are feeling out the pipeline shape.

#aop #04_event_app #poi #visitor_list #editor #curation #star #pipeline #postgis

-----

## Source

- User review (2026-05-29) of the right sidebar / Visitor list / left POI tab
  mapping. Then, after a first draft tried to pick between the seed and index
  files: *"feels like you are assuming that the way it is the way it should be.
  its not. dont be tied to any implementation, we are feeling this out. I want
  one pipeline. put shit in. move it around. save it to db. export from db to
  file. use baked file in remote envs."*

## The one pipeline (the target)

```
  put shit in / move it around      save to db           export to file        baked file
  ─────────────────────────────     ──────────           ──────────────        ──────────
  ONE editor: any geometry,         PostGIS = the         deterministic bake    static MapLibre
  any kind, drag/restyle/tag/   ──► single store of   ──► reads DB, applies ──► viewer in remote
  star/blurb. drawn or imported     record. one feature   the publish filter,   reads ONLY the
  are the same thing: a feature     = one row + its       writes GeoJSON/tiles   baked artifact.
  with a source.                    source stack.                               read-only.
       AUTHOR                          STORE                  BAKE                  SERVE
```

This is **not a new design** — it is the northstar's locked shape restated:
PostGIS is the living spine, the static website is a read-only view of
`publish`. It is also `source_register.md`'s `raw → core → publish` exactly:
author into raw/core, **the bake is the move to publish**, the remote viewer
only ever sees publish.

## Why the ★ question dissolves

There is no "where do the stars live." A star is not a thing that needs a home;
it is **one attribute on a feature row** — the feature's answer to *"is this a
published visitor destination?"* `source_register.md` already says every
feature carries `publish_status`, `confidence`, `permission`, and notes. The
"★ POI list" is just a view over that:

> `features WHERE publish_status = 'publish' AND is_destination`
> → baked into the artifact → left tab renders it, right editor edits it.

`aop_editor_seed_pois.geojson`, `aop_poi_index.json`, `aop_editor_pois_v1`,
`positioned_features`, `aop_*_overrides_v1`, and `highlight`-in-localStorage are
**all stand-ins for one DB column and one bake step.** In the one-pipeline
world they don't get reconciled — they collapse. "Drawn vs imported" stops
being a distinction: both are rows with a `source`, differing only in what
their source stack says. (The earlier draft of this card spent a whole section
choosing between the seed and the index — that entire fork was an artifact of
the scaffolding and is now void.)

## Locked product decisions (2026-05-29)

These survive the reframe; they're about behavior, not storage:

1. **★ governs all destination layers** — events, buildings, trails,
   cemeteries, visitor context, drawn POIs. The POI tab = exactly the starred
   set across these. No layer-specific exceptions.
2. **The POI tab starts empty.** Curated subset, not "everything we know." (A
   behavior change from `_done/left_panel_poi_browser.md`, which shipped ~20
   unconditional rows. Empty-state copy already exists — now at
   `website/js/main.js:1338` after the JS split, not the old `index.html:2114`.)
3. **Brand logos leave the ★ axis entirely** — cartographic decoration, never
   destinations. (They keep their own size/move drawer.)
4. **Right ★ Visitor list and left POI tab are two renderers over one set** —
   the starred/publishable destinations. Right rail keeps fly/unstar; left tab
   adds blurb, status, kind chip, `info needed — revisit` placeholder.
5. **Curation is data, not browser state.** The star and blurb belong in the
   store of record and travel into the baked artifact — so the published POI
   list is stable across browsers and auditable, per the northstar publish
   rule. (Originally phrased as "commit to seed data"; the one-pipeline reframe
   makes that "a column in the DB, baked into the export.")

## The honest gap (what does not exist yet)

The spine is promised and the box exists (`mvp/` has PostGIS, `docker-compose`,
`init_db.sql`), but **nothing connects the web editor to it.** Today the editor
writes localStorage; the seed/index files are hand-maintained; there is no
"save to DB" and no "bake from DB." The two missing pieces are the literal
middle of the pipeline:

1. **Author → DB.** The editor stops treating localStorage as truth and writes
   features to PostGIS (directly in dev, or via a thin local service).
2. **DB → baked file.** A deterministic export (SQL / ogr2ogr / `pg_dump`
   sibling) that reads `publish` and writes the artifact the static viewer
   loads. `dev_db_snapshot_reseed.md` covers the DB-dump half; the bake half is
   unwritten. The `cwc` root helper already does a "publish export check," so
   there's a seam to hang the bake on.

## Decisions locked (2026-05-29, session 2)

The push-order fork below is now answered. User picks:

1. **Push order: the bake first (b).** Prove SERVE (DB → publish view → baked
   file → viewer) before wiring the author path. The editor keeps writing
   localStorage until the author path lands.
2. **Bake artifact shape: one `publish.geojson`.** Single combined publishable
   FeatureCollection; the viewer splits by `layer` discriminator at load.
3. **Authoring surface: deferred, not locked.** User asked for pros/cons (see
   below) but did not pick. Bake-first makes this safe to defer — the bake reads
   a `publish` view agnostic to who wrote the rows, so the author choice settles
   *after* the bake is proven. **Do not assume the web editor is the writer.**

### Authoring surface — pros/cons (for the deferred pick)

- **Web editor writes DB:** matches `editor_is_the_viewer`; ★/blurb/"move it
  around" are native web gestures; localStorage stores map ~1:1 to DB writes.
  *But* needs a thin local write service (browser can't write PostGIS), the
  `source_register` stack is awkward in a light form, and it competes with
  QGIS's named cartography role.
- **QGIS authors, web read-only:** exactly the northstar shape; zero new
  write-path code; strongest `source_register` + validation-loop discipline;
  scales to real cartography. *But* breaks `editor_is_the_viewer` for curation
  (★/blurb become attribute-table edits), kills the "move it around" feel, and
  needs QGIS wired to `localhost:55432` (open MVP item 3) first.
- **Both feed one DB:** each tool to its strength, honors both rules. *But* most
  surface area (pays the web write-path cost AND QGIS upkeep), needs an
  ownership rule to avoid clobbering, and tends to collapse into "web now, QGIS
  later" = option 1 in disguise.

### Bake is already half-built (finding, 2026-05-29 session 2)

The bake mechanism exists and is northstar-shaped — bake-first is **not**
greenfield:

- `mvp/init_db.sql` already defines `raw`/`core`/`publish` schemas, the
  `source_register.sources` + `feature_sources` tables, and `publish.*` views
  filtering `permission='publish' AND publish_status='publish'`
  (trail_centerlines, park_boundaries, parcels, trailheads, hazards).
- `mvp/scripts/export_publish_geojson.sh` already bakes those views into **one
  `website/data/publish.geojson`** FeatureCollection with a `layer`
  discriminator — exactly the chosen artifact shape.

What's missing is specifically the ★/destination POI set:

1. Destination layers (buildings, cemeteries, visitor context, drawn POIs,
   event anchors) are **not in `core` tables** — they're in files/localStorage.
2. **No `publish` POI/destination view** (no `is_destination` + `publish_status`
   POI concept) and it's not in the export UNION.
3. The viewer **does not read `publish.geojson` for the POI list** — it reads
   per-layer files + localStorage.

### Bake-first slice — SHIPPED 2026-05-29 (session 2, user green-lit)

> **ANNOTATION 2026-06-08 (council):** This block names `core.pois` / `publish.pois`
> and `blurb` — both superseded since. The gold migration (2026-06-07,
> `../06_going_gold/gold_migration.md`) collapsed POIs into `core.features`
> (`layer='poi'`) and **dropped** `core.pois` + `publish.pois`; the column `blurb`
> was renamed to `description` (2026-06-08,
> `../_done/07_tables/_done/description_blurb_convergence.md`, committed `5b5fcdd`). Read the
> nouns here as: `core.features WHERE layer='poi'`, gate `publish.features`, copy
> field `description`. The SERVE behavior this block shipped is intact.

The SERVE half of the pipeline now runs end-to-end and is verified. What landed
(all in the working tree, uncommitted):

1. **`core.pois` table** (`mvp/init_db.sql`) — destination POIs as first-class
   rows: `name, kind, blurb, is_destination, status, confidence, permission,
   publish_status, source_id, geom(Point), notes`. `is_destination` is the ★
   axis; `blurb` is the visitor copy that used to live in `aop_poi_index.json`.
   Added GIST index + `updated_at` trigger registration.
2. **`publish.pois` view** = `is_destination AND permission='publish' AND
   publish_status='publish'`. (Card stated the gate as `publish_status='publish'
   AND is_destination`; `permission` added to match sibling views + the
   northstar publish rule. Comment in the SQL notes this.)
3. **`export_publish_geojson.sh`** UNION extended with `publish.pois` (added
   `kind`/`blurb` columns NULL across the other branches); bakes POIs into
   `website/data/publish.geojson` under `layer='poi'`.
4. **Seed** `mvp/scripts/seed_core_pois.sql` (idempotent, owns rows via a named
   source) — 3 rows derived one-time from existing files: **AOP Pavilion** and
   **Ellis Cemetery** (`publish`), plus **Proving Grounds (candidate)** left
   `permission='unknown' / publish_status='candidate'` so the gate must exclude
   it. Confirmed: `core.pois` has 3 rows, `publish.pois` exposes 2.
   (Visitor-support callouts were *not* seeded — their polygons are positioned
   label boxes, not real town geometry; seeding their centroids would be
   geographically false. Left for when real coords land.)
5. **Viewer wiring** (`website/index.html`): `buildPoiGroups()` gained a
   `published_destinations` group fed from `publishDataCache` `layer==='poi'`
   (rendered first; the legacy six-source blocks are untouched — that collapse
   is still deferred). New `publish-pois` map circle layer. New group
   label/order in `aop_poi_index.json`.

**Verifier:** `mvp/scripts/playwright_verify_baked_pois.py` — PASS on all
checks (2 baked POIs with blurbs, candidate excluded, map layer renders 2, POI
tab group renders both, no console errors). Regression: `feature_list` /
`presets` show only their documented pre-existing failures
(publishable-section / OSM-section-move / mobile-overlap); `trails` passes.

**What's still NOT done (deferred, not in this slice):**
- The **AUTHOR** half — nothing writes `core.pois` from the editor yet
  (authoring-surface fork still open, see above). Today the seed SQL is the only
  writer.
- **Collapsing the scaffolding** — the legacy buildings/trails/cemeteries/
  visitor/event/editorPois sources in `buildPoiGroups()` still render alongside
  the baked group. Migrating them onto `core.pois` is the next chunk.
- ~~`dev_db_snapshot_reseed.md` should fold `seed_core_pois.sql` into the reseed
  path so a fresh dev DB comes up with these rows.~~ **Done 2026-05-29** — seed
  mounted into `docker-entrypoint-initdb.d`; fresh-init verified (`core.pois`=3,
  `publish.pois`=2). See that card's "Wired 2026-05-29" block.

## Open forks — the real ones now (storage is settled; these are not)

> **ANNOTATION 2026-06-08 (council):** Three of these four are now CLOSED by the
> shipped gold migration — do not re-litigate them. **Authoring surface:** the web
> editor writes via `apply_panel_overrides_to_core.py` → `core.features` → bake
> (editor_is_the_viewer); QGIS stays a future cartography surface, not a blocker.
> **Bake artifact shape:** one `publish.geojson` (shipped). **Where "move it
> around" runs:** dev-time-only (northstar V1; no prod write). **Only one is still
> open: localStorage's role** — kept as a working buffer (C3), and for the four
> *reference* layers (cemeteries/buildings/visitor/trails) it is still the *only*
> ★ store because no author→DB path exists for them yet (gold **slice 6, HELD**).
> The text below is the original 2026-05-29 fork list, kept as the record.

Decide these before any code. They are genuine; do not assume.

- **Authoring surface.** Does the web editor write the DB (the
  `ai_rules/editor_is_the_viewer.md` rule pushes this way), is QGIS the author
  and the web editor stays read-only, or do both feed one DB? Decides whether
  we build an editor→DB write path at all.
- **localStorage's role.** Ripped out, or kept as a local *working buffer* that
  you explicitly "commit" to the DB (draw offline / experiment without dirtying
  the spine)? The buffer keeps the scratch feel but adds a sync step.
- **Bake artifact shape.** One `publish.geojson`, per-layer GeoJSONs (today's
  shape), or vector tiles / PMTiles? Drives how large the park can grow before
  the static viewer chokes.
- **Where "move it around" runs.** Strictly dev-time (author locally → bake →
  deploy; remote never writes — matches static V1), or eventually an
  authenticated write path in prod? The latter is the V2 submission/moderation
  the northstar explicitly defers — assume **dev-time-only** for now unless the
  user says otherwise.

User's steer at end of the 2026-05-29 session: the two anchors to push first
are **(a) authoring surface — who writes the DB** and **(b) the bake — DB →
file → remote.** Everything else hangs off those.

### Council consult 2026-06-06 — "too many schemas; does a DB / type system fix it?"

User asked whether forcing data into the DB solves the per-source schema
fragmentation (DB requires one schema), and whether a **type system** could be
enforced on top. The council (Steward chair; Quartermaster·Mason·Witness·Warden)
resolved it, and it de-risks the authoring fork above:

- **The fragmentation is real** (Witness verified: across the 23 served
  `website/data/*.geojson`, the only keys universal to *all* files are `id` + `kind`).
- **The DB helps narrowly:** it declares the **shared spine** once (the ~9
  provenance/curation fields now hand-retyped per file) instead of per-file. It does
  **not** — and must not — flatten the per-domain attributes (a trail's `difficulty`,
  a cemetery's `burial_count`); those are real shape, not slop. And prod reads the
  **files**, not the DB, so the **bake** is what unifies the served shape, not the DB.
- **A type system is possible — and half-exists already:** the **Common Minimum
  Feature Schema** (`website/data/_schema.json` `aop-cmfs-v1` +
  `research/common_feature_schema.md`) is the one-shape contract, observably holding
  on the 18 curated layers (the 6 `machine:true` layers are deliberately exempt).
- **Shape, not vocabulary (Mason / C5):** enforce that the canonical fields *exist*;
  **never** reject an unknown value (no CHECK/enum/`NOT NULL`-on-values/row-dropping —
  that silently drops the freshest field data, worse than an honest candidate line).
- **The move is a receipt, not a new contract (Quartermaster):** a read-only audit
  that proves conformance — carded at `../06_going_gold/schema_conformance_audit.md`.
- **Whichever authoring surface you pick** (the (a) fork) writes into the **same** CMFS
  shape, and the audit guards it — so the schema question does **not** block the
  authoring decision; it makes it safer.

## Execution plan — moved to Sprint 08 (chosen 2026-06-08)

> The user picked **"build the ★ path first, then flip"** (decisions #1 + #5 both met
> before any visible change) and asked for the plan in an active sprint. The executable
> 3-slice plan now lives at **`../_done/08_data_normalization/star_driven_poi_normalization.md`**
> (spine of Sprint 08 — "Data Normalization"), with the sprint framing in
> `../_done/08_data_normalization/_readme.md`. This card stays the **design + council record**;
> that card is the **how-to-run**. Sprint 08 executes the curation-axis slice of gold
> slice 6 (HELD, `../06_going_gold/gold_migration.md`).

## What this is NOT (out of scope / guardrails)

- Not a request to start coding. This is the pipeline-shape conversation.
- Not V2 submission/moderation or prod write paths (`event_crud_upload_loop.md`,
  northstar defers).
- Not new POI data sources — the model reads what the park already has.
- Do **not** re-open the seed-vs-index file question; it's void under the
  one-pipeline frame.

## Notes for CWC (next session pickup)

- This card replaced its own first draft. If you see references elsewhere to
  "stars live in `aop_poi_index.json`" or "seed vs index," that's the dead
  framing — ignore it.
- Status: **design / feeling-out only.** No `website/index.html` change, no
  card-driven code, no schema written. Working tree clean as of this card.
- Next decision owed (from the user): pick the push order between **authoring
  surface** and **the bake**. Bring options for each; don't assume the web
  editor must be the writer until that's confirmed.
- Grounding reads before acting: `northstar/map_northstar.md` (PostGIS spine,
  static read-only V1), `northstar/source_register.md` (raw/core/publish,
  publish rule), `northstar/validation_loop.md` (observations don't overwrite),
  `tasks/04_event_app/dev_db_snapshot_reseed.md` (the DB-dump half),
  `ai_rules/editor_is_the_viewer.md` (why the editor is the authoring surface).
- The current scaffolding to eventually collapse — enumerate before deleting:
  `aop_editor_pois_v1`, `aop_editor_seed_pois.geojson`, `aop_poi_index.json`,
  `POSITIONED_FEATURES_KEY` store, `aop_visitor_context_overrides_v1`,
  `aop_brand_logos_overrides_v1`, `VISITOR_LIST_LAYERS` (`index.html:1392`),
  `buildPoiGroups()` (`:1932`), `renderVisitorListGroup()` (`:1836`).

## Predecessors / related

- `editor_three_buckets_v3c.md` — current right-rail editor (★ Visitor list at
  top of the three-bucket tree).
- `_done/left_panel_poi_browser.md` — the left POI tab this rewires from "list
  everything" to "render the published/starred set."
- `_done/poi_editor_inline_list_and_highlight.md` — origin of the ★ axis.
- `editor_unified_positioned_features.md` — the unified override store (scaffolding).
- `dev_db_snapshot_reseed.md` — the DB dump/reseed half of the bake pipeline.
- `data_integrity_publishability.md` — the publish-gate blockers this rides on.
- `../../northstar/source_register.md` — the raw/core/publish contract that
  makes this pipeline the spine, not a new invention.
