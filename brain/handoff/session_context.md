# Session Handoff: Sprint 04 pickup

Date: 20260527

Short pointer for the next session. The durable record lives in the cards.

**2026-06-01 (verifier-rot fix — test-only, no app code).** Picked up the ungated
P4 item from `10_deferred/viewer_polish_followups.md` after confirming all Sprint 04
P1 headless work is shipped+committed (incl. trail Slice 3 — the trail card's
"uncommitted/VERSION-owed" header is **stale**; Slice 3 is in `master` at v25,
`8be6e99`). The v25 full-bleed `position:fixed` `#map` canvas now occludes right-panel
buttons' hit-test points, so real `Locator.click`s timed out. **Fixed:** shared
`click_in_section` (`mvp/scripts/playwright_base.py`) now JS-dispatches the element's own
`click()` after expanding its section (the `set_toggle` pattern); `poi_editor` panel
clicks routed through it + stale `<title>` → "Trail Blazing Invitational"; `session_tools`
clock/reset routed through it. **Verified:** `session_tools` ALL PASS, `poi_editor`
RESULT: PASS, both 0 console errors; helper's other callers regression-clean
(`community_trails` 16/16, `landcover` PASS). `presets` (same class, separately tracked)
partly revived — its first toggle-click crash fixed (now runs 51 checks) but it still has
a downstream panel-click crash + 3 assertion FAILs (2 are the documented decision-gated
publishable/source-section ones, 1 "Topo restyles index contours" never previously
reached) → flagged as its own follow-up in that card. All changes are in
`mvp/scripts/` (test harness only — no `website/` change). UNCOMMITTED.

**2026-06-01 (planning only — no code) — viewer source split card opened.** User
asked whether the project needs a build step / package manager given the growing
file, and to plan splitting it. Verdict (recorded in the new card): **no build
step, no package manager** — file size is not the problem (`index.html` is 562 KB
raw / **142 KB gzipped**; the vendor libs — maplibre 1 MB — dwarf our ~9.76k-line
script). The real pain is maintainability + parallel-edit collisions. Plan = split
into external CSS + **native ES modules**, served/SW-cached as-is. New card
`tasks/04_event_app/viewer_source_split.md` (phased slices: CSS first, then leaf
utils, then one seam at a time; 27 Playwright verifiers as the parity net; gated
on `index.html` going quiescent; open fork = cut shape A/B/C, recommend C). **No
code touched** — a second agent was live in `index.html` at planning time.
Registered in `04_event_app/_readme.md` "Still active".

**2026-06-01 (worktree cleanup + Group B fully shipped incl. M13 + Groups C–D worked).** (1) **Worktree
chore resolved.** The "three locked agent worktrees" chore was **stale** — already
gone. Real remaining clutter = `aop-copy-review` worktree + `copy-review` branch
(`git cherry` → fully in master) + `integration-pwa-qa` safety-net (all swarm items
in master; its only non-master content was the **intentionally-dropped** tree-
landcover pattern, user-confirmed, recoverable at `5d825f4`). Verified-redundant;
deletion commands handed to the user via `!` (git is the user's surface). **NOTE:**
the older `session_context` blocks below claiming "master has item 20 (tree pattern)"
are now wrong — it was removed at `2fd9cc4 "icons. omg…"` on purpose. (2) **Group B
fully shipped.** Versions: **v24** committed (`c4e080c "v24 batch"`) = H1+M12; **v25**
working-tree UNCOMMITTED = M4+M5+M8+M9+M10+M13. Changes: **H1** slider rAF-coalesce
(`scheduleRebakeTiles`, index.html), **M12** install button keeps affordance on
dismiss (index.html), **M4** `fetchJson` memoized + warm-up loop (parallel overlay
fetch; SUM→MAX, index.html), **M5** per-row visibility updates counts in place
(`refreshFeatureListCounts`, no subtree rebuild, index.html), **M8** `resyncViewport`
rAF-coalesced + size-guarded (index.html), **M9** move anchor → `geometryBboxCenter`
(fixes multi-part no-op, index.html), **M10** commit-click armed next frame
(index.html), **M13** dropped contours (~14 MB) + synthetic-tracks (~1 MB) from the
`sw.js` install precache (both default-off; cache-first `/data/` still lazy-caches
them → offline-after-once). Verified by observation:
`mvp/scripts/playwright_verify_code_review_groupb.py` **15/15 PASS 0 errors** (H1
burst→1 bake; M12 dismiss/accept; M5 count `1/1→0/1` DOM nodes reused; M4 geojson
loaded; M13 served SW excludes the 2 layers, keeps essentials, SW activates at v25 /
`aop-data-v25`); `feature_list` move-commit + visibility PASS (only pre-existing
publishable-export FAIL); `sfwda_multiply` 5/5. On-device confirm owed (H1 slider,
M12 prompt, M8 iOS keyboard, M9/M10 drag, M13 install cost + offline-after-once).
**Group B complete.** (3) **Groups C–D worked** (still v25, index.html): **L10**
`setLeftTab` returns the resolved key (persist callers wrapped) + `togglePanel`
`settle` listener now has a 360 ms safety net; **L12** `map.on('error')` moved to
construction (catches initial-load errors); **L3** `tileLayerId` delegates to
`tileSourceId`; **L11** `bindEditorClick` idempotence guard; **L9** removed dead
`.left-context-card` rules (KEPT `#message` — verifier-critical load proxy, not
dead). **M19 stale** (no change — `#calendarToggle` not interactive; `#panelHeader`
accessible via its `#panelCollapse` button). **Deferred to own pass:** L1 whitespace
(88 tab lines), broad L2 extractions, L9 raw-hex sweep + pwaIosHint focus-trap; L13
note-only. Verified: `groupb` 15/15, `feature_list` (0 errors, only pre-existing
publishable FAIL), `sfwda_multiply` 5/5. **Verifier rot (pre-existing, NOT this
batch):** `session_tools` (`#clockUseInputs`) + `poi_editor` (`editor-bucket-add`,
stale `<title>`) crash in headless on a `Locator.click` the full-bleed `#map` canvas
intercepts — same class as `presets`; worth a separate force-click/reposition pass.
The card's substantive fixes are all landed; remaining = the own-pass deferrals + the
on-device confirm. **Card CLOSED → moved to `tasks/04_event_app/_done/app_code_review_followups.md`**
(deferred refactor residue routed to `tasks/10_deferred/viewer_polish_followups.md`).
See the closed card's ▶ Next up for the full per-item record.

**2026-05-31 (Sprint 04 triage pass — doc only, no code).** Re-sorted the open
Sprint 04 cards. **Moved → `04_event_app/_done/`:** `copy_review_surface.md`,
`icon_system_normalize.md`, `pwa_qa.md` (all shipped + verified; pwa_qa's only
remainder is the perpetual on-device feel-confirm, kept in its Disposition).
**Still active:** `app_code_review_followups.md`, `trail_research_integration.md`,
`pwa_qa_2.md` (near-done, user-gated on items 6 + 9), `pwa_qa_2_plan.md`
(companion), `pwa_qa_data_bakes.md` (blocked on product/boundary/source calls).
The **priority ranking** lives in `04_event_app/_readme.md` "Sprint 04 priority
(2026-05-31)": P1 = trail Slice 3 + app-review Group B (actionable now); P2 =
the data-bake decision bundle; P3 = on-device verify pass; P4 = refactor/polish.
Doc moves only, uncommitted.

**2026-05-31 (app code review + fix batch 1).** App code review (4 High / 20
Medium / 13 Low across `website/index.html` + `sw.js` + `manifest.json`; one
sweep finding — `composeFeatureFilter` id-type — retracted as a false positive
after hand-check). **Split into two cards:** DONE record at
`tasks/04_event_app/_done/app_code_review_fixes_batch1.md` and the held items at
`tasks/04_event_app/app_code_review_followups.md` (now 20 findings, grouped, with
a recommended order; next cheap slice = forks M7/M14/M17, then the on-device
batch). **Queued decision H4+L8 (SW cache-staleness) ANSWERED + shipped:** user
chose stale-while-revalidate — shell HTML self-heals (navigate caches the
response; non-nav `.html` SWR), copy JSON joins the SWR path (`SWR_SUFFIXES`),
release-checklist comment added, **`VERSION`/#appVersion v20 → v21**. SW verified
active (state=activated). **Then the no-device forks M7/M14/M17 shipped too:** M7
(ticker confirmed singleton + documented page-lifetime), M14 (4 unreferenced
files dropped from `sw.js` precache, ride v21), M17 (`EDITOR_POI_CATEGORIES`
derived from `#poiCategory` options — drift gone, verified 11/11). **20 of 37
findings now resolved, 17 held (all on-device or refactor — no decision-gated
work left).** All in the working tree (UNCOMMITTED). Verified by observation
(smoke PASS, 0 console errors): M1 (popup `closeAllMapPopups`), M2 (central popup-title escape +
stripped 12 redundant caller escapes), M3 (`fetchJson` warns on non-OK), M6
(MultiPolygon hotspot centroid), M11 (stable POI row id), M15 (About href gate),
M16 (`mergeStoreSlice` shallow-merge), M18 (positioned-feature flag clear), M20
(`?.` listener guards), H2 (free bake canvases), H3 (tainted-canvas guard), L4
(`withZoomStops` shape guard), L5 (hemisphere label), L6 (`sw.js` `status===200`),
L7 (manifest `id`). New durable verifier
`mvp/scripts/playwright_verify_code_review_fixes.py` → **PASS, 0 console errors**
(popup no-stack + no-double-escape + presets + renderAbout all confirmed). The
report's "Resolution status" block lists what was **held** (on-device/interaction
verify, cache-strategy decisions, polish-routed) with reasons. `sw.js` (L6) needs
a `VERSION` bump to reach installed users — user's call.


**2026-05-31 (copy review surface) — copy-as-data + printable review page.**
On branch **`copy-review`** (git worktree at `../aop-copy-review`), UNCOMMITTED.
New card `tasks/04_event_app/copy_review_surface.md`. Built `website/copy_review.html`
(prints every text surface in the app, each section headed with its repo-relative
root file + status + ⚑ gap flags), driven by a master registry
`website/data/aop_copy_registry.json` (13 copy kinds). Extracted the prose that
was hardcoded in `index.html` into data files: About tab → `aop_about.json`,
interface microcopy → `aop_ui_strings.json`; calendar title now reads
`event.label` from `aop_event_schedule.json`. Viewer renders from those files via
a copy-data bootstrap script (after SW-register) + `window.AOP_UI` with literal
fallbacks. `#appVersion`/`sw.js VERSION` v18→**v19**; 3 new files added to the SW
data precache. Verified: Playwright on `:8001` (worktree) — About renders from
JSON, 0 console errors over 5 loads; review page assembles all 13 kinds, 0 errors.
Screenshots + logs in `brain/output/copy_review_*`. The 4 `in_code` kinds (page
metadata, layer labels, popup strings, attribution) are cataloged in place with
file links — extraction deferred (interleaved with map render/preset logic).
Merge `copy-review` → master when ready.
Also on this branch: **trail research integration Slices 1–2 shipped** — the trail
catalog (`aop_trail_catalog.json`) is now joined to the gold trail network at
runtime (trail click popup with name/difficulty/description/onX-TR/license, and the
POI browser trails group repointed from the legacy publish placeholder to the gold
network + catalog). Card `tasks/04_event_app/trail_research_integration.md` (in the
main checkout, untracked) marked Slices 1–2 shipped; verified
(`brain/output/trail_verify.log`).

## Archive convention

Each session pruned out of here lands at `session_context_<YYYYMMDD>.md`:

- `session_context_202605201517.md` — original handoff shape (the template).
- `session_context_20260522.md` — work log from the 2026‑05‑20 → 2026‑05‑22 sessions (lidar contours, water, search, cemeteries, land cover, NAIP tracing, presets, panel collapse, activity hotspots, initial event schedule).
- `session_context_20260524.md` — work log for the 2026‑05‑23 → 2026‑05‑24 sessions, covering the full Sprint 02 close (Buckets A–H), schedule clock-times, calendar current-time indicator, left hot button, hot-control two-lane, branding logos, named-feature tagging, search tags, viewer chrome polish, default-layer policy, and code-health Pass 3.
- `session_context_202605241228.md` — CWC dump after Sprint 03 carryover lanes 1–5 shipped.
- `session_context_20260525.md` — left-rail manilla-tab design exploration; five HTML mockup variants checked in under `website/leftrail_v*.html`. Build card: `tasks/03_event_app/_done/left_rail_collapse_tabs.md`. No `website/index.html` changes.
- `session_context_20260527.md` — misc_4 items 1–5 shipped, plus the POI/About empty-space CSS fix and the tab-restore fix. All in the working tree (uncommitted). See `tasks/04_event_app/misc_4.md` "What shipped (2026-05-27)" block for the full close-out and the trail-lane verifier residue routed to `viewer_polish_followups.md`.

**2026-05-31 (pwa_qa_2) — items 1–5 shipped, 7 routed, 6 held.** Picked up
`tasks/04_event_app/pwa_qa_2.md` in a clean session (the companion
`pwa_qa_2_plan.md`'s calendar/region/item-6 code anchors were garbled by the
prior corrupted channel — re-derived everything against the real
`website/index.html`). Shipped in the working tree (UNCOMMITTED): **(1)**
calendar→event popup pins to a fixed `bottom` anchor + dropped the redundant 2nd
corrective pan (the "jerk"); **(2)** mobile calendar-pick now folds the cal card
too (`lrCloseCard('cal')`); **(3)** build version folded into the bottom-left
info ⓘ → "ⓘ v18" (`foldVersionIntoInfoControl`, standalone chip removed);
**(4+5)** Trace preset reworked to "paper map vs merged gold truth" — park bounds
+ OSM park polygon + OSM tracks OFF, SFWDA paper raster kept, merged
`aop-trail-network` ON (added a trace paint so Topo→Trace keeps difficulty
colour), legacy demo trails OFF. **Item 6** (logo overshoot on zoom-out) NOT
shipped — it's GeoJSON-symbol parent-tile scaling (device/GL only); the cap is
already a per-frame GPU expr with allow-overlap, so nothing safe to change
headlessly + the user's instruction is cut off. **Item 7** (Ellis cemetery bake)
routed → `pwa_qa_data_bakes.md` "Item E"; its paired "hide other cemeteries"
RETRACTED (item 9 hold). Plan items 8 (calendar-icon centering) + 10 (region
preset) are no-ops on false premises (see the Disposition table). New verifier
`mvp/scripts/playwright_verify_pwa_qa2.py` — all items PASS, 0 console errors
(served on **8002**; 8001 held a second agent's worktree review, left alone).
`playwright_verify_presets.py` Trace assertion updated to the new intent (it
crashes earlier on a pre-existing headless click-interception, below my edit).
**Version bumped v18→v19** (user call): `#appVersion` + `sw.js VERSION`. The
other agent is also on v19 in a worktree — reconcile at merge. Commit owed to
the user.

**2026-05-31 (icon system) — icon master sheet built.** All 13 inline UI icons in
`website/index.html` collected into a standalone tool **`website/icon_master.html`**:
as-built vs normalized compare grid, global stroke-width + optical-fit controls,
outlier flagging, inline markup editing, and paste-ready SVG export. Source audit:
all already SVG + uniform `22×22` canvas, but **3 stroke widths ship** (1.6 most,
1.4 Tree/Install, 1.2 Pencil) and art-fill ranges 68–91% (Locate is oversized at
91%). Flagged outliers: Tree, Install, Pencil (off-spec stroke), Locate (too big).
`index.html` left untouched — the page is the revision surface; recommended target
+ the 4 paste-back edits are in the new card **`tasks/04_event_app/icon_system_normalize.md`**.
Verified by Playwright (13 cards, 0 console errors). Uncommitted.

**2026-05-31 (PWA QA swarm) — most of `tasks/04_event_app/pwa_qa.md` resolved.**
7 worktree agents, each owning a disjoint region of `website/index.html`, merged
into the master working tree (UNCOMMITTED; backup branch `integration-pwa-qa`).
Shipped: items 5 (logo max-size cap + slider/export), 7 (pinch), 9 (trail dots
removed), 10 (1X search), 11+16 (calendar scroll/header/end-date), 12 (park
zoom tighter), 13 (topo/trail colors + `topo_color_compare.html`), 14 (hot
button toggle), 15 (drawer reflow), 18/19/21 (chrome icons). Item 8 was already
done (`.message` dropped). Split to **new card `pwa_qa_data_bakes.md`**: items 4,
6, 17 (data-bake/acquisition). Then both forks resolved: item 2 confirmed
superseded by V5; item 20 shipped a tree SVG (`website/img/tree.svg` tiled as a
`landcover-forest-trees` fill-pattern on satellite). On-device confirm owed for
7/13/15/20 (touch+GL, unverifiable headless). Full per-item table + merge-integrity
notes in the card's "Disposition" block. **Worktree cleanup DONE (2026-05-31):**
the 7 harness-locked agent worktrees were removed and their `worktree-agent-*`
branches force-deleted after verifying each slice is in master — proof was that
the consolidated `integration-pwa-qa` branch differs from master by only item 20
(the `landcover-forest-trees` tree pattern + `tree.svg`, which master has), and
no worktree carried uncommitted work. The empty `.claude/worktrees/` dir was
removed. Consolidated backup branch `integration-pwa-qa` **retained** (swarm
only; item 20 is working-tree/master-only) as the safety net — delete it once the
v18 swarm result is confirmed on device.

**2026-05-30 (session — iOS PWA full-bleed + V5 bottom bar) — RED BAR FIXED; bottom UI
reworked. We are CLOSE: all changes UNCOMMITTED in the working tree, build `v12-dbg`,
served straight to the phone (no commit/deploy step in this loop). Diagnostics still
live on purpose — closeout = strip them, then commit.** Files touched: `website/index.html`
+ `website/sw.js` (sw `VERSION` v7→v12, kept in sync with `#appVersion`).

- **The "red bar" root cause (the thing that ate days of v5/v6/v7 "pwa bottom math"):**
  `body,html { height:100% }` makes iOS Safari **silently drop `viewport-fit=cover`**, so an
  installed PWA's viewport returns `screenH − statusBar` (measured on-device: `innerH 762`
  on an `812` screen) and the lost ~50px lands as a DEAD BAND at the BOTTOM that a
  `position:fixed` map can't paint into → the `<body>` background showed through there.
  Confirmed by the on-screen `#dbgOverlay` readout, not theory.
- **Ruled out (don't re-litigate):** (1) the iOS **26.1** PWA status-bar regression
  (WebKit bug 301994, fixed in 26.2) — user is on **26.2+**, not affected. (2) The old
  **negative-inset hack** `#map{ top:calc(0 - --sa-top); bottom:calc(0 - --sa-bottom) }`
  is a **documented dead end** — a fixed element cannot paint into an off-viewport band.
- **FIX (verified on device — `innerH 812`, `#map`+`canvas` 812, no red):** `html,body`
  and `#map` use **`height:100dvh`** (browser tab — respects the collapsing address bar)
  with **`@media (display-mode: standalone){ html,body,#map{ height:100vh } }`** (installed
  PWA — `100vh` is full-screen AND correct on cold start; `100dvh` is NOT, per the
  full-screen-canvas guidance). `#map` = `position:fixed; top:0; left:0; width:100vw;
  height:100dvh`. `overflow:hidden` on body.
- **V5 bottom bar (now EVERY width — desktop == mobile):** collapsed edit panel renders as
  a round rust **pencil FAB, bottom-right** (`.panel.collapsed` in base styles + a
  `.panel-fab-pencil` span inside `.panel-header`, hidden unless collapsed). Map
  **attribution moved to bottom-LEFT** as a compact `ⓘ` (`attributionControl:false` in the
  `Map` ctor + `map.addControl(new maplibregl.AttributionControl({compact:true}),
  'bottom-left')`; the collapse-once helper now runs on all widths). Both icons share a flat
  **12px baseline**. The **"N publish features loaded" status (`.message`) is dropped** on
  all widths. Attribution is capped `max-width: calc(100vw - 24px - insets -
  var(--edit-fab-reserve))` so its expanded credit list can't overrun the FAB (~20px clear).
- **Edit gate — DEFERRED by user ("decide later / keep on"):** `--edit-fab-reserve` (76px,
  →`0` when off) + `html.editor-off{ .panel display:none; reserve 0 }` + a `<head>` script
  that sets `editor-off` from the `?edit` param. **Default editor-ON.** `?edit=0` previews
  the public/invisible layout (no FAB, attribution reclaims full width); `?edit=1` forces on.
  Production trigger (hostname / param / stored flag) **NOT chosen yet**. OPEN: `editor-off`
  currently hides the **whole** right panel (incl. presets / layer toggles), not just the
  editor sections — decide if a public viewer should keep those.
- **Mockups (review artifacts):** round 2 `website/bottombar_compare2.html` +
  `bottombar_v5_fab` / `v6_pill` / `v7_credits.html` (on top of round 1
  `bottombar_compare.html` + v1–v4). **V5 (FAB) chosen.** Retire per the `misc_4`
  mockup-cleanup routing once the look is locked.
- **STILL-LIVE DIAGNOSTICS to strip at closeout (kept ONLY for on-device verification):**
  red `html,body{ background:#ff0033 }` (revert to a map-toned neutral); the blue map
  background-layer paint `#1e66ff`; the green `#dbgOverlay` div + `updateDbgOverlay()` /
  resync JS; and the `-dbg` suffix on `#appVersion` + sw `VERSION`.
- **NEXT SESSION:** (1) confirm `v13-dbg` reads right on the phone (FAB bottom-right + ⓘ
  bottom-left aligned low, no overlap when ⓘ is expanded, no red band; `?edit=0` shows the
  clean public layout); (2) strip the diagnostics above + set neutral body bg + drop `-dbg`;
  (3) commit; (4) decide the gate trigger only if/when actually splitting public vs editor.
  No build card exists for this PWA work yet — if it grows, open one under the active sprint.

**2026-05-30 (session — bottom-icon baseline aligned, `v13-dbg`) — the ⓘ and the pencil
FAB now share a baseline ON THE DEVICE. Working tree, uncommitted, served straight to the
phone.** Files: `website/index.html` + `website/sw.js` (VERSION v12→v13).
- **The bug (measured from the device screenshot, NOT theorised):** `Screenshot
  2026-05-30 at 23.30.30.png` is 1125×2436 = iPhone @3x (375×812pt, so 1pt=3px). The ⓘ
  bottom sat **12pt** off the screen bottom (= its `margin-bottom:12px`); the pencil FAB
  bottom sat **62pt** off — a **50pt** gap — even though both CSS rules said `bottom:12px`.
- **Root cause (it was already in the dbg overlay):** the overlay reads `innerH 812 /
  clientH 762`. The ⓘ is a MapLibre control INSIDE `#map` (`position:fixed`) → anchors to
  the true 812px visual viewport. The pencil is `.panel` with **`position:absolute`** →
  iOS anchors it to the `<html>` content box, which it measures as **762px** (812 − the
  50px top safe area). `762−12 = 750` from top = **62px off the bottom**. `62−12 = 50` =
  exactly the top safe area. Different positioning contexts, same `bottom:12px`, 50px split.
- **WHY PLAYWRIGHT IS USELESS HERE (don't reach for it on PWA safe-area bugs again):**
  desktop Chromium has no safe area, so `env(safe-area-inset-*)`=0 and `innerH==clientH`.
  Absolute and fixed then resolve identically → Playwright reported BOTH icons at
  `fromBottom:12` (aligned). It actively masks the exact split that matters. Ground truth
  for this class of bug is the device screenshot + the on-screen dbg readout. (This is the
  same trap that ate v5–v11's "pwa bottom math".)
- **FIX:** `.panel` base rule `position:absolute → position:fixed` (anchors to the same
  viewport as the ⓘ; inert on desktop where body has no scroll). Both baselines nudged
  `12→18px` ("up a bit" per review). ⓘ left `12→16px` ("right a bit"). Pencil kept at
  `right:12px` — read "do it for the pencil" as *match the baseline*, not mirror the
  horizontal nudge (moving the FAB "right" would push it into its own corner). Say so to
  the user; easy to also nudge if they meant literal.
- **NEW DIAGNOSTIC line in `#dbgOverlay`:** `ⓘ fromBot N  ✎ fromBot N` — live
  `innerH − getBoundingClientRect().bottom` for both icons so the phone can confirm
  alignment by number. Desktop shows `18 / 18`; the phone MUST now also show equal numbers
  (was 12 / 62). **Strip this line with the other diagnostics at closeout.**
- **PWA LAYOUT LOCKED → snapshot saved.** User called the PWA styles "on point." The
  full working iOS-PWA markup + CSS (verbatim, annotated, with the five hard-won rules and
  the diagnostics-to-strip list) is now `brain/spinup/working_pwa_css.md`, pointed to from
  `brain_map.md` + `search_map.md`. This is the restore point — diff against it if the PWA
  layout ever regresses. **Not git-committed** (diagnostics still live; commit is the
  closeout step — offered to the user).

**PHASE 2 — iOS SAFARI TAB (`v14-dbg`) — diagnosed + red retired.** Device screenshot
`IMG_0719.PNG` + its `#dbgOverlay` gave ground truth: `standalone:false`, `innerH 663 /
clientH 663 / vv 663 @top0`, `screenH 812`, `#map t0 b663 h663`, `canvas h663`,
`safe T0 B0`, `ⓘ fromBot 18  ✎ fromBot 18`.
- **There is NO "short map" bug.** `#map` is `100dvh` = **663px** in the tab, and it fills
  it exactly (`#map h663` == `innerH 663` == `vv 663`). The missing `812 − 663 = 149px` is
  **Safari's own chrome** — top status bar (~50) + bottom address-bar toolbar (~99). A page
  in a Safari TAB cannot paint under that chrome (the PWA can, hence full 812). User asked
  "is there code to make it short?" — answer logged: no, it's Safari reserving the space.
- **The red bands were the diagnostic body bg.** iOS Safari tints its status bar + toolbar
  by sampling the page background; `html,body{background:#ff0033}` made both chrome zones
  red. **FIX: retired the red → manifest cream `#F5EFE0`** (`html,body{background:#F5EFE0}`).
  Invisible in the PWA (fixed map covers it); in the tab it's the neutral tint Safari shows
  in its chrome. Verify on device: bands should now read cream, not red. **The map cannot
  be made to fill Safari's chrome in a tab — that is by design, not a bug.**
- **Considered + rejected (don't re-litigate):** switching the tab to `#map{height:100vh}`
  to paint under the bottom toolbar — the §3 working-CSS comment already rejects it ("100vh
  runs too tall in a tab", bottom hidden behind the bar). Allowing scroll to minimize the
  toolbar (grows dvh) is out — we are deliberately `overflow:hidden`, no scroll, and it's
  janky. iOS `apple-mobile-web-app-status-bar-style` is inert in a tab.
- **Diagnostics after v15:** `#1e66ff` map background paint, the `#dbgOverlay` div + JS
  (incl. the `fromBot` line), the `-dbg` suffix — **ALL STRIPPED at v18 (see below).**
- **`v15-dbg` — top bar BLACK so it "disappears."** User asked to black out the top.
  `html,body{background:#000}` → iOS tints the Safari status bar + bottom band black; on a
  notched iPhone the black strips merge with the bezel/notch (white system text). One
  change cleans BOTH ends (the dark Safari address pill blends into the black bottom band
  too). Confirms the lever is body-bg sampling, not theme-color. Verify on device.
- **`v16-dbg` — inverted (concave) rounded corners.** User wanted the black frame
  rounded, not sharp. Four fixed `.screen-corner` divs (tl/tr/bl/br) after `#map`, each a
  `--frame-radius` (18px, tunable in `:root`) square painted with a radial-gradient that's
  transparent in a quarter-disc toward the map and `#000` in the outer L → a concave black
  corner that blends with the body bg + bands. `pointer-events:none`, `z-index:1` (above
  the map canvas, below all controls z≥2 so it never covers the pills/FAB). Hidden via
  `@media (display-mode: standalone)` (no bands in the PWA; device rounds the screen).
  Mechanism verified on desktop (Playwright): outer corner pixels `#000`, interiors reveal
  map/controls, 0 errors. On-device look (radius + alignment with the bands) is the user's
  to confirm; tune `--frame-radius` if 18px is too tight/loose.
- **`v17-dbg` — corner fillets scoped to iOS Safari TAB only.** Per user ("only iphone
  browser, no pwa, no browser"): `.screen-corner` is now `display:none` by default and
  shown only under `html.ios-browser`, a class the `<head>` script adds when `isIOS &&
  !standalone` (UA `/iP(hone|od|ad)/` or MacIntel+touch for iPad; standalone via
  matchMedia/navigator.standalone). Dropped the old `@media (display-mode: standalone)`
  hide. Verified (Playwright UA swap): default desktop → no `ios-browser` class, corner
  `display:none`; iPhone UA → class present, `display:block`. So PWA and desktop/non-iOS
  browsers get sharp corners; only the iOS Safari tab gets the rounded frame.
- **`v18` — DIAGNOSTICS STRIPPED, build clean (user: "happy with mobile styles").** All
  scaffolding removed: (1) the `#1e66ff` blue map-background paint → restored to `#efe7d5`
  at 3 sites (base style + two preset `paints.background`); (2) the `#dbgOverlay` div +
  `updateDbgOverlay()` + its resync wiring (incl. the `fromBot` line) deleted —
  `resyncViewport` kept (its `map.resize()` + search reposition are functional, only the
  overlay call dropped); (3) `-dbg` suffix dropped from `#appVersion` + `sw.js VERSION`,
  both now `v18`. **KEEPERS (not diagnostics):** the `#000` body bg (the black "disappear"
  chrome) and the four `.screen-corner` inverted fillets (iOS-tab-scoped). Smoke-checked:
  no console errors, no `dbgOverlay`/`updateDbgOverlay`/`1e66ff`/`-dbg` remnants (grep
  clean), body bg black, `resyncViewport` intact. The PWA §1-§8 layout rules in
  `spinup/working_pwa_css.md` are unchanged. **Still UNCOMMITTED** — the working tree is
  now the clean closeout build and is ready to commit whenever the user confirms the v18
  reload on the phone. (No build card was ever opened for this PWA work; open one under the
  active sprint if it grows.)
- **NEXT — bottom bar "fill with map" (user is open to it).** Real technique but a
  measure-and-iterate job, NOT a clean one-liner: Safari's bottom address bar is
  translucent and floats over the page, so painting the map behind it means sizing the MAP
  CANVAS to the large viewport (`100vh`/`100lvh`) while keeping controls on the visible
  area. The snag: the ⓘ attribution lives INSIDE `#map` and is bottom-anchored, so a taller
  `#map` pushes it behind the bar; iOS does NOT expose the tab toolbar height to CSS
  (`env()` insets are 0 in a tab), so re-anchoring the ⓘ above the bar needs a JS measure
  (`map.getBoundingClientRect().height − window.innerHeight` → a `--safari-bottombar` var)
  + on-device screenshot tuning. The FAB is a fixed body child so it's unaffected. The TOP
  status bar is NOT fillable in a tab — color/tint only (only the installed PWA goes
  edge-to-edge under the status bar). Do this as its own version once the user says go.

**2026-05-30 (triage) — Sprint 04 reviewed and sorted (no code).** Every card in
`tasks/04_event_app/` was assessed done / partial / not-done and moved.
**Shipped → `04_event_app/_done/`:** `calendar_group_icon_review`,
`editor_unified_tree`, `editor_three_buckets_v3c`,
`editor_unified_positioned_features`, `misc_4` (close-out header added), and a
**new split card** `bake_first_poi_serve_slice` (the shipped bake-first POI SERVE
pipeline carved out of `star_driven_poi_list` + `dev_db_snapshot_reseed`).
**Deferred → `tasks/10_deferred/`** (each got a "Deferred because" header):
`event_crud_upload_loop`, `paper_map_trail_extraction` (partial/active — flagged
it may belong on an active sprint if the edited-SVG loop continues),
`star_driven_poi_list`, `dev_db_snapshot_reseed`, `data_integrity_publishability`,
`brand_assets_and_permissions`, `calendar_placeholder_state`,
`park_bounds_icon_apply`, `rock_warblers_content_audit`, `poi_editor_followups`,
`viewer_polish_followups`. `source_layers.md` left in place (reference list, not a
card). `04_event_app/_readme.md` + `10_deferred/_readme.md` updated with the
disposition; pre-triage card list kept for history. Doc moves only, uncommitted.

**2026-05-30 (session 5g) — Locate + Install moved into left-rail float groups (V2).**
Two utility buttons that were scattered on the map chrome now stack as their own
floating groups below the calendar tab icon in `.left-controls`: **Locate** (neutral
cream 44px square, GPS-crosshair glyph) and **Install** (rust 44px square, download-to-tray
glyph). Picked V2 ("accented install") from a 4-up compare round. Implementation in
`website/index.html`: (1) new `.util-group`/`.util-btn`/`#pwaInstallBtn.util-install` CSS
matched to the `.lr-icon-col` chrome; (2) MapLibre's default top-right `GeolocateControl`
button is hidden (`.maplibregl-ctrl-top-right .maplibregl-ctrl-group{display:none}`) and
surfaced via a new `#locateBtn` that calls `geolocate.trigger()` and mirrors
`trackuserlocationstart/end`+`error` onto an `.active` (moss) state; (3) the old fixed
bottom-left `#pwaInstallBtn` + `#pwaIosHint` were relocated into `.left-controls` — the
install button *is* its own group and self-hides via the `hidden` attr until
`beforeinstallprompt` (so no empty rust card shows), single id preserved, PWA script
untouched (it's getElementById-based). Verified live (Playwright, geolocation granted):
locate visible at x13/y697 44×44 below the drawer, install rust square at y750, default
geolocate hidden, click → tracking + active state, 0 console errors. Compare round shipped
as review artifacts linked from the right panel **Comparisons** section
(`floatgroup_compare.html` + `floatgroup_v1_twins`/`v2_accent`/`v3_joined`/`v4_labeled`.html)
— retire per the `misc_4` mockup-cleanup routing once the look is locked. `website/index.html`
+ the 5 `floatgroup_*.html` mockups uncommitted.

**2026-05-30 (session 5f) — snap_trim "dangling" detector de-noised + the 3 ends verified.**
User challenged the "3 dangling ends" warning; all three verified and they were right.
`snap_trim_trails.py` had flagged any end >18 m from another feature, over-counting. Now
it classifies: **self-loops** (end rejoins its OWN line — trail "9" closes onto its own
vertex #6 at 0 m, a lollipop; not a gap), **road dead-ends** (a road that terminates in
space but joins the network at its other end — the unnamed road connects at 0 m one end,
74 m spur the other), and **trail danglers** (the real review set). Result on edited_10:
1 self-loop + 1 road dead-end + **1 true trail dangler** (unnamed trail start, 88 m from
trail 50). New `SELF_LOOP_M=2.0`; report now lists each by kind/name/gap. Served gold data
unchanged (re-run is 0 trim / 0 snap on edited_10). Minor latent bug noted: passing a
*relative* out-path trips `out.relative_to(REPO)`; default in-place run is unaffected.
`mvp/scripts/snap_trim_trails.py` uncommitted.

**2026-05-30 (session 5e) — trail search wired up.** The merged `aop-trail-network`
layer was never indexed for search, so trails were unfindable. Fixed in
`website/index.html`: (1) `indexFeatures(aopTrailNetworkData, 'trail', aopTrailNetworkToggle,
null, name→['trail <name>'])` registers every NAMED trail (number "32" or string "Riot
Hill"); unnamed edges are skipped. (2) The 2-char search floor now lets a lone digit
through (`/^\d$/`) so trails 1–9 are searchable. (3) New `searchRank()` orders matches
exact→prefix→substring, so a bare number floats the trail above building addresses that
merely contain the digit (without it, "9" buried trail 9 under "1094 Kelly Cove Road"…).
Selecting a trail flies there, flips the network layer on, pulses the highlight. Durable
coverage added to `playwright_verify_search.py` (trail-by-number, single-digit, string
name, fly+auto-enable) — PASS, no regressions. NOTE: the **20 unnamed trails** (from the
5d marker-rename fix) have no name → not searchable until the user names them in Affinity.
`website/index.html` + `mvp/scripts/playwright_verify_search.py` uncommitted.

**2026-05-29 (session 5d) — IMPORTER BUG FIXED (marker auto-renaming) + edited_10 reimported (current served).**
User: "something is renaming 32 and 58." Root cause found in `import_trace_svg.py`
`reattach_from_markers`: it stamped a nearby marker's `trail_number` onto UNNAMED
trails (then the name-fallback turned that number into the `name`). So one hand-typed
"32" became three "32"s — the #32 marker cluster sat near two unnamed neighbours — and
phantom "58"s appeared from a #58 marker on an unnamed trail the user never named.
Proof: edited_10 SVG has exactly one path named 32 and every SVG name unique, but the
importer output three 32s (sfwda-42/43 were `name=None` in the SVG). **Fix: markers no
longer assign `trail_number`/name at all — the user's typed object-name (`_editable_name`)
is the SOLE source of a trail's number/identity; markers still bootstrap DIFFICULTY for
uncoloured trails only.** Re-imported edited_10 with the fix → **0 duplicate numbers**,
32→1, 58→gone, 87 numbered / 100 named / 20 genuinely-unnamed (left for the user to name,
not auto-stamped). snap_trim 3 dangling, gold stamped, `playwright_verify_sfwda_trace.py`
PASS. This (edited_10 + fix) is the current served `aop_trail_network.geojson`,
superseding edited_11. The earlier dup find-and-fix loop (flag-red SVGs) is now moot for
auto-created dups; any remaining dups would be genuinely user-typed. `import_trace_svg.py`
+ `website/data/` uncommitted.

**2026-05-29 (session 5c) — edited_11 imported + dup find-and-fix (superseded by 5d).**
Pipeline `import → snap_trim → export_gold_trail_network --from …edited_11.svg`: 120
feats, 91 numbered, 0 grey (Easy 30 / Mod 42 / Diff 44 / Road 4). Verifier PASS.
Duplicate-number QA loop with the user: I flag duplicate-number trails RED in a
throwaway working copy → `export_trace_svg.py --color feature` → editable SVG
`aop_trail_network_2025_dupflag_edit.svg` (gold geojson left untouched; temp file
deleted after export). edited_11 cleared dups **1/47/90** (green 47→42, added 97) but
**28, 32(×3), 55 still duplicated** (55 is new — a 56 was renamed to an already-used
55). Also colour-vs-marker mismatches open: 35/95/97 green but markers moderate; 28(×2)
& one 32 colored black but markers moderate (markers = sheet symbols, stronger than the
number-band guess). Re-flagged SVG regenerated for the next pass. CAVEAT logged for the
user: don't leave any stroke red on re-export — red's nearest import anchor is orange,
so a leftover red imports as a *road*; recolour each to its real difficulty.

**2026-05-29 (session 5b) — edited_9 imported.** Same pipeline; identical aggregate
shape (120 / 94 numbered / 0 grey), diff geometric — 4 trails repositioned (11, 34, 47,
Pretender). Verifier PASS. Superseded by edited_11.

**2026-05-29 (session 5) — edited_8 imported + gold-export script.** Imported
`aop_trail_network_2025_edited_8.svg` (120 trails, osm merged into the one
`traced_trails` layer) → `website/data/aop_trail_network.geojson`: 120 edges, 94
numbered, 103 named, **0 grey** (Easy 30 / Moderate 46 / Difficult 40 / Road 4).
`snap_trim_trails.py` fixed 1 overshoot + 1 gap, 3 dangling >18 m left for review.
New **`mvp/scripts/export_gold_trail_network.py`** makes the "gold" step
reproducible: it rewrites only `_meta` (crs, colour legend, difficulty band, counts,
schema, auto-computed band-vs-colour `review_flags`) so the served file is the
self-contained gold the static viewer loads directly on a new install (no DB /
pipeline / localStorage). Run order: `import_trace_svg.py <svg>` →
`snap_trim_trails.py` → `export_gold_trail_network.py --from <svg>`. Verified: bbox
inside envelope, 0 degenerate, `playwright_verify_sfwda_trace.py` PASS. Review flags
this run: trails 35, 1, 95, 47 (colour vs number-band disagreements). Details in
`tasks/04_event_app/paper_map_trail_extraction.md` "edited_8 imported" block. All
`website/data/` + `mvp/scripts/` uncommitted.

**2026-05-29 (session 4) — string trail names + difficulty colours + snap/trim
(golden-data prep).** The merged network dropped `JW2`/`JW20` and other **named**
trails because the round-trip treated name as an integer. Fixed in
`import_trace_svg.py` (`_editable_name`: serif:id → inkscape:label → id; import
every name except `?`; non-numeric names locked) + `export_trace_svg.py` (writes
the name to both `inkscape:label` and `serif:id`). Re-import → 119 trails, 104
named, all 9 non-numeric names land (Area 51, GWT, JW1–4, JW20, Pretender, Riot
Hill). Colours switched from per-trail rainbow to **green/blue/black by difficulty**
(`assign_difficulty` band fallback; 22 grey unknowns flagged). New
`mvp/scripts/snap_trim_trails.py` cleans topology — 31 overshoots trimmed, 48 gaps
snapped, 3 dangling left for review. Re-exported the stack over the 2025 backdrop:
`brain/output/paper_trace/aop_trail_network_2025_edit.svg` (difficulty colours,
names on editable channels) — **this is the artifact for the user's review/edit pass
→ re-import = golden data.** `playwright_verify_sfwda_trace.py` PASS; overlay
`brain/output/net_2025_difficulty_overlay.png`. Details in
`tasks/04_event_app/paper_map_trail_extraction.md` "String trail names…" block. All
`website/data/` + `mvp/scripts/` + `website/index.html` uncommitted.

**2026-05-29 (session 3) — paper-map trail extraction PROTOTYPE.** New card
`tasks/04_event_app/paper_map_trail_extraction.md`. User goal: the SFWDA 2015
paper map is the only surviving record of trails the prior owner lost; extract
them cleanly. User corrected my framing — the sheet was **printed from a mapping
system, so it is positionally accurate once the (already-correct) warp is applied**;
"high for shape, low for current trails" was about 2015 *vintage*, not precision.
Built three `mvp/scripts/` scripts (need `numpy opencv-python-headless pillow
scikit-image shapely`, pip'd into the global Python): `extract_paper_trails.py`
(124 markers — 40 green Easy / 42 blue Moderate / 42 black-triangle Difficult;
triangles solved via close+OPEN since they fuse to the trail lines + trail-line
isolation), `paper_trace_warp.py` (`PaperWarp` exactly replicates the viewer's
270°-rotate + 6×6 bilinear mesh — corner self-check passes), `vectorize_paper_trails.py`
(skeletonize → graph walk → DP simplify → warp = 382 edges/1521 vertices, 116/124
markers matched). Outputs in `brain/output/paper_trace/` (scratch): `sfwda_markers.geojson`,
`sfwda_trails.geojson`, debug overlays. Verified by observation (overlays) + georef
self-check + bbox-inside-envelope. Per user ("load the data in the app to review,
refine after"), wired into `website/index.html` as two default-OFF, in-no-preset
review layers (`sfwda-trace-trails` + `sfwda-trace-markers`, toggles under External
reference) with data copied to `website/data/sfwda_traced_{trails,markers}.geojson`;
verifier `mvp/scripts/playwright_verify_sfwda_trace.py` PASS (512 features, survives
preset switch, 0 console errors). Visual: Trace preset + SFWDA raster + traced trails
shows the trace landing on the paper-map ink (`brain/output/sfwda_trace_review_traceonly.png`).
Open (refine pass): trail-number OCR (deferred, no higher-res scan), boundary-split,
camping-icon false positives, junction topology. `website/index.html` +
`website/data/` changes are UNCOMMITTED.

**2026-05-29 (session 2) — bake-first POI slice SHIPPED.** Acting on the
push-order decision (bake first; one `publish.geojson`), the SERVE half of the
star-driven pipeline now runs end-to-end: new `core.pois` table + `publish.pois`
gate in `mvp/init_db.sql`, `export_publish_geojson.sh` UNION extended with a
`layer='poi'` branch, idempotent `mvp/scripts/seed_core_pois.sql` (Pavilion +
Ellis Cemetery publish; a Proving-Grounds candidate left unpublished to prove
the gate excludes it — `core.pois`=3 rows, `publish.pois`=2), and `index.html`
renders the baked set as a `published_destinations` POI-tab group + `publish-pois`
map layer. Verifier `mvp/scripts/playwright_verify_baked_pois.py` PASS; adjacent
verifiers show only documented pre-existing fails. Authoring surface still NOT
chosen (fork open); legacy `buildPoiGroups()` scaffolding still renders alongside.
Full close-out + deferred items in `tasks/04_event_app/star_driven_poi_list.md`
"Bake-first slice — SHIPPED" block. All uncommitted.

**2026-05-29 — star-driven POI list: pipeline design (no code).** New card
`tasks/04_event_app/star_driven_poi_list.md`. Reviewed how the right-rail ★
Visitor list maps to the left POI tab; they're two lists built two ways and
only coincide for drawn POIs. Locked principle: **★ is the one curation gate;
the starred set _is_ the POI list** (all destination layers starrable, tab
starts empty, brand logos leave the ★ axis). User rejected designing against
the current files — the seed/index/localStorage stores are prototype
scaffolding. Target is **one pipeline: author → save to PostGIS → bake to file
→ static viewer serves the baked file** (= the northstar spine + source_register
`raw→core→publish`). The ★ collapses to one DB attribute + a publish-zone view;
the seed-vs-index file question is void. Gap: nothing wires the web editor to
the DB, and the DB→file bake is unwritten. Next decision owed: push order
between **(a) authoring surface — who writes the DB** and **(b) the bake**. This
was design/feeling-out only — no `website/index.html` change, tree clean.

**2026-05-28 — editor three-bucket V3c shipped.** Supersedes the unified-tree pass below. `tasks/04_event_app/editor_three_buckets_v3c.md`. The right-rail Map editor section collapses from 5 buckets to **3** (Point / Line / Polygon) plus the ★ Visitor list; Image and Callout fold into Point and Polygon by geometry (brand logos → Point/Brand, visitor context → Polygon/Visitor). Inside each bucket, source sub-groups split rows by origin (Drawn / Trailheads / Brand / Visitor) — Drawn is open by default, references collapse with their count visible. The 5-toggle layer strip is gone; the 5 `show*` inputs survive inside a hidden `#legacyLayerToggles` form block so preset capture/apply, MapLibre layer-visibility wiring, and Terra-Draw class flips keep working unchanged. Sub-group head bulk-checkboxes are the visible mirror, two-way bridged via change events. Each bucket head carries a green `+` that opens an inline `.editor-create-inline` row right inside the bucket body (bucket-scoped category select + matching primary action + cancel `✕` + help text); the footer shrinks to Export / Clear / status / help. `setDrawMode` now flips active state on every bucket's `+` and start-btn alongside the legacy hidden buttons. `draw.on('finish')` reads category from `currentCreateBucket.categorySelect.value`. A `FEATURE_LIST_LAYERS.trailheads` spec was added (read-only, no ★, no accordion); `publish.geojson` ships zero trailhead features today so the sub-group head reads `—` until trailhead data lands. **Event-schedule POIs are regular drawn POIs** — they render alongside editorPois Points inside the Point/Drawn sub-group with their `#tag` visible on the row. Mockups under `website/editor_unified_*.html` (compare pages: `editor_unified_compare.html` for V1–V4 axis pick, `editor_unified_v3_create_compare.html` for V3a/b/c create-flow pick) — retire per `misc_4` mockup-cleanup routing. Verifier impact: `playwright_verify_poi_editor.py` rewritten for the per-bucket selectors (PASS); `playwright_verify_presets.py` editor-tree assertion updated for 3-bucket shape (PASS on V3c assertions, 3 pre-existing fails remain — publishable-section / OSM-section-move / mobile-overlap, all routed to `viewer_polish_followups.md`); `playwright_verify_session_tools.py` PASS; `playwright_verify_synthetic_activity.py` PASS; `playwright_verify_feature_list.py` PASS on cemeteries/buildings/visitor/brand (3 fails pre-existing on retired publishable-section export path); `playwright_verify_event_schedule.py` PASS on tag-driven/clock-times blocks (6 fails pre-existing on trail-lane fallback). DOM snapshot screenshot at `/tmp/aop_editor_v3c.png` (not durable).

**2026-05-27 (later) — editor unified tree shipped.** `tasks/04_event_app/editor_unified_tree.md`. The right rail's `data-section="poi"` block (group toggle deck + `wirePoiPanel` two-way bridge) was deleted. The `data-section="editor"` section now hosts a five-bucket tree by renderable kind: ● Point · ╱ Line · ▭ Polygon · ⌗ Image · ⌑ Callout, plus a virtual `★ Visitor list` group at the top that live-mirrors every highlighted feature across `editorPois`, `brandLogos`, and `visitorContext` (the last two newly opted into `highlightable: true`; brand-logos and visitor-context override stores now carry `highlight` so the flag survives reload). editorPois renders three times via the new `renderFeatureList(layerKey, { onlyGroupId })` opt arg so its Point / Polygon / LineString groups split across the three matching buckets. The 5 layer toggles (`showEventSchedule`, `showTrailheads`, `showVisitorContext`, `showBrandLogos`, `showEditorPois`) move to a thin strip at the top of the editor section; the create row (category + Place / Draw / Trace + Export / Clear + status + help) drops to a `.editor-create-footer` at the bottom. `setEditorFeatureNotes` trim fix bundled in (one of the two S3 review items from `poi_editor_followups.md`). Verifier impact: `playwright_verify_poi_editor.py` PASS, `playwright_verify_synthetic_activity.py` PASS, `playwright_verify_session_tools.py` PASS, `playwright_verify_presets.py` PASS on editor-tree + console assertions (one pre-existing mobile-overlap 4 px boundary remains), `playwright_verify_feature_list.py` PASS on editor-tree + visitor-context reveal path (three `data-section="publishable"` failures pre-existing — that section does not exist), `playwright_verify_event_schedule.py` trail-lane fallback failures pre-existing per the earlier 2026-05-27 routing.

Read an archive only if you need to retrace why something was built. The durable record for each feature lives in its `tasks/*/_done/<feature>.md` build card, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.

## Where we are

Sprint 01 (MVP), Sprint 02 (Editor & Polish), and Sprint 03 (Event App Loop)
are closed. Sprint 03's reviewed cards live in `tasks/03_event_app/_done/`.
`tasks/03_event_app/misc_3.md` was left active by request. Sprint 04 starts at
`tasks/04_event_app/_readme.md`.

The Sprint 02 carryover router is archived at
`tasks/03_event_app/_done/viewer_polish_carryover.md`. Lanes 1–5 shipped
2026-05-24 (hot-control two-lane, calendar expand + scroll-into-view,
collapse-icon uniformity, default-layer audit table in `research/viewer.md`,
brand-logo size slider + add-image runbook). Lane 6 shipped its main pass in
`tasks/03_event_app/_done/code_health_pass_4.md`; residual viewer polish now
lives at `tasks/04_event_app/viewer_polish_followups.md`. Lane 7 stays on
`tasks/01_mvp/_done/community_trails_import.md` and is also visible in
`tasks/04_event_app/data_integrity_publishability.md`. The 2026-05-25 camera
correction is applied: zoom shortcuts reset to flat west-up, while Park / Topo
/ Trace layer presets preserve zoom, pitch, bearing, and independent 3D state.

**2026-05-25 Pass 4 + misc landings.** Calendar-card cream-surface chrome restored (`misc.md` "left side event calendar transparent" item — `.calendar-card` is back in the shared cream-surface group at `website/index.html:31`). Pass 4 first wave shipped via four parallel agents and landed in main: (1) `!important` cluster fully eliminated in the right-rail collapse-button + tune-control region by raising specificity to `.panel`-scoped selectors; (2) 8 safe palette token swaps (`#d8cdb4 → var(--cream-border)`, etc.); (3) full theme readability report (8 surfaces, 13 KEEP / 6 TWEAK / 4 FIX with WCAG math) recorded in `tasks/03_event_app/_done/code_health_pass_4.md`; (4) Critique-C1 hot-button copy renamed off "heat" wording — `Trail heat / Activity evidence` → `Trail activity / Where rigs spent time` in HTML defaults, `refreshHotButton` fallbacks, aria-labels, and the matching verifier assertion. Residual Pass 4 follow-ups now live in `tasks/04_event_app/viewer_polish_followups.md`.

Sprint 04's main app thrust is `tasks/04_event_app/event_crud_upload_loop.md`
— event setup, CRUD, uploads, and the submission -> review -> publish loop.
`tasks/04_event_app/dev_db_snapshot_reseed.md` carries the dev DB dump/reseed
need from `misc.md`. `tasks/03_event_app/_done/left_panel_poi_browser.md`
shipped 2026-05-25 — the viewer now has a third left-rail `POI` tab sitting
between `Events` and `About`, rendering a grouped index of event anchors,
in-park buildings, observed trails, cemeteries, off-park visitor support, and
drawn POIs. Visitor blurbs + revisit-note placeholders live in
`website/data/aop_poi_index.json` (6 groups, 20 entries, 10 placeholders
flagged for follow-up); the source GeoJSONs stay clean so re-exports can't
overwrite authored copy. Smoke checks land in the extended
`playwright_verify_presets.py`; a dedicated `playwright_verify_left_poi_browser.py`
is now carried by `tasks/04_event_app/viewer_polish_followups.md`.

**2026-05-26 — left-rail drawer shipped.** `tasks/03_event_app/_done/left_rail_collapse_tabs.md` shipped into `website/index.html`: Search / Hot / Calendar now live in a two-column left drawer with per-card icons, persisted open/closed state, hot-data auto-open that respects user-close, all-closed standalone state, and the calendar resize handle. Focused coverage: `mvp/scripts/playwright_verify_left_rail_drawer.py`.

**2026-05-26 — right-panel editor consistency.** `tasks/03_event_app/_done/right_panel_editor_consistency.md` shipped. `⧉ Export all` moved into the panel header beside `▾ Collapse panel` (the old `.panel-actions` row at the bottom of `#panelBody` is gone). Publishable section header gained its own `⧉` for parity with Source / Derived / Map editor; the POI section was deliberately not given one (its `poiGroup*` IDs don't match `sectionInputs`' `show*` filter, so the payload would be empty). Three layers that previously appeared as bare checkboxes in Publishable now get the full editor treatment: `activityHotspots`, `syntheticActivity`, and `eventSchedule` are registered in both `TUNABLE_LAYERS` (paint drawers) and `FEATURE_LIST_LAYERS` (CRUD index — 65 / 18 / 8 rows respectively, each with visibility + fly). New `refreshFeatureListData` helper lets `rebuildEventScheduleData` push fresh anchor data into the runtime without recursing through `registerFeatureListLayer`. The two failures in `playwright_verify_event_schedule.py` (search magnifier missing, hot-button click timeout) were verified pre-existing by stash + replay — not caused by this card.

**2026-05-26 — session tools shipped.** `tasks/03_event_app/_done/viewer_session_state_test_clock.md` shipped from `misc_2.md`: right-panel virtual clock controls (`aop_virtual_clock_v1`), Reset viewer, and pocket-map reload state (`aop_viewer_session_state_v1`) for active preset, active left tab, search query, and selected event. Landmark-hot decision: keep landmarks in POI/search, not a third Hot lane. Focused coverage: `mvp/scripts/playwright_verify_session_tools.py`; adjacent suites `playwright_verify_left_rail_drawer.py`, `playwright_verify_event_schedule.py`, and `playwright_verify_presets.py` passed after the startup-order fix for restoring the POI tab.

**2026-05-26 — drawn-POI CRUD reshaped.** `tasks/03_event_app/_done/poi_editor_tree_inline_accordion.md` shipped. The flat editorPois list is now a kind-grouped tree — `Drawn POI → POI / Footprint / Line → named item` (`FEATURE_LIST_LAYERS.editorPois.groups` matches on `feature.geometry.type`, and `groupForFeature` now passes `feature` through alongside `props` so other layers ignore the 2nd arg). Each leaf carries a trailing `▸` chevron that opens an inline accordion editor below the row: name, category (now mutable post-create), tag, notes (new `feature.properties.notes` field), geometry summary, action row (`🎯 Fly · ✋ Move · ⎘ Duplicate · ⧉ Copy GeoJSON · Delete`). Tag input and `⧉` copy button move off the row into the editor; visibility checkbox, `★` highlight, name (click=fly), `🎯`, `✋`, and the new `▸` chevron stay on the row. The MapLibre rename/delete popup (`openPoiPopup`) retired — map-click on a drawn POI now expands the leaf's editor in the right panel and flashes the row. Card mockup pass: `website/poi_crud_compare.html` + four `poi_crud_v{1..4}_*.html` variants; V1 (inline accordion) chosen. Same session shipped the editor seed + dump-to-GeoJSON path: `website/data/aop_editor_seed_pois.geojson` (schema `aop_editor_seed_v1`, first entry the `aop_seed_pavilion` POI at the 1010 Ellis Cove centroid carrying `seed_tag: '#pavilion'`); `maybeSeedEditorPois` runs on a fresh install or after Reset viewer and writes both the POI store and the `#pavilion` tag binding, stripping the matching tag off any other layer one-shot (migration: 1010 building → seeded POI). The building-side `maybeSeedFeatureTags` + `FEATURE_TAG_SEEDED_KEY` constant retired (the literal stays in the wipe list so existing installs get the sticky flag cleared on Reset). Workflow to update the seed lives in the create-row help text: `Export GeoJSON → replace the seed file with the download → commit`. Verifiers green: `playwright_verify_poi_editor.py` (asserts inline editor + delete; clean-slate now writes `[]` to leave the seed gate closed), `playwright_verify_feature_list.py` (POI copy path rewritten to expand the leaf first; same `[]` swap), `playwright_verify_presets.py`, `playwright_verify_session_tools.py` (Reset now asserts the seed re-installs `aop_editor_pois_v1` + `aop_feature_tags_v1` while the other ten viewer-owned keys stay cleared), `playwright_verify_event_schedule.py` (Tag-driven block rewritten: `#pavilion → editorPois/aop_seed_pavilion`, no building row pre-bound; live re-resolve test driven via `setFeatureTag` rather than the buildings drawer DOM).

The MVP backlog at `tasks/01_mvp/_readme.md` "Immediate next work" still has
open data-integrity items that unblock V1 publishable: item 9 (replace demo
trail/trailhead placeholders with real source-backed AOP data), item 3 (connect
QGIS to `localhost:55432`), item 8 (reconcile the 600+ acre official claim
against the parcel envelope), and item 10 (swap the AWS Terrarium DEM for USGS
3DEP 1 m tiles, deferred until the 10 m look earns its keep). Sprint 04 also
collects those blockers at `tasks/04_event_app/data_integrity_publishability.md`.

## Live preview ports

- Human/manual preview: `cd website && python3 -m http.server 8000` → `http://localhost:8000/`
- Playwright verifiers: `cd website && python3 -m http.server 8001` → `http://localhost:8001/`. If 8001 is occupied, clean up the stale Playwright viewer and reload 8001 instead of starting a new numbered localhost. Do not fall back to 8000 for Playwright.

## Loose ends not yet on a card

- SFWDA paper-map alignment: the 4-corner image-warp is inspection-grade. Decision still owed on whether true georeferencing (GCPs + affine/projective in GDAL/QGIS) is required before any SFWDA trail centerline can be promoted to `core.trail_centerlines`. Captured in `tasks/01_mvp/_done/community_trails_import.md`.
- `source_register.sources` rows still owed before any raw-zone context (OSM tracks/landmarks, NHD water, USGenWeb Ellis burial roster, FEMA building footprints) is promoted to a `publish.*` view. Rules: `northstar/source_register.md`.

## Sidecar artifact kept in this folder

- `event_schedule_context_20260522.json` — actively referenced by `tasks/01_mvp/_done/event_schedule_layer.md` and `research/viewer.md` as the sister-event research input. Leave in place until the schedule card is re-opened or retired.

## Session note

This file is handoff context, not a durable policy document. Keep it short. When a session ends, prune this file back to a pointer and archive the changelog to `session_context_<YYYYMMDD>.md`. Do not append session-by-session update blocks here — they belong in build cards, `research/viewer.md`, `search_map.md`, or `spinup/mvp_runbook.md`.
