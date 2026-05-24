# AOP Map Personas

TL;DR:
- Personas are a map-decision filter, not marketing copy.
- The shared job is simple: help the right person find the right place at the right time, with enough source context to act.
- Registration, payment, waivers, scoring, sponsor packets, shirt orders, and full rules live outside the map unless they change where someone goes.

#aop #personas #northstar #views #events

-----

## Source chain

- `whats_this_for.md`
- `map_northstar.md`
- `source_register.md`
- `validation_loop.md`

## How to use this

When a view, default layer, schedule row, search tag, popup, print board, or hot-button state is debated, ask:

> What is this person trying to decide right now, and what map evidence helps them decide it?

The map should answer:

- Where am I?
- Where do I go next?
- What is happening there, and when?
- What is allowed or required there?
- What can I still use if cell service fails?
- Is this official, observed, inferred, draft, or planning context?

The map should not become event-management software. It can link out to forms and rules; it should carry location, time, status, and source-backed map facts.

## Primary Personas

### Driver

The driver is the center of gravity for the park map. Before arrival they need the address, registration/check-in, schedule, rig/class context, and offline access. On course they need trails or stages, trailheads, gates, hazards, terrain, water, bathrooms, first aid, and the next session location.

Map response: Park and Topo views, trails on in Park, event schedule anchors, `#registration`, `#pavilion`, `#trailhead`, `#night-run`, and a printable driver briefing.

Do not bury drivers in raw evidence layers. They need the best current map, with uncertainty visible where it affects a decision.

### Trail Buddy / Marshal

The trail buddy or marshal works during a stage. They need one stage at a time: start, finish, ordered gates, mandatory skills, marshal post, boundary, penalty notes, emergency contact, nearest first aid, and where to report.

Map response: a Stage / Marshal view or print handout, with gate labels and emergency tags. Topo helps, but terrain is not enough without event geometry.

Do not make them interpret a general-purpose layer stack while walking the course.

### Host / AOP Staff / Event Organizer

Staff and organizers need to plan, operate, and validate the map. They care about facility layout, property bounds, roads, staging, parking, vendor areas, camping, cabins, RV sites, bathrooms, first aid, closures, capacities, source confidence, and publishability.

Map response: Trace for drawing and comparison, a future Review / Validation view for source decisions, the feature list panel, taggable buildings/POIs, event-status filters, and the print-board validation loop.

Do not hide provenance from this persona. Their job is to decide what is true enough to publish.

### First-Time Visitor / Spectator / Family

This person needs low-friction event-day wayfinding. They need parking, check-in, pavilion, what is happening now, where they can stand, bathrooms, first aid, food/vendor points, awards, raffle, weather shelter, and basic park rules.

Map response: Pavilion / Event HQ surface, calendar rows tied to tags, hot button, amenity icons, spectator-safe zones, and support-town context.

Do not expose them to tracing layers, raw GPX, or ambiguous internal labels unless clearly marked as evidence.

### Event Crew / Vendor / Sponsor

These users arrive with a job. Volunteers need check-in, shift windows, assigned post, staff route, and emergency process. Vendors need load-in route, pad/booth, power, water, trash, service hours, and contact. Sponsors need booth/logo placement, raffle or award handoff, ceremony time, and external signup context.

Map response: role-filtered event layer, load-in sheet, volunteer handout, vendor zone, sponsor/raffle/awards points, and clear external links.

Do not create empty role presets before the pads, routes, posts, and permissions are confirmed.

### Kid Crawl / Beginner Family

This group needs a beginner-safe route or zone, start time, age or supervision notes, parent/spectator boundary, bathrooms, shade/water, and awards location.

Map response: kid-crawl route or zone, safe boundary styling, schedule row, beginner labels, and a parent-friendly handout.

Do not imply a route is kid-safe until AOP or event staff confirms it.

### Out-of-Town Visitor

This person is planning the trip or a supply run. They need regional orientation, park address, main roads, lodging, camping, cabins, RV sites, grocery, fuel, restaurants, and directions.

Map response: Region / Approach view, visitor context callouts, confirmed AOP lodging/camping points, and external links for directions and services.

Do not show the dense driver layer stack by default at regional scale.

## Surface Implications

| Surface | Primary users | First job | Default posture |
| --- | --- | --- | --- |
| Region / Approach | Out-of-town visitors, vendors, sponsors, first-timers | Understand where AOP sits and how to arrive | Roads, boundary, address/directions, visitor context, confirmed lodging/camping/fuel |
| Park | Drivers, visitors, AOP staff | Read the whole property | Boundary, roads, land cover, buildings/amenities, trailheads, trails, named POIs |
| Pavilion / Event HQ | Event-day visitors, families, volunteers | Find the main event hub | Pavilion, registration/check-in, bathrooms, food/vendor, awards/raffle, nearby parking, calendar |
| Topo | Drivers, stage designers, marshals | Read terrain and route difficulty | Park payload plus hillshade, contours, water, springs, hazards/obstacles |
| Trace | Map editor, curator, AOP staff | Compare evidence and draw/verify features | Imagery, SFWDA paper map, OSM tracks, buildings, raw/reference layers |
| Review / Validation | AOP staff, map curator | Decide what can publish | Publishable layers, source/confidence/status, observations, unresolved questions |
| Event calendar | Drivers, spectators, families, volunteers | Know what happens when and where | Time, title, location tag, status, popup, fly-to |
| Left hot button | Everyone on-site during an event | Jump to the live or next useful thing | Live/imminent session first, next session second, activity evidence only when no schedule target exists |
| Activity heatmap | Drivers, staff, reviewers | See where activity evidence clusters | Raw or aggregated evidence, labeled by source/recency/confidence; not "live crowding" unless backed by live/recent aggregate data |
| Print board / handout | Drivers, marshals, AOP staff | Navigate and validate without signal | Course/stage view, grid, trail IDs, source/confidence, emergency info, QR to web map |

## Layer Rules

| Layer group | Default rule | Reason |
| --- | --- | --- |
| Boundary, roads, base land cover | Always on | Orientation comes first for every persona. |
| Buildings, amenities, trailheads, named POIs | On once verified | These answer "where do I go?" |
| Water, first aid, bathrooms, parking, camping | On once verified | Utility and safety layers should not be hidden. |
| Trails | On in Park and Topo; simplified or off in Region | Drivers need trails; regional visitors need less clutter. |
| Event POIs/routes | On when event context is selected | Event facts are time-bound and can mislead outside event windows. |
| Raw evidence layers | Off by default | SFWDA, OSM, imagery, lidar indexes, raw GPX, and tracing sources are for curation or review. |

## Open Map Questions

- Official facilities: bathrooms, porta-potties, first aid, RV sites, cabins, campsites, trash, water, power, and parking.
- Event operations: spectator-safe areas, vendor pads, volunteer posts, sponsor booth, awards, raffle, kid crawl, night run, stage boundaries, gates, and mandatory skills.
- Trail truth: trail names, difficulty, class suitability, hazards, source confidence, and last validation date.
- Rules and policies: dogs, camping, bonfire, vendor rules, emergency procedure, and cell reception.
- Offline: drivers, marshals, volunteers, and vendors need a usable path when signal fails.
- Scope boundary: payment, waiver, scoring, sponsorship, merch, and complete rules packets should link out unless location or status belongs on the map.
