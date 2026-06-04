/* AOP right panel — clean rebuild (the replacement for the index.html panel).
 *
 * ONE source of truth (PANEL_MODEL) drives ONE renderer (renderPanel).
 * No per-layer hand-written HTML, no parallel config objects, no hidden
 * mirror toggles. A node declares what it is; the renderer decides how to
 * draw it. Adding a capability = a new field on a node + one new branch in
 * the renderer, never a new surface.
 *
 * This panel now carries EVERY layer the live index page carries, grouped by
 * provenance exactly like the page it replaces: Source layers / Derived
 * layers / External reference / Map editor / User submitted. Each layer's map
 * source + paint is ported verbatim from website/js/main.js so the toggles are
 * genuinely wired, not faked.
 */
(function () {
  'use strict';

  // --- The map (prototype host) ----------------------------------------------
  // The panel describes the panel, NOT the map style. Map layers are added to
  // MapLibre here, exactly as the live app does; a panel node only references
  // the map-layer ids it controls (the `mapLayers` field). This keeps the one
  // model about the panel and lets the same model swap into index.html later.
  const REGION_BOUNDS = [[-85.782935283, 35.067164188], [-85.717154097, 35.117928496]];

  const map = new maplibregl.Map({
    container: 'map',
    style: {
      version: 8,
      sources: {},
      layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#efe7d5' } }]
    },
    center: [-85.75, 35.0925],
    zoom: 12.5,
    bearing: -90,
    maxBounds: REGION_BOUNDS,
    attributionControl: false
  });
  map.on('error', (e) => console.error(e.error || e));

  // Parsed GeoJSON kept by source id so a node's items list can be derived
  // from the same data the map draws (no second fetch, one source of truth).
  const LOADED = {};

  // --- Paint constants (ported verbatim from main.js) ------------------------
  const LANDCOVER_FILL = ['match', ['get', 'class'],
    'forest_deciduous', '#b8c1a1', 'forest_evergreen', '#a8b18f',
    'open_grass', '#ddd2ad', 'open_meadow', '#d4c79f', 'open_bare', '#c7b890', '#b8c1a1'];
  const LANDCOVER_OUTLINE = ['match', ['get', 'class'],
    'forest_deciduous', '#a6af8d', 'forest_evergreen', '#969f7c',
    'open_grass', '#cdc29c', 'open_meadow', '#c4b78d', 'open_bare', '#b7a87f', '#a6af8d'];
  const ACTIVITY_HOTSPOT_FILL = ['match', ['get', 'intensity_class'],
    'low', '#e6c86f', 'medium', '#d9903d', 'high', '#bf5a36', 'peak', '#7f2f27', '#d9903d'];
  const ACTIVITY_HOTSPOT_OPACITY = ['interpolate', ['linear'], ['get', 'intensity_norm'], 0, 0.12, 0.4, 0.28, 1, 0.58];
  const SYNTHETIC_HOTSPOT_FILL = ['match', ['get', 'intensity_class'],
    'low', '#b7d2bd', 'medium', '#6fa793', 'high', '#477c82', 'peak', '#254d5b', '#6fa793'];
  const SYNTHETIC_HOTSPOT_OPACITY = ['interpolate', ['linear'], ['get', 'intensity_norm'], 0, 0.10, 0.4, 0.24, 1, 0.52];
  const POI_COLOR = ['match', ['get', 'category'],
    'Pavilion', '#c47a44', 'Building', '#a07442', 'Restroom', '#6f8aa6', 'Parking', '#8a8576',
    'Staging area', '#9a7d96', 'Gate', '#b05a48', 'Trail trace', '#9a5a32', 'Road trace', '#6f6a5b',
    'Landmark', '#5f9183', 'Hazard', '#cf9a4a', 'Other', '#6a6256', '#6a6256'];
  const TILE_BOUNDS = [-85.782935283, 35.067164188, -85.717154097, 35.117928496];

  // Resolve the event schedule JSON (tag dictionary) into anchor points for the
  // tags that ship coordinates. The live app additionally resolves coordinate-
  // less tags (#pavilion) from per-feature #tag bindings; that resolver is not
  // brought yet, so coordinate-less anchors simply don't draw here.
  function roleForTag(tag) {
    const t = tag.toLowerCase();
    if (t.includes('pavilion') || t.includes('registration')) return 'pavilion';
    if (t.includes('proving')) return 'event_proving_ground';
    if (t.includes('checkpoint')) return 'event_checkpoint';
    if (t.includes('photo')) return 'event_photo_waypoint';
    return 'pavilion';
  }
  function resolveEventSchedule(json) {
    const feats = [];
    const locs = (json && json.locations) || {};
    for (const tag of Object.keys(locs)) {
      const c = locs[tag] && locs[tag].coordinates;
      if (!Array.isArray(c)) continue;
      feats.push({
        type: 'Feature', geometry: { type: 'Point', coordinates: c },
        properties: { feature_kind: 'event_anchor', role: roleForTag(tag), map_label: tag.replace(/^#/, ''), name: tag.replace(/^#/, '') }
      });
    }
    return { type: 'FeatureCollection', features: feats };
  }

  // Map sources + styled layers the prototype shows, ported from main.js. Each
  // entry's `layers` are the MapLibre layer specs to add once the source is
  // ready. The panel model below references these layer ids by id. Source kinds:
  //   url       — fetch a GeoJSON file (optionally run `resolve` on it)
  //   data      — inline GeoJSON (grows at runtime, e.g. user features)
  //   raster    — XYZ raster tiles      rasterDem — terrarium DEM
  //   image     — a single georeferenced image (4 corner coords)
  //   images    — bitmap icons to addImage() before the layers are added
  const MAP_DATA = [
    // ---- Publishable (publish.geojson: boundaries + trails + trailheads) ----
    {
      source: 'publish-data', url: './data/publish.geojson',
      layers: [
        { id: 'publish-boundary-fill', type: 'fill', filter: ['==', ['get', 'layer'], 'park_boundaries'], paint: { 'fill-color': '#d8c8a2', 'fill-opacity': 0.10 } },
        { id: 'publish-boundaries', type: 'line', filter: ['==', ['get', 'layer'], 'park_boundaries'], paint: { 'line-color': '#6e5a3c', 'line-width': 2.5 } },
        { id: 'publish-trails', type: 'line', filter: ['==', ['get', 'layer'], 'trail_centerlines'], paint: { 'line-color': '#9a5a32', 'line-width': 3.5 } },
        { id: 'publish-trailheads', type: 'circle', filter: ['==', ['get', 'layer'], 'trailheads'], paint: { 'circle-radius': 6, 'circle-color': '#6f8a5c', 'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 2 } }
      ]
    },
    // ---- Source layers ----
    {
      source: 'nine-patch', url: './data/aop_9_patch.geojson',
      layers: [
        { id: 'nine-patch-fill', type: 'fill', paint: { 'fill-color': '#c7a85e', 'fill-opacity': 0.10 } },
        { id: 'nine-patch-outline', type: 'line', paint: { 'line-color': '#a88246', 'line-width': 1.5, 'line-dasharray': [2, 2] } },
        { id: 'nine-patch-labels', type: 'symbol', layout: { 'text-field': ['get', 'cell_code'], 'text-size': 12, 'text-anchor': 'center' }, paint: { 'text-color': '#6a5836', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.5 } }
      ]
    },
    {
      source: 'tnmap-imagery', raster: { tiles: ['https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer/tile/{z}/{y}/{x}'], tileSize: 256, minzoom: 11, maxzoom: 22, bounds: TILE_BOUNDS },
      layers: [{ id: 'tnmap-satellite', type: 'raster', layout: { visibility: 'none' }, paint: { 'raster-opacity': 1 } }]
    },
    {
      source: 'usda-naip-imagery', raster: { tiles: ['https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/tile/{z}/{y}/{x}'], tileSize: 256, minzoom: 11, maxzoom: 17, bounds: TILE_BOUNDS },
      layers: [{ id: 'usda-naip-satellite', type: 'raster', layout: { visibility: 'none' }, paint: { 'raster-opacity': 1 } }]
    },
    {
      source: 'lidar-tiles', url: './data/aop_lidar_tiles.geojson',
      layers: [
        { id: 'lidar-tiles-fill', type: 'fill', paint: { 'fill-color': '#9a7d96', 'fill-opacity': 0.16 } },
        { id: 'lidar-tiles-outline', type: 'line', paint: { 'line-color': '#8a6f86', 'line-width': 2.5, 'line-dasharray': [4, 2] } },
        { id: 'lidar-tiles-labels', type: 'symbol', layout: { 'text-field': ['get', 'tile_code'], 'text-size': 13, 'text-anchor': 'center' }, paint: { 'text-color': '#7a6076', 'text-halo-color': '#f7f1e2', 'text-halo-width': 2 } }
      ]
    },
    {
      source: 'cemeteries', url: './data/aop_cemeteries.geojson',
      layers: [
        { id: 'cemetery-fill', type: 'fill', filter: ['==', ['get', 'geom_role'], 'parcel'], paint: { 'fill-color': '#a99aa0', 'fill-opacity': 0.4 } },
        { id: 'cemetery-outline', type: 'line', filter: ['==', ['get', 'geom_role'], 'parcel'], paint: { 'line-color': '#7d6e74', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 1, 17, 3] } },
        { id: 'cemetery-marker', type: 'circle', filter: ['==', ['get', 'geom_role'], 'marker'], paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 10, 3.5, 14, 6, 17, 8], 'circle-color': '#8a7a82', 'circle-stroke-color': ['case', ['get', 'aop_inholding'], '#c7a14e', '#f7f1e2'], 'circle-stroke-width': ['case', ['get', 'aop_inholding'], 3, 1.6] } },
        { id: 'cemetery-label', type: 'symbol', filter: ['==', ['get', 'geom_role'], 'marker'], layout: { 'text-field': ['get', 'name'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 13], 'text-offset': [0, 1.1], 'text-anchor': 'top' }, paint: { 'text-color': '#5a4e54', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 } }
      ]
    },
    // ---- Derived layers ----
    {
      source: 'aop-landcover-9patch', url: './data/aop_landcover_9patch.geojson',
      layers: [
        { id: 'landcover-9patch-forest', type: 'fill', paint: { 'fill-color': LANDCOVER_FILL, 'fill-opacity': 0.55 } },
        { id: 'landcover-9patch-forest-outline', type: 'line', paint: { 'line-color': LANDCOVER_OUTLINE, 'line-width': 0.6, 'line-opacity': 0.35 } }
      ]
    },
    {
      source: 'aop-landcover', url: './data/aop_landcover.geojson',
      layers: [
        { id: 'landcover-forest', type: 'fill', paint: { 'fill-color': LANDCOVER_FILL, 'fill-opacity': 0.9 } },
        { id: 'landcover-forest-outline', type: 'line', paint: { 'line-color': LANDCOVER_OUTLINE, 'line-width': 0.8, 'line-opacity': 0.55 } }
      ]
    },
    {
      source: 'aws-terrain-dem', rasterDem: { tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'], tileSize: 256, encoding: 'terrarium', minzoom: 0, maxzoom: 15 },
      layers: [{ id: 'lidar-hillshade', type: 'hillshade', layout: { visibility: 'none' }, paint: { 'hillshade-exaggeration': 0.6, 'hillshade-shadow-color': '#3a2f22', 'hillshade-highlight-color': '#fbf4e2', 'hillshade-accent-color': '#6b5640' } }]
    },
    {
      source: 'aop-contours', url: './data/aop_contours.geojson',
      layers: [
        { id: 'contours-minor', type: 'line', filter: ['==', ['get', 'idx'], 0], layout: { 'line-join': 'round' }, paint: { 'line-color': '#c7b48f', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.5, 16, 1.4], 'line-opacity': ['interpolate', ['linear'], ['zoom'], 16.5, 0, 17.5, 0.75] } },
        { id: 'contours-index', type: 'line', filter: ['==', ['get', 'idx'], 1], layout: { 'line-join': 'round' }, paint: { 'line-color': '#a8906a', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1, 16, 2.8], 'line-opacity': ['interpolate', ['linear'], ['zoom'], 15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 0.95, 0], 16, 0.95] } },
        { id: 'contours-labels', type: 'symbol', filter: ['==', ['get', 'idx'], 1], layout: { 'symbol-placement': 'line', 'text-field': ['concat', ['to-string', ['get', 'elev_ft']], ' ft'], 'text-size': 11, 'symbol-spacing': 320 }, paint: { 'text-color': '#7d6a4a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8, 'text-opacity': ['interpolate', ['linear'], ['zoom'], 15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 1, 0], 16, 1] } }
      ]
    },
    {
      source: 'fema-buildings', url: './data/aop_buildings.geojson',
      layers: [
        { id: 'building-footprint-fill', type: 'fill', filter: ['!=', ['get', 'aop_structure_box'], true], paint: { 'fill-color': ['match', ['get', 'occupancy_class'], 'Residential', '#c1a386', 'Agriculture', '#b7a36f', 'Assembly', '#b78f6f', 'Government', '#9da4a6', 'Unclassified', '#aaa397', '#ad987f'], 'fill-opacity': ['case', ['==', ['get', 'inside_aop_boundary'], true], 0.56, 0.34] } },
        { id: 'building-footprint-outline', type: 'line', filter: ['!=', ['get', 'aop_structure_box'], true], paint: { 'line-color': ['case', ['==', ['get', 'inside_aop_boundary'], true], '#8e5f37', '#776f61'], 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 0.5, 16, 1.8], 'line-opacity': 0.9 } },
        { id: 'building-footprint-aop-outline', type: 'line', filter: ['==', ['get', 'aop_facility'], true], paint: { 'line-color': '#7c4a2a', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.1, 16, 3.1], 'line-opacity': 0.95 } }
      ]
    },
    {
      source: 'aop-trail-network', url: './data/aop_trail_network.geojson',
      layers: [
        { id: 'aop-trail-network', type: 'line', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': ['coalesce', ['get', 'color'], '#888888'], 'line-width': 3, 'line-opacity': 0.92 } },
        { id: 'aop-trail-network-labels', type: 'symbol', filter: ['to-boolean', ['get', 'name']], layout: { 'symbol-placement': 'line-center', 'text-field': ['to-string', ['get', 'name']], 'text-size': 12 }, paint: { 'text-color': '#111', 'text-halo-color': '#fff', 'text-halo-width': 1.6 } }
      ]
    },
    {
      source: 'synthetic-activity-tracks', url: './data/aop_synthetic_activity_tracks.geojson',
      layers: [
        { id: 'synthetic-activity-tracks', type: 'line', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': ['match', ['get', 'persona'], 'north_crawl', '#254d5b', 'checkpoint_loop', '#477c82', 'photo_short', '#6fa793', 'proving_ground', '#9a7d96', 'trailhead_social', '#9a5a32', '#5f9183'], 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.7, 16, 1.8], 'line-opacity': 0.36 } }
      ]
    },
    {
      source: 'synthetic-activity-hotspots', url: './data/aop_synthetic_activity_hotspots.geojson',
      layers: [
        { id: 'synthetic-activity-hotspots-heat', type: 'heatmap', filter: ['==', ['geometry-type'], 'Point'], paint: { 'heatmap-weight': ['interpolate', ['linear'], ['get', 'intensity_norm'], 0, 0.18, 1, 1], 'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 11, 0.35, 16, 1.45], 'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 11, 16, 16, 42], 'heatmap-opacity': 0.58, 'heatmap-color': ['interpolate', ['linear'], ['heatmap-density'], 0, 'rgba(183, 210, 189, 0)', 0.24, 'rgba(183, 210, 189, 0.5)', 0.48, 'rgba(111, 167, 147, 0.64)', 0.74, 'rgba(71, 124, 130, 0.78)', 1, 'rgba(37, 77, 91, 0.92)'] } },
        { id: 'synthetic-activity-hotspots-fill', type: 'fill', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'fill-color': SYNTHETIC_HOTSPOT_FILL, 'fill-opacity': SYNTHETIC_HOTSPOT_OPACITY } },
        { id: 'synthetic-activity-hotspots-outline', type: 'line', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'line-color': '#254d5b', 'line-width': 1.2, 'line-opacity': 0.66 } },
        { id: 'synthetic-activity-hotspots-labels', type: 'symbol', filter: ['all', ['==', ['geometry-type'], 'Point'], ['!=', ['get', 'label'], '']], layout: { 'text-field': ['get', 'label'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12] }, paint: { 'text-color': '#254d5b', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.4 } }
      ]
    },
    // ---- External reference ----
    {
      source: 'usgs-water', url: './data/aop_water.geojson',
      layers: [
        { id: 'water-area-fill', type: 'fill', filter: ['==', ['get', 'water_kind'], 'water_area'], paint: { 'fill-color': '#a8c5c9', 'fill-opacity': 0.55 } },
        { id: 'waterbody-fill', type: 'fill', filter: ['==', ['get', 'water_kind'], 'waterbody'], paint: { 'fill-color': '#9fbfc4', 'fill-opacity': 0.5 } },
        { id: 'waterbody-outline', type: 'line', filter: ['==', ['get', 'water_kind'], 'waterbody'], paint: { 'line-color': '#6f9098', 'line-width': 1.2 } },
        { id: 'streams', type: 'line', filter: ['==', ['get', 'water_kind'], 'flowline'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#7fa3ac', 'line-opacity': 0.9, 'line-width': ['interpolate', ['linear'], ['zoom'], 10, ['case', ['==', ['get', 'water_class'], 'stream'], 0.9, 0.5], 14, ['case', ['==', ['get', 'water_class'], 'stream'], 2.4, 1.3], 17, ['case', ['==', ['get', 'water_class'], 'stream'], 5.5, 2.8]] } },
        { id: 'stream-labels', type: 'symbol', filter: ['all', ['==', ['get', 'water_kind'], 'flowline'], ['has', 'name']], layout: { 'symbol-placement': 'line', 'text-field': ['get', 'name'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 9, 16, 13], 'text-letter-spacing': 0.04 }, paint: { 'text-color': '#4a6c73', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 } },
        { id: 'water-points', type: 'circle', filter: ['==', ['get', 'water_kind'], 'point'], paint: { 'circle-radius': 5, 'circle-color': ['match', ['get', 'water_class'], 'spring', '#6f9aa6', 'gage', '#bb8a4a', '#7fa3ac'], 'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 1.5 } },
        { id: 'water-point-labels', type: 'symbol', filter: ['all', ['==', ['get', 'water_kind'], 'point'], ['has', 'name']], layout: { 'text-field': ['get', 'name'], 'text-size': 11, 'text-offset': [0, 1.1], 'text-anchor': 'top' }, paint: { 'text-color': '#4a6c73', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.5 } }
      ]
    },
    {
      source: 'usgs-roads', url: './data/aop_roads.geojson',
      layers: [
        { id: 'roads-local-casing', type: 'line', filter: ['==', ['get', 'road_class'], 'local'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#f3ecda', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.8, 14, 2.2, 17, 6], 'line-opacity': 0.9 } },
        { id: 'roads-local', type: 'line', filter: ['==', ['get', 'road_class'], 'local'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#b0a68c', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.4, 14, 1.2, 17, 3.2] } },
        { id: 'roads-connecting-casing', type: 'line', filter: ['==', ['get', 'road_class'], 'local_connecting'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#f3ecda', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.2, 14, 3, 17, 8], 'line-opacity': 0.95 } },
        { id: 'roads-connecting', type: 'line', filter: ['==', ['get', 'road_class'], 'local_connecting'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#cdb079', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.7, 14, 1.8, 17, 4.5] } },
        { id: 'roads-secondary-casing', type: 'line', filter: ['==', ['get', 'road_class'], 'secondary'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#f3ecda', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.6, 14, 4, 17, 9.5], 'line-opacity': 0.95 } },
        { id: 'roads-secondary', type: 'line', filter: ['==', ['get', 'road_class'], 'secondary'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#c09060', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.9, 14, 2.4, 17, 5.5] } },
        { id: 'roads-ramp-casing', type: 'line', filter: ['==', ['get', 'road_class'], 'ramp'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#bf8f55', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.5, 14, 3.5, 17, 8] } },
        { id: 'roads-ramp', type: 'line', filter: ['==', ['get', 'road_class'], 'ramp'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#d8b173', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.8, 14, 2.0, 17, 4.8] } },
        { id: 'roads-controlled-casing', type: 'line', filter: ['==', ['get', 'road_class'], 'controlled_access'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#9a7a52', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 2, 14, 5, 17, 11] } },
        { id: 'roads-controlled', type: 'line', filter: ['==', ['get', 'road_class'], 'controlled_access'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#d8b173', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.2, 14, 3, 17, 7] } },
        { id: 'roads-labels', type: 'symbol', filter: ['has', 'name'], layout: { 'symbol-placement': 'line', 'text-field': ['get', 'name'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 9, 16, 13], 'text-letter-spacing': 0.04 }, paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 } }
      ]
    },
    {
      source: 'osm-9patch', url: './data/osm_aop_9patch.geojson',
      layers: [
        { id: 'osm-park-outline', type: 'line', filter: ['==', ['get', 'leisure'], 'park'], paint: { 'line-color': '#8a9a6a', 'line-width': 2, 'line-dasharray': [3, 2] } },
        { id: 'osm-tracks', type: 'line', filter: ['==', ['get', 'highway'], 'track'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#9a5a32', 'line-width': 2, 'line-opacity': 0.95 } },
        { id: 'osm-service', type: 'line', filter: ['==', ['get', 'highway'], 'service'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#a89a7e', 'line-width': 1.5, 'line-opacity': 0.85 } }
      ]
    },
    {
      source: 'osm-named', url: './data/osm_aop_named.geojson',
      layers: [
        { id: 'osm-named-points', type: 'circle', filter: ['==', ['geometry-type'], 'Point'], paint: { 'circle-radius': 5, 'circle-color': '#c7a85e', 'circle-stroke-color': '#6a5836', 'circle-stroke-width': 1.5 } },
        { id: 'osm-named-labels', type: 'symbol', layout: { 'text-field': ['get', 'name'], 'text-size': 12, 'text-offset': [0, 1.1], 'text-anchor': 'top' }, paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.5 } }
      ]
    },
    {
      source: 'sfwda-paper',
      image: { url: './data/sfwda_aop_trail_map.webp', coordinates: [[-85.76073558646485, 35.0994390889923], [-85.74561659422288, 35.099029480793746], [-85.74647191491296, 35.083297054743525], [-85.76038739950994, 35.08300393591165]] },
      layers: [{ id: 'sfwda-paper', type: 'raster', layout: { visibility: 'none' }, paint: { 'raster-opacity': 0.7, 'raster-fade-duration': 0 } }]
    },
    {
      source: 'sfwda-trace-trails', url: './data/sfwda_traced_trails.geojson',
      layers: [
        { id: 'sfwda-trace-trails', type: 'line', layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': ['match', ['get', 'difficulty'], 'easy', '#2e8b57', 'moderate', '#2f6fb0', 'difficult', '#333333', '#b06a2c'], 'line-width': 2.5, 'line-opacity': 0.9 } }
      ]
    },
    // ---- Map editor (first-party curated + the event overlay) ----
    {
      source: 'event-schedule', url: './data/aop_event_schedule.json', resolve: resolveEventSchedule,
      layers: [
        { id: 'event-session-routes', type: 'line', filter: ['all', ['==', ['get', 'feature_kind'], 'event_session'], ['==', ['geometry-type'], 'LineString']], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': '#b45f43', 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 2, 16, 4.2], 'line-opacity': 0.92, 'line-dasharray': [3, 1.4] } },
        { id: 'event-route-labels', type: 'symbol', filter: ['all', ['==', ['get', 'feature_kind'], 'event_session'], ['==', ['geometry-type'], 'LineString']], layout: { 'symbol-placement': 'line', 'text-field': ['get', 'title'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12], 'text-keep-upright': true }, paint: { 'text-color': '#6f382b', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 } },
        { id: 'event-anchor-points', type: 'circle', filter: ['==', ['get', 'feature_kind'], 'event_anchor'], paint: { 'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 4.5, 16, 8], 'circle-color': ['match', ['get', 'role'], 'pavilion', '#8b5f38', 'event_registration', '#b05a48', 'event_stage_start', '#7f7a4b', 'event_proving_ground', '#9a7d96', 'event_checkpoint', '#b45f43', 'event_photo_waypoint', '#5f9183', '#8b5f38'], 'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 2 } },
        { id: 'event-anchor-labels', type: 'symbol', filter: ['==', ['get', 'feature_kind'], 'event_anchor'], layout: { 'text-field': ['get', 'map_label'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12], 'text-offset': [0, 1.2], 'text-anchor': 'top' }, paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 } }
      ]
    },
    {
      source: 'visitor-context', url: './data/aop_visitor_context_callouts.geojson',
      layers: [
        { id: 'visitor-context-fill', type: 'fill', paint: { 'fill-color': '#d8b173', 'fill-opacity': 0.18 } },
        { id: 'visitor-context-outline', type: 'line', layout: { 'line-join': 'round' }, paint: { 'line-color': '#8b5f38', 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.6, 16, 3.2], 'line-opacity': 0.9, 'line-dasharray': [3, 1.4] } },
        { id: 'visitor-context-labels', type: 'symbol', layout: { 'text-field': ['get', 'label'], 'text-size': ['interpolate', ['linear'], ['zoom'], 11, 10, 15, 12], 'text-line-height': 1.08, 'text-anchor': 'center', 'text-max-width': 18, 'text-padding': 4 }, paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 } }
      ]
    },
    {
      source: 'brand-logos', url: './data/aop_brand_logos.geojson',
      images: [{ name: 'brand-aop-badge', url: './assets/branding/aop-badge.png' }, { name: 'brand-rock-warblers', url: './assets/branding/rock-warblers.jpg' }],
      layers: [
        { id: 'brand-logos-icons', type: 'symbol', layout: { 'icon-image': ['get', 'icon_image'], 'icon-size': ['coalesce', ['get', 'icon_size'], 0.2], 'icon-allow-overlap': true, 'icon-ignore-placement': true, 'icon-anchor': 'center' } }
      ]
    },
    {
      source: 'editor-poi', url: './data/aop_editor_seed_pois.geojson',
      layers: [
        { id: 'editor-poi-fill', type: 'fill', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'fill-color': POI_COLOR, 'fill-opacity': 0.3 } },
        { id: 'editor-poi-outline', type: 'line', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'line-color': POI_COLOR, 'line-width': 2.5 } },
        { id: 'editor-poi-lines', type: 'line', filter: ['==', ['geometry-type'], 'LineString'], layout: { 'line-cap': 'round', 'line-join': 'round' }, paint: { 'line-color': POI_COLOR, 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 2.5, 16, 5], 'line-opacity': 0.95 } },
        { id: 'editor-poi-circles', type: 'circle', filter: ['==', ['geometry-type'], 'Point'], paint: { 'circle-radius': 7, 'circle-color': POI_COLOR, 'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 2 } },
        { id: 'editor-poi-labels', type: 'symbol', filter: ['==', ['geometry-type'], 'Point'], layout: { 'text-field': ['coalesce', ['get', 'name'], ['get', 'category']], 'text-size': 12, 'text-offset': [0, 1.2], 'text-anchor': 'top' }, paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 } },
        { id: 'editor-poi-fill-labels', type: 'symbol', filter: ['==', ['geometry-type'], 'Polygon'], layout: { 'text-field': ['coalesce', ['get', 'name'], ['get', 'category']], 'text-size': 12 }, paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 } },
        { id: 'editor-poi-line-labels', type: 'symbol', filter: ['==', ['geometry-type'], 'LineString'], layout: { 'symbol-placement': 'line', 'text-field': ['coalesce', ['get', 'name'], ['get', 'category']], 'text-size': 12, 'text-keep-upright': true }, paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 } }
      ]
    },
    {
      source: 'activity-hotspots', url: './data/aop_activity_hotspots.geojson',
      layers: [
        { id: 'activity-hotspots-heat', type: 'heatmap', filter: ['==', ['geometry-type'], 'Point'], paint: { 'heatmap-weight': ['interpolate', ['linear'], ['get', 'intensity_norm'], 0, 0.18, 1, 1], 'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 11, 0.45, 16, 1.65], 'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 11, 18, 16, 44], 'heatmap-opacity': 0.68, 'heatmap-color': ['interpolate', ['linear'], ['heatmap-density'], 0, 'rgba(230, 200, 111, 0)', 0.22, 'rgba(230, 200, 111, 0.55)', 0.45, 'rgba(217, 144, 61, 0.65)', 0.72, 'rgba(191, 90, 54, 0.76)', 1, 'rgba(127, 47, 39, 0.9)'] } },
        { id: 'activity-hotspots-fill', type: 'fill', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'fill-color': ACTIVITY_HOTSPOT_FILL, 'fill-opacity': ACTIVITY_HOTSPOT_OPACITY } },
        { id: 'activity-hotspots-outline', type: 'line', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'line-color': '#7f2f27', 'line-width': 1.1, 'line-opacity': 0.55 } },
        { id: 'activity-hotspots-labels', type: 'symbol', filter: ['all', ['==', ['geometry-type'], 'Point'], ['!=', ['get', 'label'], '']], layout: { 'text-field': ['get', 'label'], 'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12] }, paint: { 'text-color': '#5b2d25', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.4 } }
      ]
    },
    {
      // User-entered features. No URL — starts empty and grows as the user
      // creates features (inline `data` instead of a fetch).
      source: 'userFeatures', data: { type: 'FeatureCollection', features: [] },
      layers: [
        { id: 'user-feature-polys', type: 'fill', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'fill-color': '#b4561f', 'fill-opacity': 0.25 } },
        { id: 'user-feature-polys-outline', type: 'line', filter: ['==', ['geometry-type'], 'Polygon'], paint: { 'line-color': '#b4561f', 'line-width': 1.5 } },
        { id: 'user-feature-lines', type: 'line', filter: ['==', ['geometry-type'], 'LineString'], paint: { 'line-color': '#b4561f', 'line-width': 3 } },
        { id: 'user-feature-points', type: 'circle', filter: ['==', ['geometry-type'], 'Point'], paint: { 'circle-radius': 6, 'circle-color': '#b4561f', 'circle-stroke-color': '#fff', 'circle-stroke-width': 1.5 } }
      ]
    }
  ];

  // --- The one model ---------------------------------------------------------
  // The whole right panel, declared as data, grouped by provenance exactly like
  // the index page it replaces. A section holds nodes; a node has a `kind` the
  // renderer dispatches on. A 'layer' node references the map-layer ids it
  // controls via `mapLayers`. Listable layers add an `items` descriptor; layers
  // the user can draw into add a `create` descriptor. Reference layers default
  // LOCKED (read-only edit area); user-editable ones default unlocked.
  //
  // `visible` defaults mirror the live viewer's fresh-load state.
  const refItems = (source, opts) => Object.assign({ source, provenance: true, actions: ['fly', 'copy'] }, opts);

  const PANEL_MODEL = {
    title: 'AOP edit panel',
    sections: [
      {
        id: 'source-layers', label: 'Source layers', collapsed: false,
        nodes: [
          { id: 'ninePatch', kind: 'layer', label: '9-patch acquisition AOI', visible: false, mapLayers: ['nine-patch-fill', 'nine-patch-outline', 'nine-patch-labels'] },
          { id: 'satellite', kind: 'layer', label: 'Satellite imagery (TNMap 2022)', visible: false, mapLayers: ['tnmap-satellite'] },
          { id: 'usdaNaip', kind: 'layer', label: 'USDA NAIP imagery (TN 2023)', visible: false, mapLayers: ['usda-naip-satellite'] },
          { id: 'lidarTiles', kind: 'layer', label: 'Lidar tile index (USGS 3DEP)', visible: false, mapLayers: ['lidar-tiles-fill', 'lidar-tiles-outline', 'lidar-tiles-labels'] },
          {
            id: 'cemeteries', kind: 'layer', label: 'Cemeteries (TN Comptroller)', visible: false, locked: true, expanded: false, geom: 'Polygon',
            mapLayers: ['cemetery-fill', 'cemetery-outline', 'cemetery-marker', 'cemetery-label'],
            items: refItems('cemeteries', {
              filter: (f) => (f.properties || {}).geom_role === 'marker',
              key: (p) => p.name, label: (p) => p.name || 'Cemetery',
              detail: (p) => [p.parcel_id, p.acres ? p.acres + ' ac' : null].filter(Boolean).join(' · ')
            })
          }
        ]
      },
      {
        id: 'derived-layers', label: 'Derived layers', collapsed: false,
        nodes: [
          { id: 'landcover', kind: 'layer', label: 'Land cover (NAIP)', visible: true, mapLayers: ['landcover-forest', 'landcover-forest-outline'] },
          { id: 'landcover9', kind: 'layer', label: 'Land cover — 9-patch (NAIP)', visible: true, mapLayers: ['landcover-9patch-forest', 'landcover-9patch-forest-outline'] },
          { id: 'hillshade', kind: 'layer', label: 'Lidar hillshade (USGS 3DEP)', visible: false, mapLayers: ['lidar-hillshade'] },
          { id: 'contours', kind: 'layer', label: 'Lidar contours (5 ft, 1m DEM)', visible: false, mapLayers: ['contours-minor', 'contours-index', 'contours-labels'] },
          {
            id: 'boundaries', kind: 'layer', label: 'Publishable boundaries', visible: true, locked: true, expanded: false, geom: 'Polygon',
            mapLayers: ['publish-boundary-fill', 'publish-boundaries'],
            items: refItems('publish-data', {
              filter: (f) => (f.properties || {}).layer === 'park_boundaries',
              key: (p) => p.name || 'boundary', label: (p) => p.name || 'Park boundary',
              detail: (p) => [p.status, p.permission].filter(Boolean).join(' · ')
            })
          },
          {
            id: 'buildings', kind: 'layer', label: 'Park buildings (curated)', visible: true, locked: true, expanded: false, geom: 'Polygon',
            mapLayers: ['building-footprint-fill', 'building-footprint-outline', 'building-footprint-aop-outline'],
            items: refItems('fema-buildings', {
              key: (p) => p.build_id, label: (p) => p.building_label || p.address || `Building ${p.build_id}`,
              detail: (p) => p.facility_name || (p.aop_structure_box ? 'Private structure' : 'Building')
            })
          },
          {
            id: 'aopTrails', kind: 'layer', label: 'AOP trail network (merged truth)', visible: true, locked: true, expanded: false, geom: 'LineString',
            mapLayers: ['aop-trail-network', 'aop-trail-network-labels'],
            items: refItems('aop-trail-network', {
              key: (p) => p.name, label: (p) => `Trail ${p.name || '—'}${p.difficulty ? ' · ' + p.difficulty : ''}`,
              detail: (p) => [p.difficulty, p.source].filter(Boolean).join(' · ')
            })
          },
          { id: 'syntheticActivity', kind: 'layer', label: 'Simulated Saturday activity', visible: false, mapLayers: ['synthetic-activity-tracks', 'synthetic-activity-hotspots-heat', 'synthetic-activity-hotspots-fill', 'synthetic-activity-hotspots-outline', 'synthetic-activity-hotspots-labels'] }
        ]
      },
      {
        id: 'external-reference', label: 'External reference', collapsed: false,
        nodes: [
          { id: 'water', kind: 'layer', label: 'Streams & waterbodies (USGS NHD)', visible: true, mapLayers: ['water-area-fill', 'waterbody-fill', 'waterbody-outline', 'streams', 'stream-labels'] },
          { id: 'springs', kind: 'layer', label: 'Springs & gages (USGS NHD)', visible: false, mapLayers: ['water-points', 'water-point-labels'] },
          { id: 'roads', kind: 'layer', label: 'Asphalt roads (USGS National Map)', visible: true, mapLayers: ['roads-local-casing', 'roads-local', 'roads-connecting-casing', 'roads-connecting', 'roads-secondary-casing', 'roads-secondary', 'roads-ramp-casing', 'roads-ramp', 'roads-controlled-casing', 'roads-controlled', 'roads-labels'] },
          { id: 'osmPark', kind: 'layer', label: 'OSM park polygon', visible: false, mapLayers: ['osm-park-outline'] },
          { id: 'osmTracks', kind: 'layer', label: 'OSM tracks (highway=track)', visible: false, mapLayers: ['osm-tracks'] },
          { id: 'osmService', kind: 'layer', label: 'OSM service roads', visible: false, mapLayers: ['osm-service'] },
          { id: 'osmNamed', kind: 'layer', label: 'OSM named landmarks', visible: false, mapLayers: ['osm-named-points', 'osm-named-labels'] },
          { id: 'sfwda', kind: 'layer', label: 'SFWDA paper trail map', visible: false, mapLayers: ['sfwda-paper'] },
          { id: 'sfwdaTrace', kind: 'layer', label: 'SFWDA traced trails (extracted)', visible: false, mapLayers: ['sfwda-trace-trails'] }
        ]
      },
      {
        id: 'editor', label: 'Map editor', collapsed: false,
        nodes: [
          // The three geometry create-groups: where the user DRAWS features. Each
          // holds the user-entered features of its geometry; the editor (Name/
          // Notes [+Difficulty for lines] + Group + actions) is derived from
          // geometry in itemFields, not declared per node.
          {
            id: 'userPoints', kind: 'layer', label: 'Points (draw)', visible: true, expanded: true, mapLayers: ['user-feature-points'],
            items: { source: 'userFeatures', filter: (f) => f.geometry.type === 'Point', key: (p) => p._id, label: (p) => p.name || 'Untitled' },
            create: { source: 'userFeatures', geomType: 'Point', defaultProps: (seq) => ({ name: 'Point ' + seq }) }
          },
          {
            id: 'userLines', kind: 'layer', label: 'Lines (draw)', visible: true, expanded: true, mapLayers: ['user-feature-lines'],
            items: { source: 'userFeatures', filter: (f) => f.geometry.type === 'LineString', key: (p) => p._id, label: (p) => p.name || 'Untitled' },
            create: { source: 'userFeatures', geomType: 'LineString', defaultProps: (seq) => ({ name: 'Line ' + seq, difficulty: 'easy' }) }
          },
          {
            id: 'userPolys', kind: 'layer', label: 'Polygons (draw)', visible: true, expanded: true, mapLayers: ['user-feature-polys', 'user-feature-polys-outline'],
            items: { source: 'userFeatures', filter: (f) => f.geometry.type === 'Polygon', key: (p) => p._id, label: (p) => p.name || 'Untitled' },
            create: { source: 'userFeatures', geomType: 'Polygon', defaultProps: (seq) => ({ name: 'Area ' + seq }) }
          },
          {
            id: 'editorPois', kind: 'layer', label: 'Drawn POIs', visible: true, expanded: false,
            mapLayers: ['editor-poi-fill', 'editor-poi-outline', 'editor-poi-lines', 'editor-poi-circles', 'editor-poi-labels', 'editor-poi-fill-labels', 'editor-poi-line-labels'],
            items: { source: 'editor-poi', key: (p) => p.id || p.name, label: (p) => p.name || p.category || 'POI', detail: (p) => p.category || '', actions: ['fly', 'copy'] }
          },
          { id: 'eventSchedule', kind: 'layer', label: 'Event schedule POIs', visible: false, mapLayers: ['event-session-routes', 'event-route-labels', 'event-anchor-points', 'event-anchor-labels'] },
          { id: 'trailheads', kind: 'layer', label: 'Publishable trailheads', visible: true, mapLayers: ['publish-trailheads'] },
          {
            id: 'visitorContext', kind: 'layer', label: 'Visitor context callouts', visible: true, locked: true, expanded: false, geom: 'Polygon',
            mapLayers: ['visitor-context-fill', 'visitor-context-outline', 'visitor-context-labels'],
            items: refItems('visitor-context', { key: (p) => p.name || p.label, label: (p) => p.name || p.label || 'Callout' })
          },
          {
            id: 'brandLogos', kind: 'layer', label: 'Brand logos (AOP & Rock Warblers)', visible: true, expanded: false, geom: 'Point',
            mapLayers: ['brand-logos-icons'],
            items: { source: 'brand-logos', key: (p) => p.name, label: (p) => p.name || 'Logo', actions: ['fly', 'copy'] }
          }
        ]
      },
      {
        id: 'user-submitted', label: 'User submitted', collapsed: false,
        nodes: [
          {
            id: 'pubTrails', kind: 'layer', label: 'Submitted trails', visible: true, locked: true, expanded: false, geom: 'LineString',
            mapLayers: ['publish-trails'],
            items: refItems('publish-data', {
              filter: (f) => (f.properties || {}).layer === 'trail_centerlines',
              key: (p) => p.name, label: (p) => p.name || 'Trail',
              detail: (p) => [p.difficulty, p.source].filter(Boolean).join(' · ')
            })
          },
          { id: 'activityHotspots', kind: 'layer', label: 'Activity hotspots (GPX dwell)', visible: false, mapLayers: ['activity-hotspots-heat', 'activity-hotspots-fill', 'activity-hotspots-outline', 'activity-hotspots-labels'] }
        ]
      }
    ]
  };

  // --- The one renderer ------------------------------------------------------
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) node.textContent = text;
    return node;
  }

  // --- Lock (read-only gate) -------------------------------------------------
  // Everything editable is editable, but a group or item can be locked → its
  // edit area renders read-only (inputs disabled). Reference layers default
  // locked; user features default unlocked. Visibility is a VIEW control, not
  // data, so it is never lock-gated.
  const LOCK_CLOSED_SVG = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>';
  const LOCK_OPEN_SVG = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 7.5-1.5"/></svg>';

  function lockGlyph(locked) {
    const span = el('span', 'lock-glyph');
    span.innerHTML = locked ? LOCK_CLOSED_SVG : LOCK_OPEN_SVG;
    return span;
  }

  function lockButton(locked, onToggle) {
    const btn = el('button', 'lock-btn' + (locked ? ' locked' : ''));
    btn.type = 'button';
    btn.title = locked ? 'Locked — click to unlock' : 'Unlocked — click to lock';
    btn.setAttribute('aria-pressed', locked ? 'true' : 'false');
    btn.append(lockGlyph(locked));
    btn.addEventListener('click', onToggle);
    return btn;
  }

  // --- Icon toggles (eye = visibility, star = highlight) ---------------------
  // Same icon-button shape as the lock: tan when off, rust when on. The eye
  // swaps open/slashed to make hidden state unmistakable; the star fills.
  const EYE_OPEN_SVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
  const EYE_OFF_SVG = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.4 10.4 0 0 1 12 5c7 0 11 7 11 7a13.2 13.2 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.5 13.5 0 0 0 1 12s4 7 11 7a9.7 9.7 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>';
  const starSvg = (filled) => '<svg viewBox="0 0 24 24" width="16" height="16" fill="' + (filled ? 'currentColor' : 'none') + '" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26"/></svg>';

  function iconToggle(extraClass, on, title, glyphHtml, onToggle) {
    const btn = el('button', 'icon-toggle' + (extraClass ? ' ' + extraClass : '') + (on ? ' on' : ''));
    btn.type = 'button';
    btn.title = title;
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.innerHTML = glyphHtml;
    btn.addEventListener('click', onToggle);
    return btn;
  }

  function eyeToggle(node) {
    const on = !!node.visible;
    const btn = iconToggle('eye', on,
      on ? 'Visible — click to hide' : 'Hidden — click to show',
      on ? EYE_OPEN_SVG : EYE_OFF_SVG,
      () => { setLayerVisibility(node, !node.visible); rerender(); });
    btn.dataset.nodeId = node.id;        // stable hook for the visibility control
    btn.dataset.field = 'visible';
    return btn;
  }

  // Per-FEATURE highlight star (matches the live app's `properties.highlight`).
  // Highlighting is a curation/VIEW action — it surfaces the feature under POI
  // on the LEFT sidebar — NOT a data edit, so like visibility it is never
  // lock-gated. State lives on the feature props, so it rides copy/move/reassign.
  function starButton(on, onToggle) {
    return iconToggle('star', on,
      on ? 'Surfaced under POI (left) — click to remove' : 'Click to surface under POI (left)',
      starSvg(on), onToggle);
  }
  function toggleItemStar(item) {
    item.props.highlight = !(item.props.highlight === true);
    rerender();
  }

  // A node is editable (worth a lock + a reassignment target) when it can list
  // or create features. Pure visibility toggles (rasters, coverage layers) are
  // not — they get no lock and never host a reassigned user feature.
  function isEditableNode(node) { return !!(node.items || node.create); }

  // Group lock lives on the node; item lock lives on the feature props, falling
  // back to the group default when the item has no explicit override.
  function effectiveItemLock(node, item) {
    return item.props.__locked !== undefined ? item.props.__locked : !!node.locked;
  }
  function toggleGroupLock(node) { node.locked = !node.locked; rerender(); }
  function toggleItemLock(node, item) {
    item.props.__locked = !effectiveItemLock(node, item);
    rerender();
  }

  // One selection at a time: a group (a layer node) OR an item under it. The
  // selected thing shows an inline edit area directly beneath it. null = none.
  let selection = null;   // { kind:'group', nodeId } | { kind:'item', nodeId, key }

  function isSelected(sel) {
    return !!selection
      && selection.kind === sel.kind
      && selection.nodeId === sel.nodeId
      && selection.key === sel.key;
  }

  function selectTarget(sel) {
    selection = isSelected(sel) ? null : sel;   // click again to close
    rerender();
  }

  function rerender() {
    const host = document.getElementById('panelBody');
    const scroll = host.scrollTop;
    renderPanel(PANEL_MODEL, host);
    host.scrollTop = scroll;                     // keep place across the re-render
    renderLeftPanel();                           // the POI / highlights sidebar tracks the same model
    // The editor renders inline immediately below its row; pull it into view so
    // a just-created or far-down selection's editor is visible. `block:'nearest'`
    // is a no-op when it is already on screen, so it never yanks the panel.
    const open = host.querySelector('.edit-area, .node-group > .create-hint');
    if (open) open.scrollIntoView({ block: 'nearest' });
  }

  function findNodeById(id) {
    let found = null;
    nodeWalk((n) => { if (n.id === id) found = n; });
    return found;
  }

  function renderPanel(model, host) {
    host.textContent = '';
    host.append(el('h1', 'panel-title', model.title));
    // All transient surfaces render INLINE next to their trigger: the create
    // hint under the + button and the group/item editor (or move hint) under
    // the selected row. Nothing floats to the top of the list.
    for (const section of model.sections) host.append(renderSection(section));
  }

  function renderMoveHint() {
    const hint = el('div', 'create-hint');
    hint.append(el('span', 'create-hint-text', `Click the map to move “${moving.item.label || 'feature'}”.`));
    const cancel = el('button', 'create-hint-cancel', 'Cancel');
    cancel.type = 'button';
    cancel.addEventListener('click', cancelMove);
    hint.append(cancel);
    return hint;
  }

  function renderCreateHint() {
    const hint = el('div', 'create-hint');
    const text = placing.geomType === 'Point'
      ? `Click the map to place “${placing.node.label}”.`
      : `Click the map to add points to “${placing.node.label}”, double-click to finish.`;
    hint.append(el('span', 'create-hint-text', text));
    const cancel = el('button', 'create-hint-cancel', 'Cancel');
    cancel.type = 'button';
    cancel.addEventListener('click', cancelCreate);
    hint.append(cancel);
    return hint;
  }

  function renderSection(section) {
    const wrap = el('section', 'panel-section');
    if (section.collapsed) wrap.classList.add('collapsed');

    const header = el('button', 'section-header');
    header.type = 'button';
    header.append(el('span', 'section-label', section.label));
    header.append(el('span', 'section-chevron', '▸'));      // ▸
    header.addEventListener('click', () => toggleSection(section, wrap, header));
    setHeaderState(section, header);
    wrap.append(header);

    const body = el('div', 'section-body');
    for (const node of section.nodes) body.append(renderNode(node));
    wrap.append(body);
    return wrap;
  }

  function toggleSection(section, wrap, header) {
    section.collapsed = !section.collapsed;          // model is the source of truth
    wrap.classList.toggle('collapsed', section.collapsed);
    setHeaderState(section, header);
  }

  function setHeaderState(section, header) {
    header.setAttribute('aria-expanded', section.collapsed ? 'false' : 'true');
  }

  // Dispatch by kind. One place that decides how a node draws.
  function renderNode(node) {
    switch (node.kind) {
      case 'layer': return renderLayerNode(node);
      default:      return el('div', 'node node-unknown', node.label);
    }
  }

  function renderLayerNode(node) {
    const group = el('div', 'node-group');
    group.dataset.nodeId = node.id;
    const hasItems = !!node.items;
    const hasChildren = !!(node.children && node.children.length);
    const hasContent = hasItems || hasChildren;     // anything to expand?
    if (hasContent && node.expanded) group.classList.add('expanded');

    // --- Group row ---
    // No inline checkbox: visibility lives INSIDE the edit area. The row is
    // select-to-edit; an item-bearing layer also gets a chevron that expands
    // its list (the two clicks don't fight).
    const groupSel = { kind: 'group', nodeId: node.id };
    const row = el('div', 'node node-layer');
    if (isSelected(groupSel)) row.classList.add('selected');

    const select = el('button', 'node-select');
    select.type = 'button';
    select.append(el('span', 'node-label', node.label));
    const items = hasItems ? deriveItems(node) : [];
    select.addEventListener('click', () => selectTarget(groupSel));
    row.append(select);

    // Lock no longer lives on the row — it moved into the edit area, beside the
    // Visible check (see renderVisibilityField). The row keeps just the label,
    // the optional create (+), the item count, and the collapse chevron.

    if (node.create) {
      const add = el('button', 'node-create', '+');
      add.type = 'button';
      add.title = 'Add a feature (then click the map)';
      if (placing && placing.node === node) add.classList.add('active');
      add.addEventListener('click', () => startCreate(node));
      row.append(add);
    }

    if (hasContent) {
      // Count sits right next to the collapse chevron, at the row's right edge.
      if (hasItems) row.append(el('span', 'node-count', String(items.length)));
      const chevron = el('button', 'node-chevron-btn');
      chevron.type = 'button';
      chevron.setAttribute('aria-expanded', node.expanded ? 'true' : 'false');
      chevron.append(el('span', 'node-chevron', '▸'));   // ▸
      chevron.addEventListener('click', () => toggleNodeItems(node, group, chevron));
      row.append(chevron);
    }
    group.append(row);

    // Create hint sits DIRECTLY under the + button that started the draw.
    if (placing && placing.node === node) group.append(renderCreateHint());

    // Group editor expands INLINE directly under the group row when selected.
    if (isSelected(groupSel)) group.append(renderEditArea(groupFields(node), { node }, false));

    // --- Expandable content: own items, then nested child groups ---
    if (hasContent) {
      const content = el('div', 'node-content');
      if (hasItems) content.append(renderItemsList(node, items));
      if (hasChildren) {
        for (const child of node.children) content.append(renderNode(child));
      }
      group.append(content);
    }
    return group;
  }

  function renderItemsList(node, items) {
    const list = el('div', 'node-items');
    for (const item of items) {
      const itemSel = { kind: 'item', nodeId: node.id, key: item.key };
      const irow = el('div', 'item');
      if (isSelected(itemSel)) irow.classList.add('selected');
      const ibtn = el('button', 'item-select', item.label);
      ibtn.type = 'button';
      ibtn.addEventListener('click', () => selectTarget(itemSel));
      irow.append(ibtn);
      // The row is JUST a selector — star, lock, and every other control live in
      // the one generic edit module (renderEditArea) that opens below on select.
      const locked = effectiveItemLock(node, item);
      list.append(irow);
      // Item editor expands INLINE immediately below the selected item. During
      // a move, the move hint takes that same space (swapping with the editor).
      if (isSelected(itemSel)) {
        if (moving && moving.item.key === item.key) list.append(renderMoveHint());
        else list.append(renderEditArea(itemFields(node, item), { node, item }, locked));
      }
    }
    return list;
  }

  // A user-created feature carries an optional `__group` = the node id it has
  // been assigned to (via the editor's Group field). Absent → it lives in the
  // default group for its geometry.
  function geometryDefaultGroup(feature) {
    const t = feature.geometry && feature.geometry.type;
    return t === 'Point' ? 'userPoints' : t === 'LineString' ? 'userLines' : 'userPolys';
  }
  function isUserFeature(props) { return props && props._id != null; }
  function effectiveGroup(feature) {
    return (feature.properties && feature.properties.__group) || geometryDefaultGroup(feature);
  }

  // Build a node's item list: its own served features PLUS any user features
  // assigned to this node. User features always key by `_id` / label by `name`,
  // so they slot into a reference group without needing that layer's
  // key/label functions. Dedupe by key, natural sort.
  function deriveItems(node) {
    const spec = node.items;
    const seen = new Set();
    const out = [];
    let idx = 0;
    const add = (feature) => {
      const props = feature.properties || {};
      const user = isUserFeature(props);
      const key = user ? String(props._id) : (spec.key ? String(spec.key(props)) : String(idx));
      idx += 1;
      if (seen.has(key)) return;
      seen.add(key);
      const label = user ? (props.name || 'Untitled') : spec.label(props);
      out.push({ key, label, props, feature });
    };

    // 1) the node's own served source (a user feature reassigned elsewhere drops out here)
    const fc = LOADED[spec.source];
    if (fc && fc.features) {
      for (const feature of fc.features) {
        if (spec.filter && !spec.filter(feature)) continue;
        if (isUserFeature(feature.properties) && effectiveGroup(feature) !== node.id) continue;
        add(feature);
      }
    }
    // 2) user features assigned INTO this node from the shared userFeatures source
    if (spec.source !== 'userFeatures') {
      const uf = LOADED.userFeatures;
      if (uf && uf.features) {
        for (const feature of uf.features) {
          if (effectiveGroup(feature) === node.id) add(feature);
        }
      }
    }
    out.sort((a, b) => String(a.label).localeCompare(String(b.label), undefined, { numeric: true }));
    return out;
  }

  // A node's geometry: user groups encode it in create.geomType; reference
  // layers declare it as `geom`. Null = unconstrained.
  function nodeGeom(node) {
    return node.geom || (node.create && node.create.geomType) || null;
  }

  // Assignable groups for a feature, labeled by path. GEOMETRY-TYPED and limited
  // to nodes that can actually host a feature (have items or create) — a polygon
  // can't be filed under Points or a raster toggle.
  function groupOptions(feature) {
    const want = feature && feature.geometry && feature.geometry.type;
    const opts = [];
    nodeWalk((n, parents) => {
      if (n.kind !== 'layer' || !isEditableNode(n)) return;
      const g = nodeGeom(n);
      if (want && g && g !== want) return;
      opts.push({ id: n.id, label: [...parents.map((p) => p.label), n.label].join(' › ') });
    });
    return opts;
  }

  function toggleNodeItems(node, group, chevron) {
    node.expanded = !node.expanded;          // model is the source of truth
    group.classList.toggle('expanded', node.expanded);
    chevron.setAttribute('aria-expanded', node.expanded ? 'true' : 'false');
  }

  // --- Edit area -------------------------------------------------------------
  // One edit-area renderer for both groups and items. The field list decides
  // the contents; renderField dispatches by field kind.
  function groupFields(node) {
    // A layer's controls: visibility always; lock only where there's editable
    // content to gate. (Stars are per-feature, so they belong to items, not here.)
    const toggles = isEditableNode(node) ? ['visibility', 'lock'] : ['visibility'];
    const fields = [{ kind: 'controls', toggles }];
    if (node.items) fields.push({ kind: 'actions', actions: ['copyAll'] });
    return fields;
  }

  // ONE editor frame for every feature — user-drawn or reference. The data now
  // carries the Common Minimum Feature Schema (see brain/research/
  // common_feature_schema.md), so the editor no longer forks on user-vs-reference
  // or geometry: a trail's Name/Description edit the SAME way the pavilion's do.
  // Common frame = Name · Description · Kind · (facet) · provenance; facets and
  // actions slot in underneath. The lock governs whether the fields are editable.
  function itemFields(node, item) {
    const props = item.props;
    const isUser = isUserFeature(props);
    const geom = item.feature && item.feature.geometry;
    const isLine = geom && geom.type === 'LineString';

    const fields = [{ kind: 'controls', toggles: ['star', 'lock'] }];
    fields.push({ kind: 'text', label: 'Name', prop: 'name' });            // canonical
    fields.push({ kind: 'text', label: 'Description', prop: 'description' }); // canonical
    fields.push({ kind: 'static', label: 'Kind', value: props.kind || '—' });
    // Optional per-node detail summary (e.g. cemetery parcel · acres) stays a facet.
    const detail = node.items.detail ? node.items.detail(props) : '';
    if (detail) fields.push({ kind: 'static', label: 'Details', value: detail });
    // Difficulty facet: where the feature carries one, or a user-drawn line.
    if (props.difficulty != null || (isUser && isLine))
      fields.push({ kind: 'select', label: 'Difficulty', prop: 'difficulty', options: ['easy', 'moderate', 'difficult'] });
    // Provenance block — read straight from the canonical fields (auto-hides any blank).
    fields.push(...provenanceFields(props));
    if (isUser) fields.push({ kind: 'group' });                            // reassignable
    const actions = isUser ? ['fly', 'copy', 'move', 'delete'] : (node.items.actions || ['fly', 'copy']);
    fields.push({ kind: 'actions', actions });
    return fields;
  }

  function renderEditArea(fields, ctx, locked) {
    const area = el('div', 'edit-area');
    for (const field of fields) area.append(renderField(field, ctx, locked));
    return area;
  }

  function renderField(field, ctx, locked) {
    switch (field.kind) {
      case 'controls':   return renderControlsField(field, ctx, locked);  // declared toggles
      case 'text':       return renderTextField(field, ctx.item, locked);
      case 'select':     return renderSelectField(field, ctx.item, locked);
      case 'static':     return renderStaticField(field);
      case 'actions':    return renderActionsField(field, ctx, locked);
      case 'group':      return renderGroupField(ctx, locked);
      default:           return el('div', 'field field-unknown', field.kind);
    }
  }

  // Group selector — reassigns a user feature to any group (sets `__group`).
  function renderGroupField(ctx, locked) {
    const { item } = ctx;
    const wrap = el('div', 'field field-select');
    wrap.append(el('span', 'field-label', 'Group'));
    const sel = document.createElement('select');
    sel.className = 'field-input';
    sel.dataset.field = '__group';
    sel.disabled = !!locked;
    const current = effectiveGroup(item.feature);
    for (const opt of groupOptions(item.feature)) {
      const o = document.createElement('option');
      o.value = opt.id;
      o.textContent = opt.label;
      if (opt.id === current) o.selected = true;
      sel.append(o);
    }
    sel.addEventListener('change', () => {
      item.props.__group = sel.value;
      item.props.__locked = false;                  // a feature the user placed stays editable
      const target = findNodeById(sel.value);
      if (target) expandTo(target);
      selection = { kind: 'item', nodeId: sel.value, key: item.key };  // follow it to its new home
      rerender();
    });
    wrap.append(sel);
    return wrap;
  }

  function renderSelectField(field, item, locked) {
    const wrap = el('div', 'field field-select');
    wrap.append(el('span', 'field-label', field.label));
    const sel = document.createElement('select');
    sel.className = 'field-input';
    sel.dataset.field = field.prop;
    sel.disabled = !!locked;
    const current = item.props[field.prop] || '';
    for (const opt of field.options) {
      const o = document.createElement('option');
      o.value = opt;
      o.textContent = opt;
      if (current === opt) o.selected = true;
      sel.append(o);
    }
    sel.addEventListener('change', () => { item.props[field.prop] = sel.value; rerender(); });
    wrap.append(sel);
    return wrap;
  }

  function renderTextField(field, item, locked) {
    const wrap = el('div', 'field field-text');
    wrap.append(el('span', 'field-label', field.label));
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'field-input';
    input.value = item.props[field.prop] || '';
    input.dataset.field = field.prop;
    input.disabled = !!locked;
    input.addEventListener('input', () => { item.props[field.prop] = input.value; });
    input.addEventListener('change', () => rerender());
    wrap.append(input);
    return wrap;
  }

  // The control row inside the generic edit module: a DECLARATIVE list of icon
  // toggles. Each edit context (group, item, future things) just NAMES the
  // toggles it wants; the toggle binds itself to whatever is in ctx (node for a
  // layer, item for a feature). This is what lets "anything" reuse the one edit
  // module — there is no per-row special-casing left.
  const TOGGLES = {
    visibility: (ctx) => eyeToggle(ctx.node),                       // layer on/off (group)
    star:       (ctx) => starButton(ctx.item.props.highlight === true, () => toggleItemStar(ctx.item)),
    lock:       (ctx) => ctx.item
      ? lockButton(effectiveItemLock(ctx.node, ctx.item), () => toggleItemLock(ctx.node, ctx.item))
      : lockButton(!!ctx.node.locked, () => toggleGroupLock(ctx.node))
  };

  function renderControlsField(field, ctx, locked) {
    const wrap = el('div', 'field field-controls');
    for (const name of (field.toggles || [])) {
      const make = TOGGLES[name];
      if (make) wrap.append(make(ctx));
    }
    // The lock gates the fields BELOW it (not itself); explain that when locked.
    if (ctx.item && locked) wrap.append(el('span', 'edit-locked-hint-text', 'Locked — unlock to edit'));
    return wrap;
  }


  function renderStaticField(field) {
    const wrap = el('div', 'field field-static');
    wrap.append(el('span', 'field-label', field.label));
    wrap.append(el('span', 'field-value', field.value || '—'));
    return wrap;
  }

  // --- Actions (per-feature + per-layer) -------------------------------------
  const ACTIONS = {
    fly:     { label: '🎯 Fly to',            title: 'Center the map on this feature',                run: (c) => flyToItem(c.item) },
    copy:    { label: '⧉ Copy GeoJSON',        title: 'Copy this feature as GeoJSON',                  run: (c) => copyFeature(c.item) },
    move:    { label: '✋ Move',               title: 'Move — then click the map',         gated: true, run: (c) => startMove(c.node, c.item) },
    delete:  { label: '🗑 Delete',             title: 'Delete this feature',  danger: true, gated: true, run: (c) => deleteItem(c.node, c.item) },
    copyAll: { label: '⧉ Copy all as GeoJSON', title: 'Copy this layer as a GeoJSON FeatureCollection', run: (c) => copyAllFeatures(c.node) }
  };

  function renderActionsField(field, ctx, locked) {
    const wrap = el('div', 'field field-actions');
    for (const name of field.actions) {
      const spec = ACTIONS[name];
      if (!spec) continue;
      const btn = el('button', 'edit-action' + (spec.danger ? ' danger' : ''), spec.label);
      btn.type = 'button';
      btn.title = spec.title;
      if (spec.gated && locked) btn.disabled = true;
      btn.addEventListener('click', () => spec.run(ctx));
      wrap.append(btn);
    }
    return wrap;
  }

  // --- Source / provenance read-out ------------------------------------------
  // The northstar product test: a reader must see where a feature came from, how
  // trusted it is, whether it can be published, when it was checked. The data is
  // re-baked to the canonical schema, so this is now just the five provenance
  // fields — no per-source alias list. Each auto-hides when blank.
  const PROVENANCE_KEYS = [
    ['source', 'Source'], ['confidence', 'Confidence'], ['permission', 'Permission'],
    ['status', 'Status'], ['last_checked', 'Last checked']
  ];
  function provenanceFields(props) {
    return PROVENANCE_KEYS
      .filter(([k]) => props[k] != null && String(props[k]).trim() !== '')
      .map(([k, label]) => ({ kind: 'static', label, value: String(props[k]) }));
  }

  // --- Geometry helpers ------------------------------------------------------
  function eachCoord(geometry, fn) {
    const walk = (a) => { if (typeof a[0] === 'number') fn(a); else a.forEach(walk); };
    if (geometry && geometry.coordinates) walk(geometry.coordinates);
  }
  function geometryBounds(geometry) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    eachCoord(geometry, ([x, y]) => {
      if (x < minX) minX = x; if (y < minY) minY = y;
      if (x > maxX) maxX = x; if (y > maxY) maxY = y;
    });
    return minX === Infinity ? null : [[minX, minY], [maxX, maxY]];
  }
  function geometryCenter(geometry) {
    const b = geometryBounds(geometry);
    return b ? [(b[0][0] + b[1][0]) / 2, (b[0][1] + b[1][1]) / 2] : null;
  }

  // --- Action handlers -------------------------------------------------------
  function flyToItem(item) {
    const g = item.feature && item.feature.geometry;
    if (!g) return;
    if (g.type === 'Point') { map.flyTo({ center: g.coordinates, zoom: Math.max(map.getZoom(), 15), duration: 600 }); return; }
    const b = geometryBounds(g);
    if (b) map.fitBounds(b, { padding: 80, maxZoom: 17, duration: 600 });
  }

  function cleanFeature(feature) {
    const props = { ...(feature.properties || {}) };
    delete props._id; delete props.__locked;          // strip panel-internal keys
    return { type: 'Feature', geometry: feature.geometry, properties: props };
  }
  async function clipboardWrite(text) {
    try { if (navigator.clipboard && navigator.clipboard.writeText) { await navigator.clipboard.writeText(text); return true; } } catch (_) { /* fall through */ }
    try {
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.append(ta); ta.select();
      const ok = document.execCommand('copy'); ta.remove(); return ok;
    } catch (_) { return false; }
  }
  function copyFeature(item) {
    const text = JSON.stringify(cleanFeature(item.feature), null, 2);
    window.__lastCopy = text;                          // observable hook for verifiers
    clipboardWrite(text); showToast('Feature copied as GeoJSON');
  }
  function copyAllFeatures(node) {
    const fc = { type: 'FeatureCollection', features: deriveItems(node).map((it) => cleanFeature(it.feature)) };
    const text = JSON.stringify(fc, null, 2);
    window.__lastCopy = text;
    clipboardWrite(text); showToast(`Copied ${fc.features.length} feature(s) as GeoJSON`);
  }

  function deleteItem(node, item) {
    const fc = LOADED[node.items.source];
    if (!fc) return;
    const i = fc.features.indexOf(item.feature);
    if (i >= 0) fc.features.splice(i, 1);
    const source = map.getSource(node.items.source);
    if (source) source.setData(fc);
    if (isSelected({ kind: 'item', nodeId: node.id, key: item.key })) selection = null;
    rerender();
  }

  // --- Move (relocate a point / translate a line or polygon) -----------------
  let moving = null;     // { node, item } while moving, else null
  function startMove(node, item) {
    if (placing) endDraw();
    moving = { node, item };
    map.getCanvas().style.cursor = 'crosshair';
    rerender();
  }
  function endMove() { moving = null; map.getCanvas().style.cursor = ''; }
  function cancelMove() { if (!moving) return; endMove(); rerender(); }
  function applyMove(lngLat) {
    const { node, item } = moving;
    const g = item.feature.geometry;
    if (g.type === 'Point') {
      g.coordinates = lngLat;
    } else {
      const c = geometryCenter(g);
      if (!c) { endMove(); rerender(); return; }
      const dx = lngLat[0] - c[0], dy = lngLat[1] - c[1];
      eachCoord(g, (p) => { p[0] += dx; p[1] += dy; });
    }
    const source = map.getSource(node.items.source);
    if (source) source.setData(LOADED[node.items.source]);
    endMove();
    selection = { kind: 'item', nodeId: node.id, key: item.key };
    rerender();
  }

  // --- Reveal: click a feature on the map → select it in the panel -----------
  function nodeWalk(visit) {
    const rec = (node, parents, section) => {
      visit(node, parents, section);
      if (node.children) node.children.forEach((c) => rec(c, [...parents, node], section));
    };
    for (const section of PANEL_MODEL.sections) for (const n of section.nodes) rec(n, [], section);
  }
  function findNodeByLayer(layerId) {
    let found = null;
    nodeWalk((n) => { if (!found && n.items && n.mapLayers && n.mapLayers.includes(layerId)) found = n; });
    return found;
  }
  function expandTo(node) {
    nodeWalk((n, parents, section) => {
      if (n === node) { section.collapsed = false; node.expanded = true; parents.forEach((p) => { p.expanded = true; }); }
    });
  }
  function revealAtPoint(point) {
    if (!point) return;
    const ids = [];
    nodeWalk((n) => { if (n.items && n.mapLayers) ids.push(...n.mapLayers); });
    const layers = ids.filter((id) => map.getLayer(id));
    if (!layers.length) return;
    const box = [[point.x - 4, point.y - 4], [point.x + 4, point.y + 4]];   // a touch-sized target
    const hits = map.queryRenderedFeatures(box, { layers });
    if (!hits.length) return;
    const node = findNodeByLayer(hits[0].layer.id);
    if (!node || !node.items || !node.items.key) return;
    const key = String(node.items.key(hits[0].properties || {}));
    expandTo(node);
    selection = { kind: 'item', nodeId: node.id, key };
    rerender();
  }

  // --- Left sidebar: POI / user highlights -----------------------------------
  // Stars are the user's highlight: a starred feature surfaces here, under POI,
  // exactly like the live app's left-rail POI tab. One model, one renderer — the
  // list is DERIVED from the same PANEL_MODEL (every item whose props.highlight
  // is true), grouped by its layer node. Clicking a row flies to it and selects
  // it in the right panel. No second source of truth.
  function collectHighlighted() {
    const groups = [];
    nodeWalk((node) => {
      if (node.kind !== 'layer' || !node.items) return;
      const hits = deriveItems(node).filter((it) => it.props.highlight === true);
      if (hits.length) groups.push({ node, items: hits });
    });
    return groups;
  }

  function renderLeftPanel() {
    const host = document.getElementById('leftBody');
    if (!host) return;
    host.textContent = '';
    host.append(el('h1', 'panel-title', 'POI'));
    const groups = collectHighlighted();
    if (!groups.length) {
      host.append(el('p', 'poi-empty', 'Nothing starred yet. Click ★ on any item to surface it here under POI.'));
      return;
    }
    for (const g of groups) {
      const grp = el('div', 'poi-group');
      const head = el('div', 'poi-group-head');
      head.append(el('span', 'poi-group-label', g.node.label));
      head.append(el('span', 'poi-group-count', String(g.items.length)));
      grp.append(head);
      for (const item of g.items) {
        const row = el('button', 'poi-row', item.label);
        row.type = 'button';
        row.dataset.nodeId = g.node.id;
        row.dataset.key = item.key;
        row.addEventListener('click', () => gotoPoi(g.node, item));
        grp.append(row);
      }
      host.append(grp);
    }
  }

  function gotoPoi(node, item) {
    if (!node.visible) setLayerVisibility(node, true);   // a flown-to POI should be visible
    flyToItem(item);
    expandTo(node);
    selection = { kind: 'item', nodeId: node.id, key: item.key };
    rerender();
  }

  // --- Toast (brief confirmation, e.g. after a copy) -------------------------
  function showToast(msg) {
    const t = el('div', 'panel-toast', msg);
    document.body.append(t);
    setTimeout(() => t.remove(), 1300);
  }

  // --- Model -> map ----------------------------------------------------------
  function setLayerVisibility(node, on) {
    node.visible = on;
    for (const id of node.mapLayers) {
      if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', on ? 'visible' : 'none');
    }
  }

  // Push the model's declared visibility onto the map once layers exist.
  function applyAllVisibility() {
    const walk = (node) => {
      if (node.kind === 'layer') setLayerVisibility(node, node.visible);
      if (node.children) node.children.forEach(walk);
    };
    for (const section of PANEL_MODEL.sections) section.nodes.forEach(walk);
  }

  // --- Create (user-entered features) ----------------------------------------
  let placing = null;     // { node, geomType } while drawing, else null
  let draftVertices = []; // accumulated [lng,lat] for line/polygon
  let createSeq = 0;      // monotonic id source — no Date.now/random needed

  function startCreate(node) {
    moving = null;                              // creating and moving are mutually exclusive
    placing = { node, geomType: node.create.geomType };
    draftVertices = [];
    node.expanded = true;                       // so the new item is visible
    map.getCanvas().style.cursor = 'crosshair';
    map.doubleClickZoom.disable();              // dbl-click finishes a draw
    rerender();
  }

  function endDraw() {
    placing = null;
    draftVertices = [];
    map.getCanvas().style.cursor = '';
    map.doubleClickZoom.enable();
    clearDraft();
  }

  function cancelCreate() {
    if (!placing) return;
    endDraw();
    rerender();
  }

  function placeClick(lngLat) {
    if (placing.geomType === 'Point') {
      commitFeature({ type: 'Point', coordinates: lngLat });
    } else {
      draftVertices.push(lngLat);
      updateDraft();
    }
  }

  function finishDraw() {
    const verts = dedupeConsecutive(draftVertices);
    if (placing.geomType === 'LineString') {
      if (verts.length < 2) { cancelCreate(); return; }
      commitFeature({ type: 'LineString', coordinates: verts });
    } else {                                     // Polygon — close the ring
      if (verts.length < 3) { cancelCreate(); return; }
      commitFeature({ type: 'Polygon', coordinates: [[...verts, verts[0]]] });
    }
  }

  function commitFeature(geometry) {
    const node = placing.node;
    const src = node.create.source;
    createSeq += 1;
    const id = 'u' + createSeq;
    const feature = {
      type: 'Feature', geometry,
      properties: { _id: id, ...node.create.defaultProps(createSeq) }
    };
    LOADED[src].features.push(feature);
    const source = map.getSource(src);
    if (source) source.setData(LOADED[src]);
    endDraw();
    selection = { kind: 'item', nodeId: node.id, key: id };   // select → edit it
    rerender();
  }

  function dedupeConsecutive(coords) {
    const out = [];
    for (const c of coords) {
      const last = out[out.length - 1];
      if (!last || last[0] !== c[0] || last[1] !== c[1]) out.push(c);
    }
    return out;
  }

  // In-progress draw feedback (dashed line + vertex dots).
  function emptyFC() { return { type: 'FeatureCollection', features: [] }; }
  function updateDraft() {
    const feats = draftVertices.map((c) => ({ type: 'Feature', geometry: { type: 'Point', coordinates: c }, properties: {} }));
    if (draftVertices.length >= 2) {
      feats.push({ type: 'Feature', geometry: { type: 'LineString', coordinates: draftVertices }, properties: {} });
    }
    const s = map.getSource('__draft');
    if (s) s.setData({ type: 'FeatureCollection', features: feats });
  }
  function clearDraft() {
    const s = map.getSource('__draft');
    if (s) s.setData(emptyFC());
  }

  map.on('click', (e) => {
    const ll = [e.lngLat.lng, e.lngLat.lat];
    if (placing) { placeClick(ll); return; }
    if (moving) { applyMove(ll); return; }
    revealAtPoint(e.point);                     // click a feature → select it in the panel
  });
  map.on('dblclick', (e) => { if (placing && placing.geomType !== 'Point') finishDraw(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { cancelCreate(); cancelMove(); } });

  // --- Boot ------------------------------------------------------------------
  function loadMapImage(spec) {
    return new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => { try { if (!map.hasImage(spec.name)) map.addImage(spec.name, img, { pixelRatio: 2 }); } catch (_) { /* ignore */ } resolve(); };
      img.onerror = () => resolve();            // a missing icon must not break the load
      img.src = spec.url;
    });
  }

  map.on('load', async () => {
    // Fetch every GeoJSON source in PARALLEL first (27 files, one is ~14 MB),
    // then add sources + layers in declared order so draw-order is preserved.
    await Promise.all(MAP_DATA.map(async (set) => {
      if (set.raster || set.rasterDem || set.image || !set.url) return;
      try {
        let data = await (await fetch(set.url)).json();
        if (set.resolve) data = set.resolve(data);
        set.__data = data;
      } catch (err) {
        console.error('failed to fetch', set.source, err);
      }
    }));
    for (const set of MAP_DATA) {
      try {
        if (set.images) await Promise.all(set.images.map(loadMapImage));
        if (set.raster) {
          map.addSource(set.source, Object.assign({ type: 'raster' }, set.raster));
        } else if (set.rasterDem) {
          map.addSource(set.source, Object.assign({ type: 'raster-dem' }, set.rasterDem));
        } else if (set.image) {
          map.addSource(set.source, { type: 'image', url: set.image.url, coordinates: set.image.coordinates });
        } else {
          const data = set.__data !== undefined ? set.__data : set.data;
          if (data === undefined) continue;          // fetch failed above (already logged)
          LOADED[set.source] = data;
          map.addSource(set.source, { type: 'geojson', data });
        }
        for (const layer of set.layers) map.addLayer(Object.assign({ source: set.source }, layer));
      } catch (err) {
        console.error('failed to load', set.source, err);
      }
    }
    // In-progress draw layer (dashed line + vertex dots while drawing).
    map.addSource('__draft', { type: 'geojson', data: emptyFC() });
    map.addLayer({ id: '__draft-line', source: '__draft', type: 'line', filter: ['==', ['geometry-type'], 'LineString'],
      paint: { 'line-color': '#b4561f', 'line-width': 2, 'line-dasharray': [2, 1] } });
    map.addLayer({ id: '__draft-pts', source: '__draft', type: 'circle', filter: ['==', ['geometry-type'], 'Point'],
      paint: { 'circle-radius': 4, 'circle-color': '#b4561f', 'circle-stroke-color': '#fff', 'circle-stroke-width': 1 } });
    applyAllVisibility();
    renderPanel(PANEL_MODEL, document.getElementById('panelBody'));
    renderLeftPanel();                           // POI / highlights sidebar (empty until the user stars)
    window.__panelReady = true;                  // end-of-boot signal for verifiers
  });

  // Expose for verifiers / console inspection (bare globals, harness-friendly).
  window.map = map;
  window.PANEL_MODEL = PANEL_MODEL;
  window.LOADED = LOADED;
})();
