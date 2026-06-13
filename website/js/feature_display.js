/* ===========================================================================
   AOP · feature_display — the ONE feature-to-text strategy for all data
   ---------------------------------------------------------------------------
   Single source of truth for "how does a feature read when it's active on the
   map." Replaces the SIX per-layer `listRow` derivations in main.js
   (cemeteries / buildings / drawn / visitor / brand / trails) — each of which
   hard-coded its own Status/Source and picked a different blurb property. That
   per-layer branching is a development artifact; the user's call (2026-06-13):
   *"there should not [be] per-layer display rules… we need to find and
   normalise. only one text concatenation strategy for all data."*

   So this is branch-free: every field reads the SAME uniform fallback chain for
   EVERY feature, from the feature's own properties. Where a layer used to inject
   a constant (e.g. cemeteries' Source = "TN Comptroller parcels"), that value
   belongs ON the feature as data (baked in) — not in code here.

   Loaded by BOTH the reader view (main.js) and the editors via a plain <script>
   tag; attaches `window.AOPFeatureDisplay = { featureDisplay, popupHtml, esc }`.
   No build step, no module system (main.js is a vanilla IIFE).
   =========================================================================== */
(function (root) {
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g,
      c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }

  // First non-empty value across a fallback chain of property names.
  function pick(obj, keys) {
    for (const k of keys) {
      const v = obj[k];
      if (v != null && String(v).trim() !== '') return v;
    }
    return '';
  }

  // ONE strategy — the same fallback chains for ALL data, no per-layer switch.
  // The chains are the UNION of the property names the old per-layer blocks read,
  // ordered most-specific-first, so a feature that already carries the field wins.
  function featureDisplay(props) {
    props = props || {};
    const facets = props.facets || {};
    const kindRaw = pick(props, ['kind', 'category', 'cemetery_type', 'primary_occupancy', 'type']);
    return {
      name: pick(props, ['name', 'label', 'title', 'building_label', 'category']) || '(unnamed)',
      kind: kindRaw ? String(kindRaw).replace(/_/g, ' ').toLowerCase() : '',
      blurb: pick(props, ['description', 'notes', 'services', 'blurb']),
      status: pick(props, ['status', 'confidence']),
      source: pick(props, ['source', '_src', 'footprint_source']),
      caveat: pick(props, ['caveat', 'drive_time_note']),
      revisit: pick(props, ['revisit_note', 'revisitNote']) || pick(facets, ['revisit_note']),
    };
  }

  // The ONE renderer — identical contract to main.js poiPopupHtml: title, then a
  // subtitle (blurb) OR the "Info needed — revisit" placeholder, then the
  // Kind/Status/Source/Caveat meta list (each meta line only if present).
  function popupHtml(model) {
    const m = model || {};
    let s = `<p class="poi-popup-title">${esc(m.name)}</p>`;
    if (m.blurb) s += `<p class="poi-popup-subtitle">${esc(m.blurb)}</p>`;
    else if (m.revisit) s += `<p class="poi-popup-placeholder">Info needed — revisit. ${esc(m.revisit)}</p>`;
    let meta = `<dt>Kind</dt><dd>${esc(m.kind || 'unknown')}</dd>`;
    if (m.status) meta += `<dt>Status</dt><dd>${esc(m.status)}</dd>`;
    if (m.source) meta += `<dt>Source</dt><dd>${esc(m.source)}</dd>`;
    if (m.caveat) meta += `<dt>Caveat</dt><dd>${esc(m.caveat)}</dd>`;
    return s + `<dl class="poi-popup-meta">${meta}</dl>`;
  }

  root.AOPFeatureDisplay = { featureDisplay, popupHtml, esc };
})(typeof window !== 'undefined' ? window : this);
