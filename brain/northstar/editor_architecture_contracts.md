# Editor architecture contracts — the universal feature-layer model

> Locked 2026-06-06 (Sprint 05 special_operation). These exist so we **do not get
> back into the slop**: per-layer behavior smeared across `layerKey === 'X'`
> branches, two parallel list engines, curation living in browser localStorage.
> They are durable northstar contracts — they bind every agent on every turn that
> touches the editor.

#aop #northstar #editor #contracts #universal #slop

-----

## Contracts

### C1 — One feature interface; behavior lives in the spec, never at the call site

**Every layer is just a feature layer behind the one registry interface (FEATURE_LIST_LAYERS at main.js:2240). Any per-layer behavior — mutation refresh, flag persistence, property persistence, list eligibility, row label, fields, actions, geometry move, create defaults, host bridge — is declared once as a spec strategy, and call sites dispatch through the spec and NEVER name a literal layerKey.**

- *Why:* editorPois is a de-facto subclass implemented by sprinkling conditionals. Stage-1 (onMutate/persistFlag at 3300/3389) proved the strategy pattern works; the remaining branches (4096/4168/4180/4215/4583 + the dead 4328/4427 + the 7132 guard, plus panel.js 1234/814) are the same disease, not yet treated.
- *Enforce:* Region-scoped grep guard (NOT a naive whole-file count — 2334/3296 are comments): assert zero `layerKey === '<key>'` code branches in buildEditDock, setFeatureProperty, dockGroupContext, and panel.js canonicalDefaults/host-bridge. Review checklist: 'Did this change add an `=== '<layerKey>'` comparison? It must instead be a spec strategy.'

### C2 — One list engine: two renderers over one collector

**Exactly one function decides what is a destination row and what its row shape is. The left POI tab (renderPoiTab, grouped) and the right ★ Visitor list (renderVisitorListGroup, flat) are both thin renderers over that one collector (collectStarredDestinations) — neither re-derives rows, and the `highlight === true` gate is applied once in the collector.**

- *Why:* 'List features' currently exists twice: buildPoiGroups (1120) hand-writes 7 bespoke source blocks parallel to the registry, and only drawn_pois is star-gated while other layers dump wholesale; renderVisitorListGroup (1024) walks a separate hardcoded VISITOR_LIST_LAYERS (572). Two engines = curation drift by construction, and the two cover different layer sets — the desync the card names the disease.
- *Enforce:* Structural: exactly one `collectStarredDestinations(`; zero `pushRow('` source blocks; both renderers reference the collector; the collector walks Object.entries(featureListRuntime)/FEATURE_LIST_LAYERS, not a hardcoded layer array. Row-parity fixture test guards behavior. Review checklist: 'Does this add a second place that builds destination rows? Reject — extend the collector.'

### C3 — Curation is data, not browser state

**The ★ (is_destination), blurb, status, and any curation decision are attributes on the feature row that travel from the store of record into the baked publish artifact; they are NEVER sourced from per-browser localStorage as the source of truth for the published list. localStorage may be a working buffer only. (#tag→coordinate resolver bindings are a separate axis from visitor-list curation and are out of this contract's scope.)**

- *Why:* star_driven_poi_list.md decision #5 locks this so the published POI list is stable across browsers and auditable. Today curation is smeared across aop_*_v1 stores plus in-place feature.properties.highlight, and the panel swap added a second store (aop_panel_overrides_v1) — two browsers can disagree on what the POI list is.
- *Enforce:* The destination collector (C2) must not key the published set off any aop_*_v1 store; published_destinations rows read publishDataCache (layer==='poi'). Review gate: 'Is this curation value read from localStorage as truth? Reject — it is a feature attribute, baked.' Per no_limiting_code_mvp this is a sourcing contract, not a value validator: surface integrity gaps as card notes, never add row-dropping filters.

### C4 — Every work card carries a tile-independent observable acceptance test

**No layer/list/curation card is closeable without an acceptance test checked by observing the real system — a grep/structural assertion, node -c, or a DOM-level Playwright check that does NOT depend on rendered map tiles (external basemap tiles are blocked headless, so MapLibre 'load' never fires).**

- *Why:* verify_by_observation.md — a 'verified' claim was once re-derived math. CORRECTION to the audit draft: a tracked, DOM-capable test harness DOES exist (`mvp/scripts/playwright_base.py` + `playwright_verify_*.py`, 73 tracked files); what's missing is a CI auto-runner, so observable acceptance is enforced by running that harness in the loop, not by CI.
- *Enforce:* Each card stage carries a tile-independent 'Observable acceptance' line. DOM tests are written against `mvp/scripts/playwright_base.py` (no `networkidle`, no `queryRenderedFeatures`); structural checks use `node -c` + region-scoped greps.

### C5 — No limiting code in MVP: the model adds dispatch, never rejection

**The feature-interface refactor and the star/list collapse stay fully permissive — no CHECK constraints, enum locks, strict validators, or row-dropping filters introduced as a side effect of cleaning up. Spec strategy dispatch uses safe defaults and never throws on a missing strategy; an out-of-vocabulary value still renders.**

- *Why:* no_limiting_code_mvp.md is explicit and user-confirmed ('everything to display for now'). Pushing behavior into spec strategies tempts a 'while I'm here, validate category/status against an allowlist' move that would silently drop features. The publish gate's exact-string equality is an ACCEPTED failure mode, logged as a note, not fixed with a validator.
- *Enforce:* Refactor-diff grep: no new CHECK/enum-reject/throw on unexpected layer/category/status values; defaults FALL BACK (mirror refreshAfterFeatureChange's default at 3302) rather than reject. Review checklist: 'Did this add a constraint/validator/filter that can hide a row? Make it a documented card note instead.' Re-confirm with the user before treating any new gate as permanent.

### C6 — One paradigm: extend the registry, do not add a class hierarchy or a parallel surface beside it

**Universality is achieved by extending the existing config-object registry with strategy functions — NOT by introducing an ES class hierarchy, a second top-level registry object beside FEATURE_LIST_LAYERS, or a second editor HTML/app surface alongside the one vanilla-JS IIFE. The editor is the viewer.**

- *Why:* universal_feature_layer.md explicitly rejected classes for now ('a second way of doing the same thing — more slop'). The codebase is single-paradigm today (0 class declarations). The panel swap already introduced a third list engine + second store concurrently; the contract is to converge, not multiply.
- *Enforce:* grep guard: 0 `class [A-Z]` declarations in main.js, and no NEW top-level registry object beside FEATURE_LIST_LAYERS, and no new *.html under website/ that loads its own editor bundle (editor_is_the_viewer). Review checklist: 'Does this introduce a class hierarchy, a second registry, or a parallel editor file to do what the spec registry already does? Reject — extend FEATURE_LIST_LAYERS.'


## C1 enforcement command (mechanical, region-aware)

```sh
# C1 guard — non-comment `layerKey === '...'` branches (whole-file grep over-counts because of history comments at 2334/3296):
python3 -c "[print(i+1, l.strip()) for i,l in enumerate(open('website/js/main.js')) if \"layerKey === '\" in l and not l.strip().startswith('//')]"
# Target after Sprint 05: 0 (or 1 if the 7132 self-guard is kept).
```

## Codifiable requirements — the universal feature-layer interface (R1–R14)

Every layer is a `FEATURE_LIST_LAYERS` spec; behavior is a strategy on the spec;
call sites dispatch and name no layerKey. Defaults are safe and never throw.

- **R1** R1 identity: every FEATURE_LIST_LAYERS spec declares idField, rowLabel(props), and label.
- **R2** R2 mutation: per-layer post-mutation refresh is spec.onMutate() with default renderFeatureList(layerKey) — SHIPPED stage-1 (main.js:3300).
- **R3** R3 flag persistence: spec.persistFlag(feature,patch) with default savePositionedFeature — SHIPPED stage-1 (main.js:3389).
- **R4** R4 property persistence: spec.persistProperty(feature,key,value) (editorPois => saveEditorPois+refreshEditorSource; default => savePositionedFeature+refreshServedSource) REPLACES the setFeatureProperty fork at main.js:4583.
- **R5** R5 fields: a declarative spec.fields list (editorPois Category select sourced from EDITOR_POI_CATEGORIES; buildings Status readonly) REPLACES the branches at 4168/4180 (and removes the dead 4328 by deleting buildInlineEditor).
- **R6** R6 actions: a declarative spec.actions/capability (duplicate/delete opt-in, served layers omit) REPLACES the branch at 4215 (and removes the dead 4427 by deleting buildInlineEditor); deleteFeature/duplicateFeature are generic and spec-routed.
- **R7** R7 list eligibility: a spec.destination/highlightable flag plus a spec.listRow strategy lets the ONE collector (collectStarredDestinations) know which layers and rows surface to the POI tab and ★ list, filtering highlight===true once.
- **R8** R8 grouping: spec.groups[] with match(props,feature) plus a spec.groupContext(item) (editorPois geometry-bucket; default spec.label) REPLACES the dockGroupContext branch at main.js:4096.
- **R9** R9 geometry move: spec.onMove(feature,lngLat) (already present on buildings/editorPois) — call sites gate on typeof spec.onMove === 'function', naming no layer.
- **R10** R10 config co-location: editable name property is spec.nameField (default 'name', replaces FEATURE_NAME_PROP); served refresh source is spec.servedSource (replaces SERVED_SOURCE); category options live on the editorPois field (EDITOR_POI_CATEGORIES co-located, not a free-standing map).
- **R11** R11 trails register as a destination layer (FEATURE_LIST_LAYERS trails + registerFeatureListLayer('trails', aopTrailNetworkCache)) so they are starrable uniformly; brand logos are explicitly NOT destinations (their own size/move drawer; star_driven decision #3).
- **R12** R12 panel parity: node specs declare createDefaults(geomType) (cemeteries returns geom_role='marker' for Point, replacing panel.js:1234) and hostKey (replacing the HOST_HIGHLIGHT_LAYER identity map at panel.js:814).
- **R13** R13 fallback discipline: every spec strategy has a safe default and never throws on absence (mirror the if-typeof-function-else-default pattern); an unrecognized layer/value still renders (C5).
- **R14** R14 single collector vocabulary: there is one destination-row shape; renderPoiTab (grouped) and renderVisitorListGroup (flat) consume the same rows; the activityHotspots/syntheticActivity twins share one makeHotspotSpec factory; the fly-to button is one makeFlyButton helper.

## Related

- `../tasks/05_special_operation/_readme.md` — the sprint executing these.
- `../tasks/05_special_operation/universal_feature_layer.md` — the root-cause refactor + stages.
- `../tasks/10_deferred/star_driven_poi_list.md` — the product design (one pipeline; star governs all destinations).
- `../ai_rules/no_limiting_code_mvp.md`, `../ai_rules/editor_is_the_viewer.md`, `../ai_rules/verify_by_observation.md`.
