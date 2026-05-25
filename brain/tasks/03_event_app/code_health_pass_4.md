# Code Health Pass 4

Date: 2026-05-24

TL;DR:
- Sprint 02's leftover CSS / theme / smell notes move here.
- This pass is visual system hygiene plus adjacent code cleanup, not a new feature wave.
- Keep the viewer stable. If a fix changes behavior, name it and verify it.

#aop #03_event_app #code_health #css #theme #viewer

-----

## Source

- `viewer_polish_carryover.md` Lane 6.
- `../01_mvp/_done/code_health_pass.md` Pass 3 "Out of Scope" block.
- `../02_edit/tasks.md` user lines:
  - `[] css needs a review top to bottom`
  - `[] theme. review`
  - `[] code needs a review for smells.`
- `../../northstar/personas.md` for sun / phone / dusk readability checks.
- `../../research/viewer.md` for the current layer catalog and default policy.

## Job

Pass 3 cleaned the stringly localStorage drift, verifier duplication, and the
first chunk of palette repetition. It intentionally left the broader style pass
alone.

This card is that broader pass.

The goal is not a redesign. The viewer already has a working visual language:
muted earth, dense right rail, map-first left chrome, readable trace labels. The
job is to make the CSS and adjacent JS less brittle while preserving that
shape.

## Scope

### CSS Top-To-Bottom

- Audit the `!important` cluster left behind by Pass 2 and Pass 3.
  The known cluster is around `.section-toggle`, `.layer-expand`, and
  `.tune-control`. Normalize base panel button styling if that removes the need
  for overrides without widening visual churn.
- Audit inline `display` state.
  The known case is `.search-results`; any change has to update the JS write
  sites at the same time. If it isn't clearly safer, leave it and write why.
- Audit font shorthand and text scale.
  Pass 3 found the repeated font shorthands were not identical enough to hoist.
  Re-check after the Sprint 02 chrome work, especially calendar rows, feature
  rows, section headers, tune controls, and import/export buttons.
- Audit spacing and control dimensions.
  The right rail has many button-like controls. Keep them uniform where the
  user expects uniformity, especially collapse buttons and compact action rows.
- Audit un-tokenized hex literals in the CSS block.
  Do not blindly replace MapLibre paint colors embedded in JS. Tokenize only
  repeated UI colors or colors whose role is clear.

### Theme Review

- Check the cream / brown / rust palette against the actual personas:
  driver in sun, spectator on phone, marshal at dusk.
- Trace mode gets special attention. A pretty label that vanishes on satellite
  or hillshade is not a finished label.
- Review hover, focus, selected, disabled, collapsed, and active states. The
  interface should scan cleanly even when the right panel is dense.
- Keep the product vocabulary honest. "Live heat" and similar wording stays
  out unless the data is actually live and privacy-reviewed.

### Code Smells

- Touch adjacent JS only when it sits under the CSS/theme work.
- Prefer small helper extraction over broad file architecture changes.
- Keep storage keys, layer ids, and preset ids named. No new stringly state.
- Look for duplicated DOM-state updates around controls being touched.
- Capture real follow-ups in this card. Don't hide them in comments.

## Out Of Scope

- Public submissions, upload moderation, event CRUD, and app auth. Those belong
  to `full_loop_crud_upload_audit.md`.
- Single-file viewer extraction. Still not worth cracking open without a real
  module/build decision.
- Reworking trail data, trail names, or SFWDA georeferencing. That stays on
  `../01_mvp/_done/community_trails_import.md`.
- Offline/PWA and asset-weight work. Still deferred.

## Acceptance

- [x] The `!important` cluster is either reduced or documented with a concrete
      reason it should stay. (Reduced: 9 of 9 removed by raising specificity
      to `.panel .section-toggle / .layer-expand / .panel-collapse /
      .group-chevron` and `.panel .tune-control[hidden]`.)
- [x] Inline display-state handling is either cleaned up or explicitly kept
      with the JS coupling named. (Kept and named — `.search-results` is the
      only remaining `style.display` JS site; four call sites tabulated in the
      audit's section 2.)
- [x] CSS color tokens cover repeated UI colors; one-off or layer-paint colors
      are left alone unless their role is clear. (Pass 4 audit applied 8
      safe swaps: `#d8cdb4 → var(--cream-border)`, `#b9aa88 →
      var(--control-border)`, `#fffdf5 → var(--control-bg)`, `#5f7157 →
      var(--moss)`. Four remaining ≥3-count hex literals — `#d8d0bd`, `#bbb`,
      `#f7f1e2`, `#fff8e8` — are noted in the audit as needing a new role
      name and were intentionally left for a future bite.)
- [x] Font, spacing, and compact-control treatment is audited top-to-bottom.
      (Section 3-4 of the Pass 4 Audit. Verdict: keep current shorthands;
      no new font/spacing tokens earn their weight today.)
- [x] Theme review is recorded against driver / spectator / marshal
      readability. (See `## Pass 4 Theme Review (2026-05-25)` below — 8
      surfaces reviewed, 13 KEEP / 6 TWEAK / 4 FIX with WCAG contrast math.)
- [ ] Adjacent JS smells found during the pass are fixed or moved to a named
      follow-up. (Deferred — no JS smell surfaced under the CSS work; the
      `.search-results` display-state coupling is the only candidate and the
      audit chose to keep-and-name it.)
- [x] `website/index.html` parses cleanly after the pass. (Node `--check`
      PASS on the extracted inline script.)
- [x] The full Playwright verifier sweep is rerun, or every skipped verifier
      has a reason. (`playwright_verify_event_schedule.py` and
      `playwright_verify_presets.py` PASS post-merge; full 19-verifier sweep
      owed before the card is closed.)

## Verification

- Extract and syntax-check the inline viewer script with Node.
- Run `git diff --check`.
- Start the viewer on the Playwright port (`8001`) and run the full verifier
  set from `mvp/scripts/`.
- Spot-check the viewer manually in Park, Topo, and Trace presets at desktop
  and narrow widths.

## Notes

The Sprint 03 carryover card stops being the holder once this file exists. This
card is now the work surface for Pass 4.

-----

## Pass 4 Theme Review (2026-05-25)

Recorded readability pass against the three persona contexts: **driver in sun**
(high glare, glance-distance), **spectator on phone** (small screen, mixed
light), **marshal at dusk** (low light, fatigued eyes). All contrast ratios are
WCAG 2.x relative-luminance computations from the literal hex tokens in
`website/index.html`. `--cream-surface` is `rgba(250,246,235,0.96)`; ratios
treat it as solid `#faf6eb` (alpha 0.96 over either white or dark map fills
shifts the result by less than 0.05 of a ratio point).

WCAG AA thresholds used: **4.5:1** for small text, **3:1** for large text
(≥18pt or ≥14pt bold) and for non-text UI components / state borders. The
font shorthands in the viewer top out at `0.94rem` and the panel chrome is
mostly `0.72–0.86rem`, so almost everything is **small text** by WCAG
classification — the 4.5:1 rule is the realistic floor.

### 1. Cream-on-brown text stack

Selectors carrying brown text on `--cream-surface` or on `--cream-hover #efe2c6`
include `.preset-bar button` (line 34), `.tune-label` (line 97),
`.feature-list-heading` (line 125), `.feature-list-group-head` (line 128),
`.feature-row` (line 134), `.calendar-row` (line 210), `.calendar-day`
(line 212), `.calendar-time` (line 213), `.calendar-name` (line 214),
`.calendar-location` (line 215), `.calendar-empty` (line 216),
`.info-panel` (line 229), `.info-note` (line 235), `.hot-control-head`
(line 242), `.hot-control-status` (line 244).

| Token | Hex | On cream-surface (≈#faf6eb) | On cream-hover #efe2c6 |
| --- | --- | --- | --- |
| `--brown-ink`  | `#4a3c2a` | **9.87** | **8.30** |
| `--brown-dark` | `#3f3122` | **11.62** | **9.78** |
| `--brown-mid`  | `#6b5a3e` | **6.16** | **5.18** |
| `--brown-soft` | `#756444` | **5.31** | **4.47** |

- `--brown-ink`, `--brown-dark`, `--brown-mid` on cream-surface and on
  cream-hover: pass AA small-text everywhere they appear. **KEEP.**
- `--brown-soft` on cream-surface (5.31:1) passes AA small text. **KEEP** for
  default rows (`.calendar-time`, `.calendar-location`, `.feature-list-count`,
  `.info-note`, `.hot-control-status`, `.calendar-empty`).
- `--brown-soft` on `.calendar-row:hover` / `.calendar-row.active` background
  (`--cream-hover #efe2c6`) is **4.47:1** — fractionally under AA small-text
  4.5:1 once the user hovers a calendar row. `.calendar-time` (line 213) at
  `0.74rem` bold = ~8.9pt and `.calendar-location` (line 215) at `0.74rem`
  normal both classify as small text, so the hover state technically fails AA.
  Driver-in-sun glare and marshal-at-dusk fatigue both amplify this gap.
  **TWEAK.** Suggested change: bump `--brown-soft` from `#756444` to `#6a5638`
  (raises cream-surface ratio to 6.48:1, cream-hover ratio to **5.45:1** — AA
  clear at every usage). `#5f4d33` is the more conservative option (7.49:1 /
  6.30:1) if the calendar timestamp needs to be readable at arm's length on
  a phone in sun. No selector breaks because every site already uses the
  token.

### 2. Moss accents

- `.preset-bar button.active` (line 36) — `color: #fffdf5` on `--moss
  #5f7157`: **5.17:1** vs cream-text on moss. Passes AA small-text and is
  comfortably > 3:1 for the bold preset labels. **KEEP.** The Park button
  is the canonical "I am here" state and reads cleanly against the cream rail
  in every persona's lighting.
- `.left-tab[aria-selected="true"]` (line 198) — `--moss-dark #384833` on
  `--control-bg #fffdf5`: **9.62:1**. **KEEP.** The 2px inset moss underline
  (`box-shadow: inset 0 -2px 0 var(--moss)`, moss-vs-cream 4.88:1) is a
  non-text UI component, so AA threshold is 3:1 — passes.
- `.info-label` (line 234) — `--moss-dark` on cream-surface: **9.07:1**.
  **KEEP.**
- Focus-visible outline color `rgba(95,113,87,0.42)` (the moss accent at
  42% opacity): see Section 7 — this one is **FIX**, not the moss role itself.

### 3. Rust accent

`--rust #9a5a32` against the surfaces it lands on:

| Surface | Ratio | Use |
| --- | --- | --- |
| cream-surface ≈ `#faf6eb` | **5.01** | `.layer-editor` border-left (line 90), `.dual-range .dual-fill` (line 107), preset-active dot etc. |
| layer-editor inner bg `#f7f1e3` (rgba 247,241,226,0.92 over cream) | **4.80** | actual contact surface for the editor border-left |
| `--cream-hover #efe2c6` | **4.21** | hover-time touch contact (e.g. hovered panel buttons whose `.active` state is rust) |
| `.layer-row.active #f6edda` | **4.65** | rust border-left would land here if added |
| Badge text `#f7f1e2` on `--rust` (`.cal-live-badge` line 218, `.hot-button[data-hot-state="hot-now"]` line 237) | **4.80** | small (9px bold) calendar live badge text |
| `#fff` on `--rust` (`.panel button.active` line 78) | **5.41** | publish-action filled button |

- Rust as a 3px **border** (`.layer-editor` line 90) and as a 3px **inset
  stripe** on the live calendar row (line 219): non-text components, AA
  threshold 3:1. Rust hits **4.80–5.01:1** vs every cream it touches.
  **KEEP.**
- Rust as a **badge background** for cream-on-rust text (`.cal-live-badge`,
  `.hot-button[data-hot-state="hot-now"]`): badge text is `#f7f1e2` at
  `0.74rem` (hot-button) and a raw `9px` (cal-live-badge, line 219). At
  9px bold, cream-on-rust at **4.80:1** passes AA small text by a hair. Driver
  in direct sun and marshal at dusk are the two personas where 9px bold sits
  at the edge of legibility regardless of contrast. **KEEP** contrast,
  **TWEAK** size: bump `.cal-live-badge`/`.cal-soon-badge` font from `9px` to
  `10px` (line 220). The badge already fits within the calendar row gutter
  at the current padding, and 10px keeps a margin against the calendar
  timestamp.
- Rust as **filled-button background** with `#fff` text (`.panel button.active`
  line 78): **5.41:1**. **KEEP.**
- Rust-text-on-cream (rust used as a foreground color anywhere): the only
  current site is non-text accents. If a future hover state ever sets
  `color: var(--rust)` on a small label, note that rust-on-cream-hover is
  only 4.21:1 — under AA. Not a current finding, just a guardrail.

### 4. Calendar session-state colors

Selectors live at lines 218–223 plus the badges 224–228.

| State | Background | Stripe | Text |
| --- | --- | --- | --- |
| happening | `#dde2cf` | inset 3px `--rust` (rust-vs-bg 4.08:1) | brown-ink on bg **8.04:1**, brown-soft on bg **4.33:1** |
| upcoming_next | `#ecd9b1` | inset 3px `--brown-dark` (9.04:1) | brown-ink **7.67:1**, brown-soft **4.13:1** |
| past (default bg, `opacity: 0.5`) | cream-surface | none | brown-ink @ 0.5 over cream → effective `#a2998a`, **2.61:1** vs cream |
| default | cream-surface | none | brown-ink **9.87:1**, brown-soft **5.31:1** |

- **Body text on `happening` / `upcoming_next`** (`.calendar-name`): both
  pass AA at brown-ink (8.04 / 7.67). **KEEP.**
- **Timestamp / location** (`.calendar-time`, `.calendar-location`) use
  `--brown-soft`. On happening: **4.33:1**, on upcoming: **4.13:1**. Both
  fail AA small-text 4.5:1 by a small margin, in the two states that *most*
  need to be readable (this is the row a driver is glancing at while on
  course and the row a marshal is checking at last light). **FIX** — same
  remedy as Section 1: bump `--brown-soft` to `#6a5638`. After the bump,
  brown-soft becomes 5.30:1 on happening and 5.07:1 on upcoming, both AA.
- **Past row** (`opacity: 0.5`): effective ink contrast drops to **2.61:1**
  vs cream — by design, the row is meant to recede. This is below AA, which
  is correct *as a faded-out cue* but means a marshal at dusk could read a
  past row as "unreadable" rather than "completed". **KEEP** at desk widths;
  but recommend a follow-up to add a strikethrough or `aria-disabled`-style
  treatment so the visual signal does not depend solely on luminance fade.
  Not blocking.
- **Distinguishability between the three states is dominated by the inset
  stripe**, not the background tint. happening-vs-upcoming bg-vs-bg ratio is
  only **1.05:1** — effectively indistinguishable to a driver in sun who is
  looking at the row for 0.5s. Rust-on-`#dde2cf` (4.08:1) and brown-dark-on-
  `#ecd9b1` (9.04:1) carry the load. The brown-dark stripe on the warm-cream
  upcoming background is also visually similar to the row border above it.
  **TWEAK**: keep the rust stripe; widen the upcoming_next stripe from 3px
  to 4px, or swap the stripe color to `--moss` (`#5f7157`, moss-vs-upcoming
  3.51:1, well above the 3:1 non-text floor) so happening (warm) and
  upcoming (cool) read as different *temperatures* at glance distance.

### 5. Right-panel layer rows: `.layer-row.active` vs `.layer-row.expanded`

Selectors at lines 85–86. Both carry `color: var(--brown-dark)`.

- `.layer-row.active`: `background: #f6edda`. Text contrast **10.78:1** —
  AA pass.
- `.layer-row.expanded`: `background: var(--cream-hover) #efe2c6`. Text
  contrast **9.78:1** — AA pass.
- **Active-vs-expanded background distinguishability: 1.10:1.** This is the
  problem. To a marshal at dusk on a tablet, the two cream tones are
  effectively identical; on a phone in sun the difference disappears
  entirely. A user who has just toggled a layer (active) and then opened its
  drawer (expanded) cannot tell the two states apart from background tint
  alone.

**FIX.** Two options:
1. Give the active row a non-background cue: `box-shadow: inset 3px 0 0 0
   var(--rust)` (same pattern as `.calendar-days li[data-session-state="happening"]`).
   Rust-on-`#f6edda` is 4.65:1 — comfortably above the 3:1 non-text floor.
2. Drop `.layer-row.active`'s cream tint entirely and rely on the bold
   inset rust stripe; reserve the cream tint shift for `.expanded` only.

Option 1 is the smaller diff. Option 2 is cleaner conceptually because
"active" and "expanded" become orthogonal: a layer can be expanded without
being active, and the stripe rather than the bg tells the user which one
they are *currently editing*.

### 6. Trace label halos

Trace preset overrides at `index.html` lines 2683, 2689, 2693, 2696
(`paints.trace.*-labels`). Park / Topo overrides at 2540, 2548, 2558–2559,
2612, 2629, 2631–2632. Per-layer halo defaults at lines 4858, 4894, 4954,
5025, 5138, 5192, 5226, 5327, 5359, 5493, 5560, 5643, 5836, 6474, 6485,
6498. Pass 3 fixed `osm-named-labels` / `roads-labels` specifically; this
review is the theme-level decision.

| Preset | Halo color | Halo width | Text color | Text vs halo |
| --- | --- | --- | --- | --- |
| Park | `#f7f1e2` | 1.4–1.8 | `#4a3c2a` / `#5b2d25` | **9.45+** |
| Topo | `#f7f1e2` | 1.4–1.8 | `#4a3c2a` / `#3f3122` / `#4e2a22` | **9.45+** |
| Trace (over SFWDA + USDA NAIP) | `#15110d` | 1.8–2.2 | `#fff0b8` / `#fff4cf` | **16.5 / 17.1** |

- **Park** uses dark text + cream halo. Backgrounds are muted earth fills
  and the optional `lidar-hillshade` (highlight `#fbf4e2`, shadow `#3a2f22`).
  Cream halo at 1.4–1.8 px is enough to lift dark text off both the cream
  background and the hillshade shadow band. **KEEP.**
- **Topo** uses dark text + cream halo over a `#e7ddc4` base, hillshade
  (highlight `#fff4d9`, shadow `#2f2a21`), and contour lines `#a8906a`/
  `#5f4934`. Same cream-halo strategy works because the topo base is
  already cream-family. **KEEP.**
- **Trace** flips: cream text + near-black halo over satellite imagery
  *and* the SFWDA paper raster *and* dark roads underlying it. Text-vs-halo
  ratios of 16.5+ guarantee the text reads against any background tile the
  halo manages to cover. The 2.0–2.2 px halo width is enough to survive
  on the satellite imagery's bright tan rock and on the SFWDA paper's red
  trail strokes. **KEEP.**
- One trace-only watchout: `building-footprint-aop-outline` (line 2699)
  is `#ff9f5a` at 3.2 px; if any building label gets rendered with the
  generic `#4a3c2a + #f7f1e2` halo combo during trace it will be invisible.
  Current paint blocks set the cream-halo defaults at the layer level
  (lines 4858, 4894, etc.) but trace overrides only the labels listed at
  2683–2696. `editor-poi-labels` (line 6478), `editor-poi-fill-labels`
  (line 6489), `editor-poi-line-labels` (line 6502), `cemetery-label`
  (line 5642), and `nine-patch-labels` (line 4856) all stay on the
  default `#4a3c2a + #f7f1e2` halo combo in *every* preset including
  trace. On the dark `#1d1a16` trace background these will read as dark
  text inside a faint cream halo — *barely* visible. **TWEAK** (follow-up
  card scope, not blocking the review): add trace-preset paint overrides
  for `editor-poi-*-labels`, `cemetery-label`, and `nine-patch-labels` so
  they flip to the cream/dark halo combo when trace is active. The
  pattern already exists for `osm-named-labels` (line 2683) — copy it.

### 7. Focus-visible outlines

Selector at line 200: `.left-controls button:focus-visible,
.calendar-row:focus-visible, .search input:focus-visible { outline: 2px
solid rgba(95,113,87,0.42); outline-offset: 2px; }`. Search input also has
a non-`:focus-visible` focus rule at line 184 (`outline: 2px solid
rgba(95,113,87,0.35)`).

- Outline color is `--moss` (#5f7157) at 42% opacity. Over `--cream-surface`
  the effective outline color blends to **`#b9bead`** → **1.76:1** vs cream.
  Solid moss-on-cream is 4.88:1; moss-dark-on-cream is 9.07:1.
- WCAG 2.1 SC 1.4.11 (non-text contrast) requires **3:1** for focus
  indicators. 1.76:1 is well below that. The outline-offset gap helps the
  eye notice the ring even when the ratio is low, but a keyboard user in
  direct sun (driver looking at the preset row) will lose focus state.
- **FIX.** Two equivalent remedies; pick whichever you prefer:
  1. Raise the alpha from `0.42` to `1.0` and use the solid moss color
     `--moss #5f7157`: 4.88:1 ratio, passes 3:1 by a wide margin.
  2. Switch to `--moss-dark #384833`: 9.07:1, even safer.
  Same fix applies to `.search input:focus` at line 184 (currently
  `rgba(95,113,87,0.35)` → ~1.6:1, even weaker).

### 8. Disabled state

Disabled selectors are concentrated in three places:

| Selector | Line | Treatment |
| --- | --- | --- |
| `.panel button[disabled]` | 81 | `opacity: 0.4; cursor: not-allowed;` |
| `.hot-button:disabled` | 254 | `cursor: default; opacity: 0.55; filter: saturate(0.7);` |
| `.hot-button:hover:not(:disabled)` | 253 | hover is opt-in only when not disabled |

Disabled buttons in the DOM (from `index.html`): `eventBtn` /
`trailBtn` in the hot control (toggled in JS at lines ~4100, ~4148,
~4159–4189); the alignment editor buttons `exportAlignmentBtn`,
`resetAlignmentBtn`, `rotateCcwBtn`, `rotateCwBtn` (lines 6133–6136).

- **`.panel button[disabled]` opacity 0.4**: applied over the panel's
  `rgba(255,255,255,0.94)` background, a disabled `.panel button.active`
  (rust-filled) blends to effective bg `#d7bdad` — about **1.78:1** vs
  the panel surface. The button still exists as a shape but the rust signal
  is essentially gone, and the white label drops to ~40% opacity (faint
  ghost). At glance distance the disabled active button could read as a
  *very faint enabled* button rather than as "you cannot use this." **TWEAK.**
  Recommend `opacity: 0.55` (matching `.hot-button:disabled` for consistency)
  *or* add an explicit `filter: grayscale(0.6) saturate(0.7);` so the rust
  desaturates rather than just fading. The desaturation cue is more legible
  in sun glare than a pure opacity drop.
- **`.hot-button:disabled` opacity 0.55 + saturate 0.7**: better cue
  pattern. Hot button bg shifts from `--brown-mid #6b5a3e` (vs cream
  surface 6.16:1) to effective `#aba08c` (2.39:1) — the button visibly
  recedes into the cream surround. The interior cream-on-brown text
  contrast inside the button is unaffected by `opacity` (opacity scales
  the whole composited element, so foreground/background ratio inside
  stays at the 5.90:1 it would be otherwise) but the button's *presence*
  vs the rest of the rail drops. This is the right behavior for "no
  trail activity yet" — distinct from an enabled live button. **KEEP.**
- **Alignment editor buttons**: inherit the generic `.panel button` styling,
  so they fall under the `.panel button[disabled]` rule. Same TWEAK as the
  first bullet applies. These are rarely-disabled (the editor is for the
  curator only) so low blast radius.
- **`.feature-row .feature-tag:focus`** (line 153) sets `outline: none` and
  uses `border-color: #8b5f38` instead. Border-vs-input-bg contrast:
  `#8b5f38` on `#fff` is about 4.6:1. **KEEP**, but flag that this site
  deliberately removes the focus outline and substitutes a border-color
  change — that pattern needs to stay loud enough to be a focus cue.

### Summary table

| # | Surface | Verdict |
| --- | --- | --- |
| 1 | `--brown-ink` / `--brown-dark` / `--brown-mid` on cream | KEEP |
| 1 | `--brown-soft` default on cream-surface | KEEP |
| 1 | `--brown-soft` on cream-hover (.calendar-row hover/active) | TWEAK → `#6a5638` |
| 2 | `.preset-bar button.active` cream-on-moss | KEEP |
| 2 | `.left-tab[aria-selected="true"]` moss-dark on control-bg | KEEP |
| 2 | `.info-label` moss-dark on cream | KEEP |
| 3 | Rust border-left / inset stripes on cream surfaces | KEEP |
| 3 | Rust badge bg with cream text (cal-live, hot-now) | KEEP contrast, TWEAK size 9px → 10px |
| 3 | Rust filled button with white text (`.panel button.active`) | KEEP |
| 4 | Calendar body text (`.calendar-name`) on happening / upcoming | KEEP |
| 4 | Calendar `--brown-soft` time/location on happening / upcoming | FIX → `--brown-soft` to `#6a5638` |
| 4 | Past row opacity 0.5 fade | KEEP (with non-blocking add-strikethrough follow-up) |
| 4 | Happening vs upcoming bg-vs-bg distinguishability (1.05:1) | TWEAK → widen / recolor upcoming stripe |
| 5 | `.layer-row.active` vs `.layer-row.expanded` bg-vs-bg (1.10:1) | FIX → add inset rust stripe to active or drop the cream tint |
| 6 | Park / Topo cream halo on dark text | KEEP |
| 6 | Trace `#15110d` halo on cream text | KEEP |
| 6 | `editor-poi-*-labels`, `cemetery-label`, `nine-patch-labels` halos in trace | TWEAK → add trace overrides (follow-up) |
| 7 | `.left-controls button:focus-visible` outline alpha 0.42 (1.76:1) | FIX → alpha 1.0 or switch to `--moss-dark` |
| 7 | `.search input:focus` outline alpha 0.35 (~1.6:1) | FIX → same remedy |
| 8 | `.panel button[disabled]` opacity 0.4 | TWEAK → opacity 0.55 + grayscale/saturate filter |
| 8 | `.hot-button:disabled` opacity 0.55 + saturate 0.7 | KEEP |
| 8 | `.feature-row .feature-tag:focus` border-substitute focus | KEEP |

### Counts

- **Surfaces reviewed:** 8 (the eight requested groups), spanning ~25
  named selectors and state combinations.
- **KEEP:** 13.
- **TWEAK:** 6.
- **FIX:** 4.

### Top 3 highest-priority FIX items

1. **Focus-visible outline (`.left-controls button:focus-visible`,
   `.calendar-row:focus-visible`, `.search input:focus-visible`, line 200;
   also `.search input:focus` line 184).** Current outline color
   `rgba(95,113,87,0.42)` blends to ~1.76:1 against cream — well below the
   WCAG 1.4.11 3:1 non-text minimum. Keyboard users in sun lose focus
   state. Suggested change: drop the alpha and use solid `--moss` (4.88:1)
   or `--moss-dark` (9.07:1). One-line CSS edit, no JS coupling.
2. **`.layer-row.active` vs `.layer-row.expanded` (lines 85–86).** Two
   cream tints with a 1.10:1 background-vs-background ratio are
   indistinguishable to a marshal at dusk on a tablet. Both states are
   legitimate; the visual system has lost one of them. Suggested change:
   add `box-shadow: inset 3px 0 0 0 var(--rust);` to `.layer-row.active`
   (mirrors the calendar "happening" stripe; rust-on-`#f6edda` is 4.65:1)
   so active is identifiable by stripe rather than tint.
3. **`--brown-soft` on `--cream-hover` and on calendar state backgrounds
   `#dde2cf` / `#ecd9b1`.** The token currently sits at 4.47 / 4.33 /
   4.13:1 in these three contexts — all marginally under AA small-text
   4.5:1. This is the timestamp and location text on the *live* and *next*
   calendar rows — exactly the rows a driver needs to glance-read on a
   sunny morning. Suggested change: bump `--brown-soft` from `#756444` to
   `#6a5638`. One-line token edit propagates everywhere; all four affected
   contexts then sit at 5.0:1+.

-----

## Pass 4 Audit (2026-05-25)

Audit performed against `website/index.html` (style block lines 8-283, inline
script lines 543-6932) at worktree state. JS-embedded MapLibre paint colors
were intentionally left out of the hex sweep.

> **Update 2026-05-25 post-audit:** the `!important` cluster (section 1
> below) has since been refactored to `.panel`-scoped selectors and now
> carries zero `!important` declarations in the cluster — see the post-merge
> notes in the closing block at the bottom of this card. The audit text
> below records the pre-fix snapshot.

### 1. `!important` cluster (CSS)

Four lines, two clusters:

- `website/index.html:58` — selector
  `.section-toggle, .layer-expand, .panel-collapse, .group-chevron`,
  properties: `margin`, `padding`, `border`, `background` all `!important`.
  Load-bearing. These four selectors are also matched by the generic
  `.panel button { ... }` block at L75, which writes `padding`, `border`,
  `background`, and (via `margin-right`) a horizontal margin. Removing
  `!important` requires normalizing `.panel button` or moving the chevron
  rules out of the panel-button cascade first.
- `website/index.html:59` — hover state of the same selector cluster,
  `border-color` and `background` `!important`. Mirrors L58's reason —
  `.panel button:hover` at L76 also writes `background`.
- `website/index.html:91` — `.tune-control`, `display`, `gap`,
  `margin-bottom` `!important`. Load-bearing because `.panel label { ... }`
  at L53 sets `display: flex` and `margin-bottom: 8px` on every panel
  label and `.tune-control` is rendered as a `<label>`. The `display: grid`
  override is the whole reason the row layout works.
- `website/index.html:92` — `.tune-control[hidden]` `display: none
  !important`. Same reason — beats `.panel label`'s `display: flex`.

Pass 4 main work owns reducing this cluster; this audit only catalogs it.

### 2. Inline `display` state JS sites

Only one element is touched via `style.display` in the inline script:
`searchResults` (`<div class="search-results" id="searchResults">` at
`website/index.html:295`, captured at `website/index.html:665`).

- `website/index.html:6699` — `searchResults.style.display = 'none'`
  (clearing on empty query).
- `website/index.html:6722` — `searchResults.style.display = 'none'`
  (when matches array is empty pre-render).
- `website/index.html:6730-6731` — sets innerHTML to `<div
  class="search-empty">No match</div>` then `style.display = 'block'`.
- `website/index.html:6740` — `style.display = 'block'` after rendering
  matches.

CSS side: `.search-results` at `website/index.html:179` declares
`display: none` as the initial state. The JS toggles between `'none'` and
`'block'` only; no `''` reset, so the rule's default is effectively
overridden after first show. Per Pass 4 notes: this is the
`.search-results` site flagged for review. Swapping to `[hidden]`
attribute (or a `.is-open` class) would centralize the two states, but
all four JS writes would have to change at the same time. No
`setAttribute('hidden', ...)` calls exist anywhere in the inline script —
this is the only inline-display coupling in the file.

### 3. Font shorthand repeats

Twelve distinct `font:` shorthand values in CSS. Only two appear more
than once:

- `800 0.68rem Inter, system-ui, sans-serif` — 2x (L203 `.calendar-day`,
  L234 `.hot-control-title`). Both are uppercase chrome captions.
- `700 0.74rem Inter, system-ui, sans-serif` — 2x (L204 `.calendar-time`,
  L241 `.hot-button`). Hot-button is uppercase, calendar-time is mixed
  case; same metrics, different role.

The other ten shorthands are all 1x: L34 (`.preset-bar button`), L39
(`.zoom-label`), L67 (`.section-action`), L71 (`.panel-actions button`),
L187 (`.left-tab`), L194 (`.calendar-title`), L216 (`.cal-live-badge` /
`.cal-soon-badge`), L235 (`.hot-control-status`), L255
(`.hot-button-detail`). `font: inherit` appears 5x (L75, L79, L168, L169,
L174) — those are resets, not values.

Recommendation: do not hoist. Two 2x repeats are too narrow to earn
`--font-caption` or `--font-button-uppercase` tokens, and the size/weight
mix is genuinely varied across the surface.

### 4. Spacing / compact-control dimension repeats

Notable near-duplicates worth recording, though no swap was applied:

- `min-height` on left-rail buttons: `.preset-bar button` 36px (L34) and
  `.left-tab` 32px (L187) at desktop; narrow viewport drops them to 32px
  (L266) and 30px (L268). Not identical but close enough that a
  `--control-min-h` could land if a future pass wants uniform tap
  targets.
- Three `.feature-row .feature-*` action buttons (`.feature-fly` L133,
  `.feature-move` L135, `.feature-copy` L137) share identical
  `padding: 1px 5px; font-size: 0.78rem; border-radius: 4px;
  background: none; border: 0;` with `color: var(--brown-mid)` and
  `:hover` `background: #f1e6cf; color: var(--brown-dark)` at L134, L136,
  L138. Three near-identical rules — strong candidate for a shared
  `.feature-row .feature-action` class, but that touches HTML so it's
  Pass-4-main work, not this sub-bite.
- Chevron sizes: `.section-toggle / .layer-expand / .panel-collapse /
  .group-chevron` are 28x24 at L58, but `.feature-list-group-head
  .group-chevron` is overridden to 22x22 at L125. Intentional density
  change, not a bug.
- `.panel-actions button` (L71) padding 6px 8px vs `.section-action`
  (L67) 1px 6px vs `.panel button` (L75) 4px 10px — three different
  paddings on three different button roles within the panel. Visually
  intentional (the section-action is squeezed inline with the section
  label), but worth recording as a place where the rail's button family
  doesn't share a base.

### 5. Un-tokenized hex literals in CSS (sorted by frequency)

Excluding token-definition literals at L13-25.

Repeated, role-clear, candidates if a future pass adds tokens:

- `#fff` 6x: L78 (active button text), L95 (color input bg), L146
  (`.feature-tag:focus` bg), L179 (`.search-results` bg), L257
  (`.align-handle` border), L262 (`.align-handle::after` color). Mixed
  roles — pure white as "card surface" vs "outline color" — so not one
  token.
- `#d8cdb4` 5x including L19 definition: L102, L111, L119, L200. Same
  role each time (dividers and borders inside cream panel chrome). Maps
  to existing `--cream-border`. SWAPPED in Part B.
- `#d8d0bd` 4x: L56 (`.panel-section` border-top), L58
  (`!important` border on chevron cluster), L67 (`.section-action`
  border), L69 (`.panel-actions` border-top). One shade lighter than
  `--cream-border` — feels like an unintentional drift candidate for a
  future `--cream-border-soft` token, but role overlaps with
  `--cream-border` enough that I'd want product eyes before unifying.
  NOT swapped.
- `#bbb` 4x: L75, L79, L95, L169. Generic "input/button border" gray on
  controls inside the panel — does not fit the cream/brown system at
  all; likely vestigial. NOT swapped.
- `#f7f1e2` 4x: L107, L108 (dual-range thumb), L217 (cal badge text),
  L241 (hot-button text). The "cream foreground on dark" color. Clearly
  named role (foreground-on-dark) but no existing token; could earn
  `--cream-fg` in a future pass.
- `#b9aa88` 3x including L21 definition: L71, L163. Maps to existing
  `--control-border`. SWAPPED in Part B.
- `#fff8e8` 3x: L58, L71, L163. Recurrent "warm button surface" — one
  shade off from `--control-bg` (#fffdf5). Role is clear, no existing
  token; future pass could earn `--control-bg-warm`. NOT swapped.
- `#f1e6cf` 3x: L134, L136, L138. The three feature-row action hovers
  noted above. Role: "feature-row action hover bg". Single use site
  trio; would be cleaner with the shared `.feature-action` class than a
  token. NOT swapped.
- `#c8a463` 3x: L155, L156 (`feature-row-flash` keyframe), L162
  (`.feature-list-move-banner` border). Move-mode amber accent. Clear
  role; no token yet. NOT swapped (only 2 distinct call sites — keyframe
  is one logical surface).

Single-use literals (paint accents): `#384833`, `#e3ebdc`, `#9a5a32`,
`#444`, `#d8d8d8`, `#ececec`, `#f6edda`, `#c8b88d`, `#fffcef`, `#8b5f38`,
`#f3e6c4`, `#b08a4a`, `#ccc`, `#e8dcc3`, `#888`, `#999`, `#b9c7ad`,
`#dde2cf`, `#ecd9b1`, `#ff9500`, `#ffd400`, `#fffdf5` (1 raw use),
`#5f7157` (1 raw use), `#f7e3b5` 2x, `#f7d36b` 2x, `#ff3366` 2x, `#000`
3x, `#5c5548` 2x, `#c8b8a0` 2x, `#f6f6f6` 2x. Per the ≥3 + clear-role
rule none of these earn new tokens this pass; some (`#ff3366`,
`#ff9500`, `#ffd400`, `#000`) are align-handle paint colors that should
stay local to that mode.

### Audit recommendation

- Token swaps in Part B touch only hex literals that map to already-named
  tokens. No new tokens introduced.
- `!important` cluster, `.search-results` JS coupling, and the
  `.feature-action` shared-class refactor are all flagged for Pass 4
  main, not this sub-bite.

-----

## Shipped 2026-05-25

Four parallel sub-bites landed against the Pass 4 scope. See the Audit and
Theme Review sections above for the full detail; this block names the code
deltas and the open follow-ups.

### CSS

- **`!important` cluster reduced to zero in the right-panel cluster.** The
  `.section-toggle / .layer-expand / .panel-collapse / .group-chevron` block
  and the `.tune-control` row layout are now scoped under `.panel` (raising
  class+class specificity from `(0,1,0)` to `(0,2,0)`), which beats the
  generic `.panel button` and `.panel label` rules without needing the
  `!important` flag. Computed-style parity confirmed before/after. Files:
  `website/index.html` around lines 58-66 and 91-101.
- **Safe token swaps.** Eight literal hex occurrences for `--cream-border`,
  `--control-border`, `--control-bg`, and `--moss` were swapped to the
  existing token names. No new tokens introduced.

### Hot-button copy (critique C1)

- **Trails lane copy renamed off "heat" wording.** `Trail heat / Activity
  evidence` → `Trail activity / Where rigs spent time`. Updated in the HTML
  defaults, the `refreshHotButton` fallbacks (no-event + coming-up
  branches), and the `aria-label`s. Verifier
  `mvp/scripts/playwright_verify_event_schedule.py` assertion updated to
  match. Critique-followups card C-item ticked. Two-lane card's Copy
  section synced to the new strings.

### Calendar card chrome

- **`.calendar-card` regained its cream-surface chrome.** Added to the
  shared `.search-shell / .preset-bar / .left-context-card / .hot-control`
  group at `website/index.html:31`; the explicit `background: transparent`
  override at `website/index.html:191` removed. The moss-tint left-tabs
  strip still sits on top of the cream surface.

### Open follow-ups (named, not in this card's scope)

- **`--brown-soft` AA contrast tweak.** Theme review found three contexts
  (`--cream-hover`, calendar `happening`, calendar `upcoming_next`) where
  `#756444` sits at 4.13–4.47:1 on small text — marginally under AA 4.5:1
  for the timestamp/location strings on the live and next calendar rows.
  Suggested one-token bump to `#6a5638`. Holding for a follow-up bite — a
  palette token change is the kind of edit that wants its own verifier
  sweep, not a rider on this commit.
- **Focus-visible outline alpha.** Pass 4 Theme Review flagged the
  `rgba(95,113,87,0.42)` outline as too low contrast for sun-glance focus
  state. Holding for the same follow-up.
- **`.layer-row.active` vs `.expanded` distinction.** Two cream tints at
  ~1.10:1 bg-vs-bg. Suggested fix is an inset rust stripe (mirroring the
  calendar "happening" treatment). Holding.
- **Four remaining ≥3-count hex literals.** `#d8d0bd`, `#bbb`, `#f7f1e2`,
  `#fff8e8`. Each wants a new role name — `--cream-border-soft`,
  `--cream-fg`, `--control-bg-warm`, or similar — before tokenization.
  Held out of this pass to keep the audit scope honest.
