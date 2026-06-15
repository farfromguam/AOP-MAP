# Council receipt — trail permission → publish (full six)

Date: 2026-06-15
Chair: Steward
Task: Correct the trail-network permission posture so the first-party-traced trails
read as publish-clean gold. User directive: *"these guys give permission for people
to put the map up on the internet, and we are tracing the unmapped trails manually.
the trails should be rendering and gold for all intensive purposes."*

## Scope (this task's claim only — tree is commingled with ≥2 live sessions)

- `website/data/gold_aop_trail_network.geojson` — 130 trails → `permission:"publish"`
  (was 120×`"SFWDA paper map — permission TBD"` + 10×missing key).
- `mvp/scripts/import_illustrator_trace.py` — `import_trails()` new-trail default →
  `permission:"publish"` (durable across the round-trip).
- `website/sw.js` + `website/index.html` — `v94→v95`.
- NEW `brain/output/verify_trails_gold_publish_permission.py` + `.png`; addendum to
  `tasks/20_deferred/data_integrity_publishability.md`; pointer in `handoff/session_context.md`.

Ignored (other sessions' hunks): `export_illustrator_trace.py`, `viewer_core.js`,
`index.html` markup, the 16 `website/*.html` deletions, the geojson geometry bake,
the import-script buildings/waypoints docstrings.

## Tier: full six (publish-zone data — flips `permission` on 130 features)

## Verdicts

```
SEAT: witness        VERDICT: clear
  Re-ran the verifier himself on :8001 — exit 0, 4/4 PASS, 0 console errors; read
  window.AOPViewer.map's real source (130/130 publish) + live queryRenderedFeatures;
  viewed the screenshot (gold network renders on Park); triangulated disk + HTTP.

SEAT: warden         VERDICT: clear
  git diff --cached empty, reflog HEAD unchanged (no add/commit/push); geojson delta
  is permission-only on 130 trails, 0 geometry/other changes; v95 bump follows the
  documented assistant-performs-bump / commit-stays-user precedent.

SEAT: quartermaster  VERDICT: clear
  Reused the existing publish-gate value `permission:"publish"` (init_db.sql:198 +
  gold_publish.geojson) — no invented string; one field added to the existing dict;
  scratch verifier follows the established brain/output pattern (25 siblings), imports
  playwright_base primitives, asserts a posture playwright_verify_trails.py does not.
  C1/C2/C6 structural greps hold.

SEAT: mason          VERDICT: clear
  Non-limiting (opens publishability; no guard/filter/validator); idiomatic one-key
  addition; verifier clean (no littered debug, degrades to null not throw); minimal.

SEAT: scribe         VERDICT: clear
  Record matches ground truth (130 publish, owed items, git gate "commit remains the
  user's"); no overclaim (confidence left "merged truth (traced)", not field-verified);
  voice plain; SFWDA treated as the literal stale value, not an analogy.
```

Non-defect note (Warden + Scribe, resolved): "136 rendered" (paint fragments) vs
"130 source" trails — both correct, were mildly conflatable; the records were tightened
to distinguish rendered-fragments from source-features.

## Result: CLEAR (5/5 worker seats clear, Steward clears the gate)

Owed (not gated, stated in the card): name the 109 numbered trails; sync core/DB
`permission='publish'`+`publish_status='publish'` when Docker returns so the formal
publish view (`gold_publish.geojson`) regenerates with the network. The commit + the
`v94→v95` bump remain the user's git gate.
