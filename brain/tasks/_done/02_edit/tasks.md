1) search should be able to search tags.
2) collapse calendar on mobile / narrow widths automatically

make edit panel pop up from the bottom right. 
on mobile when collapsed its floating in the middle.

[] expand calendar on large screens

make buildings show up by default
prune buildings outside of bounds ???


come up with a list of always on. 
[] ON ALL LAYERS
-buildings
-water
-road


sometimes
bottom layer
topo
trails
waypoints

figure out who/what each view is for
tighten in on their needs.

our region circle callouts need to be positionable 

calendar needs time
[] scroll to current calendar item 

one view needs trails by default.
[] Improve view

need a dedicated hot button on the left.
fire icon???

magnifing glass on search

ability to search tags


layers need text tweaking.
currently trace has text hard to read.

[] css needs a review top to bottom
[] theme. review


[] code needs a review for smells.


we need a editor for points of intrest.

[] invert all collapse icons on right toolbar
[] fix styles on 

section headeader
<button type="button" class="section-toggle" aria-expanded="false">
    <span class="section-chevron">▾</span>
</button>

*buttons dont have the same border treatment as the other collapse icons.
we want all buttons to be uniform in style and format. only thing that can be different is icon or color.


[] see if we can get trail names they are numbered

tag cabins
tag campsites
tag pavillion bathrooms


tag excavator hill
tag big log
tag jeep entrance
tag buggy entrance

[] add aop logo

[] add rock warblers logo

figure out how much data the site takes
figure out how to reduce that amount
figure out how to cache it ~harder?

figure out how to do offline apps?
progressive web app???

-----

New tasks

when following a link from the calendar the item is selected and a tooltip pops up. this is good. however there is overlap on some screens. 

we need to make sure that we scroll to make tehe tooltip in view.

[] hot coming up being a calendar notification does not make sense....
I think hot should be only activate the heatmap 

[] ability to edit size on images.
[] document workflow for adding images.

-----

## Status index (do not edit dump lines above)

Per `../../../ai_rules/preserve_card_directives.md`, the user-written `[]` lines
above stay verbatim. This index records the current status of each one and
points at the card that owns the truth. Read the owning card before treating
any line as still-open.

| Dump line | Status | Owning card |
| --- | --- | --- |
| `[] expand calendar on large screens` | shipped | `../../03_event_app/_done/viewer_polish_carryover.md` (Lane 2) |
| `[] ON ALL LAYERS` (buildings / water / road audit) | shipped | `../../03_event_app/_done/viewer_polish_carryover.md` (Lane 4) — table in `../../../research/viewer.md` |
| `[] scroll to current calendar item` | shipped | `../../03_event_app/_done/viewer_polish_carryover.md` (Lane 2) |
| `[] Improve view` (trails-default view) | shipped | `_done/preset_persona_review.md` |
| `[] css needs a review top to bottom` | partial, S4 leftovers | `../04_event_app/viewer_polish_followups.md`; audit card archived at `../../03_event_app/_done/code_health_pass_4.md` |
| `[] theme. review` | partial, S4 leftovers | `../04_event_app/viewer_polish_followups.md`; audit card archived at `../../03_event_app/_done/code_health_pass_4.md` |
| `[] code needs a review for smells.` | partial, S4 leftovers | `../04_event_app/viewer_polish_followups.md`; audit card archived at `../../03_event_app/_done/code_health_pass_4.md` |
| `[] invert all collapse icons on right toolbar` | shipped | `../../03_event_app/_done/viewer_polish_carryover.md` (Lane 3) |
| `[] fix styles on` (section-toggle chevron) | shipped | `../../03_event_app/_done/viewer_polish_carryover.md` (Lane 3) |
| `[] see if we can get trail names they are numbered` | open (research) | `../../01_mvp/_done/community_trails_import.md` |
| `[] add aop logo` | shipped | `_done/branding.md` |
| `[] add rock warblers logo` | shipped | `_done/branding.md` |
| `[] hot coming up being a calendar notification does not make sense....` | shipped | `_done/hot_control_two_lane.md` |
| `[] ability to edit size on images.` | shipped | `../../03_event_app/_done/viewer_polish_carryover.md` (Lane 5) — `_done/branding.md` "Sprint 03 Follow-up Shipped" |
| `[] document workflow for adding images.` | shipped | `../../../spinup/add_image_to_viewer.md` |

Non-`[]` directives in the dump (free-form lines) are out of scope for this
index; they routed through the Sprint 02 triage in `_readme.md` and the
Sprint 03 carryover.
