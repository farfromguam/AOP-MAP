# Council receipt — mockup cleanup + contour styling mockup (2026-06-15)

**Goal (Steward, one line):** Remove dead mockup HTML pages and add a dev-only compare
mockup for tuning major/minor contour line styling (minor barely visible) — the user's
request verbatim: *"we have a few mockup html pages that are no longer needed. find them
and remove them. Create a new mockup for CSS styling of major and minor topography contour
lines. I want to see a few variations we can barely see the minor lines."*

**Scope (commingled tree).** A second live session shipped the v94→v95 trail-permission
work on the same tree. This task's diff: 16 deleted mockup `.html` under `website/`; new
`website/contour_styling_mockup.html`; comment-only hunks in `index.html` (@@ -7/-174/-195),
`sw.js` (@@ -68), `css/viewer.css` (line 284); brain verifier + screenshots + handoff entry.
Seats were told to IGNORE the other session's hunks (`v94→v95` bump in index.html/sw.js, all
of `viewer_core.js`).

**Tier:** core-three (low risk — dead-file deletion + dev-only mockup + comment-only shell
edits; no served/data/publish-zone change).

## Verdicts

```
SEAT: witness        VERDICT: clear
  Re-ran verify_contour_styling_mockup.py live on :8001 — 12/13 (the 1 fail is the check's
  own overbroad `.grid p` selector, not the page), 0 console errors, all 5 canvases sized,
  live-confirmed window.__CONTOURS.features.length === 911 (real 501 major + 410 minor).
  Close-up PNGs show the real faintness gradient (baseline visible → ghost barely-there,
  majors held bold). Grep: 0 non-comment runtime refs to the 16 deleted files.

SEAT: warden         VERDICT: clear
  All 16 deletions are dead mockups (0 runtime href/src/fetch refs; none in sw.js
  SHELL_ASSETS); the 6 surviving HTML are live tools. My index.html/sw.js hunks are
  comment-only; the lone non-comment line (appVersion v94→v95) is the other session's bump,
  correctly excluded → no vNN owed by this task, git gate untouched. New mockup is dev-only
  ("DEV MOCKUP not served" banner, not precached), renders real data, on-directive.
  ADVISORY (does not bounce): stale comment at css/viewer.css:284 still named the deleted
  calendar_placeholder_v2_spinner.html — same pointer class the task cleaned elsewhere.

SEAT: quartermaster  VERDICT: clear
  Mockup MIRRORS the live model (same source gold_aop_contours.geojson, same idx==0/idx==1
  filters, same contours-minor/index/labels IDs + line paint as viewer_core.js:808–850;
  baseline #c6ad84 op0.28 / major #a8855b match the Topo preset overrides 651–652) — a
  reference, not an analogy; a picked variation drops straight onto the zoom-fade endpoint.
  Loads only vendor/maplibre-gl.js — no forked viewer code, no second harness, no new
  registry. C1/C2/C6 contracts hold. Same css/viewer.css:284 advisory noted.
```

## Resolution

All three convened seats `clear`. The shared advisory (stale `css/viewer.css:284` comment
pointing at a deleted file — and the handoff note's overclaim that "all" dangling refs were
fixed) was resolved after the review: the comment was corrected and a full grep confirms
**0 remaining references** to any of the 5 deleted-file names across served html/js/css/json
(excluding the new mockup itself). Comment-only, no served behavior change.

**Steward verdict: CLEAR.** No `vNN` bump owed by this task; the commit is the user's git
gate. Awaiting the user's pick of a contour variation to wire into `viewer_core.js`.
