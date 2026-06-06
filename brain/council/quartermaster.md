# The Quartermaster — reuse & no duplicates

TL;DR: Did this **reuse what already exists**, or quietly build a second one? Check the stores before
you requisition new. One interface, one engine, one paradigm — extend the registry, don't multiply it.
This is the "no duplicates" seat, and it's the disease Sprint 05 was the cure for.

#aop #council #seat #quartermaster #reuse #dedup #dry

-----

> **Owns:** `ai_rules/extract_before_invent.md`, contracts **C1 / C2 / C6**,
> `ai_rules/harness_adapters_are_thin.md`, `ai_rules/editor_is_the_viewer.md` (as no-second-surface).

## Mandate

Default move: extract, do not invent. Before a new term, helper, schema, store, list engine, or HTML
surface gets written, the answer probably already exists in the brain or the codebase. The
`editor_architecture_contracts` exist *specifically* so we "do not get back into the slop" — per-layer
behavior smeared across `layerKey === 'X'` branches, two parallel list engines, a third store. The
Quartermaster holds that line on every diff.

## Review questions (refute the novelty — assume it already exists)

- Did this **re-implement something the brain or codebase already has**? Search `search_map.md`,
  `northstar/`, `practices/`, and the existing helpers first. If a method exists, the new one is slop.
- **C1:** Did the change add a `layerKey === '<key>'` code branch? It must be a spec strategy on
  `FEATURE_LIST_LAYERS` instead. Run the region grep — target 0 (or 1 for the kept `editorPois` guard).
- **C2:** Did it add a **second place that builds destination rows** (a new `pushRow(` block, a parallel
  layer array) instead of extending the one `collectStarredDestinations` collector? Reject — extend the
  collector.
- **C6:** Did it introduce a **class hierarchy, a second top-level registry beside `FEATURE_LIST_LAYERS`,
  or a new `*.html` editor surface**? The codebase is single-paradigm (0 class declarations); keep it.
  The editor is the viewer — no parallel app.
- Did it **fatten a harness adapter** (a skill / hook / command / agent file) with durable prose that
  belongs in the brain? Adapters are thin pointers; content lives in `brain/`.
- Parallel config maps that should be co-located on the spec (the `FEATURE_NAME_PROP` / `SERVED_SOURCE`
  smell Sprint 05 folded onto each spec — R10)?

## When the Quartermaster pulls andon

- A second engine / store / surface / registry was added to do what one already does.
- A new abstraction was invented where extracting an existing one was the move.
- A C1 / C2 / C6 guard regressed (the grep count went up).

## Verdict

`clear` when the change extends what exists and the structural greps hold (C1 branches, C2 single
collector, C6 zero classes / one registry / no new editor HTML). Otherwise `andon` with the duplicate it
introduced and the existing thing it should have extended.
