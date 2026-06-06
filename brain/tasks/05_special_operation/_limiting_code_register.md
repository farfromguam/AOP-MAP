# Sprint 05 — limiting / special / dead code register

Every limiting, special-case, dead, or parallel-scaffolding item the seal-team
audit found (2026-06-06), each with a verdict and an action. "Needed" items stay;
everything else routes to a card or is explicitly deferred. Per
`brain/ai_rules/no_limiting_code_mvp.md`, the refactor adds **dispatch, never
rejection** — no validators/caps introduced while cleaning up (contract C5).

- **[parallel scaffolding / the primary duplication; THE disease the card names]** buildPoiGroups — second hand-rolled list engine, 7 bespoke source blocks; only drawn_pois star-gated (buildings/cemeteries/visitor_support dump wholesale, trails one row per trail)
  - where: `website/js/main.js:1120-1340 (gate only at 1308)`
  - action: Collapse into one collectStarredDestinations() walking the registry filtered to highlight===true; renderPoiTab + renderVisitorListGroup consume it (card 06).
- **[parallel hardcoded list; covers a different layer set than the left tab]** VISITOR_LIST_LAYERS — hardcoded ['editorPois','brandLogos','visitorContext'] that the right ★ list walks instead of the registry's destination layers
  - where: `website/js/main.js:572 (read at 1031)`
  - action: Replace with a destination/highlightable flag on the registry specs; the one collector walks Object.entries(featureListRuntime) (card 06).
- **[special-case hack — subclass-by-conditional]** editorPois Category-select branch (live, buildEditDock Identify tab)
  - where: `website/js/main.js:4168-4178`
  - action: Migrate to spec.fields (card 02).
- **[special-case hack — subclass-by-conditional]** buildings Status readonly branch (live, buildEditDock)
  - where: `website/js/main.js:4180-4183`
  - action: Migrate to spec.fields readonly (card 02).
- **[special-case hack — editorPois-hardcoded helpers]** editorPois Duplicate/Delete actions branch (live, buildEditDock)
  - where: `website/js/main.js:4215-4220 (helpers 4511-4541)`
  - action: Migrate to spec.actions + generic deleteFeature/duplicateFeature routed through the persist seam (card 02).
- **[parallel un-migrated copy of an already-solved fork]** setFeatureProperty array-vs-override fork (the SAME fork stage-1 removed for the flag path, never migrated for the property path)
  - where: `website/js/main.js:4578-4591 (fork at 4583)`
  - action: Migrate to spec.persistProperty dispatch (card 02).
- **[special-case hack]** dockGroupContext editorPois geometry-bucket fork
  - where: `website/js/main.js:4095-4103 (branch at 4096)`
  - action: Migrate to spec.groupContext(item) with default spec.label (card 02).
- **[dead code (interleaved with live siblings; superseded by buildEditDock per the 4011/4275 comments)]** buildInlineEditor — dead function, no callers; carries two more editorPois branches (Category 4328, Duplicate/Delete 4427)
  - where: `website/js/main.js:4278-4441`
  - action: Delete the whole function FIRST (card 01) — do not migrate its branches; removes 2 branches by deletion.
- **[dead-on-deletion]** makeEditorLabel — helper called only from inside buildInlineEditor
  - where: `website/js/main.js:4442 (callers 4316/4329/4347/4368/4383/4395)`
  - action: Delete alongside buildInlineEditor (card 01).
- **[parallel registry / config duplication]** FEATURE_NAME_PROP — parallel per-layer name-property map beside the registry
  - where: `website/js/main.js:4547-4553 (read 4109/4284)`
  - action: Fold onto spec.nameField; delete the map (card 03).
- **[parallel registry / config duplication]** SERVED_SOURCE — third parallel per-layer config map (srcId+data per layerKey) read by refreshServedSource
  - where: `website/js/main.js:4558-4563 (read 4565-4573)`
  - action: Fold onto spec.servedSource; refreshServedSource reads the spec; delete the map (card 03).
- **[config that belongs on the spec field]** EDITOR_POI_CATEGORIES — editorPois-only category option list referenced only by the category branches
  - where: `website/js/main.js:4488-4497 (read 4170, 4332-dead)`
  - action: Co-locate as the editorPois category field's options source (cards 02/03).
- **[near-identical copy-paste spec blocks]** activityHotspots / syntheticActivity specs — byte-identical twins (rowLabel/rowSort/groups), differ only in label + targetLayers
  - where: `website/js/main.js:2465-2492 and 2495-2522`
  - action: Factor makeHotspotSpec(label, prefix); two factory calls (card 04).
- **[missing registration that causes a special case]** trails NOT registered as a feature-LIST layer (only TUNABLE_LAYERS paint entry at 2090) — forces the wholesale-dump special case and makes trails un-starrable
  - where: `website/js/main.js:2090 (paint only); no registerFeatureListLayer('trails')`
  - action: Register trails as a destination FEATURE_LIST_LAYERS layer (card 05).
- **[repeated DOM row builders]** Four hand-built fly-to button row builders (renderVisitorListGroup, renderPoiTab, renderFeatureListInto, buildEditDock)
  - where: `website/js/main.js:1064-1085, 1373-1415, 3891-3922, 4126-4128`
  - action: Extract makeFlyButton(feature, className) (card 08).
- **[special-case hack in a generic create path]** panel.js cemeteries create-defaults branch (geom_role stamp in canonicalDefaults)
  - where: `website/js/panel.js:1234 (canonicalDefaults 1222-1236)`
  - action: Replace with node.createDefaults(geomType) hook (card 07).
- **[parallel identity map that drifts on rename]** panel.js HOST_HIGHLIGHT_LAYER — identity map whose keys equal values, whitelisting star/tag host bridge
  - where: `website/js/panel.js:814 (read 817/830)`
  - action: Replace with node.hostKey field; hostHighlight/pushTagToHost read it (card 07).
- **[BENIGN self-exclusion in a one-shot seeder — NOT a dispatch site]** seed tag-conflict loop guard `if (layerKey === 'editorPois') continue;`
  - where: `website/js/main.js:7131-7138`
  - action: Optional: rename to a SELF constant so the literal is dropped; otherwise leave and document as intentionally-not-a-strategy, excluded from the branch count (card 02).
- **[comments, not code — inflate a naive grep -c to 9]** Comment lines referencing the old `layerKey === 'editorPois'` pattern (history of the migration)
  - where: `website/js/main.js:2334, 3296`
  - action: No action required; scope all branch-count greps to functions, not whole-file, so these are not counted (C1 enforcement note).
- **[near-miss under no_limiting_code_mvp — accepted UX: search-dropdown cap, deliberately widened to 12 for trail-number queries so trail '1X' is not dropped; NOT a POI/star/map cap]** renderSearchResults `.slice(0, limit)` (limit 8 or 12) on the typeahead dropdown
  - where: `website/js/main.js:~9879`
  - action: Keep; disposition explicitly as accepted-UX (do not promote to a feature-collection limiter). No code change.
- **[NOT a count cap — a zoom-scaling size multiplier (0.4–2.5x); brand logos off the star/destination axis]** BRAND_LOGO_CAP_* constants
  - where: `website/js/main.js:~2750-2755`
  - action: No action. Negative finding.
- **[parallel scaffolding / split-brain star persistence — the in-flight cost of the right_panel_rebuild swap]** Third list engine + second store from the panel swap (panel.js PANEL_MODEL/deriveItems/renderLeftPanel + aop_panel_overrides_v1 with highlight in EDITABLE_SERVED_KEYS, running concurrently with main.js in index.html)
  - where: `website/index.html:542/548; website/js/panel.js:79/84/814/834/1710`
  - action: OUT OF SPRINT-5 SCOPE — the swap-cleanup the rebuild card owes; record disposition on right_panel_rebuild.md and decide A) finish the swap (retire main.js list engines, panel as sole surface) or B) route all panel stars through AOP_HOST_SET_HIGHLIGHT. Do NOT leave both stores writing highlight. Flag here so it is not silently absorbed into the universal-layer work.
- **[collapse-targets gated on the open author->DB + bake-shape forks (star_driven_poi_list.md is explicit: no code until the forks are picked); SERVE half already shipped (publish.geojson core.pois)]** Parallel mini-DBs (aop_poi_index.json, aop_editor_seed_pois.geojson, aop_editor_pois_v1, aop_positioned_features_v1, aop_panel_overrides_v1)
  - where: `website/data/aop_poi_index.json; website/data/aop_editor_seed_pois.geojson; website/js/main.js:34/43/1096/7104; website/js/panel.js:79`
  - action: DEFERRED — do not collapse/reconcile yet. Note that the SERVE bake reaches the left tab as published_destinations while the legacy blocks persist; collapse when the user picks the author->DB fork. Per no_limiting_code_mvp add no validators while collapsing.

#aop #05_special_operation #register #slop #limiting_code
