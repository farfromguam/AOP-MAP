# PWA QA — data bakes & coverage (split out of pwa_qa.md)

> **CLOSED — council triage 2026-06-06.** Three of four items (4 region-callout
> bake, 6 building tiering, E Ellis-cemetery derived bake) are DONE and
> **re-confirmed by observation on the current working tree** this triage:
> `aop_buildings.geojson` = 5 curated (3 facilities Front Office/Pavilion/Farmhouse
> + 2 structure boxes); `aop_cemeteries.geojson` Ellis Point+Polygon both carry
> `burial_count:12` + the named roster + `burial_source`; `aop_visitor_context_callouts.geojson`
> ships baked geometry served from `./data/` (4 features after the 2026-06-05
> brand-logo merge — the bake claim holds, only the count drifted). The one open
> item — **Item 17, extend the 9-patch imagery** — is a distinct data-acquisition
> task gated on an owner decision, **split out to `../extend_9patch_imagery.md`**.
> **Owed but not blocking (do not reopen this card for them):** commit + the
> v27→v29 bump are the user's git gate (`no_commits.md`); the on-device look at the
> black boxes and the always-on-vs-toggle box call are refinements carried by the
> on-device smoke card.

TL;DR:
- Three items from `pwa_qa.md` were too big for the front-end QA swarm because
  they are **data-pipeline / acquisition** work, not viewer chrome. They need
  source-provenance decisions and the `raw → core → publish → bake` spine, so
  they were carved out here on 2026-05-31.
- Owner decisions are required (which buildings are "in park" vs "region", how
  far to extend the imagery AOI). Hold to `northstar/source_register.md` and
  `no_limiting_code_mvp.md` — surface integrity risks as notes, do not add
  rejecting/filtering constraints.

#aop #sprint #04_event_app #pwa_qa #data #bake

-----

## Why these split off

`pwa_qa.md` is mostly viewer/PWA chrome that parallel front-end agents resolved
in worktrees on 2026-05-31. These three need the data spine and a source call,
so they get their own card instead of blocking the chrome swarm.

## Item 4 — bake map region callouts into geojson

> "bake in map region callouts to geojson"

### DONE 2026-06-02 (verified by inspection — no code change needed)

Confirmed already satisfied. `website/data/aop_visitor_context_callouts.geojson`
(13 KB) exists and is loaded **directly from `./data/`** (`website/js/main.js`
~6983) as the always-static "Visitor context callouts" layer — geometry is baked,
not runtime-computed, so a fresh static install renders it. The clean source/copy
split the card asked for is in place: the geojson carries geometry + `name`, and
the rich callout copy is authored separately in `aop_poi_index.json`, joined at
render via `poiIndexLookup({source:'visitor_context', name})` (main.js ~1278).
`playwright_verify_feature_list.py` exercises the visitor-context row (copy emits a
GeoJSON Feature with "Monteagle plateau services") — **PASS**. Nothing owed.

- ~~**Status: possibly partial.**~~ The 2026-05-30 handoff says `misc_4` shipped an
  "images/region-callout export bake." First step: confirm what already exists
  (`website/data/aop_visitor_context_callouts.geojson`? the region-callout export
  path in `misc_4.md`) before re-baking. **→ Confirmed exists + wired (above).**
- Goal: region-level callouts are part of the served geojson (baked), not
  computed/placed only at runtime, so a fresh static install renders them.
- Route through `export_publish_geojson.sh` / the gold-export pattern if these
  are publishable features; keep the source GeoJSON clean so re-exports do not
  overwrite authored copy (the `aop_poi_index.json` precedent).

## Item 6 — buildings: bake in-park, exclude region, drop from search

> "bake buildings in park / exclude buildings in region. — do not allow them to
> be searched."

### SHIPPED 2026-06-01 (working tree, UNCOMMITTED — VERSION v26→v27)

Tiered public/private model baked end-to-end. **Public facilities** (searchable,
clickable, in the POI browser/feature list): **1010 Pavilion · 1033 Farmhouse
(rentable) · 880 Front Office**. **Private structures** (non-interactive black-box
presence markers — visible, but no search / no popup / no list): **665 · 889**
(889 is "loosely in-bounds"; its centroid reads outside, so the authored tag
overrides the geometric test). The other ~197 footprints are untouched region
reference; search now gates to facilities so they (and the boxes) are unsearchable
in one stroke.

- **Data (durable):** `mvp/scripts/import_fema_buildings.py` grew `AOP_FACILITIES`
  + `AOP_PRIVATE_STRUCTURES` maps and `apply_authored_building_tags()` (stamps
  `aop_facility`/`facility_name`/`facility_role` or `aop_structure_box`/`aop_private`,
  keyed by address, idempotent). Applied to the served
  `website/data/aop_buildings.geojson` in place (no network refetch). `inside_aop_boundary`
  kept as the geometric record. **The geometric flag still marks 4 inside (incl 665);
  that over-inclusion is the flagged acreage-reconciliation note.**
- **Viewer (`website/js/main.js`):** FEMA fill/outline filter out `aop_structure_box`
  (boxes only render via a new always-on `building-structure-box` black-fill layer with
  no popup/toggle); the prominent `building-footprint-aop-outline` highlight repointed
  from `inside_aop_boundary` → `aop_facility`; building search `indexFeatures` gated to
  facilities (name + address alias + role alias); POI-browser + feature-list "Park
  facilities" group gated to `aop_facility`; popup leads with facility name/role.
- **Copy:** `aop_poi_index.json` — 1033/880 revisit-notes resolved to real blurbs,
  group note rewritten, 665 entry dropped (now a non-listed box).
- **Verified by observation** (served on :8001): `playwright_verify_buildings.py`
  **PASS, 0 console errors** (3 facilities + 2 boxes tagged; box layer renders;
  Pavilion/Farmhouse/Front Office searchable by name + address; 665/889/383 NOT
  searchable; jump works). `playwright_verify_feature_list.py` building section
  rewritten + **PASS** (3 facilities pre-ticked, 199 other; only the documented
  pre-existing publishable-export FAIL remains). `search` PASS; `presets` building
  checks PASS (pre-existing canvas-intercept fails only); `event_schedule` #pavilion
  resolution PASS. Verifiers updated: `playwright_verify_buildings.py`,
  `playwright_verify_feature_list.py`.
- **Open / owed:** on-device look at the black boxes + facility popups; decide if the
  black boxes should stay always-on across every preset (currently yes, for privacy
  presence) or fold under the buildings toggle; whether a quiet on-map label is wanted
  for any facility. Commit + the v27 bump are the user's call (`no_commits.md`).

### EXTENDED 2026-06-03 — buildings → DERIVED + drag-editable, raw context dropped (UNCOMMITTED, v27→v28)

User: "I want it to be 'derived' now that we chose what buildings to keep — move it
to the right editor group. they are also a little off so I will need the ability to
edit things on that layer." Asked the one real fork (what the Derived layer should
contain) → user chose **split + drop raw context**: the served buildings layer is now
**only the 5 curated buildings** (3 facilities + 2 private boxes); the ~197 raw FEMA
9-patch context footprints are **dropped on purpose** (derived = curated/published
set, matching the rest of the project).

- **Data:** `website/data/aop_buildings.geojson` filtered 202 → **5** curated
  (preserving geometry + tags, `indent=1` format, added a `_derived` provenance note).
- **Importer (durable, `import_fema_buildings.py`):** new `CURATED_ADDRESSES`; `main()`
  now keeps only curated footprints AND **preserves hand-nudged geometry** from the
  prior served file (`load_prior_geometry()` by `build_id`) so a re-import never
  clobbers a drag-correction to FEMA's slightly-off polygons. Docstring + `_sources_checked`
  + summary prints updated.
- **Viewer (`website/js/main.js`):** `#showBuildings` toggle moved **Source layers →
  Derived layers** section (index.html); `SECTION_RUNTIME` buildings moved to
  `derived-layers` with `featureVisibilityLayers`/`featureTagLayers`/**`positionedFeatureLayers: ['buildings']`**;
  `buildings` spec gained an **`onMove`** (bbox-center translate → `savePositionedFeature('buildings', …)`
  → `setData('fema-buildings')` → re-register), mirroring visitor-context; `buildingsData`
  hoisted to a top-level `let` so the spec closure can reach it; **`applyPositionedFeatures('buildings', …)`**
  added to the load path so drags replay on reload; the old "Other buildings in 9-patch"
  group → **"Private structures"** (`match: aop_structure_box===true`, default-off +
  collapsed — those boxes always draw via the standalone `building-structure-box` layer
  so the list tick is inert; the row exists so the box is drag-selectable).
- **Bake (`export_positioned_features.py`):** learned the **`buildings`** layer
  (`id_field: build_id`, `indent: 1`); dump indent parametrized per-layer so a building
  bake keeps the file's `indent=1` (no churn). Path: drag → localStorage → "Export all"
  → script bakes into `aop_buildings.geojson` (5-dec rounded).
- **VERSION v27 → v28** (`#appVersion` + `sw.js`).
- **Verified by observation (served :8001):** `playwright_verify_buildings.py` **PASS,
  0 console errors** (5 curated, all-Residential, search gating intact, boxes render);
  `playwright_verify_feature_list.py` building sections **PASS** (facilities + "Private
  structures" groups, derived-section export carries buildings visibility + positioned_features,
  source-section no longer does — only the documented pre-existing publishable-export FAIL
  remains); `playwright_verify_code_review_groupb.py` **PASS** at v28; a focused drag
  observation **PASS** (✋ on the Pavilion row, footprint lands at the clicked point,
  override stored `buildings:3397585`, survives reload); `bake_layer` temp-file test
  **PASS** (5-dec round + `indent=1` preserved, siblings untouched).
- **Verifiers updated:** `playwright_verify_buildings.py` (202→5, class-mix→all-Residential),
  `playwright_verify_feature_list.py` (group `other`→`private`, counts, section-export
  source→derived), `playwright_verify_code_review_groupb.py` (SW pin v26→v28).
- **Owed:** on-device drag feel (touch + GL, unverifiable headless); commit + the v28
  bump are the user's git gate (`no_commits.md`). The drag primitive is **move only**
  (translate whole footprint), matching the project's existing drag-to-move — vertex
  reshaping was not asked for.

- **DECISION (2026-06-01, user — AAF, no geometry test needed):** "in park" is
  **exactly three named facilities**, not a boundary test — the user knows the
  park firsthand: **`1010 Ellis Cove Road` = Pavilion** (already the seeded
  `aop_seed_pavilion` POI), **`1033 Ellis Cove Road` = Farmhouse**, **`880 Ellis
  Cove Road` = Front Office**. Every other footprint = region/raw context,
  excluded from search. The FEMA data names all three only by address +
  "Single Family Dwelling", so the bake must **author** the real role names.
  **Data discrepancy noted (not a blocker):** the geometric `inside_aop_boundary`
  flag in `aop_buildings.geojson` marks **four** inside — the three above **plus
  `665 Ellis Cove Road`**. The user said "only three", so 665 is region context;
  flag the over-inclusion for the acreage-reconciliation pass (ties to the
  "600+ acre claim vs envelope" open item / MVP backlog item 8). The whitelist is
  authoritative over the geometry flag.
- ~~**Owner decision owed:** what defines "in park" vs "region"?~~ **RESOLVED above.**
- **REFINEMENT (2026-06-01, user) — tiered "presence vs destination", not a flat
  facility list.** In-bounds structures get three treatments:
  - **`1010` Pavilion** = the one **public destination**: searchable, clickable
    popup, in the POI browser/feature list (the event hub; already the seeded POI).
  - **`880` Front Office** = **black box**: dark-filled footprint so it reads as
    "a structure is here," but **not searchable**, minimal/no interaction.
  - **`665` + private house(s) on the in-bounds parcel** = **black box with zero
    interaction**: visible presence only — no search, no popup, not in any list.
    Privacy posture for private residences on AOP land (northstar: show what's
    real, gate what's private — don't route/search into someone's home).
  - **`1033` Farmhouse = OPEN** — searchable destination (like Pavilion) or black
    box (like Front Office)? Default unless the user says otherwise: **black box**
    (only the Pavilion is a confirmed public destination today; promote others as
    they become real destinations). The `aop_poi_index.json` revisit_note for 1033
    already flags it unresolved ("residence, event outbuilding, or off-limits?").
  - **Implementation shape:** bake an authored `aop_facility` (Pavilion only, for
    now) + `aop_structure_box` (the in-bounds non-facility footprints) onto the
    served data; a black-fill layer renders `aop_structure_box`; search/POI-browser/
    feature-list "in park" gate on `aop_facility`. `inside_aop_boundary` stays as
    the geometric record. **Open data q:** does "the parcel with house(es)" include
    footprints beyond `665` (centroids my boundary test missed)? Confirm the parcel
    so the right footprints get boxed, or widen the in-bounds test.
- Bake the in-park buildings as published facilities; region buildings stay as
  raw reference context (the current `#showBuildings` note already warns FEMA
  footprints are "raw reference context; verify against imagery").
- **Search:** region buildings must not appear in viewer search results. The
  front-end half lives in `indexFeatures(...)` for the buildings layer
  (`website/index.html`) — gate which building features get registered by the
  park/region flag baked in the prior step. This half is blocked until the
  classification exists, which is why item 6 stayed off the chrome swarm.
- Honor `no_limiting_code_mvp.md`: the search exclusion is a *display* scope, not
  a data-rejecting constraint — it must not drop rows from the source data.

## Item 17 — extend the 9-patch imagery coverage

> "on tall phones or wide monitors our 9 patch is not enough coverage to not see
> the edges of the map. we need to extend the 9 patch to ~bigger."

- Symptom: on tall phones / wide monitors, fitting the camera shows past the
  imagery/terrain edge → the cream background (`#efe7d5`) shows at the map edges.
- This is **data acquisition**, not CSS: the 9-patch data-acquisition AOI
  (`research/aop_data_bounds.md`, `REGION_BOUNDS` = the camera leash/maxBounds)
  defines how far imagery/topo/DEM/lidar were pulled. To stop the edge showing,
  re-acquire imagery + terrain at a larger AOI **and** widen `REGION_BOUNDS`
  to match (the leash must not exceed the data, or the edge just moves).
- Owner decision owed: how much bigger. Tie the new AOI to the worst-case
  aspect ratios (tall phone portrait, wide desktop landscape) so the fitted
  camera never reaches the data edge.
- Cross-links: `research/aop_data_bounds.md`, `data_integrity_publishability.md`
  (item 10 DEM swap lives there too), `research/viewer.md`.

## Item E (from pwa_qa_2.md item 7) — bake Ellis Cemetery info into the derived set

> "bake info from ellis cementary into our derived dataset. stop showing other
> cementaries on the 9 patch in the [park preset]"

### FINDINGS 2026-06-02 (verified by inspection) — bake DONE, publishability OWED

- **The bake already happened.** `website/data/aop_cemeteries.geojson` ships
  Ellis's full authored detail on **both** its Point and Polygon: `burial_count`
  12, the verbatim `burials` roster (9 named Ellis + 3 infants, with dates),
  `burial_source` (USGenWeb Archives, Marion County TN — transcription by Leslie
  Paul Ellis), `burial_terms` (non-commercial, contributor notice travels),
  `aka` "Bryson & Ellis Cemetery", `aop_inholding`, parcel `110 008.04`. So the
  derived/published cemetery dataset already carries the inholding context — the
  mechanical done-when ("Ellis's authored detail rides in the derived dataset")
  is met **and** the contributor notice travels in-data (USGenWeb's hard rule).
- **The "doubling" is intentional, NOT a dup.** 8 features = 4 cemeteries × {1
  Point marker + 1 Polygon parcel}. Every cemetery follows it; nothing to fix.
  (Resolves the card's "confirm marker+polygon vs accidental dup" first step.)
- **Publishability decision — RESOLVED 2026-06-03 (owner): PUBLISHABLE, keep
  shipping as-is.** The fork: the research brief said treat the roster as
  *"community research, not publishable until permission/use is settled,"* yet the
  served geojson already ships the named roster. Owner's call: AOP is a
  non-commercial hobby-event map, so the use falls inside USGenWeb's free-
  non-commercial grant, and the contributor notice travels in-data
  (`burial_source` + `burial_terms` on every Ellis feature) — their hard
  requirement is met. **No code change needed** (the data already ships it).
  Decision recorded in `brain/research/aop_ellis_cemetery.md` (Sources + Open
  questions). Re-open only if AOP monetizes (paid handouts / sponsored print).
  The provenance brief covers all 8 required source fields; the formal
  `source_register.sources` row lives in the import/publish pipeline, not the
  policy markdown — `source_register.md` is the contract, not a registry table.
  **→ Item E is now fully done.**

- **Routed here 2026-05-31** from `pwa_qa_2.md` — data-pipeline, not viewer chrome.
- **Current state:** `website/data/aop_cemeteries.geojson` carries 8 features =
  4 cemeteries each doubled (Tate, Gilliam, Bible, **Ellis**), all with the same
  parcel-derived prop set (`parcel_id`, `parcel_owner`, `acres`, `aop_inholding`,
  `note`, …). Ellis is the **AOP inholding** (parcel 110 008.04, 0.12 ac) and is
  ALREADY published as a POI via `mvp/scripts/seed_core_pois.sql`
  (`core.pois` → `publish.pois`, the rich blurb lives there).
- **What "bake info … into our derived dataset" means:** promote Ellis's authored
  detail (the burial/inholding context) into the derived/published cemetery layer
  itself — not only the POI point — so a fresh static install carries it without
  the seed SQL. Decide the source of the richer info: the handoff's owed
  **USGenWeb Ellis burial roster** (`northstar/source_register.md` lists it as a
  raw source still owed a `source_register.sources` row before any publish). Hold
  to `source_register.md`: a roster promotes through `raw → core → publish`, and
  publishability is gated on permission/confidence.
- **First step:** confirm whether the doubling in `aop_cemeteries.geojson` is
  marker+polygon or an accidental dup before baking (avoid baking a dup).
- **The paired "stop showing other cemeteries on the 9-patch" is RETRACTED** —
  `pwa_qa_2.md` item 9: the user likes the other cemeteries showing and is still
  deciding. Do NOT add a hide/filter for Tate/Gilliam/Bible. (Also honors
  `no_limiting_code_mvp.md` — no data-rejecting constraint.)

## Done-when

- Item 4: **MET (2026-06-02)** — a fresh static install renders region callouts
  from the baked geojson; source GeoJSON stays authoring-clean (copy in poi_index).
- Item 6: **MET (2026-06-01, re-verified 2026-06-02)** — in-park buildings baked as
  facilities, region buildings excluded from search, no source rows dropped.
  Owed: commit/v27 bump (user gate), on-device look, always-on-vs-toggle for boxes.
- Item 17: **OPEN** — needs imagery/terrain re-acquisition at a larger AOI + owner
  "how much bigger"; then `REGION_BOUNDS` widened to match so the fitted camera
  shows map data to every edge (no cream band) at worst-case aspect ratios.
- Item E: **MET (2026-06-03)** — Ellis's authored detail rides in the derived
  dataset, the contributor notice travels in-data, the doubling is intentional
  marker+polygon (no dup), the other cemeteries stay visible (hide retracted), and
  the **publishability fork is RESOLVED** (owner: keep shipping — non-commercial
  hobby use). Nothing owed.

## Status summary (2026-06-03)

**Three of four items are DONE** (4, 6, E). The only thing left on this card is
**Item 17** — extend the 9-patch imagery — which is genuine data re-acquisition
(pull imagery/terrain at a larger AOI, then widen `REGION_BOUNDS` to match) plus an
owner "how much bigger" call; it is **not headless-actionable** and was never part
of the QA-chrome scope. Item 6 stays UNCOMMITTED awaiting the user's git gate + v27
bump; its always-on-vs-toggle box behavior + on-device feel are refinements, not
blockers. **This card is effectively closeable down to Item 17.**
