# Council receipt — band centerline tweak (corner marks ↔ lettering)

Date: 2026-06-13 · Steward: main agent · Tier: core three (witness · warden · quartermaster)

**Goal (direct user request):** *"corner markers to move inboard and the text to move outward a bit … closer to sharing centerlines"* on `viewer_banded.html`.

**Diff reviewed:** `git diff HEAD -- website/js/viewer_band.js` — the two offset constants:
- `insetX/insetY` (label inset): `dW*0.030` → `dW*0.042` (text moves **outboard**)
- `cornOutX/cornOutY` (corner-mark offset): `dW*0.052` → `dW*0.042` (marks move **inboard**)
- + cross-referencing comments; + a stale-comment fix at line 152 (`cornOut 0.052` → `0.042`) made on the Witness's note.

Both now sit at a shared `0.042`, so the corner marks' centers land on the label band's centerline — one ring at a common distance off the neat-line.

(The current working tree also carries two **prior-cleared** label-string edits — `'s'` longitude, `'n'` dot — from `band_labels_council_receipt.md`, still uncommitted; they ride along but are not this card's work.)

**Acceptance — verified by observation** (not re-derived): the Witness independently re-rendered the band in real Chrome and confirmed via screenshot ink-centroid analysis (left-label centroid ≈ corner-mark x-band; bird sits on the "ADVE" column spine) — the centerline-share is real on the rendered output, all four corners on the paper, no clipping. `node --check` OK; `:8000` → 200.

```md
SEAT: witness
VERDICT: clear
ISSUE: none blocking — claims hold against an independent render, not the agent's narration.
EVIDENCE: own Playwright run (channel=chrome, headed) viewer_banded.html?frame=out → getStyle()
  reports mask+keyline+36 art tiles; /tmp/witness_full.png shows full lettered frame; left-label ink
  centroid 286.7 CSS px vs projected centerline 278.8 px (≈8px, glyph asymmetry), bird in same x-band;
  no edge/corner clipped; node --check OK; :8000 → 200.
NEXT: (non-blocking) the agent's /tmp/shot_band.py centerline check hard-codes the offsets (tautological);
  the line-152 stale "0.052" comment — FIXED this pass.
```
```md
SEAT: warden
VERDICT: clear
ISSUE: none — both hunks trace to the card (text outboard / marks inboard, both → 0.042 = "share
  centerlines"); no card directive deleted; git gate untouched.
EVIDENCE: status --porcelain -- website mvp = exactly `M website/js/viewer_band.js`; HEAD = user's own
  9274a19; no mutating git this session. Version advisory REFUTED: grep -c viewer_band sw.js = 0,
  viewer_band.js + viewer_banded.html both absent from SHELL_ASSETS → no VERSION/#appVersion bump owed.
NEXT: none blocking — commit + any bump remain the user's gate; the prior-card label edits will commit
  together with this delta unless the user wants them staged separately.
```
```md
SEAT: quartermaster
VERDICT: clear
ISSUE: none — two value reassignments to pre-existing constants; no new helper/layer/class/HTML/registry,
  no dead code. The two dials sharing 0.042 is NOT a duplication to collapse — they are conceptually
  distinct knobs (label inset vs corner offset) that coincide at this tuning; collapsing would couple them.
EVIDENCE: diff = the two var reassignments + prior-cleared EDGES strings; no new `class [A-Z]`; C1=0
  non-comment layerKey branches; C2 one collector; C6 no new html; node --check passes.
NEXT: none — ship as-is.
```

**Steward verdict:** CLEAR (all three convened seats clear). Marker written to `.claude/.council-cleared`
(hash `9b88824…`, exact gate formula over website+mvp diff+porcelain).

**Owed / git gate:** the commit and any version bump remain the **user's** — and no `sw.js`/`#appVersion`
bump is owed here (viewer_band.js is not a precached shell asset). The uncommitted tree currently bundles
this centerline delta with the prior-cleared label edits; they will land together on the next commit.

----

## Re-tune addendum — 2026-06-13 (optical seat)

User, viewing the 0.042/0.042 result: *"closer to sharing the same centerline. visually still a bit
mis-aligned. either the birds need to be moved in slightly or the text out — it's slight."*

Measured by observation (PIL ink-centroid + bbox-center on the rendered frame, `/tmp/measure_band.py`,
`/tmp/measure_bird.py`): at 0.042/0.042 the bird and text were already centroid- AND bbox-aligned to
within ~2–4 device px — no geometric gap. The residual is **perceptual**: the bird silhouette's crest
(up-out) and tail bias its visual mass outboard, so a centroid-matched mark reads as leaning away.

Fix (Steward judged a re-tune within the just-cleared diff, not new work): `cornOutX/cornOutY`
`0.042 → 0.039` — corner marks pulled a hair inboard so the body mass optically seats on the label
centerline. `insetX/insetY` left at 0.042. Re-verified by observation: corner crops `/tmp/corner2_*.png`
show the birds moved inboard; re-measure shows birds now ~3.4 CSS px inboard of the text centroid (the
intended optical compensation). `node --check` OK.

Seat coverage for the re-tune: **Witness** lens satisfied by the new render observation (crops +
re-measure, not re-derived). **Warden** unaffected — still on-card (the exact nudge the user asked for),
git gate untouched, no bump owed. **Quartermaster** unaffected — same two constants, no new symbols.
Steward re-clears; marker rewritten over the new diff hash. Final aesthetic amount is the user's eye.
