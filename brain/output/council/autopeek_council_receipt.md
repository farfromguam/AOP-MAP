# Council receipt — auto-peek (on-load border reveal restored)

Date: 2026-06-13
Chaired by: Steward
Tier: core three (Witness · Warden · Quartermaster) — low-risk additive UI animation
(client-side camera reveal, no publish-zone data, no contracts touched).
Card: `tasks/13_viewer_extraction/viewer_band_merge.md` — "Auto-peek restored — 2026-06-13".
Goal: restore the proof page's "Show me (auto-peek)" as an AUTOMATIC on-load reveal in the live read
viewer — pull the camera back to frame the whole printed border, hold, ease home — without leaking
proof scaffolding and without yanking the camera from a user already interacting. Plus one stale-comment
fix in `viewer_core.js` (Region-preset leash note "+13%" → BAND_PAD-relative).

Diff under review (this session): `website/js/viewer_band.js` auto-peek block
(`autoPeek`/`schedulePeek`/`killPeek` + the `schedulePeek();` call in `addBand`) and the comment-only
`website/js/viewer_core.js` ~line 401 fix.
OUT of scope (prior/uncommitted work in the same files): `BAND_PAD = 0.60` (the user's live border-feel
tuning), the hover-cursor throttle (already cleared — `hover_throttle_council_receipt.md`), and the
`snapBack` rubber-band removal (prior session).

Gate hash at review time (spans all of website/mvp): `82339c29ff38743fa18c007b02bf53addd6697e2`
HEAD: `69e9000`

-----

SEAT: witness
VERDICT: clear
ISSUE: none (sub-defect note: measured trough z≈12.91, card said "~12.8" — 0.1 drift; left vertical
legend sits slightly clipped at `padding:90`, which the card already flags as a tunable knob).
EVIDENCE: Live Chromium/Playwright on http://localhost:8001/index.html. Passive load: data frames at z=14
by t≈2.4s, auto-peek eases 14 → trough z=12.914 at t≈5.9s, holds ~1s, eases back to z=14 by t≈7.8s.
Trough screenshot reads all four edge legends live (title top, Rock Warblers right, South Pittsburg
bottom, ruler text left) + corner marks + neat-line with paper margin. Band layer count min=max=38 across
a 14s poll; console + pageerror = [] on every run. A real mouse drag during load → 0 auto down-swings
(zoom holds flat at 14), in both an early and a post-park-frame run. Exactly 1 down-swing per passive load
(runs once). node --check PASS on both files; stale-comment fix confirmed in diff.
NEXT: none. Optional (user's eye): loosen `padding:90` if the left legend should read fully un-clipped.

SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: HEAD=69e9000, nothing staged/committed, no attribution; version still v72 in `sw.js:35` +
`index.html:220` (the v72→v73 bump correctly NOT done, recorded as owed in the card). The original
"What does NOT cross" exclusion of the auto-peek is preserved verbatim (card L57) AND annotated with the
dated reversal addendum quoting the user's directive (*"the auto peek needs to go back… it needs to
stay."*) — directive annotated, not deleted. Every hunk traces to the user's directive: the auto-peek is
camera-only (`fitBounds`/`easeTo`), no reach into `panel.js`/`main.js`/`data_editor*`/any CRUD; the
`viewer_core.js` hunk is comment-only (the `0.07` outset math untouched) → the QA "no residual crud" ask.
NEXT: none. Flag to Steward: the Tier-0 hash spans all uncommitted website/ work (BAND_PAD=0.60, hover
throttle), so a `.council-cleared` marker would cover the whole working tree, not just this session.

SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: The work DELETES the would-be second mechanism rather than adding one — the proof's peek drove
`AOPViewerBand.gaps()`/`snapBack()` (over-pan + screen-space rubber-band); the diff removes
`gaps`/`rawGaps`/`snapBack`/`regionRect`/`easeOutCubic`/`SNAP_MS` and replaces them with a self-contained
`autoPeek` that (a) reuses the proof's framing recipe — `fitBounds(REGION_BOUNDS, {padding:90})`,
identical to `viewer_banded.html:254` — for the reveal, and (b) captures live camera state + `easeTo` for
the return, which no existing helper provides (`goToView` only frames fixed presets, never "current
resting view"). Cancel uses `e.originalEvent`, the native MapLibre programmatic-vs-user discriminator, not
an invented one. No forked rAF (the band's `queueRaise` z-order coalescer is untouched; the peek uses
one-shot `map.once('idle'/'moveend')` + `setTimeout`). Diff adds no `class [A-Z]`, no registry, no
`*.html`. Contract greps hold and are out of blast radius (C1/C2/C6 unchanged).
NEXT: none. (Adjacent, card-tracked: the proof page's `gaps()` button at `viewer_banded.html:232` is now
dead — that file is slated for retirement.)

-----

## Steward synthesis

Every convened seat is `clear`. The auto-peek CODE is council-cleared: it is observed working on the real
running system (Witness independently reproduced the pull-back-to-full-border-and-return, the 38-layer
hold, zero console errors, the once-per-load count, and the user-drag cancel), it stayed on the farm and
left the user's git gate untouched (Warden — the reversal of the card's own "does NOT cross" decision is
honestly annotated to the user's explicit directive), and it reuses the in-house idioms while removing the
old mechanism rather than paralleling it (Quartermaster).

**Clearance marker NOT written.** Same reason as the v72 cursor fix and the hover-throttle review: the
Tier-0 gate hash spans all of `website/`, which includes the user's uncommitted `BAND_PAD = 0.60` border
tuning — work this council did not review (it is the user's live work). Writing `.claude/.council-cleared`
with the combined hash would falsely certify that. The marker stays unwritten; the Stop hook will keep
nudging until the user's border work is committed or reviewed.

**Owed (the user's git gate):** the commit + the `#appVersion`/`sw.js VERSION` bump (v72 → v73, so
installed PWA users get the new `viewer_band.js`); retire the spent scaffolding (`viewer_banded.html` —
now also half-broken, its peek button calls the removed `gaps()`; `viewer_banded_compare.html`;
`css/viewer_band.css`).
