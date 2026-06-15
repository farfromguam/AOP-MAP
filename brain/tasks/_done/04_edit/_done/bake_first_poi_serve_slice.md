# Bake-first POI SERVE slice — SHIPPED

Date: 2026-05-29 · Closed in Sprint 04 triage 2026-05-30

TL;DR:
- This is the **shipped slice** split out of two partial cards during the Sprint
  04 triage. The SERVE half of the star-driven POI pipeline runs end-to-end:
  PostGIS `core.pois` → `publish.pois` gate → baked `publish.geojson` → static
  viewer renders the baked set. Plus the dev-DB fresh-init seed mount that makes
  a new local DB come up with these rows automatically.
- The **remaining** work on both parent cards (the AUTHOR half, the open
  pipeline forks, the full dump/restore mechanism) was routed to
  `10_deferred/` — see "Parents" below.

#aop #04_event_app #poi #pipeline #postgis #bake #done

-----

## Parents (split from)

- `10_deferred/star_driven_poi_list.md` — the one-pipeline design card. The
  bake-first SERVE slice shipped from it 2026-05-29; the AUTHOR half + the open
  forks (authoring surface, localStorage role, artifact shape, dev-time vs prod
  write) stayed open and moved to deferred.
- `10_deferred/dev_db_snapshot_reseed.md` — the POI dev-fixture-in-fresh-DB
  piece shipped from it 2026-05-29 (recorded here); the full DB dump/restore
  mechanism stayed unbuilt and moved to deferred.

## What shipped (2026-05-29, verified)

1. **`core.pois` table** (`mvp/init_db.sql`) — destination POIs as first-class
   rows: `name, kind, blurb, is_destination, status, confidence, permission,
   publish_status, source_id, geom(Point), notes`. `is_destination` is the ★
   axis; `blurb` is the visitor copy that used to live in `aop_poi_index.json`.
   GIST index + `updated_at` trigger registered.
2. **`publish.pois` view** = `is_destination AND permission='publish' AND
   publish_status='publish'` (permission added to match sibling views + the
   northstar publish rule; noted in the SQL comment).
3. **`export_publish_geojson.sh`** UNION extended with `publish.pois` (added
   `kind`/`blurb` columns NULL across the other branches); bakes POIs into the
   single `website/data/publish.geojson` under `layer='poi'`.
4. **Seed `mvp/scripts/seed_core_pois.sql`** (idempotent; owns rows via the
   named source `'AOP bake-first POI seed'`; deletes-by-source then re-inserts).
   3 rows derived one-time from existing files: **AOP Pavilion** + **Ellis
   Cemetery** (`publish`), plus **Proving Grounds (candidate)** left
   `permission='unknown' / publish_status='candidate'` to prove the gate
   excludes it. Result: `core.pois`=3, `publish.pois`=2. (Visitor-support
   callouts deliberately NOT seeded — their polygons are positioned label boxes,
   not real town geometry.)
5. **Fresh-DB seed mount** (`docker-compose.yml`, from `dev_db_snapshot_reseed`)
   — `seed_core_pois.sql` mounted into the db container's
   `/docker-entrypoint-initdb.d/`. PostGIS runs `*.sql` in sorted order on a
   fresh volume; `init_db.sql` (schema) sorts before `seed_core_pois.sql`
   (data), so a brand-new dev DB comes up with the POIs already seeded — no
   manual step. **Verified** in a throwaway fresh-volume container: schema →
   seed leaves `core.pois`=3, `publish.pois`=2; candidate gated out. Only
   affects fresh volumes; an existing `db-data` volume is untouched (apply by
   hand: `docker compose exec -T db psql -U aop -d aop_map < mvp/scripts/seed_core_pois.sql`).
6. **Viewer wiring** (`website/index.html`): `buildPoiGroups()` gained a
   `published_destinations` group fed from `publishDataCache` `layer==='poi'`
   (rendered first; the legacy six-source blocks left untouched). New
   `publish-pois` map circle layer. New group label/order in
   `aop_poi_index.json`.

## Seed cleanup policy (POI fixture)

- `seed_core_pois.sql` is **dev fixture data, not pre-prod truth.** Rows carry
  honest provenance (`permission`/`publish_status`/`confidence`); the candidate
  row intentionally exercises the `publish.pois` gate.
- When real authoring lands (the AUTHOR half), retire this seed or demote it to
  a smoke-only fixture; do not let hand-seeded rows masquerade as authored truth.

## Verification

- `mvp/scripts/playwright_verify_baked_pois.py` — **PASS** (2 baked POIs with
  blurbs, candidate excluded, map layer renders 2, POI tab group renders both,
  no console errors).
- Adjacent suites (`feature_list` / `presets`) show only their documented
  pre-existing failures (publishable-section / OSM-section-move / mobile-overlap);
  `trails` passes.

## Still deferred (NOT in this slice)

- **AUTHOR half** — nothing writes `core.pois` from the editor yet; the seed SQL
  is the only writer. Authoring-surface fork still open. → `star_driven_poi_list.md`.
- **Collapsing the scaffolding** — the legacy buildings/trails/cemeteries/
  visitor/event/editorPois sources in `buildPoiGroups()` still render alongside
  the baked group. → `star_driven_poi_list.md`.
- **Full DB dump/restore mechanism** — only the POI fixture is wired; the
  reviewable export + reseed-into-fresh-DB path is unbuilt. → `dev_db_snapshot_reseed.md`.

All shipped changes were uncommitted at triage time per `ai_rules/no_commits.md`.
