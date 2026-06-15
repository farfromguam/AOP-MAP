# Editor — unified tree by base type

Date: 2026-05-27

TL;DR:
- The right rail's **POI** section and **Map editor** section were added at
  different times. They overlap: POI is a global-group-toggle deck two-way
  bound to source toggles; Map editor is layer toggles + draw buttons + a
  kind-grouped tree limited to `editorPois`. Two surfaces, one job.
- This card collapses them into **one** Map editor section organized as a
  tree by *renderable kind*: **Point ● · Line ╱ · Polygon ▭ · Image ⌗ ·
  Callout ⌑**. Items hang under their bucket; the inline accordion that
  exists for drawn POIs becomes the leaf affordance for every author layer
  that opts in.
- A new virtual group **★ Visitor list** sits at the top of the editor and
  live-mirrors every starred feature across the buckets. The left-rail POI
  tab is unchanged — both surfaces feed off the same `props.highlight ===
  true` axis.
- The dedicated POI section is deleted. Its global-group affordance is
  carried by each bucket head's bulk-feature checkbox; the underlying
  source-layer toggles are owned by Source / Derived / External reference
  as they always were.

#aop #04_event_app #editor #right_panel #tree #poi #crud

-----

## Source

- User direction (2026-05-27): *"review the sidebar on the right and put effort into combining the POI and the map editor. they were put in at different times and they kinda work ok. but need a re-think. I want all map editor stuff to be in a tree under its base type point line polygon image callout… and in that are the items and under the items are edits. each thing can have a tag and a category and a star hand and a fly to… basically appropriate edit icon stars make them show up in the poi list on the right. this should live update."*
- User direction same turn: *"I dont have the bandwidth to make 6 decisions you need to step up here and make it happen."* — Decisions locked by the assistant per `ai_rules/act_dont_ask.md`; recorded below so any contributor can see what was decided and why.
- Predecessors:
  - `../03_event_app/_done/poi_editor_tree_inline_accordion.md` — the kind-grouped tree + inline accordion that already exists for `editorPois`. This card hoists the same shape to the top of the editor.
  - `../03_event_app/_done/poi_editor_inline_list_and_highlight.md` — the ★ axis. This card extends ★ to brand logos and visitor-context callouts so the curation gate covers every author layer.
  - `../03_event_app/_done/left_panel_poi_browser.md` — the left-rail POI tab whose `drawn_pois` group consumes the ★ gate. The same gate now feeds the right-side virtual list.
  - `../03_event_app/_done/right_panel_editor_consistency.md` — the prior right-rail pass; this card supersedes its Publishable-row inline lists for the author layers.
- Adjacent:
  - `poi_editor_followups.md` — defers reshape, source-register fields, bulk select, and the two S3 review items (notes-trim naming and Reset-viewer seed-tag rebind). Two of those (notes-trim naming, optional star inside the accordion) are bundled into this pass since we're in the editor anyway.

## Decisions (locked)

1. **Delete the POI section.** The right rail's `data-section="poi"` block is removed. Its six group toggles were a remote control on the underlying source toggles; per-bucket bulk-feature checkboxes plus the source toggles in Source / Derived / External reference cover the same affordance with a clearer mental model (bucket = renderable kind; source = where the data came from).
2. **Five buckets.** Point ● · Line ╱ · Polygon ▭ · Image ⌗ · Callout ⌑. *Image* is a renderable-kind bucket, not a geometry-type bucket: brand logos live here because they render as icon-image symbols, even though the GeoJSON underneath is a Point. *Callout* is annotation polygons with editable label boxes — visitor-context circles live here.
3. **★ extends to brand logos and visitor-context.** Both pick up `highlightable: true`; defaults stay off. The ★ axis is the curation gate for the visitor list, and it's the same axis regardless of which layer the feature lives in.
4. **Read-only leaves keep row + tag + fly + visibility; no delete, no ★.** Event-schedule anchors render as rows under the Point bucket, with their existing `tag` + visibility + fly. They have no inline accordion (their authorship lives in `aop_event_schedule.json`, not the panel) and no ★ (anchors always surface as anchors; they're not a curation axis).
5. **★ Visitor list virtual group at the top of the editor.** Live mirror of every `props.highlight === true` feature across `editorPois`, `brandLogos`, `visitorContext`. Read-only rows with name + source chip + 🎯 fly + ★ (click to unstar pulls it from the list and from the left POI tab in one move). Re-renders on every star toggle and every source-layer re-register.
6. **Create controls move to a footer.** Category select + `Place POI` / `Draw footprint` / `Trace line` / `Export GeoJSON` / `Clear all` + status line drop to the bottom of the editor section in a `.editor-create-footer` block. The tree leads; create follows.

## Out of scope

- **Buildings and cemeteries stay in their Source-layers drawer.** Hoisting 280+ FEMA polygons into the editor tree dwarfs the actual editor content. The existing Buildings drawer with `in_park` / `other` groups already handles this. If a user wants to tag a building, that's still where they do it.
- **Activity hotspots, synthetic activity, publishable trailheads stay where they are.** They're not author content — `activityHotspots` is GPX evidence (User submitted section), `syntheticActivity` is a derived simulation (Derived section), `trailheads` is read-only publish.geojson. None of them earn a tree row in this pass.
- **Per-layer accordion generalization** — the inline accordion currently knows how to edit an `editorPois` leaf (name, category, tag, notes, geometry summary, actions). Extending that to brand-logo size sliders or visitor-context label HTML is a larger refactor and is deferred to `poi_editor_followups.md` open work. In this pass, the accordion is editorPois-only; brand-logo / visitor-context rows surface their existing controls (size, ★, ✋ move, 🎯 fly) inline on the row without a chevron.
- **Reshape / re-vertex** for polygons and lines — already deferred in `poi_editor_followups.md`.
- **Source-register fields** in the editor — wait for the event/submission loop to land actual storage.

## Shape

```
<section data-section="editor">
  Header: Map editor                              ⧉  ▸

  Editor content (5 layer toggles, thin strip — kept so the layer-level
  on/off is reachable without scrolling Source / Derived sections)
    [ ] Event schedule POIs
    [ ] Publishable trailheads
    [✓] Visitor context callouts
    [ ] Brand logos
    [✓] Drawn POIs

  ★ Visitor list  (3)
    Pavilion             — drawn      🎯 ★
    AOP badge            — image      🎯 ★
    Supply run callout   — callout    🎯 ★

  ● Point          (6/9 visible · 2 ★)
    [editorPois Point rows + inline accordion]
    [eventSchedule rows — read-only, tag + visibility + fly]

  ╱ Line           (1/1 visible)
    [editorPois LineString rows + inline accordion]

  ▭ Polygon        (1/1 visible · 1 ★)
    [editorPois Polygon rows + inline accordion]

  ⌗ Image          (2/2 visible)
    [brandLogos rows with size + ★ + ✋ + 🎯]

  ⌑ Callout        (2/2 visible)
    [visitorContext rows with ★ + ✋ + 🎯]

  + Create
    Category ▾  Place POI · Draw footprint · Trace line
    Export GeoJSON · Clear all
    <status: 0 POIs, 0 footprints, 0 traces.>
    <help text: existing prose, slightly tightened.>
</section>
```

## Files touched

`website/index.html`:

- **HTML structure**
  - Delete `<section data-section="poi">` (was `:784–800`).
  - Restructure `<section data-section="editor">` (was `:802–851`):
    - Keep section header + `data-section-export="editor"` button.
    - Top strip: keep the 5 existing layer-toggle inputs intact (ids preserved — every change handler keeps wiring), but rendered inside a compact `.editor-layer-strip`.
    - New `.editor-tree` container with one `.editor-bucket` per kind.
    - Each bucket renders via the existing feature-list primitive with one new render-time option (`onlyGroupId`) so `editorPois` can be rendered three times (Point / Line / Polygon).
    - Footer `.editor-create-footer` carries the create row, export, clear, status, and help.

- **CSS**
  - New: `.editor-layer-strip`, `.editor-tree`, `.editor-bucket`, `.editor-bucket-head`, `.editor-bucket-glyph`, `.editor-bucket-body`, `.editor-visitor-list`, `.editor-visitor-list-row`, `.editor-create-footer`.
  - Reuse `.feature-list`, `.feature-list-group`, `.feature-list-rows`, `.feature-row`, `.feature-row-editor` unchanged — the bucket body is just a `.feature-list` target.

- **JS**
  - Delete `wirePoiPanel()` and the `data-poi-group / data-poi-target` two-way bridge.
  - Extend `FEATURE_LIST_LAYERS.brandLogos.highlightable = true` and `FEATURE_LIST_LAYERS.visitorContext.highlightable = true`. (Defaults stay off; ★ stays opt-in per feature.)
  - `renderFeatureList(layerKey, { onlyGroupId? })` — new opt arg. When set, only the matching group renders; the heading hides its all-groups counter and falls back to the bucket head's counter. When unset, behavior is unchanged.
  - New `EDITOR_BUCKETS` array declaring `{ id, label, glyph, leaves: [{ layerKey, onlyGroupId? }] }`.
  - New `renderEditorTree()` that, for each bucket, creates a `.editor-bucket` block with head (glyph + label + bulk-visibility checkbox + count) and a body that calls `renderFeatureList` per leaf. A new per-bucket-per-leaf DOM target is registered via `FEATURE_LIST_TARGETS` so the existing primitive renders into the bucket body.
  - New `renderVisitorListGroup()` that iterates every leaf layer (`editorPois`, `brandLogos`, `visitorContext`) and renders one read-only row per feature with `properties.highlight === true`. Source chip on each row. Click row = fly; ★ click = `toggleFeatureHighlight(layerKey, id)` (existing function, no change).
  - Live updates: `toggleFeatureHighlight` and `registerFeatureListLayer` already call `renderPoiTabIfActive()`; they pick up a new `renderVisitorListGroup()` call so the right-side surface also refreshes.
  - `setEditorFeatureNotes` rename + behavior: `String(value || '').trim()` so whitespace-only notes delete the field; var renamed from `trimmed` (misleadingly) to `next`. Closes one S3 review item from `poi_editor_followups.md`.

`mvp/scripts/playwright_verify_presets.py`:

- Tab-label assertion unchanged.
- **Remove** the right-panel POI-section assertions (six group toggles, two-way bind).
- **Add** assertions:
  - `data-section="poi"` does not exist.
  - `.editor-tree` contains five buckets (`Point`, `Line`, `Polygon`, `Image`, `Callout`).
  - `.editor-visitor-list` renders zero rows on a clean install (seed pavilion is highlighted, so this becomes `1 row` once the seed re-arms — see verifier-side note below).

`mvp/scripts/playwright_verify_poi_editor.py`:

- The editorPois inline list now lives inside the Point / Line / Polygon buckets, but the `#editorPoiList` element is gone — `editorPois` rows are rendered into bucket-scoped containers. The verifier's selectors update to reach a bucket-scoped feature-list (`[data-bucket="point"] .feature-list`, etc.).

`mvp/scripts/playwright_verify_feature_list.py`:

- Buildings / cemeteries / visitor-context / brand-logos drawer-list assertions unchanged for the layers that stay in their drawers (buildings, cemeteries).
- visitor-context and brand-logos selectors update to point at the new bucket-scoped containers.

`mvp/scripts/playwright_verify_session_tools.py`, `playwright_verify_event_schedule.py`:

- Spot-check; no expected change. If they read `#poiGroupBuildings` (etc.) directly, update or delete those assertions.

## State

- **No new localStorage keys.** Highlight, visibility, tags all persist where they already do (`aop_editor_pois_v1`, `aop_feature_visibility_v1`, `aop_feature_tags_v1`, brand-logos / visitor-context override stores). Extending ★ to brand-logos and visitor-context writes the same `properties.highlight` field into their feature objects; for those two layers `properties` lives in-memory only (the override stores already snapshot full features, so the flag travels with them on reload via the override path).

Note: the existing override stores key on `name` (visitor context) and `logo_id` (brand logos) and persist `geometry + updated`. To carry `highlight` across reload, the override store record gains an optional `properties` field. Backward compatible — absent `properties` reads as `{}`.

## Verification (2026-05-27 — shipped)

Observed on `http://localhost:8001/` with the 5 verifier scripts re-run:

- `playwright_verify_poi_editor.py` — **PASS** (0 console errors).
- `playwright_verify_synthetic_activity.py` — **PASS**.
- `playwright_verify_session_tools.py` — **PASS** (Reset re-seeds pavilion; storage keys clean).
- `playwright_verify_presets.py` — **FAIL on one pre-existing assertion** (mobile-overlap, 4 px boundary: `bar.y + bar.height = 308` vs `panel.y = 304` at viewport 500×760). The dimensions are CSS-driven by `.left-controls` height (300 px) and `.panel { bottom: 56px; max-height: clamp(...) }` (line 538) — both untouched by this card. The "no non-tile console errors" assertion at the same script: PASS.
- `playwright_verify_feature_list.py` — **FAILs are all pre-existing**:
  - Visitor-context reveal assertions updated to expect the editor section opening (not the legacy drawer); now PASS.
  - Three failures all target `data-section="publishable"`, which does not exist in the current `website/index.html` (`grep -c publishable index.html → 0`). The verifier expects a section that was renamed/folded before this card. Routed to `viewer_polish_followups.md` cleanup.
- `playwright_verify_event_schedule.py` — six failures, all on the trail-lane fallback path (`activity-hotspots toggle`, cluster zoom). Per `session_context.md` 2026-05-27 note, trail-lane verifier residue was already routed to `viewer_polish_followups.md`.

Live manual probe confirms the curation axis works end-to-end. Starring an `aop_badge` brand-logo and a `Monteagle plateau services` callout, plus the seeded pavilion, surfaces all three in the right-side **★ Visitor list** group with the correct source chips (`image`, `callout`, `drawn`) without a reload, and they re-flow to the left-rail POI tab on the same axis. Buckets render with the expected counts: Point 9/9 · 1 ★, Image 2/2 · 1 ★, Callout 2/2 · 1 ★. Screenshot at `brain/output/playwright_editor_unified_tree.png`.

## Acceptance

- [x] `data-section="poi"` is gone from `website/index.html`. No DOM, no JS bridge (`wirePoiPanel` retired); presets verifier asserts the section is absent.
- [x] The Map editor section renders a five-bucket tree in the order Point / Line / Polygon / Image / Callout. Each bucket head shows the glyph, label, a bulk-feature visibility checkbox, and a `visible/total · N ★` count. Empty buckets show "No items yet." rather than disappearing — keeps the tree shape stable.
- [x] editorPois rows split across Point / Line / Polygon by geometry, sourced from the existing three-group spec via the new `renderFeatureList(layerKey, { onlyGroupId })` opt arg. Inline accordion still works on each leaf.
- [x] brandLogos renders under Image with its existing size slider, ✋ move, 🎯 fly, plus the new ★ button. visitorContext renders under Callout with ✋ move, 🎯 fly, plus ★. Override stores extended to persist `highlight` across reload.
- [x] eventSchedule renders under Point (read-only — tag input + visibility + fly + no accordion + no ★ + no delete) alongside drawn POIs.
- [x] ★ Visitor list virtual group renders at the top of the editor with every `highlight === true` feature across the three highlightable layers, sorted by name, with source chip per row. Click row = fly. Star click = unstar (row removes itself, left POI tab refreshes).
- [x] Live update verified by observation: starring `aop_badge` and the Monteagle callout from the JS console immediately flowed both into the visitor list group with the correct chips.
- [x] Create footer carries the create row + export + clear + status + help. The button ids (`placePoiBtn`, `drawFootprintBtn`, `traceLineBtn`, `exportPoiBtn`, `clearPoiBtn`, `poiCategory`) and the 5 layer-toggle ids (`showEventSchedule`, `showTrailheads`, `showVisitorContext`, `showBrandLogos`, `showEditorPois`) are unchanged so all existing event listeners and presets keep working.
- [x] `playwright_verify_poi_editor.py` PASS — 0 console errors.
- [x] `playwright_verify_synthetic_activity.py` PASS.
- [x] `playwright_verify_session_tools.py` PASS — Reset re-seeds the pavilion; visitor list shows one row post-Reset.
- [~] `playwright_verify_presets.py` PASS on all editor-tree assertions and the `no non-tile console errors` assertion; FAIL on one pre-existing mobile-overlap assertion (4 px boundary on dimensions controlled by CSS untouched by this card).
- [~] `playwright_verify_feature_list.py` PASS on all editor-tree assertions including the updated visitor-context reveal path; FAIL only on three pre-existing `data-section="publishable"` assertions (that section does not exist in the current HTML — routed to `viewer_polish_followups.md` cleanup).
- [~] `playwright_verify_event_schedule.py` six FAILs all on the pre-existing trail-lane fallback path already noted in `session_context.md` / routed to `viewer_polish_followups.md`. Tag-driven block + clock-times block PASS.

## Verifier note: pavilion seed and ★

The seed file `website/data/aop_editor_seed_pois.geojson` ships the pavilion with `highlight: true`. Post-seed (clean install or post-Reset), the Visitor list shows one row: "Pavilion — drawn (point)". Verifier assertions for "no visitor rows" need to either:

- Wipe `aop_editor_pois_v1` to `[]` first (the existing verifier convention — `setItem('[]')` keeps the seed gate closed), then assert zero, then draw, then star, then assert one.
- Or accept the seed-armed baseline as 1 and validate the delta.

The first form is what `playwright_verify_poi_editor.py` already does for editorPois fresh-slate tests; carry the convention into the new ★ Visitor list assertions.

## Open follow-ups (intentionally deferred)

- Per-layer accordion editor for `brandLogos` (name + size + ★ + ✋ inside the chevron) and for `visitorContext` (name + label + ★ + ✋ inside the chevron). Today their inline row carries the same controls minus the accordion. Land when somebody asks.
- Bucket reordering — today the bucket order is fixed (Point / Line / Polygon / Image / Callout). If a user wants Callout above Point on a curation pass, add a drag handle on the bucket head. Defer.
- Per-bucket export — bucket-scoped `⧉` chip. The section-level `⧉ Export all` already covers the editor. Land if requested.
- `S3 review 2026-05-27 — Reset viewer re-runs maybeSeedEditorPois` from `poi_editor_followups.md`. Not in scope here; documented in `spinup/viewer_storage_migration.md` separately.

## Follow-up fix — 2026-06-06: left/right drawn-POI desync (single source of truth)

Symptom (user report): a drawn POI showed in the left-rail `POI` tab but not on
the right (★ Visitor list / Point–Line–Polygon buckets). Root cause: the two
surfaces read different stores through different triggers. The left tab reads the
canonical `editorPois` array (localStorage `aop_editor_pois_v1`) directly; the
right reads `featureListRuntime['editorPois']`, a derived projection rebuilt in
exactly one place — `refreshEditorSource()` in `website/js/main.js` — and that
rebuild was **gated** on `map.getLayer('editor-poi-circles')`. During a
basemap/preset style swap (custom layers dropped + re-added) or an early-boot
race, the layer is briefly absent, so the right side kept a stale/empty runtime
while the left, reading the array, stayed current → "left but not right."

Fix: removed the `&& map.getLayer('editor-poi-circles')` condition so the right
runtime is **always** re-registered from `editorFeatureCollection()` on every
mutation. Safe because `registerFeatureListLayer` and `applyFeatureListFilters`
already guard every `map.getLayer()` access (skip the missing layer's filter,
build state + render from data regardless). `editorPois` is now the single source
of truth; the left tab, the ★ Visitor list, and the geometry buckets are all live
projections of it. Verified by observation (Playwright, DOM-level): with
`editor-poi-circles` absent the entire load, a starred + unstarred POI rendered
correctly across all three surfaces and stayed in lockstep through a real ★ row
click (left + Visitor list both gained the newly-starred POI), zero editor
errors. Shipped as build `v51` (bumped `VERSION` in `sw.js` + `#appVersion` in
`index.html`, since `js/main.js` is a cache-first shell asset). Note: the
map-dependent verifiers (`playwright_verify_poi_editor.py` etc.) can't run to
completion in a no-external-tile sandbox — the MapLibre `load` event never fires
— so the changed path was verified directly rather than through those suites.

## Related work

- `../03_event_app/_done/poi_editor_tree_inline_accordion.md` — predecessor (the tree shape this card hoists).
- `../03_event_app/_done/poi_editor_inline_list_and_highlight.md` — predecessor (the ★ axis this card extends).
- `../03_event_app/_done/left_panel_poi_browser.md` — left-rail POI tab; right-side ★ Visitor list is the new parallel surface on the same axis.
- `../03_event_app/_done/right_panel_editor_consistency.md` — the prior right-rail pass.
- `poi_editor_followups.md` — open follow-ups; two S3 review items intersect with this work (notes-trim, Reset-seed-tag-rebind).
- `viewer_polish_followups.md` — residual viewer polish; the open `playwright_verify_right_panel_consistency.py` follow-up there becomes the natural home for the new bucket-tree assertions if a dedicated verifier is wanted.
