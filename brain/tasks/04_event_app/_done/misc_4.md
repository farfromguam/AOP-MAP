misc 4 (also in sprint 4)

> **Closed — Sprint 04 triage (2026-05-30).** Every line below is shipped,
> routed, or held by the user; nothing actionable remains on this card:
> - Items 1–5 + the "PENDING BELOW" block (POI/About empty space, tab restore):
>   **shipped 2026-05-27** (see "What shipped" below).
> - Images + region callouts in the export script: **shipped 2026-05-30** (bake
>   script `export_positioned_features.py`; positions reviewed + confirmed
>   already-committed).
> - Item 6 (sticky header scroll-with-events): **held by the user** — "leave it
>   alone." Won't-do, not pending.
> - Building tags (1033 farmhouse / 880 park offices / 1010 pavilion → native
>   footprints in DB): **routed** to `10_deferred/data_integrity_publishability.md`;
>   gated on source verification before promotion.
> - "cleanup worktrees that are unused": **user-owned chore** (destructive
>   `git worktree remove --force`; left to the user per `ai_rules/no_commits.md`,
>   also tracked in `04_event_app/_readme.md`).
> User-written directives preserved verbatim below.

events show past events button needs to go.
poi expand all groups needs to go.
about events page link needs to be added to the body of the text above as a url body link not a button

events poi about should have a consistant expand handle at the bottom.
no minimum height no max height but set defaults on page load.
browser is taller.
phone is shorter.
user can adjust as needed or can collapse completely


there is some code to assume every friday is the event week so our or countdown is 2 days vs 2+weeks. now that we have session tools this is not needed

=== RESOLVED ABOVE === PENDING BELOW ===

events looks goods
poi has a white space at the bottom and no pull handles
about has a white space and the pull handle is above that white space
it works but it is wrong. 
what are we doing different in these three tabs???

current tab in calendar is not being restored on reload

---
tag these buildings, make hem 
1033 is the farmhouse
880 is the park offices
1010 is the pavallion
make all 3 buildings native footprints. put them into our database.
export our database and reload the data.
buildings should be in two places 
buildings layers
and our footprints. at this time we are good to turn off buildings.

---

cleanup worktrees that are unused.
clean up 




---

images and region callouts should be included in our "export" script.

the updated locations will be baked into the map and we wont loose positions on data reset.

-----

## What shipped (2026-05-27)

Items 1–5 done in the working tree (uncommitted):

- Item 1: `#showPastEventsBtn` removed.
- Item 2: `#poiExpandAllBtn` removed.
- Item 3: About `Event page` button removed; Facebook URL is now an inline `<a>` on "Trail Blazing Invitational" in the lead paragraph. `.tab-footer` / `.tab-footer-btn` CSS removed.
- Item 4: Resize handles. One shared `--lr-card-body-height` on `.lr-content-col`. Each tab gets its own `.lr-resize-handle` sibling outside the scroll body. No min/max — drag to 0. Old `setCalendarBodyHeight` / `initializeCalendarResize` chain deleted. localStorage key bumped `aop_calendar_height_v1 → aop_lr_card_height_v1` (old key retained one sprint in `VIEWER_OWNED_STORAGE_KEYS` per `spinup/viewer_storage_migration.md`).
- Item 5: Friday-of-week shim removed. `parseEventAnchorFriday()` reads `eventScheduleConfig.event.date_range_label`; `CALENDAR_MONDAY_RESET_HOUR` / `mondayResetMs` deleted.

Item 6 (sticky header scroll-with-events) held out by user — leave it alone.

"PENDING BELOW" block addressed:

- POI/About empty cream space → fixed by dropping `.left-tab-panels` grid-stack-to-tallest back to `display: block` (`website/index.html:359-364`). Each tab-panel now sizes to its own content. Tab switch between Events (has `.calendar-heading`) and POI/About produces a ~62 px shift; we accept that over the dead cream gap. Reverts the misc_3 item 21 stack. Visual confirmation: `brain/output/misc_4_left_tab_{events,poi,about}.png`.
- Current tab on reload → tab restore fix shipped; the event-session auto-restore no longer force-calls `setLeftTab('events')` when `viewerSessionState.active_left_tab` is POI/About. POI and About now stay put on reload.

Routed elsewhere:

- "1033 is the farmhouse / 880 is the park offices / 1010 is the pavilion" — these are building feature-tag bindings, not a misc_4 follow-up. Owed by source verification before promotion. Captured at `tasks/04_event_app/data_integrity_publishability.md` for the tagging pass on the buildings drawer.
- "images and region callouts in the export script" — SHIPPED 2026-05-30, see below.

Verifier residue:

- `playwright_verify_event_schedule.py` Trail-lane click tests vs. `hotButtonFlyToHotspots` off→on edge (6 pre-existing FAILs) logged at `tasks/04_event_app/viewer_polish_followups.md` under Code Health. Not caused by misc_4.

No git commit per `ai_rules/no_commits.md`.

## Images + region callouts in the export script (2026-05-30)

The "images and region callouts" line is closed. Background: brand logos
(`website/data/aop_brand_logos.geojson`) and visitor-context region callouts
(`website/data/aop_visitor_context_callouts.geojson`) are **file-based** layers
the static viewer loads directly — they are not in PostGIS, so
`export_publish_geojson.sh` (PostGIS publish views only) never touched them.
Drag/resize overrides lived only in localStorage (`aop_positioned_features_v1`),
so a Reset viewer / data reset snapped them back to seed coords and lost the
placement work.

New bake script **`mvp/scripts/export_positioned_features.py`** closes the loop
(same "bake the served file" pattern as `export_gold_trail_network.py`). It reads
the viewer's right-panel export — "Export all" (`aop-viewer-preset-settings-v3`,
key `positioned_features`), section Copy (`aop-section-state-v2`, key
`positionedFeatures`), or a bare `"<layer>:<id>"` map — and bakes each
override's `geometry` (plus `icon_size` for logos) into the two seed files in
place. Runtime flags (`highlight`/`locked`) are session state and are ignored.
Coords rounded to 5 decimals to match seed style; a `generated` date is stamped
into each changed file; overrides naming an unknown id are flagged and skipped.
`--dry-run` previews.

Loop: drag/resize in viewer → right panel "Export all" → save JSON →
`python3 mvp/scripts/export_positioned_features.py <file>` → commit the changed
geojson. Both seed files carry a bake-workflow note in their metadata.

Verified on `/tmp` copies (real seed files untouched): a synthetic override
moved + resized `aop_badge`, moved the South Pittsburg callout polygon, left
`rock_warblers` alone, ignored an unknown id, and produced valid canonical
2-space GeoJSON (json.loads round-trip holds). Script + the two seed-file notes
uncommitted per `ai_rules/no_commits.md`.
### 2026-05-30 (later) — positions reviewed + baked

User exported viewer settings and asked to review + update image locations and
the visitor-context callouts. Baked the four `positioned_features` overrides into
the seed GeoJSON via `export_positioned_features.py`:

- **Brand logos** — moved off the old off-park seed (`-85.7510, …`) onto the park
  core and resized: `aop_badge` -> `-85.74157, 35.08698` size `0.2`;
  `rock_warblers` -> `-85.74188, 35.09385` size `0.19`. On-park, consistent sizes.
- **Visitor context** — near-park **directional annotation circles** (the file's
  own `_description`: "cartographic annotations, not surveyed service-area
  boundaries"); the geometry is an orientation anchor, the *label* carries the
  town + drive time. Checked each circle's bearing from park (35.087, -85.742)
  vs the real town:
  - *SP / Kimball supply run* -> 0.83 km @ 158° (SSE). Real South Pittsburg 157°,
    Kimball 119°. Matches its "SE" label. Baked as exported.
  - *Monteagle plateau services* -> the **exported drag landed at 9° (NNE)**, but
    its own "N/NW TO MONTEAGLE" label and real Monteagle (336°, NNW) are to the
    **northwest** — wrong side (the original seed was correctly NW).
    **Corrected**: re-baked the circle to `35.10362, -85.75093` = 2.02 km @ 336°
    (NNW), keeping the user's distance/radius. Trivial to revert if NNE was
    intentional.

Town coords verified via web (Monteagle 35.2384/-85.8255, South Pittsburg
35.0094/-85.7017, Kimball 35.0561/-85.6739).

NOTE: the bake output is **byte-identical to committed HEAD** — both seed files
`git diff` empty. HEAD (`747e5bc "bake image positions"` + `7c8e9d2 "bump
version"`) already carries the correct end state, including the **NNW-corrected
Monteagle** (35.10362, -85.75093). So the positions are already baked + committed;
this pass re-derived and confirmed them rather than producing a new data change.
The viewer-localStorage export the user pasted held a stale NNE Monteagle drag —
committing it would have *regressed* the already-correct file. No data commit
needed; only this note + the regenerated verifier screenshots are uncommitted.

Verifiers run against the baked files (server on :8001):
- `playwright_verify_visitor_context.py` -- **PASS** (all green: two callouts,
  labels/drive-times, deep-links, circles render, search jump, 0 console errors).
- `playwright_verify_brand_logos.py` -- **PASS on the baked data**; the only two
  FAILs are in the "Feature list panel" section ("feature list opens with 2 rows
  -- []" / "rows expose both logo_ids -- set()"). Verified **pre-existing** by
  swapping in the HEAD version of the file and replaying -- identical failures, so
  the panel-row selector is broken independent of this change. All data
  assertions passed with the new coords/sizes (seed, icon_image registration,
  icon_size slider live+persisted, drag-to-move, reload persistence). The
  panel-row regression belongs to `viewer_polish_followups.md`, not this edit.

### 2026-05-30 (later) — PWA bottom-space fix (notch follow-up)

After the notch/safe-area work (`viewport-fit=cover`, `--sa-*` insets), the user
flagged the BOTTOM in the installed PWA: "white space below the map margin" +
"excess padding." Two distinct causes, both fixed in `website/index.html`:

1. **White band = the MapLibre attribution control, not a map gap.** The map
   canvas fills the viewport fine (`#map` is `position:fixed; inset:0`, canvas
   measured 390×844 in sim). The "white space" was the verbose per-source
   attribution string wrapping to a ~104px **solid-white box** at the narrow PWA
   width. MapLibre v5.24 auto-compacts the control at container width ≤640px but
   starts it EXPANDED (`maplibregl-compact-show`), only minimizing to the ⓘ on
   the first map *drag*. The class is auto-added once, at the empty→first-content
   transition (after `load`, since this viewer adds sources dynamically). Fix: a
   `sourcedata` listener (`collapseAttribOnce`) waits for `maplibregl-compact`,
   removes `compact-show` + the `open` attr once, and unbinds — so it starts as
   the ⓘ and still expands on tap. **Guarded to `innerWidth ≤ 640`** so desktop
   keeps its full-width attribution bar (this build carries the `compact` class
   even when wide, an init-timing quirk, so the width check — not the class — is
   what scopes the collapse to phones). Verified: mobile 24×24 ⓘ, tap→expands;
   desktop full bar unchanged (matches the committed original); 0 console errors.

2. **Excess padding = base offset stacked on the home-indicator inset.** Bottom
   chrome used `calc(BASE + var(--sa-bottom))`, so a 34px home indicator added to
   the 12px base = a 46px gap. Switched the edge-anchored bottoms to
   `max(BASE, var(--sa-bottom))` (take the larger, don't sum): `.message` and the
   desktop `.panel` → `max(12px, var(--sa-bottom))`; the mobile `.panel`'s
   message-bar reserve → `calc(max(12px, var(--sa-bottom)) + 44px)`. In the PWA:
   message gap 46→34px, panel gap 90→78px. In a plain browser (sa=0): unchanged.
   Also set `html` background to the map cream (was `body` only) as a belt against
   any sub-pixel strip on real iOS.

Bundled in: a build-version chip (`.util-version` / `#appVersion`, "v5") under the
Install square in the left rail — always visible since the install button
self-hides once installed — and a `sw.js` bump `VERSION v4→v5` (the two name the
same build, kept in sync by comment).

NOT the same as the `poi`/`about` left-tab "white space at the bottom" items
above — those are the left-rail content-panel heights, still open.

Verified by observation only (Playwright, simulated `--sa-top:47px`/
`--sa-bottom:34px` per the code's DevTools-override note — Chromium can't emulate
iOS `env(safe-area-inset-*)`). Before/after sim screenshots confirmed the white
band gone and the tighter bottom. Originally done on the `worktree-pwa-bottom-space`
worktree; **merged into the main checkout** (`website/index.html` + `website/sw.js`,
3-way merged over the `callapse panel` commit — disjoint regions, 0 conflicts) and
the worktree removed.
