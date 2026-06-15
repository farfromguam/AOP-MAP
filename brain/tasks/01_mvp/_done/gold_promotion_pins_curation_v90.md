# Gold promotion + pins gating + publish curation (v90 batch)

> **RESOLVED → SHIPPED (CODE+DATA, UNCOMMITTED). Directive #1 was REVERSED by the user
> 2026-06-14 (later same day).** The earlier ANDON (below, struck) was correct against
> directive #1 *as originally stated* (Park + Satellite). But the user then looked at the
> running Park+Satellite result and said, verbatim: *"the pins show up on satellite but not
> topo. this is backwards."* — i.e. pins belong on the **Topo** navigational read, **not** on
> Satellite. So the shipped `viewer_core.js:774` (`pinsOn = presetId === 'park' || presetId ===
> 'topo'`) is now **correct**, not a regression. Directive #1 below is rewritten to the reversed
> intent and the verifier's pin asserts were flipped to match (Topo visible, Satellite hidden).
> Re-verified by observation — all 8 pin checks PASS (`/tmp/verify_v90_batch.py` on `:8001`:
> Park+Topo visible, Trace+Satellite hidden, Park-return visible); the lone FAIL is external
> `tnmap.tn.gov` satellite tiles unreachable from the sandboxed run (network artifact, 0 app
> console errors). Council (core three) cleared the pin flip:
> `brain/output/council/pins_topo_not_satellite_20260614.md`. `v89→v90` bump already in tree;
> the commit is the user's git gate.
>
> > ~~ANDON (Scribe, 2026-06-14): code reads `park || topo`, reverse of directive #1 as then
> > stated; fix to Park + Satellite.~~ **Superseded — the user reversed directive #1 itself; the
> > code is now what the user wants. Do NOT flip back to Park+Satellite.**

Date: 2026-06-14

TL;DR:
- A 9-item user batch over the read viewer + served data: gate location pins out
  of Trace/Topo, promote the two remaining **silver** files to **gold** (rename +
  re-stamp + reference sweep), curate the publish group (drop Saturday segments,
  de-dupe Ellis, add Jackson Point), unname the `sfwda-*` placeholder trails,
  number Launchpad, and star the Shower House.

#aop #01_mvp #gold #medallion #pins #publish #curation #v90

-----

## The directives (user, 2026-06-14) → what shipped

1. **No pins in Trace or Satellite → Park + Topo only.** (REVERSED — see top block.
   First stated as "Park + Satellite only"; the user reversed it later the same day after
   seeing the result — *"pins show up on satellite but not topo. this is backwards."* — so
   pins belong on the **Topo** navigational read, not the Satellite imagery.) `applyPreset`
   (`website/js/viewer_core.js:774`) gates the always-on location pins — camp waypoints
   (`aop-waypoints[-labels]`) + facility name pins (`aop-facility-pin`/`-labels`) — to
   **Park + Topo only** via `pinsOn = presetId === 'park' || presetId === 'topo'`; brand
   logos are NOT pins and stay. Verifier pin asserts flipped to match (Topo visible,
   Satellite hidden); re-verified by observation — all 8 pin checks PASS.
2. **Saturday Afternoon Activity segments not starred → removed.** Both
   `trail_centerlines:3/4` (`highlight:true`) deleted from the publish group
   (supersedes "un-star"). Also removed their 2 orphaned `aop_poi_index.json` entries.
3. **Star the Shower House.** `highlight:true` added to the Shower House feature in
   `gold_aop_buildings.geojson` (per-feature maturity stays **bronze** — starred,
   not promoted).
4. **`sfwda-*` trails unnamed.** The 20 placeholder names (`sfwda-1`, `sfwda-15`, …;
   all `trail_number:null`) set to `name:null` in `gold_aop_trail_network.geojson`
   (name:null trails 10 → 30).
5. **Launchpad numbered.** Trail #1 `name` "Launchpad" → **"1 Launchpad"** in the
   data. `trailDisplayName` got a guard so a name that already leads with its number
   isn't double-prefixed (would have read "1 1 Launchpad"); display reads "1 Launchpad".
6. **Visitor context callouts silver → gold.** `silver_aop_visitor_context_callouts.geojson`
   → `gold_aop_visitor_context_callouts.geojson` (file rename + `_meta` + per-feature
   `maturity` re-stamped gold).
7. **Publish silver → gold, one Ellis removed.** `silver_publish.geojson` →
   `gold_publish.geojson`. The two Ellis entries were the **inholding parcel polygon**
   (`park_boundaries:ellis-inholding`) and a duplicate **POI point**
   (`editorPois:ellis-cemetery`, which the gold camp waypoints already carry) — the
   redundant POI point was removed, the parcel kept.
8. (= #2) all Saturday segments removed.
9. **Jackson Point → gold publish group.** The OSM peak (GNIS 1289241) added to
   `gold_publish.geojson` as a gold `poi` feature. Publish group: 6 → **4** features
   (parcel envelope, Ellis inholding parcel, AOP Pavilion, Jackson Point).

## Reference sweep + tier source-of-truth

- `silver_* → gold_*` swept across `viewer_core.js`, `main.js`, `panel.js`,
  `data_editor_map.js`, `sw.js`, `_schema.json`, `_data_manifest.json`,
  `export_illustrator_trace.py`, `rename_data_medallion.py` (no `silver_*` refs left
  in `website/` or `mvp/`).
- `mvp/scripts/stamp_maturity.py` `MATURITY` map (the per-file source of truth):
  `publish.geojson` + `aop_visitor_context_callouts.geojson` flipped silver → gold.
- `auditProductionTiers()` is data-driven — once the served files read gold it
  self-clears; only Shower House (bronze) remains a legitimate flag.
- Cache `v89 → v90` (`sw.js` VERSION + `index.html #appVersion`). NB: the working
  tree was at v89 (HEAD), not the v90 the prior handoff implied — index.html had been
  reverted mid-session; this one bump covers the pending cemetery fix + this batch.

## Acceptance (observed, not re-derived)

`/tmp/verify_v90_batch.py` (clean Playwright context, `:8001`) — after the directive-#1
reversal, **19 PASS / 1 FAIL**, the lone FAIL being external `tnmap.tn.gov` satellite tiles
unreachable from the sandboxed run (network artifact, not an app error — 0 app console errors;
the original 20/20 was logged where that CDN was reachable): no `silver_*` request; gold_publish
+ gold_visitor load; **pins visible Park + Topo, hidden Trace + Satellite, visible Park-return**;
trail #1 name & display == "1 Launchpad"; 0 trail names still `sfwda-*`; 30 null names; publish
has no Saturday, has Jackson Point, keeps the Ellis inholding parcel, drops the bare Ellis POI,
4 features; Shower House `highlight:true`; visitor + publish `_meta` gold.

## Owed (git gate + durability)

- **Commit is the user's git gate.** Files: `viewer_core.js`, `sw.js`, `index.html`,
  `gold_aop_trail_network.geojson`, `gold_aop_buildings.geojson`, `aop_poi_index.json`,
  `_schema.json`, `_data_manifest.json`, the renamed `gold_publish.geojson` +
  `gold_aop_visitor_context_callouts.geojson` (with the deleted `silver_*` pair),
  `stamp_maturity.py`, and the swept `main.js`/`panel.js`/`data_editor_map.js`/
  `export_illustrator_trace.py`/`rename_data_medallion.py`. (The tree is commingled
  with other cards' uncommitted work — review scoped to this card's set.)
- **Durability gap (served-only curation).** The publish edits landed on the served
  `gold_publish.geojson`. `raw/publish.geojson` (mixed-format machine export, not
  cleanly re-serializable by hand) + the PostGIS `publish` view still carry the 2
  Saturday segments + the de-duped Ellis POI and lack Jackson Point — a re-bake would
  reintroduce/drop them. Same precedent as the off-park-cemetery fix. DB curation owed
  when Docker is up.
