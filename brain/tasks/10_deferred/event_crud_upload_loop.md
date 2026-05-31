# Event CRUD + Upload Loop

> **Deferred — Sprint 04 triage (2026-05-30).** Not started — every Acceptance
> box is open. **Deferred because** it is large multi-phase work that needs
> scoping decisions first (the Open Questions below: invite-codes vs accounts,
> who moderates, R2 vs S3, photo publishability, GPX-timestamp handling, whether
> QGIS review stays mandatory) and a stable `core`/storage baseline. This is the
> sprint's main future thrust; promote back to an active sprint once the forks
> are answered.

Sprint 03 proved the shape in an audit. Sprint 04 is where the app loop becomes
real: staff event CRUD first, upload-backed evidence second, contributor
submissions behind a review gate third.

People submit evidence. Staff promotes map truth.

#aop #04_event_app #events #crud #uploads #moderation

-----

## Source

- `../03_event_app/_done/full_loop_crud_upload_audit.md`
- `../03_event_app/_done/right_panel_editor_consistency.md`
- `../03_event_app/_done/poi_editor_tree_inline_accordion.md`
- `../03_event_app/_done/sprint_02_critique_followups.md` section H
- `../../northstar/map_northstar.md`
- `../../northstar/source_register.md`

## Scope

### 1. Staff Event CRUD

Build the first durable event records:

- event name, slug, date window, status, description, registration URL, permission note, publish flag
- event sessions with time, title, location tag, route refs, status
- event features as point / line / polygon records tied to an event
- archive/withdraw semantics instead of hard delete after public use

Seed from `website/data/aop_event_schedule.json` or generate that JSON from the
database. Long term, the JSON is output, not source of truth.

### 2. Upload Intake Foundation

Build upload metadata and raw object handling before public intake:

- immutable original file object
- metadata row before upload
- GPX first, then KML / KMZ / GeoJSON / photo
- MIME/extension/size validation
- parsed geometry lands as raw/submitted evidence
- source-register rows and feature-source links created automatically

Object storage target is still open: Cloudflare R2 or AWS S3.

### 3. Contributor Submissions

Put this behind invite codes or accounts.

Minimum submission types:

- trail trace drawn on the map
- GPX / KML / KMZ / GeoJSON upload
- landmark point with note
- landmark photo or attachment
- hazard / closure / correction
- note attached to an existing feature

Every submission carries event id when relevant, contributor identity, timestamp,
geometry, note, permission, and review state.

### 4. Moderation + Promotion

Moderator queue states:

- submitted
- needs_info
- needs_field_check
- reviewed
- verified
- rejected
- duplicate
- promoted
- redacted

Promotion creates observations and source links first. Core trails, trailheads,
landmarks, hazards, and event features update only after review.

### 5. First Event-Ops View

Sprint 02 named Approach / Event HQ / Stage Marshal style views as the missing
persona surface. Pick one view when staff event CRUD lands, not as a detached
visual preset.

Suggested first answer: **Event HQ**. It can combine event sessions, facilities,
parking/camping, registration, and the moderation/status surfaces staff actually
use during setup.

## Open Questions

- Invite codes only, or accounts?
- Who moderates: AOP staff, Rock Warblers, map maintainer, or role-based mix?
- R2 or S3?
- Are contributor photos publishable at all, or evidence-only?
- Should GPX timestamps be retained, blurred, or stripped after extraction?
- Does QGIS review remain mandatory before any app-promoted feature reaches `publish`?

## Acceptance

- [ ] Staff can create, edit, publish, archive, and restore a draft event.
- [ ] Staff can add sessions and tag them to locations or routes.
- [ ] Staff can add point / line / polygon event features.
- [ ] Public export can reproduce the current event schedule layer from database-backed data.
- [ ] A GPX upload creates an immutable raw object.
- [ ] Parsed upload geometry lands as raw/submitted evidence, not as a trail.
- [ ] Source-register rows and feature-source links are created automatically.
- [ ] Moderator can see uploads and submissions in a queue.
- [ ] Contributor can submit a trail trace behind an invite/account gate.
- [ ] Contributor can submit a landmark point with note and optional photo.
- [ ] Contributor can withdraw or edit while the submission is still unreviewed.
- [ ] Moderator can reject, duplicate, request info, mark needs field check, verify, or promote.
- [ ] Promotion creates or updates reviewed observations/core features and source links.
- [ ] Publish export includes only permissioned, publishable features.
- [ ] Raw attachments stay private unless explicitly marked publishable.
- [ ] One event-ops view ships with the first staff CRUD surface.

## Out of Scope

- Ticketing, payments, registration, waivers.
- Live scoring or timing.
- Public photo gallery.
- Native mobile app.
- Letting contributors edit core trails directly.

## Verification

- Run one event seed from database to event schedule JSON.
- Upload one GPX through the app and confirm raw object, parsed geometry, source row, and feature-source link.
- Submit one landmark with photo and confirm it stays private until reviewed.
- Promote one submission into `core.observations`, then into a core feature.
- Export publish views and confirm the static viewer displays only publishable features.
