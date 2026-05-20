# AOP Map MVP - Static Site

This directory contains a starter static MapLibre viewer for publishable AOP map layers.

## How to preview

Serve the directory from a local web server:

```bash
cd website
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

The viewer fetches `data/publish.geojson`, so direct `file://` preview is not the preferred path.

## Data

The viewer looks for a local GeoJSON file at:

- `website/data/publish.geojson`

The file should contain a GeoJSON FeatureCollection with publishable features.

## Local setup

This viewer now uses local vendor MapLibre assets in `website/vendor/`, so it can run as a local preview without relying on the CDN for the map runtime.

## Layers

The viewer currently renders:
- publishable boundaries as light blue fills with blue outlines
- publishable trails as orange lines
- publishable trailheads as green dots

## Next step

Load verified AOP trail and trailhead data into PostGIS, then export the publish views again.
