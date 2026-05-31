# Sprint 04: Event App Pickup

Sprint 04 starts from the Sprint 03 closeout.

The goal is not to reopen every Sprint 03 card. The shipped cards move to
`../03_event_app/_done/`; the still-owed work gets a clean Sprint 04 holder.
`../03_event_app/misc_3.md` stays where it is, untouched.

#aop #sprint #04_event_app #pickup

-----

## Sprint 04 triage (2026-05-30)

Reviewed every card in this folder and sorted it to `_done/` or `10_deferred/`.
The lists below this block are the **pre-triage** record (kept for history).

**Shipped → `_done/`:**

- `calendar_group_icon_review.md` — clipboard glyph wired into `#lrTabCal`.
- `editor_unified_tree.md` — five-bucket editor tree (shipped 05-27).
- `editor_three_buckets_v3c.md` — collapsed to three buckets + per-bucket create
  (shipped 05-28; supersedes the tree pass).
- `editor_unified_positioned_features.md` — unified override store + lock flag
  (shipped 05-29).
- `misc_4.md` — items 1–5, the PENDING block, and the images/region-callout
  export bake; remaining lines routed or user-held (close-out header added).
- `bake_first_poi_serve_slice.md` — **new card, split out** of
  `star_driven_poi_list.md` + `dev_db_snapshot_reseed.md`: the shipped bake-first
  POI SERVE pipeline (`core.pois` → `publish.pois` → `publish.geojson` → viewer)
  plus the fresh-DB seed mount.

**Deferred → `../10_deferred/`** (each carries its own "Deferred because"):

- `event_crud_upload_loop.md`, `paper_map_trail_extraction.md` (partial/active),
  `star_driven_poi_list.md` (remainder), `dev_db_snapshot_reseed.md` (remainder),
  `data_integrity_publishability.md`, `brand_assets_and_permissions.md`,
  `calendar_placeholder_state.md`, `park_bounds_icon_apply.md`,
  `rock_warblers_content_audit.md`, `poi_editor_followups.md`,
  `viewer_polish_followups.md`.

**Left in place:** `source_layers.md` — a reference layer-inventory list (used by
the provenance grouping in `paper_map_trail_extraction.md` / `research/viewer.md`),
not a task card with acceptance criteria, so it was not sorted.

**Open chore (unchanged):** the three locked agent worktrees + `worktree-agent-*`
branches noted below are destructive cleanup, still owed by the user.

-----

## Post-triage cards (added after 2026-05-30)

New work opened after the triage above lives directly in this folder:

- `icon_system_normalize.md` — inline-UI icon stroke/optical normalization.
- `pwa_qa.md` / `pwa_qa_2.md` / `pwa_qa_data_bakes.md` — iOS-PWA QA swarm + the
  split-out data-bake items.
- `_done/app_code_review_fixes_batch1.md` — **DONE.** The 15 no-decision fixes
  from the 2026-05-31 app code review **+ H4/L8** (the queued SW cache-staleness
  decision, answered stale-while-revalidate; `VERSION` v20 → v21). Applied to the
  working tree and verified (new verifier
  `mvp/scripts/playwright_verify_code_review_fixes.py`, 0 console errors, SW
  active). One sweep finding retracted as a false positive.
- `app_code_review_followups.md` — **NOT DONE (active).** The 17 still-held
  findings, self-contained, grouped (on-device / polish / refactor) with a
  recommended order. All no-device work is done; next slice is the on-device
  batch (H1, M12 first), verified on the iPhone.
- `trail_research_integration.md` — **SCOPE.** Wire the persisted trail catalog
  (names + descriptions + landmarks) into the live viewer via a runtime sidecar
  join on `trail_number`. Surfaces: trail-click popup (new), left POI browser
  (repoint to the gold network), search preview. Forks: license/publish gate +
  which trail dataset is canonical. 9 of 87 numbered trails have descriptions
  today; the rest are owed upstream.

-----

## Current cards (pre-triage record)

- `event_crud_upload_loop.md` - staff event CRUD, upload intake, contributor submissions, moderation, promotion, and the first event-ops view.
- `dev_db_snapshot_reseed.md` - repeatable dev/pre-prod PostGIS dump and reseed.
- `rock_warblers_content_audit.md` - replace sister-event placeholder copy once Rock Warblers confirm real event details.
- `data_integrity_publishability.md` - source-backed trails, acreage reconciliation, DEM swap, POI gap pass, and synthetic-vs-real activity boundaries.
- `viewer_polish_followups.md` - residual verifier, left-rail, right-panel, load-animation, and code-health follow-ups.
- `calendar_placeholder_state.md` - pending-pick calendar loading placeholder mockups from `misc_3.md` item 13.
- `calendar_group_icon_review.md` - resolved 2026-05-29: Clipboard + ruled lines wired into `#lrTabCal` (misc_3.md item 16).
- `poi_editor_followups.md` - drawn-POI accordion follow-ups that did not need to block Sprint 03.
- `brand_assets_and_permissions.md` - raster cleanup and brand-use permission posture.
- `park_bounds_icon_apply.md` - pick one boundary-derived Park icon and wire it into the viewer.
- `editor_unified_tree.md` - combine the right rail's POI and Map editor sections into one tree by base type (Point / Line / Polygon / Image / Callout) with a live ★ Visitor list group.
- `editor_three_buckets_v3c.md` - supersedes the prior tree pass: collapse to three buckets (Point / Line / Polygon), delete the 5-toggle strip, source sub-groups inside each bucket (Drawn open, refs collapsed), and per-bucket `+` opens an inline create row.

## Extraction map

| Sprint 03 source | Sprint 04 holder |
| --- | --- |
| `full_loop_crud_upload_audit.md` | `event_crud_upload_loop.md` |
| `dev_db_snapshot_reseed.md` | `dev_db_snapshot_reseed.md` |
| `left_sidebar_content_audit.md` | `rock_warblers_content_audit.md` |
| `left_panel_poi_browser.md` | `data_integrity_publishability.md`, `viewer_polish_followups.md` |
| `left_rail_collapse_tabs.md` | `viewer_polish_followups.md` |
| `code_health_pass_4.md` | `viewer_polish_followups.md` |
| `calendar_placeholder_state.md` | `calendar_placeholder_state.md`, `viewer_polish_followups.md` |
| `right_panel_editor_consistency.md` | `viewer_polish_followups.md`, `event_crud_upload_loop.md` |
| `poi_editor_inline_list_and_highlight.md` | `poi_editor_followups.md` |
| `poi_editor_tree_inline_accordion.md` | `poi_editor_followups.md`, `event_crud_upload_loop.md` |
| `sprint_02_critique_followups.md` | `brand_assets_and_permissions.md`, `data_integrity_publishability.md`, `viewer_polish_followups.md`, `event_crud_upload_loop.md` |
| `load animations.md` | `viewer_polish_followups.md` |
| `park_bounds_icon_review.md` | `park_bounds_icon_apply.md` |

Fully shipped or fully routed Sprint 03 cards with no active Sprint 03 work
left: `left_panel_context_tabs.md`, `viewer_polish_carryover.md`,
`viewer_session_state_test_clock.md`, `misc.md`, and `misc_2.md`.

`misc_3.md` triage (2026-05-27) routed:

| misc_3 item | Sprint 04 holder |
| --- | --- |
| 13 (calendar placeholder mockup) | `calendar_placeholder_state.md` |
| 14 (retire old mockup pages) | `viewer_polish_followups.md` → "Mockup Cleanup" |
| 16 (calendar group icon review) | `calendar_group_icon_review.md` |
| 18 (brand-logos default-on permission posture) | `brand_assets_and_permissions.md` (reconcile-conflict line) |

Operational chore not on a brain card: three locked agent worktrees at
`.claude/worktrees/agent-{abad7f93392b08c89,aca52a42ecb6d6b69,af4a7643c3598a24c}`
plus branches `worktree-agent-*` remain after the 2026-05-27 triage. Patches
captured at `/tmp/aop_agent_patches/{bucketB,bucketC,bucketD_road}.patch`.
Cleanup is destructive (`git worktree remove --force` + `git branch -D`), so
left to the user per `ai_rules/no_commits.md`.

## Shape

Keep the northstar constraint visible: app work captures evidence and event
operations. It does not let public submissions overwrite trusted map truth.
