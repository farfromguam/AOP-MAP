# Witness receipt — vegetation land-cover (simplification + corner render fix)

Date: 2026-06-14. Surface: live read viewer at http://localhost:8001/
(`window.AOPViewer.map`). Backs the "verified by observation" claims in
`brain/tasks/01_mvp/_done/landcover_layer.md` and `brain/research/viewer.md`.

## Pass 1 — vegetation simplification (committed da5d032 v79)

Observed on the live viewer (council Witness re-ran `playwright_verify_landcover.py`
and a separate clean capture):

- Both served files carry only `class=vegetation` (park 18 feats, 9-patch 165);
  the five retired sub-classes are gone.
- Fill is one flat green `#b8c1a1`; paper background `#efe7d5`; 9-patch layer is
  the lowest drawn (base of stack); features render (park 18/18, 9-patch 165/172).
- Console errors: the verifier's own summary line did not flush under a temp-fs
  tail hang, so a separate clean Playwright capture (`console.error` + `pageerror`,
  clean process close) was run → **0 console errors**, exit 0.

## Pass 2 — corner rendering fix (committed 692464b v81)

User report: empty TR/BR/BL corners + patches "popping" at zoom; satellite shows
dense trees there. Root cause: the dissolved forest was one ~28k-vertex / 282-hole
polygon → MapLibre fill tessellation dropped chunks. Fix: cap per-polygon
complexity (drop <~5000 m² holes + light simplify) → max 3976 verts / 47 holes
(9-patch), 187/0 (park); coverage ±0.1%.

Observed (fresh render agent, Region preset + z12.4/13/14/15):

- CORNERS: the previously-empty TR/BR/BL data-rectangle corners now fill with
  green (compare `diag_veg_region_preset.png` broken vs `veg_fixed_region_preset.png`).
- CONTINUOUS: base-hidden capture (`veg_fixed_z124_lite.png`) shows one connected
  canopy with only organic clearings — no geometric voids.
- POP: green coverage stable across z12.4→z15 (qRF 9-patch 145→169→96→14 is
  viewport-windowing of counts, not blink-out; coverage ~33%→78%).
- **0 console errors** at every step.

VERDICT: clear — both the simplification and the corner-fill fix are observed on
the running system, not narrated. Artifacts: `brain/output/veg_fixed_*.png`,
`brain/output/diag_veg_*.png`, `brain/output/playwright_landcover_*.png`.
