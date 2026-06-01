# Trail Research Integration — scope

Status: **Slices 1–3 SHIPPED**, merged to `master` (`67df0f4`) on top of
the pwa_qa2 v19 build — see `copy_review_surface.md`. The onX→park-voice rewrite is
**DONE** (descriptions are now original AOP wording, brain voice), so the onX-copyright
caveat is dropped. **Slice 3 shipped 2026-06-01 and is now COMMITTED** (tree
clean; `search-result-desc` + `renderSearchResults` confirmed in
`website/js/main.js` after the source split). Slice 4 (landmark geometry) remains
deferred (blocked on landmark coordinates, most of which do not exist yet). The
license/publish gate is still owed before any public publish. Authored 2026-05-31.

Goal: wire the persisted trail research (names + descriptions + named landmarks)
into the live viewer so a trail on the map carries its name, difficulty, and
write-up — on click, in the left POI browser, and in search — instead of showing
only a bare number.

#aop #04_event_app #trails #integration #shipped

-----

## SHIPPED (2026-05-31, branch `copy-review`)

Runtime sidecar join, exactly as recommended below. No prose baked into geometry.

- **Catalog loader** — `fetchTrailCatalog()` + `trailCatalog` Map + `trailCatalogLookup(props)`
  in `index.html`, mirroring `fetchPoiIndex`. Joins by `trail_number` (numeric
  `name` fallback). `aop_trail_catalog.json` already in the SW data precache.
- **Slice 1 — trail click popup (NEW).** `bindPopup('aop-trail-network', …)`:
  title = catalog name + number (`Little Dipper (Trail 9)`); rows lead with the
  **map-color Difficulty** (park authority), then catalog About / Length / onX TR
  (secondary) / Connects-to. Un-catalogued trails show Number + Difficulty +
  "write-up owed". (Fork 3 = map color first; done.) No license footer — the
  descriptions are original AOP wording (see Fork 1).
- **Slice 2 — POI browser trails group repointed.** Was iterating the legacy
  `publishDataCache` `trail_centerlines` (2 observed GPX segments); now iterates the
  **gold `aop-trail-network`** (Fork 2 = gold; done), deduped to one row per trail
  (network has multiple edges per number), unnamed edges skipped, numbered-first
  sort. 9 catalogued trails get the write-up; the rest carry a "name/description
  owed" placeholder so the gap stays auditable.
- **Fork 1 (license) — RESOLVED by rewriting.** The 8 onX-sourced descriptions were
  rewritten in the project's own voice (`brain/voice/voice_guide.md`): same facts
  (difficulty, obstacles, what connects), original wording. The onX-copyright concern
  no longer applies, so the license footer/caveat was dropped from the trail popup,
  the POI row popup, and the registry. Trail 96 keeps the park's own 2015 wording.
  Fact provenance stays in each catalog row's `sources` array.
- **Copy registry updated** — `aop_copy_registry.json` `trail_catalog` kind now
  lists the three live surfaces + the runtime-join (no license note; descriptions
  rewritten in brain voice), so the printable copy-review page reflects the wiring.

### Slice 3 — search description preview (SHIPPED 2026-06-01, main checkout, uncommitted)

When a search hit is a catalogued trail, the result row now stacks the trail
number/name over a muted, one-line description so the dropdown previews the
write-up before you click. Implementation in `website/index.html`:

- **`renderSearchResults()` (~10516).** For `match.kind === 'trail'`, look up the
  catalog via `trailCatalogLookup({ name: match.name })` — the search groups carry
  no feature props, but the gold network's display name *is* the trail number
  ("9", "32"), and the lookup keys off a numeric name, so it resolves the same
  entry the popup + POI browser do. If `cat.description` exists, the row wraps the
  label + a new `.search-result-desc` in a vertical `.search-result-text` column
  (with `.search-kind` kept as a top-aligned flex sibling); description truncated
  to ~80 chars + `…`. **Non-trail / un-catalogued / no-description rows render
  byte-identically to before** (single line, no wrapper). Description text is set
  via `textContent` in a second pass (not `innerHTML`) so first-party copy is never
  parsed as markup.
- **CSS (~712).** `.search-item` gained `align-items: flex-start`; new
  `.search-result-text` (vertical column), `.search-result-label`, and
  `.search-result-desc` (0.74rem, `--brown-soft`, one-line ellipsis clamp). Uses
  the real `:root` palette vars.
- **Coverage:** the same 9 catalogued trails (1, 2, 3, 5, 6, 7, 9, 11, 96) that
  light up in the popup/browser now preview in search; the other ~110 show the
  bare number/name as before — the gap stays visible, not hidden.

**Verified by observation** (Playwright `playwright_verify_search.py` on `:8001`,
main checkout, re-run by hand 2026-06-01): full suite **PASS, 0 console errors**.
Durable Slice 3 assertions added to the verifier — trail 96 + trail 11 rows carry
a `.search-result-desc` with the catalog text (truncated to 80 chars ending `…`);
un-catalogued `11X` and road/address hits carry **no** desc line. (One pre-existing
verifier setup bug fixed alongside: the "trail search auto-enables the network
layer" check lacked a `showAopTrailNetwork` reset, so an earlier trail search left
the layer on and the precondition was stale — added the reset, in-pattern with the
file's other pre-assertion resets; test-setup only, doesn't mask the feature.)
A user-facing `VERSION` bump is **owed** for this change but **not** done (user's
call, per `ai_rules/no_commits.md`).

**Verified by observation** (Playwright on `:8001`, worktree): POI trails group
121 rows incl. ~100 trails, "Launchpad" joined to its rewritten description, 101
owed-placeholder chips, Launchpad row popup shows the rewritten description with no
onX caveat; trail map popup observed for un-catalogued (Trail 50/68 → Number +
Difficulty + owed) AND catalogued (`Little Dipper (Trail 9)` → About + onX TR2, no
license footer); 0 console errors. Re-verified against the merged `master`
(copy-review 20/20, trail 11/11). Logs/screenshot: `brain/output/trail_verify.log`,
`trail_integration.png`.

**Still owed:** Slice 4 (landmark geometry — blocked on placing the 8 catalog
landmarks, most have no coordinates), names/descriptions for the ~110
un-catalogued trails (field work / park-supplied list), and promotion to
`publish.*` (source rows + license gate). Whether to retire the legacy
`publish.geojson trail_centerlines` + its `bindPopup('publish-trails')` is still
open (MVP backlog item 9 / `data_integrity_publishability.md`). A `VERSION` bump
covering Slices 1–3 is owed (user's call).

-----

## TL;DR

- The research **is** persisted and the join is clean: every catalog trail
  number exists in the served network. **9 of 87 numbered trails** light up with
  a description today; the other 78 numbered + 20 unnamed edges still carry only
  number + difficulty (that is real-world ceiling, not a bug — see
  `research/aop_trail_name_index.md`).
- Recommended shape: **runtime sidecar join**, catalog stays source of truth,
  join on `trail_number`. Do **not** bake description text into the served
  geometry (same principle the POI index already follows — keeps re-exports clean
  and keeps licensed text in one gated file).
- Three surfaces: **(A) trail click popup** (new — none today), **(B) left POI
  browser trails group** (exists but points at the wrong dataset — repoint),
  **(C) search** (already finds trails; optionally show a description preview).
- Two real forks owed before public exposure: the **license gate** (onX-derived
  prose is "rewrite before public publish") and **which trail dataset** the POI
  browser + popups should read.

-----

## What is persisted (inputs)

Full inventory in the 2026-05-31 review; the load-bearing files:

| File | What | Role in integration |
| --- | --- | --- |
| `website/data/aop_trail_network.geojson` | **Gold** served geometry. 120 edges, 87 numbered, 100 named, 20 unnamed. Props: `trail_number`, `name`, `difficulty`, `color`, `source`, `review_status`, `id`, `kind`. | The join **target** — what renders + is searchable. |
| `website/data/aop_trail_catalog.json` | **Curated catalog**, schema `aop-trail-catalog-v1`. 9 trails (1,2,3,5,6,7,9,11,96) with name/difficulty/TR/length/description/`connects[]`/sources + 8 named landmarks. | The **source of truth** for descriptions. |
| `brain/import/community_trails/aop_trail_descriptions.json` | Raw harvested prose (onX `og:description` + Trail 96 Wayback). | Upstream raw zone; catalog supersedes it for the viewer. |
| `brain/research/aop_trail_name_index.md` | The research write-up: why AOP is numbers-only, difficulty bands, license posture. | Authority for the caveats below. |
| `website/data/sfwda_traced_markers.geojson` / `sfwda_numbered_trails.geojson` | 124 georeferenced paper-map markers / 67 per-trail traces. | **Not** needed for description join (gold already labels). Separate review layers. |

## Current viewer state (the join target + surfaces)

- **Render + labels:** `aop-trail-network` line layer + `aop-trail-network-labels`
  (`website/index.html` ~9226). Colored by baked `color`, labelled by `name`.
- **Search:** `indexFeatures(aopTrailNetworkData, 'trail', …)` (~9259) registers
  every named trail; select → fly + enable layer + pulse. **Working.**
- **Click → detail: NONE.** `bindPopup(...)` exists for `publish-trails`,
  `publish-trailheads`, `osm-tracks`, lidar, contours — but **nothing is bound to
  `aop-trail-network`.** Clicking a trail does nothing today. This is the main new
  wiring.
- **Left POI browser "trails" group exists** (`pushRow('trails', …)`,
  `index.html:2465`) **but reads the wrong dataset** — it iterates
  `publishDataCache` features where `layer === 'trail_centerlines'` (the legacy
  `publish.geojson` placeholder set, MVP backlog item 9), not the gold
  `aop-trail-network`. So the browser's trail list and the map's trails are two
  different sources. **Wrinkle to resolve.**
- **Proven sidecar pattern to reuse:** `aop_poi_index.json` +
  `poiIndexLookup({source, …})` already attaches visitor blurbs to features by
  `source` + an identifying prop, and surfaces `revisit_note` as auditable
  "info needed" placeholders. The trail join is the same shape, keyed on
  `trail_number`.

## The join

- **Key:** network `trail_number` ↔ catalog `number`. Verified **100% hit** —
  all 9 catalog numbers `[1,2,3,5,6,7,9,11,96]` are present in the network.
- **Coverage after integration:**
  - 9 numbered trails → full popup/browser entry (name, difficulty, description,
    length, TR, connects).
  - 78 numbered trails → number + difficulty only (description owed).
  - 20 unnamed edges → geometry + difficulty only (name owed — user names these
    in Affinity, per the importer note).
- Per-row caveat the catalog already carries: park-map **color** is the park's
  own difficulty authority; onX TR can disagree (6/7 read green on the map, Mod on
  onX). Popup should lead with the **map color**, show onX TR as secondary.

## Recommended approach — runtime sidecar join

Mirror the POI-index mechanism; keep the catalog whole.

1. **Load the catalog at startup** like `poiIndex`: fetch `aop_trail_catalog.json`,
   build `trailCatalog = Map<number → trail>`. One fetch, fail-soft to `{}`.
2. **Trail click popup (Slice 1).** `bindPopup('aop-trail-network', 'Trail', …)`
   whose rows fall back to feature props, then enrich from `trailCatalog.get(trail_number)`:
   name, difficulty (map color first), description, length, TR, `connects` as
   "Connects to: 3, 18, 22, 50". No catalog entry → number + difficulty only.
3. **Left POI browser (Slice 2).** Repoint the `trails` group from
   `publishDataCache/trail_centerlines` to the gold `aop-trail-network`; attach the
   catalog description via `trail_number`; rows with no description get a
   `revisitNote`-style "name/description owed" placeholder so the 78+20 gaps stay
   auditable (same convention as the POI index).
4. **Search preview (Slice 3, optional).** When a search hit is a catalogued
   trail, show the one-line description under the result.
5. **Landmarks (Slice 4, separate).** The 8 catalog landmarks (Area 51, Battle
   Creek, Lesson/Freeze/Bounty/Riot zones, Jeep/Buggy entrances) mostly have **no
   coordinates**. Only ones with derivable geometry become POIs; the rest stay
   catalog-only until placed. Low confidence — keep out of Slices 1–3.

**Why not bake into the geojson:** the POI index design note is explicit —
authored copy lives in a sidecar so a re-export of geometry can't overwrite it,
and the onX-derived text is licensed. Baking descriptions into
`aop_trail_network.geojson` (via `export_gold_trail_network.py`) would re-mix
licensed prose into the served geometry and get clobbered on the next SVG
re-import. Sidecar keeps both clean.

**Alternative considered:** fold the 9 descriptions into `aop_poi_index.json`
under the existing `trails` group. Reuses the loader with zero new code, but
flattens the catalog's structured fields (connects, TR, length, landmarks,
per-row license) into a blurb-only schema. Rejected as the primary path; the
catalog is richer and already exists. (If we want one loader, the POI-index
`trails` group can simply be the thing Slice 2 repoints + enriches.)

## Forks owed (decide before/within the work)

1. **License / publish gate.** Catalog prose is paraphrased from onX and flagged
   *"rewrite in the park's voice before any public publish"*; promotion out of raw
   needs `source_register` rows + permission (`northstar/source_register.md`). The
   park authorized **assembly/curation**, not verbatim public republish.
   - *Recommendation:* show descriptions now in the **editor/default** view (the
     viewer is the editing surface — `ai_rules/editor_is_the_viewer`), tagged with
     their license; do the voice-rewrite pass before any public-gated build
     (`?edit=0`). Surfacing them internally is in-bounds today.
2. **Which trail dataset is canonical for the browser + popups** —
   `aop-trail-network` (gold, what renders) vs `publish.geojson trail_centerlines`
   (legacy placeholder). *Recommendation:* gold. Then decide whether the legacy
   `trail_centerlines` rows + `bindPopup('publish-trails')` get retired (ties to
   MVP backlog item 9 / `data_integrity_publishability.md`).
3. **Difficulty display** when map color and onX TR disagree — lead with map
   color (recommended), TR secondary. Cheap, but state it so it's not silent.

## Out of scope / owed upstream

- Names + descriptions for the ~110 un-catalogued trails — needs field work or a
  park-supplied list (`aop_trail_name_index.md` "owed_work"). Integration surfaces
  the gap; it does not fill it.
- Naming the 20 unnamed network edges (user, in Affinity → re-import).
- Promoting any of this to `publish.*` (license + source rows first).
- Attaching landmark geometry (Slice 4 precondition).

## Verification (per `ai_rules/verify_by_observation`)

- Playwright: click trails 1 and 96 → popup shows name + description; click an
  un-catalogued numbered trail → number + difficulty, no error; left browser
  trails group lists gold trails with the 9 descriptions + placeholders for the
  rest; 0 console errors. Extend `playwright_verify_left_poi_browser` /
  `playwright_verify_presets` rather than a new bespoke suite where possible.
- Eyeball: descriptions read right on the map, license caveat present in the
  editor view, public (`?edit=0`) view honors the gate decision.

## Effort read

Slices 1–2 are the value and are small (one fetch + one `bindPopup` + repointing
one existing loop). Slice 3 is a nicety. Slice 4 is blocked on geometry. Fork 1
(license gate) is a decision, not code. Recommend shipping Slices 1–2 behind the
editor view, logging the gaps, and leaving 3–4 + the publish-rewrite as
follow-ups.
