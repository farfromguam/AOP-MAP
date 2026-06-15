# Council receipt — Hot Rocks Comp Pad starred into the POI list (2026-06-14)

**Goal:** *"Hot rock comp pad needs to be starred and show up in poi list."* The pad is a
camp **waypoint**; the reader POI directory's `STAR_GROUPS` had no waypoints group, so a
star alone wouldn't surface it.

**Change (this task's hunks only — tree commingled, prior changes already committed at v92):**
- `website/data/gold_aop_waypoints_traced.geojson`: Hot Rocks Comp Pad +`"highlight":true`
  (only highlighted waypoint).
- `website/js/viewer_core.js`: module-scoped `poiWaypointsData` (L309) assigned from the
  already-loaded `aopWaypointsData` (L2498, after the existing fetch) + a
  `{ id:'waypoints', label:'Camp POIs', data:()=>poiWaypointsData }` STAR_GROUPS entry (L1808).
- `brain/output/verify_hot_rocks_in_poi_list.py` (new verifier) + doc records.

**Tier:** core three (Witness · Warden · Quartermaster) — ★-curation + a one-entry viewer
extension; low risk, no provenance claim (the pad is an existing first-party traced waypoint).
**Deterministic gate:** `node --check website/js/viewer_core.js` passes; JSON valid.

## Verdicts

```md
SEAT: witness
VERDICT: clear
ISSUE: none — "11/11 PASS" reproduces on live :8001 and rests on real DOM + live-source reads.
EVIDENCE: re-ran verify_hot_rocks_in_poi_list.py → 11/11 PASS, console_errors []. Verifier reads the LIVE
  aop-waypoints source for the "only Hot Rocks highlighted" check (not the file), the rendered
  .poi-list-group/.poi-row DOM, and the live .maplibregl-popup after a real row click. Assertions are
  EXACTLY-strict (highlighted == [NAME]; camp_names == [NAME]; count == "1") — negative-control confirmed
  they flip to FAIL on absent group / extra waypoint / count≠1. Source has 1 of 23 highlighted; node --check OK.
BLIND SPOTS (named, non-blocking): headless basemap tiles blocked, so the map-canvas dot paint isn't proven
  (the POI-list/popover path — the task — is fully exercised); popover meta-removal is prior cleared work.
NEXT: none.

SEAT: warden
VERDICT: clear
ISSUE: none blocking — directive done 1:1; durability honestly flagged. Git-gate wording was stale (fixed):
  HEAD is now 813d4c9 "schedule tweaks" with sw.js VERSION='v92' COMMITTED, not "HEAD v90 / v92 uncommitted".
EVIDENCE: git diff HEAD = exactly 4 paths (the geojson, viewer_core.js, 2 brain docs); diff of sw.js/index.html
  empty → no agent bump/commit/attribution. grep -c '"highlight"' on the geojson = 1 (Hot Rocks only); its
  coords byte-identical pre/post (no geometry mutation); no other waypoint property changed. The three
  viewer_core.js hunks are exactly the card's (var L309, assignment-after-existing-fetch L2498, one STAR_GROUPS
  entry L1808) — no other group altered, no new engine. Durability gap (authored-on-served; Affinity round-trip
  strips authored fields; bake_poi_stars.py doesn't cover this trace file) stated in the card + handoff.
NEXT: the v92→v93 bump + commit are the user's git gate (now stated as owed in card + handoff, per this finding).

SEAT: quartermaster
VERDICT: clear
ISSUE: none — extended the existing single POI directory; no second engine, fetch, gate, or dead code.
EVIDENCE: one new STAR_GROUPS entry; buildPoiGroups/renderPoiTab unchanged (still iterate STAR_GROUPS).
  poiWaypointsData assigned from the already-loaded aopWaypointsData — only ONE fetch of the file in the module
  (no duplicate). poiWaypointsData declared→assigned→consumed by the new group's data() (reachable, not dead).
  Existing ★ gate (p.highlight !== true) reused; curation is data (highlight:true), no new gating path.
  C1=0, C6 (0 classes / 1 STAR_GROUPS registry / no new editor html), C2 (single buildPoiGroups collector) hold.
NEXT: none.
```

**Steward synthesis:** full clear — Witness · Warden · Quartermaster all `clear`, no open
andon. The change extends the existing ★-gated directory; provenance/source-led intact
(curation flag on an accepted first-party waypoint). **User's git gate (owed, not done by
the agent):** v92 is committed, so this uncommitted shell+data change is owed a **v92→v93**
bump (`sw.js VERSION` + `#appVersion`) plus the commit, to reach already-cached PWA clients.
