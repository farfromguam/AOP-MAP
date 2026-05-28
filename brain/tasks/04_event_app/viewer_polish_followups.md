# Viewer Polish Follow-ups

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
- `calendar_group_icon_review.md` (item 16 pending-pick card)
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
- [ ] Assert every Publishable editor row carries a `>`/expand control where expected.
- [ ] Assert each exportable section header carries `⧉`, and the panel header carries global `⧉ Export all`.
- [ ] Decide whether `Layer notes` deserves a section export action. Current leaning: no, because it is prose/tooling, not layer state.
- [ ] Consider a "next up" marker in the event-schedule feature list once real event CRUD exists.
- [ ] **2026-05-27 — `playwright_verify_feature_list.py` `data-section="publishable"` assertions are stale.** Three failures: `publishable: ↑ Export button present`, `publishable payload carries visitor_context_overrides`, `publishable payload carries visitor-context-fill paint`. `grep -c publishable website/index.html → 0` — that section does not exist; the toggles that the verifier expects there (`#showVisitorContext`, etc.) now live inside `data-section="editor"` after the editor unified-tree rework. Decision (pre-existing): either re-introduce a `publishable` section that owns the publishable-promotion contract, or rewrite these three assertions to read from `editor` and document that "publishable" is no longer a separate UI surface. Surfaced by `editor_unified_tree.md`; not caused by it.
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
- [ ] Pick a calendar-group icon candidate from `calendar_group_icon_review.md` and wire it into the live left-rail chip / tab strip.
- [ ] Retire old comparison mockups after choices land. Full inventory at time of 2026-05-27 misc_3 triage: `website/leftrail_*.html` (~40+ files), `website/poi_crud_*.html`, `website/calendar_placeholder_*.html`, `website/calendar_group_icon_review.html`, `website/load_animations.html`, `website/park_bounds_icon_review.html`, `website/hot_glyph_options.html`, `website/button_icon_picker.html`.
- [ ] Keep one left-sidebar comparison surface for layout/CSS review.
- [ ] Keep one right-panel comparison surface for layout/CSS review. Current candidate is `website/poi_crud_compare.html` with V1 chosen; decide whether to keep the compare page, keep only `poi_crud_v1_accordion.html`, or replace it with a newer right-panel baseline.
- [ ] Remove stale variant files only after the winning behavior is documented in the owning card.

## Process

- [ ] Add a tiny `decisions/` log pattern for future multi-variant explorations before pruning artifacts. It should capture short variant summaries and why the winner won.

## Acceptance

- [ ] No known viewer-polish follow-up is stranded only inside a Sprint 03 `_done` card.
- [ ] Critical gaps have focused Playwright coverage or a named reason for manual-only verification.
- [ ] Load animation remains either backlog-only or ships with state-safe startup proof.
- [ ] Code-health leftovers are closed honestly, not carried as inert checkboxes.
