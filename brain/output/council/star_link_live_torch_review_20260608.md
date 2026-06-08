# Council done-review — live star→left-link bugfix + 🔥 torch cache button (2026-06-08)

**Steward verdict: FULL CLEAR (full six).** Clearance marker written to
`.claude/.council-cleared` (`d916acc…`) over the website/mvp diff.

## Goal (one line)
Complete the sprint-08 POI-flip's LIVE author→left-link path for the two reference layers that
silently failed (cemeteries marker/parcel twin-mismatch; trails missing panel→host bridge + missing
`applyPositionedFeatures('trails')`), and add a Torch cache button under Session tools — non-limiting,
no second engine, verified by observation, recorded.

## Tier
Full six — touches a widely-used resolution fn (`positionedFeatureIdFor`) + the user-facing star
feature, completing a slice of the sprint-08 flip (itself full-six reviewed). The already-cleared flip
hunks (receipt `sprint08_done_review_20260608.md`) rode the same uncommitted tree; seats focused on the
new hunks.

## The diff reviewed
`website/js/main.js` (`trailRowId` helper; `positionedFeatureIdFor` honors `spec.idFor`;
`persistFeatureFlagChange` re-runs `applyPositionedFeatures(layerKey, runtime.data)`; trails spec
`idFor`; `applyPositionedFeatures('trails', …)` at registration; `torchCache()` + button const +
wiring), `website/js/panel.js` (`hostKey:'trails'` on `aopTrails`; stale no-hostKey comment corrected),
`website/index.html` (`#torchCache` button + `#appVersion` v56), `website/sw.js` (VERSION v56), new
`mvp/scripts/playwright_verify_star_links_live.py`.

## Seat verdicts (all `clear`)
- **witness — clear.** Re-ran live on :8001: `playwright_verify_star_links_live.py` all 9 PASS (each of
  the four layers surfaces a fresh ★ 0→1 AND survives reload; trails proven with `__trail_row_id`
  STRIPPED → exercises the new `trailRowId`/`idFor` derivation). Regressions PASS
  (`starred_poi_flip` still gates, `star_collector`, `data_groups_embed`). `node --check` clean. C1=0,
  no new class, the "row-dropping" diff hits are C5-guardrail comments only. Served `#appVersion`=v56.
- **warden — clear.** Every hunk traces to the directive; "some code is lacking" authorizes the fix, not
  just a report. Button under `session-tools` beside Reset viewer. Git gate untouched (HEAD `c781f59`,
  no staged, no attribution); v55→v56 is a working-tree edit matching project practice; commit OWED. No
  drift into held gold slice-6. Card directives preserved additively.
- **quartermaster — clear.** Genuine reuse: one `applyPositionedFeatures` (def main.js:3078; +2 call
  sites), one `trailRowId` (def :3024) that REPLACED the old inline stamp derivation, `spec.idFor` a
  generic hook (not a layerKey branch), `hostKey` the existing bridge, new verifier distinct coverage
  (live author loop vs flip's baked clean-profile). No C1/C2/C6 violation.
- **mason — clear.** No limiting code (`trailRowId`→null for unnamed edges preserves the pre-existing
  identity-absence behavior, byte-for-byte; not a new vocabulary gate). Re-apply idempotent. `torchCache`
  touches only Cache Storage + SW registrations, never localStorage (stars/edits survive). No
  throw-on-unknown; try/catch fallbacks. Idiomatic.
- **scribe — clear.** Handoff + card accurate to the diff; OWED (the commit) + the performed v55→v56 bump
  stated; completion recorded as a by-observation acceptance result; new verifier named; no durable fact
  left only in chat; voice plain. No peer-reference surface.

## Non-blocking nit (fixed in-review, not an andon)
Witness + Mason both flagged the `panel.js` comment that still listed "trails" among no-hostKey nodes —
now stale after `hostKey:'trails'`. Corrected to name the four bridged layers + brand-logos-only
exception. Comment-only; behavior unchanged.

## OWED (the user's git gate)
The commit — 4 `website/` files + `mvp/scripts/playwright_verify_star_links_live.py` + the brain records
(handoff + card + this receipt). Production ★ curation stays the user's to author.
