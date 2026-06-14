# Council done-review — v90 gold-promotion + pins + publish-curation batch

Date: 2026-06-14
Chair: Steward. Tier: full six (publish-zone data + broad file-rename sweep).
Card: `brain/tasks/01_mvp/gold_promotion_pins_curation_v90.md`
Scope: this task's claim only (tree commingled with the cemetery card + other sessions).

## Goal (one line)
Land the user's 9-item batch on the read viewer + served data: gate location pins per
the user's preset call, promote the two silver files to gold (rename + sweep), curate
the publish group, unname `sfwda-*` trails, number Launchpad, star the Shower House.

## Verdict receipts (as synthesized by the Steward)

SEAT: quartermaster
VERDICT: clear
EVIDENCE: pins gate extends `applyPreset`/`setLayerVisibility` (pins were never in
PRESET_LAYERS — nothing to duplicate); silver→gold reused `stamp_maturity.MATURITY` +
the rename pattern (hand `mv`+sweep justified — the script renames canonical→prefixed,
not silver→gold); Jackson Point follows the AOP-Pavilion publish-poi schema; one
`trailDisplayName`, guard added in place. C1/C2/C6 greps at target; `node --check` clean;
0 residual `silver_*` refs.

SEAT: witness
VERDICT: clear (andon resolved)
ISSUE (was): "20/20" receipt was false against the on-disk code (code shipped Park+Topo,
record/verifier still said Park+Satellite).
RESOLUTION: the user reversed directive #1 in-place; verifier flipped to Park+Topo; fresh
observed re-run on `:8001` = 20/20, 0 app console errors (lone external `tnmap.tn.gov`
satellite-tile flake in headless is not an app error). Receipt now matches the running system.

SEAT: warden
VERDICT: clear (andon resolved)
ISSUE (was): directive #1 shipped inverted vs the directive as originally stated.
RESOLUTION: the user reversed the directive itself (verbatim quote on the card); the code
is the user's final call. No mutating git (HEAD unchanged), no attribution, the v89→v90
bump performed-not-committed (commit is the user's gate). Cemetery-card hunks correctly
scoped out.

SEAT: mason
VERDICT: clear (andon resolved)
EVIDENCE: pins gate is preset-driven visibility via guarded `setLayerVisibility` (never
throws, drops no source rows — not a C5 limiter); `trailDisplayName` guard replicated 7/7
cases (avoids "1 1 Launchpad", preserves all prior outputs); the 20 name:null edits + the
publish feature removals are user-directed DATA edits, not code filters; Shower House star
composites with the existing `highlight` gate; no dead code. Pins direction = user reversal.

SEAT: scribe
VERDICT: clear (andon resolved)
EVIDENCE: card RESOLVED→SHIPPED with the user's reversal quoted + acceptance result + the
artifact named; handoff corrected to Park+Topo + the council clearance; `data_maturity_tiers.md`
reads gold=11/silver=0 with the promotion explained; durability gap (raw/publish + PostGIS)
and the commit/v-bump git gate stated plainly; prose in the user's plain voice.

## Result: FULL CLEAR.
The contested pin flip was separately cleared by a core-three council
(`pins_topo_not_satellite_20260614.md`). The 8 data directives were verified throughout.
Clearance marker refreshed (best-effort; goes stale on the next concurrent edit — the
durable authority is the card verdict above). The commit + the v90 bump remain the user's git gate.
