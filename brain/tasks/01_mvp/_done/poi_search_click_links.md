# POI search / click / links + G-Central scrub (viewer batch, v89)

TL;DR: One viewer-polish batch from the user. Camp POIs (waypoints) are now
searchable and clickable with descriptions; the Hot Rocks Comp Pad reads as an
RC-crawl comp pad; the AOP badge and Rock Warblers logos got real tooltips; a
**data-driven final link** now renders in any popup (region callouts → Marion
County tourism, AOP badge → its site, Rock Warblers → its event page); and
**"G-Central" is scrubbed** from the product. A trail-free SFWDA paper sheet
(user-supplied) now overlays the **Trace** preset. All 8 items shipped + verified
at **v89**.

#aop #viewer #poi #callouts #search #v89

-----

## What shipped (all verified by observation, `/tmp/verify_poi_batch.py` — ALL PASS, 0 console errors)

1. **Camp POIs searchable** — `gold_aop_waypoints_traced.geojson` is now indexed
   (`indexFeatures` in `viewer_core.js`, right after the waypoint layers). "Hot
   Rocks", "Cabin 3", etc. surface in search; the result kind-tag reads the
   per-feature kind (comp pad / cabin / rv site / cemetery / entrance …) instead
   of a flat "poi".
2. **Camp POIs clickable + descriptions** — `aop-waypoints` added to
   `INTERACTIVE_POPUP_LAYERS`, so a click opens the normalized
   `AOPFeatureDisplay` card. Descriptions authored onto the gold features where
   there's something to say (9 of them); plain camp rows (RV Site N, Cabin N)
   stay name+kind. Authored copy lives ON the data (no `aop_poi_index` plumbing
   for waypoints; the gold file is the source — there is no `raw/` archive for it).
3. **Hot Rocks Comp Pad note** — `description` = "Purpose-built scale RC
   rock-crawling competition pad — set up specifically for the RC crawler comps
   held at the park." (`kind` = "comp pad").
4. **AOP badge tooltip** — `description` added to the `aop_badge` brand-logo
   feature (was null).
5. **Rock Warblers tooltip** — `description` added to the `rock_warblers`
   feature (was null).
6. **A final link attribute in the tooltip (data-driven, not hard-coded)** —
   `feature_display.js` `featureDisplay()` now reads `link`/`linkLabel` from
   `link_url`/`link_label`, and `popupHtml()` renders a styled `<a
   class="poi-popup-link">` as the LAST element when present (CSS in
   `viewer.css`). Destinations live on the data:
   - region callouts (South Pittsburg/Kimball, Monteagle) → `https://visitmarioncountytn.com/`
   - AOP badge → `https://adventureoffroadpark.com/`
   - Rock Warblers → the verified FB event page (the only Rock Warblers URL in
     the repo; no standalone team site found — swap if one surfaces).
7. **G-Central scrubbed** — removed the " / G-Central" nickname from every
   product reference: served `gold_aop_buildings` / `silver_publish` /
   `bronze_aop_editor_seed_pois`, their `raw/` archives, `aop_poi_index.json`,
   `_data_manifest.json`, the old-page comment (`main.js`), and the active
   `northstar/events/show_and_shine_northstar.md`. "AOP Pavilion" / "Pavilion"
   now stands alone. Verifier confirms 0 hits in served data.

Version bumped **v88 → v89** (`sw.js` VERSION + `index.html` #appVersion); all
edited assets (`viewer_core.js`, `feature_display.js`, `viewer.css`) are in
`SHELL_ASSETS`, and the data caches refresh on the bump.

## Data discipline followed — and the durability caveat (council Steward andon)

Per the user ("update the root/ gold/ source data, no shortcuts, no
hardcoding"): every authored field landed ON the feature, not in JS — the only
code change is the GENERIC `link` renderer in `feature_display.js` (no
per-feature URLs or copy). All served files render correctly **today**.

But "loss-free re-bake via served + `raw/`" is only true for the **raw-pipeline**
layers (e.g. `bronze_aop_editor_seed_pois`, `aop_poi_index`), where
`rebake_canonical.py` reads `raw/`. It is **NOT** true for the three layers I
edited that are **DB-baked from `core.features`** by
`export_publish_geojson.sh` (`REFERENCE_LAYERS`, line 123):

- `silver_aop_visitor_context_callouts.geojson` — the **new `link_url`/`link_label`
  on the 4 callouts + the AOP/Rock Warblers `description`s** live only in the
  served file.
- `gold_aop_buildings.geojson` and `silver_publish.geojson` — the **G-Central
  scrub** on the pavilion description.

`rebake_canonical.py` **evicted** these four reference files (callouts/buildings/
cemeteries/trails) + publish on 2026-06-10 ("one writer per served file"); it does
NOT read their `raw/`. So **my `raw/` edits to callouts/buildings/publish are
inert** (belt-and-suspenders only), and a future `export_publish_geojson.sh` run
**reverts** the new callout links/descriptions and **restores G-Central** in
buildings/publish — unless these are folded into **`core.features`** first.

**Owed (needs Docker/PostGIS, not available this session):** fold the 4
`link_url`/`link_label` + 2 brand `description`s into `core.features` (the
callouts writer), and scrub "G-Central" from the `core.features` pavilion
description, so a DB re-export reproduces this batch. Until then the served files
are the live truth and must not be regenerated from the DB without re-applying.

## Left intact on purpose

- **Historical / test references to G-Central** — session archives, `_done`
  cards, and the `playwright_verify_gC_identity.py` / `verify_gMeta_bake.py`
  fixtures still say "G-Central"; those are durable records / test inputs, not
  product. `event_schedule_context_20260522.json` (sister-event research input)
  also keeps it.
- `_data_manifest.json` was sed-patched (not regenerated) to avoid pulling in
  unrelated medallion-rename churn; re-running `build_data_manifest.py` is the
  clean regen when the DB is up.

## 8. "No-trails" paper-map overlay on the Trace preset — DONE

The user supplied a clean trail-free export (`brain/import/sfwda_aop_trail_map_no_trails.png`,
2500×1817, identical dims to the original sheet so the existing alignment quad
applies). It keeps the paper's chrome — title, legend, entrance labels, icons —
and drops the trails, markers, AND the boundary (all now in the vector layers).

- Converted to `website/data/sfwda_aop_trail_map_no_trails.webp` (89 KB) and
  added to `sw.js` `DATA_ASSETS` (precached beside the original sheet).
- **Rotation + warp (the user's correction: "rotated -90 degrees and have a warp
  applied see old_index").** A single 4-corner MapLibre image source can't apply
  the georeferencing warp and ignores the orientation, so the first attempt
  rendered mis-oriented. Fixed by porting the old page's proven bake
  (`main.js`): `viewer_core.js` now loads the sheet, **rotates it by
  `orientation_cw_degrees` (270° = −90°)** onto a canvas (`rotateToCanvas`),
  **slices it into a `GRID_N×GRID_N` (6×6 = 36) mesh** (`sliceCanvasN`), and adds
  one `sfwda-notrails-tile-r-c` image source per tile warped to its four
  `grid_6x6` nodes (TL/TR/BR/BL). Helpers `loadImageEl` / `rotateToCanvas` /
  `sliceCanvasN` / `bilinearGridFromCorners` are ported verbatim. Added right
  after the satellite raster so the tiles sit **above** hillshade/satellite but
  **below** every vector layer (trails/waypoints draw on top).
- `PRESET_LAYERS.showSfwdaNoTrails → SFWDA_NOTRAILS_TILE_IDS` (the 36 tile ids,
  computed up front); toggle is `true` in the **Trace** preset only (false in
  Park/Topo/Satellite, matching how `showSfwda` is enumerated). Tiles render at
  `raster-opacity 0.7` (the old page's paper-tile default). Verified: 36/36 tiles
  present + visible in Trace, 0 in Park, rotation + warp correct, no overlay
  errors (`brain/output/verify_notrails_trace2.png`).
- Pitfall caught in verification: MapLibre `image` sources reject an
  `attribution` property (it threw and dropped the source); omitted.

The earlier auto-inpaint attempt (`brain/output/sfwda_no_trails_candidate.png`)
is superseded by the user's clean export and is no longer used.
