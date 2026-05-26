# Right-panel editor consistency

Date: 2026-05-25

TL;DR:
- The right rail is supposed to be one editor. Today two layers (Simulated
  Saturday activity, Event schedule POIs) ship as bare checkboxes with no
  drawer and no feature list, and a third (Activity hotspots) has a tune
  drawer but no per-feature index. The Export-all button is also marooned at
  the bottom of the panel, far from its sibling control `Collapse panel`.
- Two registries decide whether a row gets the editor treatment:
  `TUNABLE_LAYERS` (paint drawer) and `FEATURE_LIST_LAYERS` (CRUD index).
  Three layers need to be registered into both so they inherit the
  drawer + feature-list + ★/fly/copy/move/tag primitives the other layers
  already use.
- One more polish: every section header should carry its own `⧉` action,
  and the panel-level `⧉ Export all` should sit beside `▾` in the panel
  header — `.panel-actions` at the bottom of `#panelBody` retires.

#aop #03_event_app #editor #right_panel #tune #feature_list #export

-----

## Source

- User direction (2026-05-25): *"review our editor on the right side there
  are some inconsistencies 1) the export button is at the bottom and not at
  the top next to the global collapse expand. 2) publishable has simulated
  saturday activity and event schedule POIs that don't have the correct
  styling or expanded edit options. the POIs are just kinda thrown in there
  and not really an editor. we need an index of items and CRUD buttons."*
- Predecessors:
  - `../02_edit/_done/poi_editor_v2.md` — feature-list primitive (rows,
    visibility, fly, copy, tag, move).
  - `poi_editor_inline_list_and_highlight.md` — `editorPois` inline list +
    highlight flag; shows the per-layer-target retargeting pattern.
  - `viewer_polish_carryover.md` — Sprint 02 carryover; the panel chrome and
    section-action `⧉` pattern landed there.

## Diagnosis (recorded so the fix is not a guess)

`wireLayerEditRows()` at `website/index.html:3848` only wraps a row in
`.layer-row` (with a `▸` expand button + drawer plumbing) when the layer
appears in `TUNABLE_LAYERS`. A row gets a per-feature CRUD list only when it
*also* appears in `FEATURE_LIST_LAYERS`.

Current registry coverage for the Publishable section (`index.html:656–673`):

| Row | `TUNABLE_LAYERS` | `FEATURE_LIST_LAYERS` | Result |
| --- | --- | --- | --- |
| trails | yes | no | drawer, no list |
| boundaries | yes | no | drawer, no list |
| trailheads | yes | no | drawer, no list |
| activityHotspots | yes | **no** | drawer, **no list** |
| **syntheticActivity** | **no** | **no** | **bare checkbox** |
| **eventSchedule** | **no** | **no** | **bare checkbox** |
| visitorContext | yes | yes | full editor |
| brandLogos | yes | yes | full editor |

Section-export `⧉` is also missing from two section headers:
- `data-section="publishable"` at `index.html:657–662`
- `data-section="poi"` at `index.html:681–687`

## Decisions

- **Promote Export-all into the panel header.** It's the panel-level peer
  of `Collapse panel`. The `.panel-header` grid grows to carry both
  controls; `.panel-actions` at `index.html:768–770` retires.
- **Register three layers in `TUNABLE_LAYERS`** so they get a real paint
  drawer:
  - `syntheticActivity` — opacity drives `synthetic-activity-tracks`,
    `synthetic-activity-hotspots-{heat,fill,outline,labels}` opacities;
    color drives the hotspot outline + labels; width drives the hotspot
    outline. Mirrors the existing `activityHotspots` entry.
  - `eventSchedule` — opacity drives `event-session-routes`,
    `event-route-labels`, `event-anchor-points`, `event-anchor-labels`;
    color drives `event-anchor-points` (circle-color), the route line, and
    the labels; width drives the route line. Concrete layer IDs read from
    the existing `layerToggleGroups` entry at `index.html:1615` so this
    cannot drift from the registered toggle set.
  - `activityHotspots` already exists in `TUNABLE_LAYERS`; no change.
- **Register three layers in `FEATURE_LIST_LAYERS`** so they get a CRUD
  index inheriting the row primitive:
  - `eventSchedule` — `idField: 'anchor_id'` (or whatever the
    `eventScheduleToGeojson` output carries; verify in `index.html:4452`
    before wiring). Rows from `eventScheduleData.features`. Flat list
    sorted by start time, falling back to label. Per-row controls:
    visibility checkbox (hides one anchor without flipping the layer),
    fly-to (existing), tag input is off (anchors already resolve through
    `locations`). Move-to is off — locations live in
    `aop_event_schedule.json` and should be edited there, not dragged.
  - `syntheticActivity` — `idField: 'hotspot_id'`. Rows from
    `aop_synthetic_activity_hotspots.geojson`. Flat list sorted by
    intensity desc then name. Per-row: visibility + fly. Move off
    (synthetic data is deterministic; moving has no meaning).
  - `activityHotspots` — `idField: 'hotspot_id'`. Same shape as
    syntheticActivity. Visibility + fly. Move off.
- **Add `data-section-export` `⧉` button** to the Publishable section
  header for parity with Source / Derived / Map editor. The POI section is
  deliberately *not* given a `⧉` — its checkboxes (`poiGroup*`) are derived
  bindings of `show*` toggles owned by other sections, and `sectionInputs`
  filters on `id.startsWith('show')`, so exporting `poi` would yield an
  empty payload. The POI surface is reconstructed from its source-section
  exports.
- **Per-feature visibility** writes into the same
  `aop_feature_visibility_v1` store every other feature-list layer uses.
  No new storage key — the registry primitive handles persistence.
- **No new tune sliders for `eventSchedule` route width** until the user
  asks. The default route is a single line; one width control is the
  minimum useful set. Resist multi-band tuning here.

## Out of scope

- No left-rail changes. The left POI tab still surfaces `event_anchors`
  through `aop_poi_index.json` — that pipeline is untouched.
- No data-shape changes to `aop_event_schedule.json`,
  `aop_synthetic_activity_hotspots.geojson`, or
  `aop_activity_hotspots.geojson`. We *read* what's there; we do not
  rewrite the schemas.
- No CRUD-create for event anchors from the panel. "Add a session"
  belongs in `full_loop_crud_upload_audit.md`, not here. This card is
  about exposing the existing items as an editable index, not authoring
  new ones.

## Files touched

- `website/index.html`
  - **Header chrome:** `.panel-header` grid expanded to host
    `#exportAll` next to `#panelCollapse`. `.panel-actions` (containing
    `#exportAll`) removed from `#panelBody`. CSS for `.panel-export`
    or reuse of `.section-action` styling.
  - **Section headers:** add `<button … data-section-export="publishable" …>`
    to the Publishable header and `<button … data-section-export="poi" …>`
    to the POI header. Grid columns already accommodate via existing
    `.section-header` rule at `:180`.
  - **`TUNABLE_LAYERS`:** add `syntheticActivity` and `eventSchedule`
    entries. Mirror `activityHotspots` shape for the synthetic one; the
    event-schedule entry uses route + anchor layer IDs from
    `layerToggleGroups` at `:1615`.
  - **`FEATURE_LIST_LAYERS`:** add `activityHotspots`, `syntheticActivity`,
    `eventSchedule` entries. Register each via `registerFeatureListLayer`
    after their data loads (event schedule already loads via
    `eventScheduleToGeojson`; synthetic + hotspots load via fetch
    elsewhere in the file).
  - **Section-export wiring:** `buildSectionPayload` / `applySectionPayload`
    already iterate by `data-section`; adding the new `⧉` buttons in HTML is
    sufficient. If the section payload helpers gate on a known section
    list, add `publishable` and `poi` to that list.

## Acceptance

- [x] Panel header carries both `▾` (collapse) and `⧉` (export-all).
      `.panel-actions` row at the bottom of `#panelBody` is gone.
- [x] Publishable section header carries a `⧉` button. (POI section
      deliberately excluded — see Decisions.)
- [x] Simulated Saturday activity row in Publishable expands a drawer
      (opacity/color/width sliders) and an inline feature list of hotspots
      (18 rows) with visibility + fly.
- [x] Event schedule POIs row in Publishable expands a drawer and an
      inline feature list of event anchors (8 rows) with visibility +
      fly. Tag input absent.
- [x] Activity hotspots row in Publishable expands the existing drawer
      *and* a new feature list of hotspots (65 rows) with visibility +
      fly.
- [x] Per-feature visibility on any of the three lists hides the
      corresponding map feature only (not the whole layer) and survives
      reload — proven by the feature-list verifier's reload assertion,
      which exercises the same primitive.
- [x] No regressions in existing editor surfaces: drawn POIs inline list,
      buildings drawer + list, cemeteries drawer + list, visitor-context
      list, brand-logos list, SFWDA drawer with the grid-edit controls.
- [x] `playwright_verify_synthetic_activity.py` passes (0 console errors).
- [x] `playwright_verify_feature_list.py` passes (one assertion flip
      explicitly intended: publishable now has the `⧉` button it formerly
      lacked; POI section took over the "no export" negative assertion).
- [x] `playwright_verify_presets.py` passes (0 non-tile console errors).
- [ ] `playwright_verify_event_schedule.py` — two failures reproduce on
      baseline (search magnifier icon missing, hot button click timeout).
      Neither is caused by this card.
- [x] Manual: ★ stays exclusive to `editorPois` (the new lists do not
      carry `highlightable`, so no star button renders).

## Verification

```text
python3 -u mvp/scripts/playwright_verify_feature_list.py       → RESULT PASS
python3 -u mvp/scripts/playwright_verify_synthetic_activity.py → RESULT PASS
python3 -u mvp/scripts/playwright_verify_presets.py            → RESULT PASS
python3 -u mvp/scripts/playwright_verify_event_schedule.py     → RESULT FAIL  (pre-existing, not from this card)
```

`playwright_verify_feature_list.py` needed one assertion flip: it explicitly
asserted Publishable had **no** export button. That assertion was retired in
favour of asserting Publishable **does** carry one, with the same negative
assertion now pointing at the POI section (which we deliberately left
unexported — see Decisions).

`playwright_verify_event_schedule.py` reports two failures that reproduce on
the pre-change baseline (verified by stash + replay):

- `[FAIL] search magnifier icon present` — the verifier expects a
  `.search .search-icon` SVG inside the left-rail search shell; no such
  element exists in `website/index.html`. Pre-existing gap; unrelated to
  the editor surface this card touches.
- `Locator.click: Timeout 30000ms exceeded` on `#hotButton` in the Hot
  control "live" block. The hot button is present and reports
  `hidden === false` in the immediately-prior snapshot assertion, but
  Playwright's strict visibility check times out at click time. Also
  pre-existing.

Both are tracked in `viewer_polish_carryover.md`'s open-followups orbit (or
deserve a new card) — flagged here so the next session does not blame this
work for them.

## Open follow-ups (not blocking)

- Dedicated `playwright_verify_right_panel_consistency.py` that asserts:
  every Publishable row carries a `▸` button; every section header carries
  a `⧉` button; header `⧉ Export all` is present.
- Decide whether the `Layer notes` section (`data-section="notes"`,
  `:746`) also deserves a `⧉` — it currently has none and its content is
  prose, so probably not. Captured here so the decision is intentional.
- The event-schedule feature list could grow a "next-up" marker that
  follows the live calendar countdown — defer until `viewer_polish_carryover`
  lane priorities clear.

## Related work

- `../02_edit/_done/poi_editor_v2.md` — feature-list primitive.
- `poi_editor_inline_list_and_highlight.md` — per-layer-target retargeting
  pattern; this card stays on the default `#featureList` drawer slot.
- `viewer_polish_carryover.md` — Sprint 02 carryover; the section-action
  `⧉` precedent and the panel chrome cleanups live there.
- `full_loop_crud_upload_audit.md` — the Sprint 03 thrust that will own
  authoring (create) for event sessions, not this card.
