# Data editor + map viewer — see the point while you edit it

The shipped `data_editor.html` is a blind spreadsheet: you can type a Lat/Lng but you can't see
**where** the point lands. The user asked for *"a simple map viewer so that I can make informed edit
decisions"* and *"some mockups about possible options"* in the established compare-page review pattern.

**✅ MOCKUPS SHIPPED + VERIFIED (2026-06-13). Layout choice pending the user.**

-----

## What shipped — one engine, four layouts, one review page

Same move as `right_sidebar_compare.html`: **one direction (add a map to the editor), four placements.**
Every take is the **real editor** (same round-trip-safe `getVal`/`setVal`, same per-file
`localStorage['aop_dataedit::<file>']` autosave + close-flush) with **one map added** and **two-way
selection sync** — click a row's `#` to fly there, **edit a Lat/Lng and watch the marker move on the
satellite**, click a map feature to jump to its row.

- `website/js/data_editor_map.js` — shared engine; reads `window.AOP_MAP_MODE`. Renders all geometry
  (points, trail lines, parcel polygons) over the **same TNMap satellite** the public viewer uses (Street
  toggle = OSM). Selected feature highlighted in rust; Lat/Lng stay read-only for lines/polygons.
- `data_editor_map_v1_side.html` — **V1 side dock**, grid left / map pinned right (~44%). The literal
  "map viewer in the right sidebar." **Recommended.**
- `data_editor_map_v2_drawer.html` — **V2 bottom drawer**, grid full-width / collapsible map dock below.
  The phone-in-the-field shape.
- `data_editor_map_v3_mapfirst.html` — **V3 map first**, map primary on the left / grid as right sidebar.
- `data_editor_map_v4_overlay.html` — **V4 slide-in overlay**, grid unchanged full-width / map slides in
  on select or tap. Smallest diff to the shipped editor.
- `data_editor_map_compare.html` — the **review page**: 4 live iframes + the placement-axes table +
  recommendation (one URL, per the always-produce-a-compare-page rule).

## Recommendation (in the page)

**V1 side dock.** It's literally what was asked — a map in the right sidebar — and gives the highest
payoff for the job (informed edits): the map is always beside the grid, so every coordinate is confirmed
against the imagery with no click. V2 stays in the pocket for field/phone; V4 is the minimal-change option.

## Acceptance

[x] Each layout loads the real served files via the manifest dropdown (default `publish.geojson`), renders
    the editable grid AND a satellite map, with no console/page errors.
[x] Two-way sync: click row `#` → highlight + fly-to; edit a Point's Lat/Lng → marker moves live; click a
    map feature → selects its row.
[x] Editor parity preserved (add/delete/export/reset, per-file autosave, round-trip-safe) — map is additive.
[x] Compare page renders all four live for side-by-side choice.

## Verification (by observation, 2026-06-13)

- `cd website && python3 -m http.server 8000`, open `http://localhost:8000/data_editor_map_compare.html`.
- Headless (Playwright, `/tmp/verify_editor_map.py`): all four PASS — 6 rows from `publish.geojson`, map
  canvas present, row-select highlights, a Point Lat/Lng edit dispatches with **0 console/page errors**.
  Screenshots `/tmp/edmap_{side,drawer,mapfirst,overlay}.png` + `/tmp/edmap_compare.png` — satellite tiles,
  rust selected-marker, and each placement render as designed.

## Council done-review (2026-06-13) — CLEAR (5 seats)

Witness/Warden/Quartermaster/Mason/Scribe all clear. Receipt:
`../../output/council/data_editor_map_done_review_20260613.md`. Witness re-drove the running system (own
stricter probe: Lat edit propagated into the persisted FC, all features kept, 48 real tile requests).
Quartermaster: not a second editor app — the 5 files are the established mockup convention, the engine is a
DRYer reuse of `data_editor.html`, C1=0/C6=0 (main.js untouched). Mason's one finding — a dead no-op CSS
rule in the engine — was removed + re-verified (node --check + 4/4 Playwright PASS). Warden: HEAD unchanged,
no commit, mockups not in `sw.js` so no version bump due yet.

## Round 2 (2026-06-13) — V1 chosen + the active-feature text preview

User: *"go with the first one [V1]. add below the iphone image the text of the feature as it will be shown
when it's active in the map. show me some variations on that."* Read: V1 (side dock) is the layout; below
the map, preview the selected feature **as the public map popup renders it when active** — and vary that
preview.

Found the real "active" presentation: the map popup `poiPopupHtml` (`main.js:1339`) — **title · blurb (or
"Info needed — revisit" placeholder) · Kind · Status · Source · Caveat**, styled by `.poi-tab-popup` in
`css/app.css:748`. The engine now mirrors that field model exactly (`popupModel`/`popupCardHtml`), reading
Name/Description/Kind live from the grid and Status/Source/Caveat from the feature's properties, **updating
as you type**. Added a preview region below the map (`window.AOP_PREVIEW_STYLE`), four takes:

- `data_editor_v1_preview_a_popup.html` — **A: faithful popup card** (re-creation of the real popup — same
  fields/order/look; Source shows the feature's own value, where the live map sometimes fills it per layer). **Rec.**
- `data_editor_v1_preview_b_phone.html` — **B: phone frame** (same popup, on a device screen — the "iphone").
- `data_editor_v1_preview_c_fields.html` — **C: labeled fields** (empty-state flagged; a fill-in checklist).
- `data_editor_v1_preview_d_chips.html` — **D: chip card** (richer; NOT today's popup → implies a live-map rework).
- `data_editor_v1_preview_compare.html` — the review page (4 live iframes + compare table + rec).

Verified by observation (Playwright `/tmp/verify_preview.py`): all 4 PASS — idle prompt → select populates
the real feature title → editing Name updates the preview live, 0 console/page errors. Screenshots
`/tmp/pv_{popup,phone,fields,chips,compare}.png`.

## Owed (after the user picks a layout)

> **CLOSED 2026-06-13 — the mockup+review phase is done; the production fold-in was extracted.** The
> shipped, council-cleared work of this card (one engine, four layouts, four previews, compare pages,
> verified by observation) is complete, so the card moves to `_done/`. The remaining production work —
> pick preview A/B/C/D, fold V1 + the chosen preview into `data_editor.html`, retire the mockups,
> precache + `VERSION` bump — is **gated on the user's preview pick** and now lives as a dedicated
> deferred task: **`../../20_deferred/data_editor_fold_into_production.md`**.

- Fold the chosen mode into `data_editor.html` (engine already shared), retire the mockups.
- Offline field use needs basemap precache (later); the grid + autosave already work offline with a blank
  basemap. PWA precache + the user's `VERSION` bump are the user's git-gate steps. **UNCOMMITTED.**
