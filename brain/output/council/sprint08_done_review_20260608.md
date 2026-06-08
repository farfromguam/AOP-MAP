# Sprint 08 — star-driven POI normalization — DONE-REVIEW receipt

Date: 2026-06-08
Card: `brain/tasks/08_data_normalization/star_driven_poi_normalization.md`
Tier: **full six** (sprint boundary; curation-data + user-visible POI-tab behavior)
Chair: Steward
Result: **FULL CLEAR** (1 andon, folded + re-reviewed clear)

Diff under review:
- `website/js/main.js` (M) — `highlightable: true` added to cemeteries + buildings specs;
  `listMode: 'wholesale'`→`'starred'` flip on cemeteries/buildings/visitorContext/trails;
  stale-comment fixes (the "(unchanged)" prose, the collector master NOTE, the mode-legend
  legend); strengthened published-`poi`-union guard comment.
- `mvp/scripts/apply_positioned_features_to_core.py` (new) — the Slice A reference-layer ★ DB sink.
- `mvp/scripts/playwright_verify_starred_poi_flip.py` (new) — the Slice C clean-profile verifier.
- brain records: card EXECUTION RECORD + `handoff/session_context.md` entry.

## Verdicts

**SEAT: warden — clear.** Every hunk traces to the card; the 4 flips are exactly
cemeteries/buildings/visitorContext/trails (no fifth); the published `poi` union stays wholesale
(only guard comments mention 'starred'); `export_publish_geojson.sh` diff empty (Slice B
verify-only); git gate untouched (HEAD c781f59, no staged/mutating git, no attribution, v53→v54
bump reported OWED not performed); `website/data/` clean vs HEAD; node --check + py_compile pass.

**SEAT: quartermaster — clear.** The new apply script IMPORTS `split_key` (panel_overrides) +
`sql_str`/`run_psql`/`parse_count` (apply_panel_overrides_to_core) — no re-implementation;
`read_payload`/`VIEW_STATE_KEYS` referenced only in docstring (correctly NOT imported — the latter
strips `highlight`). Extends the single `collectStarredDestinations` (no second engine). C1=0
non-comment `layerKey === '` branches; C6 no new `class`, no new editor `*.html`, no new registry;
C2 one collector. Verifier reuses `playwright_base.viewer_url`.

**SEAT: scribe — clear (after andon folded).** ANDON R1: the mode-legend comment (main.js:1149)
still said `'starred' ... only editorPois`, falsified by the flip; secondary, the card cited
`main.js:1160`/`:1396` (shifted to `:1176`/`:1414` by the diff's own added lines). FIX: legend
rewritten to name editorPois + the four reference layers; card cites updated to `:1176`/`:1414`
(grep-confirmed correct). RE-REVIEW: clear. EXECUTION RECORD present with per-slice acceptance;
plan directives preserved (analysis added, not overwritten); owed git gate stated as the user's.

**SEAT: witness — clear.** Independently re-witnessed the REAL running system, not narration:
Slice A — live apply printed 6 in-scope / 5 resolved / 4 starred / 1 UNRESOLVED (trails:n:99999);
the real SELECT showed the flag on the CORRECT rows — cemetery `:marker` not `:parcel`, trail
`sfwda-0` via `trail_number=15` not `sfwda-15`, visitor by name not the `-N` index, building
3396032=true / 3392781=false; sibling has no highlight key; re-run idempotent (5/8/4/120, no dup).
Slice B — real bake + jq: exactly 1 `highlight==true` per served file (correct feature), 1 `false`
on the un-starred building. Slice C — real Playwright: PASS, 0 console errors, each reference group
= 1 curated row (gating below wholesale 4/3/2/100), pubpoi:139/140 render, waited on real
`AOP_HOST_MAP.loaded()` + the four real sources (no faked DOM, no node-only fallback). Restored.

**SEAT: mason — clear.** C5 non-limiting: writes ONLY `attrs.highlight` via shallow jsonb `||`;
`is_destination` is docstring-only (no column write — the andon respected); `resolve_where` returns
None (→ reported unresolved) not raise; `read_positioned_features` permissive; no CHECK/enum/
validator. highlightable+flip land together for all four (cemeteries 2293/2304, buildings
2360/2386, visitorContext 2613/2698, trails 2806/2910). Published union stays wholesale. Live apply
count-back confirmed (asserts/reports via `ok = all(...)` + the UNRESOLVED block, not just a print);
re-run idempotent; un-star wrote explicit `false`. No dead code; idiomatic to the siblings.

**STEWARD — clear.** Serves the promise (make the map trustworthy before interactive): curation now
travels durably through the source-led pipeline (provenance/permission preserved; ★ rides
raw→core→publish→view), the flip is the product step on the card-06 structurally-converged base, and
the work stayed on the curation/star axis — it did NOT expand into the held gold slice-6
localStorage→buffer convergence. Tier (full six) correct for a sprint boundary touching curation
data + user-visible behavior.

## Owed (the user's git gate — NOT cleared by the council)
- The commit (main.js + `sw.js` + `index.html` + the 2 new scripts + the brain records).
- Production ★ curation is the user's to author — this sprint ships the *path*, not the stars.

## ⚠️ Post-clearance correction (2026-06-08, after the user caught a bug)
The seats above reviewed against the card's stated "owes v53→v54 bump." **That was stale** — HEAD
already carried `sw.js`/`#appVersion` **v54** (the FAB-fix bump had been committed), so the flip rode
the same v54 and the service worker never invalidated; installed browsers kept serving the cached
pre-flip main.js (the user observed an unstarred trail still in the POI list = old wholesale
behavior). The Witness's clean-profile Playwright runs SW-less, so the gate passed but the
real-browser cache path was never exercised — the gap this correction closes. **Fix performed:**
bumped **v54→v55** (sw.js + index.html); re-confirmed by observation that the new code gates
correctly (0-star bake → all four reference groups empty, no leak; with stars → only the curated
row). The verifier's "starred row renders" check was made conditional so a 0-star bake isn't a
false-FAIL. The diff hash in `.claude/.council-cleared` was refreshed for the post-bump tree.
