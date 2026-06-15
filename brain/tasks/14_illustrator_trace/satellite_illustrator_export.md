# Satellite 9-patch → Illustrator hand-trace export (+ round-trip)

Started: 2026-06-14
Status: SHIPPED + **first real Affinity round-trip ingested** (2026-06-14, verified
by observation — see "First real round-trip" below: 130 trails / 26 waypoints / 6
buildings, importer hardened for Affinity's export). Export + import originally
verified by observation. **Council-cleared**
(Witness · Quartermaster · Mason clear; Warden clear-in-isolation — the andon was
on a concurrent session's commingled tree, not this work; receipt
`brain/output/council/illustrator_trace_export.md`). Mason andon → fixed: the
importer now carries full gold props forward (provenance-preserving re-merge).
GIT (observed 2026-06-14): the **user committed all the code** — `website/`+`mvp/`
(importer, waypoints + facility-pin layers, Shower House merge, `v86` bump) is in HEAD
as the user's own commit **`59e4686`** (`git diff HEAD -- website mvp` empty; no agent
touched git; no attribution trailer). That commit is subject-titled "v84" though its
content is `v86` and it commingles the trace/landcover/v83 sessions — the user's commit
+ message, left as-is. Only the brain records remain uncommitted. No `.claude/.council-cleared`
marker needed now (the committed code shows an empty diff, so the Stop hook has nothing
material to gate). Full council (incl. waypoints + facility-label increments) cleared —
see `brain/output/council/illustrator_trace_import.md`.

The user wants to hand-trace the AOP satellite over the real imagery in Adobe
Illustrator, refining the gold trail network and placing waypoints/buildings, then
re-import — using the **layer names** as the truth. Their words:

> "make a export of the satellite map 9 patch for illustrator hand tracing.
> include gold trails / waypoints / buildings. I will edit and we will make gold.
> the names need to be the layer names. I will edit in illustrator and on
> re-import we use those."

This is the satellite + Illustrator sibling of the paper-map / Inkscape extraction
(`tasks/20_deferred/paper_map_trail_extraction.md`). Same round-trip idea, new
backdrop (NAIP satellite, not the SFWDA paper map) and a UTM frame instead of the
mesh warp.

## What ships

Two scripts, mirroring `export_trace_svg.py` / `import_trace_svg.py`:

- `mvp/scripts/export_illustrator_trace.py` → writes
  `brain/output/illustrator_trace/aop_satellite_trace.svg` (~9.2 MB) +
  `satellite_9patch.jpg` (standalone backdrop). Open the SVG in Illustrator. Each
  trail group also carries `data-fid` (its stable gold id) so re-import can
  re-merge provenance even after a rename.
- `mvp/scripts/import_illustrator_trace.py` → reads the edited SVG back to
  GeoJSON. Default writes `website/data/aop_trail_network.geojson` (the gold
  network); `--all` also emits `aop_waypoints_traced.geojson` +
  `aop_buildings_traced.geojson`. **Provenance-preserving:** each trail's edited
  geometry + name are the new truth, but its other gold props (`color`,
  `maturity`, `permission`, …) are carried forward from the prior gold feature it
  matches (by `data-fid`, then name) — a round-trip does NOT strip provenance.
  A user-drawn-new trail (no match) gets thin "needs review" provenance.

Run, edit, re-import:
```
python3 mvp/scripts/export_illustrator_trace.py
# … trace / refine / rename layers in Illustrator, save SVG …
python3 mvp/scripts/import_illustrator_trace.py path/to/edited.svg
python3 mvp/scripts/export_gold_trail_network.py   # re-stamp the gold _meta
```

## The SVG

Four `<g>` layers, top → bottom: **Satellite** (locked NAIP ortho), **Buildings**
(5 in-park footprints), **Waypoints** (5 named point POIs), **Gold Trails**
(120 lines, coloured by difficulty). The category layers are the ONLY groups.

**Each feature is ONE named geometry OBJECT — a `<path>` or `<circle>`, no wrapper
group, NO drawn text.** The name is the object name, written in every channel an
editor surfaces: `id` (Illustrator's `_xHH_` Layers-panel name + SVG round-trip),
`inkscape:label` (Inkscape), `serif:id` (Affinity), `<title>` child. So "Front
Office" is the polygon object itself, named — not a text item on the artboard
(the user's 2026-06-14 correction: *"the Front office should be a polygon named
correctly as a object name not a physical document object"*). Verified: the SVG
contains **0 `<text>`/`<tspan>` elements** and 0 wrapper groups inside the category
layers. Unnamed trails carry their feature id (`sfwda-N`) as the placeholder
object name to rename.

## Data sources

| Layer | File | Notes |
| --- | --- | --- |
| Satellite | `mvp/cache/imagery/naip_2023_9patch.tif` | NAIP 2023, 4-band, **EPSG:26916** (NAD83/UTM 16N), 3996×3742 px @ 1.525 m/px. Gitignored cache. |
| Gold Trails | `website/data/aop_trail_network.geojson` | 120 LineStrings, `maturity:gold`, `color`+`difficulty`+`name`/`trail_number`. |
| Buildings | `website/data/aop_buildings.geojson` | 5 in-park footprints (665, 889 Ellis Cove, Front Office, Farmhouse, Pavilion). |
| Waypoints | `gold_aop_waypoints_traced.geojson` (the SERVED set) | **Re-sourced 2026-06-14** — was `silver/gold_publish` POIs + `bronze_aop_editor_seed_pois` (pre-trace stubs holding only the user-deleted "AOP Pavilion"). The export now sources the same served gold the viewer draws and the import writes, so the round-trip is faithful (24 waypoints incl. RV sites/cabins/comp pads/entrances/★ POIs). Ellis kept; off-park Tate/Bible/Gilliam are bronze-only and stay out. |

## Frame / projection (the load-bearing part)

The SVG frame **IS the raster's own CRS** — UTM 16N metres, origin at the raster
NW corner (read from the GeoTIFF `ModelPixelScale`/`ModelTiepoint`), `x = E − E₀`,
`y = N₀ − N`. Because the frame is the raster grid, vectors land 1:1 on the imagery
with **no raster resampling** (full pixel fidelity) and the `<image>` places at the
pixel box. Vector lng/lat → UTM is done with a self-contained transverse-Mercator
series (GRS80, lon₀ −87°, k₀ 0.9996) — **no GDAL/pyproj on this machine** (Docker
down too). The projection params live in the SVG `<metadata>` so import inverts in
lock-step. Datum note: vectors are WGS84, projected with NAD83/GRS80 params — the
~1 m CONUS datum slip is sub-pixel at 1.5 m/px and accepted.

**Shared frame (2026-06-14):** the raster-read + backdrop-embed + projection
`<metadata>` was extracted into a `RasterFrame` class in `export_illustrator_trace.py`
so the sibling vegetation exporter (`export_landcover_svg.py`,
`tasks/01_mvp/_done/landcover_layer.md`) reuses the exact same UTM-16N frame instead
of re-implementing it. This exporter's `main()` now calls `RasterFrame` too. The
refactor is **output-neutral**: the HEAD pre-refactor script and the refactored
script bake `aop_satellite_trace.svg` to the **identical md5** on the same inputs.
(A fresh bake differs from the *committed* SVG only because a concurrent session
edited this exporter's input `aop_trail_network.geojson` — independent of the
refactor; verified by the council Witness, 2026-06-14.)

## Verified by observation (2026-06-14)

- **Projection:** forward∘inverse round-trips sub-mm; the documented 9-patch bbox
  falls fully inside the raster frame (raster is slightly larger than the AOI).
- **Alignment:** building footprints sit on real structures and the pavilion
  marker in the staging field; the trail mass sits on the wooded park ridge
  (`brain/output/illustrator_trace/_verify_buildings_3x.png`, `_verify_overlay.png`).
  This is gross registration confirmed by eye — at 1.5 m/px a footprint is a few
  pixels, so "on the structure" is what the image proves, not pixel-exact rooftop
  registration.
- **Round-trip:** export → import (in memory, source file untouched) gives
  120/120 trails, 0 vertex-count mismatches, **max vertex error ~0.91 cm** (the
  2-decimal metre rounding in the path `d`), 100/120 names exact (the 20 are the
  genuinely-unnamed trails on their placeholder id), waypoints 5/5 and buildings
  5/5 names exact. **Provenance carry** re-verified after the council fix: all 120
  re-imported trails keep `maturity`/`color`/`permission` (props re-merged from the
  prior gold by `data-fid`). `ai_escape`/`ai_unescape` round-trips incl. spaces,
  digits, hyphens, `#`, `/`, and a leading-underscore name (`_15`).
- **SVG structure:** 4 layers, 1 embedded `<image>`, every feature group carries
  all three name channels (0 missing).

## First real round-trip — Affinity Designer (2026-06-14)

The user hand-traced in **Affinity Designer** and dropped the edited export at
`brain/import/trace_upload/aop_satellite_trace.svg` (+ the `.afdesign` master).
Affinity's SVG export differs hard from the generated one; the importer was
hardened to ingest it (the card's "confirm against the first real edited file"):

- **`<metadata>` stripped** → `load_meta` falls back to the original export's frame
  (deterministic: same raster + fixed UTM params). **Frame is intact — no rescale:**
  Affinity rounded the viewBox (`6092.6`→`6093`) but did NOT rescale geometry, so the
  frame applies 1:1. Evidence: the unedited originals reproject onto HEAD's committed
  geometry at the SVG's own quantization floor — the path `d` carries 2-decimal-metre
  coords, so a vertex returns within **~1–2.4 cm** of HEAD (sub-pixel at 1.5 m/px).
  Larger per-vertex deltas are the user's **real hand-edits**, not frame error (e.g.
  Ground Control moved ~1 m; trail 67 + two others changed vertex counts). *(The
  separate **0.7 cm** figure is the importer's in-memory self-round-trip — export→
  reimport without saving — NOT a measurement of the committed gold file; don't
  conflate them.)*
- **Names moved onto wrapper `<g>`s.** Affinity wraps every *moved/new* object in
  `<g transform=… serif:id="Name">` with the name on the wrapper, geometry (no name)
  inside. `walk` now carries an **inherited name** down to the leaf and composes the
  wrapper transform, so grouped features (Front Office, Shower House, all new
  waypoints) keep their names instead of importing as `None`.
- **Layer match.** `collect_layer` also matches `serif:id` + the dash-id (Affinity
  renamed `id="Gold-Trails"`, kept `serif:id="Gold Trails"`).
- **Provenance w/o `data-fid`** (Affinity strips `data-*`): match order is now
  data-fid → exact name → name-as-prior-id (unnamed `sfwda-N`) → **leading trail
  number** (carries gold lineage through a rename like `Launchpad`→`1 Launchpad`).
- **Number-prefix normalization.** The export names a trail by its plain name
  (`Launchpad`); the user re-prefixed the number for legibility (`1 Launchpad`).
  The viewer label already composes `<n> name`, so the importer strips a leading
  `<trail_number> ` → stored name reverts to `Launchpad`, label renders `1 Launchpad`
  (no `1 1 Launchpad`). Stable round-trip.
- **Stray-POI sweep.** Waypoint `<circle>`s are swept from **every** editable layer,
  so two entrance pins drawn into the Gold Trails layer (`Jeep Entrance`,
  `Buggy Entrance`) are ingested, not silently dropped.

**Ingested (verified by observation):** `aop_trail_network.geojson` = **130**
trails (120 gold-provenance carried incl. all 8 renamed, **10** new user-traced —
9 unnamed + the de-identified long-67), `aop_waypoints_traced.geojson` = **26**
named POIs, `aop_buildings_traced.geojson` = **6** (incl. moved Front Office +
new Shower House). The live viewer ingests all 130 and renders them with clean,
un-doubled labels, **0 fatal console errors** (`brain/output/verify_ingest_viewer.py`
PASS, 195 trail feats rendered); the satellite overlay shows correct registration +
sensible placement (`brain/output/illustrator_trace/_verify_ingest.png`,
`_verify_ingest_camp.png`).

**Trail 67:** the user split it — a short 14-vertex segment keeps `67` (gold), the
long 65-vertex original they de-named in Affinity → imports as a blank/unknown new
trail (their call: *"the short is 67 the long should be blank/unknown"*).

**Re-import is read-modify-write on `aop_trail_network.geojson`** (it reads the live
gold as the provenance baseline), so run it **once against the committed baseline** —
re-running on its own output drifts provenance. To redo: restore from HEAD first
(`git show HEAD:website/data/aop_trail_network.geojson > …`), then import once.

**Wired into the read viewer (2026-06-14, user: "I am not seeing it in the map"):**
The new POIs were INVISIBLE for two reasons — (1) the service worker precaches the
data files and only refreshes on a `VERSION` bump (so the cached app served the old
v83 data), and (2) the waypoints had **no layer**. Fixed:
- **Waypoints** → new `aop-waypoints` source + `aop-waypoints` (circle) +
  `aop-waypoints-labels` (symbol) layers in `viewer_core.js` (mirrors the
  trail-network/water-points pattern), reading `aop_waypoints_traced.geojson`,
  shown in every preset. Added to the `sw.js` `DATA_ASSETS` precache.
- **Shower House** → merged into the WIRED `aop_buildings.geojson` (NOT a swap — a
  swap would strip the existing 5 buildings' FEMA/ORNL address+facility provenance);
  added as one raw-zone feature (the other 5 untouched). The user's refined Front
  Office *geometry* was left for later (the existing footprint already renders).
- **Cache bump** `v83`→`v84` (`sw.js` `VERSION` + `index.html` `#appVersion`) so the
  new trail/waypoint/building data is served past the cache-first SW.
- **Verified by observation:** `brain/output/verify_waypoints_layer.py` PASS on
  `:8001` — `aop-waypoints` + labels exist, **26/26 render**, Shower House present
  (6 buildings), 0 fatal console errors; `_verify_waypoints_live.png`. `node --check`
  clean on `viewer_core.js`.

**Building name labels (2026-06-14, user: "the farmhouse office pavillion shower
house need labels … maybe a pin on top of the polygons"):** a polygon can be labelled
directly (a symbol layer drops the name at the centroid), but at park zoom a bare
floating label is hard to tie to a small footprint — so a **pin + name** reads better.
Added `aop-facilities` (a point source DERIVED in JS from each `aop_facility===true`
building's `centroid_lng/lat` — a circle can't sit at a polygon centroid, it draws at
every vertex) + `aop-facility-pin` (rust `#8a4b2a` marker, distinct from the blue camp
waypoints) + `aop-facility-labels` (name, `text-allow-overlap` so the 4 key anchors
never declutter away). Covers **Front Office, Farmhouse, Pavilion, Shower House**; the
two private Ellis Cove houses stay as the dark presence boxes (their data says "private
— presence only, not a destination"). No new data file (derived from the wired
buildings). Cache bump `v85`→`v86`. **Verified on `:8001`:** 4/4 pins + 4/4 names
render, 0 fatal errors, `node --check` clean (`_verify_facility_labels.png`).

**Off-park cemeteries de-promoted from gold (2026-06-14, user: "off park
cementaries should not have made it to gold. they need to be bronze. we got what
we needed from the raw cementary data"):** the trace swept **all four** county
cemeteries into the gold waypoints (line 86 sources them from
`aop_cemeteries.geojson` markers), so the read viewer drew Tate, Bible, Gilliam,
**and** Ellis — when only **Ellis** (the in-park inholding, the one
`aop_inholding===true` feature) belongs on the published map. The three off-park
cemeteries are *bronze* reference and already live in `bronze_aop_cemeteries.geojson`
(`stamp_maturity.py` already models this: line 71 "cemeteries: Ellis gold + 3
bronze", line 93 "Ellis is per-feature gold"). Fix: removed the Tate/Bible/Gilliam
features from the served `gold_aop_waypoints_traced.geojson` (26→**23** features;
Ellis kept, with its in-park description). **A `vNN` cache bump is OWED (the user's
git gate, not the agent's — `completion_gate.md`):** the served data changed, so the
SW will serve stale cached data until `sw.js` `VERSION` + `index.html` `#appVersion`
are bumped `v89`→`v90` at commit time. (An earlier pass bumped them in the working
tree; the council Warden pulled andon — the bump is the user's — so it was reverted to
`v89` and left as this owed note.) Nothing lost — the three remain bronze in
`bronze_aop_cemeteries.geojson`. **Verified by observation** (`/tmp/verify_cemetery_fix.py`
on `:8001`, `/tmp/verify_cemetery_fix.png`): with the whole 9-patch framed (so an
off-park marker would paint if present), `queryRenderedFeatures` on `aop-waypoints`
returns cemetery-kind == `['Ellis Cemetery']`, zero stray Tate/Bible/Gilliam labels,
0 console errors.

**Durability gap CLOSED — cemeteries removed from the round-trip (2026-06-14, user:
"remove it from the export and the import ... I dont want it. cleanup. we need to be
able to edit the master ai sheet and re-upload as needed"):** the served-only fix
above would have been undone by the next re-import (the trace SOURCE still carried all
four). Now the pipeline itself is cemetery-free:

> **SUPERSEDED 2026-06-14** (see the "round-trip review + two bakes" addendum below):
> the waypoint export source described in the next bullet — `silver/gold_publish` POIs +
> `bronze_aop_editor_seed_pois` (Ellis seeding via publish, the `gold_publish` cross-session
> rename obligation) — **no longer applies.** The export now sources the served
> `gold_aop_waypoints_traced.geojson` (which already carries Ellis-only and excludes the
> off-park three), so there is no publish/editor-seed waypoint path and no `load()` path
> left to move. The cemetery-DROP-on-import (next-but-one bullet) is unchanged and still
> in force. History kept; read the bullet as of-its-date, not current.

- **`export_illustrator_trace.py`** — dropped `aop_cemeteries.geojson` as a waypoint
  source entirely. Ellis still seeds in because it is *also* a publish POI
  (`silver_publish.geojson`, `kind="poi"`, name "Ellis Cemetery"); Tate/Bible/Gilliam
  were cemetery-only, so they no longer enter the template.
  **Cross-session dependency (2026-06-14):** a concurrent session is promoting publish
  silver→gold (`silver_publish.geojson`→`gold_publish.geojson`). This export references
  the **HEAD** name (`silver_publish.geojson`) on purpose — not coupling to their
  uncommitted rename. When that promotion commits, this one `load()` path must move to
  `gold_publish.geojson`. (The import path — the actual re-upload workflow — does NOT
  read publish, so it is unaffected.)
- **`import_illustrator_trace.py`** — drops any waypoint whose name ends with
  "Cemetery" **except** "Ellis Cemetery". Matched on NAME, not `data-kind`, because
  Affinity strips `data-*` on export (so the kind tag is gone in the real master).
- **Stale medallion paths fixed in both scripts** (the round-trip was broken
  independently of cemeteries after the "medallion rename" commit `91a017e` renamed the
  served files): export now reads `gold_aop_trail_network.geojson` /
  `gold_aop_buildings.geojson` / `silver_publish.geojson` /
  `bronze_aop_editor_seed_pois.geojson`; import reads+writes
  `gold_aop_trail_network.geojson`, writes `gold_aop_waypoints_traced.geojson` and
  `bronze_aop_buildings_traced.geojson`. So a re-upload now lands on the SERVED files.

**Verified by observation (2026-06-14):** `python3 -m py_compile` clean on both
scripts; ran the fixed import against the real Affinity master
(`brain/import/trace_upload/aop_satellite_trace.svg --all`) — output: `trails: 130
(120 carried, 10 new), buildings: 6, waypoints: 23 (dropped 3 off-park cemeteries:
Tate Cemetery, Bible Cemetery, Gilliam Cemetery)`, Ellis kept. The served files were
backed up first and **restored** after the run, so the working tree still holds only
the Ellis-only served waypoints from the prior fix (no re-import output kept). `git
status` shows exactly: the two scripts + `gold_aop_waypoints_traced.geojson` +
`sw.js` + `index.html`.

**Found while verifying — authored waypoint copy does NOT survive a re-import (owed,
user's call):** the camp-waypoint **descriptions, `location_tag`s, and meaningful
`kind`s** (Hot Rocks Comp Pad's RC-crawl note, Firepit `#firepit`, Ellis's "private
inholding" blurb, cabin/rv-site/comp-pad kinds) are authored ONTO the served gold
file, not stored in the SVG — so the re-import flattens every `kind` to `poi` and
drops all descriptions. This is the same loss the *trails* avoid via provenance-carry
(merge prior gold props by `data-fid`/name). To make "re-upload as needed" truly
non-destructive, mirror that for waypoints: read the prior served
`gold_aop_waypoints_traced.geojson`, carry `description`/`kind`/`location_tag`/`link_*`
forward by name on import. Not done here (it is a separate enhancement, not part of
the cemetery removal) — flagged so a re-upload isn't run blind. **Also still owed:**
a re-imported file is written `indent=1` and without the `_meta` maturity block, so it
needs a re-stamp (`stamp_maturity.py` — itself carrying stale un-prefixed keys from the
medallion rename, a separate cleanup) before it matches the served compact+`_meta`
shape.

**Owed / next (left for the user's call):**
- **10 new trails need names + difficulty** (currently grey / needs-review).
- **Waypoints are a flat raw-zone marker layer** — richer POI-tab integration
  (blurbs, kinds/icons, grouping, search) is the next slice, gated by
  `northstar/source_register.md`. The trace `permission` is still "SFWDA — TBD".
- **Front Office** refined geometry from the trace not yet applied (cosmetic;
  existing FEMA footprint still renders).
- **Git state (observed):** the user **committed all the code** — `website/` + `mvp/`
  (the importer, the waypoints + facility-pin layers, the Shower House merge, and the
  `v86` bump) are in HEAD as the user's own commit **`59e4686`** (author Christopher
  Fryman; `git diff HEAD -- website mvp` empty). No agent touched git. Note: that
  commit's subject reads "v84" though its content is `v86`, and it commingles the
  trace, landcover, and v83 sessions — the user's commit + message, left as-is (not the
  agent's to rewrite). **Only the brain records remain uncommitted** (this card, the
  handoff, the verifiers/screenshots) — the user commits those when they choose.
- `AOP Pavilion` waypoint was deleted by the user (the Pavilion *building* stays).

## Open / next

- **The user edits, then we re-import.** `import_illustrator_trace.py` is built and
  self-round-trip-verified, AND now proven against the first real Affinity export
  (see above). The importer composes ancestor transforms, inherits wrapper names,
  and reduces curves to endpoints.
- **Raster choice.** NAIP 2023 (1.5 m/px, on-disk, offline) is the default. The
  viewer's sharper **TNMap 2022 6-inch** is online-tiles only (licensing =
  inspection, not republish) — swap in if the user wants more detail for tracing.
- **Waypoints are thin** (5). They're the only named point POIs that exist; the
  user will add/rename more by hand.
- **Promotion still owed** — same as the paper-map card: the trace is raw-zone,
  not `publish`; the gold network's `permission` is still "SFWDA paper map —
  permission TBD".

Sources/voice: `northstar/source_register.md`, `research/aop_data_bounds.md`,
`tasks/20_deferred/paper_map_trail_extraction.md`.

## Addendum 2026-06-14 — waypoint ★/authored-field durability (re-import carry-forward)

The "Owed" durability gap (a re-import strips authored waypoint fields) is **closed**.
User: *"fix the star durability … it needs to survive a db export or a re-import. save
it to the gold data directly. no shortcuts."*

Findings: (1) **DB export is a non-threat** — `gold_aop_waypoints_traced.geojson` is a
FILE-based gold layer; no DB/canonical bake regenerates it (only `publish.geojson` is
PostGIS-exported, and `bake_poi_stars.py` doesn't cover waypoints). So a DB export can't
strip the waypoint ★. (2) The real threat was `import_illustrator_trace.py`'s
`import_points()`, which rebuilt every waypoint from the SVG as bare `{name, kind}` —
stripping `highlight`/`description`/`location_tag` on a re-import (unlike trails, which
already carry provenance).

Fix (no shortcut — the ★ stays ON the gold feature; the pipeline preserves it):
- **`import_points()` is now provenance-preserving** (mirrors `import_trails`): a
  waypoint's edited geometry + name are the new truth, but its authored gold props
  (`highlight`, `description`, `location_tag`, tags, …) carry forward from the prior gold
  by name; SVG `data-kind` wins when present, else the authored kind is kept; an unmatched
  point is a thin new POI.
- **`preserve_unmatched_authored()`** keeps prior ★(`highlight:true`)/`#location_tag` POIs
  that AREN'T in the SVG — so a GPX-sourced pin added straight to gold (Gravity Gauntlet)
  survives a re-import. To DELETE such a POI, remove it from the gold file directly (the
  trace master isn't authoritative over hand-curated pins). Dropped cemeteries are never
  resurrected (`_is_dropped_cemetery` lifted to module scope + reused here).
- The export side is unchanged: the ★ is re-merged from prior gold on import, not stored
  in the SVG.

**No served-data / app change** — this is a build-pipeline script, so no `vNN` bump is
owed for it (the v93 bump already covers the served star data). Verified by observation —
`brain/output/verify_waypoint_star_durability.py` **14/14 PASS**: drives the REAL
`import_points` + `preserve_unmatched_authored` with a synthetic edited Waypoints SVG
against the actual current gold as prior — Hot Rocks keeps its ★ + description (geometry
updated), Gravity Gauntlet + the Firepit anchor are preserved, a brand-new POI stays
thin, a non-authored absent waypoint (RV Site 1) is NOT resurrected, and the live gold
file is untouched (read-only test). **Caveat (honest):** not run against the user's real
Affinity master (a binary; the in-repo `aop_satellite_trace.svg` is a stale 1-waypoint
stub that a real `--all` run would gut — the import is authoritative on existence for
non-curated points, so always re-import from the COMPLETE master).

Council-cleared core-three + Mason: `brain/output/council/waypoint_star_durability_20260614.md`.
Two NEXT notes from the council (neither blocking):
- **Real-Affinity round-trip not yet observed (Witness).** The carry-forward LOGIC is
  verified against the real gold via a synthetic edited SVG, but a genuine Affinity
  export→edit→`import --all` against a COPY of gold (exercising metadata-frame recovery +
  Affinity's wrapper-`<g>`/`data-*` stripping on the real POI set) is owed before treating
  end-to-end durability as fully observed.
- **Name-collision (Mason).** The by-name prior index is case-insensitive, so two distinct
  gold POIs sharing a lowercased name would both survive `preserve_unmatched_authored`. A
  pre-existing index property — a data-integrity note, not enforced.

## Addendum 2026-06-14 — round-trip review + two bakes before the next re-edit

User: *"review the trail point polygon export process. we have some data updates that
need to be baked into the gold data before I edit the sheet again and re-upload for
processing."* Reviewed all three geometry layers by observation; found the export was
out of sync with the served gold on two counts and baked the fixes. **Build-pipeline
only (export/import scripts) + one served-JS comment — no served-data change, no `vNN`
bump owed for the data; the comment edit is non-behavioral.**

Three-layer health at the start (verified, not narrated):

| Layer | Export reads | Import writes | State |
| --- | --- | --- | --- |
| **Trails** | `gold_aop_trail_network` ✓ | `gold_aop_trail_network` ✓ (provenance carried) | healthy |
| **Waypoints** | publish POIs + editor-seed = **1 stub** (AOP Pavilion, deleted) ✗ | `gold_aop_waypoints_traced` ✓ (★/desc/tag carried + unmatched preserved) | **export broken** |
| **Buildings** | `gold_aop_buildings` ✓ | `bronze_aop_buildings_traced` (**dead file the viewer ignores**, thin props, no provenance) ✗ | **import broken** |

**The waypoint danger:** a re-export gave a Waypoints layer with **1** circle, not the
**24** the viewer actually draws/`gold_aop_waypoints_traced` holds. Editing that sheet
and re-uploading would have dropped ~18 authored waypoints (RV sites, cabins, racetrack,
playground, entrances, Ellis) — only the ★/`#tag` ones (Hot Rocks, Gravity Gauntlet,
Firepit) survive via `preserve_unmatched_authored`.

**Bake 1 — export Waypoints now source `gold_aop_waypoints_traced.geojson`**
(`export_illustrator_trace.py`). Export + import now share ONE waypoint truth; the
pre-trace publish/editor-seed stubs are dropped (they only held the user-deleted "AOP
Pavilion" — not resurrected). Fresh export emits **Waypoints 24**.

**Bake 2 — import no longer strips the baked "<number> <name>"**
(`import_illustrator_trace.py`). The stored convention is now `1 Launchpad` (Goal.md:
*"make the proper fix so its Number Name"*; 80 trails store the number in the name). The
old strip would silently revert `1 Launchpad`→`Launchpad` on every round-trip. Removed
it; the edited name is authoritative verbatim. The now-false `viewer_core.js`
`trailDisplayName` comment (claimed the name stays "clean" + the import strips) was
corrected to match — comment-only, no behavior change.

**Bake 3 — buildings (polygon) round-trip wired into the served gold (DONE — the full
loop now works for all three geometry types).** User: *"I think we need the full loop
working for all types. right now you say polygons are broken. this is not ideal long
term."* The import wrote `bronze_aop_buildings_traced.geojson` — a file the viewer never
read — with thin `{name, kind}` (no FEMA/ORNL provenance), so polygon edits were silently
discarded. `import_polys` is now provenance-preserving and writes the served
`gold_aop_buildings.geojson` (carrying its top-level `_meta` maturity stamp + FEMA source
lineage). Design (mirrors trails/waypoints, plus a buildings-specific carry-unchanged
rule):
- **Provenance carried by name** — FEMA/ORNL address, occupancy, source, permission,
  `aop_facility`, the ★ `highlight` all carry from prior gold; the trace is authoritative
  on geometry, not on the source record.
- **Unchanged footprint → carried VERBATIM** (`_ring_unchanged`, 0.5 m tol). A re-import is
  a TRUE no-op for buildings the user didn't touch: geometry + `centroid_lng/lat` +
  `area_sqm/sqft` preserved EXACTLY. This is load-bearing — FEMA's source area is
  authoritative and the equirect re-measure differs from it by up to **11%** (665 Ellis
  123.49→109.82 m²), and the facility pin reads the stored centroid (`viewer_core.js`
  ~2485), so neither may be silently overwritten on an untouched building.
- **Edited / new footprint → recompute** centroid + area from the traced ring (reusing
  `import_fema_buildings.ring_centroid` / `signed_ring_area`, the SAME convention the
  served centroids were built with), so the pin and the editor Area row (`main.js` ~8893)
  track the edit.
- **Unmatched-preserve** — a curated building absent from the SVG survives (delete from
  the gold file directly, same rule as waypoints).
- **`_clean_ring`** — the export emits a polygon as the closing vertex explicitly PLUS a
  `Z`, so a round-trip double-closes (a 5-vertex footprint returns as 6); de-duping keeps
  the vertex-average centroid faithful (without it, unchanged buildings skewed up to
  ~3 m).
`bronze_aop_buildings_traced.geojson` is now ORPHANED (nothing reads or writes it) — a
cleanup candidate, left for the user (the agent didn't create it).

**Verified by observation:** `brain/output/verify_buildings_roundtrip.py` **22/22 PASS**
(read-only: 6 buildings carried with FEMA provenance; all 6 centroids/areas/geometries
preserved EXACTLY on the unchanged round-trip; a synthetic +50 m footprint edit moves the
centroid ~50 m and recomputes the area while keeping provenance; a building dropped from
the SVG is preserved; served gold untouched). Plus a REAL `import --all` on the fresh
export (backup/restore): `trails: 130 · buildings: 6 (4 facilities) · waypoints: 24` all
written to served gold, `_meta.maturity=gold` + FEMA address preserved, then restored —
`git diff -- website/data` clean. Regression: `verify_trace_roundtrip_baked.py` 24/24 +
`verify_waypoint_star_durability.py` still PASS. `py_compile` clean. **When the user runs
a real re-upload, all three served gold files change → owes the user's `vNN` bump then
(not now — the scripts don't change served data).**

**Verified by observation:** `brain/output/verify_trace_roundtrip_baked.py` **24/24
PASS** (read-only: drives the real export/import against the served gold as prior —
24 waypoints exported & round-tripped with nothing dropped, both ★ + descriptions +
kinds + `#tags` carried, AOP Pavilion not resurrected, off-park cemeteries out,
`1 Launchpad` survives verbatim, 80 number-name trails + 120 gold provenance preserved,
served gold untouched). Regression: `verify_waypoint_star_durability.py` still PASS.
`py_compile` both scripts + `node --check viewer_core.js` clean. Fresh faithful export
written to `brain/output/illustrator_trace/aop_satellite_trace.svg` (Gold Trails 130 |
Waypoints 24 | Buildings 6) — that is the sheet to open in Affinity for the next edit.
**Caveat:** the generated-export round-trip keeps `data-*`; the real Affinity master
strips them — that stripped-attr path is covered by `verify_waypoint_star_durability.py`,
and a genuine Affinity export→edit→`import --all` on a COPY of gold is still the owed
end-to-end observation (Witness note above).
