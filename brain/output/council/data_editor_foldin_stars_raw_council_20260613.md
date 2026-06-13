# Council done-review — data editor fold-in + stars/raw/true-preview (2026-06-13)

**Convened by:** Steward, on user request ("have the council meet on just this change").
**Scope (enforced):** the data-editor change ONLY — `website/data_editor.html`, `website/js/data_editor_map.js`,
deleted `website/data_editor_v1_preview_a_popup.html`. Full diff vs session-start baseline (`git diff 00cbe1a`)
at `/tmp/council_dataeditor.diff`. The concurrent band/ⓘ/v68 work in the same tree (`viewer_band.js`,
`viewer_core.js`, `index.html`, `sw.js`, `viewer.css`, `band_*`/`v2_*` PNGs) was explicitly OUT of scope.

**Cards reviewed against:**
- `tasks/20_deferred/_done/data_editor_fold_into_production.md` (fold-in; preview A picked)
- `tasks/12_field_schedule_editor/_done/data_editor_stars_raw_record.md` (stars + raw + true preview)

## Verdicts — 5/5 CLEAR

| Seat | Verdict | One-line |
|------|---------|----------|
| **Witness** | clear | Re-drove the live `:8000` system; re-ran both verifiers (fold-in PASS, stars/raw/parity 13/13, 0 errors) + own probe of all 6 rows' parity + star paint/glyph change. Not re-derived. |
| **Warden** | clear | Every hunk traces to a card line; no scope drift, no deleted directive, no over-deletion. **Working agent did NOT bypass the git gate** — the concurrent `v68` broad commit captured the fold-in; the stars/raw slice is still uncommitted. |
| **Quartermaster** | clear | Reuse not duplication: `data_editor.html` is a thin shell loading the shared engine (net editor `*.html` −1); star reuses `properties.highlight` (same convention as `panel.js`/`bake_poi_stars.py`); preview/raw use the ONE `feature_display.js`. C1/C2/C6 hold. |
| **Mason** | clear | No limiting code (no validator/row-drop/throw); `previewCardHtml()` byte-identical to the prior branches (`git show HEAD`); round-trip safe; `renderPreview` re-wires tab buttons on fresh DOM (no stale handlers). `node --check` clean. |
| **Scribe** | clear | Both cards record result + verification-by-observation + the owed user git-gate; fold-in filed to `_done/`; handoff entries accurate; plain voice, no puffery, no misspellings. |

**Steward synthesis:** full clear. The change reused the existing engine + star data-model + shared display
strategy instead of building a second surface; doneness is observed (the Witness reproduced it), it stayed on
the farm and inside the cards, and it landed durably in the brain.

## Non-blocking notes (fixed after review)
1. **Witness + Scribe:** the cards/handoff cited `viewer_core.js:1603`/`:2469` for the popup-body sites; the
   real lines are ≈:1665/:2531 (the file is being concurrently edited, so line numbers drift). Corrected to
   cite the **functions** (`gotoPoi()` + the map-click handler) with approximate lines.
2. **Scribe:** "12-line shell" was imprecise; corrected to "thin shell (24 lines, ~12 structural + comment)."

## Gate marker
Not written to `.claude/.council-cleared`: the shared working tree still holds the concurrent band/ⓘ work, so
a tree-wide diff hash would not match this scoped clearance (same call prior mixed-tree sessions made). This
receipt is the durable record of the clearance.

## Owed (unchanged — the user's git gate)
The stars/raw slice (`website/js/data_editor_map.js`) is UNCOMMITTED. Offline precache of
`data_editor.html` + `js/data_editor_map.js` in `sw.js` + the `VERSION`/`#appVersion` bump + the commit
remain the user's (`no_commits.md`).
