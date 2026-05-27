# Park Bounds Icon Apply

Sprint 03 produced the review artifact. Sprint 04 picks one boundary-derived
icon and wires it into the Park zoom button.

#aop #04_event_app #viewer #icons #park_bounds

-----

## Source

- `../03_event_app/_done/park_bounds_icon_review.md`
- `../../../website/park_bounds_icon_review.html`
- `../../../website/index.html`
- `../../../website/data/publish.geojson`

## Work

- [ ] Pick one variant by code, `PB1` through `PB9`.
- [ ] Confirm the chosen icon reads at 22 x 22 px on cream, moss-active, and dark control contexts.
- [ ] Confirm it is distinguishable from Region zoom, Pavilion zoom, and the Park-style map preset.
- [ ] Replace only the inline SVG inside `#zoomPark`.
- [ ] Keep camera, preset, localStorage, and MapLibre behavior unchanged.

## Verification

- [ ] Smoke the left control row at desktop width.
- [ ] Smoke the left control row at mobile width.
- [ ] Confirm `website/park_bounds_icon_review.html` still documents the choice.
