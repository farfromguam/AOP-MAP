# Council plan review — Sprint 08 star-driven POI normalization (2026-06-08)

> **Type:** plan review. **Tier:** full six (DB migration + publish-zone-adjacent +
> user-visible sprint spine). **Chair:** Steward. **Verdict: FULL CLEAR** after one andon
> round (2 andons folded, 2 precision conditions folded). 1 review round + 1 narrow re-review.

#aop #council #plan #sprint08 #star #poi #normalization #clear

-----

## What was reviewed

`tasks/08_data_normalization/star_driven_poi_normalization.md` — the 3-slice plan to build the
durable ★ path for the four reference layers (buildings/cemeteries/visitor/trails) and then
flip the POI tab to the curated set. Each seat saw the plan + the design source + the live
code/DB, prompted to refute.

## Round 1 — verdicts

| Seat | R1 | Finding |
|------|----|---------|
| **Witness** | andon | Two FACT corrections. (1) Grounding #4 trails row was wrong: `sfwda-<n>` is a **sequential load index**, not the trail number (`sfwda-0`→trail 15, `sfwda-100`→trail 68) — resolution must join editor `trail_number`/`name` → core `attrs->>'trail_number'`/`attrs->>'name'`. (2) The inherited "reference rows can't render headless" claim is false — the runtime DOES seed headless (registrations inside `map.on('load')`); Slice C must assert per-group row counts with a long-enough settle, not the node fallback. Everything else verified true. |
| **Quartermaster** | clear* | Sibling apply script justified (genuinely different inputs). Condition: draw the reuse line — REUSE `split_key`/`round_coords`/`dumps_geom`/`geom_kind` + the `_applied` count==input scaffold; DO NOT reuse `read_payload` (wrong payload shape) or `VIEW_STATE_KEYS` (strips `highlight`, the field the slice carries). Leave `export_positioned_features.py` OWED with the disjoint-axis fact. |
| **Mason** | andon | Two fixes. (1) **Drop the dual-write** — `attrs.highlight` is the single source of truth; the reference bake reads `attrs` verbatim and reads the `is_destination` column *nowhere* for these four layers, so a column write has no consumer and drifts. (2) Tighten Slice C to verify-first ("verify the existing render fires; add a field only if observation shows a gap"), not "render the fields" (C2 re-derive risk). Confirmed the design fork (DB-lookup sink) and the whole-design C5 stance. |
| **Warden** | clear* | Scope on-farm; decision #3 (brand logos off the ★ axis) structurally guaranteed; legacy-writer OWED correct; git gate untouched; sprint placement honest (scoped slice of HELD gold slice 6, user green-lit). Conditions: name the visitor join column (`attrs->>'name'`, since `source_key` is the `-N` index); disambiguate the `FEATURE_LIST_LAYERS` block (2266/2321) from the same-named `LAYER_CONFIGS` block (~2094/2115); name the owed bump `v53`→`v54`. |
| **Scribe** | clear | Brain consistent across the plan card, the sprint `_readme`, the deferred design card + pointer, the two `_readme`s, and the handoff — no file contradicts "ready." Voice plain. References treated as artifacts, not analogies. Gold-slice-6 relationship stated precisely. |

\* Quartermaster/Warden cleared with conditions (folded); the blocking andons were Witness + Mason.

## Fixes folded into the plan

1. Grounding #4 trails row → join on `attrs->>'trail_number'`/`attrs->>'name'`; noted the
   ~33 numberless + ~20 nameless unresolvable edges. (Witness)
2. Grounding #4 visitor row → match on `attrs->>'name'` (fall back `label`); `-N` is a
   synthetic index. (Witness/Warden)
3. Slice A → `attrs.highlight` is the single source of truth; **is_destination column write
   removed**; un-star clears it symmetrically. (Mason)
4. Slice A → explicit reuse line (REUSE the four helpers + `_applied` scaffold; DO NOT reuse
   `read_payload`/`VIEW_STATE_KEYS`). (Quartermaster)
5. Slice A → `highlightable` add targets the `FEATURE_LIST_LAYERS` specs (2266/2321), not the
   `LAYER_CONFIGS` block. (Warden)
6. Slice B → OWED note carries the disjoint-axis fact (legacy bakes geometry only; shared
   clobber vector is geometry, not the star). (Quartermaster)
7. Slice C → verify-first wording; per-group row-count acceptance; corrected the headless
   claim; verifier hooks `window.AOP_HOST_MAP` + waits on the load event; bump named `v53`→`v54`.
   (Mason/Witness/Warden)
8. Design fork marked RESOLVED (DB-lookup sink, Mason + Quartermaster).

## Re-review — verdicts

Witness · Mason · Quartermaster · Warden re-reviewed the edited plan over the live system.
**All four `clear`.** Witness re-verified the trail-index fact and observed the reference
runtime seeding headless live (`window.AOP_HOST_MAP`, `load_fired=true`, reference groups
populated). Mason confirmed the dual-write is gone and Slice C is verify-first. Quartermaster
confirmed the reuse line is precise (one non-blocking phrasing nit on "hard-gated," since
folded). Warden confirmed all three reminders and the untouched git gate.

## Steward — FULL CLEAR

The plan is council-approved. It carries everything a ralph-loop needs: per-slice
tile-independent observable acceptance, the loop contract, the standing conditions (Witness
re-witness + `AOP_HOST_MAP` hook; Mason count==input + highlightable-with-the-flip), and the
resolved design fork. No open andon.

**Next (the user's gates):** commit-pause (commit the Sprint-08 plan), then ralph-loop the
slices in a fresh session. The commit and the `v53`→`v54` bump stay the user's git gate.

Touched only `brain/` this turn — no `website/`/`mvp/`, so the Tier-0 Stop-hook did not
self-fire and no clearance marker is owed (the marker is for code-diff done-reviews).
