# Council receipt — Gravity Gauntlet schedule links to the point (2026-06-14)

**Task (user, verbatim):** *"make sure the schedule links to the proper point. there should be
examples."* The `sat-gravity-gauntlet` session ("The Gravity Gauntlet") was tagged
`location_tag:"#trails"` — coordinate-less on purpose, so the schedule join gave it a null
geometry (calendar row flew nowhere, no popup). Fixed by mirroring the existing `#firepit`
example.

**Diff reviewed (scoped, two hunks in `website/data/aop_event_schedule.json`):**
1. `locations["#gravity-gauntlet"]` added — `role:"event_stage_start"`, `label:"Gravity Gauntlet"`,
   `confidence:"high"`, `source` naming the GPX, `coordinates:[-85.7515, 35.09191]` (**identical
   to the gold waypoint**), modeled key-for-key on `#firepit`.
2. session `sat-gravity-gauntlet` `location_tag` `#trails` → `#gravity-gauntlet`.
Plus `brain/output/verify_gravity_gauntlet_schedule_link.py` and the card/handoff records.
**Data-only — no JS** (the coordinate-bearing-location → event_anchor path pre-exists in
`event_schedule_geojson.js:129-156`). Seats told to ignore the rest of the commingled tree
(contours lazy-load, the gold-geojson pin change, `viewer_core.js`).

**Tier:** full six (published event-schedule product data). Steward chaired; five worker seats.

## Verdicts — all clear

```
SEAT: witness        VERDICT: clear
  Re-ran verify_gravity_gauntlet_schedule_link.py on live :8001 → 15/15 PASS, 0 console errors.
  Real observation: live event-schedule source holds an event_anchor Point at [-85.7515,35.09191]
  (raw json has 0 event_anchor strings → it's transform output, not a file echo); clicks the real
  .calendar-row, reads the rendered popup (title "The Gravity Gauntlet", Location/Tag correct),
  getCenter before/after (moved), project()+queryRenderedFeatures confirm pin AND anchor paint at
  the same screen point. Coord identical to the gold waypoint. Not tautological.

SEAT: warden         VERDICT: clear
  Exactly 2 hunks (+12/-1): the new location + the single session retag. 4 sessions remain #trails,
  1 is #gravity-gauntlet — no other session touched, no entry invented. Coord = gold waypoint (no
  fabricated pin). Git gate intact: HEAD still 813d4c9, sw.js / #appVersion unchanged, verifier is
  read-only. Card honestly supersedes the prior "not done" note rather than silently deleting it.

SEAT: quartermaster  VERDICT: clear
  Zero JS in the schedule path: event_schedule_geojson.js + main.js UNCHANGED; the viewer_core.js
  tree-diff touches no schedule line (it's the parallel Camp-POIs/contours work). New location
  reuses #firepit's exact 6 keys/order; role "event_stage_start" reuses #trails's value. One
  canonical transform (window.AOPEventSchedule), main.js:6301 the pre-existing delegating wrapper —
  no second engine/layer/index. Verifier observes, doesn't reimplement. C1/C2/C6 greps at target.

SEAT: mason          VERDICT: clear
  JSON valid (18 sessions). Key set identical to #firepit, no dead/foreign fields. coordinates
  [-85.7515,35.09191] are [lon,lat] (no swap) and byte-equal the gold GG waypoint. role
  "event_stage_start" is pre-existing; the event-anchor circle-color match (viewer_core.js:2695)
  maps it to #7f7a4b with a trailing default — permissive, no throw/validator/row-drop added.

SEAT: scribe         VERDICT: clear
  Follow-up subsection records what changed, WHY #trails produced a null geometry, the acceptance
  (15/15 PASS / 0 errors / :8001), and the git gate (uncommitted v92→v93, the user's). Handoff
  "not done" line replaced with DONE — no stale contradiction. #firepit treated as the real mirrored
  example (verified: its coords match a Firepit waypoint, 3 sessions tagged to it), not an analogy.
  Voice plain, quotes the user verbatim, no over-claim.
```

**Result: CLEAR (5/5 convened seats).** Steward clears the gate. The user's git gate (the
v92→v93 `sw.js`/`#appVersion` bump + the commit) is not part of this clearance — it stays the user's.
