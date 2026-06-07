# Council review — Gold migration RETIREMENT step (collapse core.pois → core.features)

Date: 2026-06-06 · Tier: full six · Chair: Steward · Verdict: **FULL CLEAR** (no andon)
Card: `brain/tasks/06_going_gold/gold_migration.md` (Retirement step + RETIREMENT CLOSED block)

The loop's last action. Collapsed `core.pois` into the converged `core.features` (layer='poi'). The
correctness crux: dropping `publish.pois` from the bake while leaving the apply path on `core.pois`
would have BROKEN the POI edit path — so the collapse rewired the apply path + the seed too, not just
the bake.

## Verdicts (all six clear)

- **Witness — CLEAR.** Independently re-proved the full rewired pipeline: applied an edit (Pavilion) +
  delete (Ellis) → confirmed it wrote `core.features` (not the deprecated `core.pois`) → baked →
  `--require-author` PASS (edited name+blurb in `published_destinations` as `pubpoi:139` — the
  core.features serial, proving the new source; Ellis absent; 0 console errors). Negative control:
  `--require-author` FAILs with no edit (can't degrade to baseline-PASS). Restored core + files clean.
- **Quartermaster — CLEAR.** The two-table duplicate is structurally collapsed — nothing reads/writes
  `core.pois`/`publish.pois` in the apply/bake/seed path (all target `core.features`/`publish.features`);
  apply reused the one parser (`panel_overrides.py`), no new file; one POI pipeline, one seed. The
  deprecated table + mirrored rows remaining (DROP owed-to-human, no-DELETE rule) is the acceptable
  resolution. *Noted (pre-existing, out of scope):* the old render-bound `playwright_verify_baked_pois.py`
  still narrates core.pois→publish.pois and is invoked by no runner — inert; a human could repoint/delete
  it so a future reader doesn't mistake it for the live POI verifier.
- **Mason — CLEAR.** The C5 / no-silent-drop guarantees survived the rewire: still never throws/skips/
  drops; UPSERT ON CONFLICT (no bare UPDATE); count==input asserted; delete archives (scoped
  `AND layer='poi'` so a POI delete can't archive a building); the seed's old `DELETE FROM core.pois`
  replaced by `ON CONFLICT` (no `DELETE FROM core` anywhere); idempotent; no new CHECK/enum; minimal,
  idiomatic.
- **Warden — CLEAR.** Loop contract #4 honored (no DELETE FROM core; `core.pois` rows kept = 4, mirrored;
  table + view kept with deprecation comments, not dropped). Every hunk traceable to the retirement; the
  loop correctly STOPPED (no slice-6 edits to main.js/panel.js). Git gate untouched (HEAD ce920bd, no
  commit/bump/attribution; no shell asset → no bump owed). Production byte-identical to HEAD (publish.geojson
  6 features incl Ellis). "DROP is owed-to-human" framing correct.
- **Scribe — CLEAR.** Record complete + honest: the RETIREMENT CLOSED block + handoff capture the
  collapse, the edit-path-correctness point, the 5 shipped changes, acceptance a/b/c, 141 features, the
  no-DELETE/deprecate decision, the OWED-to-human DROP, and "loop STOPS / slice 6 HELD." The
  `seed_core_pois.sql` filename-vs-content mismatch is acknowledged in its header. State sums to 141.

## Observable acceptance (all green)

- (a) zero `core.pois` rows unmirrored in `core.features` (= 0).
- (b) `publish.pois` no longer in `export_publish_geojson.sh` (POI arm reads `publish.features WHERE
  layer='poi'`).
- (c) slice-1 author verifier PASS reading POIs from `publish.features` — baseline + `--require-author`.

Final state: `core.features` holds **141 features** (buildings 5 + cemeteries 8 + visitor 4 + trails 120
+ poi 4). Production served files byte-identical to HEAD.

## Owed (human / user's git gate — NOT the loop)

- DROP the deprecated `core.pois` table + `publish.pois` view once confirmed unused (destructive).
- Retire the dormant per-layer legacy writers of the reference served files (slices 2–5 OWED).
- Optionally delete/repoint the inert `playwright_verify_baked_pois.py` orphan.
- The commit + adopting any baked serialization are the user's git gate. Slice 6 is HELD.
