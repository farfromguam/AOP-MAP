# Icon system — collect, compare, normalize

TL;DR:
- The app's UI icons drifted: mixed stroke widths and very different art-fill, so
  some read heavy (Region, Pavilion, Topo) and some thin (Pencil, Tree, Locate).
- New standalone tool **`website/icon_master.html`** collects all 13 inline UI
  icons onto one master sheet, compares as-built vs normalized, flags the
  off-spec ones, and exports paste-ready SVG.
- Open decision (a visual fork): confirm the target stroke + how to treat the 4
  flagged outliers, then paste the normalized SVG back into `index.html`.

#aop #icons #ui #viewer #normalize

-----

## The problem

User: "the icons are different… some have thick line weights. we need them all
SVG, all the same base canvas size, all the same stroke width." The earlier
`brain/output/icon_audit/` pass measured rendered screenshots optically; this
card works from the **source** in `website/index.html`.

Findings from the source (all already inline SVG, all already `viewBox="0 0 22 22"`
— so canvas size is uniform; the drift is stroke + optical size):

- **Three stroke widths ship today:** `1.6` (10 icons), `1.4` (Tree/Satellite,
  Install), `1.2` (Pencil FAB).
- **Art-fill varies ~68–91%** of the 22-box. `Locate` fills **91%** — it is
  literally bigger than its neighbours. Most others sit ~70–77%.
- Optical weight (stroke ÷ art-extent) spans **0.077 → 0.107**, a ~1.4× spread,
  which is what the eye reads as "uneven."

## Inventory — 13 unique icons

| id | name | group | index.html | src stroke | notes |
|----|------|-------|-----------|-----------|-------|
| zoomRegion | Region | Zoom | 876 | 1.6 | corner brackets |
| zoomPark | Park (fit) | Zoom | 879 | 1.6 | heptagon + dot |
| zoomPavilion | Pavilion | Zoom | 882 | 1.6 | roof + columns (dense) |
| presetPark | Park map | Preset | 887 | 1.6 | folded map |
| presetTopo | Topo | Preset | 890 | 1.6 | contour waves |
| presetTrace | Trace | Preset | 893 | 1.6 | framed photo |
| presetSatellite | Satellite (tree) | Preset | 896 | **1.4** | tree — off-spec |
| lrTabSearch | Search | Left tab | 907 | 1.6 | also search field @932 |
| lrTabHot | Hot (flame) | Left tab | 913 | 1.6 | also JS glyph @7385 (identical path) |
| lrTabCal | Calendar | Left tab | 919 | 1.6 | reads as clipboard |
| locateBtn | Locate | Utility | 1032 | 1.6 | **91% fill — too big** |
| pwaInstallBtn | Install | Utility | 1046 | **1.4** | white-on-rust |
| panelFabPencil | Pencil (FAB) | FAB | 1074 | **1.2** | white-on-rust |

**Duplicates to keep in sync when editing:** Search is rendered twice (tab @907 +
search field @932); the Hot flame is also re-injected by JS @7385 — same path.

## The tool: `website/icon_master.html`

Standalone, self-contained (palette lifted from `index.html :root`). Served from
the `website/` dir like the other compare pages. Sections:

1. **Audit chips** — live count of stroke widths / canvas uniformity.
2. **Controls (sticky):** global stroke-width slider, optical-fit % (auto-scales
   each icon's bbox to a uniform footprint via a `<g transform>` +
   `vector-effect:non-scaling-stroke`, so stroke stays constant while size
   normalizes), preview-size, background swatches (cream/white/rust/moss/map to
   test contrast — Install & Pencil are white-on-rust), and toggles for
   auto-fit / force-round-caps / 22-grid overlay.
3. **Master sheet grid** — one card per icon: **as-built** vs **normalized**
   preview, metrics (src stroke, art-fill %, optical weight), an optical bar,
   inline **Edit markup** textarea (live re-render — this is the "revise &
   update" surface), and **Copy (stroke)** / **Copy (stroke+fit)** buttons that
   emit paste-ready `<svg>`. Off-spec cards get a red border + red metric.
4. **In-situ strip** — the normalized icons on faithful app chrome (cream pills
   & tabs, rust util/FAB) at ~22px, the real uniformity test.

Verified by observation (Playwright, served on :8001): 13 cards, 0 console
errors, flags fire on the 4 outliers (Tree, Locate, Install, Pencil), exports
are valid SVG. Default state (stroke 1.6, fit 72%) already makes the in-situ
strip read as one family.

## Open decision (visual fork — owner: user)

The page is the decision surface. Recommended target after eyeballing the
in-situ strip: **stroke `1.6`, optical-fit ~72%.** That implies four edits in
`index.html` (mirror the Search/Hot duplicates):

1. **Satellite/Tree** (896): `1.4 → 1.6`.
2. **Install** (1046): `1.4 → 1.6`.
3. **Pencil FAB** (1074): `1.2 → 1.6`.
4. **Locate** (1032): shrink art ~0.79 so it stops filling 91% — either via the
   exported `<g scale>` or by hand-pulling the crosshair arms inward.

`index.html` is intentionally **untouched** so the look can be confirmed on the
page first; applying is mechanical once the target is locked (copy each card's
normalized SVG over the matching block). Dense icons (Pavilion) may still read a
touch heavy at equal stroke — judge on the in-situ strip and redraw if needed.

## Revisions — 2026-05-31 (session 2, user punch-list)

Applied to **both** `website/index.html` and `website/icon_master.html` (so the
master sheet stays a faithful mirror of the shipping icons):

1. **Sidebar link** — `icon_master.html` added to the right-panel **Comparisons**
   list (top row, `◌ Master sheet` badge), so the tool opens from the app.
2. **Old flame restored** — the uncommitted single-outline 22×22 flame was
   reverted to the committed **Heroicons fire** (24×24, two paths — outer flame +
   inner curl), at the left-rail tab (`:913`, stroke 1.75) and the JS-injected
   hot glyph (`:7385`, stroke 2.1). On 24×24, 1.75 ≈ 1.60 on 22×22, so it reads
   in-family. The master sheet now carries per-icon `vb` (viewBox) support: a
   `24`-unit icon's stroke/optical/flag are judged in 22-equivalent terms, so the
   flame is **not** mis-flagged as a 4th stroke width.
3. **Filled dots** — first pass shrank them (Trace `1.3→1.0`, Park `1.1→0.9`),
   then the user judged that too small and they were re-sized up to the final:
   **Park centre `r=1.4`, Trace endpoints `r=1.4`, Locate centre `r=1.3`** (Locate
   was "almost right", small bump). All dots are `fill="currentColor"
   stroke="none"` so the root stroke doesn't ring them. **Demo-parity fix:** the
   master sheet's Park/Trace dot data was missing `stroke="none"`, so the demo had
   been drawing those dots *with* a 1.6 ring (fatter than the app) — added it so
   the demo now mirrors the app exactly.
4. **Locate + Pencil midline** — measured first (Playwright + ink-centroid): both
   were actually centred. Locate's real anomaly was **size** — it filled 91% of
   the canvas vs ~77% for the family, which is what read as "off". Fix: scaled the
   crosshair in (`r 6.4→5.4`, ticks pulled in, centre dot `1.3→1.1`) so it fills
   ~77% and sits like the others; kept it centred (a crosshair wants centre).
   Pencil's diagonal body sat a touch high in the rust FAB, so its path was nudged
   **down ~0.5** (`M…3.5→4`, etc.) to align its midline with the calendar/search
   cohort. Both confirmed on-device-style screenshots.

5. **Stroke unification — DONE (user said "bring those three to 1.6").** The last
   three off-spec icons were bumped to `1.6` in both files: Tree/Satellite
   (`:896`), Install (`:1046`), Pencil FAB (`:1074`). The master sheet now flags
   **0** icons; the audit reads "stroke 1.6 × 13 · one stroke weight — uniform ✓"
   (the flame's native 1.75 on its 24-canvas is the 1.6 equivalent). Verified on
   the rust surfaces — Install + Pencil at 1.6 read clean, not heavy.

6. **Container CSS — on-screen stroke parity (the real "still thicker" bug).**
   Uniform *source* stroke (1.6 in a 22-unit viewBox) only renders uniformly if
   every icon's SVG is displayed at the same pixel size, because on-screen stroke
   px = `displayPx × (strokeUU ÷ viewBox)`. Measured the live app (Playwright,
   computed-style stroke × rendered width) and found the offenders were **errant
   sizing rules on the containers**, not the SVGs:
   - `.panel.collapsed .panel-fab-pencil svg { width:24px }` → pencil rendered
     **1.75px** (24 × 1.6/22), visibly thicker. **Fixed → 22px** (= 1.6px). The
     56px FAB still reads fine with a 22px glyph.
   - mobile `@media(max-width:760px) .pill-bar .pill > button svg { width:20px }`
     → zoom+preset pills (incl. Tree) rendered **1.45px**, thinner than the 22px
     tabs. **Fixed → 22px** (= 1.6px). Verified no pill-bar overflow at 390px
     (`scrollWidth==clientWidth`, bar right 382 < 390).
   - The flame's 24-unit viewBox shown in a 22px `.lr-tab` already lands at
     1.604px — correct, left as-is.
   After the fix **every chrome-button icon renders at 1.6px on desktop and
   mobile.** The one remaining sub-1.6 is the **search-field magnifier**
   (`.search-icon`, 15px adornment inside the text input → 1.09px). That is a
   deliberate small-in-field size, NOT a button; matching its weight would need a
   ~2.35 source stroke (heavy in a delicate input). Left as-is, flagged for the
   user.

   **Lesson for the brain:** "same stroke-width" in the SVG ≠ same stroke on
   screen. Whenever an icon's container sizes its `svg` off the 22px baseline
   (`.lr-tab`/`.util-btn`/`.pill > button`/`#pwaInstallBtn`/FAB), the rendered
   weight drifts. Keep all chrome-icon `svg` boxes at 22px.

7. **Implementation normalized — the "fattens differently when zoomed" bug.**
   User zoomed in and saw the icons fatten unevenly → correctly inferred they were
   *built differently*. They were: a markup audit found (a) the flame on a 24-grid
   while the rest were 22, (b) `stroke-width` scattered on child paths for some
   icons but on the `<svg>` root for others, and (c) **inconsistent
   `stroke-linejoin`** — many defaulted to `miter`, which spikes out at sharp
   corners (Region brackets, heptagon vertices, pavilion peak, tree apex) and
   exaggerates when zoomed, while round-join/curved icons stayed soft. Same 1.6px
   *perpendicular* stroke, but visibly different corners.
   **Fix:** every icon rewritten to ONE canonical shape —
   `<svg viewBox="0 0 22 22" fill="none" stroke="currentColor" stroke-width="1.6"
   stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">` + geometry
   only (no per-child stroke attrs; filled dots keep `fill="currentColor"
   stroke="none"`). The flame was converted off its 24-grid by scaling both paths
   ×22/24 (arc-aware: rx/ry/endpoints scale, rotation+flags untouched —
   pixel-identical to the original, verified). The JS hot glyph (`#7385`) got the
   same 22-grid/1.6 treatment. Verified (Playwright): **all 14 icons now report
   viewBox `0 0 22 22`, root `1.6 / round / round`, ZERO child stroke attrs,
   1.6px effective**; zoom-render confirms every corner is now round, no miter
   spikes; 0 console errors. The only sub-1.6 is still the 15px in-field search
   magnifier (now canonical in structure, just smaller by design).

**Done. Every UI icon is now structurally identical — same 22×22 viewBox, same
root attributes, round caps + joins, 1.6 source stroke, 1.6px on screen — so they
differ only in their geometry and fatten uniformly at any zoom.** Lesson for the
brain: enforce the single canonical `<svg>` shape above for any new chrome icon;
never put stroke attrs on child paths or omit `stroke-linejoin`. No open forks.

## Status

`website/icon_master.html` + `website/index.html` updated + verified by
observation (Playwright, 0 console errors; flame restored, dots smaller, locate
resized, pencil nudged, sidebar link live). All uncommitted. Prior scratch
measurement artifacts remain under `brain/output/icon_audit/`.
