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

Publishable layers, from `data/publish.geojson`:
- boundaries as light blue fills with blue outlines
- trails as orange lines
- trailheads as green dots

Reference and context layers, toggled from the panel (off by default unless noted):
- 3D terrain and lidar hillshade (AWS Terrain Tiles / USGS 3DEP)
- lidar 5 ft contours (USGS 3DEP 1 m DEM)
- TNMap 2022 satellite imagery
- 9-patch acquisition AOI and the USGS 3DEP lidar tile index
- asphalt roads (USGS National Map; on by default)
- streams, waterbodies, springs, and gages (USGS NHD)
- community OSM layers: park polygon, tracks, service roads, named landmarks
- SFWDA 2015 paper trail map, with an in-viewer alignment editor

## Next step

Load verified AOP trail and trailhead data into PostGIS, then export the publish views again.
