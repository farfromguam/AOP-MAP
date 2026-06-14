---
session: five-item-review (opus — viewer fixes)
status: done
claim: website/js/viewer_core.js, website/js/main.js, website/index.html, website/sw.js, website/data/aop_landcover.geojson, website/data/aop_landcover_9patch.geojson, mvp/scripts/simplify_landcover_vegetation.py, mvp/scripts/playwright_verify_landcover.py + brain/output/{observe_five,verify_five,diag_*}.py + obs5_*/v5_* shots
started: 2026-06-14T09:20
---

Posting this because the concurrent **illustrator-trace** session correctly flagged
my changes as unclaimed (its handoff entry, Warden andon). This IS that work — the
user's "five-item review."

- 09:20 claimed the read viewer + landcover data/pipeline for a 5-item review.
- Items shipped (all verified by observation on `:8001`, 0 console errors, v82→v83):
  1. Trail labels number-first (`aop-trail-network-labels` text-field): "1 Launchpad" / "15".
  2. POI/search selection highlight PERSISTS until next select (pulse settles, not hides).
  3. 3D orientation locked: `touchPitch`/`dragRotate` disabled; pan+zoom keep; button still tilts.
  4. Park no-tree base → `#e7ddc4` (the Topo/Trace base) per the user.
  5. Vegetation corner render: 9-patch giant fill polygon (3976v/47h) → grid-subdivided
     324 pieces + LineString outline; renders in all 4 quadrants. `simplify_landcover_vegetation.py`
     rewritten + both data files regenerated from the 5class cache; outline layers filtered to LineString.
- Touched `main.js` only for the same landcover geometry-type filter (same files feed both hosts).
- Fixed two pre-existing Map-serialization hangs in `playwright_verify_landcover.py` (fitBounds/zoomTo
  arrows returned the Map). Verifier now 23 PASS, RESULT: PASS.
- **No `.council-cleared` written** (tree commingled with the illustrator session — same reason it noted).
- DONE → next: user reviews the diff + commits at the git gate. Council review owed if/when the two
  sessions' trees are separated. My files are listed above so the other session can exclude them.
