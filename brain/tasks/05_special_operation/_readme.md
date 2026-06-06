# Sprint 05 — special_operation

> Opened 2026-06-06 by user mandate after a slop review: "the pattern extends
> universally... there should not be 7 of anything... one code path universal."

## Mission

Finish making **every layer just a feature layer behind one interface.** Sprint 04
shipped stage 1 of `universal_feature_layer.md` (`onMutate`/`persistFlag` spec hooks —
do NOT re-open). This sprint executes the rest: kill the remaining `layerKey === 'X'`
smear, collapse the **two list engines** into one star-driven collector, register
**trails** as a starrable destination layer, trim the dead/parallel scaffolding, and
apply the high-severity dedup — **no big-bang** on a 10k-line file we cannot fully
render headless.

## Contracts & requirements

The durable contracts (C1–C6) and codifiable requirements (R1–R14) live in
`brain/northstar/editor_architecture_contracts.md`. Every card carries a
**tile-independent** observable acceptance test (grep / `node -c` / DOM-level
Playwright via `mvp/scripts/playwright_base.py`).

## Card order (sequential — nearly all touch `js/main.js`, so no parallel collisions)

1. `01_delete_dead_inline_editor.md` — Delete the dead buildInlineEditor function (main.
2. `02_spec_fields_actions_persist_axis.md` — Push the live buildEditDock per-layer behavior into FEATURE_LIST_LAYERS spec strategies so the dock, setFeatureProperty, and dockGroupContext dispatch through the spec and name no layerKey.
3. `03_collapse_parallel_config_maps.md` — Remove the standalone per-layer lookup tables that live next to FEATURE_LIST_LAYERS and fold their data onto each spec, so the registry is the single config home.
4. `04_dedup_hotspot_spec_twins.md` — Collapse the two near-identical FEATURE_LIST_LAYERS specs (activityHotspots 2465-2492, syntheticActivity 2495-2522) — which differ only in label and targetLayers — into a makeHotspotSpec(label, layerPrefix) factory, removing ~24 lines of copy-paste and the duplicated rowLabel/rowSort.
5. `05_register_trails_as_destination_layer.md` — Add a `trails` (aop-trail-network) entry to FEATURE_LIST_LAYERS with highlightable:true and a registerFeatureListLayer('trails', aopTrailNetworkCache) call at load, plus the dedup-per-trail/catalog-lookup logic expressed as spec strategies.
6. `06_one_star_driven_collector.md` — Replace buildPoiGroups' 7 bespoke source blocks with a single collectStarredDestinations() that walks FEATURE_LIST_LAYERS destination layers from featureListRuntime, applies the `highlight === true` gate ONCE, and returns uniform rows via a spec.
7. `07_panel_create_defaults_and_host_bridge.md` — Remove the two per-layer special cases in panel.
8. `08_dedup_fly_button_row_builder.md` — Centralize the 'fly-to button' DOM gesture duplicated across renderVisitorListGroup (1064-1085), renderPoiTab (1373-1415), renderFeatureListInto (3891-3922), and buildEditDock (4126-4128) into one makeFlyButton(feature, className) helper.

## Out of scope, but tracked

- The **panel-swap cleanup** (panel.js introduced a third list engine + a second
  highlight store, `aop_panel_overrides_v1`, running concurrently with main.js).
  Owned by `_done/right_panel_rebuild.md`; see `_limiting_code_register.md`.
- The **parallel mini-DB collapse** (poi_index / seed / localStorage stores → one DB
  column + bake) stays **deferred** in `10_deferred/star_driven_poi_list.md` pending
  the author→DB fork. Do not reconcile those files in this sprint.

#aop #sprint #05_special_operation #editor #refactor #universal #slop
