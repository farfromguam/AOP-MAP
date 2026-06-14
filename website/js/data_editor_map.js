/* ===========================================================================
   AOP · Data editor + map — the production editor engine
   ---------------------------------------------------------------------------
   This IS the editor behind `data_editor.html`, which loads it as a thin shell
   (V1 'side-right' layout + 'popup' preview — the user's pick, folded in
   2026-06-13). It is the original `data_editor.html` engine (same getVal/setVal
   round-trip, same per-file localStorage['aop_dataedit::<file>'] autosave) PLUS
   a MapLibre map and two-way selection sync.

   A host HTML sets `window.AOP_MAP_MODE` to one of:
     'side-right'  grid left, map pinned right         (V1 — production)
     'map-first'   map left (primary), grid right      (V3)
     'bottom'      grid full-width, map dock at bottom (V2)
     'overlay'     grid full-width, map slides in      (V4)
   V2/V3/V4 were the review-mockup placements; they stay supported but only V1
   ships. `window.AOP_PREVIEW_STYLE` (popup | phone | fields | chips) picks the
   below-map preview; production uses 'popup'.
   =========================================================================== */
(function () {
  const MODE = window.AOP_MAP_MODE || 'side-right';
  // Optional preview of the selected feature's text AS IT SHOWS WHEN ACTIVE ON
  // THE PUBLIC MAP (faithful to main.js `poiPopupHtml`). Set by the preview
  // mockups; null in the plain layout mockups. One of: popup | phone | fields | chips.
  const PREVIEW = window.AOP_PREVIEW_STYLE || null;
  const MANIFEST = './data/_data_manifest.json';
  const PARK = [-85.748, 35.090]; // [lng,lat] default for a new point
  const REGION_BOUNDS = [[-85.782935283, 35.067164188], [-85.717154097, 35.117928496]];
  const COLS = [
    { key: 'name', label: 'Name', cls: 'wide' },
    { key: 'tag', label: 'Tag', cls: '' },
    { key: 'kind', label: 'Kind', cls: '' },
    { key: 'lat', label: 'Lat', cls: 'num' },
    { key: 'lng', label: 'Lng', cls: 'num' },
    { key: 'desc', label: 'Description', cls: 'wide' },
  ];

  let fc = null, baked = null, file = null, saveTimer = null;
  let map = null, mapReady = false, sel = -1;

  /* ---------- shared style + mode layout (injected so the HTML stays thin) -- */
  const CSS = `
  :root{--ink:#23201a;--muted:#6b6358;--line:#ddd5c4;--paper:#f4efe4;--card:#fffdf7;
    --accent:#7a5c2e;--accent2:#2e6b3f;--danger:#9a3b3b;--bar:#2e2a22;--hot:#ff7a1a}
  *{box-sizing:border-box}html,body{margin:0;height:100%}
  body{background:var(--paper);color:var(--ink);
    font:15px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
    display:flex;flex-direction:column;overflow:hidden}
  .bar{flex:0 0 auto;background:var(--bar);color:#f4efe4;padding:max(8px,env(safe-area-inset-top)) 14px 8px;z-index:30}
  .bar h1{margin:0;font-size:15px;font-weight:650;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
  .bar select{font:inherit;font-size:14px;padding:4px 8px;border-radius:8px;border:1px solid #555;background:#fffdf7;color:var(--ink)}
  .bar .meta{font-size:12px;opacity:.85;margin-top:3px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
  .bar .mapbtn{margin-left:auto;font:inherit;font-size:13px;font-weight:650;border:1px solid #6a6354;background:#3a3528;color:#f4efe4;border-radius:8px;padding:5px 10px;cursor:pointer}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#7bbf8a;margin-right:5px}
  .saved{color:#bfe3c7}
  .hint{flex:0 0 auto;color:var(--muted);font-size:12px;margin:6px 12px;padding:0}

  /* the two panes */
  .stage{flex:1 1 auto;min-height:0;display:flex}
  .gridpane{min-height:0;min-width:0;overflow:auto;background:var(--paper)}
  .mappane{position:relative;min-height:0;min-width:0;background:#bcb6a4}
  .mapcanvas{position:absolute;inset:0}
  .mapbasemap{position:absolute;top:8px;left:8px;z-index:5;display:flex;gap:4px}
  .mapbasemap button{font:inherit;font-size:12px;font-weight:600;border:1px solid #00000022;background:#fffdf7cc;color:var(--ink);border-radius:7px;padding:4px 8px;cursor:pointer;backdrop-filter:blur(4px)}
  .mapbasemap button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
  .maptip{position:absolute;bottom:8px;left:8px;z-index:5;background:#fffdf7cc;color:var(--muted);font-size:11px;padding:3px 8px;border-radius:7px;backdrop-filter:blur(4px)}

  /* table (matches data_editor.html) */
  table{border-collapse:collapse;background:var(--card);border:1px solid var(--line);min-width:100%}
  th{background:#efe9da;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.03em;text-align:left;padding:7px 8px;position:sticky;top:0;white-space:nowrap;z-index:2}
  td{border-top:1px solid var(--line);padding:2px;vertical-align:middle}
  tr.sel td{background:#fff6e6}
  td.rn{color:var(--muted);font-variant-numeric:tabular-nums;text-align:right;padding:2px 8px;font-size:12px;cursor:pointer;white-space:nowrap}
  td.rn:hover{color:var(--accent);font-weight:700}
  tr.sel td.rn{color:var(--hot);font-weight:800}
  input.cell{width:100%;min-width:84px;font:inherit;padding:7px;border:1px solid transparent;border-radius:6px;background:transparent;color:var(--ink)}
  input.cell:hover{border-color:var(--line)}
  input.cell:focus{outline:none;border-color:var(--accent);background:#fff}
  input.num{min-width:92px;font-variant-numeric:tabular-nums}
  input.ro{color:var(--muted);background:#f6f2e8}
  input.wide{min-width:170px}
  .delbtn{border:1px solid #e6c9c9;background:#fff;color:var(--danger);border-radius:7px;width:30px;height:30px;cursor:pointer;font-size:14px}

  .actions{flex:0 0 auto;display:flex;gap:8px;padding:8px 12px calc(8px + env(safe-area-inset-bottom));background:#fffdf7;border-top:1px solid var(--line);z-index:30}
  .actions button{flex:1;padding:11px;font:inherit;font-weight:650;border-radius:10px;border:1px solid var(--line);background:#fff;cursor:pointer}
  .actions .primary{background:var(--accent2);color:#fff;border-color:var(--accent2)}
  .actions .ghost{color:var(--muted)}

  /* ===== mode: side-right (V1) — grid left, map pinned right ===== */
  .stage[data-mode="side-right"]{flex-direction:row}
  .stage[data-mode="side-right"] .gridpane{flex:1 1 56%}
  .stage[data-mode="side-right"] .mappane{flex:1 1 44%;min-width:300px;border-left:1px solid var(--line)}

  /* ===== mode: map-first (V3) — map left (primary), grid right ===== */
  .stage[data-mode="map-first"]{flex-direction:row}
  .stage[data-mode="map-first"] .mappane{flex:1 1 60%;order:1}
  .stage[data-mode="map-first"] .gridpane{flex:1 1 40%;min-width:300px;order:2;border-left:1px solid var(--line)}

  /* ===== mode: bottom (V2) — grid full width, map docked below ===== */
  .stage[data-mode="bottom"]{flex-direction:column}
  .stage[data-mode="bottom"] .gridpane{flex:1 1 auto}
  .stage[data-mode="bottom"] .mappane{flex:0 0 var(--dockh,42vh);border-top:2px solid var(--accent)}
  .stage[data-mode="bottom"].collapsed .mappane{flex-basis:0;border-top:0;overflow:hidden}
  .dockbar{position:absolute;top:0;left:0;right:0;z-index:6;display:flex;align-items:center;gap:8px;
    background:#2e2a22ee;color:#f4efe4;font-size:12px;font-weight:600;padding:4px 10px}
  .dockbar button{margin-left:auto;font:inherit;font-size:12px;border:1px solid #6a6354;background:#3a3528;color:#f4efe4;border-radius:6px;padding:3px 8px;cursor:pointer}
  .stage:not([data-mode="bottom"]) .dockbar{display:none}

  /* ===== mode: overlay (V4) — grid full width, map slides in over the right ===== */
  .stage[data-mode="overlay"]{flex-direction:row;position:relative}
  .stage[data-mode="overlay"] .gridpane{flex:1 1 100%}
  .stage[data-mode="overlay"] .mappane{position:absolute;top:0;right:0;bottom:0;width:min(50%,520px);
    border-left:1px solid var(--line);box-shadow:-8px 0 22px #0003;transform:translateX(101%);
    transition:transform .22s ease;z-index:20}
  .stage[data-mode="overlay"].mapopen .mappane{transform:translateX(0)}
  .mapclose{position:absolute;top:8px;right:8px;z-index:7;width:30px;height:30px;border-radius:50%;
    border:1px solid #00000022;background:#fffdf7cc;color:var(--ink);font-size:15px;cursor:pointer;backdrop-filter:blur(4px)}
  .stage:not([data-mode="overlay"]) .mapclose{display:none}

  /* ===== feature preview region (below the map) ===== */
  /* the map pane becomes a column: map on top, preview below */
  .mappane.haspreview{display:flex;flex-direction:column}
  .mappane.haspreview .mapbox{flex:1 1 auto;position:relative;min-height:120px}
  .previewpane{flex:0 0 auto;max-height:46%;overflow:auto;background:#efe7d5;border-top:2px solid var(--accent);
    padding:10px 12px;-webkit-overflow-scrolling:touch}
  .previewpane .pvcap{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);
    font-weight:700;margin:0 0 8px;display:flex;align-items:center;gap:6px}
  .previewpane .pvcap .live{width:7px;height:7px;border-radius:50%;background:#2e6b3f;box-shadow:0 0 0 3px #2e6b3f22}
  .previewpane .idle{color:var(--muted);font-size:13px;padding:14px 4px;text-align:center}

  /* the faithful map popup card (mirrors css/app.css .poi-tab-popup) */
  .poic{background:#f7f1e2;border:1px solid #d8cdb4;border-radius:9px;padding:11px 13px;
    box-shadow:0 4px 14px #0002;max-width:300px;font-family:Inter,system-ui,sans-serif}
  .poic .poi-popup-title{margin:0 0 4px;font:800 .95rem Inter,system-ui,sans-serif;line-height:1.2;color:#2e2418}
  .poic .poi-popup-subtitle{margin:0 0 6px;font-size:.84rem;line-height:1.32;color:#2e2418}
  .poic .poi-popup-placeholder{margin:0 0 6px;padding:6px 7px;border-radius:5px;background:#ecd9b1;color:#2a1f12;font-size:.8rem;line-height:1.3}
  .poic .poi-popup-meta{margin:0;padding:0;font-size:.76rem;color:#5a4828}
  .poic .poi-popup-meta dt{display:inline;font-weight:700}
  .poic .poi-popup-meta dd{display:inline;margin:0 8px 0 4px}
  .poic .poi-popup-meta dt::before{content:"";display:block}
  .poic .tip{width:14px;height:14px;background:#f7f1e2;border-left:1px solid #d8cdb4;border-bottom:1px solid #d8cdb4;
    transform:rotate(-45deg);margin:-18px auto 6px;border-radius:0 0 0 3px}

  /* phone frame */
  .phone{margin:2px auto 4px;width:208px;border:8px solid #1c1a16;border-radius:30px;background:#1c1a16;
    box-shadow:0 8px 22px #0004;position:relative;padding:14px 8px 16px}
  .phone::before{content:"";position:absolute;top:7px;left:50%;transform:translateX(-50%);width:64px;height:15px;background:#1c1a16;border-radius:0 0 12px 12px;z-index:2}
  .phone .screen{background:linear-gradient(160deg,#7c8a63,#566048);border-radius:20px;min-height:150px;padding:26px 9px 12px;position:relative;overflow:hidden}
  .phone .screen::after{content:"●  ●  ●";position:absolute;bottom:5px;left:0;right:0;text-align:center;color:#ffffff66;font-size:8px;letter-spacing:2px}
  .phone .pin{width:13px;height:13px;border-radius:50%;background:#ff7a1a;border:2px solid #fff;box-shadow:0 1px 4px #0006;margin:2px auto 8px}
  .phone .poic{max-width:none;box-shadow:0 6px 16px #0005}

  /* labeled field rows (utilitarian, empty-state aware) */
  .pvfields{display:flex;flex-direction:column;gap:1px;background:var(--line);border:1px solid var(--line);border-radius:8px;overflow:hidden}
  .pvfields .fr{display:grid;grid-template-columns:84px 1fr;gap:8px;background:var(--card);padding:7px 9px}
  .pvfields .fr dt{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.03em;font-weight:700;padding-top:1px}
  .pvfields .fr dd{margin:0;color:var(--ink);font-size:13.5px;line-height:1.3;word-break:break-word}
  .pvfields .fr.title dd{font-weight:700}
  .pvfields .fr .empty{color:#b08a5a;font-style:italic}
  .pvfields .fr .revisit{color:#9a3b3b}

  /* chip card (richer presentation) */
  .pvchip{background:var(--card);border:1px solid var(--line);border-radius:11px;overflow:hidden;box-shadow:0 3px 12px #0001}
  .pvchip .hd{background:var(--accent);color:#fff;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.05em;padding:5px 12px}
  .pvchip .bd{padding:10px 12px}
  .pvchip .nm{font:800 1.05rem Inter,system-ui,sans-serif;line-height:1.2;color:var(--ink);margin:0 0 4px}
  .pvchip .bl{font-size:13px;line-height:1.35;color:var(--ink);margin:0 0 9px}
  .pvchip .bl.empty{color:#b08a5a;font-style:italic}
  .pvchip .chips{display:flex;flex-wrap:wrap;gap:6px}
  .pvchip .chips span{font-size:11px;font-weight:600;padding:3px 9px;border-radius:20px;background:#efe9da;color:var(--accent);border:1px solid var(--line)}
  .pvchip .chips span b{font-weight:800;color:var(--ink);margin-right:4px;text-transform:uppercase;font-size:9.5px;letter-spacing:.04em}

  /* ===== star (highlight) toggle in the grid ===== */
  th.starh{width:32px;text-align:center;padding:7px 4px}
  td.starcell{padding:2px 2px;text-align:center}
  .starbtn{border:1px solid var(--line);background:#fff;color:#cdbf9a;border-radius:7px;width:30px;height:30px;cursor:pointer;font-size:15px;line-height:1;padding:0}
  .starbtn:hover{border-color:var(--accent)}
  .starbtn.on{color:#e0a32e;border-color:#e0a32e;background:#fdf6e3}

  /* ===== preview/raw tabs + the raw record ===== */
  .pvtabs{display:flex;gap:4px;margin:0 0 8px}
  .pvtabs button{font:inherit;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;
    border:1px solid var(--line);background:#fff;color:var(--muted);border-radius:7px;padding:4px 10px;cursor:pointer}
  .pvtabs button.on{background:var(--accent);color:#fff;border-color:var(--accent)}
  .pvraw{margin:0;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    white-space:pre;overflow:auto;background:#fffdf7;border:1px solid var(--line);border-radius:8px;padding:9px 10px;color:#3a3320;max-width:100%}
  `;

  /* show the bar map toggle only where it controls something */
  function wantsMapToggle() { return MODE === 'overlay' || MODE === 'bottom'; }

  /* ---------- field read/write (PRESERVES everything we don't show) -------- */
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const keyFor = f => 'aop_dataedit::' + f;
  function firstCoord(g) { if (!g) return null; let c = g.coordinates; while (Array.isArray(c) && Array.isArray(c[0])) c = c[0]; return Array.isArray(c) ? c : null; }
  function isPoint(feat) { return feat.geometry && feat.geometry.type === 'Point'; }
  function getVal(feat, key) {
    const p = feat.properties || (feat.properties = {});
    if (key === 'tag') return p.tag != null ? p.tag : (p.category != null ? p.category : '');
    if (key === 'desc') return p.description != null ? p.description : '';
    if (key === 'lat' || key === 'lng') { const c = firstCoord(feat.geometry); if (!c) return ''; return key === 'lat' ? c[1] : c[0]; }
    return p[key] != null ? p[key] : '';
  }
  function setVal(feat, key, val) {
    const p = feat.properties || (feat.properties = {});
    if (key === 'tag') { if ('category' in p && !('tag' in p)) p.category = val; else p.tag = val; return; }
    if (key === 'desc') { p.description = val; return; }
    if (key === 'lat' || key === 'lng') {
      if (!feat.geometry || feat.geometry.type !== 'Point') return;
      const c = feat.geometry.coordinates; const n = parseFloat(val); if (Number.isNaN(n)) return;
      if (key === 'lat') c[1] = n; else c[0] = n; return;
    }
    p[key] = val;
  }

  /* ---------- bbox of any geometry (for fly-to of lines/polygons) --------- */
  function bboxOf(g) {
    if (!g || !g.coordinates) return null;
    let mnx = Infinity, mny = Infinity, mxx = -Infinity, mxy = -Infinity;
    (function walk(c) {
      if (typeof c[0] === 'number') { mnx = Math.min(mnx, c[0]); mxx = Math.max(mxx, c[0]); mny = Math.min(mny, c[1]); mxy = Math.max(mxy, c[1]); }
      else c.forEach(walk);
    })(g.coordinates);
    return isFinite(mnx) ? [[mnx, mny], [mxx, mxy]] : null;
  }

  /* ---------- DOM scaffold ------------------------------------------------- */
  const $ = id => document.getElementById(id);
  function scaffold() {
    const st = document.createElement('style'); st.textContent = CSS; document.head.append(st);
    document.body.innerHTML = `
      <div class="bar">
        <h1>Data editor + map · <select id="fileSel"></select>
          ${wantsMapToggle() ? '<button class="mapbtn" id="mapToggle">🗺 Show map</button>' : ''}
        </h1>
        <div class="meta">
          <span><span class="dot"></span>${MODE}</span>
          <span id="saveTxt" class="saved">—</span>
          <span id="srcTxt"></span>
          <span id="countTxt"></span>
          <span id="starTxt"></span>
        </div>
      </div>
      <p class="hint" id="hint">Click a row's # to fly the map there. Edit Lat/Lng and watch the point move on the imagery. Click a map feature to jump to its row. Tap ★ to mark a place for the viewer's list; the Raw tab below the map shows the full record.</p>
      <div class="stage" id="stage" data-mode="${MODE}">
        <div class="gridpane"><div id="grid" style="padding:10px">Loading…</div></div>
        <div class="mappane${PREVIEW ? ' haspreview' : ''}">
          <div class="mapbox">
            <div class="mapcanvas" id="map"></div>
            <div class="dockbar">Map dock <button id="dockToggle">Hide ▾</button></div>
            <button class="mapclose" id="mapClose" title="Close map">✕</button>
            <div class="mapbasemap">
              <button data-bm="sat" class="on">Satellite</button>
              <button data-bm="street">Street</button>
            </div>
            <div class="maptip" id="maptip">—</div>
          </div>
          ${PREVIEW ? '<div class="previewpane" id="preview"></div>' : ''}
        </div>
      </div>
      <div class="actions">
        <button class="primary" id="addBtn">＋ Add point</button>
        <button id="exportBtn">⤓ Export file</button>
        <button class="ghost" id="resetBtn">↺ Reset</button>
      </div>`;
  }

  /* ---------- map ---------------------------------------------------------- */
  function initMap() {
    if (typeof maplibregl === 'undefined') { $('maptip').textContent = 'MapLibre not loaded'; return; }
    map = new maplibregl.Map({
      container: 'map',
      style: { version: 8, sources: {}, layers: [{ id: 'bg', type: 'background', paint: { 'background-color': '#cfc9b6' } }] },
      center: PARK, zoom: 14, maxBounds: REGION_BOUNDS, attributionControl: false,
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.on('error', e => console.error(e.error || e));
    map.on('load', () => {
      map.addSource('sat', { type: 'raster', tileSize: 256, minzoom: 11, maxzoom: 22,
        tiles: ['https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer/tile/{z}/{y}/{x}'] });
      map.addSource('street', { type: 'raster', tileSize: 256,
        tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'] });
      map.addLayer({ id: 'sat', type: 'raster', source: 'sat' });
      map.addLayer({ id: 'street', type: 'raster', source: 'street', layout: { visibility: 'none' } });

      map.addSource('feats', { type: 'geojson', data: emptyFC() });
      // polygons
      map.addLayer({ id: 'f-fill', type: 'fill', source: 'feats', filter: ['==', ['geometry-type'], 'Polygon'],
        paint: { 'fill-color': '#2e6b3f', 'fill-opacity': 0.18 } });
      map.addLayer({ id: 'f-fill-sel', type: 'fill', source: 'feats', filter: ['all', ['==', ['geometry-type'], 'Polygon'], ['==', ['get', '_i'], -1]],
        paint: { 'fill-color': '#ff7a1a', 'fill-opacity': 0.3 } });
      // lines (+ polygon outlines render as line too)
      map.addLayer({ id: 'f-line', type: 'line', source: 'feats',
        paint: { 'line-color': '#2e6b3f', 'line-width': 2.4 } });
      map.addLayer({ id: 'f-line-sel', type: 'line', source: 'feats', filter: ['==', ['get', '_i'], -1],
        paint: { 'line-color': '#ff7a1a', 'line-width': 4.5 } });
      // points
      map.addLayer({ id: 'f-pt', type: 'circle', source: 'feats', filter: ['==', ['geometry-type'], 'Point'],
        paint: { 'circle-radius': 5, 'circle-color': '#f4efe4', 'circle-stroke-color': '#7a5c2e', 'circle-stroke-width': 2 } });
      map.addLayer({ id: 'f-pt-sel', type: 'circle', source: 'feats', filter: ['all', ['==', ['geometry-type'], 'Point'], ['==', ['get', '_i'], -1]],
        paint: { 'circle-radius': 9, 'circle-color': '#ff7a1a', 'circle-stroke-color': '#fff', 'circle-stroke-width': 3 } });

      ['f-pt', 'f-line', 'f-fill'].forEach(id => {
        map.on('click', id, e => { const i = e.features[0].properties._i; if (i != null) select(+i, false); });
        map.on('mouseenter', id, () => map.getCanvas().style.cursor = 'pointer');
        map.on('mouseleave', id, () => map.getCanvas().style.cursor = '');
      });
      mapReady = true;
      syncMapData();
    });

    // basemap toggle
    document.querySelectorAll('.mapbasemap button').forEach(b => b.onclick = () => {
      const want = b.dataset.bm;
      document.querySelectorAll('.mapbasemap button').forEach(x => x.classList.toggle('on', x === b));
      map.setLayoutProperty('sat', 'visibility', want === 'sat' ? 'visible' : 'none');
      map.setLayoutProperty('street', 'visibility', want === 'street' ? 'visible' : 'none');
    });
  }
  function emptyFC() { return { type: 'FeatureCollection', features: [] }; }
  function mapFC() {
    if (!fc) return emptyFC();
    return { type: 'FeatureCollection', features: (fc.features || []).map((f, i) => ({
      type: 'Feature', geometry: f.geometry,
      properties: Object.assign({}, f.properties, { _i: i }),
    })) };
  }
  function syncMapData() { if (mapReady) map.getSource('feats').setData(mapFC()); }
  function setSelFilter() {
    if (!mapReady) return;
    map.setFilter('f-pt-sel', ['all', ['==', ['geometry-type'], 'Point'], ['==', ['get', '_i'], sel]]);
    map.setFilter('f-line-sel', ['==', ['get', '_i'], sel]);
    map.setFilter('f-fill-sel', ['all', ['==', ['geometry-type'], 'Polygon'], ['==', ['get', '_i'], sel]]);
  }
  function flyToSel() {
    if (!mapReady || sel < 0) return;
    const g = fc.features[sel] && fc.features[sel].geometry;
    if (!g) return;
    if (g.type === 'Point') { map.flyTo({ center: g.coordinates, zoom: Math.max(map.getZoom(), 16.5), duration: 700 }); }
    else { const bb = bboxOf(g); if (bb) map.fitBounds(bb, { padding: 60, maxZoom: 17, duration: 700 }); }
    const f = fc.features[sel];
    $('maptip').textContent = (f.properties && (f.properties.name || f.properties.id)) || ('row ' + (sel + 1)) + ' · ' + (g.type);
  }

  /* ---------- selection (two-way) ----------------------------------------- */
  function select(i, fly) {
    sel = i; setSelFilter();
    document.querySelectorAll('#grid tr').forEach(tr => tr.classList.toggle('sel', +tr.dataset.i === i));
    const row = document.querySelector('#grid tr[data-i="' + i + '"]');
    if (row) row.scrollIntoView({ block: 'nearest' });
    if (MODE === 'overlay') openMap(true);
    if (MODE === 'bottom') $('stage').classList.remove('collapsed'), map && map.resize();
    if (fly !== false) flyToSel();
    renderPreview();
  }

  /* ---------- feature preview (Preview tab) + the raw record (Raw tab) ------ */
  // Preview tab: the model + popup HTML come from the ONE shared strategy
  // (js/feature_display.js) that the reader view uses too — not a local copy —
  // so the card is a TRUE preview, byte-identical to the viewer popup body
  // (viewer_core.js sets it to exactly popupHtml(featureDisplay(props))).
  // Raw tab: the full working GeoJSON record (every field, not just the six
  // grid columns), reflecting your unsaved edits — so you can see/confirm
  // properties the grid doesn't surface (id, status, source, caveat, highlight…).
  let previewTab = 'preview';
  function previewCardHtml(m) {
    const popupCardHtml = window.AOPFeatureDisplay.popupHtml;
    if (PREVIEW === 'phone') {
      return `<div class="phone"><div class="screen"><div class="pin"></div><div class="poic">${popupCardHtml(m)}</div></div></div>`;
    } else if (PREVIEW === 'fields') {
      const empty = '<span class="empty">— empty</span>';
      const row = (lab, val, cls) => `<div class="fr ${cls || ''}"><dt>${lab}</dt><dd>${val}</dd></div>`;
      let sub;
      if (m.blurb) sub = esc(m.blurb);
      else if (m.revisit) sub = `<span class="revisit">Info needed — revisit. ${esc(m.revisit)}</span>`;
      else sub = empty;
      return `<div class="pvfields">`
        + row('Title', esc(m.name), 'title')
        + row('Blurb', sub)
        + row('Kind', esc(m.kind))
        + row('Status', m.status ? esc(m.status) : empty)
        + row('Source', m.source ? esc(m.source) : empty)
        + row('Caveat', m.caveat ? esc(m.caveat) : empty)
        + `</div>`;
    } else if (PREVIEW === 'chips') {
      const chip = (lab, val) => val ? `<span><b>${lab}</b>${esc(val)}</span>` : '';
      return `<div class="pvchip"><div class="hd">${esc(m.kind)}</div><div class="bd">`
        + `<p class="nm">${esc(m.name)}</p>`
        + `<p class="bl${m.blurb ? '' : ' empty'}">${m.blurb ? esc(m.blurb) : (m.revisit ? 'Info needed — revisit. ' + esc(m.revisit) : 'No description yet')}</p>`
        + `<div class="chips">${chip('Status', m.status)}${chip('Source', m.source)}${chip('Caveat', m.caveat)}</div>`
        + `</div></div>`;
    }
    // default 'popup' — the faithful map popup card (unchanged from the fold-in)
    return `<div class="poic">${popupCardHtml(m)}</div><div class="tip"></div>`;
  }
  function renderPreview() {
    if (!PREVIEW) return;
    const host = $('preview'); if (!host) return;
    const tabs = `<div class="pvtabs">`
      + `<button data-tab="preview" class="${previewTab === 'preview' ? 'on' : ''}">Preview</button>`
      + `<button data-tab="raw" class="${previewTab === 'raw' ? 'on' : ''}">Raw record</button>`
      + `</div>`;
    const wire = () => host.querySelectorAll('.pvtabs button').forEach(b => b.onclick = () => { previewTab = b.dataset.tab; renderPreview(); });
    if (sel < 0 || !fc || !fc.features[sel]) {
      const what = previewTab === 'raw' ? 'see its full raw record.' : 'preview how it reads when active on the map.';
      host.innerHTML = tabs + `<div class="idle">Select a row to ${what}</div>`;
      wire(); return;
    }
    if (previewTab === 'raw') {
      const cap = '<p class="pvcap">Raw GeoJSON record · your working copy</p>';
      host.innerHTML = tabs + cap + `<pre class="pvraw">${esc(JSON.stringify(fc.features[sel], null, 2))}</pre>`;
      wire(); return;
    }
    const FD = window.AOPFeatureDisplay;
    if (!FD) { host.innerHTML = tabs + '<div class="idle">feature_display.js not loaded.</div>'; wire(); return; }
    const m = FD.featureDisplay(fc.features[sel].properties);
    const cap = '<p class="pvcap"><span class="live"></span>As shown when active on the map</p>';
    host.innerHTML = tabs + cap + previewCardHtml(m);
    wire();
  }

  /* ---------- grid render -------------------------------------------------- */
  function render() {
    const feats = fc.features || (fc.features = []);
    $('srcTxt').textContent = localStorage.getItem(keyFor(file)) ? 'your edits' : 'published';
    $('countTxt').textContent = feats.length + ' rows';
    updateStarCount();
    let html = '<table><thead><tr><th>#</th><th class="starh" title="Star (highlight) — shows in the viewer’s places list">★</th>' + COLS.map(c => `<th>${c.label}</th>`).join('') + '<th></th></tr></thead><tbody>';
    feats.forEach((f, i) => {
      const starred = (f.properties || {}).highlight === true;
      html += `<tr data-i="${i}"${i === sel ? ' class="sel"' : ''}><td class="rn" data-go="${i}" title="Fly map here">${i + 1}</td>`;
      html += `<td class="starcell"><button class="starbtn ${starred ? 'on' : ''}" data-star="${i}" title="${starred ? 'Starred — shows in the viewer’s places list. Click to unstar.' : 'Not starred. Click to star (highlight=true).'}">${starred ? '★' : '☆'}</button></td>`;
      COLS.forEach(c => {
        const ro = (c.key === 'lat' || c.key === 'lng') && !isPoint(f);
        const v = getVal(f, c.key);
        html += `<td><input class="cell ${c.cls} ${ro ? 'ro' : ''}" data-i="${i}" data-k="${c.key}" value="${esc(v)}" ${ro ? 'readonly title="geometry edited on the map, not here"' : ''}></td>`;
      });
      html += `<td><button class="delbtn" data-del="${i}" title="Delete this point">✕</button></td>`;
    });
    html += '</tbody></table>';
    $('grid').style.padding = '0';
    $('grid').innerHTML = html;
    $('grid').querySelectorAll('input.cell:not(.ro)').forEach(el => {
      el.oninput = () => {
        setVal(fc.features[+el.dataset.i], el.dataset.k, el.value);
        save();
        if (el.dataset.k === 'lat' || el.dataset.k === 'lng') { syncMapData(); if (+el.dataset.i === sel) { setSelFilter(); flyToSel(); } }
        if (+el.dataset.i === sel) renderPreview(); // live: see the active-map text change as you type
      };
      el.onfocus = () => select(+el.dataset.i, false);
    });
    $('grid').querySelectorAll('[data-go]').forEach(td => td.onclick = () => select(+td.dataset.go, true));
    $('grid').querySelectorAll('[data-star]').forEach(b => b.onclick = () => toggleStar(+b.dataset.star));
    $('grid').querySelectorAll('[data-del]').forEach(b => b.onclick = () => del(+b.dataset.del));
  }

  /* ---------- star (highlight) — the published ★ the viewer's list reads ---- */
  // Same data-model field + boolean convention as panel.js/main.js (the ★ is
  // properties.highlight === true, baked by mvp/scripts/bake_poi_stars.py and
  // published). Toggling it here writes the working FC; bake/export carry it.
  function starCount() { return (fc && fc.features || []).filter(f => (f.properties || {}).highlight === true).length; }
  function updateStarCount() { const el = $('starTxt'); if (el) { const n = starCount(); el.textContent = n ? (n + ' ★') : ''; } }
  function toggleStar(i) {
    const f = fc.features[i]; if (!f) return;
    const p = f.properties || (f.properties = {});
    p.highlight = !(p.highlight === true);
    save();
    const on = p.highlight === true;
    const btn = document.querySelector('.starbtn[data-star="' + i + '"]');
    if (btn) {
      btn.classList.toggle('on', on);
      btn.textContent = on ? '★' : '☆';
      btn.title = on ? 'Starred — shows in the viewer’s places list. Click to unstar.' : 'Not starred. Click to star (highlight=true).';
    }
    updateStarCount();
    if (i === sel) renderPreview(); // the raw record shows highlight
  }

  function del(i) {
    const f = fc.features[i]; const nm = (f.properties && f.properties.name) || 'this point';
    if (!confirm(`Delete "${nm}"?`)) return;
    fc.features.splice(i, 1); if (sel === i) sel = -1; save(); render(); syncMapData(); setSelFilter(); renderPreview();
  }
  function addPoint() {
    fc.features = fc.features || [];
    fc.features.push({ type: 'Feature', properties: { name: '', tag: '', kind: 'poi' }, geometry: { type: 'Point', coordinates: [PARK[0], PARK[1]] } });
    save(); render(); syncMapData();
    select(fc.features.length - 1, true);
    const nameCell = [...document.querySelectorAll('#grid tr')].pop().querySelector('input.cell');
    if (nameCell) { nameCell.focus(); }
  }

  /* ---------- save / export / reset (matches data_editor.html) ------------ */
  function markSaved(t) { $('saveTxt').textContent = t; }
  function writeNow() {
    if (!fc || !file) return;
    try { localStorage.setItem(keyFor(file), JSON.stringify(fc)); markSaved('saved to this device'); $('srcTxt').textContent = 'your edits'; }
    catch (e) { markSaved('SAVE FAILED'); }
  }
  function save() { markSaved('saving…'); clearTimeout(saveTimer); saveTimer = setTimeout(writeNow, 250); }
  function flushPending() { clearTimeout(saveTimer); writeNow(); }

  /* ---------- boot -------------------------------------------------------- */
  async function loadFile(f) {
    file = f; sel = -1;
    let stored = null; try { const r = localStorage.getItem(keyFor(f)); stored = r ? JSON.parse(r) : null; } catch (e) {}
    try { baked = await (await fetch('./data/' + f, { cache: 'no-store' })).json(); }
    catch (e) { baked = await (await fetch('./data/' + f)).json().catch(() => null); }
    fc = stored || (baked ? JSON.parse(JSON.stringify(baked)) : emptyFC());
    render(); syncMapData(); setSelFilter(); renderPreview();
    if (mapReady) { const bb = dataBounds(); if (bb) map.fitBounds(bb, { padding: 50, maxZoom: 16, duration: 600 }); }
  }
  function dataBounds() {
    let mnx = Infinity, mny = Infinity, mxx = -Infinity, mxy = -Infinity;
    (fc.features || []).forEach(f => { const bb = bboxOf(f.geometry); if (bb) { mnx = Math.min(mnx, bb[0][0]); mny = Math.min(mny, bb[0][1]); mxx = Math.max(mxx, bb[1][0]); mxy = Math.max(mxy, bb[1][1]); } });
    return isFinite(mnx) ? [[mnx, mny], [mxx, mxy]] : null;
  }

  async function boot() {
    scaffold();
    let man;
    try { man = await (await fetch(MANIFEST, { cache: 'no-store' })).json(); }
    catch (e) { try { man = await (await fetch(MANIFEST)).json(); } catch (_) { $('grid').innerHTML = '<p class="hint">No data manifest. Run <code>python3 mvp/scripts/build_data_manifest.py</code>.</p>'; return; } }
    const files = (man.served || []).filter(s => s.kind === 'geojson' && (s.feature_count || 0) > 0);
    const selEl = $('fileSel'); selEl.innerHTML = '';
    // Re-group the data sources by their MEDALLION tier (read from the filename
    // prefix), so the picker reads Gold / Silver / Bronze / Delete instead of one
    // flat alphabetical list. (User, 2026-06-14: "rename and re-group.")
    const TIER_ORDER = [
      ['gold', 'Gold — production'],
      ['silver', 'Silver — pending review'],
      ['bronze', 'Bronze — not yet promoted'],
      ['delete', 'Delete — staged for removal']
    ];
    const tierOf = (f) => (f.match(/^(gold|silver|bronze|delete)_/) || [, 'bronze'])[1];
    for (const [tier, label] of TIER_ORDER) {
      const group = files.filter(s => tierOf(s.file) === tier).sort((a, b) => a.file.localeCompare(b.file));
      if (!group.length) continue;
      const og = document.createElement('optgroup'); og.label = label;
      group.forEach(s => { const o = document.createElement('option'); o.value = s.file; o.textContent = `${s.file} (${s.feature_count})`; og.append(o); });
      selEl.append(og);
    }
    const def = files.find(s => s.file === 'silver_publish.geojson') || files[0];
    selEl.value = def ? def.file : '';
    selEl.onchange = () => loadFile(selEl.value);

    initMap();
    wireChrome();
    if (def) loadFile(def.file);
  }

  /* ---------- chrome: actions + mode-specific toggles --------------------- */
  function openMap(on) { $('stage').classList.toggle('mapopen', on); if (map) setTimeout(() => map.resize(), 230); }
  function wireChrome() {
    $('addBtn').onclick = addPoint;
    $('exportBtn').onclick = () => {
      const blob = new Blob([JSON.stringify(fc, null, 2)], { type: 'application/json' });
      const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = file; a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    };
    $('resetBtn').onclick = () => {
      if (!confirm('Discard your edits to this file and return to the published version?')) return;
      localStorage.removeItem(keyFor(file)); fc = baked ? JSON.parse(JSON.stringify(baked)) : emptyFC();
      sel = -1; render(); syncMapData(); setSelFilter(); renderPreview(); markSaved('reset to published');
    };
    addEventListener('pagehide', flushPending);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') flushPending(); });

    const mt = $('mapToggle');
    if (mt) mt.onclick = () => {
      if (MODE === 'overlay') { const on = !$('stage').classList.contains('mapopen'); openMap(on); mt.textContent = on ? '🗺 Hide map' : '🗺 Show map'; }
      if (MODE === 'bottom') { const c = $('stage').classList.toggle('collapsed'); mt.textContent = c ? '🗺 Show map' : '🗺 Hide map'; if (map) setTimeout(() => map.resize(), 50); }
    };
    const dt = $('dockToggle'); if (dt) dt.onclick = () => { $('stage').classList.add('collapsed'); if (mt) mt.textContent = '🗺 Show map'; if (map) setTimeout(() => map.resize(), 50); };
    const mc = $('mapClose'); if (mc) mc.onclick = () => { openMap(false); if (mt) mt.textContent = '🗺 Show map'; };
  }

  boot();
})();
