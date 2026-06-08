# Council receipt — description→`description` convergence DONE-REVIEW

Date: 20260608. Steward-chaired. Independent Witness done-review (producer must not self-verify).
Card: `brain/tasks/07_tables/description_blurb_convergence.md`. Witness subagent: a9d6bf66e8a33d02a.

## Verdict: CLEAR (gate cleared by the Steward).

A fresh Witness re-ran all seven end-state checks on the live running system (not the producer's
narration) and CONFIRMED each:
1. DB rename landed — `core.features.description` present, `blurb` column errors (gone),
   `publish.features` exposes `description`, 159 rows / 7 non-null (no loss).
2. Fresh-volume repro — throwaway PostGIS from init_db.sql+seed_core_pois.sql only: `description`,
   no `blurb`, 3 POI rows / 2 with text.
3. Bake value-equality — baked publish.geojson POI `description` set-equal to DB by id (139/140),
   `blurb` absent, no stale `source`/`last_checked`.
4. Viewer rendered-DOM — `playwright_verify_baked_pois_author.py --require-description` PASS, the
   Pavilion subtitle in the live DOM contains "campfire all happen here", 0 console errors; the
   `--require-description` mode genuinely fails on absence (verifier read, not assumed).
5. Editor seed drift killed — served seed `description` == DB; fresh-state editor store carries the
   NEW DB text, zero old "Main pavilion at 1010 Ellis Cove Road".
6. No drift reintroduction — `rebake_canonical --check` resolves the seed canon `description` to the
   NEW text (raw source fixed).
7. Diff coherence — only convergence files dirty; the 5 non-POI reference served files clean/at-HEAD;
   shell bumped v52→v53; no commit made.

Witness left the working tree exactly as found, production DB running, throwaway container removed.

## OWED (the user's git gate, correctly NOT cleared by the producer)
The `git commit` of this diff (16 modified tracked + 3 untracked brain files) carrying the v52→v53
shell bump.

## Full-six done-review over the executed diff (Stop-hook convened /council)

Tier-0 objective gate passed: `node --check` main.js OK; C1 grep 0 non-comment matches; v53 bump
present. Then the worker seats reviewed the executed diff (fresh, prompted to refute):

- **Witness** — CLEAR (the end-state re-verification above).
- **Warden** — CLEAR. Every hunk card-traceable; git gate untouched (HEAD `4ecfffd`, bump owed-not-done);
  Slice-4 scope-down is a legitimate documented `cards_not_gospel` update; no off-farm/HELD work touched.
  Advisory: the cited pg_dump path `/tmp/aop_map_backup_predesc.dump` is gone (tmp eviction) — RENAME is
  reversible by inverse rename + fresh-volume re-bake regardless.
- **Quartermaster** — CLEAR (one physical name; reuse-true; sidecar correctly deferred; sibling
  `core.activities.description` not conflated). Surfaced two findings for the Steward (below).
- **Mason** — CLEAR. Rename complete across every DB writer/reader; permissive (no CHECK/enum/throw);
  live `publish.features` recreated and matches init_db.sql verbatim (observed via pg_get_viewdef).
- **Scribe** — CLEAR. Durable record honest + in-voice; owed (commit + v53) stated; Slice-4 scope change
  recorded with its reason; follow-ups carded.

### Steward adjudication of the two findings (NOT rubber-stamped — both fixed, re-verified)

1. **Orphan verifier** `playwright_verify_baked_pois.py:74,83-85` still read `properties.blurb` (the
   card's own blast-radius named it; I'd only converted the `_author` sibling). FIXED: retargeted
   `blurb`→`description`; re-ran — PASS (POIs carry their DB description, gate holds, 2 features render).
2. **Ellis park_boundary drop (genuine andon).** Verified by observation: the re-baked working-tree
   `publish.geojson` had dropped HEAD's `id=5 park_boundaries "Ellis Cemetery (inholding parcel)"`
   (6→5) and re-serialized all ids. That served-only hand-curated row is the flagged gold gap (not in
   the DB). Shipping it would couple a published-feature removal + id churn into a description commit.
   RESOLVED: restored `publish.geojson` to HEAD (it already serves `description` matching the DB, so the
   v53 viewer fix holds — re-verified `--require-description` PASS against the restored file). The bake
   SCRIPT convergence (Slice 2) is the durable change; the served artifact regenerates at deploy.
   FLAGGED: migrate the Ellis inholding row into `core.features` before the next deploy-bake, or that
   bake drops it.

All six seats CLEAR after the two fixes. Gate cleared; diff hash written to `.claude/.council-cleared`.
Seats: Warden a849e395ef6e732e6 · Quartermaster a75f6c24e122c2c1d · Mason a9aa25a8d249d8d94 ·
Scribe a2f07f76c27a45d0c · (Witness done-review a9d6bf66e8a33d02a).

## Slice 5 done-review (Ellis inholding migration — publish-zone data; user-directed follow-up)

After the user committed the convergence (`5b5fcdd "v53 data mutation"`) and said "continue with that
last bit," the served-only Ellis inholding park_boundary was migrated into `core.features` (new
`mvp/scripts/seed_core_park_boundaries.sql`, idempotent, mounted; live id 201). Fresh seats over the
Slice-5 diff:
- **Witness — CLEAR.** Re-observed: Ellis in core + publish gate; seed clean/idempotent (exit 0, no
  dup, the ON_ERROR_STOP report-query bug fixed); a re-bake yields 6 features incl. Ellis under
  `description` (no `blurb`), POI convergence intact; fresh-volume repro has Ellis with self-seeded
  provenance; served files restored to HEAD; HEAD still `5b5fcdd`.
- **Mason — CLEAR.** Non-limiting (ON CONFLICT DO NOTHING + WHERE NOT EXISTS, no CHECK/throw); idiom
  matches `seed_core_pois.sql`; geom `ST_SetSRID(ST_GeomFromGeoJSON(...),4326)` matches the canonical
  parcel importer; row shape matches the envelope (194).
- **Warden — CLEAR.** Scoped to the one flagged row; envelope (194) not mutated; git gate untouched;
  served files restored; the "envelope still live-only on fresh volumes" flag is honest scope-bounding.
- **Quartermaster — ANDON → re-CLEARED.** Caught that the seed's self-seeded source row diverged from
  the canonical `import_aop_parcel_boundary.sql` definition (would materialize a thinner row on a fresh
  volume, where the import isn't mounted). FIXED: copied the canonical field values verbatim
  (`arcgis_feature_service` / `reference_publish` / `medium` / full license + url + retrieved_on).
  Re-verified on a true fresh volume — the self-seeded source is byte-identical to live, Ellis
  publishes with it linked. Re-review CLEAR.

Slice 5 OWED: the commit of the diff (`seed_core_park_boundaries.sql` new + `docker-compose.yml` mount
+ card + handoff). FLAG: the working-envelope park_boundary (live 194) is still live-only on fresh
volumes — full park_boundaries fresh-volume parity is a separate cleanup.

## Scope note recorded
Slice 4 was scoped from "re-bake seed FROM DB" down to a source-data RECONCILE after observation
showed the full DB→seed re-bake reshapes the editor identity/maturity/tag model = the HELD gold
slice-6 editor-loads-DB collapse. That collapse remains the durable single-source follow-up.
