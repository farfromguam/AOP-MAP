# Council review — pins follow Park+Topo, not Park+Satellite (2026-06-14)

**Task:** User: "we have 4 — park topo trace satellite. the pins show up on satellite
but not topo. this is backwards." Flip the camp-waypoint + facility pins to follow
**Park + Topo** instead of Park + Satellite. (A reversal of the same-day decision the old
code comment recorded.)

**Change (scoped — my session's only work):**
- `website/js/viewer_core.js` `applyPreset()`: `const pinsOn = presetId === 'park' || presetId === 'topo';`
  (was `'park' || 'satellite'`), comment above it rewritten to record the reversal.
- Three descriptive comments (~2403, ~2488, ~2509) updated from "Park + Satellite / gated
  out of Trace/Topo" to "Park + Topo / gated out of Trace/Satellite". Comment-only.

The rest of `viewer_core.js`'s uncommitted diff (silver→gold medallion rename, a
`featureLabel` double-prefix fix) is prior sessions' work — out of scope, ignored per
"review your task, ignore what is not yours."

**Tier:** core three (low-risk, single-logic-line change).

**Verification (observed, not narrated):** `/tmp/verify_pins_preset.py` (race-free — waits
for the async `aop-waypoints` layer to exist before reading) against the live page on :8001,
clicking each preset and reading live `getLayoutProperty(id,'visibility')` for all four pin
layers. PASS: park=visible (tested first AND last, no state flake), topo=visible,
trace=none, satellite=none; 0 console errors. `node --check` passes.

## Verdict receipts

```
SEAT: witness
VERDICT: clear
NOTE: Running system meets acceptance (proven by a hardened, race-free re-run). Process
andon on the originally-cited verifier (it raced the async waypoint load → flaky MISSING);
resolved by adopting the race-free verifier as the canonical receipt above.

SEAT: warden
VERDICT: clear
NOTE: Every hunk traces to the user's directive; the old comment was annotated (not erased)
with the user's reversal; git gate untouched (no commit, no extra version bump — rides the
pending v90); the disclaimed medallion/featureLabel hunks confirmed not-mine.

SEAT: quartermaster
VERDICT: clear
NOTE: Extends the single existing control point (the `pinsOn` gate in applyPreset — the only
per-preset gate for these four layers; absent from PRESET_LAYERS, absent from panel.js). No
duplicate, no new path. C1/C2/C6 structural greps at target.
```

**Result: FULL CLEAR.** Clearance marker written to `.claude/.council-cleared`.

**Owed to the user (git gate):** the commit. The `sw.js`/`#appVersion` v90 bump already in
the tree (pending cemetery work) covers this JS edit's cache invalidation — no further bump.
