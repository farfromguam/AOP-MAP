# POI editor — inline list + highlight flag

Date: 2026-05-25

TL;DR:
- Drawn-POI feature list moved out of the layer-editor drawer and into the
  Map editor section, directly below the category dropdown + Place/Draw/Trace
  buttons. One canonical home for the list.
- Each editor POI row carries a new `★/☆` highlight toggle. Only highlighted
  POIs surface in the left-rail POI tab (`Drawn POIs` group). Default off,
  so scratch geometry stays out of the visitor browser.
- Other consumers of the feature-list primitive (buildings, cemeteries,
  visitor-context, brand logos) are unchanged — their list stays in the
  drawer.

#aop #03_event_app #editor #poi #feature-list #left-rail

-----

## Source

- User direction (2026-05-25): *"review our poi editor. we have the categories we need teh items to display in a list below. each item in that list should be toggleable and have an attribute to show up in the poi list on the left. so like a highlight attribute"*
- Decision passes (same session):
  - List placement: **one location** — under the categories in the Map editor section. Drawer no longer carries the list for editor POIs.
  - Highlight scope: **left-rail POI tab only**. Map paint is unaffected; visibility stays orthogonal to highlight.
- Predecessors:
  - `../02_edit/_done/poi_editor_v2.md` — the shared feature-list primitive this builds on.
  - `left_panel_poi_browser.md` — the left-rail POI tab whose `drawn_pois` group now reads through the highlight gate.

## What this card builds

1. **Inline editor-POI list**
   - New `<div id="editorPoiList">` inside `<section data-section="editor">`, after the status line. Renders via the existing feature-list primitive.
   - `renderFeatureList(layerKey)` parametrized through a per-layer target lookup (`FEATURE_LIST_TARGETS`). `editorPois` points at `#editorPoiList`; everything else still renders into the drawer's `#featureList`.
   - `refreshEditorSource()` unconditionally re-renders the editor list (no longer guarded on drawer expansion).
   - Drawer slot in `renderLayerEditor` skipped for any layer with a dedicated target — the editor POI drawer keeps opacity/color/width sliders only.
   - `revealFeatureInPanel` branches: dedicated-target layers expand their containing panel section instead of popping the drawer, then scroll/flash the row in their own home.
   - The two move-mode re-render guards (`cancelMoveMode`, `enterMoveMode`) now use `shouldRenderFeatureList(layerKey)` so editor POI rows refresh whether or not the drawer happens to be expanded.

2. **Highlight attribute**
   - New spec flag `highlightable: true` on the editorPois entry in `FEATURE_LIST_LAYERS`.
   - Row builder appends a `.feature-highlight` button between the visibility checkbox and the name when the spec opts in. `★` (on) / `☆` (off), `aria-pressed` mirrors state.
   - `.feature-row.has-highlight` widens the row grid to make room for the extra control.
   - `toggleFeatureHighlight(layerKey, featureId)` mutates `feature.properties.highlight`, then calls `saveEditorPois()` + `refreshEditorSource()` (so the flag persists in `aop_editor_pois_v1` and the list re-renders) plus `renderPoiTabIfActive()` (so the left-rail browser updates if it's the active tab).
   - Heading line for highlightable layers shows `N of M visible · K ★ to visitors` so the curation count is glanceable.

3. **Left-rail filter**
   - `buildPoiGroups()` `drawn_pois` block now skips POIs whose `properties.highlight !== true`. The `drawn_pois` group hides itself when empty, as it already did.

## State

- **Highlight flag** — `feature.properties.highlight` on each drawn POI. Lives in the same `aop_editor_pois_v1` localStorage payload as the rest of the POI; travels with the feature through `Export GeoJSON` and any re-import.
- **Per-feature visibility** — unchanged, still `aop_feature_visibility_v1`.
- **Tag bindings** — unchanged, still `aop_feature_tags_v1`.

The three axes are independent: a POI can be visible-and-highlighted, visible-and-not-highlighted, hidden-and-highlighted (still in the left rail), or hidden-and-not-highlighted.

## Files touched

- `website/index.html`
  - CSS for `#editorPoiList`, `.feature-row.has-highlight`, `.feature-row .feature-highlight`.
  - HTML: `<div id="editorPoiList" class="feature-list" hidden>` inside the Map editor section.
  - JS: `FEATURE_LIST_TARGETS` + `featureListTargetFor` + `shouldRenderFeatureList` helpers; `renderFeatureList(layerKey)` retargeted via `target`; `revealFeatureInPanel` dedicated-target branch; drawer slot guard; `toggleFeatureHighlight`; row builder star button + long-press exclusion; `editorPois` spec gains `highlightable: true`; `buildPoiGroups` `drawn_pois` highlight gate.

## Acceptance

- [x] Map editor section shows the drawn-POI list directly under the draw buttons.
- [x] Layer drawer for `Drawn POIs` no longer carries the feature list (paint sliders still present).
- [x] A fresh POI starts unhighlighted, does **not** appear in the left-rail `Drawn POIs` group, and stays drawn on the map.
- [x] Clicking ★ surfaces the POI in the left rail; unclicking ★ removes it. Survives reload.
- [x] Existing per-row controls (visibility checkbox, fly, copy, tag input, move) still function in the inline list.
- [x] Buildings, cemeteries, visitor-context, brand-logos drawer lists unchanged.
- [x] Map-click reveal on an editor POI opens the Map editor section if collapsed, scrolls the row in, and flashes it (drawer is no longer hijacked for this layer).
- [x] `playwright_verify_poi_editor.py` passes (0 console errors).
- [x] `playwright_verify_feature_list.py` passes (0 console errors, 0 failed checks). Verifier updated: `feature_list_summary(page, "editorPois")` now reads from `#editorPoiList`; `open_layer_editor(page, "editorPois")` expands the Map editor section instead of the drawer; the reveal assertion checks the Map editor section's collapsed state instead of `expandedTuneKey`.
- [x] `playwright_verify_presets.py` passes (0 non-tile console errors).

## Verification

```text
python3 -u mvp/scripts/playwright_verify_poi_editor.py    → RESULT PASS
python3 -u mvp/scripts/playwright_verify_feature_list.py  → RESULT PASS
python3 -u mvp/scripts/playwright_verify_presets.py       → RESULT PASS
```

## Caught during implementation

- **`renderFeatureList` name-shadow bug.** Renaming the function's drawer-element `featureListEl` to the parameter-friendly `target` collided with an inner `const target = findFeatureById(...)` in the move-banner block. Result: the banner was being appended to a feature object rather than the DOM, throwing silently, and no banner ever rendered. Fixed by renaming the inner var to `moveItem`. Caught by the feature-list verifier's `move banner visible after ✋ click` assertion.

## Open follow-ups

- Dedicated assertion in `playwright_verify_poi_editor.py` for the ★ toggle: draw a POI, confirm absent from `#poiList`, click ★, confirm present, reload, still present, click ★ again, absent.
- The `★ to visitors` count in the heading is informational; consider promoting it to a small chip if the curated count becomes a thing users want to scan.
- Decide whether the inline list should auto-scroll to a freshly-drawn POI (today it just appears in the list; you have to find it). Defer until somebody complains.

## Related work

- `../02_edit/_done/poi_editor_v2.md` — predecessor (shared feature-list primitive).
- `left_panel_poi_browser.md` — left-rail POI tab; the highlight flag is the gate that determines whether a drawn POI surfaces there.
- `left_sidebar_content_audit.md` — owner of the visitor-facing copy in the left rail. Highlighted POIs join the same surface those edits govern.
