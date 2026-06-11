# Council receipts — G_meta slice (maturity / `_meta` / manifest survive a fresh volume)

Date: 2026-06-10 · HEAD `bcea502` · Tier: **full six** (publish-zone served data + a bake/manifest migration).

Goal (from the card): make maturity / `_meta` / the schema manifest reproducible by the bake from the
committed `website/data/_schema.json` — not carried forward from the prior served file nor derived from
panel-tree position — so they survive a fresh volume. Findings closed:
`reference-bake-no-meta-on-fresh-volume`, `schema-manifest-stale`, `maturity-tier-derived-from-panel-tree-position`.

Diff under review: `mvp/scripts/{export_publish_geojson.sh,rebake_canonical.py,stamp_maturity.py,regen_meta.py,verify_gMeta_bake.py,playwright_verify_gMeta_maturity.py}`
· `website/js/panel.js` · `website/data/_schema.json` · the 5 served geojson (`aop_buildings`,
`aop_cemeteries`, `aop_trail_network`, `aop_visitor_context_callouts`, `publish`) · `brain/output/gMeta_design_20260610.md`.

## Verdicts

```
SEAT: witness        VERDICT: clear
```
Re-ran every verifier against the running system. `verify_gMeta_bake.py` PASS (fresh-volume strip-and-rebake
reproduces `_meta` incl. the trail gold block byte-identical to HEAD from `_schema.json` alone; manifest
self-heals 999→5 / 1999→today, curated fields preserved). `playwright_verify_gMeta_maturity.py` 19 PASS on
live DOM (Tier chip renders the baked tier, and FOLLOWS `props.maturity` mutated to a sentinel "Reference" —
a pre-fix panel.js would show the node literal). Own keyed diff vs HEAD: served delta is exactly `+maturity`
per feature, geometry unchanged, nothing dropped. Buildings `--check` DRIFT independently proven order-only
(multiset-equal) + pre-existing (reference-arm SQL has no `ORDER BY`). DB 160/159 intact.

```
SEAT: warden         VERDICT: clear
```
Every hunk traces to one of the 3 findings; out-of-scope items (`feature-visibility-paint-filter-as-curation`,
G_C, G_D) untouched and still `[ ]`. Git gate untouched: no commit since `bcea502`, no `sw.js`/`#appVersion`
bump (still v62), no attribution, no `down -v`/`DROP`/`TRUNCATE`. Owed v62→v63 bump reported, not made.

```
SEAT: quartermaster  VERDICT: clear
```
One store of record (`_schema.json`); the old `_meta`-carried-from-prior-file path is demoted to a
fresh-volume FALLBACK in both bake arms + rebake. `regen_meta.py` is ONE shared helper imported by both
`export_publish_geojson.sh` (last writer) and `stamp_maturity.py`; `rebake_canonical.write_manifest`
preserves the identical curated key set so the two writers can't drift. panel.js EXTENDS the existing
`nodeMaturity` path (`props.maturity || nodeMaturity(node)`), no parallel resolver. C1=0 / C2=1 / C6=0
structural greps at target.

```
SEAT: mason          VERDICT: andon → (fix) → clear
```
**Andon (first pass):** `regen_meta.py` shipped `gold_trail_meta()` + private-only helpers `_band`,
`_COLOR_LEGEND`, `_PROPERTY_SCHEMA` (~65 lines) with ZERO callers — kept "for a future re-author," which is
the dead-code / YAGNI failure mode. Storing the gold block verbatim (correct, since recompute is lossy) makes
the recompute fn dead, not deferred. **Fix:** the four symbols + the orphaned `Counter` import + the docstring
paragraph pointing at them were removed (pure deletion, untracked file, ~65 lines). **Re-review:** clear —
symbols gone with no dangling reference, module parses and stays coherent (`_load_schema`, `served_top_meta`,
`has_store`, `capture`, `regen_manifest`, `main`), `verify_gMeta_bake.py` re-run still PASS (behavior-preserving;
it never used the removed symbols), scope not widened, version strings still v62. Cleared the rest first pass:
no limiting code (maturity is an additive display map with safe fallback — absent/empty → node literal,
unknown tier passes through, never throws/whitelists/drops), idiomatic to `mvp/scripts/*.py`, minimal.

```
SEAT: scribe         VERDICT: clear
```
All 3 finding checkboxes flipped to `[x]` with the acceptance artifact named (not vague "done"); card
status-log + handoff updated; owed v62→v63 bump + HEAD `bcea502` stated plainly in both; finding ids / verifier
filenames / `panel.js:1485` treated as concrete grep-able references; two held items (buildings order-only
DRIFT; gold block verbatim-not-recomputed) recorded honestly; prose in the user's plain voice.

```
SEAT: steward        VERDICT: clear
```
Product lens: the slice serves the promise — *make the map trustworthy before interactive* — by making
maturity/provenance reproducible from a committed store of record (survives a fresh volume), carrying
provenance through rather than dropping it. Tier (full six) right for publish-zone data. No core fork batched.
Synthesis: every convened seat clear after the single grounded Mason andon was fixed and re-reviewed.

## Outcome
**FULL SIX CLEAR.** Clearance marker written to `.claude/.council-cleared` (hash over `website`+`mvp`).
Owed — the user's git gate: a **v62→v63 bump** (served `_meta`/`_schema.json` + the `panel.js` shell asset),
not made. Separately owed (out of this slice): a deterministic `ORDER BY` on the buildings reference-arm bake;
re-authoring the stale trail gold block (a data-correctness call).
