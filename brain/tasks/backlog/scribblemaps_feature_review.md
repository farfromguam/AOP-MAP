# Scribblemaps Parks & Rec Feature Review

Pulled feature ideas from the Scribblemaps parks-and-recreation industry page so we can see what a commercial "draw on a satellite map" tool ships, and decide which ones our map should chase, defer, or skip.

Most of these are not new ideas. Scribblemaps just packages them. The point of this card is to name the ones worth carrying into the AOP backlog, and the ones we should consciously reject so we don't drift into building a generic park-map tool.

-----

## Source

- https://www.scribblemaps.com/industries/parks-recreation -- vendor marketing page, captured 2026-05-20.
- `../../northstar/map_northstar.md` -- the V1/V2 line we are measuring against.
- `../01_mvp/aop_south_pittsburg_map_build_card.md` -- the current build card.

This is competitor reading, not a customer brief. Treat features as prompts, not requirements.


## How to read the fit tags

Each idea gets one tag:

- **V1 fit** -- already on the build card or a clean addition to print V1 / website V1.
- **V2 fit** -- belongs in the submission / collaboration phase, not before the validation loop proves itself.
- **Internal fit** -- useful for AOP staff / QGIS workflow, not for the public map.
- **Out** -- doesn't match the northstar. Recorded so we remember the decision.


## Drawing and markup

### Custom markers for trailheads, amenities, staging, signage
**Fit:** V1 fit. Build card already names trailheads/staging and print annotation layers. Confirm the icon set covers gate, parking, kiosk, staging, signage, hazard, water, restroom.

### Hazard / wash-out / blowdown / maintenance pin layer
**Fit:** V1 fit, with a caveat. The build card has a hazard/obstacle layer. Treat hazard pins like observations -- raw until reviewed -- so an "obstacle here" mark doesn't auto-publish a closure that isn't real.

### Event footprint overlays (courses, gates, registration, staging, parking)
**Fit:** V1 fit. Earlier draft of this card had this as Out under the wrong assumption that AOP doesn't host events. AOP hosts RC crawling events -- G6-style stage rallies, Pro-Line By The Fire-style multi-day adventures, and gate-based comp courses. The print board and public viewer both need an event-overlay layer. See `./rc_event_mapping_backlog.md` for the full shape.

### Highlight / fill polygons inside the park (zones)
**Fit:** V1 fit. Useful for sectors, staging, closure zones, and print legend regions. QGIS already does this; the work is naming the zone vocabulary so it stays consistent on the print board.


## Base maps and imagery

### Satellite / street / terrain / hybrid switchers on the public viewer
**Fit:** V1 fit. The static MapLibre viewer can ship two or three base styles. Decide which raster sources are license-clean for public display before adding the switcher -- this is the same decision the build card flags for hillshade/topo.

### Image overlay for historical or proposed plans
**Fit:** Internal fit. Georeferenced raster overlay of any historical AOP plan, owner sketch, or proposed-trail diagram belongs in QGIS as a reference layer. Not for public publish until permission is explicit.


## Layer and data management

### Toggle layers on/off
**Fit:** V1 fit. Already on the build card under Website V1.

### Color-coding by difficulty, use, or status
**Fit:** V1 fit. Already on the build card. The work is settling the legend vocabulary before print V1, not adding a feature.

### Multi-format import: GPX, KML, Shapefile, GeoJSON, CSV
**Fit:** Internal fit. The PostGIS spine + QGIS gives us this; we don't need user-facing import UI. Worth a small backlog card to document the canonical ingest path so volunteer GPX files end up in `raw` with provenance instead of pasted into `core`.

### GPS tracks from rangers, contractors, volunteers
**Fit:** V2 fit. This is the observation intake question. Don't build a track-ingest pipeline until the whiteboard loop tells us what people actually contribute and at what rate.


## Measurement and analysis

### Trail distance and area on the public viewer
**Fit:** V1 fit (small). A measure-distance tool in the static MapLibre viewer is cheap and visibly useful. Skip area for V1 unless someone asks.

### Elevation profile with optional calorie estimate
**Fit:** V2 candidate. Elevation profile is a real ask for off-road / hiking / trail-running maps. Calorie estimate is consumer-app fluff and should stay off the AOP map.


## Sharing and embedding

### Shareable visitor link to the map
**Fit:** V1 fit. The static MapLibre site already gives us shareable URLs. The backlog work is deciding whether deep-link parameters (`?trail=foo&zoom=...`) are worth adding.

### Embed on AOP / partner websites
**Fit:** V1 fit (small). An iframe-embeddable build is almost free once the static viewer exists. Worth a small backlog card to confirm CORS and frame-ancestors policy.

### View-only vs edit permissions on shared links
**Fit:** V2 fit. Public reads, no public writes. Don't build link-based editing.


## Mobile and access

### Mobile-browser-friendly viewer
**Fit:** V1 fit. The MapLibre viewer should be responsive from day one. Treat this as a Website V1 acceptance criterion, not a separate feature.

### "Works in the park without a download"
**Fit:** V2 candidate. The honest version is offline PMTiles with cached glyphs and sprites so a phone keeps the map alive in a cell-dead canyon. Real value, real work. Park it until the V1 publish path exists.


## Export and print

### PDF / PNG / KML / GeoJSON export
**Fit:** V1 fit. Already on the build card. The backlog item is making sure all four come out of the same publish view, not from separate hand-curated files.

### Kiosk / printed-guide display
**Fit:** V1 fit. Print V1 is the build card's deliverable. Kiosk display is the same artifact mounted differently, so the backlog item is "make the print PDF readable at kiosk distances" -- type sizes, contrast, legend prominence.


## AI features

### Natural-language map commands ("draw a 500m buffer", "color this CSV")
**Fit:** Out for V1. Cute demo, no place on a trustworthy map yet. Revisit when the data is settled and the question becomes "make routine cartography faster," not "skip the routine entirely."


## Collaboration

### Shared maps for teams, link-based edit access
**Fit:** V2 fit. Same answer as GPS track ingest. Don't build collaboration plumbing before the loop proves what gets contributed.

### Volunteer work-day coordination
**Fit:** Out. That is a workflow product, not a map product. Hand it off to a calendar or work-order tool when the need is real.


## Use cases worth keeping on the radar

### Visitor map / trail guide
**Fit:** V1 fit. This is the print + website combo. Already the build card.

### Trail maintenance work plan
**Fit:** Internal fit. The hazard + observation layers already cover this if we keep `needs_field_check` as a real status and respect it on the next print pass.

### Proposed-improvements documentation
**Fit:** V2 fit. Trails-in-consideration belong as observations with a distinct status, not as published trails. Wait for the loop.

### Advocacy / fundraising map
**Fit:** Out. Not AOP's posture; this is a friends-of-the-park use case.


## Things this review intentionally did not turn into work

- A "Scribblemaps clone" surface. We are not building a generic map drawing tool.
- A login system. V1 has no accounts. V2 will, when the loop earns it.
- A generic events module. AOP hosts RC events, but the map's job is to draw event courses, gates, and staging on the same data spine -- not to be an event ticketing or registration platform. See `./rc_event_mapping_backlog.md`.
- Calorie counters. The map is not a fitness tracker.


## What to do with this card

- Treat each **V1 fit** item as a candidate small addition to the active build card, not as a separate phase.
- Treat each **V2 fit** item as a deferred decision; do not start work without the validation loop result behind it.
- Treat each **Internal fit** item as a QGIS / staff workflow note, not a public feature.
- Leave the **Out** items in place. The record is the value.
