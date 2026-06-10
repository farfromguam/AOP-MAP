# Council receipts — G_B slice 1 (localStorage → staging buffer) · 2026-06-10

Slice: gold slice 6 **G_B** HIGH trio (G_B.1 boot read-path flip · G_B.2 one write door for reference edits · G_B.3 notes→description fold). Spec: `brain/output/gB_state_audit_design_20260610.md`.
Reviewed diff: uncommitted vs HEAD `86b6fcd "GE slice"` — `website/js/main.js`, `website/js/panel.js`, `mvp/scripts/apply_positioned_features_to_core.py`, `website/sw.js`+`website/index.html` (v61→v62 bump), + untracked spec + `mvp/scripts/playwright_verify_gB_localstorage_demotion.py`.
Tier: **full six** (HIGH-risk read-path architectural fork — the editor's published-read source).
Result: **FULL SIX CLEAR** (no andon; Mason noted one non-blocking idempotent redundancy, explicitly not worth a revision).

Orchestrator re-verification by observation: `playwright_verify_gB_localstorage_demotion.py` = **17/17 PASS** on a self-run (keystone holds EMBEDDED + STANDALONE; created/deleted still replay; fresh-LS shows baked); `node --check` clean on both JS; `git diff HEAD -- website/data` empty (served data untouched).

-----

```md
SEAT: witness
VERDICT: clear
ISSUE: none — every doneness claim is backed by a fresh observation, not narration.
EVIDENCE: Re-ran playwright_verify_gB_localstorage_demotion.py (:8001, both index.html + right_panel.html 200) →
  17/17 PASS, exit 0. A STALE name seeded into BOTH stores does NOT override baked "Front Office" (panel LOADED,
  DOM .item-select, host map source) EMBEDDED + STANDALONE; created still shows; deleted still hidden; fresh-LS
  shows baked; 0 app console errors. Falsified the assertion's teeth with a live probe: clean G_B boot renders
  "Front Office"; simulating the OLD Object.assign paint-over renders "STALE-DIFF" → DISTINGUISHABLE; the PASS
  would have FAILED pre-G_B. node --check PASS both JS. In-session edit preserved (only the 4 boot sites pass
  {boot:true}; live re-sync 3894 + commitChange in-place mutation ungated). Buildings --check drift PRE-EXISTING,
  NOT G_B (git diff HEAD -- website/data/aop_buildings.geojson empty; ordering-only, against HEAD too).
NEXT: none. Buildings --check drift is an out-of-slice bake/DB-reconciliation item. Owed user gate: the v62 bump + commit.
```

```md
SEAT: warden
VERDICT: clear
ISSUE: none — every hunk traces to G_B.1/.2/.3; git gate untouched; bump owed-not-committed and synced; served data + deferred findings untouched.
EVIDENCE: Changed set == card-scoped set exactly (apply_positioned_features_to_core.py, main.js, panel.js + sw.js/
  index.html bump + untracked spec/verifier). G_B.1→main.js applyPositionedFeatures opts.boot + 4 call-sites +
  panel.js applyStoredOverrides step-3 demote (created/deleted kept). G_B.2→panel.js commitChange hostProps bridge
  + 4 nodes hostProps:true. G_B.3→apply script notes→description fold + widened VIEW_ONLY gate. Deferred 5/6
  UNTOUCHED (grep of added lines for feature_visibility/defaultVisible/nodeMaturity/maturity/setFilter = none); no
  G_C/G_D leak. HEAD 86b6fcd unchanged, no loop commit/attribution. sw.js+index.html v61→v62 single synced step,
  uncommitted, not double-applied. git diff HEAD -- website/data EMPTY; no down -v/DROP/TRUNCATE/DELETE; 153 rows safe.
NEXT: none. Owed (user's): the commit + the in-tree v61→v62 bump (do not re-bump).
```

```md
SEAT: quartermaster
VERDICT: clear
ISSUE: none — converges onto the existing store/door, adds nothing parallel.
EVIDENCE: C1 = 0 non-comment `layerKey === '` branches in main.js/panel.js (BAKED_REFERENCE_LAYERS is a Set gated by
  .has(), not a call-site branch). C6 = 0 new class, no second registry beside FEATURE_LIST_LAYERS, no new editor
  *.html. C2 = one collectStarredDestinations. G_B.2 DELEGATES to the pre-existing AOP_HOST_SET_FEATURE_PROPS bridge
  (mirrors the unified AOP_HOST_SET_HIGHLIGHT star path) → aop_positioned_features_v1 → apply_positioned_features_to_core.py;
  hostProps:true on exactly the 4 reference nodes; NO new bridge/store/door. No twin-store re-fork (panel.js:187
  `if (!propsBridged)` skips re-storing in panel-overrides). The change REMOVES a read-replay role (C3 demote, not add).
  G_B.3 adds NO new def (fold inside existing set_clause/build_sql); other door + bake untouched (one writer). node
  --check + py_compile pass.
NEXT: none. category-as-attrs-facet is the spec's accepted Tier3 outcome, not a duplicate.
```

```md
SEAT: mason
VERDICT: clear
ISSUE: none blocking — clean purely-additive demotion, no limiting construct, no throw-instead-of-fallback, no dead code.
EVIDENCE: C5 PASS — demoteBaked gates ONLY geometry/highlight/properties boot replay (locked/icon_size still replay);
  store untouched so the diff still exports; panel created/deleted byte-unchanged (verifier CASE 2 guards it); apply
  fold additive (description wins else notes→column AND notes still in attrs); build_sql gate WIDENED (more entries
  pass), not narrowed; no CHECK/enum/validator. R13 PASS — host bridges try/catch→false, panel gates on ===true,
  falls through to buffer, never throws/loses. Boot gate fires at exactly 4 sites; live re-sync 3894 + brandLogos
  9720 ungated (full replay). In-session edit preserved; reload-until-baked is the INTENDED C3 flip (design §3),
  not data loss. No dead code (pickEditable live ×4). node --check + py_compile clean.
NEXT: optional non-blocking tidy — a bridged property+geometry edit calls pushTagToHost twice (panel.js 173+192);
  idempotent/harmless; fold only if touching the function again. Not worth a revision on its own.
```

```md
SEAT: scribe
VERDICT: clear
ISSUE: none blocking — durable artifacts exist and are honest; the keystone demotes data without destroying it.
EVIDENCE: Design doc records the TRUE per-finding state + convergence + sub-slice boundary (honest pre-implementation
  design, not a false "done"). No data loss: OVERRIDES.edits retained + still rides buildExportPayload; created/deleted
  untouched; main.js keeps locked/icon_size; apply fold keeps notes in BOTH description column AND attrs; no
  DROP/DELETE/TRUNCATE/removeItem/splice; DB door archives via archived_at. References are the thing (4 finding ids
  verbatim in the audit, addressed not paraphrased). Voice plain. git diff HEAD -- website/data empty. node --check +
  py_compile pass. Version already v61→v62 in-tree.
NEXT (orchestrator post-council, non-blocking): record the verifier PASS as this receipt; flip card G_B items 1/2/3/4
  with the GAP-B note (reference geometry still no DB door) + keystone artifact; update the design-doc status table to
  mark SHIPPED; update handoff with correct arithmetic (owed gate is v61→v62, two bumps past the stale "v60→v61").
```

```md
SEAT: steward (chair, product lens)
VERDICT: clear
ISSUE: none. Serves the promise — make the map trustworthy before interactive. The published reference view stops
  being a per-browser localStorage replay (C3 / Root 1): localStorage becomes a staging buffer for export→bake, so
  observations no longer overwrite published truth — the validation-loop discipline made real. Editor-is-the-viewer
  preserved (in-session edits still show; only stale prior-session diffs stop overriding baked truth). One home /
  one door (positioned-features → the DB column). Additive, no provenance dropped. Tier correct (full six, HIGH-risk
  read-path fork). No northstar drift.
NEXT: deferred follow-up = findings 5 (visibility, LOW) + 6 (maturity, MEDIUM, couples to the _meta-on-fresh-volume
  item) + the reference-geometry DB door (GAP B). Clear to proceed.
```
