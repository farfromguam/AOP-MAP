# Preset Persona Review

TL;DR:
- Park / Topo / Trace are now pointed in the right direction.
- They meet drivers, visitors, and editors better than before.
- They do not fully meet event-day operations yet: spectator, volunteer, vendor, sponsor, marshal, and kid-crawl needs need event/facility data plus one or two new view concepts.

#aop #presets #personas #views #02_edit

-----

## Reviewed

- `personas.md`
- `views_and_defaults.md`
- `left_hot_button.md`
- `../../research/viewer.md`
- `website/index.html`

Surfaces reviewed:

| Surface | Type | Current job |
| --- | --- | --- |
| Park | Layer preset | Default visitor / driver map |
| Topo | Layer preset | Terrain-reading map |
| Trace | Layer preset | Source-review / tracing workbench |
| 3D | Independent terrain toggle | Relief view layered onto any preset |
| Region | Camera preset | Fit the 9-patch region |
| Park | Camera preset | Fit the park boundary |
| Pavilion | Camera preset | Jump to the 1010 Ellis Cove Rd pavilion building |
| Event calendar | Time surface | Select a session, turn on event POIs/routes, fly to the tag |
| Hot button | Time/action surface | Jump to live/imminent/next session or fallback activity hotspot |

## Verdict

The three layer presets are no longer the main problem.

`Park` now serves the normal driver / visitor job: trails, trailheads, roads,
boundary, land cover, support callouts, in-park buildings, water, and drawn POIs.

`Topo` serves drivers, stage designers, and marshals who need terrain: Park plus
hillshade, contours, water, and springs.

`Trace` serves the editor / curator job: imagery, SFWDA paper map, OSM tracks,
OSM service roads, buildings, publish layers, and drawn POIs.

The gap is that several personas are not just "map readers." They are event-day
operators. They need role-specific event/facility layers that do not exist yet.

## Persona fit

| Persona | Best current surface | Fit | Gap | Improve |
| --- | --- | --- | --- | --- |
| Driver | Park, Topo, calendar, hot button | Good base map, partial event map | Trail names, difficulty, official stage/course geometry, gates, first aid, offline | Add event stages/gates/skills, confirmed hazards, driver briefing export |
| Trail buddy / marshal | Topo, print board concept | Partial | No stage boundary, ordered gates, marshal post, emergency contact, penalty notes | Add Stage / Marshal event view and print template |
| Host / AOP staff / event organizer | Trace, feature list panel, editor | Partial | No dedicated validation/source-confidence preset; no official facility inventory; no event-status filter surface | Add Review / Validation view or saved internal preset once source fields are richer |
| First-time visitor / spectator / family | Pavilion camera, calendar, hot button, Park | Partial | No spectator-safe zones, bathrooms, first aid, parking, awards, raffle, dog/weather info | Add Event HQ view after amenities are confirmed |
| Volunteer | Calendar / hot button | Weak | No shift post, volunteer check-in, staff-only route, emergency process | Add volunteer handout or role-filtered event layer |
| Vendor / food truck operator | Region camera, roads, Park | Weak | No load-in route, pad/booth zone, power/water/trash, vendor arrival window | Add Vendor Load-In sheet or event ops layer |
| Sponsor | Calendar / Pavilion | Weak | No booth/logo placement, raffle handoff, awards location, sponsorship link context | Add sponsor/booth/raffle points once AOP confirms |
| Kid crawl / beginner family | Calendar / Park | Weak | No kid-crawl route, parent boundary, supervision rules, beginner-safe area | Add kids-crawl event feature type and safe-zone styling |
| Out-of-town visitor | Region camera, visitor callouts | Partial | Region is camera-only, so it keeps dense Park layers; lodging/camping inventory not confirmed | Add Approach / Region layer preset or make a clearly labeled "Approach" mode |

## What is working

- **Park is the right default.** It now turns on buildings and water, which
  closes the biggest mismatch from `personas.md`.
- **Topo has the right audience.** It is the terrain/course-planning view. Keep
  it dense enough for drivers and stage designers.
- **Trace is correctly not visitor-facing.** It carries raw evidence and
  source-review layers. Keeping visitor context off here is right.
- **Calendar and hot button cover temporal navigation.** This matters for
  spectators, volunteers, and drivers because "what is happening now?" is not a
  static layer question.
- **Camera presets are useful, but distinct.** Region / Park / Pavilion are
  movement controls, not layer presets. That split is okay, but the duplicated
  word "Park" remains cognitively noisy.

## Main holes

### 1. No Approach / Region layer preset

The `Region` button only moves the camera. It does not simplify the layer set.
That means an out-of-town visitor can zoom out but still see the driver-focused
Park payload.

Better shape:

| Candidate | Layers |
| --- | --- |
| Approach | roads, park boundary, visitor context callouts, address/directions, camping/lodging/fuel links, maybe parking |

Do not silently make the existing `Region` zoom button alter layers unless the
control is renamed. A camera button that changes the layer stack will surprise
people.

### 2. No Event HQ view

The Pavilion camera preset gets the user to the right place, but it does not
load a role-specific event payload.

Event-day users need:

- registration / check-in
- bathrooms / porta-potties
- first aid
- parking
- vendor / food
- awards
- raffle
- spectator-safe areas
- volunteer check-in

Most of those data points are not confirmed yet. Once they exist, add an
`Event HQ` layer preset or a combined action that applies the event layer stack
and flies to Pavilion.

### 3. No Stage / Marshal view

Topo is close, but marshals need event geometry, not just terrain:

- one stage at a time
- start / finish
- ordered gates
- mandatory skills sections
- stage boundary
- marshal post
- first aid / emergency contact
- print-friendly handout

This should probably be a print/export template first, then a web preset.

### 4. No internal Review preset

Trace is a source workbench, but AOP staff also need a validation view:

- publishable layers
- source/confidence/status
- observations
- raw evidence only where it explains uncertainty
- questions still open

That is not the same as Trace. Trace says "draw and compare." Review says
"decide what is true enough to publish."

### 5. Role operations are data-blocked

Vendor, volunteer, sponsor, and kid-crawl views are not blocked by UI. They are
blocked by missing event facts and geometry:

- vendor pad / load-in route / power / water / trash
- volunteer check-in / shift posts / staff-only notes
- sponsor booth / logo / raffle handoff
- kid-crawl route / parent boundary / supervision rules
- spectator-safe areas

Do not add empty role presets before these exist. They would be buttons with no
promise behind them.

## Recommended improvements

### Now

- Keep Park / Topo / Trace as the only layer presets until event/facility data
  is real.
- Fix the known `playwright_verify_presets.py` drift called out in
  `views_and_defaults.md` so future preset changes have a clean verifier.
- Clarify the UI copy around the two `Park` controls. The top row is a layer
  preset; the second row is a zoom preset. The `Zoom` label helps, but the
  duplicate name is still easy to misread.

### Next data pass

Confirm and tag:

- `#parking`
- `#bathrooms`
- `#first-aid`
- `#vendor`
- `#awards`
- `#raffle`
- `#volunteer-checkin`
- `#kids-crawl`
- `#spectator`
- `#camping`
- `#rv-sites`
- `#cabins`

These tags unlock Event HQ, vendor load-in, volunteer handouts, and spectator
wayfinding without inventing new machinery.

### Next preset pass

Add only one new public layer preset first:

| Preset | Why first |
| --- | --- |
| Approach | Serves out-of-town visitors, vendors, sponsors, and first-timers without needing event geometry |

Then add event views after the event layer has real features:

| View | Likely surface |
| --- | --- |
| Event HQ | Web preset or hot-button secondary target |
| Stage / Marshal | Print/export template first |
| Vendor Load-In | Per-event PDF or role-filtered layer |
| Volunteer | Per-event handout or role-filtered layer |

## Do not do yet

- Do not create one preset per persona while the data is missing.
- Do not turn Trace into a public view.
- Do not make raw evidence layers default-on for visitors.
- Do not make camera zoom buttons mutate layers unless the UI clearly says so.
- Do not build registration, payment, waivers, scoring, or merch into the map.

## Bottom line

The current presets meet the broad map-reading personas better now:

- Driver: mostly yes.
- Out-of-town visitor: partial.
- Editor / curator: yes.
- Stage designer: partial through Topo.

They do not yet meet event-operations personas:

- Marshal, volunteer, vendor, sponsor, spectator, kid crawl.

That is the next shape of the work: not more toggles first, but confirmed
facilities, event geometry, and one carefully named new preset once the data can
carry it.
