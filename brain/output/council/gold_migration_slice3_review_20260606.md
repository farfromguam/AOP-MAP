# Council review — Gold migration Slice 3 (cemeteries)

Date: 2026-06-06 · Tier: full six · Chair: Steward · Verdict: **FULL CLEAR**
Card: `brain/tasks/06_going_gold/gold_migration.md` (Slices 3–5 + the SLICE 3 CLOSED block)

Slice 3 reuses the slice-2 pattern for cemeteries (the first migrated layer whose features are NOT
unique on a single id, and which carries a non-commercial burial roster). Done-review, full six, fresh
adversarial seats — each re-ran the verifier/round-trip/queries independently.

## Verdicts

- **Witness — CLEAR.** Re-ran `--layer cemeteries` (PASS, tile-independent `getSource(...).serialize()`),
  re-did the `--require-baked` marker round-trip himself (marker authored→baked→appeared on Ellis),
  confirmed `--require-baked` FAILs when absent, and confirmed the **northstar license boundary**:
  `publish.features WHERE layer='cemeteries'` = 0 and the publish.geojson carries NO roster data (the
  only "cemetery" hit is the unrelated publish-tier "Ellis Cemetery" POI). **NEXT (folded into the
  card):** make restore-and-assert-`website`-clean part of every slice's green-stop — the bake rewrites
  served files in place and the loop must not end dirty.
- **Quartermaster — CLEAR.** Verifier consolidation is a genuine de-duplication (one generic
  `playwright_verify_baked_reference_author.py`, LAYERS config; the buildings-specific file deleted, no
  orphan references — all 4 remaining mentions are intentional historical notes); composite `--id-field`
  is a clean generalization (no cemeteries special-case); no parallel bake/table; no `main.js` edit.
- **Mason — CLEAR.** `source_key_for()` never throws/skips/drops (missing field → generated key + flag);
  8/8 unique composite keys (no collision drop); mixed geom preserved (Point/Polygon/MultiPolygon, no
  coercion); every property incl. the full burial roster preserved verbatim in `attrs`; no CHECK/enum;
  generic verifier single-path.
- **Warden — CLEAR.** License boundary holds (roster only in `core.features.attrs` + the reference
  served file, never publish; source row 10 reference-tier). Git gate untouched (HEAD = `ce920bd`, no
  commit/bump/attribution, no `website/` change → no bump owed). Deleting the uncommitted slice-2
  buildings verifier to fold it into the generic is legitimate reuse, not churn. **Advisory:** a stray
  pre-existing `brain/output/council/sprint07_tables_review_20260606.md` edit sits in the tree —
  unrelated to slice 3; the user should keep it out of a slice-3 commit.
- **Scribe — CLEAR.** Card + handoff + slice-2 receipt all updated for the verifier rename (no stale
  pointer to the deleted file); source_register id 10 matches the record; voice plain/committed.

## Observed acceptance

- Baked `aop_cemeteries.geojson` prop+geom equivalent to HEAD (8/8, key sets+values identical, geom
  maxdelta < 1e-6), `_meta` `reference` carried; Ellis `burial_count=12`/`named_burial_count=9` survived.
- Viewer `--layer cemeteries` baseline PASS + `--require-baked` round-trip PASS, 0 console errors.
- `publish.features WHERE layer='cemeteries'` = 0 (roster out of the publish zone). Slices 1+2
  unregressed. Served files byte-identical to HEAD (production untouched).

## Owed

Per-layer legacy-writer retirement (same as slice 2; cemeteries' served file also has dormant
`rebake_canonical.py`/`export_positioned_features.py` writers, out of the day-of loop). The commit is
the user's git gate (no version bump owed).
