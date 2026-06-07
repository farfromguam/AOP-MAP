# Council review — Gold migration Slice 4 (visitor callouts)

Date: 2026-06-06 · Tier: full six · Chair: Steward · Verdict: **FULL CLEAR**
Card: `brain/tasks/06_going_gold/gold_migration.md` (SLICE 4 CLOSED block)

Slice 4 migrated the visitor-context layer (2 `visitor_callout` polygons + 2 `brand_logo` points) — the
first layer the viewer splits into TWO map sources, and the one that surfaced a real bake bug.

## Done-review verdicts

- **Witness — CLEAR.** Re-baked + confirmed the embedded-newline `label` is preserved (real `\n`, not a
  literal `\\n`); regression-checked buildings + cemeteries still prop-faithful after the shared
  COPY→SELECT change; re-ran `--layer visitor` baseline + did the `--require-baked` round-trip himself
  (marker on the AOP-badge logo); confirmed `publish.features` visitor = 0; restored + clean.
- **Mason — CLEAR.** Verified the COPY→SELECT fix with `od -c` (COPY emitted `\ n`, the bug; `-At`
  emits a real 0x0a) and an adversarial attr (backslash + quote + tab + emoji + embedded JSON all
  survive `-At` byte-correct) — `-At` is the correct raw-JSON emitter; COPY's TEXT format was
  double-escaping. Multi-source verifier loop is single-path; no limiting code; latent publish.geojson
  COPY risk correctly noted in-script.
- **Quartermaster — CLEAR.** Still one importer, one generic verifier (visitor is a LAYERS config row
  with a multi-source list, not a new file), one reference-bake loop (the fix applied once). No orphan
  references; no new app surface.
- **Warden — ANDON → CLEAR (re-review).** Andon: served tree dirty + publish.geojson regressed (Ellis
  park_boundaries dropped) vs the record's "restored byte-identical." Root cause: a parallel-seat race
  (Witness + Mason re-baked + restored concurrently; Warden read a transient mid-race state). Resolved:
  producer did the authoritative post-council restore (all 4 served files byte-identical to HEAD,
  publish.geojson back to 6 features incl Ellis), and a standing PRODUCTION ADOPTION warning was added.
  Re-review confirmed clean by `git show HEAD:` content + the warning present; git gate untouched.
- **Scribe — ANDON → CLEAR (re-review).** Same race-surfaced dirtiness + a record-precision demand.
  Resolved: the standing warning promotes the publish.geojson-not-bake-safe finding (slice-1, now
  triggered by every bake) and clarifies the re-serialization nuance (the bake minifies; "byte-identical
  to HEAD" = production LEFT at HEAD, not adopted). Re-review confirmed the tree byte-identical to HEAD
  (sha256 match) and the warning captures both points.

## The real bug slice 4 caught (and fixed)

A callout `label` carries embedded newlines. The reference bake's `COPY … TO STDOUT` (TEXT format)
backslash-escapes them — JSON `\n` → literal `\\n`, corrupting the newline. The baked-file assertion
(which checks attrs **values**, not just counts — the Mason condition from the slice-2 design consult)
caught it. Fixed by switching the reference-layer bake to a plain `SELECT … -At` (psql emits the json
raw). The pre-existing `publish.geojson` `COPY` has the same latent risk (noted in-script; no published
feature carries a newline today).

## Standing items promoted to the card

- **`publish.geojson` is not yet bake-safe** — a full bake drops the served-only Ellis `park_boundaries`
  (slice-1 finding). Restore to HEAD after a bake until the polygon is migrated to `core`; do not commit
  the leaner bake. (The reference layers have no such gap.)
- **Producer does the authoritative restore after the council** — parallel review seats that re-bake can
  leave transient working-tree dirt; judge production by `git show HEAD:` content, not `git status` mtime.

## Owed

Per-layer legacy-writer retirement (same as slices 2/3). The commit + any adoption of the baked
serializations are the user's git gate.
