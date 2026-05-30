# Paper-map trail extraction (vectorize the SFWDA raster)

Started: 2026-05-29
Status: PROTOTYPE — stages A/B/D/E/F running end-to-end (2026-05-29). OCR,
boundary-split, facility-icon filter, and viewer wiring still open.

Take the georeferenced SFWDA 2015 paper map, separate the difficulty markers
from the trail lines, line-trace the trails into vector paths, read each
marker's type + number, and emit georeferenced trail polylines tagged with
`{trail_number, difficulty}`. Lands in the raw zone, not `publish`.

This is the concrete method for `01_mvp` item 9 / `data_integrity_publishability.md`
"Real Trails + Trailheads": the paper map is the only AOP-internal trail figure
we have, and the digital trail geometry was lost by the prior owner.

#aop #raster #vectorize #trails #opencv #raw-zone #editor-is-the-viewer

-----

## What we have

- **Source raster (the one to process):** `brain/import/community_trails/sfwda_aop_trail_map_2015-03-11.png`
  — 2500×1817 px, lossless. (`website/data/sfwda_aop_trail_map.webp` is a 312 KB
  lossy copy for the viewer; trace from the PNG, not the WebP.) © AOP via SFWDA,
  internal/inspection only — see `import/_readme.md`.
- **Georeference (user says correct):** `website/data/sfwda_raster_alignment.json`
  — `orientation_cw_degrees: 270` + a `grid_6x6` (7×7 array of `[lng,lat]` control
  points). The viewer slices the raster into a 6×6 mesh and bilinear-maps each
  tile to its 4 control points (nonlinear warp). The exact math lives in
  `website/index.html` `defaultGridFromCorners` / `upsampleGrid` (~line 8537):
  for display-space `(u,v)∈[0,1]`, find the grid cell, bilinear-interpolate the
  4 surrounding control points. Pixel→display first applies the 270° CW rotation.
- **Reference raster (current, now the edit backdrop):** `aop_official_trail_map_2025-11.png`
  — same numbers-only scheme, ≈Nov 2025, 1024×744 px. **Verified 2026-05-29 to be
  the same cartographic base as the 2015 sheet** (newer/cleaner render), so it
  **reuses the existing 2015 warp verbatim** — no separate alignment needed.
  Proof: rectified through `PaperWarp` and overlaid the 2015 trace — ink lands on
  the trace across the whole park (`brain/output/test_2025_fit_overlay.png`).
- **OSM tracks** (`website/data/osm_aop_9patch.geojson`, 47 `highway=track`) —
  independent geometry to validate the trace against.

## Honest framing (read before building)

- **The geometry is accurate; the caveat is currency, not precision.** Owner
  attestation (2026-05-29): this sheet was **printed from a mapping system**, so
  the trail lines are true geometry, not a hand-drawn diagram — "100% accurate
  once the warp is accounted for." This reconciles with the brain's "high for
  **shape**, low for **current trails**": shape/position is trustworthy; the only
  caveat is **vintage** (2015 — the trail *inventory* may differ from today, not
  the positions). Consequence: trace **faithfully** — centerline precision and
  warp fidelity now matter, because we are recovering real geometry, and the
  output can carry **high positional confidence** (currency flagged separately).
- **The markers carry NUMBERS, not names.** Per `research/aop_trail_name_index.md`,
  the park is numbers-only by design — no name index ever existed (only ~8 onX/
  observed names, in `website/data/aop_trail_catalog.json`). So the extraction is
  keyed by **number + difficulty**; names attach later from the catalog by number.
- **"Black diamond" is rendered as a filled black TRIANGLE ▲** on this sheet
  (legend: green ● Easy / blue ■ Moderate / black ▲ Difficult). Detector must
  match a triangle, and triangles share color with trail ink, boundary, and text.

## Proposed pipeline (Python + OpenCV / scikit-image / shapely)

Fits the existing `mvp/scripts/` culture (Python + Docker GDAL + Playwright verify).

- **A — Marker detection (location + type + number).**
  - Green ● and blue ■: HSV color thresholding → connected components → centroid +
    shape (circularity vs squareness). Easy; they are the only saturated colors.
  - Black ▲ Difficult: cannot use color. Separate from trails/text/boundary by
    component shape — filled triangles are compact + solid (high fill ratio,
    ~triangular), trail lines are thin/elongated, text is small clustered blobs.
  - Per marker: centroid (pixel), type→difficulty, and the **number inside it**
    via OCR. Numbers are ~15 px tall at 2500 px → OCR will be unreliable; plan
    **OCR + human verification**, or template-match digits. A higher-res scan
    would materially improve this (see forks).
- **B — Trail-line isolation.**
  - Mask out the detected color markers; mask the title block + legend (fixed
    corner regions); detect + set aside the outer park-boundary contour (keep it
    as a separate boundary output — it is useful).
  - Binarize the remainder → the trail-line network, plus the triangle footprints
    (removed) and any stray text (filter by component size/shape).
- **C — Gap bridging.** Where a marker sat on a line it left a gap. Morphological
  closing across each marker's footprint before skeletonizing, or rejoin colinear
  skeleton endpoints within the footprint.
- **D — Skeletonize + vectorize.** Zhang-Suen / scikit-image `skeletonize` → 1 px
  centerlines → trace into a graph (junction pixels = nodes, runs = edges).
  Simplify edges with Douglas-Peucker (the contour pipeline already has DP +
  `repair_crossings.py` infra to borrow).
- **E — Marker→trail association.** Assign each marker to its nearest traced edge →
  that edge inherits `{trail_number, difficulty}`.
- **F — Georeference.** Apply the *same* mesh warp to every vertex: pixel→(270°
  rotate)→display `(u,v)`→grid cell→bilinear of the 4 control points→`[lng,lat]`.
  Reuse `sfwda_raster_alignment.json` verbatim — do **not** invent a new
  transform. (Alt route: pre-warp the raster to a GeoTIFF via GDAL TPS from the
  mesh-as-GCPs, then trace in geo space — rejected as default: extra resampling,
  and the mesh is already the authority.)
- **G — Validate by observation.** Load the output GeoJSON in the viewer's Trace
  preset over the warped raster + OSM tracks; confirm the trace lands on the ink
  and roughly agrees with OSM where they overlap. Per `ai_rules/verify_by_observation`.

## Output + source posture

- Emit `brain/import/community_trails/sfwda_traced_trails.geojson` (raw zone),
  copied to `website/data/` as a default-OFF viewer layer behind a toggle, like
  the OSM/SFWDA layers. **Not** into `publish.geojson`.
- Each feature carries `trail_number`, `difficulty`, `source_name='SFWDA AOP
  trail map 2015-03-11'`, `source_type='community_raster'`, `confidence`,
  `review_status='raster trace of schematic map; needs field/imagery review'`.
  Promotion to `core`/`publish` goes through `northstar/source_register.md`. The
  park-use curation authorization in `aop_trail_name_index.md` clears assembly,
  not public republish of the raster.

## Prototype — what runs (2026-05-29)

Three scripts in `mvp/scripts/` (need `numpy opencv-python-headless pillow
scikit-image shapely`, installed into the global Python that already carries
`playwright`). Outputs land in `brain/output/paper_trace/` (scratch, not shipped).

- `extract_paper_trails.py` — Stage A+B. Detects **124 markers**: 40 green
  circles (Easy), 42 blue squares (Moderate), 42 black triangles (Difficult).
  Color markers are trivial (HSV). The triangles share ink with the trail lines
  and usually touch one, so contour-shape failed (found only 3); fixed by
  **close (fill the white number-hole) → morphological OPEN** to strip thin lines
  and leave the solid triangle body — connectivity-independent. Then isolates the
  trail-line network (dark ink minus markers, chrome boxes, longest boundary
  contour, small text blobs). Writes `markers.json` + debug overlays.
- `paper_trace_warp.py` — Stage F. `PaperWarp` replicates the viewer warp exactly
  (270° rotate-to-canvas → row-major mesh slice → per-cell bilinear over
  `grid_6x6`). **Self-check passes**: image corners land on the alignment
  NW/NE/SE/SW control points (TL→SW, TR→NW, BR→NE, BL→SE). Emits
  `sfwda_markers.geojson` (124 difficulty-tagged points).
- `vectorize_paper_trails.py` — Stage C/D/E. Bridges marker gaps (close r≈19px),
  `skimage.skeletonize`, hand-rolled skeleton-graph walk (nodes = deg≠2), DP
  simplify, marker→nearest-edge association. **382 edges / 1521 vertices, 116/124
  markers matched** within 40px. Warps every vertex → `sfwda_trails.geojson`.
  Trace bbox sits inside the alignment envelope (georef sane). Overlay
  `trails_vector_overlay.png` tracks the network well by eye.

### Loaded in the viewer for review (2026-05-29)

Per user ("load the data in the app to review, refine after"), the trace is wired
into `website/index.html` as two **default-OFF, in-no-preset** review layers:
`sfwda-trace-trails` (lines colored by difficulty: green Easy / blue Moderate /
dark Difficult / ochre mixed-unread) and `sfwda-trace-markers` (difficulty-colored
dots). Toggles `SFWDA traced trails (extracted)` / `SFWDA traced markers
(difficulty)` sit under `External reference` next to the SFWDA raster toggle.
Registered in `LAYER_TOGGLES` (so the change handler + visibility loop self-wire)
but added to **no** preset object, so `applyPreset` never forces them (the
`hasOwnProperty` guard at `index.html` ~5087). Data copied to
`website/data/sfwda_traced_trails.geojson` + `sfwda_traced_markers.geojson`.
Verifier `mvp/scripts/playwright_verify_sfwda_trace.py` PASS: both layers load,
default off, toggle to visible (512 features), survive a preset switch, 0 console
errors. Visual review: turn on the SFWDA raster + traced trails in the **Trace**
preset — the colored trace lands on the paper-map ink (`brain/output/
sfwda_trace_review_traceonly.png`).

### Reproduce

```bash
# 1. detect markers + isolate trail lines  -> brain/output/paper_trace/
python3 mvp/scripts/extract_paper_trails.py
# 2. georeference the markers (also self-checks the warp) -> sfwda_markers.geojson
python3 mvp/scripts/paper_trace_warp.py
# 3. skeletonize + vectorize + warp the trails -> sfwda_trails.geojson
python3 mvp/scripts/vectorize_paper_trails.py
# 4. refresh the viewer copies, then verify in-app
cp brain/output/paper_trace/sfwda_trails.geojson  website/data/sfwda_traced_trails.geojson
cp brain/output/paper_trace/sfwda_markers.geojson website/data/sfwda_traced_markers.geojson
( cd website && python3 -m http.server 8001 & ) ; \
  python3 mvp/scripts/playwright_verify_sfwda_trace.py
```

Tuning knobs: `extract_paper_trails.CHROME_BOXES_FRAC` (chrome masks),
triangle area band in `detect_triangles`; `vectorize_paper_trails.SIMPLIFY_PX`
(DP tolerance), `MIN_EDGE_PX` (stub drop), `BRIDGE_PX` (gap-bridge kernel).

### Still open (next slices)

1. **Trail numbers (OCR).** Not read yet — `trail_number: null` on every feature.
   Numbers are white-on-fill, ~15px; needs a digit reader (tesseract not
   installed; consider a Docker OCR or template match) + a human-verify pass.
   This is the labeling half of the user's ask; geometry + difficulty are done.
2. **Boundary split.** The outer park boundary still partly rides in the trail
   trace; emit it as its own feature instead of mixing it in.
3. **Facility-icon false positives.** A few triangular camping-tent icons can
   read as Difficult markers; filter by the tent's base line or known locations.
4. **Junction topology.** The gap-bridge close rounds junctions slightly; a
   reconnect-endpoints bridge would preserve geometry better than a blanket close.
5. **Where it lands (fork).** Outputs are scratch. Decide: wire as a default-OFF
   viewer layer (fast visual cross-check vs OSM + the raster, matches
   `editor_is_the_viewer`) **and/or** push through the `raw → core → publish`
   PostGIS spine (`source_register`) since northstar makes PostGIS the data spine.

## Forks — resolved 2026-05-29

1. **Number legibility — RESOLVED: no higher-res source exists.** The 2500 px PNG
   is the best we have, so the trail-**number** read needs an OCR + **human-verify**
   pass. Note this is only the *number*; trail *geometry* traces fine at this
   resolution (lines are wide; numbers are ~15 px).
2. **2015 vs 2025 raster — RESOLVED: same base, 2025 is now the edit backdrop.**
   The 2025 official map proved to be the same cartographic base as the 2015 sheet
   (verified by overlay, see "Reference raster" above), so it reuses the existing
   warp verbatim — the anticipated re-warp was not needed. It is the reference for
   *what trails exist now* (added/removed since 2015); positional geometry is shared.
3. **Accuracy acceptance — RESOLVED: treat as real, high-confidence geometry.**
   Per owner attestation the map is a mapping-system export. Output carries high
   positional confidence; promotion still routes through `source_register`, and
   currency (2015 vintage) is flagged per feature.

-----

## Progress — numbers attached (2026-05-29, second pass)

Stages A (markers), B–E (line trace), F (georeference) ran via the OpenCV
pipeline (`extract_paper_trails.py` → `brain/output/paper_trace/`:
`sfwda_markers.geojson` 124 markers, `sfwda_trails.geojson` 382 edges). Those
left `trail_number: null` everywhere — the OCR fork.

The **number read is now done by eye** (tesseract.js tried and lost to eyeball
on the ~15 px stylised numerals) and attached:
- `brain/output/paper_trace/trail_number_reads.json` — the reads, keyed by pixel
  centroid (committed, reproducible).
- `mvp/scripts/attach_trail_numbers.py` matches each read to a marker by
  `centroid_px` (<30 px) and fills `trail_number` in place on the viewer layer
  `website/data/sfwda_traced_markers.geojson` + the brain copy. Idempotent.
- **82 / 124 markers numbered; 56 distinct trail numbers; 0 band-flags** — every
  attached number fell in its difficulty band, an independent cross-check that
  the eye-reads agree with the cv2 colour detection.
- Confidence per marker: 2-digit reads `high`, single-digit greens `low`.
  Unmatched 42 = unread single-digit greens + junk (legend/picnic/tent icons).

### Pipeline is now one command — `mvp/scripts/run_paper_trace_pipeline.sh`
Chains all stages so the numbers are never stale:
1 extract → 2 warp → 3 vectorize (+ dumps `trail_graph.json`) → **4 publish** (cp
brain outputs → `website/data/sfwda_traced_{markers,trails}.geojson`) → **5 attach
numbers** to markers → **6 stitch contiguous numbered trails**. Stage 4 was a
manual copy, now scripted. Verified end-to-end from a clean regen;
`playwright_verify_sfwda_trace.py` PASSes.

### Contiguous numbered trails — `build_numbered_trails.py` (stage 6)
Makes each trail whole instead of 382 fragments. Tags edges from the numbered
markers, then connects each number's marker-bearing edges through the skeleton
graph by **shortest path, penalising hops onto a different numbered trail (×6)**
so a path stays on its own ink across junctions. Output:
`website/data/sfwda_numbered_trails.geojson` — **67 trails, 58 single-part**
after the contiguity pass below (the rest branch or carry honest gaps). Also
stamps `trail_number` onto the directly-tagged edges of `sfwda_traced_trails`.
Debug overlay `brain/output/paper_trace/numbered_trails_overlay.png` — verified
the stitched lines sit on the ink and link the markers.

### Read coverage — full re-read at high zoom (2026-05-29, data pass)
Re-read **every** cv2 marker from per-marker high-zoom crops and keyed the numbers
to the detector's own centroids (`make_marker_crops.py` → `trail_number_reads.json`).
Single digits and the difficult-triangle numbers the first pass missed (41, 43,
45, 47, 49, 51, 52, 57, 59, 63, 67, 70, 71, 73, 74…) are now crisp:
- **117 / 124 markers numbered** (7 are junk — trail-line crossings read as
  triangles + the "Jeep" entrance text); **72 distinct trail numbers**.
- **Band cross-check: 116 / 117 in-band** — only one flag: a **blue circle "1"**
  near the Buggy Entrance (centroid ~1216,1457) tagged moderate. Left flagged
  (`band_flag`) for review, not guessed — likely an info/start marker, not a
  moderate trail 1.
Bands hold: Easy ● 1–20 · Moderate ■ 21–39 & 81–97 · Difficult ▲ 41–74.

**Difficulty bands (validated):** Easy ● **1–20**, Moderate ■ **21–39 & 80–99**,
Difficult ▲ **40–79**. Numbers attached so far: easy 2–12,14–18,20; moderate
21–29,32–39,81,83–87,94–98; difficult 44,50,53–74 subset.

**Triangulation note:** park-map colour is the park's own rating (authority for
park use); onX technical ratings differ for some trails — e.g. **6 Descension /
7 Ascension read GREEN on the map but onX rates them Moderate**. Recorded in
`research/aop_trail_name_index.md` + `website/data/aop_trail_catalog.json`.

### Contiguity pass (2026-05-29) — connect without over-reaching
Two fixes in `build_numbered_trails.py`, both verified on the overlay:
1. **Rejoin loose ends** — `build_bridges()` adds 354 synthetic edges between
   degree-1 skeleton ends that face each other within 70 px (colinear rejoin),
   restoring trails the lifted markers / ink gaps had cut.
2. **Local-path cap** — connect a number's pieces only through a skeleton path
   ≤ `CONNECT_CAP_PX` (420 px ≈ inter-marker spacing). Beyond that the pieces
   aren't adjacent on one trail, so they're left as an **honest gap**
   (`unjoined_gaps`) instead of grabbing a map-spanning route.

The cap was the key correctness fix: before it, trails whose same-number markers
sat far apart (e.g. 54 = two markers ~4 km apart) shortest-pathed across a third
of the network — a 133-edge / 4 km false sprawl. After: **length median 75 m,
max ~988 m**; 58/67 trails single-part, the rest either branch (parts touch at
0 m — fine) or carry flagged `unjoined_gaps` (8 trails). `linemerge` parts ≠
disconnected: a branching trail is contiguous but multi-part by definition.

Geometry welds on canonical per-node lng/lat (shared nodes are bit-identical).
Tunables: `BRIDGE_GAP_PX`, `BRIDGE_COS`, `CONNECT_CAP_PX`. Overlay:
`brain/output/paper_trace/numbered_trails_overlay.png`.

### In the app + editable SVG round-trip (2026-05-29)
- **App:** the traced markers now render with **trail-number labels** (new symbol
  layer `sfwda-trace-marker-labels`, tied to the existing `showSfwdaTraceMarkers`
  toggle). `playwright_verify_sfwda_trace.py` extended to assert the labels load /
  toggle / render — PASS.
- **Editable SVG export — `export_trace_svg.py`** → `brain/output/paper_trace/
  sfwda_trace_edit.svg`. The 6×6 mesh **warp is baked in**: the paper raster is
  rectified (scipy griddata + `cv2.remap`) into a **local-equirectangular-metres**
  frame, and the already-georeferenced vectors are projected into the same frame —
  so the four Inkscape layers (`paper_map`, `osm_tracks`, `traced_trails`,
  `traced_markers`) overlay with **no manual warping**. Projection params live in
  the SVG `<metadata>`.
- **Re-import — `import_trace_svg.py`** reads the edited `traced_trails` layer
  (handles M/L/H/V/Z + ancestor `transform=`), inverts the linear projection (no
  mesh warp), and writes `website/data/sfwda_trails_edited.geojson`. Round-trip
  verified exact: 382 lines / 1521 vertices, max vertex error **9 mm**.
- Workflow: `run_paper_trace_pipeline.sh` → `export_trace_svg.py` → edit in
  Inkscape/Illustrator (reconnect trails on the `traced_trails` layer) →
  `import_trace_svg.py` → cleaned `sfwda_trails_edited.geojson`.

**Hardened on a real Inkscape edit (2026-05-29).** First real round-trip
(`sfwda_trace_edited.svg`: 382 fragments → 43 reconnected trails) exposed what
Inkscape does on save, now all handled by `import_trace_svg.py`:
- Strips the `<metadata>` → projection is **recomputed from the alignment**
  (deterministic), not read from the SVG.
- Uniformly rescales the doc (viewBox 1394×1844 → 1859×2460, 96/72) and adds
  `matrix(1.3333…)` layer transforms → import maps **viewBox-proportionally in
  lng/lat** (any uniform rescale cancels) and composes all ancestor transforms.
- Identifies layers by `id` as well as `inkscape:label`.
- Strips `data-*` attrs and recolours strokes → **difficulty + number are
  re-attached from the unchanged markers by proximity** (≤22 m), the markers
  being the authority. Result: 43 trails, 39 numbered, 38 with difficulty, all
  inside the parcel envelope (the marker matches double as a georef check).

### Merged "truth" network + recolour round-trip (2026-05-29)
The user hand-edited BOTH layers in the SVG (reconnected trails through
intersections; fixed/removed wrong OSM tracks). New state:
- `import_trace_svg.py` now extracts **both** `traced_trails` and `osm_tracks`
  and merges them into **`website/data/aop_trail_network.geojson`** — the new
  authoritative network, both sources at one level (43 SFWDA + 45 OSM = 88 edges,
  71 numbered). Number + difficulty re-attached from markers; a distinct **per-trail
  colour** baked into each feature's `color` (same trail-number → same colour).
- **In the app:** new toggle "AOP trail network (merged truth, per-trail colour)"
  (`showAopTrailNetwork`) → layer `aop-trail-network` (line, `['get','color']`) +
  `aop-trail-network-labels`. Verifier covers it. Continuous trails → fly-to /
  highlight will work per-trail instead of per-fragment.
- **Re-export for the next cleanup pass:** `export_trace_svg.py` now takes
  `--trails/--osm/--color/--out`. The truth was re-exported distinctly-coloured:
  `export_trace_svg.py --trails aop_trail_network.geojson --osm none --color feature
  --out brain/output/paper_trace/aop_trail_network_edit.svg`. Edit intersections
  there → `import_trace_svg.py aop_trail_network_edit.svg` → updated truth.

### 2025 official map is now the edit backdrop (2026-05-29)
User: "use this map in the world as our reference, it's a bit newer… for the next
export manual edit loop; if needed I will warp the points to make it fit." The
re-warp was **not needed** — the 2025 map is the same base as 2015 (overlay proof
above). `export_trace_svg.py` gained a `--paper <png>` arg: it samples in the warp
frame but scatters the *paper-image* pixel coords, scaled proportionally
(`sx/warp.W*img_w`), so any-size render of the same map reuses the warp (identity
when dims match 2015 — back-compatible). The next manual-edit artifact is exported:
`brain/output/paper_trace/aop_trail_network_2025_edit.svg` — 2025 backdrop under
the authoritative `aop_trail_network.geojson` (88 trails, per-trail colour, 124
markers). Workflow unchanged: edit `traced_trails`/`osm_tracks` in Inkscape →
`import_trace_svg.py aop_trail_network_2025_edit.svg` → updated truth.

```bash
python3 mvp/scripts/export_trace_svg.py \
  --paper brain/import/community_trails/aop_official_trail_map_2025-11.png \
  --trails aop_trail_network.geojson --osm none --color feature \
  --out brain/output/paper_trace/aop_trail_network_2025_edit.svg
```

### Edit pass on the 2025 backdrop — re-imported (2026-05-29)
First manual edit loop against the 2025 backdrop. User edited the full stack
(`sfwda_trace_edit.svg` → `sfwda_trace_edited_2.svg`): reconnected `traced_trails`
to **62 trails** (from 382 raw fragments) and `osm_tracks` to **45**.
`import_trace_svg.py sfwda_trace_edited_2.svg` → **107 edges (62 SFWDA + 45 OSM),
76 numbered** → `website/data/aop_trail_network.geojson` (the authoritative network
the app's `showAopTrailNetwork` / `aop-trail-network` layer already serves). Inkscape
applied the usual 96/72 viewBox rescale (1394×1844 → 1859×2460) + `matrix(1.3333)`
layer transforms; the importer cancels both. Verified: 0 degenerate features, whole
network inside the alignment envelope, overlay on the 2025 backdrop lands on the ink
(`brain/output/net_2025_overlay.png`), `playwright_verify_sfwda_trace.py` PASS
(network toggles visible + renders). Number/difficulty re-attached from the unchanged
markers (≤22 m). All `website/data/` changes uncommitted.

### Trail number is now editable in the SVG editor — round-trip (2026-05-29)
The user asked for the merged truth exported so each trail's **name is its number**,
editable in the editor and surviving re-import. Done as an Inkscape-Objects-panel
channel (the active edit surface; "layers" = SVG objects):
- **Export (`export_trace_svg.py`):** every trail `<path>` now carries
  `inkscape:label="<number>"` + a child `<title>`, so each trail shows in
  Inkscape's **Objects** panel named by its number — double-click the row to
  retype it. `"?"` = no number guessed yet (31 of 107). `data-trail-number`/`id`
  kept as a fallback for files never hand-relabelled.
- **Import (`import_trace_svg.py`):** number precedence is now **label → data-attr
  → id**. A pure-integer `inkscape:label` is treated as **authoritative**
  (`_num_locked`), so `reattach_from_markers` no longer snaps a human edit back to
  the nearby marker's number (markers still fill *unlabelled* numbers + always set
  difficulty). Output features also get `name = str(trail_number)`.
- **Verified:** clean round-trip preserves all 76 numbers + sets `name==number`;
  a simulated Inkscape relabel `15→888` on a trail sitting atop a "15" marker
  survived import (was previously clobbered). `playwright_verify_sfwda_trace.py`
  PASS. Editable artifact regenerated: `brain/output/paper_trace/aop_trail_network_2025_edit.svg`.
- **Workflow:** edit numbers (Objects panel) + intersections (canvas) in Inkscape →
  `import_trace_svg.py aop_trail_network_2025_edit.svg` → updated `aop_trail_network.geojson`.
  All `website/data/` + `mvp/scripts/` changes uncommitted.

**Affinity Designer round-trip imported (2026-05-29).** The user edited in Affinity,
not Inkscape: `aop_trail_network_2025_edit_mc.svg`. Affinity drops `inkscape:label`
+ `<title>` and the embedded raster, but stores each object's (user-edited) name in
**`serif:id`** and keeps the `traced_trails` group id + the usual 96/72 viewBox
rescale (1859×2460) + `matrix(1.3333)` transform. `import_trace_svg.py` now reads
the number from **`inkscape:label` → `serif:id` → `data-trail-number` → id** (the
first integer it finds is authoritative; `_from_id` also matches Affinity's `_<num>`
ids). Imported **119 trails, 97 numbered** (up from 76 — the user filled `?`s),
`name==number`, all vertices inside the alignment envelope. Cross-check: 76 numbered
trails have their same-number marker within 40 m; 17 numbered trails have no marker
(user-typed numbers, honoured as authoritative); 4 numbers land >40 m from their
marker (1, 25, 47, 90 — left as the user's call; 25's marker is ~800 m off).
`playwright_verify_sfwda_trace.py` PASS.

### String trail names + difficulty colours + snap/trim (2026-05-29, golden-data prep)
The user opened the merged network and found `JW2`/`JW20` (and the rest of a batch
of **named** trails) had vanished. Root cause: the whole round-trip treated a
trail's **name as an integer** (`name == trail_number`) — the importer only kept a
label when `lbl.isdigit()`, so every non-numeric name the user typed in Affinity
was dropped. Fixed end-to-end:

- **`import_trace_svg.py` — names are strings now.** New `_editable_name(el)` reads
  the user's object name from `serif:id` (Affinity) → `inkscape:label` (Inkscape) →
  `id` (Affinity stores space-free names like `JW2`/`GWT` straight in `id`),
  stripping a leading `_`. Rule per the user: **import every typed name EXCEPT the
  `?` placeholder.** A pure-digit name still also sets `trail_number`; a non-numeric
  name (`JW2`, `Riot Hill`) is preserved as `name` and **locked** so marker-snap
  can't relabel it. Re-imported `aop_trail_network_2025_edit_mc.svg` → **119 trails,
  104 named, 0 `?` leaked**; all 9 non-numeric names land: `Area 51, GWT, JW1, JW2,
  JW3, JW4, JW20, Pretender, Riot Hill`.
- **Colour by difficulty, not the per-trail rainbow.** `assign_colors` now paints
  green `#1f9d3a` Easy / blue `#2438c8` Moderate / black `#111111` Difficult / grey
  `#888888` unknown. New `assign_difficulty` fills difficulty in confidence order:
  marker proximity (reattach, ≤22 m) → **number band** (Easy 1–20, Moderate 21–39 &
  80–99, Difficult 40–79). Non-numeric names with no nearby marker stay grey for
  review (we don't guess difficulty from a name's digits). Result: 30 easy / 38 mod
  / 29 difficult / **22 grey** (the grey set: `890`, the JW1–4/Pretender/Riot Hill
  named trails, + ~12 unnamed). The app toggle relabelled "…colour by difficulty";
  `aop-trail-network` already reads `['get','color']`, so the app shows it too.
- **`snap_trim_trails.py` (NEW) — "trails end on another."** Conservative topology
  cleanup on the network, in local metres: **TRIM** short overshoot stubs (an end
  that crosses past a junction and dead-ends ≤`TRIM_M`=18 m beyond → cut back to the
  crossing) then **SNAP** short gaps (an end ≤`SNAP_M`=18 m from another trail → move
  onto it + weld the point in as a shared vertex). Only degree-1 endpoints move.
  First run: **31 trimmed, 48 snapped, 3 still dangling** (>18 m — left for the human
  pass). 0 degenerate features, bbox inside envelope. Tunables: `SNAP_M`, `TRIM_M`,
  `EPS_M`. Run order: `import_trace_svg.py` → `snap_trim_trails.py` → `export_trace_svg.py`.
- **`export_trace_svg.py` — name survives the next round-trip.** Each trail `<path>`
  now writes its NAME (any string) to BOTH `inkscape:label` and `serif:id` (+ child
  `<title>`), with `_xml_attr` escaping and the `serif:` namespace declared on the
  root, so the name shows + edits in whichever editor the user opens. Re-exported the
  stack over the 2025 backdrop with `--color difficulty`:
  `brain/output/paper_trace/aop_trail_network_2025_edit.svg` (119 trails, 124 markers).
- **Verified:** `playwright_verify_sfwda_trace.py` PASS; export→import→export round-trip
  preserves all 9 names + 104 named; overlay `brain/output/net_2025_difficulty_overlay.png`
  shows the green/blue/black trace landing on the 2025 paper ink. **This SVG is the
  artifact handed to the user for the review/edit pass → re-import = golden data.**
  Workflow: edit names (Objects panel) + intersections (canvas) →
  `import_trace_svg.py aop_trail_network_2025_edit.svg` → `snap_trim_trails.py` →
  updated `aop_trail_network.geojson`. All `website/data/` + `mvp/scripts/` uncommitted.

For the review pass, the user owns: the **22 grey** (set difficulty), the **3
dangling** ends snap/trim wouldn't close at 18 m, and confirming the new named trails.

**edited_4 imported (2026-05-29, latest golden).** `aop_trail_network_2025_edited_4.svg`
(21:28): 120 trails (user added one), 102 named, all 9 string names, 0 grey — Easy 32 /
Moderate 44 / Difficult 40 / 4 roads. snap/trim auto-fixed 1 overshoot, 3 honest gaps
remain. Re-exported `aop_trail_network_2025_edit.svg` + overlay; verifier PASS. This is
the current served `aop_trail_network.geojson`.

**edited_8 imported + gold-export script (2026-05-29) — current served network.**
`aop_trail_network_2025_edited_8.svg` (120 trail paths, osm merged into the one
`traced_trails` layer — no separate `osm_tracks` group). Round-trip:
`import_trace_svg.py aop_trail_network_2025_edited_8.svg` → 120 edges, 94 numbered,
103 named, **0 grey** (the 4 `None`-difficulty features are exactly the 4 roads) →
Easy 30 / Moderate 46 / Difficult 40 / Road 4. `snap_trim_trails.py` auto-fixed
1 overshoot + 1 gap, **3 still dangling >18 m** (left for the human pass).

New **`mvp/scripts/export_gold_trail_network.py`** formalizes the previously
hand-done "gold" step: it replaces the importer's thin round-trip `_meta` with the
full self-contained block (crs, `color_legend`, `difficulty_band`, feature/colour
counts, `property_schema`, `generated_from`, and **auto-computed `review_flags`** —
numbered trails whose hand-set colour contradicts their number band). Features are
never touched; only `_meta` is rewritten, deterministically from the features, so
the gold metadata is reproducible on a fresh install instead of hand-maintained.
This makes the served `website/data/aop_trail_network.geojson` the **gold file the
static viewer loads directly on a new install** — no DB, pipeline, or localStorage
in the path (`index.html` `fetchJson('./data/aop_trail_network.geojson')`).

**Marker auto-renaming bug FIXED (2026-05-29).** The user hit phantom trail renames
("something is renaming 32 and 58"). Cause: `import_trace_svg.reattach_from_markers`
assigned a nearby marker's `trail_number` to **unnamed** trails, and the name-fallback
(`name = name or str(trail_number)`) then turned that into the trail's `name`. So a
single hand-typed "32" became three (the #32 marker cluster sat near two unnamed
neighbours), and "58"s appeared on unnamed trails near a #58 marker. Verified: the
edited_10 SVG carries exactly one path named "32" (all SVG names unique), yet the old
importer emitted three. **Fix: markers no longer assign `trail_number`/name — the user's
typed object-name (`_editable_name`) is the sole authority for a trail's number/identity.
Markers still bootstrap DIFFICULTY for trails the user left uncoloured (a colour
bootstrap, not an identity one).** Re-import of edited_10 → 0 duplicate numbers (was a
recurring 32/55/890 mess), 87 numbered / 100 named / 20 deliberately-unnamed (left for the
user, not auto-stamped). This retires the duplicate-number find-and-fix loop for
*auto-created* dups; any future dup is now genuinely user-typed.

**edited_9 imported (2026-05-29) — current served network.** Same pipeline
(`import → snap_trim → export_gold_trail_network --from aop_trail_network_2025_edited_9.svg`).
Identical aggregate shape to edited_8 (120 / 94 numbered / 103 named / 0 grey;
Easy 30 / Mod 46 / Diff 40 / Road 4; same 4 review flags 35/1/95/47) — the diff is
geometric: **4 trails repositioned (11, 34, 47, Pretender)**, same total vertex
count (2602), so reconnect/nudge fixes, not adds. Verifier PASS. This is the
current served file; supersedes edited_8.

Verified: network bbox sits fully inside the alignment envelope (georef sane), 0
degenerate features, `playwright_verify_sfwda_trace.py` **PASS** (toggles
`showAopTrailNetwork`, asserts `aop-trail-network` visible + renders >0 edges).
This run's `review_flags` (band-vs-colour disagreements for the human pass): trail
**35** (easy vs moderate band), **1** (moderate vs easy band — the long-standing
Buggy-Entrance blue-circle "1"), **95** (easy vs moderate band), **47** (easy vs
difficult band). Run order is now **`import_trace_svg.py <svg>` → `snap_trim_trails.py`
→ `export_gold_trail_network.py --from <svg>`**. All `website/data/` + `mvp/scripts/`
changes uncommitted. This is the current served `aop_trail_network.geojson`.

**App label layer now shows non-numeric names (2026-05-29).** The data carried
`name='Area 51'/'JW2'/…` correctly, but the `aop-trail-network-labels` symbol layer
filtered `['has','trail_number']` and rendered `['get','trail_number']` — so the 9
named-but-unnumbered trails never showed a label in the app. Changed to filter
`['to-boolean',['get','name']]` + render `['get','name']` (labels by name string;
numeric trails still show their number since `name==number`; roads/unnamed have
name=null → unlabelled). Verified in-app: labels layer renders, all 9 non-numeric
names present in source; `playwright_verify_sfwda_trace.py` PASS. (`website/index.html`.)

**Hand-set stroke colours are now the difficulty authority + orange = roads
(2026-05-29).** The user recoloured every trail green/blue/black in Affinity and
asked why greys persisted. Cause: the importer **threw the SVG stroke colours
away** and re-derived difficulty from markers + number-band, so any hand-coloured
trail with no marker (the JW/Riot Hill/Pretender named trails) went grey. Fix in
`import_trace_svg.py`: new `_parse_color` (reads `style="...stroke:rgb()/#hex/named"`
— Affinity writes `style`, not `stroke=`) + `_stroke_class` (nearest-RGB-anchor →
easy/moderate/difficult/road/None). The user's colour now wins; markers/band only
fill what was left uncoloured. **Orange `#f25e0d` = ROADS** (user's call), not a 4th
difficulty: orange features get `kind:"road"`, `difficulty:null`, and are skipped by
marker number/difficulty inheritance + band-guessing (so a road near a marker doesn't
become "trail 22"). `assign_colors` paints roads orange, trails by difficulty.
`export_trace_svg.py` now treats the baked `color` as authoritative (roads re-export
orange). Result on `aop_trail_network_2025_edited_3.svg` (20:42): **115 trails (36
easy / 42 moderate / 37 difficult, 0 grey) + 4 roads**; export strokes 36/42/37/4;
`playwright_verify_sfwda_trace.py` PASS; overlay shows orange roads by the Buggy
Entrance. NOTE: third near-identical filename — `aop_trail_network_2025_edited_3.svg`
(20:42) is the colour-final one; supersedes both `edited_3` (20:20) and `edit_3` (20:31).

**edit_3 imported = golden data (2026-05-29).** NOTE two near-identical filenames:
`aop_trail_network_2025_edited_3.svg` (20:20) was a first save; the authoritative one
is `aop_trail_network_2025_edit_3.svg` (20:31, 19 `?`) — import THAT. (I imported the
20:20 file first by mistake; the user corrected me.) `import_trace_svg.py` → 119 trails
/ 104 named / all 9 string names;
`snap_trim_trails.py` found **0 to trim, 0 to snap** — the user's manual reconnections
already closed every junction at ≤18 m. **3 honest gaps remain**: two unnamed (74 m,
91 m) + trail `9` end (18.2 m, just over cutoff). Difficulty 29 easy / 39 mod / 29 diff
/ 22 grey. Re-exported `aop_trail_network_2025_edit.svg` from the golden network +
overlay `brain/output/net_2025_difficulty_overlay.png`. Verifier note: bumped the
`playwright_verify_sfwda_trace.py` page-load wait 15s→30s — full headless load runs
~10s (rectified imagery + all layers), 15s was a flaky budget; app loads with 0 errors.
PASS. Still uncommitted.

**Merged network re-grouped to Derived layers (2026-05-30).** The
`showAopTrailNetwork` toggle moved out of `External reference` into `Derived
layers` in `website/index.html`: the merged gold network is a product we
*computed* from the SFWDA raster, not an external feed, so it belongs beside the
other derived outputs (land cover, contours, boundaries, synthetic activity) per
the `source_layers.md` provenance grouping. The raw `SFWDA traced trails/markers`
prototypes stay in `External reference` next to the raster they trace against.
DOM-only move — `sectionInputs()`/`SECTION_RUNTIME` are containment-driven, so the
network's per-section export now lands under derived-layers automatically; toggle
ref, layer-visibility wiring, data fetch, and presets all key on the element ID
and were untouched. `playwright_verify_sfwda_trace.py` PASS. `research/viewer.md`
inventory + provenance prose updated in the same pass. Uncommitted.

### Still open
- **Resolve the blue-circle "1"** band-flag near the Buggy Entrance (info/start
  marker vs trail?) — one human glance at the sheet.
- **8 trails with `unjoined_gaps`** (esp. 1, 50, 54): same-number markers too far
  apart for a confident local join. Either the trace skeleton is broken there, or
  the markers are genuinely scattered (trail 1's "1" labels appear all over). Left
  as honest gaps — needs field/imagery confirmation, not a bigger cap (which just
  re-introduces false sprawl).
- **Wire `sfwda_numbered_trails.geojson` into the viewer** (toggle + `trail_number`
  label layer) — data ready; index.html wiring owned by the trace effort.
- [DONE] Markers numbered (stage 5, 117/124) + contiguous numbered trails (stage 6).
- [DONE] Full high-zoom read; 116/117 numbers in difficulty band.
- [DONE] Loose-end rejoin + local-path cap (no false sprawl); overlay verified.
- [DONE] Verify-by-observation — `playwright_verify_sfwda_trace.py` PASS + overlay.
