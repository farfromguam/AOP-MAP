# Viewer Source Split — plan (no build step)

Status: **CLOSED 2026-06-01 — Stage 1 SHIPPED + verified + COMMITTED**
(`d795f11` "split apart index.html"; `VERSION`/#appVersion **v26**; tree clean).
**User chose to STOP at Stage 1**, so Stage 2 (JS subdivision) is **not owed
work** — the ES-module (c) and classic-multi-file (b) carve options are retained
below as *future options only*; open a fresh card if JS sub-navigation is ever
wanted. Authored 2026-06-01; the line numbers throughout are now doubly stale
(index.html is **672 lines** AND the script moved to `website/js/main.js`).

-----

## What shipped — Stage 1 (CSS + JS extraction), 2026-06-01

The monolith is split into HTML + CSS + JS, served as-is, **no build step / no
package manager**. Verified at full parity (see Discoveries for the one change
to the chosen approach).

- **`website/css/app.css`** (867 lines) — both former `<style>` blocks (main +
  `#pwa-ui-lock`) moved **verbatim**, linked from `<head>` after the vendor CSS.
- **`website/js/main.js`** (9,770 lines) — the entire main script moved
  **verbatim**, loaded as a **classic** `<script src="./js/main.js">` (NOT a
  module — see Discoveries). `node --check` clean.
- **`website/index.html`: 11,299 → 673 lines** (markup + `<head>` + the 3 tail
  IIFEs only). The collision-magnet is gone: CSS / JS / markup now live in
  separate files.
- **`sw.js`**: `VERSION` v25 → v26; `./css/app.css` + `./js/main.js` added to
  `SHELL_ASSETS` (precache) and routed through **stale-while-revalidate** against
  the shell cache (same self-heal guarantee as the HTML shell — they fall through
  to network-only otherwise). `#appVersion` → v26.
- **Verifier touch:** `playwright_verify_code_review_groupb.py` version-pin
  `aop-data-v25` → `v26` (a version-bump-tied edit, not a behavior change).

**Verification (verify_by_observation):** full 27-suite run, **18 PASS / 9 FAIL,
zero new failures**. Every FAIL was proven pre-existing by serving the original
git-HEAD `index.html` on a second port (8011) and reproducing each identically:
satellite (stale title), feature_list (publishable export), event_schedule
(trail-lane fallback), presets (canvas-intercept + 3 assertions), pwa_qa2 (stale
`v18` assertion → now reads v26), brand_logos (empty feature-list open),
code_review_fixes (headless GPU `fragment shader` + calendar click timeout),
geolocate (canvas-intercept click timeout), sfwda_trace (marker layers removed at
v21). `code_review_groupb` PASSED at v26 — confirms the SW installs + activates
with the new shell files precached. 0 console errors across all passing suites.

## Discoveries (why the plan changed)

1. **ES modules (Option C) break the verifier harness.** ~20 verifiers reach app
   internals as **bare globals** — e.g. `page.evaluate("window.map = map")` reads
   the global `map`, and the harness also touches `tagToFeature`,
   `eventLocationByTag`, `__tdCount`, `setFeatureTag`, `refreshHotButton`, etc.
   A module hides all top-level bindings in module scope → `page.evaluate` can't
   see them → the hooks throw and every map-touching verifier fails (observed:
   `visibility=None`, tracebacks, **with the app itself error-free** — the failure
   is in the test hook, not the code). So the verbatim extraction had to be a
   **classic** external script, and full module conversion would mean rewriting
   the safety net at the same time as the code.
2. **`main.js` interleaves top-level execution with declarations and relies on
   whole-file function hoisting** (a top-level call at ~line 2818 resolves a
   `function` declared at ~line 8000). Separate classic `<script>` files do NOT
   share hoisting, so a naive cut-at-the-seams split throws `X is not defined` at
   load. A safe classic carve needs the bootstrap restructured (all declarations
   before all execution, or explicit load ordering) — a real refactor, not a cut.

## Stage 2 — the open fork (was: "carve into ES modules")

**DECISION (2026-06-01): user chose (a) — stop at Stage 1.** The monolith split
solved the stated problem; `main.js` stays one isolated file. (b) and (c) are
kept below as future options if JS sub-navigation is ever wanted.

Pick one:
- **(a) Stop at Stage 1.** The stated problem ("file too big / split it up") is
  solved — index.html is 673 lines, concerns separated, no build step. `main.js`
  stays one (large but isolated) file. Lowest risk. **Recommended unless the JS
  itself needs sub-navigation.**
- **(b) Classic multi-file carve (Option A).** Split `main.js` into ordered
  classic `<script src>` files (js/constants, js/map, js/poi, js/editor,
  js/calendar, js/hot, js/draw, js/search …). Preserves bare globals → harness
  stays usable. Cost: restructure the bootstrap so no cross-file top-level
  forward-reference; go seam-by-seam with a full verifier run after each. No
  build step, no module scope.
- **(c) ES modules (Option C) + harness migration.** True encapsulation, but
  requires exposing a deliberate `window` test-surface AND rewriting the
  `page.evaluate("window.map = map")`-style hooks across ~20 verifiers — i.e.
  changing the safety net and the code together. Highest risk/effort.

Original planning notes (pre-Stage-1) follow below for reference.

-----

Goal: break the one ~11.3k-line `website/index.html` into a navigable,
multi-editable set of files **without adding a build step or package manager** —
native ES modules + an external stylesheet, served as-is by `python3 -m
http.server` and precached by the hand-maintained `sw.js`.

Priority: P4-class (refactor/polish, per `_readme.md` "Sprint 04 priority"),
pulled forward by explicit user request. It is **not** a feature; it changes no
behavior. The bar is byte-for-byte behavior parity.

#aop #04_event_app #refactor #code-health #no-build

-----

## Restate (plain language)

`website/index.html` has grown to 11,299 lines / 562 KB. It is hard to navigate,
hard to diff, and hard for parallel agents to edit without colliding (the
2026-05-31 PWA-QA work needed a **7-agent worktree swarm each owning a disjoint
region of the file** — that collision pain is the real motivation). We want to
split it for maintainability. We do **not** want a bundler, npm, or any
compile-between-edit-and-reload step — that fights the "edit the file → reload →
the SW caches what's on disk" loop and `editor_is_the_viewer`.

## Northstar / rules check

- `ai_rules/editor_is_the_viewer` — `index.html` **is** the product surface.
  Splitting into co-served static files (same dir, same `http.server`, same SW)
  preserves that; a `src/`→`dist/` build would break it. The split must keep the
  served artifact directly editable. ✅ compatible.
- `ai_rules/no_limiting_code_mvp` — adding a build gate is exactly the kind of
  scaffolding that limits the MVP loop. Native modules add **no** gate. ✅ the
  no-build decision is the rule-aligned one.
- `northstar/source_register` — irrelevant (no data provenance touched). This is
  pure presentation-code restructuring.
- `spinup/working_pwa_css.md` — the **locked** iOS-PWA layout snapshot. The CSS
  extraction (Slice A) moves the `<style>` rules verbatim to an external file; it
  must not alter a single PWA rule. Diff the extracted CSS against this snapshot
  before/after. The `#pwa-ui-lock` block is part of that locked set.

## Findings (measured 2026-06-01, read-only)

**Why file size is *not* the driver:**
- `index.html` = 11,299 lines, **562 KB raw → 142 KB gzipped** over the wire.
- Vendor libs are **already external**: `maplibre-gl.js` 1.03 MB,
  `terra-draw.umd.js` 222 KB, the adapter 8.6 KB, `maplibre-gl.css` 70 KB. So the
  *library* payload dwarfs our app code; maplibre alone is ~300 KB gzipped. Our
  ~9.76k-line script is the small part of what the browser downloads, it parses
  in a few ms, and the SW caches it after first load. **Splitting buys nothing
  for the browser.** The win is 100% developer/agent ergonomics.

**Internal structure of `index.html`:**
| Region | Approx lines | Content |
|---|---|---|
| `<head>` detect script | 14–37 | editor-off / ios-browser class set. Standalone. |
| `<style>` | 39–883 (~845) | All app CSS, one block. |
| body markup | 883–1360 | HTML. **Zero inline `on*=` handlers.** |
| vendor `<script src>` | 1360–1362 | maplibre + terra-draw (already external). |
| **main app script** | **1363–11126 (~9,763)** | **The monster.** |
| tail scripts | 11133–11277 | 3 independent IIFEs: PWA install, SW register, copy-data bootstrap. |
| `<style id="pwa-ui-lock">` | 11278–11297 | PWA gesture hardening. |

**The main script — why the split is *de-risked*:**
- It runs in **bare global scope** — no IIFE, no `DOMContentLoaded` wrapper. It
  works only because the `<script>` sits *after* the markup it queries. ~246
  top-level `function`s + ~203 top-level `const`/`let`, all currently co-visible
  as globals.
- **Zero inline `on*=` handlers in the markup** — the single biggest ES-module
  hazard (module scope orphaning `onclick="fn()"` references) **does not exist
  here**. All event wiring is `addEventListener` inside the script.
- **Cross-boundary surface is tiny and already explicit:** only `lrOpenCard`,
  `lrCloseCard`, `lrResetCards`, `lrReflow` are deliberately hung on `window`
  (defined late ~11093–11122, called from handlers earlier), and `window.AOP_UI`
  is set by the copy-bootstrap tail script and read lazily by the main script.
- **The genuine coupling is *intra*-script:** functions call functions, and
  nearly everything reaches the central mutable state — `const map` (~1478),
  `let publishDataCache` (~1806, set ~10065), `fetchJson` (~8149), and the
  override stores (visitor-context ~3878, positioned-features ~3887, brand-logos
  ~3982), `#tag` binding (~4310), move-mode (~4483), feature-list panel (~3571).
  That shared state is what any module boundary has to thread.

**Natural seams (existing `// ---` banner comments — these are the cut lines):**
right-panel collapse (~1691) · trail-catalog sidecar (~1836) · unified editor
tree V3c (~1871) · POI-browser groups (~2478–2784) · feature-list panel (~3571)
· override stores (~3878–4013) · brand-logo zoom-cap (~4013) · tag binding
(~4310) · move-mode (~4483) · map→panel reveal (~4693) · export/import
(~6479) · event schedule (~6843) · session-now (~7067) · hot control (~7452) ·
drawn-POI editor + Terra Draw (~7964, ~10286) · the big layer-add bank
(~8372–10286: landcover, contours, hotspots, synthetic, NHD water, roads,
cemeteries, FEMA, OSM, SFWDA, trail network, raster aligner, publishable, brand)
· search (~10462–11126).

**Safety net:** **27** `mvp/scripts/playwright_verify_*.py` suites drive
`http://localhost:8001/` and assert behavior + `0 console errors`. A
behavior-preserving refactor must leave **every** one green **with no assertion
edits** — and the console-error checks will catch any module 404 / failed import
/ `X is not defined` from a missed global. This is the objective parity bar.

**Tooling baseline:** confirmed **zero** — no `package.json`, lockfile,
`tsconfig`, or build config anywhere outside `brain/`. `sw.js` is 247 lines,
hand-maintained precache list + `VERSION` discipline (currently v25).

## Decision (AAF)

**Settled by the user (prior turn):** no build step, no package manager — native
ES modules + external CSS, served and SW-cached as-is. This card does **not**
re-litigate that.

**Still open — *how* to cut the JS.** Three viable shapes; this is the one real
fork (effort vs. cleanliness). Suggested answer first, then the menu:

> **Suggested: Option C (shared-namespace object + ES modules), reached via a
> phased slice order that front-loads the zero-risk wins.** It gets module-scope
> encapsulation and real file separation while collapsing the import-threading
> churn (modules import one `app` object that owns `map` + caches + stores,
> instead of threading a dozen symbols through every file).

- **Option A — classic multi-file (`<script src>` × N, shared global scope).**
  Cut at the seams; **no** `import`/`export`. Lowest labor — globals stay global,
  so almost nothing rewires (only constraint: preserve source order, and ensure
  no file *reads* a later-defined symbol at top-level eval time; today's reads are
  almost all inside deferred handlers, so this is largely safe). Cons: namespace
  stays polluted, load order is manual and fragile, no encapsulation, a stray
  duplicate `const` across files throws. "Same code, more files." Good **stepping
  stone**, weak destination.
- **Option B — pure ES modules (`type="module"`, explicit import/export).**
  Cleanest dependency graph. Cons: must convert the implicit global coupling into
  explicit imports — threading `map`, `publishDataCache`, the stores, and the four
  `lr*` helpers through real import lines across ~246 functions. Volume risk, not
  conceptual. `type="module"` is deferred-by-default (runs after parse) — fine
  here, but a semantics change to keep in mind.
- **Option C — namespace object + ES modules (recommended).** A small
  `js/app.js` (or `state.js`) exports one `app` object holding `map`,
  `publishDataCache`, the stores, and the shared utils; feature modules
  `import { app }` and hang/read off it. Keeps module scope + file separation,
  but each module imports ~one thing, not twelve. Pragmatic middle for a big
  global-coupled blob. The existing `window.AOP_UI` and `lr*` exports fold into
  this object (or stay on `window` for the tail scripts' sake — decide in
  Open Questions).

## Scope

- Extract the `<style>` block(s) → external stylesheet(s), linked from `<head>`.
- Split the ~9.76k-line main script into feature files along the named seams.
- Establish one shared-state mechanism (Option C `app` object, unless the fork is
  answered otherwise) and convert intra-script global coupling to it.
- Keep the 3 tail IIFEs (PWA install, SW register, copy bootstrap) as-is or move
  them to their own small files — behavior unchanged either way.
- Update `sw.js` precache to list every new file; bump `VERSION`.
- Keep all 27 verifiers green with **no** assertion changes.

## Out of scope

- **Any bundler, npm, lockfile, transpile, or minify step.** Explicitly excluded.
- **Behavior, copy, layout, or layer changes.** This is a pure move/restructure.
  If a behavior change looks necessary, stop — it means the cut was wrong.
- **CSS rule edits.** Extraction is verbatim relocation, not a cleanup pass (raw-hex
  / token sweeps live in `10_deferred/viewer_polish_followups.md`).
- **The vendor files.** Already external; untouched.
- **Re-architecting the data/store model.** We thread the *existing* shared state
  into modules; we do not redesign it.

## Execution order (thin vertical slices — do NOT big-bang)

**Gate 0 — file must be quiescent.** Do not start until the other agent's
`index.html` work has landed **and the working tree is committed**. A
whole-file restructure conflicts with essentially every concurrent edit; racing
it guarantees a merge disaster. Confirm `git status` clean on `index.html` first.

1. **Slice A — CSS extraction (zero JS risk, do first).** Move the `<style>`
   (~39–883) and `<style id="pwa-ui-lock">` (~11278–11297) verbatim into
   `website/css/app.css` (+ keep the PWA-lock comment header). Link via
   `<link rel="stylesheet">` in `<head>`, after the vendor `maplibre-gl.css`.
   Diff extracted CSS against `spinup/working_pwa_css.md` for the PWA rules. Add
   `css/app.css` to `sw.js` precache; bump `VERSION`. **Drops ~860 lines and
   proves the external-asset + SW + VERSION loop with no script risk.** Ship and
   verify before touching any JS.
2. **Slice B — leaf utilities (lowest JS risk).** Extract the pure, `map`-free
   helpers and constants (e.g. `escapeHtml`, palette/bounds/localStorage-key
   constants, `fetchJson`) into `js/util.js` + `js/constants.js`. This is where
   the Option-C `app` object is introduced (or, under A, the first split file).
   Establish the `type="module"` entry (`js/main.js`) and confirm load order +
   `0 console errors` before going wider.
3. **Slices C…N — one feature seam at a time**, each its own ship+verify cycle,
   roughly: core/map-init → layer-add bank → POI browser → editor (tree + stores
   + feature-list + move-mode + export/import) → calendar/event-schedule/session
   → hot control → drawn-POI/Terra-Draw → search. Editor is the largest seam;
   consider sub-slicing it. After each slice: full verifier suite + console
   clean + `VERSION` bump + `sw.js` precache update.
4. **Slice Z — tail scripts.** Optionally relocate the 3 IIFEs to
   `js/pwa-install.js`, `js/sw-register.js`, `js/copy-bootstrap.js`. Behavior
   identical; resolve where `window.AOP_UI` / `lr*` exports live.

Each slice is independently shippable and independently revertible — the whole
point of not big-banging an 11k-line file under a live PWA.

## sw.js / VERSION impact

- Every new file (`css/app.css`, each `js/*.js`) **must** be added to the
  precache list, or it won't be available offline-after-once.
- `type="module"` imports are fetched by URL — the SW must cache each module file
  individually (no bundle to hide them behind). Relative paths keep the existing
  directory-scoped registration working; no import map needed.
- Bump `VERSION` (and the `#appVersion` mirror) on **each** slice so installed
  PWAs re-fetch the shell. The SWR/navigate self-heal path (from
  `_done/app_code_review_fixes_batch1.md`) heals the HTML shell; the new
  sub-resources ride the precache.

## Verifier impact

- A correct refactor changes **no** verifier assertions. Run the full suite
  before each slice (baseline) and after (parity). Any required assertion edit is
  a red flag that behavior moved — investigate, don't paper over.
- The `0 console errors` checks are the front-line catch for module/load
  breakage (404, failed `import`, orphaned global).
- Known pre-existing fails (do not attribute to this work): the headless
  `Locator.click` canvas-interception class in `session_tools`, `poi_editor`,
  `presets` (full-bleed `#map` intercepts the click — see 2026-06-01 handoff),
  and the publishable-export path in `feature_list`. Baseline them first so the
  diff is honest.

## Acceptance criteria

- No `package.json`, lockfile, or build config introduced; app still served by
  `python3 -m http.server` with no pre-step.
- `index.html` shrinks to markup + `<head>` links + `<script type="module">`
  entry (+ small tail scripts); CSS and JS live in `css/` and `js/`.
- All 27 `playwright_verify_*.py` green with **0 console errors** and **no
  assertion changes** (modulo the pre-existing fails baselined above).
- Extracted CSS is byte-equivalent in effect; PWA rules match
  `spinup/working_pwa_css.md`.
- `sw.js` precaches every new file; `VERSION` + `#appVersion` bumped; SW reaches
  `activated` on reload.
- Done in independently-shipped slices, each committed, never one big-bang diff.

## Verification steps

1. `git status` clean on `index.html` (gate 0) before starting.
2. Per slice: `cd website && python3 -m http.server 8001`, run the relevant
   verifier(s) + a broad smoke (`presets`, `feature_list`, `search`), confirm
   `0 console errors`.
3. After the JS split lands: full 27-suite run, compare against the baselined
   pre-existing-fail list — no *new* fails.
4. Confirm SW: reload twice, check `VERSION`/`#appVersion`, SW `state ===
   'activated'`, and that each new `js/`/`css/` file appears in the active cache.
5. Diff `css/app.css` PWA rules against `spinup/working_pwa_css.md`.
6. On-device PWA sanity (owed, can batch with the standing on-device pass): cold
   launch + reload still full-bleed, no console errors in the installed app.

## Open questions (what closes each)

1. **JS cut shape — A vs B vs C?** Recommend C. *Closes when:* user picks, or
   defers to my judgment (then C). Note A is also viable purely as a stepping
   stone *toward* C if mid-flight import-threading proves too churny.
2. **Where do `window.AOP_UI` + `lr*` live post-split?** The tail IIFEs run in
   their own scope and currently reach the main script only through `window`. If
   the main script becomes a module, those four `lr*` helpers + `AOP_UI` must
   stay reachable — keep them on `window` (simplest, preserves the tail scripts
   untouched) or convert the tail scripts to modules too. *Closes when:* Slice Z
   is scoped — lean keep-on-`window`.
3. **Sub-slice the editor seam?** It's the largest (tree + stores + feature-list
   + move-mode + export/import, ~1871–6843). *Closes when:* Slice B is done and
   the real per-seam size is re-measured against the (now-quiescent) file.
4. **One `js/app.css` or split CSS too?** One file is the cheap win; CSS rarely
   has the navigation pain JS does. *Closes when:* user weighs in — default: one
   `app.css` (+ keep the PWA-lock block clearly sectioned within it).
