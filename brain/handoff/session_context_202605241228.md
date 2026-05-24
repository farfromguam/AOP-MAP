# Session Context: Sprint 03 CWC Dump

Date: 20260524 12:28

This is the CWC handoff dump after Sprint 03 viewer-polish carryover work. Keep
the durable feature record in the task cards and viewer docs; use this file only
to restart the next session quickly.

## Where We Are

Repo: `/Users/christopherfryman/Documents/code/AOP MAP`

Current sprint: Sprint 03.

Active carryover card: `brain/tasks/03_event_app/viewer_polish_carryover.md`.
Parallel Sprint 03 thrust: `brain/tasks/03_event_app/full_loop_crud_upload_audit.md`.

Sprint 03 carryover lanes 1-5 are shipped:

- Lane 1: two-lane hot control was already shipped in
  `brain/tasks/02_edit/_done/hot_control_two_lane.md`.
- Lane 2: calendar wide/narrow default behavior preserved, and current
  `happening` / `upcoming_next` row now scrolls into view.
- Lane 3: right-panel collapse chevrons are normalized: collapsed `▸`,
  expanded `▾`; section collapse buttons now match the bordered layer-drawer
  button treatment.
- Lane 4: Fresh / Park / Topo / Trace default-layer audit table added to
  `brain/research/viewer.md`.
- Lane 5: Brand-logo rows now have per-logo size sliders; `icon_size` persists
  in `aop_brand_logos_overrides_v1`; add-image runbook added at
  `brain/spinup/add_image_to_viewer.md`.

Remaining carryover:

- Lane 6: Pass 4 CSS + theme + code-smell card under `01_mvp/`.
- Lane 7: numbered trail-name research pointer stays with
  `brain/tasks/01_mvp/_done/community_trails_import.md`.

## Files Touched By This CWC Work

- `website/index.html`
- `mvp/scripts/playwright_verify_event_schedule.py`
- `mvp/scripts/playwright_verify_brand_logos.py`
- `brain/tasks/03_event_app/viewer_polish_carryover.md`
- `brain/tasks/02_edit/_done/branding.md`
- `brain/research/viewer.md`
- `brain/spinup/add_image_to_viewer.md`
- narrow stale-lane-count updates in `brain/brain_map.md`,
  `brain/handoff/session_context.md`, and `brain/tasks/_readme.md`

Playwright verifier screenshots were regenerated under `brain/output/`.

## Verification

Passed:

```text
inline viewer script parse
python3 -m py_compile mvp/scripts/playwright_verify_event_schedule.py mvp/scripts/playwright_verify_brand_logos.py
git diff --check
python3 mvp/scripts/playwright_verify_brand_logos.py
python3 mvp/scripts/playwright_verify_event_schedule.py
```

Both Playwright verifiers were run against `http://localhost:8001/`.

## Local Server Note

The Playwright viewer was started with:

```bash
cd website
python3 -m http.server 8001
```

Sandboxed commands could not bind/connect to localhost, so server start and
Playwright verifier runs needed escalation.

## Dirty Tree Note

At the time of this dump, `git status --short` includes changed files from this
work plus pre-existing/parallel brain updates:

- `brain/brain_map.md`
- `brain/handoff/session_context.md`
- `brain/handoff/session_context_20260524.md`
- `brain/search_map.md`
- `brain/tasks/01_mvp/_readme.md`
- `brain/tasks/02_edit/_readme.md`
- `brain/tasks/_readme.md`

Do not assume all of those were created by this CWC work. Only lane-count
staleness was touched in the orientation files where needed.

## Next Best Pickups

1. Create/start the Lane 6 Pass 4 CSS + theme + code-smell card.
2. Or move into the main Sprint 03 event-app loop from
   `brain/tasks/03_event_app/full_loop_crud_upload_audit.md`, starting with
   staff event CRUD/schema planning.
3. Keep the MVP data-integrity backlog visible: source-backed trail data,
   QGIS/PostGIS inspection, acreage reconciliation, and later AOP-specific DEM
   tiles.
