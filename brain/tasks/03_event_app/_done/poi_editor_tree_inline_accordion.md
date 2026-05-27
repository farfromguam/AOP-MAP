# POI editor — tree + inline accordion CRUD

Date: 2026-05-26

TL;DR:
- Flat drawn-POI list re-shapes into a tree: `Drawn POI` → `POI / Footprint / Line` → named item.
- Each leaf gains an inline accordion editor — name, category (now mutable), tag, ★ visitor surface, ☑ on-map, notes (new field), geometry summary, action row.
- Map-click on a drawn POI retires the MapLibre rename/delete popup and routes into the same panel editor instead.

#aop #03_event_app #editor #poi #crud #feature-list

-----

## Source

- User direction (2026-05-26): *"review the crud for user placed points lines and areas. it needs a re-work. ... nested trees. with edit features at the terminal node."*
- Tree shape locked same session: `Drawn POI > poi | footprint | line > named item`.
- Variant pick: V1 inline accordion (mockup at `website/poi_crud_v1_accordion.html`, compare page at `website/poi_crud_compare.html`).
- Predecessor: `poi_editor_inline_list_and_highlight.md` (the flat inline list this replaces).
- Adjacent: `full_loop_crud_upload_audit.md` — Sprint 03's main thrust. The editor here is the contributor-side surface that later submissions / notes / source-register fields plug into.

## Why the rework

The current CRUD has two thin terminals:

1. The list row (`☑ ★ name #tag 🎯 ✋ ⧉`) — fast actions, no real edit.
2. The MapLibre click popup (`<input> Save | Delete`) — name + delete only.

Neither lets you change category post-create, attach notes, or carry source-register context. As Sprint 03 starts adding event features, submissions, and review state, the editor has to grow. The mockup wave chose inline accordion as the home for that growth.

## What ships in MVP

### Tree shape

- Three groups under editorPois, matched by `feature.geometry.type`:
  - **POI** — `Point` — glyph `●`
  - **Footprint** — `Polygon` — glyph `▭`
  - **Line** — `LineString` — glyph `╱`
- Within each kind, rows sort by name (was: category-then-name on the flat list).
- Group head shows kind glyph, label, and `N / M visible · K ★` count.
- Empty kinds collapse out automatically (already supported by the primitive).

### Inline accordion editor

- New row-trailing chevron `▸ / ▾` opens an editor block below the row, pushing siblings down. One leaf editor open at a time per layer.
- Editor fields:
  - **Name** — text input. Writes `feature.properties.name`.
  - **Category** — `<select>` of the 11 categories. Now mutable post-create. Writes `feature.properties.category`.
  - **Tag** — `#tag` input. Same primitive as the existing `feature-tag` row input — moved into the editor, removed from the row.
  - **★ Surface to visitors** + **☑ Visible on map** — toggle pair. Mirror the row star and visibility checkbox; either surface updates the other.
  - **Notes** — new textarea. Writes `feature.properties.notes`. Persists in the same `aop_editor_pois_v1` localStorage payload and travels with `Export GeoJSON`.
  - **Geometry** — read-only summary line. Points show `lat, lng`; polygons/lines show vertex count.
  - **Actions** — `🎯 Fly`, `✋ Move`, `⎘ Duplicate`, `⧉ Copy GeoJSON`, `Delete`.
- Close `✕` button collapses back to a row.
- Editor block is `<div class="feature-row-editor" data-feature-id="…">` inserted into the same `.feature-list-rows` container so the chevron and the editor share a layout column.

### Row simplification

To avoid the row becoming a control horizon:
- **Removed from row:** `#tag` input (now in editor), `⧉` copy button (now in editor).
- **Kept on row:** `☑` visibility checkbox, `★` highlight, name (click=fly), `🎯` fly button, `✋` move button.
- **Added to row:** `▸ / ▾` chevron at the right end. Click expands/collapses the editor.

### Map-click → panel editor (popup retired)

- `openPoiPopup` deleted. The MapLibre rename/delete popup no longer fires.
- `bindEditorClick` routes the click to: select the leaf, expand the section, open the inline editor for that feature.
- Reveal still flashes the row (existing `revealFeatureInPanel` flow); editor is open by the time the flash starts.

## Files touched

- `website/index.html`
  - CSS: `.feature-row-editor`, `.feature-row-expand`, group-head kind glyph.
  - HTML: Map editor section copy nudge — `Default category for next draw` (today: bare `Feature type`).
  - JS:
    - `FEATURE_LIST_LAYERS.editorPois.groups` → three kind buckets; `inlineEditor: true`.
    - `groupForFeature` and `buildFeatureListState` pass `feature` (not just `props`) to `group.match` so geometry-type matching works.
    - `renderFeatureList` — when `spec.inlineEditor`, render the expand chevron on each row; after the expanded row, render the editor block.
    - `featureListRuntime[layerKey].expandedFeatureId` — new state slot.
    - New helpers: `toggleFeatureEditor`, `setFeatureName`, `setFeatureCategory`, `setFeatureNotes`, `deleteEditorFeature`.
    - `bindEditorClick` calls the new open-editor path instead of `openPoiPopup`.
    - `openPoiPopup` function removed.

- `mvp/scripts/playwright_verify_poi_editor.py`
  - Replace `#poiNameInput / #poiSaveBtn / #poiDeleteBtn` popup assertions with editor-block assertions (`.feature-row-editor input[name="name"]`, the editor's Delete button).
  - Add an assertion: drawn POI sorts under the right kind group (`Polygon → Footprint`, etc.).
  - Add an assertion: category dropdown in the editor changes the category property.

- `mvp/scripts/playwright_verify_feature_list.py`
  - Tag-binding flow: the tag input now lives inside the editor (expand the leaf first, then read/write the tag).

## State

- `aop_editor_pois_v1` — same key. Two new properties on each feature:
  - `properties.notes` — string, optional. Default missing → empty textarea.
  - `properties.category` — already exists, now mutable from the editor.
- `aop_feature_visibility_v1`, `aop_feature_tags_v1` — unchanged.
- No new localStorage keys. No migration needed; absent `notes` reads as empty.

## Acceptance

- [x] Drawing a POI / Footprint / Line lands the feature in its kind group.
- [x] Clicking the chevron on a row expands the editor below it, pushes siblings down, and closes any other open editor (`featureListRuntime[layerKey].expandedFeatureId` enforces "one open per layer").
- [x] Name edit persists across reload.
- [x] Category dropdown mutation updates `feature.properties.category` and survives reload.
- [x] Notes textarea persists across reload and exports with the feature in `Export GeoJSON`.
- [~] Star + on-map toggles live on the row only in MVP — re-introducing them inside the editor is deferred (see Open follow-ups). The row controls remain visible directly above the editor when it's open.
- [x] Clicking a drawn POI on the map opens the panel editor; the legacy MapLibre rename/delete popup retired with `openPoiPopup`.
- [x] Buildings, cemeteries, visitor-context, brand-logos rows in the layer-tuner drawer are unchanged (their `spec.inlineEditor` is unset, so they keep the row-level tag input + `⧉` copy button).
- [x] `playwright_verify_poi_editor.py` passes — 56 / 0, including new assertions for the inline editor (`legacy popup retired`, `inline editor block rendered`, `editor exposes name / category / notes inputs`, `POI deleted via inline editor`, `footprint deleted via inline editor`).
- [x] `playwright_verify_feature_list.py` passes — POI `⧉ Copy GeoJSON` test rewritten to expand the leaf via `toggleFeatureEditor('editorPois', id)` and click the editor's `Copy GeoJSON` action.
- [x] `playwright_verify_presets.py` passes — 0 non-tile console errors.

## Open follow-ups

- Reshape (re-vertex) action for polygons / lines — deferred. Today's mockup has no reshape; Move handles re-positioning.
- Source-register fields (source, confidence, permission, publishable, last-checked) — pluggable into the same editor surface once the Sprint 03 loop lands.
- "Move within tree" (re-categorize as a different kind, e.g. promote a Point to a Polygon) is out of scope — geometry kind stays immutable; category is the editable axis.
- Backlog candidate: bulk select N leaves in a kind group, apply a category change. Not in MVP.
- A "(seeded)" chip next to the geometry chip in the inline editor would surface the `properties.source === 'aop_editor_seed_v1'` flag at the leaf level. Defer until somebody needs to scan it.

## Editor seed + dump-to-GeoJSON (2026-05-26 follow-up landed)

Same session, the user asked for two things on top of the tree work:
- *"can we make some things by default"* — seed defaults for the editor.
- *"we need a dump user generated data to geojson for next clean load"* — a repo-checked seed that survives a Reset viewer.
- *"the 1010 building needs to be moved from building data to db to export to seeded feature"* — retire the building-side #pavilion auto-tag; the seeded POI owns the binding.

### What shipped

- `website/data/aop_editor_seed_pois.geojson` — canonical seed, schema `aop_editor_seed_v1`. First entry: a `Pavilion` Point at the 1010 Ellis Cove centroid (`[-85.7482512, 35.0907264]`), `id=aop_seed_pavilion`, `highlight: true`, `seed_tag: "#pavilion"`. Update workflow documented in the create-row help text: `Export GeoJSON → replace this file with the download → commit`.
- `maybeSeedEditorPois` in `website/index.html`:
  - Gate: fires only when `aop_editor_pois_v1` is absent (`null`). An empty array means the user explicitly cleared; the seed does not bring features back uninvited.
  - Stamps every seeded feature with `properties.source = 'aop_editor_seed_v1'` and `properties.layer = 'editor_poi'`.
  - Reads `seed_tag` per feature and writes it into `aop_feature_tags_v1` under the `editorPois` slice. Strips the same `#tag` off any other layer's slice (one-shot migration: 1010 building → seeded POI). Removes the `seed_tag` property after binding so it doesn't double-write on the next register pass.
  - Calls `saveEditorPois → refreshEditorSource → rebuildTagLookup → rebuildEventScheduleData` so the schedule resolver picks up the new binding without a reload.
- Boot wiring at the end of the editor-section setup: `maybeSeedEditorPois();` (fire-and-forget; async fetch).
- `resetViewerState` calls `maybeSeedEditorPois()` after wiping `VIEWER_OWNED_STORAGE_KEYS`, so Reset viewer re-installs the seed instead of leaving the editor empty.
- The 1010 building's first-ever-load `#pavilion` auto-seed (`maybeSeedFeatureTags`) retired entirely. The `FEATURE_TAG_SEEDED_KEY` constant is gone; the literal `aop_feature_tags_seeded_v1` stays in `VIEWER_OWNED_STORAGE_KEYS` as a string so existing installs still get their sticky flag cleared on Reset.

### Verifier updates

- `playwright_verify_poi_editor.py`: clean slate now writes `[]` to `aop_editor_pois_v1` (key present, empty array) instead of `removeItem`, so the seed loader's fresh-install gate stays closed during the verifier's own draw flow.
- `playwright_verify_feature_list.py`: same `setItem('[]')` swap before the three-test-POI push.
- `playwright_verify_session_tools.py`: post-Reset assertion split into "should-be-gone" keys vs. seed-re-written keys (`aop_editor_pois_v1`, `aop_feature_tags_v1`, and `aop_feature_visibility_v1` come back as the seed lands). New assertions: the re-seeded pavilion's id is `aop_seed_pavilion` and the re-seeded `#pavilion` tag binding lives under `editorPois`.
- `playwright_verify_event_schedule.py`: `reset_tag_storage` now clears `aop_editor_pois_v1` too (re-arms the seed loader on every fresh run). The "Tag-driven location resolution" block now asserts `#pavilion → editorPois/aop_seed_pavilion` (not buildings) and confirms no building row carries the binding. The live re-resolve test moved off DOM tag-input typing and onto `setFeatureTag` calls; `window.setFeatureTag = setFeatureTag` is added to the verifier's window exposure block.

### Tracking

The user asked *"do you track???"* — yes. Two markers ride with every seeded feature:

- `properties.source = 'aop_editor_seed_v1'` — distinguishes seed-installed features from user-drawn ones in `Export GeoJSON` and in any future source-register query.
- The seed file itself carries `schema: 'aop_editor_seed_v1'` at the FeatureCollection level, so the migration story has a version anchor when the schema changes (forward-only per `spinup/viewer_storage_migration.md`).

## Related work

- `poi_editor_inline_list_and_highlight.md` — the flat inline list this card supersedes.
- `right_panel_editor_consistency.md` — same panel chrome the editor lives inside.
- `full_loop_crud_upload_audit.md` — Sprint 03 thrust; this is the contributor-side editor.
- `viewer_polish_carryover.md` — Sprint 02 carryover router.
