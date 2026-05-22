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

## Update: Chattanooga regional anchor + per-town deep links (2026-05-21)

The user asked for the SE callout to carry a distance to Chattanooga on the
circle (not the popup) to orient riders to the region, and flagged that the
`Food` links for both callouts opened the same page top.

- The SE `South Pittsburg / Kimball` label gained a fourth line on the circle:
  `Chattanooga metro ~35 mi | ~45 min`. Distance-Cities lists South Pittsburg
  to Chattanooga at 30 driving miles / ~35 min via I-24; the ~35 mi / ~45 min
  figure rounds that plus the Ellis Cove Road park approach. Added the
  Distance-Cities South Pittsburg-to-Chattanooga source to `_sources_checked`
  and noted the provenance in the SE feature's `distance_note` / `services` /
  `examples` / `source_summary` so the popup detail stays honest.
- `Food` and `Lodging` links now deep-link per town with a `#:~:text=` browser
  text fragment. The Marion County Tourism restaurants/hotels pages group
  listings under town headings but expose no anchor ids, so a text fragment is
  the only way to scroll to a town on a page we do not control. The SE callout
  covers both of its towns with a two-fragment directive (Kimball is the I-24
  interchange town and close enough to belong on the same circle): food ->
  `#:~:text=South%20Pittsburg&text=Kimball`, lodging ->
  `#:~:text=Kimball&text=South%20Pittsburg` (lodging scrolls to the Kimball
  hotel cluster first). Monteagle callout -> `#:~:text=Monteagle`. On a browser
  without text-fragment support the link still opens the correct page.
- `mvp/scripts/playwright_verify_visitor_context.py` gained checks for the
  Chattanooga anchor line, for the food/lodging links being distinct and
  text-fragment-deep-linked, and for the SE links covering both towns. Its
  Chromium launch now passes `--enable-unsafe-swiftshader` and its
  `wait_for_function` calls use timer polling, so the run survives a GPU-less
  headless host (software WebGL starves the default rAF poll). Full run: 25/25
  PASS, 0 console errors.
- Catalog `research/viewer.md` ("Visitor Context Callouts") updated.
