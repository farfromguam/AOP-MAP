# Sprint 03: Event App Loop

TL;DR:
- Sprint 03 starts as the app-loop audit for event setup, CRUD, uploads, and moderated trail / landmark submissions.
- Keep the northstar constraint visible: submissions enter as observations, not direct edits to the trusted map.

#aop #sprint #03_event_app #submissions #events

-----

## Current contents

- `full_loop_crud_upload_audit.md` - audit report for event setup, CRUD surfaces, upload capabilities, and the submission-to-review-to-publish loop.
- `viewer_polish_carryover.md` - the Sprint 02 `[]` punchlist that didn't ship, organized into seven lanes. Lanes 1-5 shipped; Lane 6 moved to `code_health_pass_4.md`; Lane 7 stays on `../01_mvp/_done/community_trails_import.md`.
- `code_health_pass_4.md` - Sprint 02 CSS / theme / smell carryover, kept in Sprint 03 because this is viewer polish, not MVP map-spine work.
- `left_panel_context_tabs.md` - shipped left-panel UI pass: mobile-first control stack, Events / Park / About tabs, and context-card verifier coverage.
- `dev_db_snapshot_reseed.md` - dev/pre-prod data snapshot and reseed task from `misc.md`.
- `sprint_02_critique_followups.md` - holding card for issues surfaced from a critique of the closed Sprint 02 work (fixed verifier failures, AOP badge default-on, masked FAILs, hot-button polish, localStorage hygiene, taxonomy drift).
- `misc.md` - scratch intake. Route anything durable into a card.

## Shape

This sprint is not "build a community app first."

It is the bridge from the current static viewer plus PostGIS spine into a staff-curated event and submission loop. Event setup can move ahead first. Public or semi-public submissions stay behind invite codes, moderation, source register links, and publish gates.
