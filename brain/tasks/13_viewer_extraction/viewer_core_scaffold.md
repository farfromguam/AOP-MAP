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

- [ ] `website/viewer.html` + `website/js/viewer_core.js` exist and load with **zero console/page errors**.
- [ ] The map renders the published-layer style at the park; `index.html` is **untouched** (git shows it
      unmodified).
- [ ] **Presets** (park/topo/trace/satellite), **zoom** (region/park/pavilion), and **3D** all work in
      the new viewer and match the old page's behavior (observed, side by side).
- [ ] The dev-reference layers were **not** ported (confirm the published-vs-reference line held).
- [ ] Line-cost recorded under Verification, with an andon note if presets dragged more than expected.

## Verification

- `cd website && python3 -m http.server 8000`, open `http://localhost:8000/viewer.html` beside
  `http://localhost:8000/index.html`.
- Playwright / headless: load `viewer.html`, assert the 4 presets + 3 zoom buttons + 3D each change the
  rendered map (fixed-camera control test per `ai_rules/verify_by_observation.md` — observe pixels, do
  not re-derive the expected style). Screenshot each preset. 0 console errors.
- Reuse the existing per-preset verifiers as the behavior contract where they exist.
- _(fill in on completion: line counts, what each ported helper cost, andon notes.)_

## Notes

Build alongside; the live page is the reference, never the patient. No commits without the user's git
gate (`no_commits.md`). `viewer.html` is a new file (not a shell asset in `sw.js` yet) — no `#appVersion`
bump owed until it is precached, which is a later slice. Card the **Search** slice once this one's
line-cost is in hand (`_readme.md` slate item 2).
