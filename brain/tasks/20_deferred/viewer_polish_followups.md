# Viewer Polish Follow-ups

> **Deferred — Sprint 04 triage (2026-05-30).** This is an open follow-ups /
> verifier-residue backlog. A handful of items shipped (marked `[x]` inline);
> the bulk are open and the Acceptance section is unmet. **Deferred because** it
> is a standing polish backlog waiting on focus, not a discrete deliverable —
> pull individual items into an active sprint as they earn priority.

Sprint 03 shipped the big viewer chrome moves. This card is the residue worth
keeping visible in Sprint 04.

If a follow-up is just "nice someday," punt it. If it protects trust,
readability, or verifier coverage, land it.

#aop #04_event_app #viewer #polish #verifiers

-----

## Source

- `../03_event_app/_done/code_health_pass_4.md`
- `../03_event_app/_done/left_panel_poi_browser.md`
- `../03_event_app/_done/left_rail_collapse_tabs.md`
- `../03_event_app/_done/right_panel_editor_consistency.md`
- `../03_event_app/_done/load animations.md`
- `../03_event_app/_done/sprint_02_critique_followups.md`
- `../03_event_app/misc_3.md` (items 14, 16; routing block 2026-05-27)
- `calendar_group_icon_review.md` (item 16 — resolved 2026-05-29)
- `calendar_placeholder_state.md` (item 13 pending-pick card)
- `../backlog/load_animation_intro.md`

## Left Rail

- [ ] Audit mobile <=760 px drawer treatment: full-width behavior, tiny-screen `--tab-h`, and no overlap with bottom/right panels.
- [ ] Confirm `.left-tab` naming collision between app tabs and old mockup variants cannot leak specificity into live viewer CSS.
- [ ] Keep load-animation intro out of normal startup unless it satisfies the backlog guardrails: no saved-state override, no visible collapse/reopen cycle, no second camera reset, respects `prefers-reduced-motion`, and has focused verifier coverage.

## POI Browser

- [ ] Add dedicated `playwright_verify_left_poi_browser.py`.
- [ ] Cover placeholder chip count, click-row fly, popup HTML, and source-layer auto-enable.
- [ ] Decide whether the `owed_work` array should render in the POI tab or stay as JSON-only reviewer metadata.
- [ ] Decide whether Drawn POIs deserve a visible group for first-time visitors, or should hide until at least one highlighted user POI exists.

## Right Panel

- [ ] Add dedicated `playwright_verify_right_panel_consistency.py`.
- [ ] **2026-06-03 — panel hygiene beyond the editor (routed from the editor v1 pass).** The editor v1 (`../04_event_app/editor_v1_editable_layers.md`) deliberately stayed on the editing surface and left these owner/content calls: (a) the **"Comparisons" / Review section** ships dev-mockup links (`copy_review.html`, `icon_master.html`, the `*_compare.html` pages) to end users — hide behind `?debug` or retire once choices land; (b) the **"Layer notes"** section is 9 `<small>` paragraphs of dev-facing prose taking ~15% of panel height — move to a help affordance; (c) the **`#showTrailheads` orphan toggle** (hidden in `#legacyLayerToggles`, registration early-returns — publish.geojson ships 0 trailheads); (d) **orphan paint specs** for `activityHotspots` / `syntheticActivity` (registered, no editor host); (e) **dead export plumbing** — `exportSectionToClipboard` / `exportAllToClipboard` are now unwired (buttons removed) but left in place — remove once confirmed unused by preset save; (f) **dead row CSS already removed** in the v1 pass (`.feature-move/.feature-lock/.feature-tag/.feature-size-control`). Each needs an owner yes/no before deletion.
- [ ] Assert every Publishable editor row carries a `>`/expand control where expected.
- [ ] Assert each exportable section header carries `⧉`, and the panel header carries global `⧉ Export all`.
- [ ] Decide whether `Layer notes` deserves a section export action. Current leaning: no, because it is prose/tooling, not layer state.
- [ ] Consider a "next up" marker in the event-schedule feature list once real event CRUD exists.
- [ ] **2026-05-27 — `playwright_verify_feature_list.py` `data-section="publishable"` assertions are stale.** Three failures: `publishable: ↑ Export button present`, `publishable payload carries visitor_context_overrides`, `publishable payload carries visitor-context-fill paint`. `grep -c publishable website/index.html → 0` — that section does not exist; the toggles that the verifier expects there (`#showVisitorContext`, etc.) now live inside `data-section="editor"` after the editor unified-tree rework. Decision (pre-existing): either re-introduce a `publishable` section that owns the publishable-promotion contract, or rewrite these three assertions to read from `editor` and document that "publishable" is no longer a separate UI surface. Surfaced by `editor_unified_tree.md`; not caused by it.
- [x] **2026-05-28 — editor-three-bucket V3c review polish (loudest 3).** Post-ship review of `_done/editor_three_buckets_v3c.md` (see brain handoff `session_context.md`). Fixed in `website/index.html`: (a) brand-logo row name column was crushed to ~8 px wide because three nested left-paddings (`.editor-bucket-body` 22 px + `.editor-subgroup-body` 20 px + `.feature-list-rows` 22 px) ate the row's horizontal budget; reduced bucket/subgroup padding-left to 8 px and zeroed `.editor-bucket-body .feature-list-rows` padding-left — name column now reads "AOP badge" / "Rock Warblers" on one line alongside the size slider. (b) Sub-group collapsed chevron pointed up (`▴`) instead of right (`▸`) because JS set `textContent = '▸'` *and* CSS applied `transform: rotate(-90deg)` to the same element; dropped the CSS rotation so the JS glyph toggle (▾/▸) matches the bucket-chev behaviour. (c) Redundant inner "● POI 1/1" feature-list-group-head inside each Drawn POIs sub-group: the bucket already announces the geometry kind, so the inner head was three-deep nesting saying the same thing; added `.editor-bucket-body .feature-list-group-head { display: none; }`. Verified: `playwright_verify_poi_editor.py` PASS; `playwright_verify_presets.py` still fails only on the pre-existing mobile-overlap 4 px boundary already routed in the V3c card.
- [x] **2026-05-28 — Drawn POIs sub-group head flattened into the bucket head.** Follow-up to the above pass after user spotted lingering nesting: every bucket carried a "● Drawn POIs" sub-group head right under its bucket head ("● Point" / "╱ Line" / "▭ Polygon"), and the two bars were near-clones (chevron + bulk + dot + label + count). Drawn POIs is always the bucket's primary content — reference sources (Trailheads / Brand logos / Visitor context) are the real second axis. Hid the Drawn sub-group head and zeroed its body padding so drawn rows render flush in the bucket body; empty-state placeholder for Drawn dropped (the bucket's `+` is the create action). Reference sub-groups keep their full heads. Three loose CSS rules on `.editor-subgroup[data-source="drawn"]` at `website/index.html:384–393`. Verifier impact: `playwright_verify_poi_editor.py` clicked `[data-editor-source-bulk="line-drawn"]` for the showEditorPois mirror test; that bulk is now display:none so Playwright actionability blocked the click. Updated the assertion to use the Line bucket-level bulk (`[data-editor-bucket-bulk="line"]`) — same wiring, since Line's only source is drawn. Full PASS.
- [x] **2026-06-03 — Park buildings (Derived) feature rows: name column crushed to 0 px.** User: "Park buildings (curated, drag to adjust) all edit is o one line and I cannot read the names. this is broken." Reproduced by observation (served `website/` on :8042, opened Derived layers → `toggleTunableExpansion('buildings')`): the three public-facility rows (880/1010/1033 Ellis Cove) rendered their addresses **one character per line** vertically while the controls jammed onto one line. Root cause: `buildings` is the only layer that puts the `#tag` input **on the row** (`taggable && !inlineEditor`; `editorPois` is taggable too but `inlineEditor:true` moves its tag into the accordion — `main.js:3810`). The shared `.feature-row` grid is `18px · minmax(0,1fr)[name] · tag(84px) · copy · fly · move · lock`; inside the 380 px `#layerEditor` the wide tag input + four icon buttons consumed the whole row, collapsing the only flexible column (name) to **0 px** (measured `nameWidth:0`, `grid-template-columns: 18px 0px 94px …`), so `overflow-wrap:anywhere` broke the address per-character. **Fix (general, not buildings-only):** rows that carry the row-level tag get a `has-tag` class (`main.js`, in the tag-input block) and a two-line CSS layout (`website/css/app.css`, after `.feature-row.move-target`): `grid-template-areas: "vis name name name name name" / "tag tag copy fly move lock"`. Name now reads full-width on line 1 (measured `nameWidth:257`), tag input + ⧉/🎯/✋/🔒 sit on line 2. `has-tag` never co-occurs with `has-highlight` (buildings aren't highlightable) so the base grid override is safe. `#appVersion`/`sw.js VERSION` **v28→v29** (shell-asset change; invalidates the cached broken css/js). Verified by observation: `playwright_verify_buildings.py` **PASS, 0 console errors**; `playwright_verify_feature_list.py` buildings panel + all-5-curated + cemetery/brand/visitor rows PASS, only the **documented pre-existing** `publishable: ↑ Export button present` stale-section FAIL remains (line 52 above), 0 console errors. UNCOMMITTED (user's git gate); on-device read-confirm owed.
- [x] **2026-05-31 — expanded edit panel could not scroll long content.** User: "i cant seem to scroll in it anymore." Root cause in `togglePanel` (`website/index.html`): the scroll container is `.panel` (`overflow-y:auto`, capped at viewport height) wrapping `.panel-body` (`overflow:hidden`) whose `max-height` is animated for the collapse. The expand branch set `panelBody.style.maxHeight = scrollHeight + 'px'` and relied **only** on a `transitionend` to clear that cap — but the first expand animated from computed `max-height:none` (the `collapsed` class is removed before measuring), and browsers fire **no `transitionend` when animating from `none`**. So the cap stuck at the expand-time `scrollHeight` (~402 px, measured with inner sections collapsed); opening any section grew content to ~3220 px, which was then clipped by `overflow:hidden` with no way to scroll to it (`.panel` had nothing to overflow). **Fix:** expand now animates from an explicit `0px` (so the transition runs and `transitionend` reliably fires), and a `setTimeout(360ms)` safety net plus a `dropCap` guarded by `!panelCollapsed` clear the inline cap unconditionally — the body then grows to natural height and `.panel` scrolls. Reproduced + verified by observation (Playwright on :8001): pre-fix `panel_canScroll:false`, cap stuck `402px`, `scrollTop` 0; post-fix cap `(none)`, `panel_canScroll:true`, `scrollTop` reaches max (2496), collapse/re-expand/rapid-toggle cycles all settle clean, 0 console errors.
- [x] **S3 review 2026-05-27 — collapsed panel swallows feature-click reveal.** `revealFeatureInPanel` at `website/index.html:3226` opens the containing section, expands the editor row, and scrolls into view, but if the user has the panel collapsed (`panelCollapsed === true`, toggle at `:1111`) all that work happens behind a closed panel. Affects every map-click → panel reveal path: buildings, cemeteries, visitor-context, brand-logos, and the new S3 drawn-POI map-click → inline-accordion editor (`bindEditorClick` at `:8424`). The S3 inline-editor card promises "Map-click on a drawn POI opens the panel editor" — collapsed-panel silently breaks that promise. **Shipped 2026-05-27:** auto-expand path chosen — `revealFeatureInPanel` at `website/index.html:3149` now calls `togglePanel()` when `panelCollapsed === true`, preserving the Sprint 03 promise across all reveal paths. User can re-collapse if intentional. New assertion block added to `playwright_verify_feature_list.py` "0) Collapsed-panel auto-expand on reveal" (collapse → reveal → assert `panelCollapsed === false` + drawer expanded). Full suite PASS.

## Left Rail (S3 review 2026-05-27)

- [ ] **`lrOpenCard({ auto: true })` suppression is too broad.** Gate at `website/index.html:8967-8975` is `options.auto && lrHasSavedState && !lrOpen[c]`. `lrHasSavedState` flips true on the **first** drawer click of any card, not just on a user-close of the target card. Scenario: fresh viewer, no saved state → user opens search by clicking → save fires → later hot data arrives → `lrOpenCard('hot', { auto: true })` suppresses because `lrHasSavedState`, so the Hot tab never auto-opens even though the user never closed it. The `left_rail_collapse_tabs.md` card describes the intent as "auto-open respects a saved user-close state" — the implementation is "any saved state suppresses auto-open." Verifier `playwright_verify_left_rail_drawer.py:153-174` covers the user-close-hot path but not the user-opens-search-then-hot-arrives path. Fix needs per-card user-close tracking (e.g. a `lrUserClosed[c]` map) so search interaction doesn't silence hot auto-open.

## Code Health

- [ ] Revisit the adjacent-JS-smell acceptance row from Pass 4. If no concrete smell exists, close it explicitly instead of carrying a fake task.
- [ ] Tokenize the four remaining repeated hex literals only when the role names are clear: `#d8d0bd`, `#bbb`, `#f7f1e2`, `#fff8e8`.
- [ ] Extend the presets verifier to cover the five new trace-preset label-halo overrides if the verifier is touched again.
- [ ] Decide whether named-feature-tagging camera tolerance should tighten from `5e-4` degrees once data densifies.
- [ ] **S3 review 2026-05-27 — normalize tab/space indentation drift in inline script.** 90 lines start with a literal `\t` (one tab) while the surrounding file uses 4-space indent. Concentrated in S3-shipped blocks: `resetDefaultPavilionTagRuntime` (`website/index.html:2995-3011`), `resetFeatureListRuntimeDefaults` (`:3013-3024`), `refreshFeatureListData` (`:3295-3303`), `BUILT_IN_PRESETS` opening/closing (`:3949`, `:4220`), `rebuildEventScheduleData` partial (`:5342-5365`), `resetViewerState` partial (`:5471-5518`), and the boot block at `:8493-8498`. Behavior-identical; the cleanup keeps future diffs reviewable. Stand-alone bite — don't ride along with semantic changes in the same regions.
- [ ] **S3 review 2026-05-27 — `registerFeatureListLayer` → `rebuildEventScheduleData` → `refreshFeatureListData` double-work.** First registration of `eventSchedule` runs `applyFeatureListFilters` + `persistFeatureVisibility` inside `registerFeatureListLayer` (`:3347-3348`), then `rebuildEventScheduleData` (`:3355`) immediately calls `refreshFeatureListData` (`:5363`) which rebuilds state + filters again. Same on every subsequent register pass for any layer that triggers a tag rebind. Wasteful but not broken; document or guard if perf shows up on the profiler.
- [ ] **misc_4 2026-05-27 — Trail-lane verifier vs. hot-button toggle behavior.** `playwright_verify_event_schedule.py` Trail-lane click tests expect a click on `#showActivityHotspots` to flip the lane ON, but the button handler treats a click while the lane is already selected as a toggle-OFF — `hotButtonFlyToHotspots` is only called on the off→on edge. 6 pre-existing FAILs surfaced during the misc_4 pass, not caused by misc_4. Either rewrite the test to deselect first, or change the handler so a click on an already-selected trail lane re-runs `hotButtonFlyToHotspots` without flipping state.

- [x] **2026-05-27 — `bindPanelReveal` missing draw-mode guard.** `playwright_verify_poi_editor.py` failed at `#drawFootprintBtn` click because the 3rd POI placement at (720, 470) landed on a `visitorContext` callout, and the generic `bindPanelReveal` (`website/index.html:3203`) fired `revealFeatureInPanel('visitorContext', ...)` alongside Terra Draw's point commit. `toggleTunableExpansion` at `:4574` auto-collapses the editor section when expanding a drawer outside it (so the inline editor "dominates"), so the next click landed in a collapsed section. **Fix:** added `if (draw && draw.getMode && draw.getMode() !== 'static') return;` to `bindPanelReveal`, mirroring the existing guard in `bindEditorClick` at `:8350`. `playwright_verify_poi_editor.py` and `playwright_verify_feature_list.py` both PASS after the change. Affected every layer with `bindPanelReveal`: buildings, cemeteries, visitor-context, brand-logos, event-schedule anchors — none of them should pull reveal focus while the user is actively drawing.

## Mockup Cleanup

- [ ] Pick and wire one calendar loading placeholder variant from `calendar_placeholder_state.md`.
- [x] **2026-05-29 — Calendar-group icon picked and wired.** Candidate A (Clipboard + ruled lines) lifted into `#lrTabCal` SVG. Compare page retired. See `calendar_group_icon_review.md`.
- [x] **2026-06-13 — BULK RETIREMENT DONE (77 files deleted; `website/*.html` 119 → 42).**
  Settled-choice mockups removed; choices live in `index.html`/`panel.js` and the
  owning cards (re-verified against `index.html`'s own ✓/◌ Comparisons status board).
  - **Deleted (applied, choice landed):** `bottombar_*` (9; V5 FAB), `floatgroup_*`
    (5; V2), `editor_unified_*` (8; V3c), `add_any_type_*` (5; V2), `poi_crud_*`
    (4; V1), `editor_dock_types_compare` (1), `hot_glyph_options` (1),
    `button_icon_picker` (1), `topo_{color,trail,trail_orange}_compare` (3; sienna/
    V1 bg/O6), `right_sidebar_{a_slim,b_chips,c_dock}` (3; old A/B/C, superseded by
    the v1–v4 rebuild), and 26 non-survivor `leftrail_*`.
  - **Deleted (orphan, user-confirmed):** `mapborder_*` (11; no owning card, not
    referenced, superseded by the active `viewer_banded.html` Option-B band work).
  - **`index.html` Comparisons section:** 6 dead `<a>` links removed (bottombar/
    editor_unified/floatgroup/topo×3); 5 survive (copy_review, icon_master,
    leftrail_compare_v2, right_sidebar_compare, park_bounds_icon_review). Two stale
    `js/main.js` topo doc-comments repointed to the brain. `node --check` clean,
    served :8001 headless = **0 console errors, 5 Comparisons links render**.
  - **Reference integrity:** scanned all remaining `*.html`/`*.js` — no ref to any
    deleted file. Pre-existing dangling refs left untouched (out of scope): the
    kept `leftrail_*` survivors back-link a never-existent `leftrail_compare.html`
    (the v1 page, retired before this pass); `copy_review.html → res.html`.
  - No git op by this cleanup (per `no_commits.md`). The user subsequently committed
    the working tree — this cleanup bundled with parallel band/viewer work — as
    `87afe8f "cleanup & viewer work"`. Git-recoverable.
- [x] **Left-sidebar survivor kept:** `leftrail_compare_v2.html` + the 9 variants it
  iframes (`leftrail_current`, `eventflow_{focus,ribbon,timeline}`,
  `gates_{dash,horizon,tag}`, `tabs_{blaze,manilla,ruled}`) + `leftrail_motion`
  (referenced by the kept `load_animations.html`).
- [x] **Right-panel survivor kept:** the live `right_panel.html` is the right-panel
  baseline; `right_sidebar_compare.html` (+ its v1–v4 iframes) kept as the OPEN
  per-row edit-toolkit comparison. `poi_crud_compare.html` was already gone.
- [x] **2026-06-13 — last three pending sets resolved by the user; cleanup complete.**
  `website/*.html` 33 → 25 (119 at sweep start). The current live `index.html` is the
  clean viewer spike (`6b911ec`); the deleted compare/review pages were referenced only
  by the parked `old_index.html`, whose Comparisons section was trimmed to its 3 valid
  survivors (`copy_review`, `icon_master`, `leftrail_compare_v2`). No dangling refs.
  - **Calendar placeholder → V2 spinner.** Kept `calendar_placeholder_v2_spinner.html`;
    retired `v1_skeleton`, `v3_pulse`, `v4_dotprogress` + the throwaway
    `calendar_placeholder_compare.html` (4). **OWED:** wire V2 into the live calendar
    loading state — DEFERRED until the viewer spike settles (don't collide with the
    user's in-flight `index.html`/`viewer_core.js`). Card: `calendar_placeholder_state.md`.
  - **Park-bounds icon → dropped.** User: "nothing for park bounds icon." Retired
    `park_bounds_icon_review.html`. The `park_bounds_icon_apply` card's PB1–PB9 pick is
    abandoned for now (current `#zoomPark` SVG stands); its reference to the review page
    is now stale — update that card if the icon swap is ever reopened.
  - **Right-sidebar toolkit → dropped.** User: "nothing for right sidebar compare."
    Retired `right_sidebar_compare.html` + `right_sidebar_v{1_dock,2_takeover,3_split,4_sheet}.html`
    (5). The live right-panel surface is `right_panel.html` (kept); any wired toolkit
    behavior already lives in `panel.js`.
- [x] **2026-06-13 — data_editor BOTH axes decided; all 9 data_editor_* mockups
  retired except the winner config + the data-grid tool.** Architecture clarified:
  `js/data_editor_map.js` (KEPT, the shared engine) holds all layout+preview logic;
  the mockup HTMLs were 15-line config shims (`window.AOP_MAP_MODE` / `AOP_PREVIEW_STYLE`).
  - **Preview axis → A (popup).** User: "keep the v1 preview compare A — that's what we
    wanted to go with" (overrides the earlier card note leaning C/labeled-fields).
    Retired `data_editor_v1_preview_{b_phone,c_fields,d_chips,compare}.html` (4).
  - **Map-layout axis → V1 side (`AOP_MAP_MODE='side-right'`).** User: "that was decided;
    its first option was promoted to the one we just cleaned up." Retired
    `data_editor_map_{compare,v1_side,v2_drawer,v3_mapfirst,v4_overlay}.html` (5).
  - **Winner preserved:** the chosen combo (side-right map + popup preview) is fully
    captured in the KEPT `data_editor_v1_preview_a_popup.html` (`AOP_MAP_MODE='side-right';
    AOP_PREVIEW_STYLE='popup'`) + the engine `js/data_editor_map.js`. No design lost by
    deleting `data_editor_map_v1_side.html`. (NB: the standalone data-grid `data_editor.html`
    is the OLD grid-only tool, NOT the map fold — the combined map+editor lives in the
    a_popup page; the `data_editor_fold_into_production.md` fold went to the engine, not
    into `data_editor.html`.)
  - 9 files retired total this pass; `website/*.html` 42 → 33. Only the deleted compare
    pages referenced the deleted variants — no dangling refs (Witness-confirmed).
- [x] Tools/masters kept: `icon_master.html`, `data_sources.html`, `copy_review.html`.
  Products kept: `index`, `right_panel`, `data_editor`, `schedule_editor`, `viewer`,
  `viewer_banded`.

## Code-review refactor residue (from `app_code_review_followups`, 2026-06-01)

The app code-review card closed (`04_event_app/_done/app_code_review_followups.md`)
with these lowest-priority refactor items consciously deferred to their own pass —
no behavior change, no urgency. Pulled here so they're not stranded in a `_done` card.

- [ ] **L1 — whitespace.** ~88 leading-tab lines in the space-indented
  `website/index.html` (scattered ~4404–4429, ~7003-area, ~10255-area — original
  ranges drifted with v19→v25). Own whitespace-only pass; convert tabs→spaces matching
  each line's surrounding indent.
- [ ] **L2 — shared-helper extractions** (deferred subset). `loadObjectStore` (3
  identical `loadXStore` wrappers), `buildFeatureRow` (the ~250-line row builder —
  risky, coordinate with M5's in-place path), `clampRound`/`trimZeros`, a roads config
  array (~10 near-identical `addLayer` objects), `forEachTile` (3 tile-loop reimpls).
- [ ] **L9 — palette + dialog** (deferred subset). The raw-hex→`:root`-token sweep
  (dozens of sites; do with screenshot diffs to catch visual regressions) + a
  `#pwaIosHint` `role="dialog"` focus-trap/return-focus. (Dead `.left-context-card`
  rules already removed; `#message` intentionally KEPT — verifier load proxy, not dead.)
- [x] **Verifier rot — `session_tools` + `poi_editor` FIXED (2026-06-01).** Both
  crashed in headless because the v25 full-bleed `position:fixed` `#map` canvas now
  overlaps the right-panel buttons' hit-test points, so a real `Locator.click` is
  intercepted by the canvas / sticky `#panelHeader` and retries until it times out.
  **Fix:** the shared `click_in_section` helper (`mvp/scripts/playwright_base.py`) now
  dispatches the element's own `click()` via JS after expanding its section — the same
  dispatch `set_toggle` already uses for the same documented "real click times out"
  reason (the real handler still runs; only the synthetic-mouse hit-test, a headless
  geometry artifact, is bypassed). `poi_editor`'s panel-interior clicks
  (`editor-bucket-add` point/polygon/line, the inline-editor deletes, the line-bucket
  bulk) routed through it, and its stale `<title>` assertion fixed
  (`"AOP Map Viewer"` → `"Trail Blazing Invitational"`). `session_tools`' clock/reset
  buttons routed through it (its preset/tab/calendar clicks are not panel-interior and
  were never occluded). **Verified by observation (`:8001`, 2026-06-01):**
  `session_tools` ALL PASS / 0 console errors; `poi_editor` RESULT: PASS / 0 console
  errors. Regression-checked the helper's other callers: `community_trails` 16/16,
  `landcover` PASS.
- [ ] **`presets` verifier rot + gated assertion FAILs (own pass).** `presets` is the
  same click-rot class. Its first crash (the editor `.section-toggle` raw click) was
  fixed 2026-06-01 (JS-dispatch, mirroring the file's own line-387 pattern), which
  revives **51 checks** that now actually run. But it still (a) crashes again later in
  the "Inline layer tuning + snapshot" section on another panel-interior raw click
  (route the same way), and (b) reports 3 assertion FAILs: "visitor context lives with
  publishable map layers" + "source/reference inputs live under Source layers" — these
  two are the **decision-gated** publishable-section / OSM-section-move fails already
  tracked in the "Right Panel" block above (the editor unified-tree rework moved those
  sections; assertions await the reintroduce-section-vs-rewrite-assertion decision) —
  and "Topo restyles index contours", which was never being *reached* before (presets
  crashed earlier) so it needs a fresh look before assuming it's a real regression.
  Left as a flagged follow-up: `presets` is separately tracked and partly
  decision-gated, so it is not made fully green by the click-rot fix alone.

## Process

- [ ] Add a tiny `decisions/` log pattern for future multi-variant explorations before pruning artifacts. It should capture short variant summaries and why the winner won.

## Acceptance

- [ ] No known viewer-polish follow-up is stranded only inside a Sprint 03 `_done` card.
- [ ] Critical gaps have focused Playwright coverage or a named reason for manual-only verification.
- [ ] Load animation remains either backlog-only or ships with state-safe startup proof.
- [ ] Code-health leftovers are closed honestly, not carried as inert checkboxes.
