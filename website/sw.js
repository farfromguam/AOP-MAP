/* AOP Map service worker.
 *
 * Three caches, three strategies:
 *   - shell  (cache-first)            app code + icons. Precached on install; the
 *                                     app opens with no network once installed.
 *   - data   (cache-first)            local GeoJSON/JSON/WebP under ./data/.
 *                                     Best-effort precached on install so a single
 *                                     online "install + open" warms most layers for
 *                                     the field; the two heaviest default-off layers
 *                                     are excluded (see DATA_ASSETS / M13) and
 *                                     anything missed is cached on first view.
 *   - tiles  (cache-first, capped)    third-party raster basemaps (TNMap satellite,
 *                                     AWS terrain, USDA NAIP). Best-effort: a tile is
 *                                     only available offline if it was viewed online.
 *                                     Capped by entry count so it can't crowd out the app.
 *
 * Exceptions (stale-while-revalidate — instant from cache, refresh on signal so
 * installed users don't get stuck on stale content between VERSION bumps):
 *   - ./data/aop_event_schedule.json (event timetable)
 *   - ./data/aop_ui_strings.json, aop_about.json, aop_copy_registry.json (copy)
 *   - the app shell HTML — navigations are network-first AND refresh the cached
 *     shell; a non-navigation .html fetch is stale-while-revalidate.
 * Bulky GeoJSON stays cache-first and only refreshes on a VERSION bump.
 *
 * Bump VERSION to invalidate the shell + data caches on the next deploy. The tile
 * cache is intentionally version-independent — tiles never change, so re-downloading
 * them on every release would waste the user's data.
 */

// RELEASE CHECKLIST when app code or data changes:
//   1. bump VERSION here   2. bump #appVersion in index.html (~line 1063)
//   3. reconcile DATA_ASSETS below with `ls website/data/`
// Shell HTML + copy JSON self-heal (stale-while-revalidate), so a missed bump is
// less dangerous than before — but bulky GeoJSON only refreshes on a bump.
const VERSION = 'v90'; // keep in sync with #appVersion in index.html
const SHELL_CACHE = `aop-shell-${VERSION}`;
const DATA_CACHE = `aop-data-${VERSION}`;
const TILE_CACHE = 'aop-tiles'; // unversioned on purpose — see header note
const TILE_CACHE_MAX = 1500;

// App shell — must all cache successfully or install fails. Keep this list to
// things that definitely exist and are small.
const SHELL_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './vendor/maplibre-gl.css',
  './vendor/maplibre-gl.js',
  './vendor/terra-draw.umd.js',
  './vendor/terra-draw-maplibre-gl-adapter.umd.js',
  // App shell code, split out of index.html (viewer_source_split). Served
  // stale-while-revalidate (see fetch handler) so a missed VERSION bump still
  // self-heals like the HTML shell; precached here for offline-first load.
  './css/app.css',
  // The ONE shared event-schedule resolver (going gold G_E): both main.js and
  // panel.js read window.AOPEventSchedule, so it precaches with the app shell.
  './js/event_schedule_geojson.js',
  // The ONE feature-to-text strategy (normalize_feature_display): shared by
  // main.js + the editors via window.AOPFeatureDisplay, precached with the shell.
  './js/feature_display.js',
  // Front-end read view (Sprint 13 viewer extraction, slice 7 swap): index.html
  // is now the clean viewer, which loads these two. Precached so the front end
  // is offline-first.
  './css/viewer.css',
  './js/viewer_core.js',
  // Off-edge decorative band — geolocated neat-line frame drawn on top of the
  // core (loaded by index.html after viewer_core.js). Precached so the framed
  // viewer is offline-first; the band fetches the corner mark below at runtime.
  './js/viewer_band.js',
  './assets/branding/rw-mark.svg',
  // The old all-in-one page is parked at old_index.html and still uses these
  // (main.js + the embedded panel); the standalone field editors load them too.
  // Kept in the precache shell so those pages also work offline.
  './js/main.js',
  // Right-panel swap (Stage 1): the embedded one-model panel + its scoped styles.
  './css/panel-embed.css',
  './js/panel.js',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
];

// Local data — best-effort precache. A 404 or rename here must NOT break install,
// so these are fetched with allSettled rather than addAll. Whatever isn't here
// (or fails) still gets cached the first time the app fetches it online.
const DATA_ASSETS = [
  './data/gold_publish.geojson',
  './data/aop_poi_index.json',
  './data/aop_trail_catalog.json',
  './data/gold_aop_trail_network.geojson',
  './data/gold_aop_roads.geojson',
  './data/gold_aop_water.geojson',
  './data/gold_aop_buildings.geojson',
  './data/gold_aop_waypoints_traced.geojson',
  './data/bronze_aop_cemeteries.geojson',
  './data/gold_aop_landcover.geojson',
  './data/gold_aop_landcover_9patch.geojson',
  './data/bronze_aop_9_patch.geojson',
  './data/bronze_aop_lidar_tiles.geojson',
  './data/gold_aop_activity_hotspots.geojson',
  './data/delete_aop_synthetic_activity_hotspots.geojson',
  './data/gold_aop_visitor_context_callouts.geojson',
  // Deliberately NOT precached (M13): gold_aop_contours.geojson (~14 MB) and
  // delete_aop_synthetic_activity_tracks.geojson (~1 MB) are the two heaviest layers and
  // both default OFF (showContours / showSyntheticActivity unchecked). Precaching
  // them forced a ~15 MB background download the moment a phone installs — bad on
  // weak field signal, for layers most installs never turn on. The cache-first
  // `/data/` fetch handler still caches each the first time it IS viewed online,
  // so "offline-after-once" holds for whoever actually enables them.
  // (brand logos merged into gold_aop_visitor_context_callouts.geojson, 2026-06-05)
  './data/bronze_aop_editor_seed_pois.geojson',
  './data/aop_event_schedule.json',
  './data/aop_about.json',
  './data/aop_ui_strings.json',
  './data/aop_copy_registry.json',
  './data/bronze_osm_aop_9patch.geojson',
  './data/bronze_osm_aop_named.geojson',
  './data/sfwda_aop_trail_map.webp',
  './data/sfwda_aop_trail_map_no_trails.webp',
  './data/sfwda_raster_alignment.json',
  './data/delete_sfwda_traced_trails.geojson',
  // Removed as of v21 (unreferenced by index.html — present on disk only):
  // aop_synthetic_activity_report.json, bronze_sfwda_traced_markers.geojson,
  // bronze_sfwda_numbered_trails.geojson, bronze_sfwda_trails_edited.geojson. Re-add here if
  // any gets wired into the viewer.
];

// Same-origin paths that are stale-while-revalidate instead of cache-first, so
// edits reach installed users without a VERSION bump. Matched by pathname suffix.
const SWR_SUFFIXES = [
  '/data/aop_event_schedule.json',
  '/data/aop_ui_strings.json',
  '/data/aop_about.json',
  '/data/aop_copy_registry.json',
];

// Hosts whose responses are third-party raster basemap tiles.
const TILE_HOSTS = [
  'tnmap.tn.gov',
  's3.amazonaws.com',
  'gis.apfo.usda.gov',
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const shell = await caches.open(SHELL_CACHE);
    await shell.addAll(SHELL_ASSETS); // fail-hard: shell must be complete

    // Best-effort warm the data cache. Never throws, so install always succeeds.
    const data = await caches.open(DATA_CACHE);
    await Promise.allSettled(
      DATA_ASSETS.map(async (url) => {
        const res = await fetch(url, { cache: 'reload' });
        if (res.ok) await data.put(url, res.clone());
      })
    );

    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keep = new Set([SHELL_CACHE, DATA_CACHE, TILE_CACHE]);
    const names = await caches.keys();
    await Promise.all(names.map((n) => (keep.has(n) ? null : caches.delete(n))));
    await self.clients.claim();
  })());
});

// Keep a cache from growing without bound: trim oldest entries (Cache API returns
// keys in insertion order) down to max.
async function trimCache(cacheName, max) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  if (keys.length <= max) return;
  for (let i = 0; i < keys.length - max; i++) {
    await cache.delete(keys[i]);
  }
}

async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await fetch(request);
  // status===200, not res.ok: a 206 Partial Content passes res.ok but throws on
  // Cache.put. No ranged request reaches here today, but guard against it.
  if (res && res.status === 200) cache.put(request, res.clone());
  return res;
}

async function cacheFirstTile(request) {
  const cache = await caches.open(TILE_CACHE);
  const hit = await cache.match(request);
  if (hit) return hit;
  const res = await fetch(request);
  // Tile servers may return opaque (CORS-less) responses; cache those too —
  // MapLibre still renders them. Only skip genuine error statuses we can see.
  if (res && (res.ok || res.type === 'opaque')) {
    await cache.put(request, res.clone());
    trimCache(TILE_CACHE, TILE_CACHE_MAX); // fire-and-forget
  }
  return res;
}

// Stale-while-revalidate: answer from cache immediately, refresh in the background.
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const hit = await cache.match(request);
  const network = fetch(request)
    .then((res) => {
      if (res && res.status === 200) cache.put(request, res.clone());
      return res;
    })
    .catch(() => null);
  return hit || (await network) || Response.error();
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const sameOrigin = url.origin === self.location.origin;

  // App opens offline: serve the cached shell for navigations.
  if (request.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const res = await fetch(request);
        // Refresh the cached shell so the offline fallback isn't frozen at the
        // last VERSION bump (stale-while-revalidate for the app shell).
        if (res && res.status === 200) {
          const cache = await caches.open(SHELL_CACHE);
          cache.put('./index.html', res.clone());
        }
        return res;
      } catch (_) {
        const cache = await caches.open(SHELL_CACHE);
        return (await cache.match('./index.html')) || (await cache.match('./')) || Response.error();
      }
    })());
    return;
  }

  if (sameOrigin) {
    // Copy + event schedule self-heal between bumps (see SWR_SUFFIXES).
    if (SWR_SUFFIXES.some((s) => url.pathname.endsWith(s))) {
      event.respondWith(staleWhileRevalidate(request, DATA_CACHE));
      return;
    }
    if (url.pathname.includes('/data/')) {
      event.respondWith(cacheFirst(request, DATA_CACHE));
      return;
    }
    if (url.pathname.endsWith('.html')) {
      event.respondWith(staleWhileRevalidate(request, SHELL_CACHE));
      return;
    }
    // App shell code split out of index.html (./css/, ./js/). Stale-while-
    // revalidate like the HTML shell so edits reach installed users on the next
    // reload even if a VERSION bump is missed; precached in SHELL_ASSETS too.
    if (url.pathname.includes('/css/') || url.pathname.includes('/js/')) {
      event.respondWith(staleWhileRevalidate(request, SHELL_CACHE));
      return;
    }
    if (url.pathname.includes('/vendor/') || url.pathname.includes('/icons/') ||
        url.pathname.endsWith('/manifest.json')) {
      event.respondWith(cacheFirst(request, SHELL_CACHE));
      return;
    }
    return; // anything else same-origin: default network
  }

  // Third-party raster basemap tiles: best-effort offline.
  if (TILE_HOSTS.includes(url.hostname)) {
    event.respondWith(cacheFirstTile(request));
    return;
  }
  // All other cross-origin requests: leave to the network.
});
