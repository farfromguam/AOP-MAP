# Data editor — true preview parity + change stars + view raw record

> **✅ DONE 2026-06-13 — built + verified by observation; council run on the data-editor diff only.**
> Follow-on to the just-shipped fold-in
> (`../../20_deferred/_done/data_editor_fold_into_production.md`). Three things the user asked for on
> `data_editor.html` after the fold-in landed.

TL;DR:
- **True preview** — confirmed (not just asserted) the editor's Preview card renders the *exact* text the
  public viewer shows when a feature is active. Both call the same `window.AOPFeatureDisplay`
  (`feature_display.js`); the viewer sets its popup body to exactly `popupHtml(featureDisplay(props))`
  (`viewer_core.js` `gotoPoi()` directory click ≈:1665, map-click handler ≈:2531 — line numbers drift while
  that file is actively edited; cite the functions), and the editor's `.poic` card is the same
  expression. Proven by observation across both pages.
- **Change stars** — added a ★ column to the grid that toggles `properties.highlight` (the published ★
  the viewer's "starred places" list reads; same boolean convention as `panel.js`/`main.js:3705`).
- **View raw record** — added a **Raw record** tab beside **Preview** in the below-map pane, showing the
  full working GeoJSON feature (every field, not just the six grid columns).

#aop #sprint12 #data_editor #stars #raw_record #true_preview #git_gate

-----

## What the user asked

> *"ensure the assembled text here in this view is the same as in the viewer. I want this to be a true
> preview. We should also have the ability to change stars and view the raw record."* (2026-06-13)

## What I found before building

- **Parity already held at the code level.** The fold-in already routed the preview through the shared
  `feature_display.js`. The viewer builds its popup body as nothing but `popupHtml(featureDisplay(props))`
  in both popup paths; the editor preview is `<div class="poic">${popupHtml(featureDisplay(props))}</div>`
  — same function, same raw props → same text. So "ensure" = wire-true verification + don't break it,
  not a rebuild.
- **A "star" is `properties.highlight === true`** — a published, source-traceable data-model field baked
  by `mvp/scripts/bake_poi_stars.py`, read by the viewer's `STAR_GROUPS` directory list. The toggle
  convention everywhere else is an explicit boolean (`main.js:3705` `props.highlight = !props.highlight`;
  `highlight` is in `panel_overrides.EDITABLE_KEYS` and IS published). The data editor had no way to set it.

## What I built (all in `website/js/data_editor_map.js`; `data_editor.html` shell unchanged)

1. **★ column** — a compact star cell after the row `#`. ☆ (muted) / ★ (gold) per row; click toggles
   `properties.highlight` (explicit `true`/`false`, matching the system convention), autosaves to the
   per-file `aop_dataedit::<file>` key, updates the button + a "N ★" count in the meta bar. Visible for
   all rows at once, mirroring the viewer's starred list. Not added to the popup (the viewer's popup
   doesn't show the star — keeping the Preview a true preview).
2. **Raw record tab** — the below-map preview pane gained a two-button tab strip: **Preview** (the
   unchanged faithful popup card) and **Raw record** (`<pre>` of `JSON.stringify(fc.features[sel], null, 2)`
   — the full working feature, reflecting unsaved edits, so you can see/confirm fields the grid never
   surfaces: `id`, `status`, `source`, `caveat`, `highlight`, `confidence`, `permission`, …). The popup
   card builder was extracted to `previewCardHtml()` so the Preview tab is **byte-identical** to before.

## Acceptance

- [x] Preview card text == the viewer's active-feature popup text — **proven by observation** (not
      re-derived): editor `.poic` === `popupHtml(featureDisplay(props))` === the viewer page's own value
      for the same props.
- [x] A ★ control toggles `properties.highlight` and persists into the working FC; reflects in the grid +
      a star count.
- [x] A raw-record view shows the full feature, including fields outside the six grid columns.
- [x] Editor parity preserved (round-trip-safe grid, per-file autosave, two-way map sync) — additive only.
- [x] Verified by observation (Playwright, 0 console/page errors).

## Verification (by observation, 2026-06-13)

`/tmp/verify_editor_stars_raw_parity.py` (Playwright on `:8000`, `node --check` clean), **13/13 PASS, 0
console / 0 page errors**:

- **Parity:** editor's rendered `.poic` === in-page `popupHtml(featureDisplay(AOP-Pavilion-props))` ===
  the `index.html` viewer page's own value for the same props (same module, both pages). Chained with the
  viewer code (`viewer_core.js` `gotoPoi()`/map-click handler, ≈:1665/:2531), the Preview tab equals the
  viewer popup body.
- **Stars:** Pavilion starts unstarred → click ★ → persisted FC `highlight===true`, button ★, count
  bumped → click again → `highlight===false`, button ☆.
- **Raw:** Raw tab shows the full record (`type`/`geometry`/`coordinates`/name) plus non-grid fields
  (`permission`/`status`/`id`/`confidence`/`severity`).
- Shots: `../../output/data_editor_stars_raw.png`.

## Owed (the user's git gate)

- **UNCOMMITTED.** Diff is `website/js/data_editor_map.js` (M) only this slice (the fold-in's
  `data_editor.html` + retired mockup are the prior diff). Offline precache + `VERSION`/`#appVersion`
  bump + commit remain the user's (`no_commits.md`). Report; do not perform.

## Source

- `../../20_deferred/_done/data_editor_fold_into_production.md` — the fold-in this builds on.
- `mvp/scripts/bake_poi_stars.py`, `mvp/scripts/panel_overrides.py` — the star (`highlight`) data model.
- `website/js/feature_display.js`, `website/js/viewer_core.js` — the shared display strategy + the viewer
  popup paths the preview matches.
