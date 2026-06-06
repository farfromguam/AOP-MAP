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

> **Add-controls mockups 2026-06-05:** `website/add_any_type_compare.html` + 4 takes
> (`add_any_type_v{1_pills,2_icons,3_picker,4_addrow}.html`) for moving the layer-row
> `+` INTO the inline group edit area beside the eye + lock, and splitting it into
> **+ POI · + Line · + Polygon** (add any geometry to any layer). On the current panel
> base; every take selects a Polygon layer (Park buildings) to show point/line add.
> Verified headless (0 console errors); shots `brain/output/playwright_add_any_type_*.png`.
>
> **WIRED 2026-06-05 (v42→v43): user picked V2 ("go with v2, we don't need the ADD") →
> shipped into `js/panel.js`.** The `+` is off the row; the group control row now shows
> eye + lock + a divider + three icon buttons (pin/line/polygon, each a small `+` badge,
> no "ADD" caption). `nodeCreateSpec` → `nodeCanCreate`/`makeCreateSpec(node, geomType)` so
> any geometry drops into the node's OWN source; `startCreate(node, geomType)`; rendered via
> a `add` flag on `groupFields`'s controls field. Add is never lock-gated (fresh draw is
> editable). CSS `.add-type`/`.add-divider` in `right_panel.html` + `panel-embed.css`.
> Verified by observation (`/tmp/verify_add_wiring.py`, 17/17, 0 errors): +POI placed a
> POINT and +Line a LINESTRING into the buildings *polygon* layer; pure-visibility layers
> show no icons. Shots `brain/output/playwright_add_wiring_{editarea,buildings}.png`. See the
> 2026-06-05 ADD-ANY-TYPE WIRED entry in `handoff/session_context.md`. Owed: commit + v43 are
> the user's git gate; promote the verifier to `mvp/scripts/` at commit.

> **Refresh 2026-06-05:** `right_sidebar_compare.html` was rebuilt on the CURRENT
> reworked panel (`right_panel.html`/`panel-embed.css`) as base — an iframe grid of
> **4 placement variations** of this one tabbed panel: V1 bottom dock
> (`right_sidebar_v1_dock.html`), V2 full takeover (`_v2_takeover.html`), V3 fixed
> split (`_v3_split.html`), V4 floating sheet (`_v4_sheet.html`, 3-tab — Display
> folded into Edit). All fix the "width when scroll is present" issue with
> `scrollbar-gutter:stable` + edit-panel-outside-the-scroll-region.
>
> **CHOSEN + WIRED 2026-06-05 (v35→v36):** user picked **V2 (full-panel takeover)**
> and added a **Raw** tab + a "what file does this come from?" requirement. Wired
> into the LIVE `js/panel.js` (one renderer for standalone + embed): a selected
> FEATURE opens the takeover (`renderFeatureEditor`, `‹ Layers` back bar) with **5
> tabs** — Identify · Edit · Display · Source · **Raw**; a selected LAYER keeps its
> inline controls (no empty-tab takeover). **Source tab shows the served File**
> (`SOURCE_FILE`/`fileForItem` off `MAP_DATA` urls + feature `_src`), kept distinct
> from the provenance `Source` register. **Raw tab** = read-only full-feature JSON
> (`cleanFeature`) + Copy; re-upload deferred. Fields route to tabs via a `tab` tag
> on each `itemFields` entry. Verified headless (standalone + embed, 0 console
> errors). Owed: on-device feel; commit + v36 are the user's git gate. See the
> 2026-06-05 V2-takeover entry in `handoff/session_context.md`.
>
> **STYLING/TABS FIXED 2026-06-05 (v36→v37):** the v36 wiring emitted the DOM but the
> demo's takeover LAYOUT was never ported — `.feature-editor` was a bare in-flow
> `display:flex` block with no `.fe-body` scroll rule, so in embed it rendered buried
> below the kept sections (cramped ~169px card, tabs low/dead on a small screen). The
> old "tabs don't toggle" report was a layout/reachability problem, NOT `#map`
> occlusion (`elementFromPoint` returns the tab itself). **Final shape (after the
> user's "make the tabs the same overall height" follow-up):** the takeover is an
> **in-flow, compact** editor that drives the panel height and, via
> `.aop-feature-editing` (added by `js/panel.js`), **hides the surrounding chrome**
> (panel header, kept Session-tools/Review sections, save footer) while a feature is
> open so it owns the whole panel. `.fe-top` (back/head/tabs) is `position:sticky`;
> the body **grid-stacks the panes** (`display:grid`, every `.fe-pane` in
> `grid-area:1/1`, inactive `visibility:hidden`) so the body sizes to the TALLEST tab
> and **every tab is the same height — no reflow** on the bottom-anchored embed card.
> (An interim absolute-overlay + full-height pin was tried first but superseded: it
> kept height constant only by going full-height, which left big empty space and
> still jumped when not pinned.) Re-verified with **real pointer clicks**
> (`/tmp/verify_takeover_v37.py` — standalone + embed desktop + embed mobile, 21/21
> ×3, 0 console errors; panel height identical on all 5 tabs). Files: `panel-embed.css`
> · `right_panel.html` · `js/panel.js` · `sw.js` · `index.html`.
>
> **IDENTIFY FIELDS 2026-06-05 (v37→v38):** added a **Tag** field to the Identify tab
> (`itemFields`: `{kind:'text', prop:'tag'}`, after Description) and made **Description a
> textarea** (`multiline:true` → `renderTextField` emits `<textarea rows=3>`; textarea CSS
> `resize:vertical; min-height:64px`). `tag` persists/bakes as a normal feature prop.
> Verified (`/tmp/verify_tag_desc.py`): embed + standalone, fields present + editable +
> persist, equal-height tabs intact, 0 console errors.
>
> **EVENT-SCHEDULE TAG BRIDGE WIRED 2026-06-05 (v39→v40):** the Tag field now drives the
> live event-schedule resolver. `main.js` exposes `AOP_HOST_SET_TAG(layerKey,props,tag)`
> (mirrors `AOP_HOST_SET_HIGHLIGHT`): resolves the feature by idField, mirrors `props.tag`
> onto the host feature, routes through the existing `setFeatureTag` (store +
> `rebuildTagLookup` + `rebuildEventScheduleData`). `rebuildTagLookup` now ALSO reads each
> feature's own `props.tag` so a BAKED tag resolves on load (the localStorage store still
> overrides). Panel `commitChange` → `pushTagToHost` (reuses the ★ node→host map).
> Verified by observation (`/tmp/verify_tag_bridge3.py`): tagging building 665 Ellis Cove
> Road `#pavilion` via the panel **moves the live anchor to that building's centroid**;
> clearing unbinds; #pavilion still seeds on fresh load (no regression); 0 console errors.
> Gotcha: `#registration`/`#pavillion` are `alias_of:#pavilion` — bind the BASE tag. Closes
> the event-schedule tag-bridge follow-up.
>
> **DATA-MATURITY TIERS (gold/silver) WIRED 2026-06-05 (v41→v42):** the panel now
> groups the tree by **maturity**, not only provenance. New **Gold data** +
> **Silver — pending review** sections sit at the top (above Source/Derived/External
> reference/Map editor/User submitted); each editable group row shows a **maturity
> chip** and the feature **Source tab** shows the served **File + Tier · locked**.
> Gold = `aop_trail_network.geojson` (the only gold today); silver = visitor
> callouts (pending text review), park buildings, and `publish.geojson`. The tier
> lives in each served file's `_meta` (`maturity`/`group`/`locked`), stamped by new
> **`mvp/scripts/stamp_maturity.py`** (runs LAST; `rebake_canonical.py` now carries
> `_meta` forward so a re-bake won't drop it). Lock/unlock + add-new-into-the-file
> already existed (`nodeCreateSpec` synthesizes a draw spec for any single-geometry
> listable layer; the lock gates *existing* features, never new draws), so "gold is
> locked, unlock to edit, but you can always add items" worked out of the box. Full
> contract: `brain/research/data_maturity_tiers.md`. Files: `js/panel.js` ·
> `css/panel-embed.css` · `right_panel.html` · `website/data/*` (re-stamped) ·
> `_schema.json` · `sw.js`/`index.html` (v42). Verified by observation
> (`/tmp/verify_maturity.py`, 23/23 ×2 surfaces, 0 console errors; shots
> `brain/output/playwright_maturity_{tree,standalone,embed}.png`). **Deferred:**
> the legacy-key strip (gated on the index→panel swap); physical file renames.
> Owed: on-device feel; commit + the v42 bump are the user's git gate.

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
