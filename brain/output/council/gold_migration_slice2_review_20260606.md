# Council review — Gold migration Slice 2 (`core.features` + buildings)

Date: 2026-06-06 · Tier: full six · Chair: Steward · Verdict: **FULL CLEAR**
Card: `brain/tasks/06_going_gold/gold_migration.md` (Slice 2)

## Two convenings

This slice was reviewed twice, per the user's "consult the council at each stage":

1. **Design consult (pre-build, full six).** Convened over the slice-2 *design fork* before any
   code. Three andons, all folded in before building:
   - **Witness andon (load-bearing):** the card's premise that `map.on('load')` never fires headless
     is FALSE (verified on :8001). It fires; tiles block only paint/`queryRenderedFeatures`. So a map
     source's loaded data IS readable tile-independently via
     `getSource('<id>').serialize().data.features`. → corrected the Observable acceptance standard +
     Loop-contract #5 (propagates to slices 3–5).
   - **Quartermaster andon:** do NOT make the bake a 4th writer of `aop_buildings.geojson`. →
     resolved: the bake writes the file the viewer already reads (no repoint, no shell-asset change);
     the 3 legacy writers stay dormant (out of the day-of loop) with an explicit owed-note for
     retirement (the `export_positioned_features.py` branch can only go after a buildings apply-door
     exists).
   - **Mason andon ×2:** publish views/bake drop `attrs` by omission → `publish.features` must
     `SELECT attrs` and the bake must spread it; the baked-file assertion must check an attrs *value*,
     not just count. Both folded in.
   - **Warden + Scribe cleared** with conditions (annotate-don't-overwrite the card; true reference
     permission; reference-tier source_register row; carry the legacy retirement as a note).
   - **Root call (Steward, brain-settled):** buildings are reference-tier (FEMA "no warranty" /
     private "presence only", `_meta.maturity='silver'`) — the publish gate correctly excludes them.
     The card's "publish.geojson carries the buildings" drifted from the northstar; corrected so
     reference layers bake to their OWN served file. The same holds for slices 3–5 (cemeteries,
     visitor callouts, trails — all non-`publish` permission).

2. **Done-review (post-build, full six).** Convened over the actual diff.
   - **Witness — CLEAR.** Independently re-ran the verifier (PASS, 0 console errors), re-did the
     `--require-baked` marker round-trip (marker travels core→bake→serve→viewer), confirmed the
     verifier FAILs-when-marker-absent (cannot silently degrade to baseline-PASS), confirmed the
     `getSource(...).serialize()` read is tile-independent, and restored the tree clean.
   - **Quartermaster — CLEAR.** One bake extended (not a parallel script); legacy writers absent
     from the diff + not invoked by the loop; `import_layer_to_core_features.py` genuinely generic
     (reuses the `apply_panel_overrides_to_core.py` idiom, not a duplicate); ONE `core.features`
     table; `git diff website/` empty (no C1/C2/C6 risk).
   - **Mason — CLEAR.** Both design andons fixed (verified on a live re-bake: zero prop keys
     dropped/added, `facility_role` survived); `pg_constraint` on `core.features` = p/u/f only (no
     CHECK/enum); no row-drop/throw/skip/coerce; `geometry(Geometry,4326)` is the right mixed-geom
     choice; importer idempotent with count==input asserted.
   - **Warden — CLEAR.** Card annotated not overwritten; buildings keep true FEMA permission (DB
     query); publish.features gate unchanged + returns 0 buildings; git gate untouched (HEAD
     unchanged, no commit/bump/attribution); no shell asset → no bump owed; every hunk
     slice-2-traceable; legacy retirement correctly deferred.
   - **Scribe — ANDON then CLEAR (re-review).** 5 record gaps (served files left dirty by parallel
     seats; missing `data_maturity_tiers.md` `_meta`-carry note; inaccurate "preserved below the
     divider" wording; an over-claimed slice-1-caveat propagation; missing handoff entry). All 5
     fixed; re-review confirmed each by observation + the prior-good items (source_register row 9
     reference-tier; the in-card Observable correction durable for an autonomous re-read).

## Observed acceptance (artifacts)

- Baked-file assertion: regenerated `aop_buildings.geojson` prop+geom equivalent to HEAD (5/5, key
  sets+values identical, geom maxdelta < 1e-6), `facility_role` survived.
- Viewer assertion: `playwright_verify_baked_buildings_author.py` (generalized in slice 3 into
  `playwright_verify_baked_reference_author.py --layer buildings`) baseline PASS + `--require-baked`
  PASS (marker round-trip), 0 console errors.
- Gate works: `publish.features WHERE layer='buildings'` = 0; `publish.geojson` byte-identical to HEAD.
- Slice-1 POI verifier unregressed (PASS). Production served files restored byte-identical to HEAD.

## Owed (next increment, NOT slice 2)

Retire the 3 dormant legacy writers of `aop_buildings.geojson` once the buildings apply-door exists
(`apply_panel_overrides_to_core.py` `layer='buildings'` + a layer-aware geom builder). The commit is
the user's git gate (no version bump owed — no shell asset touched).
