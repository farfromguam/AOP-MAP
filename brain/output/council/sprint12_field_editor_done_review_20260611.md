# Council done-review — Sprint 12 field schedule editor

Date: 2026-06-11. Chair: Steward. Diff: `website/schedule_editor.html` (new), `brain/tasks/12_field_schedule_editor/_readme.md` (new), `brain/handoff/session_context.md` (pointer). Card: `tasks/12_field_schedule_editor/_readme.md`. Tier: 5 seats (new user-facing editor handling schedule data + sprint boundary).

**Outcome: CLEAR.** All five seats clear; one field-hardening finding applied before clearance.

```
SEAT: witness        VERDICT: clear
Drove the page headless (localStorage cleared first): event "Rock Warblers Trail Blazing Invitational",
13 cards, edit→autosave→localStorage, RELOAD + COLD-LOAD survive, add 13→14, reorder swap, delete 14→13,
reset flips your-edits→published. Zero console/page errors. Artifacts /tmp/witness_sched.png, /tmp/witness_persist.py.

SEAT: mason           VERDICT: clear
Full-doc deepCopy override is lossless — empirically preserved activity/inspired_by/location_tag/id +
top-level locations(7)+event block on round-trip. Export serializes whole doc. No limiting construct
(status datalist = suggestion not enum; render iterates all sessions; no row-drop/validator/throw). boot()
degrades gracefully. NOTES: (1) addSession mints thinner session → downstream import must tolerate missing
optional keys; (2) sub-250ms unload window → add pagehide/visibilitychange flush. → BOTH ADDRESSED:
flush APPLIED + verified; import-tolerance noted on card for the Export→DB step.

SEAT: quartermaster   VERDICT: clear
No duplication. Does not re-implement event_schedule_geojson.js (no GeoJSON transform — flat tabular edit
of the served doc, written back verbatim). New key aop_schedule_override_v1 collides with none of 18
existing aop_*_v1. Sibling of data_sources.html standalone pattern, not a second viewer/editor. C1/C2/C6
intact (main.js/panel.js untouched).

SEAT: warden          VERDICT: clear
Git gate intact: no agent commit (HEAD 0c57f6e is the user's), sw.js unchanged, VERSION/#appVersion
untouched — precache + bump correctly OWED to user. Blast radius true: main.js + panel.js untouched;
editor self-contained, no <script src>. On-scope (basic offline field editor = the directive). New sprint
dir additive. (Noticed: the sprint-11 manifest nit-fix sits uncommitted in the tree alongside this — the
user's to stage/commit.)

SEAT: scribe          VERDICT: clear
Card has reproducible verification + observed numbers; honest limit (offline edit propagates only when a
device regains signal) recorded not overclaimed; owed stated (precache+bump, Export→DB, optional overlay);
UNCOMMITTED; handoff a short pointer; plain self-true voice, references treated as the thing.
```

Post-clearance hardening (this session): `pagehide` + `visibilitychange→hidden` flush added to
`schedule_editor.html` and verified by observation (edit → fire close event with no debounce wait → edit
present in localStorage; clean reload still 13 sessions, no errors). Carried-forward note: the
addSession thinner-shape tolerance check belongs to finishing step 2 (Export→DB).
