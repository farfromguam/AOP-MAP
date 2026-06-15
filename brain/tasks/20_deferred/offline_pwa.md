# Offline & PWA

Reduce site weight, cache aggressively, and turn the static viewer into an installable progressive web app so the field-use promise in `../../northstar/map_northstar.md` survives contact with a no-signal trail.

-----

## Deferred because

The active sprint (`../_done/02_edit/_readme.md`) is going to add tagged POIs, possibly more named-feature layers, and shift several layers from default-off to default-on. Each of those changes the bytes-on-first-load number. One measurement against a stable surface beats one measurement per layer added.

## Source

- `../_done/02_edit/tasks.md` items: "figure out how much data the site takes" through "progressive web app???"
- `../../northstar/map_northstar.md` — offline / field-use promise.
- Standing constraint: prefer pre-baked static assets (GeoJSON, PMTiles, locally cached raster tiles) over live tile/feature services. The satellite basemap (TNMap) and hillshade / 3D terrain (AWS Terrarium) are still live-network and do not yet satisfy offline — caching or baking those rasters is part of the scope below.

## Phases

1. **Measure.** DevTools Network panel + bundle inventory of `website/data/`. Produce a baseline: bytes-on-first-load, bytes-on-cache-hit, by-layer breakdown. Identify the top three offenders before touching the long tail.
2. **Reduce.** Tile pyramids for rasters, PMTiles for large vectors, image optimization on PNG/JPEG. Target the top three first.
3. **Cache.** Service worker for tile + JSON caching. Strategy needs to distinguish "rarely changes" (basemap, FEMA buildings) from "may change weekly" (event schedule, POIs).
4. **Install.** PWA manifest. Installable from mobile browser. Define a freshness / refresh story so an installed app doesn't silently show stale event data.

## Open Questions

### 1. Tile format for the rasters?

**Suggested:** PMTiles where the source license allows it; XYZ passthrough for public services that ban repackaging.

**Why:** PMTiles is the single-file offline path; some upstream tile services (TNMap, USDA NAIP) forbid local mirroring without permission. The license check is non-negotiable.

### 2. Service-worker strategy?

**Suggested:** Cache-first for raster tiles + static GeoJSON; stale-while-revalidate for the event schedule JSON.

**Why:** Tiles never change once published; the schedule is the only piece a visitor wants fresh.

## Out of Scope

- Native mobile apps. PWA is the ceiling for this sprint family.
- Offline editing / write-back. The editor stays online-only until the read story is solid.

## Acceptance

[ ] Baseline measurement recorded in this card.
[ ] First-load size reduced below an agreed target (target set once baseline is in).
[ ] Service worker caches tile + JSON; verified by loading the site, going offline, and reloading.
[ ] Site installable as a PWA on mobile.
[ ] Freshness story documented so installed users know what's stale.

## Verification

- DevTools → Network → "disable cache" + reload → record total transferred.
- Reload with cache → record transferred.
- Application → Service Workers → confirm registered.
- Airplane mode → reload → site renders with last-cached data.
- Install prompt fires on a fresh mobile profile.
