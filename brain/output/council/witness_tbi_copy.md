# Witness receipt — TBI.copy content update (v77, uncommitted)

SEAT: witness
VERDICT: clear
ISSUE: none
DATE: 2026-06-14

## What I actually observed (running system on http://localhost:8001/, server confirmed HTTP 200)

### Calendar render — the named gap, INDEPENDENTLY VERIFIED
The verifier's own DOM probe (`verify_tbi_copy.py` line 84-88) reads `#calendarDays`
BEFORE clicking into the Events tab, so it reported "1 rows, first=''". That is a
probe-ordering artifact, not a render failure. I ran my own Playwright read
(`/tmp/witness_cal.py`, swiftshader GL) that clicks `#leftTabEvents`, waits, then
reads the DOM:
- `#calendarDays` -> 18 `<li>` rows, ALL real (`realLiCount = 18`, none `.calendar-empty`)
- Rows are real `<button class="calendar-row" data-session-id="fri-arrive" ...>` etc.
- First six names: Arrive + camp setup, Registration + 50/50 raffle tickets, Trail
  exploration, Rock Hard Adventure Tour, Fire + s'mores, Open exploration
- Full set includes Driver meeting (Sat 9:00 AM), Show & Shine, Warbler Peck and Pop,
  The Gravity Gauntlet, PRO Line Before the Fire, Driver Doodles, High Noon awards,
  Clean/wrap/pack up
- Anchors render: #pavilion - Pavilion (base camp), #trails - Park trails,
  #camping-field - Camping Field
- Live countdown text: "Gates open in 5D 15H"
So the live calendar genuinely renders the 18 real sessions with a working countdown.
The card's claim is backed by observation, not narration.

### Screenshots (Read directly, cropped + 2x upscaled left panel)
- tbi_about.png: About tab shows "About the Rock Warblers", welcome intro w/ Trail
  Blazing Invitational link, Mandatory skills = "Good attitude", Rigs w/ 1.55/1.9/2.2
  classes + "No dig, no rear steer". Real copy rendered.
- tbi_events.png: Events tab shows "ROCK WARBLERS TRAIL BLAZING INVITATIONAL",
  Fri Jun 19 - Sun Jun 21 2026, "GATES OPEN IN 5D 15H", FRI rows (Arrive + camp setup
  #camping-field, Registration + 50/50 #pavilion). The screenshot DOES show the live
  calendar + working countdown as the card claims.

### Verifier re-run (mine): `python3 brain/output/verify_tbi_copy.py` -> 30/30, EXIT=0
The checks that matter are GL-INDEPENDENT real reads of the running app:
- About DOM read from `#aboutInfoPanel` (h2, intro, 5 items, subhead, 9 info-copy
  paras, 5 rules, note, trail-buddies removed) -- real DOM, not re-derived.
- Schedule uses the SAME in-page transform the calendar+map consume
  (`window.AOPEventSchedule.eventScheduleToGeojson`) on the live fetched config:
  status=live, 18 sessions, anchors == ['#pavilion'], days Fri/Sat/Sun, composed
  window "9:00 AM · Morning" for sat-driver-meeting, real session titles. Authentic
  transform output, not narrated math.
- "no real (non-GL) errors": 4 messages, all classified GL flake (fragment shader),
  0 real errors.

### Data-file claims, checked directly
- aop_event_schedule.json: status "live"; 18 sessions; locations #pavilion/#trails/
  #camping-field where ONLY #pavilion carries `coordinates` (one map anchor; the
  other two are coordinate-less, honest, zero fabricated pins).
- aop_about.json: driver_meeting = {heading "Driver's Meeting", paragraphs[7],
  rules{lead, items[5]}}; 5 items [Mandatory skills, Rigs, The park, The map, The crew].

### Code hunks in scope (only these)
- viewer_core.js renderAbout driver_meeting hunk: textContent throughout (no innerHTML/
  XSS), Array.isArray guards, missing-field tolerant. Idiomatic. node --check OK.
- viewer_core.js + main.js attribution: "proposed from sister-event references" ->
  "Rock Warblers Trail Blazing Invitational". node --check OK on both.
- old_index.html editor <small> de-hedged. viewer.css adds .info-subhead/.info-rules.
- No constraint/validator/row-dropping/throw-on-unknown code added.

### Triangulation against authoritative source (brain/import/TBI.copy)
Rendered copy is faithful to the lead's real copy: Driver's Meeting script, 5 rules,
Rigs/Park/Map/Crew all match (light typo/grammar cleanup, e.g. Pavillon->pavilion).
Trail Buddies (source line 67 `>>> remove`) is removed. The `[insert rock warbler
call]` placeholder (source line 93) is correctly omitted and tracked in owed_work --
an honest deferral, disclosed in the card, not a defect.

## Verdict reasoning
Every "verified/works/done" claim points at a real observation of the running system:
live DOM reads, the GL-independent in-page transform on live config, two screenshots
that show what's claimed, and the source-of-truth copy. The one named gap (empty
calendar in the verifier's headless probe) is a probe-ordering artifact, not a render
failure -- I observed the real 18-session calendar + countdown rendering myself.

EVIDENCE: tbi_about.png, tbi_events.png (Read + cropped), `python3 brain/output/verify_tbi_copy.py` 30/30 EXIT=0, /tmp/witness_cal.py live DOM read (18 calendarDays rows + countdown), direct JSON inspection of aop_event_schedule.json/aop_about.json, git diff of in-scope hunks, node --check on both JS files, brain/import/TBI.copy triangulation.
NEXT: none
