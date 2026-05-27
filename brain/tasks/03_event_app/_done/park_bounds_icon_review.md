# Park Bounds Zoom Icon

Pick a low-poly park-boundary icon for the Park zoom button.

The review page explores inline SVG candidates derived from the real
`park_boundaries` GeoJSON silhouette. The app does not change until a winner
is chosen.

-----

## Source

- User request, 2026-05-27: make a low-poly park bounds icon for the park
  boundary preset zoom level; put versions in a review HTML file; do not
  change the app yet.
- User correction, 2026-05-27: the baseline looked like a blob; use the park
  bounds from GeoJSON as the icon source, then make it low-poly.
- User direction, 2026-05-27: remove interior decorations, rotate every icon
  90 degrees clockwise, and mark the pavilion with a dot.
- `../../../website/index.html` - current `#zoomPark` button in the
  Region / Park / Pavilion zoom group.
- `../../../website/data/publish.geojson` - source feature
  `layer=park_boundaries`, id `2`.
- `../../../website/button_icon_picker.html` - earlier control-row icon
  review artifact.

## Scope

- Create `../../../website/park_bounds_icon_review.html`.
- Compare several real-boundary icon variants in the real 22 x 22 px pill-bar
  slot.
- Keep icons inline-SVG friendly: `viewBox="0 0 22 22"`, `currentColor`,
  no raster assets, no runtime dependency.
- Normalize the GeoJSON boundary into icon space and simplify it into
  low-poly silhouettes.
- Rotate the boundary silhouette 90 degrees clockwise in icon space.
- Remove interior decoration. The only interior mark is the pavilion dot,
  sourced from the app's pavilion camera coordinate.
- After selection, replace only the SVG inside `#zoomPark`.

## Out of Scope

- No `website/index.html` change in this pass.
- No camera, preset, localStorage, or MapLibre behavior changes.
- No new app icon system until this one icon proves the direction.

## Acceptance

[ ] User chooses one variant by code (`PB1` through `PB9`).
[ ] Chosen SVG reads on cream, moss active, and dark control contexts.
[ ] Chosen SVG is distinguishable from Region zoom, Pavilion zoom, and the
    Park-style map preset.
[ ] App follow-up replaces only the `#zoomPark` icon markup.

## Verification

[X] Review artifact exists at `website/park_bounds_icon_review.html`.
[X] Live viewer left untouched for this pass.
[ ] Future app card: apply chosen SVG to `website/index.html`.
[ ] Future app card: smoke the left control row at desktop and mobile widths.
