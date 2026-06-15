# Council — Park-bounds border toned to a faint tint-edge (2026-06-15)

**Scope:** the `publish-boundaries` line paint in `website/js/viewer_core.js` only
(base `addLayer` + Park + Topo preset overrides). Concurrent 3D-spin work and other
uncommitted tree state were out of scope per the task-scoped council rule.

**Claim:** User — *"the park bounds have a dark border. remove the border. there is a
tint on the land that should do the same"* → *"ok keep the border if you need it to
click on. make it way less visible. only a tad darker than the fill."* Border kept as
the click target (`INTERACTIVE_POPUP_LAYERS`), re-painted dark→faint so the
`publish-boundary-fill` tint's opacity step does the separating: Park `#6e5a3c` w2.5 →
`#c4b48c` w1.5 op0.5; Topo `#4d3928` w3 → `#d4b974` w1.5 op0.5; base addLayer to match.
Trace/Satellite `showBoundaries:false` → their override is a dead no-op, left untouched.

**Verification:** `brain/output/verify_park_border_faint.py` — 8/8 PASS, 0 console
errors; screenshots `park_border_faint_{park,topo}[_closeup].png`.

## Seat verdicts

- **Witness (verification): CLEAR.** Independently re-ran the verifier (8/8 PASS, 0
  errors, exit 0) — live `getPaintProperty` reads the faint values, not re-derived math.
  Looked at the actual full-parcel screenshots: faint tint-edge ring, not a dark line.
  Confirmed Trace `#fff0b8` boundary is dead config behind `showBoundaries:false`.
- **Quartermaster (reuse/no-dupes): CLEAR.** Edited the single existing
  `publish-boundaries` layer in place; reused the existing `publish-boundary-fill` tint,
  the existing `INTERACTIVE_POPUP_LAYERS` click path, and the shared `playwright_base`
  verifier harness. No second layer, no parallel tint, no re-implemented helper. C1/C2/C6
  hold.
- **Warden (scope/git-gate): ANDON → RESOLVED.** The served work is on-farm (every paint
  hunk traces to the directive; layer kept; no scope-widen; clean attribution on the
  commit). The andon was a *staleness* flag on the handoff note: the user committed
  **v96** (`0d7b750`) mid-session — bundling this change with the 3D-spin work, the contour
  cleanup, and a task-move — so the note's "(UNCOMMITTED) / committed HEAD is v95 / no bump
  owed" was false. Resolved by correcting the handoff note to "shipped in v96 (committed
  `0d7b750`)"; the v95→v96 cache bump rode that same commit. The commingled commit is the
  user's git-gate call, not a defect.

**Outcome:** CLEAR. Served change verified by observation and on-farm; record corrected.
