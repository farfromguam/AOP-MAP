# Council review receipt — `gold_migration.md` (Going Gold spine plan)

Date: 2026-06-06 · Chair: Steward · Tier: **full six** (high-risk: sprint-spine
architectural migration to be executed by an autonomous ralph loop) · Artifact reviewed:
`brain/tasks/06_going_gold/gold_migration.md` (+ `_readme.md`, `schema_conformance_audit.md`).

**Outcome: FULL CLEAR after 4 rounds.** Every seat ran in a fresh, independent context,
prompted to refute, grounded in the real repo. The plan was hardened materially between rounds —
this receipt is the artifact backing "the council cleared it," not a narration.

## Round-by-round

**Round 1 — all six pulled andon** (the plan was nowhere near loop-safe as first written):
- **Witness** — the cited proof `playwright_verify_baked_pois.py` is NOT headless
  (`rendered_count(['publish-pois'])==2` → `queryRenderedFeatures`; `wait_until="networkidle"`),
  so "SERVE half PROVEN" was overstated; DB bring-up unstated; slices 2–6 acceptance hand-wavy.
- **Scribe** — "match by a stable key" ambiguous (`core.pois.id` is serial; exports key
  `<source>:<id>`; `created[]` has no serial) → a loop guesses differently each iteration; no
  run-commands; no per-slice record step.
- **Quartermaster** — "sibling sharing payload parsing" unenforced → loop re-implements the
  parser (second copy); `core.pois`/`core.features` coexist with no retirement verifier.
- **Mason** — "deleted = archive" but `core.pois` has no archive column + parent script
  hard-deletes; nothing forbade the apply path throwing/skipping (silent row-drop).
- **Warden** — slice 6 unbounded theme; slices 3–5 one paragraph; a checklist line told the loop
  to bump VERSION (the user's git gate).

**Round 2** — full rewrite. **Warden & Scribe CLEAR.** Witness & Mason held:
- Witness — slices 2–5 still pointed at render-bound verifiers; slice 2 asserted the pre-bake
  source file; slice-1 refactor cited a non-existent baker verifier.
- Mason — the plan reused the parser but didn't tell the loop to STRIP its inherited
  skip/throw/return-None drops from the DB sink.

**Round 3** — added the Observable-acceptance standard (baked-file assertion + star_collector
author verifier; no render/closure), fixed the phantom verifier (fixture-diff), sealed the
parser drop branches. **Witness & Quartermaster CLEAR.** Mason held:
- Mason — a narrower instance survived: `edits[]` bare `UPDATE … WHERE source_key` is a silent
  zero-row no-op (lost edit) on a non-matching key; the grep can't see it.

**Round 4** — `edits[]` made an upsert (`ON CONFLICT (source_key) DO UPDATE`), bare UPDATE
banned, count==input acceptance added; folded in Quartermaster's shared-verifier-seam tightening.
**Mason CLEAR.**

## Final verdicts (the receipts)

```
SEAT: warden        VERDICT: clear (R2)  — slice 6 HELD+bounded; VERSION line reworded to owed-not-performed; slices 3–5 split + retirement its own gated step; clear STOP.
SEAT: scribe        VERDICT: clear (R2)  — match rule exact (source_key); literal Run-it block; per-slice Record-on-green; slices named with source+verifier; voice in register.
SEAT: quartermaster VERDICT: clear (R3)  — one panel_overrides.py parser, two sinks (no copy); single extended bake; retirement collapses the two-table dup; new author verifiers are a justified DIFFERENT artifact (render-bound ones can't be headless); C1/C2/C6 hold.
SEAT: witness       VERDICT: clear (R3)  — Observable-acceptance standard = baked-file assertion + star_collector author verifier; no networkidle/queryRenderedFeatures/publishDataCache; refactor proven by fixture diff. (NEXT: re-witness on the first slice's REAL verifier output before trusting "green.")
SEAT: mason         VERDICT: clear (R4)  — all three branches UPSERT; bare UPDATE banned; deleted→archive (no DELETE); R13 closed (unknown→text, missing→default, unparseable→notes, never zero-row); free-form JSONB, no CHECK/enum; no over-build.
SEAT: steward       VERDICT: clear       — serves the locked northstar (PostGIS spine → bake → static read-only V1; V2 deferred); provenance carried; core fork moved slowly (4 rounds).
```

## Standing conditions the loop inherits (from the seats' NEXTs)

- **Witness:** the apply script + the 5 `playwright_verify_baked_*_author.py` do NOT exist yet —
  the loop writes them. Re-witness on the FIRST slice's real verifier output before any "green"
  is trusted; "the script printed PASS" is not observation until the verifier is the headless-safe
  one and its output is read.
- **Mason:** verify the `count == input` acceptance executes against a live apply before slice-1 green.

## Provenance

Seats were spawned as fresh `council-{warden,witness,quartermaster,mason,scribe}.py` subagents
(resumable ids in the 2026-06-06 session transcript). This review did not commit and did not
touch `website/`/`mvp/` — it hardened the brain plan only. The user's git gate (commit + the
ralph loop trigger) is next, and is the user's.
