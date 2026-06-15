# Council receipt — schedule rows drop the raw #tag prefix (2026-06-14)

**Goal:** Remove the internal `#tag` join-key prefix from the user-facing
event-schedule calendar rows so each row shows just the human location label.
Directive: *"I dont want to see #pavilion followed by pavilion. feels redundant."*

**Change (this task's diff only — tree is commingled with concurrent sessions):**
- `website/js/viewer_core.js` `renderEventCalendar`: `.calendar-location` span
  `${escapeHtml(tag)} - ${escapeHtml(location)}` → `${escapeHtml(location)}`.
- `website/js/main.js` editor copy: identical one-line change.
- `brain/output/verify_schedule_no_tag_prefix.py` (new verifier, 8/8 PASS on `:8001`).
- Doc records: `tasks/01_mvp/_done/event_schedule_layer.md` addendum + handoff Latest.

**Tier:** core three (Witness · Warden · Quartermaster) — copy-removal, data
unchanged, observation-verified, low risk.

**Deterministic gate:** `node --check` passes on both changed JS files.

## Verdicts

```md
SEAT: witness
VERDICT: clear
ISSUE: none — "verified by observation" is backed by a reproducible observation, not narration.
EVIDENCE: Re-ran verify_schedule_no_tag_prefix.py against live :8001 → RESULT: PASS, 8/8,
  console_errors: []. Verifier reads real rendered .calendar-location textContent + the live
  resolver source (getSource('event-schedule')). 18 rows == 18 resolver sessions; all 8 #pavilion
  rows render "Pavilion (base camp)", all 3 #firepit rows "Firepit", zero raw '#'. curl of
  :8001/js/{viewer_core,main}.js shows the patched lines (no stale cache).
NEXT: none.

SEAT: warden
VERDICT: clear
ISSUE: none — both hunks map 1:1 to the directive; data/popup-diagnostic/unrelated UI untouched; git gate intact.
EVIDENCE: git diff HEAD shows only the two calendar-location prefix drops; `tag` survives as fallback.
  HEAD = ee7f5cd "v90"; no agent commit, no co-author trailer, no mutating git. sw.js/#appVersion
  v90→v92 is the concurrent About-tab session's shell bump (one bump), not attributable here; no
  second bump. Card addendum quotes the directive verbatim — no deleted directive.
NEXT: the v92 bump + commit remain the user's git gate.

SEAT: quartermaster
VERDICT: clear
ISSUE: none — duplicated render changed identically in both copies; no divergence, no dead code, no new render path.
EVIDENCE: viewer_core.js:1354 and main.js:7086 both now `${escapeHtml(location)}`. `tag` remains a
  live `location_label || tag` fallback in both. Pure in-place -/+ swap, no new helper/registry.
  C1 layerKey branches = 0; C6: 0 new classes / 1 registry / no new editor *.html; C2: 1 collector.
NEXT: none. (Aside: the two-file render duplication is pre-existing from the viewer extraction;
  retiring it would mean sharing the one render, not forking a third — out of scope for this card.)
```

**Steward synthesis:** full clear — every convened seat `clear`, no open andon.
The version bump (v92) and commit remain the user's git gate.
