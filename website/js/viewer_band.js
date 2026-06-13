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
// "Option B" leash (this file): a UNIFORM, pixel-space pull limit on ALL FOUR
// sides, independent of the 9-patch shape / bearing / window aspect:
//   • Inside the 9-patch            → no gap → mask fully hidden.
//   • Pull past any edge            → you may reveal at most MAX_PULL px of the
//     exterior on that side; the mask grows to cover exactly that gap.
//   • Can't fill the viewport       → (zoomed out / odd aspect) the mask covers
//     the whole margin so no exterior shows — the 9-patch stays fully on screen.
//   • Release                       → eases back so the gap closes and the mask
//     retracts. The px leash is enforced in screen space, so top/bottom behave
//     exactly like left/right even when the 9-patch fills one axis.
(function () {
  'use strict';

  var MAX_PULL = 72;   // px — how far past the 9-patch you may pull on ANY side
                       // (uniform; this is the mask's max reveal on an overpull).
  var EPS = 2;         // px — gaps under this read as "filled" (rounding guard).
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

    // SIGNED bare-margin on each viewport side (negative = the 9-patch edge is
    // OFF-screen past that edge) plus the 9-patch's own screen extent. The leash
    // and the mask both read from this.
    function rawGaps() {
      var c = map.getContainer();
      var W = c.clientWidth, H = c.clientHeight;
      var r = regionRect();
      return {
        l: r.minX, r: W - r.maxX, t: r.minY, b: H - r.maxY,
        wpx: r.maxX - r.minX, hpx: r.maxY - r.minY, W: W, H: H
      };
    }

    // Clamped, non-negative gaps — what the mask actually covers per side.
    function gaps() {
      var g = rawGaps();
      return { l: Math.max(0, g.l), r: Math.max(0, g.r),
               t: Math.max(0, g.t), b: Math.max(0, g.b), W: g.W, H: g.H };
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

    // Option-B leash, enforced in screen pixels so it is uniform on all sides:
    //   • if the 9-patch FILLS an axis (taller/wider than the viewport) → it's an
    //     overpull; cap the exterior shown on each side at MAX_PULL px.
    //   • if the 9-patch CANNOT fill an axis → keep it fully on screen (no edge
    //     pushed off); the mask covers the leftover margin.
    // A counter-pan (jump, no animation) pins the camera at the limit; a guard
    // stops the panBy's own 'move' from re-entering.
    var clamping = false;
    function axisCorrection(gA, gB, extent, viewport) {
      if (extent >= viewport) {                 // overpull regime → cap at MAX_PULL
        if (gA > MAX_PULL) return (gA - MAX_PULL);
        if (gB > MAX_PULL) return -(gB - MAX_PULL);
      } else {                                   // can't fill → keep 9-patch on screen
        if (gA < 0) return gA;
        if (gB < 0) return -gB;
      }
      return 0;
    }
    function enforceLeash() {
      if (clamping) return;
      var g = rawGaps();
      var dx = axisCorrection(g.l, g.r, g.wpx, g.W);
      var dy = axisCorrection(g.t, g.b, g.hpx, g.H);
      if (dx !== 0 || dy !== 0) {
        clamping = true;
        map.panBy([dx, dy], { duration: 0 });
        clamping = false;
      }
    }

    function onMove() { enforceLeash(); update(); }

    map.on('move', onMove);
    map.on('render', update);
    map.on('resize', onMove);
    map.on('dragstart', function () { userDragged = true; });
    map.on('moveend', function () {
      if (snapping) { snapping = false; return; }   // ignore the snap's own moveend
      if (!userDragged) return;                       // ignore preset / zoom moves
      userDragged = false;
      snapBack();
    });

    enforceLeash();
    update();

    // Verify hook for the proof's Playwright check.
    window.AOPViewerBand = { update: update, gaps: gaps, rawGaps: rawGaps,
                             enforceLeash: enforceLeash, region: region, MAX_PULL: MAX_PULL };
  }

  boot(0);
})();
