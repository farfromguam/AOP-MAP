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

DONE → next: name the 10 new traced trails; editor (`panel.js`) medallion re-group
(deferred — chip learns bronze, tree layout owed). Card:
`tasks/02_edit/_done/six_item_viewer_batch_20260614.md`. UNCOMMITTED (git gate).
