# Data Integrity + Publishability

> **Deferred — Sprint 04 triage (2026-05-30).** Only the positioned-feature bake
> sub-item is done (marked `[x]` below; also recorded in `_done/misc_4.md`).
> Everything else is **deferred because** it is gated on outside truth: real
> source-backed trail/trailhead data (rides on the SFWDA extraction), the
> acreage reconciliation, the DEM upgrade decision, the POI placeholder
> resolutions, and the synthetic-activity honesty call. Also owns the
> building-tag promotion routed out of `_done/misc_4.md` (1033 farmhouse / 880
> park offices / 1010 pavilion → native footprints), gated on source verification.

The viewer chrome is ahead of the trusted data spine.

Sprint 04 needs to pay down the publishability blockers before the event app
adds another layer of confidence theater.

#aop #04_event_app #data_integrity #publishability #sources

-----

## Source

- `../03_event_app/_done/sprint_02_critique_followups.md`
- `../03_event_app/_done/left_panel_poi_browser.md`
- `../03_event_app/_done/viewer_polish_carryover.md` Lane 7 pointer
- `../01_mvp/_readme.md` Immediate next work
- `../01_mvp/_done/community_trails_import.md`
- `../../northstar/source_register.md`

## Work

### Real Trails + Trailheads

- [ ] Replace demo/smoke `trail_centerlines` and trailheads with real source-backed AOP data.
- [ ] Promote at least one real source-backed centerline before declaring V1 publishable.
- [ ] Continue SFWDA numbered-trail-name research on the community-trails card and promote only when source posture is clean.
- [ ] Connect QGIS to `localhost:55432` and inspect source/feature tables if that is still undone locally.

### Acreage Reconciliation

- [ ] Reconcile AOP's 600+ acre public claim against the parcel envelope, deed acreage, and any related holdings.
- [ ] Record the answer in the bounds/source docs before the viewer leans on a hard acreage claim.

### DEM Source

- [ ] Swap the AWS Terrarium DEM for AOP-specific USGS 3DEP 1 m derived tiles when the current 10 m terrain stops being good enough.
- [ ] Extend terrain verifier coverage when the new source lands.

### POI Gap Pass

The Sprint 03 POI tab shipped with `info needed - revisit` placeholders.

- [ ] Resolve Event anchor placeholders: `#proving-grounds`, `#north-technical`, `#night-checkpoint`, `#photo-waypoint`.
- [ ] Resolve building placeholders: 1033, 665, and 880 Ellis Cove Road.
- [ ] Resolve cemetery placeholders: Gilliam, Bible, Tate.
- [ ] Promote synthetic activity segment labels to real named trails only after the trail-name source work lands.
- [ ] Decide whether `aop_poi_index.json` `owed_work` should render in the POI tab for non-coder review.

### Positioned-feature bake (DONE 2026-05-30)

- [x] Bake brand-logo + region-callout drag/resize positions to disk so they
      survive a data reset. `mvp/scripts/export_positioned_features.py` reads the
      viewer's "Export all" / section-Copy JSON and writes the moved geometry
      (+ logo `icon_size`) into `website/data/aop_brand_logos.geojson` and
      `website/data/aop_visitor_context_callouts.geojson`. These two layers are
      file-based, not PostGIS, so they are out of scope for
      `export_publish_geojson.sh`. Close-out: `misc_4.md`.

### Synthetic Activity Boundary

- [ ] Decide whether first-party activity hotspots are clearly synthetic/test-grade or ready for visitor-facing "activity" treatment.
- [ ] If still synthetic, badge popups and hot-button fallback honestly or hold the fallback until real GPX backs it.

## Acceptance

- [ ] Publishable trail/trailhead layers no longer depend on demo geometry.
- [ ] Acreage claim has a documented source-backed answer.
- [ ] Terrain source posture is either upgraded or explicitly deferred with reason.
- [ ] POI placeholder count is reduced or each remaining placeholder has a named owner/source path.
- [ ] Activity-hotspot UI cannot be mistaken for live or real-user data when the source is synthetic.

-----

## Addendum 2026-06-14 — trail PERMISSION blocker resolved (user directive)

User (verbatim): *"these guys give permission for people to put the map up on the
internet, and we are tracing the unmapped trails manually. the trails should be
rendering and gold for all intensive purposes."*

This resolves the **permission** half of "Real Trails + Trailheads" above. Two
facts the prior assessment lacked: (1) **AOP (the landowner) grants public web
publishing** of the map — so the `"SFWDA paper map — permission TBD"` string on the
trail network was **stale**, not a real blocker; (2) the trails are **first-party
manual traces** (the satellite/Affinity round-trip), legitimately gold-tier
provenance, not a copy of SFWDA's paper map.

**Done:**
- `website/data/gold_aop_trail_network.geojson` — all **130** trails set to
  `permission: "publish"` (was 120 × `"SFWDA paper map — permission TBD"` + 10 ×
  missing key). `"publish"` is the project's own publish-gate value
  (`publish.features WHERE permission='publish' AND publish_status='publish'`;
  matches the boundary/POI convention already in `gold_publish.geojson`).
- `mvp/scripts/import_illustrator_trace.py` `import_trails()` new-trail default now
  sets `permission: "publish"` — so a re-import of the Affinity master carries the
  clean posture forward (matched trails carry it by name already; freshly-traced
  unmapped trails come in publish-clean, not thin/`TBD`). **Durable across the
  round-trip.**
- Verified by observation on `:8001` —
  `brain/output/verify_trails_gold_publish_permission.py` **4/4 PASS**, 0 console
  errors: trail layer visible on Park default, 136 rendered paint-fragments (the
  130 source trails fanned across tiles), the LIVE viewer's loaded source reads
  `permission=publish` on all 130 source features, no `TBD` left.
  Screenshot `brain/output/trails_gold_publish_permission.png` shows the network
  rendering. Served-data change → **v94→v95** bump performed (`sw.js` + `#appVersion`);
  **commit remains the user's**.

**Still owed (NOT permission — these are real, and smaller now):**
- **Names** — 109 of 130 trails are bare numbers (21 named). Content gap the user
  is actively closing via tracing; not a publish blocker (a numbered candidate can
  publish).
- **Confidence stays honest** — `confidence` left as `"merged truth (traced)"`
  (traced from current imagery), NOT inflated to field-verified. Field GPX would
  upgrade it; the trace is the current basis.
- **Core/DB sync (durability gap, recurring)** — `core.features` trails still carry
  the old permission; when Docker returns, set `permission='publish'` AND
  `publish_status='publish'` so the **formal publish view** (`gold_publish.geojson`,
  currently 4 features, 0 trails — DB-baked, not hand-edited) regenerates with the
  trail network. The read viewer already draws trails from
  `gold_aop_trail_network.geojson` directly, so rendering does not wait on this.
  **⚠️ See the 2026-06-15 addendum below — this instruction can't be run as written;
  the export pipeline diverged from the served filenames and the DB trails are stale
  vs the file.**

-----

## Addendum 2026-06-15 — Docker came back; DB↔served reproducibility is BROKEN (diagnosed, no DB change by user direction)

User: *"docker is up now"* (after the prior session flagged "core.features owed when
Docker returns"). Brought PostGIS up (`mvp-db-1` on `:55432`), inspected the converged
spine by observation (`core.features` 160 rows, `publish.features` view 6 rows — the old
per-layer `core.park_boundaries` etc. that `./cwc` still checks were folded into
`core.features` on 2026-06-07, so `./cwc`'s "missing" lines are a stale check, not a real
gap). Before mutating the canonical DB I traced the bake pipeline end-to-end and found the
owed instructions **rest on an assumption that is no longer true.** Offered the user
full-reconcile / scrubs-only / diagnose-only; **user chose DIAGNOSE ONLY — no DB changes
made this session** (the DB is byte-for-byte as found: 160/6). This addendum is the record.

**THE ROOT FINDING — the GeoJSON export pipeline silently diverged from the served files
at the medallion `gold_` rename (commit `91a017e`).** `mvp/scripts/export_publish_geojson.sh`
still writes `publish.geojson` + `aop_{buildings,cemeteries,visitor_context_callouts,trail_network}.geojson`
(its `OUTPUT_FILE` + `REFERENCE_LAYERS`), **none of which exist on disk** — the viewer reads
`gold_publish.geojson` + `gold_aop_*.geojson`. So running the export today **creates orphan
old-named files; it does NOT regenerate the served gold.** Consequence: **the served gold
GeoJSON layers are currently NOT reproducible from the DB** — they have become file-maintained,
which breaks the going-gold slice-6 "served = pure function of the DB + the script" guarantee
(`06_going_gold/gold_migration.md`). The medallion rename updated the served files and the
trace round-trip scripts (per the 2026-06-14 handoff) but never touched `export_publish_geojson.sh`
or the `_schema.json` store-of-record keys. **The schedule arm is the exception — it bakes to
`aop_event_schedule.json` (NOT renamed), so that pipeline + `core.events`/`core.event_meta` are
still connected.**

**Stale-DB inventory (DB vs the curated served gold — observed, not the prior session's notes):**
- **G-Central still in `core.features`** — poi id 139 (`AOP Pavilion`) `attrs.event_location`
  carries `label:"AOP Pavilion / G-Central"`, `map_label:"G-Central"`, `confidence:"medium"`;
  building id 2 (`Pavilion`) `description` starts `"G-Central. The on-site building…"`. Served is
  fully clean (`grep -ri g-central website/data` → none). Exact served targets staged: schedule
  `#pavilion` → `label:"Pavilion (base camp)"`, `map_label:"Pavilion"`, `confidence:"high"`; building
  → `"AOP Pavilion. The on-site building that hosts registration, awards, and the campfire. Footprint
  from FEMA structures data; AOP confirms it's the pavilion."` (G-Central → AOP Pavilion is the only
  delta). This scrub matters even with the GeoJSON pipeline broken, because the **schedule** arm is
  connected — a schedule re-bake would otherwise regress G-Central back into `aop_event_schedule.json`.
- **Monteagle callout** `description` = the old `"Plateau services, ~30 min northwest via I-24…"`;
  served has the new `"The plateau cluster up the mountain…"` copy (shipped this week).
- **Trail data-model FORK** — `core.features` has **120 stale `trails`-layer rows** (all
  `permission='SFWDA paper map — permission TBD'`, `publish_status` NULL); the served
  `gold_aop_trail_network.geojson` has **130 file-based traces** (the Illustrator round-trip is the
  live authority). The owed "set the 120 to publish" would publish a **stale, incomplete** set, AND
  bakes to the orphan `aop_trail_network.geojson` anyway. Real options: (a) re-import the 130 traces
  into `core.features` so the DB is the store-of-record, or (b) keep trails file-based and retire the
  DB's stale 120 from the publishable set. Not a mechanical UPDATE.
- **Saturday-Activity segments still pass the publish gate** in the DB (`publish.features` shows
  `trail_centerlines | Saturday Afternoon Activity (segment 1/2)` + `field_tracks` twins
  `reference_publish`); served `gold_publish.geojson` already dropped them (served-only curation).
- **Cemeteries are already correct in the DB** — only Ellis is published (`permission/publish_status
  = publish`); Bible/Gilliam/Tate sit unpublished (empty gate) = bronze reference, matching the served
  posture. Less owed than the prior note implied.

**Recommended path when the user greenlights (I have the exact served copy staged to execute fast):**
1. `pg_dump` `core.features` first (reversibility; runbook "do not lose local data").
2. Reconcile DB content to the curated served truth: G-Central→Pavilion, new Monteagle copy, Saturday
   segments out of the publish gate.
3. Decide the trail fork (recommend: re-import the 130 traces so the DB reproduces the network).
4. **Repair the pipeline** — apply the `gold_` rename to `export_publish_geojson.sh`
   (`OUTPUT_FILE` + `REFERENCE_LAYERS`) and the `_schema.json` store-of-record keys.
5. Prove with `export_publish_geojson.sh --check` (NON-WRITING — bakes to `.check` side-paths and
   byte-compares) that the served gold reproduces from the DB before any real write. Only then run it
   for real.

**No fire:** the served viewer is unaffected — the GeoJSON layers are file-maintained and correct;
this is about restoring DB→served reproducibility (the source-led promise), not a visible bug.
