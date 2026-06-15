# Star-driven POI normalization — the reference-layer ★ path, then the flip

> **Sprint 08 spine. FULL plan — COUNCIL-CLEARED (full six, 2026-06-08).**
> Receipt: `../../../output/council/sprint08_plan_review_20260608.md`.
> Plan committed by the user as `c781f59 "data normalization plan"` (the commit-pause gate).

> ## ✅ EXECUTION RECORD — all 3 slices GREEN by observation (2026-06-08, ralph loop)
> Ralph-looped in a fresh session after the commit-pause. CODE+DB, UNCOMMITTED;
> `v53`→`v54` bump + the commit are OWED (the user's git gate). Verified by observation,
> not re-derivation (the standing Witness/Mason conditions held).
>
> - **Slice A — reference-layer ★ door (DONE).** Added `highlightable: true` to the
>   cemeteries + buildings `FEATURE_LIST_LAYERS` specs (Mason precondition — lands WITH the
>   Slice C flip). New `mvp/scripts/apply_positioned_features_to_core.py`: reads the
>   positioned-features map (the `aop-viewer-preset-settings-v3` bundle's
>   `positioned_features`, or a bare slice), filters to the four reference editor-layerKeys,
>   resolves each to its core row by the Grounding-#4 per-layer DB lookup, and UPSERTs
>   `attrs.highlight` (single source of truth — `is_destination` NOT written). REUSED
>   `split_key` (panel_overrides) + `sql_str`/`run_psql`/`parse_count` (apply_panel_overrides);
>   did NOT reuse `read_payload`/`VIEW_STATE_KEYS`. **Observed:** a test bundle starring one
>   feature per layer landed the flag on the *correct* core row — cemetery **:marker** (not
>   :parcel), trail **sfwda-0** (resolved by `trail_number=15`, not the `sfwda-15` index),
>   visitor **by name** (not the `-N` index), building direct; siblings untouched; un-star wrote
>   explicit `false`; `trails:n:99999` reported UNRESOLVED (loud, never thrown); brandLogos /
>   editorPois / geometry-only entries skipped; **idempotent** (re-run: 4 starred, row counts
>   5/8/4/120 unchanged — no dup).
> - **Slice B — ★ travels into the bake (DONE, verify-only).** No bake change needed
>   (`export_publish_geojson.sh:87-93` emits `'properties', attrs` verbatim). **Observed:**
>   after apply→bake, each served reference file (`aop_buildings/cemeteries/
>   visitor_context_callouts/trail_network.geojson`) carried exactly one `"highlight":true` on
>   the starred feature (building 3396032, Bible **marker**, Monteagle, trail 15) and `false`
>   on the un-starred building. Served files **restored byte-identical to HEAD** afterward (via
>   read-only `git show HEAD:… > …`, since the bake-vs-HEAD drift is pre-existing and
>   `git checkout` is the user's gate); DB test stars reverted (0 remain).
> - **Slice C — flip + render (DONE).** Flipped `listMode: 'wholesale'`→`'starred'` on
>   cemeteries / buildings / visitorContext / trails; updated the stale "wholesale (unchanged)"
>   prose; strengthened the published-`poi`-union guard comment (bake is its gate, never
>   `'starred'`); refreshed the collector's master NOTE (the flip landed). New
>   `mvp/scripts/playwright_verify_starred_poi_flip.py` (clone of star_collector) — clean
>   profile, waits on the **load** event via `window.AOP_HOST_MAP` + all four reference sources
>   carrying data (the Witness condition), asserts per-group counts from the **actual baked
>   files**. **Observed (PASS, 0 console errors):** each reference POI group shows only its
>   curated ★ row (trail 15 not all 100; the facility not all 3; etc. — the flip GATES);
>   `pubpoi:139/140` still render (bake-gated, unaffected); a starred row renders with content.
>   Existing `playwright_verify_star_collector.py` still PASS (no regression).
>
> **OWED (the user's git gate):** the commit (main.js + `sw.js` + `index.html` + the 2 new scripts
> + brain records). The actual production ★ curation is the user's to author (this sprint ships the
> *path*, not the stars).
>
> **⚠️ VERSION-BUMP CORRECTION (2026-06-08, after the user caught a bug):** the card's "owes v53→v54"
> was STALE — HEAD already carried `sw.js`/`#appVersion` **v54** (the FAB-fix bump was committed). My
> flip touched main.js but rode the same v54, so the service worker never invalidated and installed
> browsers kept serving the cached pre-flip code (old wholesale trails — the symptom the user saw: an
> unstarred trail still in the POI list). The Playwright verifier runs SW-less in a fresh context, so
> it never hit that path. **Fixed: bumped v54→v55** (sw.js + index.html). Confirmed by observation the
> new code gates correctly — 0-star bake → all four reference groups EMPTY (no leak); with stars →
> each group shows only its curated row. **Deploy note:** the flip is live; with no production stars
> authored, a fresh visitor sees those groups empty (the plan's "author stars first" step is the
> user's to do). Council done-review CLEAR before this correction:
> `../../../output/council/sprint08_done_review_20260608.md`.

> ## ⚠️ LIVE AUTHOR→LINK COMPLETION (2026-06-08, after the user reported "stars not linked to the left")
> The flip made the four reference layers show ONLY ★ rows, but two of four had an **incomplete live
> author→link path** in the user's own browser (the clean-profile baked path the slice verifier covers
> was fine; the *live ★ in the editor* path was not). Diagnosed by observation:
> **buildings/visitorContext linked; cemeteries/trails did not.**
> - **Cemeteries:** the ★ toggle resolved to the deduped *parcel* twin (`findFeatureById`), but
>   `collectStarredDestinations` reads the *marker* twin (`listFromData`) — flag landed on the wrong row.
>   Fix: `persistFeatureFlagChange` re-runs `applyPositionedFeatures(layerKey, runtime.data)` after
>   persisting (the parcel+marker convergence a reload already got; reuses the replay, idempotent).
> - **Trails:** panel `aopTrails` node had no `hostKey` (★ fell to the panel-overrides store the host
>   never reads), and the host never called `applyPositionedFeatures('trails')` (no reload durability).
>   Fix: extracted `trailRowId` + trails-spec `idFor` (so the bridge resolves the panel's stamp-less
>   served props by trail_number/name) + `hostKey:'trails'` + the missing apply call.
>
> Verified by observation: all four LINK live + survive reload, 0 console errors; flip/collector/embed
> verifiers unregressed. New guard `mvp/scripts/playwright_verify_star_links_live.py`. Shipped alongside
> a **🔥 Torch cache** button (Session tools) for the cache half of the user's hypothesis. Touched
> `main.js`+`panel.js`+`index.html` → **v55→v56** bump. See handoff 2026-06-08 (top). Commit OWED.

> ## ⚠️ SLICE D — STAR-ONLY (2026-06-08, user override of Slice C's "keep published wholesale")
> After a council consult traced what the left POI list actually shows (receipt
> `../../../output/council/left_poi_list_source_consult_20260608.md`), the user asked why the list had
> content when nothing was starred — and directed: **"make the list star-only … where did you get the
> idea that this old static code not db powered is good to keep around? we are maintaining a bunch of
> spike code."** This **overrides** Slice C's decision to keep the published-`poi` union wholesale
> (`cards_not_gospel`): the user wants the POI tab to be *exactly* the ★-curated set, with the two
> non-star feeds removed.
>
> **Shipped (CODE+DATA, UNCOMMITTED, v56→v57 bump PERFORMED, commit OWED):**
> - **main.js** — removed the two wholesale unions from `collectStarredDestinations`: input 2
>   (published `poi` from `publish.geojson`, bake-gated) and input 3 (event anchors from
>   `aop_event_schedule.json`, a static non-DB file). The collector is now a single walk over the
>   registry's ★-gated specs. Removed the now-dead `publishDataCache` (declared + assigned, zero readers
>   after the union went); updated the collector header + the stale event-bindings comment. The event
>   **schedule itself is untouched** — it still powers the Events tab (`renderEventSchedule`/
>   `resolveEventLocation`); it is just no longer mirrored into the POI list.
> - **aop_poi_index.json** — dropped the now-unreferenced `published_destinations` + `event_anchors`
>   group defs, the 8 `event_schedule`/published blurb entries, and the matching `owed_work` line.
> - **sw.js + index.html** — **v56→v57** (a shell asset changed; cache must invalidate or installed
>   browsers keep the wholesale code — the exact bug class the v54→v55 correction above caught).
>
> **Verified by observation (clean profile, SW-less Playwright):**
> - Left POI list **10 rows → 1**: the published group (2) and event group (7) are GONE; the only row
>   is the one star-fed feature (the `aop_seed_pavilion` drawn POI, which ships `highlight:true`).
>   0 console errors. (`mvp/scripts/diagnose_left_poi_list.py`.)
> - Star-DRIVEN proven both directions: `playwright_verify_star_links_live.py` PASS — authoring a ★ on
>   each of the four reference layers surfaces its row live + survives reload.
> - `playwright_verify_starred_poi_flip.py` updated to the star-only contract (published + event groups
>   asserted ABSENT) → PASS; `playwright_verify_star_collector.py` updated (published group GONE) → PASS.
> - **Events tab NOT regressed (Witness-confirmed differentially).** The Witness served HEAD on :8002 and
>   ran `playwright_verify_event_schedule.py` against HEAD and the working tree: BYTE-IDENTICAL results
>   (116 PASS / 8 FAIL, identical fail+pass sets). All 8 FAILs are **pre-existing on HEAD** (`#pavillion`
>   data alias, headless-tile camera-fly geometry, expanded-panel glyph, the `#tag` accordion, 3
>   trail-lane defaults) — none caused by this diff (the schedule JSON is byte-identical to HEAD; the diff
>   only stopped the POI LIST from mirroring the schedule). The map's published layer + feature search are
>   also unregressed (live DOM reads).
> - `data_groups_embed` PASS; `node --check main.js` PASS.
>
> **Pre-existing, NOT touched (flagged):** two `publish`/`trail_centerlines` blurb entries
> (`Saturday Afternoon Activity segment 1/2`, group `trails`) remain in `aop_poi_index.json`; the trails
> list uses `trailCatalogLookup`, not `poiIndexLookup`, so they were already orphaned before this change
> — left alone to avoid scope creep.
>
> **OWED (the user's git gate):** the commit (`main.js` + `sw.js` + `index.html` +
> `aop_poi_index.json` + the updated verifiers + brain records), with the v57 bump.

Date: 2026-06-08

TL;DR:
- Normalize curation across **all** destination layers into the one `core.features`-backed
  pipeline, then flip the POI tab to the curated ★ set (star_driven decisions #1/#2/#5).
- The structural work already shipped (one collector, gold store, one bake). What's missing
  is the **durable ★ path** for the four reference layers (buildings/cemeteries/visitor/
  trails): today their ★ is ephemeral browser state, baked nowhere.
- User decision (2026-06-08): **build the ★ path first, then flip** — #1 + #5 both met
  before anything visible changes; nothing empty in production.

#aop #08_data_normalization #star #poi #core_features #bake #curation #postgis

-----

## Design source (the why — do not re-derive here)

- `../10_deferred/star_driven_poi_list.md` — the feeling-out doc, locked product decisions
  #1–#5, and the 2026-06-08 full-six council readiness verdict at its top.
- `../../../output/council/star_driven_poi_list_consult_20260608.md` — the consult receipt.
- Executes a **scoped piece of gold slice 6** (HELD, `../../06_going_gold/gold_migration.md`):
  the four reference layers' ★ moves from per-browser localStorage to a durable
  `core.features` attribute that bakes into the served artifact. Curation/star axis only.

## Grounding (observed 2026-06-08 — the facts the slices stand on)

1. **The ★ lives in `aop_positioned_features_v1`, not the panel-overrides store.**
   `toggleFeatureHighlight` (`main.js:3691`) → `persistFeatureFlagChange` (`:3774`) →
   default `savePositionedFeature` (`:2970`), which writes `{highlight}` keyed by
   `${layerKey}:${spec.idField}` into `POSITIONED_FEATURES_KEY`. (editorPois is the
   exception — its `persistFlag` is `saveEditorPois`.) So `apply_panel_overrides_to_core.py`
   (which reads the *panel-overrides* export) is the **wrong** sink for reference-layer ★.
2. **The viewer's full export carries it.** The `aop-viewer-preset-settings-v3` "Export all"
   bundle round-trips the whole positioned-features store, `highlight` included
   (`savePositionedFeature:2978`). The legacy file-baker `export_positioned_features.py`
   *chooses* to ignore `highlight` ("session state, not authored data") — a new core sink
   does not have to.
3. **The bake already carries `attrs` verbatim.** `export_publish_geojson.sh:77-95` emits
   `'properties', attrs` for each reference layer from `core.features`. So writing
   `attrs.highlight = true` on a core row makes the served file carry `highlight`, which the
   collector reads at `main.js:1176` (`props.highlight === true`). **No bake change needed.**
4. **The editor ★ key diverges from `core.features.source_key` for 3 of 4 layers** — this is
   the real work of Slice A (resolution by per-layer DB lookup, not string-munging):

   | editor key (`layerKey:idField`) | core `source_key` | resolve to |
   |---|---|---|
   | `buildings:<build_id>` | `buildings:<build_id>` | **direct** (build_id == the key) |
   | `cemeteries:<parcel_id>` | `cemeteries:<parcel_id>:parcel` **+** `:marker` | the **`:marker`** row (the row the list surfaces via `listPredicate geom_role==='marker'`) |
   | `visitorContext:<name>` | `visitor:aop_visitor_context_callouts-N` | core layer is `visitor` (not `visitorContext`); the `source_key` `-N` is a synthetic index, **not** the name — match on **`attrs->>'name'`** (fall back to `label`); exclude `kind=brand_logo` (decision #3) |
   | `trails:<__trail_row_id>` (`n:<num>`/`name:<name>`) | `trails:sfwda-<n>` | the `sfwda-<n>` suffix is a **sequential load index, unrelated to the trail number** (Witness: `sfwda-0`→trail 15, `sfwda-100`→trail 68). Resolve by joining editor `trail_number`/`name` → core **`attrs->>'trail_number'`** (unique, non-empty) / **`attrs->>'name'`**, NOT the source_key suffix. ~33 numberless + ~20 nameless edges carry no `__trail_row_id` and are intentionally unresolvable. |

5. **Clean-profile durability holds.** `applyPositionedFeatures` (`:2997-3019`) replays the
   local store over served props in the author's browser; in a clean profile (no store) the
   **served** value drives — which is exactly the durability the flip needs, and what the
   Slice C acceptance tests.

## Slice A — reference-layer ★ door (AUTHOR→STORE)

The meat. Make a starred reference feature's ★ land durably in `core.features`.

- **Add `highlightable: true`** to the cemeteries + buildings specs. **The destination
  specs in `FEATURE_LIST_LAYERS` (cemeteries `main.js:~2266`, buildings `~2321`), NOT the
  same-named `LAYER_CONFIGS` block ~170 lines above (~2094/2115)** — Warden disambiguation.
  **Mason precondition** (consult andon): without the ★ control these layers cannot carry an
  authored ★, so flipping them to `'starred'` later would be a banned **C5** row-dropping
  filter. The `highlightable` add and the Slice C flip must land together. (visitorContext +
  trails are already `highlightable`.)
- **New `mvp/scripts/apply_positioned_features_to_core.py`** — sibling to
  `apply_panel_overrides_to_core.py`. **Draw the reuse line precisely** (Quartermaster):
  - **REUSE** from `panel_overrides.py`: `split_key` / `round_coords` / `dumps_geom` /
    `geom_kind` and the `apply_panel_overrides_to_core.py` `_applied` temp-table +
    `count==input` upsert scaffold (`ON CONFLICT (source_key)`, never bare UPDATE). Do not
    re-implement these — re-implementing them IS the fork.
  - **DO NOT reuse** `panel_overrides.py`'s `read_payload` (it parses the panel-overrides
    *shape* — `edits{}`/`created[]`/`deleted[]` — not the `positioned_features` map) or
    `VIEW_STATE_KEYS` (it **strips `highlight`**,
    the one field this slice exists to carry — reusing it would silently no-op the slice).
    This script reads the `aop-viewer-preset-settings-v3` bundle's `positioned_features` map
    (or a bare `${layerKey}:${id} -> {highlight,…}` slice) and keeps `highlight`.
  - Filter to the four reference editor-layerKeys; map editor-layerKey → core layer
    (`visitorContext`→`visitor`); resolve each key to its core row(s) by the per-layer DB
    lookup in the Grounding #4 table.
  - **UPSERT `attrs = attrs || '{"highlight":true}'`** on the resolved core row, keyed by
    `source_key`. **`attrs.highlight` is the SINGLE source of truth** — do NOT also write the
    `is_destination` column (Mason andon: the reference bake reads `attrs` verbatim and reads
    `is_destination` *nowhere* for these four layers, so a column write has no consumer and
    will drift). Idempotent; `count == resolved-input` asserted via an `_applied` temp table;
    **never** drop/skip/throw on an unresolved key — land a `notes` flag and continue (C5,
    gold's store-first-skip-rest).
  - Un-star (`highlight:false` in the store) clears `attrs.highlight` symmetrically, so an
    un-star survives — mirror `applyPositionedFeatures:3009`.
- **Observable acceptance (tile-independent):** star one feature in **each** of the four
  layers in the editor → "Export all" → run the apply → `SELECT` shows the ★ flag on the
  correct core row (the `:marker` row for cemeteries, the right `visitor`/`trails` row by
  name/num); a non-starred sibling is untouched; re-run is idempotent (count==input, no dup).

## Slice B — ★ travels into the bake (STORE→SERVE)

- **Verify-only** (Grounding #3): run `export_publish_geojson.sh`; the served
  `aop_buildings.geojson` / `aop_cemeteries.geojson` / `aop_visitor_context_callouts.geojson`
  / `aop_trail_network.geojson` carry `highlight:true` on the starred features' properties.
  Add the key explicitly **only** if observation shows the collector needs it top-level
  rather than under the verbatim `attrs`.
- **Observable acceptance:** star → apply (Slice A) → bake → `grep`/`jq` the served file shows
  `"highlight":true` on the starred feature and absent on the rest; **restore served files to
  HEAD after verifying** (the durable change is DB + scripts; the served artifact regenerates
  at the user's deploy).
- **Flag (Quartermaster):** `export_positioned_features.py` is a partly-superseded legacy
  file-baker (visitor moved into `core.features` at gold slice 4). It does **not** clobber the
  ★: it writes only `geometry`/`icon_size` and explicitly ignores `highlight` (its line 27),
  so the **only shared axis with the DB bake is geometry** — that, not the star, is the lone
  clobber vector. Retirement is therefore *scoped* (it needs a buildings apply-door first, per
  gold), not reflexive. Note it OWED with this disjoint-axis fact so a later hand doesn't
  panic-retire it; Slice B's "restore served files to HEAD after verifying" keeps the DB bake
  the one durable writer for this sprint.

## Slice C — flip + render (SERVE→view)

- **Flip `listMode: 'wholesale'`→`'starred'`** on cemeteries / buildings / visitorContext /
  trails (`main.js` ~2274 / ~2345 / ~2653 / ~2860).
- **Published `layer==='poi'` union stays wholesale** (`main.js:1224`) — the bake is its
  curation gate; **never** retrofit `'starred'` onto it. Write it as a code comment.
- **Verify the left-tab curation fields render** for a starred reference row (blurb / status /
  kind chip / `info needed — revisit` placeholder). These are **already produced** — the
  revisit chip is live at `main.js:1414`, `renderPoiTab` renders blurb/kind/status
  (`~1374-1392`), and the collector rows carry blurb/status/kind/sourceChip. So this is
  **verify the existing render still fires for the flipped layers; add a field ONLY if
  observation shows a gap** (Mason — verify-first like Slice B; do not re-derive rows, C2).
- Touches `main.js` → **owes a `sw.js` / `#appVersion` bump (`v53`→`v54`)** (the bump is the
  user's git gate — report it, do not perform it).
- **Observable acceptance (C4 — clone `mvp/scripts/playwright_verify_star_collector.py`):**
  in a clean profile, assert **per-reference-group row counts** — a feature starred-in-core
  (Slice A→B) is present in its POI-tab group; unstarred reference groups are **0**;
  `pubpoi:1`/`pubpoi:2` still render; 0 console errors. **Correction to the harness's inherited
  claim** (Witness): reference-layer `featureListRuntime` DOES seed headless — the registrations
  run inside `map.on('load')` (`main.js:7675/8638/8732/8857/9073`) and populate without tiles
  given a long-enough settle; assert the DOM row counts directly, do NOT fall back to the
  `poi_rows_surfaces.js` node check for the reference half. Tile-independent — no `networkidle`,
  no `queryRenderedFeatures`.

## Guardrails (inherited from the consult)

- **C5 — non-limiting.** The ★ gate reads an authored attribute (`highlight === true`); it
  never rejects an unknown `kind`/`status`/`category`, and an out-of-vocabulary value still
  renders. The `'starred'` listMode is legitimate **only while** the layer is `highlightable`.
  A `'starred'` layer without `highlightable` is a C5 violation by construction — that is why
  Slice A's `highlightable` add and Slice C's flip travel together.
- **The apply never drops a row.** An unresolved key is flagged in `notes`, not skipped
  silently and not thrown on (gold's store-first discipline).
- **Published rows are bake-curated, never `'starred'`** — code comment so a later hand can't
  regress it.
- **No second engine / store / surface.** Extend `collectStarredDestinations` + the existing
  specs; reuse `panel_overrides.py`; no new collector, registry, editor store key, or editor
  HTML (C2 / C3 / C6). The new apply script is a STORE-side sink, not a UI surface.

## The design fork — RESOLVED by the plan-council (2026-06-08)

Slice A resolves the editor-key↔source_key divergence by **DB lookup inside a new sibling
apply script** (editor + bake unchanged). The alternative — bake `source_key` into served
reference `attrs` so the editor keys the ★ by `source_key` directly — is more uniform but
touches the editor's persist path **and** the bake, and adds an editor store field.
**Council confirmed the DB-lookup sink** (Mason + Quartermaster): smallest blast radius,
reuses the gold apply pattern, no editor/bake change; the alternative multiplies surfaces,
exactly what the reuse lens disfavors.

## Loop contract / gates

plan → **council the plan** (full six — DB + publish-zone + user-visible) → user
**commit-pause** → **ralph-loop the slices in a fresh session** (gold/sprint-07 cadence).
Each slice: do → verify by observation → **record on green** → stop. The commit and the
`vNN` bump stay the user's git gate.

**Standing conditions the loop inherits:**
- **Witness** — the new apply script + the cloned Slice-C verifier don't exist yet; the loop
  writes them. Re-witness Slice A's REAL apply output (the correct core row carries the flag)
  and Slice C's REAL clean-profile DOM before trusting any "green." The cloned Slice-C verifier
  must hook **`window.AOP_HOST_MAP`** (not `window.map`, a lexical const that's absent) and
  `wait_for_function` on the **load event** before asserting reference-group row counts — the
  inherited harness's `wait_loaded` only waits on the publish message, which fires *pre-load*
  and does NOT prove the reference registrations ran.
- **Mason** — the `highlightable` add lands with (or before) the flip for cemeteries+buildings;
  confirm the `count==input` acceptance runs against a live apply before Slice A closes.

## Predecessors / related

- `../10_deferred/star_driven_poi_list.md` — the design + council verdict (this card's why).
- `../05_special_operation/_done/06_one_star_driven_collector.md` — the one collector + the
  `listMode` strategy this flip uses.
- `../../06_going_gold/gold_migration.md` — the AUTHOR→STORE→BAKE→SERVE loop this extends;
  `apply_panel_overrides_to_core.py` + `panel_overrides.py` are the reuse base; gold slice 6
  (HELD) is the broader convergence this takes a scoped slice of.
- `../../../northstar/editor_architecture_contracts.md` — C2/C3/C5/C6.
- `../../../northstar/source_register.md` — the raw→core→publish curation contract.
