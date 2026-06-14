pages

http://localhost:8000  (and /index.html)
    - THE FRONT END — the clean day-of viewer

http://localhost:8000/schedule_editor.html
    - day before editor. should produce baked files 
    - event specific

http://localhost:8000/data_editor.html
    - week before editor. should produce baked files 
    - park specific

tester → NOT a page. A MODE on the read viewer, reached by url params:
    http://localhost:8000/index.html?tester=1
    (editor_is_the_viewer: V2 is V1 with more controls, not a fork. The test
     fixtures already ride URL params — ?clock= for the date offset.)
    - week before tester
    - has limited sidebar
    [x] date shifting feature clock=YYYY-MM-DDTHH:MM fixture (viewer_core.js).
    [x] lat long shifting feature → ?tester=1
    
    [ ] on-tester EDIT FAB (Locate + Edit side by side) — waits on the editor porting into the
        extracted read core (still in panel.js / old_index.html). The .tester class + the
        right:80px FAB slot are already reserved.
    full test link: /index.html?tester=1&clock=YYYY-MM-DDTHH:MM

Working:
http://localhost:8000/mapborder_compare.html



http://localhost:8000/old_index.html
    - legacy all in one page (parked, not deleted)


---

Data sources:

(all under website/data/. the viewer reads these straight off disk — no build step.
 grouped like the right panel: spine / source / derived / external / editor / user.
 "live" = loaded by the viewer. canonical removal note lives in sw.js DATA_ASSETS
 ~L121: four files are "present on disk only, unreferenced by index.html" since v21.)

LIVE — geojson the viewer loads:

  spine (PostGIS export):
    publish.geojson                       publishable trails + boundaries + trailheads

  source layers (raw external feeds we pulled):
    aop_9_patch.geojson                   9-patch acquisition AOI overlay
    aop_lidar_tiles.geojson               USGS 3DEP LAZ tile index
    aop_buildings.geojson                 FEMA USA Structures footprints
    aop_cemeteries.geojson                TN Comptroller cemetery parcels (incl. Ellis inholding)
    aop_water.geojson                     USGS NHD streams / waterbodies / springs
    aop_roads.geojson                     USGS National Map asphalt roads

  derived layers (computed from the sources):
    aop_landcover.geojson                 NAIP+lidar 5-class land cover (park)
    aop_landcover_9patch.geojson          same, over the full 9-patch (~4.5 MB)
    aop_contours.geojson                  5 ft lidar contours (~13 MB; default OFF, NOT precached)
    aop_trail_network.geojson             merged AOP trail truth, coloured by difficulty
    aop_activity_hotspots.geojson         real GPX dwell hotspots
    aop_synthetic_activity_tracks.geojson  simulated Saturday tracks (default OFF, NOT precached)
    aop_synthetic_activity_hotspots.geojson  simulated Saturday hotspots
    aop_visitor_context_callouts.geojson  callout polygons + brand logos (kind=brand_logo)

  external reference (vectors/raster we trace against):
    osm_aop_9patch.geojson                OSM park polygon / tracks / service roads
    osm_aop_named.geojson                 OSM named landmarks
    sfwda_traced_trails.geojson           SFWDA paper-map traced trails
    sfwda_aop_trail_map.webp              SFWDA paper map raster   (+ sfwda_raster_alignment.json)

  editor / first-party:
    aop_editor_seed_pois.geojson          seeds the editor on a fresh viewer
    aop_event_schedule.json               schedule (resolved to in-memory geojson, no file checked in)

  user:
    aop_user_features.geojson             user-positioned feature store (editor)

  support json (read, not map layers):
    aop_poi_index.json                    POI-tab visitor copy + owed_work gaps
    aop_trail_catalog.json                trail blurbs / catalog
    aop_about.json                        About tab
    aop_ui_strings.json                   UI microcopy
    aop_copy_registry.json                copy-review tooling
    _data_manifest.json / _schema.json    data manifest + maturity schema

CAN BE REMOVED — on disk only, no live viewer reference (sw.js v21 note):
    aop_synthetic_activity_report.json    build sidecar, not a layer (regen: simulate_saturday_activity.py; no raw/ copy)
    sfwda_traced_markers.geojson          difficulty markers — superseded by the merged network*
    sfwda_numbered_trails.geojson         per-trail contiguous geometry — paper-trace input, now superseded
    sfwda_trails_edited.geojson           edited SFWDA trails — superseded
  → all three sfwda_* originals are preserved under website/data/raw/, and the paper-trace
    pipeline (run_paper_trace_pipeline.sh) can regenerate them, so the top-level copies are safe to drop.
  * note: research/viewer.md still lists "SFWDA traced markers" as a viewer layer, but no live JS
    loads it. reconcile viewer.md when these are removed.

sibling dirs (NOT viewer-served, keep):
    website/data/raw/      pre-bake canonical inputs read by rebake_canonical.py / stamp_maturity.py / bake_panel_overrides.py
    website/compare_data/  topo-trail compare fixture (build_topo_trail_compare_data.py + its playwright verifier)