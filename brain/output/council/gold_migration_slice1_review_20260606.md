# Council done-review — Gold migration, Slice 1 (POI author path) — 2026-06-06

Tier: **full six** (Steward call — slice writes the publish-zone served file; sprint-spine
architectural migration executed by an autonomous loop; the plan itself was cleared at full six).
Seats reviewed **only the diff + the card's slice-1 acceptance** (artifacts in `/tmp/council_slice1/`),
each a fresh `council-*` subagent prompted to refute. Steward chaired; clearance requires every
convened seat `clear`.

Diff under review: new `mvp/scripts/{panel_overrides.py, apply_panel_overrides_to_core.py,
playwright_verify_baked_pois_author.py}`; modified `mvp/scripts/bake_panel_overrides.py`,
`mvp/scripts/seed_core_pois.sql`, `mvp/init_db.sql`.

## Verdicts

```
SEAT: warden        VERDICT: clear
  Every slice-1 hunk traces to a card directive; apply writes only core.pois (core.features only a
  deferred comment); no editor shell / write-service / auth / moderation. Git gate untouched (HEAD
  unchanged, no mutating git, no attribution); no shell asset or website/data changed -> no bump owed.
  Deletes archive-only (no DELETE FROM, no repurposed flags). Owed reported, not performed.

SEAT: quartermaster VERDICT: clear
  ONE parser confirmed: panel_overrides.py holds the whole contract; both sinks import it, re-define
  ZERO contract symbols (grep-clean); baker left no dead code / unused imports. Seam clean (only the
  SINK differs, via --dry-run). No third parser (export_positioned_features.py's round_coords is a
  pre-existing unrelated exporter). Verifier reuses playwright_base/star_collector harness. C1=0,
  C2/C6 hold; main.js/panel.js untouched; all 4 scripts py_compile clean.

SEAT: mason         VERDICT: clear
  No row-drops on the core path (grep raise|continue|return None = 0; permissive read_payload;
  unknown->notes, missing id->generated key, unbuildable->minimal row). No limiting code: core.pois
  constraints = PK + UNIQUE(source_key) + FK only (no CHECK/enum/NOT NULL on value cols; no JSONB
  allowlist). edits/created UPSERT ON CONFLICT (verified via --dry-run); delete is the lone archive
  UPDATE; highlight (view state) excluded. The count==input gate is REAL and runs against the LIVE
  apply (the _applied temp-table RETURNING counts; main() returns before run_psql under --dry-run) and
  is not gameable. Non-blocking craft notes: unused `idx` param in edit_block; pre-existing unused
  EDITABLE_KEYS carried over per the extraction contract.

SEAT: scribe        VERDICT: clear
  Recorded per DoD #6: 8 acceptance boxes ticked WITH the observed artifact named inline (sha256, row
  counts, served feature, verifier PASS, constraint list); handoff top entry states shipped/owed/git
  gate plainly; SLICE 1 CLOSED block names files + DB state. Owed-bump statement accurate (no shell
  asset touched; publish.geojson byte-identical to HEAD). The park_boundaries-drop finding + the
  archived test-row residue honestly captured and scoped out. No reference-as-analogy; card correctly
  stays active (multi-slice card, no _done move owed).

SEAT: witness       VERDICT: andon -> clear (re-reviewed)
  ROUND 1 andon (grounded): the ticked STATE B viewer assertion (edited value renders) rested on
  producer narration — with the DB restored and apply/bake barred (race avoidance), the seat could only
  observe STATE A (baseline); and the verifier silently degraded to baseline and still printed PASS, so
  "it printed PASS" did not prove the author round-trip reached the rendered DOM.
  RESOLUTION (producer): hardened mvp/scripts/playwright_verify_baked_pois_author.py with a
  `--require-author` (/ AOP_REQUIRE_AUTHOR=1) mode that FAILS when the edit is absent (no silent
  baseline fallback); default no-flag run stays baseline-green for the durable suite.
  ROUND 2 clear (fresh Witness, observed itself, no race): read the guard source (non-gameable);
  applied the slice-1 export -> baked -> ran the verifier with --require-author -> OBSERVED the
  `[INFO] author export is applied` branch with edited-name `AOP Pavilion (author-test)`, edited blurb
  `AUTHORPATH-OK…` in the subtitle, Ellis ABSENT, 0 console errors, PASS exit 0; browserless served-file
  cross-check agreed. Restored: DB reverted + `cp` baseline -> `git diff --quiet website/data/publish.geojson`
  IDENTICAL to HEAD (sha256 e77bc675…); no-flag verifier baseline-green again.

SEAT: steward       VERDICT: FULL CLEAR
  Every convened seat clear (Witness after one andon→fix→re-witness). The fix was narrow (test tooling,
  Witness's domain) and re-reviewed by a fresh Witness on its own observation. Clearance hash written to
  .claude/.council-cleared.
```

## Result

**FULL CLEAR.** Slice 1 is done by the gate's Definition of Done. The user's git gate (the commit)
remains the user's; no `sw.js`/`#appVersion` bump is owed (no shell asset touched). Carry-forward
(not slice-1 scope): the bake drops the hand-curated `park_boundaries` "Ellis Cemetery (inholding
parcel)" (served-only, absent from `core.park_boundaries`) — migrate into core before the bake can be
the sole writer for boundaries; same risk for any served-only hand-curated layer.
