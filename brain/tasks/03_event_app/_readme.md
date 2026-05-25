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
- `left_sidebar_content_audit.md` - opened 2026-05-25 after the Rock Warblers Trail Blazing Invitational rebrand of the left sidebar (calendar header, Event tab, About tab) in production voice. A second 2026-05-25 pass merged the Event and About tabs into a single About tab and dropped `.left-tabs` to two columns. Audit closes when Rock Warblers confirm the real specifics behind sister-event placeholders.
- `left_panel_poi_browser.md` - pending Sprint 03 card; routes `misc.md`'s "browseable POI list in the left rail" into a new third `POI` tab, restoring `.left-tabs` to three columns.
- `poi_editor_inline_list_and_highlight.md` - opened 2026-05-25. Drawn-POI feature list relocated from the layer drawer into the Map editor section under the categories; per-row `★/☆` highlight toggle gates which drawn POIs surface in the left-rail POI tab.
- `left_rail_collapse_tabs.md` - opened 2026-05-25. Design exploration for a "manilla tab drawer" that wraps the search / hot / calendar cards in one collapse-aware shell with per-card icon toggles, upward absorption, and the closed-icon-as-island visual. Five HTML mockup variants live at `website/leftrail_v{1..5}_*.html`; variant pick is the open decision. Composes with `left_panel_context_tabs.md` (the tabs inside the calendar card) and `left_panel_poi_browser.md` (the pending POI tab) since the drawer wraps the context card from outside.
- `dev_db_snapshot_reseed.md` - dev/pre-prod data snapshot and reseed task from `misc.md`.
- `sprint_02_critique_followups.md` - holding card for issues surfaced from a critique of the closed Sprint 02 work (fixed verifier failures, AOP badge default-on, masked FAILs, hot-button polish, localStorage hygiene, taxonomy drift).
- `misc.md` - scratch intake. Route anything durable into a card.

## Shape

This sprint is not "build a community app first."

It is the bridge from the current static viewer plus PostGIS spine into a staff-curated event and submission loop. Event setup can move ahead first. Public or semi-public submissions stay behind invite codes, moderation, source register links, and publish gates.
