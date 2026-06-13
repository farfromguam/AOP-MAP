# Sprint 11 — Client convergence (the real debt) + the data x-ray

TL;DR:
- The user (2026-06-10) asked, exhausted, for an honest assessment: how much of this is
  worth keeping, how much is paper mache, and is the client littered with per-layer adapter
  code. They asked for a **table viewer for all data sources** so they can see under the hood.
- The x-ray got built and verified: **`website/data_sources.html`** + its generator
  **`mvp/scripts/build_data_manifest.py`** → `website/data/_data_manifest.json`. Shipped card:
  `_done/data_source_inventory.md`.
- The honest finding (the three layers of reality, below) is that **the data spine is good and
  the client is the debt** — not the other way around. The spine card for fixing it is
  `client_layer_registry.md`.

#aop #sprint #11 #client #convergence #data_xray #diagnosis

-----

## The assessment (2026-06-10) — three layers of reality, in very different states

Grounded in the live DB, the served files, and a grep of the client — not in memory.

**① The spine — PostGIS store of record — SOLID. Keep all of it.**
The "many different schemas" the user remembers fighting are gone at the DB level. The 2026-06-07
gold cleanup folded eight per-layer `core.*` tables into **one** `core.features` (CMFS spine columns
+ free-form JSONB `attrs`, no key allowlist). 160 rows across 12 layers, all one row shape. Siblings:
`core.events` (13, the WHEN), `core.activities` (12, the reusable WHAT), `core.event_meta` (1, the
umbrella), `source_register.sources` (12) + `feature_sources` (15) for provenance, `raw.*` capture
tables. `publish.features` is the one publish gate (6 rows pass it today). This is a legitimately
normalized design. It is not paper mache.

**② What's served — `website/data/` — MIXED, but mostly principled; just never mapped for the user.**
31 files. Classified by origin in the manifest: **6 core-backed** bakes (publish.geojson, buildings,
cemeteries, trail_network, visitor_context, event_schedule — these trace to the spine), **6 sidecars**
(authored copy joined at bake), **1 runtime-buffer** (editor scratch), **18 raw-pipeline** (contours,
landcover, water, roads, OSM, SFWDA traces, lidar, synthetic activity — imagery/terrain/derived that by
northstar design never passes the publish gate). It *looks* like "30 schemas"; it's really ~6 spine
shapes + a pile of derived coverage. The viewer now draws that map.

**③ The client — `website/js/main.js` (~10.6k lines) — large, but NOT the paper mache I first called it.**
First pass I read a raw grep (~800 per-layer string references, 40–87 per layer) as "adapter slop" and
told the user the client was the real debt. **That was an overstatement — corrected on inspection.** Most
of those ~800 hits are *legitimate*: the declarative `FEATURE_LIST_LAYERS` registry's own spec keys
(main.js:2187), the `TUNABLE_LAYERS` paint registry (main.js:1711), inherent MapLibre style setup (26
sources, 82 style layers like `cemetery-fill`/`cemetery-outline`), and history comments. The actual
anti-pattern — per-layer behavior branches at call sites — is the project's **C1 contract**, and a direct
grep confirms **C1 = 0** (no non-comment `layerKey === '...'` branches) and **C6 = 0** (no class
hierarchy). Prior sprints (06/08/09) already did the convergence; it meets its own enforced contracts.
The honest residual is **file size / modularity** (one 10.6k-line file is hard to navigate), which is an
*optional* refactor, not urgent debt.

**Reframe for the user (corrected):** you have MORE worth keeping than you feared on BOTH sides — the
data spine is normalized AND the client already meets its own convergence contracts (C1=0). The
"movie set / paper mache" fear, checked against the actual bones, is mostly fear. There is no big
client-rebuild grind owed. See `client_layer_registry.md` for the (small) residual and the real punch
list of what genuinely remains.

## The slate (thin vertical slices, each green before the next)

1. **`_done/data_source_inventory.md` — SHIPPED + VERIFIED.** The x-ray page + generator. Re-runnable.
2. **`client_layer_registry.md` — the spine.** One data-source registry/loader in the client that every
   layer flows through, then migrate layers onto it one at a time. Each migration verified by the
   existing playwright suite (the per-layer verifiers already exist — they are the safety net).
3. (Earned later, not pre-carded) sidecar→core convergence; the publishability story for reference
   layers; dead mockup-HTML cleanup. Card these when slice 2 proves the pattern.

## Loop contract

The convergence work is a candidate for a ralph loop, BUT slice 2 edits the **production client** in a
high-blast-radius file. Per `work_independently` "stop only for true forks / irreversible," the loop is
**not** started blind: the user picks the green light and the first slice. No commits without the user's
git gate (`no_commits.md`).
