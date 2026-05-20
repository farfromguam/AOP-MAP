# AOP Map MVP - Static Site

This directory contains a starter static MapLibre viewer for publishable AOP map layers.

## How to preview

Open `website/index.html` in a browser, or serve the directory from a local web server.

## Data

The viewer looks for a local GeoJSON file at:

- `website/data/publish.geojson`

The file should contain a GeoJSON FeatureCollection with publishable features.

## Local setup

This viewer now uses local vendor MapLibre assets in `website/vendor/`, so it can run as a local preview without relying on the CDN for the map runtime.

## Layers

The viewer currently renders:
- publishable boundaries as blue lines
- publishable trails as orange lines
- publishable trailheads as green dots

## Next step

Replace `website/data/publish.geojson` with real exported publish-layer data from the PostGIS database, or extend the viewer to load PMTiles.
