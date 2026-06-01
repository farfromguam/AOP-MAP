# Copy review surface + copy-as-data

TL;DR:
- Built a single **printable copy-review page** (`website/copy_review.html`) that
  assembles every text surface in the app in one place to proof, each section
  headed with the repo-relative root file where that copy lives.
- Backed by a **master registry** (`website/data/aop_copy_registry.json`) that
  lists every copy "kind", its root file(s), where it surfaces, status, and
  whether the copy is in a data file or still in code.
- **Extracted the prose that was trapped in `index.html`** into data files:
  About tab → `aop_about.json`; interface microcopy → `aop_ui_strings.json`;
  calendar title now reads from `aop_event_schedule.json`. The viewer renders
  from those files with literal fallbacks.
- Shipped on branch `copy-review` (git worktree). Verified by Playwright +
  on-screen observation. UNCOMMITTED.

#aop #copy #content #review #print #editor-is-the-viewer

-----

## Why

The user asked for one place to proof all the app's words ("schedule callouts,
about… etc."), with links to where each root file lives, and a `schedule.json`-style
data file **per kind of thing** so copy is reviewable *data*, not strings buried
in code. Their list was explicitly not meant to be limiting — so this catalogs
*every* copy surface, not just the named ones.

Decision taken (user picked "extract everything now"): pull the hardcoded prose
out of `index.html` into per-kind data files and rewire the viewer to read them,
rather than only cataloging in place.

## Framing — Rock Warblers-first (2026-05-31)

User correction: **this app is a Rock Warblers product, not an AOP product.** The
Rock Warblers crew built it for their own events (the Trail Blazing Invitational
first) at Adventure Off Road Park — AOP is the **venue / host**, not the publisher.
The underlying source-traceable map and data spine is still the AOP map (the
northstar promise is unchanged); it's the shipped *viewer / PWA* that fronts as
Rock Warblers.

What that means for copy:

- **App identity / chrome was AOP-first** and is the frame to flip: `manifest.json`
  name + short_name + description ("AOP Map — Adventure Off Road Park", "AOP Map",
  "trail map for Adventure Off Road Park"), `aop_ui_strings.json` `app.title`
  ("AOP Map Viewer") + `app.home_screen_title` ("AOP Map"), and the in-code
  `<title>` + `apple-mobile-web-app-title` in `index.html`. Lead with Rock
  Warblers; keep AOP as the venue line.
- **Already Rock Warblers-first, left as-is:** the About tab ("About the Rock
  Warblers", "Built by Rock Warblers, for Rock Warblers"), the calendar (the Rock
  Warblers schedule), the Rock Warblers brand logo.
- **AOP-described copy is fine** — POI blurbs, trail catalog, visitor context
  describe the *place*. AOP is the place; describing it isn't an AOP-first framing
  problem and should stay.

This is really a project-shape fact, so it likely belongs in the northstar
(`whats_this_for.md` / `personas.md`), scoped to the *app surface* — elevate once
confirmed (northstar is locked, so flagged rather than written there unprompted).
App name is a small branding fork: crew-forward ("Rock Warblers Trail Map") vs
event-forward ("Trail Blazing Invitational") vs crew+venue ("Rock Warblers @ AOP").

**Reframed — shipped 2026-05-31 (mainline).** First cut went crew-forward
("Rock Warblers Trail Map" / "Rock Warblers"); user pulled it back — it read like
Rock Warblers *owns the park*. It's a Rock Warblers app, but **AOP is the
venue / host, not RW's land**. Landed **event-forward** instead — the name is the
RW event, AOP is plainly just where it happens:
- `manifest.json`: name → "Trail Blazing Invitational — Rock Warblers", short_name
  → "Trail Blazing", description → "The Rock Warblers' Trail Blazing Invitational
  at Adventure Off Road Park, South Pittsburg, TN. Trail map + event guide, works
  offline."
- `aop_ui_strings.json` `app.title` → "Trail Blazing Invitational",
  `home_screen_title` → "Trail Blazing" (drives the live `document.title`).
- `index.html` `<title>` → "Trail Blazing Invitational",
  `apple-mobile-web-app-title` → "Trail Blazing"; the `aop_copy_registry.json`
  `page_metadata` mirror updated to match.

**Voice rule learned: lead with the Rock Warblers event; never word the app so it
implies RW owns AOP.** The About tab already keeps this straight (crew = "Rock
Warblers… we build the rigs, walk the stages"; park = "Adventure Off Road Park…
private ridge") — left as-is.

Verified by observation (Playwright on mainline): live `document.title` =
"Trail Blazing Invitational", apple title = "Trail Blazing", manifest reframed,
copy-review page shows the new strings, zero old-name / AOP-first leftovers, 0
console/page errors. **Version bumped v21 → v22** (`#appVersion` + `sw.js VERSION`,
verified in sync + rendered) so installed PWA users pull the reframed chrome +
manifest on next load — they were SW-cached and would otherwise keep the old name.

## What shipped

### New data files (`website/data/`)
- **`aop_about.json`** (`aop-about-v1`) — the About-tab copy: heading, intro
  (lead + FB link + tail), 8 label/text items, closing note, `owed_work`.
- **`aop_ui_strings.json`** (`aop-ui-strings-v1`) — interface microcopy: page
  title, search placeholder, calendar countdown/loading/empty/unavailable, POI
  loading/empty, the hot-button labels, plus `*_reference` blocks for copy still
  set in markup (install steps, preset/zoom/tab labels, panel heading).
- **`aop_copy_registry.json`** (`aop-copy-registry-v1`) — the master index. 13
  kinds, each with `root_files` (repo-relative), `surfaces`, `status`
  (live/proposed/owed), `extraction` (data/in_code), `renderer`, and — for
  in-code kinds — the literal `copy` mirrored in so the review page is
  self-contained.

### New page
- **`website/copy_review.html`** — standalone, vendored-nothing, print-optimized.
  Fetches the registry, then loads each kind's root file and renders the actual
  copy grouped by kind. Each section header shows the kind, status + where-it-lives
  badges, the **repo-relative root path** (the filesystem location) plus a
  clickable `view ↗` link for `website/`-rooted files, and the surfaces it shows
  in. Gaps (null POI blurbs / `revisit_note`, `owed_work`,
  brand permission note, `proposed` caveats) render as ⚑ flags. Has a
  "Print / Save PDF" button, a "Show only gaps" filter, and a summary table.

### `index.html` rewires (copy → data, with literal fallbacks)
- About panel (`#aboutInfoPanel`) is now filled by a **copy-data bootstrap
  script** (added after the SW-register block) that fetches `aop_about.json`
  and builds the *same* DOM (`h2`, `.info-copy` + anchor, `.info-list` li >
  `.info-label` + span, `.info-note`) so the existing CSS holds. Inline About
  HTML removed; one no-JS fallback line kept.
- Same bootstrap sets `document.title`, the search placeholder, and the
  countdown label from `aop_ui_strings.json`, and exposes `window.AOP_UI`.
- `renderEventSchedule` sets the calendar title from `event.label` (the
  hardcoded "Rock Warblers…" span got `id="calendarTitle"`; label is the single
  source in `aop_event_schedule.json`).
- `refreshHotButton` idle/state labels and the calendar/POI empty+loading
  literals now read `window.AOP_UI?.…` with the old literal as fallback, so a
  missing strings file never breaks the viewer.
- `#appVersion` v18 → **v19**.

### `sw.js`
- `VERSION` v18 → **v19**; added `aop_about.json`, `aop_ui_strings.json`,
  `aop_copy_registry.json` to `DATA_ASSETS` (best-effort precache, so About +
  microcopy are available offline like every other layer).

## The 13 kinds (current status)

| Kind | Root file | Status | Where |
| --- | --- | --- | --- |
| About tab | `aop_about.json` | proposed | data |
| Event schedule | `aop_event_schedule.json` | proposed | data |
| POI visitor blurbs | `aop_poi_index.json` | proposed | data |
| Trail catalog | `aop_trail_catalog.json` | proposed | data |
| Visitor context callouts | `aop_visitor_context_callouts.geojson` | live | data |
| Brand logos | `aop_brand_logos.geojson` | live | data |
| Interface microcopy | `aop_ui_strings.json` | live | data |
| PWA metadata | `manifest.json` | live | data |
| Page title / metadata | `index.html` | live | in_code |
| Layer toggle labels | `index.html` / `research/viewer.md` | live | in_code |
| Map feature popups | `index.html` | live | in_code |
| Map attribution / credits | `index.html` | live | in_code |
| Show & Shine awards | `northstar/events/show_and_shine_northstar.md` | owed | not-in-app |

## Extraction line (what was deliberately NOT ripped out)

The four `in_code` kinds — page metadata, layer toggle labels, per-feature popup
strings, attribution credits — are **cataloged with file locations + the literal
copy mirrored into the registry** but left in the markup/JS this pass. They are
interleaved with toggle IDs, preset capture/apply logic, and per-feature map
render code; extracting them risks the locked viewer for little copy-review gain
(layer labels + provenance are already the authoritative catalog in
`research/viewer.md`). They show on the review page from the registry's `copy`
arrays. Extraction is a clean follow-up if wanted.

## Verification (by observation)

Served the worktree `website/` on `:8001`; Playwright + screenshots:
- `index.html` (5 consecutive loads): About renders from JSON (h2 + 8 items +
  link + note), calendar title = `event.label`, `document.title` + search
  placeholder + `window.AOP_UI` from `aop_ui_strings.json`, **0 console errors**.
  Screenshot `brain/output/copy_review_index_about.png` shows the About tab and
  the `v19` chip.
- `copy_review.html`: 13 kind sections + 13 summary rows, all copy assembled
  (About, sessions, trails, visitor context), gap flags present, root-path links
  rendered, no per-kind load errors, **0 console errors**. Full-page screenshot
  `brain/output/copy_review_page.png`.
- One transient `Could not compile fragment shader` pageerror appeared on a
  single earlier run; a 5× re-probe showed 0 shader errors and is unrelated to
  copy changes (plain DOM/fetch can't compile shaders) — headless-WebGL
  flakiness. Logs: `brain/output/copy_verify.log`, `shader_probe.log`.

## Owed / next

- This is **proposed** event copy — confirm the About format/rules and the
  600-acre figure with the event lead / AOP before it reads as official
  (`aop_about.json` `owed_work`).
- POI blurbs: authored blurbs are now in the project voice (see the 2026-05-31
  voice-pass block below); 11 `null` blurbs still carry `revisit_note` gaps
  (`aop_poi_index.json`).
- Trail catalog: rewrite onX-sourced descriptions in the park's voice before any
  public publish (license).
- Wire the Show & Shine award set into the schedule or a handout once locked.
- Optional follow-up: extract the four `in_code` kinds to data files.

## Trail research integration (same branch, 2026-05-31)

On this branch we also shipped Slices 1–2 of
`tasks/04_event_app/trail_research_integration.md` — wiring the trail catalog
(names + descriptions) into the live viewer so those refined text blocks have a
real surface before they are "applied". Runtime sidecar join (no prose baked into
geometry), mirroring the POI-index pattern:

- `fetchTrailCatalog()` + `trailCatalogLookup(props)` join `aop_trail_catalog.json`
  to the gold `aop-trail-network` by `trail_number`.
- **Slice 1:** new `bindPopup('aop-trail-network', …)` — name + map-color difficulty
  (park authority) + catalog About / length / onX TR (secondary) / connects;
  un-catalogued trails → number + difficulty + "owed". No license footer.
- **Slice 2:** POI browser trails group repointed from the legacy
  `publish.geojson trail_centerlines` to the gold network + catalog (one row per
  trail, ~100 rows, 9 with write-ups, the rest "name/description owed").
- **Descriptions rewritten in brain voice** (`brain/voice/voice_guide.md`): the 8
  onX-sourced write-ups are now original AOP wording (same facts, new sentences),
  so the prior onX-copyright caveat is dropped everywhere. Trail 96 keeps the
  park's own 2015 wording.
- `aop_copy_registry.json` `trail_catalog` kind updated to the 3 live surfaces.

Verified by observation (`brain/output/trail_verify.log`, `trail_integration.png`).
Full record + remaining forks in `trail_research_integration.md`.

## POI-blurb voice pass (2026-05-31)

The About tab and the trail catalog were already rewritten in the project voice
(`brain/voice/voice_guide.md`); the **POI visitor blurbs** in `aop_poi_index.json`
still read like the older 2026-05-25 authoring — serviceable, but a notch off the
bar and leaking plumbing into reader copy. Brought them up:

- `#pavilion`, `#registration`, and the 1010 building blurb dropped the
  implementation tails (`via the #pavilion tag`, `via the #registration alias`,
  `confirmed by the user`) for reader-facing wording — provenance kept (which
  building, FEMA footprint, AOP-confirmed), plumbing gone.
- `#observed-trailhead` + Saturday-segment-2 blurbs tightened to the present-author
  voice; every fact preserved.
- `updated_at` → 2026-05-31. Six string edits, no key/structure change.

What was deliberately **left**: the 11 `null`-blurb `revisit_note` gaps (real owed
work, not voice), all internal `purpose`/group-`note`/provenance metadata,
the `in_code` kinds (popup/attribution/layer-label/page-title strings — structural
source-name strings, extraction still deferred), and **trail 96**'s preserved 2015
park wording. One thing to flag: trail 96's kept line ("Passable by modified Jeeps
and Trucks") is literal 1:1-OHV framing in a scale-RC catalog — intentional as a
historical artifact, but worth a look on the user's own edit pass.

Verified by observation: `copy_review.html` renders all 13 kind sections, 0
console/page errors, all 5 rewrites present and all 3 plumbing strings gone; the
viewer consumes `aop_poi_index.json` with 0 console errors and shows the rewrites
in the POI tab (1 transient headless-WebGL shader `pageerror`, the documented
flake, unrelated to copy). Edited in an isolated worktree, then the **content was
moved into the master working tree directly (no git merge)** at the user's
direction — there are upstream git changes the merge should not disturb. The
worktree's file is byte-identical to what shipped to master.

## Files (branch `copy-review`, uncommitted)
- new: `website/copy_review.html`, `website/data/aop_about.json`,
  `website/data/aop_ui_strings.json`, `website/data/aop_copy_registry.json`
- edited: `website/index.html` (copy bootstrap + calendar title + hot/empty
  strings + **trail catalog loader + trail popup + POI trails repoint**),
  `website/sw.js`
- brain (main checkout): `tasks/04_event_app/trail_research_integration.md`
  marked Slices 1–2 shipped.
