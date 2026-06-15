# Council receipt — 3D map spin re-enabled while tilted (2026-06-15)

**Task / directive:** User: *"review the 3d map. we used to be able to spin it around
while it was tilted. now it seems to be disabled. we want to enable it."*

**Change (on-card):** `website/js/viewer_core.js` — removed `touchZoomRotate.disableRotation()`
+ `dragRotate.disable()`, added `pitchWithRotate:false` to the map constructor, kept
`touchPitch.disable()`. Pitch stays button-only; spin (two-finger twist / right-click drag)
is back. Shell asset → v95→v96 bump (`sw.js`+`#appVersion`). **Committed by the user as HEAD
`0d7b750` "v96"** (commingled with a concurrent park-border session + contour cleanup — the
user's git-gate call).

**Tier:** core three (Witness · Warden · Quartermaster) — single-handler viewer behavior
change, not a sprint boundary or publish-zone data change.

**Verification artifact:** `brain/output/verify_spin_while_tilted.py` — 7/7 PASS by observation
(live handlers dragRotate=on / touchZoomRotate=on / touchPitch=off; a real right-button drag spun
the bearing 16° (-90→-106) while pitch held at 58°, Δ0.0°).

## Round 1 — three andons

- **Witness → andon:** recorded "7/7 PASS, 0 errors" was contradicted by a re-run (6/7) — an
  intermittent `Could not compile fragment shader:` pageerror (headless SwiftShader sky shader).
- **Warden → andon:** three `publish-boundaries` paint hunks commingled in `viewer_core.js`
  looked off-card.
- **Quartermaster → andon:** `brain/output/verify_five.py:141` still asserted the OLD locked
  contract (`dragRotate is False`), now broken by the change — two camera verifiers contradicting.

## Resolutions

- **Witness:** filtered the shader-compile error as environmental in `verify_spin_while_tilted.py`
  (alongside the existing tnmap/favicon filters; the diff touches no shader code) and corrected the
  record in the handoff + `pwa_qa.md` item 7 to state the intermittent headless-only error honestly,
  naming the earlier "0 errors" as wrong.
- **Warden:** the boundary hunks belong to a CONCURRENT "park-bounds border" session (own card,
  own verifier `verify_park_border_faint.py` 8/8, own receipt) — not this task's work, and now
  committed in `0d7b750`. Reverting them was never mine (cross-session destruction). My uncommitted
  diff is brain-only; git gate untouched (no mutating git, no attribution; the user authored `0d7b750`).
- **Quartermaster:** updated `verify_five.py` item 3 IN PLACE — header reworded + dated v96 comment,
  the single assertion flipped to `dragRotate ... is True`; pan/zoom/touch-pitch/3D-button checks
  intact. No new/parallel verifier. The two camera verifiers now agree. `verify_five.py` item 5's
  pre-existing crash (stale `data/aop_landcover_9patch.geojson`, renamed by the going-gold work)
  is a different card's debt — left flagged, not fixed (on-farm).

## Round 2 — re-review verdicts (fresh seats)

- **SEAT: witness — CLEAR.** Re-ran the verifier (7/7); 0 product errors across a 6-load probe
  (shader error intermittent, did not fire); filter excludes only 4 specific substrings, not a
  blanket; `git show 0d7b750` has zero shader/sky/fog refs.
- **SEAT: quartermaster — CLEAR.** item 3 updated in place, no duplication; verifiers agree;
  C1=0 / C6=0-class+no-new-html / C2=1 hold; item-5 stale path correctly left for its owning card.
- **SEAT: warden — CLEAR.** `0d7b750` authored+committed by the user (no co-author trailers);
  boundary work owns its own card/verifier/receipt; my working tree is brain-only; item-7 directive
  annotated (reversed), never erased.

**Result: 3/3 CLEAR.** Owed (not blockers): on-device confirm of the pinch-vs-twist responsiveness
trade-off (the re-enabled twist may regress the `pwa_qa.md` item-7 pinch-start fix); the user's
commit is their git gate (already taken for the spin change; the brain-only corrections in this
round remain uncommitted for the user).
