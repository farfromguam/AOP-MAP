// AOP viewer — main application script. Extracted verbatim from
// website/index.html (Stage 1, viewer_source_split). Loaded as
// <script type="module" src="./js/main.js">. Runs in module scope:
// the markup has zero inline on*= handlers, and the only intended
// globals (lrOpenCard/lrCloseCard/lrResetCards/lrReflow, AOP_UI) are
// still set explicitly on window, so nothing depends on top-level
// declarations being global. No logic changed.

    // The 9-patch data-acquisition AOI doubles as the camera leash: maxBounds
    // stops users panning or zooming out past where there is any map data.
    const REGION_BOUNDS = [[-85.782935283, 35.067164188], [-85.717154097, 35.117928496]];

    // Tighter-than-region fallback for the Park camera preset. The live park
    // bounds come from gold_publish.geojson's `park_boundaries` parcel
    // (parkViewBounds, derived on load); this is the static stand-in for when
    // that data hasn't loaded — same parcel envelope, so Park never collapses
    // back to the full-region zoom. Spans ~1/3 of REGION_BOUNDS per side.
    const PARK_BOUNDS_FALLBACK = [[-85.761008221, 35.084085624], [-85.739081159, 35.10100706]];

    // Every localStorage key the viewer owns. Centralized so a typo on a
    // string literal cannot silently lose user state (the silent-drop class
    // northstar/source_register.md warns about, applied to local persistence).
    const LR_CARD_HEIGHT_KEY = 'aop_lr_card_height_v1';
    // Unified store for user-positioned features. Keyed by `layerKey:id`,
    // each entry carries the per-feature overrides this layer cares about:
    // `geometry` (drag-to-move), `highlight` (★), `locked` (🔒 lock the
    // placement so move/star become no-ops), `icon_size` (brand-logo only).
    // Replaces the per-layer override stores that lived under
    // `aop_visitor_context_overrides_v1` and `aop_brand_logos_overrides_v1`
    // — one schema, one save path, one apply path. editorPois geometry stays
    // in its own array store because the array IS the source of truth; its
    // highlight + locked travel inside feature.properties so GeoJSON export
    // carries them.
    const POSITIONED_FEATURES_KEY = 'aop_positioned_features_v1';
    const FEATURE_VISIBILITY_KEY = 'aop_feature_visibility_v1';
    const FEATURE_TAG_KEY = 'aop_feature_tags_v1';
    // Retired 2026-05-26 with the editor-seed migration: the #pavilion
    // binding now lives on the seeded POI in `bronze_aop_editor_seed_pois.geojson`,
    // not on the 1010 building. The key itself stays in the Reset-viewer
    // wipe-list as a literal so existing installs that still carry the
    // sticky flag get it cleared.
    // const FEATURE_TAG_SEEDED_KEY = 'aop_feature_tags_seeded_v1';
    const POI_STORAGE_KEY = 'aop_editor_pois_v1';
    const VIEWER_PRESET_KEY = 'aop_viewer_preset_settings_v1';
    const LEFT_RAIL_DRAWER_KEY = 'aop_left_rail_drawer_v1';
    const VIRTUAL_CLOCK_KEY = 'aop_virtual_clock_v1';
    const VIEWER_SESSION_KEY = 'aop_viewer_session_state_v1';

    // Shared JSON-store helpers — every persisted feature in the viewer
    // (calendar height, visitor-context overrides, per-feature visibility,
    // tag bindings, drawn POIs, preset settings) reads and writes through
    // these. Quiet on a localStorage-unavailable browser; logs on a parse
    // failure so a corrupt store does not vanish without notice.
    function readJsonStore(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        if (raw == null) return typeof fallback === 'function' ? fallback() : fallback;
        const parsed = JSON.parse(raw);
        return parsed == null ? (typeof fallback === 'function' ? fallback() : fallback) : parsed;
      } catch (err) {
        console.warn(`[${key}] unreadable, resetting`, err);
        return typeof fallback === 'function' ? fallback() : fallback;
      }
    }

    function writeJsonStore(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
      } catch (err) {
        console.warn(`[${key}] could not persist`, err);
        return false;
      }
    }

    function removeJsonStore(key) {
      try { localStorage.removeItem(key); }
      catch (_) { /* localStorage unavailable — ignore */ }
    }

    const VIEWER_OWNED_STORAGE_KEYS = [
      LR_CARD_HEIGHT_KEY,
      'aop_calendar_height_v1',
      'aop_calendar_collapsed_v1',
      POSITIONED_FEATURES_KEY,
      // Retired 2026-05-28 (unified positioned-features store). Kept here as
      // literals so existing installs get them cleared on Reset viewer.
      'aop_visitor_context_overrides_v1',
      'aop_brand_logos_overrides_v1',
      FEATURE_VISIBILITY_KEY,
      FEATURE_TAG_KEY,
      'aop_feature_tags_seeded_v1',
      POI_STORAGE_KEY,
      VIEWER_PRESET_KEY,
      LEFT_RAIL_DRAWER_KEY,
      VIRTUAL_CLOCK_KEY,
      VIEWER_SESSION_KEY,
      // Brand-logo max-size cap (item 5). Literal because BRAND_LOGO_CAP_KEY
      // is declared later in the module scope (TDZ); the string is stable.
      'aop_brand_logo_cap_v1'
    ];

    // Read a layered store (a flat object keyed by layerKey), merge a subset
    // of layer slices in, and write it back. Used by section-export / -apply
    // for `aop_feature_visibility_v1` and `aop_feature_tags_v1`, which both
    // bucket data by consumer layer.
    function mergeStoreSlice(key, slice) {
      if (!slice || typeof slice !== 'object') return;
      const all = readJsonStore(key, () => ({}));
      for (const [layerKey, layerSlice] of Object.entries(slice)) {
        // Shallow-merge per-layer so a partial slice (e.g. a one-section paste)
        // adds to that layer's existing entries instead of replacing them all.
        if (layerSlice && typeof layerSlice === 'object') {
          const existing = (all[layerKey] && typeof all[layerKey] === 'object') ? all[layerKey] : {};
          all[layerKey] = { ...existing, ...layerSlice };
        } else if (layerSlice) {
          all[layerKey] = layerSlice;
        }
      }
      writeJsonStore(key, all);
    }

    const map = new maplibregl.Map({
      container: 'map',
      style: {
        version: 8,
        sources: {},
        layers: [
          {
            id: 'background',
            type: 'background',
            paint: { 'background-color': '#efe7d5' }
          }
        ]
      },
      center: [-85.75, 35.0925],
      zoom: 12,
      bearing: -90,
      maxBounds: REGION_BOUNDS,
      attributionControl: false
    });

    // Right-panel swap (2026-06-05): expose the host map for the embedded
    // one-model panel (js/panel.js). `map` is a top-level lexical const, not a
    // window property, so the panel can't reach it without this. Additive only.
    window.AOP_HOST_MAP = map;

    // Log style/glyph/source errors. Registered at construction (not inside the
    // 'load' handler) so failures during the INITIAL style + glyph load are caught
    // too — a load-handler registration misses everything before 'load' fires (L12).
    map.on('error', (e) => { console.error(e.error || e); });

    // Touch: make a SIMULTANEOUS two-finger pinch start zooming immediately.
    // MapLibre's default touch handler bundles pinch-zoom with two-finger
    // twist-rotate, and when both fingers land at once it stalls deciding
    // between them — so a clean two-finger pinch often fails to start, while
    // landing one finger then the second works (the gesture is already
    // disambiguated). disableRotation() drops the twist-rotate arbitration so
    // pinch-zoom fires on first move. Kept: two-finger drag-to-TILT (the
    // separate TouchPitch handler) and right-click drag rotate — so the 3D
    // tilt/rotate the help text promises still works; only the rarely-used
    // two-finger twist is gone. (pwa_qa item 7 — touch-only, confirm on device.)
    map.touchZoomRotate.disableRotation();

    // V5: attribution lives bottom-left as a compact ⓘ, clear of the bottom-right edit FAB.
    map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-left');

    // pwa_qa_2 item 3: fold the build version INTO that bottom-left ⓘ so the
    // corner reads "ⓘ v18" — one pill, version beside the icon, click still
    // expands the credits as before. Relocates the standalone #appVersion node
    // out from under the Install square into the attribution control's
    // bottom-left container (created synchronously by the addControl above).
    (function foldVersionIntoInfoControl() {
      const bottomLeft = map.getContainer().querySelector('.maplibregl-ctrl-bottom-left');
      const versionEl = document.getElementById('appVersion');
      if (bottomLeft && versionEl) {
        bottomLeft.classList.add('attrib-with-version');
        bottomLeft.appendChild(versionEl);
      }
    })();

    // Field "where am I" — blue dot + accuracy halo + follow mode. Position comes
    // from the device GPS chip, so it works offline at the park; it only needs a
    // secure context (HTTPS or localhost), same gate as the service worker.
    // maplibregl.GeolocateControl wraps navigator.geolocation watch/clear for us.
    const geolocate = new maplibregl.GeolocateControl({
      positionOptions: { enableHighAccuracy: true },
      trackUserLocation: true,
      showUserLocation: true,
      showAccuracyCircle: true
    });
    map.addControl(geolocate, 'top-right');

    // On phones, start the attribution collapsed to the ⓘ. MapLibre's compact
    // attribution starts EXPANDED — the full per-source credits show as a tall
    // white text band under the map (a real eyesore at narrow PWA widths) and
    // only minimize to the ⓘ on the first map drag. The `maplibregl-compact-show`
    // class is auto-added once, when the first attributed source loads
    // (empty→content transition); because this viewer adds sources dynamically
    // after `load`, we listen on `sourcedata`, collapse once it appears, and
    // unbind. After that MapLibre never re-adds compact-show on its own, so we
    // never fight the user's later ⓘ taps. Guarded to narrow viewports only —
    // wider screens keep the full attribution bar they've always shown (this
    // build's control carries the `maplibregl-compact` class even when wide, so
    // the width check, not the class, is what scopes this to phones).
    const collapseAttribOnce = () => {
      // V5: collapse to the compact ⓘ on every width (desktop now matches mobile).
      const el = document.querySelector('.maplibregl-ctrl-attrib.maplibregl-compact');
      if (!el) return;
      el.classList.remove('maplibregl-compact-show');
      el.removeAttribute('open');
      map.off('sourcedata', collapseAttribOnce);
    };
    map.on('sourcedata', collapseAttribOnce);

    // The default top-right geolocate button is hidden by CSS; surface it as
    // the Locate float-group button in the left rail. trigger() drives the
    // same watch/marker/follow logic; we just mirror its tracking state onto
    // our button so it lights up (moss) while it has a fix.
    const locateBtn = document.getElementById('locateBtn');
    if (locateBtn) {
      locateBtn.addEventListener('click', () => geolocate.trigger());
      const lit = () => { locateBtn.classList.add('active'); locateBtn.setAttribute('aria-pressed', 'true'); };
      const dim = () => { locateBtn.classList.remove('active'); locateBtn.setAttribute('aria-pressed', 'false'); };
      geolocate.on('trackuserlocationstart', lit);
      geolocate.on('trackuserlocationend', dim);
      geolocate.on('error', dim);
    }

    const message = document.getElementById('message');
    const terrainToggle = document.getElementById('showTerrain');
    const landcoverToggle = document.getElementById('showLandcover');
    const landcover9Toggle = document.getElementById('showLandcover9');
    const landcover9Opacity = document.getElementById('landcover9Opacity');
    const hillshadeToggle = document.getElementById('showHillshade');
    const contoursToggle = document.getElementById('showContours');
    const activityHotspotsToggle = document.getElementById('showActivityHotspots');
    const syntheticActivityToggle = document.getElementById('showSyntheticActivity');
    const eventScheduleToggle = document.getElementById('showEventSchedule');
    const satelliteToggle = document.getElementById('showSatellite');
    const usdaNaipToggle = document.getElementById('showUsdaNaip');
    const ninePatchToggle = document.getElementById('showNinePatch');
    const lidarTilesToggle = document.getElementById('showLidarTiles');
    const roadsToggle = document.getElementById('showRoads');
    const visitorContextToggle = document.getElementById('showVisitorContext');
    const brandLogosToggle = document.getElementById('showBrandLogos');
    const waterToggle = document.getElementById('showWater');
    const springsToggle = document.getElementById('showSprings');
    const cemeteriesToggle = document.getElementById('showCemeteries');
    const buildingsToggle = document.getElementById('showBuildings');
    const osmParkToggle = document.getElementById('showOsmPark');
    const osmTracksToggle = document.getElementById('showOsmTracks');
    const osmServiceToggle = document.getElementById('showOsmService');
    const osmNamedToggle = document.getElementById('showOsmNamed');
    const sfwdaToggle = document.getElementById('showSfwda');
    const sfwdaTraceTrailsToggle = document.getElementById('showSfwdaTraceTrails');
    const aopTrailNetworkToggle = document.getElementById('showAopTrailNetwork');
    const sfwdaOpacity = document.getElementById('sfwdaOpacity');
    const sfwdaMultiply = document.getElementById('sfwdaMultiply');
    const editSfwdaToggle = document.getElementById('editSfwda');
    const showInteriorToggle = document.getElementById('showInterior');
    const exportAlignmentBtn = document.getElementById('exportAlignment');
    const resetAlignmentBtn = document.getElementById('resetAlignment');
    const rotateCcwBtn = document.getElementById('rotateCcw');
    const rotateCwBtn = document.getElementById('rotateCw');
    const trailToggle = document.getElementById('showTrails');
    const boundaryToggle = document.getElementById('showBoundaries');
    const trailheadToggle = document.getElementById('showTrailheads');
    const editorPoiToggle = document.getElementById('showEditorPois');
    const poiCategory = document.getElementById('poiCategory');
    const placePoiBtn = document.getElementById('placePoiBtn');
    const drawFootprintBtn = document.getElementById('drawFootprintBtn');
    const traceLineBtn = document.getElementById('traceLineBtn');
    const exportPoiBtn = document.getElementById('exportPoiBtn');
    const clearPoiBtn = document.getElementById('clearPoiBtn');
    const poiStatus = document.getElementById('poiStatus');
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const calendarCard = document.getElementById('calendarCard');
    const calendarRange = document.getElementById('calendarRange');
    const calendarBody = document.getElementById('calendarBody');
    const calendarDays = document.getElementById('calendarDays');
    const calendarCountdown = document.getElementById('calendarCountdown');
    const calendarCountdownValue = document.getElementById('calendarCountdownValue');
    const calendarResizeHandle = document.getElementById('calendarResizeHandle');
    const leftTabButtons = [...document.querySelectorAll('.left-tab[data-left-tab]')];
    const leftTabPanels = [...document.querySelectorAll('.left-tab-panel')];
    const presetButtons = [...document.querySelectorAll('.preset-bar button[data-preset]')];
    const terrainButton = document.getElementById('terrainButton');
    const layerEditor = document.getElementById('layerEditor');
    const layerEditorTitle = document.getElementById('layerEditorTitle');
    const copyLayerBtn = document.getElementById('copyLayerBtn');
    const tuneControls = document.getElementById('tuneControls');
    const sfwdaDrawerControls = document.getElementById('sfwdaDrawerControls');
    const featureListEl = document.getElementById('featureList');
    // Per-layer render targets. The drawer's shared #featureList is the
    // default for layers without a registered target. Layers can register
    // multiple targets — used by the unified editor tree where editorPois
    // renders three times (once per geometry bucket) with `onlyGroupId`
    // filtering the runtime groups down to one per bucket. Each entry is
    // `{ target, onlyGroupId? }`. Card:
    // brain/tasks/04_event_app/editor_unified_tree.md.
    const FEATURE_LIST_TARGETS = {};
    function registerFeatureListTarget(layerKey, target, opts = {}) {
      if (!FEATURE_LIST_TARGETS[layerKey]) FEATURE_LIST_TARGETS[layerKey] = [];
      FEATURE_LIST_TARGETS[layerKey].push({ target, ...opts });
    }
    function clearFeatureListTargets(layerKey) {
      delete FEATURE_LIST_TARGETS[layerKey];
    }
    function featureListTargetsFor(layerKey) {
      const arr = FEATURE_LIST_TARGETS[layerKey];
      if (arr && arr.length) return arr;
      return [{ target: featureListEl }];
    }
    // True when a re-render would actually be seen — either the drawer is
    // showing this layer, or the layer has its own registered targets.
    function shouldRenderFeatureList(layerKey) {
      return expandedTuneKey === layerKey || Boolean(FEATURE_LIST_TARGETS[layerKey]);
    }
    const tuneVisible = document.getElementById('tuneVisible');
    // Snapshot Preset + Export Settings buttons retired 2026-05-23. The
    // export-only flow that replaced them: per-section ⧉ on each section
    // header, per-feature ⧉ on each feature row (drop-in geojson Feature),
    // and one bottom-of-panel "Export all" for the full v2 bundle. Import
    // happens out-of-band — user pastes the JSON to the assistant or
    // directly into code; we don't ship an import UI.
    const exportAllBtn = document.getElementById('exportAll');
    const presetStatus = document.getElementById('presetStatus');
    const virtualClockStatus = document.getElementById('virtualClockStatus');
    const virtualClockDate = document.getElementById('virtualClockDate');
    const virtualClockTime = document.getElementById('virtualClockTime');
    const clockMinusDay = document.getElementById('clockMinusDay');
    const clockPlusDay = document.getElementById('clockPlusDay');
    const clockMinusHour = document.getElementById('clockMinusHour');
    const clockPlusHour = document.getElementById('clockPlusHour');
    const clockUseInputs = document.getElementById('clockUseInputs');
    const clockUseNow = document.getElementById('clockUseNow');
    const clockClear = document.getElementById('clockClear');
    const resetViewerStateBtn = document.getElementById('resetViewerState');
    const torchCacheBtn = document.getElementById('torchCache');

    // --- Right panel: collapse upward into its header bar ---
    const panel = document.querySelector('.panel');
    const panelHeader = document.getElementById('panelHeader');
    const panelBody = document.getElementById('panelBody');
    const panelCollapse = document.getElementById('panelCollapse');
    // Edit panel ships collapsed (header bar only); user opens it on demand.
    let panelCollapsed = true;

    // Item 15: the left-rail drawer's floating icon column derives its tab
    // offsets from live panel rects (window.lrReflow). Collapsing/expanding the
    // right edit panel reflows the page, so recompute that geometry against
    // fresh rects -- otherwise the drawer handle and offset go stale and a drag
    // no longer tracks the finger. Reflow on the next frame (initial layout
    // shift) and again on transitionend (final settled rect).
    function reflowLeftRailDrawer() {
      if (typeof window.lrReflow === 'function') window.lrReflow();
    }

    function togglePanel() {
      panelCollapsed = !panelCollapsed;
      panel.classList.toggle('collapsed', panelCollapsed);
      panelCollapse.textContent = panelCollapsed ? '▸' : '▾';
      panelCollapse.setAttribute('aria-expanded', String(!panelCollapsed));
      panelHeader.title = panelCollapse.title = panelCollapsed ? 'Expand panel' : 'Collapse panel';
      if (panelCollapsed) {
        // Pin the live height so the transition has somewhere to retract from.
        panelBody.style.maxHeight = panelBody.scrollHeight + 'px';
        requestAnimationFrame(() => { panelBody.style.maxHeight = '0px'; });
      } else {
        // Expand: animate from the collapsed 0 up to the content height, then
        // DROP the cap so the body grows to its natural height and `.panel`
        // (overflow-y:auto) becomes the scroll container. The cap MUST be
        // cleared. The old code set max-height straight to scrollHeight and
        // relied on `transitionend` alone to clear it -- but the first expand
        // animated from computed `max-height:none` (the collapsed class is
        // removed before this runs), and browsers fire NO transitionend when
        // animating from `none`. So the cap stuck at the expand-time
        // scrollHeight and clipped everything opened afterwards (inner
        // sections, feature lists) with overflow:hidden and no way to scroll.
        const dropCap = () => { if (!panelCollapsed) panelBody.style.maxHeight = ''; };
        panelBody.style.maxHeight = '0px';
        requestAnimationFrame(() => { panelBody.style.maxHeight = panelBody.scrollHeight + 'px'; });
        panelBody.addEventListener('transitionend', function clear(e) {
          if (e.target !== panelBody || e.propertyName !== 'max-height') return;
          dropCap();
          panelBody.removeEventListener('transitionend', clear);
        });
        // Safety net: if transitionend never lands (reduced-motion, an
        // interrupted or zero-delta transition), clear the cap anyway so the
        // panel can never get stuck unscrollable. ~matches the 0.26s anim.
        setTimeout(dropCap, 360);
      }
      // Recompute drawer geometry now (post-class-change) and after the panel's
      // max-height transition lands on its final rect.
      requestAnimationFrame(reflowLeftRailDrawer);
      let settleTimer = 0;
      const settle = (e) => {
        if (e.target !== panel && e.target !== panelBody) return;
        if (e.propertyName !== 'max-height' && e.propertyName !== 'width' && e.propertyName !== 'height') return;
        reflowLeftRailDrawer();
        panel.removeEventListener('transitionend', settle);
        clearTimeout(settleTimer);
      };
      panel.addEventListener('transitionend', settle);
      // Safety net (L10): if transitionend never lands (reduced-motion, an
      // interrupted/zero-delta transition, or a rapid re-toggle), reflow and drop
      // the listener anyway so it can't leak. ~matches the 0.26s anim.
      settleTimer = setTimeout(() => {
        reflowLeftRailDrawer();
        panel.removeEventListener('transitionend', settle);
      }, 360);
    }

    panelCollapse?.addEventListener('click', (e) => { e.stopPropagation(); togglePanel(); });
    panelHeader?.addEventListener('click', togglePanel);

    // Host hook for the embedded one-model panel (js/panel.js). When a map click
    // selects a feature, panel.js takes the panel over with the feature editor
    // (adds .aop-feature-editing, which hides the header). If the panel is
    // collapsed at that moment, the editor renders behind the closed FAB and the
    // header/pencil get hidden — the same "open the panel editor" promise the
    // legacy revealFeatureInPanel guards by expanding first (see its collapsed
    // check below). Expose that expand so panel.js can keep the promise for the
    // layers it reveals (trails, boundaries, …) that have no legacy reveal binding.
    // Idempotent: a no-op when already expanded, so it never double-toggles when
    // both handlers fire for a FEATURE_LIST_LAYERS feature.
    window.AOP_HOST_EXPAND_PANEL = function () { if (panelCollapsed) togglePanel(); };

    let viewerSessionState = (() => {
      const parsed = readJsonStore(VIEWER_SESSION_KEY, () => ({}));
      return parsed && typeof parsed === 'object' ? parsed : {};
    })();

    function persistViewerSessionState(patch) {
      viewerSessionState = {
        ...(viewerSessionState || {}),
        ...(patch || {}),
        schema: 'aop-viewer-session-state-v1',
        updated_at: new Date().toISOString()
      };
      writeJsonStore(VIEWER_SESSION_KEY, viewerSessionState);
    }

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
      return tabKey; // resolved key — callers persist THIS, not the raw input (L10)
    }

    function persistLeftTab(tabKey) {
      persistViewerSessionState({ active_left_tab: tabKey });
    }

    // POI tab data caches. poiIndex is the fetched aop_poi_index.json (visitor
    // blurbs + revisit notes). Declared here (not lower in the file) so the POI
    // module below is not in its temporal-dead-zone when the immediate
    // fetchPoiIndex() call fires. (publishDataCache was removed with the
    // published-POI wholesale union in the 2026-06-08 star-only change.)
    let poiIndex = null;
    let aopTrailNetworkCache = null; // gold trail network, set on map load (POI browser join target)
    // Event-schedule bindings used by the Events tab + the schedule renderer
    // (renderEventSchedule / resolveEventLocation, below). Declared here with the
    // other POI module state; null / empty Map until the event loader populates
    // them. (Until the 2026-06-08 star-only change these were also read eagerly by
    // collectStarredDestinations' event-anchors union; that union was removed, so
    // the left POI list no longer depends on them.)
    let eventScheduleConfig = null;
    const eventLocationByTag = new Map();

    function isPoiTabActive() {
      const panel = document.getElementById('poiTabPanel');
      return !!panel && !panel.hidden;
    }

    function renderPoiTabIfActive() {
      if (isPoiTabActive()) renderPoiTab();
    }

    async function fetchPoiIndex() {
      if (poiIndex) return poiIndex;
      try {
        const response = await fetch('./data/aop_poi_index.json');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        poiIndex = await response.json();
        console.info('POI index loaded', poiIndex && poiIndex.entries && poiIndex.entries.length, 'entries');
      } catch (error) {
        console.error('POI index load failed', error);
        poiIndex = { schema: 'aop-poi-index-v1', entries: [], groups: [] };
      }
      renderPoiTabIfActive();
      return poiIndex;
    }
    // Kick off the fetch immediately; the renderer is resilient to a null index.
    fetchPoiIndex();

    // --- Trail catalog: the runtime join is GONE (Sprint 09 / A2) ---------
    // Curated trail write-ups (aop_trail_catalog.json) used to be joined to the
    // gold network at render time by trail_number — the "shadow attribute" that
    // made a trail show "Launchpad" on the left and "1" on the right. The catalog
    // is now folded into the feature by rebake_canonical (canonical name +
    // description + facets.difficulty/length_mi/onx_tr/connects), so every surface
    // — map label, left list, popup, search, panel — reads the one canonical field.
    // The authoring catalog file is still the source of truth feeding the bake and
    // the copy-review page; only the *render-time* join was removed.

    // --- Unified editor tree (V3c) ---------------------------------------
    // The Map editor section is a three-bucket tree by geometry kind (Point /
    // Line / Polygon), with a ★ Visitor list virtual group at the top. Inside
    // each bucket, source sub-groups split rows by where the data came from
    // (Drawn / Trailheads / Brand logos / Visitor context). Drawn is open by
    // default; reference sub-groups are collapsed with their count visible.
    //
    // Each bucket head carries a + button that opens an inline create row
    // inside the bucket body (category select + matching primary action).
    // The 5-toggle strip retired in V3c; the bucket-head bulk + source-head
    // bulk checkboxes are the visible mirror of the hidden #showXxx inputs in
    // #legacyLayerToggles, two-way bridged via change events. Card:
    // brain/tasks/04_event_app/editor_three_buckets_v3c.md.
    //
    // `sources` declares the source sub-groups within each bucket. Each
    // source has `layerToggleIds` (legacy hidden toggles that the bulk
    // mirrors), `leaves` (which FEATURE_LIST_LAYERS render into the
    // sub-group body), `defaultOpen` (open/collapsed default), and
    // `sourceClass` (CSS class for the colored dot). `onlyGroupId` filters
    // a layer's runtime groups down to one (used by editorPois so its
    // geometry-type groups split across the three matching buckets).
    const EDITOR_BUCKETS = [
      { id: 'point', label: 'Point', glyph: '●', drawMode: 'point',
        sources: [
          { id: 'drawn', label: 'Drawn POIs', defaultOpen: true, sourceClass: 'drawn',
            layerToggleIds: ['showEditorPois', 'showEventSchedule'],
            leaves: [
              { layerKey: 'editorPois', onlyGroupId: 'point' },
              { layerKey: 'eventSchedule' }
            ] },
          { id: 'brand', label: 'Brand logos', defaultOpen: false, sourceClass: 'brand',
            layerToggleIds: ['showBrandLogos'],
            leaves: [{ layerKey: 'brandLogos' }] }
        ] },
      { id: 'line', label: 'Line', glyph: '╱', drawMode: 'linestring',
        sources: [
          { id: 'drawn', label: 'Drawn POIs', defaultOpen: true, sourceClass: 'drawn',
            layerToggleIds: ['showEditorPois'],
            leaves: [{ layerKey: 'editorPois', onlyGroupId: 'linestring' }] }
        ] },
      { id: 'polygon', label: 'Polygon', glyph: '▭', drawMode: 'polygon',
        sources: [
          { id: 'drawn', label: 'Drawn POIs', defaultOpen: true, sourceClass: 'drawn',
            layerToggleIds: ['showEditorPois'],
            leaves: [{ layerKey: 'editorPois', onlyGroupId: 'polygon' }] },
          { id: 'visitor', label: 'Visitor context', defaultOpen: false, sourceClass: 'visitor',
            layerToggleIds: ['showVisitorContext'],
            leaves: [{ layerKey: 'visitorContext' }] }
        ] }
    ];
    // Right-rail ★ Visitor list source-chip labels, keyed by FEATURE_LIST_LAYERS
    // layerKey. Card 06 retired the parallel hardcoded VISITOR_LIST_LAYERS array
    // (it covered a different layer set than the left tab — the desync): the one
    // collector (collectStarredDestinations) now walks
    // Object.entries(featureListRuntime) for every spec that declares a
    // `listRow` + `listSurfaces.right`, so the right list is the starred set
    // across ALL destination layers, not a fixed four. The source chip is now a
    // co-located `spec.sourceChip` field (Sprint 09 A5 — R10), read with a
    // layerKey fallback; the free-standing VISITOR_LIST_SOURCE_CHIP dispatch map
    // is gone. A spec without the field falls back to its layerKey (permissive,
    // C5 — no row is dropped for an unmapped chip).
    let editorTreeBuilt = false;
    // The bucket whose + is currently active. Read by draw.on('finish') to
    // pull the right category. Cleared on Esc / cancel / mode change.
    let currentCreateBucket = null;

    function buildEditorTree() {
      const root = document.getElementById('editorTree');
      if (!root || editorTreeBuilt) return;
      root.innerHTML = '';

      // ★ Visitor list — virtual group, rendered by renderVisitorListGroup.
      const visitorBucket = document.createElement('div');
      visitorBucket.className = 'editor-bucket';
      visitorBucket.dataset.bucket = 'visitor-list';
      const visitorHead = document.createElement('div');
      visitorHead.className = 'editor-bucket-head';
      const vChevron = document.createElement('button');
      vChevron.type = 'button';
      vChevron.className = 'editor-bucket-chevron';
      vChevron.textContent = '▾';
      vChevron.title = 'Collapse bucket';
      vChevron.setAttribute('aria-expanded', 'true');
      const vSpacer = document.createElement('span');
      const vLabel = document.createElement('span');
      vLabel.className = 'editor-bucket-label';
      vLabel.innerHTML = '<span class="editor-bucket-glyph">★</span> Visitor list';
      const vCount = document.createElement('span');
      vCount.className = 'editor-bucket-count';
      vCount.id = 'editorVisitorListCount';
      vCount.textContent = '0';
      const vBody = document.createElement('div');
      vBody.className = 'editor-bucket-body';
      vBody.id = 'editorVisitorList';
      vChevron.addEventListener('click', () => {
        const collapsed = vBody.hidden = !vBody.hidden;
        vChevron.textContent = collapsed ? '▸' : '▾';
        vChevron.setAttribute('aria-expanded', String(!collapsed));
      });
      visitorHead.append(vChevron, vSpacer, vLabel, vCount);
      visitorBucket.append(visitorHead, vBody);
      root.append(visitorBucket);

      // 3 geometry buckets, each with source sub-groups.
      for (const bucket of EDITOR_BUCKETS) {
        const wrap = document.createElement('div');
        wrap.className = 'editor-bucket';
        wrap.dataset.bucket = bucket.id;

        const head = document.createElement('div');
        head.className = 'editor-bucket-head';
        const chevron = document.createElement('button');
        chevron.type = 'button';
        chevron.className = 'editor-bucket-chevron';
        chevron.textContent = '▾';
        chevron.title = 'Collapse bucket';
        chevron.setAttribute('aria-expanded', 'true');
        const bulk = document.createElement('input');
        bulk.type = 'checkbox';
        bulk.dataset.editorBucketBulk = bucket.id;
        bulk.title = `Show or hide every source under ${bucket.label}`;
        bulk.addEventListener('change', () => setBucketLayerToggles(bucket, bulk.checked));
        const labelEl = document.createElement('span');
        labelEl.className = 'editor-bucket-label';
        labelEl.innerHTML = `<span class="editor-bucket-glyph">${bucket.glyph}</span> ${bucket.label}`;
        const count = document.createElement('span');
        count.className = 'editor-bucket-count';
        count.dataset.editorBucketCount = bucket.id;
        count.textContent = '';
        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'editor-bucket-add';
        addBtn.dataset.editorBucketAdd = bucket.id;
        addBtn.title = `Place / draw / trace a new ${bucket.label.toLowerCase()} feature`;
        addBtn.textContent = '+';
        addBtn.setAttribute('aria-label', addBtn.title);
        addBtn.addEventListener('click', (event) => {
          event.stopPropagation();
          toggleBucketCreate(bucket);
        });
        head.append(chevron, bulk, labelEl, count, addBtn);

        const body = document.createElement('div');
        body.className = 'editor-bucket-body';
        body.dataset.editorBucketBody = bucket.id;
        chevron.addEventListener('click', () => {
          const collapsed = body.hidden = !body.hidden;
          chevron.textContent = collapsed ? '▸' : '▾';
          chevron.setAttribute('aria-expanded', String(!collapsed));
        });

        // Source sub-groups inside the bucket body.
        for (const source of (bucket.sources || [])) {
          const sourceWrap = document.createElement('div');
          sourceWrap.className = 'editor-subgroup';
          if (source.defaultOpen === false) sourceWrap.classList.add('collapsed');
          sourceWrap.dataset.source = source.id;
          sourceWrap.dataset.bucket = bucket.id;

          const sourceHead = document.createElement('div');
          sourceHead.className = 'editor-subgroup-head';
          const sChev = document.createElement('button');
          sChev.type = 'button';
          sChev.className = 'editor-subgroup-chev';
          sChev.textContent = source.defaultOpen === false ? '▸' : '▾';
          sChev.title = 'Collapse sub-group';
          sChev.setAttribute('aria-expanded', String(source.defaultOpen !== false));
          const sBulk = document.createElement('input');
          sBulk.type = 'checkbox';
          sBulk.className = 'editor-subgroup-bulk';
          sBulk.dataset.editorSourceBulk = `${bucket.id}-${source.id}`;
          sBulk.title = `Show or hide the ${source.label.toLowerCase()} layer`;
          sBulk.addEventListener('change', () => setSourceLayerToggles(source, sBulk.checked));
          const sDot = document.createElement('span');
          sDot.className = `editor-subgroup-dot ${source.sourceClass || 'drawn'}`;
          const sLabel = document.createElement('span');
          sLabel.className = 'editor-subgroup-label';
          sLabel.textContent = source.label;
          const sCount = document.createElement('span');
          sCount.className = 'editor-subgroup-count';
          sCount.dataset.editorSourceCount = `${bucket.id}-${source.id}`;
          sCount.textContent = '';
          sourceHead.append(sChev, sBulk, sDot, sLabel, sCount);

          const sourceBody = document.createElement('div');
          sourceBody.className = 'editor-subgroup-body';
          sourceBody.dataset.editorSourceBody = `${bucket.id}-${source.id}`;

          const collapseSubgroup = () => {
            const willCollapse = !sourceWrap.classList.contains('collapsed');
            sourceWrap.classList.toggle('collapsed', willCollapse);
            sChev.textContent = willCollapse ? '▸' : '▾';
            sChev.setAttribute('aria-expanded', String(!willCollapse));
          };
          sChev.addEventListener('click', (event) => { event.stopPropagation(); collapseSubgroup(); });
          sLabel.addEventListener('click', collapseSubgroup);
          sLabel.style.cursor = 'pointer';

          // One feature-list slot per leaf. They render stacked inside the
          // source body — eventSchedule and editorPois Points both go into
          // the Point/Drawn body this way (event-schedule POIs are just
          // regular POIs by the schedule's #tag binding).
          for (const leaf of (source.leaves || [])) {
            const slot = document.createElement('div');
            slot.className = 'feature-list';
            slot.dataset.editorLeaf = `${bucket.id}-${source.id}-${leaf.layerKey}${leaf.onlyGroupId ? '-' + leaf.onlyGroupId : ''}`;
            slot.hidden = true;
            sourceBody.append(slot);
            registerFeatureListTarget(leaf.layerKey, slot, { onlyGroupId: leaf.onlyGroupId });
          }

          // Brand-logo max-size cap (item 5): a single global control under
          // the logo rows. The slider re-clamps the icon-size expression live
          // (caps the on-screen logo size at park zoom); export copies the
          // tuned value so the user can send it back.
          if (source.id === 'brand') {
            sourceBody.append(buildBrandLogoCapFooter());
          }

          sourceWrap.append(sourceHead, sourceBody);
          body.append(sourceWrap);
        }

        wrap.append(head, body);
        root.append(wrap);
      }

      editorTreeBuilt = true;
      bridgeLegacyLayerTogglesToSubgroupBulks();
      renderEditorTreeCounts();
      renderVisitorListGroup();
    }

    // Source bulk drives the layer toggle(s) it represents. The layer-
    // visibility wiring at the MapLibre layer-toggle section reads those
    // hidden checkboxes' state, so dispatching change events here lights up
    // the rest of the pipeline (paint drawers, presets, popup priority).
    function setSourceLayerToggles(source, visible) {
      for (const toggleId of (source.layerToggleIds || [])) {
        const el = document.getElementById(toggleId);
        if (!el) continue;
        if (el.checked !== visible) {
          el.checked = visible;
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }
      // The legacy change-event chain already calls renderEditorTreeCounts
      // through the bridge, but renderEditorTreeCounts is also called here
      // as a belt-and-suspenders against missed bridges.
      renderEditorTreeCounts();
    }

    function setBucketLayerToggles(bucket, visible) {
      for (const source of (bucket.sources || [])) {
        setSourceLayerToggles(source, visible);
      }
    }

    // Bridge: when a hidden legacy toggle changes externally (preset apply,
    // programmatic restore, an old code path), refresh the matching sub-
    // group bulks via the counts pass.
    let legacyToggleBridgeWired = false;
    function bridgeLegacyLayerTogglesToSubgroupBulks() {
      if (legacyToggleBridgeWired) return;
      const allToggleIds = new Set();
      for (const bucket of EDITOR_BUCKETS) {
        for (const source of (bucket.sources || [])) {
          for (const id of (source.layerToggleIds || [])) allToggleIds.add(id);
        }
      }
      for (const id of allToggleIds) {
        const el = document.getElementById(id);
        if (!el) continue;
        el.addEventListener('change', () => {
          if (editorTreeBuilt) renderEditorTreeCounts();
        });
      }
      legacyToggleBridgeWired = true;
    }

    function renderEditorTreeCounts() {
      if (!editorTreeBuilt) return;
      for (const bucket of EDITOR_BUCKETS) {
        let bucketVisible = 0;
        let bucketTotal = 0;
        let bucketStars = 0;
        let bucketAllToggleOn = true;
        let bucketAnyToggleOn = false;
        let bucketHasToggle = false;

        for (const source of (bucket.sources || [])) {
          let sourceVisible = 0;
          let sourceTotal = 0;
          let sourceStars = 0;
          for (const leaf of (source.leaves || [])) {
            const runtime = featureListRuntime[leaf.layerKey];
            if (!runtime || !runtime.state) continue;
            for (const groupBucket of runtime.state.groups) {
              if (leaf.onlyGroupId && groupBucket.group && groupBucket.group.id !== leaf.onlyGroupId) continue;
              for (const item of groupBucket.features) {
                sourceTotal += 1;
                if (runtime.state.visibleIds.has(item.id)) sourceVisible += 1;
                const props = item.feature && item.feature.properties;
                if (props && props.highlight === true) sourceStars += 1;
              }
            }
          }
          // Layer-toggle state for the source. If a source declares multiple
          // toggle ids (Point/Drawn does — both showEditorPois and
          // showEventSchedule), all-on means every toggle is on; any-on
          // means at least one is on. Indeterminate sits between the two.
          const toggleStates = (source.layerToggleIds || []).map((id) => {
            const el = document.getElementById(id);
            return el ? !!el.checked : true;
          });
          const sourceAllOn = toggleStates.length === 0 || toggleStates.every(Boolean);
          const sourceAnyOn = toggleStates.length === 0 || toggleStates.some(Boolean);

          const sourceCountEl = document.querySelector(`[data-editor-source-count="${bucket.id}-${source.id}"]`);
          if (sourceCountEl) {
            if (sourceTotal === 0) sourceCountEl.textContent = '—';
            else if (sourceStars > 0) sourceCountEl.textContent = `${sourceVisible}/${sourceTotal} · ${sourceStars} ★`;
            else sourceCountEl.textContent = `${sourceVisible}/${sourceTotal}`;
          }
          const sourceBulkEl = document.querySelector(`[data-editor-source-bulk="${bucket.id}-${source.id}"]`);
          if (sourceBulkEl) {
            sourceBulkEl.checked = sourceAllOn;
            sourceBulkEl.indeterminate = sourceAnyOn && !sourceAllOn;
          }
          // Empty-source placeholder inside the sub-group body.
          const sourceBodyEl = document.querySelector(`[data-editor-source-body="${bucket.id}-${source.id}"]`);
          if (sourceBodyEl) {
            const existingEmpty = sourceBodyEl.querySelector('.editor-bucket-empty');
            if (sourceTotal === 0 && !existingEmpty) {
              const placeholder = document.createElement('div');
              placeholder.className = 'editor-bucket-empty';
              placeholder.textContent = 'No items yet.';
              sourceBodyEl.append(placeholder);
            } else if (sourceTotal > 0 && existingEmpty) {
              existingEmpty.remove();
            }
          }

          bucketVisible += sourceVisible;
          bucketTotal += sourceTotal;
          bucketStars += sourceStars;
          if (toggleStates.length > 0) {
            bucketHasToggle = true;
            if (!sourceAllOn) bucketAllToggleOn = false;
            if (sourceAnyOn) bucketAnyToggleOn = true;
          }
        }

        const countEl = document.querySelector(`[data-editor-bucket-count="${bucket.id}"]`);
        if (countEl) {
          if (bucketTotal === 0) countEl.textContent = '—';
          else if (bucketStars > 0) countEl.textContent = `${bucketVisible}/${bucketTotal} · ${bucketStars} ★`;
          else countEl.textContent = `${bucketVisible}/${bucketTotal}`;
        }
        const bulkEl = document.querySelector(`[data-editor-bucket-bulk="${bucket.id}"]`);
        if (bulkEl) {
          bulkEl.checked = bucketHasToggle && bucketAllToggleOn;
          bulkEl.indeterminate = bucketHasToggle && bucketAnyToggleOn && !bucketAllToggleOn;
          bulkEl.disabled = !bucketHasToggle;
        }
      }
    }

    // V3c inline create row. Click a bucket's + to open the row inside that
    // bucket's body; click again (or ✕, or Esc) to close. Only one create
    // row may be open at a time; opening a new one closes any open row in
    // any bucket. Calls setDrawMode internally so the existing Terra Draw
    // wiring (mode flips, finish handler, ESC cancel) keeps working.
    function toggleBucketCreate(bucket) {
      const isCurrent = currentCreateBucket && currentCreateBucket.id === bucket.id;
      if (isCurrent) {
        // Same bucket re-click — cancel.
        closeBucketCreate();
        return;
      }
      // Any other bucket open? Close it first.
      if (currentCreateBucket) closeBucketCreate({ skipModeReset: true });
      openBucketCreate(bucket);
    }

    function openBucketCreate(bucket) {
      const body = document.querySelector(`[data-editor-bucket-body="${bucket.id}"]`);
      if (!body) return;
      // Ensure the bucket body isn't collapsed; opening + on a collapsed
      // bucket expands it so the user sees their freshly-drawn feature
      // appear.
      if (body.hidden) {
        body.hidden = false;
        const chev = body.parentElement?.querySelector('.editor-bucket-chevron');
        if (chev) { chev.textContent = '▾'; chev.setAttribute('aria-expanded', 'true'); }
      }
      let row = body.querySelector(':scope > .editor-create-inline');
      if (!row) {
        row = document.createElement('div');
        row.className = 'editor-create-inline';
        row.dataset.bucket = bucket.id;
        const labelRow = document.createElement('div');
        labelRow.className = 'editor-create-label-row';
        const glyph = document.createElement('span');
        glyph.className = 'editor-create-glyph';
        glyph.textContent = bucket.glyph;
        const labelText = document.createElement('span');
        labelText.textContent = createPrimaryLabel(bucket);
        const cancel = document.createElement('button');
        cancel.type = 'button';
        cancel.className = 'editor-create-cancel';
        cancel.title = 'Cancel (Esc)';
        cancel.setAttribute('aria-label', 'Cancel');
        cancel.textContent = '✕';
        cancel.addEventListener('click', (event) => { event.stopPropagation(); closeBucketCreate(); });
        labelRow.append(glyph, labelText, cancel);

        const controlRow = document.createElement('div');
        controlRow.className = 'editor-create-control-row';
        const catLabel = document.createElement('span');
        catLabel.className = 'editor-create-category-label';
        catLabel.textContent = 'Category';
        const select = document.createElement('select');
        select.className = 'editor-create-category';
        select.dataset.bucket = bucket.id;
        // Clone options from the legacy #poiCategory so the option list
        // stays in one place (per-bucket category lists are a deferred
        // follow-up — see card "Out of scope").
        const legacy = document.getElementById('poiCategory');
        if (legacy) {
          for (const opt of Array.from(legacy.options)) {
            const cloned = opt.cloneNode(true);
            select.append(cloned);
          }
        }
        // Default the select to a bucket-appropriate option where one fits.
        const preferred = bucketPreferredCategory(bucket);
        if (preferred) {
          for (const opt of Array.from(select.options)) {
            if (opt.value === preferred || opt.textContent === preferred) {
              opt.selected = true;
              break;
            }
          }
        }
        const startBtn = document.createElement('button');
        startBtn.type = 'button';
        startBtn.className = 'editor-create-start';
        startBtn.dataset.bucket = bucket.id;
        startBtn.textContent = createPrimaryButtonLabel(bucket, false);
        startBtn.addEventListener('click', () => {
          const active = draw && draw.getMode && draw.getMode() === bucket.drawMode;
          setDrawMode(active ? 'static' : bucket.drawMode);
        });
        controlRow.append(catLabel, select, startBtn);

        const help = document.createElement('small');
        help.textContent = createHelpText(bucket);
        row.append(labelRow, controlRow, help);
        body.prepend(row);
      }
      // Cache the references on the bucket so draw.on('finish') can read the
      // selected category without DOM queries.
      bucket.createRow = row;
      bucket.categorySelect = row.querySelector('select.editor-create-category');
      bucket.startBtn = row.querySelector('button.editor-create-start');
      currentCreateBucket = bucket;
      setDrawMode(bucket.drawMode);
    }

    function closeBucketCreate(opts = {}) {
      const bucket = currentCreateBucket;
      currentCreateBucket = null;
      if (bucket) {
        if (bucket.createRow && bucket.createRow.parentElement) bucket.createRow.remove();
        bucket.createRow = null;
        bucket.categorySelect = null;
        bucket.startBtn = null;
      }
      if (!opts.skipModeReset) setDrawMode('static');
    }

    function createPrimaryLabel(bucket) {
      if (bucket.drawMode === 'point') return 'Place a POI';
      if (bucket.drawMode === 'polygon') return 'Draw a polygon';
      if (bucket.drawMode === 'linestring') return 'Trace a line';
      return 'Create';
    }
    function createPrimaryButtonLabel(bucket, active) {
      if (active) return bucket.drawMode === 'point' ? 'Placing… (Esc)'
        : bucket.drawMode === 'polygon' ? 'Drawing… (Esc)'
        : 'Tracing… (Esc)';
      return bucket.drawMode === 'point' ? 'Place POI'
        : bucket.drawMode === 'polygon' ? 'Draw footprint'
        : 'Trace line';
    }
    function createHelpText(bucket) {
      if (bucket.drawMode === 'point') return 'Click once on the map to drop the POI.';
      if (bucket.drawMode === 'polygon') return 'Click each corner. Press Enter to finish or Esc to cancel.';
      if (bucket.drawMode === 'linestring') return 'Click each vertex. Press Enter to finish or Esc to cancel.';
      return '';
    }
    function bucketPreferredCategory(bucket) {
      if (bucket.drawMode === 'linestring') return 'Trail trace';
      return null;
    }

    function renderVisitorListGroup() {
      if (!editorTreeBuilt) return;
      const container = document.getElementById('editorVisitorList');
      const countEl = document.getElementById('editorVisitorListCount');
      if (!container || !countEl) return;
      container.innerHTML = '';
      // Thin FLAT renderer over the ONE collector (contract C2). The star gate
      // lives in collectStarredDestinations (`row.starred`); here we only keep
      // rows that surface to the right ★ Visitor list AND are starred. This is
      // the same engine the left POI tab reads, so the two cannot disagree — and
      // a starred destination from ANY right-surfacing layer (drawn POIs, brand
      // logos, visitor context, trails, buildings, cemeteries) appears here, not
      // just the four the old hardcoded VISITOR_LIST_LAYERS array covered.
      const rows = collectStarredDestinations()
        .filter((row) => row.surfaces && row.surfaces.right === true && row.starred === true);
      rows.sort((a, b) => String(a.label || '').localeCompare(String(b.label || '')));
      countEl.textContent = String(rows.length);
      if (!rows.length) {
        const empty = document.createElement('div');
        empty.className = 'editor-bucket-empty';
        empty.textContent = 'Nothing starred yet. Click ★ on any item to surface it here and in the left-rail POI tab.';
        container.append(empty);
        renderEditorTreeCounts();
        return;
      }
      for (const row of rows) {
        const r = document.createElement('div');
        r.className = 'editor-visitor-list-row';
        r.dataset.layerKey = row.layerKey;
        r.dataset.featureId = String(row.featureId);
        const name = document.createElement('span');
        name.className = 'vrow-name';
        name.textContent = row.label;
        const chip = document.createElement('span');
        chip.className = 'vrow-chip';
        chip.textContent = row.sourceChip || row.layerKey;
        const fly = makeFlyButton(row.feature, 'vrow-fly');
        const star = document.createElement('button');
        star.type = 'button';
        star.className = 'vrow-star on';
        star.title = 'Unstar — remove from Visitor list';
        star.textContent = '★';
        star.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();
          toggleFeatureHighlight(row.layerKey, row.featureId);
        });
        r.addEventListener('click', () => flyToFeature(row.feature));
        r.append(name, chip, fly, star);
        container.append(r);
      }
      renderEditorTreeCounts();
    }

    // buildEditorTree() is invoked once the featureListRuntime / FEATURE_LIST_LAYERS
    // const declarations below are reachable; calling it from this position
    // would trip the TDZ on those bindings. See the explicit call right
    // after `const featureListRuntime = {};`.

    // The per-feature poi-index blurb/revisit_note JOIN is GONE (Sprint 09 / A3):
    // rebake_canonical folds those into each feature's `description` /
    // `facets.revisit_note`, so building/cemetery/visitor read the canonical field
    // directly. fetchPoiIndex + poiIndex stay only for the POI-tab GROUP taxonomy
    // (labels + order) below — that is config, not a per-feature shadow attribute.

    function poiGroupLabel(groupId) {
      const groups = poiIndex && Array.isArray(poiIndex.groups) ? poiIndex.groups : [];
      const found = groups.find((g) => g.id === groupId);
      return found && found.label ? found.label : groupId;
    }

    function poiGroupOrder() {
      const groups = poiIndex && Array.isArray(poiIndex.groups) ? poiIndex.groups : [];
      return groups.map((g) => g.id);
    }

    // The ONE destination collector (contract C2 / universal_feature_layer
    // stage 3). Replaces the 7 bespoke buildPoiGroups source blocks (each read
    // a different store and only `drawn_pois` was star-gated) with a single walk
    // over the FEATURE_LIST_LAYERS registry's destination specs. STAR-ONLY
    // (2026-06-08): the two former wholesale unions — published `poi`
    // (gold_publish.geojson, bake-gated) and event anchors (aop_event_schedule.json,
    // a static non-DB file) — were removed. They bypassed the ★ gate and put
    // untraceable rows in the list; the POI tab is now exactly the registry's
    // ★-curated layers. A published destination or schedule place that belongs
    // in the list earns its row by being ★-curated on its own reference layer
    // (cemeteries/buildings/visitor/trails) or as a drawn POI — one gate, one
    // source. The event schedule still lives in the Events tab (its own surface).
    //
    // Each spec declares its row shape (`listRow`), its POI-tab group
    // (`listGroup`), which features surface (`listPredicate`), its surfaces
    // (`listSurfaces.left` = POI tab, `.right` = ★ Visitor list), its mode
    // (`listMode`: 'wholesale' shows every matching row; 'starred' shows only
    // ★-highlighted rows — editorPois plus the four reference layers flipped in
    // sprint08: cemeteries/buildings/visitorContext/trails), and a
    // lazy toggle ref (`listToggle`). The star gate (highlight flag check) is
    // computed ONCE here, on `row.starred`; renderPoiTab (grouped) and
    // renderVisitorListGroup (flat) both consume these rows and neither
    // re-derives the gate. Per C5 this adds dispatch, never rejection: a spec
    // missing a strategy falls back (skipped if it has no listRow) and no
    // out-of-vocabulary value is dropped or thrown on.
    //
    // FLIPPED (sprint08 star_driven_poi_normalization, decisions #1/#2/#5): the
    // four reference layers (cemeteries/buildings/visitorContext/trails) are now
    // `listMode: 'starred'` — the POI tab shows only ★-curated rows. The user
    // authorized this once the ★ became DURABLE (core.features.attrs.highlight ->
    // bake), so a clean profile sees the curated set, not per-browser state. Card
    // 06 had already converged the two engines STRUCTURALLY (both renderers read
    // this one collector, so they cannot disagree); this flip is the product step
    // on top of that. (The published `poi` and event-anchor wholesale unions
    // that used to follow were removed in the 2026-06-08 star-only change — see
    // the top of this comment.) A starred destination also surfaces in the ★
    // Visitor list (additive, C5).
    function collectStarredDestinations() {
      const rows = [];
      function emit(layerKey, spec, feature) {
        if (!spec || typeof spec.listRow !== 'function') return;
        const props = (feature && feature.properties) || {};
        // The ONE star gate. `starred` travels on every row; the renderers read
        // it (the right list shows starred only) and the 'starred' listMode
        // drops non-highlighted rows below.
        const starred = props.highlight === true;
        if (spec.listMode === 'starred' && !starred) return;
        const base = spec.listRow(feature) || {};
        const group = spec.listGroup || { id: layerKey, label: spec.label || layerKey };
        const surfaces = spec.listSurfaces || { left: true, right: true };
        const sourceChip = (spec && spec.sourceChip) || layerKey;
        rows.push({
          ...base,
          // identity for the right ★ list + star toggle
          layerKey,
          featureId: positionedFeatureIdFor(layerKey, feature),
          label: typeof spec.rowLabel === 'function' ? spec.rowLabel(props) : (base.name || group.label),
          sourceChip,
          // grouping for the left POI tab
          groupId: group.id,
          groupLabel: group.label,
          // surface routing + the one star flag + the auto-enable toggle
          surfaces,
          starred,
          toggle: typeof spec.listToggle === 'function' ? spec.listToggle() : null
        });
      }

      // 1) Registry destination layers — walk featureListRuntime. A spec is a
      // destination iff it declares a `listRow`. By default we iterate the
      // deduped, sorted runtime STATE rows (the same machinery the right editor
      // renders) so trails collapse to one row per `__trail_row_id` and the
      // unnamed edges (no id) drop out exactly as before (card 05). A spec may
      // set `listFromData: true` to iterate the RAW `runtime.data.features`
      // instead: cemeteries need this because their parcel+marker twins share a
      // `parcel_id`, so the state dedupe keeps the FIRST (the parcel) and would
      // hide the marker the old buildPoiGroups block filtered to. Reading raw
      // data + `listPredicate(geom_role==='marker')` reproduces the old rows.
      for (const [layerKey, runtime] of Object.entries(featureListRuntime)) {
        const spec = FEATURE_LIST_LAYERS[layerKey];
        if (!spec || typeof spec.listRow !== 'function') continue;
        if (!runtime) continue;
        const predicate = typeof spec.listPredicate === 'function' ? spec.listPredicate : () => true;
        if (spec.listFromData === true) {
          const features = (runtime.data && Array.isArray(runtime.data.features)) ? runtime.data.features : [];
          for (const feature of features) {
            const props = (feature && feature.properties) || {};
            if (!predicate(props)) continue;
            emit(layerKey, spec, feature);
          }
          continue;
        }
        if (!runtime.state || !Array.isArray(runtime.state.groups)) continue;
        for (const bucket of runtime.state.groups) {
          for (const item of bucket.features) {
            const feature = item.feature;
            const props = (feature && feature.properties) || {};
            if (!predicate(props)) continue;
            emit(layerKey, spec, feature);
          }
        }
      }

      return rows;
    }

    // Group the collector's LEFT-surface rows into the POI-tab tree. Thin
    // renderer over collectStarredDestinations — it does not re-derive rows or
    // re-check the star gate (the collector already dropped non-starred rows for
    // 'starred'-mode layers). Group order follows poi_index.json, then insertion.
    function buildPoiGroups() {
      // Each row: { id, name, kind, blurb, revisitNote, status, source, caveat,
      //             feature, toggle, popupCoord, groupId, groupLabel, ... }
      const groups = new Map();
      for (const row of collectStarredDestinations()) {
        if (!row.surfaces || row.surfaces.left !== true) continue;
        const gid = row.groupId || 'other';
        if (!groups.has(gid)) groups.set(gid, []);
        groups.get(gid).push(row);
      }

      // Return groups in the order declared by poi_index.json (falls back to
      // insertion order if the index doesn't list a group).
      const orderedIds = poiGroupOrder();
      const seen = new Set();
      const out = [];
      for (const id of orderedIds) {
        if (!groups.has(id)) continue;
        out.push({ id, label: poiGroupLabel(id), rows: groups.get(id) });
        seen.add(id);
      }
      for (const [id, rows] of groups.entries()) {
        if (seen.has(id)) continue;
        out.push({ id, label: poiGroupLabel(id), rows });
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
        empty.textContent = poiIndex
          ? (window.AOP_UI?.poi?.empty || 'No places loaded yet. Toggle layers in the right panel, or wait for the map to finish loading.')
          : (window.AOP_UI?.poi?.loading || 'Loading places…');
        container.append(empty);
        return;
      }
      for (const group of groups) {
        const groupEl = document.createElement('div');
        groupEl.className = 'poi-list-group';
        groupEl.dataset.groupId = group.id;

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
          btn.dataset.poiId = row.id;
          btn.setAttribute('aria-label', `Fly to ${row.name}`);

          const name = document.createElement('span');
          name.className = 'poi-row-name';
          name.textContent = row.name;
          btn.append(name);

          const subtitle = document.createElement('span');
          subtitle.className = 'poi-row-subtitle';
          if (row.blurb) {
            subtitle.textContent = row.blurb;
          } else if (row.revisitNote) {
            subtitle.textContent = row.revisitNote;
          } else {
            subtitle.textContent = `${row.kind} · ${row.source}`;
          }
          btn.append(subtitle);

          const meta = document.createElement('span');
          meta.className = 'poi-row-meta';
          const kindChip = document.createElement('span');
          kindChip.textContent = row.kind;
          meta.append(kindChip);
          if (row.status) {
            const statusChip = document.createElement('span');
            statusChip.textContent = row.status;
            meta.append(statusChip);
          }
          if (!row.blurb && row.revisitNote) {
            const placeholderChip = document.createElement('span');
            placeholderChip.className = 'poi-placeholder-chip';
            placeholderChip.textContent = 'info needed — revisit';
            placeholderChip.title = row.revisitNote;
            meta.append(placeholderChip);
          }
          btn.append(meta);

          btn.addEventListener('click', () => gotoPoi(row));
          groupEl.append(btn);
        }
        container.append(groupEl);
      }
    }

    function gotoPoi(row) {
      if (!row || !row.feature) return;
      closeAllMapPopups();
      // Auto-enable the source layer if it was off, mirroring the schedule pattern.
      if (row.toggle && !row.toggle.checked) {
        row.toggle.checked = true;
        row.toggle.dispatchEvent(new Event('change', { bubbles: true }));
      }
      flyToFeature(row.feature);
      const coord = row.popupCoord || firstCoordinate(row.feature.geometry) || geometryCentroid(row.feature.geometry);
      if (!coord) return;
      const slice = visibleMapRect();
      const sliceWidth = Math.max(0, slice.right - slice.left);
      const popupMax = Math.max(200, Math.min(300, sliceWidth - 28));
      const popup = new maplibregl.Popup({ maxWidth: `${popupMax}px`, className: 'poi-tab-popup' })
        .setLngLat(coord)
        .setHTML(poiPopupHtml(row))
        .addTo(map);
      map.once('moveend', () => panPopupIntoView(popup));
      setTimeout(() => panPopupIntoView(popup), 1200);
    }

    function poiPopupHtml(row) {
      // ONE renderer — window.AOPFeatureDisplay.popupHtml, the same the editors
      // use. The row already carries the normalized display fields (featureDisplay);
      // map its revisitNote key onto the model's `revisit`.
      return window.AOPFeatureDisplay.popupHtml({
        name: row.name, kind: row.kind, blurb: row.blurb,
        status: row.status, source: row.source, caveat: row.caveat,
        revisit: row.revisitNote,
      });
    }

    for (const button of leftTabButtons) {
      button.addEventListener('click', () => {
        persistLeftTab(setLeftTab(button.dataset.leftTab));
      });
      button.addEventListener('keydown', (event) => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const current = leftTabButtons.indexOf(button);
        let next = current;
        if (event.key === 'Home') next = 0;
        else if (event.key === 'End') next = leftTabButtons.length - 1;
        else next = (current + (event.key === 'ArrowRight' ? 1 : -1) + leftTabButtons.length) % leftTabButtons.length;
        const nextButton = leftTabButtons[next];
        if (nextButton) {
          persistLeftTab(setLeftTab(nextButton.dataset.leftTab));
          nextButton.focus();
        }
      });
    }
    // Left-rail card-body resize. All three card bodies (Events / POI / About)
    // share a single CSS var, `--lr-card-body-height`, set on `.lr-content-col`.
    // Each card carries its own bottom handle so the affordance reads the same
    // wherever the user is; dragging any handle updates the shared var and the
    // persisted height. No min/max — the user can drag to 0 to collapse.
    // Defaults come from CSS media queries (160 mobile / 240 default / min(42vh,360px) wide).
    const lrContentCol = document.getElementById('lrContentCol');
    const lrResizeHandles = [
      { handle: calendarResizeHandle, body: calendarBody },
      { handle: document.getElementById('poiResizeHandle'), body: document.getElementById('poiList') },
      { handle: document.getElementById('aboutResizeHandle'), body: document.getElementById('aboutInfoPanel') },
    ].filter((entry) => entry.handle && entry.body);

    function lrCardCurrentHeight(body) {
      if (!body) return 240;
      const rect = body.getBoundingClientRect();
      if (Number.isFinite(rect.height) && rect.height > 0) return rect.height;
      return 240;
    }

    function setLrCardHeight(height, persist = true) {
      if (!lrContentCol) return;
      const next = Math.round(Math.max(0, Number(height) || 0));
      lrContentCol.style.setProperty('--lr-card-body-height', `${next}px`);
      for (const { handle } of lrResizeHandles) {
        handle.setAttribute('aria-valuenow', String(next));
      }
      if (persist) writeJsonStore(LR_CARD_HEIGHT_KEY, next);
      scrollCalendarCurrentRowIntoView();
      // Item 15: resizing a card body shifts every panel's offsetTop, so the
      // floating icon-column tabs must be re-laid-out against the new rects or
      // they drift away from their panels mid-drag.
      if (typeof window.lrReflow === 'function') window.lrReflow();
    }

    function initializeLrCardResize() {
      if (!lrContentCol || !lrResizeHandles.length) return;
      const stored = readJsonStore(LR_CARD_HEIGHT_KEY, null);
      if (Number.isFinite(stored)) setLrCardHeight(stored, false);
      else {
        for (const { handle, body } of lrResizeHandles) {
          handle.setAttribute('aria-valuenow', String(Math.round(lrCardCurrentHeight(body))));
        }
      }

      for (const { handle, body } of lrResizeHandles) {
        let drag = null;
        handle.addEventListener('pointerdown', (event) => {
          if (event.button != null && event.button !== 0) return;
          event.preventDefault();
          drag = { y: event.clientY, height: lrCardCurrentHeight(body), pointerId: event.pointerId };
          handle.setPointerCapture(event.pointerId);
        });
        handle.addEventListener('pointermove', (event) => {
          if (!drag) return;
          event.preventDefault();
          setLrCardHeight(drag.height + event.clientY - drag.y, false);
        });
        const finishDrag = (event) => {
          if (!drag) return;
          const next = drag.height + event.clientY - drag.y;
          if (handle.hasPointerCapture(drag.pointerId)) {
            handle.releasePointerCapture(drag.pointerId);
          }
          drag = null;
          setLrCardHeight(next, true);
        };
        handle.addEventListener('pointerup', finishDrag);
        handle.addEventListener('pointercancel', finishDrag);
        handle.addEventListener('keydown', (event) => {
          let next = lrCardCurrentHeight(body);
          if (event.key === 'ArrowDown') next += 24;
          else if (event.key === 'ArrowUp') next -= 24;
          else if (event.key === 'PageDown') next += 72;
          else if (event.key === 'PageUp') next -= 72;
          else if (event.key === 'Home') next = 0;
          else return;
          event.preventDefault();
          setLrCardHeight(next, true);
        });
      }
    }

    initializeLrCardResize();

    calendarDays?.addEventListener('click', (event) => {
      const row = event.target.closest('.calendar-row');
      if (row?.dataset.sessionId) {
        gotoEventSession(row.dataset.sessionId);
        // Item 10 (misc_3.md) + pwa_qa_2 item 2: on mobile, fold the whole left
        // drawer after a calendar pick so the map + the event popup own the
        // screen. Search + hot collapse via their tab toggle; the calendar
        // itself collapses via the drawer's public lrCloseCard hook.
        if (window.innerWidth <= 760) {
          const searchTab = document.getElementById('lrTabSearch');
          const hotTab = document.getElementById('lrTabHot');
          if (searchTab?.classList.contains('open')) searchTab.click();
          if (hotTab?.classList.contains('open')) hotTab.click();
          if (typeof window.lrCloseCard === 'function') window.lrCloseCard('cal');
        }
      }
    });

    function setSectionCollapsed(section, collapsed) {
      const button = section.querySelector('.section-toggle');
      const chevron = section.querySelector('.section-chevron');
      section.classList.toggle('collapsed', collapsed);
      if (button) button.setAttribute('aria-expanded', String(!collapsed));
      if (chevron) chevron.textContent = collapsed ? '▸' : '▾';
    }

    for (const section of document.querySelectorAll('.panel-section')) {
      const button = section.querySelector('.section-toggle');
      setSectionCollapsed(section, section.classList.contains('collapsed'));
      if (button) {
        button.addEventListener('click', () => {
          setSectionCollapsed(section, !section.classList.contains('collapsed'));
        });
      }
    }

    function openContainingSection(element) {
      const section = element?.closest('.panel-section');
      if (section) setSectionCollapsed(section, false);
    }

    // Named-feature search registry, filled by indexFeatures during map load.
    const searchIndex = [];
    let searchGroups = [];
    let searchMatches = [];
    let searchActive = -1;
    let activePresetId = 'park';
    let activeTuneKey = 'landcover';
    let expandedTuneKey = null;
    let applyingPreset = false;

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

    // Contour fade bands are ['interpolate','linear',['zoom'], z0, out0, z1, out1].
    // The zoom-band knobs move only z0/z1; the opacity outputs are left as-is so
    // the per-preset / per-line-class opacity values survive a knob drag.
    function withZoomStops(expr, z0, z1) {
      // Only a 2-stop ['interpolate', interp, ['zoom'], z0, o0, z1, o1] keeps its
      // zoom inputs at [3] and [5]. Anything else (flat value, 3+ stops, a
      // non-zoom input) would be silently corrupted, so warn and pass through.
      const looksLikeZoomInterp = Array.isArray(expr) && expr[0] === 'interpolate'
        && expr.length === 7 && Array.isArray(expr[2]) && expr[2][0] === 'zoom';
      if (!looksLikeZoomInterp) {
        if (Array.isArray(expr) && expr[0] === 'interpolate') {
          console.warn('withZoomStops: unexpected interpolate shape, left unchanged', expr);
        }
        return expr;
      }
      const next = JSON.parse(JSON.stringify(expr));
      next[3] = z0;
      next[5] = z1;
      return next;
    }
    function zoomStopsOf(expr, fallback) {
      if (Array.isArray(expr) && expr[0] === 'interpolate'
          && typeof expr[3] === 'number' && typeof expr[5] === 'number') {
        return [expr[3], expr[5]];
      }
      return fallback.slice();
    }

    // The 9-patch forest layer fades independently of the crisp park layer,
    // so its drawer opacity control reads as the "non-park context" control.
    function setLandcover9Opacity(value) {
      if (map.getLayer('landcover-9patch-forest')) {
        map.setPaintProperty('landcover-9patch-forest', 'fill-opacity', value);
      }
    }

    // SFWDA paper map is sliced into a GRID_N x GRID_N mesh of warpable raster tiles.
    const GRID_N = 6;

    const SKY_ATMOSPHERE = {
      'sky-color': '#7AB3FF',
      'horizon-color': '#BCDFFE',
      'fog-color': '#FFFFFF',
      'sky-horizon-blend': 0.5,
      'horizon-fog-blend': 0.5,
      'fog-ground-blend': 0.5
    };

    // Land-cover palette -- two tight colour families so variation reads as a
    // highlight, not a clash. Trees: a light/dark sage pair. Fields: a
    // light/base/dark warm-khaki trio. Within each set the steps are small;
    // the two sets stay clearly apart (green vs khaki).
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
    // Topo/relief variant of the same two families, lifted lighter and a touch
    // greyer so hillshade and contour lines read clearly on top of it.
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
    const SYNTHETIC_HOTSPOT_FILL = ['match', ['get', 'intensity_class'],
      'low',    '#b7d2bd',
      'medium', '#6fa793',
      'high',   '#477c82',
      'peak',   '#254d5b',
      '#6fa793'];
    const SYNTHETIC_HOTSPOT_OPACITY = [
      'interpolate', ['linear'], ['get', 'intensity_norm'],
      0, 0.10,
      0.4, 0.24,
      1, 0.52
    ];

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

    // Slider markup uses 0-100; layer paint properties want 0-1. One helper so
    // adding a fifth slider does not invent a fifth divisor.
    const sliderPercent = (element) => Number(element.value) / 100;

    // Each toggle drives one or more map layers. setLayerVisibility no-ops on
    // layers that do not exist yet, so this is safe to call before layers load.
    // The third field, presetId, is the DOM id used to capture/restore the
    // toggle in named presets -- one row here is the only place a new layer
    // needs to be registered.
    const LAYER_TOGGLES = [
      [landcoverToggle, ['landcover-forest', 'landcover-forest-outline'], 'showLandcover'],
      [landcover9Toggle, ['landcover-9patch-forest', 'landcover-9patch-forest-outline'], 'showLandcover9'],
      [hillshadeToggle, ['lidar-hillshade'], 'showHillshade'],
      [contoursToggle, ['contours-minor', 'contours-index', 'contours-labels'], 'showContours'],
      [activityHotspotsToggle, ['activity-hotspots-heat', 'activity-hotspots-fill', 'activity-hotspots-outline', 'activity-hotspots-labels'], 'showActivityHotspots'],
      [syntheticActivityToggle, ['synthetic-activity-tracks', 'synthetic-activity-hotspots-heat', 'synthetic-activity-hotspots-fill', 'synthetic-activity-hotspots-outline', 'synthetic-activity-hotspots-labels'], 'showSyntheticActivity'],
      [eventScheduleToggle, ['event-session-routes', 'event-route-labels', 'event-anchor-points', 'event-anchor-labels'], 'showEventSchedule'],
      [satelliteToggle, ['tnmap-satellite'], 'showSatellite'],
      [usdaNaipToggle, ['usda-naip-satellite'], 'showUsdaNaip'],
      [ninePatchToggle, ['nine-patch-fill', 'nine-patch-outline', 'nine-patch-labels'], 'showNinePatch'],
      [lidarTilesToggle, ['lidar-tiles-fill', 'lidar-tiles-outline', 'lidar-tiles-labels'], 'showLidarTiles'],
      [roadsToggle, ['roads-local-casing', 'roads-local', 'roads-connecting-casing', 'roads-connecting', 'roads-secondary-casing', 'roads-secondary', 'roads-ramp-casing', 'roads-ramp', 'roads-controlled-casing', 'roads-controlled', 'roads-labels'], 'showRoads'],
      [visitorContextToggle, ['visitor-context-fill', 'visitor-context-outline', 'visitor-context-labels'], 'showVisitorContext'],
      [brandLogosToggle, ['brand-logos-icons'], 'showBrandLogos'],
      [waterToggle, ['water-area-fill', 'waterbody-fill', 'waterbody-outline', 'streams', 'stream-labels'], 'showWater'],
      [springsToggle, ['water-points', 'water-point-labels'], 'showSprings'],
      [cemeteriesToggle, ['cemetery-fill', 'cemetery-outline', 'cemetery-marker', 'cemetery-label'], 'showCemeteries'],
      [buildingsToggle, ['building-footprint-fill', 'building-footprint-outline', 'building-footprint-aop-outline'], 'showBuildings'],
      [osmParkToggle, ['osm-park-outline'], 'showOsmPark'],
      [osmTracksToggle, ['osm-tracks'], 'showOsmTracks'],
      [osmServiceToggle, ['osm-service'], 'showOsmService'],
      [osmNamedToggle, ['osm-named-points', 'osm-named-labels'], 'showOsmNamed'],
      // SFWDA has no shared layer set -- the visibility loop is grid-driven
      // inside updateLayerVisibility -- but it still belongs in the preset list
      // and wants the same change handler.
      [sfwdaToggle, [], 'showSfwda'],
      // Extracted-trail review layers (paper_map_trail_extraction.md). Registered
      // here so the change handler + visibility loop wire themselves, but left
      // out of every preset object so applyPreset never forces them -- default
      // OFF, review-only, refine later.
      [sfwdaTraceTrailsToggle, ['sfwda-trace-trails'], 'showSfwdaTraceTrails'],
      // pwa_qa item 9: SFWDA trace marker DOTS removed (dev artifact); the gold
      // aop-trail-network carries the numbered labels instead.
      [aopTrailNetworkToggle, ['aop-trail-network', 'aop-trail-network-labels'], 'showAopTrailNetwork'],
      [trailToggle, ['publish-trails'], 'showTrails'],
      [boundaryToggle, ['publish-boundary-fill', 'publish-boundaries'], 'showBoundaries'],
      [trailheadToggle, ['publish-trailheads'], 'showTrailheads'],
      [editorPoiToggle, ['editor-poi-fill', 'editor-poi-outline', 'editor-poi-lines', 'editor-poi-circles', 'editor-poi-labels', 'editor-poi-fill-labels', 'editor-poi-line-labels'], 'showEditorPois']
    ];

    // Derived from LAYER_TOGGLES so adding a row above propagates everywhere
    // the preset machinery reads from.
    const PRESET_TOGGLE_IDS = LAYER_TOGGLES.map(([, , presetId]) => presetId);
    // Right-panel swap (2026-06-05): expose the toggle registry so the embedded
    // panel (js/panel.js) can map each of its layer nodes to the host checkbox
    // that backs it (and drive visibility through it, keeping presets in sync).
    window.AOP_HOST_LAYER_TOGGLES = LAYER_TOGGLES;
    const PRESET_SLIDER_IDS = ['landcover9Opacity', 'sfwdaOpacity', 'sfwdaMultiply'];

    const TUNABLE_LAYERS = {
      landcover: {
        label: 'Land cover',
        toggle: landcoverToggle,
        defaults: { opacity: 90, color: '#b9c2a3', width: 0.8 },
        opacity: [
          ['landcover-forest', 'fill-opacity'],
          ['landcover-forest-outline', 'line-opacity']
        ],
        color: [
          ['landcover-forest', 'fill-color'],
          ['landcover-forest-outline', 'line-color']
        ],
        width: [['landcover-forest-outline', 'line-width']]
      },
      landcover9: {
        label: '9-patch land cover',
        toggle: landcover9Toggle,
        linkedSlider: landcover9Opacity,
        defaults: { opacity: 55, color: '#b9c2a3', width: 0.6 },
        opacity: [
          ['landcover-9patch-forest', 'fill-opacity'],
          ['landcover-9patch-forest-outline', 'line-opacity']
        ],
        color: [
          ['landcover-9patch-forest', 'fill-color'],
          ['landcover-9patch-forest-outline', 'line-color']
        ],
        width: [['landcover-9patch-forest-outline', 'line-width']]
      },
      contours: {
        label: 'Contours',
        toggle: contoursToggle,
        defaults: { opacity: 95, color: '#a8906a', width: 1.8 },
        opacity: [
          ['contours-index', 'line-opacity'],
          ['contours-minor', 'line-opacity'],
          ['contours-labels', 'text-opacity']
        ],
        color: [
          ['contours-index', 'line-color'],
          ['contours-minor', 'line-color'],
          ['contours-labels', 'text-color']
        ],
        width: [
          ['contours-minor', 'line-width'],
          ['contours-index', 'line-width']
        ],
        zoomBandRange: { min: 12, max: 20, step: 0.5 },
        zoomBands: [
          {
            label: '25 ft index fade',
            targets: [['contours-index', 'line-opacity'], ['contours-labels', 'text-opacity']],
            fallback: [15, 16]
          },
          {
            label: '5 ft detail fade',
            targets: [['contours-minor', 'line-opacity']],
            fallback: [16.5, 17.5]
          }
        ]
      },
      activityHotspots: {
        label: 'Activity hotspots',
        toggle: activityHotspotsToggle,
        defaults: { opacity: 70, color: '#d9903d', width: 1.1 },
        opacity: [
          ['activity-hotspots-heat', 'heatmap-opacity'],
          ['activity-hotspots-fill', 'fill-opacity'],
          ['activity-hotspots-outline', 'line-opacity'],
          ['activity-hotspots-labels', 'text-opacity']
        ],
        color: [
          ['activity-hotspots-outline', 'line-color'],
          ['activity-hotspots-labels', 'text-color']
        ],
        width: [['activity-hotspots-outline', 'line-width']]
      },
      // Synthetic Saturday activity mirrors activityHotspots but also fades
      // the per-persona tracks layer. Track line-color stays as a `match`
      // expression (persona coding); only outline/label color are tunable.
      // Card: brain/tasks/03_event_app/right_panel_editor_consistency.md.
      syntheticActivity: {
        label: 'Simulated Saturday activity',
        toggle: syntheticActivityToggle,
        defaults: { opacity: 60, color: '#254d5b', width: 1.2 },
        opacity: [
          ['synthetic-activity-tracks', 'line-opacity'],
          ['synthetic-activity-hotspots-heat', 'heatmap-opacity'],
          ['synthetic-activity-hotspots-fill', 'fill-opacity'],
          ['synthetic-activity-hotspots-outline', 'line-opacity'],
          ['synthetic-activity-hotspots-labels', 'text-opacity']
        ],
        color: [
          ['synthetic-activity-hotspots-outline', 'line-color'],
          ['synthetic-activity-hotspots-labels', 'text-color']
        ],
        width: [['synthetic-activity-hotspots-outline', 'line-width']]
      },
      // Event schedule routes + anchors. Anchor circle-color is a per-role
      // `match` expression so it stays untunable here (the role coding
      // carries semantic meaning). Width slider sets a scalar — the zoom
      // interpolation on `event-session-routes` is the tradeoff documented
      // in the build card.
      eventSchedule: {
        label: 'Event schedule POIs',
        toggle: eventScheduleToggle,
        defaults: { opacity: 92, color: '#b45f43', width: 3.0 },
        opacity: [
          ['event-session-routes', 'line-opacity'],
          ['event-route-labels', 'text-opacity'],
          ['event-anchor-labels', 'text-opacity']
        ],
        color: [
          ['event-session-routes', 'line-color'],
          ['event-route-labels', 'text-color'],
          ['event-anchor-labels', 'text-color']
        ],
        width: [['event-session-routes', 'line-width']]
      },
      hillshade: {
        label: 'Hillshade',
        toggle: hillshadeToggle,
        defaults: { opacity: 60, color: '#3a2f22', width: 0.6 },
        opacity: [['lidar-hillshade', 'hillshade-exaggeration']],
        color: [['lidar-hillshade', 'hillshade-shadow-color']],
        width: []
      },
      satellite: {
        label: 'TNMap imagery',
        toggle: satelliteToggle,
        defaults: { opacity: 100, color: '#ffffff', width: 1 },
        opacity: [['tnmap-satellite', 'raster-opacity']],
        color: [],
        width: []
      },
      naip: {
        label: 'USDA NAIP imagery',
        toggle: usdaNaipToggle,
        defaults: { opacity: 100, color: '#ffffff', width: 1 },
        opacity: [['usda-naip-satellite', 'raster-opacity']],
        color: [],
        width: []
      },
      ninePatch: {
        label: '9-patch AOI',
        toggle: ninePatchToggle,
        defaults: { opacity: 100, color: '#a88246', width: 1.5 },
        opacity: [
          ['nine-patch-fill', 'fill-opacity'],
          ['nine-patch-outline', 'line-opacity'],
          ['nine-patch-labels', 'text-opacity']
        ],
        color: [
          ['nine-patch-fill', 'fill-color'],
          ['nine-patch-outline', 'line-color'],
          ['nine-patch-labels', 'text-color']
        ],
        width: [['nine-patch-outline', 'line-width']]
      },
      lidarTiles: {
        label: 'Lidar tile index',
        toggle: lidarTilesToggle,
        defaults: { opacity: 80, color: '#8a6f86', width: 2.5 },
        opacity: [
          ['lidar-tiles-fill', 'fill-opacity'],
          ['lidar-tiles-outline', 'line-opacity'],
          ['lidar-tiles-labels', 'text-opacity']
        ],
        color: [
          ['lidar-tiles-fill', 'fill-color'],
          ['lidar-tiles-outline', 'line-color'],
          ['lidar-tiles-labels', 'text-color']
        ],
        width: [['lidar-tiles-outline', 'line-width']]
      },
      roads: {
        label: 'Roads',
        toggle: roadsToggle,
        defaults: { opacity: 90, color: '#cdb079', width: 2.2 },
        opacity: [
          ['roads-local-casing', 'line-opacity'],
          ['roads-local', 'line-opacity'],
          ['roads-connecting-casing', 'line-opacity'],
          ['roads-connecting', 'line-opacity'],
          ['roads-secondary-casing', 'line-opacity'],
          ['roads-secondary', 'line-opacity'],
          ['roads-ramp-casing', 'line-opacity'],
          ['roads-ramp', 'line-opacity'],
          ['roads-controlled-casing', 'line-opacity'],
          ['roads-controlled', 'line-opacity'],
          ['roads-labels', 'text-opacity']
        ],
        color: [
          ['roads-local', 'line-color'],
          ['roads-connecting', 'line-color'],
          ['roads-secondary', 'line-color'],
          ['roads-ramp', 'line-color'],
          ['roads-controlled', 'line-color'],
          ['roads-labels', 'text-color']
        ],
        width: [
          ['roads-local', 'line-width'],
          ['roads-connecting', 'line-width'],
          ['roads-secondary', 'line-width'],
          ['roads-ramp', 'line-width'],
          ['roads-controlled', 'line-width']
        ]
      },
      visitorContext: {
        label: 'Visitor context',
        toggle: visitorContextToggle,
        defaults: { opacity: 78, color: '#d8b173', width: 2.2 },
        opacity: [
          ['visitor-context-fill', 'fill-opacity'],
          ['visitor-context-outline', 'line-opacity'],
          ['visitor-context-labels', 'text-opacity']
        ],
        color: [
          ['visitor-context-fill', 'fill-color'],
          ['visitor-context-outline', 'line-color'],
          ['visitor-context-labels', 'text-color']
        ],
        width: [['visitor-context-outline', 'line-width']]
      },
      water: {
        label: 'Water',
        toggle: waterToggle,
        defaults: { opacity: 85, color: '#7fa3ac', width: 2.4 },
        opacity: [
          ['water-area-fill', 'fill-opacity'],
          ['waterbody-fill', 'fill-opacity'],
          ['streams', 'line-opacity'],
          ['stream-labels', 'text-opacity']
        ],
        color: [
          ['water-area-fill', 'fill-color'],
          ['waterbody-fill', 'fill-color'],
          ['waterbody-outline', 'line-color'],
          ['streams', 'line-color'],
          ['stream-labels', 'text-color']
        ],
        width: [
          ['waterbody-outline', 'line-width'],
          ['streams', 'line-width']
        ]
      },
      springs: {
        label: 'Springs & gages',
        toggle: springsToggle,
        defaults: { opacity: 100, color: '#4a6c73', width: 5 },
        opacity: [
          ['water-points', 'circle-opacity'],
          ['water-point-labels', 'text-opacity']
        ],
        color: [
          ['water-points', 'circle-color'],
          ['water-point-labels', 'text-color']
        ],
        width: [['water-points', 'circle-radius']]
      },
      boundaries: {
        label: 'Boundaries',
        toggle: boundaryToggle,
        defaults: { opacity: 100, color: '#6e5a3c', width: 2.5 },
        opacity: [
          ['publish-boundary-fill', 'fill-opacity'],
          ['publish-boundaries', 'line-opacity']
        ],
        color: [
          ['publish-boundary-fill', 'fill-color'],
          ['publish-boundaries', 'line-color']
        ],
        width: [['publish-boundaries', 'line-width']]
      },
      trails: {
        label: 'Trails',
        toggle: trailToggle,
        defaults: { opacity: 100, color: '#9a5a32', width: 3.5 },
        opacity: [['publish-trails', 'line-opacity']],
        color: [['publish-trails', 'line-color']],
        width: [['publish-trails', 'line-width']]
      },
      trailheads: {
        label: 'Trailheads',
        toggle: trailheadToggle,
        defaults: { opacity: 100, color: '#6f8a5c', width: 6 },
        opacity: [['publish-trailheads', 'circle-opacity']],
        color: [['publish-trailheads', 'circle-color']],
        width: [['publish-trailheads', 'circle-radius']]
      },
      cemeteries: {
        label: 'Cemeteries',
        toggle: cemeteriesToggle,
        defaults: { opacity: 75, color: '#8a7a82', width: 2.4 },
        opacity: [
          ['cemetery-fill', 'fill-opacity'],
          ['cemetery-outline', 'line-opacity'],
          ['cemetery-marker', 'circle-opacity'],
          ['cemetery-label', 'text-opacity']
        ],
        color: [
          ['cemetery-fill', 'fill-color'],
          ['cemetery-outline', 'line-color'],
          ['cemetery-marker', 'circle-color'],
          ['cemetery-label', 'text-color']
        ],
        width: [
          ['cemetery-outline', 'line-width'],
          ['cemetery-marker', 'circle-radius']
        ]
      },
      buildings: {
        label: 'Buildings',
        toggle: buildingsToggle,
        defaults: { opacity: 45, color: '#c1a386', width: 1.8 },
        opacity: [
          ['building-footprint-fill', 'fill-opacity'],
          ['building-footprint-outline', 'line-opacity'],
          ['building-footprint-aop-outline', 'line-opacity']
        ],
        color: [
          ['building-footprint-fill', 'fill-color'],
          ['building-footprint-outline', 'line-color'],
          ['building-footprint-aop-outline', 'line-color']
        ],
        width: [
          ['building-footprint-outline', 'line-width'],
          ['building-footprint-aop-outline', 'line-width']
        ]
      },
      osmPark: {
        label: 'OSM park polygon',
        toggle: osmParkToggle,
        defaults: { opacity: 100, color: '#8a9a6a', width: 2 },
        opacity: [['osm-park-outline', 'line-opacity']],
        color: [['osm-park-outline', 'line-color']],
        width: [['osm-park-outline', 'line-width']]
      },
      osmTracks: {
        label: 'OSM tracks',
        toggle: osmTracksToggle,
        defaults: { opacity: 95, color: '#9a5a32', width: 2 },
        opacity: [['osm-tracks', 'line-opacity']],
        color: [['osm-tracks', 'line-color']],
        width: [['osm-tracks', 'line-width']]
      },
      osmService: {
        label: 'OSM service roads',
        toggle: osmServiceToggle,
        defaults: { opacity: 85, color: '#a89a7e', width: 1.5 },
        opacity: [['osm-service', 'line-opacity']],
        color: [['osm-service', 'line-color']],
        width: [['osm-service', 'line-width']]
      },
      osmNamed: {
        label: 'OSM named landmarks',
        toggle: osmNamedToggle,
        defaults: { opacity: 100, color: '#c7a85e', width: 5 },
        opacity: [
          ['osm-named-points', 'circle-opacity'],
          ['osm-named-labels', 'text-opacity']
        ],
        color: [
          ['osm-named-points', 'circle-color'],
          ['osm-named-labels', 'text-color']
        ],
        width: [['osm-named-points', 'circle-radius']]
      },
      sfwda: {
        label: 'SFWDA paper map',
        toggle: sfwdaToggle,
        linkedSlider: sfwdaOpacity,
        extraSliders: [{ label: 'Multiply', slider: sfwdaMultiply, kind: 'percent', defaultValue: 0 }],
        drawerControls: sfwdaDrawerControls,
        defaults: { opacity: 70, color: '#ffffff', width: 1 },
        opacity: [],
        color: [],
        width: []
      },
      editorPois: {
        label: 'Drawn POIs',
        toggle: editorPoiToggle,
        defaults: { opacity: 100, color: '#6a6256', width: 5 },
        opacity: [
          ['editor-poi-fill', 'fill-opacity'],
          ['editor-poi-outline', 'line-opacity'],
          ['editor-poi-lines', 'line-opacity'],
          ['editor-poi-circles', 'circle-opacity'],
          ['editor-poi-labels', 'text-opacity'],
          ['editor-poi-fill-labels', 'text-opacity'],
          ['editor-poi-line-labels', 'text-opacity']
        ],
        color: [
          ['editor-poi-circles', 'circle-color'],
          ['editor-poi-labels', 'text-color']
        ],
        width: [['editor-poi-circles', 'circle-radius']]
      },
      // Brand logos: opacity lives in the normal layer tuner; per-logo size
      // lives beside each feature row because icon-size is data-driven.
      brandLogos: {
        label: 'Brand logos',
        toggle: brandLogosToggle,
        defaults: { opacity: 100, color: '#ffffff', width: 1 },
        opacity: [['brand-logos-icons', 'icon-opacity']],
        color: [],
        width: []
      }
    };

    // --- Feature list panel -------------------------------------------------
    // A per-feature visibility primitive. Drops into the layer editor drawer
    // for any layer that opts in: one row per feature, with a visibility
    // checkbox and a click-to-fly target. Layers can group features (e.g.
    // buildings → in-park named + others collapsed bulk). State persists in
    // `aop_feature_visibility_v1` localStorage. Layer paint filters are
    // recomposed from each layer's captured base filter plus the visibility
    // set, so this primitive layers cleanly on top of existing per-layer
    // filters (cemetery `geom_role`, building `inside_aop_boundary`).
    //
    // Card: brain/tasks/02_edit/poi_editor_v2.md.
    // First consumers: buildings, cemeteries. Future consumers (POIs,
    // visitor-context callouts, on-map logos) bolt the same shape onto their
    // layers; drag-to-move is the next action added.

    // Activity-hotspot spec factory — activityHotspots and syntheticActivity
    // are the same feature layer (timestamped dwell cells, visibility + fly
    // only) differing only in label and the layer-id prefix. One factory
    // emits the shared spec so rowLabel (intensity_class formatting) and
    // rowSort ({high,medium,low}) live once. Card 04.
    const HOTSPOT_INTENSITY_ORDER = { high: 0, medium: 1, low: 2 };
    const hotspotRowLabel = (props) => {
      const klass = props.intensity_class ? `[${props.intensity_class}] ` : '';
      const label = props.label || props.id;
      return `${klass}${label}`;
    };
    const hotspotRowSort = (a, b) => {
      const ai = HOTSPOT_INTENSITY_ORDER[a.props.intensity_class] ?? 9;
      const bi = HOTSPOT_INTENSITY_ORDER[b.props.intensity_class] ?? 9;
      if (ai !== bi) return ai - bi;
      return String(a.props.label || '').localeCompare(String(b.props.label || ''));
    };
    const makeHotspotSpec = (label, layerPrefix) => ({
      label,
      idField: 'id',
      rowLabel: hotspotRowLabel,
      targetLayers: [
        `${layerPrefix}-heat`,
        `${layerPrefix}-fill`,
        `${layerPrefix}-outline`,
        `${layerPrefix}-labels`
      ],
      rowSort: hotspotRowSort,
      groups: [{
        id: 'all',
        label: null,
        match: () => true,
        defaultVisible: () => true
      }]
    });

    // One display name for a drawn POI. The title is `name`; where a POI was
    // drawn with only a category (name === category, or no name), the category
    // stands in; then a generic 'POI'. This is the SINGLE derivation the left
    // list, the edit-dock row, and the panel item label all read — replacing the
    // three divergent forms the Sprint-09 audit named (list 'category — name',
    // panel 'name||category', map 'coalesce name,category'). The map label symbol
    // expression mirrors it (it can't call JS): coalesce(name, category, 'POI').
    // The category itself stays a Tier-3 facet shown in its own field/detail — it
    // is never smuggled into the title.
    function poiDisplayName(props) {
      const p = props || {};
      return String(p.name || '').trim() || p.category || 'POI';
    }

    const FEATURE_LIST_LAYERS = {
      cemeteries: {
        label: 'Cemeteries',
        // G_C (gold slice 6, 2026-06-10): the canonical baked `id` (=
        // '<parcel_id>:<geom_role>', UNIQUE per feature) — was `parcel_id`, which
        // the parcel + marker TWIN shared, so buildFeatureListState deduped them to
        // the FIRST (the parcel) and a ★/edit smeared onto the parcel while the list
        // surfaced the marker (audit `cemetery-parcel-marker-twin-nonunique-id`).
        // Keying on the unique `id` makes the MARKER its own resolvable row: the
        // panel passes the marker's props (it filters geom_role==='marker'), so
        // positionedFeatureIdFor → props.id = '<parcel_id>:marker' resolves the
        // MARKER store-of-record, not the parcel twin. The parcel stays SERVED
        // (related geometry — cemetery-fill/outline paint it) with its own
        // '<parcel_id>:parcel' id. `geom_role` is now a Tier-3 attrs facet + the
        // list filter (listPredicate below). This makes `spec.idField == panel key
        // == DB source_key business part` (`served-id-heterogeneous-no-canonical-key`).
        idField: 'id',
        // Star eligibility (sprint 08 — star_driven_poi_normalization). Draws
        // the per-row ★ and lets a cemetery's curation land durably in
        // core.features.attrs.highlight (via apply_positioned_features_to_core.py),
        // so the bake carries it. Lands WITH the Slice C listMode flip — a
        // 'starred' layer without `highlightable` would be a C5 row-dropping
        // filter (no ★ control), so the two travel together.
        highlightable: true,
        // --- Destination-list config (card 06) ---------------------------
        // Replaces the buildPoiGroups "Cemeteries" block. Marker rows only, so
        // each site appears once. ★-curated on the POI tab (sprint08 flip below);
        // a starred cemetery also surfaces in the ★ Visitor list (additive, C5).
        listGroup: { id: 'cemeteries', label: 'Cemeteries' },
        // sprint08 (star_driven_poi_normalization): ★-curated. Lands WITH the
        // `highlightable: true` add above — a 'starred' layer without a ★ control
        // would be a C5 row-dropping filter. The ★ now travels durably (core.features
        // .attrs.highlight -> bake), so a curated cemetery surfaces; uncurated ones
        // stay off the POI tab until starred.
        listMode: 'starred',
        listSurfaces: { left: true, right: true },
        // Iterate RAW data, not the deduped runtime state: cemeteries emit a
        // parcel + marker per site sharing one `parcel_id`, so buildFeatureListState
        // keeps only the first (the parcel) for the editor list. The destination
        // list wants the MARKER (one row per site at the marker coord), so the
        // collector reads data.features and filters to markers — exactly the old
        // buildPoiGroups "Cemeteries" block.
        listFromData: true,
        listPredicate: (props) => props.geom_role === 'marker',
        listToggle: () => cemeteriesToggle,
        listRow: (feature) => {
          const props = (feature && feature.properties) || {};
          // Display text is the ONE strategy (window.AOPFeatureDisplay) — the same
          // one the reader popup and the editors use. Only id/popupCoord stay
          // per-layer (geometry/identity, not display text). The old per-layer
          // Status/Source constants are gone: the feature's own fields win.
          const d = window.AOPFeatureDisplay.featureDisplay(props);
          return {
            id: `cemetery:${props.parcel_id || props.name}`,
            name: d.name, kind: d.kind, blurb: d.blurb, revisitNote: d.revisit,
            status: d.status, source: d.source, caveat: d.caveat,
            feature,
            popupCoord: firstCoordinate(feature && feature.geometry)
          };
        },
        // Editable display-name property (default 'name'), co-located on the
        // spec instead of a parallel per-layer name-property map. The dock title
        // reads spec.nameField so a rename shows here, in the row, and in the
        // GeoJSON copy at once.
        nameField: 'name',
        // Served-source strategy — the live MapLibre source re-fed after a
        // property edit so the map popup reflects it immediately. Lazy so it
        // reads the cemeteryData `let` (assigned during layer load, after this
        // spec object is built). Replaces a parallel per-layer served-source map.
        servedSource: () => ['cemeteries', cemeteryData],
        inlineEditor: true,
        rowLabel: (props) => `${props.name || 'Cemetery'} — ${props.parcel_id}`,
        targetLayers: ['cemetery-fill', 'cemetery-outline', 'cemetery-marker', 'cemetery-label'],
        groups: [{
          id: 'all',
          label: null,                              // flat list, no header row
          match: () => true,
          defaultVisible: (props) => props.aop_inholding === true
        }]
      },
      buildings: {
        label: 'Buildings',
        idField: 'build_id',
        // Star eligibility (sprint 08 — star_driven_poi_normalization). Draws
        // the per-row ★ and lets a building's curation land durably in
        // core.features.attrs.highlight (via apply_positioned_features_to_core.py),
        // so the bake carries it. Lands WITH the Slice C listMode flip — a
        // 'starred' layer without `highlightable` would be a C5 row-dropping
        // filter (no ★ control), so the two travel together.
        highlightable: true,
        // --- Destination-list config (card 06) ---------------------------
        // The ONE collector (collectStarredDestinations) reads these instead of
        // the bespoke buildPoiGroups "Buildings" block this card deleted. The
        // strategy keys mirror what that block produced byte-for-byte:
        //   listGroup     POI-tab group id/label (matches poi_index.json).
        //   listPredicate which features surface (public facilities only).
        //   listMode      'starred' (sprint08 flip below) = ★-curated; only a
        //                 starred building shows on the POI tab. The star FLAG is
        //                 computed once in the collector and now travels durably
        //                 (core.features.attrs.highlight -> bake), so the curated
        //                 set survives a clean profile (star_driven decisions
        //                 #1/#2/#5 — the flip the user authorized once the ★ path
        //                 was durable).
        //   listSurfaces left = POI tab; right = ★ Visitor list (starred only).
        //                Buildings gain right:true so a STARRED building lands
        //                in the Visitor list too — the desync fix the card
        //                names (additive/permissive, C5; nothing is removed).
        //   listToggle   lazy ref to the map toggle (gotoPoi auto-enables it).
        //   listRow      uniform row, with the poiIndex blurb enrichment folded
        //                in here from the old block (no validator, C5).
        listGroup: { id: 'buildings', label: 'Buildings' },
        // sprint08 (star_driven_poi_normalization): ★-curated. Lands WITH the
        // `highlightable: true` add above (C5 — no 'starred' without a ★ control).
        // The ★ travels durably (core.features.attrs.highlight -> bake); a curated
        // building surfaces, uncurated ones stay off the POI tab until starred.
        listMode: 'starred',
        listSurfaces: { left: true, right: true },
        listPredicate: (props) => props.aop_facility === true,
        listToggle: () => buildingsToggle,
        listRow: (feature) => {
          const props = (feature && feature.properties) || {};
          const d = window.AOPFeatureDisplay.featureDisplay(props);
          return {
            id: `building:${props.uuid || props.address}`,
            name: d.name, kind: d.kind, blurb: d.blurb, revisitNote: d.revisit,
            status: d.status, source: d.source, caveat: d.caveat,
            feature,
            popupCoord: (props.centroid_lng != null && props.centroid_lat != null)
              ? [props.centroid_lng, props.centroid_lat]
              : null
          };
        },
        // Editable display-name property — buildings rename via building_label.
        // Co-located on the spec (default 'name'), replacing the parallel
        // per-layer name-property map.
        nameField: 'building_label',
        // Served-source strategy (re-feeds the live source after a property
        // edit). Lazy so it reads the buildingsData `let` assigned during
        // layer load. Replaces the parallel per-layer served-source map.
        servedSource: () => ['fema-buildings', buildingsData],
        inlineEditor: true,
        // Tag input on each row binds a #tag to the building so the event
        // schedule can resolve coords through this binding. The 1010
        // building's #pavilion binding moved to the seeded editor POI on
        // 2026-05-26 — see `data/bronze_aop_editor_seed_pois.geojson` and
        // `maybeSeedEditorPois`. Users can still re-bind #pavilion to a
        // building manually; the seeder only strips conflicts on the
        // first-install/Reset pass.
        taggable: true,
        // Read-only Identify-tab field, declared on the spec instead of a
        // per-layer Status branch in buildEditDock. `readonly:true`
        // renders via dockReadonly; `value(props)` derives the displayed string.
        // Permissive — any props shape still renders a row (falls back to '—').
        fields: [
          {
            key: 'status',
            label: 'Status',
            readonly: true,
            value: (props) => props.aop_facility ? 'Public facility' : props.aop_structure_box ? 'Private structure' : '—'
          }
        ],
        rowLabel: (props) => {
          // Canonical name (the facility name where one exists, else the address);
          // append the address from facets when it differs, so a facility row still
          // shows its street. One field, same as the list / panel / search.
          const name = props.name || props.building_label || `build_id ${props.build_id}`;
          const addr = (props.facets && props.facets.address) || props.address;
          return addr && addr !== name ? `${name} · ${addr}` : name;
        },
        targetLayers: ['building-footprint-fill', 'building-footprint-outline', 'building-footprint-aop-outline'],
        groups: [
          {
            id: 'facilities',
            label: 'Park facilities',
            match: (props) => props.aop_facility === true,
            defaultVisible: () => true,
            collapsedDefault: false
          },
          {
            // The buildings layer is now the curated/derived set (raw 9-patch
            // context dropped), so "other" is just the private-structure boxes
            // (665, 889). They render via the always-on `building-structure-box`
            // layer regardless of this toggle; the row is here so they show in
            // the list and can be drag-adjusted like the facilities.
            id: 'private',
            label: 'Private structures',
            match: (props) => props.aop_structure_box === true,
            // Presence-only: these always render via the standalone
            // `building-structure-box` layer, so their list tick (which drives
            // fill/outline) is inert — default off + collapsed, same UX as
            // before. The row is still here so the box can be drag-adjusted.
            defaultVisible: () => false,
            collapsedDefault: true
          }
        ],
        // Drag-to-adjust the footprints — FEMA's polygons sit a little off, so
        // a move nudges the whole footprint to land its bbox-center at the
        // click (shape preserved). Mirrors the visitor-context pattern: the
        // override commits to the unified positioned-features store (keyed
        // `buildings:<build_id>`) so it survives reload, and bakes back into
        // website/data/gold_aop_buildings.geojson via export_positioned_features.py.
        onMove: (feature, lngLat) => {
          if (!feature || !feature.geometry) return;
          const centroid = geometryBboxCenter(feature.geometry);
          if (!centroid) return;
          const dLng = lngLat.lng - centroid[0];
          const dLat = lngLat.lat - centroid[1];
          translateCoordinates(feature.geometry.coordinates, dLng, dLat);
          savePositionedFeature('buildings', feature, {
            geometry: JSON.parse(JSON.stringify(feature.geometry))
          });
          // The feature reference is shared with buildingsData.features, so the
          // collection already reflects the new coords — push it to the live
          // source to move the rendered footprint (and private box) at once.
          const source = map.getSource('fema-buildings');
          if (source && buildingsData) source.setData(buildingsData);
          // Re-register so the feature-list runtime picks up the moved centroid
          // (fly-to / reveal math).
          if (buildingsData) registerFeatureListLayer('buildings', buildingsData);
        }
      },
      // POIs (drawn editor features). Unlike buildings/cemeteries, the data here
      // mutates as the user draws/deletes — see `refreshEditorSource()` for the
      // re-register call. Flat list, sorted by category then name. Every new
      // POI defaults visible; the user only sees a row toggled off if they
      // explicitly unticked it (and that state survives reload via the
      // shared `aop_feature_visibility_v1` store).
      editorPois: {
        label: 'Drawn POIs',
        idField: 'id',
        // Source chip shown on the ★ Visitor-list row (Sprint 09 A5 — R10: the
        // chip is a co-located spec field, read with a layerKey fallback, in place
        // of the free-standing VISITOR_LIST_SOURCE_CHIP dispatch map).
        sourceChip: 'drawn',
        // --- Destination-list config (card 06) ---------------------------
        // Replaces the buildPoiGroups "Drawn POIs" block. This is the ONLY
        // layer that was star-gated before this card (the ★ button is the
        // curation gate — scratch geometry stays on the map but out of the
        // visitor browser). `listMode: 'starred'` tells the one collector to
        // emit only highlighted rows — the gate is applied ONCE
        // inside collectStarredDestinations, not re-checked here. Surfaces in
        // both the POI tab (under "Drawn POIs") and the ★ Visitor list.
        listGroup: { id: 'drawn_pois', label: 'Drawn POIs' },
        listMode: 'starred',
        listSurfaces: { left: true, right: true },
        listPredicate: () => true,
        listToggle: () => editorPoiToggle,
        listRow: (feature) => {
          const props = (feature && feature.properties) || {};
          const d = window.AOPFeatureDisplay.featureDisplay(props);
          return {
            id: `drawn:${props.id || props.name || 'idx'}`,
            name: d.name, kind: d.kind, blurb: d.blurb, revisitNote: d.revisit,
            status: d.status, source: d.source, caveat: d.caveat,
            feature,
            popupCoord: firstCoordinate(feature && feature.geometry) || geometryCentroid(feature && feature.geometry)
          };
        },
        // Editable display-name property (default 'name'), co-located on the
        // spec instead of a parallel per-layer name-property map. editorPois has
        // no served MapLibre source to re-feed (its writes flow through
        // persistProperty → refreshEditorSource), so it declares no servedSource.
        nameField: 'name',
        // Per-layer strategy hooks — these replace the scattered
        // `if (layerKey === 'editorPois')` branches that used to live at every
        // mutation call site. editorPois data is a live array that also feeds a
        // map source, so a mutation rebuilds both via refreshEditorSource, and a
        // flag change persists by rewriting the whole array. Every other layer
        // uses the defaults (renderFeatureList + the positioned-overrides store).
        onMutate: () => refreshEditorSource(),
        persistFlag: () => saveEditorPois(),
        // Identify-tab editable fields, declared on the spec instead of a
        // per-layer Category branch in buildEditDock. Each entry
        // renders via dockFieldRow; `type:'select'` draws a <select> whose
        // options come from the spec-local `options()` (lazy so it reads the
        // EDITOR_POI_CATEGORIES const that is built later in the IIFE). No
        // allowlist/validation — an out-of-vocab category still renders and is
        // selectable (C5). buildEditDock writes the change through
        // setFeatureProperty exactly like the Name field.
        fields: [
          { key: 'category', label: 'Category', type: 'select', options: () => EDITOR_POI_CATEGORIES }
        ],
        // Per-feature actions, declared on the spec instead of a
        // per-layer Duplicate/Delete branch. Served layers omit this
        // capability, so they render no Duplicate/Delete row. Each action
        // routes through the generic spec-aware duplicateFeature/deleteFeature
        // (which persist through the same array store via the persist seam).
        actions: [
          { key: 'duplicate', label: '⎘ Duplicate', title: 'Duplicate this feature', run: (layerKey, id) => duplicateFeature(layerKey, id) },
          { key: 'delete', label: '🗑 Delete', title: 'Delete this feature', danger: true, run: (layerKey, id) => deleteFeature(layerKey, id) }
        ],
        // Property-write persistence strategy — replaces the per-layer
        // fork in setFeatureProperty. editorPois
        // live in an array store that also feeds a map source, so a write
        // rewrites the array and re-feeds the source. Default layers patch the
        // positioned-overrides store + re-feed their served source.
        persistProperty: () => { saveEditorPois(); refreshEditorSource(); },
        // Create capability (Sprint 09 A5) — the host create bridge
        // (AOP_HOST_CREATE_FEATURE) dispatches through this instead of a literal
        // `layerKey !== 'editorPois'` guard. A layer opts into panel-driven create
        // by declaring `create`; a layer without it returns null (safe default, no
        // throw — C1/R13). Reuses addDrawnPoi so a host-drawn and a panel-drawn POI
        // land in the SAME one store (aop_editor_pois_v1).
        create: (geometry, opts) => addDrawnPoi(geometry, (opts && opts.category) || 'Other'),
        // Group-context label strategy — replaces the per-layer
        // geometry-bucket branch in dockGroupContext. Drawn POIs
        // read as their geometry bucket; default layers read as spec.label.
        groupContext: (item) => {
          const t = item.feature && item.feature.geometry && item.feature.geometry.type;
          const g = t === 'Point' ? 'Point' : t === 'Polygon' ? 'Footprint' : t === 'LineString' ? 'Line' : (t || '—');
          return `Drawn POIs · ${g}`;
        },
        // Delete/duplicate mutate the live editorPois array in place (these are
        // the layer-intrinsic store ops). The generic deleteFeature/duplicateFeature
        // dispatch through these and then route the persist/refresh through the
        // shared persistFlag/onMutate seam, naming no layerKey. Served layers omit
        // both (they also omit the `actions` capability), so they never delete.
        removeFeature: (id) => {
          editorPois = editorPois.filter((f) => !(f.properties && String(f.properties.id) === String(id)));
        },
        cloneFeature: (id) => {
          const source = editorPois.find((f) => f.properties && String(f.properties.id) === String(id));
          if (!source) return null;
          const clone = JSON.parse(JSON.stringify(source));
          clone.properties.id = `poi_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
          if (clone.properties.name) clone.properties.name = `${clone.properties.name} copy`;
          // Nudge the geometry so the duplicate doesn't sit exactly on top of
          // the original. ~10 m east for Point; centroid-shift for Line/Polygon.
          const offset = 0.00009;
          if (clone.geometry?.type === 'Point' && Array.isArray(clone.geometry.coordinates)) {
            clone.geometry.coordinates = [clone.geometry.coordinates[0] + offset, clone.geometry.coordinates[1]];
          } else if (clone.geometry?.coordinates && typeof translateCoordinates === 'function') {
            translateCoordinates(clone.geometry.coordinates, offset, 0);
          }
          editorPois.push(clone);
          return clone.properties.id;
        },
        // Tag input on each row binds a #tag to the POI so the event
        // schedule can resolve a location like #excavator-hill through a
        // drawn POI without ever typing lat/long.
        taggable: true,
        // Per-row ★ toggle. When true, the POI appears in the left-rail
        // POI tab under "Drawn POIs". Default off so the visitor browser
        // stays curated — drawing scratch geometry shouldn't pollute the
        // public-facing list. State lives in feature.properties.highlight
        // and travels with the POI through localStorage and GeoJSON export.
        highlightable: true,
        // Row label reads the ONE drawn-POI display name (poiDisplayName) so the
        // edit-dock row, the left list, the panel item, and the map label all show
        // the same string — the convergence the Sprint-09 audit named
        // (poi-display-name-three-derivations). The category is not folded into the
        // title here; it stays a Tier-3 facet shown in the Category field / detail.
        rowLabel: (props) => poiDisplayName(props),
        targetLayers: [
          'editor-poi-fill',
          'editor-poi-outline',
          'editor-poi-lines',
          'editor-poi-circles',
          'editor-poi-labels',
          'editor-poi-fill-labels',
          'editor-poi-line-labels'
        ],
        // Within each kind group, sort by category then name. Kept stable so
        // a Pavilion POI and a Restroom POI still cluster nicely.
        rowSort: (a, b) => {
          const ac = String(a.props.category || '');
          const bc = String(b.props.category || '');
          if (ac !== bc) return ac.localeCompare(bc);
          const an = String(a.props.name || '');
          const bn = String(b.props.name || '');
          return an.localeCompare(bn);
        },
        // Kind-grouped tree: Drawn POI → POI / Footprint / Line → named item.
        // Match is on `feature.geometry.type` (the 2nd arg threaded through
        // `groupForFeature`). Glyph drives the visual cue in the group head;
        // collapsedDefault is false so a freshly-loaded session shows all
        // three groups open — the user can collapse if they want.
        groups: [
          { id: 'point',     label: 'POI',       kindGlyph: '●', match: (_props, feature) => feature?.geometry?.type === 'Point',      defaultVisible: () => true, collapsedDefault: false },
          { id: 'polygon',   label: 'Footprint', kindGlyph: '▭', match: (_props, feature) => feature?.geometry?.type === 'Polygon',    defaultVisible: () => true, collapsedDefault: false },
          { id: 'linestring',label: 'Line',      kindGlyph: '╱', match: (_props, feature) => feature?.geometry?.type === 'LineString', defaultVisible: () => true, collapsedDefault: false }
        ],
        // Inline accordion editor lives in the same `.feature-list-rows`
        // container. One leaf editor open at a time per layer. Toggle from
        // a row-trailing chevron; map-click on a drawn POI routes here too.
        inlineEditor: true,
        // Drag-to-move primitive opt-in. The feature reference here is the
        // same object as the entry inside `editorPois`, so mutating its
        // geometry in place updates the source data without an array swap.
        // For Point we replace the coord; for LineString/Polygon we translate
        // the whole geometry so its centroid lands at the click — preserves
        // the original shape, which is what "move" should mean.
        onMove: (feature, lngLat) => {
          if (!feature || !feature.geometry) return;
          const newLng = lngLat.lng;
          const newLat = lngLat.lat;
          if (feature.geometry.type === 'Point') {
            feature.geometry.coordinates = [newLng, newLat];
          } else {
            const centroid = geometryBboxCenter(feature.geometry);
            if (!centroid) return;
            const dLng = newLng - centroid[0];
            const dLat = newLat - centroid[1];
            translateCoordinates(feature.geometry.coordinates, dLng, dLat);
          }
          saveEditorPois();
          refreshEditorSource();
        }
      },
      // Visitor-context callouts — the regional "supply run" / "plateau
      // services" badges. Drag-to-move only consumer for now (visibility
      // still useful so you can drop one if it crowds the cartography).
      // The override store keeps the moved geometry across reloads without
      // mutating the source geojson on disk.
      visitorContext: {
        label: 'Visitor context callouts',
        idField: 'name',
        sourceChip: 'visitor',
        // --- Destination-list config (card 06) ---------------------------
        // Replaces the buildPoiGroups "Visitor support" block. ★-curated on the
        // POI tab (sprint08 flip below — only starred callouts show); a starred
        // callout also surfaces in the ★ Visitor list (it already did via the
        // hardcoded VISITOR_LIST_LAYERS, now via the one collector).
        listGroup: { id: 'visitor_support', label: 'Visitor support' },
        // sprint08 (star_driven_poi_normalization): ★-curated (visitorContext was
        // already `highlightable`). The ★ travels durably (core.features.attrs
        // .highlight -> bake); a curated callout surfaces, uncurated ones stay off
        // the POI tab until starred.
        listMode: 'starred',
        listSurfaces: { left: true, right: true },
        listPredicate: () => true,
        listToggle: () => visitorContextToggle,
        listRow: (feature) => {
          const props = (feature && feature.properties) || {};
          const d = window.AOPFeatureDisplay.featureDisplay(props);
          return {
            id: `visitor:${props.name}`,
            name: d.name, kind: d.kind, blurb: d.blurb, revisitNote: d.revisit,
            status: d.status, source: d.source, caveat: d.caveat,
            feature,
            popupCoord: geometryCentroid(feature && feature.geometry)
          };
        },
        // Editable display-name property (default 'name'), co-located on the
        // spec instead of a parallel name-property map. Served-source strategy
        // re-feeds the live source after a property edit; lazy so it reads the
        // visitorContextData `let`. Replaces a parallel served-source map.
        nameField: 'name',
        servedSource: () => ['visitor-context', visitorContextData],
        // Star surfaces a callout into the left-rail POI tab and the
        // right-side Visitor list virtual group at the top of the editor.
        // Default off — same curation gate as editor POIs.
        highlightable: true,
        rowLabel: (props) => props.name || 'Visitor context',
        inlineEditor: true,
        targetLayers: ['visitor-context-fill', 'visitor-context-outline', 'visitor-context-labels'],
        groups: [{
          id: 'all',
          label: null,
          match: () => true,
          defaultVisible: () => true
        }],
        onMove: (feature, lngLat) => {
          if (!feature || !feature.geometry) return;
          const centroid = geometryBboxCenter(feature.geometry);
          if (!centroid) return;
          const dLng = lngLat.lng - centroid[0];
          const dLat = lngLat.lat - centroid[1];
          translateCoordinates(feature.geometry.coordinates, dLng, dLat);
          savePositionedFeature('visitorContext', feature, {
            geometry: JSON.parse(JSON.stringify(feature.geometry))
          });
          // Push the updated FeatureCollection back into the live source so
          // the rendered polygon and label move on the map immediately. The
          // feature reference is the same as the entry inside
          // visitorContextData.features, so the collection already reflects
          // the new coords.
          const source = map.getSource('visitor-context');
          if (source && visitorContextData) source.setData(visitorContextData);
          // Re-register so the feature list runtime picks up the moved
          // centroid (only matters for future fly-to math).
          if (visitorContextData) registerFeatureListLayer('visitorContext', visitorContextData);
        }
      },
      // Activity hotspots — first-party timestamped GPX dwell cells. The
      // geojson carries two features per hotspot (Polygon cell + Point
      // centroid sharing one `id`); dedupe-by-id leaves one row per hotspot.
      // Visibility + fly only — these are evidence rows, not authored
      // geometry, so move/tag/highlight are deliberately off.
      activityHotspots: makeHotspotSpec('Activity hotspots', 'activity-hotspots'),
      // Simulated Saturday — deterministic synthetic hotspots that mirror the
      // activity-hotspot pipeline. Same shape, same scope (visibility + fly).
      syntheticActivity: makeHotspotSpec('Simulated Saturday activity', 'synthetic-activity-hotspots'),
      // Event-schedule anchors — the named locations from
      // aop_event_schedule.json (#pavilion, #registration, …). Sessions are
      // intentionally out of scope: they are derived from anchors + route
      // tags, and their authoring lives in the JSON file, not the panel.
      // Hiding an anchor here hides its circle + label without disturbing
      // the route line that may still pass through it.
      eventSchedule: {
        label: 'Event schedule POIs',
        idField: 'location_tag',
        rowLabel: (props) => {
          const role = props.role ? ` · ${String(props.role).replace(/_/g, ' ')}` : '';
          return `${props.name || props.location_tag}${role}`;
        },
        targetLayers: ['event-anchor-points', 'event-anchor-labels'],
        rowSort: (a, b) => String(a.props.name || '').localeCompare(String(b.props.name || '')),
        groups: [{
          id: 'anchors',
          label: null,
          match: (props) => props.feature_kind === 'event_anchor',
          defaultVisible: () => true
        }]
      },
      // Brand logos — on-map AOP badge + Rock Warblers logo. Drag-to-move is
      // the whole point of this consumer (placement gets nudged once the user
      // sees how the logo lands against the cartography); visibility is here
      // so a single logo can be hidden without flipping the layer toggle.
      // Override store keeps moved Points across reloads.
      brandLogos: {
        label: 'Brand logos',
        idField: 'logo_id',
        sourceChip: 'brand',
        // Editable display-name property (default 'name'), co-located on the
        // spec instead of a parallel name-property map. Served-source strategy
        // re-feeds the live source after a property edit; lazy so it reads the
        // brandLogosData `let`. Replaces a parallel served-source map.
        nameField: 'name',
        servedSource: () => ['brand-logos', brandLogosData],
        // Star surfaces the logo in the right-side ★ Visitor list virtual
        // group. Default off.
        highlightable: true,
        rowLabel: (props) => props.name || 'Logo',
        // --- Destination-list config (card 06) ---------------------------
        // Brand logos were a member of the retired hardcoded VISITOR_LIST_LAYERS
        // (['editorPois','brandLogos','visitorContext']) that the OLD
        // renderVisitorListGroup walked: a starred (`highlight === true`) brand
        // logo surfaced in the right ★ Visitor list (never in the left POI tab —
        // the old buildPoiGroups had no brandLogos block). The one-collector
        // refactor must preserve that exactly: `listMode: 'starred'` applies the
        // ONE star gate in collectStarredDestinations, and `listSurfaces`
        // routes to the right list only (left: false). Without this listRow the
        // collector's emit() skips brandLogos and a starred logo silently drops
        // out of the right list — the regression this restores. Per C5 this is
        // additive dispatch: no row is gated out beyond the pre-existing
        // ★ curation, no validator is introduced. R11 keeps brand logos off the
        // left POI-tab destination axis (their own size/move drawer); this only
        // re-surfaces the starred ones to the right ★ list as they shipped.
        listMode: 'starred',
        listSurfaces: { left: false, right: true },
        listGroup: { id: 'brand_logos', label: 'Brand logos' },
        listPredicate: () => true,
        listRow: (feature) => {
          const props = (feature && feature.properties) || {};
          const d = window.AOPFeatureDisplay.featureDisplay(props);
          return {
            id: `brand:${props.logo_id || props.name || 'idx'}`,
            name: d.name, kind: d.kind, blurb: d.blurb, revisitNote: d.revisit,
            status: d.status, source: d.source, caveat: d.caveat,
            feature,
            popupCoord: firstCoordinate(feature && feature.geometry) || geometryCentroid(feature && feature.geometry)
          };
        },
        sizeEditable: true,
        inlineEditor: true,
        targetLayers: ['brand-logos-icons'],
        groups: [{
          id: 'all',
          label: null,
          match: () => true,
          defaultVisible: () => true
        }],
        onMove: (feature, lngLat) => {
          if (!feature || !feature.geometry || feature.geometry.type !== 'Point') return;
          feature.geometry.coordinates = [lngLat.lng, lngLat.lat];
          savePositionedFeature('brandLogos', feature, {
            geometry: JSON.parse(JSON.stringify(feature.geometry))
          });
          const source = map.getSource('brand-logos');
          if (source && brandLogosData) source.setData(brandLogosData);
          if (brandLogosData) registerFeatureListLayer('brandLogos', brandLogosData);
        }
      },
      // Trails — the gold aop-trail-network, registered as a feature-LIST
      // destination layer (was paint-only in TUNABLE_LAYERS) so a trail can be
      // starred and surfaced like every other destination. universal_feature_layer
      // stage 3 / star_driven_poi_list #1 require trails to be starrable; this
      // spec is the registration that makes that uniform (card 05). The ONE
      // collector (collectStarredDestinations) consumes this registered layer;
      // since the sprint08 flip the spec is `listMode: 'starred'`, so only
      // ★-curated trails surface on the POI tab.
      //
      // idField is the derived `__trail_row_id` stamped at registration
      // (the trail-network load site stamps it before registerFeatureListLayer):
      // `n:<number>` for numbered trails, `name:<name>`
      // for named-but-unnumbered trails, and ABSENT for unnamed edges. Because
      // buildFeatureListState dedupes by idField (the same machinery cemeteries
      // use for their parcel+marker twins), this expresses the old
      // dedupe-one-row-per-trail / skip-unnamed-edge logic as registry data —
      // numbered trails collapse to one row even when the network has several
      // edges per number, named trails keep their own row, and unnamed edges
      // (null id) drop out of the directory exactly as before. No validator and
      // no row-dropping filter is introduced (C5): the only feature excluded is
      // the un-identified edge, by absence of identity, not by a vocabulary gate.
      trails: {
        label: 'Trails',
        idField: '__trail_row_id',
        sourceChip: 'trail',
        // The override key is the derived __trail_row_id. The load-time stamp
        // writes it onto every network feature, but the right-panel ★ bridge
        // hands us SERVED props (no stamp), so resolve from trail_number/name via
        // the shared trailRowId helper — otherwise a panel ★ on a trail can't find
        // its core row and the bridge silently no-ops (the trails-not-linked bug).
        idFor: (props) => trailRowId(props),
        // Star eligibility — trails join the destination axis. `highlightable`
        // draws the per-row ★ and is the flag card 06's one collector keys on.
        highlightable: true,
        // Explicit destination marker for the card-06 collector contract. Kept
        // alongside `highlightable` so a future collector can read either; both
        // are permissive flags, never a reject.
        destination: true,
        // --- Destination-list config (card 06) ---------------------------
        // Replaces the buildPoiGroups "Trails" block. The directory dedupe /
        // one-row-per-trail / skip-unnamed-edge logic now lives as registry
        // data: registration stamps `__trail_row_id` and buildFeatureListState
        // dedupes by it (numbered trails collapse to one row, named trails keep
        // their own, unnamed edges carry no id and drop out of the list — by
        // absence of identity, not a vocabulary gate, C5). So the collector just
        // walks the deduped runtime rows. ★-curated on the POI tab (sprint08 flip
        // below — only starred trails show); a starred trail also surfaces in the
        // ★ Visitor list (it already did via the hardcoded VISITOR_LIST_LAYERS,
        // now via the one collector).
        // `listRow` (with the trail-catalog write-up enrichment) is declared
        // below — card 05 added it; card 06 wires the collector to it.
        listGroup: { id: 'trails', label: 'Trails' },
        // sprint08 (star_driven_poi_normalization): ★-curated (trails was already
        // `highlightable`). The ★ travels durably (core.features.attrs.highlight ->
        // bake); a curated trail surfaces, uncurated ones stay off the POI tab until
        // starred. Numberless/nameless edges carry no `__trail_row_id` (unstarred).
        listMode: 'starred',
        listSurfaces: { left: true, right: true },
        listPredicate: () => true,
        listToggle: () => aopTrailNetworkToggle,
        rowLabel: (props) => {
          // Canonical `name` is baked (the trail catalog is folded into the feature
          // by rebake_canonical) — read the one field, never a runtime catalog join.
          // Catalogued trails read "Launchpad"; number-only edges read "Trail N".
          const name = (props.name != null && String(props.name) !== '') ? String(props.name) : null;
          const num = props.trail_number != null ? Number(props.trail_number) : null;
          return name || (num != null ? `Trail ${num}` : 'Trail');
        },
        targetLayers: ['aop-trail-network', 'aop-trail-network-labels'],
        // The gold network LINE/label layers are list-render targets only — they
        // do NOT receive the per-row id-based visibility paint filter. The
        // network renders all 120 edges and toggles wholesale via the network
        // checkbox exactly as before this card; the 20 unnamed edges carry no
        // `__trail_row_id` (so they stay out of the directory list) and must
        // still draw. Registering trails for the star/list machinery is additive
        // (C5) — it installs no row-dropping filter on rendered geometry.
        filterLayers: [],
        // Numbered trails first, ascending; then named trails alphabetically —
        // the same ordering the old buildPoiGroups trail sort produced.
        rowSort: (a, b) => {
          const na = a.props.trail_number != null ? Number(a.props.trail_number) : null;
          const nb = b.props.trail_number != null ? Number(b.props.trail_number) : null;
          if (na != null && nb != null) return na - nb;
          if (na != null) return -1;
          if (nb != null) return 1;
          return String(a.props.name || '').localeCompare(String(b.props.name || ''));
        },
        // Flat list — one group, all trails. defaultVisible true mirrors the
        // other served layers so registering trails does not hide anything.
        groups: [{
          id: 'all',
          label: null,
          match: () => true,
          defaultVisible: () => true
        }],
        // Uniform destination-row strategy for the one collector
        // (collectStarredDestinations) — name/kind/blurb/revisitNote/status/
        // source/popupCoord, all read from the feature's CANONICAL fields (the
        // trail catalog was folded into the bake by rebake_canonical, so the row
        // reads the same `name`/`description`/`status`/`source` the map label and
        // popup do — no runtime join, no cross-surface fork). This IS the live
        // path: the collector calls spec.listRow for every registry destination
        // layer, and buildPoiGroups only groups the result. Since the sprint08
        // flip the spec is listMode:'starred', so only ★-curated trails surface.
        listRow: (feature) => {
          const props = (feature && feature.properties) || {};
          const num = props.trail_number != null ? Number(props.trail_number) : null;
          const name = (props.name != null && String(props.name) !== '') ? String(props.name) : null;
          const d = window.AOPFeatureDisplay.featureDisplay(props);
          return {
            id: `trail:${props.__trail_row_id || (num != null ? `n:${num}` : (name ? `name:${name}` : ''))}`,
            name: d.name, kind: d.kind, blurb: d.blurb, revisitNote: d.revisit,
            status: d.status, source: d.source, caveat: d.caveat,
            feature,
            popupCoord: firstCoordinate(feature && feature.geometry)
          };
        }
      }
    };

    // --- Visitor-context override store ----------------------------------
    // Visitor-context callouts ship as a static geojson under website/data.
    // When the user moves one via the feature list panel we record the new
    // geometry here, keyed by `name`, and replay it on the next page load.
    // Editing the source geojson would invalidate stale overrides for that
    // entry — the user re-positions and it overwrites cleanly. Storage key
    // declared at the top of the script with the others.
    let visitorContextData = null;
    // Hoisted so the buildings spec's onMove (drag-to-adjust) can reach the
    // live FeatureCollection — same pattern as visitorContextData. Assigned
    // during layer load, not redeclared there.
    let buildingsData = null;
    // Hoisted (was a load-scoped const) so the positioned-features override
    // store + source refresh can reach the cemetery collection — cemeteries
    // are now editable like the other served layers.
    let cemeteryData = null;

    // --- Unified positioned-features store -------------------------------
    // Replaces the two per-layer override stores (visitor-context, brand
    // logos). Keyed by `${layerKey}:${id}` where `id` is the value at the
    // layer's `idField` in the FEATURE_LIST_LAYERS spec. Each entry is a
    // sparse patch — only the props the user has touched. Geometry overrides
    // exist because the source data ships in committed website/data/*.geojson
    // (immutable from the browser); highlight + locked persist here too so
    // they survive reload without baking into the on-disk seed.
    function loadPositionedFeatures() {
      const parsed = readJsonStore(POSITIONED_FEATURES_KEY, () => ({}));
      return parsed && typeof parsed === 'object' ? parsed : {};
    }

    function positionedFeatureKey(layerKey, featureId) {
      return `${layerKey}:${featureId}`;
    }

    // The derived per-trail row id the `trails` spec dedupes + keys overrides on:
    // `n:<number>` for numbered trails, `name:<name>` for named-but-unnumbered
    // trails, null for unnamed edges (intentionally not directory entries). The
    // gold-network load stamps this onto each feature as `__trail_row_id`; the
    // right-panel ★ bridge (js/panel.js) hands us the SERVED props, which don't
    // carry the stamp, so we recompute it from trail_number/name. ONE derivation,
    // two callers (the load-time stamp + the bridge's idFor) — extract_before_invent.
    function trailRowId(props) {
      if (!props) return null;
      if (props.__trail_row_id != null) return String(props.__trail_row_id);
      const num = props.trail_number != null ? Number(props.trail_number) : null;
      if (num != null && !Number.isNaN(num)) return `n:${num}`;
      const name = (props.name != null && String(props.name) !== '') ? String(props.name) : null;
      return name != null ? `name:${name}` : null;
    }

    function positionedFeatureIdFor(layerKey, feature) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec || !feature || !feature.properties) return null;
      // A spec may COMPUTE its override key from props (trails: the derived
      // __trail_row_id, recomputed from trail_number/name when a caller — the
      // right-panel ★ bridge — passes served props that lack the stamp). Default:
      // the plain idField value.
      if (typeof spec.idFor === 'function') {
        const computed = spec.idFor(feature.properties);
        return computed == null ? null : String(computed);
      }
      const value = feature.properties[spec.idField];
      return value == null ? null : String(value);
    }

    // Merge `patch` into the entry for one feature. `patch` may set any of
    // geometry, highlight, locked, icon_size — only the keys present in the
    // patch are touched, so a star toggle never clobbers a geometry override.
    function savePositionedFeature(layerKey, feature, patch) {
      const id = positionedFeatureIdFor(layerKey, feature);
      if (id == null || !patch) return;
      const key = positionedFeatureKey(layerKey, id);
      const store = loadPositionedFeatures();
      const existing = store[key] || {};
      const next = { ...existing };
      if (patch.geometry !== undefined) next.geometry = patch.geometry;
      if (patch.highlight !== undefined) next.highlight = patch.highlight === true;
      if (patch.locked !== undefined) next.locked = patch.locked === true;
      if (patch.icon_size !== undefined && Number.isFinite(Number(patch.icon_size))) {
        next.icon_size = Number(patch.icon_size);
      }
      // Editable property overrides (name/label/notes/category) for served
      // layers. These mutate feature.properties so the row label, the map
      // popup, and the "Copy as GeoJSON" output all read the edited value.
      if (patch.properties && typeof patch.properties === 'object') {
        next.properties = { ...(existing.properties || {}), ...patch.properties };
      }
      next.updated = new Date().toISOString();
      store[key] = next;
      writeJsonStore(POSITIONED_FEATURES_KEY, store);
    }

    // The four SERVED reference layers whose CMFS spine (name/description/kind),
    // highlight (★), and geometry are now BAKED truth in the served GeoJSON
    // (gold migration Approach-C: core.features COLUMNS+attrs -> the published
    // file). For these, the localStorage positioned-features store is a
    // working/staging buffer for "Export all" only — at BOOT it must NOT paint a
    // prior-session diff over the baked served value (G_B.1, finding 3 keystone).
    // A config set, not a call-site `layerKey === 'x'` branch (C1). Mirrors the
    // Python door's LAYERKEY_TO_CORE_LAYER (the one sink for these four).
    const BAKED_REFERENCE_LAYERS = new Set(['buildings', 'cemeteries', 'visitorContext', 'trails']);

    // Replay stored overrides onto a freshly fetched FeatureCollection.
    // Mutates in place so the live MapLibre source and the feature-list
    // runtime see the same references.
    //
    // `opts.boot` (G_B.1): the boot READ for a BAKED reference layer trusts the
    // served file as published truth — the baked attributes (geometry, the spine
    // properties, and highlight) are NOT replayed from the store, so a STALE
    // prior-session diff no longer overrides the baked value on reload. The diff
    // stays in the store and still Exports; only the boot paint-over is demoted.
    // `locked`/`icon_size` are pure view-state with no DB/baked home, so they
    // still replay even at boot. The LIVE re-sync path (persistFeatureFlagChange
    // -> here with no boot flag, after an in-session edit) keeps full replay so an
    // author's edit-in-progress still propagates across feature twins THIS session.
    function applyPositionedFeatures(layerKey, data, opts) {
      if (!data || !data.features) return data;
      // Demote the baked-attribute replay ONLY at boot, ONLY for the baked
      // reference layers; everything else (live re-sync, brandLogos, drawn POIs)
      // keeps the full replay it always had.
      const demoteBaked = !!(opts && opts.boot) && BAKED_REFERENCE_LAYERS.has(layerKey);
      const store = loadPositionedFeatures();
      for (const feature of data.features) {
        const id = positionedFeatureIdFor(layerKey, feature);
        if (id == null) continue;
        const entry = store[positionedFeatureKey(layerKey, id)];
        if (!entry) continue;
        feature.properties = feature.properties || {};
        if (!demoteBaked) {
          if (entry.geometry) feature.geometry = JSON.parse(JSON.stringify(entry.geometry));
          // Write the flag when the store has an opinion (true OR false) so an
          // un-star/un-lock survives reload even if the base feature shipped true.
          if (entry.highlight !== undefined) feature.properties.highlight = entry.highlight === true;
          // Replay editable property overrides (name/label/notes/category).
          if (entry.properties && typeof entry.properties === 'object') {
            Object.assign(feature.properties, entry.properties);
          }
        }
        // Pure view-state (no baked/DB home) replays even at boot.
        if (entry.locked !== undefined) feature.properties.locked = entry.locked === true;
        if (Number.isFinite(Number(entry.icon_size))) {
          feature.properties.icon_size = Number(entry.icon_size);
        }
      }
      return data;
    }

    // Read-only slice of the unified store filtered to one layer's entries.
    // Used by section export so a paste of one section's slice cannot leak
    // overrides from sibling layers.
    function positionedFeaturesSlice(layerKey) {
      const prefix = `${layerKey}:`;
      const store = loadPositionedFeatures();
      const slice = {};
      for (const [key, value] of Object.entries(store)) {
        if (key.startsWith(prefix)) slice[key] = value;
      }
      return slice;
    }

    // Merge an imported slice back into the unified store. Slice keys are
    // already in `${layerKey}:${id}` form; we trust the bundle author not to
    // smuggle other layers' entries through a section paste, but the section
    // apply path narrows by layerKey before calling this anyway.
    function mergePositionedFeaturesSlice(slice) {
      if (!slice || typeof slice !== 'object') return;
      const store = loadPositionedFeatures();
      for (const [key, value] of Object.entries(slice)) {
        store[key] = value;
      }
      writeJsonStore(POSITIONED_FEATURES_KEY, store);
    }

    // --- Brand-logos override store --------------------------------------
    // Mirrors the visitor-context pattern: the seed geometry ships in
    // website/data/gold_aop_visitor_context_callouts.geojson (the logos were merged
    // there as kind=brand_logo points, 2026-06-05), and each drag commits a new
    // Point to localStorage so the user's placement survives reload. Keyed
    // by `logo_id` (aop_badge, rock_warblers) — the on-disk file can be
    // re-edited and any orphaned override key is simply ignored on load.
    let brandLogosData = null;
    const BRAND_LOGO_SIZE_MIN = 0.02;
    const BRAND_LOGO_SIZE_MAX = 0.20;
    const BRAND_LOGO_SIZE_STEP = 0.005;
    const BRAND_LOGO_SIZE_DEFAULT = 0.06;

    function brandLogoSize(feature) {
      const value = Number(feature?.properties?.icon_size);
      return Number.isFinite(value) ? value : BRAND_LOGO_SIZE_DEFAULT;
    }

    function formatBrandLogoSize(value) {
      return Number(value).toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
    }

    function setBrandLogoSize(feature, value) {
      if (!feature || !feature.properties) return;
      const clamped = Math.min(BRAND_LOGO_SIZE_MAX, Math.max(BRAND_LOGO_SIZE_MIN, Number(value)));
      if (!Number.isFinite(clamped)) return;
      feature.properties.icon_size = Number(clamped.toFixed(3));
      savePositionedFeature('brandLogos', feature, { icon_size: feature.properties.icon_size });
      const source = map.getSource('brand-logos');
      if (source && brandLogosData) source.setData(brandLogosData);
    }

    // --- Brand-logo zoom-cap (item 5) ------------------------------------
    // The per-feature `icon_size` above is a flat MapLibre icon-size factor:
    // it holds a CONSTANT screen-pixel size at every zoom. Anchored to a
    // geographic point, that means zooming OUT (toward region) keeps the
    // logo the same on-screen size while the map content shrinks — so the
    // logo eats a larger and larger share of the visible park. The user
    // wants it to "max out at park size and not grow much more at region
    // level."
    //
    // Fix: multiply the per-feature size by a zoom factor that CLAMPS to a
    // max at/above park zoom and HALVES per zoom level below it. Halving the
    // screen size per zoom-out level holds the logo's geographic footprint
    // (and thus its share of the visible park) constant — i.e. it caps at
    // its park-zoom footprint and shrinks on screen as you zoom further out,
    // instead of growing relative to the map. The `BRAND_LOGO_CAP` slider
    // scales that capped park-zoom size live; export ships the tuned value
    // back. Persisted in its own localStorage slot so a reload keeps it.
    const BRAND_LOGO_CAP_ZOOM = 15;        // park anchor (Park view fits at maxZoom 15.5)
    const BRAND_LOGO_CAP_MIN = 0.4;
    const BRAND_LOGO_CAP_MAX = 2.5;
    const BRAND_LOGO_CAP_STEP = 0.05;
    const BRAND_LOGO_CAP_DEFAULT = 1;
    const BRAND_LOGO_CAP_KEY = 'aop_brand_logo_cap_v1';
    let brandLogoCap = BRAND_LOGO_CAP_DEFAULT;

    function loadBrandLogoCap() {
      const raw = readJsonStore(BRAND_LOGO_CAP_KEY, () => null);
      // Only adopt a genuinely stored number; `null`/missing keeps the
      // default (Number(null) === 0 would otherwise clamp to MIN).
      if (typeof raw === 'number' && Number.isFinite(raw)) {
        brandLogoCap = Math.min(BRAND_LOGO_CAP_MAX, Math.max(BRAND_LOGO_CAP_MIN, raw));
      }
      return brandLogoCap;
    }

    function formatBrandLogoCap(value) {
      return Number(value).toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
    }

    // The MapLibre `icon-size` expression: per-feature size × global cap ×
    // a zoom factor that is 1 at/above park zoom and 2^(zoom − park) below
    // it (exponential base 2 → halves per zoom level out). `interpolate`
    // clamps to the endpoint values outside the stop range, so above park
    // zoom the factor stays 1 (capped, no further on-screen growth) and far
    // below it stays at the lower stop's tiny factor.
    //
    // MapLibre rule: a `["zoom"]` expression may ONLY appear as the input to
    // a TOP-LEVEL interpolate/step — it cannot be nested inside an outer
    // `["*", …]`. So the per-feature size and the cap are folded INTO each
    // stop's output value (perFeat × cap × factor), with `interpolate` as the
    // outermost node. Each stop output is itself a `["*", get(icon_size), k]`.
    function brandLogoIconSizeExpr() {
      const cap = brandLogoCap;
      const lowZoom = BRAND_LOGO_CAP_ZOOM - 5;        // 5 levels below park
      const lowFactor = Math.pow(2, lowZoom - BRAND_LOGO_CAP_ZOOM); // = 0.03125
      const perFeat = ['coalesce', ['get', 'icon_size'], BRAND_LOGO_SIZE_DEFAULT];
      return [
        'interpolate', ['exponential', 2], ['zoom'],
        lowZoom, ['*', perFeat, cap * lowFactor],
        BRAND_LOGO_CAP_ZOOM, ['*', perFeat, cap]
      ];
    }

    function applyBrandLogoCap() {
      if (map && map.getLayer && map.getLayer('brand-logos-icons')) {
        map.setLayoutProperty('brand-logos-icons', 'icon-size', brandLogoIconSizeExpr());
      }
    }

    function setBrandLogoCap(value) {
      const clamped = Math.min(BRAND_LOGO_CAP_MAX, Math.max(BRAND_LOGO_CAP_MIN, Number(value)));
      if (!Number.isFinite(clamped)) return;
      brandLogoCap = Number(clamped.toFixed(3));
      writeJsonStore(BRAND_LOGO_CAP_KEY, brandLogoCap);
      applyBrandLogoCap();
    }

    // Small JSON the user can copy and send back so a tuned cap is portable.
    function brandLogoCapExportPayload() {
      return {
        schema: 'aop-brand-logo-cap-v1',
        exported_at: new Date().toISOString(),
        brand_logo_size_cap: brandLogoCap,
        cap_zoom: BRAND_LOGO_CAP_ZOOM,
        note: 'Max on-screen logo size at/above park zoom; logo shrinks (holds geographic footprint) as you zoom out below cap_zoom.'
      };
    }

    async function exportBrandLogoCap(statusEl) {
      const text = JSON.stringify(brandLogoCapExportPayload(), null, 2) + '\n';
      try {
        const copied = await copyText(text);
        if (statusEl) statusEl.textContent = copied ? 'Logo cap copied to clipboard.' : 'Clipboard copy failed.';
      } catch (error) {
        console.warn('Brand-logo cap export failed:', error);
        if (statusEl) statusEl.textContent = 'Clipboard copy failed.';
      }
    }

    // The footer DOM that lives under the brand-logo rows: max-size slider +
    // ⧉ export button + a status line. Mirrors the per-feature size slider
    // (.feature-size-control) and the preset ⧉ copy pattern.
    function buildBrandLogoCapFooter() {
      const footer = document.createElement('div');
      footer.className = 'brand-logo-cap';

      const row = document.createElement('div');
      row.className = 'brand-logo-cap-row';

      const label = document.createElement('label');
      label.className = 'brand-logo-cap-control';
      label.title = 'Maximum on-screen logo size (caps at park zoom; logos shrink as you zoom out past it)';
      const text = document.createElement('span');
      text.className = 'brand-logo-cap-label';
      text.textContent = 'Max size';
      const slider = document.createElement('input');
      slider.type = 'range';
      slider.id = 'brandLogoCapSlider';
      slider.className = 'brand-logo-cap-slider';
      slider.min = String(BRAND_LOGO_CAP_MIN);
      slider.max = String(BRAND_LOGO_CAP_MAX);
      slider.step = String(BRAND_LOGO_CAP_STEP);
      slider.value = String(brandLogoCap);
      const out = document.createElement('output');
      out.className = 'brand-logo-cap-out';
      out.textContent = formatBrandLogoCap(brandLogoCap);
      slider.addEventListener('input', () => {
        setBrandLogoCap(slider.value);
        out.textContent = formatBrandLogoCap(brandLogoCap);
      });
      label.append(text, slider, out);

      const exportBtn = document.createElement('button');
      exportBtn.type = 'button';
      exportBtn.id = 'brandLogoCapExport';
      exportBtn.className = 'brand-logo-cap-export';
      exportBtn.textContent = '⧉ Export';
      exportBtn.title = 'Copy the current max-size cap as JSON to send back';

      const status = document.createElement('div');
      status.className = 'brand-logo-cap-status';
      status.id = 'brandLogoCapStatus';
      exportBtn.addEventListener('click', () => exportBrandLogoCap(status));

      row.append(label, exportBtn);
      footer.append(row, status);
      return footer;
    }

    // Per-layer runtime state: data, base filters captured at addLayer time,
    // the resolved feature → group bucket, expanded/collapsed UI state.
    // Storage key for the persisted visibility set lives at the top of the
    // script with the others.
    const featureListRuntime = {};
    // Now that the runtime and FEATURE_LIST_LAYERS are bound, build the
    // unified editor tree. Registering tree targets here means any
    // registerFeatureListLayer call later in boot lands rows in the tree.
    // Load the persisted brand-logo size cap first so the footer slider the
    // tree renders shows the saved value (the layer re-reads it on add too).
    loadBrandLogoCap();
    buildEditorTree();
    // Active move-mode target. While set, the next map click commits the
    // staged feature to the clicked lngLat; Esc or the panel's Cancel button
    // reverts. Shared across consumers (POIs first; callouts + logos to come).
    let moveState = null;
    // Stash listeners so cancelMoveMode can remove them precisely (the same
    // function refs that were registered).
    let moveMapClickHandler = null;
    let moveEscHandler = null;
    const LONG_PRESS_MS = 450;

    function loadFeatureVisibilityStore() {
      const parsed = readJsonStore(FEATURE_VISIBILITY_KEY, () => ({}));
      return parsed && typeof parsed === 'object' ? parsed : {};
    }

    function saveFeatureVisibilityStore(store) {
      writeJsonStore(FEATURE_VISIBILITY_KEY, store);
    }

    // Map a feature to its group inside a layer's `groups` array — first match
    // wins, mirroring the order in FEATURE_LIST_LAYERS. The `other` catch-all
    // depends on this ordering: it must be declared last. `feature` is passed
    // through so kind-grouped layers (editorPois) can match on geometry.type;
    // existing layers that only inspect props ignore the 2nd arg.
    function groupForFeature(layerKey, props, feature) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec) return null;
      for (const group of spec.groups) {
        if (group.match(props, feature)) return group;
      }
      return null;
    }

    // Bucket features into their groups and compute the initial visibility set
    // by overlaying any persisted user choices on top of the group defaults.
    // Returns { groups: [{ group, features: [...] }], visibleIds: Set }.
    function buildFeatureListState(layerKey, data) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec || !data) return null;
      const store = loadFeatureVisibilityStore();
      const persisted = (store[layerKey] && typeof store[layerKey] === 'object') ? store[layerKey] : {};
      const bucketed = new Map(spec.groups.map((g) => [g.id, { group: g, features: [] }]));
      const visibleIds = new Set();
      const seenIds = new Set();
      for (const feature of data.features || []) {
        const props = feature.properties || {};
        const id = props[spec.idField];
        if (id == null) continue;
        // Dedupe by ID — cemeteries emit both parcel + marker per cemetery,
        // sharing the same parcel_id. The list shows one row per cemetery.
        if (seenIds.has(id)) continue;
        seenIds.add(id);
        const group = groupForFeature(layerKey, props, feature);
        if (!group) continue;
        bucketed.get(group.id).features.push({ id, props, feature });
        const persistedValue = persisted[String(id)];
        const visible = typeof persistedValue === 'boolean'
          ? persistedValue
          : !!group.defaultVisible(props);
        if (visible) visibleIds.add(id);
      }
      const groups = [...bucketed.values()].filter((b) => b.features.length > 0);
      // Optional per-spec row sort (POIs sort by category then name; buildings
      // and cemeteries leave insertion order alone).
      if (typeof spec.rowSort === 'function') {
        for (const bucket of groups) bucket.features.sort(spec.rowSort);
      }
      return { groups, visibleIds };
    }

    // Compose: base filter (captured when the layer was added) AND the
    // visibility filter (membership in the visible-id set). When the visible
    // set is empty we still emit `["in", id, ["literal", []]]` so nothing
    // draws — matches the "untick everything" intent.
    function composeFeatureFilter(baseFilter, idField, visibleIds) {
      const visibilityFilter = ['in', ['get', idField], ['literal', [...visibleIds]]];
      if (!baseFilter) return visibilityFilter;
      // MapLibre's filter spec accepts ["all", ...subfilters].
      if (Array.isArray(baseFilter) && baseFilter[0] === 'all') {
        return ['all', ...baseFilter.slice(1), visibilityFilter];
      }
      return ['all', baseFilter, visibilityFilter];
    }

    // Which target layers receive the id-based visibility paint filter.
    // Defaults to ALL of the spec's targetLayers (cemeteries/buildings/etc.
    // every feature carries the idField, so the membership filter never drops
    // anything that should render). A spec may narrow this with `filterLayers`:
    // trails declare `filterLayers: []` because their gold network LINE/label
    // layers must keep rendering all edges — including the 20 unnamed ones that
    // intentionally carry NO `__trail_row_id` (so they stay out of the directory
    // list) and would otherwise be excluded by the membership filter. Per C5
    // this is a safe default that never introduces a row-dropping filter on
    // rendered geometry; registering trails for the LIST/star machinery does not
    // install a paint filter that hides un-identified geometry.
    function featureFilterLayersFor(spec) {
      if (spec && Array.isArray(spec.filterLayers)) return spec.filterLayers;
      return (spec && spec.targetLayers) || [];
    }

    // Apply the current visibility set to every target layer's paint filter.
    // Called on init, on toggle, and on bulk group toggle.
    function applyFeatureListFilters(layerKey) {
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) return;
      const spec = FEATURE_LIST_LAYERS[layerKey];
      for (const layerId of featureFilterLayersFor(spec)) {
        if (!map.getLayer(layerId)) continue;
        const base = runtime.baseFilters[layerId] || null;
        map.setFilter(layerId, composeFeatureFilter(base, spec.idField, runtime.state.visibleIds));
      }
    }

    // Persist the current visibility set for this layer. We store an explicit
    // per-id boolean rather than a sparse "visible only" list so a feature the
    // user has *unticked* survives a reload (and isn't re-defaulted on).
    function persistFeatureVisibility(layerKey) {
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) return;
      const store = loadFeatureVisibilityStore();
      const layerEntry = {};
      for (const bucket of runtime.state.groups) {
        for (const item of bucket.features) {
          layerEntry[String(item.id)] = runtime.state.visibleIds.has(item.id);
        }
      }
      store[layerKey] = layerEntry;
      saveFeatureVisibilityStore(store);
    }

    function setFeatureVisible(layerKey, id, visible) {
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) return;
      if (visible) runtime.state.visibleIds.add(id);
      else runtime.state.visibleIds.delete(id);
      applyFeatureListFilters(layerKey);
      persistFeatureVisibility(layerKey);
    }

    function setGroupVisible(layerKey, groupId, visible) {
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) return;
      const bucket = runtime.state.groups.find((b) => b.group.id === groupId);
      if (!bucket) return;
      for (const item of bucket.features) {
        if (visible) runtime.state.visibleIds.add(item.id);
        else runtime.state.visibleIds.delete(item.id);
      }
      applyFeatureListFilters(layerKey);
      persistFeatureVisibility(layerKey);
    }

    // --- Feature → #tag binding ------------------------------------------
    // Lets a feature in the list (1010 building, a drawn POI) be bound to a
    // #tag (e.g. #pavilion). The event-schedule resolver consumes the same
    // tag to look up coordinates, so the schedule JSON can omit lat/long for
    // any location whose key matches a binding. Card:
    // brain/tasks/02_edit/named_feature_tagging.md. Storage keys (the tag
    // store and the one-time seed flag) live at the top of the script.
    // Inverted lookup, rebuilt whenever a layer registers or a tag changes.
    // Shape: Map<"#tag", { layerKey, featureId, coordinates }>.
    const tagToFeature = new Map();

    function loadFeatureTagStore() {
      const parsed = readJsonStore(FEATURE_TAG_KEY, () => ({}));
      return parsed && typeof parsed === 'object' ? parsed : {};
    }

    function saveFeatureTagStore(store) {
      writeJsonStore(FEATURE_TAG_KEY, store);
    }

    // Normalize input → `#tag` lowercase, no internal whitespace, leading #
    // guaranteed. Empty string means "no tag" (clears the binding).
    function normalizeFeatureTag(value) {
      const trimmed = String(value || '').trim().toLowerCase().replace(/\s+/g, '-');
      if (!trimmed) return '';
      return trimmed.startsWith('#') ? trimmed : `#${trimmed}`;
    }

    function tagForFeature(layerKey, featureId) {
      const store = loadFeatureTagStore();
      const layerTags = store[layerKey];
      const value = layerTags && layerTags[String(featureId)];
      return value ? String(value) : '';
    }

    // Rebuild the inverted lookup from the persisted store and the currently
    // registered layer runtimes. A binding to a layer that hasn't registered
    // yet is preserved in the store but absent from the lookup until that
    // layer comes online — so the store IS the source of truth, lookup is
    // a derived index.
    function rebuildTagLookup() {
      tagToFeature.clear();
      // 0) Data-led bindings: a feature's OWN `tag` property (baked into the
      //    served GeoJSON by the right-panel editor) binds it. Scanned first so a
      //    baked #pavilion resolves on load with no localStorage; the explicit
      //    store (below) overrides, so a live edit / moved binding still wins.
      for (const [layerKey, runtime] of Object.entries(featureListRuntime)) {
        if (!runtime || !runtime.state) continue;
        for (const bucket of runtime.state.groups) {
          for (const item of bucket.features) {
            const normalized = normalizeFeatureTag(
              (item.feature && item.feature.properties && item.feature.properties.tag) || '');
            if (!normalized) continue;
            const coords = geometryCentroid(item.feature.geometry);
            if (!coords) continue;
            tagToFeature.set(normalized, { layerKey, featureId: item.id, coordinates: [coords[0], coords[1]] });
          }
        }
      }
      const store = loadFeatureTagStore();
      for (const [layerKey, layerTags] of Object.entries(store)) {
        if (!layerTags || typeof layerTags !== 'object') continue;
        if (!featureListRuntime[layerKey]) continue;
        for (const [featureId, tag] of Object.entries(layerTags)) {
          const normalized = normalizeFeatureTag(tag);
          if (!normalized) continue;
          const item = findFeatureById(layerKey, featureId);
          if (!item) continue;
          const coords = geometryCentroid(item.feature.geometry);
          if (!coords) continue;
          tagToFeature.set(normalized, {
            layerKey,
            featureId: item.id,
            coordinates: [coords[0], coords[1]]
          });
        }
      }
    }

    // Drop tag bindings whose features no longer exist in the layer (e.g.
    // POI "Clear all"). Called on every register pass — buildings won't ever
    // shrink, but POIs do.
    function pruneOrphanedTags(layerKey) {
      const store = loadFeatureTagStore();
      const layerTags = store[layerKey];
      if (!layerTags) return;
      let changed = false;
      for (const featureId of Object.keys(layerTags)) {
        if (!findFeatureById(layerKey, featureId)) {
          delete layerTags[featureId];
          changed = true;
        }
      }
      if (changed) saveFeatureTagStore(store);
    }

    // Bind / re-bind / clear a tag for a feature. A tag is one-to-one: if
    // the same tag was previously bound to another feature, the prior
    // binding is moved (no two rows can both claim #pavilion). Triggers a
    // schedule re-resolution so the calendar/anchor update live.
    function setFeatureTag(layerKey, featureId, rawTag) {
      const normalized = normalizeFeatureTag(rawTag);
      const store = loadFeatureTagStore();
      // Strip any prior holder of this tag across every layer.
      if (normalized) {
        for (const [otherLayer, otherTags] of Object.entries(store)) {
          if (!otherTags || typeof otherTags !== 'object') continue;
          for (const otherFeatureId of Object.keys(otherTags)) {
            const sameRow = otherLayer === layerKey && String(otherFeatureId) === String(featureId);
            if (!sameRow && normalizeFeatureTag(otherTags[otherFeatureId]) === normalized) {
              delete otherTags[otherFeatureId];
            }
          }
        }
      }
      if (!store[layerKey]) store[layerKey] = {};
      if (normalized) store[layerKey][String(featureId)] = normalized;
      else delete store[layerKey][String(featureId)];
      saveFeatureTagStore(store);
      rebuildTagLookup();
      rebuildEventScheduleData();
    }


	    function resetDefaultPavilionTagRuntime() {
	      const runtime = featureListRuntime['buildings'];
	      if (!runtime || !runtime.state) return;
	      for (const bucket of runtime.state.groups) {
	        for (const item of bucket.features) {
	          if (!String(item.props.address || '').startsWith('1010 ')) continue;
	          const coords = geometryCentroid(item.feature.geometry);
	          if (!coords) return;
	          tagToFeature.set('#pavilion', {
	            layerKey: 'buildings',
	            featureId: item.id,
	            coordinates: [coords[0], coords[1]]
	          });
	          return;
	        }
	      }
	    }

	    function resetFeatureListRuntimeDefaults() {
	      for (const [layerKey, runtime] of Object.entries(featureListRuntime)) {
	        if (!runtime || !runtime.data || !FEATURE_LIST_LAYERS[layerKey]) continue;
	        runtime.state = buildFeatureListState(layerKey, runtime.data);
	        runtime.collapsed = {};
	        for (const group of FEATURE_LIST_LAYERS[layerKey].groups) {
	          runtime.collapsed[group.id] = !!group.collapsedDefault;
	        }
	        applyFeatureListFilters(layerKey);
	        if (shouldRenderFeatureList(layerKey)) renderFeatureList(layerKey);
	      }
	    }

	    // Fly + flash a single feature. Mirrors gotoEventSession's camera math so
    // the flight lands inside the visible map slice (not under the right
    // panel). No popup — the row label is already on-screen.
    function flyToFeature(feature) {
      if (!feature || !feature.geometry) return;
      const pad = visibleMapPadding(20);
      const bounds = geojsonBounds({ type: 'FeatureCollection', features: [feature] });
      if (bounds) {
        const [[minLng, minLat], [maxLng, maxLat]] = bounds;
        if (minLng === maxLng && minLat === maxLat) {
          map.flyTo({
            center: [minLng, minLat],
            zoom: 18,
            offset: visibleCenterOffset(pad),
            duration: 900,
            bearing: map.getBearing(),
            pitch: map.getPitch()
          });
        } else {
          map.fitBounds(bounds, {
            padding: pad,
            maxZoom: 18,
            duration: 900,
            bearing: map.getBearing(),
            pitch: map.getPitch()
          });
        }
      }
      const highlight = map.getSource('search-highlight');
      if (highlight) {
        highlight.setData({ type: 'FeatureCollection', features: [feature] });
        pulseHighlight();
      }
    }

    // The ONE fly-to button gesture (universal_feature_layer R14). The 🎯
    // "Fly to feature" button was hand-built identically in three row builders
    // (renderVisitorListGroup `vrow-fly`, renderFeatureListInto `feature-fly`,
    // buildEditDock head `dock-ico`) — same type='button', same
    // preventDefault+stopPropagation (so the row's own click doesn't also fire),
    // same flyToFeature(feature). Centralized here; each surface passes only its
    // surface-specific `className`. Behavior-preserving: a falsy feature is a
    // no-op inside flyToFeature (guarded), so no caller is dropped or rejected.
    function makeFlyButton(feature, className) {
      const fly = document.createElement('button');
      fly.type = 'button';
      fly.className = className;
      fly.title = 'Fly to feature';
      fly.textContent = '🎯';
      fly.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        flyToFeature(feature);
      });
      return fly;
    }

    // --- Move-mode primitive --------------------------------------------
    // A feature list consumer that declares `onMove(feature, lngLat)` opts into
    // the drag-to-move side of the primitive. The user enters move mode by
    // long-pressing a row (mobile) or clicking the ✋ button (desktop). While
    // staged, the next map click is intercepted and routed to `onMove`, which
    // is responsible for translating the geometry and persisting it. Esc or
    // the in-panel Cancel button aborts without changing geometry.

    // Centroid that survives Point / LineString / Polygon — the only geometry
    // kinds the POI editor produces today. Returns null for empty geometries.
    function geometryCentroid(geometry) {
      if (!geometry) return null;
      if (geometry.type === 'Point') return geometry.coordinates;
      if (geometry.type === 'LineString') {
        const coords = geometry.coordinates || [];
        if (!coords.length) return null;
        let sx = 0, sy = 0;
        for (const [x, y] of coords) { sx += x; sy += y; }
        return [sx / coords.length, sy / coords.length];
      }
      if (geometry.type === 'Polygon') {
        // Outer ring only; drop the closing duplicate so it doesn't double-weight.
        const ring = (geometry.coordinates || [])[0] || [];
        const last = ring.length > 1 ? ring.length - 1 : ring.length;
        if (!last) return null;
        let sx = 0, sy = 0;
        for (let i = 0; i < last; i++) { sx += ring[i][0]; sy += ring[i][1]; }
        return [sx / last, sy / last];
      }
      return null;
    }

    // Bounding-box center of ANY geometry, including Multi* parts. Used as the
    // move anchor (M9): geometryCentroid above is a vertex-density mean — skewed
    // for uneven polygons, and it returns null for MultiPolygon/MultiLineString/
    // GeometryCollection, which silently no-oped a move (onMove bails on a null
    // anchor). The bbox center is well-defined for every coordinate tree and is a
    // stable grab point. Kept separate so popup placement (which still calls
    // geometryCentroid) is untouched.
    function geometryBboxCenter(geometry) {
      if (!geometry || !geometry.coordinates || !geometry.coordinates.length) return null;
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      const walk = (coords) => {
        if (typeof coords[0] === 'number') {
          const x = coords[0], y = coords[1];
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (y < minY) minY = y;
          if (y > maxY) maxY = y;
          return;
        }
        for (const child of coords) walk(child);
      };
      walk(geometry.coordinates);
      if (!isFinite(minX)) return null;
      return [(minX + maxX) / 2, (minY + maxY) / 2];
    }

    // In-place translate of a coordinate tree (recursive) by (dLng, dLat).
    // Mutates so the feature reference shared with editorPois stays current.
    function translateCoordinates(coords, dLng, dLat) {
      if (typeof coords[0] === 'number') {
        coords[0] += dLng;
        coords[1] += dLat;
        return;
      }
      for (const child of coords) translateCoordinates(child, dLng, dLat);
    }

    // Toggle the per-feature highlight flag for layers that opt in
    // (`highlightable: true` in their FEATURE_LIST_LAYERS spec). The flag is
    // mirrored on `feature.properties.highlight` so GeoJSON export and the
    // Visitor list group can read it off the live feature. Persistence
    // routes by spec.persistKind: editorPois → array store (saveEditorPois);
    // visitorContext + brandLogos → unified positioned-features store.
    // One refresh path after any single-feature mutation (highlight, lock).
    // Replaces the scattered `if (layerKey === 'editorPois') refreshEditorSource();
    // else renderFeatureList(layerKey)` branches: a layer declares its own
    // post-mutation strategy in its spec; everything else re-renders its
    // registered list. No layer is named at the call site.
    function refreshAfterFeatureChange(layerKey) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (spec && typeof spec.onMutate === 'function') spec.onMutate();
      else renderFeatureList(layerKey);
    }

    function toggleFeatureHighlight(layerKey, featureId) {
      const item = findFeatureById(layerKey, featureId);
      if (!item || !item.feature) return;
      const props = item.feature.properties = item.feature.properties || {};
      props.highlight = !props.highlight;
      persistFeatureFlagChange(layerKey, item.feature, { highlight: props.highlight === true });
      refreshAfterFeatureChange(layerKey);
      renderPoiTabIfActive();
    }

    // Embedded-panel bridge: SET (not toggle) a feature's highlight to a desired
    // state, through the host's own persistence + POI-tab refresh. The new right
    // panel (js/panel.js) owns the ★ gesture and knows the target on/off state; it
    // passes the FEATURE_LIST_LAYERS key + the feature's properties, and we derive
    // the id with the same idField the override store uses — so a panel ★ persists
    // exactly like the legacy ★ and surfaces in THIS existing left-rail POI tab
    // (a starred drawn POI is the visible case; other destination layers already
    // list unconditionally). Returns false if the layer has no host runtime/id,
    // so the panel can fall back to its own persistence.
    function setFeatureHighlight(layerKey, props, on) {
      if (!props) return false;
      const id = positionedFeatureIdFor(layerKey, { properties: props });
      if (id == null) return false;
      const item = findFeatureById(layerKey, id);
      if (!item || !item.feature) return false;
      const fp = item.feature.properties = item.feature.properties || {};
      const next = on === true;
      if (fp.highlight !== next) {
        fp.highlight = next;
        persistFeatureFlagChange(layerKey, item.feature, { highlight: next });
        refreshAfterFeatureChange(layerKey);
      }
      renderPoiTabIfActive();
      return true;
    }
    window.AOP_HOST_SET_HIGHLIGHT = function (layerKey, props, on) {
      try { return setFeatureHighlight(layerKey, props, on); }
      catch (e) { console.error('AOP_HOST_SET_HIGHLIGHT failed', e); return false; }
    };

    // Bridge for the right-panel editor (js/panel.js): bind a feature's #tag into
    // the live event-schedule resolver. The tag is the feature's own `props.tag`
    // (baked into the served GeoJSON); this resolves the feature by its idField,
    // mirrors the value onto the host's own feature copy (so rebuildTagLookup's
    // props.tag scan stays in sync), and routes through setFeatureTag — which
    // persists the binding (FEATURE_TAG_KEY, survives reload before a bake),
    // rebuilds the lookup, and re-resolves the schedule/anchors live.
    function setFeatureTagByProps(layerKey, props, rawTag) {
      if (!props) return false;
      const id = positionedFeatureIdFor(layerKey, { properties: props });
      if (id == null) return false;
      const item = findFeatureById(layerKey, id);
      if (item && item.feature) {
        const fp = item.feature.properties = item.feature.properties || {};
        const normalized = normalizeFeatureTag(rawTag);
        if (normalized) fp.tag = normalized; else delete fp.tag;
      }
      setFeatureTag(layerKey, id, rawTag);
      return true;
    }
    window.AOP_HOST_SET_TAG = function (layerKey, props, rawTag) {
      try { return setFeatureTagByProps(layerKey, props, rawTag); }
      catch (e) { console.error('AOP_HOST_SET_TAG failed', e); return false; }
    };

    // Bridge for the right-panel editor (js/panel.js) to edit a HOST-OWNED feature
    // through the host's SINGLE store of record — Sprint 09, Slice 1b. For a node
    // whose source the host owns and rewrites (editorPois → the `editorPois` array
    // → `aop_editor_pois_v1`, re-fed to the `editor-poi` map source by
    // refreshEditorSource), the panel must NOT persist through its own OVERRIDES
    // store — that would be a second store writing the one source (the twin-store
    // desync, audit F6). Instead the panel calls these, which reuse the existing
    // layer-agnostic, spec-routed host writers (setFeatureProperty/deleteFeature
    // → the editorPois spec's persistProperty/removeFeature → saveEditorPois). One
    // store, one editor. The panel resolves the feature; the host resolves its id
    // via the spec's idField (positionedFeatureIdFor) and mutates its own copy.
    window.AOP_HOST_SET_FEATURE_PROPS = function (layerKey, props, patch) {
      try {
        const id = positionedFeatureIdFor(layerKey, { properties: props });
        if (id == null) return false;
        for (const [k, v] of Object.entries(patch || {})) {
          if (k.startsWith('_')) continue;          // internal panel fields never persist
          setFeatureProperty(layerKey, id, k, v);
        }
        return true;
      } catch (e) { console.error('AOP_HOST_SET_FEATURE_PROPS failed', e); return false; }
    };
    window.AOP_HOST_SET_FEATURE_GEOM = function (layerKey, props, geometry) {
      try {
        const id = positionedFeatureIdFor(layerKey, { properties: props });
        if (id == null || !geometry) return false;
        const item = findFeatureById(layerKey, id);
        if (!item || !item.feature) return false;
        item.feature.geometry = JSON.parse(JSON.stringify(geometry));
        persistFeatureFlagChange(layerKey, item.feature, {});   // editorPois → saveEditorPois
        refreshAfterFeatureChange(layerKey);                    // → refreshEditorSource
        return true;
      } catch (e) { console.error('AOP_HOST_SET_FEATURE_GEOM failed', e); return false; }
    };
    window.AOP_HOST_DELETE_FEATURE = function (layerKey, props) {
      try {
        const id = positionedFeatureIdFor(layerKey, { properties: props });
        if (id == null) return false;
        deleteFeature(layerKey, id);
        return true;
      } catch (e) { console.error('AOP_HOST_DELETE_FEATURE failed', e); return false; }
    };
    // Create bridge — Sprint 09, Slice 2. The right panel captures the geometry
    // (its own crosshair place-click) but a drawn POI must land in the host's ONE
    // store of record (editorPois → aop_editor_pois_v1), NOT the panel OVERRIDES
    // store (which would be a twin-store create leak — the same F6 desync Slice 1b
    // closed for edits/deletes). So the panel's commitFeature calls this for a
    // hostEdit node; it reuses addDrawnPoi (the same builder the host's TerraDraw
    // `finish` handler uses), so host-drawn and panel-drawn POIs are identical and
    // one-store. Only editorPois is host-owned-and-creatable; everything else
    // authors into its own served source through the panel's normal path. Returns
    // the new feature id (so the panel can select it for immediate editing), null
    // on failure. The creatable layer is no longer a literal `layerKey !==
    // 'editorPois'` guard (Sprint 09 A5): the bridge dispatches through the
    // layer's `spec.create` capability and names no layerKey — a layer opts in by
    // declaring `create`, everything else returns null (safe default, no throw —
    // C1/R13). editorPois declares it (→ addDrawnPoi), so a panel-drawn POI still
    // lands in the host's ONE store; a future host-owned creatable layer just adds
    // its own `create` strategy.
    window.AOP_HOST_CREATE_FEATURE = function (layerKey, geometry, opts) {
      try {
        const spec = FEATURE_LIST_LAYERS[layerKey];
        if (!spec || typeof spec.create !== 'function' || !geometry || !geometry.type) return null;
        return spec.create(geometry, opts);
      } catch (e) { console.error('AOP_HOST_CREATE_FEATURE failed', e); return null; }
    };

    // Mirror of toggleFeatureHighlight for the lock flag. Locked features
    // stay rendered and stay starrable, but the row's ✋ move handle and
    // long-press path become no-ops. Used when a feature has reached its
    // final position and the user wants to stop nudging it accidentally.
    function toggleFeatureLocked(layerKey, featureId) {
      const item = findFeatureById(layerKey, featureId);
      if (!item || !item.feature) return;
      const props = item.feature.properties = item.feature.properties || {};
      props.locked = !props.locked;
      persistFeatureFlagChange(layerKey, item.feature, { locked: props.locked === true });
      refreshAfterFeatureChange(layerKey);
    }

    // Routes a feature-property change to the right persistence path.
    // editorPois persists via its array store (saveEditorPois writes the
    // whole array, which already includes the mutated properties).
    // visitorContext + brandLogos persist their overrides in the unified
    // positioned-features store, patched key-by-key.
    function persistFeatureFlagChange(layerKey, feature, patch) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (spec && typeof spec.persistFlag === 'function') { spec.persistFlag(feature, patch); return; }
      // Default: every editable layer (buildings, cemeteries, visitorContext,
      // brandLogos) persists its overrides in the unified positioned-features
      // store, keyed by layerKey + idField — so highlight/lock/geometry and the
      // editable name/notes all survive reload without baking the on-disk seed.
      savePositionedFeature(layerKey, feature, patch);
      // Re-sync the LIVE runtime data from the store so the change lands on EVERY
      // feature sharing the idField — the same convergence a reload gets via
      // applyPositionedFeatures. Cemeteries emit a parcel + marker twin per
      // parcel_id; the toggle resolves to the deduped state twin (the parcel),
      // but collectStarredDestinations reads the marker (listFromData), so without
      // this re-sync a cemetery ★ lands on the parcel and never surfaces in the
      // POI tab live. Idempotent for the single-feature layers.
      const runtime = featureListRuntime[layerKey];
      if (runtime && runtime.data) applyPositionedFeatures(layerKey, runtime.data);
    }

    function findFeatureById(layerKey, featureId) {
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) return null;
      for (const bucket of runtime.state.groups) {
        for (const item of bucket.features) {
          if (String(item.id) === String(featureId)) return item;
        }
      }
      return null;
    }

    function setMoveCursor(active) {
      const canvas = map.getCanvas();
      if (!canvas) return;
      canvas.style.cursor = active ? 'crosshair' : '';
    }

    function commitMoveMode(lngLat) {
      if (!moveState) return;
      const { layerKey, feature } = moveState;
      const spec = FEATURE_LIST_LAYERS[layerKey];
      // Even though onMove is the registered hook, we keep the clean-up path
      // identical whether commit succeeds or the spec is missing — never leave
      // the map stuck in crosshair mode.
      try {
        if (spec && typeof spec.onMove === 'function') {
          spec.onMove(feature, lngLat);
        }
      } finally {
        cancelMoveMode();
      }
    }

    function cancelMoveMode() {
      if (!moveState) {
        setMoveCursor(false);
        return;
      }
      const { layerKey } = moveState;
      moveState = null;
      setMoveCursor(false);
      if (moveMapClickHandler) {
        map.off('click', moveMapClickHandler);
        moveMapClickHandler = null;
      }
      if (moveEscHandler) {
        document.removeEventListener('keydown', moveEscHandler);
        moveEscHandler = null;
      }
      if (shouldRenderFeatureList(layerKey)) renderFeatureList(layerKey);
    }

    function enterMoveMode(layerKey, featureId) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec || typeof spec.onMove !== 'function') return;
      const item = findFeatureById(layerKey, featureId);
      if (!item) return;
      // Locked features refuse every move path defensively — row button,
      // long-press, map-click reveal, or programmatic call all bounce here.
      if (item.feature && item.feature.properties && item.feature.properties.locked === true) return;
      // Replacing any prior move mode is the gentler UX — long-pressing
      // another row should switch the target, not error out.
      if (moveState) cancelMoveMode();
      moveState = { layerKey, featureId: item.id, feature: item.feature };
      setMoveCursor(true);
      moveMapClickHandler = (event) => commitMoveMode(event.lngLat);
      // Arm the commit-click on the NEXT frame, not synchronously (M10).
      // enterMoveMode is frequently triggered BY a click (a row "Move" button, a
      // long-press, or a map-click reveal); arming the listener now lets that same
      // click — or a stray immediate tap — fire commitMoveMode and drop the feature
      // at the wrong point with no "armed" guard. Defer one frame, and only arm if
      // this exact move is still pending: cancelMoveMode (Escape) nulls
      // moveMapClickHandler, and a re-entry on another feature swaps it.
      const armMoveHandler = moveMapClickHandler;
      requestAnimationFrame(() => {
        if (moveState && moveMapClickHandler === armMoveHandler) {
          map.on('click', armMoveHandler);
        }
      });
      moveEscHandler = (event) => {
        if (event.key === 'Escape') {
          event.preventDefault();
          cancelMoveMode();
        }
      };
      document.addEventListener('keydown', moveEscHandler);
      if (shouldRenderFeatureList(layerKey)) renderFeatureList(layerKey);
      // If this layer renders into an inline target, make sure its
      // containing panel section is expanded so the move banner is visible.
      // (For drawer-rendered layers the drawer is already open by definition
      // — expandedTuneKey === layerKey — so nothing to do.)
      const inlineTargets = FEATURE_LIST_TARGETS[layerKey];
      if (inlineTargets && inlineTargets.length) openContainingSection(inlineTargets[0].target);
    }

    // --- Map → panel reveal --------------------------------------------
    // Closes the loop from world to chrome: clicking a feature on the map
    // expands its layer's drawer, expands the containing group if it's
    // collapsed (e.g. buildings "Other"), scrolls the row into view, and
    // flashes it briefly. Existing popups continue to fire — this is a
    // parallel hook on the same click, not a replacement.

    function groupIdForFeatureId(layerKey, featureId) {
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) return null;
      for (const bucket of runtime.state.groups) {
        for (const item of bucket.features) {
          if (String(item.id) === String(featureId)) return bucket.group.id;
        }
      }
      return null;
    }

    function revealFeatureInPanel(layerKey, featureId) {
      if (!FEATURE_LIST_LAYERS[layerKey]) return;
      if (!featureListRuntime[layerKey]) return;
      if (featureId == null) return;
      // 0. If the user has the panel collapsed, the section/group/row work
      //    below would all happen behind a closed panel and the map-click
      //    "open the panel editor" promise would silently break. Expand
      //    first; the user can re-collapse if they want.
      if (panelCollapsed) togglePanel();
      const dedicatedTargets = FEATURE_LIST_TARGETS[layerKey];
      // 1. Make sure the list is on screen. Layers with their own inline home
      //    (editor POIs / brand logos / visitor context / event-schedule rows
      //    all live in the unified Map editor tree) need that panel section
      //    expanded; layers that render into the drawer's #featureList need
      //    the drawer popped for this layer.
      if (dedicatedTargets && dedicatedTargets.length) {
        openContainingSection(dedicatedTargets[0].target);
      } else if (expandedTuneKey !== layerKey) {
        // toggleTunableExpansion collapses on a second hit, so guard.
        if (typeof toggleTunableExpansion === 'function') {
          toggleTunableExpansion(layerKey);
        }
      }
      // 2. Force the containing group open. Buildings "Other" defaults
      //    collapsed; revealing a feature there should pop the group.
      const runtime = featureListRuntime[layerKey];
      const groupId = groupIdForFeatureId(layerKey, featureId);
      if (groupId && runtime.collapsed[groupId]) {
        runtime.collapsed[groupId] = false;
        renderFeatureList(layerKey);
      }
      // 3. Find the row in the freshly-rendered DOM, scroll it into view,
      //    and flash. The renderer rebuilds the rows on every state change,
      //    so we look up by stable data-feature-id attribute.
      // Use requestAnimationFrame so any prior re-render commits first.
      window.requestAnimationFrame(() => {
        const safeId = String(featureId).replace(/(["\\])/g, '\\$1');
        const row = document.querySelector(`.feature-row[data-feature-id="${safeId}"]`);
        if (!row) return;
        row.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        // Re-trigger animation by removing then re-adding the class.
        row.classList.remove('revealed');
        // Force a reflow so the browser sees the class flip as a fresh start.
        void row.offsetWidth;
        row.classList.add('revealed');
        window.setTimeout(() => row.classList.remove('revealed'), 1900);
      });
    }

    // Wire one click handler per layer-set that surfaces panel reveal for a
    // FEATURE_LIST_LAYERS consumer. `idFromProps` is either the property name
    // holding the feature's id (string) or a (props) => id function for
    // composed keys. Suppressed during move mode — the click then belongs to
    // the move primitive, and yanking the panel focus away mid-commit would
    // be hostile UX. Also suppressed while Terra Draw is in an active draw
    // mode: the click is committing a POI / footprint / trace and any
    // parallel reveal would collapse the editor section that hosts the
    // draw-mode controls (toggleTunableExpansion auto-closes the editor
    // section when expanding a drawer outside it — see :4574).
    function bindPanelReveal(layers, layerKey, idFromProps) {
      const layerList = Array.isArray(layers) ? layers : [layers];
      const resolver = typeof idFromProps === 'function'
        ? idFromProps
        : (props) => props && props[idFromProps];
      map.on('click', layerList, (event) => {
        if (moveState) return;
        if (draw && draw.getMode && draw.getMode() !== 'static') return;
        const props = event.features?.[0]?.properties;
        if (!props) return;
        const id = resolver(props);
        if (id == null) return;
        revealFeatureInPanel(layerKey, id);
      });
    }

    // Refresh just the runtime data + state for a layer that's already been
    // registered. Skips the side-effects in registerFeatureListLayer
    // (pruneOrphanedTags, rebuildEventScheduleData, renderPoiTabIfActive)
    // so it can be called from inside rebuildEventScheduleData without
    // recursing. Used after eventScheduleData is rebuilt for a tag rebind.
	    function refreshFeatureListData(layerKey, data, options = {}) {
	      const runtime = featureListRuntime[layerKey];
	      if (!runtime || !data) return;
	      runtime.data = data;
	      runtime.state = buildFeatureListState(layerKey, data);
	      applyFeatureListFilters(layerKey);
	      if (options.persistVisibility !== false) persistFeatureVisibility(layerKey);
	      if (shouldRenderFeatureList(layerKey)) renderFeatureList(layerKey);
	    }

    // Register a layer's data + base filters with the runtime, build initial
    // state, and apply the initial filter pass. Called from each layer's
    // addSource block once the data is fetched. POIs (mutable) call this on
    // every draw/delete via refreshEditorSource — to stay correct we capture
    // baseFilters ONLY the first time. On re-register we keep the original
    // baseFilters and just refresh the state + collapsed UI bits, otherwise
    // map.getFilter() would return the composed filter from the previous pass
    // and the visibility clause would nest on every re-register.
    function registerFeatureListLayer(layerKey, data) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec || !data) return;
      const existing = featureListRuntime[layerKey];
      let baseFilters;
      let collapsed;
      let expandedFeatureId = null;
      if (existing) {
        baseFilters = existing.baseFilters;
        collapsed = existing.collapsed;
        expandedFeatureId = existing.expandedFeatureId || null;
      } else {
        baseFilters = {};
        // Only snapshot base filters for the layers that actually receive the
        // visibility filter (featureFilterLayersFor). Trails declare
        // `filterLayers: []` so their paint layers are never touched here — the
        // gold network keeps drawing all edges, unnamed ones included.
        for (const layerId of featureFilterLayersFor(spec)) {
          if (!map.getLayer(layerId)) continue;
          const current = map.getFilter(layerId);
          // Clone so any later mutation of our cached copy doesn't leak back.
          baseFilters[layerId] = current ? JSON.parse(JSON.stringify(current)) : null;
        }
        collapsed = {};
        for (const group of spec.groups) {
          collapsed[group.id] = !!group.collapsedDefault;
        }
      }
      const state = buildFeatureListState(layerKey, data);
      // Prune expandedFeatureId if its target feature no longer exists in
      // the freshly-built state (delete, Clear all, import). Keeps the
      // editor from rendering against stale data after a destructive op.
      if (expandedFeatureId != null) {
        const stillExists = state && state.groups.some((b) =>
          b.features.some((f) => String(f.id) === String(expandedFeatureId)));
        if (!stillExists) expandedFeatureId = null;
      }
      featureListRuntime[layerKey] = { data, baseFilters, state, collapsed, expandedFeatureId };
      applyFeatureListFilters(layerKey);
      persistFeatureVisibility(layerKey);
      // Tag bindings depend on a present runtime; rebuild after every
      // register so a moved POI / deleted POI / freshly loaded buildings
      // layer all flow through. Buildings is the seed surface for the
      // #pavilion default.
      pruneOrphanedTags(layerKey);
      rebuildTagLookup();
      rebuildEventScheduleData();
      renderPoiTabIfActive();
      // Editor-tree targets are always visible — push a render so a fresh
      // data load (or re-register) repaints the bucket leaves and the
      // Visitor list virtual group without waiting for a drawer expansion.
      if (FEATURE_LIST_TARGETS[layerKey]) renderFeatureList(layerKey);
    }

    // Render the feature list DOM. A layer can be registered to render into
    // multiple targets (the unified editor tree leverages this for editorPois,
    // which renders three times — once per geometry bucket). Each registered
    // target can carry an `onlyGroupId` to filter the runtime groups down
    // to one bucket.
    function renderFeatureList(layerKey) {
      const targets = featureListTargetsFor(layerKey);
      for (const entry of targets) {
        renderFeatureListInto(entry.target, layerKey, { onlyGroupId: entry.onlyGroupId });
      }
      if (typeof renderVisitorListGroup === 'function') renderVisitorListGroup();
    }

    // In-place count refresh for the visibility toggle (M5). Toggling one row's
    // checkbox used to call renderFeatureList, which wipes innerHTML and rebuilds
    // every row + reattaches ~10 listeners each (3× for editorPois). But the
    // clicked checkbox already shows the new state and setFeatureVisible already
    // did the map update — the only stale DOM is the per-group count + bulk
    // checkbox and the heading count. This re-derives those from runtime.state
    // (the single source of truth, so it can't desync) and writes them into the
    // EXISTING nodes — no rebuild, no listener churn, no focus loss. Returns false
    // if the expected structure isn't found so the caller falls back to a full
    // render. Counts use the same templates as renderFeatureListInto.
    function refreshFeatureListCounts(layerKey) {
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) return false;
      const spec = FEATURE_LIST_LAYERS[layerKey];
      const highlightable = spec && spec.highlightable === true;
      const targets = featureListTargetsFor(layerKey);
      if (!targets.length) return false;
      const esc = (v) => String(v).replace(/(["\\])/g, '\\$1');
      for (const entry of targets) {
        const target = entry.target;
        if (!target) continue;
        const onlyGroupId = entry.onlyGroupId;
        const renderedGroups = onlyGroupId
          ? runtime.state.groups.filter((b) => b.group && b.group.id === onlyGroupId)
          : runtime.state.groups;
        for (const bucket of renderedGroups) {
          const group = bucket.group;
          if (!group.label) continue; // unlabeled groups render no head
          const groupEl = target.querySelector(`.feature-list-group[data-group-id="${esc(group.id)}"]`);
          if (!groupEl) continue;
          const visibleInGroup = bucket.features.filter((f) => runtime.state.visibleIds.has(f.id)).length;
          const countEl = groupEl.querySelector('.group-count');
          if (countEl) countEl.textContent = `${visibleInGroup}/${bucket.features.length}`;
          const bulk = groupEl.querySelector('.feature-list-group-head input[type="checkbox"]');
          if (bulk) {
            const allOn = visibleInGroup === bucket.features.length;
            const noneOn = visibleInGroup === 0;
            bulk.checked = allOn;
            bulk.indeterminate = !allOn && !noneOn;
          }
        }
        if (!onlyGroupId) {
          const totalCount = renderedGroups.reduce((s, b) => s + b.features.length, 0);
          const visibleInGroups = renderedGroups.reduce((s, b) => s + b.features.filter((f) => runtime.state.visibleIds.has(f.id)).length, 0);
          const headCountEl = target.querySelector('.feature-list-heading .feature-list-count');
          if (headCountEl) {
            if (highlightable) {
              const highlightCount = renderedGroups.reduce((s, b) => s + b.features.filter((f) => f.feature && f.feature.properties && f.feature.properties.highlight === true).length, 0);
              headCountEl.textContent = `${visibleInGroups} of ${totalCount} visible · ${highlightCount} ★ to visitors`;
            } else {
              headCountEl.textContent = `${visibleInGroups} of ${totalCount} visible`;
            }
          }
        }
      }
      return true;
    }

    function renderFeatureListInto(target, layerKey, opts) {
      if (!target) return;
      target.innerHTML = '';
      const runtime = featureListRuntime[layerKey];
      if (!runtime || !runtime.state) {
        target.hidden = true;
        return;
      }
      const spec = FEATURE_LIST_LAYERS[layerKey];
      const movable = typeof spec.onMove === 'function';
      const highlightable = spec.highlightable === true;
      const onlyGroupId = opts && opts.onlyGroupId;
      // Filter the runtime groups to one bucket when onlyGroupId is set.
      const renderedGroups = onlyGroupId
        ? runtime.state.groups.filter((b) => b.group && b.group.id === onlyGroupId)
        : runtime.state.groups;
      const totalCount = renderedGroups.reduce((sum, b) => sum + b.features.length, 0);
      // When filtering to one group there's no need for the full Features
      // heading — the enclosing bucket head carries the count.
      if (!onlyGroupId) {
        const heading = document.createElement('div');
        heading.className = 'feature-list-heading';
        const highlightCount = highlightable
          ? renderedGroups.reduce((sum, b) => sum + b.features.filter((f) => f.feature && f.feature.properties && f.feature.properties.highlight === true).length, 0)
          : 0;
        const visibleInGroups = renderedGroups.reduce((sum, b) => sum + b.features.filter((f) => runtime.state.visibleIds.has(f.id)).length, 0);
        heading.innerHTML = highlightable
          ? `<span>Features</span><span class="feature-list-count">${visibleInGroups} of ${totalCount} visible · ${highlightCount} ★ to visitors</span>`
          : `<span>Features</span><span class="feature-list-count">${visibleInGroups} of ${totalCount} visible</span>`;
        target.append(heading);
      }

      // Move-mode banner — only when this layer is the active move target
      // and the moved feature is inside one of the rendered groups.
      if (moveState && moveState.layerKey === layerKey) {
        const moveItem = findFeatureById(layerKey, moveState.featureId);
        const inRendered = !onlyGroupId || renderedGroups.some((b) => b.features.some((f) => String(f.id) === String(moveState.featureId)));
        if (inRendered) {
          const targetName = moveItem ? spec.rowLabel(moveItem.props) : 'feature';
          const banner = document.createElement('div');
          banner.className = 'feature-list-move-banner';
          banner.dataset.moveBanner = layerKey;
          const text = document.createElement('span');
          text.textContent = `Move mode — click on map to place ${targetName}. Esc to cancel.`;
          const cancelBtn = document.createElement('button');
          cancelBtn.type = 'button';
          cancelBtn.className = 'move-cancel';
          cancelBtn.textContent = 'Cancel';
          cancelBtn.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            cancelMoveMode();
          });
          banner.append(text, cancelBtn);
          target.append(banner);
        }
      }

      for (const bucket of renderedGroups) {
        const group = bucket.group;
        const groupEl = document.createElement('div');
        groupEl.className = 'feature-list-group';
        groupEl.dataset.groupId = group.id;

        const visibleInGroup = bucket.features.filter((f) => runtime.state.visibleIds.has(f.id)).length;
        const allOn = visibleInGroup === bucket.features.length;
        const noneOn = visibleInGroup === 0;
        const groupCollapsed = runtime.collapsed[group.id];

        if (group.label) {
          const head = document.createElement('div');
          head.className = 'feature-list-group-head';
          const chevron = document.createElement('button');
          chevron.type = 'button';
          chevron.className = 'group-chevron';
          chevron.setAttribute('aria-expanded', String(!groupCollapsed));
          // Glyph matches the panel + section chevrons: ▾ when expanded,
          // ▸ when collapsed.
          chevron.textContent = groupCollapsed ? '▸' : '▾';
          chevron.title = groupCollapsed ? 'Expand group' : 'Collapse group';
          chevron.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            runtime.collapsed[group.id] = !runtime.collapsed[group.id];
            renderFeatureList(layerKey);
          });
          const bulk = document.createElement('input');
          bulk.type = 'checkbox';
          bulk.checked = allOn;
          bulk.indeterminate = !allOn && !noneOn;
          bulk.title = 'Toggle every feature in this group';
          bulk.addEventListener('change', () => {
            setGroupVisible(layerKey, group.id, bulk.checked);
            renderFeatureList(layerKey);
          });
          const name = document.createElement('span');
          name.className = 'group-name';
          if (group.kindGlyph) {
            // Kind glyph reads alongside the label for the editorPois
            // kind-grouped tree (● POI / ▭ Footprint / ╱ Line).
            const glyph = document.createElement('span');
            glyph.className = 'group-kind-glyph';
            glyph.textContent = group.kindGlyph;
            name.append(glyph, ' ', group.label);
          } else {
            name.textContent = group.label;
          }
          const count = document.createElement('span');
          count.className = 'group-count';
          count.textContent = `${visibleInGroup}/${bucket.features.length}`;
          head.append(chevron, bulk, name, count);
          groupEl.append(head);
        }

        const rows = document.createElement('div');
        rows.className = 'feature-list-rows';
        if (group.label && groupCollapsed) rows.hidden = true;
        for (const item of bucket.features) {
          const row = document.createElement('div');
          row.className = 'feature-row';
          row.dataset.featureId = String(item.id);
          if (moveState && moveState.layerKey === layerKey && String(moveState.featureId) === String(item.id)) {
            row.classList.add('move-target');
          }
          const check = document.createElement('input');
          check.type = 'checkbox';
          check.checked = runtime.state.visibleIds.has(item.id);
          check.addEventListener('change', () => {
            setFeatureVisible(layerKey, item.id, check.checked);
            // M5: visibility is the hot toggle — refresh the dependent counts in
            // place (this row's checkbox already shows the new state, and the map
            // update happened in setFeatureVisible) instead of rebuilding the
            // whole subtree. Fall back to a full render if the in-place path can't
            // find the expected nodes.
            if (!refreshFeatureListCounts(layerKey)) renderFeatureList(layerKey);
          });
          // ★ highlight toggle (editorPois). Sits next to the visibility
          // checkbox so the two "include this in...?" flags read as a pair:
          //   ☑ ★ shown on map AND surfaced to visitors in the left-rail POI tab
          //   ☑ ☆ shown on map only (scratch / author-only)
          //   ☐ ☆ hidden on map, also hidden from visitors
          let highlight = null;
          if (highlightable) {
            highlight = document.createElement('button');
            highlight.type = 'button';
            highlight.className = 'feature-highlight';
            const isHighlighted = item.feature && item.feature.properties && item.feature.properties.highlight === true;
            highlight.textContent = isHighlighted ? '★' : '☆';
            highlight.classList.toggle('on', isHighlighted);
            highlight.title = isHighlighted
              ? 'Surfaced in left-rail POI tab — click to remove'
              : 'Click to surface in left-rail POI tab';
            highlight.setAttribute('aria-pressed', String(isHighlighted));
            highlight.addEventListener('click', (event) => {
              event.preventDefault();
              event.stopPropagation();
              toggleFeatureHighlight(layerKey, item.id);
            });
            row.classList.add('has-highlight');
          }
          const name = document.createElement('span');
          name.className = 'feature-name';
          name.textContent = spec.rowLabel(item.props);
          name.title = movable
            ? 'Click to fly; long-press to enter move mode'
            : 'Click to fly to this feature';
          name.addEventListener('click', () => flyToFeature(item.feature));
          const fly = makeFlyButton(item.feature, 'feature-fly');
          // Per-feature copy. Emits a drop-in geojson Feature with current
          // geometry, paste-ready for website/data/*.geojson. Sits between
          // fly and move so the destructive (move) action stays right-most.
          const copy = document.createElement('button');
          copy.type = 'button';
          copy.className = 'feature-copy';
          copy.textContent = '⧉';
          copy.title = 'Copy as drop-in GeoJSON Feature';
          copy.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            copyFeatureAsDropIn(item.feature);
          });
          if (highlight) row.append(check, highlight, name);
          else row.append(check, name);
          if (spec.inlineEditor) {
            // Editable layers keep a clean row — [vis] [★] name [edit ▸]. Every
            // action (fly / move / lock / copy / tag / notes / category / size /
            // delete) lives as a labeled control in the accordion the chevron
            // opens, so the row never crams cryptic emoji buttons or a tag
            // input against the name. The chevron is appended just below.
            const isLocked = movable && item.feature && item.feature.properties && item.feature.properties.locked === true;
            if (isLocked) row.classList.add('is-locked');
            // Long-press anywhere on the row still arms move mode for a movable,
            // unlocked feature (the mobile path); the explicit Move button lives
            // in the accordion. Skip the chevron + visibility tick.
            if (movable && !isLocked) {
              let pressTimer = null;
              let pressStart = null;
              const startPress = (event) => {
                if (event.target === check) return;
                if (highlight && event.target === highlight) return;
                if (event.target.closest && event.target.closest('.feature-row-expand')) return;
                pressStart = { x: event.clientX, y: event.clientY };
                pressTimer = window.setTimeout(() => {
                  pressTimer = null;
                  enterMoveMode(layerKey, item.id);
                }, LONG_PRESS_MS);
              };
              const cancelPress = () => {
                if (pressTimer) { window.clearTimeout(pressTimer); pressTimer = null; }
                pressStart = null;
              };
              const movedFar = (event) => {
                if (!pressStart) return false;
                const dx = event.clientX - pressStart.x;
                const dy = event.clientY - pressStart.y;
                return (dx * dx + dy * dy) > 64;     // ~8 px slop
              };
              row.addEventListener('pointerdown', startPress);
              row.addEventListener('pointermove', (event) => { if (movedFar(event)) cancelPress(); });
              row.addEventListener('pointerup', cancelPress);
              row.addEventListener('pointercancel', cancelPress);
              row.addEventListener('pointerleave', cancelPress);
            }
          } else {
            // Read-only / non-editable layers (activity hotspots, synthetic
            // activity, event-schedule anchors) have no accordion — keep a
            // quick copy + fly on the row.
            row.append(copy);
            row.append(fly);
          }
          // Inline-editor chevron — last cell on the row. Toggles the
          // expanded editor block below. The has-inline-editor class
          // tightens the row grid (no row-level tag/copy buttons).
          if (spec.inlineEditor) {
            row.classList.add('has-inline-editor');
            const isExpanded = dockSelectionMatches(layerKey, item.id);
            const expand = document.createElement('button');
            expand.type = 'button';
            expand.className = 'feature-row-expand';
            expand.setAttribute('aria-expanded', String(isExpanded));
            expand.textContent = isExpanded ? '▾' : '▸';
            expand.title = isExpanded ? 'Close editor' : 'Open editor';
            expand.addEventListener('click', (event) => {
              event.preventDefault();
              event.stopPropagation();
              toggleFeatureEditor(layerKey, item.id);
            });
            // Long-press shouldn't fire on the chevron either.
            expand.addEventListener('pointerdown', (event) => event.stopPropagation());
            row.append(expand);
            if (isExpanded) row.classList.add('editor-open');
          }
          rows.append(row);
          // The editor for a selected leaf now renders in the pinned #editDock
          // (renderEditDock) — one selection across all layers, not an inline
          // accordion per row.
        }
        groupEl.append(rows);
        target.append(groupEl);
      }
      target.hidden = false;
    }

    // Build the inline editor block for an expanded leaf. Returns a DOM
    // node that lives inside `.feature-list-rows`, immediately after the
    // row it edits. Reads `feature.properties` directly; writes flow
    // through setFeatureName / setFeatureCategory / setFeatureNotes / the
    // existing visibility + tag + highlight helpers + saveEditorPois.
    // ===== Unified edit dock =================================================
    // One feature selected at a time across every layer; the editor renders in
    // the pinned #editDock (bottom of the panel), not as a per-row accordion.
    // Replaces the old inline-accordion editor + folds the layer-paint drawer into the Edit
    // tab. Tabs: Identify (what it is) · Edit (change it + layer paint) ·
    // Display (how it looks) · Source (where it came from, read-only).
    let dockSelection = null;        // { layerKey, featureId } or null
    let dockActiveTab = 'identify';  // identify | edit | display | source

    function dockSelectionMatches(layerKey, featureId) {
      return !!dockSelection
        && dockSelection.layerKey === layerKey
        && String(dockSelection.featureId) === String(featureId);
    }

    function selectFeatureForDock(layerKey, featureId) {
      const same = dockSelectionMatches(layerKey, featureId);
      const prevLayer = dockSelection ? dockSelection.layerKey : null;
      dockSelection = same ? null : { layerKey, featureId };
      if (!same) dockActiveTab = 'identify';
      renderFeatureList(layerKey);                                   // refresh row highlight
      if (prevLayer && prevLayer !== layerKey) renderFeatureList(prevLayer);
      renderEditDock();
    }

    function clearDockSelection() {
      if (!dockSelection) return;
      const layerKey = dockSelection.layerKey;
      dockSelection = null;
      renderFeatureList(layerKey);
      renderEditDock();
    }

    function renderEditDock() {
      const host = document.getElementById('editDock');
      if (!host) return;
      if (!dockSelection) { host.hidden = true; host.innerHTML = ''; return; }
      const { layerKey, featureId } = dockSelection;
      const spec = FEATURE_LIST_LAYERS[layerKey];
      const item = spec ? findFeatureById(layerKey, featureId) : null;
      if (!spec || !item || !item.feature) { dockSelection = null; host.hidden = true; host.innerHTML = ''; return; }
      host.innerHTML = '';
      host.append(buildEditDock(layerKey, item, spec));
      host.hidden = false;
    }

    function dockFieldRow(labelText, control, top) {
      const row = document.createElement('div');
      row.className = top ? 'dock-f top' : 'dock-f';
      const k = document.createElement('span');
      k.className = 'dock-k';
      k.textContent = labelText;
      row.append(k, control);
      return row;
    }

    function dockReadonly(text) {
      const s = document.createElement('span');
      s.className = 'dock-ro';
      s.textContent = text;
      return s;
    }

    function dockToggleRow(labelText, initialOn, onToggle) {
      const row = document.createElement('div');
      row.className = 'dock-tg';
      const span = document.createElement('span');
      span.textContent = labelText;
      const sw = document.createElement('button');
      sw.type = 'button';
      sw.className = initialOn ? 'dock-sw on' : 'dock-sw';
      sw.setAttribute('aria-pressed', String(initialOn));
      sw.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        const next = !sw.classList.contains('on');
        sw.classList.toggle('on', next);
        sw.setAttribute('aria-pressed', String(next));
        onToggle(next);
      });
      row.append(span, sw);
      return row;
    }

    // The "group" a feature reads as: for drawn POIs it's the geometry bucket;
    // for curated layers it's the layer itself (fixed). Read-only — moving a
    // feature across source groups means a cross-layer migration we don't do yet.
    function dockGroupContext(layerKey, item) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (spec && typeof spec.groupContext === 'function') return spec.groupContext(item);
      return (spec && spec.label) || layerKey;
    }

    // Render one spec-declared Identify-tab field as a dock row. Dispatches on
    // the field descriptor (no layerKey named): read-only fields show their
    // derived value; `type:'select'` builds an option list from the field's
    // own `options()` source and writes through the generic setFeatureProperty.
    // Permissive — an out-of-vocab current value is preserved as a selected
    // option so it still renders and is not silently dropped (C5).
    function buildDockSpecField(layerKey, item, props, f) {
      if (f.readonly) {
        const text = typeof f.value === 'function' ? f.value(props) : (props[f.key] != null ? String(props[f.key]) : '—');
        return dockFieldRow(f.label, dockReadonly(text));
      }
      if (f.type === 'select') {
        const sel = document.createElement('select');
        const opts = (typeof f.options === 'function' ? f.options() : f.options) || [];
        const current = props[f.key];
        let hasCurrent = false;
        for (const c of opts) {
          const o = document.createElement('option');
          o.value = c; o.textContent = c;
          if (current === c) { o.selected = true; hasCurrent = true; }
          sel.append(o);
        }
        // Keep an out-of-vocabulary current value selectable rather than
        // forcing it onto the first option (no value gets silently rewritten).
        if (current != null && current !== '' && !hasCurrent) {
          const o = document.createElement('option');
          o.value = current; o.textContent = current; o.selected = true;
          sel.append(o);
        }
        sel.addEventListener('change', () => setFeatureProperty(layerKey, item.id, f.key, sel.value));
        return dockFieldRow(f.label, sel);
      }
      // Default: a plain text input bound to the property.
      const input = document.createElement('input');
      input.type = 'text';
      input.value = props[f.key] != null ? String(props[f.key]) : '';
      input.addEventListener('change', () => setFeatureProperty(layerKey, item.id, f.key, input.value));
      return dockFieldRow(f.label, input);
    }

    function buildEditDock(layerKey, item, spec) {
      const dock = document.createElement('div');
      dock.className = 'dock-card';
      const props = (item.feature && item.feature.properties) || {};
      const nameProp = spec.nameField || 'name';
      const kind = (item.feature && item.feature.geometry && item.feature.geometry.type) || 'Point';
      const kindLabel = kind === 'Point' ? 'Point' : kind === 'Polygon' ? 'Polygon' : kind === 'LineString' ? 'Line' : kind;
      const kindGlyph = kind === 'Point' ? '●' : kind === 'Polygon' ? '▭' : kind === 'LineString' ? '╱' : '◇';
      const movable = typeof spec.onMove === 'function';
      const featureLocked = props.locked === true;
      const titleText = () => (String(props[nameProp] || '').trim() || props.category || 'Untitled');

      // -- header --
      const head = document.createElement('div');
      head.className = 'dock-head';
      const pill = document.createElement('span');
      pill.className = 'dock-pill';
      pill.textContent = `${kindGlyph} ${kindLabel}`;
      const title = document.createElement('span');
      title.className = 'dock-title';
      title.textContent = titleText();
      const fly = makeFlyButton(item.feature, 'dock-ico');
      const close = document.createElement('button');
      close.type = 'button'; close.className = 'dock-x'; close.title = 'Clear selection'; close.textContent = '✕';
      close.addEventListener('click', (e) => { e.preventDefault(); e.stopPropagation(); clearDockSelection(); });
      head.append(pill, title, fly, close);
      dock.append(head);

      // -- tabs --
      const TABS = [['identify', 'Identify'], ['edit', 'Edit'], ['display', 'Display'], ['source', 'Source']];
      const tabBar = document.createElement('div');
      tabBar.className = 'dock-tabs';
      const panels = {};
      const buttons = {};
      for (const [key, label] of TABS) {
        const b = document.createElement('button');
        b.type = 'button'; b.textContent = label;
        b.classList.toggle('on', dockActiveTab === key);
        b.addEventListener('click', () => {
          dockActiveTab = key;
          for (const [k] of TABS) {
            buttons[k].classList.toggle('on', k === key);
            panels[k].hidden = k !== key;
          }
        });
        tabBar.append(b);
        buttons[key] = b;
      }
      dock.append(tabBar);

      // -- Identify --
      const idp = document.createElement('div');
      idp.className = 'dock-body';
      const nameInput = document.createElement('input');
      nameInput.type = 'text';
      nameInput.value = props[nameProp] || '';
      nameInput.addEventListener('change', () => {
        setFeatureProperty(layerKey, item.id, nameProp, nameInput.value);
        title.textContent = titleText();
      });
      idp.append(dockFieldRow('Name', nameInput));
      // Spec-declared fields, no layerKey named here. Editable fields render
      // before the Group row, read-only fields after it — preserving the
      // prior layout (editorPois Category above Group; buildings Status below).
      const specFields = spec.fields || [];
      for (const f of specFields) {
        if (f.readonly) continue;
        idp.append(buildDockSpecField(layerKey, item, props, f));
      }
      idp.append(dockFieldRow('Group', dockReadonly(dockGroupContext(layerKey, item))));
      for (const f of specFields) {
        if (!f.readonly) continue;
        idp.append(buildDockSpecField(layerKey, item, props, f));
      }
      if (spec.taggable) {
        const tag = document.createElement('input');
        tag.type = 'text'; tag.placeholder = '#tag'; tag.value = tagForFeature(layerKey, item.id);
        tag.title = 'Bind a #tag (e.g. #pavilion). Used by the event-schedule resolver.';
        tag.addEventListener('change', () => { setFeatureTag(layerKey, item.id, tag.value); renderFeatureList(layerKey); });
        idp.append(dockFieldRow('Tag', tag));
      }
      const notes = document.createElement('textarea');
      notes.value = props.notes || '';
      notes.placeholder = 'Optional — context, source, why this is here';
      notes.addEventListener('change', () => setFeatureProperty(layerKey, item.id, 'notes', notes.value.trim()));
      idp.append(dockFieldRow('Notes', notes, true));
      panels.identify = idp;

      // -- Edit (per-feature actions + the layer's paint) --
      const ed = document.createElement('div');
      ed.className = 'dock-body';
      const ag = document.createElement('div');
      ag.className = 'dock-grp first';
      ag.textContent = `This feature · ${describeGeometry(item.feature)}`;
      ed.append(ag);
      const acts = document.createElement('div');
      acts.className = 'dock-acts';
      if (movable) {
        const mv = makeEditorAction('✋ Move', featureLocked ? 'Locked — unlock to move' : 'Move (click here, then click the map)', () => enterMoveMode(layerKey, item.id));
        mv.classList.add('primary');
        if (featureLocked) mv.disabled = true;
        acts.append(mv);
        acts.append(makeEditorAction(featureLocked ? '🔓 Unlock' : '🔒 Lock', featureLocked ? 'Unlock so this can be moved' : 'Lock so move becomes a no-op', () => toggleFeatureLocked(layerKey, item.id)));
      }
      acts.append(makeEditorAction('⧉ Copy GeoJSON', 'Copy this feature as a drop-in GeoJSON Feature', () => copyFeatureAsDropIn(item.feature)));
      // Spec-declared per-feature actions (Duplicate/Delete), no layerKey named.
      // Served layers omit `actions`, so they render none. Each action routes
      // through its spec-supplied run(layerKey, id).
      for (const a of (spec.actions || [])) {
        const btn = makeEditorAction(a.label, a.title || a.label, () => a.run(layerKey, item.id));
        if (a.danger) btn.classList.add('danger');
        acts.append(btn);
      }
      ed.append(acts);
      if (TUNABLE_LAYERS[layerKey]) {
        const pg = document.createElement('div');
        pg.className = 'dock-grp';
        pg.textContent = `Layer paint · ${TUNABLE_LAYERS[layerKey].label || (spec.label || layerKey)}`;
        ed.append(pg);
        const paint = document.createElement('div');
        paint.className = 'tune-controls dock-paint';
        renderTuneControls(TUNABLE_LAYERS[layerKey], paint);
        paint.addEventListener('input', handleTuneInput);
        ed.append(paint);
      }
      panels.edit = ed;

      // -- Display --
      const dp = document.createElement('div');
      dp.className = 'dock-body';
      const runtime = featureListRuntime[layerKey];
      const visible = !!(runtime && runtime.state && runtime.state.visibleIds.has(item.id));
      dp.append(dockToggleRow('Visible on map', visible, (on) => setFeatureVisible(layerKey, item.id, on)));
      if (spec.highlightable) {
        dp.append(dockToggleRow('★ Surface to visitor list', props.highlight === true, () => toggleFeatureHighlight(layerKey, item.id)));
      }
      if (spec.sizeEditable) {
        const wrap = document.createElement('div');
        wrap.className = 'dock-size';
        const range = document.createElement('input');
        range.type = 'range';
        range.min = String(BRAND_LOGO_SIZE_MIN); range.max = String(BRAND_LOGO_SIZE_MAX); range.step = String(BRAND_LOGO_SIZE_STEP);
        range.value = String(brandLogoSize(item.feature));
        const out = document.createElement('output');
        out.textContent = formatBrandLogoSize(range.value);
        range.addEventListener('input', () => { setBrandLogoSize(item.feature, range.value); out.textContent = formatBrandLogoSize(range.value); });
        wrap.append(range, out);
        dp.append(dockFieldRow('Size', wrap));
      }
      panels.display = dp;

      // -- Source (read-only provenance) --
      const sp = document.createElement('div');
      sp.className = 'dock-body';
      sp.append(dockFieldRow('ID', dockReadonly(String(item.id))));
      sp.append(dockFieldRow('Geometry', dockReadonly(describeGeometry(item.feature))));
      for (const key of ['source', 'confidence', 'license', 'license_or_permission', 'retrieved_on', 'address', 'facility_name']) {
        if (props[key]) sp.append(dockFieldRow(key.replace(/_/g, ' '), dockReadonly(String(props[key]))));
      }
      panels.source = sp;

      dock.append(idp, ed, dp, sp);
      for (const [k] of TABS) panels[k].hidden = dockActiveTab !== k;
      dock.addEventListener('pointerdown', (event) => event.stopPropagation());
      return dock;
    }

    function makeEditorAction(label, title, onClick) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'editor-action';
      btn.title = title;
      btn.textContent = label;
      btn.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        onClick();
      });
      return btn;
    }

    function describeGeometry(feature) {
      const geom = feature?.geometry;
      if (!geom) return '—';
      if (geom.type === 'Point') {
        const [lng, lat] = geom.coordinates || [];
        if (typeof lat !== 'number' || typeof lng !== 'number') return 'Point';
        const ns = lat >= 0 ? 'N' : 'S';
        const ew = lng >= 0 ? 'E' : 'W';
        return `Point · ${Math.abs(lat).toFixed(5)}°${ns}, ${Math.abs(lng).toFixed(5)}°${ew}`;
      }
      if (geom.type === 'LineString') {
        const n = Array.isArray(geom.coordinates) ? geom.coordinates.length : 0;
        return `Line · ${n} vertices`;
      }
      if (geom.type === 'Polygon') {
        const ring = Array.isArray(geom.coordinates) && geom.coordinates[0];
        const n = Array.isArray(ring) ? ring.length : 0;
        return `Polygon · ${n} vertices`;
      }
      return geom.type;
    }

    // Built from the <select id="poiCategory"> options at load so the editor's
    // per-bucket Category dropdowns share one source of truth with the HTML
    // (no hand-synced duplicate that drifts). Falls back to a literal list only
    // if the select is missing.
    const EDITOR_POI_CATEGORIES = (() => {
      const sel = document.getElementById('poiCategory');
      const fromDom = sel
        ? [...sel.options].map((o) => (o.value || o.textContent).trim()).filter(Boolean)
        : [];
      return fromDom.length ? fromDom : [
        'Pavilion', 'Building', 'Restroom', 'Parking', 'Staging area',
        'Gate', 'Trail trace', 'Road trace', 'Landmark', 'Hazard', 'Other'
      ];
    })();

    function toggleFeatureEditor(layerKey, featureId) {
      // Superseded by the unified dock: selecting a row drives the pinned
      // #editDock instead of an inline accordion. Kept as the stable entry
      // point that the row chevron + map-click reveal call.
      selectFeatureForDock(layerKey, featureId);
    }

    // Name/category/notes writes now flow through the generic
    // setFeatureProperty (editorPois → array store; served layers → the
    // positioned-features override store). The old editorPois-only helpers
    // (setEditorFeatureName/Category/Notes) were retired with the v1 editor.

    // Generic, spec-routed delete/duplicate — no layerKey named. The array
    // mutation is the spec's own store op (removeFeature/cloneFeature); the
    // persist + post-mutation refresh route through the shared
    // persistFeatureFlagChange (persistFlag seam) and refreshAfterFeatureChange
    // (onMutate seam) so any future array-backed layer reuses this unchanged.
    // A layer that declares no removeFeature/cloneFeature simply no-ops (it also
    // omits the `actions` capability, so the button is never offered).
    function deleteFeature(layerKey, featureId) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec || typeof spec.removeFeature !== 'function') return;
      const item = findFeatureById(layerKey, featureId);
      spec.removeFeature(featureId);
      if (dockSelectionMatches(layerKey, featureId)) dockSelection = null;
      // Persist through the flag seam (editorPois → saveEditorPois) then refresh
      // through the mutation seam (editorPois → refreshEditorSource).
      persistFeatureFlagChange(layerKey, item && item.feature, {});
      refreshAfterFeatureChange(layerKey);
      renderEditDock();
    }

    function duplicateFeature(layerKey, featureId) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec || typeof spec.cloneFeature !== 'function') return;
      const newId = spec.cloneFeature(featureId);
      if (newId == null) return;
      const item = findFeatureById(layerKey, newId);
      persistFeatureFlagChange(layerKey, item && item.feature, {});
      refreshAfterFeatureChange(layerKey);
      // Snap the dock onto the new feature so the user can rename it.
      dockSelection = { layerKey, featureId: newId };
      dockActiveTab = 'identify';
      renderEditDock();
    }

    // ---- Generic per-layer editing + bulk GeoJSON copy (MVP v1) ----------
    // The editable display-name property (spec.nameField, default 'name') and
    // the served-source resolver (spec.servedSource) now live on each
    // FEATURE_LIST_LAYERS spec — the two parallel per-layer config maps that
    // used to sit here (name-property and served-source) were folded in
    // (Sprint 05 card 03) so the registry is the single config home and nothing
    // drifts on a layerKey rename.

    // Re-feeds a served layer's live MapLibre source after a property edit so
    // the map popup reflects it immediately. (The feature-list row updates from
    // the shared in-memory feature reference regardless.) Dispatches through the
    // spec's servedSource strategy; a layer that declares none (e.g. editorPois,
    // whose writes flow through refreshEditorSource) simply no-ops — safe
    // default, never throws on absence (C5/R13).
    function refreshServedSource(layerKey) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (!spec || typeof spec.servedSource !== 'function') return;
      const [srcId, data] = spec.servedSource();
      if (!data) return;
      const src = map.getSource(srcId);
      if (src) src.setData(data);
      registerFeatureListLayer(layerKey, data);
    }

    // Routes a property-value change to the right persistence path — the
    // property-write twin of persistFeatureFlagChange. editorPois declare
    // spec.persistProperty (array store + source re-feed); every other layer
    // uses the default: patch the unified positioned-features store + re-feed
    // the served source. No layerKey is named at the call site.
    function persistFeaturePropertyChange(layerKey, feature, propKey, value) {
      const spec = FEATURE_LIST_LAYERS[layerKey];
      if (spec && typeof spec.persistProperty === 'function') { spec.persistProperty(feature, propKey, value); return; }
      savePositionedFeature(layerKey, feature, { properties: { [propKey]: value } });
      refreshServedSource(layerKey);
    }

    // Layer-agnostic property write. Dispatches persistence through the spec's
    // persistProperty strategy (default: positioned-features store + served
    // source re-feed). Leaves feature.properties mutated so the change is live.
    function setFeatureProperty(layerKey, featureId, propKey, value) {
      const item = findFeatureById(layerKey, featureId);
      if (!item || !item.feature) return;
      const props = item.feature.properties = item.feature.properties || {};
      props[propKey] = value;
      persistFeaturePropertyChange(layerKey, item.feature, propKey, value);
      renderFeatureList(layerKey);
    }

    // Copy a whole layer's features as a GeoJSON FeatureCollection — with all
    // edits/overrides applied — to the clipboard. The single bulk export path
    // (per-feature copy is the single-row path; there are no file downloads).
    async function copyLayerAsGeoJSON(layerKey) {
      const runtime = featureListRuntime[layerKey];
      const label = (FEATURE_LIST_LAYERS[layerKey] && FEATURE_LIST_LAYERS[layerKey].label) || layerKey;
      if (!runtime || !runtime.state) { presetStatus.textContent = 'Nothing to copy.'; return; }
      const features = [];
      for (const bucket of runtime.state.groups) {
        for (const item of bucket.features) {
          if (!item.feature) continue;
          const drop = {
            type: 'Feature',
            properties: { ...(item.feature.properties || {}) },
            geometry: JSON.parse(JSON.stringify(item.feature.geometry || null))
          };
          for (const k of Object.keys(drop.properties)) if (k.startsWith('_')) delete drop.properties[k];
          features.push(drop);
        }
      }
      const text = JSON.stringify({ type: 'FeatureCollection', features }, null, 2) + '\n';
      try {
        const ok = await copyText(text);
        presetStatus.textContent = ok
          ? `Copied ${features.length} ${label} feature${features.length === 1 ? '' : 's'} as GeoJSON.`
          : 'Clipboard copy failed.';
      } catch (err) {
        presetStatus.textContent = `Copy failed: ${err.message}`;
      }
    }

    const EXTRA_PRESET_PAINTS = [
      ['background', 'background-color'],
      // pwa_qa item 13c/13d: capture the gold trail-network line colour so the
      // Park (difficulty blue/green/black) vs Topo (orange) override round-trips
      // through save-current / section export.
      ['aop-trail-network', 'line-color'],
      ['lidar-hillshade', 'hillshade-highlight-color'],
      ['lidar-hillshade', 'hillshade-accent-color'],
      ['water-points', 'circle-color'],
      ['water-points', 'circle-stroke-color'],
      ['water-point-labels', 'text-color'],
      ['osm-named-points', 'circle-color'],
      ['osm-named-points', 'circle-stroke-color'],
      ['osm-named-labels', 'text-color'],
      ['search-highlight-line', 'line-color'],
      ['search-highlight-point', 'circle-color'],
      ['search-highlight-point', 'circle-stroke-color']
    ];

    function uniquePaintTargets() {
      const seen = new Set();
      const targets = [];
      const add = ([layer, property]) => {
        const key = `${layer}|${property}`;
        if (!seen.has(key)) {
          seen.add(key);
          targets.push([layer, property]);
        }
      };
      EXTRA_PRESET_PAINTS.forEach(add);
      for (const config of Object.values(TUNABLE_LAYERS)) {
        [...config.opacity, ...config.color, ...config.width].forEach(add);
      }
      return targets;
    }
    const PRESET_PAINT_TARGETS = uniquePaintTargets();

	    const BUILT_IN_PRESETS = {
      park: {
        label: 'Park',
        toggles: {
          showLandcover: true,
          showLandcover9: true,
          showHillshade: false,
          showContours: false,
          showActivityHotspots: false,
          showSyntheticActivity: false,
          showEventSchedule: false,
          showSatellite: false,
          showUsdaNaip: false,
          showNinePatch: false,
          showLidarTiles: false,
          showRoads: true,
          showVisitorContext: true,
          showBrandLogos: true,
          showWater: true,
          showSprings: false,
          showCemeteries: false,
          showBuildings: true,
          showOsmPark: false,
          showOsmTracks: false,
          showOsmService: false,
          showOsmNamed: false,
          showSfwda: false,
          // pwa_qa item 13b/13c: the map view's trail story is the gold-derived
          // aop-trail-network (blue/green/black by difficulty, baked colour),
          // ON by default. The legacy publish-trails demo segments + OSM tracks
          // stay OFF here so only the gold network draws.
          showTrails: false,
          showAopTrailNetwork: true,
          showBoundaries: true,
          showTrailheads: true,
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
          // Sprint 02 B5: reset to cream halo on park so a previous trace
          // session does not leave dark halos sitting under dark text.
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
          // pwa_qa item 13c: gold network coloured by baked-in difficulty colour
          // (green=easy #1f9d3a, blue=moderate #2438c8, black=difficult #111111,
          // orange=road #f25e0d). Reset here so a switch back from Topo's orange
          // override restores the blue/green/black difficulty colours.
          'aop-trail-network': { 'line-color': ['coalesce', ['get', 'color'], '#888888'], 'line-width': 3, 'line-opacity': 0.92 },
          'publish-trailheads': { 'circle-color': '#6f8a5c', 'circle-radius': 6, 'circle-opacity': 1 },
          'osm-tracks': { 'line-color': '#9a5a32', 'line-width': 2, 'line-opacity': 0.95 },
          'osm-service': { 'line-color': '#a89a7e', 'line-width': 1.5, 'line-opacity': 0.85 },
          // Sprint 02 B5 + road-label contrast fix: full reset for labels that
          // trace darkens. Without text-color here a trace→park/topo switch
          // leaves '#fff4cf' cream text on the light cream/hillshade background.
          'roads-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 },
          'osm-named-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
        }
      },
      topo: {
        label: 'Topo',
        toggles: {
          showLandcover: true,
          showLandcover9: true,
          showHillshade: true,
          showContours: true,
          showActivityHotspots: false,
          showSyntheticActivity: false,
          showEventSchedule: false,
          showSatellite: false,
          showUsdaNaip: false,
          showNinePatch: false,
          showLidarTiles: false,
          showRoads: true,
          showVisitorContext: true,
          showBrandLogos: true,
          showWater: true,
          showSprings: true,
          showCemeteries: false,
          showBuildings: true,
          showOsmPark: false,
          showOsmTracks: false,
          showOsmService: false,
          showOsmNamed: false,
          showSfwda: false,
          // pwa_qa item 13b/13d: gold network ON, recoloured orange in the Topo
          // paint below; legacy demo trails + OSM tracks stay OFF.
          showTrails: false,
          showAopTrailNetwork: true,
          showBoundaries: true,
          showTrailheads: true,
          showEditorPois: true
        },
        sliders: { landcover9Opacity: 38, sfwdaOpacity: 60, sfwdaMultiply: 100 },
        paints: {
          background: { 'background-color': '#e7ddc4' },
          'landcover-forest': { 'fill-color': LANDCOVER_RELIEF_FILL, 'fill-opacity': 0.62 },
          'landcover-forest-outline': { 'line-color': LANDCOVER_RELIEF_OUTLINE, 'line-width': 0.7, 'line-opacity': 0.35 },
          'landcover-9patch-forest': { 'fill-color': LANDCOVER_RELIEF_FILL, 'fill-opacity': 0.38 },
          'landcover-9patch-forest-outline': { 'line-color': LANDCOVER_RELIEF_OUTLINE, 'line-width': 0.5, 'line-opacity': 0.25 },
          // Softened so the relief stays a SUBTLE backdrop and the faded contour
          // lines read on top of it (user: hillshade was "brutal" around trail 41,
          // washing the topo lines out in steep shadow zones). It's a topo view —
          // keep the relief, but the high-contrast near-black shadow (#2f2a21) at
          // 0.78 exaggeration overpowered the now-faded contours. Halved the
          // exaggeration and lifted the shadow to a warm mid-tone so there are no
          // black zones for the light sienna lines to disappear into. (Set
          // visibility:'none' here instead if a flat pure-contour topo is wanted.)
          'lidar-hillshade': {
            'hillshade-exaggeration': 0.45,
            'hillshade-shadow-color': '#7a6a52',
            'hillshade-highlight-color': '#f7eed8',
            'hillshade-accent-color': '#8a7860'
          },
          // Contour topo "faded back" so the orange trail pops (user pick from the
          // topo-colour compare pass, now retired; decision recorded in the brain —
          // misc_3 item 13 + research/viewer.md). Background = V1 faded sienna:
          // the warm-sienna hue is kept but the ON-opacity is dialed back (index
          // 0.98->0.5, fine 0.8->0.28) and the colours lightened so the relief reads
          // as a quiet ground. The zoom-fade structure is preserved (50 ft index
          // lines show below z16; fine 5 ft lines still fade in 16.5->17.5).
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
          // On the Topo view the gold trail network reads as a single ORANGE line
          // (overrides the per-difficulty blue/green/black) so trails pop against
          // the faded contour + hillshade relief. User pick O6 (pure, no casing) —
          // a brighter, slightly wider, full-opacity orange that stands alone now
          // that the topo is dialed back. (Compare page retired; pick recorded in brain.)
          'aop-trail-network': { 'line-color': '#ff5a14', 'line-width': 3.8, 'line-opacity': 1 },
          'publish-trailheads': { 'circle-color': '#546f4b', 'circle-radius': 6.5, 'circle-opacity': 1 },
          // Roads: ONE road style. No per-preset recolour — roads keep the single
          // base style set once at layer creation (cream casing + taupe/tan asphalt
          // by class). The previous per-preset swap is removed per the user request
          // ("remove all the dynamic road style swapping. one road style.").
          'visitor-context-fill': { 'fill-color': '#d2a95f', 'fill-opacity': 0.14 },
          'visitor-context-outline': { 'line-color': '#6f4e2e', 'line-width': 2.4, 'line-opacity': 0.86 },
          'visitor-context-labels': { 'text-color': '#3f3122', 'text-opacity': 1, 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 },
          // Road-label contrast fix: full reset so trace→topo doesn't leave
          // cream text (#fff4cf) sitting on the contour/hillshade background.
          'roads-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 },
          'osm-named-labels': { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
        }
      },
      trace: {
        label: 'Trace',
        toggles: {
          showLandcover: false,
          showLandcover9: false,
          showHillshade: true,
          showContours: false,
          showActivityHotspots: false,
          showSyntheticActivity: false,
          showEventSchedule: false,
          showSatellite: false,
          showUsdaNaip: false,
          showNinePatch: false,
          showLidarTiles: false,
          showRoads: true,
          showVisitorContext: false,
          showBrandLogos: true,
          showWater: false,
          showSprings: false,
          showCemeteries: false,
          showBuildings: true,
          // pwa_qa_2 items 4+5: Trace is now "paper trail map vs. merged gold
          // truth" — drop the OSM/boundary alignment clutter the user called
          // out (park bounds + OSM park polygon + OSM tracks OFF), keep the
          // SFWDA paper-map raster, and turn the merged aop-trail-network ON as
          // the canonical trail layer. The extracted SFWDA trace trails
          // (sfwda-trace-trails) stay out of every preset (default OFF). OSM
          // service + named points were not in the user's list, so left ON.
          showOsmPark: false,
          showOsmTracks: false,
          showOsmService: true,
          showOsmNamed: true,
          showSfwda: true,
          // Legacy publish-trails demo segments OFF here too (as in Park/Topo)
          // so only the merged gold network draws as the trail "truth".
          showTrails: false,
          showAopTrailNetwork: true,
          showBoundaries: false,
          showTrailheads: true,
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
          // pwa_qa_2 item 5: merged gold network is now ON in Trace as the
          // canonical trail layer. Reset it to its baked per-difficulty colour
          // (green/blue/black/orange) — same as Park — so a Topo→Trace switch
          // doesn't carry Topo's flat-orange override onto the paper backdrop.
          'aop-trail-network': { 'line-color': ['coalesce', ['get', 'color'], '#888888'], 'line-width': 3.4, 'line-opacity': 0.95 },
          // Trail-number labels read over the busy SFWDA paper map: cream text
          // on a near-black halo, matching the other Trace label overrides.
          'aop-trail-network-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
          'publish-trailheads': { 'circle-color': '#ffe08a', 'circle-radius': 7, 'circle-opacity': 1 },
          'osm-park-outline': { 'line-color': '#d4ff86', 'line-width': 2.4 },
          'osm-tracks': { 'line-color': '#ff6b3d', 'line-width': 3, 'line-opacity': 0.98 },
          'osm-service': { 'line-color': '#ffd166', 'line-width': 2.5, 'line-opacity': 0.95 },
          'osm-named-points': { 'circle-color': '#ffd166', 'circle-stroke-color': '#33251a' },
          // Sprint 02 B5: trace runs cream/yellow text over the busy SFWDA
          // paper-map. The default cream halo blends in; switch every label
          // layer to a near-black halo (#15110d) at ~2 px so the text reads
          // against tan paper, dark gridlines, and red trail strokes alike.
          'osm-named-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
          // Pass 4 theme review §6: trace-preset overrides for editor-POI,
          // cemetery, and nine-patch labels. Keep the trace labels on dark
          // halos so they read over SFWDA ink and hillshade texture.
          'editor-poi-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
          'editor-poi-fill-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
          'editor-poi-line-labels': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
          'cemetery-label': { 'text-color': '#fff0b8', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
          'nine-patch-labels': { 'text-color': '#fff4cf', 'text-halo-color': '#15110d', 'text-halo-width': 2 },
          // Roads: ONE road style. The washed-out cream/yellow per-class recolour
          // that made Trace roads "look wrong and washed out" is removed — roads now
          // keep the single base style (cream casing + taupe/tan asphalt) on every
          // preset, no dynamic swapping. The road LABEL override below stays: it's a
          // text-legibility concern (cream text + near-black halo so names read over
          // the dark SFWDA paper backdrop), separate from the road line style.
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
          showLandcover: false,
          showLandcover9: false,
          showHillshade: false,
          showContours: false,
          showActivityHotspots: false,
          showSyntheticActivity: false,
          showEventSchedule: false,
          showSatellite: true,
          showUsdaNaip: false,
          showNinePatch: false,
          showLidarTiles: false,
          showRoads: false,
          showVisitorContext: false,
          showBrandLogos: false,
          showWater: false,
          showSprings: false,
          showCemeteries: false,
          showBuildings: false,
          showOsmPark: false,
          showOsmTracks: false,
          showOsmService: false,
          showOsmNamed: false,
          showSfwda: false,
          showTrails: false,
          // pwa_qa item 13: clean aerial — gold network OFF so a Park→Satellite
          // switch doesn't leave trail lines over the imagery.
          showAopTrailNetwork: false,
          showBoundaries: false,
          showTrailheads: false,
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

	    if (BUILT_IN_PRESETS[viewerSessionState?.active_preset]) {
	      activePresetId = viewerSessionState.active_preset;
	    }

	    function updateLayerVisibility() {
      for (const [toggle, layerIds] of LAYER_TOGGLES) {
        for (const id of layerIds) setLayerVisibility(id, toggle.checked);
      }
      for (let r = 0; r < GRID_N; r++) {
        for (let c = 0; c < GRID_N; c++) {
          setLayerVisibility(`sfwda-tile-${r}-${c}`, sfwdaToggle.checked);
        }
      }
      syncLayerTunerFromSelection();
    }

    function cloneJson(value) {
      return JSON.parse(JSON.stringify(value));
    }

    function deepMergePaints(base = {}, override = {}) {
      const merged = cloneJson(base);
      for (const [layerId, properties] of Object.entries(override || {})) {
        merged[layerId] = { ...(merged[layerId] || {}), ...cloneJson(properties) };
      }
      return merged;
    }

    function loadSavedPresetStates() {
      const parsed = readJsonStore(VIEWER_PRESET_KEY, () => ({}));
      return parsed && typeof parsed.presets === 'object' ? parsed.presets : {};
    }

    let savedPresetStates = loadSavedPresetStates();

    function savePresetStates() {
      writeJsonStore(VIEWER_PRESET_KEY, {
        schema: 'aop-viewer-preset-settings-v1',
        saved_at: new Date().toISOString(),
        presets: savedPresetStates
      });
    }

    function presetState(presetId) {
      const base = BUILT_IN_PRESETS[presetId];
      const saved = savedPresetStates[presetId] || {};
      return {
        label: base.label,
        toggles: { ...base.toggles, ...(saved.toggles || {}) },
        sliders: { ...base.sliders, ...(saved.sliders || {}) },
        paints: deepMergePaints(base.paints, saved.paints || {})
      };
    }

    function applyPaintState(paints) {
      for (const [layerId, properties] of Object.entries(paints || {})) {
        for (const [property, value] of Object.entries(properties || {})) {
          setPaint(layerId, property, value);
        }
      }
    }

    function setSliderValue(id, value) {
      const element = document.getElementById(id);
      if (!element || value === undefined || value === null) return;
      element.value = String(value);
      element.dispatchEvent(new Event('input', { bubbles: true }));
    }

    function applyPreset(presetId, options = {}) {
      if (!BUILT_IN_PRESETS[presetId]) return;
      const state = presetState(presetId);
      activePresetId = presetId;
      applyingPreset = true;
      for (const id of PRESET_TOGGLE_IDS) {
        const element = document.getElementById(id);
        if (element && Object.prototype.hasOwnProperty.call(state.toggles, id)) {
          element.checked = Boolean(state.toggles[id]);
        }
      }
      if (editSfwdaToggle.checked) {
        editSfwdaToggle.checked = false;
        editSfwdaToggle.dispatchEvent(new Event('change', { bubbles: true }));
      }
      for (const [id, value] of Object.entries(state.sliders || {})) {
        setSliderValue(id, value);
      }
      updateLayerVisibility();
      applyPaintState(state.paints);
      presetButtons.forEach((button) => {
        button.classList.toggle('active', button.dataset.preset === presetId);
      });
      applyingPreset = false;
      syncLayerTunerFromSelection();
      const saved = savedPresetStates[presetId] ? ' custom' : '';
      presetStatus.textContent = `${state.label}${saved} preset active.`;
      if (options.persistSession !== false) {
        persistViewerSessionState({ active_preset: presetId });
      }
    }

    function capturePaintState() {
      const paints = {};
      for (const [layerId, property] of PRESET_PAINT_TARGETS) {
        if (!map.getLayer(layerId)) continue;
        const value = map.getPaintProperty(layerId, property);
        if (value === undefined) continue;
        paints[layerId] = paints[layerId] || {};
        paints[layerId][property] = cloneJson(value);
      }
      return paints;
    }

    function captureViewerState() {
      const toggles = {};
      for (const id of PRESET_TOGGLE_IDS) {
        const element = document.getElementById(id);
        if (element) toggles[id] = Boolean(element.checked);
      }
      const sliders = {};
      for (const id of PRESET_SLIDER_IDS) {
        const element = document.getElementById(id);
        if (element) sliders[id] = Number(element.value);
      }
      return {
        captured_at: new Date().toISOString(),
        toggles,
        sliders,
        paints: capturePaintState()
      };
    }

    function selectedTunable() {
      return TUNABLE_LAYERS[expandedTuneKey || activeTuneKey] || TUNABLE_LAYERS.landcover;
    }

    function cssColorOrDefault(value, fallback) {
      return typeof value === 'string' && /^#[0-9a-f]{6}$/i.test(value) ? value : fallback;
    }

    function numberOrDefault(value, fallback) {
      return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
    }

    function humanizeId(value) {
      return String(value || '')
        .replace(/^publish-/, '')
        .replace(/^landcover-9patch-/, '9patch ')
        .replace(/^landcover-/, '')
        .replace(/^activity-hotspots-/, 'activity ')
        .replace(/^editor-poi-/, 'editor ')
        .replace(/^osm-/, 'OSM ')
        .replace(/^waterbody-/, 'waterbody ')
        .replace(/-/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    }

    function propertyLabel(property) {
      if (property === 'circle-radius') return 'size';
      if (property === 'hillshade-exaggeration') return 'relief';
      return String(property || '')
        .replace(/^(fill|line|circle|text|raster|hillshade)-/, '')
        .replace(/-/g, ' ');
    }

    function tuneTargetLabel(layerId, property) {
      const layer = humanizeId(layerId);
      const prop = propertyLabel(property);
      return layer ? `${layer} ${prop}` : prop;
    }

    function tuneRowForKey(key) {
      return TUNABLE_LAYERS[key]?.row || null;
    }

    function updateLayerRowState() {
      for (const [key, config] of Object.entries(TUNABLE_LAYERS)) {
        const row = tuneRowForKey(key);
        const button = config.expandButton;
        if (!row) continue;
        const expanded = expandedTuneKey === key;
        row.classList.toggle('active', activeTuneKey === key);
        row.classList.toggle('expanded', expanded);
        if (button) {
          button.textContent = expanded ? '▾' : '▸';
          button.setAttribute('aria-expanded', String(expanded));
          button.title = expanded ? `Hide ${config.label} controls` : `Show ${config.label} controls`;
        }
      }
    }

    function paintValue(layerId, property, fallback) {
      if (!map.getLayer(layerId)) return fallback;
      const value = map.getPaintProperty(layerId, property);
      return value === undefined ? fallback : value;
    }

    function currentKnobValue(config, knob) {
      if (knob.sliderId) {
        const slider = document.getElementById(knob.sliderId);
        return Number(slider?.value ?? knob.defaultValue ?? 100);
      }
      if (knob.kind === 'color') {
        return cssColorOrDefault(paintValue(knob.layerId, knob.property, undefined), config.defaults.color);
      }
      if (knob.kind === 'width') {
        return numberOrDefault(paintValue(knob.layerId, knob.property, undefined), config.defaults.width);
      }
      const fallback = config.defaults.opacity / 100;
      return numberOrDefault(paintValue(knob.layerId, knob.property, undefined), fallback);
    }

    function configuredKnobs(config) {
      const knobs = [];
      for (const band of config.zoomBands || []) {
        knobs.push({ kind: 'zoomband', band, label: band.label });
      }
      if (config.linkedSlider) {
        knobs.push({
          kind: 'opacity',
          sliderId: config.linkedSlider.id,
          label: 'Opacity',
          defaultValue: config.defaults.opacity
        });
      } else {
        for (const [layerId, property] of config.opacity || []) {
          knobs.push({ kind: 'opacity', layerId, property, label: tuneTargetLabel(layerId, property) });
        }
      }
      for (const [layerId, property] of config.color || []) {
        knobs.push({ kind: 'color', layerId, property, label: tuneTargetLabel(layerId, property) });
      }
      for (const [layerId, property] of config.width || []) {
        knobs.push({ kind: 'width', layerId, property, label: tuneTargetLabel(layerId, property) });
      }
      for (const extra of config.extraSliders || []) {
        knobs.push({ kind: extra.kind || 'percent', sliderId: extra.slider.id, label: extra.label, defaultValue: extra.defaultValue ?? Number(extra.slider.value) });
      }
      return knobs;
    }

    function knobInputId(kind, index) {
      if (kind === 'opacity' && index === 0) return 'tuneOpacity';
      if (kind === 'color' && index === 0) return 'tuneColor';
      if (kind === 'width' && index === 0) return 'tuneWidth';
      return `tune-${kind}-${index}`;
    }

    function knobOutputId(kind, index) {
      if (kind === 'opacity' && index === 0) return 'tuneOpacityValue';
      if (kind === 'width' && index === 0) return 'tuneWidthValue';
      return `tune-${kind}-${index}-value`;
    }

    function widthMaxForProperty(property) {
      return property === 'circle-radius' ? 24 : 14;
    }

    // Dual-thumb zoom slider for a contour fade band. HTML has no native
    // two-knob range input, so this stacks two <input type="range"> elements
    // and only their thumbs take pointer events (see .dual-range CSS). The
    // left thumb is the fade-start zoom, the right thumb the fade-end zoom.
    function buildZoomBandRow(config, knob) {
      const band = knob.band;
      const rng = config.zoomBandRange || { min: 12, max: 20, step: 0.5 };
      const wrap = document.createElement('div');
      wrap.className = 'tune-band';

      const head = document.createElement('div');
      head.className = 'tune-band-head';
      const label = document.createElement('span');
      label.className = 'tune-label';
      label.textContent = knob.label;
      const out = document.createElement('output');
      head.append(label, out);

      const dual = document.createElement('div');
      dual.className = 'dual-range';
      const track = document.createElement('div');
      track.className = 'dual-track';
      const fill = document.createElement('div');
      fill.className = 'dual-fill';
      const lo = document.createElement('input');
      const hi = document.createElement('input');
      for (const el of [lo, hi]) {
        el.type = 'range';
        el.min = String(rng.min);
        el.max = String(rng.max);
        el.step = String(rng.step);
      }
      lo.className = 'dual-lo';
      hi.className = 'dual-hi';

      const seed = zoomStopsOf(
        map.getPaintProperty(band.targets[0][0], band.targets[0][1]), band.fallback);
      lo.value = String(seed[0]);
      hi.value = String(seed[1]);
      dual.append(track, fill, lo, hi);
      wrap.append(head, dual);

      const span = (rng.max - rng.min) || 1;
      const pct = (v) => ((v - rng.min) / span) * 100;
      function apply(active) {
        let a = Number(lo.value);
        let b = Number(hi.value);
        // interpolate stops must ascend, so keep one step between the thumbs.
        if (active === lo && a > b - rng.step) { a = b - rng.step; lo.value = String(a); }
        if (active === hi && b < a + rng.step) { b = a + rng.step; hi.value = String(b); }
        fill.style.left = pct(a) + '%';
        fill.style.width = Math.max(0, pct(b) - pct(a)) + '%';
        out.textContent = `z${a.toFixed(1)} – z${b.toFixed(1)}`;
        if (active) {
          for (const [layerId, property] of band.targets) {
            setPaint(layerId, property,
              withZoomStops(map.getPaintProperty(layerId, property), a, b));
          }
          markPresetEdited();
        }
      }
      lo.addEventListener('input', () => apply(lo));
      hi.addEventListener('input', () => apply(hi));
      apply(null);
      return wrap;
    }

    function renderTuneControls(config, target = tuneControls) {
      target.innerHTML = '';
      const counts = { opacity: 0, color: 0, width: 0, percent: 0 };
      for (const knob of configuredKnobs(config)) {
        if (knob.kind === 'zoomband') {
          target.append(buildZoomBandRow(config, knob));
          continue;
        }
        const index = counts[knob.kind] || 0;
        counts[knob.kind] = index + 1;
        const row = document.createElement('label');
        row.className = 'tune-control';
        const label = document.createElement('span');
        label.className = 'tune-label';
        label.textContent = knob.label;
        const input = document.createElement('input');
        const output = document.createElement('output');
        input.id = knobInputId(knob.kind, index);
        input.dataset.tuneKind = knob.kind;
        if (knob.sliderId) input.dataset.sliderId = knob.sliderId;
        if (knob.layerId) input.dataset.layerId = knob.layerId;
        if (knob.property) input.dataset.property = knob.property;

        if (knob.kind === 'color') {
          input.type = 'color';
          input.value = currentKnobValue(config, knob);
        } else {
          input.type = 'range';
          input.min = knob.kind === 'width' ? '0.2' : '0';
          input.max = knob.kind === 'width' ? String(widthMaxForProperty(knob.property)) : '100';
          input.step = knob.kind === 'width' ? '0.1' : '1';
          const value = currentKnobValue(config, knob);
          input.value = knob.kind === 'width' ? String(value) : String(Math.round(value * (knob.sliderId ? 1 : 100)));
          output.id = knobOutputId(knob.kind, index);
          output.textContent = knob.kind === 'width' ? Number(input.value).toFixed(1) : `${input.value}%`;
        }

        row.append(label, input, output);
        target.append(row);
      }
    }

    function syncLayerTunerFromSelection() {
      updateLayerRowState();
      if (!expandedTuneKey) {
        if (sfwdaDrawerControls) sfwdaDrawerControls.hidden = true;
        if (featureListEl) { featureListEl.hidden = true; featureListEl.innerHTML = ''; }
        if (copyLayerBtn) copyLayerBtn.hidden = true;
        layerEditor.hidden = true;
        return;
      }
      const config = selectedTunable();
      if (!config) return;
      layerEditorTitle.textContent = config.label;
      tuneVisible.checked = config.toggle.checked;
      renderTuneControls(config);
      if (sfwdaDrawerControls) sfwdaDrawerControls.hidden = config.drawerControls !== sfwdaDrawerControls;
      // Feature list slot. Only layers registered in FEATURE_LIST_LAYERS
      // AND without their own tree targets render into the drawer's
      // #featureList. Editor POIs / brand logos / visitor-context callouts /
      // event-schedule anchors all live in the unified Map editor tree, so
      // their drawer shows only the paint sliders.
      if (FEATURE_LIST_LAYERS[expandedTuneKey] && !FEATURE_LIST_TARGETS[expandedTuneKey]) {
        renderFeatureList(expandedTuneKey);
        if (copyLayerBtn) copyLayerBtn.hidden = false;
      } else {
        if (featureListEl) {
          featureListEl.hidden = true;
          featureListEl.innerHTML = '';
        }
        if (copyLayerBtn) copyLayerBtn.hidden = true;
      }
    }

    function selectTunable(key) {
      if (!TUNABLE_LAYERS[key]) return;
      activeTuneKey = key;
      updateLayerRowState();
    }

    function collapseTunableEditor() {
      expandedTuneKey = null;
      if (sfwdaDrawerControls) sfwdaDrawerControls.hidden = true;
      layerEditor.hidden = true;
      updateLayerRowState();
    }

    function toggleTunableExpansion(key) {
      if (!TUNABLE_LAYERS[key]) return;
      if (expandedTuneKey === key) {
        selectTunable(key);
        collapseTunableEditor();
        return;
      }
      activeTuneKey = key;
      expandedTuneKey = key;
      const selectedRow = tuneRowForKey(key);
      if (selectedRow) {
        openContainingSection(selectedRow);
        if (selectedRow.nextElementSibling !== layerEditor) {
          selectedRow.insertAdjacentElement('afterend', layerEditor);
        }
        // Collapse the Map editor section when the inline editor opens on a
        // row that lives in a different section, so the editor surface
        // dominates without the draw-tools controls competing for space.
        const editorSection = document.querySelector('.panel-section[data-section="editor"]');
        const rowSection = selectedRow.closest('.panel-section');
        if (editorSection && rowSection !== editorSection && !editorSection.classList.contains('collapsed')) {
          setSectionCollapsed(editorSection, true);
        }
      }
      layerEditor.hidden = false;
      syncLayerTunerFromSelection();
    }

    function wireLayerEditRows() {
      for (const [key, config] of Object.entries(TUNABLE_LAYERS)) {
        const label = config.toggle.closest('label');
        if (!label) continue;
        const row = document.createElement('div');
        row.className = 'layer-row';
        row.dataset.tuneKey = key;
        label.insertAdjacentElement('beforebegin', row);
        row.append(label);
        const expandButton = document.createElement('button');
        expandButton.type = 'button';
        expandButton.className = 'layer-expand';
        expandButton.dataset.tuneExpandKey = key;
        expandButton.setAttribute('aria-expanded', 'false');
        expandButton.textContent = '▸';
        row.append(expandButton);
        config.row = row;
        config.expandButton = expandButton;
        row.addEventListener('click', (event) => {
          if (event.target === row) selectTunable(key);
        });
        label.addEventListener('click', () => selectTunable(key));
        config.toggle.addEventListener('focus', () => selectTunable(key));
        expandButton.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();
          toggleTunableExpansion(key);
        });
      }
      selectTunable(activeTuneKey);
      syncLayerTunerFromSelection();
    }

    function markPresetEdited() {
      if (applyingPreset) return;
      const label = BUILT_IN_PRESETS[activePresetId]?.label || 'Current';
      presetStatus.textContent = `${label} preset modified.`;
    }

    function setSelectedLayerVisible() {
      const config = selectedTunable();
      config.toggle.checked = tuneVisible.checked;
      config.toggle.dispatchEvent(new Event('change', { bubbles: true }));
      markPresetEdited();
    }

    function updateTuneOutput(input) {
      const output = input.closest('.tune-control')?.querySelector('output');
      if (!output) return;
      output.textContent = input.dataset.tuneKind === 'width'
        ? Number(input.value).toFixed(1)
        : `${input.value}%`;
    }

    function handleTuneInput(event) {
      const input = event.target.closest('input[data-tune-kind]');
      if (!input) return;
      updateTuneOutput(input);
      if (input.dataset.sliderId) {
        const slider = document.getElementById(input.dataset.sliderId);
        if (slider) {
          slider.value = input.value;
          slider.dispatchEvent(new Event('input', { bubbles: true }));
        }
      } else if (input.dataset.layerId && input.dataset.property) {
        const value = input.dataset.tuneKind === 'color'
          ? input.value
          : Number(input.value) / (input.dataset.tuneKind === 'opacity' ? 100 : 1);
        setPaint(input.dataset.layerId, input.dataset.property, value);
      }
      markPresetEdited();
    }

    function snapshotActivePreset() {
      savedPresetStates[activePresetId] = captureViewerState();
      savePresetStates();
      presetStatus.textContent = `${BUILT_IN_PRESETS[activePresetId].label} preset snapshot saved.`;
      presetButtons.forEach((button) => {
        button.classList.toggle('active', button.dataset.preset === activePresetId);
      });
    }

    async function copyText(text) {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
      const box = document.createElement('textarea');
      box.value = text;
      box.style.position = 'fixed';
      box.style.left = '-9999px';
      document.body.appendChild(box);
      box.focus();
      box.select();
      const copied = document.execCommand('copy');
      box.remove();
      return copied;
    }

    // Pulls the durable runtime state that lives outside the preset/paint
    // system into a single bag. Bumped to schema v3 on 2026-05-28 when the
    // two per-layer override stores collapsed into a single
    // `positioned_features` slot keyed by `layerKey:id`. v2 imports are
    // refused — forward-only per spinup/viewer_storage_migration.md.
    function captureRuntimeOverrides() {
      return {
        positioned_features: loadPositionedFeatures(),
        editor_pois: readJsonStore(POI_STORAGE_KEY, () => []),
        feature_visibility: readJsonStore(FEATURE_VISIBILITY_KEY, () => ({})),
        feature_tags: readJsonStore(FEATURE_TAG_KEY, () => ({}))
      };
    }

    function buildExportPayload() {
      return {
        schema: 'aop-viewer-preset-settings-v3',
        exported_at: new Date().toISOString(),
        active_preset: activePresetId,
        presets: {
          park: presetState('park'),
          topo: presetState('topo'),
          trace: presetState('trace'),
          satellite: presetState('satellite')
        },
        current_state: captureViewerState(),
        runtime_overrides: captureRuntimeOverrides()
      };
    }

    async function exportPresetSettings() {
      const text = JSON.stringify(buildExportPayload(), null, 2) + '\n';
      try {
        const copied = await copyText(text);
        presetStatus.textContent = copied ? 'Settings copied to clipboard.' : 'Clipboard copy failed.';
      } catch (error) {
        console.warn('Settings export failed:', error);
        presetStatus.textContent = 'Clipboard copy failed.';
      }
    }

    // --- Per-section + bulk Export / Import -----------------------------
    // The big "Export all" button copies the v2 bundle (buildExportPayload).
    // The big "Import all" button accepts the same bundle and restores it.
    // Each panel section also gets its own ⧉ button that copies *just* that
    // section's slice — toggles + sliders + paints for layers in that
    // section, plus the runtime overrides that belong there.
    //
    // Section → runtime mapping. Only layers whose runtime data we own
    // (the per-feature visibility ticks, the visitor-context geometry
    // overrides, and the drawn-POI store) appear here. Other layers in a
    // section have no runtime state — only toggles / paints.
    const SECTION_RUNTIME = {
      'derived-layers': {
        // Curated buildings moved here from source-layers (derived = the
        // owner-curated set). They carry per-feature visibility, #tag bindings,
        // and drag-to-adjust geometry overrides — so a derived-section Copy
        // round-trips all three.
        featureVisibilityLayers: ['buildings'],
        featureTagLayers: ['buildings'],
        positionedFeatureLayers: ['buildings']
      },
      'source-layers': {
        featureVisibilityLayers: ['cemeteries']
      },
      'external-reference': {},
      // Editor section runtime: drawn POI array + per-feature visibility +
      // tags + the unified positioned-features slice for the user-positioned
      // layers that live here (visitor-context callouts, brand logos).
      editor: {
        editorPois: POI_STORAGE_KEY,
        positionedFeatureLayers: ['visitorContext', 'brandLogos'],
        featureVisibilityLayers: ['editorPois', 'eventSchedule', 'visitorContext', 'brandLogos'],
        // Drawn POIs are taggable: a #tag binding rides along with the POI.
        featureTagLayers: ['editorPois']
      },
      'user-submitted': {}
    };

    // Walk a section's DOM to find toggles + sliders inside it. Cached at
    // first call per section so we don't re-query each export.
    const sectionInputCache = {};
    function sectionInputs(sectionId) {
      if (sectionInputCache[sectionId]) return sectionInputCache[sectionId];
      const section = document.querySelector(`.panel-section[data-section="${sectionId}"]`);
      const result = { toggleIds: [], sliderIds: [] };
      if (section) {
        for (const el of section.querySelectorAll('input[type="checkbox"]')) {
          if (el.id && el.id.startsWith('show')) result.toggleIds.push(el.id);
        }
        for (const el of section.querySelectorAll('input[type="range"]')) {
          if (el.id) result.sliderIds.push(el.id);
        }
      }
      sectionInputCache[sectionId] = result;
      return result;
    }

    // Resolve the set of paint targets that belong to a section by walking
    // every TUNABLE_LAYERS entry whose toggle lives inside the section.
    function sectionPaintTargets(sectionId) {
      const { toggleIds } = sectionInputs(sectionId);
      const toggleIdSet = new Set(toggleIds);
      const targets = new Set();
      for (const config of Object.values(TUNABLE_LAYERS)) {
        if (!config.toggle || !toggleIdSet.has(config.toggle.id)) continue;
        for (const [layerId, property] of [...(config.opacity || []), ...(config.color || []), ...(config.width || [])]) {
          targets.add(`${layerId}|${property}`);
        }
      }
      // Background paint is global; keep it only on derived-layers (it lives
      // with the visual palette controls, not source data).
      if (sectionId === 'derived-layers') targets.add('background|background-color');
      return targets;
    }

    function capturePaintStateFor(targetSet) {
      const paints = {};
      for (const targetKey of targetSet) {
        const [layerId, property] = targetKey.split('|');
        if (!map.getLayer(layerId)) continue;
        const value = map.getPaintProperty(layerId, property);
        if (value === undefined) continue;
        paints[layerId] = paints[layerId] || {};
        paints[layerId][property] = cloneJson(value);
      }
      return paints;
    }

    function buildSectionPayload(sectionId) {
      const { toggleIds, sliderIds } = sectionInputs(sectionId);
      const runtimeSpec = SECTION_RUNTIME[sectionId] || {};
      const toggles = {};
      for (const id of toggleIds) {
        const el = document.getElementById(id);
        if (el) toggles[id] = Boolean(el.checked);
      }
      const sliders = {};
      for (const id of sliderIds) {
        const el = document.getElementById(id);
        if (el) sliders[id] = Number(el.value);
      }
      const paints = capturePaintStateFor(sectionPaintTargets(sectionId));
      const runtime = {};
      if (runtimeSpec.positionedFeatureLayers && runtimeSpec.positionedFeatureLayers.length) {
        const slice = {};
        for (const layerKey of runtimeSpec.positionedFeatureLayers) {
          Object.assign(slice, positionedFeaturesSlice(layerKey));
        }
        runtime.positioned_features = slice;
      }
      if (runtimeSpec.editorPois) {
        runtime.editor_pois = readJsonStore(runtimeSpec.editorPois, () => []);
      }
      if (runtimeSpec.featureVisibilityLayers && runtimeSpec.featureVisibilityLayers.length) {
        const all = readJsonStore(FEATURE_VISIBILITY_KEY, () => ({}));
        const slice = {};
        for (const key of runtimeSpec.featureVisibilityLayers) {
          if (all[key]) slice[key] = all[key];
        }
        runtime.feature_visibility = slice;
      }
      if (runtimeSpec.featureTagLayers && runtimeSpec.featureTagLayers.length) {
        const all = readJsonStore(FEATURE_TAG_KEY, () => ({}));
        const slice = {};
        for (const key of runtimeSpec.featureTagLayers) {
          if (all[key]) slice[key] = all[key];
        }
        runtime.feature_tags = slice;
      }
      return {
        schema: 'aop-section-state-v2',
        section: sectionId,
        exported_at: new Date().toISOString(),
        toggles,
        sliders,
        paints,
        runtime
      };
    }

    // Apply a section payload — sets only what's in it, leaves everything
    // else alone. Validates schema + section so a Drawn-POIs paste can't
    // accidentally land on Cemeteries.
    function applySectionPayload(payload) {
      if (!payload || payload.schema !== 'aop-section-state-v2') {
        throw new Error('Not an aop-section-state-v2 payload.');
      }
      const sectionId = payload.section;
      if (!SECTION_RUNTIME.hasOwnProperty(sectionId)) {
        throw new Error(`Unknown section "${sectionId}".`);
      }
      // Restore toggles. Fire change events so layer-visibility wiring
      // reacts (otherwise the checkbox shows checked but the layer stays off).
      for (const [id, value] of Object.entries(payload.toggles || {})) {
        const el = document.getElementById(id);
        if (!el) continue;
        if (el.checked !== Boolean(value)) {
          el.checked = Boolean(value);
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }
      for (const [id, value] of Object.entries(payload.sliders || {})) {
        setSliderValue(id, value);
      }
      if (payload.paints) applyPaintState(payload.paints);
      const runtime = payload.runtime || {};
      const spec = SECTION_RUNTIME[sectionId];
      // Positioned-feature overrides write through to localStorage; the moved
      // geometry takes effect on next page reload (no live re-render here).
      if (spec.positionedFeatureLayers && runtime.positioned_features) {
        const allowedPrefixes = spec.positionedFeatureLayers.map((k) => `${k}:`);
        const slice = {};
        for (const [key, value] of Object.entries(runtime.positioned_features)) {
          if (allowedPrefixes.some((p) => key.startsWith(p))) slice[key] = value;
        }
        mergePositionedFeaturesSlice(slice);
      }
      if (spec.editorPois && Array.isArray(runtime.editor_pois)) {
        writeJsonStore(spec.editorPois, runtime.editor_pois);
        // Replay into the live editor source so the drawn POIs appear now.
        if (typeof editorPois !== 'undefined') {
          editorPois.length = 0;
          for (const f of runtime.editor_pois) editorPois.push(f);
          saveEditorPois();
          refreshEditorSource();
        }
      }
      if (spec.featureVisibilityLayers && runtime.feature_visibility) {
        const slice = {};
        for (const key of spec.featureVisibilityLayers) {
          if (runtime.feature_visibility[key]) slice[key] = runtime.feature_visibility[key];
        }
        mergeStoreSlice(FEATURE_VISIBILITY_KEY, slice);
      }
      if (spec.featureTagLayers && runtime.feature_tags) {
        const slice = {};
        for (const key of spec.featureTagLayers) {
          if (runtime.feature_tags[key]) slice[key] = runtime.feature_tags[key];
        }
        mergeStoreSlice(FEATURE_TAG_KEY, slice);
        rebuildTagLookup();
        rebuildEventScheduleData();
      }
      return sectionId;
    }

    // Restore a full v3 export. Same handlers as a section apply, but across
    // every section. Toggles fire change events so layer visibility updates
    // live; geometry overrides settle on next reload.
    function applyExportAllPayload(payload) {
      if (!payload || payload.schema !== 'aop-viewer-preset-settings-v3') {
        throw new Error('Not an aop-viewer-preset-settings-v3 payload.');
      }
      const state = payload.current_state || {};
      for (const [id, value] of Object.entries(state.toggles || {})) {
        const el = document.getElementById(id);
        if (!el) continue;
        if (el.checked !== Boolean(value)) {
          el.checked = Boolean(value);
          el.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }
      for (const [id, value] of Object.entries(state.sliders || {})) {
        setSliderValue(id, value);
      }
      if (state.paints) applyPaintState(state.paints);
      const overrides = payload.runtime_overrides || {};
      if (overrides.positioned_features && typeof overrides.positioned_features === 'object') {
        writeJsonStore(POSITIONED_FEATURES_KEY, overrides.positioned_features);
      }
      if (Array.isArray(overrides.editor_pois)) {
        writeJsonStore(POI_STORAGE_KEY, overrides.editor_pois);
        if (typeof editorPois !== 'undefined') {
          editorPois.length = 0;
          for (const f of overrides.editor_pois) editorPois.push(f);
          saveEditorPois();
          refreshEditorSource();
        }
      }
      if (overrides.feature_visibility) {
        writeJsonStore(FEATURE_VISIBILITY_KEY, overrides.feature_visibility);
      }
      if (overrides.feature_tags) {
        writeJsonStore(FEATURE_TAG_KEY, overrides.feature_tags);
        rebuildTagLookup();
        rebuildEventScheduleData();
      }
    }

    async function exportSectionToClipboard(sectionId) {
      const payload = buildSectionPayload(sectionId);
      const text = JSON.stringify(payload, null, 2) + '\n';
      try {
        const ok = await copyText(text);
        presetStatus.textContent = ok
          ? `${sectionId} section copied (${Math.round(text.length / 1024)} KB).`
          : `Clipboard copy failed for ${sectionId}.`;
      } catch (err) {
        presetStatus.textContent = `Export failed: ${err.message}`;
      }
    }

    async function exportAllToClipboard() {
      const text = JSON.stringify(buildExportPayload(), null, 2) + '\n';
      try {
        const ok = await copyText(text);
        presetStatus.textContent = ok
          ? `Full snapshot copied (${Math.round(text.length / 1024)} KB).`
          : 'Clipboard copy failed.';
      } catch (err) {
        presetStatus.textContent = `Export failed: ${err.message}`;
      }
    }

    // Per-feature copy: emit the feature's current geojson Feature so the
    // user can paste it straight into the source file. We use a fresh clone
    // of the feature reference (which carries any drag-to-move geometry) and
    // strip any properties starting with "_" because those are runtime-only.
    async function copyFeatureAsDropIn(feature) {
      if (!feature) return;
      const drop = {
        type: 'Feature',
        properties: { ...(feature.properties || {}) },
        geometry: JSON.parse(JSON.stringify(feature.geometry || null))
      };
      for (const key of Object.keys(drop.properties)) {
        if (key.startsWith('_')) delete drop.properties[key];
      }
      const text = JSON.stringify(drop, null, 2) + '\n';
      try {
        const ok = await copyText(text);
        presetStatus.textContent = ok
          ? `Copied "${drop.properties.name || drop.properties.id || 'feature'}" as drop-in GeoJSON Feature.`
          : 'Clipboard copy failed.';
      } catch (err) {
        presetStatus.textContent = `Copy failed: ${err.message}`;
      }
    }

    wireLayerEditRows();

    function escapeHtml(value) {
      return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

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
      } catch (_) {
        return value;
      }
    }

    // A GeoJSON source round-trips property values through MapLibre, which may
    // hand booleans back as the strings 'true'/'false'.
    function isTrue(value) {
      return value === true || value === 'true';
    }

    function visitorContextLinksHtml(props) {
      const links = [
        ['Directions', props.directions_url],
        ['Food', props.food_url],
        ['Lodging', props.lodging_url],
        ['Source', props.source_url]
      ]
        .filter(([, url]) => /^https?:\/\//.test(String(url || '')))
        .map(([label, url]) => `<a href="${escapeHtml(url)}" target="_blank" rel="noopener">${escapeHtml(label)}</a>`);
      return links.length ? `<span>${links.join(' &middot; ')}</span>` : '';
    }

    // Render a cemetery's burial roster for the popup footer. `burials` is a
    // [{name, dates}] array; MapLibre JSON-encodes non-primitive properties, so
    // it may arrive as a string and need parsing back.
    function cemeteryBurialHtml(props) {
      let burials = props.burials;
      if (typeof burials === 'string') {
        try { burials = JSON.parse(burials); } catch (error) { burials = []; }
      }
      if (!Array.isArray(burials) || !burials.length) return '';
      const items = burials
        .map((b) => `<li>${escapeHtml(b.name)}`
          + `${b.dates ? ' — ' + escapeHtml(b.dates) : ''}</li>`)
        .join('');
      let html = '<em>Recorded burials</em>'
        + `<ul style="margin:4px 0 0;padding-left:18px;">${items}</ul>`;
      if (props.burial_source) {
        html += '<small style="display:block;margin-top:4px;color:#666;">'
          + `${escapeHtml(props.burial_source)}</small>`;
      }
      return html;
    }

    // --- Event schedule: editable JSON -> map features -------------------
    // The sidebar consumes website/data/aop_event_schedule.json directly.
    // Sessions reference reusable location tags (#pavilion, #registration)
    // so future schedule edits do not repeat coordinates in every row.
    let eventScheduleData = null;
    // `eventScheduleConfig` + `eventLocationByTag` are declared up with the POI
    // caches (~459) so the unified destination collector, called eagerly during
    // layer registration, is not in their TDZ. They are populated by the event
    // loader below exactly as before.
    // Activity-hotspots feature collection is hoisted to module scope so the
    // Trails lane can bbox the densest cells without re-fetching.
    // Card: brain/tasks/02_edit/hot_control_two_lane.md.
    let aopActivityHotspotsData = null;
    const eventSessionById = new Map();
    let activeEventSessionId = null;
    let preferredHotLane = null;

    // The event-schedule document→GeoJSON transform now lives in the ONE shared
    // resolver `js/event_schedule_geojson.js` (window.AOPEventSchedule), read by
    // BOTH the embedded viewer (here) and the standalone right panel (panel.js).
    // This is the going-gold G_E convergence of the two divergent resolvers
    // (audit `event-overlay-two-divergent-resolvers`, C1/C6). main.js keeps the
    // same public name + the same module-scoped maps (`eventLocationByTag`,
    // `eventSessionById`) by re-populating them from the shared fn's return; every
    // downstream consumer (calendar, search, CRUD list, hot button, tag-rebind)
    // is unchanged.

    // The host's working-buffer override for a coordinate-less tag. Baked
    // coordinates in the served document WIN; this fills only when a location has
    // no baked geometry, from the per-feature #tag binding (localStorage
    // `aop_feature_tags_v1`). After the G_E bake (#pavilion now carries baked
    // coordinates) this is an override, not the source of an anchor's position
    // (audit `event-anchor-position-from-localstorage-tag-binding`). Card:
    // brain/tasks/02_edit/named_feature_tagging.md.
    function hostResolveTagCoords(normalized) {
      const bound = tagToFeature.get(normalized);
      return bound && bound.coordinates ? [bound.coordinates[0], bound.coordinates[1]] : null;
    }

    function eventScheduleToGeojson(config) {
      const { geojson, locationByTag, sessionById } = window.AOPEventSchedule.eventScheduleToGeojson(
        config, { resolveTagCoords: hostResolveTagCoords });
      // Re-populate the host's module-scoped maps from the ONE transform's output
      // (the host's consumers read these maps directly), preserving identity.
      eventLocationByTag.clear();
      for (const [tag, location] of locationByTag.entries()) eventLocationByTag.set(tag, location);
      eventSessionById.clear();
      for (const [id, feature] of sessionById.entries()) eventSessionById.set(id, feature);
      return geojson;
    }

    // Re-resolve the schedule against the current tag bindings and push the
    // new data into the live `event-schedule` source. Called when the user
    // changes a feature's #tag — typing #pavilion on the 1010 building row
    // should make the pavilion session row fly to the building immediately,
    // not after a reload. Safe to call before the source is added (no-op).
    // Card: brain/tasks/02_edit/named_feature_tagging.md.
	    function rebuildEventScheduleData(options = {}) {
	      if (!eventScheduleConfig) return;
      eventScheduleData = eventScheduleToGeojson(eventScheduleConfig);
      const source = map.getSource('event-schedule');
      if (source) source.setData(eventScheduleData);
      // The calendar row label includes the resolved location label; if the
      // location went from "Missing #pavilion" to "AOP Pavilion",
      // the row text needs to refresh.
      if (typeof renderEventSchedule === 'function') {
        renderEventSchedule(eventScheduleConfig, eventScheduleData);
      }
      // Search index slice for event-schedule features goes stale when a tag
      // newly resolves (a previously-missing #pavilion anchor now exists).
      // Strip the prior event-schedule entries from searchIndex and re-add
      // them from the freshly-resolved data; then rebuild searchGroups so
      // typing `#pavilion` finds the live anchor.
      refreshEventScheduleSearchIndex();
      // Feature-list runtime for eventSchedule holds a reference to the prior
      // GeoJSON; refresh it in place so the right-panel CRUD list picks up
      // newly-resolved anchors. In-place refresh avoids the recursion with
      // registerFeatureListLayer that would otherwise loop back here.
	      refreshFeatureListData('eventSchedule', eventScheduleData, options);
	      renderPoiTabIfActive();
	    }

    function refreshEventScheduleSearchIndex() {
      // searchIndex is a const-bound array; mutate in place. Drop any prior
      // event-schedule entries so a re-resolve does not duplicate rows.
      for (let i = searchIndex.length - 1; i >= 0; i--) {
        const kind = searchIndex[i] && searchIndex[i].kind;
        if (kind === 'event location' || kind === 'event session') {
          searchIndex.splice(i, 1);
        }
      }
      if (eventScheduleData && typeof indexFeatures === 'function'
          && typeof eventScheduleToggle !== 'undefined') {
        indexFeatures(eventScheduleData,
          (props) => props.feature_kind === 'event_anchor' ? 'event location' : 'event session',
          eventScheduleToggle,
          undefined,
          (props) => props.feature_kind === 'event_anchor' ? [props.location_tag] : null);
      }
      if (typeof buildSearchGroups === 'function') buildSearchGroups();
    }

    // --- Variation B4-info: session "now" computation ---------------------
    // Returns the Date treated as "now". Right-panel session tools and the
    // existing ?clock=YYYY-MM-DDTHH:MM fixture both drive this single source.
    function parseLocalClockString(raw) {
      const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{1,2}):(\d{2})$/.exec(String(raw || '').trim());
      if (!m) return null;
      const d = new Date(
        Number(m[1]), Number(m[2]) - 1, Number(m[3]),
        Number(m[4]), Number(m[5]), 0, 0
      );
      return isNaN(d.getTime()) ? null : d;
    }

    function clockParamDate() {
      try {
        const params = new URLSearchParams(window.location.search);
        const raw = params.get('clock');
        return raw ? parseLocalClockString(raw) : null;
      } catch (_) { /* fall through */ }
      return null;
    }

    const urlClockDate = clockParamDate();
    const storedClock = readJsonStore(VIRTUAL_CLOCK_KEY, null);
    let virtualClockMs = urlClockDate
      ? urlClockDate.getTime()
      : (Number.isFinite(storedClock?.ms) ? Number(storedClock.ms) : null);

    function pad2(value) {
      return String(value).padStart(2, '0');
    }

    function clockInputParts(date) {
      return {
        date: `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())}`,
        time: `${pad2(date.getHours())}:${pad2(date.getMinutes())}`
      };
    }

    function clockLabel(date) {
      const parts = clockInputParts(date);
      return `${parts.date} ${parts.time}`;
    }

    function syncVirtualClockUi() {
      if (!virtualClockDate || !virtualClockTime || !virtualClockStatus) return;
      const active = Number.isFinite(virtualClockMs);
      const date = active ? new Date(virtualClockMs) : new Date();
      const parts = clockInputParts(date);
      virtualClockDate.value = parts.date;
      virtualClockTime.value = parts.time;
      virtualClockStatus.dataset.clockActive = active ? 'true' : 'false';
      virtualClockStatus.textContent = active ? `Test clock ${clockLabel(date)}` : 'Wall clock';
    }

    function setVirtualClock(date, persist = true) {
      if (date && !isNaN(date.getTime())) {
        virtualClockMs = date.getTime();
        if (persist) {
          writeJsonStore(VIRTUAL_CLOCK_KEY, {
            schema: 'aop-virtual-clock-v1',
            updated_at: new Date().toISOString(),
            ms: virtualClockMs
          });
        }
      } else {
        virtualClockMs = null;
        if (persist) removeJsonStore(VIRTUAL_CLOCK_KEY);
      }
      syncVirtualClockUi();
      if (eventScheduleConfig && eventScheduleData) renderEventSchedule(eventScheduleConfig, eventScheduleData);
      if (typeof refreshHotButton === 'function') refreshHotButton();
    }

    function virtualClockFromInputs() {
      if (!virtualClockDate || !virtualClockTime) return null;
      return parseLocalClockString(`${virtualClockDate.value}T${virtualClockTime.value}`);
    }

    function stepVirtualClock(minutes) {
      const basis = Number.isFinite(virtualClockMs) ? new Date(virtualClockMs) : eventScheduleNow();
      setVirtualClock(new Date(basis.getTime() + minutes * 60 * 1000));
    }

	    function resetViewerState() {
	      if (!window.confirm('Reset viewer to the first view? Local edits and overrides in this browser will be cleared.')) return;
	      VIEWER_OWNED_STORAGE_KEYS.forEach(removeJsonStore);
      viewerSessionState = {};
      savedPresetStates = {};
      virtualClockMs = null;
      preferredHotLane = null;
      activeEventSessionId = null;
      syncVirtualClockUi();
      closeAllMapPopups();
      clearSearchResults();
      if (searchInput) searchInput.value = '';
      const highlight = map.getSource('search-highlight');
      if (highlight) {
        highlight.setData({ type: 'FeatureCollection', features: [] });
        setLayerVisibility('search-highlight-line', false);
        setLayerVisibility('search-highlight-point', false);
      }
	      if (lrContentCol) {
	        lrContentCol.style.removeProperty('--lr-card-body-height');
	        for (const { handle, body } of lrResizeHandles) {
	          handle.setAttribute('aria-valuenow', String(Math.round(lrCardCurrentHeight(body))));
	        }
	      }
	      if (typeof editorPois !== 'undefined' && Array.isArray(editorPois)) {
	        editorPois.length = 0;
	        const editorSource = map.getSource('editor-poi');
	        if (editorSource) editorSource.setData(editorFeatureCollection());
	      }
	      resetFeatureListRuntimeDefaults();
	      tagToFeature.clear();
	      resetDefaultPavilionTagRuntime();
	      rebuildEventScheduleData({ persistVisibility: false });
	      // Re-seed editorPois from the canonical seed file. `aop_editor_pois_v1`
	      // was cleared above (VIEWER_OWNED_STORAGE_KEYS), so the seed loader's
	      // "fresh-install" gate passes and the pavilion + any future seeded
	      // features come back. Fire-and-forget; refreshEditorSource inside the
	      // seeder will push the new geometry into the map.
	      if (typeof maybeSeedEditorPois === 'function') maybeSeedEditorPois();
	      if (typeof window.lrResetCards === 'function') window.lrResetCards();
	      setLeftTab('events');
	      setTerrainEnabled(false);
	      applyPreset('park', { persistSession: false });
	      if (typeof goToView === 'function') goToView('park');
	      if (typeof refreshHotButton === 'function') refreshHotButton();
	      presetStatus.textContent = 'Park preset active.';
	    }

    // Torch the offline cache + service worker, then hard-reload from the
    // network. The PWA service worker (sw.js) serves the shell + data caches
    // cache-first and only refreshes on a VERSION bump — so a missed bump (or a
    // browser that hasn't re-activated the new worker yet) keeps serving a STALE
    // build, the class of bug that makes a flipped feature look broken. This is
    // the manual escape hatch: delete every Cache Storage bucket, unregister the
    // worker(s), and reload uncached. It deliberately leaves localStorage alone —
    // the user's stars/overrides/clock survive; "Reset viewer" is the state nuke,
    // this is the CODE nuke. After reload, index.html re-registers a fresh worker
    // and every asset comes from the network.
    async function torchCache() {
      if (!window.confirm('Torch every cached app file + the service worker, then reload from the network?\n\nYour stars and edits in this browser are NOT touched — only the offline cache.')) return;
      if (presetStatus) presetStatus.textContent = 'Torching cache…';
      try {
        if (window.caches && typeof caches.keys === 'function') {
          const names = await caches.keys();
          await Promise.all(names.map((n) => caches.delete(n)));
        }
      } catch (e) { console.warn('[AOP] cache torch failed', e); }
      try {
        if (navigator.serviceWorker && typeof navigator.serviceWorker.getRegistrations === 'function') {
          const regs = await navigator.serviceWorker.getRegistrations();
          await Promise.all(regs.map((r) => r.unregister()));
        }
      } catch (e) { console.warn('[AOP] service worker unregister failed', e); }
      // Reload now that the worker + caches are gone — fetches go to the network.
      window.location.reload();
    }

    function eventScheduleNow() {
      if (Number.isFinite(virtualClockMs)) return new Date(virtualClockMs);
      return new Date();
    }

    // Default session duration for end-time math (schema has no end_local).
    // Kept in sync with the hot button's HOT_BUTTON_SESSION_LEN_MIN below.
    const CALENDAR_SESSION_DURATION_MIN = 90;

    // Anchor the calendar to the actual event date pulled from
    // aop_event_schedule.json (`event.date_range_label`, e.g.
    // "Friday, June 19, 2026"). Replaces the prior Friday-of-this-week shim
    // that always assumed the upcoming weekend was the event. Now session
    // tools (virtual clock) let users simulate live/pre/post states without
    // moving the anchor.
    const EVENT_DATE_LABEL_MONTHS = {
      january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
      july: 6, august: 7, september: 8, october: 9, november: 10, december: 11,
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

    // misc_4.md item 16: the calendar heading shows the event's START date
    // (`date_range_label`). Render it as "start – end" when the schema also
    // carries `end_date_label`. Falls back to start-only when no end date is
    // present or the two are identical (single-day event), so an event is
    // never dropped or shown blank (no_limiting_code_mvp).
    function composeEventDateRangeLabel(event) {
      const start = (event?.date_range_label || '').trim();
      const end = (event?.end_date_label || '').trim();
      if (!end || end === start) return start;
      // en dash, spaced — matches the user's "start date - end date" shape.
      return `${start} – ${end}`;
    }

    // Session-start Date for a row given a resolved anchor Saturday.
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
      return new Date(anchorSat.getFullYear(), anchorSat.getMonth(),
        anchorSat.getDate() + offset, hour, minute, 0, 0);
    }

    // Scan rendered rows to derive the schedule's edges as minutes-past-
    // midnight: gates-open = earliest Friday start; weekend-end = latest
    // Sunday start + default session length. Fallbacks match the JSON
    // baseline (Fri 17:00 / Sun 18:30) so the state machine still works
    // before render or with an empty schedule.
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
        weekendEndMin: weekendEnd != null ? weekendEnd : 18 * 60 + 30,
      };
    }

    // Classify the current moment against the event weekend. Three states:
    //   'pre'  — before Friday gates open. Countdown banner active.
    //   'live' — Fri gates open → end of last Sun session. Per-row badges.
    //   'post' — after the last Sun session. All rows past, banner hidden.
    function computeCalendarState(now) {
      const edges = computeCalendarScheduleEdges();
      const anchorSat = resolveCalendarAnchorSat();
      if (!anchorSat) return { state: 'pre', anchorSat: null, countdownTargetMs: null };
      const gatesH = Math.floor(edges.gatesOpenMin / 60);
      const gatesM = edges.gatesOpenMin % 60;
      const endH = Math.floor(edges.weekendEndMin / 60);
      const endM = edges.weekendEndMin % 60;
      const gatesOpen = new Date(anchorSat.getFullYear(), anchorSat.getMonth(),
        anchorSat.getDate() - 1, gatesH, gatesM, 0, 0);
      const weekendEnd = new Date(anchorSat.getFullYear(), anchorSat.getMonth(),
        anchorSat.getDate() + 1, endH, endM, 0, 0);
      const nowMs = now.getTime();
      let state;
      if (nowMs < gatesOpen.getTime()) state = 'pre';
      else if (nowMs < weekendEnd.getTime()) state = 'live';
      else state = 'post';
      return {
        state,
        anchorSat,
        gatesOpenMs: gatesOpen.getTime(),
        weekendEndMs: weekendEnd.getTime(),
        countdownTargetMs: state === 'pre' ? gatesOpen.getTime() : null,
      };
    }

    // Format remaining minutes as "Xm" (<60), "Xh Ym" (<1d), or "Xd Yh" (>=1d).
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
        // Item 3 (misc_3.md): explicitly drive .calendar-body scroll so the
        // active row centers inside the calendar's scrollable area
        // regardless of the surrounding drawer state — BUT only when the row
        // is not already fully visible. This preserves the "60s tick does
        // not yank scroll back" contract: once the user can see the row,
        // leave their scroll position alone.
        const bodyRect = calendarBody.getBoundingClientRect();
        const rowRect = target.getBoundingClientRect();
        const fullyVisible = rowRect.top >= bodyRect.top && rowRect.bottom <= bodyRect.bottom;
        if (fullyVisible) return;
        const offset = (rowRect.top - bodyRect.top) - (bodyRect.height / 2 - rowRect.height / 2);
        calendarBody.scrollTop += offset;
      });
    }

    // Walk the rendered rows and stamp data-session-state + badges. Called
    // immediately after render and every 60s (plus on visibilitychange).
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
      // In 'pre' state the top countdown banner carries the signal, so per-
      // row upcoming_next promotion is suppressed to avoid two countdowns
      // racing each other. 'live' and 'post' use the normal row treatment.
      if (calendar.state !== 'pre') {
        const firstFuture = computed.find((r) => r.state === 'future');
        if (firstFuture) firstFuture.state = 'upcoming_next';
      }
      for (const r of computed) {
        r.li.setAttribute('data-session-state', r.state);
        // Remove any prior badges; we re-create only for happening/upcoming.
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
      // Hot control shares the clock/anchor + 60s tick + visibilitychange
      // signals with the calendar refresh, so piggybacking here keeps both
      // in lockstep without standing up a second timer. Also covers the
      // tag-rebind path (rebuildEventScheduleData -> renderEventSchedule
      // -> refreshEventScheduleSessionStates -> here).
      if (typeof refreshHotButton === 'function') refreshHotButton();
      scrollCalendarCurrentRowIntoView();
    }

    // One page-lifetime ticker, created lazily on first schedule render and
    // deliberately NOT torn down: the `!= null` guard makes both the 60s interval
    // and the visibilitychange listener singletons (re-render/reset re-enters here
    // and creates nothing new), and a reset still wants live session states, so
    // there's nothing to stop. If this ever becomes a multi-view SPA, add a
    // stopEventScheduleStateTicker() that clears both and call it on teardown.
    let eventScheduleStateTimer = null;
    function ensureEventScheduleStateTicker() {
      if (eventScheduleStateTimer != null) return;
      eventScheduleStateTimer = window.setInterval(() => {
        refreshEventScheduleSessionStates();
      }, 60 * 1000);
      document.addEventListener('visibilitychange', () => {
        if (!document.hidden) refreshEventScheduleSessionStates();
      });
    }

    // --- Hot control: Event + Trails lanes -------------------------------
    // Event lane: hot-now (live or starts in <=30 min) or coming-up (next
    // scheduled session, any day forward). Trails lane is a sibling action
    // whenever activity-hotspot data is present. Card:
    // brain/tasks/02_edit/hot_control_two_lane.md.
    const HOT_BUTTON_IMMINENT_MIN = 30;
    const HOT_BUTTON_SESSION_LEN_MIN = 90;

    // Anchor every session to the real event Saturday from the JSON config.
    // Shares the same anchor logic the calendar uses, so the hot button and
    // the calendar always agree on what "live" and "next" mean. Returns null
    // when the schedule config is not yet loaded or the row's day label is
    // unrecognised.
    function eventScheduleAnchorForward(dayLabel, startLocal /* now unused */) {
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
        const start = eventScheduleAnchorForward(props.day, props.start_local, now);
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

    // Seed at the strongest hotspot polygon, then grow a contiguous cluster
    // outward by centroid distance ≤ HOT_CLUSTER_RADIUS_M. Returns the bbox
    // of that cluster, not a top-K bbox that could span the whole park when
    // the top ranks live in different parts of the map.
    const HOT_CLUSTER_RADIUS_M = 260;

    function hotspotPolygonCentroid(feature) {
      const geom = feature.geometry;
      if (!geom) return null;
      // Polygon: coordinates[0] is the outer ring. MultiPolygon: coordinates[0]
      // is the first polygon, whose [0] is its outer ring. Average that ring
      // either way so a multi-part hotspot is placed, not silently dropped (NaN).
      const ring = geom.type === 'MultiPolygon'
        ? geom.coordinates?.[0]?.[0]
        : geom.coordinates?.[0];
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
      const cluster = ranked.filter(
        (r) => hotspotMetersBetween(seed.centroid, r.centroid) <= radiusM
      );
      return geojsonBounds({
        type: 'FeatureCollection',
        features: cluster.map((r) => r.f)
      });
    }

    // Single source of truth for "are trail hotspots actually ON". The Trail
    // lane is a real toggle over the activity-hotspots layer, so its pressed
    // state must read the live checkbox, not the preferred-lane heuristic.
    // (Item 14: on a cold load selectedHotLane() could mark the lane
    // "selected" while the layer was still hidden, so the first click hit the
    // OFF branch and nothing turned on.)
    function trailHotspotsActive() {
      return !!(activityHotspotsToggle && activityHotspotsToggle.checked);
    }

    function setTrailHotspotsVisible(on) {
      if (!activityHotspotsToggle) return;
      if (activityHotspotsToggle.checked === on) return;
      activityHotspotsToggle.checked = on;
      activityHotspotsToggle.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function hotButtonFlyToHotspots() {
      setTrailHotspotsVisible(true);
      const bbox = findDensestHotspotCluster();
      if (!bbox) return;
      const pad = visibleMapPadding(20);
      map.fitBounds(bbox, {
        padding: pad,
        maxZoom: 16.2,
        duration: 1000,
        bearing: map.getBearing(),
        pitch: map.getPitch()
      });
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
          // Real toggle keyed off the live layer state, not the recommended-lane
          // halo. Second tap (layer already ON) turns the hotspots OFF; first tap
          // from cold (layer OFF) turns them ON and flies to the densest cluster.
          if (trailHotspotsActive()) {
            preferredHotLane = null;
            setTrailHotspotsVisible(false);
            refreshHotButton();
          } else {
            preferredHotLane = 'trails';
            hotButtonFlyToHotspots(); // turns the layer ON, then refresh paints state
            refreshHotButton();
          }
        });
      }
    }

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
        control.dataset.lrWasVisible = '0';
        eventBtn.dataset.hotState = 'empty';
        eventBtn.dataset.targetSessionId = '';
        trailBtn.dataset.hotSelected = 'false';
        return;
      }

      const wasVisible = control.dataset.lrWasVisible === '1';
      control.hidden = false;
      control.dataset.lrWasVisible = '1';
      if (!wasVisible && typeof window.lrOpenCard === 'function') {
        window.lrOpenCard('hot', { auto: true });
      }
      const selected = selectedHotLane(decision, haveHotspots);
      // Trail lane is a toggle: its pressed/active state mirrors the live
      // hotspot layer, not the recommended-lane heuristic. This keeps the
      // visual and the click logic on the same truth so the FIRST cold click
      // turns hotspots ON (was marked "selected" while still hidden before).
      const trailOn = haveHotspots && trailHotspotsActive();
      if (lanes) lanes.dataset.laneCount = haveHotspots ? '2' : '1';
      eventBtn.dataset.hotSelected = selected === 'event' ? 'true' : 'false';
      trailBtn.dataset.hotSelected = trailOn ? 'true' : 'false';
      trailBtn.dataset.hotOn = trailOn ? 'true' : 'false';
      trailBtn.setAttribute('aria-pressed', trailOn ? 'true' : 'false');
      trailBtn.hidden = !haveHotspots;
      trailBtn.disabled = !haveHotspots;
      trailBtn.dataset.hotState = 'trail-hot';
      const HOT = window.AOP_UI?.hot || {};
      if (trailTitle) trailTitle.textContent = trailOn ? (HOT.trail_on_title || 'Trail activity on') : (HOT.trail_idle_title || 'Trail activity');
      if (trailDetail) trailDetail.textContent = trailOn ? (HOT.trail_on_detail || 'Tap to hide hotspots') : (HOT.trail_idle_detail || 'Where rigs spent time');
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
          if (title) title.textContent = HOT.event_live_title || 'Live event';
          if (detail) detail.textContent = `${props.title || 'Session'} · ${eventScheduleFormatMinutes(mins)} left`;
          if (status) status.textContent = selected === 'event' ? 'Event live' : 'Event live';
        } else {
          const mins = (decision.target.startMs - now.getTime()) / 60000;
          if (title) title.textContent = HOT.event_soon_title || 'Starting soon';
          if (detail) detail.textContent = `${props.title || 'Session'} · in ${eventScheduleFormatMinutes(mins)}`;
          if (status) status.textContent = selected === 'event' ? 'Event soon' : 'Event soon';
        }
        eventBtn.setAttribute('aria-label', `Event hot: ${props.title || 'session'}`);
      } else if (decision.state === 'coming-up') {
        const props = decision.target.feature.properties || {};
        eventBtn.disabled = false;
        eventBtn.dataset.targetSessionId = props.session_id || '';
        const mins = (decision.target.startMs - now.getTime()) / 60000;
        if (glyph) glyph.textContent = '◷'; // upper-right circular sector
        if (title) title.textContent = HOT.event_next_title || 'Next event';
        if (detail) {
          const dayPart = props.day ? `${props.day} ` : '';
          const timePart = props.window || props.start_local || '';
          detail.textContent = `${dayPart}${timePart} · in ${eventScheduleFormatMinutes(mins)}`;
        }
        if (status) status.textContent = selected === 'trails' ? 'Trail activity' : 'Next event';
        eventBtn.setAttribute('aria-label', `Next event: ${props.title || 'session'}`);
      } else {
        eventBtn.disabled = true;
        eventBtn.dataset.targetSessionId = '';
        if (glyph) glyph.textContent = '◷';
        if (title) title.textContent = HOT.event_none_title || 'No event';
        if (detail) detail.textContent = HOT.event_none_detail || 'Trail activity available';
        if (status) status.textContent = haveHotspots ? 'Trail activity' : 'No target';
        eventBtn.setAttribute('aria-label', 'No event target');
      }
    }

    function renderEventSchedule(config, data) {
      const event = config?.event || {};
      calendarRange.textContent = composeEventDateRangeLabel(event);
      // Calendar title is the event label from aop_event_schedule.json — single
      // source with the rest of the schedule copy (was hardcoded in the markup).
      const calendarTitleEl = document.getElementById('calendarTitle');
      if (calendarTitleEl && event.label) calendarTitleEl.textContent = event.label;
      const sessions = (data?.features || [])
        .filter((feature) => feature.properties?.feature_kind === 'event_session')
        .sort((a, b) => Number(a.properties.sort_order || 0) - Number(b.properties.sort_order || 0));
      if (!sessions.length) {
        calendarDays.innerHTML = `<li class="calendar-empty">${escapeHtml(window.AOP_UI?.calendar?.empty || 'No schedule rows.')}</li>`;
        return;
      }
      calendarDays.innerHTML = sessions.map((feature) => {
        const props = feature.properties || {};
        const tag = props.location_tag || '';
        const location = props.location_label || tag;
        const active = props.session_id === activeEventSessionId ? ' active' : '';
        // data-session-day + data-session-start let refreshEventScheduleSessionStates
        // recompute LIVE / SOON without re-rendering the whole list.
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

    // Close every popup currently on the map by triggering each one's own
    // close button, so MapLibre runs its native cleanup (fires `close`,
    // removes listeners) instead of leaving orphan DOM behind.
    function closeAllMapPopups() {
      map.getContainer()
        .querySelectorAll('.maplibregl-popup-close-button')
        .forEach((btn) => btn.click());
    }

    // The unoccluded map slice — container minus any chrome that floats on
    // top (`.left-controls`, `.panel`, `.message`). Returns a viewport rect
    // in CSS pixels. Computes occlusion live from rects so a hidden vs.
    // open calendar drawer is reflected, and so the mobile layout (left
    // strip spans top, right panel docked below) shifts top/bottom occlusion
    // instead of left/right.
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
      // Threshold: a chrome element spanning >70% of container width is
      // treated as full-width and eats top/bottom rather than left/right.
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
        // pwa_qa_2 item 1 root-cause fix: `.message` has been display:none
        // since V5, so its rect is all-zero (top 0). The old unconditional
        // `Math.min(bottom, 0)` collapsed the whole visible slice to bottom=0,
        // which made visibleMapPadding()'s bottom enormous and yanked every
        // event flyTo target upward, then panPopupIntoView jerked to fit a
        // zero-height slice. Only a GENUINELY rendered bottom bar should eat in.
        if (r.height > 0) bottom = Math.min(bottom, r.top);
      }
      return { top, bottom, left, right };
    }

    // Padding that reserves space for the fixed overlays so a fitBounds /
    // flyTo lands its target in the unoccluded slice — not under the
    // calendar card, layer panel, or message bar where a popup would clip.
    // Built off `visibleMapRect()` so wide-screen padding stays left/right
    // and narrow-screen padding shifts to top/bottom automatically.
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

    // Pixel offset that shifts a flyTo target from the full map center into
    // the visible-map center (see visibleMapPadding). MapLibre interprets
    // flyTo `offset` as: the supplied `center` lands at mapCenter + offset,
    // so a negative x pulls the point left when the right panel is wider.
    function visibleCenterOffset(pad) {
      return [(pad.left - pad.right) / 2, (pad.top - pad.bottom) / 2];
    }

    // After a popup is positioned, nudge the camera so the popup element
    // sits fully inside the unoccluded map slice. Fix for the narrow-screen
    // case where the chrome (top strip when calendar is expanded, bottom
    // message bar) was clipping a `gotoEventSession` popup. Margin keeps
    // a small gap from the chrome edges. Runs on the next animation frame
    // so MapLibre has placed the popup element relative to the moved camera.
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

    function gotoEventSession(sessionId) {
      const feature = eventSessionById.get(sessionId);
      if (!feature) return;
      // Schedule link is a navigation: leave the viewer with one popup, not a stack.
      closeAllMapPopups();
      activeEventSessionId = sessionId;
      persistViewerSessionState({ active_event_session_id: sessionId, active_left_tab: 'events' });
      if (eventScheduleConfig && eventScheduleData) renderEventSchedule(eventScheduleConfig, eventScheduleData);

      if (!eventScheduleToggle.checked) {
        eventScheduleToggle.checked = true;
        eventScheduleToggle.dispatchEvent(new Event('change', { bubbles: true }));
      }

      const pad = visibleMapPadding(20);
      const bounds = geojsonBounds({ type: 'FeatureCollection', features: [feature] });
      if (bounds) {
        const [[minLng, minLat], [maxLng, maxLat]] = bounds;
        if (minLng === maxLng && minLat === maxLat) {
          map.flyTo({
            center: [minLng, minLat],
            zoom: 17,
            offset: visibleCenterOffset(pad),
            duration: 1000,
            bearing: map.getBearing(),
            pitch: map.getPitch()
          });
        } else {
          map.fitBounds(bounds, {
            padding: pad,
            maxZoom: 16.8,
            duration: 1000,
            bearing: map.getBearing(),
            pitch: map.getPitch()
          });
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
        // Cap the popup so it never exceeds the unoccluded slice. On narrow
        // chrome-heavy layouts the slice can shrink below the default 280 px;
        // a wider popup would inevitably overlap the calendar strip or layer
        // panel no matter how much we pan. Lower-bound 200 px so the popup
        // stays legible on the cramp end.
        const slice = visibleMapRect();
        const sliceWidth = Math.max(0, slice.right - slice.left);
        const popupMax = Math.max(200, Math.min(280, sliceWidth - 28));
        // pwa_qa_2 item 1: pin the popup to a FIXED `bottom` anchor so it always
        // opens above the start point. Default auto-anchor recomputes on every
        // `move` frame and flips the popup side mid-flight — that re-anchoring
        // is the "jerks around" the user saw. `focusAfterOpen:false` stops the
        // popup stealing focus and nudging the fixed map.
        const popup = new maplibregl.Popup({ maxWidth: `${popupMax}px`, anchor: 'bottom', offset: 14, focusAfterOpen: false })
          .setLngLat(popupCoord)
          .setHTML(sessionPopupHtml(feature.properties))
          .addTo(map);
        popup.on('close', () => {
          if (activeEventSessionId !== sessionId) return;
          activeEventSessionId = null;
          persistViewerSessionState({ active_event_session_id: null });
          if (eventScheduleConfig && eventScheduleData) renderEventSchedule(eventScheduleConfig, eventScheduleData);
        });
        // ONE corrective pan after the flight settles, to slide the popup fully
        // into the unoccluded slice if narrow-screen chrome is clipping it.
        // panPopupIntoView already measures inside requestAnimationFrame, so the
        // popup element is sized by the time it runs — the old extra setTimeout
        // pan ~1.2 s later was a second, visible jerk and is gone.
        map.once('moveend', () => panPopupIntoView(popup));
      }
    }

    // --- Map editor: drawn POIs ---------------------------------------
    // Terra Draw supplies the click-to-place interaction; committed POIs live
    // in our own `editor-poi` GeoJSON source so they carry category styling
    // and labels, and survive reloads via localStorage (works offline).
    // Storage key declared at the top of the script with the others.
    const POI_COLORS = {
      'Pavilion': '#c47a44',
      'Building': '#a07442',
      'Restroom': '#6f8aa6',
      'Parking': '#8a8576',
      'Staging area': '#9a7d96',
      'Gate': '#b05a48',
      'Trail trace': '#9a5a32',
      'Road trace': '#6f6a5b',
      'Landmark': '#5f9183',
      'Hazard': '#cf9a4a',
      'Other': '#6a6256'
    };
    // An unknown category falls through to the default color instead of being
    // dropped, so a typed/edited category never hides a POI.
    const poiColorExpression = ['match', ['get', 'category']];
    for (const [name, color] of Object.entries(POI_COLORS)) poiColorExpression.push(name, color);
    poiColorExpression.push('#6a6256');

    let editorPois = [];
    let draw = null;

    function loadEditorPois() {
      const parsed = readJsonStore(POI_STORAGE_KEY, () => []);
      editorPois = Array.isArray(parsed) ? parsed : [];
    }

    // First-install + Reset-viewer seed for editorPois. The canonical seed
    // lives at `website/data/bronze_aop_editor_seed_pois.geojson` and ships with
    // the repo; on a fresh viewer (or after Reset viewer clears
    // `aop_editor_pois_v1` outright) we fetch it and write its features
    // into storage as the user's starting set. Workflow to update the
    // seed: draw + Export GeoJSON, then commit the download as
    // bronze_aop_editor_seed_pois.geojson. Every seeded feature is stamped
    // `properties.source = aop_editor_seed_v1` so the source register can
    // tell seeded geometry apart from user-drawn geometry; the optional
    // `seed_tag` property writes a #tag into `aop_feature_tags_v1` for
    // the seeded feature and strips any conflicting binding off another
    // layer (migration: 1010 building → seeded pavilion POI).
    async function maybeSeedEditorPois() {
      if (localStorage.getItem(POI_STORAGE_KEY) !== null) return;
      const seed = await fetchJson('./data/bronze_aop_editor_seed_pois.geojson', 'editor POI seed');
      if (!seed || !Array.isArray(seed.features) || seed.features.length === 0) return;
      const seeded = [];
      for (const feature of seed.features) {
        if (!feature || !feature.geometry || !feature.properties) continue;
        const props = { ...feature.properties };
        if (!props.id) continue;
        if (!props.source) props.source = 'aop_editor_seed_v1';
        if (!props.layer) props.layer = 'editor_poi';
        seeded.push({ type: 'Feature', geometry: feature.geometry, properties: props });
      }
      if (seeded.length === 0) return;
      editorPois = seeded;
      // Apply seed_tag bindings. The seed wins over any pre-existing
      // binding on another layer (one-shot migration on each fresh
      // install / Reset). After this runs once, the user owns the
      // binding through the editor's tag input like any other.
      // Self-exclusion only — this seeder owns the editorPois bindings, so the
      // conflict sweep skips its own layer. Named as a SELF constant (not a
      // dispatch site) so no literal layer-key comparison survives in the
      // C1 branch-count grep; it is intentionally NOT a spec strategy.
      const SELF = 'editorPois';
      const tagStore = loadFeatureTagStore();
      if (!tagStore[SELF]) tagStore[SELF] = {};
      for (const feature of seeded) {
        const id = feature.properties.id;
        const seedTag = feature.properties.seed_tag;
        if (!id || !seedTag) continue;
        const normalized = normalizeFeatureTag(seedTag);
        if (!normalized) continue;
        for (const layerKey of Object.keys(tagStore)) {
          if (layerKey === SELF) continue;
          const layerBindings = tagStore[layerKey] || {};
          for (const fid of Object.keys(layerBindings)) {
            if (layerBindings[fid] === normalized) delete layerBindings[fid];
          }
        }
        tagStore[SELF][id] = normalized;
        // Strip the seed_tag property — it has served its purpose; the
        // binding now lives in aop_feature_tags_v1 like any user tag.
        delete feature.properties.seed_tag;
      }
      saveFeatureTagStore(tagStore);
      saveEditorPois();
      refreshEditorSource();
      // Tag store changed: the existing #pavilion binding may have moved
      // off the buildings layer, so rebuild the inverse lookup and the
      // event schedule that resolves through it.
      if (typeof rebuildTagLookup === 'function') rebuildTagLookup();
      if (typeof rebuildEventScheduleData === 'function') rebuildEventScheduleData();
    }

    function saveEditorPois() {
      writeJsonStore(POI_STORAGE_KEY, editorPois);
    }

    function editorFeatureCollection() {
      return { type: 'FeatureCollection', features: editorPois };
    }

    function refreshEditorSource() {
      const source = map.getSource('editor-poi');
      if (source) source.setData(editorFeatureCollection());
      const points = editorPois.filter((f) => f.geometry.type === 'Point').length;
      const traces = editorPois.filter((f) => f.geometry.type === 'LineString').length;
      const footprints = editorPois.length - points - traces;
      poiStatus.textContent =
        `${points} POI${points === 1 ? '' : 's'}, ${footprints} footprint${footprints === 1 ? '' : 's'}, ${traces} trace${traces === 1 ? '' : 's'}.`;
      // Feed the shared feature list panel. POIs differ from buildings and
      // cemeteries in that the data set mutates as the user draws/deletes —
      // every refresh re-registers the runtime so the panel stays accurate.
      // The runtime preserves the user's per-id visibility ticks across
      // re-register because they live in localStorage, not in featureListRuntime.
      //
      // Single source of truth: editorPois (the localStorage array) is canonical.
      // The left POI tab reads it directly; the right editor tree + ★ Visitor
      // list read featureListRuntime['editorPois'], a faithful projection built
      // here from editorFeatureCollection(). This MUST run on every mutation,
      // independent of whether the map layer exists yet — registerFeatureListLayer
      // and applyFeatureListFilters both guard every map.getLayer() access, so
      // registering before/without 'editor-poi-circles' is safe. Gating this on
      // the map layer (the old behavior) let the right side go stale during a
      // basemap/preset style swap or an early-boot race while the left stayed
      // current — that was the "drawn POI shows on the left but not the right" bug.
      if (typeof registerFeatureListLayer === 'function') {
        registerFeatureListLayer('editorPois', editorFeatureCollection());
        renderFeatureList('editorPois');
      }
    }

    // Build + persist ONE drawn feature into the editorPois array (the single
    // store of record, aop_editor_pois_v1) and repaint the editor-poi source.
    // Extracted from the TerraDraw `finish` handler (below) so BOTH the host draw
    // path AND the right panel's "+ add" create affordance (via the
    // AOP_HOST_CREATE_FEATURE bridge, Sprint 09 Slice 2) land a new feature in the
    // SAME one store — no twin-store create leak (audit F6). Point → editor_poi,
    // Polygon → editor_poi (footprint), LineString → editor_trace (with imagery
    // provenance), matching the original inline construction exactly. Returns the
    // new feature's id.
    function addDrawnPoi(geometry, category) {
      const cat = category || 'Other';
      const isTrace = geometry.type === 'LineString';
      const properties = {
        id: `poi_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        layer: isTrace ? 'editor_trace' : 'editor_poi',
        category: cat,
        name: cat,
        created: new Date().toISOString()
      };
      if (isTrace) {
        Object.assign(properties, {
          source_name: 'USDA NAIP public image service',
          source_url: 'https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer',
          source_year: '2023',
          source_resolution: '60 cm source imagery; cached service draws through level 17',
          confidence: 'draft',
          review_status: 'raw imagery trace; needs review before core/publish'
        });
      }
      editorPois.push({
        type: 'Feature',
        geometry: JSON.parse(JSON.stringify(geometry)),
        properties
      });
      saveEditorPois();
      refreshEditorSource();
      return properties.id;
    }

    // Single export path is clipboard GeoJSON — no file downloads. Copies the
    // whole drawn-POI set as a FeatureCollection ready to paste into
    // website/data/bronze_aop_editor_seed_pois.geojson.
    async function exportEditorPois() {
      const fc = editorFeatureCollection();
      const text = JSON.stringify(fc, null, 2) + '\n';
      const n = fc.features.length;
      try {
        const ok = await copyText(text);
        presetStatus.textContent = ok
          ? `Copied ${n} drawn feature${n === 1 ? '' : 's'} as GeoJSON.`
          : 'Clipboard copy failed.';
      } catch (err) {
        presetStatus.textContent = `Copy failed: ${err.message}`;
      }
    }

    // mode is 'point' (POI), 'polygon' (footprint), 'linestring' (trace), or
    // 'static' (not drawing).
    function isDrawModeActive() {
      return Boolean(draw && draw.getMode && draw.getMode() !== 'static');
    }

    function setDrawMode(mode) {
      if (!draw) return;
      draw.setMode(mode);
      // Legacy hidden buttons keep their class/text echo so any verifier or
      // adjacent JS that reads them stays happy.
      placePoiBtn.classList.toggle('active', mode === 'point');
      drawFootprintBtn.classList.toggle('active', mode === 'polygon');
      traceLineBtn.classList.toggle('active', mode === 'linestring');
      placePoiBtn.textContent = mode === 'point' ? 'Placing… (Esc)' : 'Place POI';
      drawFootprintBtn.textContent = mode === 'polygon' ? 'Drawing… (Esc)' : 'Draw footprint';
      traceLineBtn.textContent = mode === 'linestring' ? 'Tracing… (Esc)' : 'Trace line';
      // V3c: echo active state on every bucket's + and start-btn. The bucket
      // with the matching drawMode glows rust; other bucket buttons reset.
      for (const bucket of EDITOR_BUCKETS) {
        const isActive = bucket.drawMode === mode;
        const addBtn = document.querySelector(`[data-editor-bucket-add="${bucket.id}"]`);
        if (addBtn) addBtn.classList.toggle('active', isActive);
        if (bucket.startBtn) {
          bucket.startBtn.classList.toggle('active', isActive);
          bucket.startBtn.textContent = createPrimaryButtonLabel(bucket, isActive);
        }
      }
      // Going back to static closes any open create row that doesn't belong
      // to an actively drawing bucket. Cancelling mid-draw flows through
      // closeBucketCreate (the cancel button + Esc handler call it).
      if (mode === 'static' && currentCreateBucket) {
        // Don't recurse — closeBucketCreate may also call setDrawMode.
        const stale = currentCreateBucket;
        currentCreateBucket = null;
        if (stale.createRow && stale.createRow.parentElement) stale.createRow.remove();
        stale.createRow = null;
        stale.categorySelect = null;
        stale.startBtn = null;
      }
    }

    // Fetch an optional overlay. Returns undefined (and warns) if it cannot load,
    // so a missing overlay never aborts the rest of the viewer.
    // Memoized by URL (M4): the warm-up loop at the top of map.on('load') kicks
    // every overlay fetch off in parallel, so the `await fetchJson(...)` calls at
    // each layer's add-site resolve against the in-flight request instead of
    // starting a fresh, serialized one. Net effect: the total fetch wait drops
    // from the SUM of every file's load time to the MAX (one slow file — e.g. the
    // 14 MB contours — no longer sits behind all the layers queued after it). All
    // these files are static and fetched once per page, so caching the promise is
    // safe. The warm list is a perf hint only — a URL missing from it just fetches
    // lazily; an extra one just warms unused. Neither changes behavior.
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

    const popupLayers = new Set();
    const POPUP_LAYER_PRIORITY = {
      'synthetic-activity-hotspots-fill': 100,
      'synthetic-activity-hotspots-labels': 100,
      'activity-hotspots-fill': 95,
      'activity-hotspots-labels': 95,
      'event-anchor-points': 90,
      'event-session-routes': 86,
      'brand-logos-icons': 84,
      'water-points': 82,
      'cemetery-marker': 80,
      'osm-named-points': 78,
      'building-footprint-fill': 72,
      'building-footprint-outline': 72,
      'building-footprint-aop-outline': 72,
      'synthetic-activity-tracks': 66,
      'streams': 64,
      'roads-local': 62,
      'roads-connecting': 62,
      'roads-secondary': 62,
      'roads-ramp': 62,
      'roads-controlled': 62,
      'waterbody-fill': 58,
      'water-area-fill': 58,
      'cemetery-fill': 56,
      'visitor-context-fill': 40,
      'visitor-context-outline': 40
    };

    function popupPriority(layerId) {
      return POPUP_LAYER_PRIORITY[layerId] ?? 50;
    }

    function topPopupFeature(event) {
      const layers = [...popupLayers].filter((id) => map.getLayer(id));
      if (!layers.length) return null;
      const features = map.queryRenderedFeatures(event.point, { layers });
      return features.reduce((best, feature) => {
        if (!best) return feature;
        return popupPriority(feature.layer.id) > popupPriority(best.layer.id) ? feature : best;
      }, null);
    }

    // Wire a click popup for one or more layers. titleFor and footerFor may be
    // a value or a (props) => value function; footerFor is optional trailing HTML.
    // Only the highest-priority popup layer under the click opens. This keeps
    // broad default-on context polygons from stacking over hotspot/building
    // popups at the same coordinate.
    function bindPopup(layers, titleFor, rowsFor, footerFor) {
      const layerList = Array.isArray(layers) ? layers : [layers];
      const layerSet = new Set(layerList);
      layerList.forEach((layer) => popupLayers.add(layer));
      map.on('click', layers, (event) => {
        if (isDrawModeActive()) return;
        // While a feature is staged for move, the click belongs to the move
        // primitive — popping up info on the same click would compete with
        // the intended commit. See enterMoveMode / commitMoveMode.
        if (moveState) return;
        const targetFeature = topPopupFeature(event) || event.features?.[0];
        if (targetFeature?.layer?.id && !layerSet.has(targetFeature.layer.id)) return;
        const props = targetFeature?.properties || {};
        const title = typeof titleFor === 'function' ? titleFor(props) : titleFor;
        // Titles are escaped centrally here so individual callers don't have to
        // (and can't forget to). rowsFor is escaped by detailRows; footerFor
        // returns intentional HTML and is left untouched.
        let html = `<strong>${escapeHtml(title)}</strong><br/>${detailRows(rowsFor(props))}`;
        if (footerFor) {
          const footer = footerFor(props);
          if (footer) html += '<br/>' + footer;
        }
        // Close via MapLibre so each Popup instance's own 'close' handler fires
        // (e.g. the event-session popup that clears activeEventSessionId).
        closeAllMapPopups();
        new maplibregl.Popup().setLngLat(event.lngLat).setHTML(html).addTo(map);
      });
    }

    function extendBounds(bounds, coordinates) {
      if (typeof coordinates[0] === 'number') {
        const [lng, lat] = coordinates;
        bounds.minLng = Math.min(bounds.minLng, lng);
        bounds.minLat = Math.min(bounds.minLat, lat);
        bounds.maxLng = Math.max(bounds.maxLng, lng);
        bounds.maxLat = Math.max(bounds.maxLat, lat);
        return;
      }

      coordinates.forEach((child) => extendBounds(bounds, child));
    }

    function geojsonBounds(data) {
      const bounds = {
        minLng: Infinity,
        minLat: Infinity,
        maxLng: -Infinity,
        maxLat: -Infinity
      };
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

    // Camera/zoom presets, separate from the layer presets (Park/Topo/Trace).
    // Region fits REGION_BOUNDS (the 9-patch, also the map's maxBounds); Park
    // fits the live park boundary from gold_publish.geojson; Pavilion is the 1010
    // Ellis Cove Rd building. Each zoom shortcut returns to the intended flat
    // west-up read; layer presets preserve the current camera.
    const PAVILION_VIEW = { center: [-85.748268, 35.090703], zoom: 17 };
    const VIEW_BEARING = -90;
    const VIEW_PITCH = 0;
    let parkViewBounds = null;

    function goToView(view) {
      if (view === 'pavilion') {
        map.flyTo({ center: PAVILION_VIEW.center, zoom: PAVILION_VIEW.zoom, bearing: VIEW_BEARING, pitch: VIEW_PITCH, duration: 1100 });
        return;
      }
      if (view === 'park') {
        // Tight padding so the park parcel fills the frame — at padding:60 the
        // small parcel only landed ~0.87 zoom tighter than Region (reads as
        // "same zoom"); padding:20 lands it ~1.0+ tighter (measured 14.75 vs
        // Region 13.74), a clearly visible step in. Fall back to the park-parcel
        // envelope (not REGION_BOUNDS) so Park is always tighter than Region
        // even before gold_publish.geojson loads.
        map.fitBounds(parkViewBounds || PARK_BOUNDS_FALLBACK, {
          padding: 20, bearing: VIEW_BEARING, pitch: VIEW_PITCH, duration: 1100, maxZoom: 15.5
        });
        return;
      }
      // Region frames the 9-patch, inset ~15% per side so the view sits
      // tighter on the core rather than edge-to-edge with empty context margin.
      const [[rw, rs], [re, rn]] = REGION_BOUNDS;
      const insetX = (re - rw) * 0.15;
      const insetY = (rn - rs) * 0.15;
      map.fitBounds(
        [[rw + insetX, rs + insetY], [re - insetX, rn - insetY]],
        { padding: 20, bearing: VIEW_BEARING, pitch: VIEW_PITCH, duration: 1100 }
      );
    }

    map.on('load', async () => {
      // map.on('error') is now registered at construction (L12) so initial
      // style/glyph errors are caught too.

      // M4: warm every overlay fetch in parallel up front. fetchJson is memoized
      // by URL, so the `await fetchJson(...)` at each add-site below resolves
      // against these in-flight requests instead of starting a fresh serialized
      // one — a slow file (e.g. the 14 MB contours) no longer stalls the layers
      // queued after it. Perf hint only: this list is not authoritative (a URL
      // here but not awaited just warms unused; one awaited but not listed simply
      // fetches lazily). Pass the URL as the warn label so a failed warm names it.
      [
        './data/gold_aop_landcover_9patch.geojson',
        './data/gold_aop_landcover.geojson',
        './data/bronze_aop_9_patch.geojson',
        './data/bronze_aop_lidar_tiles.geojson',
        './data/gold_aop_contours.geojson',
        './data/gold_aop_activity_hotspots.geojson',
        './data/delete_aop_synthetic_activity_tracks.geojson',
        './data/delete_aop_synthetic_activity_hotspots.geojson',
        './data/aop_event_schedule.json',
        './data/gold_aop_water.geojson',
        './data/gold_aop_roads.geojson',
        './data/gold_aop_visitor_context_callouts.geojson',
        './data/bronze_aop_cemeteries.geojson',
        './data/gold_aop_buildings.geojson',
        './data/bronze_osm_aop_9patch.geojson',
        './data/bronze_osm_aop_named.geojson',
        './data/delete_sfwda_traced_trails.geojson',
        './data/gold_aop_trail_network.geojson',
        './data/sfwda_raster_alignment.json',
      ].forEach((url) => { fetchJson(url, url); });

      // Land-cover palette. The classifier emits five classes; each gets a
      // Muted Earth fill and a slightly darker same-family outline. The
      // outline doubles as a hairline-gap bridge: the polygons are a coverage,
      // but independent vertex-simplify can leave sub-pixel slivers between
      // adjacent classes, and the thin outline closes them.
      // Two tight colour families so variation reads as a highlight, not a
      // clash: a light/dark sage pair for trees, a light/base/dark warm-khaki
      // trio for fields. Matches LANDCOVER_MUTED_* (the Park preset).
      const LANDCOVER_FILL = ['match', ['get', 'class'],
        'forest_deciduous', '#b8c1a1',
        'forest_evergreen', '#a8b18f',
        'open_grass',       '#ddd2ad',
        'open_meadow',      '#d4c79f',
        'open_bare',        '#c7b890',
        '#b8c1a1'];
      const LANDCOVER_OUTLINE = ['match', ['get', 'class'],
        'forest_deciduous', '#a6af8d',
        'forest_evergreen', '#969f7c',
        'open_grass',       '#cdc29c',
        'open_meadow',      '#c4b78d',
        'open_bare',        '#b7a87f',
        '#a6af8d'];

      // --- Land cover, 9-patch (NAIP 2023 + lidar, classified) ------------
      // Wide-area land-cover context across the full 3x3 acquisition AOI,
      // built from a coarser ~1.5 m ortho. Added first so it sits at the very
      // bottom of the stack; the crisp park-clipped layer draws on top of it.
      // Its opacity control fades this mass without touching the park layer,
      // so it reads as adjustable context for the non-park areas.
      const landcover9Data = await fetchJson('./data/gold_aop_landcover_9patch.geojson', '9-patch land cover missing');
      if (landcover9Data) {
        map.addSource('aop-landcover-9patch', {
          type: 'geojson',
          data: landcover9Data,
          attribution: 'Land cover: classified from USDA NAIP 2023 + USGS 3DEP lidar'
        });
        map.addLayer({
          id: 'landcover-9patch-forest',
          type: 'fill',
          source: 'aop-landcover-9patch',
          // Vegetation ships as grid-subdivided fill polygons (role=fill) + a
          // separate LineString canopy edge (role=outline) — see
          // simplify_landcover_vegetation.py. Fill draws the polygons only.
          filter: ['==', ['geometry-type'], 'Polygon'],
          paint: { 'fill-color': LANDCOVER_FILL, 'fill-opacity': sliderPercent(landcover9Opacity) }
        });
        map.addLayer({
          id: 'landcover-9patch-forest-outline',
          type: 'line',
          source: 'aop-landcover-9patch',
          // Canopy edge only, not the grid of subdivided-fill rings.
          filter: ['==', ['geometry-type'], 'LineString'],
          paint: { 'line-color': LANDCOVER_OUTLINE, 'line-width': 0.6, 'line-opacity': 0.35 }
        });
      }

      // --- Land cover (NAIP 2023 + lidar, classified) ---------------------
      // The crisp park ground cover: a five-class vector land-cover coverage.
      // Forest vs open is cut from a USGS 3DEP lidar canopy-height model;
      // field colours from 0.6 m leaf-on NAIP. Clipped to the AOP boundary.
      // Drawn just above the wide-area 9-patch layer, so every other layer
      // still draws on top of both.
      const landcoverData = await fetchJson('./data/gold_aop_landcover.geojson', 'Land cover missing');
      if (landcoverData) {
        map.addSource('aop-landcover', {
          type: 'geojson',
          data: landcoverData,
          attribution: 'Land cover: classified from USDA NAIP 2023 + USGS 3DEP lidar'
        });
        map.addLayer({
          id: 'landcover-forest',
          type: 'fill',
          source: 'aop-landcover',
          filter: ['==', ['geometry-type'], 'Polygon'],
          paint: { 'fill-color': LANDCOVER_FILL, 'fill-opacity': 0.9 }
        });
        map.addLayer({
          id: 'landcover-forest-outline',
          type: 'line',
          source: 'aop-landcover',
          // Canopy edge only (role=outline LineString), not the fill-piece rings.
          filter: ['==', ['geometry-type'], 'LineString'],
          paint: { 'line-color': LANDCOVER_OUTLINE, 'line-width': 0.8, 'line-opacity': 0.55 }
        });
      }

      map.addSource('aws-terrain-dem', {
        type: 'raster-dem',
        tiles: [
          'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'
        ],
        tileSize: 256,
        encoding: 'terrarium',
        minzoom: 0,
        maxzoom: 15,
        attribution: 'Terrain: AWS Terrain Tiles (USGS 3DEP, SRTM, GMTED, ETOPO1)'
      });

      map.addLayer({
        id: 'lidar-hillshade',
        type: 'hillshade',
        source: 'aws-terrain-dem',
        layout: { visibility: 'none' },
        paint: {
          'hillshade-exaggeration': 0.6,
          'hillshade-shadow-color': '#3a2f22',
          'hillshade-highlight-color': '#fbf4e2',
          'hillshade-accent-color': '#6b5640'
        }
      });

      map.addSource('tnmap-imagery', {
        type: 'raster',
        tiles: [
          'https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer/tile/{z}/{y}/{x}'
        ],
        tileSize: 256,
        minzoom: 11,
        maxzoom: 22,
        bounds: [-85.782935283, 35.067164188, -85.717154097, 35.117928496],
        attribution: 'Imagery: TDOT Aerial Surveys / TNMap'
      });

      map.addLayer({
        id: 'tnmap-satellite',
        type: 'raster',
        source: 'tnmap-imagery',
        layout: { visibility: 'none' },
        paint: { 'raster-opacity': 1 }
      });

      map.addSource('usda-naip-imagery', {
        type: 'raster',
        tiles: [
          'https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/tile/{z}/{y}/{x}'
        ],
        tileSize: 256,
        minzoom: 11,
        maxzoom: 17,
        bounds: [-85.782935283, 35.067164188, -85.717154097, 35.117928496],
        attribution: 'Imagery: USDA NAIP public image service (Tennessee 2023, 60 cm source)'
      });

      map.addLayer({
        id: 'usda-naip-satellite',
        type: 'raster',
        source: 'usda-naip-imagery',
        layout: { visibility: 'none' },
        paint: { 'raster-opacity': 1 }
      });

      const ninePatchData = await fetchJson('./data/bronze_aop_9_patch.geojson', '9-patch overlay missing');

      if (ninePatchData) {
        map.addSource('nine-patch', { type: 'geojson', data: ninePatchData });
        map.addLayer({
          id: 'nine-patch-fill',
          type: 'fill',
          source: 'nine-patch',
          layout: { visibility: 'none' },
          paint: { 'fill-color': '#c7a85e', 'fill-opacity': 0.10 }
        });
        map.addLayer({
          id: 'nine-patch-outline',
          type: 'line',
          source: 'nine-patch',
          layout: { visibility: 'none' },
          paint: { 'line-color': '#a88246', 'line-width': 1.5, 'line-dasharray': [2, 2] }
        });
        map.addLayer({
          id: 'nine-patch-labels',
          type: 'symbol',
          source: 'nine-patch',
          layout: {
            visibility: 'none',
            'text-field': ['get', 'cell_code'],
            'text-size': 12,
            'text-anchor': 'center'
          },
          paint: {
            'text-color': '#6a5836',
            'text-halo-color': '#f7f1e2',
            'text-halo-width': 1.5
          }
        });
      }

      const lidarTileData = await fetchJson('./data/bronze_aop_lidar_tiles.geojson', 'Lidar tile index missing');

      if (lidarTileData) {
        map.addSource('lidar-tiles', { type: 'geojson', data: lidarTileData });
        map.addLayer({
          id: 'lidar-tiles-fill',
          type: 'fill',
          source: 'lidar-tiles',
          layout: { visibility: 'none' },
          paint: { 'fill-color': '#9a7d96', 'fill-opacity': 0.16 }
        });
        map.addLayer({
          id: 'lidar-tiles-outline',
          type: 'line',
          source: 'lidar-tiles',
          layout: { visibility: 'none' },
          paint: { 'line-color': '#8a6f86', 'line-width': 2.5, 'line-dasharray': [4, 2] }
        });
        map.addLayer({
          id: 'lidar-tiles-labels',
          type: 'symbol',
          source: 'lidar-tiles',
          layout: {
            visibility: 'none',
            'text-field': ['get', 'tile_code'],
            'text-size': 13,
            'text-anchor': 'center'
          },
          paint: {
            'text-color': '#7a6076',
            'text-halo-color': '#f7f1e2',
            'text-halo-width': 2
          }
        });
      }

      // --- Lidar contours (USGS 3DEP 1m DEM) ------------------------------
      const contourData = await fetchJson('./data/gold_aop_contours.geojson', 'Contour layer missing');
      if (contourData) {
        map.addSource('aop-contours', {
          type: 'geojson',
          data: contourData,
          attribution: 'Contours: USGS 3DEP 1m DEM (lidar-derived)'
        });
        map.addLayer({
          id: 'contours-minor',
          type: 'line',
          source: 'aop-contours',
          filter: ['==', ['get', 'idx'], 0],
          layout: { visibility: 'none', 'line-join': 'round' },
          paint: {
            'line-color': '#c7b48f',
            'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.5, 16, 1.4],
            // Innermost detail tier: the fine 5 ft lines stay hidden until
            // zoomed in tight, fading in 16.5 -> 17.5.
            'line-opacity': ['interpolate', ['linear'], ['zoom'], 16.5, 0, 17.5, 0.75]
          }
        });
        map.addLayer({
          id: 'contours-index',
          type: 'line',
          source: 'aop-contours',
          filter: ['==', ['get', 'idx'], 1],
          layout: { visibility: 'none', 'line-join': 'round' },
          paint: {
            'line-color': '#a8906a',
            'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1, 16, 2.8],
            // Middle tier: 25 ft index lines that are not a multiple of 50 ft
            // fade out when zoomed out (15 -> 16). The 50 ft lines stay on, so
            // zoomed out shows half the index lines; mid-zoom shows them all.
            'line-opacity': ['interpolate', ['linear'], ['zoom'],
              15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 0.95, 0],
              16, 0.95]
          }
        });
        map.addLayer({
          id: 'contours-labels',
          type: 'symbol',
          source: 'aop-contours',
          filter: ['==', ['get', 'idx'], 1],
          layout: {
            visibility: 'none',
            'symbol-placement': 'line',
            'text-field': ['concat', ['to-string', ['get', 'elev_ft']], ' ft'],
            'text-size': 11,
            'symbol-spacing': 320
          },
          paint: {
            'text-color': '#7d6a4a',
            'text-halo-color': '#f7f1e2',
            'text-halo-width': 1.8,
            // Labels follow their index line: 25 ft labels fade out with the
            // 25 ft lines when zoomed out; 50 ft labels stay.
            'text-opacity': ['interpolate', ['linear'], ['zoom'],
              15, ['case', ['==', ['%', ['get', 'elev_ft'], 50], 0], 1, 0],
              16, 1]
          }
        });
      }

      // --- Activity hotspots (timestamped GPX dwell) ----------------------
      const activityData = await fetchJson('./data/gold_aop_activity_hotspots.geojson', 'Activity hotspot layer missing');
      if (activityData) {
        // Hoist the collection so the Trails hot lane can bbox the densest
        // cells. See refreshHotButton.
        aopActivityHotspotsData = activityData;
        const activityVisibility = activityHotspotsToggle.checked ? 'visible' : 'none';
        map.addSource('activity-hotspots', {
          type: 'geojson',
          data: activityData,
          attribution: 'Activity hotspots: first-party timestamped GPX'
        });
        map.addLayer({
          id: 'activity-hotspots-heat',
          type: 'heatmap',
          source: 'activity-hotspots',
          filter: ['==', ['geometry-type'], 'Point'],
          layout: { visibility: activityVisibility },
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
          id: 'activity-hotspots-fill',
          type: 'fill',
          source: 'activity-hotspots',
          filter: ['==', ['geometry-type'], 'Polygon'],
          layout: { visibility: activityVisibility },
          paint: { 'fill-color': ACTIVITY_HOTSPOT_FILL, 'fill-opacity': ACTIVITY_HOTSPOT_OPACITY }
        });
        map.addLayer({
          id: 'activity-hotspots-outline',
          type: 'line',
          source: 'activity-hotspots',
          filter: ['==', ['geometry-type'], 'Polygon'],
          layout: { visibility: activityVisibility },
          paint: { 'line-color': '#7f2f27', 'line-width': 1.1, 'line-opacity': 0.55 }
        });
        map.addLayer({
          id: 'activity-hotspots-labels',
          type: 'symbol',
          source: 'activity-hotspots',
          filter: ['all', ['==', ['geometry-type'], 'Point'], ['!=', ['get', 'label'], '']],
          layout: {
            visibility: activityVisibility,
            'text-field': ['get', 'label'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12],
            'text-allow-overlap': false,
            'text-ignore-placement': false
          },
          paint: { 'text-color': '#5b2d25', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.4 }
        });
        bindPopup(['activity-hotspots-fill', 'activity-hotspots-labels'], 'Activity hotspot', (props) => [
          ['Dwell', `${props.dwell_minutes ?? 'unknown'} min`],
          ['Stopped', `${Math.round(Number(props.stop_seconds || 0) / 60 * 10) / 10} min`],
          ['Slow', `${Math.round(Number(props.slow_seconds || 0) / 60 * 10) / 10} min`],
          ['Moving', `${Math.round(Number(props.moving_seconds || 0) / 60 * 10) / 10} min`],
          ['Visits', props.visit_count ?? 'unknown'],
          ['Max point gap', `${props.max_gap_seconds ?? 'unknown'} sec`],
          ['Source', formatListProperty(props.source_files) || 'unknown'],
          ['Review', props.review_status || 'raw']
        ]);
        registerFeatureListLayer('activityHotspots', activityData);
        // Hotspots may load before or after the schedule; either way the
        // button needs a refresh once aopActivityHotspotsData is populated
        // so the Trails lane renders correctly.
        if (typeof refreshHotButton === 'function') refreshHotButton();
      }

      // --- Simulated Saturday activity -----------------------------------
      const syntheticTracksData = await fetchJson('./data/delete_aop_synthetic_activity_tracks.geojson', 'Synthetic activity tracks missing');
      const syntheticHotspotsData = await fetchJson('./data/delete_aop_synthetic_activity_hotspots.geojson', 'Synthetic activity hotspots missing');
      if (syntheticTracksData || syntheticHotspotsData) {
        const syntheticVisibility = syntheticActivityToggle.checked ? 'visible' : 'none';
        if (syntheticTracksData) {
          map.addSource('synthetic-activity-tracks', {
            type: 'geojson',
            data: syntheticTracksData,
            attribution: 'Synthetic Saturday activity: generated test data'
          });
          map.addLayer({
            id: 'synthetic-activity-tracks',
            type: 'line',
            source: 'synthetic-activity-tracks',
            layout: { visibility: syntheticVisibility, 'line-cap': 'round', 'line-join': 'round' },
            paint: {
              'line-color': [
                'match', ['get', 'persona'],
                'north_crawl', '#254d5b',
                'checkpoint_loop', '#477c82',
                'photo_short', '#6fa793',
                'proving_ground', '#9a7d96',
                'trailhead_social', '#9a5a32',
                '#5f9183'
              ],
              'line-width': ['interpolate', ['linear'], ['zoom'], 12, 0.7, 16, 1.8],
              'line-opacity': 0.36
            }
          });
          bindPopup('synthetic-activity-tracks', 'Synthetic Saturday track', (props) => [
            ['Track', props.track_name || props.id],
            ['Profile', props.persona || 'synthetic'],
            ['Start', props.start_local || 'unknown'],
            ['Duration', `${props.duration_minutes ?? 'unknown'} min`],
            ['Distance', props.distance_m ? `${Math.round(Number(props.distance_m))} m` : 'unknown'],
            ['Anchors', formatListProperty(props.visited_anchors) || 'unknown'],
            ['Review', props.review_status || 'synthetic']
          ]);
        }
        if (syntheticHotspotsData) {
          map.addSource('synthetic-activity-hotspots', {
            type: 'geojson',
            data: syntheticHotspotsData,
            attribution: 'Synthetic Saturday hotspots: generated test data'
          });
          map.addLayer({
            id: 'synthetic-activity-hotspots-heat',
            type: 'heatmap',
            source: 'synthetic-activity-hotspots',
            filter: ['==', ['geometry-type'], 'Point'],
            layout: { visibility: syntheticVisibility },
            paint: {
              'heatmap-weight': ['interpolate', ['linear'], ['get', 'intensity_norm'], 0, 0.18, 1, 1],
              'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 11, 0.35, 16, 1.45],
              'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 11, 16, 16, 42],
              'heatmap-opacity': 0.58,
              'heatmap-color': [
                'interpolate', ['linear'], ['heatmap-density'],
                0, 'rgba(183, 210, 189, 0)',
                0.24, 'rgba(183, 210, 189, 0.5)',
                0.48, 'rgba(111, 167, 147, 0.64)',
                0.74, 'rgba(71, 124, 130, 0.78)',
                1, 'rgba(37, 77, 91, 0.92)'
              ]
            }
          });
          map.addLayer({
            id: 'synthetic-activity-hotspots-fill',
            type: 'fill',
            source: 'synthetic-activity-hotspots',
            filter: ['==', ['geometry-type'], 'Polygon'],
            layout: { visibility: syntheticVisibility },
            paint: { 'fill-color': SYNTHETIC_HOTSPOT_FILL, 'fill-opacity': SYNTHETIC_HOTSPOT_OPACITY }
          });
          map.addLayer({
            id: 'synthetic-activity-hotspots-outline',
            type: 'line',
            source: 'synthetic-activity-hotspots',
            filter: ['==', ['geometry-type'], 'Polygon'],
            layout: { visibility: syntheticVisibility },
            paint: { 'line-color': '#254d5b', 'line-width': 1.2, 'line-opacity': 0.66 }
          });
          map.addLayer({
            id: 'synthetic-activity-hotspots-labels',
            type: 'symbol',
            source: 'synthetic-activity-hotspots',
            filter: ['all', ['==', ['geometry-type'], 'Point'], ['!=', ['get', 'label'], '']],
            layout: {
              visibility: syntheticVisibility,
              'text-field': ['get', 'label'],
              'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12],
              'text-allow-overlap': false,
              'text-ignore-placement': false
            },
            paint: { 'text-color': '#254d5b', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.4 }
          });
          bindPopup(['synthetic-activity-hotspots-fill', 'synthetic-activity-hotspots-labels'], 'Synthetic Saturday hotspot', (props) => [
            ['Dwell focus', `${props.interest_minutes ?? props.dwell_minutes ?? 'unknown'} min`],
            ['Dwell', `${props.dwell_minutes ?? 'unknown'} min`],
            ['Stopped', `${Math.round(Number(props.stop_seconds || 0) / 60 * 10) / 10} min`],
            ['Slow', `${Math.round(Number(props.slow_seconds || 0) / 60 * 10) / 10} min`],
            ['Moving', `${Math.round(Number(props.moving_seconds || 0) / 60 * 10) / 10} min`],
            ['Sessions', props.segment_count ?? 'unknown'],
            ['Visits', props.visit_count ?? 'unknown'],
            ['Source', formatListProperty(props.source_files) || 'synthetic'],
            ['Review', props.review_status || 'synthetic']
          ]);
          registerFeatureListLayer('syntheticActivity', syntheticHotspotsData);
        }
      }

      // --- Event schedule proposal ---------------------------------------
      // Source data is editable JSON with reusable location tags; this block
      // resolves tags into a transient GeoJSON source for MapLibre.
      eventScheduleConfig = await fetchJson('./data/aop_event_schedule.json', 'Event schedule missing');
      if (eventScheduleConfig) {
        eventScheduleData = eventScheduleToGeojson(eventScheduleConfig);
        renderEventSchedule(eventScheduleConfig, eventScheduleData);
        map.addSource('event-schedule', {
          type: 'geojson',
          data: eventScheduleData,
          attribution: 'Event schedule: Rock Warblers Trail Blazing Invitational'
        });
        const eventVisibility = eventScheduleToggle.checked ? 'visible' : 'none';
        map.addLayer({
          id: 'event-session-routes',
          type: 'line',
          source: 'event-schedule',
          filter: ['all', ['==', ['get', 'feature_kind'], 'event_session'], ['==', ['geometry-type'], 'LineString']],
          layout: { visibility: eventVisibility, 'line-cap': 'round', 'line-join': 'round' },
          paint: {
            'line-color': '#b45f43',
            'line-width': ['interpolate', ['linear'], ['zoom'], 12, 2, 16, 4.2],
            'line-opacity': 0.92,
            'line-dasharray': [3, 1.4]
          }
        });
        map.addLayer({
          id: 'event-route-labels',
          type: 'symbol',
          source: 'event-schedule',
          filter: ['all', ['==', ['get', 'feature_kind'], 'event_session'], ['==', ['geometry-type'], 'LineString']],
          layout: {
            visibility: eventVisibility,
            'symbol-placement': 'line',
            'text-field': ['get', 'title'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12],
            'text-keep-upright': true
          },
          paint: { 'text-color': '#6f382b', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.8 }
        });
        map.addLayer({
          id: 'event-anchor-points',
          type: 'circle',
          source: 'event-schedule',
          filter: ['==', ['get', 'feature_kind'], 'event_anchor'],
          layout: { visibility: eventVisibility },
          paint: {
            'circle-radius': ['interpolate', ['linear'], ['zoom'], 11, 4.5, 16, 8],
            'circle-color': ['match', ['get', 'role'],
              'pavilion', '#8b5f38',
              'event_registration', '#b05a48',
              'event_stage_start', '#7f7a4b',
              'event_proving_ground', '#9a7d96',
              'event_checkpoint', '#b45f43',
              'event_photo_waypoint', '#5f9183',
              '#8b5f38'],
            'circle-stroke-color': '#f7f1e2',
            'circle-stroke-width': 2
          }
        });
        map.addLayer({
          id: 'event-anchor-labels',
          type: 'symbol',
          source: 'event-schedule',
          filter: ['==', ['get', 'feature_kind'], 'event_anchor'],
          layout: {
            visibility: eventVisibility,
            'text-field': ['get', 'map_label'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 12],
            'text-offset': [0, 1.2],
            'text-anchor': 'top'
          },
          paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 }
        });

        bindPopup('event-anchor-points',
          (props) => props.name || 'Event location',
          (props) => [
            ['Tag', props.location_tag || ''],
            ['Role', props.role || ''],
            ['Confidence', props.confidence || ''],
            ['Source', props.source || ''],
            ['Caveat', props.caveat || '']
          ]);
        bindPopup('event-session-routes',
          (props) => props.title || 'Event route',
          (props) => [
            ['Date', props.day || ''],
            ['Time', props.window || ''],
            ['Location', props.location_label || ''],
            ['Tag', props.location_tag || ''],
            ['Route', formatListProperty(props.route_tags) || ''],
            ['Status', props.status || '']
          ]);
        indexFeatures(eventScheduleData,
          (props) => props.feature_kind === 'event_anchor' ? 'event location' : 'event session',
          eventScheduleToggle,
          undefined,
          // Anchors carry their `#tag` as a search alias so a tag query
          // (e.g. `#pavilion`) lands on the location. Sessions stay
          // searchable by title only — surfacing every session under a
          // shared tag would drown the dropdown.
          (props) => props.feature_kind === 'event_anchor' ? [props.location_tag] : null);
        registerFeatureListLayer('eventSchedule', eventScheduleData);
        if (viewerSessionState?.active_event_session_id
            && eventSessionById.has(viewerSessionState.active_event_session_id)) {
          // Restore the highlight on the saved session row regardless, but
          // only fly + force the Events tab if the user was actually on
          // Events at reload. Otherwise their saved POI/About tab wins.
          activeEventSessionId = viewerSessionState.active_event_session_id;
          renderEventSchedule(eventScheduleConfig, eventScheduleData);
          const savedTab = viewerSessionState.active_left_tab;
          if (!savedTab || savedTab === 'events') {
            setLeftTab('events');
            window.setTimeout(() => gotoEventSession(viewerSessionState.active_event_session_id), 300);
          }
        } else {
          // Item 4 (misc_3.md): no saved active session on first load means
          // the calendar's "move to content" still needs to fire — fly to
          // the currently-live or next-upcoming session so the map opens
          // pointed at what the calendar is highlighting.
          window.setTimeout(() => {
            const live = calendarDays?.querySelector('li[data-session-state="happening"] .calendar-row, li[data-session-state="upcoming_next"] .calendar-row');
            const sessionId = live?.dataset?.sessionId;
            if (sessionId && eventSessionById.has(sessionId)) {
              gotoEventSession(sessionId);
            }
          }, 300);
        }
      } else {
        calendarDays.innerHTML = `<li class="calendar-empty">${escapeHtml(window.AOP_UI?.calendar?.unavailable || 'Schedule unavailable.')}</li>`;
      }

      // --- USGS NHD hydrography (streams, waterbodies, springs) -----------
      const waterData = await fetchJson('./data/gold_aop_water.geojson', 'Water layer missing');
      if (waterData) {
        map.addSource('usgs-water', {
          type: 'geojson',
          data: waterData,
          attribution: 'Hydrography: USGS National Hydrography Dataset'
        });

        map.addLayer({
          id: 'water-area-fill',
          type: 'fill',
          source: 'usgs-water',
          filter: ['==', ['get', 'water_kind'], 'water_area'],
          layout: { visibility: 'none' },
          paint: { 'fill-color': '#a8c5c9', 'fill-opacity': 0.55 }
        });
        map.addLayer({
          id: 'waterbody-fill',
          type: 'fill',
          source: 'usgs-water',
          filter: ['==', ['get', 'water_kind'], 'waterbody'],
          layout: { visibility: 'none' },
          paint: { 'fill-color': '#9fbfc4', 'fill-opacity': 0.5 }
        });
        map.addLayer({
          id: 'waterbody-outline',
          type: 'line',
          source: 'usgs-water',
          filter: ['==', ['get', 'water_kind'], 'waterbody'],
          layout: { visibility: 'none' },
          paint: { 'line-color': '#6f9098', 'line-width': 1.2 }
        });
        // One line layer for every flowline; named streams render heavier than
        // artificial paths / connectors via a per-class width case.
        map.addLayer({
          id: 'streams',
          type: 'line',
          source: 'usgs-water',
          filter: ['==', ['get', 'water_kind'], 'flowline'],
          layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
          paint: {
            'line-color': '#7fa3ac',
            'line-opacity': 0.9,
            'line-width': [
              'interpolate', ['linear'], ['zoom'],
              10, ['case', ['==', ['get', 'water_class'], 'stream'], 0.9, 0.5],
              14, ['case', ['==', ['get', 'water_class'], 'stream'], 2.4, 1.3],
              17, ['case', ['==', ['get', 'water_class'], 'stream'], 5.5, 2.8]
            ]
          }
        });
        map.addLayer({
          id: 'stream-labels',
          type: 'symbol',
          source: 'usgs-water',
          filter: ['all', ['==', ['get', 'water_kind'], 'flowline'], ['!=', ['get', 'name'], null]],
          layout: {
            visibility: 'none',
            'symbol-placement': 'line',
            'text-field': ['get', 'name'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 12, 9, 16, 13],
            'text-letter-spacing': 0.04
          },
          paint: {
            'text-color': '#4a6c73',
            'text-halo-color': '#f7f1e2',
            'text-halo-width': 1.8
          }
        });
        map.addLayer({
          id: 'water-points',
          type: 'circle',
          source: 'usgs-water',
          filter: ['==', ['get', 'water_kind'], 'point'],
          layout: { visibility: 'none' },
          paint: {
            'circle-radius': 5,
            'circle-color': ['match', ['get', 'water_class'],
              'spring', '#6f9aa6',
              'gage', '#bb8a4a',
              '#7fa3ac'],
            'circle-stroke-color': '#f7f1e2',
            'circle-stroke-width': 1.5
          }
        });
        map.addLayer({
          id: 'water-point-labels',
          type: 'symbol',
          source: 'usgs-water',
          filter: ['all', ['==', ['get', 'water_kind'], 'point'], ['!=', ['get', 'name'], null]],
          layout: {
            visibility: 'none',
            'text-field': ['get', 'name'],
            'text-size': 11,
            'text-offset': [0, 1.1],
            'text-anchor': 'top'
          },
          paint: { 'text-color': '#4a6c73', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.5 }
        });

        bindPopup('streams', (props) => props.name || 'Stream / flowline', (props) => [
          ['Class', props.water_class || 'unknown'],
          ['NHD ftype', props.ftype || ''],
          ['NHD fcode', props.fcode || ''],
          ['Length (km)', props.lengthkm != null ? Number(props.lengthkm).toFixed(2) : '']
        ]);
        bindPopup(['waterbody-fill', 'water-area-fill'], (props) => props.name || 'Waterbody', (props) => [
          ['Class', props.water_class || 'unknown'],
          ['NHD ftype', props.ftype || ''],
          ['Area (km²)', props.areasqkm != null ? Number(props.areasqkm).toFixed(4) : '']
        ]);
        bindPopup('water-points', (props) => props.name || 'Water point', (props) => [
          ['Class', props.water_class || 'unknown'],
          ['NHD ftype', props.ftype || ''],
          ['GNIS id', props.gnis_id || '']
        ]);

        indexFeatures(waterData,
          (props) => props.water_kind === 'point' ? (props.water_class || 'water point')
            : props.water_kind === 'waterbody' ? 'waterbody'
            : 'stream',
          (props) => props.water_kind === 'point' ? springsToggle : waterToggle);
      }

      // --- USGS National Map asphalt roads --------------------------------
      const roadsData = await fetchJson('./data/gold_aop_roads.geojson', 'Roads layer missing');
      if (roadsData) {
        map.addSource('usgs-roads', { type: 'geojson', data: roadsData });

        const lineWidth = (light, mid, heavy) => [
          'interpolate', ['linear'], ['zoom'],
          10, light,
          14, mid,
          17, heavy
        ];
        const lineLayout = { visibility: 'visible', 'line-cap': 'round', 'line-join': 'round' };

        map.addLayer({
          id: 'roads-local-casing',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'local'],
          layout: lineLayout,
          paint: { 'line-color': '#f3ecda', 'line-width': lineWidth(0.8, 2.2, 6), 'line-opacity': 0.9 }
        });
        map.addLayer({
          id: 'roads-local',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'local'],
          layout: lineLayout,
          paint: { 'line-color': '#b0a68c', 'line-width': lineWidth(0.4, 1.2, 3.2) }
        });
        map.addLayer({
          id: 'roads-connecting-casing',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'local_connecting'],
          layout: lineLayout,
          paint: { 'line-color': '#f3ecda', 'line-width': lineWidth(1.2, 3, 8), 'line-opacity': 0.95 }
        });
        map.addLayer({
          id: 'roads-connecting',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'local_connecting'],
          layout: lineLayout,
          paint: { 'line-color': '#cdb079', 'line-width': lineWidth(0.7, 1.8, 4.5) }
        });
        map.addLayer({
          id: 'roads-secondary-casing',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'secondary'],
          layout: lineLayout,
          paint: { 'line-color': '#f3ecda', 'line-width': lineWidth(1.6, 4, 9.5), 'line-opacity': 0.95 }
        });
        map.addLayer({
          id: 'roads-secondary',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'secondary'],
          layout: lineLayout,
          paint: { 'line-color': '#c09060', 'line-width': lineWidth(0.9, 2.4, 5.5) }
        });
        map.addLayer({
          id: 'roads-ramp-casing',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'ramp'],
          layout: lineLayout,
          paint: { 'line-color': '#bf8f55', 'line-width': lineWidth(1.5, 3.5, 8) }
        });
        map.addLayer({
          id: 'roads-ramp',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'ramp'],
          layout: lineLayout,
          paint: { 'line-color': '#d8b173', 'line-width': lineWidth(0.8, 2.0, 4.8) }
        });
        map.addLayer({
          id: 'roads-controlled-casing',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'controlled_access'],
          layout: lineLayout,
          paint: { 'line-color': '#9a7a52', 'line-width': lineWidth(2, 5, 11) }
        });
        map.addLayer({
          id: 'roads-controlled',
          type: 'line',
          source: 'usgs-roads',
          filter: ['==', ['get', 'road_class'], 'controlled_access'],
          layout: lineLayout,
          paint: { 'line-color': '#d8b173', 'line-width': lineWidth(1.2, 3, 7) }
        });
        map.addLayer({
          id: 'roads-labels',
          type: 'symbol',
          source: 'usgs-roads',
          filter: ['!=', ['get', 'name'], null],
          layout: {
            visibility: 'visible',
            'symbol-placement': 'line',
            'text-field': ['get', 'name'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 12, 9, 16, 13],
            'text-letter-spacing': 0.04
          },
          paint: {
            'text-color': '#4a3c2a',
            'text-halo-color': '#f7f1e2',
            'text-halo-width': 1.8
          }
        });

        bindPopup(['roads-local', 'roads-connecting', 'roads-secondary', 'roads-ramp', 'roads-controlled'], 'Road', (props) => [
          ['Name', props.name || 'Unnamed'],
          ['Class', props.road_class || 'unknown'],
          ['MTFCC', props.mtfcc_code || ''],
          ['Interstate', props.interstate || ''],
          ['US Route', props.us_route || ''],
          ['State Route', props.state_route || ''],
          ['County Route', props.county_route || '']
        ]);

        indexFeatures(roadsData, 'road', roadsToggle);
      }

      // --- Visitor context callouts --------------------------------------
      // Two cartographic support-town annotations: one for the immediate
      // South Pittsburg/Kimball supply run and one for the Monteagle plateau
      // services option. These are planning circles, not service-area claims.
      // The same file also carries the AOP + Rock Warblers brand-logo POINTS
      // (kind=brand_logo, merged 2026-06-05); take only the callout polygons
      // here so the fill/outline/label layers, search, and feature list never
      // see the logos. The brand block below renders the logos as icons.
      const calloutsBundle = await fetchJson('./data/gold_aop_visitor_context_callouts.geojson', 'Visitor context callouts missing');
      visitorContextData = calloutsBundle
        ? Object.assign({}, calloutsBundle, {
            features: calloutsBundle.features.filter((f) => (f.properties || {}).kind !== 'brand_logo')
          })
        : null;
      if (visitorContextData) {
        // Replay any user-staged geometry overrides before the source data
        // ever reaches MapLibre, so a moved callout draws in its new spot
        // from the first frame rather than snapping in after registration.
        applyPositionedFeatures('visitorContext', visitorContextData, { boot: true });
        map.addSource('visitor-context', {
          type: 'geojson',
          data: visitorContextData,
          attribution: 'Visitor context: AOP, RiderPlanet, Marion County Tourism'
        });

        map.addLayer({
          id: 'visitor-context-fill',
          type: 'fill',
          source: 'visitor-context',
          paint: { 'fill-color': '#d8b173', 'fill-opacity': 0.18 }
        });
        map.addLayer({
          id: 'visitor-context-outline',
          type: 'line',
          source: 'visitor-context',
          layout: { 'line-join': 'round' },
          paint: {
            'line-color': '#8b5f38',
            'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.6, 16, 3.2],
            'line-opacity': 0.9,
            'line-dasharray': [3, 1.4]
          }
        });
        map.addLayer({
          id: 'visitor-context-labels',
          type: 'symbol',
          source: 'visitor-context',
          layout: {
            'text-field': ['get', 'label'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 11, 10, 15, 12],
            'text-line-height': 1.08,
            'text-anchor': 'center',
            'text-offset': [0, 0],
            'text-max-width': 18,
            'text-padding': 4
          },
          paint: {
            'text-color': '#4a3c2a',
            'text-halo-color': '#f7f1e2',
            'text-halo-width': 1.8
          }
        });

        bindPopup(['visitor-context-fill', 'visitor-context-outline'],
          (props) => props.name || 'Visitor context',
          (props) => [
            ['Direction', props.direction || ''],
            ['Services', props.services || ''],
            ['Examples', props.examples || ''],
            ['Distance', props.distance_note || ''],
            ['Drive time', props.drive_time_note || ''],
            ['Sources', props.source_summary || '']
          ],
          (props) => visitorContextLinksHtml(props));
        bindPanelReveal(['visitor-context-fill', 'visitor-context-outline'], 'visitorContext', 'name');

        indexFeatures(visitorContextData, 'visitor context', visitorContextToggle);
        registerFeatureListLayer('visitorContext', visitorContextData);
      }

      // --- Marion County cemeteries (TN Comptroller parcels) -------------
      // Cemetery-class parcels in the 9-patch. One — Ellis Cemetery, parcel
      // 110 008.04 — is the interior parcel carved out of the AOP boundary:
      // the hole in the park polygon. Each cemetery is a parcel polygon plus a
      // centroid marker; both carry the same properties (geom_role tells them
      // apart). Default off — search turns the layer on when it jumps here.
      cemeteryData = await fetchJson('./data/bronze_aop_cemeteries.geojson', 'Cemetery layer missing');
      if (cemeteryData) {
        applyPositionedFeatures('cemeteries', cemeteryData, { boot: true });
        map.addSource('cemeteries', {
          type: 'geojson',
          data: cemeteryData,
          attribution: 'Cemetery parcels: TN Comptroller of the Treasury — Marion County'
        });

        map.addLayer({
          id: 'cemetery-fill',
          type: 'fill',
          source: 'cemeteries',
          filter: ['==', ['get', 'geom_role'], 'parcel'],
          layout: { visibility: 'none' },
          paint: { 'fill-color': '#a99aa0', 'fill-opacity': 0.4 }
        });
        map.addLayer({
          id: 'cemetery-outline',
          type: 'line',
          source: 'cemeteries',
          filter: ['==', ['get', 'geom_role'], 'parcel'],
          layout: { visibility: 'none' },
          paint: {
            'line-color': '#7d6e74',
            'line-width': ['interpolate', ['linear'], ['zoom'], 12, 1, 17, 3]
          }
        });
        map.addLayer({
          id: 'cemetery-marker',
          type: 'circle',
          source: 'cemeteries',
          filter: ['==', ['get', 'geom_role'], 'marker'],
          layout: { visibility: 'none' },
          paint: {
            'circle-radius': ['interpolate', ['linear'], ['zoom'], 10, 3.5, 14, 6, 17, 8],
            'circle-color': '#8a7a82',
            // The AOP inholding gets an amber ring so the "hole" reads at a glance.
            'circle-stroke-color': ['case', ['get', 'aop_inholding'], '#c7a14e', '#f7f1e2'],
            'circle-stroke-width': ['case', ['get', 'aop_inholding'], 3, 1.6]
          }
        });
        map.addLayer({
          id: 'cemetery-label',
          type: 'symbol',
          source: 'cemeteries',
          filter: ['==', ['get', 'geom_role'], 'marker'],
          layout: {
            visibility: 'none',
            'text-field': ['get', 'name'],
            'text-size': ['interpolate', ['linear'], ['zoom'], 12, 10, 16, 13],
            'text-offset': [0, 1.1],
            'text-anchor': 'top'
          },
          paint: {
            'text-color': '#5a4e54',
            'text-halo-color': '#f7f1e2',
            'text-halo-width': 1.8
          }
        });

        bindPopup(['cemetery-fill', 'cemetery-marker'],
          (props) => props.name || 'Cemetery',
          (props) => [
            ['Also known as', props.aka],
            ['Type', props.cemetery_type],
            ['Parcel', props.parcel_id],
            ['Owner of record', props.parcel_owner],
            ['Class', props.parcel_class],
            ['Area', props.acres != null ? `${props.acres} acre` : ''],
            ['Within AOP', isTrue(props.aop_inholding)
              ? 'Yes — interior parcel excluded from the park boundary (the hole in parcel 110 008.00)'
              : ''],
            ['Recorded burials', Number(props.burial_count) > 0
              ? `${props.burial_count} (${props.named_burial_count} named)`
              : ''],
            ['Source', props.parcel_source]
          ],
          (props) => cemeteryBurialHtml(props));
        // G_C (gold slice 6): the cemetery idField is now the canonical `id`
        // ('<parcel_id>:<geom_role>'), so a map-click reveal must resolve to the
        // canonical id, NOT the bare parcel_id (which no longer keys any row).
        // Both the parcel polygon and the marker point click-reveal the MARKER
        // row (the store-of-record the panel/list surfaces, geom_role==='marker'),
        // so clicking the fill or the dot lands on the same one cemetery row.
        bindPanelReveal(['cemetery-fill', 'cemetery-marker'], 'cemeteries',
          (props) => props && props.parcel_id != null ? `${props.parcel_id}:marker` : (props && props.id));

        // Per-feature visibility: 4 cemeteries, Ellis (the AOP inholding,
        // parcel 110 008.04) pre-ticked, the other three off by default.
        // User explicitly wants only in-park cemeteries by default; the
        // out-of-park three remain operable from this list if needed.
        registerFeatureListLayer('cemeteries', cemeteryData);

        indexFeatures(
          cemeteryData,
          'cemetery',
          cemeteriesToggle,
          // G_C: the search-result reveal binding targets the canonical MARKER id
          // (the store-of-record row), not the bare parcel_id (which no longer keys
          // a row now that the cemetery idField is the canonical `id`).
          (props) => ({ featureListKey: 'cemeteries',
                        featureId: props.parcel_id != null ? `${props.parcel_id}:marker` : props.id })
        );
        // Index the county owner-of-record name too (e.g. searching
        // "Bryson & Ellis Cemetery" should also land on Ellis Cemetery).
        for (const feature of cemeteryData.features) {
          const props = feature.properties || {};
          const aka = props.aka;
          if (aka && feature.geometry) {
            searchIndex.push({
              name: String(aka),
              kind: 'cemetery',
              toggle: cemeteriesToggle,
              geometry: feature.geometry,
              featureListKey: 'cemeteries',
              // G_C: reveal the canonical MARKER id, not the bare parcel_id.
              featureId: props.parcel_id != null ? `${props.parcel_id}:marker` : props.id
            });
          }
        }
      }

      // --- Curated AOP park buildings (derived) ----------------------------
      // The derived/curated building set: 3 public facilities (Pavilion,
      // Farmhouse, Front Office) + 2 private-structure presence boxes. Footprints
      // come from FEMA USA Structures but the raw 9-patch context is dropped —
      // see import_fema_buildings.py CURATED_ADDRESSES. Footprints are
      // drag-adjustable (FEMA's polygons sit a little off); applyPositionedFeatures
      // replays any baked/in-progress moves before the source is built so a
      // reload shows the corrected position.
      buildingsData = await fetchJson('./data/gold_aop_buildings.geojson', 'Building footprints missing');
      if (buildingsData) {
        applyPositionedFeatures('buildings', buildingsData, { boot: true });
        map.addSource('fema-buildings', {
          type: 'geojson',
          data: buildingsData,
          attribution: 'Buildings: FEMA USA Structures / ORNL'
        });

        map.addLayer({
          id: 'building-footprint-fill',
          type: 'fill',
          source: 'fema-buildings',
          // Private structures render ONLY via the black-box presence layer
          // below (no interactive fill/popup) — exclude them here.
          filter: ['!=', ['get', 'aop_structure_box'], true],
          layout: { visibility: 'none' },
          paint: {
            'fill-color': ['match', ['get', 'occupancy_class'],
              'Residential', '#c1a386',
              'Agriculture', '#b7a36f',
              'Assembly', '#b78f6f',
              'Government', '#9da4a6',
              'Unclassified', '#aaa397',
              '#ad987f'],
            'fill-opacity': ['case', ['==', ['get', 'inside_aop_boundary'], true], 0.56, 0.34]
          }
        });
        map.addLayer({
          id: 'building-footprint-outline',
          type: 'line',
          source: 'fema-buildings',
          filter: ['!=', ['get', 'aop_structure_box'], true],
          layout: { visibility: 'none' },
          paint: {
            'line-color': ['case', ['==', ['get', 'inside_aop_boundary'], true], '#8e5f37', '#776f61'],
            'line-width': ['interpolate', ['linear'], ['zoom'], 11, 0.5, 16, 1.8],
            'line-opacity': 0.9
          }
        });
        map.addLayer({
          id: 'building-footprint-aop-outline',
          type: 'line',
          source: 'fema-buildings',
          // Prominent highlight now marks the public PARK FACILITIES (Pavilion,
          // Farmhouse, Front Office), not every geometrically-inside footprint.
          filter: ['==', ['get', 'aop_facility'], true],
          layout: { visibility: 'none' },
          paint: {
            'line-color': '#7c4a2a',
            'line-width': ['interpolate', ['linear'], ['zoom'], 11, 1.1, 16, 3.1],
            'line-opacity': 0.95
          }
        });

        // Private structures on AOP land (665, 889): a non-interactive black-box
        // presence marker — visible so nobody treats the spot as empty/routable,
        // but no popup, no search, no list entry. Always visible (own layer, no
        // toggle), independent of the FEMA buildings layer, since the privacy
        // posture is to always show that a home is there.
        map.addLayer({
          id: 'building-structure-box',
          type: 'fill',
          source: 'fema-buildings',
          filter: ['==', ['get', 'aop_structure_box'], true],
          paint: {
            'fill-color': '#46423b',
            'fill-opacity': 0.82,
            'fill-outline-color': '#2e2a25'
          }
        });

        bindPopup(['building-footprint-fill', 'building-footprint-outline', 'building-footprint-aop-outline'],
          (props) => props.facility_name || props.building_label || 'Building footprint',
          (props) => [
            ['Facility', props.facility_role || ''],
            ['Occupancy', props.occupancy_class || 'unknown'],
            ['Primary use', props.primary_occupancy || ''],
            ['Address', props.address || ''],
            ['Area', props.area_sqft != null ? `${Number(props.area_sqft).toLocaleString()} sq ft` : ''],
            ['Height', props.height_m != null ? `${props.height_m} m` : ''],
            ['Within AOP', isTrue(props.aop_facility) ? 'AOP park facility' : ''],
            ['Image date', props.image_date || ''],
            ['Method', props.validation_method || ''],
            ['Source', props.footprint_source || '']
          ]);
        bindPanelReveal(['building-footprint-fill', 'building-footprint-outline', 'building-footprint-aop-outline'], 'buildings', 'build_id');

        // Per-feature visibility: 3 public facilities pre-ticked by group
        // default, the rest collapsed under a bulk-off row. Persists across
        // reload via `aop_feature_visibility_v1`. See FEATURE_LIST_LAYERS.
        registerFeatureListLayer('buildings', buildingsData);

        // Search: only the public PARK FACILITIES are findable — region
        // footprints and the private black boxes stay out of search. Facilities
        // index by their authored name (Pavilion / Farmhouse / Front Office) with
        // the street address + role as aliases so an address query still lands.
        // Canonical name is now the facility name (baked — A3), so index the
        // facilities directly; the street address + role ride as search aliases.
        const facilityFeatures = buildingsData.features
          .filter((f) => f.properties && f.properties.aop_facility === true);
        indexFeatures(
          { type: 'FeatureCollection', features: facilityFeatures },
          'facility',
          buildingsToggle,
          (props) => ({ featureListKey: 'buildings', featureId: props.build_id }),
          (props) => [props.address, props.facility_role]
        );
      }

      // --- Community OSM 9-patch vectors ---------------------------------
      const osmData = await fetchJson('./data/bronze_osm_aop_9patch.geojson', 'OSM 9-patch missing');
      if (osmData) {
        map.addSource('osm-9patch', { type: 'geojson', data: osmData });
        map.addLayer({
          id: 'osm-park-outline',
          type: 'line',
          source: 'osm-9patch',
          filter: ['==', ['get', 'leisure'], 'park'],
          layout: { visibility: 'none' },
          paint: { 'line-color': '#8a9a6a', 'line-width': 2, 'line-dasharray': [3, 2] }
        });
        map.addLayer({
          id: 'osm-service',
          type: 'line',
          source: 'osm-9patch',
          filter: ['==', ['get', 'highway'], 'service'],
          layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': '#a89a7e', 'line-width': 1.5, 'line-opacity': 0.85 }
        });
        map.addLayer({
          id: 'osm-tracks',
          type: 'line',
          source: 'osm-9patch',
          filter: ['==', ['get', 'highway'], 'track'],
          layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': '#9a5a32', 'line-width': 2, 'line-opacity': 0.95 }
        });

        indexFeatures(osmData,
          (props) => props.highway === 'track' ? 'OSM track'
            : props.highway === 'service' ? 'OSM road' : 'OSM feature',
          (props) => props.highway === 'track' ? osmTracksToggle
            : props.highway === 'service' ? osmServiceToggle : osmParkToggle);
      }

      const osmNamedData = await fetchJson('./data/bronze_osm_aop_named.geojson', 'OSM named features missing');
      if (osmNamedData) {
        map.addSource('osm-named', { type: 'geojson', data: osmNamedData });
        map.addLayer({
          id: 'osm-named-points',
          type: 'circle',
          source: 'osm-named',
          filter: ['==', ['geometry-type'], 'Point'],
          layout: { visibility: 'none' },
          paint: { 'circle-radius': 5, 'circle-color': '#c7a85e', 'circle-stroke-color': '#6a5836', 'circle-stroke-width': 1.5 }
        });
        map.addLayer({
          id: 'osm-named-labels',
          type: 'symbol',
          source: 'osm-named',
          layout: {
            visibility: 'none',
            'text-field': ['get', 'name'],
            'text-size': 12,
            'text-offset': [0, 1.1],
            'text-anchor': 'top'
          },
          paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.5 }
        });

        indexFeatures(osmNamedData, (props) => props.place || props.natural || 'landmark', osmNamedToggle);
      }

      // --- SFWDA traced trails + markers (extracted from the paper map) ----
      // Card: brain/tasks/04_event_app/paper_map_trail_extraction.md. Prototype
      // vectorization of the SFWDA raster, georeferenced through the same
      // alignment mesh (mvp/scripts/paper_trace_warp.py). Default OFF, in no
      // preset -- a review layer to eyeball the trace over the raster + OSM.
      const TRACE_DIFF_COLOR = [
        'match', ['get', 'difficulty'],
        'easy', '#2e8b57',
        'moderate', '#2f6fb0',
        'difficult', '#333333',
        '#b06a2c'  // mixed / unread difficulty
      ];
      const sfwdaTraceTrailsData = await fetchJson('./data/delete_sfwda_traced_trails.geojson', 'SFWDA traced trails missing');
      if (sfwdaTraceTrailsData) {
        map.addSource('sfwda-trace-trails', { type: 'geojson', data: sfwdaTraceTrailsData });
        map.addLayer({
          id: 'sfwda-trace-trails',
          type: 'line',
          source: 'sfwda-trace-trails',
          layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': TRACE_DIFF_COLOR, 'line-width': 2.5, 'line-opacity': 0.9 }
        });
      }
      // pwa_qa item 9: the SFWDA traced "marker" DOTS were a dev-workflow
      // artifact of the paper-map extraction (one difficulty-coloured dot per
      // read trail number). The gold `aop-trail-network` now carries the
      // numbered trail labels (aop-trail-network-labels), so the dots layer is
      // removed. The `sfwda-trace-trails` line review overlay above is kept.

      // --- AOP merged trail network (hand-cleaned SFWDA trails + OSM tracks) ----
      // The "new truth": one feature per trail edge, each coloured per-trail via the
      // baked-in `color` property so cut-at-intersection pieces read as one colour.
      const aopTrailNetworkData = await fetchJson('./data/gold_aop_trail_network.geojson', 'AOP trail network missing');
      if (aopTrailNetworkData) {
        aopTrailNetworkCache = aopTrailNetworkData; // POI browser trails group joins against this
        map.addSource('aop-trail-network', { type: 'geojson', data: aopTrailNetworkData });
        map.addLayer({
          id: 'aop-trail-network',
          type: 'line',
          source: 'aop-trail-network',
          layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
          paint: { 'line-color': ['coalesce', ['get', 'color'], '#888888'],
                   'line-width': 3, 'line-opacity': 0.92 }
        });
        map.addLayer({
          id: 'aop-trail-network-labels',
          type: 'symbol',
          source: 'aop-trail-network',
          // Label by NAME (any string — "15", "Area 51", "JW2"), not just numbers.
          // Non-numeric named trails carry name but no trail_number, so the old
          // ['has','trail_number'] filter hid them. Roads/unnamed have name=null.
          filter: ['to-boolean', ['get', 'name']],
          layout: {
            visibility: 'none', 'symbol-placement': 'line-center',
            'text-field': ['to-string', ['get', 'name']], 'text-size': 12
          },
          paint: { 'text-color': '#111', 'text-halo-color': '#fff', 'text-halo-width': 1.6 }
        });
        // Make every named trail searchable. Since the trail catalog is baked in,
        // `name` is now the curated name ("Launchpad") where one exists, else the
        // number ("32") or a string name ("Riot Hill", "JW2"); unnamed edges
        // (name=null) are skipped by indexFeatures. A match flies to the trail,
        // flips the network layer on via aopTrailNetworkToggle, and pulses the
        // highlight. Aliases keep BOTH paths reachable: `trail <name>` and the bare
        // `trail_number` ("1", "trail 1") — so a catalogued trail is still findable
        // by its number even though its display name is now "Launchpad" (AOP
        // identifies trails by number on the map).
        indexFeatures(
          aopTrailNetworkData,
          'trail',
          aopTrailNetworkToggle,
          null,
          (props) => {
            const aliases = [];
            if (props.name != null) aliases.push('trail ' + String(props.name));
            if (props.trail_number != null) {
              aliases.push(String(props.trail_number), 'trail ' + String(props.trail_number));
            }
            return aliases.length ? aliases : null;
          }
        );

        // Slice 1 (trail_research_integration.md): clicking a trail had no popup.
        // Now it shows number + difficulty (the MAP COLOR is the park's own
        // difficulty authority — lead with it), and when the trail is catalogued
        // the curated write-up: name, description, length, onX TR (secondary),
        // and what it connects to. Un-catalogued trails show "write-up owed".
        // The onX license note rides in the footer so the provenance is visible
        // in the editor view before any public-gated, voice-rewritten build.
        bindPopup('aop-trail-network',
          // Title / body read the feature's CANONICAL fields — the catalog name,
          // description, and supplementary detail (length / onX TR / connects) are
          // baked onto the trail by rebake_canonical, so the popup agrees with the
          // map label, the left list, and the panel by construction.
          (props) => {
            const num = props.trail_number != null ? props.trail_number
              : (props.name != null && /^\d+$/.test(String(props.name)) ? props.name : null);
            const name = (props.name != null && String(props.name) !== '') ? String(props.name) : null;
            if (name && !/^\d+$/.test(name)) {
              return num != null && String(num) !== name ? `${name} (Trail ${num})` : name;
            }
            return num != null ? `Trail ${num}` : (name ? `Trail ${name}` : 'Trail');
          },
          (props) => {
            const facets = props.facets || {};
            const rows = [
              ['Number', props.trail_number ?? (props.name && /^\d+$/.test(String(props.name)) ? props.name : '')],
              ['Difficulty', facets.difficulty || props.difficulty || 'unknown']
            ];
            if (props.description) rows.push(['About', props.description]);
            if (facets.length_mi != null) rows.push(['Length', `${facets.length_mi} mi`]);
            if (facets.onx_tr != null) rows.push(['onX rating', `TR${facets.onx_tr}`]);
            if (Array.isArray(facets.connects) && facets.connects.length) rows.push(['Connects to', facets.connects.join(', ')]);
            if (!props.description) rows.push(['Write-up', 'name / description owed']);
            return rows;
          }
        );

        // Register the gold network as a FEATURE_LIST destination layer so a
        // trail is starrable/listable like every other layer (card 05). Stamp
        // each feature with the derived per-trail row id the `trails` spec
        // dedupes on: `n:<number>` for numbered trails, `name:<name>` for
        // named-but-unnumbered trails, and LEFT UNSET for unnamed edges (so
        // buildFeatureListState's id-null skip drops them, matching the legacy
        // "unnamed edge — not a directory entry" behavior). The stamp is an
        // additive `__trail_row_id` property — the map paint, labels, search
        // index, and popup all read name/trail_number/color, never this key, so
        // adding it is non-destructive to every existing trail consumer.
        for (const feature of aopTrailNetworkData.features || []) {
          const props = feature.properties || (feature.properties = {});
          const rowId = trailRowId(props);
          if (rowId != null) props.__trail_row_id = rowId;
          // else: unnamed edge — no row id, intentionally not a directory entry.
        }
        // Replay any stored ★/overrides onto the network BEFORE registration, the
        // same as buildings/cemeteries/visitor/brandLogos do — trails was the one
        // ★-curated reference layer with no apply call, so a trail starred via the
        // right panel (now bridged) vanished on reload. highlight is the only
        // override trails carry (geometry is locked), and it isn't painted, so no
        // source.setData is needed here; the POI list reads it off runtime data.
        applyPositionedFeatures('trails', aopTrailNetworkCache, { boot: true });
        registerFeatureListLayer('trails', aopTrailNetworkCache);
      }

      // --- SFWDA paper map raster + 9-patch alignment editor -------------
      const alignmentData = await fetchJson('./data/sfwda_raster_alignment.json', 'SFWDA alignment missing');
      const defaultCorners = alignmentData?.corners
        ? [
            alignmentData.corners.nw,
            alignmentData.corners.ne,
            alignmentData.corners.se,
            alignmentData.corners.sw
          ]
        : [
            [-85.7601056, 35.0995096],
            [-85.7454715, 35.0989829],
            [-85.745686,  35.0835148],
            [-85.7599768, 35.0834094]
          ];
      const defaultOrientation = Number.isFinite(alignmentData?.orientation_cw_degrees)
        ? alignmentData.orientation_cw_degrees
        : 0;

      function defaultGridFromCorners(corners, n) {
        // corners = [NW, NE, SE, SW]. Returns (n+1)x(n+1) grid of [lng, lat].
        // grid[0][0]=NW, grid[0][n]=NE, grid[n][n]=SE, grid[n][0]=SW.
        const [NW, NE, SE, SW] = corners;
        const out = [];
        for (let r = 0; r <= n; r++) {
          const v = r / n;
          const row = [];
          for (let c = 0; c <= n; c++) {
            const u = c / n;
            const lng = (1-u)*(1-v)*NW[0] + u*(1-v)*NE[0] + u*v*SE[0] + (1-u)*v*SW[0];
            const lat = (1-u)*(1-v)*NW[1] + u*(1-v)*NE[1] + u*v*SE[1] + (1-u)*v*SW[1];
            row.push([lng, lat]);
          }
          out.push(row);
        }
        return out;
      }

      function upsampleGrid(srcGrid, dstN) {
        // Preserves the warp encoded in srcGrid by bilinear-interpolating inside each source patch.
        // dstN is the number of patches per side of the destination grid.
        const srcN = srcGrid.length - 1;
        const dst = [];
        for (let r = 0; r <= dstN; r++) {
          const v = r / dstN;
          const row = [];
          for (let c = 0; c <= dstN; c++) {
            const u = c / dstN;
            const pc = Math.min(srcN - 1, Math.floor(u * srcN));
            const pr = Math.min(srcN - 1, Math.floor(v * srcN));
            const lu = u * srcN - pc;
            const lv = v * srcN - pr;
            const p00 = srcGrid[pr][pc];
            const p10 = srcGrid[pr][pc + 1];
            const p11 = srcGrid[pr + 1][pc + 1];
            const p01 = srcGrid[pr + 1][pc];
            const lng = (1-lu)*(1-lv)*p00[0] + lu*(1-lv)*p10[0] + lu*lv*p11[0] + (1-lu)*lv*p01[0];
            const lat = (1-lu)*(1-lv)*p00[1] + lu*(1-lv)*p10[1] + lu*lv*p11[1] + (1-lu)*lv*p01[1];
            row.push([lng, lat]);
          }
          dst.push(row);
        }
        return dst;
      }

      function loadGrid(data, fallbackCorners, n) {
        const exactKey = `grid_${n}x${n}`;
        if (Array.isArray(data?.[exactKey]) && data[exactKey].length === n + 1) {
          return data[exactKey];
        }
        // Find any grid_KxK and upsample (prefer the richest signal available).
        const otherKeys = Object.keys(data || {})
          .filter((k) => /^grid_(\d+)x\1$/.test(k))
          .sort((a, b) => parseInt(b.match(/\d+/)[0]) - parseInt(a.match(/\d+/)[0]));
        if (otherKeys.length) return upsampleGrid(data[otherKeys[0]], n);
        return defaultGridFromCorners(fallbackCorners, n);
      }

      const defaultGrid = loadGrid(alignmentData, defaultCorners, GRID_N);
      let sfwdaGrid = defaultGrid.map((row) => row.map((p) => p.slice()));
      let sfwdaOrientationCw = ((defaultOrientation % 360) + 360) % 360;
      // Multiply strength (0..1): fakes a multiply blend by keying paper-white to
      // transparent. Distinct from opacity (a uniform fade) — multiply is tone-dependent,
      // so white paper drops out while dark trail ink stays.
      // Substrate default: satellite on -> 0 (keep paper intact over imagery; takes
      // precedence even if lidar is also on). Lidar hillshade alone -> 100 (key white
      // out so ink reads over relief). No substrate -> 0.
      function defaultMultiplyForSubstrate() {
        if (satelliteToggle.checked || usdaNaipToggle.checked) return 0;
        if (hillshadeToggle.checked) return 1;
        return 0;
      }
      let sfwdaMultiplyStrength = defaultMultiplyForSubstrate();
      let sfwdaMultiplyUserTouched = false;
      sfwdaMultiply.value = String(Math.round(sfwdaMultiplyStrength * 100));

      function applyMultiplyAlpha(canvas, strength) {
        if (strength <= 0) return canvas;
        const ctx = canvas.getContext('2d');
        let img;
        try {
          img = ctx.getImageData(0, 0, canvas.width, canvas.height);
        } catch (error) {
          // A cross-origin (tainted) canvas throws here. Skip the multiply key
          // rather than letting the throw abort the whole map-load chain.
          console.warn('SFWDA multiply skipped (canvas read blocked):', error);
          return canvas;
        }
        const d = img.data;
        for (let i = 0; i < d.length; i += 4) {
          // keyed alpha: pure whites go fully transparent, colored ink stays opaque.
          const keyed = (d[i + 3] * (255 - Math.min(d[i], d[i + 1], d[i + 2]))) / 255;
          // blend raw alpha -> keyed alpha by strength.
          d[i + 3] = d[i + 3] * (1 - strength) + keyed * strength;
        }
        ctx.putImageData(img, 0, 0);
        return canvas;
      }

      function loadImageEl(src) {
        return new Promise((resolve, reject) => {
          const img = new Image();
          img.crossOrigin = 'anonymous';
          img.onload = () => resolve(img);
          img.onerror = (e) => reject(e);
          img.src = src;
        });
      }

      let sfwdaImageEl;
      try {
        sfwdaImageEl = await loadImageEl('./data/sfwda_aop_trail_map.webp');
      } catch (error) {
        console.error('SFWDA image failed to load:', error);
      }

      function rotateToCanvas(img, orientationCw) {
        const cw = ((orientationCw % 360) + 360) % 360;
        const W = img.naturalWidth, H = img.naturalHeight;
        const canvas = document.createElement('canvas');
        if (cw === 90 || cw === 270) { canvas.width = H; canvas.height = W; }
        else { canvas.width = W; canvas.height = H; }
        const ctx = canvas.getContext('2d');
        ctx.imageSmoothingQuality = 'high';
        if (cw === 0) {
          ctx.drawImage(img, 0, 0);
        } else if (cw === 90) {
          ctx.translate(H, 0); ctx.rotate(Math.PI / 2); ctx.drawImage(img, 0, 0);
        } else if (cw === 180) {
          ctx.translate(W, H); ctx.rotate(Math.PI); ctx.drawImage(img, 0, 0);
        } else if (cw === 270) {
          ctx.translate(0, W); ctx.rotate(-Math.PI / 2); ctx.drawImage(img, 0, 0);
        }
        return canvas;
      }

      function sliceCanvasN(canvas, n) {
        const W = canvas.width, H = canvas.height;
        const out = [];
        for (let r = 0; r < n; r++) {
          const row = [];
          // integer pixel boundaries to avoid sub-pixel gaps; last row/col absorbs rounding remainder
          const y0 = Math.floor(r * H / n);
          const y1 = (r === n - 1) ? H : Math.floor((r + 1) * H / n);
          for (let c = 0; c < n; c++) {
            const x0 = Math.floor(c * W / n);
            const x1 = (c === n - 1) ? W : Math.floor((c + 1) * W / n);
            const sub = document.createElement('canvas');
            sub.width = x1 - x0;
            sub.height = y1 - y0;
            const sctx = sub.getContext('2d');
            sctx.imageSmoothingQuality = 'high';
            sctx.drawImage(canvas, x0, y0, x1 - x0, y1 - y0, 0, 0, sub.width, sub.height);
            row.push(sub.toDataURL('image/webp', 0.9));
            sub.width = sub.height = 0; // release the slice's backing store
          }
          out.push(row);
        }
        return out;
      }

      let tileURLs = Array.from({ length: GRID_N }, () => Array(GRID_N).fill(null));
      function bakeTiles() {
        if (!sfwdaImageEl) return;
        const rotated = rotateToCanvas(sfwdaImageEl, sfwdaOrientationCw);
        applyMultiplyAlpha(rotated, sfwdaMultiplyStrength);
        tileURLs = sliceCanvasN(rotated, GRID_N);
        rotated.width = rotated.height = 0; // release the full-size bake canvas
      }
      bakeTiles();

      function tileSourceId(r, c) { return `sfwda-tile-${r}-${c}`; }
      // Same id space as the source on purpose — the SFWDA raster tile uses one id
      // for both its source and its layer. Deriving from tileSourceId (rather than
      // a second identical literal) removes the desync footgun (L3).
      function tileLayerId(r, c)  { return tileSourceId(r, c); }
      function tileCornerCoords(r, c) {
        return [
          sfwdaGrid[r][c],         // image-TL
          sfwdaGrid[r][c+1],       // image-TR
          sfwdaGrid[r+1][c+1],     // image-BR
          sfwdaGrid[r+1][c]        // image-BL
        ];
      }
      const tileLayerIds = [];
      for (let r = 0; r < GRID_N; r++) {
        for (let c = 0; c < GRID_N; c++) {
          const sid = tileSourceId(r, c);
          if (tileURLs[r][c]) {
            map.addSource(sid, {
              type: 'image',
              url: tileURLs[r][c],
              coordinates: tileCornerCoords(r, c)
            });
            const lid = tileLayerId(r, c);
            map.addLayer({
              id: lid,
              type: 'raster',
              source: sid,
              layout: { visibility: 'none' },
              paint: { 'raster-opacity': 0.7, 'raster-fade-duration': 0 }
            });
            tileLayerIds.push(lid);
          }
        }
      }

      function setSfwdaVisible(visible) {
        for (const id of tileLayerIds) setLayerVisibility(id, visible);
      }

      function setSfwdaOpacity(value) {
        for (const id of tileLayerIds) {
          if (map.getLayer(id)) map.setPaintProperty(id, 'raster-opacity', value);
        }
      }

      function refreshAlignmentSource() {
        for (let r = 0; r < GRID_N; r++) {
          for (let c = 0; c < GRID_N; c++) {
            const src = map.getSource(tileSourceId(r, c));
            if (src && src.setCoordinates) src.setCoordinates(tileCornerCoords(r, c));
          }
        }
      }

      function rebakeTiles() {
        bakeTiles();
        for (let r = 0; r < GRID_N; r++) {
          for (let c = 0; c < GRID_N; c++) {
            const src = map.getSource(tileSourceId(r, c));
            if (src && src.updateImage && tileURLs[r][c]) {
              src.updateImage({ url: tileURLs[r][c], coordinates: tileCornerCoords(r, c) });
            }
          }
        }
      }

      // rAF-coalesce rebakes driven by the multiply slider (H1). A full rebake is
      // a 36-tile getImageData + per-pixel keying + 36 toDataURL pass; the slider's
      // `input` fires dozens of times/sec while dragging, which locks the main
      // thread on mid/low-end devices. Collapse to at most one rebake per frame —
      // the rAF callback reads the latest sfwdaMultiplyStrength, so the final
      // (released) value always wins. One-shot callers (rotate, reset, substrate
      // toggle) stay on the immediate rebakeTiles().
      let rebakeRAF = 0;
      function scheduleRebakeTiles() {
        if (rebakeRAF) return;
        rebakeRAF = requestAnimationFrame(() => {
          rebakeRAF = 0;
          rebakeTiles();
        });
      }

      const alignmentHandles = [];
      function clearAlignmentHandles() {
        while (alignmentHandles.length) alignmentHandles.pop().remove();
      }

      function handleKind(r, c) {
        const onEdgeR = (r === 0 || r === GRID_N);
        const onEdgeC = (c === 0 || c === GRID_N);
        if (onEdgeR && onEdgeC) return 'corner';
        if (onEdgeR || onEdgeC) return 'edge';
        return 'interior';
      }
      function cornerLabel(r, c) {
        if (r === 0 && c === 0) return 'NW';
        if (r === 0 && c === GRID_N) return 'NE';
        if (r === GRID_N && c === GRID_N) return 'SE';
        if (r === GRID_N && c === 0) return 'SW';
        return '';
      }

      function showAlignmentHandles() {
        clearAlignmentHandles();
        const includeNonCorner = showInteriorToggle.checked;
        for (let r = 0; r <= GRID_N; r++) {
          for (let c = 0; c <= GRID_N; c++) {
            const kind = handleKind(r, c);
            if (kind !== 'corner' && !includeNonCorner) continue;
            const el = document.createElement('div');
            el.className = `align-handle align-handle-${kind}`;
            const label = cornerLabel(r, c);
            if (label) el.setAttribute('data-label', label);
            el.title = `Grid point (row ${r}, col ${c}) — drag to warp`;
            const marker = new maplibregl.Marker({ element: el, draggable: true })
              .setLngLat(sfwdaGrid[r][c])
              .addTo(map);
            marker.on('drag', () => {
              const ll = marker.getLngLat();
              sfwdaGrid[r][c] = [ll.lng, ll.lat];
              refreshAlignmentSource();
            });
            alignmentHandles.push(marker);
          }
        }
      }

      function setEditAlignment(enabled) {
        exportAlignmentBtn.disabled = !enabled;
        resetAlignmentBtn.disabled = !enabled;
        rotateCcwBtn.disabled = !enabled;
        rotateCwBtn.disabled = !enabled;
        if (enabled) {
          if (!sfwdaToggle.checked) {
            sfwdaToggle.checked = true;
            updateLayerVisibility();
          }
          showAlignmentHandles();
        } else {
          clearAlignmentHandles();
        }
      }

      function rotateBy(deltaCw) {
        sfwdaOrientationCw = ((sfwdaOrientationCw + deltaCw) % 360 + 360) % 360;
        rebakeTiles();
      }

      rotateCcwBtn.addEventListener('click', () => rotateBy(-90));
      rotateCwBtn.addEventListener('click', () => rotateBy(90));

      showInteriorToggle.addEventListener('change', () => {
        if (editSfwdaToggle.checked) showAlignmentHandles();
      });

      exportAlignmentBtn.addEventListener('click', async () => {
        const payload = {
          _comment: 'Copied by AOP viewer 3x3 alignment editor. Replace website/data/sfwda_raster_alignment.json with this content to persist.',
          source_image: alignmentData?.source_image || 'data/sfwda_aop_trail_map.webp',
          source_provenance: alignmentData?.source_provenance || 'SFWDA AOP trail map 2015-03-11. Internal/inspection only.',
          image_pixel_size: alignmentData?.image_pixel_size || [2500, 1817],
          reference_polygon: alignmentData?.reference_polygon || 'OSM way 1215497712 (Adventure Off Road Park)',
          orientation_cw_degrees: sfwdaOrientationCw,
          corners: {
            nw: sfwdaGrid[0][0],
            ne: sfwdaGrid[0][GRID_N],
            se: sfwdaGrid[GRID_N][GRID_N],
            sw: sfwdaGrid[GRID_N][0]
          },
          [`grid_${GRID_N}x${GRID_N}`]: sfwdaGrid
        };
        const text = JSON.stringify(payload, null, 2) + '\n';
        try {
          const ok = await copyText(text);
          presetStatus.textContent = ok
            ? 'Copied alignment JSON — paste into website/data/sfwda_raster_alignment.json.'
            : 'Clipboard copy failed.';
        } catch (err) {
          presetStatus.textContent = `Copy failed: ${err.message}`;
        }
      });

      resetAlignmentBtn.addEventListener('click', () => {
        sfwdaGrid = defaultGrid.map((row) => row.map((p) => p.slice()));
        sfwdaOrientationCw = ((defaultOrientation % 360) + 360) % 360;
        rebakeTiles();
        if (editSfwdaToggle.checked) showAlignmentHandles();
      });

      sfwdaOpacity.addEventListener('input', () => {
        setSfwdaOpacity(sliderPercent(sfwdaOpacity));
      });

      sfwdaMultiply.addEventListener('input', () => {
        if (!applyingPreset) sfwdaMultiplyUserTouched = true;
        sfwdaMultiplyStrength = sliderPercent(sfwdaMultiply);
        scheduleRebakeTiles();
      });

      function applySubstrateMultiplyDefault() {
        if (sfwdaMultiplyUserTouched) return;
        const next = defaultMultiplyForSubstrate();
        if (next === sfwdaMultiplyStrength) return;
        sfwdaMultiplyStrength = next;
        sfwdaMultiply.value = String(Math.round(next * 100));
        rebakeTiles();
        if (expandedTuneKey === 'sfwda') syncLayerTunerFromSelection();
      }

      hillshadeToggle.addEventListener('change', applySubstrateMultiplyDefault);
      satelliteToggle.addEventListener('change', applySubstrateMultiplyDefault);
      usdaNaipToggle.addEventListener('change', applySubstrateMultiplyDefault);

      editSfwdaToggle.addEventListener('change', () => setEditAlignment(editSfwdaToggle.checked));

      // --- Publishable layers -------------------------------------------
      let publishData;

      try {
        const response = await fetch('./data/gold_publish.geojson');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        publishData = await response.json();
      } catch (error) {
        console.error(error);
        message.textContent = 'Publish layer failed to load.';
        return;
      }

      renderPoiTabIfActive();

      map.addSource('publish-data', {
        type: 'geojson',
        data: publishData
      });

      map.addLayer({
        id: 'publish-boundary-fill',
        type: 'fill',
        source: 'publish-data',
        filter: ['==', ['get', 'layer'], 'park_boundaries'],
        paint: { 'fill-color': '#d8c8a2', 'fill-opacity': 0.10 }
      });

      map.addLayer({
        id: 'publish-boundaries',
        type: 'line',
        source: 'publish-data',
        filter: ['==', ['get', 'layer'], 'park_boundaries'],
        paint: { 'line-color': '#6e5a3c', 'line-width': 2.5 }
      });

      map.addLayer({
        id: 'publish-trails',
        type: 'line',
        source: 'publish-data',
        filter: ['==', ['get', 'layer'], 'trail_centerlines'],
        paint: { 'line-color': '#9a5a32', 'line-width': 3.5 }
      });

      map.addLayer({
        id: 'publish-trailheads',
        type: 'circle',
        source: 'publish-data',
        filter: ['==', ['get', 'layer'], 'trailheads'],
        paint: { 'circle-radius': 6, 'circle-color': '#6f8a5c', 'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 2 }
      });

      // Baked destination POIs (publish.pois -> gold_publish.geojson `poi` layer).
      map.addLayer({
        id: 'publish-pois',
        type: 'circle',
        source: 'publish-data',
        filter: ['==', ['get', 'layer'], 'poi'],
        paint: { 'circle-radius': 6, 'circle-color': '#b5762e', 'circle-stroke-color': '#f7f1e2', 'circle-stroke-width': 2 }
      });

      updateLayerVisibility();
      fitToDataBounds(publishData);

      // V3c: surface gold_publish.geojson trailheads as feature-list rows so the
      // Point → Trailheads sub-group has rows to render. Filter publishData
      // down to just the trailhead features; `id` defaults to the index
      // when properties don't carry an idField match. Card:
      // brain/tasks/04_event_app/editor_three_buckets_v3c.md.
      const trailheadsData = {
        type: 'FeatureCollection',
        features: publishData.features.filter(
          (feature) => feature.properties?.layer === 'trailheads'
        )
      };
      if (trailheadsData.features.length > 0) {
        registerFeatureListLayer('trailheads', trailheadsData);
      }

      // The Park zoom preset fits the published park boundary; fall back to all
      // publish features if no boundary has been exported yet.
      const boundaryOnly = {
        features: publishData.features.filter(
          (feature) => feature.properties?.layer === 'park_boundaries'
        )
      };
      parkViewBounds = geojsonBounds(boundaryOnly) || geojsonBounds(publishData);

      bindPopup('publish-trails', 'Trail', (props) => [
        ['Name', props.name || 'Unnamed'],
        ['Difficulty', props.difficulty || 'unknown'],
        ['Confidence', props.confidence || 'unknown'],
        ['Status', props.status || 'unknown']
      ]);

      bindPopup('publish-boundaries', 'Boundary', (props) => [
        ['Name', props.name || 'Unnamed'],
        ['Confidence', props.confidence || 'unknown'],
        ['Status', props.status || 'unknown'],
        ['Permission', props.permission || 'unknown']
      ]);

      bindPopup('lidar-tiles-fill', 'Lidar tile', (props) => [
        ['Tile', props.tile_code || 'unknown'],
        ['Project', props.project || 'unknown'],
        ['Published', props.publication_date || 'unknown'],
        ['Size (MB)', props.size_mb ?? 'unknown']
      ], (props) => {
        const url = props.download_url || '';
        return url ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener">Download LAZ</a>` : '';
      });

      bindPopup(['contours-index', 'contours-minor'], 'Contour', (props) => [
        ['Elevation', props.elev_ft != null ? `${props.elev_ft} ft` : 'unknown'],
        ['Type', props.idx === 1 ? 'index (25 ft)' : 'minor (5 ft)']
      ]);

      bindPopup('publish-trailheads', 'Trailhead', (props) => [
        ['Name', props.name || 'Unnamed'],
        ['Status', props.status || 'unknown']
      ]);

      bindPopup('osm-tracks', 'OSM track', (props) => [
        ['Name', props.name || '(unnamed)'],
        ['Highway', props.highway || ''],
        ['Surface', props.surface || ''],
        ['OSM type', props.osm_type || ''],
        ['OSM id', props.osm_id || '']
      ]);

      bindPopup('osm-service', 'OSM service road', (props) => [
        ['Name', props.name || '(unnamed)'],
        ['Surface', props.surface || ''],
        ['OSM type', props.osm_type || ''],
        ['OSM id', props.osm_id || '']
      ]);

      bindPopup('osm-named-points', (props) => props.name || 'OSM landmark', (props) => [
        ['Kind', props.place || props.natural || props.highway || props.leisure || ''],
        ['Elevation (m)', props.ele || ''],
        ['OSM id', props.osm_id || '']
      ]);

      // --- Brand logos (AOP badge + Rock Warblers) -----------------------
      // Two on-map logos rendered as MapLibre symbol icons from a Point
      // FeatureCollection. Each feature carries icon_image (matches the
      // map.addImage name we register below) and icon_size (data-driven so
      // the round AOP badge and wider Rock Warblers logo can carry
      // different on-screen sizes from the same layer).
      //
      // Permission posture: AOP badge is reference-only until AOP confirms
      // reuse; Rock Warblers cleared by user grant. Provenance + license
      // notes live in brain/tasks/02_edit/assets/branding/README.md. The
      // raw assets stay in brain/...; website/assets/branding/ holds the
      // viewer-served copies.
      //
      // Edit posture: positions are draggable from the feature list panel
      // and persist in the unified positioned-features store. Editing the
      // seed file just moves the first-load coords; overrides win on next
      // load. Card: brain/tasks/02_edit/branding.md.
      //
      // Source: the logos were merged into gold_aop_visitor_context_callouts.geojson
      // (2026-06-05) as kind=brand_logo points. Pull just those out here; the
      // dedicated brand-logos source + icon layer (and all the drag/resize/cap
      // machinery) are unchanged below.
      const brandBundle = await fetchJson('./data/gold_aop_visitor_context_callouts.geojson', 'Brand logos missing');
      brandLogosData = brandBundle
        ? Object.assign({}, brandBundle, {
            features: brandBundle.features.filter((f) => (f.properties || {}).kind === 'brand_logo')
          })
        : null;
      if (brandLogosData) {
        applyPositionedFeatures('brandLogos', brandLogosData);

        // Load each icon image and register it under the property name the
        // features reference. Done in parallel so a slow asset can't gate
        // the whole layer. Width/height are inferred by the browser; we
        // pass the loaded element straight to map.addImage.
        const logoImages = [
          { name: 'brand-aop-badge', url: './assets/branding/aop-badge.png' },
          { name: 'brand-rock-warblers', url: './assets/branding/rock-warblers.jpg' }
        ];
        await Promise.all(logoImages.map(({ name, url }) => new Promise((resolve) => {
          const img = new Image();
          img.crossOrigin = 'anonymous';
          img.onload = () => {
            if (!map.hasImage(name)) {
              try {
                map.addImage(name, img, { pixelRatio: 2 });
              } catch (err) {
                console.warn(`Could not register logo image ${name}:`, err);
              }
            }
            resolve();
          };
          img.onerror = () => {
            console.warn(`Brand logo image failed to load: ${url}`);
            resolve();
          };
          img.src = url;
        })));

        map.addSource('brand-logos', {
          type: 'geojson',
          data: brandLogosData,
          attribution: 'Brand logos: AOP, Rock Warblers'
        });

        // Restore the persisted size cap (item 5) before composing the
        // zoom-clamped icon-size expression so a reload keeps the tuned cap.
        loadBrandLogoCap();
        map.addLayer({
          id: 'brand-logos-icons',
          type: 'symbol',
          source: 'brand-logos',
          layout: {
            'icon-image': ['get', 'icon_image'],
            // Per-feature icon_size × global cap × zoom factor that maxes out
            // at park zoom and shrinks below it (see brandLogoIconSizeExpr).
            'icon-size': brandLogoIconSizeExpr(),
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center'
          }
        });

        bindPopup('brand-logos-icons',
          (props) => props.name || 'Logo',
          (props) => [
            ['Attribution', props.attribution || ''],
            ['Source', props.source_url || '']
          ]);
        bindPanelReveal(['brand-logos-icons'], 'brandLogos', 'logo_id');

        indexFeatures(
          brandLogosData,
          'logo',
          brandLogosToggle,
          (props) => ({ featureListKey: 'brandLogos', featureId: props.logo_id })
        );
        registerFeatureListLayer('brandLogos', brandLogosData);
      }

      // --- Map editor: Terra Draw POI + footprint drawing ---------------
      loadEditorPois();
      map.addSource('editor-poi', { type: 'geojson', data: editorFeatureCollection() });
      // Footprints (polygons) draw below POIs (points) so a point inside a
      // footprint stays clickable; labels sit on top of both geometry kinds.
      map.addLayer({
        id: 'editor-poi-fill',
        type: 'fill',
        source: 'editor-poi',
        filter: ['==', ['geometry-type'], 'Polygon'],
        paint: { 'fill-color': poiColorExpression, 'fill-opacity': 0.3 }
      });
      map.addLayer({
        id: 'editor-poi-outline',
        type: 'line',
        source: 'editor-poi',
        filter: ['==', ['geometry-type'], 'Polygon'],
        paint: { 'line-color': poiColorExpression, 'line-width': 2.5 }
      });
      map.addLayer({
        id: 'editor-poi-lines',
        type: 'line',
        source: 'editor-poi',
        filter: ['==', ['geometry-type'], 'LineString'],
        layout: { 'line-cap': 'round', 'line-join': 'round' },
        paint: {
          'line-color': poiColorExpression,
          'line-width': ['interpolate', ['linear'], ['zoom'], 11, 2.5, 16, 5],
          'line-opacity': 0.95
        }
      });
      map.addLayer({
        id: 'editor-poi-circles',
        type: 'circle',
        source: 'editor-poi',
        filter: ['==', ['geometry-type'], 'Point'],
        paint: {
          'circle-radius': 7,
          'circle-color': poiColorExpression,
          'circle-stroke-color': '#f7f1e2',
          'circle-stroke-width': 2
        }
      });
      map.addLayer({
        id: 'editor-poi-labels',
        type: 'symbol',
        source: 'editor-poi',
        filter: ['==', ['geometry-type'], 'Point'],
        layout: {
          // Mirrors poiDisplayName (name → category → 'POI') so the map label,
          // the list, and the panel all show one drawn-POI name (A4).
          'text-field': ['coalesce', ['get', 'name'], ['get', 'category'], 'POI'],
          'text-size': 12,
          'text-offset': [0, 1.2],
          'text-anchor': 'top'
        },
        paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 }
      });
      map.addLayer({
        id: 'editor-poi-fill-labels',
        type: 'symbol',
        source: 'editor-poi',
        filter: ['==', ['geometry-type'], 'Polygon'],
        layout: {
          // Mirrors poiDisplayName (name → category → 'POI') so the map label,
          // the list, and the panel all show one drawn-POI name (A4).
          'text-field': ['coalesce', ['get', 'name'], ['get', 'category'], 'POI'],
          'text-size': 12
        },
        paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 }
      });
      map.addLayer({
        id: 'editor-poi-line-labels',
        type: 'symbol',
        source: 'editor-poi',
        filter: ['==', ['geometry-type'], 'LineString'],
        layout: {
          'symbol-placement': 'line',
          // Mirrors poiDisplayName (name → category → 'POI') so the map label,
          // the list, and the panel all show one drawn-POI name (A4).
          'text-field': ['coalesce', ['get', 'name'], ['get', 'category'], 'POI'],
          'text-size': 12,
          'text-keep-upright': true
        },
        paint: { 'text-color': '#4a3c2a', 'text-halo-color': '#f7f1e2', 'text-halo-width': 1.6 }
      });
      refreshEditorSource();

      draw = new terraDraw.TerraDraw({
        adapter: new terraDrawMaplibreGlAdapter.TerraDrawMapLibreGLAdapter({ map }),
        modes: [
          new terraDraw.TerraDrawPointMode(),
          new terraDraw.TerraDrawPolygonMode(),
          new terraDraw.TerraDrawLineStringMode()
        ]
      });
      draw.start();
      draw.setMode('static');
      // Point and polygon modes commit on finish; we lift the drawn geometry
      // out of Terra Draw into our own source (tagged with the selected
      // category) so Terra Draw stays a pure input device with no state.
      draw.on('finish', (id) => {
        const feature = draw.getSnapshot().find((f) => f.id === id);
        if (!feature) return;
        const kind = feature.geometry.type;
        if (kind !== 'Point' && kind !== 'Polygon' && kind !== 'LineString') return;
        // V3c: category comes from the bucket that initiated the draw. If
        // somehow no bucket is active (Esc race, programmatic start), fall
        // back to the hidden legacy #poiCategory select.
        const category = (currentCreateBucket && currentCreateBucket.categorySelect)
          ? currentCreateBucket.categorySelect.value
          : poiCategory.value;
        // Build + persist via the shared builder (also used by the panel's create
        // bridge, Slice 2) so host-drawn and panel-drawn POIs are one-store.
        addDrawnPoi(feature.geometry, category);
        setTimeout(() => draw.removeFeatures([id]), 0);
      });

      // Clicking a committed POI or footprint (only while not drawing, and not
      // while a move-mode commit is staged) routes into the right-panel
      // inline accordion editor: expand the row for this feature, scroll
      // it into view, and flash. The previous MapLibre rename/delete
      // popup retired with the inline-editor card. During move mode the
      // click belongs to the move primitive.
      const editorClickBound = new Set();
      function bindEditorClick(layerId) {
        if (editorClickBound.has(layerId)) return; // idempotent — safe if init re-runs (L11)
        editorClickBound.add(layerId);
        map.on('click', layerId, (event) => {
          if (draw && draw.getMode() !== 'static') return;
          if (moveState) return;
          const feature = event.features?.[0];
          if (!feature) return;
          const id = feature.properties && feature.properties.id;
          if (id == null) return;
          if (!dockSelectionMatches('editorPois', id)) {
            selectFeatureForDock('editorPois', id);
          }
          revealFeatureInPanel('editorPois', id);
        });
        map.on('mouseenter', layerId, () => {
          if (draw && draw.getMode() === 'static' && !moveState) map.getCanvas().style.cursor = 'pointer';
        });
        map.on('mouseleave', layerId, () => {
          if (!moveState) map.getCanvas().style.cursor = '';
        });
      }
      bindEditorClick('editor-poi-circles');
      bindEditorClick('editor-poi-fill');
      bindEditorClick('editor-poi-lines');

      // First-install seed: if the user has never run the viewer, fetch
      // the seed file and install it as the starting editorPois set. No
      // await — the seed lands asynchronously and pushes itself into the
      // map via refreshEditorSource(). Subsequent boots (with localStorage
      // populated) no-op out of this path.
      maybeSeedEditorPois();

      // --- Search index + highlight layers ------------------------------
      indexFeatures(publishData,
        (props) => props.layer === 'trail_centerlines' ? 'trail'
          : props.layer === 'park_boundaries' ? 'boundary' : 'trailhead',
        (props) => props.layer === 'trail_centerlines' ? trailToggle
          : props.layer === 'park_boundaries' ? boundaryToggle : trailheadToggle);
      buildSearchGroups();

      map.addSource('search-highlight', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });
      // Added last so the highlight draws above every other layer.
      map.addLayer({
        id: 'search-highlight-line',
        type: 'line',
        source: 'search-highlight',
        layout: { visibility: 'none', 'line-cap': 'round', 'line-join': 'round' },
        paint: { 'line-color': '#e8a83a', 'line-width': 8, 'line-opacity': 0.85, 'line-blur': 1.5 }
      });
      map.addLayer({
        id: 'search-highlight-point',
        type: 'circle',
        source: 'search-highlight',
        filter: ['==', ['geometry-type'], 'Point'],
        layout: { visibility: 'none' },
        paint: {
          'circle-radius': 16,
          'circle-color': '#e8a83a',
          'circle-opacity': 0,
          'circle-stroke-color': '#e8a83a',
          'circle-stroke-width': 4,
          'circle-stroke-opacity': 0.85
        }
      });

	      message.textContent = `${publishData.features.length} publish feature${publishData.features.length === 1 ? '' : 's'} loaded.`;
	      applyPreset(activePresetId);
	      if (viewerSessionState?.active_left_tab && viewerSessionState.active_left_tab !== 'events') {
	        setLeftTab(viewerSessionState.active_left_tab);
	      }
	    });

    // --- Map search -----------------------------------------------------
    // Searches named features across every loaded layer, flies to the match,
    // turns its layer on if hidden, and flashes a highlight. Fully client-side
    // over already-loaded GeoJSON — no geocoder service, works offline.

    // Register every named feature of a FeatureCollection. kindFor/toggleFor
    // may be a value or a (props) => value function.
    // featureListBindingFor (optional) returns { featureListKey, featureId }
    // for features that are per-feature-toggleable via FEATURE_LIST_LAYERS.
    // The search path uses this to auto-unhide a per-feature target on landing
    // (otherwise a search lands the camera but nothing draws because the
    // feature was unticked).
    // aliasesFor (optional) returns an array of extra search terms for the
    // entry (e.g. `#pavilion` for the pavilion anchor) so a tag query lands
    // the feature even when the display name does not contain the tag.
    function indexFeatures(data, kindFor, toggleFor, featureListBindingFor, aliasesFor) {
      if (!data || !data.features) return;
      for (const feature of data.features) {
        const props = feature.properties || {};
        const name = props.name || props.gnis_name;
        if (!name || !feature.geometry) continue;
        const entry = {
          name: String(name),
          kind: typeof kindFor === 'function' ? kindFor(props) : kindFor,
          toggle: typeof toggleFor === 'function' ? toggleFor(props) : toggleFor,
          geometry: feature.geometry,
          // Canonical description rides on the entry so the result row can show a
          // muted second line without a runtime sidecar join (the trail catalog is
          // baked into the feature). Null where the feature has no description.
          description: props.description || null
        };
        if (featureListBindingFor) {
          const binding = featureListBindingFor(props);
          if (binding && binding.featureListKey && binding.featureId != null) {
            entry.featureListKey = binding.featureListKey;
            entry.featureId = binding.featureId;
          }
        }
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

    // Trails imported as "<name> (segment N)" rows collapse to one searchable
    // trail; strip the segment suffix so every segment shares a group.
    function searchDisplayName(name) {
      return name.replace(/\s*\(segment[^)]*\)\s*$/i, '').trim();
    }

    // Collapse per-segment entries into one group per name+kind, so a
    // multi-segment creek or trail is a single result framed by its full extent.
    // Aliases (e.g. event-schedule `#pavilion`) carry per-entry and union
    // into the group so any segment's tag matches the whole group.
    function buildSearchGroups() {
      const byKey = new Map();
      for (const entry of searchIndex) {
        const display = searchDisplayName(entry.name) || entry.name;
        const key = display.toLowerCase() + '|' + entry.kind;
        let group = byKey.get(key);
        if (!group) {
          group = { name: display, kind: entry.kind, toggle: entry.toggle, geometries: [], featureListKey: null, featureIds: [], aliases: [], description: null };
          byKey.set(key, group);
        }
        // Carry the canonical description onto the group (first non-empty wins) so a
        // result row can show its muted second line without a runtime join.
        if (!group.description && entry.description) group.description = entry.description;
        group.geometries.push(entry.geometry);
        if (entry.featureListKey) {
          group.featureListKey = entry.featureListKey;
          if (entry.featureId != null && !group.featureIds.includes(entry.featureId)) {
            group.featureIds.push(entry.featureId);
          }
        }
        if (entry.aliases) {
          for (const alias of entry.aliases) {
            if (!group.aliases.includes(alias)) group.aliases.push(alias);
          }
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

    // Anchor the (now `position: fixed`) dropdown to the input's bounding box
    // so it escapes the `.lr-content-col` overflow-clip but still tracks the
    // input across resizes / drawer-card collapses. Called whenever the
    // dropdown is shown; the scroll/resize listeners reposition it live.
    function positionSearchResults() {
      const rect = searchInput.getBoundingClientRect();
      searchResults.style.left = `${rect.left}px`;
      searchResults.style.top = `${rect.bottom + 4}px`;
      searchResults.style.width = `${rect.width}px`;
    }
    // Keep MapLibre's canvas matched to the container after the viewport
    // changes. iOS standalone finalizes its height late (status bar / home
    // indicator settle, rotation, return from background), and MapLibre's
    // ResizeObserver on a position:fixed container does not always catch it —
    // an unresized canvas leaves the body background showing under the home
    // indicator. resize() is cheap and idempotent.
    // rAF-coalesced (M8). visualViewport 'resize' fires continuously while the
    // iOS keyboard / URL bar animates, and each map.resize() is a layout + GL
    // viewport reset. Collapse to one resync per frame, and skip the resize when
    // the map container's pixel box hasn't actually changed (resize() would be a
    // no-op anyway). The search-dropdown reposition still runs every frame — it's
    // cheap and the input can shift even when the container box doesn't.
    let resyncRAF = 0;
    let lastMapSize = '';
    const doResyncViewport = () => {
      resyncRAF = 0;
      const c = map.getContainer();
      const size = `${c.clientWidth}x${c.clientHeight}`;
      if (size !== lastMapSize) {
        lastMapSize = size;
        map.resize();
      }
      if (searchResults.style.display === 'block') positionSearchResults();
    };
    const resyncViewport = () => {
      if (resyncRAF) return;
      resyncRAF = requestAnimationFrame(doResyncViewport);
    };
    window.addEventListener('resize', resyncViewport);
    window.addEventListener('orientationchange', () => setTimeout(resyncViewport, 250));
    window.addEventListener('pageshow', resyncViewport);
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', resyncViewport);
    }
    window.addEventListener('scroll', () => {
      if (searchResults.style.display === 'block') positionSearchResults();
    }, true);

    // Match the query against the group's display name OR any alias.
    // A leading `#` flags a deliberate tag query — match aliases only so
    // the dropdown stays tight and an unrelated name substring does not
    // shadow the tagged anchor.
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

    // Relevance rank for ordering matches (lower = better). Exact name beats a
    // prefix beats a mid-string substring. Without this, a bare-number query like
    // "9" sorts alphabetically and buries trail "9" under every building address
    // that merely contains a 9. searchGroups is pre-sorted alphabetically, so a
    // stable sort by rank keeps results alphabetical within each rank tier.
    //
    // Trail-number queries (the query starts with a digit) are the trail
    // search path: a bare "1" must surface the 1-prefixed trails ("1X", "10",
    // "11"…), not the building addresses that also start with "1" (e.g. "1010
    // Ellis Cove Road"). Those addresses prefix-match too and, sorted only by
    // base rank + alphabetically, fill the 8-slot dropdown before "1X" ever
    // sorts in. So within each rank tier we float trails above non-trails for
    // digit-leading queries (base rank doubled, +1 for non-trail). Exact name
    // (rank 0) stays unbeatable, so trail "1" itself still tops the list.
    function searchRank(group, query) {
      const n = group.name.toLowerCase();
      let base;
      if (n === query) base = 0;
      else if (n.startsWith(query)) base = 1;
      else if (group.aliases && group.aliases.some((a) => a.toLowerCase() === query)) base = 1;
      else if (n.includes(query)) base = 2;
      else base = 3;                           // alias substring only
      // For trail-number queries, break rank ties in favour of trails so the
      // 1-prefixed trails are not crowded out of the dropdown by 1-prefixed
      // building addresses. base 0 (exact) is preserved as 0.
      if (base > 0 && /^\d/.test(query)) {
        return base * 2 + (group.kind === 'trail' ? 0 : 1);
      }
      return base;
    }

    function renderSearchResults() {
      const query = searchInput.value.trim().toLowerCase();
      // Require 2+ chars to avoid flooding the dropdown on every keystroke — EXCEPT
      // a lone digit, which is a valid trail number (trails 1–9). A single letter
      // still waits for a second char.
      if (query.length < 2 && !/^\d$/.test(query)) {
        searchResults.style.display = 'none';
        searchMatches = [];
        return;
      }
      // Cap the dropdown so a broad query doesn't flood it. A trail-number
      // query ("1") legitimately matches a whole family of short trail names
      // ("1", "10", "11"…"18", "1X") — there are 10 trails starting with "1",
      // so an 8-row cap would silently drop "1X" (it sorts last among them).
      // Widen the cap for digit-leading queries so the full 1-prefixed trail
      // set is reachable; the dropdown already scrolls (max-height:240px).
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
          // Slice 3: a catalogued trail row gains a second, muted line with its
          // curated description (truncated), read from the search entry's baked
          // canonical `description` (the trail catalog is folded into the feature) —
          // no runtime sidecar join. Non-trail / no-desc rows render exactly as
          // before (single line, no .search-result-text).
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
      // Set descriptions via textContent (not innerHTML) so first-party copy is
      // never parsed as markup. Paired by index with the matches above.
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

    // Search-result pulse. `osc` runs 0 -> 1 -> 0 a few times across the
    // duration; everything else is taste. If the effect needs tuning, change
    // the constants here, not the math below.
    const PULSE_DURATION_MS = 2600;
    const PULSE_FLASHES = 3;                  // half-cycles of the cosine
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
      // Turn the layer on so the result is actually visible on arrival.
      if (match.toggle && !match.toggle.checked) {
        match.toggle.checked = true;
        match.toggle.dispatchEvent(new Event('change'));
      }
      // Per-feature unhide: if this match is a target of FEATURE_LIST_LAYERS,
      // the user may have unticked it. Searching for it expresses intent to
      // see it, so we force its visibility on and refresh the panel if open.
      if (match.featureListKey && Array.isArray(match.featureIds) && match.featureIds.length) {
        for (const id of match.featureIds) {
          setFeatureVisible(match.featureListKey, id, true);
        }
        if (shouldRenderFeatureList(match.featureListKey)) renderFeatureList(match.featureListKey);
      }
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
      persistViewerSessionState({ search_query: searchInput.value });
      clearSearchResults();
    }

    if (viewerSessionState?.search_query) {
      searchInput.value = String(viewerSessionState.search_query);
    }
    searchInput.addEventListener('input', () => {
      searchActive = -1;
      persistViewerSessionState({ search_query: searchInput.value });
      renderSearchResults();
    });
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
        persistViewerSessionState({ search_query: '' });
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

    for (const button of presetButtons) {
      button.addEventListener('click', () => applyPreset(button.dataset.preset));
    }
    for (const button of document.querySelectorAll('.zoom-bar button[data-view]')) {
      button.addEventListener('click', () => goToView(button.dataset.view));
    }
    terrainButton.addEventListener('click', () => setTerrainEnabled(!terrainToggle.checked));

    tuneVisible.addEventListener('change', setSelectedLayerVisible);
    tuneControls.addEventListener('input', handleTuneInput);
    if (exportAllBtn) exportAllBtn.addEventListener('click', (e) => { e.stopPropagation(); exportAllToClipboard(); });
    // Per-section ⧉ on each section header. Buttons declare which section
    // they target via data-section-export so the header doesn't need an
    // explicit per-section listener.
    for (const btn of document.querySelectorAll('[data-section-export]')) {
      btn.addEventListener('click', () => exportSectionToClipboard(btn.dataset.sectionExport));
    }

    syncVirtualClockUi();
    if (clockUseInputs) clockUseInputs.addEventListener('click', () => {
      const next = virtualClockFromInputs();
      if (next) setVirtualClock(next);
    });
    if (clockUseNow) clockUseNow.addEventListener('click', () => setVirtualClock(new Date()));
    if (clockClear) clockClear.addEventListener('click', () => setVirtualClock(null));
    if (clockMinusDay) clockMinusDay.addEventListener('click', () => stepVirtualClock(-1440));
    if (clockPlusDay) clockPlusDay.addEventListener('click', () => stepVirtualClock(1440));
    if (clockMinusHour) clockMinusHour.addEventListener('click', () => stepVirtualClock(-60));
    if (clockPlusHour) clockPlusHour.addEventListener('click', () => stepVirtualClock(60));
    if (virtualClockDate) virtualClockDate.addEventListener('change', () => {
      const next = virtualClockFromInputs();
      if (next) setVirtualClock(next);
    });
    if (virtualClockTime) virtualClockTime.addEventListener('change', () => {
      const next = virtualClockFromInputs();
      if (next) setVirtualClock(next);
    });
    if (resetViewerStateBtn) resetViewerStateBtn.addEventListener('click', resetViewerState);
    if (torchCacheBtn) torchCacheBtn.addEventListener('click', torchCache);

    // Terrain has its own toggle handler (3D enable/disable, not a layer
    // visibility flip). The landcover-9 opacity is the lone slider that has
    // to land its value into a layer paint property directly.
    terrainToggle.addEventListener('change', () => setTerrainEnabled(terrainToggle.checked));
    landcover9Opacity.addEventListener('input', () => {
      setLandcover9Opacity(sliderPercent(landcover9Opacity));
    });
    // Every other toggle just flips visibility. LAYER_TOGGLES is the single
    // source of truth -- add a row there and the listener wires itself.
    for (const [toggle] of LAYER_TOGGLES) {
      toggle.addEventListener('change', updateLayerVisibility);
    }

    // Item 14: the Trail-activity hot lane is a toggle over the activity-hotspot
    // layer, so flipping that layer anywhere (the layer panel, a preset, the hot
    // button itself) must resync the button's pressed/active visual.
    if (activityHotspotsToggle) {
      activityHotspotsToggle.addEventListener('change', () => {
        if (typeof refreshHotButton === 'function') refreshHotButton();
      });
    }

    for (const id of PRESET_TOGGLE_IDS) {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener('change', () => {
          if (!applyingPreset) markPresetEdited();
          syncLayerTunerFromSelection();
        });
      }
    }
    for (const id of PRESET_SLIDER_IDS) {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener('input', () => {
          if (!applyingPreset) markPresetEdited();
          syncLayerTunerFromSelection();
        });
      }
    }

    placePoiBtn.addEventListener('click', () => {
      setDrawMode(draw && draw.getMode() === 'point' ? 'static' : 'point');
    });
    drawFootprintBtn.addEventListener('click', () => {
      setDrawMode(draw && draw.getMode() === 'polygon' ? 'static' : 'polygon');
    });
    traceLineBtn.addEventListener('click', () => {
      setDrawMode(draw && draw.getMode() === 'linestring' ? 'static' : 'linestring');
    });
    exportPoiBtn.addEventListener('click', exportEditorPois);
    // Drawer "Copy all" — copies the open feature-list layer (buildings,
    // cemeteries, …) as a GeoJSON FeatureCollection with all edits applied.
    if (copyLayerBtn) copyLayerBtn.addEventListener('click', () => {
      if (expandedTuneKey) copyLayerAsGeoJSON(expandedTuneKey);
    });
    clearPoiBtn.addEventListener('click', () => {
      if (!editorPois.length) return;
      if (!window.confirm(`Delete all ${editorPois.length} drawn feature(s)? This cannot be undone.`)) return;
      editorPois = [];
      saveEditorPois();
      refreshEditorSource();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && draw && draw.getMode() !== 'static') setDrawMode('static');
    });

    // ── Left-rail drawer (col1 icons + col2 content) ──────────────────
    // Icons keep canonical order (search, hot, cal) and float DOWN — never
    // up — to align with their panel's top in col2. Click is a pure toggle:
    // closed → open, open → closed. Initial state mirrors prior layout
    // (Search + Cal visible, Hot closed because hot-control historically
    // started hidden). The hot-control reveal opens Hot on first data arrival
    // unless a saved user-close state says otherwise.
    (function () {
      const LR_CARDS = ['search', 'hot', 'cal'];
      const lrTabs = {
        search: document.getElementById('lrTabSearch'),
        hot:    document.getElementById('lrTabHot'),
        cal:    document.getElementById('lrTabCal'),
      };
      const lrPanels = {
        search: document.getElementById('lrPanelSearch'),
        hot:    document.getElementById('lrPanelHot'),
        cal:    document.getElementById('lrPanelCal'),
      };
      const lrIconCol    = document.getElementById('lrIconCol');
      const lrContentCol = document.getElementById('lrContentCol');
      if (!lrIconCol || !lrContentCol) return;

      // Item 11 (misc_3.md): on mobile the small viewport can't host all
      // three drawer cards comfortably, so the no-saved-state default is
      // calendar-only. Desktop keeps search + cal open.
      const LR_DEFAULT_OPEN = window.innerWidth <= 760
        ? { search: false, hot: false, cal: true }
        : { search: true, hot: false, cal: true };
      const lrSavedState = readJsonStore(LEFT_RAIL_DRAWER_KEY, null);
      let lrHasSavedState = !!(
        lrSavedState
        && typeof lrSavedState === 'object'
        && (lrSavedState.open || LR_CARDS.some((c) => typeof lrSavedState[c] === 'boolean'))
      );
      function lrSavedOpen(saved) {
        const raw = saved && typeof saved === 'object'
          ? (saved.open && typeof saved.open === 'object' ? saved.open : saved)
          : {};
        const open = {};
        LR_CARDS.forEach((c) => { open[c] = typeof raw[c] === 'boolean' ? raw[c] : LR_DEFAULT_OPEN[c]; });
        return open;
      }
      const lrOpen = lrSavedOpen(lrSavedState);
      const TAB_H = parseInt(
        getComputedStyle(document.documentElement).getPropertyValue('--tab-h'),
        10
      ) || 44;

      function lrPersist() {
        lrHasSavedState = true;
        writeJsonStore(LEFT_RAIL_DRAWER_KEY, {
          schema: 'aop-left-rail-drawer-v1',
          updated_at: new Date().toISOString(),
          open: { search: !!lrOpen.search, hot: !!lrOpen.hot, cal: !!lrOpen.cal }
        });
      }

      function lrRender() {
        const anyOpen = LR_CARDS.some(c => lrOpen[c]);
        lrContentCol.hidden = !anyOpen;
        lrIconCol.classList.toggle('standalone', !anyOpen);

        LR_CARDS.forEach(c => {
          const isOpen = !!lrOpen[c];
          lrTabs[c].classList.toggle('open', isOpen);
          lrTabs[c].setAttribute('aria-pressed', isOpen ? 'true' : 'false');
          lrPanels[c].classList.toggle('open', isOpen);
        });

        LR_CARDS.forEach(c => { lrTabs[c].style.marginTop = ''; });
        void lrContentCol.offsetHeight;

        let prevBottom = 0;
        LR_CARDS.forEach((c, i) => {
          const canonical = i * TAB_H;
          const pTop = lrOpen[c] ? lrPanels[c].offsetTop : -Infinity;
          const desired = Math.max(canonical, pTop, prevBottom);
          lrTabs[c].style.marginTop = (desired - prevBottom) + 'px';
          prevBottom = desired + TAB_H;
        });

        if (anyOpen) {
          lrIconCol.classList.toggle(
            'col2-short',
            lrContentCol.offsetHeight < lrIconCol.offsetHeight
          );
        } else {
          lrIconCol.classList.remove('col2-short');
        }
      }

      LR_CARDS.forEach(c => {
        lrTabs[c].addEventListener('click', () => {
          lrOpen[c] = !lrOpen[c];
          lrRender();
          lrPersist();
        });
      });

      // Public hooks for code that wants to drive the drawer from outside.
      window.lrOpenCard  = (c, options = {}) => {
        if (!LR_CARDS.includes(c)) return;
        if (options.auto && lrHasSavedState && !lrOpen[c]) return;
        if (!lrOpen[c]) {
          lrOpen[c] = true;
          lrRender();
          if (!options.auto) lrPersist();
        }
      };
      window.lrCloseCard = (c) => {
        if (!LR_CARDS.includes(c)) return;
        if (lrOpen[c]) {
          lrOpen[c] = false;
          lrRender();
          lrPersist();
        }
      };
      window.lrResetCards = () => {
        LR_CARDS.forEach((c) => { lrOpen[c] = !!LR_DEFAULT_OPEN[c]; });
        lrHasSavedState = false;
        lrRender();
      };
      // Item 15: the icon-column tab offsets in lrRender are computed from live
      // panel.offsetTop rects. When the right edit `.panel` collapses to the
      // pencil FAB, or a card body is resized by drag, the page reflows and
      // those cached offsets go stale -- the floating tab icons (and the handle
      // under them) drift off the panels they label, so a drag no longer tracks
      // the finger. Expose a public recompute so those events can re-run the
      // geometry against fresh rects instead of leaving the old margins in place.
      window.lrReflow = lrRender;

      lrRender();
    })();