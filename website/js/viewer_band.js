// viewer_band.js — GEOLOCATED off-edge decorative band ("printed neat-line"),
// wired onto the REAL MapLibre map of the clean viewer core.
//
// WHY THIS IS A REWRITE (2026-06-13): the band used to be a screen-space HTML
// overlay — eight axis-aligned <div> tiles repositioned every frame from the
// 9-patch's screen *bounding box*. That works top-down, but in 3D (pitch + the
// terrain toggle) the 9-patch projects to a perspective TRAPEZOID, and an
// axis-aligned rectangle of divs cannot follow it — the frame floats flat over a
// tilted scene instead of sitting on the ground. The user's call: "these are 2d
// map elements that need to be geolocated... once done it will conform to the
// landscape." So the band is now drawn as ACTUAL map layers tied to the region's
// geographic boundary; MapLibre projects them through the same camera as the map
// (bearing, pitch, terrain), so the frame conforms to the landscape automatically.
//
// The band is four geolocated pieces, all pinned to the 9-patch rectangle:
//   1. paper mask  — a donut fill (huge outer ring minus the 9-patch hole) that
//      covers everything OUTSIDE the 9-patch, so data spill is hidden and the
//      visible map is always the clean 9-patch. Drapes on terrain in 3D.
//   2. keyline     — a line along the 9-patch boundary (the neat-line).
//   3. lettering   — each edge label is RENDERED to an image (exact picked
//      typography) and placed as a ground-aligned icon just OUTSIDE its edge, on
//      the paper. Ground-locked icon size (exponential base 2) means each label
//      holds a fixed FRACTION of its edge at every zoom (so it never overflows —
//      what the old per-frame JS font hack was chasing) and it foreshortens with
//      the terrain in 3D. (Icons place unconditionally — MapLibre line-placed text
//      drops out when a full-region edge straddles a vector-tile boundary.)
//   4. corner marks— the Rock Warblers mark stamped at each boundary corner, laid
//      flat on the ground (icon rotation + pitch aligned to the map).
//
// Camera behaviour is unchanged from the rubber-band era: the map's own maxBounds
// is the hard backstop, and on RELEASE after a drag past the edge snapBack() eases
// the 9-patch back into frame. That logic is screen-space (it just pulls the
// camera) and is kept verbatim; only the VISUAL band moved onto the map.
(function () {
  'use strict';

  var SNAP_MS = 520;   // ms — release rubber-band duration.
  var ZREF = 13;       // zoom at which the px sizes below are measured; ground-lock
                       // doubles them per zoom level (exponential base 2).

  var PAPER = '#e3d7bb', INK = '#3a2c1a', TITLE_INK = '#2a1f12', SUB_INK = '#5a4828';

  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

  // Ground-locked size: an interpolate-by-zoom whose two stops are 4 zoom levels
  // apart with a 16× ratio == exactly 2^zoom, so the element holds a fixed ground
  // (map) size — it scales WITH the 9-patch at every zoom and so can never overflow
  // its edge (this is what the old per-frame JS font hack was chasing, now native).
  function scalarSizeExpr(pxAtRef) {
    return ['interpolate', ['exponential', 2], ['zoom'],
      ZREF - 2, pxAtRef / 4, ZREF + 2, pxAtRef * 4];
  }

  function boot(tries) {
    var V = window.AOPViewer;
    if (!V || !V.map) {
      if ((tries || 0) < 150) return setTimeout(function () { boot((tries || 0) + 1); }, 40);
      console.warn('[viewer_band] AOPViewer.map never appeared — core not exposing the map.');
      return;
    }
    var map = V.map;
    var region = V.regionBounds ||
      [[-85.782935283, 35.067164188], [-85.717154097, 35.117928496]];
    var W = region[0][0], S = region[0][1], E = region[1][0], N = region[1][1];
    var dW = E - W, dH = N - S;

    // Text sits this far OUTSIDE the boundary (a fraction of the region), so the
    // lettering prints on the paper margin rather than straddling the neat-line.
    var insetX = dW * 0.060, insetY = dH * 0.060;
    var maskPad = 2.0;   // deg — large enough that the paper covers the whole
                         // visible ground out to the horizon when pitched in 3D.

    // ── geolocated geometry ──────────────────────────────────────────────────
    var ring = [[W, S], [E, S], [E, N], [W, N], [W, S]];

    var maskFeature = { type: 'Feature', properties: {}, geometry: {
      type: 'Polygon', coordinates: [
        [[W - maskPad, S - maskPad], [E + maskPad, S - maskPad],
         [E + maskPad, N + maskPad], [W - maskPad, N + maskPad], [W - maskPad, S - maskPad]],
        ring   // hole = the clean 9-patch
      ] } };

    var keylineFeature = { type: 'Feature', properties: {},
      geometry: { type: 'LineString', coordinates: ring } };

    // Edge → text. The lettering is RENDERED to an image (so the picked typography
    // survives exactly — weight, 0.42em tracking, uppercase, the typographic glyphs
    // ·°′—) and placed as a GROUND-ALIGNED icon at each edge's midpoint, just
    // OUTSIDE the boundary on the paper. Icons place unconditionally and lie flat on
    // the ground (icon-rotation/pitch-alignment: map), so they foreshorten with the
    // terrain in 3D — and, unlike MapLibre line-placed text, they don't drop out
    // when a full-region edge line straddles a vector-tile boundary. `rot` orients
    // each label along its edge in MAP space (bearing-independent), so the lettering
    // tracks the landscape as the map rotates and tilts.
    var midLng = (W + E) / 2, midLat = (S + N) / 2;
    var EDGES = [
      { key: 'n', label: 'Adventure Off Road Park',                              at: [midLng, N + insetY], rot: 0,
        fontPx: 13, weight: 800, color: TITLE_INK, spacing: 0.42 },
      { key: 's', label: 'South Pittsburg · Marion County · Tennessee — MMXXVI', at: [midLng, S - insetY], rot: 0,
        fontPx: 10, weight: 700, color: SUB_INK, spacing: 0.30 },
      { key: 'w', label: '35° 00′ North · Cumberland Plateau',                   at: [W - insetX, midLat], rot: -90,
        fontPx: 10, weight: 700, color: SUB_INK, spacing: 0.30 },
      { key: 'e', label: '85° 36′ West · Trail Blazing Invitational',            at: [E + insetX, midLat], rot: 90,
        fontPx: 10, weight: 700, color: SUB_INK, spacing: 0.30 }
    ];

    // Render each label to a supersampled (DPR=4) ImageData stamp and register it
    // as a map image named 'band-lab-<key>'. Canvas letterSpacing reproduces the
    // band's 0.42em tracking; the system-ui fallback covers it if Inter isn't loaded.
    function buildLabelImages() {
      var DPR = 4;
      for (var i = 0; i < EDGES.length; i++) {
        var e = EDGES[i], name = 'band-lab-' + e.key;
        if (map.hasImage(name)) continue;
        var cv = document.createElement('canvas'), ctx = cv.getContext('2d');
        var font = e.weight + ' ' + (e.fontPx * DPR) + 'px Inter, system-ui, sans-serif';
        var ls = e.spacing * e.fontPx * DPR;
        var txt = e.label.toUpperCase();
        ctx.font = font;
        if ('letterSpacing' in ctx) ctx.letterSpacing = ls + 'px';
        var w = Math.ceil(ctx.measureText(txt).width) + Math.round(ls) + e.fontPx * DPR;
        var h = Math.ceil(e.fontPx * DPR * 1.7);
        cv.width = w; cv.height = h;
        ctx.font = font;                                  // a resize clears the ctx
        if ('letterSpacing' in ctx) ctx.letterSpacing = ls + 'px';
        ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillStyle = e.color;
        ctx.fillText(txt, w / 2, h / 2);
        try { map.addImage(name, ctx.getImageData(0, 0, w, h), { pixelRatio: DPR }); }
        catch (err) { console.warn('[viewer_band] label image failed:', e.key, err); }
      }
    }

    var labelFC = { type: 'FeatureCollection', features: EDGES.map(function (e) {
      return { type: 'Feature',
               properties: { icon: 'band-lab-' + e.key, rot: e.rot },
               geometry: { type: 'Point', coordinates: e.at } };
    }) };

    var cornerFC = { type: 'FeatureCollection',
      features: [[W, S], [E, S], [E, N], [W, N]].map(function (c) {
        return { type: 'Feature', properties: {}, geometry: { type: 'Point', coordinates: c } };
      }) };

    // ── corner mark: rasterise rw-mark.svg into a flat INK silhouette stamp ───
    // (mirrors the CSS mask+background-color trick: draw the art, then source-in
    // fill it with the neat-line ink so it reads as a printed stamp). The SVG is
    // width/height:100%, so it has no intrinsic size — give the <img> an explicit
    // box before it loads so the canvas raster is sharp.
    function loadMark(cb) {
      if (map.hasImage('rw-mark')) return cb();
      var SZ = 128;
      var img = new Image();
      img.width = SZ; img.height = SZ;
      img.crossOrigin = 'anonymous';
      img.onload = function () {
        try {
          var cv = document.createElement('canvas'); cv.width = SZ; cv.height = SZ;
          var ctx = cv.getContext('2d');
          ctx.drawImage(img, 0, 0, SZ, SZ);
          ctx.globalCompositeOperation = 'source-in';
          ctx.fillStyle = INK; ctx.fillRect(0, 0, SZ, SZ);
          if (!map.hasImage('rw-mark')) map.addImage('rw-mark', ctx.getImageData(0, 0, SZ, SZ), { pixelRatio: 2 });
        } catch (err) { console.warn('[viewer_band] rw-mark raster failed:', err); }
        cb();
      };
      img.onerror = function () { console.warn('[viewer_band] rw-mark image failed to load'); cb(); };
      img.src = './assets/branding/rw-mark.svg';
    }

    // ── add the band layers (idempotent), on TOP of the core's layers ────────
    var BAND_LAYERS = ['band-mask', 'band-keyline', 'band-labels', 'band-marks'];
    function addBand() {
      if (map.getSource('band-mask')) { raiseBand(); return; }

      map.addSource('band-mask', { type: 'geojson', data: maskFeature });
      map.addLayer({ id: 'band-mask', type: 'fill', source: 'band-mask',
        paint: { 'fill-color': PAPER, 'fill-antialias': true } });

      map.addSource('band-keyline', { type: 'geojson', data: keylineFeature });
      map.addLayer({ id: 'band-keyline', type: 'line', source: 'band-keyline',
        layout: { 'line-join': 'miter', 'line-cap': 'square' },
        paint: { 'line-color': INK, 'line-width': 1.5 } });

      map.addSource('band-labels', { type: 'geojson', data: labelFC });
      map.addLayer({ id: 'band-labels', type: 'symbol', source: 'band-labels',
        layout: {
          'icon-image': ['get', 'icon'],
          'icon-rotate': ['get', 'rot'],
          'icon-size': scalarSizeExpr(1.6),
          'icon-rotation-alignment': 'map',
          'icon-pitch-alignment': 'map',
          'icon-allow-overlap': true,
          'icon-ignore-placement': true,
          'icon-anchor': 'center'
        } });

      if (map.hasImage('rw-mark')) {
        map.addSource('band-marks', { type: 'geojson', data: cornerFC });
        map.addLayer({ id: 'band-marks', type: 'symbol', source: 'band-marks',
          layout: {
            'icon-image': 'rw-mark',
            'icon-size': scalarSizeExpr(0.17),
            'icon-rotation-alignment': 'map',
            'icon-pitch-alignment': 'map',
            'icon-allow-overlap': true,
            'icon-ignore-placement': true,
            'icon-anchor': 'center'
          } });
      }
      raiseBand();
    }

    // Keep the band on top if the core adds any layer after us.
    function raiseBand() {
      for (var i = 0; i < BAND_LAYERS.length; i++) {
        if (map.getLayer(BAND_LAYERS[i])) map.moveLayer(BAND_LAYERS[i]);
      }
    }

    // ── snapBack (camera rubber-band) — unchanged screen-space logic ─────────
    // Screen-space bbox of the 9-patch (axis-aligned extent of the four projected
    // corners). Only used to decide how far to pull the camera back on release.
    function regionRect() {
      var pts = [map.project([W, S]), map.project([W, N]), map.project([E, S]), map.project([E, N])];
      var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
        if (p.y < minY) minY = p.y; if (p.y > maxY) maxY = p.y;
      }
      return { minX: minX, minY: minY, maxX: maxX, maxY: maxY };
    }
    function rawGaps() {
      var c = map.getContainer();
      var r = regionRect();
      return { l: r.minX, r: c.clientWidth - r.maxX, t: r.minY, b: c.clientHeight - r.maxY };
    }
    function gaps() {
      var g = rawGaps();
      return { l: Math.max(0, g.l), r: Math.max(0, g.r), t: Math.max(0, g.t), b: Math.max(0, g.b) };
    }
    var snapping = false, userDragged = false;
    function snapBack() {
      var g = gaps();
      var dx = g.l - g.r, dy = g.t - g.b;
      if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
        snapping = true;
        map.panBy([dx, dy], { duration: SNAP_MS, easing: easeOutCubic });
      }
    }
    map.on('dragstart', function () { userDragged = true; });
    map.on('moveend', function () {
      if (snapping) { snapping = false; return; }
      if (!userDragged) return;
      userDragged = false;
      snapBack();
    });

    // ── boot the band once the core's style + layers are in ──────────────────
    function whenReady(tries) {
      if (map.isStyleLoaded()) {
        // Let the core's async load handler finish its addLayer calls, then build
        // the label + corner images and add the band on top; re-raise once on the
        // next idle for good measure. document.fonts.ready keeps the canvas
        // lettering from measuring before Inter (if used) has loaded.
        var start = function () { loadMark(function () { buildLabelImages(); addBand(); }); };
        setTimeout(function () {
          if (document.fonts && document.fonts.ready) document.fonts.ready.then(start, start);
          else start();
        }, 1200);
        map.once('idle', function () { if (map.getSource('band-mask')) raiseBand(); });
        return;
      }
      if ((tries || 0) < 200) return setTimeout(function () { whenReady((tries || 0) + 1); }, 150);
      console.warn('[viewer_band] style never loaded — band not added.');
    }
    whenReady(0);

    // Verify hook for the proof's Playwright checks + the "Show me" button.
    window.AOPViewerBand = {
      addBand: addBand, raiseBand: raiseBand,
      gaps: gaps, rawGaps: rawGaps, snapBack: snapBack, region: region,
      layers: BAND_LAYERS
    };
  }

  boot(0);
})();
