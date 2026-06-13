# Slice 1 — Viewer core scaffold + first port (presets / zoom / 3D)

TL;DR:
- Stand up the **empty clean core** the rest of the sprint ports into: a new `website/viewer.html` +
  `website/js/viewer_core.js` carrying *only* the MapLibre map, the published-layer style/sources,
  region/park bounds, the bottom ⓘ attribution, and an empty left-control shell.
- Port the **first feature** into it — **map presets + zoom + 3D terrain** (the map basics) — and
  **measure what it actually drags in.** That number is the sprint's calibration: the real
  line-cost-per-feature, and the first test of whether the "5 generations" is sediment we route around
  or load-bearing structure.
- Builds **alongside** `index.html` — the live page is never touched. Verified by observation against the
  old page's behavior.

#aop #sprint #13 #viewer #core #scaffold #presets #slice

-----

## Why this slice first

The clean core has to exist before anything can be ported into it, and the first port has to be the map
basics because every other control sits on the map. Presets/zoom/3D are also a good calibration target:
they touch the style registry (`LAYER_TOGGLES` `main.js:1661`, `TUNABLE_LAYERS` `main.js:1711`,
`applyPreset` `main.js:5423`) without touching the editor at all, so the line-cost they report is a clean
read of "what a real read feature costs to carry."

## What to build

**`website/viewer.html`** — a minimal shell, NOT a copy of `index.html`. Carry over only:
- `<head>`: viewport/PWA meta, `maplibre-gl.css`, and a NEW `css/viewer.css` (start empty; pull rules
  from `app.css` only as a ported control needs them — do not link `app.css` wholesale).
- `<body>`: `#map`, the `.left-controls` **shell** with the pill-bar markup (zoom + preset + 3D buttons
  from `index.html:53–83`), and the bottom message/ⓘ. Leave the drawer (Search/Hot/Calendar), Locate,
  Install for later slices — empty placeholders or omitted.
- No `.panel` (the right editor) at all. No `panel.js`, no `event_schedule_geojson.js` yet (comes with
  the calendar slice), no editor scripts.

**`website/js/viewer_core.js`** — the clean core. Port from `main.js` ONLY:
- Map construction (`new maplibregl.Map`, region bounds `REGION_BOUNDS`, maxBounds, the base style).
- The **published-layer** sources + style layers (presets park/topo/trace/satellite and the curated
  vector layers they show). Do NOT port the dev-reference layers (9-patch AOI, lidar tile index, NAIP,
  OSM service/tracks, SFWDA raster, synthetic activity) — they are not the read product.
- `applyPreset` + the zoom/region/pavilion view jumps + the 3D terrain toggle, and *only* the helpers
  those call (`setLayerVisibility`, `setPaint`, the preset-paint apply path). Trace each call; stop when
  the dependency chain closes. Anything `applyPreset` does not reach does not come over.

## The measurement (this is the point of the slice)

Record, in this card under Verification:
- **Lines of `viewer_core.js`** after the presets/zoom port closes — vs the editor-free fraction of
  `main.js` it replaces.
- For each helper pulled in: was it needed, or did it drag a chain that suggests bloat? If presets cost
  far more than expected, **flag it here and stop** — that is the andon the user described, and it tells
  us the published-layer style itself carries debt worth assessing before we port more.

## Acceptance

- [x] `website/viewer.html` + `website/js/viewer_core.js` exist and load with **zero console/page errors**.
- [x] The map renders the published-layer style at the park; `index.html` is **untouched** (git shows it
      unmodified — `git status` lists only the 3 new files).
- [x] **Presets** (park/topo/trace/satellite), **zoom** (region/park/pavilion), and **3D** all work in
      the new viewer and match the old page's behavior (observed, side by side — see Verification).
- [x] The dev-reference layers were **not** ported (confirm the published-vs-reference line held).
- [x] Line-cost recorded under Verification, with an andon note if presets dragged more than expected.

## Verification

- `cd website && python3 -m http.server 8000`, open `http://localhost:8000/viewer.html` beside
  `http://localhost:8000/index.html`.
- Playwright / headless: load `viewer.html`, assert the 4 presets + 3 zoom buttons + 3D each change the
  rendered map (fixed-camera control test per `ai_rules/verify_by_observation.md` — observe pixels, do
  not re-derive the expected style). Screenshot each preset. 0 console errors.
- Reuse the existing per-preset verifiers as the behavior contract where they exist.

### Done — 2026-06-13 (slice 1 shipped, verified by observation)

**Files (built alongside; `index.html`/`main.js` untouched):**
`website/viewer.html` (63 lines) · `website/css/viewer.css` (75 lines, pulled rule-by-rule from
`app.css`, each block citing its source line) · `website/js/viewer_core.js` (895 lines).

**Verification (real running system, not re-derived).** Served on `:8011`,
`/tmp/verify_viewer_core.py` (fixed-camera control test per `ai_rules/verify_by_observation.md`):
**19/19 PASS, 0 console errors, 0 page errors.** Presets don't move the camera, so a preset switch is a
fixed-camera test by construction — each of park/topo/trace/satellite renders a **distinct frame**
(4 distinct SHA hashes); Satellite pulled TNMap aerial tiles; the 3 zoom buttons each moved the camera
(distinct frames); 3D pressed→pitched (distinct frame) and pulled AWS terrarium DEM tiles, then
un-pressed. Screenshots in `brain/output/viewer_core_*.png` + `index_park_edit0.png`. **Side-by-side vs
`index.html?edit=0`:** the base read matches (land cover, boundary, roads, blue water, gold trail
network blue/green/black, the two ochre visitor circles, both brand logos, buildings). The only deltas
are the deferred surfaces — the left-rail drawer (Search/Hot/Calendar) and the pavilion POI/event dots —
which belong to later slices. The published-vs-reference line held.

**Line-cost (the point of the slice).** `viewer_core.js` = 895 total (757 code / 105 comment / 33 blank):
- **`map.on('load')` layer build = 411 lines** — the 12 published-layer sources + style (land cover ×2,
  AWS terrain DEM + hillshade, TNMap aerial, contours, water/springs, roads, visitor context, buildings,
  gold trail network, publish boundaries/trails/trailheads, brand logos).
- **`BUILT_IN_PRESETS` literal = 175 lines** — ported byte-for-byte; the preset style registry.
- **~309 lines** map construction + fetch/bounds helpers + palette consts + the *actual*
  preset/zoom/3D logic. The feature logic alone (`applyPreset`+`applyPaintState`+`PRESET_LAYERS`+
  `goToView`+`setTerrainEnabled`/`syncTerrainControl`) is **~90 lines**.

**Andon read: NO stop — presets did NOT drag more than expected; the opposite.** The
presets/zoom/3D *feature* is cheap (~90 lines). The cost is the **published-layer style it operates on**
(~586 lines: 411 build + 175 paint registry), and that is **load-bearing** — it is the read product
(the layers a reader actually sees), not sediment. So the calibration: a real read feature
(presets/zoom/3D + the base read layers) costs **~895 clean lines**, carrying **12 layers**, vs the same
surface tangled across `main.js`'s 10,603.

**Where the "5 generations" debt actually lives (sediment routed around, not load-bearing):** every
layer add-site in `main.js` is wrapped in 2–5 editor/POI hooks the read core does not need —
`bindPopup` (→ `poiPopupHtml`, slice 4), `indexFeatures` (search, slice 2), `applyPositionedFeatures`
(drag-to-move overrides), `bindPanelReveal`/`registerFeatureListLayer` (editor feature list), plus the
brand-logo size-cap store and slider plumbing. And `applyPreset` in `main.js` is **not editor-free** as
the card guessed: it drives visibility through the editor's checkbox registry (`PRESET_TOGGLE_IDS` →
`getElementById` → `updateLayerVisibility` reads `toggle.checked`) and carries snapshot / layer-tuner /
session-persistence tails (`savedPresetStates`, `syncLayerTunerFromSelection`,
`persistViewerSessionState`). The clean core **severs the checkbox indirection** — a DOM-free
`PRESET_LAYERS` map (preset bool → layer ids) drives layers straight — and drops the three tails. That
severance is the single biggest structural simplification the extraction bought.

**Scope lines drawn (deliberate, documented):**
- **Popups dropped** (style layers only). Not reached by presets/zoom/3D; `bindPopup` drags the
  `poiPopupHtml`/`feature_display` chain = slice 4. Clicking a feature shows no popup yet.
- **Dev-reference layers NOT carried:** 9-patch AOI grid, lidar tile index, NAIP, OSM tracks/service/
  named, SFWDA raster, synthetic + GPX activity hotspots, cemeteries. Consequence: the **Trace** preset
  in the clean core is a degraded relief view (hillshade + roads + buildings + gold trails + trailheads)
  — its SFWDA-paper/OSM **workbench** refs are gone. That confirms Trace is really an editor/tracing
  preset, not a day-of read preset; flagging for the user's published-layer-line call (readme fork 2).
- **Later-slice layers absent (preset bools no-op on them):** `editor-poi-*` (slice 4 POI),
  `event-schedule` (slice 3 calendar), `publish-pois` ★ destinations (slice 4). `setLayerVisibility`/
  `setPaint` guard on `getLayer`, so the verbatim preset paints for all absent layers no-op harmlessly.
- **Brand-logo size-cap store dropped:** logos render at the inlined default cap (1) instead of the
  editor's persisted/tunable cap.
- **One de-dup vs `main.js`:** the land-cover fill/outline `match` exprs are defined once (module-level)
  and reused at the add-site, rather than `main.js`'s two identical copies (module + load-handler).

**Trim-or-keep checkpoint (council/Mason note):** the verbatim `BUILT_IN_PRESETS` carries ~17 paint
entries (+ the `ACTIVITY_HOTSPOT_OPACITY` const that backs two of them) for layers the read core doesn't
draw — they no-op now and are the honest, measured cost of a byte-faithful port. They stop being dead
when slices 3/4 add their layers. **At each later slice, decide trim-or-keep per family:** any layer
family a later slice does NOT bring (e.g. Trace's `osm-*`/`sfwda-*` workbench refs, if the user draws the
published line to exclude them — readme fork 2) must have its preset paint/toggle entries trimmed at that
decision point, so the verbatim port never silently hardens into permanent orphan weight.

**Owed / git gate:** UNCOMMITTED (no_commits — the user's gate). `viewer.html` is **not** in `sw.js`
`SHELL_ASSETS` yet, so **no `#appVersion`/`VERSION` bump owed** (precache is a later slice). Next card per
the slate: **Search** (`searchInput` + `buildSearchGroups`/`renderSearchResults`).

## Notes

Build alongside; the live page is the reference, never the patient. No commits without the user's git
gate (`no_commits.md`). `viewer.html` is a new file (not a shell asset in `sw.js` yet) — no `#appVersion`
bump owed until it is precached, which is a later slice. Card the **Search** slice once this one's
line-cost is in hand (`_readme.md` slate item 2).
