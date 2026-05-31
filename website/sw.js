/* AOP Map service worker.
 *
 * Three caches, three strategies:
 *   - shell  (cache-first)            app code + icons. Precached on install; the
 *                                     app opens with no network once installed.
 *   - data   (cache-first)            local GeoJSON/JSON/WebP under ./data/.
 *                                     Best-effort precached on install so a single
 *                                     online "install + open" warms every layer for
 *                                     the field; anything missed is cached on first view.
 *   - tiles  (cache-first, capped)    third-party raster basemaps (TNMap satellite,
 *                                     AWS terrain, USDA NAIP). Best-effort: a tile is
 *                                     only available offline if it was viewed online.
 *                                     Capped by entry count so it can't crowd out the app.
 *
 * Exception: ./data/aop_event_schedule.json is stale-while-revalidate — it shows
 * instantly from cache but refreshes whenever there is signal, so installed users
 * don't get stuck on a stale event timetable.
 *
 * Bump VERSION to invalidate the shell + data caches on the next deploy. The tile
 * cache is intentionally version-independent — tiles never change, so re-downloading
 * them on every release would waste the user's data.
 */

const VERSION = 'v14'; // keep in sync with #appVersion in index.html
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
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-maskable-512.png',
  './icons/apple-touch-icon.png',
];

// Local data — best-effort precache. A 404 or rename here must NOT break install,
// so these are fetched with allSettled rather than addAll. Whatever isn't here
// (or fails) still gets cached the first time the app fetches it online.
const DATA_ASSETS = [
  './data/publish.geojson',
  './data/aop_poi_index.json',
  './data/aop_trail_catalog.json',
  './data/aop_trail_network.geojson',
  './data/aop_roads.geojson',
  './data/aop_water.geojson',
  './data/aop_buildings.geojson',
  './data/aop_cemeteries.geojson',
  './data/aop_contours.geojson',
  './data/aop_landcover.geojson',
  './data/aop_landcover_9patch.geojson',
  './data/aop_9_patch.geojson',
  './data/aop_lidar_tiles.geojson',
  './data/aop_activity_hotspots.geojson',
  './data/aop_synthetic_activity_hotspots.geojson',
  './data/aop_synthetic_activity_tracks.geojson',
  './data/aop_synthetic_activity_report.json',
  './data/aop_visitor_context_callouts.geojson',
  './data/aop_brand_logos.geojson',
  './data/aop_editor_seed_pois.geojson',
  './data/aop_event_schedule.json',
  './data/osm_aop_9patch.geojson',
  './data/osm_aop_named.geojson',
  './data/sfwda_aop_trail_map.webp',
  './data/sfwda_raster_alignment.json',
  './data/sfwda_traced_trails.geojson',
  './data/sfwda_traced_markers.geojson',
  './data/sfwda_numbered_trails.geojson',
  './data/sfwda_trails_edited.geojson',
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
  if (res && res.ok) cache.put(request, res.clone());
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
      if (res && res.ok) cache.put(request, res.clone());
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
        return await fetch(request);
      } catch (_) {
        const cache = await caches.open(SHELL_CACHE);
        return (await cache.match('./index.html')) || (await cache.match('./')) || Response.error();
      }
    })());
    return;
  }

  if (sameOrigin) {
    // Event schedule is the one thing a visitor wants fresh.
    if (url.pathname.endsWith('/data/aop_event_schedule.json')) {
      event.respondWith(staleWhileRevalidate(request, DATA_CACHE));
      return;
    }
    if (url.pathname.includes('/data/')) {
      event.respondWith(cacheFirst(request, DATA_CACHE));
      return;
    }
    if (url.pathname.includes('/vendor/') || url.pathname.includes('/icons/') ||
        url.pathname.endsWith('/manifest.json') || url.pathname.endsWith('.html')) {
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
