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
  // The 9-patch data-acquisition AOI is the region the decorative band frames.
  const REGION_BOUNDS = [[-85.782935283, 35.067164188], [-85.717154097, 35.117928496]];
  // Camera leash (maxBounds): the 9-patch padded outward so you can pull PAST the
  // off-edge band. The band (viewer_band.js) draws its neat-line + lettering to
  // REGION_BOUNDS and its art (lettering + corner marks) reaches ~0.12 of the region
  // beyond it. At 0.13 the wall landed right on the border text/images — you couldn't
  // pull past them. 0.22 leaves a strip of paper margin past the lettering so the
  // over-pull peek clears the border, while still stopping before the camera wanders
  // far into blank paper. (Was REGION_BOUNDS exactly pre-band, then 0.13.)
  const BAND_PAD = 0.22;
  const REGION_MAXBOUNDS = (function (b, f) {
    const w = b[0][0], s = b[0][1], e = b[1][0], n = b[1][1];
    const dx = (e - w) * f, dy = (n - s) * f;
    return [[w - dx, s - dy], [e + dx, n + dy]];
  })(REGION_BOUNDS, BAND_PAD);
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
    maxBounds: REGION_MAXBOUNDS,
    attributionControl: false
  });

  // Catch style/glyph/source errors from construction onward (main.js:151).
  map.on('error', (e) => { console.error(e.error || e); });

  // ── Band seam ──────────────────────────────────────────────────────────
  // Expose the live map + the (tight) region the decorative band frames, so
  // js/viewer_band.js can attach its geolocated neat-line layers on top. The
  // band draws to regionBounds; the camera leash is the padded REGION_MAXBOUNDS
  // above. This is the only thing the core leaks to window, on purpose — it
  // replaces the constructor shim the viewer_banded.html proof page used to fake.
  window.AOPViewer = { map, regionBounds: REGION_BOUNDS };

  // Two-finger pinch zooms immediately; keep drag-to-tilt + right-click rotate
  // for the 3D view (main.js:163).
  map.touchZoomRotate.disableRotation();

  // Bottom-left ⓘ attribution (main.js:166). Two faces of the same version:
  //  - COLLAPSED: a small "v64" label sits beside the ⓘ (#appVersion, folded in
  //    below). CSS hides it when the ⓘ is expanded.
  //  - EXPANDED: the build credit "Made by Rock Warblers · v64" rides in the
  //    attribution body via customAttribution.
  // #appVersion (index.html) is the version-of-record, synced with VERSION in sw.js.
  const versionEl = document.getElementById('appVersion');
  const version = versionEl ? versionEl.textContent.trim() : '';
  const madeBy = 'Made by Rock Warblers' + (version ? ' · ' + version : '');
  map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: madeBy }), 'bottom-left');

  // Collapse the compact attribution to the ⓘ on the FIRST source load, then unbind
  // so later ⓘ taps are the user's (main.js:206-214). Collapse early on purpose: the
  // expanded control aggregates every source's attribution as sources load, so
  // lingering only lets the layer disclaimers pile onto the "Made by Rock Warblers"
  // credit and bury it. Quick collapse keeps the credit clean; the full disclaimers
  // live behind the ⓘ tap (state 3).
  const collapseAttribOnce = () => {
    const el = document.querySelector('.maplibregl-ctrl-attrib.maplibregl-compact');
    if (!el) return;
    el.classList.remove('maplibregl-compact-show');
    el.removeAttribute('open');
    map.off('sourcedata', collapseAttribOnce);
  };
  map.on('sourcedata', collapseAttribOnce);

  // Fold the version label in beside the ⓘ (a sibling AFTER the attrib element,
  // so the CSS `.maplibregl-compact-show ~ .attrib-version` can hide it on expand).
  (function foldVersionBesideInfo() {
    const bottomLeft = map.getContainer().querySelector('.maplibregl-ctrl-bottom-left');
    if (bottomLeft && versionEl) {
      bottomLeft.classList.add('attrib-with-version');
      versionEl.classList.add('attrib-version');
      versionEl.hidden = false;
      bottomLeft.appendChild(versionEl);
    }
  })();

  // ── Tester surface (brain/pages.md "week before tester") ───────────────
  // A field-test view reached by a LINK, not a separate HTML file
  // (ai_rules/editor_is_the_viewer): /index.html?tester=1 turns it on. The date
  // offset is the existing ?clock= fixture above; this adds the lat/long offset,
  // so the full test link is /index.html?tester=1&clock=YYYY-MM-DDTHH:MM .
  function testerParamOn() {
    try {
      const v = new URLSearchParams(window.location.search).get('tester');
      return v !== null && v !== '0';
    } catch (_) { return false; }
  }
  const TESTER = testerParamOn();

  // Lat/long offset (GPS spoof). The tester walks their real neighborhood and the
  // blue dot walks the PARK: the FIRST real fix is pinned to the park anchor, and
  // every later fix keeps its real delta from that first fix. Done by wrapping
  // navigator.geolocation BEFORE the GeolocateControl reads it, so the whole locate
  // machinery below (blue dot, accuracy halo, follow mode, the lit FAB) is reused
  // untouched — it just receives shifted coordinates. Additive degree offset; the
  // small longitude-scale distortion between the tester's latitude and the park's
  // is immaterial for a walk-around field test.
  const TESTER_ANCHOR = [-85.748268, 35.090703]; // park pavilion (= PAVILION_VIEW.center)
  if (TESTER && navigator.geolocation) {
    const geo = navigator.geolocation;
    const realGet = geo.getCurrentPosition.bind(geo);
    const realWatch = geo.watchPosition.bind(geo);
    let offset = null; // [dLng, dLat], locked on the first real fix
    const shift = (pos) => {
      const c = pos.coords;
      if (!offset) offset = [TESTER_ANCHOR[0] - c.longitude, TESTER_ANCHOR[1] - c.latitude];
      return {
        timestamp: pos.timestamp,
        coords: {
          latitude: c.latitude + offset[1],
          longitude: c.longitude + offset[0],
          accuracy: c.accuracy,
          altitude: c.altitude,
          altitudeAccuracy: c.altitudeAccuracy,
          heading: c.heading,
          speed: c.speed
        }
      };
    };
    geo.getCurrentPosition = (success, error, options) =>
      realGet((pos) => success(shift(pos)), error, options);
    geo.watchPosition = (success, error, options) =>
      realWatch((pos) => success(shift(pos)), error, options);
    console.info('[tester] lat/long offset on — Locate pins your first fix to the park pavilion; real movement is preserved.');
  }

  // Visible "TESTER" chip so a field tester on a phone can tell the test surface
  // (shifted GPS/clock) from the live day-of viewer. The `.tester` html class is
  // also where the future edit affordances hang (see index.html Locate-FAB note).
  if (TESTER) {
    document.documentElement.classList.add('tester');
    const badge = document.createElement('div');
    badge.className = 'tester-badge';
    badge.textContent = 'TESTER';
    badge.title = 'Test surface — GPS and/or clock may be shifted';
    document.body.appendChild(badge);
  }

  // Field "where am I" — blue dot + accuracy halo + follow mode, from the device
  // GPS (works offline at the park). The default top-right button is hidden by
  // CSS; the left-rail Locate button drives it (main.js:186-228).
  const geolocate = new maplibregl.GeolocateControl({
    positionOptions: { enableHighAccuracy: true },
    trackUserLocation: true,
    showUserLocation: true,
    showAccuracyCircle: true
  });
  map.addControl(geolocate, 'top-right');
  const locateBtn = document.getElementById('locateBtn');
  if (locateBtn) {
    locateBtn.addEventListener('click', () => geolocate.trigger());
    const lit = () => { locateBtn.classList.add('active'); locateBtn.setAttribute('aria-pressed', 'true'); };
    const dim = () => { locateBtn.classList.remove('active'); locateBtn.setAttribute('aria-pressed', 'false'); };
    geolocate.on('trackuserlocationstart', lit);
    geolocate.on('trackuserlocationend', dim);
    geolocate.on('error', dim);
  }

  // ── Control DOM (the pill-bar shell in viewer.html) ────────────────────
  const message = document.getElementById('message');
  const terrainToggle = document.getElementById('showTerrain'); // hidden checkbox: 3D state
  const terrainButton = document.getElementById('terrainButton');
  const presetButtons = [...document.querySelectorAll('.preset-bar button[data-preset]')];
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');
  const calendarCard = document.getElementById('calendarCard');
  const calendarRange = document.getElementById('calendarRange');
  const calendarBody = document.getElementById('calendarBody');
  const calendarDays = document.getElementById('calendarDays');
  const calendarCountdown = document.getElementById('calendarCountdown');
  const calendarCountdownValue = document.getElementById('calendarCountdownValue');
  const leftTabButtons = [...document.querySelectorAll('.left-tab[data-left-tab]')];
  const leftTabPanels = [...document.querySelectorAll('.left-tab-panel')];

  let activePresetId = 'park';
  let parkViewBounds = null;

  // Named-feature search registry, filled by indexFeatures during map load.
  const searchIndex = [];
  let searchGroups = [];
  let searchMatches = [];
  let searchActive = -1;

  // Event-schedule state, populated by the event loader during map load.
  let eventScheduleConfig = null;
  let eventScheduleData = null;
  let eventLocationByTag = new Map();
  let eventSessionById = new Map();
  let activeEventSessionId = null;

  // Activity-hotspots (GPX dwell) state + the user's preferred Hot lane.
  let aopActivityHotspotsData = null;
  let preferredHotLane = null;

  // POI-directory state. The directory reads the baked ★ (properties.highlight)
  // straight off the served features — the star is a published data-model field
  // (mvp/scripts/bake_poi_stars.py), not an editor/localStorage or index side-join.
  let poiBuildingsData = null;
  let poiVisitorData = null;
  let poiPublishData = null;

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
  const ACTIVITY_HOTSPOT_FILL = ['match', ['get', 'intensity_class'],
    'low',    '#e6c86f',
    'medium', '#d9903d',
    'high',   '#bf5a36',
    'peak',   '#7f2f27',
    '#d9903d'];
  const ACTIVITY_HOTSPOT_OPACITY = [
    'interpolate', ['linear'], ['get', 'intensity_norm'],
    0, 0.12,
    0.4, 0.28,
    1, 0.58
  ];
  // The activity-hotspots layer set, toggled by the Hot Trails lane (the
  // "where the cool spots are" discovery affordance). Default OFF; surfaced on
  // demand, independent of the layer presets (like 3D).
  const ACTIVITY_HOTSPOT_LAYERS = ['activity-hotspots-heat', 'activity-hotspots-fill', 'activity-hotspots-outline', 'activity-hotspots-labels'];

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
    // Region: frame the whole 9-patch with a paper margin so the decorative band
    // (neat-line + lettering, drawn at the 9-patch boundary by viewer_band.js) seats
    // fully in view. The old framing inset ~15% per side to fill the viewport with the
    // data-rich centre — but that cropped the band off every edge. Now we OUTSET ~7%
    // per side: the band lettering sits ~4% outside the boundary, and the camera leash
    // (maxBounds) is +13%, so this reveals the whole frame while staying inside the
    // leash. The button's label — "the full 9-patch region" — now matches what it shows.
    const [[rw, rs], [re, rn]] = REGION_BOUNDS;
    const outX = (re - rw) * 0.07;
    const outY = (rn - rs) * 0.07;
    map.fitBounds(
      [[rw - outX, rs - outY], [re + outX, rn + outY]],
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

  // ── Event schedule + calendar (ported from main.js) ────────────────────
  // The drawer's Calendar/Events tab. Editor seams severed: the virtual-clock
  // Session-tools UI + stored clock are gone (only the ?clock= fixture + wall
  // clock remain); the event-schedule checkbox toggle becomes setLayerVisibility;
  // every persistViewerSessionState call is dropped. The document→GeoJSON
  // transform is the ONE shared resolver (window.AOPEventSchedule).

  // detailRows / list helpers (main.js:6205-6223).
  function detailRows(rows) {
    return rows
      .filter(([, value]) => value !== undefined && value !== null && value !== '')
      .map(([label, value]) => `${escapeHtml(label)}: ${escapeHtml(value)}`)
      .join('<br/>');
  }
  function formatListProperty(value) {
    if (Array.isArray(value)) return value.join(', ');
    if (typeof value !== 'string') return value;
    const trimmed = value.trim();
    if (!trimmed.startsWith('[')) return value;
    try {
      const parsed = JSON.parse(trimmed);
      return Array.isArray(parsed) ? parsed.join(', ') : value;
    } catch (_) { return value; }
  }

  // Clock: the ?clock=YYYY-MM-DDTHH:MM test fixture, else the wall clock. The
  // Session-tools virtual-clock UI + its localStorage are NOT carried.
  function parseLocalClockString(raw) {
    const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{1,2}):(\d{2})$/.exec(String(raw || '').trim());
    if (!m) return null;
    const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]), Number(m[4]), Number(m[5]), 0, 0);
    return isNaN(d.getTime()) ? null : d;
  }
  function clockParamDate() {
    try {
      const raw = new URLSearchParams(window.location.search).get('clock');
      return raw ? parseLocalClockString(raw) : null;
    } catch (_) { return null; }
  }
  const urlClockDate = clockParamDate();
  function eventScheduleNow() {
    return urlClockDate ? new Date(urlClockDate.getTime()) : new Date();
  }

  const CALENDAR_SESSION_DURATION_MIN = 90;
  const EVENT_DATE_LABEL_MONTHS = {
    january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
    july: 6, august: 7, september: 8, october: 9, november: 10, december: 11
  };
  function parseEventAnchorFriday() {
    const label = eventScheduleConfig?.event?.date_range_label;
    if (!label) return null;
    const m = /([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})/.exec(String(label));
    if (!m) return null;
    const month = EVENT_DATE_LABEL_MONTHS[m[1].toLowerCase()];
    if (month == null) return null;
    const day = Number(m[2]);
    const year = Number(m[3]);
    if (!Number.isFinite(day) || !Number.isFinite(year)) return null;
    return new Date(year, month, day, 0, 0, 0, 0);
  }
  function resolveCalendarAnchorSat() {
    const friday = parseEventAnchorFriday();
    if (!friday) return null;
    return new Date(friday.getFullYear(), friday.getMonth(), friday.getDate() + 1, 0, 0, 0, 0);
  }
  function composeEventDateRangeLabel(event) {
    const start = (event?.date_range_label || '').trim();
    const end = (event?.end_date_label || '').trim();
    if (!end || end === start) return start;
    return `${start} – ${end}`;
  }
  function eventScheduleStartFromAnchor(dayLabel, startLocal, anchorSat) {
    if (!anchorSat) return null;
    const day = String(dayLabel || '').trim().toLowerCase();
    const tm = /^(\d{1,2}):(\d{2})$/.exec(String(startLocal || '').trim());
    if (!tm) return null;
    const hour = Number(tm[1]);
    const minute = Number(tm[2]);
    if (!Number.isFinite(hour) || hour < 0 || hour > 23) return null;
    if (!Number.isFinite(minute) || minute < 0 || minute > 59) return null;
    let offset;
    if (day === 'friday') offset = -1;
    else if (day === 'saturday') offset = 0;
    else if (day === 'sunday') offset = 1;
    else return null;
    return new Date(anchorSat.getFullYear(), anchorSat.getMonth(), anchorSat.getDate() + offset, hour, minute, 0, 0);
  }
  function computeCalendarScheduleEdges() {
    let gatesOpen = null;
    let weekendEnd = null;
    if (calendarDays) {
      for (const li of calendarDays.querySelectorAll('li[data-session-day]')) {
        const day = (li.getAttribute('data-session-day') || '').toLowerCase();
        const tm = /^(\d{1,2}):(\d{2})$/.exec((li.getAttribute('data-session-start') || '').trim());
        if (!tm) continue;
        const minutes = Number(tm[1]) * 60 + Number(tm[2]);
        if (day === 'friday') {
          if (gatesOpen === null || minutes < gatesOpen) gatesOpen = minutes;
        } else if (day === 'sunday') {
          const end = minutes + CALENDAR_SESSION_DURATION_MIN;
          if (weekendEnd === null || end > weekendEnd) weekendEnd = end;
        }
      }
    }
    return {
      gatesOpenMin: gatesOpen != null ? gatesOpen : 17 * 60,
      weekendEndMin: weekendEnd != null ? weekendEnd : 18 * 60 + 30
    };
  }
  function computeCalendarState(now) {
    const edges = computeCalendarScheduleEdges();
    const anchorSat = resolveCalendarAnchorSat();
    if (!anchorSat) return { state: 'pre', anchorSat: null, countdownTargetMs: null };
    const gatesH = Math.floor(edges.gatesOpenMin / 60);
    const gatesM = edges.gatesOpenMin % 60;
    const endH = Math.floor(edges.weekendEndMin / 60);
    const endM = edges.weekendEndMin % 60;
    const gatesOpen = new Date(anchorSat.getFullYear(), anchorSat.getMonth(), anchorSat.getDate() - 1, gatesH, gatesM, 0, 0);
    const weekendEnd = new Date(anchorSat.getFullYear(), anchorSat.getMonth(), anchorSat.getDate() + 1, endH, endM, 0, 0);
    const nowMs = now.getTime();
    let state;
    if (nowMs < gatesOpen.getTime()) state = 'pre';
    else if (nowMs < weekendEnd.getTime()) state = 'live';
    else state = 'post';
    return {
      state, anchorSat,
      gatesOpenMs: gatesOpen.getTime(),
      weekendEndMs: weekendEnd.getTime(),
      countdownTargetMs: state === 'pre' ? gatesOpen.getTime() : null
    };
  }
  function eventScheduleFormatMinutes(minutes) {
    const m = Math.max(0, Math.round(minutes));
    if (m < 60) return `${m}m`;
    if (m < 1440) {
      const h = Math.floor(m / 60);
      const rem = m % 60;
      return rem === 0 ? `${h}h` : `${h}h ${rem}m`;
    }
    const d = Math.floor(m / 1440);
    const remH = Math.floor((m % 1440) / 60);
    return remH === 0 ? `${d}d` : `${d}d ${remH}h`;
  }
  function calendarCurrentItem() {
    return calendarDays?.querySelector('li[data-session-state="happening"]')
      || calendarDays?.querySelector('li[data-session-state="upcoming_next"]')
      || null;
  }
  function scrollCalendarCurrentRowIntoView() {
    if (!calendarBody || !calendarDays) return;
    const target = calendarCurrentItem();
    if (!target) return;
    window.requestAnimationFrame(() => {
      if (!target.isConnected) return;
      const bodyRect = calendarBody.getBoundingClientRect();
      const rowRect = target.getBoundingClientRect();
      const fullyVisible = rowRect.top >= bodyRect.top && rowRect.bottom <= bodyRect.bottom;
      if (fullyVisible) return;
      const offset = (rowRect.top - bodyRect.top) - (bodyRect.height / 2 - rowRect.height / 2);
      calendarBody.scrollTop += offset;
    });
  }
  // Stamp data-session-state + LIVE/SOON badges + the countdown. Runs after
  // render and on the 60s tick. (refreshHotButton is guarded — Hot is slice 5;
  // typeof on the undeclared name is a safe no-op until then.)
  function refreshEventScheduleSessionStates() {
    if (!calendarDays) return;
    const now = eventScheduleNow();
    const nowMs = now.getTime();
    const calendar = computeCalendarState(now);
    if (calendarCard) calendarCard.setAttribute('data-calendar-state', calendar.state);
    const rows = Array.from(calendarDays.querySelectorAll('li[data-session-day]'));
    const computed = rows.map((li) => {
      const day = li.getAttribute('data-session-day') || '';
      const start = li.getAttribute('data-session-start') || '';
      const startDate = eventScheduleStartFromAnchor(day, start, calendar.anchorSat);
      if (!startDate) return { li, state: 'future', startMs: Infinity, endMs: Infinity };
      const startMs = startDate.getTime();
      const endMs = startMs + CALENDAR_SESSION_DURATION_MIN * 60 * 1000;
      let state = 'future';
      if (nowMs >= startMs && nowMs < endMs) state = 'happening';
      else if (nowMs >= endMs) state = 'past';
      return { li, state, startMs, endMs };
    });
    if (calendar.state !== 'pre') {
      const firstFuture = computed.find((r) => r.state === 'future');
      if (firstFuture) firstFuture.state = 'upcoming_next';
    }
    for (const r of computed) {
      r.li.setAttribute('data-session-state', r.state);
      const prior = r.li.querySelector('.cal-live-badge, .cal-soon-badge');
      if (prior) prior.remove();
      if (r.state === 'happening') {
        const badge = document.createElement('span');
        badge.className = 'cal-live-badge';
        badge.setAttribute('data-badge', 'live');
        badge.textContent = 'LIVE';
        r.li.appendChild(badge);
      } else if (r.state === 'upcoming_next') {
        const untilMin = (r.startMs - nowMs) / 60000;
        const badge = document.createElement('span');
        badge.className = 'cal-soon-badge';
        badge.setAttribute('data-badge', 'soon');
        badge.textContent = eventScheduleFormatMinutes(untilMin);
        r.li.appendChild(badge);
      }
    }
    if (calendarCountdown && calendarCountdownValue) {
      if (calendar.state === 'pre' && calendar.countdownTargetMs != null) {
        const untilMin = (calendar.countdownTargetMs - nowMs) / 60000;
        calendarCountdownValue.textContent = eventScheduleFormatMinutes(untilMin).toUpperCase();
        calendarCountdown.hidden = false;
      } else {
        calendarCountdown.hidden = true;
      }
    }
    if (typeof refreshHotButton === 'function') refreshHotButton();
    scrollCalendarCurrentRowIntoView();
  }
  let eventScheduleStateTimer = null;
  function ensureEventScheduleStateTicker() {
    if (eventScheduleStateTimer != null) return;
    eventScheduleStateTimer = window.setInterval(() => { refreshEventScheduleSessionStates(); }, 60 * 1000);
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) refreshEventScheduleSessionStates();
    });
  }

  function renderEventSchedule(config, data) {
    const event = config?.event || {};
    calendarRange.textContent = composeEventDateRangeLabel(event);
    const calendarTitleEl = document.getElementById('calendarTitle');
    if (calendarTitleEl && event.label) calendarTitleEl.textContent = event.label;
    const sessions = (data?.features || [])
      .filter((feature) => feature.properties?.feature_kind === 'event_session')
      .sort((a, b) => Number(a.properties.sort_order || 0) - Number(b.properties.sort_order || 0));
    if (!sessions.length) {
      calendarDays.innerHTML = `<li class="calendar-empty">No schedule rows.</li>`;
      return;
    }
    calendarDays.innerHTML = sessions.map((feature) => {
      const props = feature.properties || {};
      const tag = props.location_tag || '';
      const location = props.location_label || tag;
      const active = props.session_id === activeEventSessionId ? ' active' : '';
      return `<li data-session-day="${escapeHtml(props.day || '')}" data-session-start="${escapeHtml(props.start_local || '')}">`
        + `<button type="button" class="calendar-row${active}" data-session-id="${escapeHtml(props.session_id)}">`
        + `<span class="calendar-day">${escapeHtml(props.day_short || props.day || '')}</span>`
        + '<span>'
        + `<span class="calendar-time">${escapeHtml(props.window || '')}</span>`
        + `<span class="calendar-name">${escapeHtml(props.title || props.name || '')}</span>`
        + `<span class="calendar-location">${escapeHtml(tag)} - ${escapeHtml(location)}</span>`
        + '</span></button></li>';
    }).join('');
    refreshEventScheduleSessionStates();
    ensureEventScheduleStateTicker();
  }

  // Popup-fit helpers: keep a session popup inside the unoccluded map slice
  // (the container minus the floating .left-controls). main.js also subtracts
  // the editor .panel — absent here, so the querySelector simply returns null.
  function firstCoordinate(geometry) {
    if (!geometry?.coordinates) return null;
    let coords = geometry.coordinates;
    while (Array.isArray(coords) && Array.isArray(coords[0])) coords = coords[0];
    return Array.isArray(coords) && typeof coords[0] === 'number' ? coords : null;
  }
  function sessionPopupHtml(props) {
    return `<strong>${escapeHtml(props.title || props.name || 'Event session')}</strong><br/>`
      + detailRows([
        ['Date', props.day],
        ['Time', props.window],
        ['Location', props.location_label],
        ['Tag', props.location_tag],
        ['Route', formatListProperty(props.route_tags)],
        ['Status', props.status],
        ['Inspired by', formatListProperty(props.inspired_by)],
        ['Caveat', props.caveat]
      ]);
  }
  function closeAllMapPopups() {
    map.getContainer().querySelectorAll('.maplibregl-popup-close-button').forEach((btn) => btn.click());
  }
  function visibleMapRect() {
    const container = map.getContainer().getBoundingClientRect();
    const width = container.right - container.left;
    let top = container.top;
    let bottom = container.bottom;
    let left = container.left;
    let right = container.right;
    const leftEl = document.querySelector('.left-controls');
    const rightEl = document.querySelector('.panel');
    const bottomEl = document.querySelector('.message');
    const fullWidth = (r) => (r.right - r.left) >= width * 0.7;
    if (leftEl) {
      const r = leftEl.getBoundingClientRect();
      if (fullWidth(r)) top = Math.max(top, r.bottom);
      else left = Math.max(left, r.right);
    }
    if (rightEl) {
      const r = rightEl.getBoundingClientRect();
      if (fullWidth(r)) bottom = Math.min(bottom, r.top);
      else right = Math.min(right, r.left);
    }
    if (bottomEl) {
      const r = bottomEl.getBoundingClientRect();
      if (r.height > 0) bottom = Math.min(bottom, r.top);
    }
    return { top, bottom, left, right };
  }
  function visibleMapPadding(extra = 20) {
    const container = map.getContainer().getBoundingClientRect();
    const vis = visibleMapRect();
    return {
      top: Math.max(0, vis.top - container.top) + extra,
      bottom: Math.max(0, container.bottom - vis.bottom) + extra,
      left: Math.max(0, vis.left - container.left) + extra,
      right: Math.max(0, container.right - vis.right) + extra
    };
  }
  function visibleCenterOffset(pad) {
    return [(pad.left - pad.right) / 2, (pad.top - pad.bottom) / 2];
  }
  function panPopupIntoView(popup, margin = 14) {
    if (!popup || typeof popup.getElement !== 'function') return;
    const el = popup.getElement();
    if (!el) return;
    requestAnimationFrame(() => {
      const popupRect = el.getBoundingClientRect();
      if (!popupRect.width || !popupRect.height) return;
      const vis = visibleMapRect();
      let dx = 0;
      let dy = 0;
      if (popupRect.right > vis.right - margin) dx = popupRect.right - (vis.right - margin);
      else if (popupRect.left < vis.left + margin) dx = popupRect.left - (vis.left + margin);
      if (popupRect.bottom > vis.bottom - margin) dy = popupRect.bottom - (vis.bottom - margin);
      else if (popupRect.top < vis.top + margin) dy = popupRect.top - (vis.top + margin);
      if (dx === 0 && dy === 0) return;
      map.panBy([dx, dy], { duration: 240 });
    });
  }

  const EVENT_LAYER_IDS = ['event-session-routes', 'event-route-labels', 'event-anchor-points', 'event-anchor-labels'];
  function gotoEventSession(sessionId) {
    const feature = eventSessionById.get(sessionId);
    if (!feature) return;
    closeAllMapPopups();
    activeEventSessionId = sessionId;
    if (eventScheduleConfig && eventScheduleData) renderEventSchedule(eventScheduleConfig, eventScheduleData);
    // Selection-driven: the event layers are default-off; showing a session
    // turns them on (replaces main.js's eventScheduleToggle.checked = true).
    for (const id of EVENT_LAYER_IDS) setLayerVisibility(id, true);
    const pad = visibleMapPadding(20);
    const bounds = geojsonBounds({ type: 'FeatureCollection', features: [feature] });
    if (bounds) {
      const [[minLng, minLat], [maxLng, maxLat]] = bounds;
      if (minLng === maxLng && minLat === maxLat) {
        map.flyTo({ center: [minLng, minLat], zoom: 17, offset: visibleCenterOffset(pad), duration: 1000, bearing: map.getBearing(), pitch: map.getPitch() });
      } else {
        map.fitBounds(bounds, { padding: pad, maxZoom: 16.8, duration: 1000, bearing: map.getBearing(), pitch: map.getPitch() });
      }
    }
    const highlight = map.getSource('search-highlight');
    if (highlight && feature.geometry) {
      highlight.setData({ type: 'FeatureCollection', features: [feature] });
      pulseHighlight();
    }
    const popupCoord = eventLocationByTag.get(feature.properties.location_tag)?.coordinates
      || firstCoordinate(feature.geometry);
    if (popupCoord) {
      const slice = visibleMapRect();
      const sliceWidth = Math.max(0, slice.right - slice.left);
      const popupMax = Math.max(200, Math.min(280, sliceWidth - 28));
      const popup = new maplibregl.Popup({ maxWidth: `${popupMax}px`, anchor: 'bottom', offset: 14, focusAfterOpen: false })
        .setLngLat(popupCoord)
        .setHTML(sessionPopupHtml(feature.properties))
        .addTo(map);
      popup.on('close', () => {
        if (activeEventSessionId !== sessionId) return;
        activeEventSessionId = null;
        if (eventScheduleConfig && eventScheduleData) renderEventSchedule(eventScheduleConfig, eventScheduleData);
      });
      map.once('moveend', () => panPopupIntoView(popup));
    }
  }

  // Events / About tab switch (main.js:446; POI tab is slice 4, dropped here).
  function setLeftTab(tabKey) {
    if (!leftTabButtons.some((button) => button.dataset.leftTab === tabKey)) tabKey = 'events';
    for (const button of leftTabButtons) {
      const selected = button.dataset.leftTab === tabKey;
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
    }
    for (const panel of leftTabPanels) {
      panel.hidden = panel.id !== `${tabKey}TabPanel`;
    }
    if (tabKey === 'events') scrollCalendarCurrentRowIntoView();
    if (tabKey === 'poi') renderPoiTab();
    return tabKey;
  }

  // About panel render (ported from the index.html copy-data bootstrap). Only
  // http(s) links are assigned so a hand-edited JSON link can't run script.
  function renderAbout(about, panel) {
    panel.textContent = '';
    if (about.heading) {
      const h = document.createElement('h2');
      h.textContent = about.heading;
      panel.append(h);
    }
    if (about.intro) {
      const p = document.createElement('p');
      p.className = 'info-copy';
      if (about.intro.lead) p.append(document.createTextNode(about.intro.lead));
      if (about.intro.link && about.intro.link.url) {
        const a = document.createElement('a');
        if (/^https?:\/\//i.test(String(about.intro.link.url))) a.href = about.intro.link.url;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = about.intro.link.text || about.intro.link.url;
        p.append(a);
      }
      if (about.intro.tail) p.append(document.createTextNode(about.intro.tail));
      panel.append(p);
    }
    if (Array.isArray(about.items) && about.items.length) {
      const ul = document.createElement('ul');
      ul.className = 'info-list';
      about.items.forEach((item) => {
        const li = document.createElement('li');
        const label = document.createElement('span');
        label.className = 'info-label';
        label.textContent = item.label || '';
        const body = document.createElement('span');
        body.textContent = item.text || '';
        li.append(label, body);
        ul.append(li);
      });
      panel.append(ul);
    }
    if (about.note) {
      const note = document.createElement('p');
      note.className = 'info-note';
      note.textContent = about.note;
      panel.append(note);
    }
  }

  // ── Hot now — two lanes (ported from main.js:6781-7057) ────────────────
  // The drawer's third tab. EVENT lane: "Live event" / "Starting soon" /
  // "Next event", driven by the schedule clock; click flies to the session.
  // TRAILS lane: toggles the activity-hotspots layer (the "where the cool spots
  // are" discovery) and flies to the densest dwell cluster. The activity-hotspots
  // checkbox indirection is severed — the lane drives the layers directly via
  // setLayerVisibility.
  const HOT_BUTTON_IMMINENT_MIN = 30;
  const HOT_BUTTON_SESSION_LEN_MIN = 90;
  const HOT_CLUSTER_RADIUS_M = 260;
  // Seed at the strongest hotspot polygon, grow a contiguous cluster by centroid
  // distance, and return its bbox (not a top-K bbox that could span the park).
  function hotspotPolygonCentroid(feature) {
    const geom = feature.geometry;
    if (!geom) return null;
    const ring = geom.type === 'MultiPolygon' ? geom.coordinates?.[0]?.[0] : geom.coordinates?.[0];
    if (!Array.isArray(ring) || !ring.length) return null;
    let sx = 0, sy = 0, n = 0;
    for (const c of ring) {
      if (!Array.isArray(c) || c.length < 2) continue;
      sx += c[0]; sy += c[1]; n += 1;
    }
    return n ? [sx / n, sy / n] : null;
  }
  function hotspotMetersBetween(a, b) {
    const latRad = (a[1] + b[1]) * 0.5 * Math.PI / 180;
    const dx = (a[0] - b[0]) * 111320 * Math.cos(latRad);
    const dy = (a[1] - b[1]) * 110540;
    return Math.hypot(dx, dy);
  }
  function findDensestHotspotCluster(radiusM = HOT_CLUSTER_RADIUS_M) {
    const data = aopActivityHotspotsData;
    if (!data?.features?.length) return null;
    const ranked = data.features
      .filter((f) => f.geometry?.type === 'Polygon' && f.properties)
      .map((f) => ({
        f,
        score: Number(f.properties.intensity_norm ?? f.properties.dwell_minutes ?? 0),
        centroid: hotspotPolygonCentroid(f)
      }))
      .filter((r) => Number.isFinite(r.score) && r.centroid)
      .sort((a, b) => b.score - a.score);
    if (!ranked.length) return geojsonBounds(data);
    const seed = ranked[0];
    const cluster = ranked.filter((r) => hotspotMetersBetween(seed.centroid, r.centroid) <= radiusM);
    return geojsonBounds({ type: 'FeatureCollection', features: cluster.map((r) => r.f) });
  }
  // Trail-lane layer state, read + driven directly (no editor checkbox).
  function trailHotspotsActive() {
    return !!(map.getLayer('activity-hotspots-fill')
      && map.getLayoutProperty('activity-hotspots-fill', 'visibility') === 'visible');
  }
  function setTrailHotspotsVisible(on) {
    for (const id of ACTIVITY_HOTSPOT_LAYERS) setLayerVisibility(id, on);
  }
  function hotButtonFlyToHotspots() {
    setTrailHotspotsVisible(true);
    const bbox = findDensestHotspotCluster();
    if (!bbox) return;
    map.fitBounds(bbox, { padding: visibleMapPadding(20), maxZoom: 16.2, duration: 1000, bearing: map.getBearing(), pitch: map.getPitch() });
  }
  function eventScheduleAnchorForward(dayLabel, startLocal) {
    const anchorSat = resolveCalendarAnchorSat();
    if (!anchorSat) return null;
    return eventScheduleStartFromAnchor(dayLabel, startLocal, anchorSat);
  }
  function computeHotButtonTarget() {
    const now = eventScheduleNow();
    const nowMs = now.getTime();
    let live = null;
    let imminent = null;
    let nextFuture = null;
    for (const feature of eventSessionById.values()) {
      const props = feature.properties || {};
      const start = eventScheduleAnchorForward(props.day, props.start_local);
      if (!start) continue;
      const startMs = start.getTime();
      const endMs = startMs + HOT_BUTTON_SESSION_LEN_MIN * 60 * 1000;
      if (nowMs >= startMs && nowMs < endMs) {
        if (!live || startMs < live.startMs) live = { feature, startMs, endMs };
        continue;
      }
      if (startMs > nowMs) {
        const minsUntil = (startMs - nowMs) / 60000;
        if (minsUntil <= HOT_BUTTON_IMMINENT_MIN) {
          if (!imminent || startMs < imminent.startMs) imminent = { feature, startMs, endMs };
        }
        if (!nextFuture || startMs < nextFuture.startMs) nextFuture = { feature, startMs, endMs };
      }
    }
    if (live) return { state: 'hot-now', target: live, kind: 'live' };
    if (imminent) return { state: 'hot-now', target: imminent, kind: 'imminent' };
    if (nextFuture) return { state: 'coming-up', target: nextFuture };
    return { state: 'no-event' };
  }
  function hotEventAvailable(decision) {
    return decision.state === 'hot-now' || decision.state === 'coming-up';
  }
  function selectedHotLane(decision, haveHotspots) {
    const eventAvailable = hotEventAvailable(decision);
    if (preferredHotLane === 'event' && eventAvailable) return 'event';
    if (preferredHotLane === 'trails' && haveHotspots) return 'trails';
    if (decision.state === 'hot-now') return 'event';
    if (haveHotspots) return 'trails';
    if (eventAvailable) return 'event';
    return '';
  }
  function attachHotButton() {
    const eventBtn = document.getElementById('hotButton');
    const trailBtn = document.getElementById('hotTrailButton');
    if (eventBtn && eventBtn.dataset.bound !== '1') {
      eventBtn.dataset.bound = '1';
      eventBtn.addEventListener('click', () => {
        if (eventBtn.disabled) return;
        preferredHotLane = 'event';
        refreshHotButton();
        const id = eventBtn.dataset.targetSessionId;
        if (id) gotoEventSession(id);
      });
    }
    if (trailBtn && trailBtn.dataset.bound !== '1') {
      trailBtn.dataset.bound = '1';
      trailBtn.addEventListener('click', () => {
        if (trailBtn.disabled) return;
        // Toggle keyed off the live layer state: second tap (layer ON) hides the
        // hotspots; first tap from cold turns them ON and flies to the cluster.
        if (trailHotspotsActive()) {
          preferredHotLane = null;
          setTrailHotspotsVisible(false);
          refreshHotButton();
        } else {
          preferredHotLane = 'trails';
          hotButtonFlyToHotspots();
          refreshHotButton();
        }
      });
    }
  }
  // Called by refreshEventScheduleSessionStates (render + 60s tick), so both
  // lanes update in lockstep with the calendar against the same clock.
  function refreshHotButton() {
    attachHotButton();
    const control = document.getElementById('hotControl');
    const lanes = document.getElementById('hotLanes');
    const status = document.getElementById('hotControlStatus');
    const eventBtn = document.getElementById('hotButton');
    const trailBtn = document.getElementById('hotTrailButton');
    if (!control || !eventBtn || !trailBtn) return;
    const glyph = document.getElementById('hotButtonGlyph');
    const title = document.getElementById('hotButtonTitle');
    const detail = document.getElementById('hotButtonDetail');
    const trailTitle = document.getElementById('hotTrailButtonTitle');
    const trailDetail = document.getElementById('hotTrailButtonDetail');
    const decision = computeHotButtonTarget();
    const haveHotspots = !!(aopActivityHotspotsData?.features?.length);
    const eventAvailable = hotEventAvailable(decision);
    if (!eventAvailable && !haveHotspots) {
      control.hidden = true;
      eventBtn.dataset.hotState = 'empty';
      eventBtn.dataset.targetSessionId = '';
      trailBtn.dataset.hotSelected = 'false';
      return;
    }
    control.hidden = false;
    const selected = selectedHotLane(decision, haveHotspots);
    const trailOn = haveHotspots && trailHotspotsActive();
    if (lanes) lanes.dataset.laneCount = haveHotspots ? '2' : '1';
    eventBtn.dataset.hotSelected = selected === 'event' ? 'true' : 'false';
    trailBtn.dataset.hotSelected = trailOn ? 'true' : 'false';
    trailBtn.dataset.hotOn = trailOn ? 'true' : 'false';
    trailBtn.setAttribute('aria-pressed', trailOn ? 'true' : 'false');
    trailBtn.hidden = !haveHotspots;
    trailBtn.disabled = !haveHotspots;
    trailBtn.dataset.hotState = 'trail-hot';
    if (trailTitle) trailTitle.textContent = trailOn ? 'Trail activity on' : 'Trail activity';
    if (trailDetail) trailDetail.textContent = trailOn ? 'Tap to hide hotspots' : 'Where rigs spent time';
    const trailGlyph = document.getElementById('hotTrailButtonGlyph');
    if (trailGlyph) trailGlyph.textContent = trailOn ? '✓' : '❖';
    trailBtn.setAttribute('aria-label', trailOn ? 'Hide trail activity' : 'Show trail activity');

    eventBtn.dataset.hotState = decision.state;
    eventBtn.dataset.hotPriority = decision.state === 'hot-now' ? 'alert' : '';
    const now = eventScheduleNow();
    if (decision.state === 'hot-now') {
      const props = decision.target.feature.properties || {};
      eventBtn.disabled = false;
      eventBtn.dataset.targetSessionId = props.session_id || '';
      if (glyph) glyph.innerHTML = '<svg viewBox="0 0 22 22" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14.082 4.78A7.564 7.564 0 0 1 11 19.25 7.562 7.562 0 0 1 5.535 6.46 7.596 7.596 0 0 0 8.25 8.801a8.234 8.234 0 0 1 3.081-6.295 7.526 7.526 0 0 0 2.751 2.273Z"/><path d="M11 16.5a3.438 3.438 0 0 0 .454-6.845 5.491 5.491 0 0 0-1.765 3.25 5.476 5.476 0 0 1-1.955-.918A3.438 3.438 0 0 0 11 16.5Z"/></svg>';
      if (decision.kind === 'live') {
        const mins = (decision.target.endMs - now.getTime()) / 60000;
        if (title) title.textContent = 'Live event';
        if (detail) detail.textContent = `${props.title || 'Session'} · ${eventScheduleFormatMinutes(mins)} left`;
        if (status) status.textContent = 'Event live';
      } else {
        const mins = (decision.target.startMs - now.getTime()) / 60000;
        if (title) title.textContent = 'Starting soon';
        if (detail) detail.textContent = `${props.title || 'Session'} · in ${eventScheduleFormatMinutes(mins)}`;
        if (status) status.textContent = 'Event soon';
      }
      eventBtn.setAttribute('aria-label', `Event hot: ${props.title || 'session'}`);
    } else if (decision.state === 'coming-up') {
      const props = decision.target.feature.properties || {};
      eventBtn.disabled = false;
      eventBtn.dataset.targetSessionId = props.session_id || '';
      const mins = (decision.target.startMs - now.getTime()) / 60000;
      if (glyph) glyph.textContent = '◷';
      if (title) title.textContent = 'Next event';
      if (detail) {
        const dayPart = props.day ? `${props.day} ` : '';
        const timePart = props.window || props.start_local || '';
        detail.textContent = `${dayPart}${timePart} · in ${eventScheduleFormatMinutes(mins)}`;
      }
      if (status) status.textContent = selected === 'trails' ? 'Trail activity' : 'Next event';
      eventBtn.setAttribute('aria-label', `Next event: ${props.title || 'session'}`);
    } else {
      // No event target, but hotspots are available — event lane idles, trails lead.
      eventBtn.disabled = true;
      eventBtn.dataset.targetSessionId = '';
      if (glyph) glyph.textContent = '◷';
      if (title) title.textContent = 'No event';
      if (detail) detail.textContent = 'Trail activity available';
      if (status) status.textContent = haveHotspots ? 'Trail activity' : 'No target';
      eventBtn.setAttribute('aria-label', 'No event target');
    }
  }

  // ── POI directory (slice 4b) — ★-driven from the data model ────────────
  // The directory IS the set of features the DATA marks as destinations:
  // properties.highlight === true (the baked ★ — mvp/scripts/bake_poi_stars.py).
  // This is the live page's own model; the read core reads the SAME published
  // field, so the editor and the viewer agree on one source — no editor registry,
  // no localStorage, no index side-join. Each carried dataset routes its starred
  // features to a group; the taxonomy (label + order) is inline. Groups whose
  // layers the read core doesn't carry (cemeteries, drawn) just don't appear
  // until those layers are carried.
  const STAR_GROUPS = [
    { id: 'buildings', label: 'Buildings in the park', data: () => poiBuildingsData },
    { id: 'trails', label: 'Trails', data: () => poiPublishData, pred: (p) => p.layer === 'trail_centerlines' },
    { id: 'visitor_support', label: 'Visitor support (off-park)', data: () => poiVisitorData }
  ];
  function flyToFeature(feature) {
    if (!feature || !feature.geometry) return;
    const pad = visibleMapPadding(20);
    const bounds = geojsonBounds({ type: 'FeatureCollection', features: [feature] });
    if (bounds) {
      const [[minLng, minLat], [maxLng, maxLat]] = bounds;
      if (minLng === maxLng && minLat === maxLat) {
        map.flyTo({ center: [minLng, minLat], zoom: 18, offset: visibleCenterOffset(pad), duration: 900, bearing: map.getBearing(), pitch: map.getPitch() });
      } else {
        map.fitBounds(bounds, { padding: pad, maxZoom: 18, duration: 900, bearing: map.getBearing(), pitch: map.getPitch() });
      }
    }
    const highlight = map.getSource('search-highlight');
    if (highlight) {
      highlight.setData({ type: 'FeatureCollection', features: [feature] });
      pulseHighlight();
    }
  }
  function buildPoiGroups() {
    const out = [];
    for (const group of STAR_GROUPS) {
      const data = group.data();
      if (!data || !Array.isArray(data.features)) continue;
      const rows = [];
      for (const feature of data.features) {
        const p = feature.properties || {};
        if (p.highlight !== true) continue;          // the ★ gate, read from the data
        if (group.pred && !group.pred(p)) continue;
        const d = window.AOPFeatureDisplay ? window.AOPFeatureDisplay.featureDisplay(p) : {};
        rows.push({
          name: d.name || '(unnamed)',
          blurb: d.blurb || '',
          kind: d.kind || '',
          status: d.status || '',
          revisitNote: d.revisit || '',
          feature
        });
      }
      if (rows.length) out.push({ id: group.id, label: group.label, rows });
    }
    return out;
  }
  function renderPoiTab() {
    const container = document.getElementById('poiList');
    if (!container) return;
    const groups = buildPoiGroups();
    const totalRows = groups.reduce((sum, g) => sum + g.rows.length, 0);
    container.innerHTML = '';
    if (totalRows === 0) {
      const empty = document.createElement('p');
      empty.className = 'poi-empty';
      empty.textContent = poiBuildingsData ? 'No starred places yet.' : 'Loading places…';
      container.append(empty);
      return;
    }
    for (const group of groups) {
      const groupEl = document.createElement('div');
      groupEl.className = 'poi-list-group';
      const head = document.createElement('div');
      head.className = 'poi-list-group-head';
      const label = document.createElement('span');
      label.textContent = group.label;
      const count = document.createElement('span');
      count.className = 'poi-list-group-count';
      count.textContent = `${group.rows.length}`;
      head.append(label, count);
      groupEl.append(head);
      for (const row of group.rows) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'poi-row';
        btn.setAttribute('aria-label', `Fly to ${row.name}`);
        const name = document.createElement('span');
        name.className = 'poi-row-name';
        name.textContent = row.name;
        btn.append(name);
        const subtitle = document.createElement('span');
        subtitle.className = 'poi-row-subtitle';
        subtitle.textContent = row.blurb || `${row.kind} · ${row.status}`.trim();
        btn.append(subtitle);
        const meta = document.createElement('span');
        meta.className = 'poi-row-meta';
        if (row.kind) { const c = document.createElement('span'); c.textContent = row.kind; meta.append(c); }
        if (row.status) { const c = document.createElement('span'); c.textContent = row.status; meta.append(c); }
        btn.append(meta);
        btn.addEventListener('click', () => gotoPoi(row));
        groupEl.append(btn);
      }
      container.append(groupEl);
    }
  }
  function renderPoiTabIfActive() {
    const panel = document.getElementById('poiTabPanel');
    if (panel && !panel.hidden) renderPoiTab();
  }
  function gotoPoi(row) {
    if (!row || !row.feature || !window.AOPFeatureDisplay) return;
    closeAllMapPopups();
    flyToFeature(row.feature);
    const coord = firstCoordinate(row.feature.geometry);
    if (!coord) return;
    const model = window.AOPFeatureDisplay.featureDisplay(row.feature.properties || {});
    const slice = visibleMapRect();
    const popupMax = Math.max(200, Math.min(300, Math.max(0, slice.right - slice.left) - 28));
    const popup = new maplibregl.Popup({ maxWidth: `${popupMax}px`, className: 'poi-tab-popup' })
      .setLngLat(coord)
      .setHTML(window.AOPFeatureDisplay.popupHtml(model))
      .addTo(map);
    map.once('moveend', () => panPopupIntoView(popup));
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

    // --- Activity hotspots (GPX dwell) — "where the cool spots are" (main.js:8017) ---
    // THE discovery layer: time-weighted from first-party timestamped GPX. Default
    // OFF; the Hot Trails lane toggles it on and flies to the densest cluster.
    const activityData = await fetchJson('./data/aop_activity_hotspots.geojson', 'Activity hotspot layer missing');
    if (activityData) {
      aopActivityHotspotsData = activityData;
      map.addSource('activity-hotspots', {
        type: 'geojson', data: activityData,
        attribution: 'Activity hotspots: first-party timestamped GPX'
      });
      map.addLayer({
        id: 'activity-hotspots-heat', type: 'heatmap', source: 'activity-hotspots',
        filter: ['==', ['geometry-type'], 'Point'],
        layout: { visibility: 'none' },
        paint: {
          'heatmap-weight': ['interpolate', ['linear'], ['get', 'intensity_norm'], 0, 0.18, 1, 1],
          'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 11, 0.45, 16, 1.65],
          'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 11, 18, 16, 44],
          'heatmap-opacity': 0.68,
          'heatmap-color': [
            'interpolate', ['linear'], ['heatmap-density'],
            0, 'rgba(230, 200, 111, 0)',
            0.22, 'rgba(230, 200, 111, 0.55)',
            0.45, 'rgba(217, 144, 61, 0.65)',
            0.72, 'rgba(191, 90, 54, 0.76)',
            1, 'rgba(127, 47, 39, 0.9)'
          ]
        }
      });
      map.addLayer({
        id: 'activity-hotspots-fill', type: 'fill', source: 'activity-hotspots',
        filter: ['==', ['geometry-type'], 'Polygon'],
        layout: { visibility: 'none' },
        paint: { 'fill-color': ACTIVITY_HOTSPOT_FILL, 'fill-opacity': ACTIVITY_HOTSPOT_OPACITY }
      });
      map.addLayer({
        id: 'activity-hotspots-outline', type: 'line', source: 'activity-hotspots',
        filter: ['==', ['geometry-type'], 'Polygon'],
        layout: { visibility: 'none' },
        paint: { 'line-color': '#7f2f27', 'line-width': 1.1, 'line-opacity': 0.55 }
      });
      map.addLayer({
        id: 'activity-hotspots-labels', type: 'symbol', source: 'activity-hotspots',
        filter: ['all', ['==', ['geometry-type'], 'Point'], ['!=', ['get', 'label'], '']],
        layout: {
          visibility: 'none', 'text-field': ['get', 'label'],
          'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12],
          'text-allow-overlap': false, 'text-ignore-placement': false
        },
        paint: { 'text-color': '#5b2d25', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.4 }
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
    poiVisitorData = visitorContextData;
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
    poiBuildingsData = buildingsData;
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
    poiPublishData = publishData;

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

    // --- Event schedule (main.js:8208-8339) ---
    // The shared resolver turns the served {event,locations,sessions} document
    // into anchor + session GeoJSON. The 4 layers start hidden (selection-driven,
    // not preset-driven); a calendar row / search match unhides them.
    eventScheduleConfig = await fetchJson('./data/aop_event_schedule.json', 'Event schedule missing');
    if (eventScheduleConfig && window.AOPEventSchedule) {
      const built = window.AOPEventSchedule.eventScheduleToGeojson(eventScheduleConfig);
      eventScheduleData = built.geojson;
      eventLocationByTag = built.locationByTag;
      eventSessionById = built.sessionById;
      renderEventSchedule(eventScheduleConfig, eventScheduleData);
      map.addSource('event-schedule', {
        type: 'geojson', data: eventScheduleData,
        attribution: 'Event schedule: proposed from sister-event references'
      });
      map.addLayer({
        id: 'event-session-routes', type: 'line', source: 'event-schedule',
        filter: ['all', ['==', ['get', 'feature_kind'], 'event_session'], ['==', ['geometry-type'], 'LineString']],
        layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
        paint: {
          'line-color': '#b45f43',
          'line-width': ['interpolate', ['linear'], ['zoom'], 12, 2, 16, 4.2],
          'line-opacity': 0.92, 'line-dasharray': [3, 1.4]
        }
      });
      map.addLayer({
        id: 'event-route-labels', type: 'symbol', source: 'event-schedule',
        filter: ['all', ['==', ['get', 'feature_kind'], 'event_session'], ['==', ['geometry-type'], 'LineString']],
        layout: {
          visibility: 'none', 'symbol-placement': 'line',
          'text-field': ['get', 'title'],
          'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12],
          'text-keep-upright': true
        },
        paint: { 'text-color': '#6f382b', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
      });
      map.addLayer({
        id: 'event-anchor-points', type: 'circle', source: 'event-schedule',
        filter: ['==', ['get', 'feature_kind'], 'event_anchor'],
        layout: { visibility: 'none' },
        paint: {
          'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 4.5, 16, 8],
          'circle-color': ['match', ['get', 'role'],
            'pavilion', '#8b5f38', 'event_registration', '#b05a48', 'event_stage_start', '#7f7a4b',
            'event_proving_ground', '#9a7d96', 'event_checkpoint', '#b45f43', 'event_photo_waypoint', '#5f9183',
            '#8b5f38'],
          'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 2
        }
      });
      map.addLayer({
        id: 'event-anchor-labels', type: 'symbol', source: 'event-schedule',
        filter: ['==', ['get', 'feature_kind'], 'event_anchor'],
        layout: {
          visibility: 'none', 'text-field': ['get', 'map_label'],
          'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12],
          'text-offset': [0, 1.2], 'text-anchor': 'top'
        },
        paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 }
      });
      // Anchors searchable; their #tag is a search alias. A match unhides the
      // event layers (selection-driven).
      indexFeatures(eventScheduleData,
        (props) => props.feature_kind === 'event_anchor' ? 'event location' : 'event session',
        () => EVENT_LAYER_IDS,
        (props) => props.feature_kind === 'event_anchor' ? [props.location_tag] : null);
      // Open pointed at whatever the calendar is highlighting (live / next).
      window.setTimeout(() => {
        const live = calendarDays?.querySelector('li[data-session-state="happening"] .calendar-row, li[data-session-state="upcoming_next"] .calendar-row');
        const sessionId = live?.dataset?.sessionId;
        if (sessionId && eventSessionById.has(sessionId)) gotoEventSession(sessionId);
      }, 300);
    } else if (calendarDays) {
      calendarDays.innerHTML = '<li class="calendar-empty">Schedule unavailable.</li>';
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
    renderPoiTabIfActive();
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
  // PWA viewport health (main.js:10084-10118; working_pwa_css.md §7). iOS finalizes
  // the standalone viewport height LATE (status-bar / home-indicator settle, rotation,
  // return from background) and MapLibre's ResizeObserver on the position:fixed #map
  // doesn't always catch it — an unresized canvas leaves the body bg showing under the
  // home indicator. map.resize() is cheap + idempotent. rAF-coalesced (visualViewport
  // 'resize' fires continuously while the iOS URL bar / keyboard animates), and the
  // resize is skipped when the container box hasn't actually changed. The position:fixed
  // search dropdown reposition rides along.
  let resyncRAF = 0;
  let lastMapSize = '';
  const doResyncViewport = () => {
    resyncRAF = 0;
    const c = map.getContainer();
    const size = `${c.clientWidth}x${c.clientHeight}`;
    if (size !== lastMapSize) { lastMapSize = size; map.resize(); }
    if (searchResults.style.display === 'block') positionSearchResults();
  };
  const resyncViewport = () => {
    if (resyncRAF) return;
    resyncRAF = requestAnimationFrame(doResyncViewport);
  };
  window.addEventListener('resize', resyncViewport);
  window.addEventListener('orientationchange', () => setTimeout(resyncViewport, 250));
  window.addEventListener('pageshow', resyncViewport);
  if (window.visualViewport) window.visualViewport.addEventListener('resize', resyncViewport);
  window.addEventListener('scroll', () => { if (searchResults.style.display === 'block') positionSearchResults(); }, true);

  // ── Left-rail drawer reflow + tabs (main.js:10485-10569) ───────────────
  // Two cards (Search, Calendar), both open by default. The icon tabs float
  // down to meet their panel's top. Each card's open/closed state persists
  // across reloads (localStorage), the same way the card-height pref below does;
  // the external lrOpenCard/lrCloseCard hooks stay dropped in the read core.
  const LR_CARDS = ['search', 'hot', 'cal'];
  const lrTabs = {
    search: document.getElementById('lrTabSearch'),
    hot: document.getElementById('lrTabHot'),
    cal: document.getElementById('lrTabCal')
  };
  const lrPanels = {
    search: document.getElementById('lrPanelSearch'),
    hot: document.getElementById('lrPanelHot'),
    cal: document.getElementById('lrPanelCal')
  };
  const lrIconCol = document.getElementById('lrIconCol');
  const lrContentCol = document.getElementById('lrContentCol');
  if (lrIconCol && lrContentCol) {
    // Hot defaults closed (live desktop default); a target un-hides the
    // hot-control inside, so opening the Hot tab reveals the lane.
    const LR_DEFAULT_OPEN = { search: true, hot: false, cal: true };
    // Persist which cards are open so a user's drawer layout survives reload.
    // Forward-only key per viewer_storage_migration.md; tolerant of the old
    // viewer's { open: {...} } envelope on the same key, else falls to defaults.
    const DRAWER_KEY = 'aop_left_rail_drawer_v1';
    const readDrawerOpen = () => {
      try {
        const raw = JSON.parse(localStorage.getItem(DRAWER_KEY) || 'null');
        const src = (raw && typeof raw === 'object')
          ? (raw.open && typeof raw.open === 'object' ? raw.open : raw)
          : null;
        const open = {};
        LR_CARDS.forEach((c) => { open[c] = typeof src?.[c] === 'boolean' ? src[c] : LR_DEFAULT_OPEN[c]; });
        return open;
      } catch (_) { return { ...LR_DEFAULT_OPEN }; }
    };
    const lrOpen = readDrawerOpen();
    const writeDrawerOpen = () => {
      try { localStorage.setItem(DRAWER_KEY, JSON.stringify({ search: !!lrOpen.search, hot: !!lrOpen.hot, cal: !!lrOpen.cal })); } catch (_) { /* private mode / quota */ }
    };
    const TAB_H = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--tab-h'), 10) || 44;
    const lrRender = () => {
      const anyOpen = LR_CARDS.some((c) => lrOpen[c]);
      lrContentCol.hidden = !anyOpen;
      lrIconCol.classList.toggle('standalone', !anyOpen);
      LR_CARDS.forEach((c) => {
        const isOpen = !!lrOpen[c];
        lrTabs[c].classList.toggle('open', isOpen);
        lrTabs[c].setAttribute('aria-pressed', isOpen ? 'true' : 'false');
        lrPanels[c].classList.toggle('open', isOpen);
      });
      LR_CARDS.forEach((c) => { lrTabs[c].style.marginTop = ''; });
      void lrContentCol.offsetHeight;
      let prevBottom = 0;
      LR_CARDS.forEach((c, i) => {
        const canonical = i * TAB_H;
        const pTop = lrOpen[c] ? lrPanels[c].offsetTop : -Infinity;
        const desired = Math.max(canonical, pTop, prevBottom);
        lrTabs[c].style.marginTop = (desired - prevBottom) + 'px';
        prevBottom = desired + TAB_H;
      });
      lrIconCol.classList.toggle('col2-short', anyOpen && lrContentCol.offsetHeight < lrIconCol.offsetHeight);
    };
    LR_CARDS.forEach((c) => {
      lrTabs[c].addEventListener('click', () => { lrOpen[c] = !lrOpen[c]; lrRender(); writeDrawerOpen(); });
    });
    // Resizing a card body shifts every panel's offsetTop, so the floating
    // icon-column tabs must re-lay-out against the new rects (initLrCardResize
    // calls this). Expose the existing reflow rather than build a second one.
    window.lrReflow = lrRender;
    lrRender();
  }

  // ── Schedule "clipboard" resize (main.js initializeLrCardResize) ─────────
  // Restore the per-card drag handle the viewer swap deferred. Each card body
  // (Events / POI / About) shares one --lr-card-body-height var on
  // .lr-content-col, so dragging any handle keeps the three heights consistent.
  // Height persists in localStorage so a grown schedule survives reload — the
  // only session pref the read core keeps; everything else stays stateless.
  (function initLrCardResize() {
    const lrCol = document.getElementById('lrContentCol');
    const handles = [
      { handle: document.getElementById('calendarResizeHandle'), body: document.getElementById('calendarBody') },
      { handle: document.getElementById('poiResizeHandle'), body: document.getElementById('poiList') },
      { handle: document.getElementById('aboutResizeHandle'), body: document.getElementById('aboutInfoPanel') }
    ].filter((entry) => entry.handle && entry.body);
    if (!lrCol || !handles.length) return;

    const HEIGHT_KEY = 'aop_lr_card_height_v1';
    const readStoredHeight = () => {
      try {
        const raw = localStorage.getItem(HEIGHT_KEY);
        const n = raw == null ? NaN : Number(JSON.parse(raw));
        return Number.isFinite(n) ? n : null;
      } catch (_) { return null; }
    };
    const writeStoredHeight = (value) => {
      try { localStorage.setItem(HEIGHT_KEY, JSON.stringify(value)); } catch (_) { /* private mode / quota */ }
    };

    function cardCurrentHeight(body) {
      if (!body) return 240;
      const rect = body.getBoundingClientRect();
      return (Number.isFinite(rect.height) && rect.height > 0) ? rect.height : 240;
    }

    function setCardHeight(height, persist) {
      const next = Math.round(Math.max(0, Number(height) || 0));
      lrCol.style.setProperty('--lr-card-body-height', `${next}px`);
      for (const { handle } of handles) handle.setAttribute('aria-valuenow', String(next));
      if (persist) writeStoredHeight(next);
      scrollCalendarCurrentRowIntoView();
      if (typeof window.lrReflow === 'function') window.lrReflow();
    }

    const stored = readStoredHeight();
    if (Number.isFinite(stored)) setCardHeight(stored, false);
    else for (const { handle, body } of handles) handle.setAttribute('aria-valuenow', String(Math.round(cardCurrentHeight(body))));

    for (const { handle, body } of handles) {
      let drag = null;
      handle.addEventListener('pointerdown', (event) => {
        if (event.button != null && event.button !== 0) return;
        event.preventDefault();
        drag = { y: event.clientY, height: cardCurrentHeight(body), pointerId: event.pointerId };
        handle.setPointerCapture(event.pointerId);
      });
      handle.addEventListener('pointermove', (event) => {
        if (!drag) return;
        event.preventDefault();
        setCardHeight(drag.height + event.clientY - drag.y, false);
      });
      const finishDrag = (event) => {
        if (!drag) return;
        const next = drag.height + event.clientY - drag.y;
        if (handle.hasPointerCapture(drag.pointerId)) handle.releasePointerCapture(drag.pointerId);
        drag = null;
        setCardHeight(next, true);
      };
      handle.addEventListener('pointerup', finishDrag);
      handle.addEventListener('pointercancel', finishDrag);
      handle.addEventListener('keydown', (event) => {
        let next = cardCurrentHeight(body);
        if (event.key === 'ArrowDown') next += 24;
        else if (event.key === 'ArrowUp') next -= 24;
        else if (event.key === 'PageDown') next += 72;
        else if (event.key === 'PageUp') next -= 72;
        else if (event.key === 'Home') next = 0;
        else return;
        event.preventDefault();
        setCardHeight(next, true);
      });
    }
  })();

  // Left-tab switch (Events / About) + calendar row → fly to the session.
  for (const button of leftTabButtons) {
    button.addEventListener('click', () => setLeftTab(button.dataset.leftTab));
  }
  calendarDays?.addEventListener('click', (event) => {
    const row = event.target.closest('.calendar-row');
    if (row?.dataset.sessionId) gotoEventSession(row.dataset.sessionId);
  });

  // About panel copy (data/aop_about.json), best-effort — a missing file just
  // leaves the literal fallback in the markup.
  (function loadAbout() {
    const panel = document.getElementById('aboutInfoPanel');
    if (!panel) return;
    fetch('./data/aop_about.json')
      .then((res) => (res.ok ? res.json() : null))
      .then((about) => { if (about) renderAbout(about, panel); })
      .catch(() => {});
  })();

  // POI directory renders from the baked ★ on the served data (read in the load
  // handler via renderPoiTabIfActive); nothing to fetch up front.

  // ── Feature click popups — the ONE normalized strategy (slice 4) ───────
  // Click a curated/published feature → its "what is this line, where did it
  // come from?" card, via the shared window.AOPFeatureDisplay (the same module
  // the live page + editors use). Branch-free: every feature reads the same
  // fallback chain. (The POI-tab directory + ★-destinations are slice 4b.)
  const INTERACTIVE_POPUP_LAYERS = [
    'aop-trail-network', 'publish-trails', 'publish-trailheads', 'publish-boundaries',
    'building-footprint-fill', 'building-footprint-aop-outline',
    'visitor-context-fill', 'water-points', 'streams',
    'event-anchor-points', 'event-session-routes', 'brand-logos-icons'
  ];
  function interactivePopupLayers() {
    return INTERACTIVE_POPUP_LAYERS.filter((id) => map.getLayer(id));
  }
  map.on('click', (e) => {
    if (!window.AOPFeatureDisplay) return;
    const layers = interactivePopupLayers();
    if (!layers.length) return;
    const feats = map.queryRenderedFeatures(e.point, { layers });
    if (!feats.length) return;
    const model = window.AOPFeatureDisplay.featureDisplay(feats[0].properties || {});
    closeAllMapPopups();
    const slice = visibleMapRect();
    const popupMax = Math.max(200, Math.min(300, Math.max(0, slice.right - slice.left) - 28));
    const popup = new maplibregl.Popup({ maxWidth: `${popupMax}px`, className: 'poi-tab-popup' })
      .setLngLat(e.lngLat)
      .setHTML(window.AOPFeatureDisplay.popupHtml(model))
      .addTo(map);
    map.once('moveend', () => panPopupIntoView(popup));
  });
  map.on('mousemove', (e) => {
    const layers = interactivePopupLayers();
    if (!layers.length) return;
    map.getCanvas().style.cursor = map.queryRenderedFeatures(e.point, { layers }).length ? 'pointer' : '';
  });
})();
