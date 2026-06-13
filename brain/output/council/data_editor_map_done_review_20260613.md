# Council done-review — data editor + map viewer (mockups)

Date: 2026-06-13
Card: `tasks/12_field_schedule_editor/data_editor_map_viewer.md`
Diff: new/untracked — `website/js/data_editor_map.js` + `website/data_editor_map_v{1..4}_*.html` +
`website/data_editor_map_compare.html` (+ the card + one `handoff/session_context.md` entry).
Cleared diff hash (gate formula, `website`+`mvp`): `88f3a265b9d9e8862e438410dc7840b59453dbcb`

Goal (Steward, from the card): give the user a simple map viewer on the data editor so they can make
informed edit decisions — delivered as 4 layout mockups + a compare/review page (the
`right_sidebar_compare.html` pattern). Layout choice is the user's; nothing folded into the shipped editor yet.

Tier: five seats (more than core-three) — a new ~390-line JS engine + 5 new editor HTML files directly
implicate the C6 "no new editor HTML" and C2 "second list engine" contracts, plus verification & recording.

## Verdicts — ALL CLEAR

- **witness — clear.** Re-drove the running system: re-ran `/tmp/verify_editor_map.py` (exit 0, 4/4 PASS),
  read all 5 screenshots (real TNMap tiles, rust selected-marker, correct per-mode layouts), and ran a
  stricter own probe — Lat edit propagates into the persisted FC (+0.003 exactly, all 6 features kept),
  48 real tnmap tile requests. Caveat (non-blocking): producer verifier filters tile error strings and its
  "marker moves" check only asserts the input fired; Witness covered those gaps independently. Map-click→row
  path proven by code-read + the symmetric row→map half observed (real headless map-click blocked by
  external-tile `map.load`). Optional future: a `window.AOP_EDMAP={map}` test hook + canvas-click assertion.
- **warden — clear.** HEAD unchanged (`0c57f6e`), nothing staged, no mutating git/attribution; every hunk
  traces to the card; mockups absent from `sw.js` → no VERSION bump due yet; pre-existing uncommitted files
  (build_data_manifest.py, _data_manifest.json, data_editor.html, schedule_editor.html) not attributed here.
- **quartermaster — clear.** C1=0, C6=0 (main.js untouched), one `FEATURE_LIST_LAYERS` registry, one
  `collectStarredDestinations`. The 5 HTML files are the established mockup convention (46 such already);
  the engine is a faithful, DRYer reuse of `data_editor.html` field logic. Fold-back-and-retire is owed.
- **mason — clear** (one cosmetic finding, FIXED). Flagged a dead no-op CSS rule
  (`.stage:not([data-mode="overlay"]) .bar .mapbtn,.stage[data-mode]{}`); removed it this session,
  re-verified (node --check + 4/4 Playwright PASS). No limiting code, no throw-on-unknown, round-trip-safe
  (`mapFC` clones props, shares geometry read-only, `fc` unmutated), null/load-order guarded; field logic
  byte-for-byte with the shipped sibling.
- **scribe — clear.** Card complete (what shipped, 4/4 acceptance by observation with artifacts named,
  owed + user git-gate, UNCOMMITTED); handoff dated 2026-06-13 and pointing at the card;
  `right_sidebar_compare.html` treated as the real reused pattern (file exists); voice plain.

## Result

Gate CLEARED. Owed (the user's): pick a layout → fold the chosen mode into `data_editor.html` + retire the
mockups; later, offline basemap precache + add to `sw.js` SHELL_ASSETS + the user's `VERSION`/`#appVersion`
bump + the commit.

-----

## Round 2 (same day) — V1 chosen + active-feature text preview

Diff added: preview region in `website/js/data_editor_map.js` (`popupModel`/`popupCardHtml`/`renderPreview`
mirroring `main.js:1339` poiPopupHtml + `css/app.css:748`) + 4 preview mockups
(`data_editor_v1_preview_{a_popup,b_phone,c_fields,d_chips}.html`) + `data_editor_v1_preview_compare.html`.
Cleared diff hash: `6afd3491ac65e8bb676366a88d343a78c1bf02ab`.

ALL FIVE CLEAR (Witness/Mason/Quartermaster/Warden/Scribe):
- witness — clear. Field model + order match poiPopupHtml line-for-line; re-ran `/tmp/verify_preview.py`
  (4/4, live edit shows in preview), read `/tmp/pv_*.png`. Flagged two overstatements in the prose →
  FIXED this session: "pixel-copy" softened to "faithful re-creation"; Source-value caveat added (live map
  sometimes fills Source per layer, editor shows the feature's own value).
- mason — clear. Every interpolated value `esc()`'d (fuzzed XSS → 0 leaks/throws); no limiting code;
  renderPreview no-ops on null PREVIEW / guards sel<0; live-update only for the selected row; no dead code.
- quartermaster — clear. main.js is a vanilla IIFE with zero exports → nothing to import; the popup mirror
  is a justified self-contained copy (prior ruling), bounded by the card's fold-back/retire. main.js
  untouched; C1/C2/C6 at target.
- warden — clear. main.js/panel.js/css/app.css/sw.js/data_editor.html all empty diffs; HEAD unmoved; no
  premature fold into the shipped editor; mockups not in sw.js → no bump due.
- scribe — clear. Round-2 card section + handoff complete; references real and load-bearing; voice plain.

Owed unchanged: user picks A/B/C/D → fold V1 + that preview into `data_editor.html` + retire mockups; then
the user's sw.js precache + VERSION bump + commit.

-----

## Round 3 (same day) — normalize feature display, slice S1

User directive: *"there should not [be] per-layer display rules… find and normalise. only one text
concatenation strategy for all data."* Slice S1: built `website/js/feature_display.js` (one branch-free
`featureDisplay` + `popupHtml`); the editor preview now calls it (local copy deleted). main.js NOT touched
(S3). Card: `tasks/12_field_schedule_editor/normalize_feature_display.md`. Cleared diff hash:
`a2b4ee0feb762e09de293205ad107a6426b71d24`.

ALL FIVE CLEAR (Witness/Quartermaster/Mason/Warden/Scribe):
- witness — clear. Re-verified by observation: editor routes through `window.AOPFeatureDisplay` (no local
  copy), `featureDisplay` branch-free, `/tmp/verify_preview.py` 4/4, and the cemetery finding (served data
  carries the real source/status that main.js:2244 overrides with constants). node --check both.
- quartermaster — clear. Justified shared destination with a committed S3 retirement plan; editor is a
  consumer (net less duplication); main.js untouched; C1=0/C2/C6 hold. Nit (non-blocking): engine's local
  `esc` duplicates FD.esc — LEFT INTENTIONALLY (the plain layout mockups don't load feature_display.js, so
  the engine must stay self-sufficient).
- mason — clear. All 7 interpolated values escaped (fuzzed evil input → 0 leaks/throws); no limiting code;
  one strategy, no per-layer switch; no dead code.
- warden — clear. main.js/panel.js/css/sw.js/data_editor.html untouched; slicing correct per move_slowly;
  no version bump due (module not in sw.js); git gate intact. (Pre-existing build_data_manifest.py /
  _data_manifest.json edits are NOT this slice's — prior session.)
- scribe — clear. Card + handoff complete, references real (main.js:1339/2187 + the per-layer consts), voice plain.

Owed: S2 bake the uniform display fields onto served features; S3 refactor main.js to the one strategy +
delete its 6 per-layer rules + verify popup parity by observation (carries the user's VERSION bump); S4
confirm editor==map.

-----

## Round 4 (same day) — normalize feature display S2+S3+S4 (the shipped viewer)

User: *"do what you must."* S2 found UNNEEDED (data already CMFS-normalized — verified). S3 done: main.js's
6 per-layer `listRow` + `poiPopupHtml` now route through `window.AOPFeatureDisplay`; `feature_display.js`
loaded in index.html + precached in sw.js. Zero per-layer display constants remain. Cleared diff hash:
`279b0974c3ecce940932b3ec1e3a011e5c66b74c`. Card: `tasks/12_field_schedule_editor/normalize_feature_display.md`.

ALL FIVE CLEAR (Witness/Mason/Quartermaster/Warden/Scribe):
- witness — clear. Live viewer 0 real errors (only headless-WebGL noise); shipped `AOPFeatureDisplay` on real
  data shows real provenance (cemetery full Comptroller source, trail `sfwda_trace_edited`) not the old
  constants; 0 display constants in code; field-presence audit — no layer goes blank; node OK.
- mason — clear. 6 listRow blocks keep the 10-key row shape; only display reads the changed values
  (collectStarredDestinations gates on highlight/predicate; search uses a separate index); dead `facets`
  removed; `poiDisplayName`/`escapeHtml` still used; no throw/limiting code.
- quartermaster — clear. Consolidation: popup renderer now one (module) + delegate; per-layer constants gone;
  matches the `event_schedule_geojson.js` shared-module pattern; C1=0/C2/C6 hold.
- warden — clear. VERSION/#appVersion left at v62 (user's bump, owed); diff = only the intended hunks; no
  re-bake overreach. NOTE: pre-existing `build_data_manifest.py`/`_data_manifest.json` (prior round) should
  ride a SEPARATE commit, not the normalize commit.
- scribe — clear. Card discloses the intended live-popup changes (table); owed stated; references real; voice plain.

OWED — the user's git gate: **`VERSION`/`#appVersion` v62→v63 bump + commit** (sw.js SHELL_ASSETS + index.html
changed). Warden's note: commit the normalize change separately from the stale manifest tooling.
