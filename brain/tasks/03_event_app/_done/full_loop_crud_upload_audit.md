# Full Loop CRUD + Upload Audit

TL;DR:
- The map already has pieces of the loop: static read views, browser-only POI editing, GPX ingest, source register links, and a proven observation -> promotion smoke test.
- It does not yet have a real app CRUD layer, upload pipeline, attachment model, contributor identity, moderation queue, or event feature schema.
- Sprint 03 should build staff event CRUD first, then contributor submissions into `raw` / `core.observations`, then moderation and publish export. People submit evidence. Staff promotes map truth.

#aop #tasks #03_event_app #crud #uploads #events #observations

-----

## Source

- `../../northstar/map_northstar.md` - V2 submissions wait for the validation loop; observations do not overwrite trails directly.
- `../../northstar/source_register.md` - every submitted, traced, or imported feature needs provenance, confidence, permission, and publish status.
- `../../northstar/validation_loop.md` - capture, source, review, promote, document.
- `../01_mvp/aop_south_pittsburg_map_build_card.md` - Phoenix / LiveView is future stack for submissions, not Website V1.
- `../01_mvp/mvp_validation_loop.md` - smoke test already proves observation capture, review, promotion, provenance, and export.
- `../01_mvp/event_schedule_layer.md` - current schedule is static JSON with tag-resolved locations.
- `../backlog/rc_event_mapping_backlog.md` - event vocabulary: stages, gates, skills sections, checkpoints, loops, registration, camping, parking.
- `../backlog/rcmap_feature_review.md` - peer expectation: KMZ, photos, report issues, events, ratings; public contributions are V2.
- `../../../mvp/init_db.sql` - current PostGIS schema.
- `../../../website/index.html` - current static viewer, browser-side editor, local exports, event schedule rendering.
- `../../../mvp/scripts/README.md` - import / export scripts and validation-loop flow.

## Current Loop

### Read

The public read surface exists.

`website/index.html` reads `website/data/publish.geojson` plus static context files for roads, water, buildings, cemeteries, OSM, SFWDA, lidar, activity hotspots, and `aop_event_schedule.json`. Search, presets, layer toggles, popups, and event schedule jumps all work against static files.

Current publish export is thin: `publish.geojson` has one park boundary and two trail centerline features. There are no publishable trailheads in the current file.

### Create

Create exists in three different places, none of them the app layer:

- Browser editor creates points, footprints, and line traces with Terra Draw. They live in `localStorage` under `aop_editor_pois_v1`.
- `mvp/scripts/import_gpx_track.sh` imports GPX into `raw.gpx_captures` and `core.field_tracks`, with source rows and feature-source links.
- `mvp/scripts/run_validation_loop_smoke.sh` proves a board-review observation can land in `core.observations` and promote into `core.trail_centerlines`.

The current event schedule is created by editing `website/data/aop_event_schedule.json` by hand.

### Update

Update is mostly local or manual.

- Browser-drawn features can be renamed, moved, hidden, and exported.
- Visitor-context callouts and per-feature visibility persist in localStorage.
- Event sessions and locations update only by editing JSON.
- PostGIS tables have `updated_at` triggers, but there is no app UI for updates.

QGIS is still the intended serious editing surface for the map spine. The app should not replace that in Sprint 03.

### Destroy

Destroy is not a first-class policy yet.

The browser editor can delete one drawn feature or clear all local drawn features. The database has status and publish gates, but no explicit archive / withdrawn / redacted lifecycle for event features, submissions, or attachments.

Hard delete should be rare once evidence enters the source register. Normal "destroy" should mean hidden, withdrawn, rejected, archived, or redacted.

### Upload

Upload is not built.

Current paths are local scripts and browser export:

- GPX import exists, but it is a staff command-line workflow.
- Generic GeoJSON import exists, but it does not set provenance automatically.
- Browser POI export writes GeoJSON to a local download.
- Full / section viewer exports copy JSON to clipboard.
- There is no server-side file upload, direct-to-object-storage flow, photo attachment model, moderation inbox, antivirus / MIME validation, EXIF policy, or R2/S3 bucket wiring.

## Gap Summary

The database knows how to hold map evidence. The viewer knows how to display and sketch. The missing thing is the app spine between them.

The next app layer needs to own:

- event records
- event feature records
- contributor / invite identity
- submissions
- uploads and attachments
- moderation decisions
- promotion into core map features
- export back to the static viewer / PMTiles path

Without that, "people submit trails and landmarks" becomes a pile of files and browser state. Useful for a session. Bad as a source of truth.

## Proposed Sprint 03 Loop

### 1. Staff Sets Up An Event

Create an event record:

- name
- slug
- date window
- status: `draft`, `announced`, `live`, `closed`, `archived`
- public description
- external registration URL
- source / permission note
- publish flag

Add event features:

- registration / wristband check
- pavilion / G-Central
- parking and camping zones
- stage starts and finishes
- gates
- checkpoints
- photo waypoints
- skills sections
- routes / loops
- hazards and closures

The existing JSON schedule can remain the first authoring format, but it should become an export from the app or a seed into the app. Long-term, JSON is not the source of truth for events.

### 2. Staff Publishes An Event Map

Read side:

- public event page
- public event map layer
- printable course / stage packets
- status-aware public viewer toggle

Publish rule:

- draft features stay internal
- announced / live features can publish if permission allows
- raw evidence can display only when visibly marked as raw or proposed

### 3. Contributors Submit Trails And Landmarks

Submission types:

- trail trace drawn on map
- GPX / KML / KMZ upload
- landmark point
- landmark photo
- hazard / closure / correction
- note attached to an existing trail, landmark, or event feature

Minimum capture fields:

- event id, optional but strongly preferred during event windows
- feature type
- geometry
- note
- submitter display name or contributor id
- contact, optional depending on invite policy
- capture timestamp
- device GPS accuracy, when browser geolocation is used
- permission checkbox: AOP map project may review and use this submission

Every submission becomes observation evidence. Nothing jumps straight into `core.trail_centerlines`, `core.trailheads`, or a publish view.

### 4. Uploads Land In Raw Storage

Object storage:

- direct upload to R2/S3 with a presigned URL
- file metadata row created before upload
- object key stores event id, submission id, and attachment id
- original file is immutable
- derived thumbnails / parsed geometry are separate objects or rows

Allowed first-pass file types:

- `.gpx`
- `.kml`
- `.kmz`
- `.geojson`
- `.jpg`
- `.jpeg`
- `.png`

Upload checks:

- size caps by file type
- extension and MIME validation
- parse validation for geospatial files
- image dimension cap
- EXIF GPS handling policy
- virus / malware scan hook before moderator download

Privacy rule:

Photos and GPX files should default to private evidence. Public map output should use reviewed geometry / notes, not raw contributor files, unless permission and review explicitly allow publication.

### 5. Moderator Reviews

Queue states:

- `submitted`
- `needs_info`
- `needs_field_check`
- `reviewed`
- `verified`
- `rejected`
- `duplicate`
- `promoted`
- `redacted`

Moderator actions:

- view submission on map
- inspect attachments
- edit normalized geometry copy
- link submission to an existing map feature
- split / merge GPX segments
- classify as trail, trailhead, landmark, hazard, closure, event feature, or note
- set confidence and permission
- add source-register link
- request more info
- reject with reason
- promote into core

This is the real "update" surface for submissions.

### 6. Promotion Updates The Map Spine

Promotion targets:

- `core.trail_centerlines`
- `core.trailheads`
- `core.hazards`
- `core.print_annotations`
- future `core.landmarks`
- future event feature tables

Promotion must create `source_register.feature_sources` links. One promoted trail may have many sources: GPX, photo, board markup, AOP staff confirmation, old paper map, imagery trace.

Publish export stays gated by permission and publish status.

### 7. Event Closes And Becomes Evidence

Closing an event should not delete it.

Closed event data becomes a source for future maps:

- which routes were actually used
- where people got confused
- which landmarks became operationally important
- which submissions were promoted
- which raw claims need another field check

That history is valuable. Archive it, do not flatten it.

## CRUD Matrix

| Object | Create | Read | Update | Destroy |
| --- | --- | --- | --- | --- |
| Event | Staff creates draft | Public sees announced/live; staff sees all | Staff edits details, status, registration URL, publish flag | Archive; hard delete only empty drafts |
| Event session | Staff creates schedule row | Public schedule/sidebar | Staff edits time, title, location tag, route refs | Cancel/hidden; preserve history after publish |
| Event feature | Staff draws/imports point, line, polygon | Event map, printable packets | Staff edits geometry, class, order, width, role, status | Archive/withdraw; do not hard delete after public use |
| Contributor | Invite or account creation | Staff sees identity needed for review | Staff updates role/trust/contact | Disable; preserve attribution where legal |
| Submission | Contributor creates from form/upload/map draw | Contributor sees own; moderators see queue | Contributor can amend before review; moderator normalizes | Withdraw/reject/redact; hard delete spam/PII when needed |
| Attachment | Contributor uploads file/photo | Staff preview; public only if promoted and allowed | Moderator edits title, visibility, derived thumbnail | Redact or delete object under retention policy |
| Observation | App creates from accepted submission | Staff review layers | Moderator sets confidence/review status | Reject/archive; preserve source unless redacted |
| Core map feature | QGIS/staff promotion creates | Public if publishable; staff always | QGIS/staff edit with source links | Retire/supersede; hard delete only mistakes before publish |
| Publish export | Script/job creates static viewer files | Static viewer reads | Re-export from publish views | Old exports archived or overwritten by release policy |

## Data Model Needed

Use current `raw`, `core`, `publish`, and `source_register` zones. Add only what the loop earns.

Suggested first schema:

- `core.events`
- `core.event_sessions`
- `core.event_features`
- `core.event_feature_sources` or use the existing generic `source_register.feature_sources`
- `core.event_feature_links` for features reused from buildings, POIs, trailheads, or landmarks
- `core.submissions`
- `core.submission_attachments`
- `core.submission_reviews`
- `raw.uploads`
- `raw.submitted_geometries`

Likely also needed:

- `core.landmarks`
- `core.facilities`
- `core.contributors`
- `core.invites`
- `core.audit_log`

Keep geometry in EPSG:4326. Keep uploaded file source CRS / metadata separately.

## API / App Surface

Phoenix / LiveView still fits the original build card.

Minimum staff routes:

- list / create / edit events
- edit event schedule
- draw or attach event features
- upload event packet source files
- moderation queue
- submission detail
- promote / reject / request info
- export publish files

Minimum contributor routes:

- enter invite code
- choose event
- submit trail
- submit landmark
- upload GPX / KML / KMZ / GeoJSON / photo
- see own submission status
- withdraw or amend while still `submitted`

Do not build scoring, registration, ticketing, waiver signing, live race timing, or social feeds here.

## Security And Trust

Required before public intake:

- invite codes or accounts
- rate limits
- CSRF protection
- file size limits
- content-type validation
- object storage private by default
- moderator-only original downloads
- audit log for status changes and promotion
- redaction path for PII or bad uploads
- explicit permission checkbox on every submission

Nice later:

- contributor trust levels
- duplicate detection
- browser GPS capture
- offline draft queue / PWA
- automatic GPX simplification preview

## Recommended Sprint 03 Slices

### Slice A - Staff event CRUD

Build `core.events`, `core.event_sessions`, and `core.event_features`. Seed from the current `aop_event_schedule.json`. Let staff create, edit, archive, and publish event records.

Acceptance:

[ ] Staff can create a draft event.
[ ] Staff can add sessions and tagged locations.
[ ] Staff can add point / line / polygon event features.
[ ] Public export can reproduce the current event schedule layer from database-backed data.

### Slice B - Upload intake foundation

Build upload metadata, object storage, and parser hooks. GPX first.

Acceptance:

[ ] A GPX upload creates an immutable raw object.
[ ] Parsed geometry lands as raw/submitted evidence, not as a trail.
[ ] Source register rows and feature-source links are created automatically.
[ ] Moderator can see the upload in a queue.

### Slice C - Trail and landmark submissions

Build the contributor form behind invite codes. Support map-drawn geometry and optional attachments.

Acceptance:

[ ] Contributor can submit a trail trace.
[ ] Contributor can submit a landmark point with note and optional photo.
[ ] Submission carries event id, permission, contributor identity, timestamp, and geometry.
[ ] Contributor can withdraw or edit while the submission is still unreviewed.

### Slice D - Moderation and promotion

Turn submissions into reviewed observations and promoted map features.

Acceptance:

[ ] Moderator can reject, duplicate, request info, mark needs field check, verify, or promote.
[ ] Promotion creates or updates a core map feature and source links.
[ ] Publish export includes only permissioned, publishable features.
[ ] Raw attachments stay private unless explicitly marked publishable.

## Decisions

### 1. Does Sprint 03 build public submissions immediately?

**Suggested:** No. Build staff event CRUD and upload-backed moderation first.

Why: The northstar is explicit. The map earns submissions through a review loop. Staff CRUD and upload plumbing are reusable; public intake without moderation is just mess with a login screen.

### 2. Are event features core map features?

**Suggested:** Event features are first-class core records, but not all are permanent park features.

Why: A checkpoint, gate, registration desk, or photo waypoint has real geometry and source context. Some exist only for one event. Keep them tied to `event_id` and status rather than pretending every event point is a permanent landmark.

### 3. What does destroy mean?

**Suggested:** Archive, withdraw, reject, redact, or supersede. Hard delete only empty drafts, spam, malware, or legally sensitive material.

Why: The source register needs history. A wrong trail claim can still explain why a correction was made. But bad uploads and PII need a real redaction path.

### 4. Should browser-drawn POIs become submissions?

**Suggested:** Yes, but only through an explicit "Submit this" action in the app.

Why: Local editor state is useful for sketching. It is not evidence until a person attaches permission, event context, and source metadata.

## Open Questions

- Invite code only, or full accounts?
- Who moderates: AOP staff, Rock Warblers, map maintainer, or all with roles?
- Which object storage target: Cloudflare R2 or AWS S3?
- What is the first real event this should model?
- Are contributor photos publishable at all, or evidence-only?
- Should GPX timestamps be retained, blurred, or stripped after hotspot extraction?
- Do we need QGIS review before any app-promoted feature reaches `publish`?

## Out Of Scope

- Ticketing, payments, registration, or waivers.
- Live scoring / timing.
- Social features.
- Public photo gallery.
- Native mobile app.
- Letting contributors edit core trails directly.

## Verification

For the report itself:

[X] Current viewer CRUD surface checked in `website/index.html`.
[X] Current database schema checked in `mvp/init_db.sql`.
[X] GPX import and promotion scripts checked.
[X] Validation-loop and source-register northstar checked.
[X] Existing event backlog and schedule layer checked.

For future implementation:

[ ] Run one event seed from database to event schedule JSON.
[ ] Upload one GPX through the app and confirm raw object + parsed geometry + source links.
[ ] Submit one landmark with photo and confirm it stays private until reviewed.
[ ] Promote one submission into `core.observations` then into a core feature.
[ ] Export publish views and confirm the static viewer displays only publishable features.
