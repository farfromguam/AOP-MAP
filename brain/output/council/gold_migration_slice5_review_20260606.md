# Council review — Gold migration Slice 5 (trail network)

Date: 2026-06-06 · Tier: full six · Chair: Steward · Verdict: **FULL CLEAR** (no andon)
Card: `brain/tasks/06_going_gold/gold_migration.md` (SLICE 5 CLOSED block)

The last migration slice: all 120 trail-network LineStrings → `core.features`. Pure reuse (trails added
as config to the established importer/verifier/bake), so the new variable was scale (120 features) + the
rich gold `_meta`. The race-avoidance guidance (judge production by `git show HEAD:` content, not
`git status` mtime; producer does the authoritative restore) held — no false andon this round.

## Verdicts (all six clear)

- **Witness — CLEAR.** Re-ran `--layer trails` (PASS, `getSource('aop-trail-network').serialize()` = 120,
  tile-independent, 0 errors); did the marker round-trip himself (marker on trail '15'); confirmed
  `--require-baked` FAILs when absent; confirmed gold `_meta` (about/color_legend) carried + per-feature
  `color` preserved; gate = 0; restored byte-identical to HEAD.
- **Quartermaster — CLEAR.** No new file (the two scripts are slice-2/3 artifacts reused); trails is a
  single LAYERS config row + one REFERENCE_LAYERS token, not a code branch; one importer / one generic
  verifier / one bake loop over all four reference layers; no orphan references.
- **Mason — CLEAR.** 120/120 preserve `color`/`difficulty`/`trail_number` in attrs; all LINESTRING (no
  coercion); pg_constraint p/u/f only (no CHECK/enum); `-At` bake handles 120 without truncation; gold
  `_meta` carried forward not flattened; count==input asserted (no silent drop).
- **Warden — CLEAR.** Config-only + on-farm; git gate untouched (HEAD ce920bd, no commit/bump/
  attribution); production byte-identical to HEAD incl. publish.geojson's 6 features (Ellis intact);
  trails permission stays reference ('SFWDA paper map — permission TBD'), publish.features trails = 0;
  legacy-writer retirement correctly deferred.
- **Scribe — CLEAR.** Card ticks + CLOSED block accurate (source id 12, gold _meta carry, 120/120,
  round-trip on '15', NEXT=Retirement); handoff names "all four reference layers = 137"; provenance
  matches (id 12, reference); recipe table points at the generic `--layer trails`; production restored
  to HEAD (sha256 match — the `git status` M was mtime-only); PRODUCTION ADOPTION warning present.

## State after slice 5

`core.features` holds all four reference layers: buildings 5 + cemeteries 8 + visitor 4 + trails 120 =
**137 features**. `publish.features` = 0 (all reference layers correctly out of the publish zone).
Production served files byte-identical to HEAD. Next: the Retirement step (collapse `core.pois` into
`core.features`), then STOP — slice 6 is HELD.
