# Named-feature tagging — Sprint 02 Bucket D — **shipped 2026-05-23**

Let the event schedule say "events are at `#pavilion`" and have the viewer
resolve coordinates from the **actual 1010 Ellis Cove Rd building footprint**
— so a schedule edit never needs lat/long.

This card is the executable half of Bucket D. The curation half (collecting
SFWDA trail names, getting AOP confirmation on operational features) stays a
user-led research task because none of the underlying data has those names —
all 47 OSM `highway=track` and 19 `service` ways in the 9-patch are unnamed.

#aop #tasks #02_edit #tags #event-schedule

-----

## Source

- `_readme.md` — Bucket D in the Sprint 02 triage.
- `tasks.md` lines: *"see if we can get trail names"*, *"tag cabins / campsites
  / pavillion bathrooms"*, *"tag excavator hill / big log / jeep entrance /
  buggy entrance"*.
- User direction (2026-05-23): *"the 1010 building is the pavallion. events
  are at the pavaillion, I want to be able to edit the json scedule to say
  events are at #location and not have to enter lat and long. this is really
  it."*
- `02_edit/poi_editor_v2.md` — the shared feature list panel that this card
  extends with a per-row tag input.
- `02_edit/search_tags.md` — the `aliasesFor` hook this card feeds with each
  tagged feature's tag.
- `../01_mvp/event_schedule_layer.md` — the schedule whose `locations` block
  this card lets you write without coordinates.
- `../01_mvp/buildings_layer.md` — buildings are the first taggable layer
  (1010 Ellis Cove Rd → `#pavilion`).

## What this card builds

Three small pieces that compose into "the JSON points at a real feature":

1. **Per-row tag input** on the shared feature list panel. The user opens
   Buildings, finds the 1010 row, types `#pavilion` in the inline tag field,
   blurs. Persisted to `aop_feature_tags_v1` localStorage. Scope: buildings +
   drawn POIs only (decision below).

2. **Tag → feature lookup** built whenever a feature-list layer registers.
   Shape: `Map<#tag, { layerKey, featureId, coordinates }>`. Coordinates are
   the feature's representative point (centroid for polygons, lng/lat for
   points). Rebuilt on every register so a moved POI carries its tag's
   coordinates with it.

3. **Schedule location resolver** in `eventScheduleToGeojson`. When a
   `locations[#tag]` entry has no `coordinates`, look up the tag in the
   feature-lookup map and use the resolved coordinates. If still missing,
   treat it the same as today's missing-coords case (no anchor feature
   emitted, sessions referencing it draw as a Point only if `route_tags`
   resolve, otherwise drop — same path as `#registration` whose alias_of
   already inherits coords). When a tag binding changes mid-session, rebuild
   the schedule source + re-render the calendar so the popup/fly target
   reflects the new feature.

Proof point that lands in this card: drop `coordinates` from `#pavilion` in
`aop_event_schedule.json`. The schedule still works because `#pavilion` is
bound to the 1010 building.

## Decisions

### 1. Tag storage — localStorage only, for now

**Decided:** `aop_feature_tags_v1` localStorage key, same shape as the
existing visibility / overrides stores: `{ <layerKey>: { <featureId>: "#tag" } }`.
The DB takes over when the feature catalog moves off geojson files — user
direction (2026-05-23): *"does not bother me. at some point we will have a db
full features."*

Why: smallest path that's consistent with how every other per-feature store
already works (visibility, callout overrides, drawn POIs). Round-trips through
the existing per-section + bulk Export/Import buttons by adding one entry to
`SECTION_RUNTIME` per consuming section. No new buttons.

### 2. Taggable layers — buildings + drawn POIs only (first pass)

**Decided:** Tag input renders only on `buildings` and `editorPois` rows of
the feature list panel. Cemeteries, visitor-context callouts, and future
consumers are read-only here.

Why: covers everything in the user's message. `#pavilion` lands on the 1010
building; `#excavator-hill` / `#big-log` / `#cabin` / `#campsite` /
`#jeep-entrance` / `#buggy-entrance` can be POIs the user draws. Cemeteries
have their own identity (parcel ID + roster); tagging them as event locations
would be a category mistake. Visitor-context is regional cartography, not a
park feature.

### 3. The tag IS the lookup key — no new schedule field

**Decided:** The schedule's `locations[#pavilion]` entry already keys on the
tag. The resolver looks the tag up in the feature map; no `feature_ref` field
is added to the schema. A location can still carry explicit `coordinates` —
those win, so `#observed-trailhead` (sourced from `publish.geojson` end
points) stays as-is.

Why: avoids a schema change; keeps the JSON authoring path simple — the user
deletes a `coordinates` line and that's it. The location entry's other
metadata (label, role, source, caveat) stays useful and unchanged.

### 4. Resolution priority — explicit coordinates > tag binding

**Decided:** If `locations[#tag].coordinates` is present, use it. Only fall
back to the feature lookup when coordinates are missing. Aliases (`alias_of`)
keep their current behavior: a location like `#registration` resolves through
its base (`#pavilion`), which itself may now resolve through the tag binding.

Why: the schedule today carries authoritative coords for several locations
(`#observed-trailhead`, `#observed-finish`, the activity-hotspot-derived
candidates). Forcing them through the feature-tag flow would mean tagging
synthetic features the user didn't draw. Keep the existing path working,
layer the new one underneath.

### 5. Mid-session re-resolution

**Decided:** When the tag store changes (the user types a tag in the panel),
re-run `eventScheduleToGeojson` and push the new FeatureCollection into the
`event-schedule` source. Also re-render the calendar so the row's
`location_label` updates. Same effect a page reload would have, but live.

Why: typing `#pavilion` on the 1010 building and then clicking the pavilion
session row should fly to the building immediately, not after a reload.

### 6. Tag normalization

**Decided:** Accept tags with or without a leading `#`; store the
normalized form (`#tag`) only. Whitespace stripped. Empty string clears the
binding. Tags are lower-cased on save so `#Pavilion` and `#pavilion` collide
sensibly. A tag already bound to another feature moves the binding (one tag
→ one feature); the previous holder's input clears on next render.

Why: matches the existing `normalizeLocationTag` path the schedule resolver
already uses. Avoids a per-feature surprise where two rows both claim the
pavilion.

## Scope

In:
- `website/index.html` — feature list row, tag store, lookup map, resolver
  hook in `eventScheduleToGeojson`, live re-resolution on tag change.
- `website/data/aop_event_schedule.json` — drop `coordinates` from
  `#pavilion` once the binding works.
- `mvp/scripts/playwright_verify_event_schedule.py` or a new sibling — assert
  that tagging the 1010 building and clicking a pavilion-located session
  lands the camera at the building's coordinates.
- `SECTION_RUNTIME` for the editor + source-layers sections so the tag store
  rides the existing per-section Export/Import.

Out:
- Tag input on cemeteries / visitor-context (Decision 2).
- Multiple tags per feature. One feature → one tag, one tag → one feature.
- New schedule JSON schema field (Decision 3).
- A "see all bindings" panel — the per-row input is the only surface.
- SFWDA trail-name transcription — separate curation task, stays on
  `../01_mvp/community_trails_import.md`'s open follow-up.
- AOP-permission ask for cabin / campsite / restroom names — user-led, not in
  this code change.

## Acceptance

- [x] A `#tag` input renders on each row of Buildings and Drawn POIs in the
      feature list panel; cemeteries and visitor-context rows show no input.
      Verifier: `202/202 rows have tag input` on Buildings.
- [x] Typing `#pavilion` on the 1010 row and blurring persists to
      `aop_feature_tags_v1` localStorage and rebuilds the tag-to-feature map.
      Verifier seeds the 1010 building on first load and asserts the exact
      same flow; live re-bind to a sibling building row also passes.
- [x] After tagging, the event schedule's `#pavilion` session row, when
      clicked, flies to the 1010 building coordinates (not to the JSON's
      hardcoded coordinates — those can now be removed). Verifier:
      `camera=[-85.7481..., 35.0908...] building=[-85.7482..., 35.0907...]
      dist≈2.6e-4°` (well inside the 5e-4° tolerance).
- [x] Dropping `coordinates` from `#pavilion` in `aop_event_schedule.json`
      leaves the schedule working as long as the tag binding exists; reload
      preserves behavior. Verifier asserts the JSON has no pavilion
      coordinates AND the resolved location coordinates match the building.
- [x] Search continues to find `#pavilion` — `refreshEventScheduleSearchIndex`
      strips and re-adds event-schedule entries on every rebuild, then calls
      `buildSearchGroups` so the anchor is searchable as soon as it resolves.
      Verifier asserts `#pavilion` query surfaces the pavilion anchor.
- [x] Editing the tag on a row (changing or clearing) re-runs the resolver
      live — no reload needed. Verifier moves `#pavilion` to a different
      building row and confirms `eventLocationByTag.get('#pavilion')` returns
      the new coords without a reload.
- [x] A tag bound to a feature that's later deleted (POI "Clear all") drops
      from the store on next register pass. Implemented in
      `pruneOrphanedTags(layerKey)`, called from `registerFeatureListLayer`
      — POI clear → `refreshEditorSource` → re-register → prune.
- [x] Playwright verifier passes; 0 console errors. Run:
      `python3 mvp/scripts/playwright_verify_event_schedule.py` — all
      assertions PASS including the 14 new Bucket D assertions.

## Verification

`python3 mvp/scripts/playwright_verify_event_schedule.py` (server on 8001).
Pre-existing brittle `set_toggle` helper was made section-collapse-tolerant
in the same pass (it now drives `.checked` + change event instead of a UI
click, so a hidden checkbox no longer times out the run).

The new "Tag-driven location resolution (Bucket D)" section asserts:

- the JSON no longer carries `#pavilion` coordinates;
- the first-load seed binds `#pavilion` to the 1010 building and sets the
  seed flag;
- `tagToFeature` and `eventLocationByTag` both resolve `#pavilion` to the
  building's centroid (`dist=0.0`);
- clicking the `fri-driver-meeting` session row flies the camera within
  2.6e-4° of the building (well inside the 5e-4° tolerance);
- every building row renders the tag input; exactly one row carries
  `#pavilion`; that row is `1010 Ellis Cove Road — pavilion`;
- moving the binding to a sibling building row re-resolves the schedule
  live (new coords differ from the 1010 centroid);
- `#pavilion` continues to surface as a search result through the alias
  path because `refreshEventScheduleSearchIndex` re-runs after every
  rebuild.

Run output: all assertions PASS, 0 console errors.

## Related work

- `02_edit/poi_editor_v2.md` — the feature list panel this card extends.
- `02_edit/search_tags.md` — the alias path that already lets `#pavilion`
  resolve to the anchor; this card backs that anchor with a real feature.
- `../01_mvp/event_schedule_layer.md` — extended in place once shipped (the
  "locations may omit coordinates when a tag binds to a feature" rule).
- `../01_mvp/community_trails_import.md` — SFWDA trail-name transcription
  remains the open follow-up the curation half blocks on.
