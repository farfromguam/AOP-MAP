# Editor — three buckets, per-bucket create (V3c)

Date: 2026-05-28

TL;DR:
- Supersedes `_done/editor_unified_tree.md` (shipped earlier today). That pass
  collapsed POI + Map editor into one section with five buckets (Point / Line /
  Polygon / Image / Callout) above a 5-toggle layer strip. This pass collapses
  the buckets to **three** (Point / Line / Polygon), deletes the strip, and
  pushes the create affordance into each bucket.
- The five-toggle strip (`showEventSchedule`, `showTrailheads`,
  `showVisitorContext`, `showBrandLogos`, `showEditorPois`) had two problems:
  it duplicated three sub-group bulk-checkboxes outright, and it framed
  "Image" and "Callout" as top-level kinds when they are render styles on
  Points and Polygons.
- Locked direction from the V3c mockup: each bucket head carries a green `+`.
  Click it to open an **inline create row** under the head — bucket-scoped
  category select + matching primary action (Place / Draw / Trace). Footer
  shrinks to Export / Clear / status / help.
- Event-schedule POIs are regular drawn POIs — they render in the Drawn
  sub-group under Point with their `#tag` visible. No separate group.

#aop #04_event_app #editor #right_panel #tree #create #v3c

-----

## Source

- User direction (2026-05-27, after `editor_unified_tree.md` shipped earlier
  the same day): *"there is some redundancy in our right sidebar. map editor
  has old groups that toggle. Event schedule POIs / Publishable trailheads /
  Visitor context callouts / Brand logos / Drawn POIs — all these should be
  toggled by the items below. in point line polygon image or callout sections.
  review this and report back this is not the only issue."*
- Clarifications on the same turn:
  - *"go ahead and fix these things. we are trying to make a editor where
    things live in one place. point line and polygon are the new thing."*
  - *"event schedule poi are just regular pois."*
  - *"I am thinking each section needs its own create buttons."*
  - Variant pick: **V3** for the tree shape (sub-grouped buckets, Drawn open,
    reference sub-groups collapsed). Variant pick: **V3c** for the create
    flow (bucket-head `+` expands inline create row; footer shrinks).

## Predecessors

- `_done/editor_unified_tree.md` — the unified-tree pass this revises. Five
  buckets, 5-toggle strip, footer-owned create row.
- `_done/poi_editor_tree_inline_accordion.md` — the kind-grouped tree shape
  for drawn POIs (the leaf accordion stays untouched).
- `_done/poi_editor_inline_list_and_highlight.md` — the `★` curation axis.
- `_done/left_panel_poi_browser.md` — left-rail POI tab; the `★ Visitor list`
  group keeps its parallel surface on the same axis.

## Mockups (delivered before this card)

- `website/editor_unified_compare.html` — first-round compare (V1 sub-grouped /
  V2 chips / V3 focused / V4 dots). User picked **V3**.
- `website/editor_unified_v3_create_compare.html` — second-round compare for
  the create-flow placement (V3a bucket-head + / V3b sub-group + / V3c inline
  create). User picked **V3c**.
- Source files: `website/editor_unified_v1_subgroups.html`,
  `..._v2_chips.html`, `..._v3_focused.html`, `..._v4_dots.html`,
  `..._v3a_buckethead.html`, `..._v3b_subgrouphead.html`,
  `..._v3c_inline.html`. Throwaway mockups; retire after this card lands per
  the existing pattern (`misc_4` "Mockup Cleanup" routes to
  `viewer_polish_followups.md`).

## Decisions (locked)

1. **Three buckets, not five.** Image and Callout are render styles, not
   geometry kinds. Brand logos are Points that render as icon-images — they
   live under Point. Visitor context callouts are Polygons that render with
   label boxes — they live under Polygon.
2. **Sub-groups by source inside each bucket.**
   - Point: Drawn POIs (incl. event-schedule POIs by tag) · Trailheads (read-
     only) · Brand logos.
   - Line: Drawn POIs.
   - Polygon: Drawn POIs · Visitor context.
3. **Default collapse: Drawn open, reference sub-groups collapsed.** Counts
   visible on collapsed heads. This is the V3 "focused" opinion.
4. **Sub-group head bulk-checkbox is the layer-level on/off.** The 5-toggle
   strip is gone from the visible UI. The underlying `showEventSchedule` /
   `showTrailheads` / `showVisitorContext` / `showBrandLogos` /
   `showEditorPois` inputs stay in the DOM as **hidden** form elements (to
   keep the existing JS wiring — paint drawers, preset capture/apply, MapLibre
   layer visibility — intact). The sub-group bulk-checkbox is the visible
   mirror; two-way bind in both directions. Event-schedule has no dedicated
   sub-group, so `showEventSchedule` is mirrored to the Drawn-sub-group's
   bulk only when every event-schedule row's visibility matches the layer
   state (otherwise the bulk goes indeterminate).
5. **Bucket-head `+` opens an inline create row.** One `+` button per Point /
   Line / Polygon bucket head (Visitor list bucket has no `+`). Click toggles
   the row open; the row contains: glyph + label ("Draw a polygon"), category
   `<select>`, primary action button (Place POI / Draw footprint / Trace
   line), cancel `✕`, helper text. Active state echoes on the `+` (rust fill)
   and the primary button label ("Drawing… (Esc)"). Esc cancels.
6. **One global category list for V3c.** Per-bucket category customization
   (Polygon-only categories, etc.) is a follow-up. For this pass each
   bucket's category select uses the same option list as today's footer
   select, scoped per bucket so each bucket remembers its last pick across
   re-opens.
7. **Footer keeps Export / Clear / status / help.** No draw buttons, no
   category select.
8. **Event-schedule POIs render alongside drawn POIs in the Drawn sub-group
   under Point.** Data file (`website/data/aop_event_schedule.json`) is
   untouched in this pass. The Drawn sub-group body renders two stacked
   feature-list slots: one for `editorPois` Point rows, one for
   `eventSchedule` rows. Their counts add into the sub-group head count.
   Migrating event-schedule POIs into the `editorPois` store is a deferred
   follow-up (open follow-ups below).
9. **Trailheads register a FEATURE_LIST_LAYERS runtime.** Today `trailheads`
   has a spec at `index.html:2419` but `registerFeatureListLayer('trailheads',
   ...)` is never called. The publish-data fetch path adds one call so the
   sub-group can render read-only rows (no `★`, no `▸` accordion, no delete).

## Out of scope

- **Event-schedule POI data migration.** Today event-schedule anchors come
  from `aop_event_schedule.json` via `rebuildEventScheduleData`. Moving them
  into `aop_editor_pois_v1` proper is the natural next step but is its own
  card — touches the schedule resolver, the seed file, and the export flow.
  Tracked under follow-ups.
- **`activityHotspots` / `syntheticActivity` orphan editors.** They're
  registered as `FEATURE_LIST_LAYERS` but the Publishable section that hosted
  them is gone — flagged in the review that preceded this card. Re-homing
  them belongs in `viewer_polish_followups.md`, not this card.
- **Per-bucket category lists.** Categories are the same global list for
  every bucket in this pass.
- **Per-layer accordion editor for `brandLogos` / `visitorContext`.** Same
  scope as the prior card: row controls stay inline (size, ★, ✋, 🎯); no
  chevron accordion.
- **Reshape / re-vertex** for polygons and lines — already deferred.

## Shape

```
<section data-section="editor">
  Header: Map editor                              ⧉  ▾

  ★ Visitor list (live mirror of every highlighted feature)

  ● Point          ☑  9/9 · 1★            + ← bucket-head create button
  ──────────────────────────────────────
    ▾ ● Drawn POIs        5/5 · 1★       (default open)
        Pavilion #pavilion          ▸ 🎯 ✋
        Registration #registration  ▸ 🎯 ✋
        … (event-schedule rows merge in by tag)
    ▸ ● Trailheads        2/2           (default collapsed)
    ▸ ● Brand logos       2/2 · 1★      (default collapsed)

  ╱ Line           ☑  1/1                 +
    ▾ ● Drawn POIs        1/1
        North loop trace            ▸ 🎯 ✋

  ▭ Polygon        ☑  3/3 · 1★            + ← active
  ──────────────────────────────────────
    ┌ Draw a polygon                              ✕ ← inline create row,
    │ Category [ Big tent ▾ ]   [ Drawing… (Esc) ] (open while + is active)
    │ Click corners; Enter to finish, Esc to cancel.
    └
    ▾ ● Drawn POIs        1/1
        Big tent footprint          ▸ 🎯 ✋
    ▸ ● Visitor context   2/2 · 1★

  Footer:
    Export GeoJSON · Clear all
    0 POIs, 0 footprints, 0 traces. (helper prose)
</section>
```

## Files touched

`website/index.html`:

- **HTML**
  - Delete `.editor-layer-strip` block (currently `:826–832`). Five `<input
    type="checkbox" id="show…">` elements move into a single hidden form
    block (`<div hidden aria-hidden="true" id="legacyLayerToggles">…</div>`)
    placed at the bottom of `data-section="editor"` so element-id lookups
    keep working.
  - `<div id="editorTree" class="editor-tree">` stays; renderer rebuilt below.
  - `.editor-create-footer`: delete `#poiCategory`, `#placePoiBtn`,
    `#drawFootprintBtn`, `#traceLineBtn`. Keep `#exportPoiBtn`, `#clearPoiBtn`,
    `#poiStatus`, the help paragraph. Trim help text slightly: drop the
    "pick category then place / draw / trace" sentence (now per-bucket) and
    keep the `#pavilion` seed + Export-to-bake workflow lines.

- **CSS**
  - New: `.editor-bucket-head .add-btn`, `.editor-bucket-head .add-btn.active`,
    `.editor-bucket-body .editor-create-inline`,
    `.editor-create-inline .label-row`,
    `.editor-create-inline .control-row`,
    `.editor-create-inline .start-btn`,
    `.editor-create-inline .cancel`.
  - New: `.editor-subgroup`, `.editor-subgroup-head`, `.editor-subgroup-body`,
    `.editor-subgroup-head .source-dot.{drawn,trailhead,brand,visitor}`,
    `.editor-subgroup.collapsed …`. Source dots use the same colors as the
    V3c mockup (rust / blue / gold / purple).
  - Reuse `.feature-list`, `.feature-list-group`, `.feature-list-rows`,
    `.feature-row`, `.feature-row-editor` unchanged.

- **JS**
  - **`EDITOR_BUCKETS` reshape (5 → 3 with `sources`):**
    ```
    [
      { id:'point',   label:'Point',   glyph:'●', drawMode:'point',
        sources:[
          { id:'drawn',     label:'Drawn POIs',  defaultOpen:true,
            leaves:[{layerKey:'editorPois',onlyGroupId:'point'},{layerKey:'eventSchedule'}],
            layerToggleId:'showEditorPois' },
          { id:'trailhead', label:'Trailheads',  defaultOpen:false,
            leaves:[{layerKey:'trailheads'}],   layerToggleId:'showTrailheads' },
          { id:'brand',     label:'Brand logos', defaultOpen:false,
            leaves:[{layerKey:'brandLogos'}],   layerToggleId:'showBrandLogos' }
        ] },
      { id:'line',    label:'Line',    glyph:'╱', drawMode:'linestring',
        sources:[ { id:'drawn', label:'Drawn POIs', defaultOpen:true,
            leaves:[{layerKey:'editorPois',onlyGroupId:'linestring'}],
            layerToggleId:'showEditorPois' } ] },
      { id:'polygon', label:'Polygon', glyph:'▭', drawMode:'polygon',
        sources:[
          { id:'drawn',   label:'Drawn POIs',     defaultOpen:true,
            leaves:[{layerKey:'editorPois',onlyGroupId:'polygon'}],
            layerToggleId:'showEditorPois' },
          { id:'visitor', label:'Visitor context', defaultOpen:false,
            leaves:[{layerKey:'visitorContext'}],
            layerToggleId:'showVisitorContext' }
        ] }
    ];
    ```
    Note: `showEditorPois` is the same layer toggle for all three Drawn
    sub-groups; toggling any one flips the shared layer. `showEventSchedule`
    isn't on the layerToggleId axis — it's a sibling layer also rendered into
    the Point/Drawn sub-group; handled inside the bulk-checkbox logic.
  - **`buildEditorTree()`** iterates buckets → sources → leaves. Each source
    gets `.editor-subgroup` with head (chevron, source-dot, label, count,
    bulk-checkbox) and body (one `.feature-list` slot per leaf, registered
    via `registerFeatureListTarget`). Default-collapse comes from
    `source.defaultOpen === false`. Bucket head adds a `+` button with click
    handler `toggleBucketCreate(bucket)`.
  - **`toggleBucketCreate(bucket)`** opens/closes the inline create row.
    When opening, renders an `.editor-create-inline` div as the first child
    of the bucket body; the row carries category `<select>` (cloned options
    from the legacy `#poiCategory`), primary `<button class="start-btn">`,
    cancel `<button class="cancel">`, helper text. Clicking the primary
    button calls `setDrawMode(bucket.drawMode)` and sets the
    `currentCreateBucket = bucket` so `draw.on('finish')` knows which
    bucket's category to read. Cancel calls `setDrawMode('static')` and
    closes the row.
  - **`draw.on('finish')`** reads `currentCreateBucket?.categorySelect.value`
    instead of the legacy `poiCategory.value`. Falls back to a sensible
    default if no bucket is active (shouldn't happen).
  - **`setDrawMode(mode)`** stops toggling the three retired footer buttons
    and instead toggles `.active` on every bucket's `+` button matching
    `bucket.drawMode === mode`. Labels on the bucket's primary `start-btn`
    flip to "Drawing… (Esc)" while active.
  - **`renderEditorTreeCounts()`** sums per-source counts into the source
    head (`visible/total · N★` or `—`), then sums all sources for the
    bucket head. Sub-group bulk-checkbox uses
    `runtime.state.visibleIds.size === total` for `checked`,
    `0 < visible < total` for `indeterminate`.
  - **Sub-group bulk-checkbox change handler:** flips per-feature visibility
    for every feature in the source's leaves (existing
    `setFeatureVisible(layerKey, id, visible)` path) *and* mirrors to the
    hidden `layerToggleId` checkbox — `getElementById('showTrailheads').checked
    = visible; dispatch change` to drive the MapLibre layer-visibility wiring
    at `index.html:2105–2128`.
  - **Reverse bridge:** when `showTrailheads` (etc.) changes externally
    (preset apply, programmatic restore), update the matching sub-group
    bulk-checkbox state via a small wiring at the top of the editor-section
    init.
  - **Trailheads runtime registration:** in the trailheads load path (find
    where `aop_publishable_trailheads` lands; search for the trailhead
    feature collection), call `registerFeatureListLayer('trailheads',
    trailheadsData)` so the sub-group body has rows to render. Trailheads
    spec already exists at `:2419`; add `highlightable: false` to keep ★
    off, and confirm the row controls are read-only (no `▸` accordion).

`website/data/`: no changes.

`mvp/scripts/playwright_verify_presets.py`:
- Update the right-panel editor-section assertions:
  - `.editor-tree` contains exactly 4 buckets (Visitor list + Point + Line +
    Polygon), not 5.
  - Each Point/Line/Polygon bucket has a `[data-add-bucket="<id>"]` button.
  - Hidden `legacyLayerToggles` form block exists and still hosts the 5
    show-checkbox inputs (so the rest of the verifier's preset assertions
    keep working).

`mvp/scripts/playwright_verify_poi_editor.py`:
- Replace selectors that reached `.editor-bucket[data-bucket="point"]
  .feature-list` with the new sub-group-scoped selector
  `.editor-bucket[data-bucket="point"] .editor-subgroup[data-source="drawn"]
  .feature-list`.
- Add an assertion that the `+` button on Point opens an inline create row
  with a category select.

`mvp/scripts/playwright_verify_feature_list.py`:
- Update visitor-context selectors to the new
  `[data-bucket="polygon"] [data-source="visitor"]` path.
- Update brand-logo selectors to `[data-bucket="point"] [data-source="brand"]`.

`mvp/scripts/playwright_verify_event_schedule.py`:
- The Tag-driven block currently expects event-schedule rows under the Point
  bucket but not nested inside a sub-group. Update to look in the Drawn
  sub-group's second feature-list slot (`[data-bucket="point"]
  [data-source="drawn"] .feature-list:nth-of-type(2)`).

## State

- **No new localStorage keys.** Highlight, visibility, tags persist where
  they already do.
- **Sub-group open/closed state** is in-memory only for V3c (matches the
  V3 mockup default). Persisting per-bucket sub-group state is a follow-up
  if users ask for it.
- **Per-bucket `currentCreateBucket`** lives in JS only; cancelled by Esc,
  page reload, or another bucket's `+` opening (only one bucket can be
  actively drawing at a time).

## Phasing (suggested implementation order)

The card lands as one shipped pass, but the work is internally phased so an
intermediate save point exists if the session is interrupted:

1. **HTML scaffold.** Move the 5 layer toggles into a hidden form block.
   Delete the visible `.editor-layer-strip`. Trim the footer (remove the
   three draw buttons + category select). Add the `start-btn`/`+` icon
   style block to CSS.
2. **`EDITOR_BUCKETS` reshape + `buildEditorTree` rewrite.** Three buckets,
   sources, leaves. Sub-group head with bulk-checkbox + source-dot + count.
   Default-collapse non-Drawn. Layer-toggle two-way bridge.
3. **Trailheads runtime registration.** Add the
   `registerFeatureListLayer('trailheads', ...)` call.
4. **Bucket-head `+` + inline create row + per-bucket category state.**
   `toggleBucketCreate`, `setDrawMode` updates, `draw.on('finish')` reads
   bucket category.
5. **Verifier updates.** Re-run the five Playwright verifiers; expect the
   pre-existing trail-lane / publishable-section failures to remain (they're
   routed in `viewer_polish_followups.md`).

## Verification (2026-05-28 — shipped)

Observed on `http://localhost:8001/` with the relevant Playwright verifiers
re-run after each phase landed:

- `playwright_verify_poi_editor.py` — **PASS** (all 50+ assertions; the
  rewritten Point / Polygon / Line + clicks, inline create row open/close,
  per-bucket category select, and the Line/Drawn sub-group bulk → hidden
  `#showEditorPois` bridge all work end-to-end). Screenshot bank refreshed.
- `playwright_verify_session_tools.py` — **PASS** (Reset clears
  viewer-owned localStorage and re-seeds the pavilion, no console errors).
- `playwright_verify_synthetic_activity.py` — **PASS**.
- `playwright_verify_presets.py` — **PASS** on the new editor-tree
  assertions (buckets = visitor-list + point + line + polygon; Point sources
  = drawn + trailhead + brand; Polygon sources = drawn + visitor). 3 fails
  remain, **all pre-existing** and routed to `viewer_polish_followups.md`:
  (a) `visitor context lives with publishable map layers` — the `publishable`
  section was retired before this card; (b) `source/reference inputs live
  under Source layers` — showOsmTracks/showSfwda moved to External reference
  before this card; (c) `left controls do not overlap panel on narrow
  screens` — the same 4 px mobile-overlap boundary documented in
  `_done/editor_unified_tree.md`.
- `playwright_verify_feature_list.py` — **PASS** on the
  cemeteries / buildings / visitor-context / brand-logo rows. 3 fails
  remain, **all pre-existing** on the retired `data-section="publishable"`
  surface (Export button + visitor-context override payload +
  visitor-context-fill paint export). Routed to
  `viewer_polish_followups.md`.
- `playwright_verify_event_schedule.py` — **PASS** on the tag-driven /
  clock-times / search blocks. 6 trail-lane fallback failures remain,
  **all pre-existing** per `session_context.md` (already routed to
  `viewer_polish_followups.md`).

DOM snapshot confirms: 4 editor-tree buckets render in order (visitor-list,
point, line, polygon); the 6 expected source sub-groups exist in the right
buckets (`point/drawn`, `point/trailhead`, `point/brand`, `line/drawn`,
`polygon/drawn`, `polygon/visitor`); each Point/Line/Polygon bucket head
carries its own green `+`; clicking Polygon's `+` opens an inline create
row inside the Polygon bucket body with category select + primary action +
cancel; the hidden `#legacyLayerToggles` block keeps all five
`show*` inputs reachable for preset capture/apply.

## Acceptance

- [x] `data-section="editor"` carries no `.editor-layer-strip` block. The 5
  show-checkbox inputs live inside a hidden form block at the bottom of the
  section.
- [x] `.editor-tree` renders 4 buckets: Visitor list, Point, Line, Polygon.
- [x] Each Point / Line / Polygon bucket head shows: chevron + bulk-vis
  checkbox + glyph + label + count + green `+` button.
- [x] Sub-groups: Point has 3 (Drawn / Trailheads / Brand logos); Line has 1
  (Drawn); Polygon has 2 (Drawn / Visitor context).
- [x] Drawn sub-groups are expanded by default; Trailheads / Brand logos /
  Visitor context sub-groups are collapsed by default with counts visible.
- [x] Toggling a sub-group bulk-checkbox flips both per-feature visibility
  *and* the corresponding hidden layer-toggle (`showTrailheads`,
  `showBrandLogos`, `showVisitorContext`, `showEditorPois`).
- [x] Clicking a bucket's `+` opens an inline create row inside that bucket
  body. The row carries a category `<select>`, a primary action button
  matching the bucket's draw mode, and a cancel `✕`. Esc closes the row.
- [x] Clicking the primary button starts Terra Draw in the bucket's mode;
  finishing the draw lands a feature in `editorPois` with the row's selected
  category. The new feature renders in the Drawn sub-group of the matching
  bucket.
- [x] Footer shows only: Export GeoJSON, Clear all, status, help text.
- [x] Event-schedule POIs render in the Point bucket's Drawn sub-group with
  their `#tag` visible on the row.
- [~] Trailheads sub-group registers a runtime, but `publish.geojson` ships
  zero `layer === 'trailheads'` features today (only `park_boundaries` and
  `trail_centerlines`), so the runtime stays unregistered and the sub-group
  head shows `—`. Once trailhead data lands in the publish payload, the
  sub-group renders read-only rows automatically (visibility + fly only;
  no ★, no `▸`).
- [x] `playwright_verify_poi_editor.py`, `playwright_verify_session_tools.py`,
  and `playwright_verify_synthetic_activity.py` PASS.
- [~] `playwright_verify_presets.py`, `playwright_verify_feature_list.py`,
  `playwright_verify_event_schedule.py` PASS on the editor-tree assertions;
  pre-existing failures (mobile-overlap, publishable-section,
  trail-lane fallback) remain as routed in `viewer_polish_followups.md`.

## Open follow-ups (intentionally deferred)

- **Event-schedule POI data migration.** Move anchors from
  `aop_event_schedule.json` into the editorPois store with `tag` properties;
  the schedule resolver looks up by tag rather than coordinates. Touches
  `rebuildEventScheduleData`, the seed file, and the export flow.
- **`activityHotspots` / `syntheticActivity` re-home.** Both registered as
  `FEATURE_LIST_LAYERS` but no UI host since Publishable section retired.
  Land in `viewer_polish_followups.md`.
- **Per-bucket category lists.** Polygon ≠ Point category options.
- **Per-bucket sub-group open/closed state persistence.**
- **Per-bucket `+` keyboard shortcut.** `P` / `L` / `G`? Not worth a card
  until users ask.
- **Trailheads ★ axis.** Trailheads are arguably curation-worthy; today they
  ship `highlightable: false`. Land if the visitor browser asks for them.

## Related work

- `_done/editor_unified_tree.md` — direct predecessor; this card revises it.
- `_done/poi_editor_tree_inline_accordion.md` — leaf accordion shape (untouched).
- `_done/poi_editor_inline_list_and_highlight.md` — ★ axis (extended in the
  prior card, not this one).
- `poi_editor_followups.md` — drawn-POI follow-ups; some intersect.
- `viewer_polish_followups.md` — orphan editors + verifier residue.
