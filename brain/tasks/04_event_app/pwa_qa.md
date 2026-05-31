bottom row items should all fit on one horizontal row.
make a few mockups to compare this. minimal. 

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

all comparison mockups should be put on the right sidebar with a link the the item to look at. I will review and pull attributes from each different column.

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

iOS 26 note (the "home row thing" the user noticed): iOS 26 / iPadOS 26 made the
Home indicator AUTO-HIDE — it fades after you switch into an app and only returns
on a deliberate bottom swipe (pre-26 it stayed visible). This is VISUAL ONLY: the
gesture zone and `env(safe-area-inset-bottom)` (~34px on Face ID iPhones) are
UNCHANGED. So reserving that inset as empty space looks worse now that the bar
usually isn't even drawn — which is why pulling the cards down is correct.
Refs: reverttosaved.com "The quiet exit of the Home indicator in iOS 26 and
iPadOS 26" (2025-06-13); DEV "Make Your PWAs Look Handsome on iOS".