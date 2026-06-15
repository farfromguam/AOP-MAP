# Council receipt — contours lazy-load (phone-load fix) (2026-06-14)

**Goal:** the viewer *"takes a long time to load on phones"* — remove unnecessary
initial load weight. Found: `viewer_core.js` fetched the **~13 MB**
`gold_aop_contours.geojson` with a **blocking `await` in `map.on('load')`**, though
contours are `visibility:'none'` in every preset but Topo (default Park) — and the load
handler is a sequential await chain, so **all park content (water/roads/buildings/trails/
waypoints/parcel/schedule) was serialized BEHIND** the 13 MB download+parse.

**Change (this task's hunks only — viewer_core.js is commingled with the Hot Rocks
STAR_GROUP, Gravity Gauntlet data, and POI-metadata changes from other cards):**
- Removed the eager contour fetch+addSource+addLayer from `map.on('load')`.
- Added idempotent `ensureContours()` (same defs, moved) called from `applyPreset` only
  when `preset.toggles.showContours` is true (Topo); the `.then` reads the live
  `activePresetId` so a quick Topo→Park toggle leaves contours hidden.
- No data/pipeline change. New verifier + doc records.

**Tier:** core three + Mason (load-path/concurrency change with a Topo→Park race).
**Deterministic gate:** `node --check website/js/viewer_core.js` passes.

## Verdicts

```md
SEAT: witness
VERDICT: clear
ISSUE: none — "9/9 PASS, no Park contour fetch, lazy on Topo" reproduces on live :8001, real observation.
EVIDENCE: re-ran verify_contours_lazy_load.py twice → 9/9 PASS, exit 0, console_errors []. page.on('request')
  attaches pre-goto; PARK contour_requests==[] is a TRUE negative from the same listener that captured exactly
  one gold_aop_contours.geojson request in the TOPO arm. PARK live map: waypoints+buildings present, no
  aop-contours source. TOPO after real #presetTopo click: source added, contours-index visible. File is
  13,219,469 bytes (real payload).
BLIND SPOTS (named): proves request-made/not-made, not wall-clock load on a throttled phone (the win is a sound
  inference from removing a 13 MB blocking await); headless has no SW so the precache-exclude path isn't exercised.
NEXT: optional — second Topo press to assert fetch-count stays 1; throttled-network timing to measure the win.

SEAT: warden
VERDICT: clear
ISSUE: none blocking — card-traceable, contour rendering byte-identical when shown, default behavior unchanged, git gate untouched.
EVIDENCE: byte-comparison of the removed eager block vs ensureContours() — addSource + 3 addLayer
  (paint/filter/layout visibility:'none') line-for-line identical; only added wrapper + other cards' lines.
  No other layer's load altered; gold_aop_contours.geojson not in diffstat (data/pipeline untouched). applyPreset
  fires ensureContours only on showContours, re-reads activePresetId at resolve (Topo→Park leaves hidden).
  git diff HEAD of sw.js + index.html EMPTY — no agent bump/SW/#appVersion edit; both read v92; node --check PASS;
  no mutating git/attribution. Owed v92→v93 bump stated as the user's gate in handoff + card. Deploy-junk flag
  left as user's call, nothing deleted (git status: 0 deletions under website/).
NEXT: handoff flag bundled data/delete_*.geojson, but two are precached/active in sw.js (misnamed, not dead) —
  CORRECTED in the handoff so the user doesn't delete a live layer. v92→v93 bump remains the user's.

SEAT: quartermaster
VERDICT: clear
ISSUE: none — pure relocation reusing existing machinery; no duplicate engine/store/fetch/preset-map.
EVIDENCE: the addSource+3 addLayer defs in ensureContours are byte-identical to the deleted eager block (only
  the wrapper differs). Reuses existing setLayerVisibility (351), applyPaintState (756), PRESET_LAYERS.showContours
  (555), BUILT_IN_PRESETS (575), memoized fetchJson (364) — none on a + line. gold_aop_contours.geojson fetched
  exactly once (in ensureContours). No orphaned contourData; ensureContours reached from applyPreset. C1=0, C6
  (0 classes/no new editor html), C2 (single collectStarredDestinations, untouched) hold.
NEXT (flag, don't fix): contours is the only lazy heavy layer; activity-hotspots/landcover/water/roads/buildings/
  trail-network still eager-await in map.on('load') — a future convergence card onto the ensure<Layer>() pattern.

SEAT: mason
VERDICT: clear
ISSUE: none — race-correct, idempotent, TDZ-free, non-limiting, idiomatic.
EVIDENCE: (1) RACE — the .then reads LIVE BUILT_IN_PRESETS[activePresetId], not a captured presetId; "last
  preset the user ends on wins" (Topo→Park → hidden; Topo→Park→Topo → visible). Park never registers a .then.
  (2) IDEMPOTENCE — fetchJson memoizes by URL + contoursReady memoizes the add; the map.getSource guard has NO
  await before the synchronous addSource/addLayer, so no interleave/double-add throw on the single-threaded loop.
  (3) TDZ — ensureContours is a hoisted decl; contoursReady is a module let set at module-eval before any
  click/load handler. node --check PASS. (4) no validator/throw/row-drop added; moved defs match idiom; fetchJson
  fails soft (warn, !contourData guard → "no contours, map fine"). (5) auditProductionTiers guards on
  map.getSource → degrades cleanly when contours absent at load.
NEXT (advisory): auditProductionTiers now skips the contour-tier check at load (dev-only warn, gold data,
  harmless) — noted on the card. "Converge other heavy layers onto ensureContours()" is a separate card.
```

**Steward synthesis:** full clear — Witness · Warden · Quartermaster · Mason all `clear`,
no open andon. Two NEXT notes folded in (handoff `delete_*` correction; the
auditProductionTiers skip noted on the card). The default Park load drops ~13 MB and is no
longer serialized behind the contour download. **User's git gate (owed):** v92 is committed,
so this uncommitted shell change is owed a **v92→v93** bump + commit. Quartermaster's
broader note — other heavy layers still eager-await — is a worthwhile future perf card.
