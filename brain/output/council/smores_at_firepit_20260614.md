# Council receipt — s'mores at the firepit (2026-06-14)

Scoped to one task's claim: `website/data/aop_event_schedule.json` (the two
`location_tag` retags). Tree commingled with a live `clear-search-defocus` session
(viewer_core.js / sw.js / index.html v90→v91) — seats told to ignore those hunks.
Tier: core three. Steward cleared.

Change: `fri-fire` + `sat-fire` ("Fire + s'mores") `location_tag` `#pavilion`→`#firepit`,
completing item 6 of the six-item batch (which had moved only the PRO Line race).
Source `brain/import/TBI.copy`: "head to the fire pit for some smores." User: "Smores
should be at the firepit."

Acceptance observation: `brain/output/verify_smores_at_firepit.py` 12/12 PASS, 0
console errors on `:8001`.

-----

SEAT: witness
VERDICT: clear
ISSUE: none — doneness backed by an observation of the real running system.
EVIDENCE: re-ran the verifier himself (RESULT PASS, exit 0, 12/12, console_errors: []);
the verifier reads the live `event-schedule` GeoJSON source (not re-derived math); both
hunks confirmed inside the correct `fri-fire`/`sat-fire` "Fire + s'mores" objects (no
off-by-one onto neighbors); triangulation TBI.copy ↔ JSON ↔ running resolver all agree.
NEXT: none — git gate (vNN bump + commit) stays the user's.

SEAT: warden
VERDICT: clear
ISSUE: none — card-traceable, git gate untouched, no bleed into the concurrent session.
EVIDENCE: `git diff HEAD -- website/data/aop_event_schedule.json` = 2 hunks (2/2);
adjacent PRO Line session already `#firepit`, left untouched; `#firepit` is a real
defined anchor (role firepit, coords from the gold waypoint). HEAD unchanged at
`ee7f5cd "v90"`; no commit, no second bump — the v90→v91 bump is the other session's and
this fix rides the re-keyed DATA_CACHE. Data-only; JS/HTML hunks are the other session's.
NEXT: none owed for this slice.

SEAT: quartermaster
VERDICT: clear
ISSUE: none — pure two-value data retag riding the one existing transform; no novelty.
EVIDENCE: `grep -c '"#firepit": {'` = 1 (no duplicate location added — reuses the tag
baked by item 6); `git diff HEAD -- website/js/event_schedule_geojson.js` empty (canonical
`eventScheduleToGeojson` untouched); C1/C2/C6 structural greps hold (0 layerKey branches,
0 new `class`, no new editor html in scope).
NEXT: none — clear to close.

-----

STEWARD: clear. Every convened seat `clear`. The user's git gate (the `vNN` bump and the
commit) remains the user's — the council does not push past it. Whole-tree Tier-0 marker
is best-effort under concurrency; this per-task receipt is the durable authority.
