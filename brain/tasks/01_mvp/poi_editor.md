# POI Editor

Give the viewer the ability to draw point features -- pavilions, buildings, restrooms, parking, staging areas, gates, landmarks, hazards -- directly on the map. The viewer is the editor: editing is a mode added to `website/index.html`, not a separate page or app.

This is the first editing surface in the web viewer. Until now the viewer was read-only over exported `publish.geojson`. This card adds drawing without disturbing that read path.

#aop #tasks #mvp #editor #poi #terradraw #maplibre

-----

**Status: DONE (2026-05-21).** Point POIs and polygon footprints both draw,
label, persist, and export in the viewer. PostGIS write-back and select/move
remain follow-ups (see below). Outcome section records what shipped.

## Source

- `../../northstar/map_northstar.md` -- "QGIS is the cartography and editing surface" / "Website V2 is submission and moderation". This card moves a slice of editing into the web viewer ahead of the full V2 build.
- `aop_south_pittsburg_map_build_card.md` -- stage 4 (Website V1) and stage 6 (Website V2).
- User direction (2026-05-21): "the editor is just going to be this with editing features" and "we need to add pavilions and buildings and poi and such".

## Scope

- In: point POIs and polygon footprints with a category, on-map labels, click-to-rename, click-to-delete, browser persistence, GeoJSON export.
- Out: line drawing, vertex move/select on committed features, writing features back to PostGIS, source/confidence/permission metadata per the source register.

## Decisions

### 1. Draw library?

**Decided:** Terra Draw (`terra-draw` 1.30.0 + `terra-draw-maplibre-gl-adapter` 1.4.1), vendored as UMD bundles in `website/vendor/`.

**Why:** Terra Draw is actively maintained, framework-agnostic, and extends cleanly to polygon/line modes for footprints and trails later. The `@watergis/maplibre-gl-terradraw` wrapper was considered (ships a ready toolbar) but rejected: it is an ESM/bundler package and `website/` has no build step. Vendoring the UMD bundles keeps the existing plain-`<script>` pattern and stays offline-safe -- consistent with [[project-offline-requirement]].

### 2. Where do drawn POIs live?

**Decided:** Terra Draw is a pure input device. On `finish`, the placed point is lifted out of Terra Draw into our own `editor-poi` GeoJSON source, tagged with the selected category, and Terra Draw is cleared. The `editor-poi` source owns styling, labels, and popups.

**Why:** Terra Draw's point styling has no text labels and its store is awkward to persist. A parallel source gives full control and a clean offline persistence story.

### 3. Persistence?

**Decided:** `localStorage` (key `aop_editor_pois_v1`), plus an Export button that downloads `aop_editor_pois.geojson`.

**Why:** A static viewer cannot write server-side. localStorage survives reloads and works in the field with no network. Export is the bridge into PostGIS / the brain until a save endpoint exists.

### 4. No limiting code

The category is a dropdown but the chosen value is stored as a free string; nothing rejects an edited/unknown category. The circle-color `match` expression has a default branch so an unknown category still renders. Consistent with [[feedback-no-limiting-code-mvp]].

## Acceptance

- [x] Terra Draw + adapter vendored as UMD; viewer still loads offline.
- [x] "Map editor" panel section: category select, Place POI, Draw footprint, Export GeoJSON, Clear all, count.
- [x] Point mode places categorized POIs; committed POIs render as colored circles with labels.
- [x] Polygon mode draws categorized footprints; committed footprints render as colored fill + outline with a centered label.
- [x] Point and footprint modes are mutually exclusive; Escape exits either.
- [x] Click a POI or footprint to rename or delete it.
- [x] Features persist in localStorage and survive reload.
- [x] "Drawn POIs" toggle hides/shows all five editor layers via `LAYER_TOGGLES`.
- [x] Export writes a valid GeoJSON FeatureCollection (points + polygons).
- [x] Playwright verification script, all checks pass, 0 console errors.

## Verification

- `mvp/scripts/playwright_verify_poi_editor.py` -- 2026-05-21 run: 38/38 checks PASS, 0 console errors. Covers point placement, footprint drawing, persistence, reload, popups, and the layer toggle. Screenshots `brain/output/playwright_poi_*.png`.
- `node --check` on the inline viewer script: syntax OK.

## Outcome

Completed 2026-05-21.

- `website/vendor/terra-draw.umd.js`, `terra-draw-maplibre-gl-adapter.umd.js` -- vendored UMD bundles.
- `website/index.html` -- "Map editor" panel section; `editor-poi` GeoJSON source with five render layers (`editor-poi-fill`, `editor-poi-outline`, `editor-poi-circles`, `editor-poi-labels`, `editor-poi-fill-labels`, geometry-filtered so points and polygons style independently); Terra Draw point + polygon modes wired as input via `setDrawMode`; rename/delete popup for both geometry kinds; localStorage persistence; GeoJSON export. Feature properties: `id`, `layer` (`editor_poi`), `category`, `name`, `created`. Footprints close on the Enter key or by clicking the first corner (Terra Draw polygon mode).
- `mvp/scripts/playwright_verify_poi_editor.py` -- verification script.

## Follow-ups (not blocking)

- Select/move mode for committed features (today: delete + re-draw).
- Write exported features into PostGIS `core` with a source-register row, so drawn POIs and footprints carry source/confidence/permission like every other feature and can flow into `publish.geojson`.
- Make drawn features searchable (the search index is built once at load).
