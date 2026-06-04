# Editor — one unified edit dock for every right-panel edit

Date: 2026-06-03

TL;DR:
- User: *"all edits on the right should use this new singular edit interface…
  if a layer has specific settings it should also be in this edit panel. do
  research and ensure all our use cases are covered. make some mockups that show
  the different types."*
- Converges the right panel on **one** edit surface: a bottom-pinned **edit
  dock** (variant C from `right_sidebar_compare.html`) that appears only while a
  feature is selected. Replaces the per-row accordion (`buildInlineEditor`) AND
  the separate layer-editor drawer (`#layerEditor` opacity/color/width/size).
- Layer-specific settings move **into** the dock (no separate drawer): brand-logo
  **Size**, building **Public/Private + footprint drag**, cemetery **roster +
  source/license**, callout **placement**, line/polygon **vertices**, plus the
  per-feature **★ surface** and **visibility** toggles that today are scattered
  row controls.

#aop #04_event_app #editor #right_panel #unified_dock #mvp

-----

## Research — the edit surface today (cited inventory)

Two read-only audits (code + brain), 2026-06-03. Sources: `website/js/main.js`
(`buildInlineEditor` ~3913–4076; FEATURE_LIST_LAYERS specs ~2238–2560; layer
drawer ~4983–5013; `aop_positioned_features_v1` ~2579–2683), and brain cards
`_done/editor_three_buckets_v3c.md`, `editor_v1_editable_layers.md`,
`poi_editor_followups.md`, `opacity_and_multiply_separate.md`, `personas.md`.

Editable/listed layers and their capabilities:

| Layer | Geom/bucket | Editable | Name | Cat | Tag | Notes | ★ | Move | Lock | Dup/Del | Special |
|---|---|---|---|---|---|---|---|---|---|---|---|
| editorPois (drawn) | Point/Line/Poly | yes | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | vertices (deferred) |
| brandLogos | Point | yes | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | **Size** (icon_size) |
| visitorContext | Polygon | yes | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | callout placement |
| buildings | Polygon (derived) | yes | ✓ (building_label) | — | ✓ | ✓ | — | ✓ | ✓ | — | **Public/Private**, footprint drag |
| cemeteries | Polygon (derived) | ref | ✓ | — | — | ✓ | — | — | — | — | **roster + license** |
| trailheads | Point | ref | — | — | — | — | — | — | — | — | read-only |
| eventSchedule | Point | ref | — | — | — | — | — | — | — | — | tag-bound, read-only |

Layer-LEVEL settings that also live on the right today (must find a home):
visibility toggles (legacy `#legacyLayerToggles`), opacity/color/width paint
sliders per `TUNABLE_LAYERS`, preset capture/apply, "Copy all as GeoJSON".
Rule: **opacity and multiply stay separate controls** (`opacity_and_multiply_separate.md`).

## The three archetypes (what the dock must cover)

1. **Drawn feature (full CRUD)** — Point / Line / Polygon. All fields + Move /
   Vertices / Duplicate / Delete.
2. **Curated movable** — brand logo, building, visitor callout. Editable fields +
   Move / Lock; **no Duplicate/Delete**; one special setting each.
3. **Reference / read-only** — trailhead, event POI, cemetery. Same shell, inputs
   locked, provenance shown; visibility + fly (+ copy) only.

## Design — one shell, contents adapt (CONTRACT CONFIRMED 2026-06-03)

`header → tabs (Identify · Edit · Display · Source) → tab body`. Identical
skeleton for every type; only the populated fields/actions change. User chose the
**4-tab** model (keep the Edit tab over a persistent action row), and chose to
fold layer paint into the **Edit tab** ("either same edit tab or a paint tab").

- **Identify** (what it is): Name, Category (drawn only), **Group** = settable
  subgroup (drawn only; fixed+read-only for curated), Tag, Notes, building
  Public/Private status.
- **Edit** (change it + layer paint): the action set — Move · Vertices (line/poly)
  · Duplicate · Copy GeoJSON · Lock · Delete (only those that apply) — under a
  "This feature" group, **plus** the layer's paint (opacity / color / width) under
  a "Layer paint · <layer>" group. Opacity and multiply stay separate per
  `opacity_and_multiply_separate.md`.
- **Display** (how it looks): Visible-on-map, ★ Surface-to-visitors, brand Size
  slider (per-feature appearance).
- **Source** (where it came from): origin, coords, confidence, license, cemetery
  roster. Read-only.
- **Read-only layers** (trailhead, event POI, cemetery): SAME shell, inputs
  locked, "reference" banner, Edit tab disabled; visibility + fly (+ copy) only.

Honors prior rounds: flat tree (no bucket boxes / source dots), dock shows ONLY
when something is selected (no collapsed/empty state), Group is settable.

Mockups: `website/editor_dock_types_compare.html` (7 types) and the state/pattern
reference `website/right_sidebar_compare.html`. Shots:
`brain/output/playwright_editor_dock_types.png`, `playwright_dock_cell_*.png`.

## Application plan (NOT yet done — code is the next pass)

In `website/`:
1. **CSS** (`css/app.css`): port the dock shell from the mockup (header/tabs/
   body/fields/actions/slider/seg/roster/toggle), bottom-pinned in the panel.
2. **`buildEditDock(layerKey, item, spec)`** replaces `buildInlineEditor`: renders
   the tabbed shell, reads spec flags to decide fields/actions, writes via the
   existing `setFeatureProperty` / `savePositionedFeature` / tag store / array
   store — **no new persistence**, reuse `aop_positioned_features_v1` etc.
3. **Selection model**: one selected feature at a time → dock pinned at panel
   bottom; clearing selection (✕ / map-click empty) removes the dock. Replaces
   the per-row accordion injection.
4. **Fold the layer-editor drawer** (`#layerEditor` paint sliders) into the dock's
   Display/Source tabs OR keep layer-level paint at the layer row but route
   per-feature settings through the dock (decision — see Forks).
5. **Keep** the 3-bucket V3c tree, `★` mirroring, single GeoJSON-copy export,
   preset capture, legacy hidden toggles (preset compat).
6. **Verifiers**: update `playwright_verify_poi_editor.py`,
   `playwright_verify_feature_list.py`, `playwright_verify_presets.py` for the new
   selectors; bump `VERSION` (shell-asset).

## Forks / decisions — RESOLVED 2026-06-03

- **Tab model**: 4 tabs — Identify · Edit · Display · Source. (User: "Keep 4 tabs
  (add Edit)".)
- **Layer paint**: folded into the **Edit** tab as a "Layer paint" group. (User:
  "either same edit tab or a paint tab" → chose same edit tab to stay at 4.)
- **Read-only layers**: same dock, fields locked, Edit tab disabled, "reference"
  banner. (Assistant call for a singular interface.)
- **Layer with no per-feature list** (hillshade/contours/landcover style layers):
  OPEN — these have paint but no feature to select. Likely the dock opens in
  "layer mode" (Edit/paint only) when a layer row is picked. Decide during wiring.

## What shipped (CODE, UNCOMMITTED, v30→v31)

Files: `website/js/main.js`, `website/css/app.css`, `website/index.html`,
`website/sw.js`.

- **One dock, every edit.** New `buildEditDock(layerKey, item, spec)` +
  `renderEditDock()` render a single 4-tab dock (Identify · Edit · Display ·
  Source) into a new `#editDock` element pinned to the panel bottom. The per-row
  accordion injection is gone; `buildInlineEditor` is dead (left with a
  deprecation note — safe to delete in cleanup).
- **Single selection across all layers.** New `dockSelection` + `dockActiveTab`;
  `selectFeatureForDock` / `clearDockSelection` / `dockSelectionMatches`. The row
  `▸` chevron (`toggleFeatureEditor` → `selectFeatureForDock`), map-click reveal
  (`map.on('click', editor-poi…)`), duplicate, and delete all drive the dock.
  `✕` or re-clicking the row clears it → dock hides (two-state: visible or not).
- **Layer paint folded into the Edit tab.** `renderTuneControls(config, target)`
  generalized to take a target; the dock's Edit tab renders the layer's
  `TUNABLE_LAYERS` paint into a `.dock-paint` container wired to the existing
  `handleTuneInput`. Verified live: drawn POIs show 10 paint rows, visitor
  context 7, brand logos 1 — the real sliders, applying to the map.
- **Panel restructured** to a flex column (`.panel` overflow hidden + flex; new
  `.panel-body` flex:1 scroll region) so the tree scrolls and the dock pins to
  the bottom. Collapsed-FAB hides the dock.
- **Field/action adaptation is spec-driven** (unchanged flags): Category +
  Duplicate/Delete only for `editorPois`; Tag for `taggable`; Size for
  `sizeEditable` (brand logos, Display tab); Move/Lock for `onMove`; ★ for
  `highlightable`. Group + building Public/Private render **read-only** (cross-
  layer migration / status-flip need new backend — deferred, see below).

**Verified by observation** (served :8000, headless Chromium, 0 console errors):
selecting a drawn POI opens the dock (title "AOP Pavilion", 4 tabs); Edit tab =
5 actions + "Layer paint · Drawn POIs" sliders; Display = Visible + ★ toggles;
`✕` re-hides. Brand logo → Size + Move/Lock/Copy, no Category/Delete. Visitor
context (Polygon) → Move/Lock/Copy, 7 paint rows. Shots:
`brain/output/playwright_app_dock_selected.png`, `…_edit_tab.png`,
`…_identify_tab.png`.

## Deferred (followups)

- **Settable Group** (move a feature between source groups) — needs cross-layer
  migration; currently read-only context.
- **Building Public/Private flip** — has cascading effects (search gating,
  structure-box layer, group membership); read-only for now.
- **Vertex / reshape editing** for lines/polygons — still not built (pre-existing
  deferral); the dock omits the button rather than show a dead one.
- **Read-only reference dock** for trailheads / event-schedule POIs — they aren't
  `inlineEditor` layers so they keep row-level fly/copy and don't open a dock
  ("all *edits* use the dock"; read-only things aren't edits).
- **Delete dead `buildInlineEditor`** (~160 lines) and consider retiring the
  `#layerEditor` paint drawer now that feature-layer paint lives in the dock
  (drawer still serves style-only layers: hillshade/contours/landcover).

## Status

SHIPPED, UNCOMMITTED (v30→v31). Verified headless, 0 console errors. **Owed:**
on-device feel; commit + the v31 bump are the user's git gate.
