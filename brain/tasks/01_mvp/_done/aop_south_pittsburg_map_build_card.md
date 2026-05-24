# AOP South Pittsburg Map Build Card

Build the AOP map on one durable spine: PostGIS for living data, QGIS for cartography and print, MapLibre/PMTiles for the website, and Phoenix only when submissions become worth building.

The first version should be a serious map, not a community app. Print the wall map, publish the read-only web map, use real-world markup to learn what people actually contribute, then build intake around that pattern.

-----

## Source

- `../research/aop_south_pittsburg_sources.md` -- source stack, open questions, first QGIS pass.


## Stack

**Chosen:** PostGIS + QGIS + MapLibre + PMTiles + Cloudflare + Phoenix + R2/S3.

PostGIS is the source of truth once this becomes more than a one-person GIS file. QGIS reads from it for editing, styling, georeferencing, print layout, SVG/PDF export, and geospatial PDF output. The website reads published exports from the same data. V2 submissions write observations back into the same database.

GeoPackage still matters, but not as the long-term spine. Use it for snapshots, field packets, backup, offline work, and handoff.


## Staged Work

### 1. Data Spine

Create the living map database and the layer schema.

Deliverables:
- PostGIS database with baseline spatial extensions enabled.
- Layer tables for park boundary candidates, parcels, trail centerlines, trail observations, trailheads/staging, hazards/obstacles, drainage, contours, source register, and print annotations.
- Core fields for `source`, `confidence`, `permission`, `status`, `last_verified`, and `notes`.
- Export scripts for GeoJSON, PMTiles-ready data, and GeoPackage snapshots.

Done means the map can be edited in QGIS without inventing schema as we go.


### 2. Base Map Assembly

Build the first usable GIS map.

Deliverables:
- QGIS project connected to PostGIS.
- TNMap imagery, USGS topo, parcel data, DEM hillshade, slope, contours, and hydro/drainage layers.
- Candidate park boundary from Comptroller parcels, with the 600+ acre mismatch called out instead of papered over.
- 9-patch data acquisition AOI around the current two-parcel working envelope for satellite/orthoimagery, topo, DEM, and lidar pulls.
- Trail candidates from official material, SFWDA, RiderPlanet/app checks, imagery, hillshade, and field GPX when available.
- Source-confidence styling so unverified data is visibly unverified.

Done means we can point at the map and explain what every line claims, where it came from, and how much we trust it.


### 3. Print V1

Make the large-format map people can mark up.

Deliverables:
- Large-format QGIS print layout.
- Coordinate grid and sector labels.
- Trail candidate IDs.
- Difficulty and confidence legend.
- Version/date stamp.
- QR code to the web map.
- Registration marks so board photos can be lined back up to the GIS map.
- Exported PDF, geospatial PDF, and SVG/layer exports for layout software.

Done means we can print on laminated/whiteboard material and use the board as a real validation surface.


### 4. Website V1

Publish the same map as a read-only web viewer.

Deliverables:
- Static MapLibre site.
- Published trail, boundary, parcel, and observation layers.
- Layer toggles for difficulty, confidence, parcels, hillshade/topo, and candidate/validated trails.
- Click details showing trail name, difficulty, source, confidence, and verification status.
- Download links for the current print PDF and source notes where appropriate.

Done means someone can scan the wall-map QR code and inspect the current map without needing a GIS tool.


### 5. Whiteboard Validation Loop

Use the printed board before building intake software.

Deliverables:
- Marker/sticker legend for new trail, correction, obstacle, closure, difficulty change, landmark, and question.
- Board-photo capture process after each review session.
- Transcription pass into a PostGIS `observations` layer.
- Review status values: `raw`, `reviewed`, `verified`, `rejected`, `needs_field_check`.
- Next-print process that incorporates verified changes and leaves unresolved ones visible.

Done means the wall map becomes a repeatable data collection workflow, not a one-time artifact.


### 6. Website V2

Only build this once the validation loop proves the contribution pattern.

Deliverables:
- Phoenix/LiveView submission and admin app.
- Phone GPS capture with `lat`, `lng`, `accuracy_m`, timestamp, and optional heading.
- Image upload to R2/S3 with thumbnail generation.
- Observation form for note, trail name, type, difficulty, and closure/hazard fields.
- Invite-code or account-based contributor access.
- Moderation queue that promotes observations into verified map layers.
- Export path back to QGIS/PMTiles/GeoJSON.

Done means public or semi-public contributors can submit useful field observations without polluting the map.


## Implementation Notes

Start with the source ledger, not the trails.

The risky part is not drawing lines. The risky part is knowing which lines are publishable, which are inspection-only, and which are guesses wearing a nicer hat. Every imported or hand-drawn feature needs a source row behind it, with permission status carried all the way to export.

Use three data zones:
- `raw` for imported parcels, GPX, raster-derived traces, and reference captures.
- `core` for the edited working map.
- `publish` for views or exports that are explicitly safe for print and web.

Keep `source` relational. One trail can come from the official map, an app trace, imagery, hillshade, and a board correction. A scalar `source` field will collapse exactly the thing the map needs to preserve. Use a source register plus feature-source links where the provenance matters.

Set the coordinate rule early. A practical default: store working vector geometry in `EPSG:4326` for GPS/web interchange, keep source CRS metadata on import, and use projected views or QGIS project settings for length/area work. Do not let exports silently define the CRS policy.

Treat observations as observations. Board marks, app checks, GPX rides, and user submissions should not overwrite trail centerlines directly. They feed a review queue that promotes changes into the verified trail layer.

Website V1 has one extra decision the card should not hide: PMTiles covers the publishable vector overlays, but hillshade/topo imagery needs its own raster strategy. For V1, either use allowed public tile services directly or publish only derived/static rasters that the license permits. Commercial basemaps stay inspection-only unless their terms say otherwise.

Phoenix is future stack, not V1 stack. The V1 website should be static unless the validation loop proves a real intake workflow.


## First Implementation Pass

1. Create the PostGIS database with `raw`, `core`, and `publish` schemas.
2. Add source register tables before any map feature tables.
3. Load the AOP AOI, Marion County parcels, TNMap imagery reference, USGS topo reference, DEM, hillshade, slope, contours, and drainage.
4. Resolve the parcel / acreage mismatch enough to draw a clearly labeled working envelope.
5. Create the 9-patch data acquisition bounds around the working envelope; use it for raster/terrain context, while keeping trails inside the park working envelope.
6. Add empty candidate trail, observation, hazard, trailhead, and print annotation layers.
7. Wire QGIS styles around confidence, status, and permission.
8. Export `publish` views to GeoJSON / PMTiles input, plus a GeoPackage snapshot.
9. Build the first print layout before the static web viewer, because the whiteboard loop is the data product.


## Out of Scope For V1

- Public photo submissions.
- Login, accounts, or contributor roles.
- Automated trail routing.
- Treating app-exported trails as authoritative.
- Legal boundary claims beyond parcel-reference context.
- Publishing anything that licensing or AOP permission does not allow.


## Open Questions

### 1. Do we start PostGIS immediately?

**Suggested:** Yes.

**Why:** The work already points toward a website and possible submissions. Starting with PostGIS avoids treating GeoPackage as canonical and then migrating when multi-user data arrives.

**Alternative:**
- **GeoPackage first:** simpler for a pure QGIS prototype, but it creates an avoidable handoff once submissions and review enter the picture.


### 2. Is V2 a custom web app or a field-tool workflow?

**Suggested:** Delay the decision.

**Why:** QField, Mergin Maps, or an Esri field stack may solve trusted field collection faster than custom software. A custom Phoenix app makes more sense if the goal is broad community intake, branded public contribution, or AOP-facing workflow control.

**Alternative:**
- **Build Phoenix immediately:** viable, but too early unless the wall-map loop proves we need that surface.


## Acceptance

[ ] Layer schema exists and can hold source, confidence, permission, and review status.
[ ] Source register exists and publish exports filter out unknown or disallowed source material.
[ ] QGIS project reads the authoritative data source.
[ ] Print V1 exports as large-format PDF and editable SVG/layer assets.
[ ] Website V1 displays the same layer model as the print map.
[ ] Wall-map validation loop produces transcribed observations.
[ ] V2 submission scope remains blocked until the contribution pattern is proven.


## Verification

- Open the QGIS project and confirm source layers are editable from PostGIS.
- Export a print PDF/SVG and inspect layer grouping in external layout software.
- Export web layers and load them in the MapLibre viewer.
- Run one board-markup session and verify the marks can be traced back into the observation layer.
