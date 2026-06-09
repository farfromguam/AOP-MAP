# Council done-review — shadow-attribute resolution slice A5 (2026-06-09)

**Slice:** Path A / A5 — edge-dispatch → spec strategies (C1). The LAST Path-A slice; the loop STOPS at the
Path A/B boundary after it.
**Tier:** full six (editor JS with a behavior-affecting create path; sprint-closing C1 convergence).
**Closes (5 catalog ids):** `host-create-bridge-hardcodes-editorpois` · `visitor-list-source-chip-freestanding-map` ·
`panel-explicit-host-toggle-map` · `panel-userfeatures-source-special-casing` · `panel-positional-synthetic-index-identity`.
**Diff under review (A5 increment — pure JS, no data change):** `website/js/main.js` (`spec.create` capability +
the create-bridge dispatch; `sourceChip` co-located on 4 specs + the read; `VISITOR_LIST_SOURCE_CHIP` deleted),
`website/js/panel.js` (`USER_FEATURES_SOURCE` const + `usesUserFeatures` predicate replacing the `'userFeatures'`
literals; `node.hostToggle` + the sfwda node field, `EXPLICIT_HOST_TOGGLE` deleted; deriveItems canonical-id
fallback), the new verifier `mvp/scripts/playwright_verify_shadow_a5_dispatch.py`, the card A5 DONE block + the 5
audit-catalog DONE-A5 annotations.

**RESULT: FULL SIX CLEAR.** One Witness flakiness andon was folded mid-review (see below) and re-confirmed.

-----

SEAT: witness
VERDICT: clear (after a folded andon — re-confirmed)
ISSUE (folded): the FIRST A5 verifier's final sub-assertion ("select the bridge-created feature in the panel")
was a re-seed RACE — the embedded panel only re-seeds its working copy on its own commitFeature (panel.js:2092)
or at boot, so whether the bridge-created feature appeared in the panel tree was non-deterministic (it PASSED in
the Witness run, FAILED in the parallel Mason run). FOLD: that step was replaced by two deterministic live
editability checks (edit the created feature through the panel's edit bridge AOP_HOST_SET_FEATURE_PROPS → the
live source reflects the rename; + the panel editorPois Name input live-editable on the always-present seed POI).
EVIDENCE: re-ran the revised `playwright_verify_shadow_a5_dispatch.py` 5 consecutive times on the live :8001
viewer — all RESULT: PASS, exit 0, 0 console errors, distinct fresh `poi_*` ids, create before/after `1 -> 2
found=True` every run. The create path is real (`AOP_HOST_CREATE_FEATURE` → main.js spec.create dispatch →
editorPois `create`→addDrawnPoi; 'buildings' → null). The edit check observes the live MapLibre source after a
real `setData` (AOP_HOST_SET_FEATURE_PROPS → setFeatureProperty → persistProperty → refreshEditorSource →
source.setData → re-read = "Restroom (renamed)"). The seed Name input reads a real DOM `.field-input` value.
Structural assertions read the shipped files (C1=0 non-comment layerKey===, C6=0 class, the dispatch maps gone).
A1/A2/A3/A4 verifiers re-run → all PASS. NEXT: A5 andon CLOSED.

SEAT: quartermaster
VERDICT: clear
ISSUE: none — A5 CONVERGES per-layer call-site special-casing into the one spec/node registry; it does not
multiply.
EVIDENCE: C1 region grep on main.js = 0 non-comment `layerKey === '` branches; A5 added NO new `=== '<literal>'`
/ `!== '<literal>'` call-site dispatch. The four edge-dispatches converged onto the ONE registry/node: create
bridge reads `spec.create` via `FEATURE_LIST_LAYERS[layerKey]` (variable index, the literal guard GONE); the chip
reads `spec.sourceChip` (VISITOR_LIST_SOURCE_CHIP deleted, `sourceChip` a field on 4 existing specs); the host
toggle reads `node.hostToggle` (EXPLICIT_HOST_TOGGLE deleted, field on the existing sfwda node); userFeatures →
ONE `usesUserFeatures(spec)` predicate (1 def, 5 call sites) + ONE `USER_FEATURES_SOURCE` const. deriveItems
reuses the canonical `props.id` (no new id scheme). C6: 0 classes, no new top-level registry, no new website/*.html;
C2: one `collectStarredDestinations`. The verifier reuses `playwright_base.viewer_url`. `node --check` clean.

SEAT: mason
VERDICT: clear
ISSUE: none — A5 adds dispatch, never rejection; safe defaults, no throw-on-absence, no dead code, no foreign
idiom, behavior-preserving on every point I own.
EVIDENCE: the create bridge `if (!spec || typeof spec.create !== 'function' || ...) return null` — a layer without
the capability returns null, never throws (live: 'buildings' → null). `(spec && spec.sourceChip) || layerKey`,
`node.hostToggle` (falsy-safe), `usesUserFeatures(spec)` = `!!spec && spec.source === USER_FEATURES_SOURCE` (safe on
null). deriveItems id-fallback fires only when `spec.key` is falsy; ALL 9 items-nodes declare a `key`, so the new
branch is dead-defensive, never live — no dedup collision possible (no key-less node exists). No CHECK/enum/validator/
row-dropping filter. The removed maps (VISITOR_LIST_SOURCE_CHIP, EXPLICIT_HOST_TOGGLE) are fully gone (not
commented-out); `idx` still referenced (last-resort fallback). All new capabilities are read somewhere. `node --check`
clean. (The verifier-flakiness note is a Witness item, folded above — not a Mason finding.)

SEAT: warden
VERDICT: clear
ISSUE: none — every A5 hunk traces to one of the five named findings; the git gate is untouched; the loop stopped
at the Path A/B boundary.
EVIDENCE: the five findings → hunks all traced (create bridge → spec.create; sourceChip field; node.hostToggle;
USER_FEATURES_SOURCE+usesUserFeatures; deriveItems canonical-id). The userFeatures multi-site touch is the SAME
finding (converging the one literal). Surface area is pure JS — only main.js + panel.js tracked-changed by A5; the
served *.geojson set belongs to A1–A4 (cleared); the verifier writes no data. No Path-B DB/identity/localStorage
door added; gold slice 6 (`../06_going_gold/gold_migration.md`) untouched. Git gate UNTOUCHED: HEAD e34c1b8, no
commit, no sw.js/#appVersion bump in the diff (owed, reported). Card directives intact (the Path-A/B boundary +
the Path-B HELD list preserved; A5 DONE block is an addition). Means-divergence noted (not drift): the card named
`spec.idField`; the shipped fix uses the canonical `id` VALUE — same finding closed.

SEAT: scribe
VERDICT: clear
ISSUE: none
EVIDENCE: the A5 DONE block (card, before the PATH A/B BOUNDARY line) records the 5 closes, the deterministic
live-DOM verifier + RESULT: PASS, the folded Witness andon, and the owed git gate (rides the one Path-A batch bump +
commit). All 5 A5 `Closes:` ids grep-resolve to one catalog home each and carry append-only `DONE A5 (2026-06-09)`
annotations mirroring A1–A4's form; coverage line A5=5 consistent. The receipt records all six seat verdicts + the
Steward synthesis. Handoff updated (A5 done; PATH A COMPLETE; NEXT = the user's commit/bump + optional gold slice 6).
Voice plain/terse, references concrete (treated as the thing), no misspellings.

SEAT: steward (chair)
VERDICT: clear
SYNTHESIS: A5 closes Path A — the C1 convergence the audit named. Five per-layer call-site special-casings (the
create guard, the source-chip map, the host-toggle map, the userFeatures literal, the positional-index identity)
are now declarative spec/node capabilities with safe defaults: behavior lives in the spec, the call sites name no
literal, and an unrecognized layer/value still renders (no limiting code). The one user-facing path (create) is
observed live and deterministically; the structural-only sub-changes are honestly labeled as such (they render
into the hidden #editorTree under embed). The Witness flakiness was folded into a deterministic verifier and
re-confirmed 5/5 — verification reliability, not just a passing run. Additive, on-farm, git gate untouched, A1–A4
unregressed. **The ralph loop is DONE: Path A (A1·A2·A3·A4·A5) is complete and council-cleared; the loop STOPS at
the Path A/B boundary.** Owed remains the user's: ONE `sw.js`/`#appVersion` bump + one commit covering the whole
Path-A batch. Path B (gold slice 6 — DB door / identity / bake reproducibility) is HELD for the user's pull.
