# Left Panel POI Browser

Date: 2026-05-25

TL;DR:
- Shipped 2026-05-25. The viewer now has a third left-rail tab, `POI`, sitting
  between `Events` and `About` inside `#calendarCard`.
- The tab renders a grouped, scrollable index of places (event anchors,
  in-park buildings, observed trails, cemeteries, off-park visitor support,
  and the user's drawn POIs). Click a row to fly the map, auto-enable the
  source layer, and open a POI-tab popup.
- Visitor blurbs and "info needed — revisit" placeholders live in
  `website/data/aop_poi_index.json` — a single auditable file so gaps stay
  visible in git rather than hiding as TODOs in code.
- A parallel right-panel `POI` section (also shipped 2026-05-25) carries
  group-level visibility toggles two-way bound to the source-layer toggles
  in Source / Derived / Publishable / Map editor. Same six groups as the
  left tab; flipping any group hides or shows that whole POI kind.

#aop #03_event_app #viewer #left_panel #poi

-----

## Source

- `misc.md` 2026-05-24 loose bullet: *"need a poi viewer on the left side so
  that a user can browse locations and read about them. clicking will take them
  to the location on the map."*
- `left_panel_context_tabs.md` — original Events / Park / About left-tab shape.
- `left_sidebar_content_audit.md` — the 2026-05-25 Rock Warblers rebrand that
  merged the old `Park` (Event) and `About` tabs into a single `About` tab and
  freed the third slot for this card.
- `../../research/viewer.md` — catalog of publishable POI layers (event-anchor,
  editor POIs, brand logos, visitor-context callouts, cemeteries, etc.).

## Decisions (2026-05-25)

- **Brand logos are out.** They are cartographic decoration, not destinations.
  The Brand logos drawer still owns moving/sizing them; the POI tab does not
  list them.
- **Grouped by kind, not flat.** Mirrors the right-rail
  `feature-list-group` convention so the two inventories read the same.
  Group order: Event anchors → Buildings in the park → Trails → Cemeteries →
  Visitor support → Drawn POIs.
- **Blurbs live in a separate file.** `website/data/aop_poi_index.json` is
  the single source for visitor-facing copy. The source GeoJSONs
  (`aop_buildings.geojson`, `aop_cemeteries.geojson`, `publish.geojson`)
  stay clean so a re-export from PostGIS / FEMA / Comptroller importers
  never overwrites authored copy. Visitor-context callouts already carry
  rich text in their properties and pass through as a fallback when an index
  entry has no blurb.
- **Placeholders are visible.** Rows with no blurb render a yellow
  `info needed — revisit` chip; the row's subtitle shows the `revisit_note`
  string from the index file. The `owed_work` array at the bottom of
  `aop_poi_index.json` summarizes everything still missing.

## Schema

`website/data/aop_poi_index.json` carries blurbs + placeholders. Each
`entries[]` row matches a feature by `source` (which dataset it lives in)
plus an identifying property, and supplies a `blurb` (string or null) and a
`revisit_note` (string or null).

Per-row fields rendered by the viewer:

| Field | Always shown? | If missing |
|---|---|---|
| `name` | yes | n/a |
| `kind` | yes | n/a |
| `blurb` | yes when present | placeholder + revisit_note subtitle |
| `status` / confidence | yes | `unknown` |
| `source` | yes | (kind · source) fallback subtitle |
| `caveat` | when applicable | omitted |

Click behavior: `closeAllMapPopups()` → toggle the source layer on if it was
off (mirrors `gotoEventSession`) → `flyToFeature(row.feature)` → open a
`maplibregl.Popup` with the same blurb + status + source fields at the
feature's centroid / first coord.

## Shipped

`website/index.html`:

- `.left-tabs` grid restored to three columns.
- Added `#leftTabPoi` button + `#poiTabPanel` panel; ARIA roles + keyboard
  arrow-nav inherited from the existing tab module.
- New CSS group `.poi-list / .poi-list-group / .poi-row / .poi-row-meta /
  .poi-placeholder-chip / .poi-tab-popup` driven by the existing Muted Earth
  palette tokens.
- `let publishDataCache = null; let poiIndex = null;` declared near the
  other module-scope layer caches so the POI module below them is not in
  the temporal dead zone when the immediate `fetchPoiIndex()` fires.
- `publishDataCache = publishData;` set after the publishable layer JSON
  lands, then `renderPoiTabIfActive()` to refresh.
- POI module: `fetchPoiIndex()`, `poiIndexLookup()`, `poiGroupLabel()`,
  `poiGroupOrder()`, `buildPoiGroups()`, `renderPoiTab()`, `gotoPoi()`,
  `poiPopupHtml()`. Hooks into `setLeftTab('poi')`,
  `registerFeatureListLayer()`, and `rebuildEventScheduleData()` so the
  list refreshes when any of its source layers reloads.
- Empty state: "Loading places…" while the fetches are in flight, then
  "No places loaded yet…" if nothing matches.

`website/data/aop_poi_index.json` (new file):

- 6 groups, 20 entries, with 10 placeholder entries (`blurb: null` +
  explicit `revisit_note`).
- Includes an `owed_work` array summarizing the placeholder list so a
  contributor can scan one file to find every gap.

Right panel (`website/index.html`):

- New `<section data-section="poi">` between Publishable and Map editor.
  Six group checkboxes (`#poiGroupEventAnchors`, `#poiGroupBuildings`,
  `#poiGroupTrails`, `#poiGroupCemeteries`, `#poiGroupVisitorSupport`,
  `#poiGroupDrawnPois`) each carrying `data-poi-target=<source-toggle-id>`.
- `wirePoiPanel()` (called once at module init) hydrates initial state
  from the source toggles and installs change listeners both directions.
  An `echoing` flag suppresses feedback loops when one surface mirrors
  the other.

`mvp/scripts/playwright_verify_presets.py`:

- Tab-label assertion updated from `["Events", "About"]` to
  `["Events", "POI", "About"]`.
- New assertions: POI tab opens on click, renders at least one row and one
  group.
- Right-panel POI section assertions: six group toggles render; clicking a
  group toggle propagates to the underlying source toggle (visibility goes
  visible); dispatching a `change` on the source toggle mirrors back to
  the group toggle.

## Gap list (placeholders shipped)

The following rows render with `info needed — revisit` chips. Each is owed
either AOP confirmation, on-site verification, or downstream research:

- **Event anchors (4):** `#proving-grounds`, `#north-technical`,
  `#night-checkpoint`, `#photo-waypoint`. All resolve to coordinates from
  GPX hotspots or candidate footprints, but none have AOP-confirmed visitor
  copy yet.
- **Buildings (3):** 1033, 665, and 880 Ellis Cove Road. FEMA tags them
  residential; the event schedule lists 665 as a Proving Grounds candidate.
  No AOP-confirmed roles yet.
- **Cemeteries (3):** Gilliam, Bible, Tate. Each sits in the 9-patch but
  outside the AOP working envelope. Visitor relevance and accessibility
  unknown.
- **Trails:** the two `Saturday Afternoon Activity (segment N)` rows carry
  blurbs but their `revisit_note` points at the SFWDA numbered-trail-name
  research on `../01_mvp/_done/community_trails_import.md` — promote them
  to real named trails once that lands.

## Acceptance

- [x] New `POI` tab inside `#calendarCard` renders a scrollable POI list
      when at least one supported layer is loaded. `.left-tabs` grid back to
      three columns.
- [x] Each row shows a name and a short context line; click flies the map
      and opens the bound popup.
- [x] Empty state renders when no supported layers are loaded
      ("Loading places…" pre-fetch, "No places loaded yet…" post-fetch).
- [x] Mobile width 360 px / 390 px keeps the left rail within the existing
      clear-of-panel height (presets verifier mobile checks still PASS).
- [ ] Dedicated `playwright_verify_left_poi_browser.py` covering:
      placeholder chip count, click-row-flies-camera, popup HTML contains
      the row's blurb / placeholder text, and source-layer auto-enable.
      The presets verifier covers the smoke checks but a focused verifier
      is owed before the next sprint pickup.

## Verification

```text
node --check on inline script: PASS
python3 -u mvp/scripts/playwright_verify_presets.py: RESULT PASS
  (incl. new POI tab assertions: rows >= 1, groups >= 1)
python3 -u mvp/scripts/playwright_verify_event_schedule.py: RESULT PASS
Playwright manual snapshot: 5 groups / 20 rows / 10 placeholders,
  0 console errors. Screenshot at brain/output/playwright_poi_tab.png.
```

## Out of scope

- POI editing, creation, deletion. Right-rail `Editor POIs` drawer still
  owns that surface.
- Submissions from non-staff visitors. Stays on
  `full_loop_crud_upload_audit.md`.
- New POI data sources. The list reads what the viewer already loads.
- Cross-linking *from* the map back to the POI tab (clicking a building
  popup on the map does not jump to that row in the tab — defer until a
  user asks for it).

## Open follow-ups

- Run the field/source pass against the gap list above so the
  `info needed — revisit` chips fade out.
- Consider promoting the `owed_work` array in `aop_poi_index.json` into a
  rendered "info needed" section at the bottom of the tab so a non-coder
  reviewer can see the full gap list without grepping JSON.
- Decide whether Drawn POIs deserve their own group at all (today it only
  populates when a user has drawn something — empty for first-time
  visitors). Keep or hide based on feedback.
