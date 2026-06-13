# Council receipt — geolocated band (viewer_band.js)

Date: 2026-06-13
Reviewed unit: the geolocated decorative band on the proof page `website/viewer_banded.html`
(committed rewrite at HEAD v66 + the uncommitted `-90` label re-map + the inset fix).
Chair: Steward. Tier: core-three (Witness · Warden · Quartermaster) + Mason (dead-code/clean was a live question).

Goal (one line): make the band geolocated so it conforms to the landscape in 3D, with the lettering
re-mapped so the default `-90°` view reads like the picked design — proof page only.

## Acceptance criteria
1. Band geolocated (MapLibre fill mask + line keyline + ground-aligned icon lettering + corner marks) →
   conforms to the landscape in 3D (foreshortens onto the ground plane when pitched).
2. Lettering renders with the picked typography (canvas→icon, because `symbol-placement:line-center`
   text placed 0 across a vector-tile boundary split).
3. Text-scaling / "HR" overflow dissolved via ground-locked sizing.
4. Labels re-mapped so the default `-90°` reads like the picked design (title top / location bottom /
   35°N left / 85°W right).

## Verdicts
- WARDEN — clear. On the farm: only `viewer_band.js` (the re-map) + the brain record changed by this agent;
  `viewer_band.js` is loaded ONLY by `viewer_banded.html` (grep), not the production `index.html` shell;
  no mutating git by this agent (v65/v66 were a concurrent session); sw.js bump NOT owed (`viewer_band.js`
  not in `sw.js` SHELL_ASSETS; production shell is `./index.html`).
- QUARTERMASTER — clear. No new engine/registry/helper/surface; structural guards (C1/C2/C6) hold and are
  untouched. `addImage`/`scalarSizeExpr` reuse is justified divergence (the band tints an SVG + rasterizes
  typography the core's direct-img path can't express). FOLLOW-UP (separate cleanup card, not a gate): the
  OLD screen-space band remnants survive as dead duplicates — the `#bandFrame` 8-tile div block
  (`viewer_banded.html`) + all `.band-tile`/`.band-label`/`#bandFrame` rules in `viewer_band.css` are no
  longer driven by the JS; delete them so only the geolocated path remains.
- MASON — clear. No limiting code (the mask hides spill cosmetically, drops no data); no spec strategy that
  throws; `sizeExpr` fully removed (0 refs); kept helpers all live (scalarSizeExpr/regionRect/rawGaps/gaps/
  snapBack); re-map internally consistent (bearing -90 → top=W/bottom=E/left=S/right=N; rotations
  -90/-90/180/0 under icon-rotation-alignment:map render upright & non-mirrored; all 4 labels land outside
  their edge on the paper); idiom matches viewer_core.js. `node --check` PASS.
- WITNESS — andon → (fixed) → clear.
  - ANDON: criterion 4 was refuted by its own first artifact `band_remap_2d.png` (Region preset at -90):
    only the SIDE labels rendered; title-top / location-bottom were CLIPPED off-screen (labels sat 6%
    outside the region; the Region preset's ~20px padding crops the height-limited axis).
  - FIX (the only change to re-judge): label inset 6% → 3% (`insetX/insetY = dW/dH*0.030`) so the lettering
    hugs the neat-line and stays inside a tight region-fit.
  - RE-REVIEW CLEAR: `band_fix2_margin.png` (-90 + a little margin) shows all four in the picked layout —
    TITLE "ADVENTURE OFF ROAD PARK" across the TOP (no clip), "SOUTH PITTSBURG · MARION COUNTY · TENNESSEE
    — MMXXVI" bottom, "35° 00′ NORTH · CUMBERLAND…" left, "85° 36′ WEST · TRAIL BLAZING INVITATIONAL" right.
    `band_fix2_3d.png` (-90, 3D) shows the title across the top of the pitched trapezoid, foreshortened onto
    the ground — 3D conformance preserved with the smaller inset. `node --check` PASS.
    Out-of-scope caveat: loosening the Region preset's 20px padding is a core-side follow-up, not the band.

## Steward synthesis
Full clear — every convened seat `clear` (Witness via the andon bounce). Verified-by-observation artifacts:
`band_icon_flat.png` (north-up, all labels), `band_wide_3d.png` / `band_fix2_3d.png` (3D conformance),
`band_fix2_margin.png` (the -90 picked layout). 0 console errors; `node --check` clean.

## Clearance marker — NOT written
The Tier-0 marker (`.claude/.council-cleared`) was deliberately NOT written: the uncommitted `website/`
tree also holds a concurrent session's work (`viewer.css`, `index.html`, `viewer_core.js`, `sw.js`) that
this council did NOT review, and the gate's clearance hash is wholesale over `website`/`mvp`. Writing it
would falsely clear unreviewed work. The band slice is cleared on its own merits (this receipt); the marker
waits until the band diff is isolated at the user's commit.

## Cleanup follow-up (owed, not done — needs its own card)
Delete the dead old-engine band: the `#bandFrame` div block in `viewer_banded.html` and the
`.band-tile`/`.band-label`/`#bandFrame[data-deco]` rules in `viewer_band.css` (and the now-no-op `?deco=`
param + `viewer_banded_compare.html`).
