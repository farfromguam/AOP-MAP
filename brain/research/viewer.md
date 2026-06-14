# The AOP Viewer

TL;DR:
- `website/index.html` is the static MapLibre viewer -- one file, vendored
  libraries, no build step, runs offline.
- It shows three publishable layers from `publish.geojson` plus ~20 toggleable
  reference layers, has a feature search box, and an in-map POI/footprint editor.
- This is the viewer's home doc: the layer catalog. Per-layer build detail that
  has its own task card is linked, not duplicated.

#aop #viewer #maplibre #layers #reference

-----

## What the viewer is

`website/index.html` is the Website V1 surface from the build card: a static
MapLibre map, read-only over `publish.geojson` plus an editing mode. It is a
single HTML file with an inline `<script>`, MapLibre and Terra Draw vendored
under `website/vendor/`, and no build step. It reads GeoJSON straight from
`website/data/` and works with no network -- a hard requirement, see
`[[project-offline-requirement]]`.

Editing is a mode inside this viewer, not a separate app -- see
`[[feedback-editor-is-the-viewer]]`. The POI editor and the SFWDA alignment
editor both live here.

Serve it with `python3 -m http.server` from `website/`; see
`spinup/mvp_runbook.md`.

When a layer is added, changed, or removed in `index.html`, update the inventory
and detail below in the same pass. This catalog is only useful while it matches
the file.

## Layer inventory

Default-ON layers are marked; everything else is OFF until toggled, so the
viewer opens cleanly with no network. "Detail" points to the doc that records
how the layer was built.

The right panel groups layers by provenance, following `tasks/04_event_app/source_layers.md`:
`Source layers` holds the raw external rasters and parcel feeds we acquired
(9-patch AOI, satellite + NAIP imagery, lidar tile index, FEMA buildings, TN
cemeteries). `Derived layers` holds what we computed from those sources (land
cover, hillshade, contours, publishable boundaries, the merged AOP trail
network, simulated Saturday activity). `External reference` holds external
vectors and the SFWDA raster we trace against (USGS water/springs/roads, OSM
cluster, SFWDA paper map, and the raw SFWDA traced-trail/marker prototypes the
merged network was curated from).
`Map editor` holds first-party items curated in the editor and baked into the
export (event schedule POIs, publishable trailheads, visitor context callouts,
brand logos, drawn POIs). The brand logos (AOP badge + Rock Warblers) no longer
have their own file: they were merged into
`aop_visitor_context_callouts.geojson` as `kind=brand_logo` point features
(2026-06-05) and the viewer/panel split that one file back into a callout-polygon
source and a brand-logo icon source by `kind`. `User submitted` holds
contributor-shaped layers (submitted trails, activity hotspots).

| Toggle label | Data / source | Default | Detail |
| --- | --- | --- | --- |
| Publishable trails | `publish.geojson` (`core` -> `publish` views) | on | build card; `northstar/source_register.md` |
| Publishable boundaries | `publish.geojson` | on | build card |
| Publishable trailheads | `publish.geojson` | on | build card |
| Drawn POIs | `localStorage` + editor export | on | `tasks/01_mvp/poi_editor.md` |
| Asphalt roads (USGS National Map) | `aop_roads.geojson` | on | "Asphalt Roads Layer" below |
| Land cover (NAIP) | `aop_landcover.geojson` | on | "Land-Cover Layer" below |
| Land cover — 9-patch (NAIP) | `aop_landcover_9patch.geojson` | on | "Land-Cover Layer" below |
| Visitor context callouts | `aop_visitor_context_callouts.geojson` | on | `tasks/01_mvp/visitor_context_callouts.md`; "Visitor Context Callouts" below |
| 3D button | AWS Terrain Tiles | off | "Lidar Hillshade and 3D Terrain Layers" below |
| Lidar hillshade (USGS 3DEP) | AWS Terrain Tiles | off | "Lidar Hillshade and 3D Terrain Layers" below |
| Lidar contours (5 ft, 1m DEM) | `aop_contours.geojson` | off | `tasks/01_mvp/lidar_contour_pipeline.md`; "Lidar Contour Layer" below |
| Activity hotspots (GPX dwell) | `aop_activity_hotspots.geojson` | off | `tasks/01_mvp/activity_hotspots.md`; "Activity Hotspots Layer" below |
| Simulated Saturday activity | `aop_synthetic_activity_tracks.geojson` + `aop_synthetic_activity_hotspots.geojson` | off | `tasks/01_mvp/activity_hotspots.md`; "Simulated Saturday Activity Layer" below |
| AOP trail network (merged truth, colour by difficulty) | `aop_trail_network.geojson` | off | `tasks/04_event_app/paper_map_trail_extraction.md` |
| Event schedule POIs | `aop_event_schedule.json` | off | `tasks/01_mvp/event_schedule_layer.md`; "Event Schedule Layer" below |
| Satellite imagery (TNMap 2022) | TNMap XYZ tiles | off | "Satellite Imagery" below |
| USDA NAIP imagery (TN 2023) | USDA FPAC `USDA_CONUS_PRIME` tiles | off | "USDA NAIP Imagery / Tracing Source" below |
| 9-patch acquisition AOI | `aop_9_patch.geojson` | off | "9-Patch Acquisition AOI Overlay" below |
| Lidar tile index (USGS 3DEP) | `aop_lidar_tiles.geojson` | off | "Lidar Tile Index Layer" below |
| Streams & waterbodies (USGS NHD) | `aop_water.geojson` | on (A2) | "Hydrography / Water Layer" below |
| Springs & gages (USGS NHD) | `aop_water.geojson` | off | "Hydrography / Water Layer" below |
| Cemeteries (TN Comptroller parcels) | `aop_cemeteries.geojson` | off | `tasks/01_mvp/cemeteries_layer.md`; "Cemeteries Layer" below |
| Building footprints (FEMA USA Structures) | `aop_buildings.geojson` | on (A2) | `tasks/01_mvp/buildings_layer.md`; "Building Footprints Layer" below |
| OSM park polygon | `osm_aop_9patch.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| OSM tracks (highway=track) | `osm_aop_9patch.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| OSM service roads | `osm_aop_9patch.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| OSM named landmarks | `osm_aop_named.geojson` | off | `tasks/01_mvp/community_trails_import.md` |
| SFWDA paper trail map | `sfwda_aop_trail_map.webp` + `sfwda_raster_alignment.json` | off | `tasks/01_mvp/community_trails_import.md` |
| SFWDA traced trails (extracted) | `sfwda_traced_trails.geojson` | off | `tasks/04_event_app/paper_map_trail_extraction.md` |
| SFWDA traced markers (difficulty) | `sfwda_traced_markers.geojson` | off | `tasks/04_event_app/paper_map_trail_extraction.md` |

The viewer also has a feature search box and the POI/footprint/trace editor -- see
"Viewer capabilities" below.

### Default-layer audit

Recorded 2026-05-24 for Sprint 03 carryover Lane 4; updated 2026-05-27 for
the Trace hillshade and Satellite preset changes. Fresh load matches the `Park`
layer preset unless the browser has a saved custom preset override.

| Toggle | Fresh | Park | Topo | Trace | Satellite |
| --- | --- | --- | --- | --- | --- |
| Satellite imagery (TNMap 2022) | off | off | off | off | on |
| USDA NAIP imagery (TN 2023) | off | off | off | off | off |
| 9-patch acquisition AOI | off | off | off | off | off |
| Lidar tile index (USGS 3DEP) | off | off | off | off | off |
| Asphalt roads (USGS National Map) | on | on | on | on | off |
| Streams & waterbodies (USGS NHD) | on | on | on | off | off |
| Springs & gages (USGS NHD) | off | off | on | off | off |
| Cemeteries (TN Comptroller parcels) | off | off | off | off | off |
| Building footprints (FEMA USA Structures) | on | on | on | on | off |
| OSM park polygon | off | off | off | on | off |
| OSM tracks (highway=track) | off | off | off | on | off |
| OSM service roads | off | off | off | on | off |
| OSM named landmarks | off | off | off | on | off |
| SFWDA paper trail map | off | off | off | on | off |
| Land cover (NAIP) | on | on | on | off | off |
| Land cover -- 9-patch (NAIP) | on | on | on | off | off |
| Lidar hillshade (USGS 3DEP) | off | off | on | on | off |
| Lidar contours (5 ft, 1m DEM) | off | off | on | off | off |
| Publishable trails | on | on | on | on | off |
| Publishable boundaries | on | on | on | on | off |
| Publishable trailheads | on | on | on | on | off |
| Activity hotspots (GPX dwell) | off | off | off | off | off |
| Simulated Saturday activity | off | off | off | off | off |
| Event schedule POIs | off | off | off | off | off |
| Visitor context callouts | on | on | on | off | off |
| Brand logos (AOP & Rock Warblers) | on | on | on | on | off |
| Drawn POIs | on | on | on | on | off |

Audit read: the user's always-on set (`buildings`, `water`, `road`) is true
for Fresh/Park/Topo, with Trace intentionally keeping buildings and roads while
dropping water and land-cover for the hillshade/SFWDA/OSM workbench. Topo adds
hillshade, contours, and springs; Trace adds hillshade plus SFWDA and OSM
references while keeping trails / waypoints visible for tracing context.
Satellite is intentionally imagery-only, with the normal paper background as
the no-tile fallback.

## Viewer capabilities

### UI presets and layer tuning

Added 2026-05-21 and revised 2026-05-24. The viewer has a top-left control
cluster with search, the `Hot now` lanes, four preset buttons (`Park`, `Topo`,
`Trace`, and `Satellite`), a dedicated `3D` button, zoom shortcuts, and a
tabbed context card for Events / POI / About content.

- `Park` is the clean Muted Earth vector map: land cover, roads, publishable
  boundary/trails/trailheads, visitor context callouts, water (streams +
  waterbodies), and the FEMA building footprints (feature-list filter keeps
  the 4 in-park footprints on by default, the 198 outside-park collapsed
  off). Springs stay topo-only.
- `Topo` is the relief read of Park: same payload plus hillshade, lidar
  contours, and springs/gages.
- `Trace` is the workbench: lidar hillshade, SFWDA paper map, OSM
  tracks/service roads, OSM named landmarks, buildings, with land cover and
  aerial imagery off and high-contrast reference styling for tracing/review.
- `Satellite` is the 2022 TNMap aerial alone. Its fallback background is the
  normal paper color so tile gaps or load failures do not produce a black
  "nothing" state.

The `3D` button is independent of presets. Turning it on binds MapLibre terrain
and pitches the camera; switching between layer presets leaves the 3D state
alone.

Below the preset bar, a zoom row holds three **zoom presets** -- `Region`,
`Park`, and `Pavilion`. These move the camera only; they do not touch layers or
the layer presets (note the name collision: the `Park` *layer* preset and the
`Park` *zoom* preset are different controls). `Region` fits the documented
9-patch acquisition AOI, `Park` fits the published park boundary from
`publish.geojson`, and `Pavilion` flies in tight (zoom 17) on the 1010 Ellis
Cove Road building. All three zoom presets reset the camera to flat west-up
(bearing -90, pitch 0).

The map's `maxBounds` is set to the 9-patch (`REGION_BOUNDS`), so the camera is
leashed: users cannot pan or zoom out past where there is map data. `Region` is
therefore the widest the camera can go -- it fits the 9-patch edge-to-edge with
no margin. All viewer data (contours, water, roads, buildings, activity
hotspots, the visitor context callouts, publish layers) sits inside the
9-patch, so the leash hides nothing.

The right panel is the `AOP edit panel`. Selecting a layer row moves the inline
editor directly under that row, initialized from the layer's current MapLibre
paint values. It can change visibility, opacity, color, and width/size where
those controls are appropriate for that layer; controls that cannot represent
the current paint expression stay hidden. The 9-patch land-cover opacity and
SFWDA paper-map opacity/multiply/alignment controls live in their layer drawers,
not as loose rows under the section. `Snapshot preset` stores the current
toggles/sliders/paint state for the active preset in `localStorage`
(`aop_viewer_preset_settings_v1`). `Export settings` copies a JSON payload to
the clipboard with all four resolved presets plus the current state so the user
can paste preferred settings back into the session.

The right panel groups layers by provenance role. `Derived layers` contains
viewer-ready outputs generated from source material: land cover, the 9-patch
land-cover context, lidar hillshade/contours, the merged AOP trail network
(extracted/traced/merged from the SFWDA paper map), activity hotspots, the event
schedule overlay, and visitor context callouts. `Source layers` contains the
inspectable inputs and reference overlays: TNMap and USDA imagery, the
9-patch and lidar tile acquisition
indexes, USGS/FEMA/TN Comptroller context layers, OSM, and the SFWDA paper map.
The inline layer editor works in either group.

**Data-maturity tiers (2026-06-05).** The reworked one-model panel
(`website/js/panel.js`) additionally groups the tree by **maturity**: `Gold data`
and `Silver — pending review` sections sit above the provenance sections, each
editable group row carries a maturity chip, and a feature's Source tab shows its
served File + Tier. The tier lives in each served file's `_meta`
(`maturity`/`group`/`locked`), stamped by `mvp/scripts/stamp_maturity.py` and
recorded per layer in `website/data/_schema.json`. Full contract:
`research/data_maturity_tiers.md`.

The right panel is **collapsible**. Its `AOP edit panel` heading is a clickable
header bar (`.panel-header`) with a chevron button (`#panelCollapse`). Clicking
the header or the chevron retracts the panel body upward into the header,
leaving just the title bar so the map underneath is visible; clicking again
expands it back down. The body (`#panelBody`) animates via a `max-height`
transition. Default state is expanded.

The left control stack also hosts a two-lane `Hot now` control (`#hotControl`)
near the top of the stack, below search. The Event lane (`#hotButton`)
selects the live/imminent/next scheduled session and reuses the calendar
`gotoEventSession` popup path. The Trails lane (`#hotTrailButton`) turns on the
activity-hotspots layer and fits the hotspot target, so trail-first users do not
have to wait for the schedule to be empty. Card:
`tasks/02_edit/hot_control_two_lane.md`.

The bottom of the left stack is a two-column left-rail drawer wrapping Search,
Hot now, and `#calendarCard`. The 44 px icon column opens/closes each card; the
content column stacks open cards from the top. Drawer state persists in
`aop_left_rail_drawer_v1`. The Hot card auto-opens when hot data first arrives
unless a saved user-close state says otherwise. Dedicated verification:
`mvp/scripts/playwright_verify_left_rail_drawer.py`.

The right panel has a `Session tools` section for staff/test operations. It
drives a virtual event clock with date/time inputs plus `-1d`, `+1d`, `-1h`,
`+1h`, `Set`, `Now`, and `Clear` controls. The clock uses the same path as the
`?clock=YYYY-MM-DDTHH:MM` fixture and persists in `aop_virtual_clock_v1`; while
active the UI labels itself as a test clock. `Reset viewer` clears viewer-owned
localStorage (`aop_viewer_session_state_v1`, the virtual clock, left drawer,
calendar height, preset/settings overrides, feature visibility/tags, editor POIs,
visitor context overrides, and brand-logo overrides), closes transient popups and
highlights, and reapplies the first-run Park preset, default view, default tab,
and default drawer state.

Pocket-map reload state lives in `aop_viewer_session_state_v1`. It records the
active layer preset, active left context tab, search query, and selected event
session; drawer open/closed state and calendar body height stay in their existing
surface-specific keys. Landmark navigation remains a POI/search concern, not a
third Hot lane. Card: `tasks/03_event_app/_done/viewer_session_state_test_clock.md`.
Dedicated verification: `mvp/scripts/playwright_verify_session_tools.py`.

`#calendarCard` is a tabbed context card. The default `Events` tab renders
session rows from `website/data/aop_event_schedule.json`. The JSON is
intentionally schedule-first: rows carry `date_label`, `time_label`, `title`,
and a `location_tag` such as `#pavilion` or `#registration`; coordinates live
once under `locations`. The viewer resolves those tags into transient MapLibre
features at load time. Row selection turns on the default-off `Event schedule
POIs` overlay, moves the camera to the row's point/route, and opens a session
popup. The event title row (`#calendarToggle`) is now static; the drawer's Cal
icon owns open/close. The calendar body has a bottom resize handle
(`#calendarResizeHandle`) and persists height in `aop_calendar_height_v1`.

The `About` tab now carries the merged event and map-project context:
Rock Warblers Trail Blazing Invitational posture, AOP as private scale-RC land,
and the source-backed validation-loop promise. Public submissions are still
deferred to the later moderated app loop.

The third tab is `POI` (shipped 2026-05-25, card
`tasks/03_event_app/_done/left_panel_poi_browser.md`). It renders a grouped,
scrollable directory of places already drawn on the map: event anchors,
in-park buildings, observed trails, cemeteries, off-park visitor support, and
the user's drawn POIs. Each row shows a name, a 1-2 sentence visitor blurb,
and chips for kind / status / source. Click a row to fly the map, auto-enable
the source layer if it was off, and open a popup with the same fields. Rows
where the blurb is still owed render a yellow `info needed — revisit` chip;
the subtitle on those rows carries the explicit revisit note. Visitor copy
and revisit notes live in a single file, `website/data/aop_poi_index.json`,
so the source GeoJSONs (`aop_buildings.geojson`, `aop_cemeteries.geojson`,
`publish.geojson`) can be re-exported without losing authored copy, and so
gaps stay auditable in git rather than hiding as TODOs in code. The index
file's `owed_work` array summarizes every gap in one place.

A parallel `POI` section in the right edit panel (sits between
`Publishable` and `Map editor`) carries six group-level visibility toggles —
Event anchors, Buildings in the park, Trails, Cemeteries, Visitor support,
Drawn POIs. Each box is two-way bound to the source-layer toggle that
backs the group (`#showEventSchedule`, `#showBuildings`, `#showTrails`,
`#showCemeteries`, `#showVisitorContext`, `#showEditorPois`), so flipping
visibility from any surface stays in sync.

Verification: `mvp/scripts/playwright_verify_presets.py`,
`mvp/scripts/playwright_verify_event_schedule.py`,
`mvp/scripts/playwright_verify_left_rail_drawer.py`, and
`mvp/scripts/playwright_verify_session_tools.py`.

### Feature search

Added 2026-05-20. No new files, no dependency, fully client-side over the
already-loaded GeoJSON -- so it works offline.

- `indexFeatures()` registers every named feature as each layer's data loads;
  `buildSearchGroups()` collapses a multi-segment feature into one result framed
  by its full extent. ~127 named features index today.
- Trails are searchable: the publish `trail_centerlines` layer indexes as kind
  `trail`, and `searchDisplayName()` strips a trailing `(segment N)` suffix so a
  GPX-imported trail collapses to one result. Real named AOP trails become
  searchable automatically once they land in `publish.geojson`.
- OSM `highway=track` ways are wired for search, but all 47 in the 9-patch are
  unnamed in OSM so none surface yet.
- The box sits in the top-left control cluster with the preset buttons:
  substring match, dropdown of up to 8 results with a kind tag, arrow-key
  navigation, Enter selects, Escape clears.
- On select it `fitBounds`/`flyTo`s to the feature, auto-enables the feature's
  layer toggle if it was off, and flashes a yellow highlight pulse.
- Tag aliases (added 2026-05-23): `indexFeatures` accepts an optional
  `aliasesFor(props)` that adds extra search terms per entry. Event-schedule
  anchors pass their `location_tag` (e.g. `#pavilion`, `#registration`)
  through it, so a tag query lands on the right anchor. A leading `#` flips
  the matcher into alias-only mode -- a `#tag` query no longer surfaces every
  session that happens to mention the tag. Card: `tasks/02_edit/search_tags.md`.
- Stale-anchor refresh (added 2026-05-23, Sprint 02 Bucket D): when a
  feature-tag binding moves and the schedule re-resolves,
  `refreshEventScheduleSearchIndex` strips the prior event-schedule entries
  from `searchIndex` and re-indexes the fresh anchors before calling
  `buildSearchGroups`. So a newly-resolvable `#pavilion` anchor is
  searchable immediately, no reload needed. Card:
  `tasks/02_edit/named_feature_tagging.md`.
- Verified: `mvp/scripts/playwright_verify_search.py` -- 12/12 PASS on
  2026-05-20; 2026-05-23 extension adds 11 tag-search assertions, all PASS,
  0 console errors. The two pre-existing FAILs ("multi-segment trail
  collapses to one result") are unrelated -- they trip on the event-anchor
  "Trailhead - Saturday Afternoon segment 2" sharing a substring with the
  observed trail and reproduce identically on master before this diff.

### POI / footprint / trace editor

The viewer can draw, label, persist (`localStorage`), and export point POIs and
polygon footprints -- pavilions, buildings, staging, gates, hazards. As of
2026-05-21 it can also draw LineString traces over imagery. Trace features are
tagged `layer=editor_trace`, `confidence=draft`, and
`review_status=raw imagery trace; needs review before core/publish`. Full record:
`tasks/01_mvp/poi_editor.md`. PostGIS write-back is the open follow-up.

## Layer detail

### Publishable Layers

The three publishable layers -- trails, boundaries, trailheads -- come from
`website/data/publish.geojson`, exported from the PostGIS `publish` views by
`mvp/scripts/export_publish_geojson.sh`. The boundaries (`layer:park_boundaries`)
now hold two features: the parcel-derived AOP working envelope and the **Ellis
Cemetery inholding parcel** (id 5), copied from `aop_cemeteries.geojson`
(2026-06-05) so the carved-out inholding is itself a publishable boundary. The
copy carries the county-parcel provenance and `permission:publish`; the
USGenWeb-restricted burial roster is deliberately left out of the publish zone
(non-commercial only -- see `research/aop_ellis_cemetery.md`). Note this is now a
hand-curated feature in an otherwise PostGIS-exported file, so a future
`export_publish_geojson.sh` run would need the inholding added to the publish view
to keep it. How features earn their way into `publish` is the source-register
contract -- see `northstar/source_register.md`, `northstar/validation_loop.md`,
and the build card.

### Visitor Context Callouts

Recorded on 2026-05-21:

- **Shared file note (2026-06-05):** this file also carries the two brand-logo
  POINT features (`kind=brand_logo`: AOP badge, Rock Warblers), merged here when
  `aop_brand_logos.geojson` was retired. Both the host viewer (`main.js`) and the
  panel (`panel.js`) split the file by `kind` at load -- the callout
  fill/outline/label layers, search, and feature list take only the
  `visitor_callout` polygons; a separate `brand-logos` source + `brand-logos-icons`
  layer take only the logo points (all the drag/resize/cap/override/bake
  machinery is unchanged, just sourced from this file). `rebake_canonical.py`
  discriminates the two by `logo_id` presence so the logos keep their own
  `brand owner`/`decorative` provenance through a re-bake.
- `website/data/aop_visitor_context_callouts.geojson` is a small cartographic
  annotation layer with two support-town circles:
  `South Pittsburg / Kimball supply run` and `Monteagle plateau services`.
- The layer is default ON in the Park and Topo presets and hidden in Trace.
  It draws as muted ochre circle fills/outlines plus multiline labels, and has
  popups with direction, services, examples, distance/drive-time notes, and
  source summaries. Each popup also has `Directions`, `Food`, `Lodging`, and
  `Source` links.
- The SE `South Pittsburg / Kimball` circle label carries a regional-anchor
  line on the circle itself — `Chattanooga metro ~35 mi | ~45 min` — so the map
  orients a rider to the nearest metro, not just the supply town. The figure
  rounds the Ellis Cove Road park approach plus the ~30 mi South Pittsburg-to-
  Chattanooga I-24 route; it is an orientation estimate, not turn-by-turn
  routing.
- `Food` and `Lodging` links deep-link to the relevant town on the Marion
  County Tourism pages with a `#:~:text=` browser text fragment (the pages
  group listings by town heading but expose no anchor ids). The SE callout
  covers both of its towns with a two-fragment directive — food scrolls to
  `South Pittsburg` and also highlights `Kimball`; lodging scrolls to `Kimball`
  (the I-24 interchange hotel cluster) and also highlights `South Pittsburg`.
  The Monteagle callout scrolls to `Monteagle`. So the two callouts no longer
  land on the same page top. On a browser without text-fragment support the
  link still opens the correct page, just at the top.
- The callouts are searchable. Searching "South Pittsburg", "Kimball", or
  "Monteagle" jumps to the relevant circle and turns the layer on if it was
  hidden.
- Sources are embedded in the GeoJSON and summarized in
  `tasks/01_mvp/visitor_context_callouts.md`: AOP official pages, RiderPlanet,
  Marion County Tourism restaurants/hotels, and South Pittsburg-to-Monteagle
  and South Pittsburg-to-Chattanooga drive-distance references. Times are
  planning estimates, not routed/live traffic data.
- Verified with `mvp/scripts/playwright_verify_visitor_context.py`.
- Drag-to-move: as of 2026-05-23 the callouts are repositionable through the
  shared feature list panel (`brain/tasks/02_edit/poi_editor_v2.md`). Opening
  the Visitor context callouts drawer surfaces a 2-row list with a ✋ move
  button; clicking ✋ then clicking the map translates the polygon so its
  centroid lands at the click. The new geometry is keyed by `name` in
  `aop_visitor_context_overrides_v1` localStorage and replayed on next load
  via `applyVisitorContextOverrides` before `addSource`. The source geojson
  on disk is never mutated, so an override is always relative to the most
  recent shipped data.
- Baking overrides to disk (2026-05-30): `mvp/scripts/export_positioned_features.py`
  reads the right-panel "Export all" / section-Copy JSON and writes the moved
  geometry back into this seed file so positions survive a data reset. The same
  script bakes brand-logo positions + `icon_size`. Both layers are file-based
  (not PostGIS), so they are out of scope for `export_publish_geojson.sh`.
  Card: `tasks/04_event_app/misc_4.md`.

### Satellite Imagery (TNMap 2022)

Recorded on 2026-05-20:

- Source: TDOT / TNMap orthoimagery, wired as a raster XYZ source --
  `https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer/tile/{z}/{y}/{x}`.
  The service is a cached (`singleFusedMapCache`) Web Mercator map with standard
  LODs, so XYZ access works directly with MapLibre.
- TNMap says source imagery is 1 ft before 2022 and 6 in from 2022 onward; the
  AOP point query returns Marion County `TN_Ortho_Year = 2022`.
- A 6-inch AOP tile fetch returns `image/jpeg` 200. Treat as inspection-only --
  do not republish the tiles. Licensing must be settled separately before any
  imagery is exported.
- Toggle `Satellite imagery (TNMap 2022)`, default OFF so the viewer still opens
  with no network.
- Verified: `mvp/scripts/playwright_verify_satellite.py`.

### USDA NAIP Imagery / Tracing Source

Recorded on 2026-05-21:

- Source: USDA FPAC-BC-GEO public NAIP ImageServer
  `https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer`.
  The USDA public image-service index reports Tennessee as `TN_NAIP`, year
  `2023`, resolution `60 Centimeters`; the service itself is a cached image
  service with `/tile/{z}/{y}/{x}` access through level 17.
- Viewer: toggle `USDA NAIP imagery (TN 2023)`, default OFF. It is an online
  inspection/tracing layer and is not cached into `website/data/`.
- Trace workflow: the map editor now has `Trace line`, backed by Terra Draw's
  LineString mode. Exported trace features carry source metadata:
  `source_name=USDA NAIP public image service`, the ImageServer URL,
  `source_year=2023`, `confidence=draft`, and a review-needed status. They are
  raw candidates only; do not promote to `core` or `publish` without the source
  register and field/imagery review.
- 2025 note: USDA's 2025 Tennessee image-date index covers AOP with acquisition
  `2025-08-30` and 4-band (`M4B`) imagery. The Marion County 2025 archive was
  downloaded to the gitignored cache as
  `mvp/cache/imagery/ortho_1-1_hm_s_tn115_2025_1.zip` (~2.6 GB), but it ships
  as MrSID. The repo's current GDAL Docker image has no MrSID driver, so the
  2025 image is available for MrSID-capable desktop GIS work but is not yet a
  browser layer.
- Verified: `mvp/scripts/playwright_verify_satellite.py` -- the USDA toggle
  requested 24 tiles from `gis.apfo.usda.gov` and produced 0 console errors on
  2026-05-21.

### 9-Patch Acquisition AOI Overlay

Recorded on 2026-05-20:

- `website/data/aop_9_patch.geojson` is a copy of
  `brain/output/aop_9_patch_data_bounds.geojson` -- the 3-by-3 data-acquisition
  grid around the parcel envelope. The grid concept and cell coordinates live in
  `research/aop_data_bounds.md`.
- Toggle `9-patch acquisition AOI`, default OFF; the overlay draws the nine
  cells with their cell-code labels (`NW`, `N`, ... `C` ... `SE`).
- This is a data-acquisition planning overlay, not a trail or boundary claim.

### Lidar Tile Index Layer

Recorded on 2026-05-20:

- The 24 USGS 3DEP LAZ tile footprints are a viewer overlay at `website/data/aop_lidar_tiles.geojson`.
- Source: TNM products API query `datasets=Lidar Point Cloud (LPC)&prodFormats=LAZ&bbox=<9-patch>`.
- Each feature carries `tile_code`, `title`, `project`, `publication_date`, `size_bytes`, `size_mb`, `download_url`, `meta_url`, `source_name`, and `source_id`.
- Footprints come straight from each tile's `boundingBox`; they are inventory metadata, not measured coverage envelopes.
- The static viewer exposes the layer behind a toggle labeled `Lidar tile index (USGS 3DEP)` with fill, outline, and `tile_code` labels, plus a popup that links the LAZ download.

### Lidar Hillshade and 3D Terrain Layers

Recorded on 2026-05-20:

- The viewer renders a lidar-derived hillshade and a 3D terrain view directly from AWS Terrain Tiles (Terrarium-encoded raster-DEM). In the AOP block the upstream elevation is USGS 3DEP, which is lidar-derived; that is the closest "see the lidar" the viewer can show without downloading the LAZ tiles.
- Source: `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`, `encoding: 'terrarium'`, `maxzoom: 15`.
- 2D shading: MapLibre `hillshade` layer `lidar-hillshade`, toggle `Lidar hillshade (USGS 3DEP)`.
- 3D terrain: `map.setTerrain` with exaggeration 1.4 plus `map.setSky`
  atmosphere, controlled by the dedicated `3D` button. Drag with right-click /
  two-finger to tilt and rotate.
- Attribution shown in the viewer credits AWS Terrain Tiles (USGS 3DEP, SRTM, GMTED, ETOPO1).
- Verified with `mvp/scripts/playwright_verify_lidar_tiles.py` on 2026-05-20: 21 of 21 checks PASS, 109 AWS Terrarium tile requests during the run, 0 console errors.
- The hillshade and 3D terrain are global-DEM derivatives, not the locally-derived 1-meter DEM lidar product. The locally-derived contour layer below is the lidar-grade product; swapping the hillshade onto AOP-specific 1 m DEM tiles is tracked at `tasks/01_mvp/_readme.md` item #10.

### Lidar Contour Layer

Recorded on 2026-05-20; updated 2026-05-21:

- The viewer has lidar-grade contour lines at `website/data/aop_contours.geojson`,
  generated from the USGS 3DEP 1-meter DEM (lidar-derived bare-earth elevation).
- Build pipeline: `mvp/scripts/build_contours.sh`. It caches the DEM, clips it to
  the 9-patch, low-pass smooths the DEM, runs `gdal_contour` at a 5-foot interval,
  attributes each line, thins with a light Douglas-Peucker pass, repairs any
  contour crossings, and exports a WGS84 GeoJSON. GDAL runs via Docker
  `ghcr.io/osgeo/gdal:ubuntu-small-latest` (see `brain/spinup/mvp_runbook.md` for
  the toolchain and the macOS file-access constraint).
- Source DEM: `USGS_one_meter_x61y389_TN_27County_blk4_2015.tif`, native CRS
  `NAD83 / UTM zone 16N` (EPSG:26916), 1 m pixels. Clipped to the full 9-patch bbox
  `-85.782935283, 35.067164188, -85.717154097, 35.117928496`; the clipped DEM is
  cached at `mvp/cache/dem/dem_9patch.tif`.
- Contour interval: 5 ft (1.524 m). Indexed (major) contour every 25 ft.
- Smoothing (2026-05-20): raw 1 m lidar contours were jagged -- crinkle from lidar
  micro-noise plus angular corners from Douglas-Peucker. The DEM is low-pass
  smoothed first: resampled 1 m -> 2 m with a cubic-spline kernel
  (`gdalwarp -r cubicspline`), which strips the micro-noise before contouring. The
  smoothed DEM is cached at `mvp/cache/dem/dem_9patch_smooth.tif`. Sampling a
  *finer* interval would worsen the noise crinkle, not help -- smoothing the surface
  is the lever.
- Crossing repair (2026-05-21): contours are isolines and can never cross, but
  Douglas-Peucker simplifies each line independently and pushed tightly-spaced
  contours across each other on steep ground (~955 crossings at a 2 m tolerance).
  The fix: a light 0.5 m DP pass, then `mvp/scripts/repair_crossings.py`. Because
  DP only *deletes* vertices, a simplified line is an exact subsequence of its raw
  line; the repair detects crossings and restores the offending segments to raw
  (non-crossing) geometry, iterating until none remain. The last build repaired
  14 crossings to 0 in 4 iterations, restoring 130 vertices -- a negligible file
  cost. Tunable: `SIMPLIFY_M` at the top of `build_contours.sh`.
- Features: 2,831 LineStrings spanning 605-1820 ft (501 indexed). Each carries
  `elev_m` (metres), `elev_ft` (whole feet), and `idx` (1 = indexed/25-ft, 0 = minor/5-ft).
- Ship format: GeoJSON, ~14 MB. Under the ~25 MB threshold, so the layer ships as
  GeoJSON rather than PMTiles. The full-resolution attributed GeoPackage is cached
  at `mvp/cache/contours/aop_contours.gpkg` (gitignored, archival / QGIS use).
- Viewer: toggle `Lidar contours (5 ft, 1m DEM)`, default OFF. Layers `contours-minor`
  (thin), `contours-index` (bold 25-ft), and `contours-labels` (elevation labels on
  index lines). Clicking any contour shows its elevation.
- Zoom-dependent visibility (2026-05-21): contour detail tiers by zoom. At lower
  zoom only 50-ft index lines stay visible; the remaining 25-ft index lines fade
  in from zoom 15 to 16; fine 5-ft `contours-minor` lines fade in from zoom 16.5
  to 17.5. The fades are baked into the base layer paint and into the `Park` /
  `Topo` preset paints so they survive a preset switch.
- Tunable fade bands (2026-05-22): the contour layer editor carries two
  dual-thumb zoom sliders -- `25 ft index fade` and `5 ft detail fade`. Each
  thumb pair is the fade-start / fade-end zoom for that tier; dragging rewrites
  only the `z0`/`z1` stops of the `interpolate` expression and leaves the
  opacity outputs intact. HTML has no native two-knob range input, so the
  widget is two stacked `<input type="range">` elements with thumb-only pointer
  events (`.dual-range` CSS, `buildZoomBandRow`). A preset switch resets the
  bands to that preset's defaults; `Snapshot preset` captures them.
- Verified with `mvp/scripts/playwright_verify_lidar_tiles.py` on 2026-05-21: all
  checks PASS, 0 console errors. An independent crossing detector confirms 0
  different-elevation crossings.

### Activity Hotspots Layer

Recorded on 2026-05-22:

- `website/data/aop_activity_hotspots.geojson` is a derived layer built from the
  first-party Gaia GPX in `brain/import/Saturday_Afternoon_Activity.gpx`.
- Builder: `mvp/scripts/build_activity_hotspots.py`. It parses timestamped GPX
  trackpoints, respects GPX segment breaks, interpolates each point-to-point
  interval into a 15 m local meter grid, and weights each cell by elapsed time.
  A cell with more dwell time draws hotter.
- Current output: 65 hotspot cells / 130 features. The GeoJSON intentionally
  contains both Polygon cells and centroid Points: polygons are the auditable
  click/print layer, points feed the MapLibre heatmap and labels.
- Properties include `dwell_seconds`, `stop_seconds`, `slow_seconds`,
  `moving_seconds`, `visit_count`, `max_gap_seconds`, `source_files`,
  `confidence`, `permission=internal`, `publish_status=hold`, and
  `review_status=raw activity evidence; not a validated trail or facility`.
- Viewer: toggle `Activity hotspots (GPX dwell)`, default OFF, under `Derived
  layers`. Layers: `activity-hotspots-heat` (soft heatmap),
  `activity-hotspots-fill` (time-weighted cells), `activity-hotspots-outline`,
  and `activity-hotspots-labels` for the strongest cells. Popups show dwell,
  stopped/slow/moving split, visits, max point gap, source, and review status.
- Source discipline: raw activity evidence only. It may suggest staging spots,
  bottlenecks, technical crawl areas, or simply conversation/repair stops. Do
  not promote it to trails or public operational claims without review and a
  privacy decision.
- Verification: `mvp/scripts/playwright_verify_activity_hotspots.py` -- PASS,
  0 console errors on 2026-05-22.
- Roadmap: `tasks/01_mvp/activity_hotspots.md`.

### Simulated Saturday Activity Layer

Recorded on 2026-05-23:

- Source: `mvp/scripts/simulate_saturday_activity.py`, seeded with event schedule
  anchors, `publish.geojson` observed Saturday trail geometry, existing GPX
  hotspot coordinates, and OSM `highway=track` / `highway=service` linework
  from `website/data/osm_aop_9patch.geojson`.
- Generated data:
  - `brain/import/synthetic_saturday_activity.gpx`
  - `website/data/aop_synthetic_activity_tracks.geojson`
  - `website/data/aop_synthetic_activity_hotspots.geojson`
  - `website/data/aop_synthetic_activity_report.json`
- Current simulation: 72 pavilion-start synthetic users / 13,713 timestamped
  GPX points / 8 route personas. 70 / 72 tracks include OSM route-following,
  with 103.34 km counted along OSM line vertices across 19 OSM way IDs.
  Hotspot extraction output is 18 cells / 36 features from 72 synthetic
  sessions; it is ranked by stopped+slow time so OSM pass-through corridors do
  not render as a dotted-line hotspot.
- Behavior modeled: shared pavilion registration/start dwell, observed-trail
  travel, OSM spine/connector travel, repeated rock-crawl attempts at technical
  anchors, short reverse moves, social/regroup dwell, and varied route lengths.
- Overlap test: report records 7 planned anchors within 50 m of existing
  first-party GPX hotspot evidence; Playwright verifies extracted top synthetic
  cells overlap existing heat and cover the strong planned anchors.
- Viewer: toggle `Simulated Saturday activity`, default OFF, under `Derived
  layers`. Layers: `synthetic-activity-tracks`,
  `synthetic-activity-hotspots-heat`, `synthetic-activity-hotspots-fill`,
  `synthetic-activity-hotspots-outline`, and
  `synthetic-activity-hotspots-labels`.
- Source discipline: synthetic test data only. It is useful for testing the
  extraction and review workflow, not for validating trails or facilities.
- Verification: `mvp/scripts/playwright_verify_synthetic_activity.py`.

### Event Schedule Layer

Recorded on 2026-05-22:

- Source: `website/data/aop_event_schedule.json`, distilled from
  `brain/handoff/event_schedule_context_20260522.json`. The sister-event
  schedules are vocabulary references only; this is not an official AOP event
  calendar.
- Data shape: `locations` is a tag dictionary (`#pavilion`, `#registration`,
  `#observed-trailhead`, `#north-technical`, etc.). A session references
  `location_tag`, and optional `route_tags`, instead of embedding coordinates.
  `#registration` is an alias of `#pavilion`; `#pavillion` is accepted as a
  misspelling alias so future edits do not silently break.
- Viewer: the left calendar card (titled `Rock Warblers Trail Blazing
  Invitational`, subtitle `Friday, June 19, 2026`) renders 12 schedule rows from
  the JSON. The left context card carries three tabs: `Events` (the calendar),
  `POI` (left-rail browseable directory of places — shipped 2026-05-25 via
  `brain/tasks/03_event_app/_done/left_panel_poi_browser.md`), and `About` (merged
  event detail + Rock Warblers team copy). Selecting a row turns on the default-off
  `Event schedule POIs`
  overlay, flies to the tagged point or route, flashes the highlight layer, and
  opens a popup with date, time, location tag, status, and source vocabulary.
- Map layers: `event-session-routes`, `event-route-labels`,
  `event-anchor-points`, and `event-anchor-labels`. The static JSON is resolved
  into an in-memory GeoJSON source named `event-schedule`; no generated GeoJSON
  file is checked in.
- Source discipline: proposed event planning context only. Facility placement,
  route choices, and activity labels need AOP confirmation before moving into a
  publishable event layer.
- Tag-driven location resolution (added 2026-05-23, Sprint 02 Bucket D):
  `locations[#tag].coordinates` is now optional. When absent, the viewer
  resolves coordinates from a per-feature `#tag` binding maintained in the
  shared feature list panel (Buildings + Drawn POIs are taggable). The
  schedule ships with `#pavilion` having no `coordinates`; the viewer seeds
  `#pavilion` → the 1010 Ellis Cove Rd building on first load
  (`aop_feature_tags_v1` localStorage; one-time `aop_feature_tags_seeded_v1`
  flag). Aliases inherit through the same path — `#registration` resolves
  through `#pavilion`. Card: `tasks/02_edit/named_feature_tagging.md`.
- Verification: `mvp/scripts/playwright_verify_event_schedule.py` -- 14 new
  Bucket D assertions cover the seed, the lookup, the live re-bind, the
  per-row tag input rendering, and the camera flight to the resolved
  location. All PASS on 2026-05-23.

### Asphalt Roads Layer

Recorded on 2026-05-20:

- Source: USGS National Map Transportation MapServer `https://carto.nationalmap.gov/arcgis/rest/services/transportation/MapServer`.
- Layers queried over the 9-patch bbox: `29` Controlled-access Highways (10 features), `30` Secondary Highways (0), `31` Local Connecting Roads (28), `32` Local Roads (76), `33` Ramps (0). Total `114` paved-network features.
- Excluded by design: layer `35` 4WD Roads, layer `36` Closed Roads, layer `37` Trails -- those would not be asphalt.
- Importer: `mvp/scripts/import_usgs_roads.sh` (curl + jq, atomic write).
- Output: `website/data/aop_roads.geojson` -- each feature tagged with `road_class` (`controlled_access`, `secondary`, `local_connecting`, `local`, `ramp`) plus `name`, `mtfcc_code`, `tnmfrc`, and route designators.
- Viewer: toggle `Asphalt roads (USGS National Map)`, default-on. Stacked layers `roads-local-casing` + `roads-local`, `roads-connecting-casing` + `roads-connecting`, `roads-secondary-casing` + `roads-secondary`, `roads-ramp-casing` + `roads-ramp`, `roads-controlled-casing` + `roads-controlled`, plus a `roads-labels` symbol layer along the line. `secondary` and `ramp` classes are styled defensively -- the importer fetches them, but the current 9-patch envelope returns 0 features in those classes. Click any class for a popup with name, MTFCC, and route designators.
- Notable named features in-AOI: I-24, Ellis Cove Rd (the AOP access road), Ellis Rd, Battlecreek Rd, Fiery Gizzard Rd, Sweetens Cove Rd.
- Picked over TNMap MAJOR_ROADS (too sparse -- interstates and state highways only, misses county/park-access roads) and Overpass/OSM (would require per-way `surface=*` filtering and local TN ways are not reliably tagged for surface).

### Hydrography / Water Layer

Recorded on 2026-05-20:

- Source: USGS National Hydrography Dataset (NHD) `https://hydro.nationalmap.gov/arcgis/rest/services/nhd/MapServer`.
- Large-scale (high-resolution) NHD layers queried over the 9-patch bbox: `6` Flowline (85 features), `9` Area (1), `12` Waterbody (3), `0` Point (5). Total `94` water features.
- Importer: `mvp/scripts/import_usgs_hydrography.sh` (curl + jq, atomic write).
- Output: `website/data/aop_water.geojson` -- each feature tagged with `water_kind` (`flowline`, `water_area`, `waterbody`, `point`) and `water_class`, plus `name` (GNIS), `gnis_id`, `fcode`, `ftype`, `lengthkm`/`areasqkm`/`elevation`, `permanent_identifier`, and `nhd_layer_id`/`nhd_layer_name`.
- Class breakdown: `55` stream, `30` artificial_path (flow paths through wide water), `1` stream_river_area, `3` lake_pond, `4` spring, `1` gage.
- Named streams in-AOI: Battle Creek (the main creek through the AOP block, mostly modeled as artificial paths inside a 0.63 km² stream/river area polygon), Big Fiery Gizzard Creek, Kelly Cove Branch, Rogers Cove Branch, Sweden Creek, Tate Cove Creek. Named springs: Gilliam Spring, Bible Spring, Fish Trap Spring.
- Viewer: two toggles in `website/index.html`. `Streams & waterbodies (USGS NHD)` is default ON (Sprint 02 A2) in Park and Topo; it drives `streams` + `stream-labels` + `waterbody-fill`/`waterbody-outline` + `water-area-fill`. `Springs & gages (USGS NHD)` stays default off and is topo-only (drives `water-points` + `water-point-labels`). Click any stream/waterbody/point for a popup with class, NHD ftype/fcode, and length or area.
- Verified with `mvp/scripts/playwright_verify_water.py` on 2026-05-20: 28 of 28 checks PASS, 0 console errors.
- All NHD water features are raw-zone context. Before any are promoted into publish layers, attach a row in `source_register.sources` per `northstar/source_register.md` (USGS NHD is public domain; confidence: high for named perennial streams, lower for unnamed/intermittent; permission: public).
- The 1m-DEM lidar contour pipeline (`brain/tasks/01_mvp/lidar_contour_pipeline.md`) is the natural cross-check: where NHD flowlines and lidar drainage scars disagree, trust the lidar for micro-terrain.

### Cemeteries Layer

Recorded on 2026-05-21:

- Source: Tennessee Comptroller of the Treasury -- Marion County parcels, `TN_County_Parcel_Map` FeatureServer layer 35 (`Marion_Parcels`) -- the same service as the AOP boundary import.
- Importer: `mvp/scripts/import_marion_cemeteries.py` queries cemetery-owned parcels (`OWNER LIKE '%CEMETERY%'`) across the 9-patch bbox, normalizes each into a readable cemetery feature, joins a hand-curated burial roster where one is known, and writes `website/data/aop_cemeteries.geojson` -- 4 cemeteries, 8 features (one parcel polygon plus one centroid marker each, tagged `geom_role`).
- The four in-AOI cemeteries: Ellis (`110 008.04`, ~0.12 ac), Gilliam (`093 029.00`, ~2.91 ac), Bible (`093 003.00`, ~0.74 ac), Tate (`093 001.02`, ~0.70 ac). All class `05 RELIGIOUS`.
- Ellis Cemetery is the AOP inholding -- the interior ring (the hole) in the AOP working-envelope polygon, parcel `110 008.04` carved out of parent parcel `110 008.00`. Confirmed by point query and bit-identical geometry. Full evidence: `research/aop_ellis_cemetery.md`.
- Viewer: toggle `Cemeteries (TN Comptroller parcels)` in `website/index.html`, default off. Layers `cemetery-fill`, `cemetery-outline`, `cemetery-marker` (amber ring on the AOP inholding), `cemetery-label`. Cemeteries are searchable; the county owner-of-record name is indexed as an alias.
- Verified with `mvp/scripts/playwright_verify_cemeteries.py` on 2026-05-21: 25 of 25 checks PASS, 0 console errors.
- All cemetery features are raw-zone context. Before any promotion to publish layers, attach a `source_register.sources` row per `northstar/source_register.md`. The Ellis burial roster comes from a USGenWeb transcription with non-commercial terms -- keep it inspection-only until use is settled.

### Building Footprints Layer

Recorded on 2026-05-21:

- Source selected: FEMA USA Structures / ORNL,
  `https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/USA_Structures_View/FeatureServer/0`.
  The ArcGIS item is `Building Footprints (FEMA USA Structures)`,
  `https://www.arcgis.com/home/item.html?id=e9fc147eaeae4dcaa4e9ad9802c7b9c6`.
- Source review: FEMA returned 202 polygon footprints in the 9-patch and was
  selected. OSM `building=*` returned 11 ways and was not imported to avoid a
  duplicate ODbL layer. TNMap FEMA BLE building footprints returned 0 features
  in the AOI.
- Importer: `mvp/scripts/import_fema_buildings.py`. It first queries object ids
  over the 9-patch bbox, then fetches those ids in GeoJSON chunks because direct
  bbox feature queries rejected the parameters. It tags each footprint by whether
  its representative point falls inside the current AOP boundary.
- Output: `website/data/aop_buildings.geojson` -- 202 footprints: 166
  Residential, 24 Agriculture, 7 Unclassified, 3 Assembly, 2 Government. Four
  footprint centroids fall inside the candidate AOP boundary: 1010, 1033, 665,
  and 880 Ellis Cove Road.
- Viewer: toggle `Building footprints (FEMA USA Structures)`, default ON
  (Sprint 02 A2) in Park, Topo, and Trace. Layers `building-footprint-fill`,
  `building-footprint-outline`, and `building-footprint-aop-outline`; the
  inside-AOP outlines draw heavier. The feature-list panel keeps the 4
  in-park rows pre-ticked and the 198 outside-park rows collapsed under a
  default-off bulk toggle, so the on-by-default Park view only draws the
  in-park footprints unless the user expands the rest. Clicking a footprint
  opens occupancy, address, area, image date, validation method, and source.
  Addressed footprints are searchable.
- Verified with `mvp/scripts/playwright_verify_buildings.py` on 2026-05-21:
  all checks PASS, 0 console errors.
- Raw-zone context only. A footprint must be checked against imagery or field
  knowledge and linked to a source-register row before becoming a publishable
  park facility.

### Land-Cover Layer

Recorded 2026-05-21 (rebuilt the same day onto lidar + leaf-on imagery).
**Simplified 2026-06-14** to a single dissolved vegetation layer (see the
"Vegetation simplification" bullet at the end of this section).

- `website/data/aop_landcover.geojson` is the viewer's base ground cover.
  It is **classified** into a five-class coverage (`forest_deciduous`,
  `forest_evergreen`, `open_grass`, `open_meadow`, `open_bare`) but **ships**
  as one dissolved `vegetation` class: the two forest greens are merged and the
  three open/non-tree classes are dropped so non-tree ground reads as the base
  map paper. ~18 vegetation polygons (down from ~154 five-class). The five-class
  build below is the intermediate; the simplify step is the last pipeline stage.
- Two data sources, each used for what it is good at:
  - **USGS 3DEP lidar** -> a canopy-height model. Forest vs open is a height
    threshold, so the forest edge is crisp and per-pixel. Imagery alone cannot
    do this: leaf-off canopy texture works but blurs the edge, and leaf-on
    canopy is too smooth to threshold at all.
  - **USDA NAIP 2023** (June, leaf-on, 4-band R/G/B/NIR, 0.6 m, the no-auth
    `USDA_CONUS_PRIME` ImageServer) -> the colours: the evergreen/deciduous
    split and the open-ground colour quantisation.
- Build pipeline:
  - `mvp/scripts/build_canopy_height.sh [park|9patch]` -- USGS 3DEP LAZ tiles
    -> PDAL `hag_delaunay` (height above the ground-classified returns) -> grid
    the per-cell max height -> mosaic -> warp onto the NAIP grid. CHM cached
    gitignored at `mvp/cache/lidar/chm_{aop,9patch}.tif`. Runs via the
    `pdal/pdal` Docker image; the warp forces `-s_srs EPSG:6576` so GDAL does
    not geoid-shift the height values (the lidar CRS carries a NAVD88 vertical
    component).
  - `mvp/scripts/build_landcover.sh` -- downloads the NAIP ortho, ensures the
    CHM, then `classify_landcover.py` (NAIP + CHM -> 5-class raster) and
    `smooth_landcover.py` (Chaikin), polygonize, clip to the AOP boundary.
    GDAL via Docker per `spinup/mvp_runbook.md`.
- Classification, stage 1 -- forest vs open: forest = `CHM > 2.5 m`, a crisp
  per-pixel cut. The CHM is a stipple of crowns, so a morphological closing
  bridges the inter-crown gaps into a coherent mass and an opening drops lone
  trees / specks. ~81% forest in the park.
- Classification, stage 2 -- sub-classes from the leaf-on NAIP colour:
  - Forest split: evergreen is the darkest tail of the canopy (conifers read
    darker than leaf-on hardwood), stand-smoothed and cut at a percentile so
    it stays a coherent accent.
  - Open split: k-means RGB colour quantisation into three clusters, majority-
    voted into contiguous fields, ranked by greenness onto grass / meadow /
    bare. A relative colour ranking within one image, not absolute crop ID.
- Water is deliberately not classified -- the USGS NHD layer already carries
  hydrography.
- Viewer: layers `landcover-forest` (fill) + `landcover-forest-outline`,
  toggle `Land cover (NAIP)`, default ON. Since the layer now ships one
  `vegetation` class, the fill is a flat green (`#b8c1a1` Park / `#c0c6ad`
  Topo) with a same-family outline — the former MapLibre `match` on `class`
  collapsed to a flat colour in `viewer_core.js` when the data was simplified.
  (`main.js`/`panel.js` still carry the old five-class `match`; with single-class
  data it falls through to the same green — cleanup owed when the editor ports.)
- 9-patch extension (`aop_landcover_9patch.geojson`): the same pipeline over
  the full 3x3 acquisition AOI, so the viewer has land-cover context around the
  park, not only inside it. The NAIP ImageServer caps an export at 4000 px and
  the 9-patch is ~6 km wide, so that ortho is pulled at ~1.5 m; the CHM is
  built from all 24 USGS 3DEP lidar tiles. `classify_landcover.py` is
  resolution-aware (it rescales its windows from the geotransform pixel size),
  so the one classifier serves both builds. Build script:
  `mvp/scripts/build_landcover_9patch.sh`.
- The 9-patch layers `landcover-9patch-forest` (fill) + `-outline` sit at the
  very base of the stack, below the crisp park layer which draws on top.
  Toggle `Land cover — 9-patch (NAIP)`, default ON, with a drawer opacity
  control (default 55%). Because the park layer covers the park
  crisply, the control effectively fades only the non-park context. Bounds are
  deliberately separate from the park layer.
- Honest limits: the 3DEP lidar is 2015, so canopy is ~8 years older than the
  2023 imagery -- growth or clearing since is not captured; the CHM catches any
  tall object, so a large barn reads as a small forest patch; the open-ground
  colour split is a relative ranking, not crop identification.
- Raw-zone context -- attach a `source_register.sources` row (NAIP = USDA
  public domain; 3DEP lidar = USGS public domain) before any promotion.
- **Vegetation simplification (2026-06-14).** The user's call: combine the two
  greens into one vegetation layer and let every non-tree area read as the base
  map. `mvp/scripts/simplify_landcover_vegetation.py` keeps the two forest
  classes, dissolves them with a unary union, then caps per-polygon complexity
  (see the render-fix bullet below), re-tags every feature `class=vegetation`,
  and drops the three open classes. Park: 154→18 features; 9-patch: 3430→165. It
  is wired as the final step of both `build_landcover.sh` and
  `build_landcover_9patch.sh` (the 5-class export is kept in the gitignored cache
  `mvp/cache/landcover/*.5class.geojson`), so a pipeline rebuild stays simplified.
  This is a directed simplification of a *derived* layer — the 5-class source is
  recoverable from git + the cache + the pipeline — not banned limiting code
  (`ai_rules/no_limiting_code_mvp.md` defers the display call to the user).
  Committed as `da5d032 v79`.
- **Corner render fix.** The first pass dissolved the canopy into one
  ~28k-vertex / 282-hole polygon, which MapLibre's `fill` tessellation could not
  fully draw — the map's TR/BR/BL corners showed empty paper even though dense
  forest is there (the user checked against the satellite). The script now caps
  complexity after the union: drop interior holes below ~5000 m² + light
  Douglas-Peucker simplify, taking the worst polygon to 3976 verts / 47 holes
  (was 28107/282), coverage ±0.1%, natural edge kept (the outline still traces
  it — no viewer change). Committed as `692464b v81`.
- Verified with `mvp/scripts/playwright_verify_landcover.py` (updated to the
  vegetation contract) plus a fresh render agent on 2026-06-14: both layers carry
  only `vegetation`, retired sub-classes gone, one flat green fill, 9-patch at the
  base of the stack, both render; after the fix the previously-empty corners fill
  with a continuous canopy, stable across zoom, **0 console errors**. The
  verifier's own console-summary line did not flush under a temp-fs hang, so the
  0-errors observation comes from clean separate captures (receipt
  `brain/output/council/witness_vegetation_render.md`; shots
  `brain/output/veg_fixed_*.png` vs `diag_veg_*.png`). (The script's editor-only
  sections are guarded so it runs against `index.html` or `old_index.html`.)
  `sw.js`/`#appVersion` rode the v79→v82 contributor bumps.
- Build card: `tasks/01_mvp/_done/landcover_layer.md` ("Update: vegetation
  simplification"; "Update: corner rendering fix").

### Cartographic palette (Muted Earth)

Recorded on 2026-05-21:

- The viewer ships a unified "Muted Earth" palette -- a warm, desaturated,
  vintage park-map look the user chose. Paper background `#efe7d5`, forest
  `#b9c2a3`, trail `#9a5a32`, contours in tan-browns, water in muted blue-grey,
  roads in muted ochre, text in warm dark brown over warm off-white halos.
- It was a map-wide retune: every layer's paint in `website/index.html` was
  adjusted in one pass so the layers read as one map rather than a stack of
  independently-coloured overlays. POI editor category colours were muted to
  fit while staying distinguishable.

## Verification scripts

Viewer layers and capabilities have Playwright checks under `mvp/scripts/`
(`playwright_verify_*.py` -- satellite, lidar tiles, terrain, water, cemeteries,
land cover, community trails, SFWDA multiply, POI editor, search, trails). They drive the
real browser, exercise the toggles, assert layer visibility and network traffic,
capture screenshots into `brain/output/`, and fail on any console error. Run the
relevant one after touching `website/index.html`. Use `8001` as the default
Playwright preview port (`cd website && python3 -m http.server 8001`); use
`WEBSITE_URL=...` only when that port is occupied. `brain/output/playwright_eyes.md`
records why the viewer vendors its libraries instead of using a CDN.
