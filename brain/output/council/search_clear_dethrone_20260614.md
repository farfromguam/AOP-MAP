# Council receipt — search-clear de-thrones the held highlight (2026-06-14, v91)

Task: clearing the search bar (backspace-to-empty or Escape) clears the held map
highlight AND de-thrones the active item. Card:
`tasks/02_edit/_done/six_item_viewer_batch_20260614.md` (addendum). Scoped diff: the
`clearActiveSelection` + `dethroneActiveEvent` hunks in `website/js/viewer_core.js`, the
v90→v91 bump in `sw.js`/`index.html`, and `brain/output/verify_search_clear_dethrone.py`
— ignoring the commingled v90-batch / landcover / s'mores hunks owned by other sessions.

Tier: core three (small, low-risk UI behavior change; not a sprint boundary or
publish-zone data).

```md
SEAT: witness
VERDICT: clear
ISSUE: none
EVIDENCE: Re-ran both verifiers live on :8001 — verify_search_clear_dethrone.py 8/8 PASS
  (highlight 1→0 on backspace-empty; active row sat-proline-fire→null + highlight 1→0 on
  Escape), verify_label_border_persist_firepit.py 13/13 PASS, 0 console errors. The
  verifier drives the app's own input/keydown/click handlers and reads the live
  getSource('search-highlight') data + .calendar-row.active DOM (observes before/after,
  proving removal). node --check OK.
NEXT: none

SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: Every in-scope hunk traces to the directive (clear highlight + de-throne on
  clear); no off-farm work (no popup-close, no blur-on-keystroke, no touch to the hold
  behavior). v90→v91 is a served shell-asset change (correct trigger, not creep). Git gate
  untouched: git log -1 = ee7f5cd v90 (no agent commit), no add/commit/push, no attribution.
  Brain records additive. The "no blur on typing path" restraint is the right call.
NEXT: none

SEAT: quartermaster
VERDICT: andon -> resolved clear
ISSUE (andon): clearActiveSelection copied the de-throne block verbatim from gotoMatch.
FIX: extracted dethroneActiveEvent() called from both gotoMatch and clearActiveSelection;
  `activeEventSessionId = null` now appears exactly once. The novel clear-highlight setData
  + pulseRAF-cancel kept as-is. The SET twin (gotoEventSession) left untouched — separate
  concern, not the flagged duplication.
EVIDENCE (re-review): grep "activeEventSessionId = null" → 1 assignment (inside the helper).
  C1/C2/C6 contract greps hold. node --check OK.
NEXT: none
```

Steward verdict: **CLEAR** — all three convened seats clear (Quartermaster's andon
resolved + re-reviewed). UNCOMMITTED; the v90→v91 bump and the commit remain the user's
git gate. Tier-0 whole-tree marker is best-effort under the live concurrent sessions
(s'mores, v90 batch, landcover) — this per-task receipt is the durable clearance.
