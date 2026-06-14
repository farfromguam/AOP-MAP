# Universal feature-layer interface — kill the `layerKey === 'X'` smear

> **✅ DONE — staged migration complete (2026-06-06; recorded 2026-06-14).** This is
> the **founding/spine card** for Sprint 05 (`special_operation`). Its three staged
> goals all shipped via the eight executable sub-cards now in `_done/`
> (`01_delete_dead_inline_editor` … `08_dedup_fly_button_row_builder`), each
> validated by observation and council-reviewed (see `_readme.md` "Sprint 05 status").
> Stage 1 landed here directly; stages 2–3 are carried by sub-cards 01–08.
> **Kept at root (not moved to `_done/`)** to preserve its inbound links — the eight
> sub-cards, `_readme.md`, `04_edit/_readme.md`, and `northstar/editor_architecture_contracts.md`
> all reference it by path; this banner + the per-stage DONE markers are the acceptance
> record (same convention as Sprint 08's spine card). **Owed (user's git gate):** the
> commit + the v52 bump (the sprint's standing owed item — `../../ai_rules/no_commits.md`).
>
> Root-cause work behind the user's "this is slop / not universal / there should not
> be 7 of anything" review. The ★→POI desync (`_done/editor_unified_tree.md`
> follow-up) was one symptom; this card is the disease.

TL;DR:
- The codebase has a **per-layer registry** (`FEATURE_LIST_LAYERS` +
  `featureListRuntime`) that the right-rail editor renders through uniformly —
  the good bones. But layer-specific *behavior* leaked OUT of the registry into
  scattered `if (layerKey === 'editorPois')` (and one `=== 'buildings'`)
  branches, ~11 of them across `website/js/main.js`. `editorPois` is effectively
  a subclass implemented by sprinkling conditionals.
- A **second, hand-rolled list engine** (`buildPoiGroups`, 7 bespoke source
  blocks) sits next to the registry to build the left POI tab — so "list
  features" exists twice, and ★ curation only got wired into 1 of the 7 blocks.
- **Target contract:** every layer is *just a feature layer* behind one
  interface. Per-layer behavior (post-mutation refresh, flag persistence,
  property persistence, list eligibility, row label, geometry move) is declared
  **once in the spec** as strategy functions. Call sites dispatch through the
  spec and **never name a layerKey**. The left POI tab and the right ★ Visitor
  list become **two renderers over one collector** that walks the registry
  filtered to starred (`highlight === true`), uniformly, trails included.

#aop #04_event_app #editor #refactor #universal #slop #poi #star

-----

## Why registry-strategy, not ES classes

Considered a `FeatureLayer` class hierarchy. Rejected for now: the file is one
vanilla-JS IIFE built around a config-object registry; adding a class paradigm
alongside it is a *second* way of doing the same thing — more slop, not less.
Extending the existing spec with strategy functions is the minimal-surprise
universal pattern and keeps one paradigm. Revisit classes only if we later
extract modules with a build step (deferred — not an MVP detour).

## The evidence (slop sites, `website/js/main.js`)

- Mutation-refresh axis: `if (layerKey === 'editorPois') refreshEditorSource();
  else renderFeatureList(layerKey)` — duplicated 3× (toggleFeatureHighlight,
  setFeatureHighlight, toggleFeatureLocked).
- Flag-persist fork: `persistFeatureFlagChange` branched editorPois (array
  store) vs everything else (positioned-overrides).
- Property/action axis: dock editor + edits branch editorPois (category field,
  duplicate, delete, property persistence) and buildings (status field).
- Two list engines: `buildPoiGroups` (7 hand-written source blocks, left tab)
  vs `FEATURE_LIST_LAYERS`/`featureListRuntime` (right editor). Only the
  `drawn_pois` block is star-gated; trails dump in wholesale (~100 rows).

## Staged migration (each stage verified before the next — no big-bang)

A big-bang rewrite of a 10k-line file we can't fully run headless (external
basemap tiles unreachable → MapLibre `load` never fires in the sandbox) IS the
slop risk. So: small, dispatch-preserving steps, DOM-verified.

1. **DONE 2026-06-06 — mutation-refresh + flag-persist axis.** Added `onMutate`
   + `persistFlag` strategy hooks to the editorPois spec; new
   `refreshAfterFeatureChange(layerKey)` dispatches via `spec.onMutate` (default
   `renderFeatureList`); `persistFeatureFlagChange` dispatches via
   `spec.persistFlag` (default `savePositionedFeature`). Removed 4 `layerKey ===
   'editorPois'` branches. Verified: `editorPois` ★ toggle still propagates to
   both the left tab and the right ★ list in sync, zero console errors, file
   parses clean (`node -c`).
2. **DONE — property/action axis.** Shipped via `_done/02_spec_fields_actions_persist_axis.md`
   (+ the dead `buildInlineEditor` deleted by `_done/01_delete_dead_inline_editor.md`
   and the parallel config maps folded by `_done/03_collapse_parallel_config_maps.md`):
   category-field, duplicate, delete, property-persist, and the buildings status field
   moved into spec strategies (`fields`, `actions`, `persistProperty`); the per-layer
   branches cleared. Validated 2026-06-06 (C1 region = 0 `layerKey === '…'` branches).
3. **DONE — collapse the two list engines.** Shipped via
   `_done/06_one_star_driven_collector.md` (+ `_done/05_register_trails_as_destination_layer.md`,
   `_done/04_dedup_hotspot_spec_twins.md`, `_done/07_panel_create_defaults_and_host_bridge.md`,
   `_done/08_dedup_fly_button_row_builder.md`): one `collectStarredDestinations()` walks the
   registry's destination layers filtered to `highlight === true`; trails registered as a
   destination layer; brand logos off the ★ axis. The POI-tab "starts empty / star-only"
   flip was carried later by Sprint 08 (`../08_data_normalization/star_driven_poi_normalization.md`)
   per `star_driven_poi_list.md` decisions #1/#2/#4.

## Related

- `../10_deferred/star_driven_poi_list.md` — the product design this executes
  (★ governs all destination layers; POI tab = the starred set; one pipeline).
- `_done/editor_unified_tree.md` — the ★ Visitor list / left-tab desync fix
  (2026-06-06 follow-up) was the first symptom of this disease.
