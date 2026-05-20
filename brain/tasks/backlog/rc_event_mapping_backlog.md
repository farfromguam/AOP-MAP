# RC Event Mapping Backlog

AOP hosts RC crawling events. The map has to draw them. This card pulls the actual shapes used by the established event formats -- Recon G6, Pro-Line By The Fire, and gate-based comp classes -- and decides what the AOP map needs to support.

Earlier backlog cards treated "events" as Out under the wrong assumption that AOP is trail-riding only. That call is reversed. Events sit on the same data spine as trails and observations -- a stage, a gate, and a checkpoint are map features with source, confidence, permission, and verification, just like a trail centerline.

-----

## Source

- Recon G6 format: https://www.axialadventure.com/axi-blog-archive-what-is-a-recon-g6.html and https://kingofthehammers.com/what-is-an-axial-recon-g6/
- Pro-Line By The Fire: https://www.prolineracing.com/bythefire.html and https://www.prolineracing.com/events/pro-line-by-the-fire.asp
- Comp-class scoring and gate widths: https://rcspotters.com/getting-started-with-rc-crawler-competition-and-the-different-classes/, https://www.canyonrc.com/competition-rules, https://www.wercrock.com/rules
- `./scribblemaps_feature_review.md`, `./rcmap_feature_review.md`, `./scaletra_feature_review.md` -- prior backlog cards being corrected.

Captured 2026-05-20.


## Event formats AOP plausibly hosts

### Recon G6-style scale rally
- Stage-based. Typically 2-4 stages per event.
- Each stage contains numbered gates a driver must pass in order, plus mandatory skills sections with an entrance and exit.
- Stage boundaries are real. Crossing them is a penalty.
- Timed. Penalties for hitting gates or boundaries. Winching, recovery, and reverses are not penalized.
- Spirit: rally + European truck trial + Camel Trophy.

### Pro-Line By The Fire-style multi-day adventure
- Day-loop format: "Cloverleaf" loops radiating from a central staging area.
- Secondary activities layered on top of the loops: GeoCache treasure hunt waypoints, photo scavenge waypoints, "Into The Night" dusk-run route.
- Competitive sub-events held inside the same footprint: Proving Grounds, Scale Trials, Mega Mud Truck Challenge, Sumo-Wars.
- Camping zones, food vendor area, registration / wristband check, parking.

### Comp-class gate course
- 4-6 courses per class.
- Class structure: Street / Weekend Warrior / Outlaw (or AOP's equivalent).
- Numbered gates with explicit minimum widths (commonly 11" or 12" per class).
- Penalty scoring: rolls, reverses, missed gates, gate touches. Lowest score wins.
- "Free for all" timing window: drivers pick course order inside an event window.


## Map features the event layer needs

### Stages
**Fit:** V1 fit. A stage is a named polygon (or polyline + corridor) with start, finish, and a boundary. Print board has to show stages clearly; public viewer toggles them on during event windows.

### Gates
**Fit:** V1 fit. Numbered point features with order, width, class applicability, and entry/exit direction. Width matters -- 11" vs 12" is a class-defining detail and must be carried as a real attribute, not free-text.

### Mandatory skills sections
**Fit:** V1 fit. A bounded sub-feature inside a stage, with explicit entrance and exit. The print board needs these called out; the legend needs a symbol for them.

### Course start / finish / checkpoints
**Fit:** V1 fit. Same shape as gates but tagged differently. Start and finish are not just "gate 1" and "gate N" -- they have rules attached.

### Day loops (Cloverleaf-style)
**Fit:** V1 fit. Polyline routes anchored at a central staging area, tagged by day and difficulty. Should publish to print and web with the same `source` / `permission` discipline as trails.

### GeoCache / photo scavenge waypoints
**Fit:** V1 fit (during events) / V2 fit (between events). Points with description, hint, and answer/proof type. Treat answers as restricted material -- a published map should not spoil an active geocache.

### Dusk-run / night-run routes
**Fit:** V1 fit. Same shape as day loops but tagged for low-light conditions and any extra hazards.

### Staging / registration / wristband check
**Fit:** V1 fit. Point features on the print board and public viewer; wristband-check location is a real wayfinding need.

### Camping zones
**Fit:** V1 fit. Polygon zones with capacity notes if AOP wants them; first-come tagging where applicable.

### Food vendor / hours
**Fit:** V1 fit (small). Point feature with hours of operation. Hours belong as an attribute, not in a sidebar.

### Parking
**Fit:** V1 fit. Polygon zones, possibly split by vehicle size or class.


## Event-data shape (data spine)

### Event as a first-class object
**Fit:** V1 fit. PostGIS spine should have an `events` table joined to features by event id. A gate or stage is not free-floating; it belongs to an event instance. Old events should not disappear -- past events are evidence of what AOP has hosted.

### Event date / window / status
**Fit:** V1 fit. `start_at`, `end_at`, `status` (`announced`, `registration_open`, `live`, `closed`, `archived`). The public viewer toggles event layers by status.

### Registration link (external)
**Fit:** V1 fit (small). Single URL field on the event row; the map links out, it does not register people. No ticketing or payment surface.

### Class-by-class course assignment
**Fit:** V1 fit. A gate or course belongs to one or more classes (Street / Weekend Warrior / Outlaw / AOP's own). Class is a tag on the feature, not a separate layer.

### Scoring rules per event
**Fit:** V2 fit. Penalty tables, time bonuses, class-by-class scoring -- this is event-software territory. The map should carry course geometry and references, not score runs.


## Print considerations

### Course / stage handout map
**Fit:** V1 fit. The same print spine that produces the trail board should produce per-event handouts (a single stage on one sheet, a Cloverleaf loop on another). One layout file per event template, not per event.

### Driver briefing pack
**Fit:** V1 fit. PDF bundle: stage maps, mandatory skills locations, class gate widths, scoring summary, emergency / wrangler contact. Generated from the same data, not maintained as a separate document.


## What this card intentionally does not turn into work

- A registration / ticketing / waiver system. AOP can use existing event platforms; the map links out.
- A live scoring / penalty-tracking app. Event-software territory.
- Spectator broadcast or live-tracking. Not the map's job.
- A general-purpose event editor open to non-AOP organizers. The events live on AOP land; AOP staff curates them.


## What to do with this card

- Add an `events` table and `event_features` join to the PostGIS spine when the first real AOP event is on the calendar.
- Extend the layer schema in the build card so gates carry width, class, and order; stages carry start/finish/boundary; mandatory skills sections carry entrance/exit.
- Add an event-status filter to the public viewer when V1 ships.
- Treat the Pro-Line By The Fire and Recon G6 documentation as a vocabulary reference, not a copy target. AOP's events will have their own shape; the map should not force them to match someone else's format.
