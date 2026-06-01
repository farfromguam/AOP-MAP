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

**Worktree cleanup (2026-06-01) — verified, commands handed to the user.** The
"three locked agent worktrees" chore below is **stale: those are already gone**
(`.claude/worktrees/` empty, no `worktree-agent-*` branches, `/tmp` patches gone).
What actually remained: the `aop-copy-review` worktree + `copy-review` branch
(`git cherry` → fully patch-present in master) and the `integration-pwa-qa`
safety-net branch (all swarm items shipped in master; its only non-master content
was the **intentionally-dropped** tree-landcover pattern — user confirmed
2026-06-01 — recoverable from history at `5d825f4`). All three are
verified-redundant; deletion commands (`git worktree remove --force` +
`git branch -D copy-review integration-pwa-qa` + `git worktree prune`) handed to
the user to run via `!` (git mutations are the user's surface, `no_commits.md`).

-----

## Post-triage cards (added after 2026-05-30)

New work opened after the triage above lives directly in this folder. The
**2026-05-31 triage pass** (below) re-sorted them; current state:

**Shipped → `_done/` (2026-05-31):**

- `copy_review_surface.md` — **DONE.** Copy-as-data registry (13 kinds) +
  printable `copy_review.html`; About/UI-strings/calendar-title extracted to
  `website/data/`; POI-blurb voice pass; `VERSION` v21 → v22. Shipped to
  mainline + Playwright-verified (0 console errors). Owed work is upstream
  (license, 11 null POI blurbs, public-gate confirm) — not card-blocking.
- `icon_system_normalize.md` — **DONE.** All 14 inline UI icons normalized to one
  family (vb22, 1.6 stroke + documented exceptions, optical-size measured). Tool
  `website/icon_master.html` + sidebar link live. Playwright-verified, "No open
  forks."
- `pwa_qa.md` — **DONE.** 21/21 items shipped / reworked / superseded / routed by
  the 7-agent swarm; "Open forks: none." Data items (4, 6, 17) were split to
  `pwa_qa_data_bakes.md`. The only remainder is the perpetual **on-device
  feel-confirm** (items 7 pinch / 13 colors / 15 drag) — recorded in the card's
  Disposition table; see the on-device pass in the priority block below.
- `_done/app_code_review_fixes_batch1.md` — **DONE.** The 15 no-decision fixes
  from the 2026-05-31 app code review **+ H4/L8** (the queued SW cache-staleness
  decision, answered stale-while-revalidate; `VERSION` v20 → v21). Applied to the
  working tree and verified (new verifier
  `mvp/scripts/playwright_verify_code_review_fixes.py`, 0 console errors, SW
  active). One sweep finding retracted as a false positive.

**Still active (this folder):**

- `app_code_review_followups.md` — **ACTIVE.** The 17 still-held findings,
  self-contained, grouped (on-device / polish / refactor) with a recommended
  order. All no-device decision work is done; next slice is the on-device batch
  (H1, M12 first), implemented by me + verified on the iPhone.
- `trail_research_integration.md` — **ACTIVE (Slices 1–2 shipped).** Trail catalog
  joined to the gold network at runtime: trail-click popup (new) + POI browser
  repointed to the gold network, both shipped + verified. Owed: Slice 3 (search
  description preview, actionable), Slice 4 (landmark geometry, blocked),
  license/publish gate + canonical-dataset fork, and ~110 un-catalogued trail
  names/descriptions upstream.
- `pwa_qa_2.md` — **ACTIVE (near-done, user-gated).** Items 1–5 shipped + verified
  (`playwright_verify_pwa_qa2.py`, `VERSION` v18 → v19); 7 routed to
  `pwa_qa_data_bakes.md`; 8/10 no-op (false premises). **Open:** item 6 (logo
  overshoot on zoom-out — device-only GL + the user's instruction was cut off) and
  item 9 (cemetery visibility — user "let me think").
- `pwa_qa_2_plan.md` — **ACTIVE (companion).** The executed triage/anchors plan for
  `pwa_qa_2.md`; kept beside it as reference until that card closes.
- `pwa_qa_data_bakes.md` — **ACTIVE (blocked on decisions).** Items 4 (region
  callouts bake), 6 (in-park vs region buildings + search exclusion), 17 (extend
  the 9-patch AOI), E (Ellis cemetery info bake). All need a product/boundary/
  source call before code — no actionable headless work.

-----

## Sprint 04 priority (2026-05-31)

Ranked across the active cards. P1 is what I can take end-to-end now; the rest is
gated on the user (decision or device) or owed upstream.

**P1 — actionable headless, do next (no gate):**

1. ~~`trail_research_integration.md` **Slice 3**~~ — **SHIPPED 2026-06-01**
   (uncommitted). Catalogued trail search hits now preview their one-line
   description; verifier extended + PASS, 0 console errors. `VERSION` bump owed.
2. `app_code_review_followups.md` **Group B** — ~~H1, M12, M4, M5, M8, M9+M10,
   M13~~ **ALL SHIPPED 2026-06-01.** v24 (committed, `c4e080c`) = H1+M12; **v25**
   (working tree, uncommitted) = M4+M5+M8+M9+M10+M13. Headless-verified by
   `playwright_verify_code_review_groupb.py` 15/15 + `feature_list`/`sfwda_multiply`;
   on-device feel/install-cost owed. **Only Groups C–D (refactor/polish) remain on
   the card. Next P1: Groups C–D, or the on-device pass.**

**P2 — decisions to unblock (bundle for one decision session):**

3. `pwa_qa_data_bakes.md` items 4 / 6 / 17 / E + `pwa_qa_2.md` item 9 (cemetery
   visibility) — all are "what's in-park vs region / which source / how big the
   AOI" calls. Answer once, then the bakes become P1.
4. `pwa_qa_2.md` item 6 — needs the user's cut-off instruction + a device session
   before touching a working logo-size cap.

**P3 — on-device verification pass (user confirms on the iPhone):**

5. The owed touch/GL confirms now sitting in `_done/pwa_qa.md` (7 pinch, 13 topo
   colors, 15 drawer-drag) + `pwa_qa_2.md` item 1 feel + whatever P1 Group B
   produces. One phone session clears the batch.

**P4 — refactor / polish (own pass, lowest):**

6. `app_code_review_followups.md` Groups C–D and the `10_deferred/viewer_polish_followups.md`
   residue — a11y on clickable divs, CSS hygiene, shared helpers, whitespace.

**Owed upstream (not codeable now):** ~110 un-catalogued trail names/descriptions
+ the trail license/publish gate (`trail_research_integration.md`); 11 null POI
blurbs + public-gate confirm (`_done/copy_review_surface.md`).

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
