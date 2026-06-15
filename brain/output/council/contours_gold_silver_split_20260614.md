# Council receipt — contours GOLD curated / full set demoted to SILVER (2026-06-14)

**Goal:** *"the major lines for the whole 9 patch and the minor lines for just the park
bounds … current data demoted to silver and this new bit our gold dataset."* Served gold
contour layer curated to a lean subset; full set preserved as silver.

**Change (this task — viewer_core.js is commingled with cleared prior work, no JS change here):**
- NEW `website/data/silver_aop_contours.geojson` (2,831 feats, `_meta.maturity: silver`, ~12.9 MB, NOT served).
- REWROTE `website/data/gold_aop_contours.geojson` lean (911 feats = 501 index whole + 410 minor clipped to the park center cell, `_meta.maturity: gold`, ~3.9 MB).
- NEW `mvp/scripts/curate_contours_gold.py` (shapely, no GDAL); `build_contours.sh` post-bake wiring (full→silver→curate→gold; stale un-prefixed output path fixed); `_data_manifest.json` re-stamped + silver entry; doc records (card, viewer.md, handoff).

**Tier:** core three + Mason (curation/clip correctness + no-limiting-code) + Scribe (maturity
demotion must land across data `_meta` / manifest / brain). **Deterministic gate:**
`python3 -m py_compile` on the script, `bash -n build_contours.sh`, manifest JSON valid.

## Verdicts

```md
SEAT: witness — VERDICT: clear
Re-ran verify_contours_curated_gold.py on live :8001 → 13/13 PASS, 0 errors. Live source count (911 =
501 index + 410 minor) read off the running MapLibre map after #presetTopo; both contour layers visible;
PARK fetched 0 contour files, TOPO fetched gold. Triangulated the minor-clip invariant independently
(all 54,281 minor vertices): worst margin outside the raw cell is 1.59e-7 deg = the 6-dp rounding the
script applies after shapely intersection; EPS=1e-6 (~0.1 m) is tight, not loose (a 1 m-outside point
would FAIL). Index spans 3.07x the cell, 89% of index vertices strictly outside (9-patch context) + also
inside (park labels). Silver 2831/silver, gold 911/gold, gold=29.6% of silver.
BLIND SPOTS: "visible" is the layout property, not a rendered-pixel receipt (basemap tiles blocked
headless); index-everywhere proven by coords not a screenshot; verifier rolls its own Playwright harness.

SEAT: warden — VERDICT: clear
Directive met exactly: index ID sets IDENTICAL gold↔silver (all 501 kept whole, none dropped); all minor
vertices inside the park cell; index reaches outside + inside. Data preserved — silver = full 2831,
raw/aop_contours.geojson intact, 0 deletions under website/. GDAL portion of build_contours.sh honestly
flagged unverified (no GDAL here); the curate step is what ran + verified. Git gate untouched: HEAD
813d4c9 (user commit), git diff of sw.js/index.html EMPTY, both v92, no agent bump/attribution; owed
v92→v93 stated. No JS change this task (the viewer_core.js hunks belong to cleared prior sessions).

SEAT: quartermaster — VERDICT: clear
No clip/bbox helper existed to reuse (shapely box/intersection/mapping direct = simplest reuse). One
pipeline post-step (build_contours.sh: silver→curate→gold), not a parallel bake. Viewer unchanged, reads
gold + filters by idx. No dead code; no orphaned un-prefixed aop_contours.geojson left. C1=0, C6 (0
classes/no new editor html), C2 (1 collector) hold.
NEXT (flag, not andon): the center-cell bbox is triplicated — curate_contours_gold.py, viewer_core.js
PARK_BOUNDS_FALLBACK, main.js — against research/aop_data_bounds.md's canonical, but no importable bounds
module exists today. Future dedup when one is created; pre-existing, not introduced here.

SEAT: mason — VERDICT: clear
BUILD-TIME data curation, not runtime limiting code (full set preserved as silver; viewer drops no live
row). PERMISSIVE per R13: unknown idx kept whole (else branch), empty intersection→None (only genuinely-
outside lines), corner-touch Point dropped, GeometryCollection→line members merged; NO raise/assert/
validator. Clip correct across all shapely result types (verified empirically on 2.0.7 w/ the real bbox).
Precision 6 dp matches the source (build_contours.sh -lco COORDINATE_PRECISION=6); properties (incl.
elev_ft the viewer's opacity/label filters need) pass through. bash -n clean; no stale host output path
survives (bare aop_contours.geojson refs are the in-container /data mount). Idiom matches sibling scripts.

SEAT: scribe — VERDICT: clear
All surfaces agree end-to-end: data _meta (gold=gold/911, silver=silver/2831, notes explain the split);
manifest re-stamped (gold 3.91 MB/911 curated note + new silver 13.22 MB/2831 not-served note) — matches
the files exactly, no stale 13 MB/2831 gold anywhere; card dated update with numbers + script + wiring +
13/13 + GDAL-honesty + owed v93; viewer.md catalog updated; handoff pointer present. Fixed one dead
pointer in-pass (handoff cited a council receipt not-yet-written → repointed to the verifier).
```

**Steward synthesis:** full clear — Witness · Warden · Quartermaster · Mason · Scribe all
`clear`, no open andon. Gold served data dropped 13.2 MB → 3.9 MB (index everywhere + minor
in the park); full fidelity preserved as silver; curation is build-time + permissive (not
limiting code); records coherent across data/manifest/brain. **User's git gate (owed):** the
served-data change rides the same **v92→v93** bump + commit. **Carry-forward NEXT
(Quartermaster):** the park center-cell bbox is triplicated against `aop_data_bounds.md`'s
canonical — converge onto a shared bounds source when one exists.
