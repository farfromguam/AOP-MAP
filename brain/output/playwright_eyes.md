# Playwright verification notes

Date: 2026-05-20

## What was checked
- Loaded the MVP static website at `http://localhost:8000` using Playwright.
- Verified the page title loaded: `AOP Map Viewer`.
- Confirmed the page message changed to `Publish layer loaded. Use the toggles to show/hide features.`
- Confirmed the MapLibre canvas was rendered (`.maplibregl-canvas` exists).

## Issue found
- The site was previously relying on external CDN assets for MapLibre:
  - `https://unpkg.com/maplibre-gl@2.18.1/dist/maplibre-gl.css`
  - `https://unpkg.com/maplibre-gl@2.18.1/dist/maplibre-gl.js`
  - `https://demotiles.maplibre.org/style.json`
- In the automated browser environment, the CDN asset requests were blocked and the map never initialized.

## Fix applied
- Added local vendor assets:
  - `website/vendor/maplibre-gl.js`
  - `website/vendor/maplibre-gl.css`
- Updated `website/index.html` to use those local assets.
- Changed the map style to an inline local style with a simple background layer so the page no longer depends on external tile service URLs.

## Evidence
- Screenshot saved at `brain/output/playwright_homepage_after_fix.png`

## Recommendation
- Replace the demo sample publish data with real AOP map data next.
- Keep the website self-contained for local MVP previews, at least until the external tile and CDN workflows are proven.
