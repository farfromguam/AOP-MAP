# Data editor — fold the chosen map+preview into production, retire the mockups

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

- [ ] User picks the preview style (A/B/C/D).
- [ ] `data_editor.html` carries the V1 map + chosen preview; round-trip-safe grid + per-file autosave
      preserved (map is additive); two-way selection sync works (row# → fly, Lat/Lng edit → marker
      moves, map click → row).
- [ ] Mockup files retired (confirmed unreferenced first); `data_editor.html` is the one editor.
- [ ] Verified by observation (Playwright, 0 console/page errors), as the mockups were.

## Owed (the user's git gate)

- `data_editor.html` is precached in `sw.js` SHELL_ASSETS only when the user wants it offline-ready;
  that + any shell-asset change owes a `VERSION`/`#appVersion` bump. The bump + commit are the user's
  (`no_commits.md`). Report it; do not perform it.

## Source

- `../12_field_schedule_editor/_done/data_editor_map_viewer.md` — the shipped+reviewed mockup card
  (layouts, previews, verification, council done-review) this was extracted from.
- `../12_field_schedule_editor/_done/data_points_editor.md` — the base `data_editor.html` being folded into.
