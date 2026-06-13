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
// The mechanic (matches the chosen V1 prototype):
//   • Normal panning inside the 9-patch  → no gap → band stays off-screen.
//   • Pull PAST the 9-patch edge          → a screen-space gap opens between the
//     9-patch and the viewport edge → the matching band strip slides in,
//     proportional to the gap, capped at the band width.
//   • Release                             → the camera eases back so the gap
//     closes → the band slides back out of sight. Never a resting state.
(function () {
  'use strict';

  var EPS = 2;         // px — gaps under this read as "filled" (rounding guard),
                       // so the band stays fully hidden during normal panning.
  var SNAP_MS = 520;

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

    var edges = {
      top: document.querySelector('.band-edge.top'),
      bottom: document.querySelector('.band-edge.bottom'),
      left: document.querySelector('.band-edge.left'),
      right: document.querySelector('.band-edge.right')
    };
    if (!edges.top) { console.warn('[viewer_band] band DOM not found'); return; }

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

    // Bare-margin (px) on each viewport side, i.e. how far the 9-patch edge has
    // pulled IN from the viewport edge.
    function gaps() {
      var c = map.getContainer();
      var W = c.clientWidth, H = c.clientHeight;
      var r = regionRect();
      return {
        l: Math.max(0, r.minX),
        r: Math.max(0, W - r.maxX),
        t: Math.max(0, r.minY),
        b: Math.max(0, H - r.maxY),
        W: W, H: H
      };
    }

    // Each strip grows from its viewport edge to exactly the 9-patch boundary, so
    // it masks the ENTIRE out-of-9-patch region (paper, ragged ends, AND any OSM
    // roads that extend past the 9-patch) — never a fixed sliver that leaves a
    // band of real data showing in the frame.
    function setEdge(el, dim, px) {
      px = (px > EPS) ? px : 0;
      el.style[dim] = px + 'px';
      el.style.borderWidth = px > 0 ? '' : '0';   // hide the keyline when retracted
    }

    function update() {
      var g = gaps();
      setEdge(edges.top, 'height', g.t);
      setEdge(edges.bottom, 'height', g.b);
      setEdge(edges.left, 'width', g.l);
      setEdge(edges.right, 'width', g.r);
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
    window.AOPViewerBand = { update: update, gaps: gaps, region: region };
  }

  boot(0);
})();
