# pwa_qa_2 — triage & implementation plan

> **EXECUTED 2026-05-31 → see the Disposition table in `pwa_qa_2.md`.** Items
> 1–5 shipped (verified by `playwright_verify_pwa_qa2.py`), 7 routed to
> `pwa_qa_data_bakes.md`, 6 left for a device session, 9 held.
>
> **Corrections to this plan (its code anchors were partly garbled by the prior
> session's corrupted channel — do not trust them blindly):**
> - The **calendar anchors were hallucinated.** No `#calCardHead` / `#calCollapse`
>   / `#calRefresh` / `.cal-act-icon` exist. The real calendar is `.calendar-card`
>   → `.calendar-heading` / `.calendar-days` / `.calendar-row`, inside the left-rail
>   drawer (`#lrPanelCal`, hook `window.lrCloseCard('cal')`). So **item 8**
>   ("icons not centered in their circles") has no target — no-op.
> - **Item 10's premise is false:** there is **no** `region` entry in
>   `BUILT_IN_PRESETS` (only park/topo/trace/satellite). The "Region zoom 13.74"
>   the plan cites is the **maxBounds zoom floor**, not a preset. Adding a region
>   preset is a fresh design fork, not the wiring tweak this plan assumed.
> - **Item 6's premise is false:** the icon-size cap is already a per-frame GPU
>   expression with `icon-allow-overlap`+`icon-ignore-placement` — there is **no**
>   deferred `setLayoutProperty` re-clamp to "bake in". The zoom-out overshoot is
>   GeoJSON-symbol parent-tile scaling (device/GL only).
>
> Original triage retained below for the reasoning trail.

Companion to `pwa_qa_2.md` (the user's raw QA list, 10 actionable items + "there
is more"). Every item lives in `website/index.html` (the 531KB single-file PWA).
This card pins the exact code surface, the fix approach, and acceptance criteria
for each, so a clean session runs them turn-key.

## Why no code shipped in the 2026-05-31 triage session

The tool channel intermittently corrupted reads of `index.html` — long/parallel
reads came back with duplicated tails and shifted line numbers (e.g. a read
"showed" `#presetRegion`/`mapOverlayControls` that a clean `grep` proved do not
exist). Single `grep`s were reliable; reads were head-reliable / tail-garbled.
Surgical edits to the live app through a channel that silently garbles the file —
with no reliable way to re-read and confirm the result, and with most of these
items only verifiable on a real device (GL render + touch + iOS safe-area, which
this viewer cannot confirm headlessly) — is exactly the hard-to-reverse case
`act_dont_ask.md` says to stop on, and breaks `verify_by_observation.md`.
**Restart Claude Code to clear the channel, then execute against the anchors
below.** First re-confirm each anchor with the grep line given.

## CONFIRMED anchors (from clean greps / read-heads, 2026-05-31)

- Version badge: `index.html:1059` →
  `<div class="util-version" id="appVersion" title="App build version">v18</div>`
- Attribution / info ⓘ: `attributionControl: false` @1474;
  `map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-left')`
  @1490; an "info / about popup wiring (the ⓘ that shows app + data credits)"
  comment sits just above ~1474. CSS note @358 re `.maplibregl-ctrl-bottom-left`.
- On-map preset row: `.map-preset-row#mapPresetRow` @879. Buttons:
  `#presetPark`@891 (`class="active"` default), `#presetTopo`@894,
  `#presetTrace`@897, `#presetSatellite`@900. **No `#presetRegion` / no
  `data-preset="region"` button exists** (grep-confirmed).
- Preset engine: `BUILT_IN_PRESETS` @5341; `applyPreset(presetId, options={})`
  @5711; button wiring `addEventListener('click', () => applyPreset(button.dataset.preset))`
  @10423; note @3008 — some layers are "out of every preset object so applyPreset
  never forces them -- default" (so layer defaults live partly outside presets).
- Calendar header: `.cal-card-head#calCardHead` @4595 → `.cal-head-left` >
  `.cal-head-title "Events"`; `.cal-head-actions` @4599 > `#calToday`@4600,
  `#calRefresh`@4601, `#calCollapse`@4602 — **a calendar collapse button already
  exists.** Body: `.cal-scroll#calScroll`@4611 > `.cal-month#calMonth`,
  `.cal-list#calList`@4613, `#calendarEmpty`, `#calendarError`; `.cal-resize#calResize`@4618.
- Calendar header CSS: `.cal-act`@431 (pill), `.cal-act-icon`@433
  (`padding:4px; width:26px; height:26px; display:inline-flex; align-items:center;
  justify-content:center`), `.cal-act-icon svg`@434 (16×16, `display:block`).
- Brand-logo size cap: CSS `.brand-logo-cap*` @502–510; `brandLogoCap` var @3899;
  `brandLogoIconSizeExpr()` @3915–3928 ("per-feature size × global cap × zoom
  factor"); applied via `setLayoutProperty('brand-logos-icons','icon-size', …)`
  @3940; `#brandLogoCapSlider`@3993.

## STILL TO LOCATE (grep first next session)

- Calendar-row click → open-event flow: the handler on `.cal-list` items that
  flies the map and shows the event tooltip/popup (items 1, 2). Try
  `grep -nE "calList|cal-item|cal-event|addEventListener.*cal|flyTo|easeTo|Popup|tooltip" index.html`.
- `#calCollapse` collapse logic + any mobile breakpoint (`grep -n "calCollapse" `,
  `grep -n "max-width" `).
- Layer keys for items 4/5/7: park bounds, OSM park polygon, OSM tracks, SFWDA
  traced trails (extracted), paper trail map, AOP trail-network merged, the
  9-patch raster, cemeteries. `grep -nE "park-bound|osm-park|osm-track|sfwda|paper|trail-network|nine|9.?patch|cemeter" index.html`.

---

## Per-item triage

### 1 — open-event jerk; tooltip must stay in window  · EXTRACT (device verify)
"the map moves to make the tooltip visible then jerks around; the tooltip on the
starting point should be in the window." Almost certainly the tooltip is shown
mid-flight and/or re-anchored every `move`, or the camera offsets to fit the
tooltip then re-settles. Fix: fly ONCE, show/anchor after `map.once('moveend',…)`
(not a `setTimeout`); if a `maplibregl.Popup`, let anchor auto + pass
`flyTo({padding})` so marker+popup fit; if a custom DOM tooltip, clamp final
position into the viewport. Acceptance: one smooth flight; popup appears settled,
fully on-screen even for edge events; no jitter at rest. Needs the open-event
flow (above) + on-device confirm.

### 2 — mobile: collapse the calendar after selecting an event  · EXTRACT (low effort)
A collapse button already exists (`#calCollapse`@4602). In the calendar-row
select handler, on phones only (`matchMedia` at the file's existing breakpoint),
invoke the same collapse path. Reopen via the existing control. Acceptance:
phone → pick event → calendar folds, map/event visible; desktop unchanged.

### 3 — move version into the ⓘ pill → "(i v18)"  · EXTRACT
Merge the standalone `#appVersion`@1059 "v18" into the bottom-left info/about ⓘ
(@1490) so the pill reads like `(i v18)`; keep the existing expand-on-click. The
ⓘ is MapLibre's compact `AttributionControl` (DOM is library-generated), so the
clean approach is to render the version into the custom about/info wiring near
~1474 (or a small sibling element styled next to the control), then remove the
`.util-version` badge. Acceptance: one pill shows "i v18"; tap expands info as
before; no separate badge remains. NOTE: this is the persistent app/about ⓘ.

### 4 — trace preset: disable park bounds, OSM park polygon, OSM tracks  · EXTRACT (config)
Edit the `trace` entry in `BUILT_IN_PRESETS`@5341 (or the default-layer wiring
flagged @3008) so those three layers are off in trace. Needs the real layer keys
(above). Acceptance: switching to Trace hides park bounds + OSM park polygon +
OSM tracks; other presets unchanged.

### 5 — disable SFWDA traced trails (extracted); keep paper-trail map + AOP merged  · EXTRACT (config)
Default the `sfwda` extracted traced-trails layer OFF while keeping the paper
trail-map raster and the merged AOP trail-network on. Same surface as item 4
(preset/default layer config). Acceptance: SFWDA extracted trails off by default;
paper map + merged network still visible.

### 6 — image max-size cap overshoots on zoom-out  · EXTRACT (perf; user note incomplete)
"as we zoom out … the image forgets it needs to stop growing and overshoots, then
shrinks down to its correct max size." The cap is applied via a deferred
`setLayoutProperty` (≈@3940) on top of `brandLogoIconSizeExpr()`@3915, so there's
a frame lag before the clamp lands. Fix direction: bake the cap INTO the icon-size
zoom expression (e.g. wrap the zoom interpolation in a `min`/clamp) so it's
enforced per frame instead of re-clamped after. **User's sentence is cut off
("see if we can change the …") — confirm intent before building.** Acceptance: no
visible grow-then-shrink on zoom-out; logos hold their cap continuously.

### 7 — bake Ellis cemetery into the derived dataset  · ROUTE → `pwa_qa_data_bakes.md`
Data-pipeline work (promote Ellis cemetery attributes into the derived/publish
set). Belongs with the other data bakes. The paired ask "stop showing other
cemeteries on the 9-patch in the park preset" is **RETRACTED** — see item 9.

### 8 — calendar top-right icons not centered in their circles  · EXTRACT (diagnose)
`.cal-act-icon`@433 ALREADY flex-centers a 16×16 SVG in a 26×26 round button, so
the off-center is most likely (a) the SVG ARTWORK not centered within its viewBox
(`#calRefresh`@4601 / `#calCollapse`@4602 glyphs — read their markup), or (b) a
`box-sizing` interaction with `padding:4px`. Diagnose by reading those two SVGs;
fix the artwork's viewBox/coords or normalize the box. Acceptance: glyphs
optically centered in both round icon buttons.

### 9 — "I actually like the cemeteries showing — let me think"  · HOLD (user deciding)
Explicit retraction of item 7's "hide other cemeteries." No action; the cemetery
visibility decision is the user's to make. Leaves item 7 = the Ellis bake only.

### 10 — on-map preset switch buttons: region, park, topo, trace, satellite  · EXTRACT
The on-map row `#mapPresetRow`@879 already has park/topo/trace/satellite but is
**missing region**. Add a `#presetRegion` button (`data-preset="region"`) reusing
an existing icon; the generic wiring @10423 will pick it up. Confirm a `region`
entry exists in `BUILT_IN_PRESETS` (handoff cites a Region zoom 13.74, so it
likely does — verify). "existing zoom level should not change when changing
presets": confirm/adjust `applyPreset` so a preset switch keeps the current
camera (handoff says Park/Topo/Trace presets already preserve zoom/pitch/bearing —
make region match and ensure none reset zoom). Acceptance: 5 on-map preset
buttons; tapping any switches layers without moving the camera.

---

## Verification note

Headless GL render is unreliable for this viewer (documented across `pwa_qa.md`
and the handoff). Verify DOM/CSS/JS logic headlessly where possible (collapse
class on mobile, version text in the pill, button presence, no console errors);
treat camera-settle (1), mobile collapse (2), preset layer visibility (4,5,10),
and logo overshoot (6) as on-device confirms.
