# Community trails import into the viewer

Started: 2026-05-20

Pull the May 2026 `brain/import/community_trails/` material into the static viewer as toggleable layers, and wire an in-viewer alignment editor for the SFWDA paper map raster so it can be pixel-aligned against OSM trail/road vectors.

#aop #import #raster #osm #alignment #editor-is-the-viewer

-----

## Why now

`brain/import/community_trails/` has the first real community-sourced trail material:

- OSM 9-patch vectors (47 `highway=track`, 19 `service`, named landmarks, OSM-version park polygon).
- SFWDA 2015-03-11 AOP paper trail map raster.

The northstar says "build the map before the app", and the viewer is already standing up the AOP working envelope, satellite, hillshade, terrain, 9-patch grid, and lidar tile index. This card adds the next visible layers: the OSM community vectors and the SFWDA paper map.

The 2015 SFWDA raster is `high for shape, low for current trails`. It cannot be trusted as authority, but it is the only AOP-internal trail figure we have until the live `adventureoffroadpark.com` map is captured. Treat it as an alignment-reference layer so the next agent can spot which OSM tracks the paper map agrees with and where it diverges.

## What is being added

### New website data files

- `website/data/osm_aop_9patch.geojson` -- copy of `brain/import/community_trails/osm_aop_9patch.geojson`. 71 features.
- `website/data/osm_aop_named.geojson` -- copy of `brain/import/community_trails/osm_aop_9patch_named.geojson`. 5 named features.
- `website/data/sfwda_aop_trail_map.webp` -- copy of `brain/import/community_trails/sfwda_aop_trail_map_2015-03-11.webp` (smaller; PNG kept in import). Inspection-only per source license.
- `website/data/sfwda_raster_alignment.json` -- alignment sidecar. Carries `corners` (NW/NE/SE/SW), `orientation_cw_degrees`, and a `grid_NxN` field (currently `grid_6x6`, a 7x7 array of [lng, lat] control points). The viewer slices the rotated source raster into N x N image sources and binds each tile to its four control points, so dragging interior control points produces a nonlinear warp. Default corners = OSM AOP polygon corners; default rotation = `270`. Loader prefers `grid_${GRID_N}x${GRID_N}` exactly, falls back to upsampling any other `grid_KxK`, then to bilinear from `corners`. Refined by the in-viewer editor.

### New viewer layers in `website/index.html`

- `osm-tracks` (line, filter `highway=track`)
- `osm-service` (line, filter `highway=service`)
- `osm-park-polygon-outline` (line, filter `leisure=park` from OSM 9-patch)
- `osm-named-points` (circle + label, from named geojson)
- `sfwda-paper-map` (image source, controlled by the alignment sidecar)

Each layer is added behind a toggle in the side panel. Initial visibility for the new layers is OFF so the viewer still opens cleanly without surprises.

### Alignment editor (matches "editor is the viewer")

When `Edit SFWDA alignment` is toggled on:

- Four draggable corner markers appear at the current image corners (labeled NW, NE, SE, SW relative to the displayed quadrilateral, not the raster's pixel orientation).
- Dragging a marker recomputes the image source coordinates live.
- `90 CCW` / `90 CW` buttons rotate the raster within the quadrilateral by reshuffling which image pixel-corner is mapped to which compass corner. The current orientation is stored in `orientation_cw_degrees` (0/90/180/270).
- `Export alignment` downloads the current 4 corners + orientation as JSON; replace `website/data/sfwda_raster_alignment.json` to persist.
- `Reset` reverts to the JSON-loaded corners and orientation.

There is no backend write -- alignment is exported as a file the user/agent commits.

## Initial corner choice

The OSM `Adventure Off Road Park` polygon (way 1215497712) is a clean north-aligned rectangle:

- NW `-85.7601056, 35.0995096`
- NE `-85.7454715, 35.0989829`
- SE `-85.745686, 35.0835148`
- SW `-85.7599768, 35.0834094`

The SFWDA raster is `2500 x 1817` pixels and is landscape with the park footprint roughly centered. Using the OSM polygon as the initial image bounds will not pixel-align the trails -- it is only a starting placement so the alignment editor has something visible to drag.

The user explicitly asked to `pixel align the jpeg map` using `the trail info`. The OSM `highway=track`/`service` layers are the alignment reference. Expect the next session to drag the 4 corners until the SFWDA trail centerlines roughly overlap the OSM track vectors.

## Out of scope here

- True affine/projective georeferencing (would need GDAL or QGIS; tracked separately).
- Promoting any OSM track into `core.trail_centerlines`. Community OSM data stays in the import zone until provenance is recorded against `source_register`.
- Republishing the SFWDA raster. The raster is loaded locally for inspection only.

## Acceptance

- [ ] `website/data/osm_aop_9patch.geojson`, `osm_aop_named.geojson`, `sfwda_aop_trail_map.webp`, and `sfwda_raster_alignment.json` exist.
- [ ] The viewer panel has toggles for OSM tracks, OSM service roads, OSM park polygon, OSM named features, and the SFWDA paper map.
- [ ] Toggling the SFWDA paper map ON shows the 2015 raster on the map.
- [ ] `Edit SFWDA alignment` mode shows four draggable corners and updates the raster live.
- [ ] `Export alignment` produces a JSON file with the current 4 corners.
- [ ] The static viewer still opens cleanly with all new layers OFF by default (except the OSM park polygon outline, which is acceptable to ship visible).

## Provenance to record later

When promoting any of this beyond the viewer:

- `name`: `OSM Overpass 9-patch 2026-05-20`, `SFWDA AOP trail map 2015-03-11`.
- `source_type`: `community_geo`, `community_raster`.
- `license_or_permission`: ODbL for OSM; copyright AOP via SFWDA for the raster -- internal-only.
- `confidence_default`: per `brain/import/_readme.md` manifest.
