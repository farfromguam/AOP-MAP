# Council done-review — shadow-attribute audit catalog (2026-06-09)

**Reviewed:** `brain/tasks/09_editor_maturity/shadow_attributes_audit.md` (the new card + its
FINDINGS catalog — 45 deduped shadow-attribute findings from the 8-lens seal-team sweep,
workflow `wf_eae016f9-626`) and the 2026-06-09 entry in `brain/handoff/session_context.md`.
**Diff:** brain-only, uncommitted (HEAD `4c168b2`; no `website/`/`mvp/` change → Tier-0 gate
did not fire; no clearance marker needed). **Tier:** FULL SIX (publish-zone-data planning,
high leverage; user named all seats). **Chair:** Steward.

## Verdicts

| Seat | Verdict | One-line |
|---|---|---|
| Witness | **clear** | Spot-checked 5 HIGH findings against real files — all citations hold (trail-name fork, publish.geojson-not-reproducible, `panel.js` 0 catalog refs, 87/120 numeric trail names + 120/120 null desc, `_schema.json` sidecar omission). The static-only gap is self-flagged and correctly scoped to *resolution* acceptance, not *catalog* acceptance — no unearned "verified." |
| Quartermaster | **clear** | Extends + tags F1–F9 / gold slice 6 honestly (points work AT slice 6, re-cards nothing); no second engine/registry/loader/surface; C1=0, C2=1, C6=0 greps hold on live code. |
| Mason | **clear** (after andon → fold → re-review) | See below. |
| Warden | **clear** | Diff brain-only + card-traceable; git gate untouched (HEAD `4c168b2`, no commit/bump/attribution); gold slice 6 deferred, not un-held. |
| Scribe | **clear** | Durably recorded (card FINDINGS + dated handoff); references are the literal thing (CMFS-as-target verified, `_schema.json` crosswalk omission confirmed by observation); user's plain voice; consumable (every finding = file:line + target). |

## The one andon (Mason) — folded and re-cleared

- **Andon:** four `target_canonical` lines phrased controlled vocabularies as enums/closed lists
  ("Tier1 kind from controlled list", "confidence+status mapped to source_register enums",
  "complete intensity_class vocabulary", "kind='poi'"), which an implementer could read as a
  reject/drop gate — the C5 "while I'm here, validate against an allowlist" drift. The Guardrails
  section stated the additive rule globally but never bound the controlled-vocab targets.
- **Fold:** added a **Binding** sentence to the C5 guardrail (every controlled-vocabulary target is
  a display mapping with a safe fallback — map known, pass unknowns through as their own label,
  mirror `_PUB_KIND.get(layer, layer)`; never reject/drop/coerce/throw; `source_register.md` is
  required-fields, not a closed enum) + a `*C5 NB:*` clarifier on each of the four findings
  (card lines ~85-90, 158, 160, 165, 166).
- **Re-review: clear** — Mason verified the binding mirrors the real permissive idioms in
  `rebake_canonical.py` (`first(...) or prov.get(...)`, `category or "poi"`, additive preserve of
  original keys). R13 (no throw on unknown) satisfied. No over-build (audit adds no code).

## Steward synthesis + rulings

**Outcome: FULL SIX CLEAR.** The catalog is grounded (every finding a real file:line), extends the
prior audits without duplication, stays additive/non-limiting, on-farm, and recorded. It is accepted
as the **work-list** for the cut+migrate effort. It is explicitly **not** a "verified runtime" claim —
the cross-surface disagreements are argued from divergent read sites (code observation); the live-app
confirmation is owed at *resolution*, not here.

**Ruling 1 — gold-slice-6 vs new resolution slices.** The convergence has **two physical paths**, and
the split decides which findings move now vs wait:
- **Path A — file/crosswalk (THIS card's scope, no slice-6 pull):** the served reference files are
  baked by `rebake_canonical.py` from `data/raw/`, *not* from `core.features`. So a large class of
  findings can be resolved by completing the **additive** crosswalk + `_schema.json` (register the two
  sidecars, add the Tier-3 facet block, fold the trail catalog's name/description/difficulty at the
  re-bake, unify the render-site display helpers) — **without** pulling the held DB door. **First slice
  recommendation: the trail-name convergence** (the seed that opened this) — bake canonical
  `name`/`description` from `aop_trail_catalog.json` so left == right == map label, drop the
  `trailCatalogLookup` at the read sites. Provable with a tile-independent DOM check, no slice-6 pull.
- **Path B — DB door / identity (gold slice 6, HELD — the user's pull):** the inherently DB/identity
  roots — `publish.geojson` not reproducible from the DB, the volatile serial-PK identity, the
  two-store localStorage-as-truth curation, the cemetery parcel/marker twin id — stay **tagged to
  gold slice 6 and HELD**. This card does **not** un-hold them or spawn slices for them; it is their
  bounded list (per `gold_migration.md:608-609`).

**Ruling 2 — the `#tag`→coordinate events binding.** Coverage-gap #8: the
`event-anchor-position-from-localStorage-tag-binding` finding is a **real** shadow attribute
(a coordinate-less event anchor positioned from a per-browser `#tag` binding = localStorage-as-truth
driving a published render). But `C3` explicitly scopes `#tag`→coord resolver bindings **out** of the
visitor-list curation axis, and this drives the **events** surface — a *different axis*. **Ruling:**
keep it in the catalog as a true finding, **tag it events-axis / out-of-scope for this card's
resolution slices**; it is re-homed to the event-schedule/overlay convergence (its own work), not a
slice here. This honors the C3 scope boundary rather than smuggling the events axis into the
reference-layer/CMFS card.

## Owed (the user's, not the gate's)
- The brain-only diff (new card + handoff entry) — the commit is the user's git gate (low stakes,
  no code/data).
- At **resolution** (not catalog): the C4 runtime observation the Witness named — a tile-independent
  Playwright/DOM read screenshotting the four trail-name surfaces + the two-browser localStorage
  divergence, and a fresh-volume DB rebuild to confirm the 139–201 serial-PK renumbering.
