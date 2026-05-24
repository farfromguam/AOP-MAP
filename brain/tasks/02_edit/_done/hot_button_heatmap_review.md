# Hot Button and Heatmap Review

Date: 2026-05-24

TL;DR:
- The hot button is directionally right for event-day personas: it gives drivers, spectators, families, volunteers, and staff one always-visible action when the calendar is collapsed.
- The heatmap is useful as activity evidence, but it should not be framed as live crowding or "right now" heat until the data is recent, aggregated, and privacy-reviewed.
- Next pass should tighten the fallback label, use a true hotspot cluster target, refresh the committed hotspot metadata, and make cross-day countdowns human-readable.

#aop #02_edit #hot_button #heatmap #personas #review

-----

## Reviewed

- `../../northstar/personas.md`
- `_done/left_hot_button.md`
- `../01_mvp/_done/activity_hotspots.md`
- `../../research/viewer.md`
- `../../../website/index.html`
- `../../../website/data/aop_activity_hotspots.geojson`
- `../../../mvp/scripts/build_activity_hotspots.py`
- `../../../mvp/scripts/playwright_verify_event_schedule.py`
- `../../../mvp/scripts/playwright_verify_activity_hotspots.py`

## Verdict

The **hot button** is the right surface. It serves the shared event-day question:
"Where do I need to go next?" The state order is correct:

1. Live or imminent session.
2. Next scheduled session.
3. Activity evidence only when no schedule target exists.

The **heatmap** is the right fallback kind, but the wording and target behavior
need more discipline. For the northstar personas, heat should mean different
things depending on data:

- Drivers can use heat as a hint for technical spots or social dwell.
- Staff can use heat as a validation prompt.
- Spectators and families may read heat as where people are right now.

That last interpretation is risky with the current source: one first-party GPX
file, internal permission, publish hold, and raw-review status.

## Findings

### 1. Heatmap fallback can be misread as live activity

The hot-button card describes the fallback as answering where the park is hot
"right now," but the committed data is raw historical activity evidence:

- `website/data/aop_activity_hotspots.geojson` metadata source file:
  `Saturday_Afternoon_Activity.gpx`
- Feature confidence: `single_track`
- Feature `publish_status`: `hold`
- Feature `review_status`: `raw activity evidence; not a validated trail or facility`

The current button copy is safer than "right now" because it says
`Activity hotspots` / `Show where rigs ran`, but a spectator or first-time
visitor can still read the heat layer as live crowding unless source and recency
are visible at the action point.

Recommended fix:

- Rename fallback detail to `Past activity evidence` or `Show activity evidence`.
- Include a short recency/source cue in the button detail or popup, such as
  `single GPX - raw evidence`.
- Reserve "live heat" language for future aggregated, recent, privacy-reviewed
  event telemetry.

### 2. "Densest cluster bbox" is not actually a cluster

`findDensestHotspotBbox(topK = 3)` sorts all hotspot polygons by
`intensity_norm`, takes the top three, and bboxes them together. That is a
ranked top-K target, not a cluster target.

In the current first-party hotspot file, rank 1 starts near
`-85.748189, 35.0903075`; ranks 2 and 3 start near
`-85.7440719, 35.0957354` / `35.0979065`. Those are far enough apart that the
fallback click can frame a broad corridor instead of an actionable hotspot.

Recommended fix:

- Pick the strongest cell, then include nearby cells within a distance threshold.
- Or cluster cells first by adjacency/distance and rank clusters by summed
  `interest_seconds`.
- Update the event-schedule verifier so fallback asserts more than visibility:
  after click, the camera should land on the chosen cluster with a bounded zoom.

### 3. The committed first-party hotspot metadata is stale

`build_activity_hotspots.py` now emits top-level `source_type`, `permission`,
`publish_status`, `review_status`, `confidence`, `rank_by`, and filter settings
in metadata. The committed `aop_activity_hotspots.geojson` metadata only has the
older core fields. Feature-level properties carry the source discipline, but the
collection-level metadata should match the builder.

Recommended fix:

- Regenerate `website/data/aop_activity_hotspots.geojson` from the current
  builder.
- Extend `playwright_verify_activity_hotspots.py` to assert top-level
  permission, publish status, review status, confidence, and rank mode.

### 4. Cross-day countdowns are technically correct but hard to read

The hot button intentionally looks ahead across days. The shared
`eventScheduleFormatMinutes()` formatter only returns minutes or hours, so a
Monday-to-Friday target can read like `in 101h`.

Recommended fix:

- Add a hot-button-specific duration formatter that emits days once the target
  is more than 24 hours out, for example `Fri 5:00 PM - in 4d 5h`.
- Keep the short minute/hour format for live and same-day imminent sessions.

### 5. Icons are still placeholders

The emoji glyphs work as a fast implementation, but they are not a designed icon
set and will not read as a coherent control once branding lands.

Recommended fix:

- Replace the glyphs with a small consistent icon set during the branding pass.
- Keep the state words; icons should assist, not carry the state alone.

## What is working

- The button is in the right chrome location and remains useful when the
  calendar is collapsed.
- It reuses the schedule clock, 60-second tick, visibility refresh, tag-rebind
  path, and `gotoEventSession`.
- Hot-now and coming-up click behavior matches calendar row behavior.
- The heatmap layer itself respects source discipline: default off, raw
  evidence status, auditable cells, labels, and explanatory popups.
- The heatmap builder correctly separates stopped, slow, and moving time, and
  keeps cells printable/clickable instead of relying only on a screen heatmap.

## Recommended next pass

1. Tighten fallback copy so it says evidence, not live heat.
2. Replace top-K bbox with true cluster targeting.
3. Regenerate first-party hotspot GeoJSON from the current builder.
4. Add metadata assertions to `playwright_verify_activity_hotspots.py`.
5. Add day-aware hot-button duration copy.
6. Defer persona-specific buttons until Event HQ / Stage / Volunteer / Vendor
   data exists. One shared hot button is still the right V1 surface.
