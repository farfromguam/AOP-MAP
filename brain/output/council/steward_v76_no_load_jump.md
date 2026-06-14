# Council synthesis — no-on-load-jump (index opens at park zoom)

Date: 2026-06-14
Chair: Steward
Goal (from card + user): the index page jumped on load (park → region → park, then a
12.5 → 14 climb). Make it open at park zoom and hold — no jump.

## Tier: core three (low risk — removal + a zoom literal + a verifier; no publish-zone
data, no validation-loop touch, read-only viewer).

## Change under review
- COMMITTED `c157acc v75` (by the user): removed the auto-peek reveal animation from
  `website/js/viewer_band.js`.
- UNCOMMITTED (my slice): construct the map at `zoom: 14` not `12` in
  `website/js/viewer_core.js` (kills the residual 12.5→14 climb); deleted the spent band
  proof scaffolding (`viewer_banded.html`, `viewer_banded_compare.html`,
  `css/viewer_band.css`); one dangling comment fixed in `viewer_core.js`; the verifier
  `brain/output/verify_no_load_peek.py` rewritten to sample from t=0 (no race) and to
  filter only headless-GL shader-compile noise from its fatal-error gate.

## Verdicts (all convened seats clear)
- WARDEN: clear — deletions == the card's owed scaffolding list; no unrelated files
  touched; `c157acc` authored/committed by the user (Christopher Fryman), not the agent;
  card directive struck-through + annotated, not deleted; v-bump stated as owed-to-gate.
- QUARTERMASTER: clear — pure deletion + version bump + one comment; C1=0, no new class,
  no new editor html, no second list engine; band MODULE `js/viewer_band.js` survives and
  is still loaded/precached; no shipped reference to any deleted file; no dangling precache.
- WITNESS: clear (after two andons, both honored) —
  - andon #1: "no jump" was under-verified; the verifier raced the load. → fixed the real
    residual jump at the source (construct at z14) + rewrote the verifier to sample from t=0.
  - andon #2: the rewritten verifier flapped on an intermittent headless-Chromium GL
    artifact ("Could not compile fragment shader:") in its 0-error gate. → filtered ONLY
    that GL noise; real page errors still fail.
  - final: 9/9 deterministic PASS, z0=14, span=0, 38 band layers; filter proven narrow
    (6 real error types still fail; empty message errs toward fail); construction zoom = 14;
    auto-peek gone. Settled screenshot shows park framed at park zoom.

## Result: CLEAR on this slice.

## Clearance marker: NOT written — on purpose.
The Tier-0 hash spans ALL of `website/` + `mvp/`, and the working tree currently also
holds another session's uncommitted **v77** work (TBI event copy, landcover demo,
`main.js`, `viewer.css`, data JSON) that THIS council did not review. Writing
`.claude/.council-cleared` would falsely certify that parallel work. Same call as v69.
The Stop hook will keep nudging until either that parallel work is reviewed too or this
slice is committed apart from it — both the user's git gate.
