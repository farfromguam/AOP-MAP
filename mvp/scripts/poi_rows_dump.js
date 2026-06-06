#!/usr/bin/env node
/*
 * Card 06 row-parity harness (tile-independent, no browser).
 *
 * Extracts the REAL buildPoiGroups (pre-refactor) or collectStarredDestinations
 * + buildPoiGroups (post-refactor) source text from a given website/js/main.js
 * and runs it against the committed fixture
 * (mvp/scripts/fixtures/poi_rows_fixture.json), so the POI-tab row-id set can be
 * diffed for parity. This runs the actual function source pulled from the file —
 * not a re-implementation — so the diff is real.
 *
 * Usage:
 *   node mvp/scripts/poi_rows_dump.js <path-to-main.js> [out.json]
 *
 * Emits the ordered POI-tab row-id list (and group structure) as JSON to stdout
 * and, if out.json is given, writes it there.
 */
'use strict';
const fs = require('fs');
const path = require('path');

const mainPath = process.argv[2];
const outPath = process.argv[3] || null;
if (!mainPath) {
  console.error('usage: node poi_rows_dump.js <main.js> [out.json]');
  process.exit(2);
}

const src = fs.readFileSync(mainPath, 'utf8');
const fixture = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'fixtures', 'poi_rows_fixture.json'), 'utf8')
);

// --- Extract a top-level `function NAME(...) { ... }` body by brace-matching ---
function extractFunction(text, name) {
  const re = new RegExp('function\\s+' + name + '\\s*\\(', 'g');
  const m = re.exec(text);
  if (!m) return null;
  // Find the opening brace of the body.
  let i = text.indexOf('{', re.lastIndex);
  if (i < 0) return null;
  let depth = 0;
  const start = m.index;
  for (let j = i; j < text.length; j++) {
    const c = text[j];
    if (c === '{') depth++;
    else if (c === '}') {
      depth--;
      if (depth === 0) return text.slice(start, j + 1);
    }
  }
  return null;
}

// Helpers the row builders depend on. Pulled from the SAME file so they stay
// faithful; if a name is absent (e.g. collectStarredDestinations pre-refactor)
// it is simply skipped.
const wanted = [
  'firstCoordinate', 'geometryCentroid', 'geometryBboxCenter', 'trailCatalogLookup',
  'poiIndexLookup', 'poiGroupLabel', 'poiGroupOrder', 'normalizeLocationTag',
  'buildPoiGroups', 'collectStarredDestinations'
];
const fns = {};
for (const name of wanted) {
  const body = extractFunction(src, name);
  if (body) fns[name] = body;
}

// Build a sandbox closure environment that mirrors the IIFE locals the row
// builders read. Toggles are inert stubs (only their identity matters for the
// row.toggle field, which is not part of the row id).
const env = {
  publishDataCache: fixture.publishDataCache,
  eventScheduleConfig: fixture.eventScheduleConfig,
  visitorContextData: fixture.visitorContext,
  aopTrailNetworkCache: fixture.trailNetwork,
  editorPois: fixture.editorPois,
  poiIndex: { groups: [
    { id: 'published_destinations', label: 'Published destinations' },
    { id: 'event_anchors', label: 'Event anchors' },
    { id: 'buildings', label: 'Buildings' },
    { id: 'trails', label: 'Trails' },
    { id: 'cemeteries', label: 'Cemeteries' },
    { id: 'visitor_support', label: 'Visitor support' },
    { id: 'drawn_pois', label: 'Drawn POIs' }
  ], entries: [] },
  trailCatalog: new Map(Object.entries(fixture.trailCatalog).map(([k, v]) => [Number(k), v])),
  eventLocationByTag: new Map(Object.entries(fixture.eventLocations).map(([k, v]) => [k.startsWith('#') ? k : `#${k}`, { coordinates: v }])),
  // featureListRuntime carries the served layers' data + a minimal state so the
  // registry-walking collector (post-refactor) sees the same rows.
  featureListRuntime: {
    buildings: { data: fixture.buildings, state: buildState(fixture.buildings, 'build_id') },
    cemeteries: { data: fixture.cemeteries, state: buildState(fixture.cemeteries, 'parcel_id') },
    visitorContext: { data: fixture.visitorContext, state: buildState(fixture.visitorContext, 'name') },
    editorPois: { data: { type: 'FeatureCollection', features: fixture.editorPois }, state: buildState({ features: fixture.editorPois }, 'id') },
    trails: { data: fixture.trailNetwork, state: buildState(fixture.trailNetwork, '__trail_row_id') },
    brandLogos: fixture.brandLogos ? { data: fixture.brandLogos, state: buildState(fixture.brandLogos, 'logo_id') } : undefined
  },
  // inert toggle stubs
  eventScheduleToggle: { id: 'showEventSchedule' },
  buildingsToggle: { id: 'showBuildings' },
  aopTrailNetworkToggle: { id: 'showAopTrailNetwork' },
  cemeteriesToggle: { id: 'showCemeteries' },
  visitorContextToggle: { id: 'showVisitorContext' },
  editorPoiToggle: { id: 'showEditorPois' },
  // normalizeLocationTag fallback if not extracted
  normalizeLocationTag: (t) => String(t || '').toLowerCase().replace(/^#/, '')
};

// Minimal runtime-state builder mirroring buildFeatureListState's shape:
// { groups: [ { group, features: [ { id, props, feature } ] } ] }, deduped by idField.
function buildState(data, idField) {
  const seen = new Set();
  const features = [];
  for (const feature of (data.features || [])) {
    const props = feature.properties || {};
    const id = props[idField];
    if (id == null) continue;
    if (seen.has(id)) continue;
    seen.add(id);
    features.push({ id, props, feature });
  }
  return { groups: [{ group: { id: 'all' }, features }], visibleIds: new Set() };
}

// Helpers the row builders + spec strategies call.
const helperOrder = [
  'firstCoordinate', 'geometryCentroid', 'geometryBboxCenter', 'trailCatalogLookup',
  'poiIndexLookup', 'poiGroupLabel', 'poiGroupOrder'
];

// Stubs the FEATURE_LIST_LAYERS spec literal + collector reference but that are
// irrelevant to row identity (persistence, source refresh, move math). Adding
// them to env keeps the literal evaluable in one `with(env)` scope.
Object.assign(env, {
  console,
  makeHotspotSpec: () => ({ label: 'hotspot', highlightable: false, groups: [{ id: 'all', label: null, match: () => true, defaultVisible: () => true }] }),
  translateCoordinates: () => {}, savePositionedFeature: () => {}, refreshEditorSource: () => {},
  saveEditorPois: () => {}, duplicateFeature: () => {}, deleteFeature: () => {},
  registerFeatureListLayer: () => {}, map: { getSource: () => null },
  EDITOR_POI_CATEGORIES: [], buildingsData: null, cemeteryData: null,
  visitorContextData2: null, brandLogosData: null,
  // The collector reads these. positionedFeatureIdFor mirrors the real
  // signature: String(feature.properties[spec.idField]).
  VISITOR_LIST_SOURCE_CHIP: { editorPois: 'drawn', brandLogos: 'brand', visitorContext: 'visitor', trails: 'trail' },
  positionedFeatureIdFor: function (layerKey, feature) {
    const spec = env.FEATURE_LIST_LAYERS && env.FEATURE_LIST_LAYERS[layerKey];
    if (!spec || !feature || !feature.properties) return null;
    const v = feature.properties[spec.idField];
    return v == null ? null : String(v);
  }
});

// Locate the FEATURE_LIST_LAYERS object literal in the source.
function specLiteral() {
  const objStart = src.indexOf('const FEATURE_LIST_LAYERS = {');
  if (objStart < 0) return '({})';
  let i = src.indexOf('{', objStart);
  let depth = 0, end = -1;
  for (let j = i; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) { end = j; break; } }
  }
  if (end < 0) return '({})';
  return '(' + src.slice(i, end + 1) + ')';
}

// Assemble ONE scope: helpers, the real spec literal, the real collector +
// buildPoiGroups, all under `with(env)` so closures capture env.* uniformly.
let code = '';
for (const name of helperOrder) if (fns[name]) code += fns[name] + '\n';
if (fns.normalizeLocationTag) code += fns.normalizeLocationTag + '\n';
else code += 'var normalizeLocationTag = env.normalizeLocationTag;\n';
code += 'env.FEATURE_LIST_LAYERS = FEATURE_LIST_LAYERS = ' + specLiteral() + ';\n';
if (fns.collectStarredDestinations) code += fns.collectStarredDestinations + '\n';
if (fns.buildPoiGroups) code += fns.buildPoiGroups + '\n';
code += `
  var groups = (typeof buildPoiGroups === 'function') ? buildPoiGroups() : [];
  var rowIds = [];
  var groupStruct = [];
  for (var gi = 0; gi < groups.length; gi++) {
    var g = groups[gi];
    var ids = (g.rows || []).map(function (r) { return r.id; });
    groupStruct.push({ id: g.id, label: g.label, rowIds: ids });
    for (var k = 0; k < ids.length; k++) rowIds.push(ids[k]);
  }
  return { rowIds: rowIds.slice().sort(), groups: groupStruct };
`;

let result;
try {
  const runner = new Function('env', `
    var FEATURE_LIST_LAYERS = {};
    with (env) {
      ${code}
    }
  `);
  result = runner(env);
} catch (e) {
  console.error('row-dump run failed:', e && e.stack || e);
  process.exit(1);
}

const json = JSON.stringify(result, null, 2);
if (outPath) fs.writeFileSync(outPath, json + '\n');
process.stdout.write(json + '\n');
