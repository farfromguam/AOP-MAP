# Editor — unify override stores, add lock flag, retire trailheads sub-group

Date: 2026-05-29

TL;DR:
- Three changes in one pass, sized for the MVP-editor simplification the user
  asked for. Nothing decorative; each cut is load-bearing.
- (1) Trailheads sub-group **deleted** from the Point bucket. It was read-only
  publish data masquerading as an editor axis, and `publish.geojson` ships
  zero trailheads today so the head read `—`. The publish-trailheads MapLibre
  layer + toggle stay; they're just no longer surfaced inside the editor.
- (2) The two per-layer override stores
  (`aop_visitor_context_overrides_v1`, `aop_brand_logos_overrides_v1`)
  collapsed into **one unified `aop_positioned_features_v1` store** keyed by
  `${layerKey}:${id}`. One spec, one save path, one apply path, one section-
  export slice. `editorPois` geometry continues to live in its own array
  store because the array IS the source of truth.
- (3) New per-feature **`locked` flag** with a 🔒 / 🔓 affordance on every
  movable row. When locked, the ✋ move button is disabled (visually
  greyed) and `enterMoveMode` refuses defensively. ★ and visibility stay
  active. Sets up the user's stated trajectory: "long term they will find
  their home and stay there" — flip one flag and the feature stops being a
  candidate for nudging.

#aop #04_event_app #editor #right_panel #unified_store #lock #mvp_simplify

-----

## Source

- User direction (2026-05-29, this conversation, picking option 3 of the
  three sizes I proposed in my read of the V3c editor's complexity):
  > "those need to be moveable because they are not in the correct space.
  > long term they will find their home and stay there"
- And: *"thinking 3. can you do all this on a worktree and not prompt me
  for anything until the end?"*
- Worktree: `.claude/worktrees/editor-mvp-simplify` on branch
  `worktree-editor-mvp-simplify`.

## Predecessors

- `_done/editor_three_buckets_v3c.md` — V3c shipped 2026-05-28; this card
  cleans up three pieces it left behind.
- `_done/editor_unified_tree.md` — earlier same-day pass; trailheads
  sub-group landed there.
- `_done/poi_editor_tree_inline_accordion.md` — leaf accordion shape
  (untouched).
- `spinup/viewer_storage_migration.md` — forward-only rule for bumping
  `aop_*_v1` localStorage keys and `aop-*-v1` bundle schemas.

## Decisions (locked)

1. **Trailheads leaves the editor tree.** It was read-only publish data and
   the editor's job is user-positioning. The right home for trailhead rows
   is eventually a derived/publish section; until that section exists and
   `publish.geojson` actually ships trailhead features, the row index lives
   nowhere. The publish-trailheads paint drawer + MapLibre layer stay
   intact — `TUNABLE_LAYERS.trailheads` is unchanged.
2. **The `FEATURE_LIST_LAYERS.trailheads` spec is deleted.** Nothing else
   referenced it; the only consumer was the now-removed source entry in
   `EDITOR_BUCKETS[0].sources`.
3. **One unified positioned-features store.** `aop_positioned_features_v1`
   replaces the two per-layer override stores. Entries are sparse patches —
   only the fields the user has touched, merged into the entry on each
   `savePositionedFeature` call. Shape:
   ```
   {
     "visitorContext:Plateau services": {
       geometry: {...}, highlight: true, locked: false, updated: "..."
     },
     "brandLogos:aop_badge": {
       geometry: {...}, icon_size: 0.12, locked: true, updated: "..."
     }
   }
   ```
4. **`editorPois` does not move into the unified store.** Its array IS the
   user's authoring substrate; `aop_editor_pois_v1` continues to hold full
   features. `highlight` and now `locked` ride inside `feature.properties`
   so they travel with GeoJSON export.
5. **Forward-only schema bump.** Export bundle goes from
   `aop-viewer-preset-settings-v2` → `v3`. Section-state schema goes from
   `aop-section-state-v1` → `v2`. Old payloads pasted into Settings are
   refused — per `spinup/viewer_storage_migration.md` we do not write
   migration code.
6. **Retired key constants stay in `VIEWER_OWNED_STORAGE_KEYS` as string
   literals** with a "retired 2026-05-28" comment, so existing installs get
   `aop_visitor_context_overrides_v1` + `aop_brand_logos_overrides_v1`
   cleared on the next Reset viewer.
7. **Lock UI is one button per row, rightmost in the action cluster.**
   🔓 = unlocked (currently editable), 🔒 = locked (parked). Click toggles.
   `aria-pressed` reflects state. When locked: row gets `.is-locked`, the
   ✋ button gets `disabled`, the brand-logo size slider becomes pointer-
   events:none + half-opacity (size is positional in spirit; locking a
   placement should lock its scale too). The long-press path that arms
   move on mobile is skipped entirely on locked rows.
8. **`enterMoveMode` short-circuits on locked features** defensively, so
   any non-row path (map-click reveal, programmatic call) bounces too.
9. **Lock persistence routes by layer.** `editorPois` → `saveEditorPois`
   (the array carries `feature.properties.locked`). `visitorContext` and
   `brandLogos` → `savePositionedFeature(layerKey, feature, { locked })`.
   A small `persistFeatureFlagChange(layerKey, feature, patch)` helper
   does the dispatch; both `toggleFeatureHighlight` and `toggleFeatureLocked`
   go through it. Same pattern collapsed the legacy
   `saveBrandLogoOverride` + `saveVisitorContextOverride` call sites in
   `toggleFeatureHighlight` (was an if/else-if/else block, now one helper
   call).

## Out of scope

- **Per-layer accordion editor for `brandLogos` / `visitorContext`.** Same
  scope decision as V3c: row controls stay inline.
- **Per-bucket category lists.** Categories are still the same global list
  for every bucket.
- **Event-schedule POI data migration.** Still deferred; tracked in V3c
  follow-ups.
- **`activityHotspots` / `syntheticActivity` re-home.** Still routed to
  `viewer_polish_followups.md`.
- **Trailheads' eventual home** — when publish.geojson starts shipping
  trailheads, the row index belongs in a derived/publish section, not the
  editor. That section doesn't exist yet (Publishable was retired before
  V3c). Tracked under follow-ups below.

## Files touched

`website/index.html`:

- **HTML:** No structural changes.
- **JS — storage layer:**
  - Added `POSITIONED_FEATURES_KEY = 'aop_positioned_features_v1'`.
  - Removed `VISITOR_CONTEXT_OVERRIDE_KEY` and `BRAND_LOGOS_OVERRIDE_KEY`
    const declarations; kept the literal strings in
    `VIEWER_OWNED_STORAGE_KEYS` with a retired-key comment.
  - Added `loadPositionedFeatures()`, `positionedFeatureKey()`,
    `positionedFeatureIdFor()`, `savePositionedFeature()`,
    `applyPositionedFeatures()`, `positionedFeaturesSlice(layerKey)`,
    `mergePositionedFeaturesSlice(slice)`.
  - Removed `loadVisitorContextOverrides`, `saveVisitorContextOverride`,
    `applyVisitorContextOverrides`, `loadBrandLogoOverrides`,
    `saveBrandLogoOverride`, `applyBrandLogoOverrides`.
- **JS — `EDITOR_BUCKETS`:** Deleted the `trailhead` source from the Point
  bucket. Now Point has Drawn + Brand only.
- **JS — `FEATURE_LIST_LAYERS`:** Deleted the `trailheads` spec entry.
  Updated `visitorContext.onMove` and `brandLogos.onMove` to call
  `savePositionedFeature(layerKey, feature, { geometry })`. Updated
  `setBrandLogoSize` to call
  `savePositionedFeature('brandLogos', feature, { icon_size })`.
- **JS — toggle helpers:**
  - Replaced the layerKey-switch inside `toggleFeatureHighlight` with a
    single `persistFeatureFlagChange(layerKey, feature, { highlight })`
    call.
  - Added `toggleFeatureLocked(layerKey, featureId)` mirror.
  - Added `persistFeatureFlagChange(layerKey, feature, patch)` dispatch
    helper.
- **JS — `enterMoveMode`:** Added the locked-feature short-circuit at the
  top of the function.
- **JS — row renderer:** Added 🔒 / 🔓 button + `.is-locked` class + the
  `move.disabled` branch when locked + long-press guard when locked. Grid
  template gained one trailing `auto` column so the new button has a slot
  in both the standard and `.has-highlight.has-inline-editor` variants.
- **JS — inline accordion editor** (`renderFeatureRowEditor`): Added the
  🔒 Lock / 🔓 Unlock action button in the editor-actions row; ✋ Move
  becomes `disabled` when locked.
- **JS — section export / import:**
  - `captureRuntimeOverrides` collapses to four slots:
    `positioned_features`, `editor_pois`, `feature_visibility`,
    `feature_tags`. Schema string becomes
    `aop-viewer-preset-settings-v3`.
  - `SECTION_RUNTIME.editor` swaps `visitorContextOverrides` for
    `positionedFeatureLayers: ['visitorContext', 'brandLogos']`.
  - `buildSectionPayload` writes a per-layer positioned-features slice
    keyed by `${layerKey}:`. Schema becomes `aop-section-state-v2`.
  - `applySectionPayload` filters incoming slice keys by allowed
    `layerKey:` prefixes so a paste cannot leak across layers, then calls
    `mergePositionedFeaturesSlice`. Schema check matches `v2`.
  - `applyExportAllPayload` checks for the `v3` schema and writes
    `runtime_overrides.positioned_features` straight to
    `POSITIONED_FEATURES_KEY`.
- **CSS:** Added `.feature-row .feature-lock`,
  `.feature-row .feature-lock.on`, `.feature-row .feature-move:disabled`,
  `.feature-row.is-locked .feature-size-control input` rules. Grew
  `.feature-row` and `.feature-row.has-highlight` grid templates by one
  trailing `auto` column. Grew
  `.feature-row.has-highlight.has-inline-editor` from 6 → 7 columns.

`mvp/scripts/playwright_verify_presets.py`:
- Point sub-group assertion: drop `point/trailhead` from the expected set,
  add an explicit `not in` for trailhead.
- Bundle schema check: `aop-viewer-preset-settings-v3`.

`mvp/scripts/playwright_verify_poi_editor.py`:
- Update the explanatory comment in the Drawn-POIs-toggle section to
  reflect that Point now bundles brand-logos alongside Drawn (no
  trailheads).

`mvp/scripts/playwright_verify_brand_logos.py`:
- `OVERRIDE_KEY` → `aop_positioned_features_v1`.
- Persistence assertions read `store['brandLogos:' + id]` instead of
  `store[id]`. The `aop_badge` move/size persistence test confirms the
  new entry shape.

`mvp/scripts/playwright_verify_feature_list.py`:
- Visitor-context "clean slate" step clears the unified store.
- Move-commit assertion reads
  `override['visitorContext:Monteagle plateau services']`.
- Export-payload section: schema check is `v3`; runtime-overrides bag
  check is `positioned_features`; round-trip key is the prefixed
  `visitorContext:Monteagle plateau services`.
- Section-payload section: schema check is `aop-section-state-v2`;
  source-layers payload asserted to **not** carry `positioned_features`;
  editor payload asserted to carry a `positioned_features` slice with the
  Monteagle prefixed key. Publishable-section assertions retired (the
  section was retired before this card; pre-existing fails routed in
  `viewer_polish_followups.md`).

`mvp/scripts/playwright_verify_session_tools.py`:
- Wipe loop includes `aop_positioned_features_v1`. Retired keys
  (`aop_visitor_context_overrides_v1`, `aop_brand_logos_overrides_v1`)
  stay in the wipe loop so the test still seeds them and asserts they're
  cleared on Reset.
- `SHOULD_BE_GONE` set gains the unified key.

`brain/`: this card, plus `MEMORY.md` updates not needed (per memory
index rule, AOP-specific facts live in the repo brain not user memory).

## State

- **New localStorage key:** `aop_positioned_features_v1`. Wiped on Reset.
- **Retired keys:** `aop_visitor_context_overrides_v1`,
  `aop_brand_logos_overrides_v1`. Existing installs get them cleared on
  next Reset; new installs never write them.
- **Bundle schemas:** `aop-viewer-preset-settings-v3` (was v2),
  `aop-section-state-v2` (was v1). v1/v2 bundles fail import per
  forward-only rule.
- **`feature.properties.locked`:** new boolean on user-positioned features.
  Persists for `editorPois` via the array store; for `visitorContext` and
  `brandLogos` via the unified store, replayed onto the in-memory feature
  by `applyPositionedFeatures`.

## Verification (2026-05-29 — shipped)

Observed on `http://localhost:8001/` (`cd website && python3 -m http.server
8001`) with the relevant Playwright verifiers re-run sequentially after
the changes landed.

**Standalone lock-flag smoke test** (custom script under `/tmp/lock_smoke.py`,
seven assertions on visitorContext + brandLogos + editorPois):

- **PASS** — T1 lock button starts unlocked on a visitor-context row.
- **PASS** — T2 click lock → row class `.is-locked`, ✋ disabled,
  store entry `{ locked: true }` lands under `visitorContext:<name>`.
- **PASS** — T3 click ✋ on a locked row then click the map → coordinates
  unchanged. Locked feature does not move.
- **PASS** — T4 reload restores lock state; `feature.properties.locked`
  is true after page reload.
- **PASS** — T5 click 🔒 again → row unlocked, store entry
  `{ locked: false }`, ✋ re-enabled.
- **PASS** — T6 brand-logos row carries the same lock + move + size +
  star controls.
- **PASS** — T7 seeded editorPois row (`aop_seed_pavilion`) carries the
  lock control.

**Playwright verifiers:**

- `playwright_verify_poi_editor.py` — **PASS** (50+ assertions; no
  failures).
- `playwright_verify_session_tools.py` — **PASS** (Reset clears every
  viewer-owned key including the new unified store; re-seeds pavilion;
  clock + session round-trip clean).
- `playwright_verify_synthetic_activity.py` — **PASS**.
- `playwright_verify_visitor_context.py` — **PASS** (all callout
  assertions including the move flow).
- `playwright_verify_brand_logos.py` — **PASS** on every changed
  assertion (move persistence under `brandLogos:aop_badge`, size
  persistence under the same key, reload restores both). 2 pre-existing
  fails remain on the legacy `#featureList` drawer path — V3c migration
  moved brand-logos rows into the editor tree, so the verifier's
  "feature list opens with 2 rows" assertion against the drawer is
  stale. Routed to `viewer_polish_followups.md` (verifier-rewrite item).
- `playwright_verify_presets.py` — **PASS** on all editor-tree + schema
  v3 assertions. 3 pre-existing fails remain, **all routed in V3c**:
  (a) `visitor context lives with publishable map layers`,
  (b) `source/reference inputs live under Source layers`,
  (c) `left controls do not overlap panel on narrow screens`. Same list
  as 2026-05-28.
- `playwright_verify_feature_list.py` — **PASS** on every changed
  assertion (clean-slate clear of unified store, move-commit under
  prefixed key, v3 export schema, positioned_features bag, Monteagle
  round-trip with prefixed key, section-state v2 schema, editor section
  carries positioned-features slice, source-layers section does NOT
  carry it). 1 pre-existing fail: `publishable: ↑ Export button
  present` — Publishable section retired before V3c. Routed to
  `viewer_polish_followups.md`.
- `playwright_verify_event_schedule.py` — **PASS** on tag-driven /
  clock-times / search blocks. 6 trail-lane fallback fails remain,
  **all pre-existing** per V3c session_context.

No new failures introduced by this card. Pre-existing failures match
the V3c shipped-card list exactly.

## Acceptance

- [x] `EDITOR_BUCKETS[0].sources` (Point) carries Drawn + Brand only —
  no `trailhead` source.
- [x] `FEATURE_LIST_LAYERS.trailheads` spec is gone.
- [x] `aop_positioned_features_v1` is the only store written by
  `savePositionedFeature`. The two retired keys are no longer written by
  any code path.
- [x] Visitor-context move + highlight + brand-logo move + brand-logo
  size + brand-logo highlight all round-trip through the unified store
  and survive reload.
- [x] Lock button renders on every movable row; click toggles state;
  state persists across reload; ✋ disabled when locked; map-click after
  ✋ on a locked row is a no-op.
- [x] Bundle export schema is `aop-viewer-preset-settings-v3`; section
  export schema is `aop-section-state-v2`. v2 / v1 imports fail.
- [x] Reset viewer wipes the new unified key plus the two retired ones.
- [x] All Playwright verifiers PASS on the assertions touched by this
  card. Pre-existing fails from V3c remain (publishable-section,
  trail-lane fallback, mobile-overlap, brand-logos-drawer).

## Open follow-ups (intentionally deferred)

- **Verifier rewrite for brand-logos drawer path.** The two surviving
  fails in `playwright_verify_brand_logos.py` come from the verifier
  reaching for `#featureList` (the layer-tune drawer) instead of the
  editor tree. Rewrite to read rows out of the editor tree. Goes into
  `viewer_polish_followups.md`.
- **Where trailheads actually lives.** When `publish.geojson` starts
  shipping trailheads, the row index belongs in a derived/publish
  section, not the editor. That section doesn't exist yet.
- **Lock UX polish.** No keyboard shortcut (L?). No accent ring on
  locked rows beyond the dim. No "lock all" bulk action. Not worth a
  card until users ask.
- **Event-schedule POI merge** into editorPois. Still deferred per V3c.
- **`activityHotspots` / `syntheticActivity` re-home.** Still deferred.
- **Per-bucket category lists.** Still deferred.

## Related work

- `_done/editor_three_buckets_v3c.md` — direct predecessor; this card
  cleans three pieces of complexity it left behind.
- `_done/poi_editor_tree_inline_accordion.md` — leaf accordion shape
  (untouched, lock added to its action row).
- `viewer_polish_followups.md` — pre-existing verifier residue lives
  here; this card's open-follow-ups inherit that routing.
- `poi_editor_followups.md` — drawn-POI follow-ups; some intersect.
