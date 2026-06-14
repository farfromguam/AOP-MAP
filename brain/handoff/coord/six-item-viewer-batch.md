---
session: six-item-viewer-batch (opus — viewer fixes + medallion tiers)
status: done
claim: website/js/viewer_core.js (display_name + outline removal + event/popup + auditProductionTiers), website/js/panel.js (MATURITY_LABEL bronze), website/data/aop_event_schedule.json, website/data/aop_waypoints_traced.geojson, mvp/scripts/stamp_maturity.py, mvp/scripts/set_feature_maturity.py (new), + all website/data/*.geojson _meta (re-stamped) + _schema.json
started: 2026-06-14T13:00
---

Six-item user drop, shipped on v87 (the v87 bump itself + landcover fill-opacity→1
belong to the **concurrent landcover-opacity session**, see below — I built on them).

- 13:00 claimed the read viewer + the data-maturity pipeline for a 6-item batch.
- Shipped + verified by observation (`:8001`, 13/13 + alert PASS, 0 console errors):
  1. Trail number-first `display_name` (label + search single source) — "1 Launchpad".
  2. Borderless tree cover — removed both landcover `-outline` layers + refs + consts.
  3. Medallion tiers — `stamp_maturity.py` (file `_meta`) + new `set_feature_maturity.py`
     (per-feature). gold=9 silver=2 bronze=11 delete=3. Ellis/5-buildings gold.
  4. Production data-tier alert — `auditProductionTiers()` (console.warn, never hides).
  5. One persistent active item — search de-thrones event; popup-close keeps it.
  6. Pro-Line at the firepit — `#firepit` location + Firepit waypoint tagged.

**COMMINGLED tree (flag for the user's git gate).** `website/js/viewer_core.js` and
the v87 bump (`index.html`/`sw.js`) are shared with a **concurrent landcover-opacity
session** (its note lives in `tasks/01_mvp/_done/landcover_layer.md`: park solid,
non-park opacity TBD, `fill-antialias:false` pending the user's % pick + the
`mockups/compare.html` chooser + `_integrate_solid_*.png`). My landcover touch was
ONLY removing the `-outline` layers (compatible with their no-border direction — I
kept their fill-opacity=1). The two sessions edit different functions of
viewer_core.js, so `git add -p` separates them cleanly. I did NOT touch their
landcover_layer.md / mockups / pngs.

DONE → next: name the 10 new traced trails. Card:
`tasks/02_edit/_done/six_item_viewer_batch_20260614.md`.

## Addendum — physical file rename + data-editor re-group (2026-06-14, v88)

The six-item batch above was **committed by the user as HEAD `91a017e` ("medallion
rename")**. The user then asked to actually RENAME the files (not just the tier
values) + re-group the data editor page ("rename and re-group. dont touch treecover").

- **File rename:** every served geojson now carries its medallion tier as a filename
  prefix — `gold_aop_trail_network.geojson`, `bronze_aop_cemeteries.geojson`,
  `silver_publish.geojson`, `delete_aop_synthetic_activity_*.geojson` (25 files).
  New `mvp/scripts/rename_data_medallion.py` (imports `stamp_maturity.MATURITY` — no
  dup) renames + sweeps the runtime refs (viewer_core 14, main 51, panel 29,
  data_editor_map 1, sw 24, old_index 1, `_schema.json` 25, `_data_manifest.json` 39).
- **Re-group:** `data_editor_map.js` now groups the file picker into `<optgroup>`
  Gold / Silver / Bronze / Delete (derived from the filename prefix).
- **`sw.js`/`#appVersion` v87→v88.** **Tree cover NOT touched** — my sweep only changed
  filename strings; the landcover session's 60% non-park opacity + `fill-antialias:false`
  are intact.
- **Verified by observation** (`:8001`): `verify_label_border_persist_firepit.py` 13/13,
  `verify_production_tier_alert.py` PASS, `verify_data_editor_regroup.py` PASS — all 0
  console errors (production viewer loads every prefixed file; the data-editor picker
  shows the 4 tier groups).
- **COMMINGLED with the concurrent landcover-opacity session** (tree cover v88, its own
  `.council-cleared` = c91d81a, now STALE because my rename changed the diff). Both are
  uncommitted; the user separates at the git gate. Did NOT touch the landcover session's
  files (`landcover_layer.md`, mockups, pngs).
- **Owed (pipeline consistency):** the ~50 `mvp/scripts` (importers/exporters/bakers +
  ~30 verifiers) still read/write CANONICAL names; `rename_data_medallion.py` is the
  documented FINAL step — re-run it after any data bake (like `stamp_maturity.py`).
  A deeper pass to make the generators emit prefixed names is Docker-gated (deferred).
