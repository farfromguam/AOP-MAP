# Council receipt — About tab reworked into web copy (v92)

Date: 2026-06-14. Chair: Steward. Tier: five seats (witness · warden · quartermaster
· mason · scribe) — above core-three because the change spans copy + a renderer
generalization + a schema change (`aop-about-v1 → v2`).

Task: rework the About-tab copy into web-appropriate content; generalize `renderAbout()`
to a `sections[] + rules` model to carry it. Continuation of
`tasks/20_deferred/_done/rock_warblers_content_audit.md` (v92 addendum).

Scope handed to each seat (commingled tree — two other live sessions): the renderAbout
hunk in `viewer_core.js` ONLY (~L1503–1581), `aop_about.json`, the `v90→v92` line in
`sw.js`/`index.html`, the `aop_about` entry in `_data_manifest.json`, the "about" kind
in `aop_copy_registry.json`, and the About-half asserts in `verify_tbi_copy.py`. Seats
told to ignore the search-clear de-throne hunks (~1063/1079/2727/2744) and the
calendar-location `#tag` hunk (~1351), which belong to other sessions.

Result: **full clear (5/5).**

```md
SEAT: witness
VERDICT: clear
EVIDENCE: Independently re-ran verify_tbi_copy.py on live :8001 — all 18 About checks
PASS (itemCount==0, subheads==["The park & the map","What to expect"], copyCount==8,
5 rules, FB link href/text correct, note correct). Triangulated with a separate
Playwright DOM read; opened tbi_about.png (live render matches). Confirmed the 2 non-About
FAILs are pre-existing tree state: #firepit comes from aop_event_schedule.json (untouched
here, owned by smores-at-firepit session); the bronze fema-buildings tier alert is from an
unrelated subsystem. node --check OK. Old about.items/driver_meeting fully absent.

SEAT: warden
VERDICT: clear
EVIDENCE: Every in-scope hunk maps to a directive line in the v92 addendum. The two cuts
(Mandatory-skills row, rig spec) are EXPLICIT user directives, not unilateral scope.
Git gate untouched — nothing staged, HEAD still ee7f5cd, work UNCOMMITTED, addendum states
the commit is owed to the user. v90→v92 is a single shared bump (no double). renderAbout
hunk is disjoint from the other sessions' hunks — no clobber.

SEAT: quartermaster
VERDICT: clear
EVIDENCE: Exactly one live renderAbout (viewer_core.js:1508); main.js carries no
about-render code and isn't loaded by index.html; old_index.html's copy is a parked
archive, not created here. Same DOM primitives + same info-* classes reused — no second
engine. aop_about.json is the single copy source (index.html holds only the loading
placeholder). No dead code: no leftover about.items/driver_meeting reference. C1/C2/C6
region greps at target; no new *.html.

SEAT: mason
VERDICT: clear
EVIDENCE: renderAbout guards every field (Array.isArray ? … : []) — permissive, no throw,
no validator, no row-dropping filter. Safety preserved: http(s)-only link gate kept;
textContent on every text node (zero innerHTML in the function). No dead code, no
over-abstraction; idiomatic to viewer_core.js. Render mapping produces exactly h2 + intro
+ crew p + 2 subheads (2 + 3 paras) + rules lead + ul(5) + note = 8 p.info-copy, 2
h3.info-subhead. node --check passes.

SEAT: scribe
VERDICT: clear
EVIDENCE: Card addendum + handoff agree on what changed, acceptance (18/18 on live :8001,
tbi_about.png), owed (600-acre reconcile), and the v92/commit git gate; record walls this
task off from the concurrent #firepit / #tag-prefix sessions. Voice in aop_about.json reads
as Hilary inviting a neighbor ("All you have to bring is a good attitude" / "Come hang
out"); "caw-craaawl!" lands as in-group lore (user-chosen v79). No invented triad, no
em-dash default joint, no borrowed sister-event vocabulary.
```

Note: under concurrency the Tier-0 `.council-cleared` whole-tree marker is best-effort and
will go stale the moment another live session writes — these per-task receipts are the
durable clearance. The user's git gate (the v92 bump + the commit) remains the user's.
