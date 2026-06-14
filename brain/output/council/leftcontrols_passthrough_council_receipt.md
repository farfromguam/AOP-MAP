# Council receipt — left-controls overlay pass-through (v72 cursor/drag fix)

Date: 2026-06-13
Chaired by: Steward
Tier: core three (Witness · Warden · Quartermaster) — CSS-only read-viewer fix, low risk.
Card: `tasks/13_viewer_extraction/viewer_drawer_schedule.md` (addendum 2026-06-13).
Goal: make the empty regions of the `.left-controls` overlay map-draggable (grab cursor)
without breaking the controls — the user's "Hand turns to a pointer in the empty area" bug.

Diff under review (this card): `website/css/viewer.css` (the pointer-events pass-through),
`website/index.html` + `website/sw.js` (v71→v72), and the two brain recordings.
Explicitly OUT of scope (pre-existing uncommitted, disclaimed to the user): `website/js/viewer_core.js`
BAND_PAD 0.13→0.22, untracked `brain/output/council/band_merge_council_receipt.md`.

Gate hash at review time (gate formula, spans website+mvp): `cd2febcf0aa046bd7aac33cecaaf03e99330ffab`

-----

SEAT: witness
VERDICT: clear
ISSUE: none
EVIDENCE: Restarted `python3 -m http.server 8001` in website/ and independently re-ran the Playwright
probes (real headless Chromium, elementFromPoint + getComputedStyle on the live DOM). Reproduced
empty→draggable (collapsed points (200,120)…(300,180),(100,70),(100,55),(60,55) and expanded gaps
(138,30)/(308,30)/(100,55) all return canvas cur=grab) and controls-live (zoomPark/searchInput focus/POI
tab/Hot toggle/Cal re-open; icon card stays solid). node --check sw.js passed; #appVersion v72 == sw VERSION.
Notes (non-blocking): verifier point (348,30) lands on the real #terrainButton (narration drift; measured
gap (308,30) passes); hidden util-install/ios-hint not click-tested but create no dead zone.
NEXT: none — version bump + commit are the user's git gate.

SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: HEAD unchanged at 2980c27 (reflog: no mutating git this session); all 6 changes uncommitted; no
attribution/co-author trailer anywhere in the diff. viewer.css change is additive pointer-events
pass-through, deletes no existing rule, traceable to the card line. v71→v72 is the documented sw.js
shell-asset step (header lines 30-32), stated as the user's gate not narrated as done. Both brain edits
append/record only. `.council-cleared` holds da39a3ee (empty-string) ≠ gate hash cd2febcf, so no marker was
slipped over the disclaimed non-card BAND_PAD work.
NEXT: none for this card; the disclaimed BAND_PAD 0.13→0.22 + untracked band receipt remain unreviewed —
noticed, not done.

SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: app.css (loaded only by the dead old_index.html; live index.html loads viewer.css) has NO
`.left-controls{pointer-events:none}` pass-through — so viewer.css is a NEW fix, not a divergent duplicate.
Re-armed children (.pill / .lr-icon-col / .lr-content-col / .util-install / .util-ios-hint) all map to real
elements in the .left-controls subtree; the fill-less .pill-bar / .lr-drawer wrappers correctly pass
through; #appVersion (hidden span) correctly unarmed; #locateBtn lives outside .left-controls. Structural
greps hold (C1=0, C6=0 new classes, C2 single collector, no new editor *.html).
NEXT: none

-----

## Steward synthesis

Every convened seat is `clear`. The card's work — the `.left-controls` overlay pass-through, the v71→v72
bump, and the recording — is **DONE** per the Definition of Done items 1–6, with the standing exception
that the commit + version bump are the user's git gate (not the agent's to clear).

**Clearance marker deliberately NOT written.** The Tier-0 gate hash spans all of `website/`, which includes
the pre-existing uncommitted `viewer_core.js` BAND_PAD 0.13→0.22 change that this council did not review and
that is outside this card. Writing `.claude/.council-cleared` with the current hash would falsely certify
that band change. So the marker is left as-is (empty-string hash); the Stop hook will keep nudging until the
band work is itself reviewed or the user commits this work apart from it. This follows the precedent in the
v69 handoff note. The honest state: this card is council-cleared; the tree also carries unreviewed band work.
