# Personas

TL;DR:
- This is a decision tool for map views, defaults, schedule rows, search tags, and print handouts.
- The through-line is not "put every event detail on the site." It is "help each person find the right place at the right time, with enough context to act."
- Registration, costs, shirts, sponsorship packets, and forms link out unless they change where somebody goes.

#aop #personas #views #events #02_edit

-----

## Source chain

- `../../northstar/whats_this_for.md`
- `../../northstar/map_northstar.md`
- `../01_mvp/event_schedule_layer.md`
- `../01_mvp/visitor_context_callouts.md`
- `../backlog/rc_event_mapping_backlog.md`
- `_readme.md`
- `tasks.md`

## What this is getting at

The personas are a filter for the map.

Not marketing personas. Not "content strategy." The practical question is:

> When this person opens the map, what are they trying to decide, and what layers, tags, schedule rows, popups, or print views help them decide it?

The shared questions:

- Where am I?
- Where do I go next?
- What is happening there, and when?
- What is allowed or required there?
- What can I do if I lose cell signal?
- Is this official, observed, draft, or just planning context?

The map serves event information, but it should not become event software.
Payment, waivers, scoring, sponsorship CRM, shirt orders, and ticketing belong
outside the map. The map can link to them.

## User-needs matrix

| User | Moment | They need | Map response | Current holes |
| --- | --- | --- | --- | --- |
| Driver | Before arrival, check-in, on course | Schedule, registration/check-in location, class/rules, trail or stage route, trailheads, gates, hazards, water, bathrooms, first aid, night-run route, offline access | Park view with trails default-on; Topo view for terrain; event overlay for stages/gates; tags like `#registration`, `#pavilion`, `#trailhead`, `#night-run`; downloadable/print driver briefing | Real trail names; verified trail difficulty; official class/rules; emergency plan; cell coverage; confirmed night-run geometry |
| Trail buddy / marshal | During stage | Ordered gates, stage boundary, penalty notes, mandatory skills, start/finish, emergency contact, nearest first aid, where to report | Stage handout or event layer; gate labels; marshal points; first-aid/emergency tags; simple print view that works while walking | Marshal assignments; checkpoint locations; radio/contact plan; official penalty language |
| Host / AOP staff / event organizer | Planning and live ops | Facility layout, property bounds, roads, staging, parking, vendor area, camping, cabins, RV sites, bathrooms, first aid, closures, source confidence, what is publishable | Internal/editing view; feature list panel; taggable buildings/POIs; source/confidence styling; event-status filters; print-board validation loop | Official facility inventory; capacities; permission to publish named features; official closure/status vocabulary |
| First-time visitor / spectator / family | Arrival and event day | Where to park, where to stand, what is happening now, pavilion/check-in, awards, raffle, food, bathrooms, first aid, dogs/rules, weather shelter | Pavilion zoom; "what's happening now" hot button; calendar rows tied to map tags; spectator-safe zones; amenity icons; support-town callouts | Spectator-safe areas; dog policy; weather/shelter plan; awards/raffle locations; first-aid point |
| Volunteer | Before shift and during shift | Arrival time, check-in, assigned post, task notes, parking, staff-only route, emergency process | Volunteer layer or filtered event handout; `#volunteer-checkin`; post markers; quick directions from parking to assignment | Volunteer role list; shift windows; staff-only notes vs public notes; emergency procedure |
| Vendor / food truck operator | Load-in, setup, service, teardown | Arrival window, gate/route, booth or truck pad, power/water/trash, service hours, registration/vendor contact, cell reception | Vendor zone polygon; load-in route; vendor POIs; hours in popup; print/load-in sheet | Vendor packet; exact pads; power/water availability; trash plan; sales rules; cell coverage |
| Sponsor | Before event and event day | Sponsor signup link, booth/logo placement, raffle/giveaway handoff, award ceremony time/location, brand visibility | Sponsor/raffle/awards points; external signup link; logo placement only after AOP permission | Sponsorship package; raffle shipping/drop-off workflow; logo permissions; booth/signage rules |
| Kid crawl / beginner family | Event day | Beginner course, age/supervision notes, start time, safe viewing, bathrooms, shade/water, awards | Kid-crawl route or zone; parent/spectator boundary; schedule row; beginner-friendly labels | Whether kid crawl exists; age/supervision rules; safe boundaries; capacity; awards location |
| Out-of-town visitor | Before trip and supply run | Hotels, campsites, cabins, RV sites, restaurants, grocery, fuel, park address, regional orientation | Region view; visitor context callouts; official AOP lodging/camping points; external links for food/lodging/directions | Confirmed 8 RV sites and 4 cabins; campsite inventory; grocery/fuel list; lodging partners |

## View implications

| Surface | Primary users | First job | Default payload | Open call |
| --- | --- | --- | --- | --- |
| Region zoom | Out-of-town visitors, vendors, sponsors, first-timers | Understand where AOP sits and how to get support nearby | Park boundary, roads, support-town callouts, address/directions, maybe lodging/camping links | Keep dense trail detail off by default here unless the user asks for it |
| Park zoom / Park preset | Drivers, visitors, AOP staff | Read the whole property | Boundary, roads, land cover, buildings/amenities, trailheads, trails, named POIs | This is the likely answer to "one view needs trails by default" |
| Pavilion zoom | Event-day users | Find check-in, schedule anchors, awards, food, bathrooms, first aid | Pavilion, registration/check-in, vendor/food, bathrooms, awards/raffle, nearby parking, calendar | Needs official amenity points and event ops locations |
| Topo preset | Drivers, stage designers, marshals | Read terrain and route difficulty | Trails, contours, hillshade, water, trailheads, hazards/obstacles | Needs difficulty/rating vocabulary and verified trail geometry |
| Trace preset | Map editor, curator, AOP staff | Compare evidence and draw/verify features | Imagery, SFWDA paper map, OSM tracks, buildings, raw/reference layers | Keep out of normal visitor default; this is workbench mode |
| Event calendar | Drivers, spectators, families, volunteers | Know what happens when and where | Time, title, location tag, route tag, popup, fly-to | Needs official schedule, status, and AOP approval |
| Left hot button | Everyone on-site during an event | Jump to the live need | **Decided 2026-05-23:** dynamic, three states. **(1) Hot now:** a session is live OR starts within **30 minutes** (`imminent_window = 30 min`) → button glows, jumps to that session's tag-resolved location. **(2) Coming up:** no session is imminent but one is on the schedule (look-ahead across days — Friday should already surface a Saturday evening session) → button points at the next session and shows the countdown, no "live" glow. **(3) Heatmap fallback:** schedule is empty or all past → button surfaces the trail-activity heatmap (`mvp/scripts/build_activity_hotspots.py` output) so it still answers "where is the park hot right now." Demo posture for development: today is Saturday (matches the current brain date 2026-05-23). | Icon should track the three states (hot-glow, coming-up, heatmap); how to surface the countdown in chrome |
| Print board / handout | Drivers, trail buddies, AOP staff | Navigate and validate without relying on signal | Course/stage view, grid, trail IDs, source/confidence, emergency info, QR to web map | Needs exact printable scales and event templates |

## Default-layer rule of thumb

Candidate policy, not locked:

| Layer group | Default | Why |
| --- | --- | --- |
| Boundary, roads, base land cover | Always on | Almost every user needs orientation first |
| Buildings, amenities, trailheads, named POIs | Always on once verified | They answer "where do I go?" |
| Water, first aid, bathrooms, parking, camping | Always on once verified | They are utility/safety layers, not optional trivia |
| Trails | On in Park and Topo; off or simplified in Region | Drivers need them; first-time regional context can get cluttered |
| Event schedule POIs/routes | Off until event context is selected, then sticky | Event layers are time-bound and can mislead outside event windows |
| Raw evidence layers | Off by default | SFWDA, OSM, imagery, lidar indexes, and tracing sources are for curation |

## Holes to close

- **Priority order.** Driver is the center of gravity, but event day pulls hard toward spectator, volunteer, vendor, and sponsor needs. Decide which surface wins when the UI is crowded.
- **Official facilities.** Pavilion is known. Bathrooms, porta-potties, first aid, RV sites, cabins, campsites, trash, water, power, and parking need confirmed points or zones.
- **Rules and policies.** Dogs, bonfire, camping rules, vendor rules, emergency procedure, and cell reception are not mapped yet.
- **Event truth.** Registration deadline, cost, sponsor/vendor signup, vendor arrival, raffle/giveaway process, awards schedule, food hours, and t-shirts need owners and official sources.
- **Spatial event features.** Kids crawl, night run, spectator areas, vendor pads, parking, stage boundaries, gates, and mandatory skills sections need geometry.
- **Trail truth.** Trail names, difficulty, class suitability, hazards, and source confidence are still the big map hole.
- **Offline.** This persona pass strengthens the offline case. Drivers, marshals, volunteers, and vendors all need a map that survives bad signal.
- **Scope boundary.** The map should link out for payment, waiver, sponsor/vendor forms, shirt orders, and full rules packets. It should only carry the location, time, status, and source-backed map facts.

## Next pass

- Turn the holes above into an AOP question list.
- Use `views_and_defaults.md` to ship the layer-default changes.
- Decide the left hot button by user moment, not icon first.
- Keep adding real feature tags as locations are confirmed: `#registration`, `#pavilion`, `#bathrooms`, `#first-aid`, `#vendor`, `#raffle`, `#awards`, `#kids-crawl`, `#night-run`.
