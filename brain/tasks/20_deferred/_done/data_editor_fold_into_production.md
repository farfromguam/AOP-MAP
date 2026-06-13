# Data editor — fold the chosen map+preview into production, retire the mockups

> **✅ DONE 2026-06-13 — gate cleared (preview A), folded in, verified by observation.** User confirmed
> the read ("thats about right") that **preview A** is the pick. `website/data_editor.html` is now the
> V1 side-dock + popup-card shell that loads the shared engine; the surviving mockup
> `data_editor_v1_preview_a_popup.html` is retired. Only the user's git-gate (precache + `VERSION` bump +
> commit) remains, which this card always scoped as the user's. Filed to `_done/`.
>
> **Deferred 2026-06-13.** Extracted from the now-closed
> `../12_field_schedule_editor/_done/data_editor_map_viewer.md` (mockups SHIPPED + council CLEAR; V1
> layout chosen). This card holds the remaining production fold-in, which is **gated on one user
> decision** (the preview style) — so it waits in deferred until the user picks.

TL;DR:
- The map+grid editor was prototyped as one shared engine (`website/js/data_editor_map.js`) + four
  layout mockups + four feature-text preview mockups, all reviewed and verified. The user already
  chose **V1 side dock** as the layout. What remains is to fold the chosen pieces into the real
  `website/data_editor.html` and retire the mockup files.
- **The one open gate:** which feature-text preview style — **A faithful popup card (recommended)** /
  B phone frame / C labeled fields / D chip card. Everything below is a quick mechanical pass once
  A/B/C/D is picked.

#aop #sprint12 #data_editor #fold_in #mockup_retirement #deferred #git_gate

-----

## The decision still owed (the gate)

Pick the active-feature text preview that renders below the V1 side-dock map. From
`data_editor_map_viewer.md` round 2 (all four verified, 0 console errors):

- **A — faithful popup card (RECOMMENDED).** Re-creates the real public-map popup (`poiPopupHtml`,
  `main.js:1339`): title · blurb / "Info needed — revisit" · Kind · Status · Source · Caveat. Matches
  what the public map shows when a feature is active.
- **B — phone frame.** Same popup on a device screen ("the iphone").
- **C — labeled fields.** Empty-state flagged; a fill-in checklist.
- **D — chip card.** Richer; NOT today's popup → implies a live-map rework (more than a fold-in).

## The fold-in (once A/B/C/D is picked)

1. Fold **V1 side dock** (grid left / map pinned right, `data_editor_map_v1_side.html`) + the chosen
   preview region into the shipped **`website/data_editor.html`**. The engine
   (`website/js/data_editor_map.js`) is already shared — wire it in; do not re-implement.
2. **Retire the mockups** (git-recoverable; confirm each is unreferenced first):
   - layouts: `data_editor_map_v1_side.html`, `data_editor_map_v2_drawer.html`,
     `data_editor_map_v3_mapfirst.html`, `data_editor_map_v4_overlay.html`, `data_editor_map_compare.html`
   - previews: `data_editor_v1_preview_a_popup.html`, `data_editor_v1_preview_b_phone.html`,
     `data_editor_v1_preview_c_fields.html`, `data_editor_v1_preview_d_chips.html`,
     `data_editor_v1_preview_compare.html`
   - keep the unchosen layouts in the pocket only if the user wants them (V2 was noted "in the pocket
     for field/phone", V4 as the minimal-change option) — default is retire all mockups, prod is the
     one editor.
3. **Offline basemap precache** (field use) — later/optional; the grid + autosave already work offline
   with a blank basemap.

## Acceptance

- [x] User picks the preview style (A/B/C/D). → **A** (faithful popup card), confirmed 2026-06-13.
- [x] `data_editor.html` carries the V1 map + chosen preview; round-trip-safe grid + per-file autosave
      preserved (map is additive); two-way selection sync works (row# → fly, Lat/Lng edit → marker
      moves, map click → row). → the engine is a superset; `data_editor.html` is now a thin shell (24 lines,
      ~12 structural + a comment) that just loads it.
- [x] Mockup files retired (confirmed unreferenced first); `data_editor.html` is the one editor.
- [x] Verified by observation (Playwright, 0 console/page errors), as the mockups were.

## Done (2026-06-13)

**The fold-in, leveraging the new viewer code as-is (no re-implementation):**

1. `website/data_editor.html` is now the **V1 side-dock + popup-card shell** — a thin HTML that sets
   `window.AOP_MAP_MODE='side-right'` + `window.AOP_PREVIEW_STYLE='popup'` and loads
   `vendor/maplibre-gl.js` → `js/feature_display.js` → `js/data_editor_map.js`. The original blind-grid
   inline script is gone: the shared engine `data_editor_map.js` is a **superset** of it (same
   `getVal`/`setVal` round-trip, same `localStorage['aop_dataedit::<file>']` autosave + `pagehide`/
   `visibilitychange` flush, same manifest dropdown defaulting to `publish.geojson`, same
   add/delete/export/reset) **plus** the satellite map + two-way sync + the preview. The preview reads the
   **same `window.AOPFeatureDisplay`** (`feature_display.js`) the public viewer uses — so the card shows
   exactly what the live map will (the normalization the deferred card predated; it no longer needs the
   stale `main.js:1339` mirror it described).
2. Retired `website/data_editor_v1_preview_a_popup.html` (confirmed unreferenced by the site first).
3. `data_editor_map.js` header comment updated: it's the **production** editor engine now, not "mockup-only"
   (V2/V3/V4 modes stay supported but only V1 ships).

**Verified by observation** (`/tmp/verify_data_editor_foldin.py`, Playwright on the running `:8000`,
`node --check` clean on both JS files): default `publish.geojson` (6 rows), `data-mode=side-right`, map
canvas + Satellite/Street toggle present, preview idle→popup-card on select; **two-way sync** — clicking
row 4 (AOP Pavilion) selects + flies, editing the Name updates the preview title live
("AOP Pavilion EDITED"), editing the Lat moved the rust marker on the imagery (before/after pixels) AND
propagated into the persisted FC (35.0907264 → **35.100726**); all **6 features preserved**;
**0 console / 0 page errors**. Shots: `../../output/data_editor_foldin_{full,before_lat,after_lat}.png`.

## Owed (the user's git gate)

- `data_editor.html` is precached in `sw.js` SHELL_ASSETS only when the user wants it offline-ready;
  that + any shell-asset change owes a `VERSION`/`#appVersion` bump. The bump + commit are the user's
  (`no_commits.md`). Report it; do not perform it.

## Source

- `../12_field_schedule_editor/_done/data_editor_map_viewer.md` — the shipped+reviewed mockup card
  (layouts, previews, verification, council done-review) this was extracted from.
- `../12_field_schedule_editor/_done/data_points_editor.md` — the base `data_editor.html` being folded into.
