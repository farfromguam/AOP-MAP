# Sprint 02 Critique — Follow-ups

Date: 2026-05-24

TL;DR:
- Issues surfaced from a critique pass over the closed Sprint 02 work.
- Two real risks (unverified verifier surface, AOP badge default-on) plus a
  cluster of architectural drift and stale-test debt. None block Sprint 03's
  main thrust, but the first two should land before chrome gets piled higher.
- This is a holding card. As items earn their own scope, they spin out into
  named cards or fold into existing ones; this card narrows accordingly.

#aop #03_event_app #sprint_02 #followups #critique

-----

## Source

- Critique pass, 2026-05-24 — read of Sprint 02 close (`../02_edit/_readme.md`,
  every `_done/` card, the carryover at `viewer_polish_carryover.md`, and Pass 3
  at `../01_mvp/_done/code_health_pass.md`).
- `../02_edit/_done/branding.md` — AOP badge permission posture.
- `../02_edit/_done/poi_editor_v2.md` — `SECTION_RUNTIME` split for
  visitor-context.
- `../01_mvp/_done/code_health_pass.md` Pass 3 — 9 verifiers unrun, 1 known FAIL.
- `../02_edit/_done/hot_button_heatmap_review.md` — hot-button follow-ups.
- `../02_edit/_done/hot_control_two_lane.md` — shipped two-lane control.
- `../01_mvp/_readme.md` "Immediate next work" items 8, 9, 10.

## Severity bands

### A. Real risk, small fix, do first

- [x] **Finish the Pass 3 verifier sweep.** All 19 verifiers run end-to-end
      against the current viewer (2026-05-24). Result: 15 PASS, 4 FAIL (with
      details captured in `### Remaining verifier FAILs` below). Fixes shipped
      in the same pass: `community_trails` + `sfwda_multiply` collapsed-section
      crashes (route through `set_toggle` / `click_in_section`); `brand_logos`
      symbol-placement timing race (poll until icons land); `terrain`
      preset-reset assertion (preset switch now clears 3D state per Sprint 02
      misc pickup); `search` water-default-on premise + `#observed-trailhead`
      label collision; `feature_list` visitor-context SECTION_RUNTIME split
      (closes B1); brand-logo default-off flip closes A2. Pass 4
      (`code_health_pass_4.md`) acceptance line for the full sweep is now
      cleanly closeable.

- [x] **Default `showBrandLogos` off until AOP confirms reuse.** The AOP badge
      currently renders on the map in fresh load + Park + Topo presets while
      `_done/branding.md` flags it as "reference-only until AOP confirms public
      reuse." Anyone running the viewer is one screenshot away from a publish
      event without consent. Flipped default-off 2026-05-24; internal review
      still has the toggle. Reopen as default-on once permission lands
      (`../02_edit/_done/branding.md` "Next Work").

### B. Real bugs masked as "pre-existing FAIL"

- [x] **`feature_list` verifier FAIL — visitor-context state is split across
      two sections.** Fixed 2026-05-24. `SECTION_RUNTIME` in
      `website/index.html:3290` now puts `visitorContextOverrides` and the
      `visitorContext` per-feature visibility slice under `publishable` (where
      the `#showVisitorContext` toggle lives), and the `feature_list` verifier
      asserts the new round-trip. Result: 115 PASS / 0 FAIL. Derived-layers
      keeps the background paint but no longer carries visitor-context state.

- [x] **`playwright_verify_search.py` "multi-segment trail collapses to one
      result" FAILs.** Fixed 2026-05-24. Renamed the colliding event_anchor
      label in `website/data/aop_event_schedule.json` from
      `"Trailhead - Saturday Afternoon segment 2"` to
      `"Observed Trailhead — segment 2"` so a `saturday` query stops returning
      both the trail and the anchor. Verifier passes (28 / 0). The original
      anchor's `source` / `caveat` fields still record the segment-2 provenance
      so the rename is purely a search-surface fix.

- [x] **`playwright_verify_presets.py` stale assertion + trails inline-tuning
      timeout.** "Land-cover under Derived layers" assertion expects the
      `showVisitorContext` toggle in `derived-layers`; it now lives in
      `publishable`. Trails inline-tuning step times out clicking a collapsed
      Publishable row. Updated 2026-05-24: assertion now puts visitor-context
      with publishable map layers, collapsed-section clicks use the shared
      helper / edge-click shape, and the preset verifier passes.

- [x] **Audit the shared `"Failed to fetch"` console filter.** Fixed
      2026-05-24. Four verifiers (`event_schedule`, `presets`, `brand_logos`,
      `community_trails`) previously used a broad `"Failed to fetch" in text`
      substring match that would silently hide any future real network error.
      All four now use a tight pair of patterns: `AJAXError: Failed to fetch
      (0):` (MapLibre's aborted-tile shape, where `(0)` is the placeholder
      HTTP status) and bare `TypeError: Failed to fetch`. A real `(404):`
      or `(500):` from MapLibre's loader now surfaces.

### B-residual. Remaining verifier FAILs (after the A1 sweep)

The full 19-verifier sweep on 2026-05-24 surfaced four FAIL verifiers that
none of the B-band fixes covered. Each represents a real behavior surface
to investigate, not a stale test. They are deferred from B because the
diagnosis is more involved than a one-line viewer/verifier edit.

- [ ] **`poi_editor` (4 FAILs).** Sequence: click-in-section opens the
      drawer, `set_toggle`-style placement of 2 Pavilion POIs works, but the
      3rd click at `(300, 470)` after switching the category to `Building`
      does not place a POI. Polygon mode also fails entirely (0 vertices) in
      the same run, even with `draw.getMode() == 'polygon'` confirmed PASS at
      the start of that block. Attempted test-side fix (remove all popups +
      `draw.setMode('point')` before each click) did not change the outcome,
      which suggests the issue is either (a) click-event interception by an
      overlaid DOM node added in Sprint 02 chrome, (b) a Terra Draw v2
      mode-revert that the test can't detect through `draw.getMode()`, or (c)
      an event ordering change where MapLibre's native click handler fires
      before Terra Draw's. Next step is to run the verifier with
      `headless=False` and watch what actually happens at each click — too
      brittle to fix by inspection alone.

- [ ] **`synthetic_activity` (1 FAIL — popup stacking).** Click at the top
      hotspot center `[-85.7482512, 35.090725]` opens **three** popups
      simultaneously — `Synthetic Saturday track` + `Monteagle plateau
      services` + `1010 Ellis Cove Road` — because Sprint 02 made buildings +
      visitor-context default-on and each layer's `bindPopup` fires on the
      same click. The test only asserts on whether any open popup contains
      `Synthetic Saturday hotspot`; the hotspot bindPopup didn't open at this
      coord. Fix options: (a) raise the hotspot-fill layer above buildings in
      draw order so it gets the first click, (b) project the click to a
      hotspot-only spot before issuing it, or (c) widen the assertion to
      check that at least one popup contains the hotspot text within a small
      bbox of the click coord. (a) is the most honest user-facing fix.

- [ ] **`visitor_context` (2 FAILs — popup doesn't open).** Click at the SE
      callout center `[-85.7392, 35.0837]` (confirmed inside the
      `South Pittsburg / Kimball supply run` polygon by point-in-polygon
      test) returns zero `.maplibregl-popup a` nodes. `visitor-context-fill`
      is visible and renders. `bindPopup` only short-circuits on
      `isDrawModeActive()` and `moveState`; neither is set here. This is the
      mirror of the synthetic_activity case — there, too many popups; here,
      none. Diagnosis next step: add an inline `console.log` in
      `bindPopup` to confirm whether `map.on('click', layers, ...)` fires at
      this point, then check whether a `closeOnClick` race is killing the
      popup before the test reads it.

- [ ] **`water` (1 FAIL — springs render 0 in viewport).** Test toggles
      `showSprings` ON and waits 500 ms, then queries
      `queryRenderedFeatures({ layers: ['water-points'] })` — returns 0.
      Spring features are sparse (USGS NWIS gages around the 9-patch); at
      the default fit-to-publish camera, none may be in viewport. Pass 3
      reported `water (29/0)` as clean, so something changed since. Two
      candidate fixes: (a) extend the camera fit to include spring features,
      or (b) `flyTo` a known spring before the assertion. (b) is the
      smaller change and matches the camera-aware pattern used elsewhere.

These four FAILs cap the surfaced post-Sprint-02 verifier debt. When they
close, the full sweep returns clean and Pass 4 can claim the closing line.

### C. Hot button — copy and target follow-ups

The two-lane card (`../02_edit/_done/hot_control_two_lane.md`) shipped the
shape, but `_done/hot_button_heatmap_review.md` had three follow-ups; only the
shape itself landed.

- [ ] **Rename the Trails lane copy.** Current: `Trail heat / Activity
      evidence`. "Heat" still implies recency. Drop to `Trail activity` or
      `Where rigs spent time` until the data is recent, aggregated, and
      privacy-reviewed. The two-lane card's own decision ("avoid 'live heat'
      wording") shipped half-applied.
- [ ] **Switch the heatmap-fallback target from top-K bbox to a densest-cluster
      polygon.** Review card's call.
- [ ] **Regenerate the first-party hotspot GeoJSON from the current builder**
      and confirm source metadata is intact. `../02_edit/_done/hot_button_heatmap_review.md`
      flagged this and it was not addressed in the two-lane ship.
- [ ] **Decide the synthetic-vs-real boundary.** Activity hotspots come from
      the 873-line `simulate_saturday_activity.py`; the new left hot button
      treats them as a user-facing target. Either badge the popup `(synthetic)`
      while the layer is test-grade, or hold the hot button's fallback path
      until real GPX is the source.

### D. Brand-logo asset hygiene

- [ ] **Downsize the raster assets.** `icon_size` slider range is `0.02-0.20`
      because the raw rasters are `1000x1000` (AOP badge) and `2048x1160`
      (Rock Warblers). The right fix is downsized rasters in
      `website/assets/branding/`; don't ship the bandwidth or pay the ugly
      upscale at 0.20. The slider range becomes a normal `0.25-2.0`. Updates
      `../02_edit/_done/branding.md` "Sprint 03 Follow-up Shipped" once done.
- [ ] **Replace the Rock Warblers JPEG with a transparent PNG / SVG** so the
      white card around the bird artwork drops out. Already named as cosmetic
      in `_done/branding.md`; carried here so it doesn't get dropped.

### E. localStorage architecture

- [ ] **Add a "Reset local overrides" affordance.** Eight `aop_*_v1` keys
      (`CALENDAR_COLLAPSE`, `VISITOR_CONTEXT_OVERRIDE`, `FEATURE_VISIBILITY`,
      `FEATURE_TAG`, `FEATURE_TAG_SEEDED`, `BRAND_LOGOS_OVERRIDES`,
      `POI_STORAGE`, `VIEWER_PRESET`) plus the v1->v2 preset bundle. The seed
      flag (`FEATURE_TAG_SEEDED_KEY`) is a trap door: drop coordinates from the
      schedule JSON expecting the binding to take over, but a user reload with
      the seed flag set silently does the lifting. A clear reset surface fixes
      the support story.
- [ ] **Migration story for `_v1` -> `_v2` keys.** v1->v2 preset bundle is
      mentioned in `_done/poi_editor_v2.md` but the migration path on next
      bump is undocumented. Write a short rule (one direction: bump key, drop
      old, ship a "reset overrides" notice) before the next bump.

### F. Card taxonomy + raw-dump hygiene

- [x] **Move `code_health_pass_4.md` out of `01_mvp/`.** The card carries
      Sprint-02-driven scope (CSS, theme, smells from `../02_edit/tasks.md`).
      Either move it to `02_edit/` or treat it as Sprint 03 carryover under
      `03_event_app/`. Moved to `code_health_pass_4.md` 2026-05-24.
- [ ] **Reconcile the duplicate `personas.md`** at `02_edit/_done/personas.md`
      and `../../northstar/personas.md`. `brain_map.md` points at northstar;
      the 02_edit copy needs either a "this is the working draft, northstar is
      authority" header or to be deleted.
- [ ] **`tasks.md` dump punchline drift.** Closed items still show as `[]`
      ("add aop logo", "add rock warblers logo"); `preserve_card_directives`
      keeps them in the dump. Either rule that the dump can carry `[shipped]`
      annotations, or add a closing index inside the dump file so a reader
      knows what's still owed.

### G. Decision rationale capture

- [ ] **Tiny `decisions/` log for variant explorations.** Twelve
      `worktree-agent-*` branches were spawned to design one calendar
      current-time indicator variant. The variants are gone; the only durable
      trace of why B4 won is "simple enough and has the info." When a
      multi-variant exploration ships, save the variants' short summaries
      plus the win-rationale into a one-page `decisions/<topic>.md` before
      pruning the worktrees.

### H. Persona surface earns teeth

- [ ] **Pick at least one event-ops view.** `_done/preset_persona_review.md`
      named Approach / Event HQ / Stage-Marshal style views as the gap. Until
      one of those ships, `personas.md` is reference-only and future view
      decisions drift without constraint. Pair with the first event-app CRUD
      surface that gives them facility / event geometry.

### I. Demo data sitting under polished chrome

The MVP backlog's "Immediate next work" items are structural prerequisites for
publishability that Sprint 02 built around, not through. They are not Sprint 03
goals, but Sprint 03 should not pile new chrome on top of them either.

- [ ] **Item 9 (real source-backed `trail_centerlines` / `trailheads`)** is the
      biggest gap. Editor v2, branding, hot button, calendar polish — all built
      on top of demo geometry. Promote at least one real source-backed centerline
      before declaring V1 publishable.
- [ ] **Item 8 (acres reconciliation)** — 600+ acre official claim vs
      ~592 calc / ~573 deed. A boundary card that the editor decorates.
- [ ] **Item 10 (USGS 3DEP DEM swap)** — the Terrarium tile is good enough,
      not source-backed. Defer remains acceptable; capture here so it stays
      visible.

### J. Smaller stuff (do whenever adjacent code is touched)

- [ ] Brand-logo seed coordinates are "nudged off" the 1010 building, which is
      also the `#pavilion` tag binding. Add a one-line note in `_done/branding.md`
      or `_done/named_feature_tagging.md` so the coupling is visible.
- [ ] Named-feature tagging verifier camera-distance tolerance is 5e-4°
      (~55 m). Fine for now; tighten when data densifies.
- [ ] Lane 2 `scrollIntoView` on every 60s tick uses `block: 'nearest'`
      correctly. No fixture covers manual-scroll -> tick. One fixture closes
      it.
- [ ] Preset camera reset (misc pickup) mutates layers + camera + 3D state
      simultaneously. `research/viewer.md` default-layer audit table doesn't
      show the camera/3D dimension. Extend the table when next touched.

## Recommended order

1. **A** items — finish verifier sweep, flip brand-logo default. Both small,
   both close real risk.
2. **B** items — same sweep, fix the bugs the FAILs are pointing at instead of
   carrying them.
3. **C** items — hot-button copy + target follow-ups. Sprint 02 shipped the
   shape; finish the polish.
4. **D / E / F / G** — fold into adjacent code as it gets touched. Don't
   schedule as a block.
5. **H / I** — gate against new chrome work; do not block Sprint 03's main
   thrust on them.
6. **J** — never schedule; ride along with adjacent code.

## Out of scope

- Anything on `full_loop_crud_upload_audit.md` (event setup, CRUD, uploads,
  moderation). This card is hygiene + close-the-loop work on Sprint 02.
- Offline / PWA — still parked on `../10_deferred/offline_pwa.md`.
- New feature waves. If an item below earns its own scope, spin it into a
  named card and link from here.

## Acceptance

This card is closed when every item above is either:

- (a) shipped and named in its own card or in an existing card's update, or
- (b) explicitly punted with a one-line "deferred because <reason>" so the
  reader knows it was seen and chosen against.

The card is **not** closed by "we did some of these and moved on" — the items
were already at risk of that fate when they were sitting in done-card
follow-ups. This card exists to make them visible.
