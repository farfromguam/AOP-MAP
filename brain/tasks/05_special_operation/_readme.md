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

## Sprint 05 status (2026-06-06)

Overnight `special_operation` run complete. **Cards 01–08: DONE + verified by
independent observation (UNCOMMITTED — the commit is the user's git gate).**

- **01** delete dead `buildInlineEditor` — DONE (pre-run).
- **02** spec fields/actions/persist axis; no `layerKey` at call sites — DONE, verified.
- **03** collapse parallel config maps (`FEATURE_NAME_PROP`/`SERVED_SOURCE` onto specs) — DONE, verified.
- **04** dedup hotspot spec twins into `makeHotspotSpec(label, layerPrefix)` — DONE, verified.
- **05** register `trails` as a starrable destination layer — DONE, verified.
- **06** one `collectStarredDestinations()`; both renderers consume it — DONE, verified (structural convergence only).
- **07** panel create-defaults + host-bridge via spec strategies — DONE, verified.
- **08** dedup fly-to button into one `makeFlyButton()` helper — DONE, verified.

**Final structural gate (real output):** C1 region command = **0** non-comment
`layerKey === '...'` branches in main.js; `node -c website/js/main.js` OK;
`node -c website/js/panel.js` OK. **VERSION v51→v52** (`sw.js` + `#appVersion`).

**Deferred (noted, not done this sprint):** the card-06 **"POI tab starts empty"
flip** stays DEFERRED pending the user's decision on `10_deferred/star_driven_poi_list.md`
#1/#2/#4 (engines converged STRUCTURALLY only, behavior preserved — wholesale layers kept
`listMode:'wholesale'`). The out-of-scope **panel-swap cleanup** (`aop_panel_overrides_v1`
second store / third list engine) and the **parallel mini-DB collapse** remain deferred.

#aop #sprint #05_special_operation #editor #refactor #universal #slop
