# Activity hotspots from user-entered trails

Started: 2026-05-22
Status: DONE (2026-05-22)

Turn timestamped user activity into a derived hotspot layer: places where a
track spends more time draw hotter. Keep it as raw activity evidence, not a
trail authority.

#aop #gpx #hotspots #activity #viewer #roadmap #source-register

-----

## Why now

The user asked to extract hotspots from a user-entered trail: "If we spend
longer time in one area its hotter."

The important split:

- **Drawn trail traces** in the viewer are geometry only. They have one created
  timestamp, not per-vertex times, so they cannot prove dwell.
- **Recorded GPX tracks** carry per-point timestamps. They can produce a real
  time-weighted heat layer.

So V1 uses the first-party Gaia GPX in `brain/import/Saturday_Afternoon_Activity.gpx`.
The output is internal/raw evidence. It does not promote any track into
`core.trail_centerlines` or `publish`.

## What shipped

- `mvp/scripts/build_activity_hotspots.py`
  - Pure-Python GPX parser and hotspot builder.
  - Reads timestamped trackpoints from one or more GPX files.
  - Respects GPX segment breaks; no heat is smeared across stopped recorder
    gaps between segments.
  - Builds 15 m time-weighted cells with 5 m / 20 s interpolation.
  - Splits dwell into `stop_seconds`, `slow_seconds`, and `moving_seconds`.
  - Caps any single interval's contribution at 600 s, and records
    `max_gap_seconds` / `capped_seconds` so suspicious heat stays visible.
- `website/data/aop_activity_hotspots.geojson`
  - Mixed FeatureCollection: one Polygon cell plus one centroid Point per hot
    cell.
  - Current output: 65 cells / 130 features from 368 GPX points and 2 GPX
    segments.
  - Properties include dwell, rank, intensity class, visit count, source file,
    confidence, permission, publish status, and review status.
- `website/index.html`
  - Toggle `Activity hotspots (GPX dwell)` under `Derived layers`, default OFF.
  - Renders a soft MapLibre heatmap from centroid points.
  - Renders auditable square hotspot cells from polygons.
  - Labels strongest cells with minutes.
  - Popup shows dwell, stopped/slow/moving split, visits, max point gap, source,
    and review status.
- `mvp/scripts/playwright_verify_activity_hotspots.py`
  - Verifies the toggle, hidden initial state, GeoJSON shape, render, popup, and
    console cleanliness.

## Synthetic Saturday stress test

Added 2026-05-23.

- `mvp/scripts/simulate_saturday_activity.py`
  - Deterministically generates many Saturday-afternoon RC activity tracks.
  - All tracks start at `#pavilion`.
  - Routes reuse the observed Saturday trail in `publish.geojson`, event
    schedule anchors, existing GPX hotspot coordinates, and OSM
    `highway=track` / `highway=service` linework from
    `website/data/osm_aop_9patch.geojson`.
  - Builds a small OSM route index and records per-track `osm_track_m`,
    `osm_route_count`, and `osm_way_ids`.
  - Rock-crawl behavior is modeled as repeated slow attempts, short reverse
    moves, and dwell at technical anchors.
- `brain/import/synthetic_saturday_activity.gpx`
  - 72 synthetic user tracks / 13,713 timestamped points.
  - Synthetic evidence only; not field data.
- `website/data/aop_synthetic_activity_tracks.geojson`
  - Viewer trace layer for inspecting the simulated user routes.
- `website/data/aop_synthetic_activity_hotspots.geojson`
  - Separate hotspot extraction output from the synthetic GPX.
  - Current output: 18 cells / 36 features from 72 synthetic sessions.
  - Synthetic extraction is intentionally ranked by stopped+slow time, filters
    low-interest pass-through cells, and caps intensity at 120 minutes so the
    pavilion does not flatten the other technical stops.
- `website/data/aop_synthetic_activity_report.json`
  - Records the scenario seed, persona counts, expected anchors, and overlap
    with existing first-party GPX hotspots and OSM route usage.
  - Current report: 72 / 72 tracks start at the pavilion; 7 planned anchors are
    within 50 m of existing hotspot evidence; 70 / 72 tracks include OSM
    route-following; 103.34 km of the synthetic traces are counted along OSM
    line vertices across 19 OSM way IDs.
- `website/index.html`
  - Toggle `Simulated Saturday activity` under `Derived layers`, default OFF.
  - Renders synthetic tracks plus hotspot heat/cells/labels.
- `mvp/scripts/playwright_verify_synthetic_activity.py`
  - Verifies hidden initial state, source metadata, all-pavilion starts,
    OSM route-following, extraction coverage, overlap with existing GPX heat,
    render, popup, and console cleanliness.

## Algorithm

For each pair of consecutive points inside the same GPX segment:

```text
dt = next_time - current_time
distance = meters_between_points
speed = distance / dt
```

The interval's time is sampled along the segment and assigned into a local
meter grid. More seconds in a cell means more heat.

Speed class:

```text
stop   < 0.05 m/s, or >= 30 s with <= 6 m movement
slow   < 0.30 m/s
moving otherwise
```

Intensity is relative to the hottest cell in the generated set:

```text
peak   >= 70% of max dwell
high   >= 40%
medium >= 18%
low    below that
```

The geometry is intentionally square cells, not only a screen heatmap. The
screen heatmap looks good, but the cell polygons are what make the layer
auditable, clickable, printable, and source-traceable.

## Source discipline

This layer is **not publishable trail data**.

Current source:

```text
brain/import/Saturday_Afternoon_Activity.gpx
source_type: field_track_gpx / first-party GPX
permission: internal
publish_status: hold
review_status: raw activity evidence; not a validated trail or facility
```

Before this leaves the inspection viewer, it needs a source-register row and a
privacy decision. A single person's GPX can reveal behavior, stops, and staging
habits. Aggregated event heat should suppress identity and exact timestamps.

## Verification

Run:

```bash
python3 mvp/scripts/build_activity_hotspots.py
cd website
python3 -m http.server 8001
```

Then, from the repo root:

```bash
python3 mvp/scripts/playwright_verify_activity_hotspots.py
```

2026-05-22 run against `WEBSITE_URL=http://localhost:8010/`: PASS, 0 console
errors. Screenshots:

```text
brain/output/playwright_activity_hotspots_initial.png
brain/output/playwright_activity_hotspots_on.png
brain/output/playwright_activity_hotspots_popup.png
brain/output/playwright_activity_hotspots_off.png
```

## Roadmap

### V1: Static first-party GPX hotspots

Status: shipped.

Purpose: prove the visual and the math from one timestamped GPX without
changing the database shape.

### V1.1: Normalize timestamped points in PostGIS

Add a queryable raw table instead of reparsing XML for derived products:

```text
raw.gpx_trackpoints
- id
- source_id
- capture_id
- track_name
- segment_index
- point_index
- recorded_at
- ele_m
- geom Point(4326)
- hdop / accuracy_m when available
- metadata
```

Then build `derived.activity_hotspot_cells` or a static export from SQL:

```text
source GPX points -> time intervals -> grid/hex aggregation -> viewer export
```

This unlocks multi-GPX aggregation, repeat-track confidence, date filters, and
QGIS inspection.

### V1.2: Multiple tracks and confidence

When more field tracks exist, split intensity into:

- `dwell_seconds`: how long people spend there.
- `track_count`: how many distinct rides support it.
- `visit_count`: how often the area is re-entered.
- `recent_dwell_seconds`: optionally time-decayed heat.

Visual rule: one track can show heat, but repeated tracks should draw with
higher confidence.

### V2: Browser GPS recorder

Add a real activity recorder to the viewer or future app:

```text
lat, lng, accuracy_m, timestamp, heading, speed_mps, session_id
```

Minimum behavior:

- Show GPS accuracy before recording.
- Pause/resume.
- Store locally when offline.
- Export GPX/GeoJSON.
- Submit only after explicit user action.
- Keep raw recordings out of publish until reviewed.

### V2.1: Hotspot review workflow

Use hotspots as prompts, not answers:

- "This may be a staging/rest spot."
- "This may be a hard obstacle or technical crawl."
- "This may be GPS drift under canopy."
- "This may be a stop caused by conversation, repair, or battery swap."

Review can promote a hotspot into a POI, hazard, trail feature, or annotation,
but the hotspot itself remains evidence.

### Event / operations layer

For event maps, aggregate anonymized session heat:

- popular staging areas
- bottlenecks
- likely spectator stops
- high-dwell technical features
- underused trail corridors

Privacy rule: event heat should aggregate enough sessions that no single driver
or route can be reconstructed from the public layer.

## Acceptance

- [x] GPX-to-hotspot builder exists and writes viewer GeoJSON.
- [x] Segment gaps are not connected.
- [x] Hotspot cells carry dwell and source/review metadata.
- [x] Viewer has a default-off derived hotspot toggle.
- [x] Viewer renders heatmap + auditable cells + labels.
- [x] Hotspot popup explains the evidence.
- [x] Playwright verification exists.
