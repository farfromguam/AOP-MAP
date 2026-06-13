// AOP viewer core — clean-room READ scaffold. Sprint 13, slice 1.
// Card: brain/tasks/13_viewer_extraction/viewer_core_scaffold.md
//
// This is the empty clean core the viewer-extraction sprint ports into. It is
// NOT a copy of js/main.js. Everything here was carried over from main.js on
// purpose; the move is the audit. What crossed:
//   - map construction + region/park bounds + bottom ⓘ attribution
//   - the published-layer sources + style (the curated vector layers the read
//     presets show) — NO dev-reference layers (9-patch AOI, lidar tile index,
//     NAIP, OSM service/tracks, SFWDA raster, synthetic activity, cemeteries)
//   - the preset / zoom / 3D systems
//
// What was deliberately LEFT in main.js (the debt the extraction routes around):
//   - the editor's checkbox registry (LAYER_TOGGLES bound to DOM toggles) —
//     replaced here by a DOM-free PRESET_LAYERS map (preset bool → layer ids)
//   - preset snapshot / layer-tuner / session-persistence tails of applyPreset
//     (savedPresetStates, syncLayerTunerFromSelection, persistViewerSessionState)
//   - feature popups (bindPopup → poiPopupHtml), search indexing (indexFeatures),
//     positioned-feature overrides (applyPositionedFeatures), the brand-logo
//     size-cap store, and the slider plumbing — all editor/POI surfaces that
//     come in later slices, none reached by applyPreset / goToView / 3D.
//
// Loaded as a classic <script>; wrapped in an IIFE so nothing leaks to window.

(function () {
  'use strict';

  // ── Bounds (main.js:9-18) ──────────────────────────────────────────────
  // The 9-patch data-acquisition AOI doubles as the camera leash (maxBounds).
  const REGION_BOUNDS = [[-85.782935283, 35.067164188], [-85.717154097, 35.117928496]];
  // Tighter-than-region fallback for the Park camera preset, used until
  // publish.geojson's park parcel loads.
  const PARK_BOUNDS_FALLBACK = [[-85.761008221, 35.084085624], [-85.739081159, 35.10100706]];

  // ── Map construction (main.js:123-166) ─────────────────────────────────
  const map = new maplibregl.Map({
    container: 'map',
    style: {
      version: 8,
      sources: {},
      layers: [
        { id: 'background', type: 'background', paint: { 'background-color': '#efe7d5' } }
      ]
    },
    center: [-85.75, 35.0925],
    zoom: 12,
    bearing: -90,
    maxBounds: REGION_BOUNDS,
    attributionControl: false
  });

  // Catch style/glyph/source errors from construction onward (main.js:151).
  map.on('error', (e) => { console.error(e.error || e); });

  // Two-finger pinch zooms immediately; keep drag-to-tilt + right-click rotate
  // for the 3D view (main.js:163).
  map.touchZoomRotate.disableRotation();

  // Bottom-left ⓘ attribution (main.js:166).
  map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-left');

  // Collapse the compact attribution to the ⓘ once the first source loads,
  // then unbind so later ⓘ taps are the user's (main.js:206-214).
  const collapseAttribOnce = () => {
    const el = document.querySelector('.maplibregl-ctrl-attrib.maplibregl-compact');
    if (!el) return;
    el.classList.remove('maplibregl-compact-show');
    el.removeAttribute('open');
    map.off('sourcedata', collapseAttribOnce);
  };
  map.on('sourcedata', collapseAttribOnce);

  // ── Control DOM (the pill-bar shell in viewer.html) ────────────────────
  const message = document.getElementById('message');
  const terrainToggle = document.getElementById('showTerrain'); // hidden checkbox: 3D state
  const terrainButton = document.getElementById('terrainButton');
  const presetButtons = [...document.querySelectorAll('.preset-bar button[data-preset]')];
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');

  let activePresetId = 'park';
  let parkViewBounds = null;

  // Named-feature search registry, filled by indexFeatures during map load.
  const searchIndex = [];
  let searchGroups = [];
  let searchMatches = [];
  let searchActive = -1;

  // ── Palette consts referenced by BUILT_IN_PRESETS (main.js:1556-1611) ───
  const SKY_ATMOSPHERE = {
    'sky-color': '#7AB3FF',
    'horizon-color': '#BCDFFE',
    'fog-color': '#FFFFFF',
    'sky-horizon-blend': 0.5,
    'horizon-fog-blend': 0.5,
    'fog-ground-blend': 0.5
  };
  // Land-cover fill/outline families: muted (Park) and relief (Topo). Also the
  // base paint for the land-cover layers below, so one definition serves both.
  const LANDCOVER_MUTED_FILL = ['match', ['get', 'class'],
    'forest_deciduous', '#b8c1a1',
    'forest_evergreen', '#a8b18f',
    'open_grass',       '#ddd2ad',
    'open_meadow',      '#d4c79f',
    'open_bare',        '#c7b890',
    '#b8c1a1'];
  const LANDCOVER_MUTED_OUTLINE = ['match', ['get', 'class'],
    'forest_deciduous', '#a6af8d',
    'forest_evergreen', '#969f7c',
    'open_grass',       '#cdc29c',
    'open_meadow',      '#c4b78d',
    'open_bare',        '#b7a87f',
    '#a6af8d'];
  const LANDCOVER_RELIEF_FILL = ['match', ['get', 'class'],
    'forest_deciduous', '#c0c6ad',
    'forest_evergreen', '#b1b89b',
    'open_grass',       '#e5dcbc',
    'open_meadow',      '#ddd2ae',
    'open_bare',        '#d1c5a0',
    '#c0c6ad'];
  const LANDCOVER_RELIEF_OUTLINE = ['match', ['get', 'class'],
    'forest_deciduous', '#aeb499',
    'forest_evergreen', '#9fa687',
    'open_grass',       '#d3caa8',
    'open_meadow',      '#cbc09b',
    'open_bare',        '#bfb28c',
    '#aeb499'];
  // Activity-hotspot opacity is referenced by the Park/Topo preset paints. The
  // activity-hotspots layer itself is dev-reference and not carried, so those
  // paint entries no-op (setPaint guards on getLayer) — the const stays so the
  // preset object ports verbatim.
  const ACTIVITY_HOTSPOT_OPACITY = [
    'interpolate', ['linear'], ['get', 'intensity_norm'],
    0, 0.12,
    0.4, 0.28,
    1, 0.58
  ];

  // ── Low-level layer helpers (main.js:1505-1515) ────────────────────────
  function setLayerVisibility(layerId, visible) {
    if (map.getLayer(layerId)) {
      map.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
    }
  }
  function setPaint(layerId, property, value) {
    if (map.getLayer(layerId)) {
      map.setPaintProperty(layerId, property, JSON.parse(JSON.stringify(value)));
    }
  }

  // ── Memoized fetch + GeoJSON bounds (main.js:7538-7665) ────────────────
  const _fetchJsonCache = new Map();
  function fetchJson(url, label) {
    if (_fetchJsonCache.has(url)) return _fetchJsonCache.get(url);
    const promise = (async () => {
      try {
        const response = await fetch(url, { cache: 'no-cache' });
        if (response.ok) return await response.json();
        console.warn(`${label}: HTTP ${response.status}`);
      } catch (error) {
        console.warn(`${label}:`, error);
      }
      return undefined;
    })();
    _fetchJsonCache.set(url, promise);
    return promise;
  }
  function extendBounds(bounds, coordinates) {
    if (typeof coordinates[0] === 'number') {
      const [lng, lat] = coordinates;
      if (lng < bounds.minLng) bounds.minLng = lng;
      if (lat < bounds.minLat) bounds.minLat = lat;
      if (lng > bounds.maxLng) bounds.maxLng = lng;
      if (lat > bounds.maxLat) bounds.maxLat = lat;
      return;
    }
    coordinates.forEach((part) => extendBounds(bounds, part));
  }
  function geojsonBounds(data) {
    const bounds = { minLng: Infinity, minLat: Infinity, maxLng: -Infinity, maxLat: -Infinity };
    (data?.features || [])
      .filter((feature) => feature.geometry?.coordinates)
      .forEach((feature) => extendBounds(bounds, feature.geometry.coordinates));
    return Number.isFinite(bounds.minLng)
      ? [[bounds.minLng, bounds.minLat], [bounds.maxLng, bounds.maxLat]]
      : null;
  }
  function fitToDataBounds(data) {
    const bounds = geojsonBounds(data);
    if (bounds) {
      map.fitBounds(bounds, { padding: 60, duration: 0, maxZoom: 14, bearing: map.getBearing() });
    }
  }

  // ── 3D terrain toggle (main.js:1625-1644) ──────────────────────────────
  function syncTerrainControl(enabled) {
    terrainToggle.checked = Boolean(enabled);
    terrainButton.classList.toggle('active', Boolean(enabled));
    terrainButton.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    terrainButton.title = enabled ? 'Return to 2D terrain view' : 'Toggle 3D terrain view';
  }
  function setTerrainEnabled(enabled) {
    syncTerrainControl(enabled);
    if (!map.getSource('aws-terrain-dem')) return;
    if (enabled) {
      map.setTerrain({ source: 'aws-terrain-dem', exaggeration: 1.4 });
      if (map.setSky) map.setSky(SKY_ATMOSPHERE);
      map.easeTo({ pitch: 60, duration: 800 });
    } else {
      map.setTerrain(null);
      if (map.setSky) map.setSky(undefined);
      map.easeTo({ pitch: 0, duration: 600 });
    }
  }

  // ── Zoom presets (main.js:7672-7703) ───────────────────────────────────
  // Camera-only; they do not touch layers or the layer presets.
  const PAVILION_VIEW = { center: [-85.748268, 35.090703], zoom: 17 };
  const VIEW_BEARING = -90;
  const VIEW_PITCH = 0;
  function goToView(view) {
    if (view === 'pavilion') {
      map.flyTo({ center: PAVILION_VIEW.center, zoom: PAVILION_VIEW.zoom, bearing: VIEW_BEARING, pitch: VIEW_PITCH, duration: 1100 });
      return;
    }
    if (view === 'park') {
      map.fitBounds(parkViewBounds || PARK_BOUNDS_FALLBACK, {
        padding: 20, bearing: VIEW_BEARING, pitch: VIEW_PITCH, duration: 1100, maxZoom: 15.5
      });
      return;
    }
    // Region: fit the 9-patch inset ~15% per side.
    const [[rw, rs], [re, rn]] = REGION_BOUNDS;
    const insetX = (re - rw) * 0.15;
    const insetY = (rn - rs) * 0.15;
    map.fitBounds(
      [[rw + insetX, rs + insetY], [re - insetX, rn - insetY]],
      { padding: 20, bearing: VIEW_BEARING, pitch: VIEW_PITCH, duration: 1100 }
    );
  }

  // ── Preset → layer-visibility map ──────────────────────────────────────
  // Extracted from main.js LAYER_TOGGLES (1655-1694): the [DOM toggle, layer
  // ids, presetId] rows, minus the DOM toggle (the editor's checkbox indirection
  // doesn't exist here) and minus the dev-reference layers the read core never
  // carries. A preset's `toggles[id]` boolean drives the mapped layers directly.
  // Toggle ids a preset names but that aren't here (showEventSchedule, showOsm*,
  // showSfwda, showCemeteries, showActivityHotspots, showEditorPois, …) are simply
  // ignored — those layers belong to later slices or to the dev pile.
  const PRESET_LAYERS = {
    showLandcover: ['landcover-forest', 'landcover-forest-outline'],
    showLandcover9: ['landcover-9patch-forest', 'landcover-9patch-forest-outline'],
    showHillshade: ['lidar-hillshade'],
    showContours: ['contours-minor', 'contours-index', 'contours-labels'],
    showSatellite: ['tnmap-satellite'],
    showRoads: ['roads-local-casing', 'roads-local', 'roads-connecting-casing', 'roads-connecting', 'roads-secondary-casing', 'roads-secondary', 'roads-ramp-casing', 'roads-ramp', 'roads-controlled-casing', 'roads-controlled', 'roads-labels'],
    showVisitorContext: ['visitor-context-fill', 'visitor-context-outline', 'visitor-context-labels'],
    showBrandLogos: ['brand-logos-icons'],
    showWater: ['water-area-fill', 'waterbody-fill', 'waterbody-outline', 'streams', 'stream-labels'],
    showSprings: ['water-points', 'water-point-labels'],
    showBuildings: ['building-footprint-fill', 'building-footprint-outline', 'building-footprint-aop-outline'],
    showAopTrailNetwork: ['aop-trail-network', 'aop-trail-network-labels'],
    showBoundaries: ['publish-boundary-fill', 'publish-boundaries'],
    showTrailheads: ['publish-trailheads'],
    showTrails: ['publish-trails']
  };

  // ── BUILT_IN_PRESETS (ported verbatim from main.js:4987-5312) ──────────
  // The style registry: the four read presets, each a full toggle map + paint
  // set. Carried byte-for-byte (including paint entries for layers the read core
  // doesn't draw, which no-op) so the cost is honest and there is no transcription
  // divergence from the live page's presets.
  const BUILT_IN_PRESETS = {
    park: {
      label: 'Park',
      toggles: {
        showLandcover: true, showLandcover9: true, showHillshade: false, showContours: false,
        showActivityHotspots: false, showSyntheticActivity: false, showEventSchedule: false,
        showSatellite: false, showUsdaNaip: false, showNinePatch: false, showLidarTiles: false,
        showRoads: true, showVisitorContext: true, showBrandLogos: true, showWater: true,
        showSprings: false, showCemeteries: false, showBuildings: true, showOsmPark: false,
        showOsmTracks: false, showOsmService: false, showOsmNamed: false, showSfwda: false,
        showTrails: false, showAopTrailNetwork: true, showBoundaries: true, showTrailheads: true,
        showEditorPois: true
      },
      sliders: { landcover9Opacity: 55, sfwdaOpacity: 70, sfwdaMultiply: 0 },
      paints: {
        background: { 'background-color': '#efe7d5' },
        'landcover-forest': { 'fill-color': LANDCOVER_MUTED_FILL, 'fill-opacity': 0.9 },
        'landcover-forest-outline': { 'line-color': LANDCOVER_MUTED_OUTLINE, 'line-width': 0.8, 'line-opacity': 0.55 },
        'landcover-9patch-forest': { 'fill-color': LANDCOVER_MUTED_FILL, 'fill-opacity': 0.55 },
        'landcover-9patch-forest-outline': { 'line-color': LANDCOVER_MUTED_OUTLINE, 'line-width': 0.6, 'line-opacity': 0.35 },
        'lidar-hillshade': {
          'hillshade-exaggeration': 0.6,
          'hillshade-shadow-color': '#3a2f22',
          'hillshade-highlight-color': '#fbf4e2',
          'hillshade-accent-color': '#6b5640'
        },
        'contours-minor': { 'line-color': '#c7b48f', 'line-opacity': ['interpolate', ['linear'], ['zoom'], 16.5, 0, 17.5, 0.75] },
        'contours-index': { 'line-color': '#a8906a', 'line-opacity': ['interpolate', ['linear'], ['zoom'], 15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 0.95, 0], 16, 0.95] },
        'contours-labels': { 'text-color': '#7d6a4a', 'text-opacity': ['interpolate', ['linear'], ['zoom'], 15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 1, 0], 16, 1] },
        'activity-hotspots-heat': { 'heatmap-opacity': 0.68 },
        'activity-hotspots-fill': { 'fill-opacity': ACTIVITY_HOTSPOT_OPACITY },
        'activity-hotspots-outline': { 'line-color': '#7f2f27', 'line-width': 1.1, 'line-opacity': 0.55 },
        'activity-hotspots-labels': { 'text-color': '#5b2d25', 'text-opacity': 1, 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.4 },
        streams: { 'line-color': '#7fa3ac', 'line-opacity': 0.9 },
        'stream-labels': { 'text-color': '#4a6c73', 'text-opacity': 1 },
        'water-area-fill': { 'fill-color': '#a8c5c9', 'fill-opacity': 0.55 },
        'waterbody-fill': { 'fill-color': '#9fbfc4', 'fill-opacity': 0.5 },
        'waterbody-outline': { 'line-color': '#6f9098', 'line-width': 1.2 },
        'visitor-context-fill': { 'fill-color': '#d8b173', 'fill-opacity': 0.18 },
        'visitor-context-outline': { 'line-color': '#8b5f38', 'line-width': 2.2, 'line-opacity': 0.9 },
        'visitor-context-labels': { 'text-color': '#4a3c2a', 'text-opacity': 1, 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 },
        'publish-boundary-fill': { 'fill-color': '#d8c8a2', 'fill-opacity': 0.1 },
        'publish-boundaries': { 'line-color': '#6e5a3c', 'line-width': 2.5, 'line-opacity': 1 },
        'publish-trails': { 'line-color': '#9a5a32', 'line-width': 3.5, 'line-opacity': 1 },
        'aop-trail-network': { 'line-color': ['coalesce', ['get', 'color'], '#888888'], 'line-width': 3, 'line-opacity': 0.92 },
        'publish-trailheads': { 'circle-color': '#6f8a5c', 'circle-radius': 6, 'circle-opacity': 1 },
        'osm-tracks': { 'line-color': '#9a5a32', 'line-width': 2, 'line-opacity': 0.95 },
        'osm-service': { 'line-color': '#a89a7e', 'line-width': 1.5, 'line-opacity': 0.85 },
        'roads-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 },
        'osm-named-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
      }
    },
    topo: {
      label: 'Topo',
      toggles: {
        showLandcover: true, showLandcover9: true, showHillshade: true, showContours: true,
        showActivityHotspots: false, showSyntheticActivity: false, showEventSchedule: false,
        showSatellite: false, showUsdaNaip: false, showNinePatch: false, showLidarTiles: false,
        showRoads: true, showVisitorContext: true, showBrandLogos: true, showWater: true,
        showSprings: true, showCemeteries: false, showBuildings: true, showOsmPark: false,
        showOsmTracks: false, showOsmService: false, showOsmNamed: false, showSfwda: false,
        showTrails: false, showAopTrailNetwork: true, showBoundaries: true, showTrailheads: true,
        showEditorPois: true
      },
      sliders: { landcover9Opacity: 38, sfwdaOpacity: 60, sfwdaMultiply: 100 },
      paints: {
        background: { 'background-color': '#e7ddc4' },
        'landcover-forest': { 'fill-color': LANDCOVER_RELIEF_FILL, 'fill-opacity': 0.62 },
        'landcover-forest-outline': { 'line-color': LANDCOVER_RELIEF_OUTLINE, 'line-width': 0.7, 'line-opacity': 0.35 },
        'landcover-9patch-forest': { 'fill-color': LANDCOVER_RELIEF_FILL, 'fill-opacity': 0.38 },
        'landcover-9patch-forest-outline': { 'line-color': LANDCOVER_RELIEF_OUTLINE, 'line-width': 0.5, 'line-opacity': 0.25 },
        'lidar-hillshade': {
          'hillshade-exaggeration': 0.45,
          'hillshade-shadow-color': '#7a6a52',
          'hillshade-highlight-color': '#f7eed8',
          'hillshade-accent-color': '#8a7860'
        },
        'contours-minor': { 'line-color': '#c6ad84', 'line-opacity': ['interpolate', ['linear'], ['zoom'], 16.5, 0, 17.5, 0.28], 'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.65, 16, 1.55] },
        'contours-index': { 'line-color': '#a8855b', 'line-opacity': ['interpolate', ['linear'], ['zoom'], 15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 0.5, 0], 16, 0.5], 'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.25, 16, 3.1] },
        'contours-labels': { 'text-color': '#8a6a42', 'text-opacity': ['interpolate', ['linear'], ['zoom'], 15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 1, 0], 16, 1] },
        'activity-hotspots-heat': { 'heatmap-opacity': 0.62 },
        'activity-hotspots-fill': { 'fill-opacity': ACTIVITY_HOTSPOT_OPACITY },
        'activity-hotspots-outline': { 'line-color': '#6e2a22', 'line-width': 1.25, 'line-opacity': 0.62 },
        'activity-hotspots-labels': { 'text-color': '#4e2a22', 'text-opacity': 1, 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.4 },
        streams: { 'line-color': '#4d8792', 'line-opacity': 0.95 },
        'stream-labels': { 'text-color': '#2f6570', 'text-opacity': 1 },
        'water-area-fill': { 'fill-color': '#8eb7be', 'fill-opacity': 0.62 },
        'waterbody-fill': { 'fill-color': '#83aeb6', 'fill-opacity': 0.58 },
        'waterbody-outline': { 'line-color': '#44747d', 'line-width': 1.5 },
        'publish-boundary-fill': { 'fill-color': '#e7c982', 'fill-opacity': 0.08 },
        'publish-boundaries': { 'line-color': '#4d3928', 'line-width': 3, 'line-opacity': 1 },
        'publish-trails': { 'line-color': '#7d4328', 'line-width': 3.8, 'line-opacity': 1 },
        'aop-trail-network': { 'line-color': '#ff5a14', 'line-width': 3.8, 'line-opacity': 1 },
        'publish-trailheads': { 'circle-color': '#546f4b', 'circle-radius': 6.5, 'circle-opacity': 1 },
        'visitor-context-fill': { 'fill-color': '#d2a95f', 'fill-opacity': 0.14 },
        'visitor-context-outline': { 'line-color': '#6f4e2e', 'line-width': 2.4, 'line-opacity': 0.86 },
        'visitor-context-labels': { 'text-color': '#3f3122', 'text-opacity': 1, 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 },
        'roads-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 },
        'osm-named-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
      }
    },
    trace: {
      label: 'Trace',
      toggles: {
        showLandcover: false, showLandcover9: false, showHillshade: true, showContours: false,
        showActivityHotspots: false, showSyntheticActivity: false, showEventSchedule: false,
        showSatellite: false, showUsdaNaip: false, showNinePatch: false, showLidarTiles: false,
        showRoads: true, showVisitorContext: false, showBrandLogos: true, showWater: false,
        showSprings: false, showCemeteries: false, showBuildings: true, showOsmPark: false,
        showOsmTracks: false, showOsmService: true, showOsmNamed: true, showSfwda: true,
        showTrails: false, showAopTrailNetwork: true, showBoundaries: false, showTrailheads: true,
        showEditorPois: true
      },
      sliders: { landcover9Opacity: 0, sfwdaOpacity: 64, sfwdaMultiply: 0 },
      paints: {
        background: { 'background-color': '#e7ddc4' },
        'usda-naip-satellite': { 'raster-opacity': 0 },
        'tnmap-satellite': { 'raster-opacity': 0 },
        'lidar-hillshade': {
          'hillshade-exaggeration': 0.82,
          'hillshade-shadow-color': '#2f2a21',
          'hillshade-highlight-color': '#fff4d9',
          'hillshade-accent-color': '#6f604c'
        },
        'publish-boundary-fill': { 'fill-color': '#fff0b8', 'fill-opacity': 0.03 },
        'publish-boundaries': { 'line-color': '#fff0b8', 'line-width': 3.4, 'line-opacity': 1 },
        'publish-trails': { 'line-color': '#ffb347', 'line-width': 4, 'line-opacity': 1 },
        'aop-trail-network': { 'line-color': ['coalesce', ['get', 'color'], '#888888'], 'line-width': 3.4, 'line-opacity': 0.95 },
        'aop-trail-network-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'publish-trailheads': { 'circle-color': '#ffe08a', 'circle-radius': 7, 'circle-opacity': 1 },
        'osm-park-outline': { 'line-color': '#d4ff86', 'line-width': 2.4 },
        'osm-tracks': { 'line-color': '#ff6b3d', 'line-width': 3, 'line-opacity': 0.98 },
        'osm-service': { 'line-color': '#ffd166', 'line-width': 2.5, 'line-opacity': 0.95 },
        'osm-named-points': { 'circle-color': '#ffd166', 'circle-stroke-color': '#33251a' },
        'osm-named-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'editor-poi-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'editor-poi-fill-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'editor-poi-line-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'cemetery-label': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'nine-patch-labels': { 'text-color': '#fff4cf', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'roads-labels': { 'text-color': '#fff4cf', 'text-opacity': 1, 'text-halo-color': '#15110d', 'text-halo-width': 2.2 },
        'activity-hotspots-heat': { 'heatmap-opacity': 0.82 },
        'activity-hotspots-fill': { 'fill-opacity': ['interpolate', ['linear'], ['get', 'intensity_norm'], 0, 0.16, 1, 0.62] },
        'activity-hotspots-outline': { 'line-color': '#ff6b3d', 'line-width': 1.5, 'line-opacity': 0.82 },
        'activity-hotspots-labels': { 'text-color': '#fff0b8', 'text-opacity': 1, 'text-halo-color': '#15110d', 'text-halo-width': 1.8 },
        'visitor-context-fill': { 'fill-color': '#ffe08a', 'fill-opacity': 0.1 },
        'visitor-context-outline': { 'line-color': '#ffe08a', 'line-width': 2.6, 'line-opacity': 0.9 },
        'visitor-context-labels': { 'text-color': '#fff4cf', 'text-opacity': 1, 'text-halo-color': '#15110d', 'text-halo-width': 2 },
        'building-footprint-fill': { 'fill-color': '#ffe0a6', 'fill-opacity': 0.22 },
        'building-footprint-outline': { 'line-color': '#fff0b8', 'line-width': 1.6, 'line-opacity': 0.88 },
        'building-footprint-aop-outline': { 'line-color': '#ff9f5a', 'line-width': 3.2, 'line-opacity': 0.95 },
        'search-highlight-line': { 'line-color': '#00d1ff' },
        'search-highlight-point': { 'circle-color': '#00d1ff', 'circle-stroke-color': '#00d1ff' }
      }
    },
    satellite: {
      label: 'Satellite',
      toggles: {
        showLandcover: false, showLandcover9: false, showHillshade: false, showContours: false,
        showActivityHotspots: false, showSyntheticActivity: false, showEventSchedule: false,
        showSatellite: true, showUsdaNaip: false, showNinePatch: false, showLidarTiles: false,
        showRoads: false, showVisitorContext: false, showBrandLogos: false, showWater: false,
        showSprings: false, showCemeteries: false, showBuildings: false, showOsmPark: false,
        showOsmTracks: false, showOsmService: false, showOsmNamed: false, showSfwda: false,
        showTrails: false, showAopTrailNetwork: false, showBoundaries: false, showTrailheads: false,
        showEditorPois: false
      },
      sliders: { landcover9Opacity: 0, sfwdaOpacity: 0, sfwdaMultiply: 0 },
      paints: {
        background: { 'background-color': '#efe7d5' },
        'tnmap-satellite': { 'raster-opacity': 1 },
        'usda-naip-satellite': { 'raster-opacity': 0 }
      }
    }
  };

  // ── Preset apply (DOM-free essence of main.js applyPreset 5383-5413) ────
  // main.js drove visibility by writing each preset bool into the editor's
  // checkboxes, then read those checkboxes back in updateLayerVisibility. The
  // clean core skips the round-trip: it reads the preset bool and drives the
  // mapped layers straight. Paints apply verbatim (no-op on layers not carried).
  function applyPaintState(paints) {
    for (const [layerId, properties] of Object.entries(paints || {})) {
      for (const [property, value] of Object.entries(properties || {})) {
        setPaint(layerId, property, value);
      }
    }
  }
  function applyPreset(presetId) {
    const preset = BUILT_IN_PRESETS[presetId];
    if (!preset) return;
    activePresetId = presetId;
    for (const [toggleId, layerIds] of Object.entries(PRESET_LAYERS)) {
      const on = Boolean(preset.toggles[toggleId]);
      for (const id of layerIds) setLayerVisibility(id, on);
    }
    applyPaintState(preset.paints);
    presetButtons.forEach((button) => {
      button.classList.toggle('active', button.dataset.preset === presetId);
    });
  }

  // ── Feature search (ported from main.js:9977-10350) ────────────────────
  // Fully client-side over the already-loaded GeoJSON — no geocoder, works
  // offline. Editor seams severed vs main.js: indexFeatures' `toggleFor` (a DOM
  // checkbox) becomes `layersFor` (the layer-ids to make visible on landing,
  // reusing PRESET_LAYERS), and the `featureListBindingFor` editor-list arg +
  // the session-persistence calls are dropped.
  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Register every named feature of a FeatureCollection. kindFor/layersFor may
  // be a value or a (props) => value function; layersFor returns the layer-id
  // array to unhide when a result lands (so the camera doesn't fly to a hidden
  // layer). aliasesFor (optional) returns extra search terms (e.g. "trail 15").
  function indexFeatures(data, kindFor, layersFor, aliasesFor) {
    if (!data || !data.features) return;
    for (const feature of data.features) {
      const props = feature.properties || {};
      const name = props.name || props.gnis_name;
      if (!name || !feature.geometry) continue;
      const layers = typeof layersFor === 'function' ? layersFor(props) : layersFor;
      const entry = {
        name: String(name),
        kind: typeof kindFor === 'function' ? kindFor(props) : kindFor,
        layers: Array.isArray(layers) ? layers : (layers ? [layers] : []),
        geometry: feature.geometry,
        description: props.description || null
      };
      if (aliasesFor) {
        const raw = aliasesFor(props);
        const aliases = (Array.isArray(raw) ? raw : [raw])
          .map((a) => String(a || '').trim())
          .filter(Boolean);
        if (aliases.length) entry.aliases = aliases;
      }
      searchIndex.push(entry);
    }
  }

  // Trails imported as "<name> (segment N)" collapse to one searchable trail.
  function searchDisplayName(name) {
    return name.replace(/\s*\(segment[^)]*\)\s*$/i, '').trim();
  }

  // Collapse per-segment entries into one group per name+kind, framed by the
  // union of their extents; aliases + the unhide layer-set union into the group.
  function buildSearchGroups() {
    const byKey = new Map();
    for (const entry of searchIndex) {
      const display = searchDisplayName(entry.name) || entry.name;
      const key = display.toLowerCase() + '|' + entry.kind;
      let group = byKey.get(key);
      if (!group) {
        group = { name: display, kind: entry.kind, layers: [], geometries: [], aliases: [], description: null };
        byKey.set(key, group);
      }
      if (!group.description && entry.description) group.description = entry.description;
      group.geometries.push(entry.geometry);
      for (const id of entry.layers) if (!group.layers.includes(id)) group.layers.push(id);
      if (entry.aliases) {
        for (const alias of entry.aliases) if (!group.aliases.includes(alias)) group.aliases.push(alias);
      }
    }
    searchGroups = [...byKey.values()].sort((a, b) => a.name.localeCompare(b.name));
  }

  function clearSearchResults() {
    searchResults.innerHTML = '';
    searchResults.style.display = 'none';
    searchMatches = [];
    searchActive = -1;
  }

  // Anchor the position:fixed dropdown to the input's box so it escapes any clip
  // but tracks the input across scroll/resize.
  function positionSearchResults() {
    const rect = searchInput.getBoundingClientRect();
    searchResults.style.left = `${rect.left}px`;
    searchResults.style.top = `${rect.bottom + 4}px`;
    searchResults.style.width = `${rect.width}px`;
  }

  // Match the query against the group name OR any alias. A leading `#` flags a
  // deliberate tag query — aliases only, so a name substring can't shadow it.
  function searchGroupMatchesQuery(group, query) {
    const tagOnly = query.startsWith('#');
    if (!tagOnly && group.name.toLowerCase().includes(query)) return true;
    if (group.aliases && group.aliases.length) {
      for (const alias of group.aliases) {
        if (alias.toLowerCase().includes(query)) return true;
      }
    }
    return false;
  }

  // Relevance rank (lower = better): exact name > prefix > mid-substring. For
  // digit-leading (trail-number) queries, float trails above non-trails so the
  // 1-prefixed trails aren't crowded out by 1-prefixed building addresses.
  function searchRank(group, query) {
    const n = group.name.toLowerCase();
    let base;
    if (n === query) base = 0;
    else if (n.startsWith(query)) base = 1;
    else if (group.aliases && group.aliases.some((a) => a.toLowerCase() === query)) base = 1;
    else if (n.includes(query)) base = 2;
    else base = 3;
    if (base > 0 && /^\d/.test(query)) {
      return base * 2 + (group.kind === 'trail' ? 0 : 1);
    }
    return base;
  }

  function renderSearchResults() {
    const query = searchInput.value.trim().toLowerCase();
    // 2+ chars to avoid flooding, EXCEPT a lone digit (a valid trail number).
    if (query.length < 2 && !/^\d$/.test(query)) {
      searchResults.style.display = 'none';
      searchMatches = [];
      return;
    }
    // Widen the cap for digit-leading queries so the full 1-prefixed trail set
    // is reachable (the dropdown scrolls).
    const limit = /^\d/.test(query) ? 12 : 8;
    searchMatches = searchGroups
      .filter((group) => searchGroupMatchesQuery(group, query))
      .sort((a, b) => searchRank(a, query) - searchRank(b, query))
      .slice(0, limit);
    if (!searchMatches.length) {
      searchResults.innerHTML = '<div class="search-empty">No match</div>';
      searchResults.style.display = 'block';
      positionSearchResults();
      return;
    }
    searchResults.innerHTML = searchMatches
      .map((match, i) => {
        // A catalogued trail row gains a second, muted line with its curated
        // description (truncated). Non-trail / no-desc rows render single-line.
        let desc = null;
        if (match.kind === 'trail' && match.description) {
          desc = match.description.length > 80
            ? match.description.slice(0, 79).trimEnd() + '…'
            : match.description;
        }
        const head = `<div class="search-item${i === searchActive ? ' active' : ''}" data-i="${i}">`;
        if (!desc) {
          return head
            + `<span>${escapeHtml(match.name)}</span>`
            + `<span class="search-kind">${escapeHtml(match.kind)}</span></div>`;
        }
        return head
          + `<span class="search-result-text">`
          + `<span class="search-result-label">${escapeHtml(match.name)}</span>`
          + `<span class="search-result-desc"></span>`
          + `</span>`
          + `<span class="search-kind">${escapeHtml(match.kind)}</span></div>`;
      })
      .join('');
    // Descriptions via textContent (not innerHTML) so first-party copy is never
    // parsed as markup. Paired by index with the matches above.
    const descNodes = searchResults.querySelectorAll('.search-item');
    searchMatches.forEach((match, i) => {
      if (match.kind !== 'trail' || !match.description) return;
      const node = descNodes[i] && descNodes[i].querySelector('.search-result-desc');
      if (node) {
        node.textContent = match.description.length > 80
          ? match.description.slice(0, 79).trimEnd() + '…'
          : match.description;
      }
    });
    searchResults.style.display = 'block';
    positionSearchResults();
  }

  // Search-result pulse — `osc` runs 0→1→0 a few times across the duration.
  const PULSE_DURATION_MS = 2600;
  const PULSE_FLASHES = 3;
  const PULSE_LINE_OPACITY_MIN = 0.2;
  const PULSE_LINE_OPACITY_RANGE = 0.7;
  const PULSE_LINE_WIDTH_MIN = 5;
  const PULSE_LINE_WIDTH_RANGE = 9;
  const PULSE_POINT_RADIUS_MIN = 12;
  const PULSE_POINT_RADIUS_RANGE = 16;
  let pulseRAF = null;
  function pulseHighlight() {
    if (!map.getLayer('search-highlight-line')) return;
    setLayerVisibility('search-highlight-line', true);
    setLayerVisibility('search-highlight-point', true);
    if (pulseRAF) cancelAnimationFrame(pulseRAF);
    const start = performance.now();
    function frame(now) {
      const t = (now - start) / PULSE_DURATION_MS;
      if (t >= 1) {
        setLayerVisibility('search-highlight-line', false);
        setLayerVisibility('search-highlight-point', false);
        pulseRAF = null;
        return;
      }
      const osc = 0.5 + 0.5 * Math.cos(t * Math.PI * 2 * PULSE_FLASHES);
      if (map.getLayer('search-highlight-line')) {
        map.setPaintProperty('search-highlight-line', 'line-opacity',
          PULSE_LINE_OPACITY_MIN + PULSE_LINE_OPACITY_RANGE * osc);
        map.setPaintProperty('search-highlight-line', 'line-width',
          PULSE_LINE_WIDTH_MIN + PULSE_LINE_WIDTH_RANGE * osc);
      }
      if (map.getLayer('search-highlight-point')) {
        map.setPaintProperty('search-highlight-point', 'circle-radius',
          PULSE_POINT_RADIUS_MIN + PULSE_POINT_RADIUS_RANGE * osc);
        map.setPaintProperty('search-highlight-point', 'circle-stroke-opacity',
          PULSE_LINE_OPACITY_MIN + PULSE_LINE_OPACITY_RANGE * osc);
      }
      pulseRAF = requestAnimationFrame(frame);
    }
    pulseRAF = requestAnimationFrame(frame);
  }

  function gotoMatch(index) {
    const match = searchMatches[index];
    if (!match) return;
    const bounds = { minLng: Infinity, minLat: Infinity, maxLng: -Infinity, maxLat: -Infinity };
    for (const geometry of match.geometries) {
      if (geometry.coordinates) extendBounds(bounds, geometry.coordinates);
    }
    if (!Number.isFinite(bounds.minLng)) return;
    // Unhide the result's layer(s) so it's visible on arrival even if the
    // current preset has them off (replaces main.js's toggle.checked = true).
    for (const id of match.layers) setLayerVisibility(id, true);
    if (bounds.minLng === bounds.maxLng && bounds.minLat === bounds.maxLat) {
      map.flyTo({ center: [bounds.minLng, bounds.minLat], zoom: 16, duration: 1100 });
    } else {
      map.fitBounds(
        [[bounds.minLng, bounds.minLat], [bounds.maxLng, bounds.maxLat]],
        { padding: 90, maxZoom: 16.5, duration: 1100, bearing: map.getBearing() }
      );
    }
    const highlight = map.getSource('search-highlight');
    if (highlight) {
      highlight.setData({
        type: 'FeatureCollection',
        features: match.geometries.map((geometry) => ({ type: 'Feature', properties: {}, geometry }))
      });
      pulseHighlight();
    }
    searchInput.value = match.name;
    clearSearchResults();
  }

  // ── Layer build ────────────────────────────────────────────────────────
  // Each add-site is the source + style only, ported from main.js. The popup
  // bindings, search indexing, feature-list registration, and positioned-feature
  // override replays that wrap each add-site in main.js are intentionally NOT
  // carried — none are reached by presets / zoom / 3D. Add order matches main.js
  // so the layer z-order is preserved.
  map.on('load', async () => {
    // --- Land cover, 9-patch (NAIP 2023 + lidar) — base of the stack (main.js:7767) ---
    const landcover9Data = await fetchJson('./data/aop_landcover_9patch.geojson', '9-patch land cover missing');
    if (landcover9Data) {
      map.addSource('aop-landcover-9patch', {
        type: 'geojson', data: landcover9Data,
        attribution: 'Land cover: classified from USDA NAIP 2023 + USGS 3DEP lidar'
      });
      map.addLayer({
        id: 'landcover-9patch-forest', type: 'fill', source: 'aop-landcover-9patch',
        // main.js seeds this from the (editor-only) opacity slider; the clean
        // core uses the Park-preset default 0.55 directly (applyPreset resets it).
        paint: { 'fill-color': LANDCOVER_MUTED_FILL, 'fill-opacity': 0.55 }
      });
      map.addLayer({
        id: 'landcover-9patch-forest-outline', type: 'line', source: 'aop-landcover-9patch',
        paint: { 'line-color': LANDCOVER_MUTED_OUTLINE, 'line-width': 0.6, 'line-opacity': 0.35 }
      });
    }

    // --- Land cover, park-clipped (main.js:7794) ---
    const landcoverData = await fetchJson('./data/aop_landcover.geojson', 'Land cover missing');
    if (landcoverData) {
      map.addSource('aop-landcover', {
        type: 'geojson', data: landcoverData,
        attribution: 'Land cover: classified from USDA NAIP 2023 + USGS 3DEP lidar'
      });
      map.addLayer({
        id: 'landcover-forest', type: 'fill', source: 'aop-landcover',
        paint: { 'fill-color': LANDCOVER_MUTED_FILL, 'fill-opacity': 0.9 }
      });
      map.addLayer({
        id: 'landcover-forest-outline', type: 'line', source: 'aop-landcover',
        paint: { 'line-color': LANDCOVER_MUTED_OUTLINE, 'line-width': 0.8, 'line-opacity': 0.55 }
      });
    }

    // --- AWS Terrain DEM + lidar hillshade (main.js:7815) ---
    // The DEM source backs both the 2D hillshade (Topo/Trace) and the 3D button.
    map.addSource('aws-terrain-dem', {
      type: 'raster-dem',
      tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
      tileSize: 256, encoding: 'terrarium', minzoom: 0, maxzoom: 15,
      attribution: 'Terrain: AWS Terrain Tiles (USGS 3DEP, SRTM, GMTED, ETOPO1)'
    });
    map.addLayer({
      id: 'lidar-hillshade', type: 'hillshade', source: 'aws-terrain-dem',
      layout: { visibility: 'none' },
      paint: {
        'hillshade-exaggeration': 0.6,
        'hillshade-shadow-color': '#3a2f22',
        'hillshade-highlight-color': '#fbf4e2',
        'hillshade-accent-color': '#6b5640'
      }
    });

    // --- TNMap aerial (Satellite preset) (main.js:7840) ---
    map.addSource('tnmap-imagery', {
      type: 'raster',
      tiles: ['https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer/tile/{z}/{y}/{x}'],
      tileSize: 256, minzoom: 11, maxzoom: 22,
      bounds: [-85.782935283, 35.067164188, -85.717154097, 35.117928496],
      attribution: 'Imagery: TDOT Aerial Surveys / TNMap'
    });
    map.addLayer({
      id: 'tnmap-satellite', type: 'raster', source: 'tnmap-imagery',
      layout: { visibility: 'none' }, paint: { 'raster-opacity': 1 }
    });

    // --- Lidar contours (Topo preset) (main.js:7952) ---
    const contourData = await fetchJson('./data/aop_contours.geojson', 'Contour layer missing');
    if (contourData) {
      map.addSource('aop-contours', {
        type: 'geojson', data: contourData,
        attribution: 'Contours: USGS 3DEP 1m DEM (lidar-derived)'
      });
      map.addLayer({
        id: 'contours-minor', type: 'line', source: 'aop-contours',
        filter: ['==', ['get', 'idx'], 0],
        layout: { visibility: 'none', 'line-join': 'round' },
        paint: {
          'line-color': '#c7b48f',
          'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.5, 16, 1.4],
          'line-opacity': ['interpolate', ['linear'], ['zoom'], 16.5, 0, 17.5, 0.75]
        }
      });
      map.addLayer({
        id: 'contours-index', type: 'line', source: 'aop-contours',
        filter: ['==', ['get', 'idx'], 1],
        layout: { visibility: 'none', 'line-join': 'round' },
        paint: {
          'line-color': '#a8906a',
          'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1, 16, 2.8],
          'line-opacity': ['interpolate', ['linear'], ['zoom'],
            15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 0.95, 0],
            16, 0.95]
        }
      });
      map.addLayer({
        id: 'contours-labels', type: 'symbol', source: 'aop-contours',
        filter: ['==', ['get', 'idx'], 1],
        layout: {
          visibility: 'none', 'symbol-placement': 'line',
          'text-field': ['concat', ['to-string', ['get', 'elev_ft']], ' ft'],
          'text-size': 11, 'symbol-spacing': 320
        },
        paint: {
          'text-color': '#7d6a4a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8,
          'text-opacity': ['interpolate', ['linear'], ['zoom'],
            15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 1, 0],
            16, 1]
        }
      });
    }

    // --- USGS NHD hydrography: streams, waterbodies, springs (main.js:8342) ---
    const waterData = await fetchJson('./data/aop_water.geojson', 'Water layer missing');
    if (waterData) {
      map.addSource('usgs-water', {
        type: 'geojson', data: waterData,
        attribution: 'Hydrography: USGS National Hydrography Dataset'
      });
      map.addLayer({
        id: 'water-area-fill', type: 'fill', source: 'usgs-water',
        filter: ['==', ['get', 'water_kind'], 'water_area'],
        layout: { visibility: 'none' },
        paint: { 'fill-color': '#a8c5c9', 'fill-opacity': 0.55 }
      });
      map.addLayer({
        id: 'waterbody-fill', type: 'fill', source: 'usgs-water',
        filter: ['==', ['get', 'water_kind'], 'waterbody'],
        layout: { visibility: 'none' },
        paint: { 'fill-color': '#9fbfc4', 'fill-opacity': 0.5 }
      });
      map.addLayer({
        id: 'waterbody-outline', type: 'line', source: 'usgs-water',
        filter: ['==', ['get', 'water_kind'], 'waterbody'],
        layout: { visibility: 'none' },
        paint: { 'line-color': '#6f9098', 'line-width': 1.2 }
      });
      map.addLayer({
        id: 'streams', type: 'line', source: 'usgs-water',
        filter: ['==', ['get', 'water_kind'], 'flowline'],
        layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
        paint: {
          'line-color': '#7fa3ac', 'line-opacity': 0.9,
          'line-width': [
            'interpolate', ['linear'], ['zoom'],
            10, ['case', ['==', ['get', 'water_class'], 'stream'], 0.9, 0.5],
            14, ['case', ['==', ['get', 'water_class'], 'stream'], 2.4, 1.3],
            17, ['case', ['==', ['get', 'water_class'], 'stream'], 5.5, 2.8]
          ]
        }
      });
      map.addLayer({
        id: 'stream-labels', type: 'symbol', source: 'usgs-water',
        filter: ['all', ['==', ['get', 'water_kind'], 'flowline'], ['!=', ['get', 'name'], null]],
        layout: {
          visibility: 'none', 'symbol-placement': 'line',
          'text-field': ['get', 'name'],
          'text-size': ['interpolate', ['linear'], ['zoom'], 12, 9, 16, 13],
          'text-letter-spacing': 0.04
        },
        paint: { 'text-color': '#4a6c73', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
      });
      map.addLayer({
        id: 'water-points', type: 'circle', source: 'usgs-water',
        filter: ['==', ['get', 'water_kind'], 'point'],
        layout: { visibility: 'none' },
        paint: {
          'circle-radius': 5,
          'circle-color': ['match', ['get', 'water_class'], 'spring', '#6f9aa6', 'gage', '#bb8a4a', '#7fa3ac'],
          'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 1.5
        }
      });
      map.addLayer({
        id: 'water-point-labels', type: 'symbol', source: 'usgs-water',
        filter: ['all', ['==', ['get', 'water_kind'], 'point'], ['!=', ['get', 'name'], null]],
        layout: {
          visibility: 'none', 'text-field': ['get', 'name'],
          'text-size': 11, 'text-offset': [0, 1.1], 'text-anchor': 'top'
        },
        paint: { 'text-color': '#4a6c73', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.5 }
      });
      indexFeatures(waterData,
        (props) => props.water_kind === 'point' ? (props.water_class || 'water point')
          : props.water_kind === 'waterbody' ? 'waterbody' : 'stream',
        (props) => props.water_kind === 'point' ? PRESET_LAYERS.showSprings : PRESET_LAYERS.showWater);
    }

    // --- USGS National Map asphalt roads (main.js:8467) ---
    const roadsData = await fetchJson('./data/aop_roads.geojson', 'Roads layer missing');
    if (roadsData) {
      map.addSource('usgs-roads', { type: 'geojson', data: roadsData });
      const lineWidth = (light, mid, heavy) => ['interpolate', ['linear'], ['zoom'], 10, light, 14, mid, 17, heavy];
      const lineLayout = { visibility: 'visible', 'line-cap': 'round', 'line-join': 'round' };
      map.addLayer({ id: 'roads-local-casing', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'local'], layout: lineLayout, paint: { 'line-color': '#f3ecda', 'line-width': lineWidth(0.8, 2.2, 6), 'line-opacity': 0.9 } });
      map.addLayer({ id: 'roads-local', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'local'], layout: lineLayout, paint: { 'line-color': '#b0a68c', 'line-width': lineWidth(0.4, 1.2, 3.2) } });
      map.addLayer({ id: 'roads-connecting-casing', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'local_connecting'], layout: lineLayout, paint: { 'line-color': '#f3ecda', 'line-width': lineWidth(1.2, 3, 8), 'line-opacity': 0.95 } });
      map.addLayer({ id: 'roads-connecting', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'local_connecting'], layout: lineLayout, paint: { 'line-color': '#cdb079', 'line-width': lineWidth(0.7, 1.8, 4.5) } });
      map.addLayer({ id: 'roads-secondary-casing', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'secondary'], layout: lineLayout, paint: { 'line-color': '#f3ecda', 'line-width': lineWidth(1.6, 4, 9.5), 'line-opacity': 0.95 } });
      map.addLayer({ id: 'roads-secondary', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'secondary'], layout: lineLayout, paint: { 'line-color': '#c09060', 'line-width': lineWidth(0.9, 2.4, 5.5) } });
      map.addLayer({ id: 'roads-ramp-casing', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'ramp'], layout: lineLayout, paint: { 'line-color': '#bf8f55', 'line-width': lineWidth(1.5, 3.5, 8) } });
      map.addLayer({ id: 'roads-ramp', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'ramp'], layout: lineLayout, paint: { 'line-color': '#d8b173', 'line-width': lineWidth(0.8, 2.0, 4.8) } });
      map.addLayer({ id: 'roads-controlled-casing', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'controlled_access'], layout: lineLayout, paint: { 'line-color': '#9a7a52', 'line-width': lineWidth(2, 5, 11) } });
      map.addLayer({ id: 'roads-controlled', type: 'line', source: 'usgs-roads', filter: ['==', ['get', 'road_class'], 'controlled_access'], layout: lineLayout, paint: { 'line-color': '#d8b173', 'line-width': lineWidth(1.2, 3, 7) } });
      map.addLayer({
        id: 'roads-labels', type: 'symbol', source: 'usgs-roads',
        filter: ['!=', ['get', 'name'], null],
        layout: {
          visibility: 'visible', 'symbol-placement': 'line',
          'text-field': ['get', 'name'],
          'text-size': ['interpolate', ['linear'], ['zoom'], 12, 9, 16, 13],
          'text-letter-spacing': 0.04
        },
        paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
      });
      indexFeatures(roadsData, 'road', () => PRESET_LAYERS.showRoads);
    }

    // --- Visitor context callouts + brand logos (one file, split by kind) ---
    // main.js:8599 / 9698 both read aop_visitor_context_callouts.geojson; fetchJson
    // memoizes so this is one request split two ways. The drag-to-move override
    // replay (applyPositionedFeatures) is editor machinery — not carried; the read
    // core draws the served (baked) geometry.
    const calloutsBundle = await fetchJson('./data/aop_visitor_context_callouts.geojson', 'Visitor context callouts missing');
    const visitorContextData = calloutsBundle
      ? Object.assign({}, calloutsBundle, { features: calloutsBundle.features.filter((f) => (f.properties || {}).kind !== 'brand_logo') })
      : null;
    if (visitorContextData) {
      map.addSource('visitor-context', {
        type: 'geojson', data: visitorContextData,
        attribution: 'Visitor context: AOP, RiderPlanet, Marion County Tourism'
      });
      map.addLayer({
        id: 'visitor-context-fill', type: 'fill', source: 'visitor-context',
        paint: { 'fill-color': '#d8b173', 'fill-opacity': 0.18 }
      });
      map.addLayer({
        id: 'visitor-context-outline', type: 'line', source: 'visitor-context',
        layout: { 'line-join': 'round' },
        paint: {
          'line-color': '#8b5f38',
          'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.6, 16, 3.2],
          'line-opacity': 0.9, 'line-dasharray': [3, 1.4]
        }
      });
      map.addLayer({
        id: 'visitor-context-labels', type: 'symbol', source: 'visitor-context',
        layout: {
          'text-field': ['get', 'label'],
          'text-size': ['interpolate', ['linear'], ['zoom'], 11, 10, 15, 12],
          'text-line-height': 1.08, 'text-anchor': 'center', 'text-offset': [0, 0],
          'text-max-width': 18, 'text-padding': 4
        },
        paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
      });
      indexFeatures(visitorContextData, 'visitor context', () => PRESET_LAYERS.showVisitorContext);
    }

    // --- FEMA building footprints (main.js:8808) ---
    const buildingsData = await fetchJson('./data/aop_buildings.geojson', 'Building footprints missing');
    if (buildingsData) {
      map.addSource('fema-buildings', {
        type: 'geojson', data: buildingsData,
        attribution: 'Buildings: FEMA USA Structures / ORNL'
      });
      map.addLayer({
        id: 'building-footprint-fill', type: 'fill', source: 'fema-buildings',
        filter: ['!=', ['get', 'aop_structure_box'], true],
        layout: { visibility: 'none' },
        paint: {
          'fill-color': ['match', ['get', 'occupancy_class'],
            'Residential', '#c1a386', 'Agriculture', '#b7a36f', 'Assembly', '#b78f6f',
            'Government', '#9da4a6', 'Unclassified', '#aaa397', '#ad987f'],
          'fill-opacity': ['case', ['==', ['get', 'inside_aop_boundary'], true], 0.56, 0.34]
        }
      });
      map.addLayer({
        id: 'building-footprint-outline', type: 'line', source: 'fema-buildings',
        filter: ['!=', ['get', 'aop_structure_box'], true],
        layout: { visibility: 'none' },
        paint: {
          'line-color': ['case', ['==', ['get', 'inside_aop_boundary'], true], '#8e5f37', '#776f61'],
          'line-width': ['interpolate', ['linear'], ['zoom'], 11, 0.5, 16, 1.8], 'line-opacity': 0.9
        }
      });
      map.addLayer({
        id: 'building-footprint-aop-outline', type: 'line', source: 'fema-buildings',
        filter: ['==', ['get', 'aop_facility'], true],
        layout: { visibility: 'none' },
        paint: {
          'line-color': '#7c4a2a',
          'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.1, 16, 3.1], 'line-opacity': 0.95
        }
      });
      // Private structures on AOP land: an always-on non-interactive presence
      // box (no toggle, no preset) so nobody reads the spot as empty (main.js:8868).
      map.addLayer({
        id: 'building-structure-box', type: 'fill', source: 'fema-buildings',
        filter: ['==', ['get', 'aop_structure_box'], true],
        paint: { 'fill-color': '#46423b', 'fill-opacity': 0.82, 'fill-outline-color': '#2e2a25' }
      });
      // Only the public park FACILITIES are searchable (region footprints +
      // private black boxes stay out); address + role ride as aliases.
      const facilityFeatures = buildingsData.features
        .filter((f) => f.properties && f.properties.aop_facility === true);
      indexFeatures(
        { type: 'FeatureCollection', features: facilityFeatures },
        'facility',
        () => PRESET_LAYERS.showBuildings,
        (props) => [props.address, props.facility_role]
      );
    }

    // --- AOP merged trail network (the gold trail truth) (main.js:9014) ---
    const aopTrailNetworkData = await fetchJson('./data/aop_trail_network.geojson', 'AOP trail network missing');
    if (aopTrailNetworkData) {
      map.addSource('aop-trail-network', { type: 'geojson', data: aopTrailNetworkData });
      map.addLayer({
        id: 'aop-trail-network', type: 'line', source: 'aop-trail-network',
        layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
        paint: { 'line-color': ['coalesce', ['get', 'color'], '#888888'], 'line-width': 3, 'line-opacity': 0.92 }
      });
      map.addLayer({
        id: 'aop-trail-network-labels', type: 'symbol', source: 'aop-trail-network',
        filter: ['to-boolean', ['get', 'name']],
        layout: {
          visibility: 'none', 'symbol-placement': 'line-center',
          'text-field': ['to-string', ['get', 'name']], 'text-size': 12
        },
        paint: { 'text-color': '#111', 'text-halo-color': '#fff', 'text-halo-width': 1.6 }
      });
      // Named trails searchable by name AND by number ("15", "trail 15").
      indexFeatures(
        aopTrailNetworkData,
        'trail',
        () => PRESET_LAYERS.showAopTrailNetwork,
        (props) => {
          const aliases = [];
          if (props.name != null) aliases.push('trail ' + String(props.name));
          if (props.trail_number != null) {
            aliases.push(String(props.trail_number), 'trail ' + String(props.trail_number));
          }
          return aliases.length ? aliases : null;
        }
      );
    }

    // --- Publishable layers: boundaries, trails, trailheads (main.js:9533) ---
    // Raw fetch (not memoized) so a failure surfaces in the bottom message, as on
    // the live page. publish-pois (★ baked destinations) are POI-slice territory —
    // not carried here.
    let publishData;
    try {
      const response = await fetch('./data/publish.geojson');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      publishData = await response.json();
    } catch (error) {
      console.error(error);
      if (message) message.textContent = 'Publish layer failed to load.';
      return;
    }

    map.addSource('publish-data', { type: 'geojson', data: publishData });
    map.addLayer({
      id: 'publish-boundary-fill', type: 'fill', source: 'publish-data',
      filter: ['==', ['get', 'layer'], 'park_boundaries'],
      paint: { 'fill-color': '#d8c8a2', 'fill-opacity': 0.10 }
    });
    map.addLayer({
      id: 'publish-boundaries', type: 'line', source: 'publish-data',
      filter: ['==', ['get', 'layer'], 'park_boundaries'],
      paint: { 'line-color': '#6e5a3c', 'line-width': 2.5 }
    });
    map.addLayer({
      id: 'publish-trails', type: 'line', source: 'publish-data',
      filter: ['==', ['get', 'layer'], 'trail_centerlines'],
      paint: { 'line-color': '#9a5a32', 'line-width': 3.5 }
    });
    map.addLayer({
      id: 'publish-trailheads', type: 'circle', source: 'publish-data',
      filter: ['==', ['get', 'layer'], 'trailheads'],
      paint: { 'circle-radius': 6, 'circle-color': '#6f8a5c', 'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 2 }
    });
    indexFeatures(publishData,
      (props) => props.layer === 'trail_centerlines' ? 'trail'
        : props.layer === 'park_boundaries' ? 'boundary' : 'trailhead',
      (props) => props.layer === 'trail_centerlines' ? PRESET_LAYERS.showTrails
        : props.layer === 'park_boundaries' ? PRESET_LAYERS.showBoundaries : PRESET_LAYERS.showTrailheads);

    // The Park zoom preset fits the published boundary; fall back to all publish
    // features if no boundary has been exported (main.js:9612-9619).
    const boundaryOnly = {
      features: publishData.features.filter((feature) => feature.properties?.layer === 'park_boundaries')
    };
    parkViewBounds = geojsonBounds(boundaryOnly) || geojsonBounds(publishData);

    // --- Brand logos (AOP badge + Rock Warblers), from the callouts file ---
    // Render only: load the two icons, add the point source, draw at a fixed
    // zoom-clamped size. The editor's drag/resize size-CAP store is NOT carried,
    // so the icon-size expression below inlines main.js's default cap (1).
    const brandLogosData = calloutsBundle
      ? Object.assign({}, calloutsBundle, { features: calloutsBundle.features.filter((f) => (f.properties || {}).kind === 'brand_logo') })
      : null;
    if (brandLogosData && brandLogosData.features.length) {
      const logoImages = [
        { name: 'brand-aop-badge', url: './assets/branding/aop-badge.png' },
        { name: 'brand-rock-warblers', url: './assets/branding/rock-warblers.jpg' }
      ];
      await Promise.all(logoImages.map(({ name, url }) => new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => {
          if (!map.hasImage(name)) {
            try { map.addImage(name, img, { pixelRatio: 2 }); }
            catch (err) { console.warn(`Could not register logo image ${name}:`, err); }
          }
          resolve();
        };
        img.onerror = () => { console.warn(`Brand logo image failed to load: ${url}`); resolve(); };
        img.src = url;
      })));
      map.addSource('brand-logos', {
        type: 'geojson', data: brandLogosData,
        attribution: 'Brand logos: AOP, Rock Warblers'
      });
      map.addLayer({
        id: 'brand-logos-icons', type: 'symbol', source: 'brand-logos',
        layout: {
          'icon-image': ['get', 'icon_image'],
          // per-feature icon_size × cap(1) × zoom factor (caps at park zoom 15,
          // halves per level below): main.js brandLogoIconSizeExpr with cap=1.
          'icon-size': ['interpolate', ['exponential', 2], ['zoom'],
            10, ['*', ['coalesce', ['get', 'icon_size'], 0.06], 0.03125],
            15, ['*', ['coalesce', ['get', 'icon_size'], 0.06], 1]],
          'icon-allow-overlap': true, 'icon-ignore-placement': true, 'icon-anchor': 'center'
        }
      });
      indexFeatures(brandLogosData, 'logo', () => PRESET_LAYERS.showBrandLogos);
    }

    // --- Search highlight overlay (main.js:9942) ---
    // Added LAST so the pulse draws above every other layer. buildSearchGroups
    // collapses the per-add-site index into ranked, segment-merged results.
    map.addSource('search-highlight', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
    map.addLayer({
      id: 'search-highlight-line', type: 'line', source: 'search-highlight',
      layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-color': '#e8a83a', 'line-width': 8, 'line-opacity': 0.85, 'line-blur': 1.5 }
    });
    map.addLayer({
      id: 'search-highlight-point', type: 'circle', source: 'search-highlight',
      filter: ['==', ['geometry-type'], 'Point'],
      layout: { visibility: 'none' },
      paint: {
        'circle-radius': 16, 'circle-color': '#e8a83a', 'circle-opacity': 0,
        'circle-stroke-color': '#e8a83a', 'circle-stroke-width': 4, 'circle-stroke-opacity': 0.85
      }
    });
    buildSearchGroups();

    // Initial framing + the first preset (main.js:9595 + 9970-9971).
    fitToDataBounds(publishData);
    if (message) message.textContent = `${publishData.features.length} publish feature${publishData.features.length === 1 ? '' : 's'} loaded.`;
    applyPreset(activePresetId);
  });

  // ── Control wiring (main.js:10364-10370, 10407) ────────────────────────
  for (const button of presetButtons) {
    button.addEventListener('click', () => applyPreset(button.dataset.preset));
  }
  for (const button of document.querySelectorAll('.zoom-bar button[data-view]')) {
    button.addEventListener('click', () => goToView(button.dataset.view));
  }
  terrainButton.addEventListener('click', () => setTerrainEnabled(!terrainToggle.checked));
  terrainToggle.addEventListener('change', () => setTerrainEnabled(terrainToggle.checked));

  // Search input + dropdown (main.js:10327-10362). Session-persistence calls
  // dropped (no viewer session state in the clean core yet).
  searchInput.addEventListener('input', () => { searchActive = -1; renderSearchResults(); });
  searchInput.addEventListener('focus', renderSearchResults);
  searchInput.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      searchActive = Math.min(searchActive + 1, searchMatches.length - 1);
      renderSearchResults();
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      searchActive = Math.max(searchActive - 1, 0);
      renderSearchResults();
    } else if (event.key === 'Enter') {
      event.preventDefault();
      gotoMatch(searchActive >= 0 ? searchActive : 0);
    } else if (event.key === 'Escape') {
      searchInput.value = '';
      clearSearchResults();
      searchInput.blur();
    }
  });
  // mousedown (not click) so it fires before the input blur closes the list.
  searchResults.addEventListener('mousedown', (event) => {
    const item = event.target.closest('.search-item');
    if (item) {
      event.preventDefault();
      gotoMatch(Number(item.dataset.i));
    }
  });
  document.addEventListener('click', (event) => {
    if (!event.target.closest('.search')) clearSearchResults();
  });
  // Keep the position:fixed dropdown anchored to the input across scroll/resize.
  // (main.js's broader resyncViewport / map.resize is PWA viewport health — a
  // later slice; search needs only the reposition.)
  window.addEventListener('scroll', () => { if (searchResults.style.display === 'block') positionSearchResults(); }, true);
  window.addEventListener('resize', () => { if (searchResults.style.display === 'block') positionSearchResults(); });
})();
