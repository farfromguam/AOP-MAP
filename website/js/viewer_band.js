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
    // Kept small so the labels stay within a tight region-fit (e.g. the Region
    // preset's ~20px padding) instead of clipping off the screen edge.
    var insetX = dW * 0.030, insetY = dH * 0.030;
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

    // ── decorative art: lettering + corner marks, baked to a DRAPED RASTER ────
    // A symbol/icon is a flat BILLBOARD pinned to ONE terrain elevation, so it can't
    // fold over the hills — a single icon floats and a row of icons just staircases.
    // The fix is the technique already proven on the SFWDA paper map (main.js ~1553):
    // bake the art to a georeferenced image and add it as `type:'image'` sources →
    // `type:'raster'` layers. MapLibre DRAPES raster/image layers onto the terrain
    // mesh (render to texture, then fold per-pixel onto the hills), so the lettering
    // conforms to the landscape CONTINUOUSLY — the same way the AOP paper map folds in
    // 3D. The paper `fill` mask and the `line` keyline already drape, so only the
    // lettering + corner marks (the old symbols) move onto the baked raster.
    //
    // The art is baked NORTH-UP and pinned by geographic corners, so it rotates/tilts
    // with the map (true geolocation). At the DEFAULT bearing of -90° the picked screen
    // layout (title top / location bottom / 35°N left / 85°W right) maps to: title→West
    // edge, location→East, 35°N→South, 85°W→North; each label's `rot` (map-space, ==
    // the canvas rotation in the north-up bake) keeps it upright along its edge there.
    var midLng = (W + E) / 2, midLat = (S + N) / 2;
    var LABEL_P = 1.6;     // label ground scale (was the symbol icon-size at ZREF)
    var MARK_P  = 0.40;    // corner-mark ground scale (was the symbol icon-size)
    var GRID_N  = 6;       // art is sliced into GRID_N² draped raster tiles (SFWDA value)

    // Metres per screen pixel at ZREF (MapLibre worldSize = 512·2^zoom = 2^(zoom+9)),
    // so a label image's pixel width maps to the ground span it should occupy.
    function metresPerPx(lat) {
      return 40075016.686 * Math.cos(lat * Math.PI / 180) / Math.pow(2, ZREF + 9);
    }

    // Edge → label keyed to the DEFAULT -90 bearing (top=West, bottom=East,
    // left=South, right=North): title top (W), location bottom (E, no year),
    // latitude left (S), event right (N).
    var EDGES = [
      { key: 'w', label: 'Adventure Off Road Park',                      at: [W - insetX, midLat], lat: midLat,     rot: -90, fontPx: 13, weight: 800, color: TITLE_INK, spacing: 0.42 },
      { key: 'e', label: 'South Pittsburg · Marion County · Tennessee',  at: [E + insetX, midLat], lat: midLat,     rot: -90, fontPx: 10, weight: 700, color: SUB_INK,   spacing: 0.30 },
      { key: 's', label: '35° 00′ North · Cumberland Plateau',           at: [midLng, S - insetY], lat: S - insetY, rot: 180, fontPx: 10, weight: 700, color: SUB_INK,   spacing: 0.30 },
      { key: 'n', label: 'Rock Warblers Trail Blazing Invitational',     at: [midLng, N + insetY], lat: N + insetY, rot: 0,   fontPx: 10, weight: 700, color: SUB_INK,   spacing: 0.30 }
    ];

    // Render one label string to a supersampled (DPR=4) canvas (exact picked
    // typography: weight, tracking, uppercase, the ·°′— glyphs; system-ui fallback if
    // Inter isn't loaded). `groundM` is the ground length the label should occupy
    // along its edge (icon-size LABEL_P at ZREF) — the bake scales it to that.
    function renderLabel(e) {
      var DPR = 4;
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
      return { canvas: cv, w: w, h: h, groundM: (w / DPR) * LABEL_P * metresPerPx(e.lat) };
    }

    // Corner marks sit OUTSIDE the neat-line corners, pushed diagonally out onto the
    // paper margin so they read as printer's corner ornaments, not dots on the line.
    var cornOutX = dW * 0.052, cornOutY = dH * 0.052;
    var CORNERS = [
      [W - cornOutX, S - cornOutY], [E + cornOutX, S - cornOutY],
      [E + cornOutX, N + cornOutY], [W - cornOutX, N + cornOutY]
    ];

    // Geographic frame of the baked art (region + a margin wide enough to hold the
    // pushed-out corner marks WHOLE — they sit at cornOut 0.052 and the rotated mark
    // box reaches ~0.05 further, so 0.12 keeps the bird/letters off the canvas edge),
    // north-up, at an isotropic resolution (so the typography isn't squashed) capped at
    // 4096 px (GPU/iOS texture limit).
    var artMx = dW * 0.12, artMy = dH * 0.12;
    var artW = W - artMx, artE = E + artMx, artS = S - artMy, artN = N + artMy;
    var spanLngM = (artE - artW) * 111320 * Math.cos(midLat * Math.PI / 180);
    var spanLatM = (artN - artS) * 110540;
    var pxPerM = 4096 / Math.max(spanLngM, spanLatM);
    var artCvW = Math.round(spanLngM * pxPerM), artCvH = Math.round(spanLatM * pxPerM);
    function gx(lng) { return (lng - artW) / (artE - artW) * artCvW; }
    function gy(lat) { return (artN - lat) / (artN - artS) * artCvH; }

    var inkCanvas = null;   // rw-mark ink silhouette canvas, set by loadMark

    // Bake lettering + corner marks into one north-up georeferenced canvas. Each label
    // is drawn rotated by `rot` (canvas clockwise == the symbol's map-space rotate) and
    // scaled to its ground length, so the baked look matches the picked design exactly —
    // only now it is a raster that DRAPES over the terrain.
    function bakeBandArt() {
      var cv = document.createElement('canvas'); cv.width = artCvW; cv.height = artCvH;
      var ctx = cv.getContext('2d');
      ctx.imageSmoothingQuality = 'high';
      for (var i = 0; i < EDGES.length; i++) {
        var e = EDGES[i], L = renderLabel(e);
        var pxLen = L.groundM * pxPerM, pxH = pxLen * (L.h / L.w);
        ctx.save();
        ctx.translate(gx(e.at[0]), gy(e.at[1]));
        ctx.rotate(e.rot * Math.PI / 180);
        ctx.drawImage(L.canvas, -pxLen / 2, -pxH / 2, pxLen, pxH);
        ctx.restore();
        L.canvas.width = L.canvas.height = 0;
      }
      if (inkCanvas) {
        var markPx = (inkCanvas.width / 2) * MARK_P * metresPerPx(midLat) * pxPerM;
        for (var c = 0; c < CORNERS.length; c++) {
          ctx.save();
          ctx.translate(gx(CORNERS[c][0]), gy(CORNERS[c][1]));
          ctx.rotate(-90 * Math.PI / 180);
          ctx.drawImage(inkCanvas, -markPx / 2, -markPx / 2, markPx, markPx);
          ctx.restore();
        }
      }
      return cv;
    }

    // ── corner mark: rasterise rw-mark.svg into a flat INK silhouette CANVAS ──
    // (draw the art, then source-in fill it with the neat-line ink so it reads as a
    // printed stamp). Kept as a canvas so the bake can draw it rotated at each corner.
    function loadMark(cb) {
      if (inkCanvas) return cb();
      var SZ = 256;
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
          inkCanvas = cv;
        } catch (err) { console.warn('[viewer_band] rw-mark raster failed:', err); }
        cb();
      };
      img.onerror = function () { console.warn('[viewer_band] rw-mark image failed to load'); cb(); };
      img.src = './assets/branding/rw-mark.svg';
    }

    // ── add the band layers (idempotent), on TOP of the core's layers ────────
    // Paper mask (fill) and keyline (line) DRAPE natively; the lettering + corner
    // marks ride a baked raster mesh (SFWDA recipe) so they DRAPE too.
    var tileLayerIds = [];
    var BAND_LAYERS = ['band-mask', 'band-keyline'];
    function addBand() {
      if (map.getSource('band-mask')) { raiseBand(); return; }

      map.addSource('band-mask', { type: 'geojson', data: maskFeature });
      map.addLayer({ id: 'band-mask', type: 'fill', source: 'band-mask',
        paint: { 'fill-color': PAPER, 'fill-antialias': true } });

      map.addSource('band-keyline', { type: 'geojson', data: keylineFeature });
      map.addLayer({ id: 'band-keyline', type: 'line', source: 'band-keyline',
        layout: { 'line-join': 'miter', 'line-cap': 'square' },
        paint: { 'line-color': INK, 'line-width': 1.5 } });

      // Bake the art, slice it into a GRID_N×GRID_N mesh, add each tile as an image
      // source → raster layer (the SFWDA paper-map technique). Tile pixel boundaries
      // and geographic corners come from the SAME cuts, so the tiles are seamless;
      // each draped raster tile folds over the terrain.
      var art = bakeBandArt();
      function lngOfPx(px) { return artW + (px / artCvW) * (artE - artW); }
      function latOfPx(py) { return artN - (py / artCvH) * (artN - artS); }
      for (var r = 0; r < GRID_N; r++) {
        var y0 = Math.floor(r * artCvH / GRID_N);
        var y1 = (r === GRID_N - 1) ? artCvH : Math.floor((r + 1) * artCvH / GRID_N);
        for (var c = 0; c < GRID_N; c++) {
          var x0 = Math.floor(c * artCvW / GRID_N);
          var x1 = (c === GRID_N - 1) ? artCvW : Math.floor((c + 1) * artCvW / GRID_N);
          var sub = document.createElement('canvas');
          sub.width = x1 - x0; sub.height = y1 - y0;
          sub.getContext('2d').drawImage(art, x0, y0, x1 - x0, y1 - y0, 0, 0, sub.width, sub.height);
          var sid = 'band-art-' + r + '-' + c;
          try {
            map.addSource(sid, { type: 'image', url: sub.toDataURL('image/png'),
              coordinates: [[lngOfPx(x0), latOfPx(y0)], [lngOfPx(x1), latOfPx(y0)],
                            [lngOfPx(x1), latOfPx(y1)], [lngOfPx(x0), latOfPx(y1)]] });
            map.addLayer({ id: sid, type: 'raster', source: sid,
              paint: { 'raster-opacity': 1, 'raster-fade-duration': 0, 'raster-resampling': 'linear' } });
            tileLayerIds.push(sid);
          } catch (err) { console.warn('[viewer_band] art tile failed:', sid, err); }
          sub.width = sub.height = 0;
        }
      }
      art.width = art.height = 0;   // release the full bake canvas
      BAND_LAYERS = ['band-mask', 'band-keyline'].concat(tileLayerIds);
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
        var start = function () { loadMark(addBand); };
        setTimeout(function () {
          if (document.fonts && document.fonts.ready) document.fonts.ready.then(start, start);
          else start();
        }, 1200);
        // Re-raise on EVERY idle: the core loads roads/rivers asynchronously and would
        // otherwise sit on top of the band. The border must stay the highest layer.
        map.on('idle', function () { if (map.getSource('band-mask')) raiseBand(); });
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
      bandLayers: function () { return BAND_LAYERS; }
    };
  }

  boot(0);
})();
