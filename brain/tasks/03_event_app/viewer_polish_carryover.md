# Viewer Polish — Sprint 02 Carryover

The `[]` punchlist that didn't ship in Sprint 02. Carried into Sprint 03 so the
event-app work doesn't start on top of half-finished chrome.

Source of the dump: `../02_edit/tasks.md`. Triage that put items in buckets:
`../02_edit/_readme.md`. Two items closed under Sprint 02 even though the `[]`
marker still appears in the dump (the AOP + Rock Warblers logos — shipped in
`../02_edit/_done/branding.md`). One item is already on a written card
(`../02_edit/hot_control_two_lane.md`) but the acceptance list is still open.

#aop #sprint #03_event_app #carryover #chrome #polish

-----

## Source

- `../02_edit/tasks.md` — raw user dump, kept verbatim.
- `../02_edit/_readme.md` — Sprint 02 triage.
- `../02_edit/hot_control_two_lane.md` — in-flight, acceptance list pending.
- `../02_edit/_done/branding.md` — closed; logo size + add-image-workflow
  follow-ups owed and pulled into this card.
- `../02_edit/_done/preset_persona_review.md` — closes the "trails default view"
  question; the `[] Improve view` line tags back here.
- `../01_mvp/_done/code_health_pass.md` — Pass 3 closed; the `[] css review`
  and `[] code smells` lines re-enter as Pass 4 scope here.
- `../01_mvp/_done/community_trails_import.md` — owner of the
  numbered-trail-name research.

## Scope

Six lanes. Order below is recommended execution order, not card layout.

### Lane 1 — Finish the two-lane hot control

The user line *"hot coming up being a calendar notification does not make
sense.... I think hot should be only activate the heatmap"* already has a card.
That card is written but the acceptance list is `[ ]` all the way down. Close
it before opening anything new on this list.

- Driver card: `../02_edit/hot_control_two_lane.md`.
- Why first: it's in-flight, it touches the same chrome region as Lane 4, and
  Lane 4's icon work has nothing to land on until the two-lane shape ships.

### Lane 2 — Calendar UX, finish what mobile started

Sprint 02 B4 shipped auto-collapse on narrow viewports plus a current-time
indicator. The inverse direction and the scroll-into-view item never landed.

- `[]` Expand calendar on large screens. Counterpart to the ≤760 px
  auto-collapse. Right now a wide viewport still respects the persisted
  `aop_calendar_collapsed_v1` flag. Add a first-load expand for ≥1024 px
  (or whichever breakpoint the chrome already uses) so a desktop user lands
  with the calendar open. Persisted user choice should still win over auto.
- `[]` Scroll to the current calendar item. The B4 work tagged each `<li>`
  with `data-session-state`. On load and on every 60 s tick, scroll the
  `happening` or `upcoming_next` row into the visible slice of the calendar
  pane. Use `scrollIntoView({ block: 'nearest' })` so a manual scroll
  doesn't get yanked away once the user has moved.

### Lane 3 — Chrome consistency on collapse controls

Two related items from the dump. The screenshot evidence is the right toolbar
on the viewer.

- `[]` Invert all collapse icons on the right toolbar. Spec is ambiguous;
  read it as "every collapse chevron should point the same direction in the
  same state." Pick one convention (collapsed → ▸, expanded → ▾) and apply
  uniformly across `.section-toggle`, `.layer-expand`, panel `.tune-control`,
  any other collapser in the right rail.
- `[]` Fix styles on the section-toggle chevron button so it inherits the
  same border treatment as the other collapse icons. User line: *"buttons
  dont have the same border treatment as the other collapse icons. we want
  all buttons to be uniform in style and format. only thing that can be
  different is icon or color."* The `.section-toggle` selector is in the
  Pass 3 `!important` cluster (`../01_mvp/_done/code_health_pass.md:207`).
  Refactor lands here, not in Pass 4.

### Lane 4 — Layer policy audit

A2 (`../02_edit/_done/views_and_defaults.md`) shipped a working answer to the
"always on" question — buildings, water, roads, plus the inherited Sprint 01
defaults (landcover, trails, boundaries, trailheads, visitor-context, editor
POIs, brand logos). The `[] ON ALL LAYERS` header in `tasks.md` is the audit
that confirms it.

- Inventory the current default-on set across fresh load + Park + Topo + Trace
  presets. Walk every `BUILT_IN_PRESETS.*.toggles` entry plus the fresh HTML
  `checked` attributes.
- Cross-check the user line: "buildings / water / road" always; "bottom
  layer / topo / trails / waypoints" sometimes.
- Output: a short table in `../../research/viewer.md` (or extend
  `views_and_defaults.md`) listing each toggle and its default state per
  preset. Not a code change unless the audit surfaces a real gap.

### Lane 5 — Branding follow-ups

Both flagged in `_done/branding.md` "Next Work" and on the dump as `[]`.

- `[]` Ability to edit size on images. `TUNABLE_LAYERS.brandLogos` currently
  exposes opacity only — raster icons skip color/width sliders. Add an
  `icon-size` slider that writes back to the per-feature `icon_size`
  override (paired with `applyBrandLogoOverrides`). Range 0.25–2.0, step
  0.05. Persist alongside the existing coordinate override.
- `[]` Document workflow for adding images. The provenance README at
  `../02_edit/assets/branding/README.md` covers raw-zone hygiene but not
  the viewer-side steps (drop into `website/assets/branding/`, add a Point
  to `aop_brand_logos.geojson`, name the `icon_image`, register via
  `map.addImage`). Write that as a short numbered runbook either in the
  branding card or as a new `../../spinup/add_image_to_viewer.md`. Decision
  goes in the card's `## Decisions` block when work starts.

### Lane 6 — Visual + code review passes

These three lines from the dump are bigger than this card on their own. They
re-enter the sprint as a focused pass.

- `[]` CSS top-to-bottom. Pass 3 hoisted six palette tokens and replaced 49
  call sites; the rest of the stylesheet was out of scope. A real
  top-to-bottom pass means font shorthand audit, spacing-scale audit,
  `!important` cluster (deferred twice now), inline-`display` hygiene, and
  the un-tokenized hex literals outside the palette set. Drive it from
  `../01_mvp/_done/code_health_pass.md` "Out of Scope" block (start a Pass 4
  card under `01_mvp/`).
- `[]` Theme review. Distinct from CSS smells. Decide whether the cream /
  brown / rust palette earns its current contrast on every label layer
  (Trace halo work in Sprint 02 B5 was a point fix, not a theme decision).
  Cross-reference `../../northstar/personas.md` — driver in sun, spectator
  on phone, marshal at dusk.
- `[]` Code review for smells. Pass 3 caught the Sprint 02 churn smells.
  Anything new gets caught in Pass 4 alongside the CSS work, scoped to
  "adjacent code being touched" per the standing rule.

### Lane 7 — Numbered trail names (research, not code)

- `[]` See if we can get trail names — they are numbered. No new card; this
  is the existing SFWDA transcription follow-up on
  `../01_mvp/_done/community_trails_import.md`. Listed here so the carryover
  doesn't quietly drop the user's directive. Owner stays with the community
  trails card; this card just points.

## Already closed

These `[]` markers in `tasks.md` are already done; left in the dump per the
`preserve_card_directives` rule, but no work owed:

- `[] add aop logo` → shipped in `../02_edit/_done/branding.md`.
- `[] add rock warblers logo` → shipped in `../02_edit/_done/branding.md`.

## Recommended order

1. **Lane 1** — finish the two-lane hot control (in-flight, frees the chrome
   region).
2. **Lane 2** — calendar expand + scroll-into-view (small, closes the B4 wave).
3. **Lane 3** — collapse-icon uniformity (small, visible win across the right
   rail).
4. **Lane 4** — default-layer audit (verification, not new code; flushes any
   silent gap before event-app work piles new toggles on top).
5. **Lane 5** — brand-logo size slider + add-image runbook.
6. **Lane 6** — Pass 4 CSS + theme review (block of focused time; defer if
   adjacent code is quiet).
7. **Lane 7** — pointer-only; no scheduling owed here.

Sprint 03's main thrust (`full_loop_crud_upload_audit.md`) can start in parallel
with Lanes 4–7. Lanes 1–3 should land first so the event-app work isn't building
chrome on top of half-finished chrome.

## Acceptance

Lane-level — each lane's individual card carries the per-item acceptance. This
card is closed when:

- [ ] `hot_control_two_lane.md` acceptance is all `[X]`.
- [ ] Wide-viewport first load shows the calendar expanded, narrow still
      auto-collapses, persisted user choice survives reload either way.
- [ ] On load and on each 60 s tick, the `happening` / `upcoming_next` row
      sits inside the visible calendar pane.
- [ ] Every collapse chevron in the right rail uses the same icon convention
      and the same border treatment.
- [ ] A short default-layer table exists in `research/viewer.md` (or extends
      `views_and_defaults.md`) and matches what the viewer actually ships on
      fresh load + each preset.
- [ ] Brand logos have a working size slider; `aop_brand_logos_overrides_v1`
      persists `icon_size`; reload survives.
- [ ] A short add-image runbook exists somewhere a human can find it
      (branding card or `spinup/`).
- [ ] A Pass 4 card exists under `01_mvp/` carrying the CSS + theme + code-smell
      scope; this card stops being the holder.

Numbered-trail-name research is **not** part of this card's acceptance — it
lives on the community-trails card.

## Verification

Lanes 1–3 + 5 ride existing Playwright verifiers; extend assertions per lane:

- `mvp/scripts/playwright_verify_event_schedule.py` — calendar expand on wide,
  auto-collapse on narrow, scroll-into-view on tick.
- `mvp/scripts/playwright_verify_brand_logos.py` — size slider drives the
  rendered `icon-size` and persists to localStorage.
- New or extended verifier for the hot-control two-lane work — already on
  `hot_control_two_lane.md` acceptance.

Lane 4 verifies by inspection of the table against the viewer's `BUILT_IN_PRESETS`
constant; no new automated check.

Lane 6 verifies by re-running the full 18-verifier sweep after the Pass 4 work
lands (same posture as Pass 3 close).

## Out of Scope

- Public submissions, event setup CRUD, upload moderation — all on
  `full_loop_crud_upload_audit.md`. This card is chrome carryover only.
- Numbered trail name transcription (research lives on community-trails card).
- Offline / PWA (still parked on `../10_deferred/offline_pwa.md`).
