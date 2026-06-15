## Disposition — QA swarm (2026-05-31)

A 7-agent worktree swarm resolved most of this card. Each agent owned a disjoint
region of `website/index.html`, committed in its own worktree, and I merged the
seven branches into the master working tree (uncommitted, per `no_commits.md`).
Consolidated backup branch: `integration-pwa-qa`. Merge verified: all inline
script blocks `node --check` clean, the one overlapping hunk (hot-lane glyph
~7083) hand-confirmed coherent, 0 non-GL console/page errors on load, DOM
reflects each change. The map canvas will not paint in this headless env (GL
context fails — the documented "Playwright unreliable for this viewer's GL"
trap), so per-item map-render behavior was verified by each agent in isolation
and final on-device/visual confirm is owed where noted.

| # | Item | Status |
|---|---|---|
| 1 | comparison mockups on right sidebar | standing rule; followed (topo compare added to Comparisons). **2026-05-31: each Comparisons row now carries an applied/open status badge** — green `✓` (winning variant live in `index.html`, with the variant name in the badge: V5 FAB / Applied / V3c / V2 / A·sienna) vs rust `◌` (still the user's pick: Right-sidebar A/B/C toolkit = Open, Park-bounds icon = Pick owed). Badge `title` carries the one-line disposition; update the badge when a comparison resolves. CSS `.cmp-status`/`.cmp-applied`/`.cmp-open`. |
| 2 | bottom row on one horizontal row (V1–V4 mockups) | **DONE** — confirmed (2026-05-31) superseded by the shipped V5 pencil-FAB rework; retire V1–V7 bottom-bar mockups per the cleanup routing |
| 3 | restrict zoom on buttons | DONE (pre-existing; verified not regressed) |
| 4 | bake region callouts to geojson | → `pwa_qa_data_bakes.md` |
| 5 | logo max size + slider + export | **SHIPPED** (zoom-clamped icon-size cap, `#brandLogoCapSlider` + ⧉ export; verified region/park ratio 0.18). Tune-and-return open |
| 6 | bake in-park / exclude region buildings from search | → `pwa_qa_data_bakes.md` |
| 7 | two-finger pinch responsiveness | **SHIPPED then REVERSED.** Originally shipped `touchZoomRotate.disableRotation()` (+ `dragRotate.disable()`) so a two-finger touch starts pinch-zoom without disambiguating against twist-rotate. **Reversed 2026-06-15 by user directive** (*"we used to be able to spin it around while it was tilted … we want to enable it"*): rotate is back on — two-finger twist + desktop right-click now spin the bearing, so the tilted 3D view orbits again. Pitch stays button-only (`touchPitch.disable()` kept + `pitchWithRotate:false`), so stray fingers still can't tilt. **Trade-off to confirm on-device:** the pinch-start responsiveness this row fixed may regress, since the two-finger handler must again disambiguate pinch-zoom vs twist. v95→v96; `brain/output/verify_spin_while_tilted.py` 7/7. |
| 8 | "X published features" — drop it | ALREADY DONE (`.message{display:none}`, the V5 drop) |
| 9 | remove trail dots | **SHIPPED** (`sfwda-trace-markers` circle layer removed; numbered labels kept) |
| 10 | "1X" in a search for trail "1" | **SHIPPED** (verified: trail 1 top, 1X surfaced, buildings demoted) |
| 11 | calendar auto-scroll + header scrolls with body | **SHIPPED** (verified: tab heights equal, auto-scroll lands on live row) |
| 12 | park zoom tighter than region | **SHIPPED** (verified: Region 13.74 / Park 14.61→14.75, delta +1.01) |
| 13 | topo colors / OSM off / blue-green-black map, orange topo | **SHIPPED** (OSM tracks off, trail network default-on, orange on topo, contours lightened, `topo_color_compare.html` for final pick); on-device color confirm owed |
| 14 | hot-spot button first-click + toggle + 2nd state | **SHIPPED** (verified cold-click→on→off; new `data-hot-on` state) |
| 15 | drawer offset after edit-panel collapse | **SHIPPED** (`window.lrReflow` recompute on collapse); on-device drag confirm owed |
| 16 | end date on calendar | **SHIPPED** (verified: "Friday, June 19 – Sunday, June 21, 2026") |
| 17 | extend 9-patch imagery coverage | → `pwa_qa_data_bakes.md` |
| 18 | icon line weights | **REWORKED — cohesive icon family, optically normalized + measured** (2026-05-31). The 05-31 swarm typed `stroke-width="1.6"` on everything (fudging the vb24 icons to 1.75/2.1) and declared it done without measuring — and never touched the bottom util icons at all. **Real root cause (per the user, confirmed by measurement):** not viewBox (all vb22) and not stroke number (all ~1.6) — it's **optical size** (how big the art is drawn *inside* the canvas) plus **white-on-rust bloom**. Icons whose art filled less of the 22 box (`locate`'s r5 circle, my narrow tree + flame) read FAT at the same stroke; the rust-fill `install`/pencil-`FAB` bloomed heavier. **Fix (one icon family):** all on vb22, art normalized to fill the same optical box (enlarged `locate` circle r5→6.4, widened the tree + flame, redrew the foreign Heroicons flame — both `lrTabHot` and the live-event JS glyph — as a geometric line flame); single 1.6 stroke with **principled, documented exceptions**: tree 1.4 (acute conifer joins bulge), `install` 1.4 + pencil FAB 1.2 (white-on-rust bloom). Shrank `zoomPark`'s blob dot r1.6→1.1. **Verified** by optical re-measurement (Playwright DSF6 + art-bbox/run-length, `brain/output/icon_audit/`): the stroke/art-size spread tightened 0.077–0.126 → **0.077–0.104**, and the `all_icons.png` strip now reads as one family. Two lessons logged: equal stroke *number* ≠ equal *rendered* weight; and equal rendered weight ≠ equal *optical* weight (art size matters). 0 vb24 icons remain. |
| 19 | bottom-left attribution overflow breathing room | **SHIPPED** (clearance widened; clears the FAB by ~24px) |
| 20 | satellite tree icon | **REWORKED — wrong interpretation removed, button glyph is now a tree** (2026-05-31). The request "satellite view needs a better tree icon" meant the **single icon that represents the satellite preset** — top-row button #7, `presetSatellite` — should be a tree. The 05-31 swarm instead read it as *tile a tree SVG across the forest polygons* and built a `landcover-forest-trees` fill-pattern layer (+ `website/img/tree.svg`) wired to the satellite toggle ("the jank ass icon field"). User rejected that: it "should never have been created." **Removed entirely:** the `landcover-forest-trees` layer, its `forest-trees` image load, its entry in the satellite `LAYER_TOGGLES` row, and the orphaned `website/img/tree.svg`. **Replaced** the satellite preset button's globe-reticle glyph with a 2-tier conifer (`fill="none" stroke="currentColor" stroke-width="1.6"`, matches the three sibling preset glyphs and inverts cleanly on the moss `.active` state). Lesson logged: I debugged *why the field wasn't rendering* (layer order) instead of questioning whether the field should exist — anchored on the prior session's framing, not the user's words. Inline script `node --check` clean; glyph swap grep-confirmed |
| 21 | icon groups 3-4-1 width | **SHIPPED** (`3fr 4fr 1fr`; per-icon width spread 13.2px→1.75px) |
| — | iOS bottom padding | RESOLVED (pre-existing, see below) |

**Owed on-device confirm** (touch/GL — cannot be checked headless): 7 pinch,
13 rendered colors, 15 drag-under-finger. **Open forks:** none — 2 confirmed
superseded by V5. **Item 20 was reworked 2026-05-31:** the swarm's tiled tree
FIELD was the wrong reading of the request and was removed wholesale; the
satellite preset button glyph (top-row #7) is now a tree — see the item 20 row. **Worktrees:** 7 harness-locked agent
worktrees remain under `.claude/worktrees/` — cleanup left to the user/harness
(`git worktree remove -f -f <path>` + `git branch -D worktree-agent-*`), consistent
with the existing convention.

-----

all comparison mockups should be put on the right sidebar with a link the the item to look at. I will review and pull attributes from each different column.

bottom row items should all fit on one horizontal row.
make a few mockups to compare this. minimal. 

> **Mockups shipped 2026-05-30 (awaiting pick).** The two stacked bottom bars
> on the phone PWA — collapsed `.panel` "AOP edit panel" header (⧉ export + ▸
> expand) and the `.message` "N publish features loaded" pill — folded into one
> horizontal row, 4 minimal takes:
> - **V1 split** (`bottombar_v1_split.html`) — moss status zone (count) | edit header, one hairline.
> - **V2 chip** (`bottombar_v2_badge.html`) — edit header owns the bar; status is a small count chip by the buttons.
> - **V3 icon** (`bottombar_v3_iconbar.html`) — pencil + "Edit", status = single load dot; tightest.
> - **V4 cells** (`bottombar_v4_cells.html`) — two named cells ("5 published" | edit); most legible, largest.
>
> Compare page: `website/bottombar_compare.html` (phone frames + attribute
> table), linked from the right-sidebar **Comparisons** section of `index.html`.
> Real count today = 5 (publish.geojson). Open: drop the status entirely (ties
> to item 7); apply to desktop too or leave it. Retire the mockups per the
> `viewer_polish_followups.md` "Mockup Cleanup" routing once a look is locked.

---

[X] restrict zoom on buttons

---

bake in map region callouts to geojson

---

make the logos a max size. 
as we zoom out these logos take up more and more map space. they need to max out at "park" size and not grow much more at region level.

we need a slider under these images to adjust this and a export button so that I can tweak and return back settings to you.

----

bake buildings in park

exclude buildings in region. - do not allow them to be searched. 

---

zoom is not immedeatly responsive. if we touch two fingers immedeatly pinch zoom tends to not start.
if we finger one down then finger two down the gesture seemns to register and zoom works consistantly

---

figure out what the "X published features is doing"
can we drop it?

---

remove the trail dots. artifact of past dev workflow. golden trail data have numbers tied to the trail.

---

searching for trail 1 works. 
1X should show up in the results for trail 1

---

[] verify: calendar event page should auto scroll to time

make the non scrolling section of the calendar (top) scroll with the bottom bit. -- this non scrolling behavior caused a height discrepency while changing tabs. they should all be the same after we do this.

---

fix park zoom level. 
region is good, park zoom level has same zoom as region. it should be tighter.

---

topo lines are too dark. 
we need a mockup with multiple colors

disable osm trails only use gold derived trails

use blue green black trails on map view.
turn them on by default on map view

make trails orange on topo view.

---

fix hot spot trails button. 
it does not work on first click.
it works if you use the next event button first.
then the hot spot works.

the hot spot should be a toggle. clicking it a second time will turn them off.

we need a second visual button state for this.

---

drawer behavior is inconsistant after collapse of edit sidebar. --- math is not being computed and the drower offset is not under the user finger

---

put end date on event calendar.
it goes event name start date.
should be 
event name  start date - end date.

---

on tall phones or wide monitors our 9 patch is not enough coverage to not see the edges of the map. 
we need to extend the 9 patch to ~bigger.

---
review our icons and ensure they all have similar line weights. 

---

the bottom left icon expanded content overflows the edit button.
it should give it some breathing room. 

---

satalite view needs a better tree icon

---

the icon groups at the top
 
3 4 1, used to be all the same width when it was  3 3 1 

now that we have 4 in the second group that group is tight.

---



## iOS bottom padding (home indicator) — RESOLVED 2026-05-30

Symptom: installed iOS PWA showed a dead band of flat-cream space below the
bottom floating cards (`.panel` "AOP edit panel" + `.message` "N publish
features loaded.").

Cause: the cards reserved the full `env(safe-area-inset-bottom)` (~34px home
indicator) as empty space beneath them. The band reads as flat cream because the
body background (`#efe7d5`) shows wherever the map doesn't paint under the
indicator on a real device.

Fix (`website/index.html`, `@media (max-width:760px)`): pull the cards to a
minimal margin instead of clearing the full inset.
- `.message` → `bottom: 8px` (non-interactive status pill; allowed to graze the
  gesture zone).
- `.panel` → `bottom: calc(8px + 44px)` = 52px (interactive editor, so it stays
  clear of the ~34px indicator).
Verified with Playwright at 393×852 + a simulated 34px inset: gap below the
message = 8px at both 0 and 34px insets, 0 console errors. Superseded the prior
`max(12px, var(--sa-bottom))` "v5" approach.

Second fix — cream bar under the home indicator (separate from the card
positions). Pulling the cards down did NOT clear it. Root cause: on a real iOS
standalone PWA the map's `position:fixed; inset:0` container's `bottom:0` lands
ABOVE the home indicator and/or MapLibre sized the canvas before iOS finalized
the standalone viewport, so the cream `body`/`#map` background shows in the band.
Chromium can't reproduce it (canvas == container == innerHeight, bottom strip
renders map terrain not cream), so it's iOS-standalone-specific. Two-part fix in
`website/index.html`:
- CSS: `#map { position: fixed; inset: 0; height: 100vh; height: 100dvh; }` —
  the explicit dynamic-viewport height forces the container to full screen even
  when `inset:0`'s bottom is short (dvh overrides vh where supported; vh is the
  fallback for older iOS).
- JS: new `resyncViewport()` calls `map.resize()` on `resize`,
  `orientationchange` (250ms deferred), `pageshow`, and `visualViewport` resize.
  The old handler only repositioned the search dropdown and never resized the
  map, so a late iOS viewport change left the canvas short.
Verified in Chromium: growing the viewport 852→900 now drives the canvas height
to match (was static before), 0 console/page errors. Needs on-device confirm. If
a cream band STILL shows after this, the remaining suspect is map data-coverage
(camera panned past the raster bounds → `#efe7d5` background layer), which is a
different fix (extend data / change background-layer colour), not safe-area.

iOS 26 note (the "home row thing" the user noticed): iOS 26 / iPadOS 26 made the
Home indicator AUTO-HIDE — it fades after you switch into an app and only returns
on a deliberate bottom swipe (pre-26 it stayed visible). This is VISUAL ONLY: the
gesture zone and `env(safe-area-inset-bottom)` (~34px on Face ID iPhones) are
UNCHANGED. So reserving that inset as empty space looks worse now that the bar
usually isn't even drawn — which is why pulling the cards down is correct.
Refs: reverttosaved.com "The quiet exit of the Home indicator in iOS 26 and
iPadOS 26" (2025-06-13); DEV "Make Your PWAs Look Handsome on iOS".