# Editor v1 — every curated layer editable, one GeoJSON-copy export

Date: 2026-06-03

TL;DR:
- User: *"we need it all cleaned up and editable. this is mvp. we need v1…
  look for smells and make a ui that a human can use. only export path is
  geojson copy."* (Said right after the buildings rows were found broken —
  see [[viewer_polish_followups]] "Right Panel" 2026-06-03 crush fix.)
- Before v1, only **drawn POIs** (`editorPois`) had the inline accordion
  editor (rename / re-categorize / notes / move / copy / delete). The curated
  served layers (buildings, cemeteries, visitor-context callouts, brand logos)
  could only toggle visibility / star / drag — no rename, notes, or proper
  edit surface. Export was scattered across **two file downloads + two
  settings-clipboard copies + per-feature copy**.
- v1 makes **all** the curated layers fully editable through the same
  accordion, cleans the feature row down to a human-readable
  `[vis] [★] name [edit ▸]`, and collapses every export to **GeoJSON copy
  only**.

#aop #04_event_app #editor #right_panel #mvp #v1 #editable #export

-----

## What shipped (CODE, UNCOMMITTED, v29→v30)

Files: `website/js/main.js`, `website/css/app.css`, `website/index.html`,
`website/sw.js`; verifiers `playwright_verify_feature_list.py`,
`playwright_verify_presets.py`.

### 1. Every curated layer is editable (parity with drawn POIs)
- Set `inlineEditor: true` on `buildings`, `cemeteries`, `visitorContext`,
  `brandLogos`. They now render the same `▸`-chevron accordion editor as
  `editorPois`.
- The accordion is now **layer-agnostic** (`buildInlineEditor`): Name (writes
  the property that layer's `rowLabel` reads — `building_label` for buildings,
  `name` elsewhere), Category (drawn POIs only), Size (brand logos only), Tag
  (taggable layers), Notes (all), Geometry summary; labeled actions **Fly here
  / Move / Lock / Copy GeoJSON**, plus **Duplicate / Delete** for drawn POIs
  only. Served/curated layers get no Delete — they are the on-disk source of
  truth (hide via the visibility tick; truly remove by editing the GeoJSON the
  Copy buttons hand you).

### 2. Persistence for served-layer edits
- Extended the unified `aop_positioned_features_v1` override store: alongside
  geometry/highlight/lock/icon_size it now carries a **`properties`** patch.
  `savePositionedFeature` merges it; `applyPositionedFeatures` replays it onto
  the fetched collection on load. So a renamed building survives reload **and**
  flows into "Copy as GeoJSON" (which reads `feature.properties` live).
- New generic helpers: `setFeatureProperty(layerKey, id, key, value)` (routes
  editorPois → array store, served → positioned override + `refreshServedSource`),
  `FEATURE_NAME_PROP` (per-layer name property), `SERVED_SOURCE` (per-layer
  `[sourceId, data]` for live `setData`). `persistFeatureFlagChange` generalized
  to route *any* non-editorPois layer to the positioned store (previously only
  visitorContext/brandLogos — buildings lock now persists too).
- `cemeteryData` hoisted from a load-scoped `const` to a top-level `let` and
  `applyPositionedFeatures('cemeteries', …)` added so cemetery overrides replay.

### 3. Clean, human-usable row
- Editable (inline-editor) rows collapse to `[vis] [★] name [edit ▸]`. Every
  action and field moved into the accordion (labeled), so the row never crams
  the cryptic `🎯 ✋ 🔒 ⧉` emoji cluster or an 84px `#tag` input against the
  name. (This also fixes the buildings name-crush at the source — the row-level
  tag input is gone, so the earlier `has-tag` two-line CSS hack was removed.)
- Read-only layers (activity hotspots, synthetic activity, event-schedule
  anchors) keep a quick copy + fly on the row (no accordion).
- Long-press anywhere on a movable row still arms move mode (mobile path).

### 4. One export path — GeoJSON copy
Removed: the footer **Export GeoJSON file download**, the panel-header
**Export-all** settings-snapshot (`#exportAll`), the **five per-section "copy
settings" ⧉** buttons (`data-section-export`), and the SFWDA **Export alignment
file download**. Kept / added:
- Per-feature **⧉ Copy GeoJSON** (in the accordion) — a drop-in Feature.
- Footer **Copy all as GeoJSON** (`#exportPoiBtn`, was the download) — the whole
  drawn-POI FeatureCollection to clipboard.
- Drawer **⧉ Copy all** (`#copyLayerBtn`) — the open feature-list layer
  (buildings, cemeteries, …) as a FeatureCollection, edits applied
  (`copyLayerAsGeoJSON`).
- SFWDA **Copy alignment JSON** (was the download) — to clipboard.
The underlying `buildSectionPayload` / `buildExportPayload` functions stay (they
back preset save/apply); only the buttons were removed.

### 5. Smell cleanup (in-scope)
- Removed the dead row-level `#tag` block + `has-tag` CSS, the dead
  `setEditorFeatureName/Category/Notes` helpers, and fixed the stale
  "Trailheads sub-group" comment in `index.html`.

## Decisions (locked unless the owner redirects)
1. **Curated layers edit in place** — buildings/cemeteries stay in the
   "Derived layers" drawer, brand/visitor stay in the editor tree; v1 added the
   editor to each *where it already lives* rather than relocating sections.
2. **No Delete on served/curated features** — they're real-world ground truth;
   hide via visibility, or edit the source GeoJSON. Delete/Duplicate stay
   drawn-POI only.
3. **Single export = clipboard GeoJSON.** No file downloads anywhere.

## Verification (2026-06-03 — by observation)
Served `website/` on :8042. **App, by observation:** buildings layer editor —
clean rows (name 0px→229px readable), accordion shows Name/Tag/Notes/Geometry +
Fly/Move/Lock/Copy GeoJSON; renamed a building → row + override update → the
`building_label` override persisted to `aop_positioned_features_v1` → **survived
reload**; 0 console errors. `playwright_verify_poi_editor.py` PASS.
**Verifiers updated for the new contract** (move/copy now open the accordion;
removed-button assertions flipped to "removed"):

- `playwright_verify_poi_editor.py` — **PASS** (its selectors already targeted
  the accordion, since editorPois always had it).
- `playwright_verify_feature_list.py` — **PASS** after updates: a shared
  `click_editor_action(fid, action)` opens a row's accordion and clicks the
  labeled button (replacing the row `.feature-move`/`.feature-copy` clicks);
  the per-section ⧉ and `#exportAll` assertions flipped to "removed"; the
  per-feature copy test uses the accordion "Copy GeoJSON" action.
- `playwright_verify_buildings.py` — **PASS** (search/visibility based,
  unaffected).
- `playwright_verify_presets.py` — only its **documented pre-existing** fails
  (visitor-context/source-section/Topo assertions + the headless
  click-interception `Locator.click` timeout, all routed in
  [[viewer_polish_followups]]). The `#exportAll` click was swapped for a
  `buildExportPayload()` code-level call, so it no longer crashes there.
- `playwright_verify_event_schedule.py` — the two building-tag assertions were
  mine (the `#tag` input moved to the accordion); updated to open the row
  accordion + read `.editor-tag`, and to verify `#pavilion` binds off-buildings
  via `tagToFeature`. After the fix, **6 fails remain, ALL proven pre-existing**
  by a git-HEAD baseline: the unmodified app+verifier served from
  `git archive HEAD` (port 8043) produced the byte-identical 6-fail list (panel
  chevron, pavilion-fly + hot-now-fly distance-threshold flakiness, trail-lane
  fallback ×3). The transient `publish.geojson` console error did not recur (a
  reload-aborted fetch, not an app bug). **Net: the v1 introduced zero new
  verifier failures.**

## Out of scope (routed, not done)
- **Panel hygiene beyond the editor**: the "Comparisons"/Review section ships
  dev-mockup links to users; the "Layer notes" prose block; the empty
  `#showTrailheads` orphan toggle; the orphaned `activityHotspots` /
  `syntheticActivity` paint specs. These are content/section calls, not editor
  means — route to [[viewer_polish_followups]], confirm with the owner.
- **Dead export plumbing**: `exportSectionToClipboard` / `exportAllToClipboard`
  are now unwired (buttons gone) but left in place; remove once confirmed
  unused by preset save.
- **Dead row CSS**: `.feature-move/.feature-lock/.feature-tag/.feature-size-control`
  rules are no longer produced by any row — safe to delete in a hygiene pass.

## Owed
- On-device read/touch confirm (iPhone): accordion editing, the per-layer Copy
  all, the long-press move.
- Commit + the v30 bump are the user's git gate.
