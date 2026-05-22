# Visitor context callouts

Started: 2026-05-21
Status: DONE (2026-05-21)

Add a couple of physical map callout areas that tell a rider where the nearest
support towns are: food, fuel, hotels, camping/lodging context, and rough drive
time.

#aop #viewer #visitor-context #callouts #support-towns

-----

## Why now

The user asked for map-marker areas physically on the map: circles with text
like "south to the city 5 miles" and "north to town X minutes," including
places to eat, sleep, and similar support context.

This is not trail data. It is cartographic visitor context, so it belongs in a
separate raw/reference GeoJSON layer and should not be promoted as an official
facility or routing claim.

## Research used

- AOP official pages confirm the office/check-in address at `1040 Ellis Cove Rd`
  and on-site rental/camping context. The bunkhouse pages also confirm AOP
  on-site sleeping options and office contact.
- RiderPlanet gives the useful access-road shape: I-24 Exit 152B -> US-72 ->
  Battle Creek Road -> Fish Trap Road -> Ellis Road -> Ellis Cove Road. It also
  lists gasoline/diesel/convenience store services 1-5 miles southeast and
  on-site water/RV/camping amenities.
- Marion County Tourism lists South Pittsburg and Kimball restaurants/hotels,
  and also Monteagle restaurants/lodging.
- Distance-Cities lists South Pittsburg to Monteagle at about 21 driving miles
  / 22 minutes. The AOP-to-Monteagle label rounds that up to about 30 minutes
  because the park adds the Ellis Cove Road approach.

Sources are embedded in `website/data/aop_visitor_context_callouts.geojson`.

## What was added

- `website/data/aop_visitor_context_callouts.geojson`
  - `South Pittsburg / Kimball supply run`: southeast support corridor, `5-8 mi`
    / `10-15 min`, food/fuel/hotels.
  - `Monteagle plateau services`: north/northwest support option, `~30 min`,
    lodging/restaurants/I-24.
- `website/index.html`
  - Toggle: `Visitor context callouts`, default ON.
  - Layers: `visitor-context-fill`, `visitor-context-outline`,
    `visitor-context-labels`.
  - Popups with direction, services, examples, distance/drive-time notes, and
    source summary.
  - Popup links: `Directions`, `Food`, `Lodging`, and `Source`. Directions use
    Google Maps routing from the AOP office address; Food/Lodging point to
    Marion County Tourism lists.
  - Search indexing, so "Monteagle" or "South Pittsburg" jumps to the relevant
    circle and turns the layer back on if hidden.
  - Included in presets: Park and Topo show the callouts; Trace hides them.
- `mvp/scripts/playwright_verify_visitor_context.py`
  - Verifies the toggle, layer visibility, GeoJSON source manifest, label text,
    rendered circles, and search jump.

## Acceptance

- [x] Two physical callout circle areas are on the map.
- [x] Each circle has useful visitor support text, not just a generic marker.
- [x] The layer is toggleable and searchable.
- [x] Popups carry source/estimate notes so rough drive times do not look like
  official routing data.
- [x] Popups have useful links for directions, food, lodging, and source checks.
- [x] Viewer catalog updated.
- [x] Playwright verification added and passing.

## Verification

- `node -e "JSON.parse(require('fs').readFileSync('website/data/aop_visitor_context_callouts.geojson'))"`
- `WEBSITE_URL=http://localhost:8000/ python3 mvp/scripts/playwright_verify_visitor_context.py`
