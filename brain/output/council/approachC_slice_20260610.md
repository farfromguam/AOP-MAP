# Council receipt — Approach-C slice (gold slice 6, "one writer per served file")

Date: 2026-06-10 · Tier: **full six** (publish-zone data + a migration) · Result: **FULL SIX CLEAR**
Cleared diff hash (`.claude/.council-cleared`): `1786f5d228cfd38d3baa771f0ab5e43c9a02e432`

## Goal reviewed
Make `export_publish_geojson.sh` the single reproducible writer for the 4 served reference files by homing
the CMFS spine in `core.features` COLUMNS via one shared bake helper, unify both editor sinks, loss-free vs
HEAD. The fork (Approach C) was decided by the user 2026-06-10.

## First pass: 3 clear, 2 andon
- **Witness — clear.** Own all-keys semantic diff + live viewer; per-feature loss-free, pure function, eviction, viewer healthy.
- **Warden — clear.** On-farm; HEAD `69fd2d3` untouched; no bump/commit/attribution; owed v60→v61 reported.
- **Quartermaster — clear.** One shared `SPINE_COLS` helper feeds both arms; real eviction (0 of 4 in CONFIG); reference sink reuses the POI sink's pattern (old `highlight_set_sql` removed); structural greps hold (C1=0, C6=0).
- **Mason — andon.** The eviction orphaned dead code in `rebake_canonical.py` (`n_building` + the `trail_join`/`poi_source` join machinery: `TRAIL_CATALOG`/`POI_INDEX`/`poi_match`/`join_name_desc`, 0 callers). Craft, no data risk.
- **Scribe — andon (real data loss).** The per-feature loss-free checks (orchestrator's + the verifier's) never inspected the **top-level FeatureCollection object**. The bake carried forward only `_meta`, silently dropping owner-authored collection-level provenance: buildings `_source`/`_derived`(the "~197 raw FEMA footprints dropped per owner decision" note)/`_generated_by`/`_sources_checked`/`_aop_9_patch_bbox`/`_source_item`/`_source_service`; cemeteries `_source`/`_generated_by`; trails collection `name`; visitor `name`/`_description`/`_sources_checked`. The record's "byte-for-byte / LOSS-FREE" claim never recorded the drop.

## Fixes
- **Scribe fix (data + record).** `export_publish_geojson.sh` both arms now carry forward **every** top-level key (not just `_meta`) — the same stopgap `_meta` already used (durable DB home = the deferred `reference-bake-no-meta-on-fresh-volume` item). Re-baked → top-level `drops=[] adds=[] value-diffs=[]` on all 4 + per-feature still 0/0. `playwright_verify_shadow_refbake_repro.py` gained a `COLLECTION-level top-level keys loss-free` assertion (closes the hole). Record: field inventory qualified to per-feature + new collection-level section; card status log + handoff updated.
- **Mason fix (dead code).** Removed `n_building`, `TRAIL_CATALOG`, `POI_INDEX`, `poi_match`, `join_name_desc` (+ caller + `poi`/`revisit_note` plumbing), and the `trail_join` branch in `facets`. Kept `_load_json` (live at 3 sites) and `SIDECARS` (live in the manifest, byte-identical → no `_schema.json` churn). Proved behavior-preserving: re-baking all 17 rebake-owned files produced byte-identical-to-HEAD output (none `M`).

## Re-review: all three affected seats clear
- **Witness — clear.** Independent top-level comparison (0 dropped/added/value-diff, all 4); twin-safe per-feature (0 mismatches, worst geom 5.0e-10°); live render (counts 5/8/2/2/120, Launchpad+Pavilion, 0 console errors, screenshot); `--check` = `same` for the 5 in-scope files.
- **Mason — clear.** Dead symbols gone (only a historical-prose comment remains); `py_compile` clean; kept symbols still live; the carry-forward + `attrs || SPINE_JSONB` overlay are additive (jsonb_strip_nulls → NULL never clobbers), not limiting.
- **Scribe — clear.** Data drop gone (`_derived` FEMA note preserved verbatim); record honest (byte-for-byte qualified, collection-level section, council entry, handoff updated); owed v60→v61 stated, HEAD still `69fd2d3`.

## Owed (the user's git gate — NOT the council's to clear)
ONE `sw.js`/`#appVersion` **v60→v61** bump covering this whole uncommitted batch (shared with the F4 batch),
at the user's commit. Files: `mvp/scripts/{export_publish_geojson.sh,apply_positioned_features_to_core.py,rebake_canonical.py,fold_sidecars_into_core_features.py,fold_served_enrichment_into_core.py,fold_served_canonical_into_core.py,playwright_verify_shadow_f4_publish_repro.py,playwright_verify_shadow_refbake_repro.py}`,
`website/data/{aop_buildings,aop_cemeteries,aop_trail_network,aop_visitor_context_callouts,publish}.geojson`,
`website/js/panel.js`, `brain/output/approachC_field_inventory_20260610.md` + the G0 screenshots + brain.
