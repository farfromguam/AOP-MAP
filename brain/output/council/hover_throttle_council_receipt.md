# Council receipt — hover-cursor throttle (beachball prime-suspect fix)

Date: 2026-06-13
Chaired by: Steward
Tier: core three (Witness · Warden · Quartermaster) — small defensive perf change, low risk.
Card: `tasks/13_viewer_extraction/viewer_poi.md` (addendum 2026-06-13, slice 4a hover handler).
Goal: remove the per-mousemove `queryRenderedFeatures` storm in the read viewer's hover-cursor
handler (the prime suspect for the user's "beachball when hovering over the trails"), preserving
the cursor behavior.

Diff under review (this card): `website/js/viewer_core.js` hover handler at ~line 2583 — rAF-coalesce
to one query per frame + skip while `map.isMoving()`; plus the `viewer_poi.md` recording.
OUT of scope (the user's live work, in the same file): `const BAND_PAD = 0.22 → 0.60` border tuning.

Gate hash at review time: `13c8d3271e1b04ba1440811f9000b9f47429c362`

-----

SEAT: witness
VERDICT: clear
ISSUE: none
EVIDENCE: Independently re-ran probes on a live server (http://localhost:8001, real headless Chromium).
Throttle proof reproduced via live method-wrap count (120 mousemoves -> 1 queryRenderedFeatures). Cursor
preservation reproduced via live getCanvas().style.cursor reads: 'pointer' on a feature point
(elementFromPoint=CANVAS, clear of overlay), '' on a verified-empty point (live query n:0, his own added
control). node --check passed. Beachball-honesty validated: 750 real hover moves x3 presets -> 0 long-tasks,
0 re-renders; the agent correctly claims only query-storm removal, NOT a cure.
NEXT: none

SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: HEAD unchanged at 69e9000 v72 border work (reflog same, no agent commit); status shows only
unstaged modifications, nothing staged, no attribution. node --check PASS. Throttle isolated at
viewer_core.js:2583-2600; the user's BAND_PAD=0.60 hunk at :32-39 is intact/untouched (separate regions,
no clobber). On-farm (user-reported beachball over trails), reuses interactivePopupLayers/isMoving/rAF,
read behavior preserved. viewer_poi.md addendum append-only, honestly labels the change unconfirmed and the
version bump as the user's gate (correctly left un-bumped).
NEXT: none. Noticed-not-done: the user's viewer_band_merge.md records BAND_PAD ending at 0.40 while code is
0.60 — the user's stale border-recording, not this card's to fix.

SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: viewer_core.js has exactly one cursor-management path; the throttle wraps that single
mousemove handler in place (no second handler, no extracted helper, no mouseenter/leave path added).
Refuted the "should have ported main.js's per-layer mouseenter/mouseleave" novelty: main.js binds 3
NON-overlapping editor layers (main.js:9916-9925) vs the read viewer's 12 OVERLAPPING fills+lines+points
(viewer_core.js:2558-2563); MapLibre's delegated layer events hit-test per-mousemove internally (the port
would NOT reduce per-move cost) and bare enter/leave over an overlapping set flickers — so throttle-the-
single-handler is the correct minimal choice. The hoverQueryRaf block is the codebase's established
rAF-coalescing idiom verbatim (rebakeRAF main.js:9391, resyncRAF main.js:10094/viewer_core.js:2358,
queueRaise viewer_band.js:297). Structural greps hold (C1=0, C6=0 new classes, C2 single collector).
NEXT: none

-----

## Steward synthesis

Every convened seat is `clear`. The throttle's CODE is council-cleared: correct, behavior-preserving,
isolated from the user's border edit, and reuses the in-house rAF idiom. Honesty held — the work claims
only that it removes the per-mousemove query storm, NOT that it cures the beachball (which could not be
reproduced in headless; owed: the user's confirmation on the real device).

**Clearance marker NOT written.** Same reason as the v72 cursor fix: the Tier-0 gate hash spans all of
`website/`, which includes the user's uncommitted `BAND_PAD = 0.60` border tuning — work this council did
not review (it is the user's live work). Writing `.claude/.council-cleared` would falsely certify that.
The marker stays unwritten; the Stop hook will keep nudging until the user's border work is committed or
reviewed. The version bump (sw.js + #appVersion) for this shell-asset change is the user's git gate.
