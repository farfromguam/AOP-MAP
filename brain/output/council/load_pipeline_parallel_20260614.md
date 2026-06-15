# Council receipt — load pipeline parallelized (v94)

Date: 2026-06-14
Steward tier: **core three** (Witness · Warden · Quartermaster)
Goal: speed up the viewer's load pipeline without changing what renders.
Scope: clean tree — only this task's changes (prior work committed at `727b910`). No commingling.
Diff: `website/js/viewer_core.js` (parallel-fetch kickoff in `map.on('load')`; publish started up-front),
`website/sw.js` + `website/index.html` (v93→v94 bump), brain recording + two `brain/output/` artifacts.
Tier-0: `node --check website/js/viewer_core.js` PASS.

## Verdicts (all clear)

```
SEAT: witness
VERDICT: clear
ISSUE: none (note: the "4,113 ms / concurrency 2" BEFORE baseline and "36 tiles" are narrated, not
  re-observable from the current tree — the serial pre-fix code is gone; the AFTER state is fully observed)
EVIDENCE: Ran verify_load_pipeline_parallel.py 3× live against :8001 (serves the edited viewer_core.js —
  "Parallel data kickoff" + "await publishFetch" confirmed in served bytes): max concurrency 13, data span
  ~400-430 ms, 14/14 PASS, exit 0, 0 console errors, reproducible. Independently confirmed SW genuinely
  blocked (controller=none) and CDP latency genuinely applies (min req dur 2ms→122ms @120ms RTT) —
  concurrency/span from real Resource Timing, not re-derived math. All 12 layers present via live
  map.getLayer(); Park PNG renders every layer. HEAD shows a true 12-call serial await chain.
NEXT: none
```

```
SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: git diff HEAD + status reviewed vs directive ("speed up loading"). Code confined to
  viewer_core.js (+38) and the two version strings; only added addLayer-matching line is a COMMENT —
  no style/order/filter/data mutation. Behavioral change is solely WHEN fetches start. fetchJson genuinely
  memoizes, so downstream awaits resolve the in-flight request; publishFetch consumed once; ensureContours
  + SFWDA build untouched. Git gate untouched — git log -1 = 727b910 (user's), nothing committed; reported
  UNCOMMITTED / "commit remains the user's". v94 bump consistent (sw.js VERSION + #appVersion), no
  DATA_ASSETS/precache touched. SFWDA-lazy follow-up genuinely deferred (.webp still loaded inline at 2192,
  only cache-warmed in kickoff). node --check PASS.
NEXT: none
```

```
SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: Reuses existing memoized fetchJson (viewer_core.js:363-378, _fetchJsonCache keyed on url).
  All 11 prefetch URLs match downstream await sites exactly (no double-fetch). publish started once
  (publishFetch) + awaited in place; old inline `await fetch('./data/gold_publish.geojson')` GONE.
  Image cache-warm is a one-shot fetch().arrayBuffer() discard — NOT a new image registry; existing
  loadImageEl + new Image() paths untouched and reread the warmed cache. ensureContours untouched;
  contours excluded from prefetch (stay lazy). Contracts: C1=0 non-comment layerKey branches in main.js;
  C6=0 new `class [A-Z]`, no new editor *.html (index.html = version bump only); C2=one
  collectStarredDestinations. node --check PASS.
NEXT: none
```

## Steward synthesis

Every convened seat `clear`. The fix is a behavior-preserving reordering of WHEN the load handler's
independent fetches start: it reuses fetchJson's existing memoization so the downstream await chain
(and thus addLayer stacking) is untouched, and it is verified by an observed measurement of the running
system (concurrency 2→13, span ~4,100→~400 ms) plus a render screenshot and a 12-layer presence read.
Owed to the user (their git gate, not the council's to clear): the commit, and the v93→v94 bump is
already performed as edits. **Gate cleared.**
