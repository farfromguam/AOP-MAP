#!/usr/bin/env node
/*
 * Card 06 convergence probe (tile-independent). Runs the REAL
 * collectStarredDestinations from a given main.js against the fixture, then —
 * with one BUILDING feature starred (highlight=true) — reports which rows land
 * on the LEFT (POI tab) surface and which land on the RIGHT (★ Visitor list)
 * surface. Asserts the both-ends convergence the card requires: a starred
 * non-editorPois destination (a building) appears in BOTH surfaces.
 *
 * Usage: node mvp/scripts/poi_rows_surfaces.js <main.js>
 */
'use strict';
const fs = require('fs');
const path = require('path');

const mainPath = process.argv[2];
if (!mainPath) { console.error('usage: node poi_rows_surfaces.js <main.js>'); process.exit(2); }
const src = fs.readFileSync(mainPath, 'utf8');
const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'poi_rows_fixture.json'), 'utf8'));

// Star the first public-facility building (b1 / uuid u1) so the convergence is
// observable. This is the NON-editorPois destination the card's DOM check uses.
for (const f of fixture.buildings.features) {
  if (f.properties && f.properties.aop_facility === true) { f.properties.highlight = true; break; }
}

function extractFunction(text, name) {
  const re = new RegExp('function\\s+' + name + '\\s*\\(', 'g');
  const m = re.exec(text); if (!m) return null;
  let i = text.indexOf('{', re.lastIndex); if (i < 0) return null;
  let depth = 0;
  for (let j = i; j < text.length; j++) {
    if (text[j] === '{') depth++;
    else if (text[j] === '}') { depth--; if (depth === 0) return text.slice(m.index, j + 1); }
  }
  return null;
}
function specLiteral() {
  const objStart = src.indexOf('const FEATURE_LIST_LAYERS = {');
  let i = src.indexOf('{', objStart), depth = 0, end = -1;
  for (let j = i; j < src.length; j++) {
    if (src[j] === '{') depth++;
    else if (src[j] === '}') { depth--; if (depth === 0) { end = j; break; } }
  }
  return '(' + src.slice(i, end + 1) + ')';
}
function buildState(data, idField) {
  const seen = new Set(), features = [];
  for (const feature of (data.features || [])) {
    const props = feature.properties || {}; const id = props[idField];
    if (id == null || seen.has(id)) continue; seen.add(id);
    features.push({ id, props, feature });
  }
  return { groups: [{ group: { id: 'all' }, features }], visibleIds: new Set() };
}

const helperOrder = ['firstCoordinate', 'geometryCentroid', 'geometryBboxCenter', 'trailCatalogLookup', 'poiIndexLookup', 'poiGroupLabel', 'poiGroupOrder'];
const fns = {};
for (const n of [...helperOrder, 'normalizeLocationTag', 'collectStarredDestinations']) {
  const b = extractFunction(src, n); if (b) fns[n] = b;
}

const env = {
  console,
  publishDataCache: fixture.publishDataCache,
  eventScheduleConfig: fixture.eventScheduleConfig,
  visitorContextData: fixture.visitorContext,
  aopTrailNetworkCache: fixture.trailNetwork,
  editorPois: fixture.editorPois,
  poiIndex: { groups: [
    { id: 'published_destinations', label: 'Published destinations' },
    { id: 'event_anchors', label: 'Event anchors' }, { id: 'buildings', label: 'Buildings' },
    { id: 'trails', label: 'Trails' }, { id: 'cemeteries', label: 'Cemeteries' },
    { id: 'visitor_support', label: 'Visitor support' }, { id: 'drawn_pois', label: 'Drawn POIs' }
  ], entries: [] },
  trailCatalog: new Map(Object.entries(fixture.trailCatalog).map(([k, v]) => [Number(k), v])),
  eventLocationByTag: new Map(Object.entries(fixture.eventLocations).map(([k, v]) => [k.startsWith('#') ? k : `#${k}`, { coordinates: v }])),
  featureListRuntime: {
    buildings: { data: fixture.buildings, state: buildState(fixture.buildings, 'build_id') },
    cemeteries: { data: fixture.cemeteries, state: buildState(fixture.cemeteries, 'parcel_id') },
    visitorContext: { data: fixture.visitorContext, state: buildState(fixture.visitorContext, 'name') },
    editorPois: { data: { type: 'FeatureCollection', features: fixture.editorPois }, state: buildState({ features: fixture.editorPois }, 'id') },
    trails: { data: fixture.trailNetwork, state: buildState(fixture.trailNetwork, '__trail_row_id') },
    brandLogos: fixture.brandLogos ? { data: fixture.brandLogos, state: buildState(fixture.brandLogos, 'logo_id') } : undefined
  },
  eventScheduleToggle: {}, buildingsToggle: {}, aopTrailNetworkToggle: {},
  cemeteriesToggle: {}, visitorContextToggle: {}, editorPoiToggle: {},
  makeHotspotSpec: () => ({ label: 'h', groups: [{ id: 'all', match: () => true }] }),
  translateCoordinates: () => {}, savePositionedFeature: () => {}, refreshEditorSource: () => {},
  saveEditorPois: () => {}, duplicateFeature: () => {}, deleteFeature: () => {},
  registerFeatureListLayer: () => {}, map: { getSource: () => null }, EDITOR_POI_CATEGORIES: [],
  buildingsData: null, cemeteryData: null, brandLogosData: null,
  VISITOR_LIST_SOURCE_CHIP: { editorPois: 'drawn', brandLogos: 'brand', visitorContext: 'visitor', trails: 'trail' },
  positionedFeatureIdFor: function (lk, f) {
    const s = env.FEATURE_LIST_LAYERS && env.FEATURE_LIST_LAYERS[lk];
    if (!s || !f || !f.properties) return null;
    const v = f.properties[s.idField]; return v == null ? null : String(v);
  },
  normalizeLocationTag: (t) => String(t || '').toLowerCase()
};

let code = '';
for (const n of helperOrder) if (fns[n]) code += fns[n] + '\n';
if (fns.normalizeLocationTag) code += fns.normalizeLocationTag + '\n';
else code += 'var normalizeLocationTag = env.normalizeLocationTag;\n';
code += 'env.FEATURE_LIST_LAYERS = FEATURE_LIST_LAYERS = ' + specLiteral() + ';\n';
code += fns.collectStarredDestinations + '\n';
code += `
  var rows = collectStarredDestinations();
  var left = rows.filter(function (r) { return r.surfaces && r.surfaces.left === true; }).map(function (r) { return r.id; });
  var right = rows.filter(function (r) { return r.surfaces && r.surfaces.right === true && r.starred === true; }).map(function (r) { return { id: r.id, layerKey: r.layerKey, featureId: r.featureId, label: r.label }; });
  return { left: left.sort(), right: right };
`;
const runner = new Function('env', 'var FEATURE_LIST_LAYERS = {};\n with (env) {\n' + code + '\n}');
const out = runner(env);

console.log('LEFT (POI tab) row ids:', JSON.stringify(out.left));
console.log('RIGHT (★ Visitor list) rows:', JSON.stringify(out.right, null, 2));

const starredBuilding = out.right.find((r) => r.layerKey === 'buildings');
const buildingOnLeft = out.left.includes('building:u1');
console.log('');
console.log('[' + (buildingOnLeft ? 'PASS' : 'FAIL') + '] starred building (building:u1) is on the LEFT POI tab');
console.log('[' + (starredBuilding ? 'PASS' : 'FAIL') + '] starred building also lands on the RIGHT ★ Visitor list (layerKey=buildings)');

// --- Brand-logo right-list regression guard (card 06) -----------------------
// Brand logos were a member of the retired hardcoded VISITOR_LIST_LAYERS: a
// starred brand logo surfaced in the right ★ Visitor list ONLY (never the left
// POI tab — the old buildPoiGroups had no brandLogos block). The one-collector
// refactor first dropped this (brandLogos had no listRow, so emit() skipped it);
// this asserts it is restored AND that it stays off the left tab (R11). The
// left-only row-parity guard structurally cannot see this drop, so it lives
// here. Requires fixture.brandLogos (logo_aop starred, logo_rw not).
let brandOk = true;
if (fixture.brandLogos) {
  const starredLogo = out.right.find((r) => r.layerKey === 'brandLogos');
  const unstarredLogoOnRight = out.right.some((r) => r.layerKey === 'brandLogos' && String(r.featureId) === 'logo_rw');
  const anyLogoOnLeft = out.left.some((id) => String(id).startsWith('brand:'));
  console.log('');
  console.log('[' + (starredLogo ? 'PASS' : 'FAIL') + '] starred brand logo (logo_aop) lands on the RIGHT ★ Visitor list (layerKey=brandLogos) — the regression card 06 restores');
  console.log('[' + (!unstarredLogoOnRight ? 'PASS' : 'FAIL') + '] unstarred brand logo (logo_rw) does NOT land on the right list (★ gate honored)');
  console.log('[' + (!anyLogoOnLeft ? 'PASS' : 'FAIL') + '] no brand logo lands on the LEFT POI tab (R11 — brand logos off the left destination axis)');
  brandOk = !!starredLogo && !unstarredLogoOnRight && !anyLogoOnLeft;
} else {
  console.log('');
  console.log('[INFO] fixture has no brandLogos block — brand-logo right-list guard skipped');
}

process.exit((buildingOnLeft && starredBuilding && brandOk) ? 0 : 1);
