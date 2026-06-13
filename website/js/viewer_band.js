// viewer_band.js — PROOF of the off-edge decorative band (V1 "rubber-band"),
// wired onto the REAL MapLibre map of the clean viewer core.
//
// Purpose: determine HOW the band integrates with the core JS + MapLibre, on a
// dedicated page, WITHOUT touching the live viewer. This is the liftable module:
// the only thing the core must provide is the map instance, the tight 9-patch
// bounds (REGION_BOUNDS), and a maxBounds loosened by ~a band's width so the
// camera can be pulled past the 9-patch edge. On viewer_banded.html those three
// are supplied by a small constructor shim (window.AOPViewer); in real
// integration viewer_core.js exposes them directly and this file drops in as-is.
//
// The band is a MASK pinned to the 9-patch rectangle: it covers everything
// OUTSIDE the 9-patch, so data layers may overfill the bounds (no per-shape
// trimming) and the user never sees spill or ragged ends — the visible map is
// always the clean 9-patch. Generalises to any park: set that park's bounds.
//
// Pull behaviour — DON'T fight the gesture; only settle on release:
//   • Inside the 9-patch            → no gap → frame hidden; pan freely.
//   • Pull past any edge            → the frame peeks in (its tiles grow with the
//     gap) and tracks the boundary live; the camera is NOT counter-panned, so a
//     drag is never yanked away mid-gesture. How far you can pull is bounded only
//     by the map's own maxBounds backstop — a user can only scroll so far.
//   • Release                       → snapBack() eases the gap closed so the frame
//     retracts and the clean 9-patch fills the view again (rubber-band).
(function () {
  'use strict';

  var EPS = 2;         // px — gaps under this read as "filled" (rounding guard).
  var SNAP_MS = 520;   // ms — release rubber-band duration.

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

    // The 9-patch frame: 8 border tiles (4 corners + 4 edges). The center is the
    // live map. JS sizes + positions each tile every frame from the 9-patch's
    // screen rectangle, so the whole frame tracks the boundary instead of the
    // viewport, and the eight tiles exactly tile the margin (clean mitred corners,
    // no overlapping full-width/full-height panels).
    function q(sel) { return document.querySelector(sel); }
    var tiles = {
      tl: q('.band-tile.corner.tl'), tr: q('.band-tile.corner.tr'),
      bl: q('.band-tile.corner.bl'), br: q('.band-tile.corner.br'),
      top: q('.band-tile.edge.top'), bottom: q('.band-tile.edge.bottom'),
      left: q('.band-tile.edge.left'), right: q('.band-tile.edge.right')
    };
    if (!tiles.top) { console.warn('[viewer_band] band DOM not found'); return; }

    function clamp(v, a, b) { return v < a ? a : (v > b ? b : v); }

    // Screen-space bbox of the 9-patch (works under the core's bearing:-90 because
    // we project all four corners and take the axis-aligned screen extent).
    function regionRect() {
      var w = region[0][0], s = region[0][1], e = region[1][0], n = region[1][1];
      var pts = [map.project([w, s]), map.project([w, n]), map.project([e, s]), map.project([e, n])];
      var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
        if (p.y < minY) minY = p.y; if (p.y > maxY) maxY = p.y;
      }
      return { minX: minX, minY: minY, maxX: maxX, maxY: maxY };
    }

    // SIGNED bare-margin on each viewport side (negative = the 9-patch edge is
    // OFF-screen past that edge). snapBack and the verify hook read from this.
    function rawGaps() {
      var c = map.getContainer();
      var W = c.clientWidth, H = c.clientHeight;
      var r = regionRect();
      return { l: r.minX, r: W - r.maxX, t: r.minY, b: H - r.maxY, W: W, H: H };
    }

    // Clamped, non-negative gaps — what the mask actually covers per side.
    function gaps() {
      var g = rawGaps();
      return { l: Math.max(0, g.l), r: Math.max(0, g.r),
               t: Math.max(0, g.t), b: Math.max(0, g.b), W: g.W, H: g.H };
    }

    // Position one tile (a corner or an edge). Degenerate tiles (no margin on that
    // side) are hidden so their keyline never shows as a hairline at the viewport
    // edge. Each tile still fills its whole slice of the margin (out to the viewport
    // edge), so the frame masks the ENTIRE out-of-9-patch region (paper, ragged
    // ends, OSM roads spilling past the boundary) — never a fixed sliver.
    function place(el, x, y, w, h) {
      if (w <= EPS || h <= EPS) { el.style.display = 'none'; return; }
      el.style.display = 'block';
      el.style.left = x + 'px'; el.style.top = y + 'px';
      el.style.width = w + 'px'; el.style.height = h + 'px';
    }

    // The lettering hugs the map-facing edge and rides the TRUE 9-patch mid-point
    // (the tile clips any overhang), so it holds its size and its position relative
    // to the landmasses as the map pans — it does not float at the viewport centre.
    function setLabel(tile, prop, px) {
      var lab = tile.firstElementChild;
      if (lab) lab.style[prop] = px + 'px';
    }

    function update() {
      var c = map.getContainer();
      var W = c.clientWidth, H = c.clientHeight;
      var r = regionRect();
      // The 9-patch boundary, clamped to the viewport. Off-screen edges collapse to
      // a zero-width margin so that side's tiles disappear.
      var Lx = clamp(r.minX, 0, W), Rx = clamp(r.maxX, 0, W);
      var Ty = clamp(r.minY, 0, H), By = clamp(r.maxY, 0, H);
      var leftW = Lx, rightW = W - Rx, topH = Ty, botH = H - By;
      var midW = Rx - Lx, midH = By - Ty;

      place(tiles.tl, 0,  0,  leftW,  topH);
      place(tiles.tr, Rx, 0,  rightW, topH);
      place(tiles.bl, 0,  By, leftW,  botH);
      place(tiles.br, Rx, By, rightW, botH);
      place(tiles.top,    Lx, 0,  midW, topH);
      place(tiles.bottom, Lx, By, midW, botH);
      place(tiles.left,   0,  Ty, leftW,  midH);
      place(tiles.right,  Rx, Ty, rightW, midH);

      var midX = (r.minX + r.maxX) / 2, midY = (r.minY + r.maxY) / 2;
      setLabel(tiles.top,    'left', midX - Lx);
      setLabel(tiles.bottom, 'left', midX - Lx);
      setLabel(tiles.left,   'top',  midY - Ty);
      setLabel(tiles.right,  'top',  midY - Ty);
    }

    // Snap the camera back so all gaps close — the band slides out with it.
    // panBy is a pure pixel translation, so it preserves zoom/bearing/pitch and
    // needs no bearing-aware math. +dx pans content left (closes a left gap);
    // +dy pans content up (closes a top gap).
    var snapping = false, userDragged = false;
    function snapBack() {
      var g = gaps();
      var dx = g.l - g.r;
      var dy = g.t - g.b;
      if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) {
        snapping = true;
        map.panBy([dx, dy], { duration: SNAP_MS, easing: easeOutCubic });
      }
    }

    // The frame tracks the boundary live during a pan (update on every move), but
    // the camera is never counter-panned mid-gesture — the user keeps the drag,
    // bounded only by the map's maxBounds backstop. Settling happens on RELEASE
    // (moveend after a real drag), via snapBack().
    map.on('move', update);
    map.on('render', update);
    map.on('resize', update);
    map.on('dragstart', function () { userDragged = true; });
    map.on('moveend', function () {
      if (snapping) { snapping = false; return; }   // ignore the snap's own moveend
      if (!userDragged) return;                       // ignore preset / zoom moves
      userDragged = false;
      snapBack();
    });

    update();

    // Verify hook for the proof's Playwright check.
    window.AOPViewerBand = { update: update, gaps: gaps, rawGaps: rawGaps,
                             snapBack: snapBack, region: region };
  }

  boot(0);
})();
