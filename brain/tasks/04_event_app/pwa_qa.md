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