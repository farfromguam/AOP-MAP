# Right panel — clean rebuild (one model, one renderer)

Date: 2026-06-04

TL;DR:
- User: *"review the right panel… the items got thrown in without much effort to
  organization. what I want is a singular Massive json object that powers the
  right panel. and a singular item/tree/editor renderer. right now… it is NOT
  that. its a bunch of hard coded, different implementations. come up with a NEW
  — completely new view, one specific for the right editor, and put the features
  back as I directed one at a time. simple clean. KISS. no extra features. no
  random edgecase support."*
- Approach (user-chosen 2026-06-04): **build it isolated & fresh, then swap.**
  New `website/right_panel.html` + `website/js/panel.js`, driven by ONE
  `PANEL_MODEL` object through ONE renderer. Prove it one feature at a time;
  swap into `index.html` once it earns it. Reversible; live app keeps working.
- First feature (user-chosen): **layer visibility toggle.** SHIPPED + verified.

- **2026-06-05 STAGE-2 FINISH PASS — store reconciliation + ★→POI bridge + SFWDA
  toggle (CODE ONLY, UNCOMMITTED, v33→v34).** User, after weighing whether the
  editor is worth maintaining, chose **finish the full editor**; for the POI
  surface chose **option 1: wire ★ → the existing host POI tab, keep current
  directory behavior** (not the deferred "starts-empty/starred-only" collapse).
  Mapped `main.js` with 2 Explore agents + observation, then shipped three
  finishes, each verified headless (served :8077, SW blocked, 0 real console
  errors):
  **(1) STORE RECONCILIATION (the real data-loss bug) — `panel.js`.** In embed
  mode the panel backed its lists with its OWN fetch, so any `setData(LOADED[src])`
  REPLACED a host-shared source and WIPED the host's persisted overrides
  (`aop_positioned_features_v1` drag/highlight/lock/size on buildings·cemeteries·
  visitor-context·brand-logos; every drawn POI in `aop_editor_pois_v1` →
  editor-poi). Fix: `seedLoadedFromHost()` — for each host-shared *editable*
  source the panel now seeds `LOADED[src]` from the host's CURRENT source data
  (`getSource(id).serialize().data` / `_data`), so every existing setData path
  (boot replay :210, delete, move, create) round-trips host overrides losslessly.
  `whenHostReady` now also waits for the LAST-added shared sources (`editor-poi`,
  `brand-logos`) so the seed reads complete host data. Verifier
  `/tmp/verify_phase1_stores.py` **9/9**: seeded both host store types, proved
  `LOADED` mirrors them, and proved a real panel create (editor-poi) + a real
  panel delete (fema-buildings) PRESERVE the seeded host data (pre-fix both wiped).
  **(2) ★ → EXISTING POI TAB (option 1) — `main.js` + `panel.js`.** `main.js` gains
  ONE additive bridge `window.AOP_HOST_SET_HIGHLIGHT(layerKey, props, on)` =
  `setFeatureHighlight` (sibling of `toggleFeatureHighlight`): derives the id via
  the host's own `positionedFeatureIdFor`, sets `highlight`, persists through the
  host store (`persistFeatureFlagChange`), and refreshes the POI tab
  (`renderPoiTabIfActive`). `panel.js` `toggleItemStar` routes through it in embed
  mode via `HOST_HIGHLIGHT_LAYER = {buildings,cemeteries,visitorContext,editorPois}`
  (trails have NO host feature-list runtime; brand logos are off the ★ axis per
  `star_driven_poi_list.md` #3; user features stay panel-side). The visible win:
  the host POI tab gates **drawn POIs** on `highlight` (`main.js:1308`), so a panel
  ★ on a drawn POI now surfaces it in the existing left-rail POI tab and persists
  (survives reload). Verifier `/tmp/verify_phase2_poi.py` **9/9**: seeded an
  un-starred drawn POI (absent from the tab) → panel ★ → appears in `#poiList` +
  `highlight=true` in `aop_editor_pois_v1` (host store) → un-star → leaves again.
  **Note (deferred, by user choice):** the host POI tab still lists facilities/
  trails/cemeteries/events/visitor-support UNCONDITIONALLY — the locked
  `star_driven_poi_list.md` design (★ = the one gate, tab = the starred set,
  starts empty) is the bigger "collapse the scaffolding" work, still gated on its
  author→DB / bake forks. Option 1 deliberately keeps current behavior.
  **(3) SFWDA PAPER TOGGLE wired in embed mode — `panel.js`.** The host SFWDA
  paper map is a 36-tile `sfwda-tile-*` grid warp driven specially inside
  `updateLayerVisibility` off `#showSfwda` (its `LAYER_TOGGLES` entry has an EMPTY
  layer set), so the panel's layer-intersection bridge couldn't find it and its
  node pointed at a non-existent `sfwda-paper` layer → the toggle was dead.
  Fix: `EXPLICIT_HOST_TOGGLE = {sfwda:'showSfwda'}` in `buildVisibilityBridge`
  maps that node to the host checkbox directly. Verifier
  `/tmp/verify_phase4_sfwda.py` **7/7**: panel eye flips `#showSfwda` → host shows
  36/36 tiles → off → 0/36. (The panel's own single-image alignment editor stays
  standalone-only; the host owns the real 6×6 warp.)
  **NO REGRESSION:** `/tmp/verify_swap.py` still **12/12**. v33→**v34**
  (`sw.js` + `#appVersion`). Files: `website/js/panel.js`, `website/js/main.js`
  (+2 additive: the highlight bridge), `website/sw.js`, `website/index.html`.
  **(4) DEAD-CODE CLEANUP — NOT done this pass; the card's Stage-2 delete list is
  CORRECTED by observation.** The owed "delete `buildEditorTree`/`renderFeatureList`/
  `renderEditDock` + `SECTION_RUNTIME`/`FEATURE_LIST_LAYERS`-as-panel" is partly
  WRONG: `renderFeatureList` (22 callers), `FEATURE_LIST_LAYERS` (17 readers) and
  `featureListRuntime` are **load-bearing for the LIVE POI tab + calendar +
  search** (not just the hidden panel); `SECTION_RUNTIME` does not exist (it's
  `featureListRuntime`); `buildEditorTree` (`main.js:583`, 1 caller :2884) REGISTERS
  runtime targets the live subsystems read (see `main.js:1091`) → load-bearing,
  do NOT delete. Genuinely DEAD: `buildInlineEditor` (`main.js:4221`, ZERO callers,
  comment says "safe to delete") — but it is INTERLEAVED with sibling helpers
  (`makeEditorLabel:4385`/`makeEditorAction:4391`/`describeGeometry:4405`) and LIVE
  functions (`deleteEditorFeature:4454`/`duplicateEditorFeature:4466`, which call
  `renderEditDock`/`renderFeatureList`), so it is not a clean single-block delete.
  `renderEditDock` (`:3984`) has 4 active callers (3973/3981/4459/4483) rendering
  into the hidden `#editDock`; `buildEditDock` (`:4048`) has 1 caller (`:3993`).
  The dead code renders HARMLESSLY into hidden DOM. **Disposition:** the user
  picked option 1 (POI), not the dead-code option; deleting interleaved dead/live
  code in a 10k-line file is risk > reward for hygiene and was NOT done — it wants
  its own carefully-verified pass with this ledger in hand.

- **2026-06-04 update:** user confirmed this IS the replacement for the index
  panel ("make sure it has all the layers"). **Slice 11** ported the full
  ~29-layer index-page set into the live page's provenance sections. See below.
- **2026-06-04 row-affordance tweak (UNCOMMITTED):** user review — *"the number
  moved to next to the collapse icon. and the lock moved to next to the visible
  check."* Done in `panel.js` + `right_panel.html`: the item **count** is now a
  direct child of the group row sitting immediately left of the collapse chevron
  (was inside `.node-select`), and the group **lock** moved off the row INTO the
  edit area beside the relocated **Visible** check (`renderVisibilityField` now
  wraps a `.field-toggle-label` + the `lockButton`; the row no longer renders a
  lock). One-model/one-renderer held — `node.locked` still drives the lock and
  still cascades to item locks via `effectiveItemLock`. Verified by observation
  (`/tmp/verify_panel_move.py`, served :8077): **11/11 checks, 0 console errors**
  — count adjacent to chevron (15px), lock adjacent to Visible (8px), both
  controls still function (checkbox flips the map layer, lock flips
  `node.locked`). Shots: `brain/output/playwright_panel_move_row.png`,
  `…_panel_move_editarea.png`. (`/tmp/verify_panel.py` is stale pre-this-change —
  it waits on a `streams` node id the all-layers model no longer has.)
- **2026-06-04 icon toggles (UNCOMMITTED):** user — *"the visible to be a
  eyeball icon that we can toggle. I also need a star icon that can be toggled."*
  The group edit area's `Visible` checkbox became an **eye icon toggle** (open =
  visible / slashed = hidden), and a new **star icon toggle** (fills when on)
  sits beside it, so the group control row is now **eye · star · lock**, three
  icon buttons sharing one shape (`.icon-toggle`: tan off / rust `.on`). Model:
  the `{kind:'visibility'}` field became `{kind:'controls'}` →
  `renderControlsField` (eye+star+lock); helpers `eyeToggle`/`starToggle` off a
  shared `iconToggle`; eye drives `node.visible`+`setLayerVisibility` (keeps the
  `data-field="visible"` verifier hook), star drives a new `node.starred`. Star
  is a working **state toggle today** (fills + persists in the model); it has no
  downstream map/highlight effect yet — that hooks into `node.starred` when the
  highlight/featured surface lands (was "★ inert until surfaces exist" in the old
  design). Interpretation chosen (reversible): group-level, in the edit-area
  control row where Visible already lived — not per-item / not on the row. KISS,
  one-model/one-renderer held. Verified by observation
  (`/tmp/verify_panel_move.py`, served :8077): **14/14 checks, 0 console errors**
  — eye flips `node.visible` + the real map layer + swaps open/slashed; star
  flips `node.starred` + fills (computed `rgb(180,86,31)`); lock still flips
  `node.locked`. Shots: `brain/output/playwright_panel_icons_editarea.png`
  (default: eye-on/star-off/lock-on) + `…_panel_icons_toggled.png` (eye-off,
  star-filled).
- **2026-06-04 star = per-feature highlight → LEFT POI sidebar (UNCOMMITTED).**
  User corrected the star's meaning: *"stars are for the user highlight under POI
  on the left sidebar."* My prior group-level placement was wrong. Grounded in
  the live app via an Explore pass (`main.js`: `properties.highlight`,
  `toggleFeatureHighlight` :3254, `buildPoiGroups` :1115 filtering
  `highlight===true`, `renderPoiTab` :1337, `gotoPoi` :1416 — star title *"surface
  in left-rail POI tab"*). Rebuilt faithfully, one-model/one-renderer: **(1)**
  removed the star from the group control row (now just **eye · lock**); **(2)**
  the star is now a **per-item** toggle on every item row (next to the lock) that
  flips `item.props.highlight` — a curation/VIEW action, so NOT lock-gated, and
  the state rides the feature props through copy/move/reassign; **(3)** added a
  **left sidebar** (`.panel-left` + `#leftBody` in `right_panel.html`) titled
  **POI** whose list is DERIVED from the SAME `PANEL_MODEL` — `collectHighlighted`
  walks nodes + `deriveItems`, filters `highlight===true`, groups by layer node;
  `renderLeftPanel` draws group-head + count + rows; **(4)** clicking a POI row →
  `gotoPoi` enables the layer if off, `flyToItem`, expands + selects it on the
  right. `rerender()` now also refreshes the left panel; boot renders it.
  **Faithful-but-simplified (noted):** highlight is in-memory only (no
  localStorage yet — same deferred-persistence fork as the rest of the rebuild);
  any feature is starrable (no per-layer `highlightable` gate — KISS); the left
  sidebar is an always-open panel, not the live app's icon-tab drawer (future).
  Seed `aop_editor_seed_pois.geojson` ships one pre-highlighted feature (**AOP
  Pavilion**), so the POI list is correctly non-empty at boot. **Verified by
  observation** (`/tmp/verify_panel_move.py`, served :8077): **16/16 checks, 0
  console errors** — control row eye+lock/no-star; per-item star present; star →
  buildings group appears under POI (row count +1, label matches); POI-row click
  flies the map + selects on the right; unstar drops it (count back to boot).
  Shots: `brain/output/playwright_panel_poi_left.png` (POI list: Park buildings
  ×2 + Drawn POIs ×1), `…_panel_item_stars.png` (filled vs hollow item stars),
  `…_panel_poi_starred.png` (both panels).
- **2026-06-04 item lock → edit area (consistency) (UNCOMMITTED).** User flagged:
  *"there is a lock on the brand logo rows and not under them in the edit area.
  what is different here?"* Diagnosed by observation: the **group** lock moved
  into the edit area last change, but **item** locks were still on the row, and
  the item edit area only showed a passive "Locked" hint (when locked) — so an
  UNLOCKED layer (brand logos has no `locked:true`, unlike the reference layers)
  showed a lock on the row and nothing in the edit area. Fix = make items match
  groups: the per-item lock now lives in the **edit area** (new `{kind:'lock'}`
  field → `renderItemLockField`, a `.field-controls` row leading the item editor;
  always clickable, with the "Locked — unlock to edit" text beside it when
  locked). Removed the lock from the item row (rows now carry only **select +
  star**) and dropped the old standalone `renderEditArea` locked-hint (the lock
  field carries it). Rule is now uniform: **locks live in the edit area, never on
  rows; rows carry quick toggles only (group: count/chevron; item: star).**
  Verified by observation (`/tmp/verify_item_lock.py`): **16/16, 0 console
  errors** — for both brandLogos (unlocked: edit-area lock open, no hint, fields
  enabled) and buildings (locked: edit-area lock closed + hint + fields disabled),
  no row lock, and the edit-area lock toggles state + gates the fields. POI/star
  flow regression-clean (`verify_panel_move.py` 16/16). Shots:
  `playwright_item_lock_brand.png`, `…_item_lock_buildings.png`.
- **2026-06-04 EVERYTHING in the edit module + declarative control row
  (UNCOMMITTED).** User set the architecture: *"even the star should go into the
  edit area. I am trying to move everything there and make a generic edit module
  that anything can use."* So: **rows are now pure selectors** (group: label +
  count + chevron + draw-`+`; item: label only) and **every control is a field in
  the one edit module** (`renderEditArea(fields, ctx, locked)`). Moved the last
  row control — the per-item **star** — into the edit area. Made the control row
  **declarative**: a `TOGGLES` registry (`visibility`/`star`/`lock`, each binding
  to ctx.node or ctx.item) + `renderControlsField(field, ctx, locked)` that renders
  whatever toggles the field NAMES. Each context just declares its row:
  editable group `['visibility','lock']`, non-editable group `['visibility']`,
  item `['star','lock']`. Deleted the bespoke `{kind:'lock'}` field +
  `renderItemLockField` (folded in). Net rule: **rows select; the generic module
  edits; controls are named toggles anything can compose.** Verified by
  observation (`/tmp/verify_generic_editor.py`): **13/13, 0 console errors** — no
  toggle/lock on any group or item row; group control rows resolve eye+lock /
  eye-only; item control row = star+lock with the locked hint + gated fields;
  edit-area star still surfaces to the left POI (+1 / −1); edit-area lock toggles
  + ungates fields. Shot: `playwright_generic_editor_item.png` (clean rows + the
  star·lock control row leading the editor). NOTE: the old throwaway
  `verify_panel_move.py` now fails — it asserted the star ON the item row (the
  superseded layout); replaced by `verify_generic_editor.py`. Not a regression.

- **2026-06-04 SAVE PATH SHIPPED — disk persistence + export + re-bake
  (UNCOMMITTED).** User: *"need a save path so that when we make updates we can
  export those and re-bake them. we dont have a db in prod all values are served
  from json."* This is slice #10's "Disk persistence" fork, now built. **Fork
  put to the user and ANSWERED: overrides = DIFFS** (not full-file replace) — the
  store keeps only what changed so git diffs stay reviewable and raw→core→publish
  survives. The loop (no DB; all JSON):
  **edit → localStorage diff → "Export edits" → `mvp/scripts/bake_panel_overrides.py`
  merges into `website/data/*.geojson` → review diff, commit → "Clear".**
  Shipped (4 files): **(1)** `website/js/panel.js` — a persistence block
  (`aop_panel_overrides_v1`): served edits store a `{properties,geometry}` diff
  keyed `"<source>:<canonical id>"` (every feature now carries a canonical `id`
  post-re-bake — that's the JS↔Python match key); drawn features are kept WHOLE
  in `created[]`; deletes in `deleted[]`. `commitChange`/`persistDelete`/
  `syncCreated` wired into the text/select/group/star/move/delete/create paths;
  `applyStoredOverrides()` replays diffs onto the fetched collections at boot
  (dedupes a baked draw by `_id`|`id` so no double-show). `highlight` is VIEW
  state — saved for convenience but the baker never bakes it. **(2)**
  `right_panel.html` — a pinned footer: **⤓ Export edits** (downloads the diff
  JSON; `window.__overridesExport` hook) · **Clear** · an unsaved-count badge.
  **(3)** `mvp/scripts/bake_panel_overrides.py` — consumes the export
  (`aop-panel-overrides-v1`): applies identity/facet props + moved geometry to
  the matched feature (stamps `last_checked`=today, the source-register honest
  minimum), appends drawn features to their OWN file with editor provenance
  (`source=AOP editor (drawn)`·`confidence=observed`·`permission=AOP
  first-party`·`status=core`), removes deletes; idempotent (`--dry-run`,
  `--no-stamp`). **(4)** `website/data/aop_user_features.geojson` — new served
  destination for drawn features (its own file so `rebake_canonical.py`, which
  re-bakes FROM `data/raw/`, never clobbers a draw). `userFeatures` source
  repointed url→this file. **Pipeline order matters** (documented in the script):
  `rebake_canonical.py` (machine refresh from raw) FIRST, then
  `bake_panel_overrides.py` (human curation on top) — else the canonical re-bake
  discards panel edits. **Verified by observation** (`/tmp/verify_panel_save.py`,
  served :8077): **14/14, 0 console errors** — create→localStorage(1); rename
  created + (unlocked) building both persist keyed correctly; export payload
  carries schema+sources+created+edits; **both survive a reload** (replayed from
  the store); baker dry-run reports the building edit + the drawn add. Real-write
  test: building renamed + `last_checked` stamped, drawn feature lands
  canonical-first with no panel-internal keys, **2nd run is a true no-op**
  (idempotent); data tree restored after. **Owed/next:** persist is its own
  `aop_panel_*_v1` key (not yet reconciled with the live app's
  `aop_positioned_features_v1` — that's the swap-time merge); the
  `rebake_canonical.py`→`bake_panel_overrides.py` ordering wants a wrapper script
  or a committed-override-layer decision if the served files ever become build
  outputs; commit is the user's git gate (incl. whether to track
  `aop_user_features.geojson`).

- **2026-06-05 SWAP "NO LAYERS" BUG — diagnosed + fixed by graceful fallback
  (UNCOMMITTED, v32→v33).** User: *"review our new edit panel integration… our
  layers are visible. Currently I do not see any layers. figure this out before
  deleting the old one fully."* **Diagnosed by observation, not theory.** The
  Stage-1 files were correct (clean-served panel = 5 sections / 32 layer rows / 0
  errors; `verify_swap.py` 12/12). The blank came from the **v31→v32 service-worker
  transition**: `sw.js` serves `/js/` + `/css/` **stale-while-revalidate**, so on
  the first reload after the bump the OLD v31 SW serves a **stale `main.js`** (no
  `window.AOP_HOST_MAP`) while the **new `panel-embed.css` loads fresh and hides
  the legacy panel**. The embedded panel polls for the host map, never finds it,
  and `#aopPanelMount` stays EMPTY → **empty new panel + hidden old panel = zero
  layers.** Reproduced exactly by serving a host-map-stripped `main.js` (`hostMap:
  false`, `newPanelNodeGroups:0`, `legacyDisplay:none`, `legacyNodeRows:5`).
  **Root flaw:** `panel-embed.css` hid the legacy panel *unconditionally*,
  independent of whether the new panel actually mounted. **Fix (fail-safe
  graceful degradation):** the legacy-hide rules are now gated on
  `body.aop-embed-ready`, a class `panel.js` adds in `finishBoot()` **only on a
  successful embedded boot**. If the boot never runs (stale `main.js`, JS error,
  20s host-map timeout), the class is never added → the **old panel stays
  visible**, so the user always has layers. Also: `whenHostReady` now logs a clear
  console error on timeout (was silent), and `VERSION` v32→**v33** (`sw.js` +
  `#appVersion`) so a stuck browser cleanly reinstalls a consistent asset set
  (skipWaiting + clients.claim already present). **Verified by observation** (served
  :8077): stale-`main.js` repro now `legacyDisplay:block` / **7 legacy sections +
  30 layer toggles visible** (graceful); normal case `aop-embed-ready:true` / **32
  new-panel rows / legacy hidden / 0 errors**; `verify_swap.py` still **12/12, 0
  errors**; pixels confirm the new panel renders all sections + the live map.
  Files: `website/js/panel.js`, `website/css/panel-embed.css`, `website/sw.js`,
  `website/index.html`. Old panel deliberately KEPT (now the fallback) per the
  user's "before deleting the old one fully" — Stage 2 cleanup still owed. Commit
  is the user's git gate.

- **2026-06-05 SWAP INTO index.html — Stage 1 SHIPPED + verified (UNCOMMITTED,
  v31→v32).** User: *"do the swap into index.html."* The long-deferred swap. Put
  the one real fork to the user → **keep everything** (the new panel drives the
  EXISTING live map; retire the patchwork; don't lose search/calendar/presets/
  PWA). Mapped the 10k-line `main.js` with 3 parallel Explore agents + observation.
  **Two facts made it safe:** (a) **78 of the new panel's 85 layers already exist
  in main.js with identical ids** (its paint was ported verbatim), so the new
  panel can drive the live layers by id; (b) the host's `setLayerVisibility`/
  `applyPreset`/`updateLayerVisibility` are reachable globals and presets work by
  setting the static `#showXxx` checkboxes then calling `updateLayerVisibility`.
  **Architecture (user's choice realized): main.js stays the host** — owns the
  map, the base layers, search, calendar, presets, PWA, terra-draw — and
  **`panel.js` gains an EMBEDDED mode** that attaches to it and is ONLY the right
  panel. **Shipped:** `panel.js` dual-mode boot (`window.AOP_PANEL_EMBED` →
  attach to `window.AOP_HOST_MAP`, add ONLY its own draw layers, fetch data for
  lists, render into `#aopPanelMount`, poll for a host layer since main.js's load
  is async); a **visibility bridge** (node → host checkbox via
  `window.AOP_HOST_LAYER_TOGGLES`; eye-toggle sets the checkbox + dispatches its
  change event so visibility flows through the host's machinery → **presets +
  panel never desync**; preset buttons resync the panel); `main.js` +2 additive
  export lines (`AOP_HOST_MAP`, `AOP_HOST_LAYER_TOGGLES`); `index.html` (load
  panel.js after main.js, `#aopPanelMount` + Export/Clear footer, session-tools
  tagged `.aop-keep`); **`css/panel-embed.css`** (NEW — the proven right_panel.html
  styles SCOPED under `#aopPanelMount` so id-specificity beats app.css's old-panel
  classes; + hides the legacy toggle/editor content while keeping its checkboxes
  in the DOM for presets); v31→v32 (`#appVersion` + `sw.js`, panel assets
  precached). **Verified by observation** (`/tmp/verify_swap.py`, SW blocked,
  :8077): **12/12, 0 real console errors** — new panel mounted on the LIVE page;
  eye-toggle flips the live layer + syncs `#showLandcover`; **Topo preset applies
  + panel resyncs**; **search 4 results**; calendar opens; **CRUD-create a POI →
  into the export/save payload**; legacy hidden, session-tools kept. Pixels:
  `brain/output/swap_live_panel.png` (panel correct; left rail + event schedule +
  countdown + map intact). **No regression to standalone** right_panel.html
  (`verify_crud_full` 16/16, `verify_panel_save` 14/14). **Stage 2 (owed, deferred):**
  the patchwork is HIDDEN, not deleted — a cleanup pass should remove
  `buildEditorTree`/`renderFeatureList`/`renderEditDock` + the
  `LAYER_TOGGLES`-render/`SECTION_RUNTIME`/`FEATURE_LIST_LAYERS`-as-panel/edit-dock
  code (main.js still runs them into hidden DOM); the new POI-star left sidebar is
  skipped in embed mode so index's own POI tab still owns highlights (two systems
  to reconcile); panel `setData` on the shared sources overwrites the host's
  `aop_positioned_features_v1` drag overrides + `aop_editor_pois_v1` POIs for an
  edited layer (store reconciliation — the new panel should read host data, or the
  old stores retire); the SFWDA-paper node (host uses a 6×6 tile warp, not the
  panel's single image) + the paint-tuning sliders are not wired in embed mode.
  Commit is the user's git gate.

- **2026-06-04 CRUD FOR ALL BASE THINGS — SHIPPED + verified (UNCOMMITTED).**
  User (MVP push): *"this is CRUD for all our base things and the ability to
  re-bake… the best you can do is 60% of any real task."* Observed the real gap
  by running the app (`/tmp/observe_crud.py`): the base/reference layers were
  **read + update-only** — Create lived ONLY on the 3 generic draw groups
  (Points/Lines/Polygons), and Move/Delete were handed ONLY to user-drawn
  features (`itemFields` gave reference items just fly+copy). So you could not
  add a building/trail/POI/callout, nor delete/move one. Closed it inside the one
  model/one renderer:
  **(C)** every editable single-geometry base layer now synthesizes a `create`
  spec (`nodeCreateSpec` — geom from `nodeGeom`, cemeteries→Point marker,
  `brandLogos` opted out via `CREATE_BLOCK` since a logo needs an icon picker), so
  the `+` now appears on **10 layers** (was 3): +cemeteries/boundaries/buildings/
  aopTrails/editorPois/visitorContext/pubTrails. A draw writes a new feature
  straight INTO that layer's own source carrying the Common Minimum Schema
  (`canonicalDefaults`), so it paints as that layer and bakes back to that
  layer's file. Created features carry `_id` (local) + `_src` (home source) +
  `__locked:false` (a feature you just drew is editable even inside a locked
  reference layer — the lock protects EXISTING curated data, not your new one).
  **(D + move)** `itemFields` now gives EVERY editable item fly/copy/**move**/
  **delete**; move+delete are lock-gated, so reference data is protected until you
  unlock it, while drawn/created features get them immediately.
  **(re-bake, source-aware)** `syncCreated` now snapshots every `_id`-bearing
  feature across ALL loaded sources (not just userFeatures); `applyStoredOverrides`
  replays each into its `_src` source with per-source dedup; `bake_panel_overrides.py`
  groups `created[]` by `_src`→file (a drawn building → `aop_buildings.geojson`,
  a plain draw → `aop_user_features.geojson`). **Diff-cleanliness fix:** the served
  files are **minified** (rebake_canonical.py writes `separators=(",",":")`,
  single line). The old baker pretty-printed (`detect_indent` can't read a
  single-line file → fell back to indent=2) → a 1-feature edit produced a
  **438-line reformat**. Rewrote `write_fc` to match the canonical minified
  format + dropped `detect_indent`; a bake is now **1 line changed** (the minified
  line, reviewable via `git diff --word-diff`). Dead config removed (`refItems`
  no longer carries `actions`/`provenance`; itemFields always renders the full set
  + provenance). **Verified by observation** (served :8077): `verify_crud_full.py`
  **16/16** (create a building into the LOCKED buildings layer via its +; it's
  unlocked+editable; carries `_src`+canonical schema; NOT leaked to userFeatures;
  has Move+Delete; existing building locked→unlock→edit; export carries the draw
  +the edit+sources; **survives reload** replayed into fema-buildings);
  `verify_crud_dm.py` **4/4** (unlock→Delete removes + records `source:id` in
  `deleted[]`; unlock→Move records a geometry diff); baker round-trip: drawn
  building bakes to `aop_buildings.geojson` (`id:u1`, schema, `last_checked`
  stamped, `_src`/`_id` stripped), edit applied, **1-line minified diff**, **2nd
  run idempotent no-op**, data tree restored; `verify_panel_save.py` **14/14
  (no regression)**; full model still renders **5 sections / 32 rows / 85 map
  layers / 0 real console errors**. (One pre-existing console flake unrelated to
  this work: the default-OFF `sfwda-paper` image layer occasionally logs
  `Failed to fetch (0) …webp` in headless though the file serves 200 — unchanged
  from HEAD.) **Owed/next (unchanged forks):** `__group` reassignment is still
  view-only (stripped on bake) — direct-create now supersedes it for filing into
  a base layer; whether `+` on a locked layer should require unlock first (chose
  always-show, new feature unlocked); the swap into `index.html`; commit is the
  user's git gate.

#aop #04_event_app #right_panel #rebuild #mvp #kiss #save_path #crud

-----

## Why (the diagnosis — confirmed in code, not theory)

The live right panel is **five interaction models stitched together**, and one
layer (e.g. buildings) is described in **six places** and rendered through
**five code paths**:

Six parallel descriptions of one layer:
1. Hand-written HTML `<label><input type="checkbox" id="showBuildings">` in
   static `<section>` blocks — `index.html` ~332–484.
2. `LAYER_TOGGLES` (`main.js:1760`) — toggle → MapLibre layer ids.
3. `PRESET_TOGGLE_IDS` (`:1803`) — derived.
4. `TUNABLE_LAYERS` (`:1806`) — paint.
5. `FEATURE_LIST_LAYERS` (`:2231`) — groups/idField/flags/rowLabel.
6. `SECTION_RUNTIME` (`:5471`) — per-section behavior.
   …plus a **hidden `#legacyLayerToggles`** mirror block (`index.html:447`)
   two-way bridged to the visible checkboxes (a preset/verifier hack).

Five render paths: `buildEditorTree`, `renderFeatureList` /
`renderFeatureListInto` / `refreshFeatureListCounts`, `buildEditDock` /
`renderEditDock`, `renderTuneControls`, dead-but-present `buildInlineEditor`.

The 2026-06-03 "unified edit dock" was bolted **onto** this, not a replacement —
which is why it still *behaves* like a patchwork. That feel is real.

## The target architecture

- **One model.** `PANEL_MODEL = { title, sections:[ { id, label, nodes:[…] } ] }`.
  A node has a `kind` the renderer dispatches on. The model describes the
  **panel**, not the map style; a node references the MapLibre layer ids it
  controls via `mapLayers` (the one thing `LAYER_TOGGLES` did, folded in).
- **One renderer.** `renderPanel → renderSection → renderNode(kind)`. Adding a
  capability = a new field on the node + one new branch in `renderNode`, never a
  new surface / new config object / new static HTML.
- **KISS.** Nothing comes back unless the user asks for it. Explicitly NOT
  carried over yet: the hidden bridge, SFWDA grid-alignment, structure-box
  presence quirk, paint drawer, edit dock, bucket tree, preset capture.

## Schema variability — the next architectural layer (2026-06-04)

User: *"the variability of the data and its sources … each one has a different
schema … I should be able to edit a trail description the same way I edit the
pavilion text."* The renderer is already one path; the **data contract under it
is not** — the same concept (title/description/kind/source) uses a different
property key in nearly every source file (audited: ~10 keys just for "name").
The hand-written `PROVENANCE_KEYS` alias list in `panel.js` is the proof — it
already unifies the *read-only* provenance half by hand; the editable identity
half (`title`/`description`/`kind`) has the same gap and is why `itemFields()`
still forks user-feature vs. reference-feature.

**RESOLVED → SHIPPED (2026-06-04, UNCOMMITTED).** User chose a **full data
re-bake**, not a render adapter: *"I would not have a half rebuild. re-bake the
data entirely in our new format. keep the raw we can refer back. our re-bake
should have our fields."* Vocabulary: *"go with what is common"* → `name` ·
`description` · `kind` + the source-register provenance block (the publish-view's
own vocabulary). Built `mvp/scripts/rebake_canonical.py` (archives pristine
originals → `website/data/raw/`, rewrites every feature canonical-first via the
crosswalk + per-layer provenance defaults, additive so the map/`index.html`
don't break, machine layers get layer-level provenance in `data/_schema.json`).
Then collapsed `panel.js` `itemFields()` to ONE frame for all features and
`PROVENANCE_KEYS` to the five canonical fields. **Verified:** map renders all
layers post-re-bake (0 errors); a trail and the pavilion now show the same
editor frame with live Name + Description. Full record + owed items in
`brain/research/common_feature_schema.md` ("Implementation — the re-bake").

## Staged re-add (user directs each, one at a time)

1. ✅ **Layer visibility toggle** — SHIPPED (below).
2. ✅ **Section collapse** — SHIPPED. Section gains a `collapsed` field (model =
   source of truth); `renderSection` draws a clickable `.section-header` (label +
   rotating chevron, `aria-expanded`); `toggleSection` flips the model field +
   `.collapsed` class; CSS hides `.section-body` when collapsed. Verified headless
   (open→collapsed→reopened: class + body-visibility + aria all track, 0 console
   errors). Shot: `brain/output/playwright_panel_rebuild_collapsed.png`.
3. ✅ **Items list under a layer (general)** — SHIPPED. A layer node can declare
   an `items` descriptor `{ source, key?, label }`: where the list comes from (a
   loaded GeoJSON source — same data the map draws, no second fetch), an optional
   dedupe `key`, and a `label`. `deriveItems(node)` is the one path every
   item-bearing layer uses (dedupe → label → natural sort). `renderLayerNode`
   now draws, for item nodes, `[checkbox] [expand button: label · count · ▸]` +
   a collapsible `.node-items` list (independent of section collapse, own
   `expanded` field + `toggleNodeItems`). Checkbox still toggles visibility; the
   expand button toggles the list. Proven general: Trail network (101 rows: 100
   numbered + 1 unnumbered bucket, default expanded) AND Buildings (5 rows,
   default collapsed). Verified headless: counts match the geojson, badge matches
   count, expand/collapse tracks class + visibility + aria, 0 console errors.
   Shot: `brain/output/playwright_panel_rebuild_items.png`.
4. ✅ **Select → inline edit area (group OR item); visibility relocated** —
   SHIPPED. One `selection` state (`{kind:'group',nodeId}` | `{kind:'item',
   nodeId,key}`, single-open, click-again-to-close); `selectTarget` re-renders
   (`rerender` preserves scrollTop). The selected row gets an `.edit-area`
   directly beneath it. **Visibility moved off the rows into the group edit
   area** — layer rows now carry NO inline checkbox; selecting a layer opens a
   group edit area whose `Visible` toggle drives `setLayerVisibility`. Items are
   selectable (`.item-select`); selecting one opens an item edit area (Details
   static line + an in-memory Notes field — disk persistence deferred). One
   `renderEditArea` + `renderField` dispatch (`visibility`/`note`/`static`) for
   both; `groupFields`/`itemFields` decide contents. Group row keeps a separate
   chevron button for the items list (the two clicks don't fight); `data-node-id`
   added to `.node-group` as a stable hook. Verified headless: 0 row checkboxes,
   visibility via edit area flips the map, item-select opens an edit area under
   the item with Notes+Details (typed note sticks), group-select opens Visible &
   clears the item (exactly one edit area open), 0 console errors. Shots:
   `playwright_panel_rebuild_item_edit.png`, `…_group_edit.png`.
5. ✅ **User-entered features + create ability** — SHIPPED. New `userFeatures`
   node ("My features") backed by a mutable in-memory FeatureCollection (MAP_DATA
   gained inline `data` alongside `url`; one `user-feature-points` circle layer).
   A node with a `create` descriptor shows a `+` on its row → `startCreate` enters
   place mode (rust hint banner + active `+` + crosshair cursor; Esc/Cancel
   aborts); the next `map.on('click')` → `placeFeature` drops a Point with a
   stable `_id` + `defaultProps(seq)` name, `setData`s the source, selects the new
   item and opens its edit area. Item edit fields are now declarable per layer
   (`items.fields`): user features get an editable **Name** (`text` field kind —
   commits on blur, re-renders so the list label + sort update; key is `_id` so a
   rename never breaks selection) + **Notes**. One new field kind, one new node —
   no new surface. Verified headless: `+` enters place mode (banner+active+
   crosshair), a fired map click adds exactly one list item + one source feature
   and ends place mode, the new item is selected with Name "Feature 1" + Notes,
   renaming updates the row label to "Pit road", 0 console errors. Shots:
   `playwright_panel_rebuild_placing.png`, `…_created.png`.
6. ✅ **Point / Line / Polygon groups, each with its own create + editor set**
   (the old layout) — SHIPPED. The single "My features" node split into three
   sibling layer nodes (`userPoints`/`userLines`/`userPolys`) over the SAME
   `userFeatures` collection, each with an `items.filter` by geometry type, its
   own `mapLayers` (circle / line / fill+outline, geometry-filtered), its own
   `create.geomType`, and its own `items.fields`. Create is geometry-aware:
   `startCreate` opens draw mode; Point commits on one click, Line/Polygon
   collect clicks and commit on **double-click** (`dedupeConsecutive` drops the
   dbl-click's duplicate vertex; `doubleClickZoom` disabled during draw; dashed
   `__draft` line + vertex dots show progress; Esc/Cancel aborts). New geometry
   sorts into its matching group automatically. **Editor sets differ per group**:
   Points = Name+Notes, Lines = Name+**Difficulty** (new `select` field kind,
   easy/moderate/hard)+Notes, Polygons = Name+Notes. Verified headless: 7 layer
   rows (3 user + 4 ref), Point(1 click)→"Point 1" no-difficulty, Line(3 clicks+
   dbl)→"Line 2" with-difficulty, Polygon→"Area 3"; source tally Point/Line/
   Polygon = 1/1/1 (filters route correctly); rename updates label; 0 console
   errors. Shot: `playwright_panel_rebuild_buckets.png`.
7. ✅ **Reference layers nest under their geometry group** — SHIPPED. A node can
   now carry `children` (sub-nodes), and the renderer wraps a group's own items +
   its child nodes in one expand-gated `.node-content` (rendered recursively via
   `renderNode`; `applyAllVisibility` walks children). Per the user: **Trail
   network nests under Lines**, **Buildings nests under Polygons**, **Park
   boundary is a single item in its own group under Polygons** (derived from
   `publish.geojson` polygon → 1 item, labeled by the parcel name). Streams also
   moved under Lines (the consistent geometry home — surfaced to the user, easy to
   move). Item counts are scoped to a group's OWN items so a parent doesn't tally
   its children. Verified headless: 7 layer rows, trails⊂Lines + buildings⊂Polys
   + boundary⊂Polys (DOM containment), boundary itemCount=1, trails=101,
   buildings=5, create still routes new geometry to the right group, 0 console
   errors. Shot: `playwright_panel_rebuild_nested.png`.
8. ✅ **Lock (read-only gate) on every group + item** — SHIPPED. A lock icon
   (open/closed padlock SVG) sits on every group row and every item row.
   Locked → the edit area renders **read-only** (a "Locked — unlock to edit" hint
   + all inputs `disabled`); unlocked → editable. **Visibility is never
   lock-gated** (it's a view control, not data). Group lock lives on `node.locked`;
   item lock lives on `props.__locked`, falling back to the group's value
   (`effectiveItemLock`), so **locking a group cascades to its non-overridden
   items**, and a single item can be unlocked inside a locked group (override).
   **Defaults: reference layers (trails/buildings/boundary/streams) LOCKED, user
   features UNLOCKED** — honors "everything editable, but I won't edit many."
   `renderField` threads `locked` to text/select/note (disable); static stays
   read-only. Verified headless: 7 group locks + a lock on every item; reference
   groups default locked / user groups unlocked; a locked trail item shows the
   hint + disabled note; unlocking it enables the note; locking a user group
   disables its item's Name (cascade); 0 console errors. Shot:
   `playwright_panel_rebuild_locked_item.png`.
9. ✅ **Edit features ported from the live dock (one batch, user-directed
   "do what NEEDS doing")** — SHIPPED. Five live-view capabilities, each added
   as a declarative node field + one renderer branch (NO `layerKey===` branches
   — that hardcoding is the live dock's actual smell, deliberately not brought):
   - **Per-feature actions** via a new `actions` field-kind + one `ACTIONS`
     registry: **🎯 Fly to** (`flyToItem` — `flyTo` a Point, `fitBounds` a
     line/poly via `geometryBounds`), **⧉ Copy GeoJSON** (`copyFeature` →
     `cleanFeature` strips `_id`/`__locked` → clipboard w/ textarea fallback +
     toast; `window.__lastCopy` observable hook), **✋ Move**, **🗑 Delete**.
     A node declares which it offers (`items.actions`); fly/copy never
     lock-gated, move/delete are. User features get all four; reference layers
     get fly+copy only.
   - **Move** — `startMove`→move-mode reuses the create map-click plumbing
     (`moving` state + hint banner + Esc/Cancel). Point: the click is the new
     location. Line/Polygon: translate every vertex by (click − `geometryCenter`).
     Vertex editing intentionally OUT (deferred in the live view too).
   - **Source / provenance read-out** — `items.provenance:true` appends
     read-only `static` fields for whichever `PROVENANCE_KEYS` the served data
     actually carries (source/confidence/license_or_permission/publish_status/
     validated/produced/address…). Answers the northstar's six product-test
     questions. On trails/buildings/boundary.
   - **Copy all as GeoJSON** per layer — group edit area gains a `copyAll`
     action (`copyAllFeatures` → FeatureCollection). The northstar-sanctioned
     export path.
   - **Reveal** — clicking a rendered feature on the map (`revealAtPoint` →
     `queryRenderedFeatures` over a 4px box → `findNodeByLayer` →
     `node.items.key`) selects its item + expands its whole chain (`nodeWalk`/
     `expandTo`).
   Verified headless (extended `/tmp/verify_panel.py`, **0 console errors**):
   reference item = Fly+Copy only + Source provenance; building item = full
   provenance block incl. Confidence; Copy-all = valid FC of 5; user point =
   Fly/Copy/Move/Delete, Copy = clean Feature (no `_id`); Move relocates the
   point to the click; Delete drops it from the collection; map-click selects
   "Trail 54 · difficult". Shots: `playwright_panel_rebuild_actions.png`,
   `/tmp/panel_userpoint.png`, `/tmp/panel_building_prov.png`.
   **Follow-up (same day): editor moved to a PINNED BOTTOM DOCK.** User: *"when
   I add a polygon the editor should be under the button. I cannot see them if
   they are far away. either directly inline or at the bottom like the live
   version."* First tried the inline option (`scrollIntoView` on the open
   `.edit-area`) — but my test never created an overflowing panel, so the check
   was vacuous and the user reported *"it did not move."* (Lesson re-learned:
   verify against the REAL failing condition, not a setup that can't fail.)
   Switched to the option they named — **the live-version bottom dock**: a new
   `#panelDock` is a fixed footer of `.panel` (panel = flex column: scrollable
   `.panel-body` + `flex:none` dock, `max-height:55%`, own scroll). The edit
   area no longer renders inline under the row (`renderLayerNode`/
   `renderItemsList` only carry the `.selected` highlight now); `renderDock()`
   resolves the current `selection` → node/item and mounts the SAME
   `renderEditArea`/`groupFields`/`itemFields` into the dock, with a header
   (geometry-kind chip + label + ✕-clear). `rerender()` calls it; `dock.dataset.sel`
   (`group:id` / `item:id:key`) is the verifier hook. Because it's a pinned
   footer, the editor is ALWAYS on screen regardless of scroll. **Verified
   against a real overflow** (`/tmp/verify_panel.py` rewritten to read the dock):
   expand Trail network → panel overflows **1967px** → scroll to TOP (Polygons
   far off-screen) → create a polygon → dock `onScreen:true`, shows
   `POLYGON · Area 1` + its editor; full suite (visibility/collapse/nesting/
   create/lock/actions/provenance/copy-all/move/delete/reveal) PASS, **0 console
   errors**. Shot: `playwright_panel_rebuild_dock_overflow.png`.
   **Follow-up #2 (same day): the create/move HINT had the identical disease.**
   User: *"click the map to place points [shows] under the aop edit panel [title]
   not under the button to add… the polygon + is way down there and the same
   instruction is at the top. Is this context rot?"* Correct catch — I'd fixed
   the editor's far-away problem but left `renderPanel` prepending the hint
   banner at the TOP of the scrollable body, so it stranded above a far-down +.
   Fix: the **create hint renders inline directly under the + button**
   (`renderLayerNode`, gated `placing.node === node`), and the **move hint
   renders in the dock** next to the Move button that triggered it
   (`renderDock`, gated `moving`). Verified against the real overflow (trails
   expanded, scrolled to the Polygons +): hint is inside the Polygons group,
   on-screen, <120px under the button, correct text; PASS, 0 console errors.
   Shot: `playwright_panel_rebuild_hint_under_button.png`. Principle for future
   slices: **any transient prompt/editor must appear where the action happens —
   never at the top of a scrolled list.**
   **Follow-up #3 (same day): reverted the dock → INLINE editor + a Group
   selector.** User: *"the editor should exist in the space with the
   instructions. I want them to swap out not jump to the bottom. all editors
   should be inline… choose an item, hit the edit, it expands immediately below.
   in the editor we should be able to set a group. so if I add a bathroom I can
   add to buildings group under polygons."* So the bottom dock is GONE
   (`#panelDock` + its CSS removed). The group/item editor again renders inline
   directly under the selected row (`renderLayerNode`/`renderItemsList`); the
   create hint (under the +) and the move hint (under the item) swap into that
   same inline space. `rerender()` `scrollIntoView({block:'nearest'})`s the open
   editor so an inline editor far down a list is still pulled into view (verified
   under a real 1967px overflow — the new Area 1 editor is fully visible).
   **New: Group reassignment.** A user feature carries an optional `__group`
   (node id); absent → its geometry's default group. `deriveItems` was
   generalized so any node lists its served features PLUS user features assigned
   to it (`effectiveGroup`), and user features always key by `_id`/label by
   `name` so they slot into a reference group cleanly. A new `group` field-kind
   (`renderGroupField`) offers every group by path label (`groupOptions` →
   "Polygons › Buildings"…) and on change sets `__group`, unlocks the feature
   (user-placed stays editable), `expandTo`s the target, and re-homes the
   selection. **Crucial fix:** `itemFields` now gives a USER feature its own
   editor by geometry (Name [+Difficulty for lines] + Notes + Group + Fly/Copy/
   Move/Delete) regardless of host group — so a bathroom moved into the locked
   reference Buildings group keeps a full editable editor, not Buildings'
   read-only reference layout. The per-node `items.fields`/`items.actions` on the
   three user groups were DELETED as redundant (the user editor is geometry-
   derived now). Verified (`/tmp/verify_panel.py`, inline-based, **0 console
   errors**): create a polygon → set Group to Polygons › Buildings → it leaves
   Polygons (count 0), joins Buildings (count 5→6), stays selected + editable
   inline under Buildings. Shots: `playwright_panel_rebuild_group_reassign.png`,
   `playwright_panel_rebuild_inline_overflow.png`. (The dock follow-up above is
   SUPERSEDED — kept as the record of why we tried it and why inline won.)
   **Follow-up #4 (same day): geometry-typed the Group selector.** User: *"why is
   it that I can put a polygon into a point group? is there no typing enforced?
   should there be?"* Verified by observation it was a real bug, not just odd: a
   polygon filed under Points **vanished from the panel** (Points' items filter
   to Point geometry; Polygons drops it on group-mismatch) yet still drew on the
   map, and its visibility decoupled (toggling Points left the polygon's
   `user-feature-polys` layer `visible`). Surfaced the trade-off against the
   locked `no_limiting_code_mvp` rule (that rule governs DATA rejection/hiding,
   not UI mis-filing) and the user chose to type it. Implemented: each node has a
   geometry — user groups via `create.geomType`, reference layers via a new
   `geom` field (`nodeGeom(node)`); `groupOptions(feature)` now offers only
   geometry-compatible groups. Verified (`/tmp/verify_panel.py`): polygon sees
   only `{userPolys, buildings, boundary}`, point only `{userPoints}`, line only
   `{userLines, trails, streams}`; reassign still works; **0 console errors**.
   This is affordance correctness (nothing hidden/rejected at the data level —
   the feature always renders and lands in a working group), consistent with the
   MVP rule's intent. Note for when MVP loosens: `no_limiting_code_mvp` still
   stands for data values/publishability; this typing is UI-only.
10. ⬜ next — **the genuine input points** (each needs a call only the user can
    make; everything cheap-and-correct is now done):
    - ✅ **Disk persistence — SHIPPED 2026-06-04** (see the "SAVE PATH SHIPPED"
      dated bullet at the top of this card). Diffs in `aop_panel_overrides_v1`,
      replayed at boot; Export → `bake_panel_overrides.py` → served GeoJSON.
      Chose its OWN key now; the live app's `aop_positioned_features_v1` is
      reconciled at swap.
    - **Layer paint sliders** (`TUNABLE_LAYERS`) — the one live edit-tab feature
      deliberately NOT brought; it re-couples map-style into the panel. KISS says
      leave out unless the user wants per-layer paint tuning here.
    - **★ highlight / #tag / category** — inert in the isolated prototype (no
      visitor list / event-schedule resolver here). Bring when those surfaces
      exist or on direction.
    - **Swap into `index.html`/`main.js`** — retire the patchwork, migrate
      verifiers, bump `VERSION`. The big one; touches the live app + the user's
      git gate. Earned feature-by-feature; ready when the user calls it.

11. ✅ **ALL LIVE LAYERS PORTED — the rebuild now carries the full index-page
    layer set (user direction: "this page && editor is supposed to replace the
    one on the main index page. make sure it has all the layers").** The panel
    was reorganized from the geometry-group layout into the **live page's exact
    provenance sections** — Source layers / Derived layers / External reference /
    Map editor / User submitted — because that is the organization on the page
    being replaced (index.html `data-section` blocks) and the northstar makes
    provenance the product. **Every one of the live app's ~29 reference layers is
    now a node**, each carrying its real `mapLayers` ids + a map source/paint
    **ported verbatim from `main.js`** so toggles are genuinely wired:
    - **Source layers:** 9-patch AOI, Satellite (TNMap raster), USDA NAIP
      (raster), Lidar tile index, Cemeteries.
    - **Derived layers:** Land cover, Land cover 9-patch, Lidar hillshade (AWS
      terrarium raster-dem), Lidar contours, Publishable boundaries, Park
      buildings, AOP trail network, Simulated Saturday activity.
    - **External reference:** Streams & waterbodies, Springs & gages, Asphalt
      roads (10 sublayers), OSM park/tracks/service/named, SFWDA paper map (image
      source, 4-corner warp), SFWDA traced trails.
    - **Map editor:** the 3 user **draw** groups (Points/Lines/Polygons — the
      create system) + Drawn POIs (editor-poi seed), Event schedule POIs
      (resolved from `aop_event_schedule.json` anchors), Publishable trailheads,
      Visitor context callouts, Brand logos (`addImage` of the two PNG/JPGs).
    - **User submitted:** Submitted trails, Activity hotspots.
    Mechanics: `MAP_DATA` generalized to five source kinds (`url` geojson w/
    optional `resolve`, inline `data`, `raster`, `rasterDem`, `image`, plus
    `images` for `addImage` icons); the boot loader fetches all 27 GeoJSON files
    in **parallel** then adds sources/layers in declared order (draw-order
    preserved). External-tile layers (TNMap/NAIP/AWS/SFWDA) ship initial
    `visibility:'none'` so no network tile is requested before `applyAllVisibility`.
    `visible` defaults mirror the live **Fresh** preset. The renderer is
    UNCHANGED in spirit — still one model, one renderer; two refinements: lock +
    group-reassignment are now gated to **editable** nodes (`isEditableNode` =
    has items or create), so a raster toggle isn't offered a padlock or as a
    drop target. **Verified by observation** (`/tmp/verify_panel_all_layers.py`
    + focused diags, served :8077): **32 panel rows across the 5 sections, all
    map layers present, initial visibility matches the model, local-layer
    toggles flip MapLibre visibility (contours/cemeteries/nine-patch/osm/springs),
    create still works (point placed + named + selected), 0 console errors** on
    load and through toggles+create. Pixels confirm the default-on set renders
    (land cover, trail network, roads, water, boundaries, buildings, **both
    brand logos** — `addImage` worked). Shot:
    `brain/output/playwright_panel_all_layers.png`. (External rasters need
    network to draw their tiles, exactly like the live app — can't render in the
    sandboxed verifier, so they're toggle-verified, not tile-verified.)
    **Deliberately faithful-but-simplified vs. the live app (noted, not lost):**
    event-schedule resolves only anchors that ship coordinates (the per-feature
    #tag seed resolver isn't brought); SFWDA paper uses a single 4-corner image
    (not the 6×6 grid-warp editor); brand `icon-size` is the static `icon_size`
    prop (no zoom-scaling expr) so logos read large at low zoom; contour
    zoom-band fade sliders + all `TUNABLE_LAYERS` paint sliders still NOT brought
    (KISS — they re-couple map-style). `index.html`/`main.js` still UNTOUCHED;
    nothing to git-gate beyond `website/right_panel.html` + `website/js/panel.js`.

## Slice 1 — SHIPPED (isolated prototype, UNCOMMITTED)

Files (new, isolated — `index.html`/`main.js` untouched):
- `website/right_panel.html` — host: full-bleed minimal MapLibre map + the new
  `.panel`; self-contained `<style>`; loads `vendor/maplibre-gl.js` + `js/panel.js`.
- `website/js/panel.js` — `PANEL_MODEL` (4 layer nodes) + the renderer
  (`renderPanel`/`renderSection`/`renderNode`/`renderLayerNode`) +
  `setLayerVisibility` (model → `map.setLayoutProperty`). The prototype map adds
  4 real layers from `website/data/` (publish boundary, trail network,
  buildings, water streams) so the toggle is genuinely wired, not faked.

**Verified by observation** (served :8077, headless Chromium, `/tmp/verify_panel.py`):
panel renders from the model (title + 4 layer rows); initial visibility matches
the model (boundary+trails `visible`, buildings+streams `none`); toggling
buildings+streams ON and boundary OFF flips MapLibre `visibility` accordingly;
**0 console errors**. Pixels confirm: boundary outline disappears, streams flood
in. Shots: `brain/output/playwright_panel_rebuild_initial.png`,
`…_panel_rebuild_toggled.png`.

To look: `python3 -m http.server 8077` in `website/`, open
`http://localhost:8077/right_panel.html`.

## Owed / next

- **Schema unification — SHIPPED** (re-bake + unified editor; see the "Schema
  variability" section above and `brain/research/common_feature_schema.md`).
  Follow-ups: commit + decide `data/raw/` commit-vs-gitignore; clean
  strip-legacy-keys pass at swap; persist in-editor Name/Description edits.
- User directs feature #2 (one at a time).
- At swap time: port the proven model+renderer into `index.html`/`main.js`,
  retire the old patchwork paths, migrate verifiers, bump `VERSION`. NOT yet —
  the new view earns the swap feature by feature first.
- Throwaway `/tmp/verify_panel.py` becomes a durable verifier at swap time.


-----

## Swap-cleanup disposition (recorded 2026-06-06, Sprint 05 triage)

The rebuild SHIPPED and the live editor is now `panel.js` → `#aopPanelMount`
(`#editDock` hidden, `index.html`). **Owed debt, carried out of Sprint 05 scope
but tracked:** the swap left a *third* list engine (`panel.js`
`PANEL_MODEL`/`deriveItems`/`renderLeftPanel`) and a *second* highlight store
(`aop_panel_overrides_v1`, `highlight` in `EDITABLE_SERVED_KEYS`) running
concurrently with `main.js`. Two stores must not both write `highlight`.
Decision still owed: **(A)** finish the swap — retire the `main.js` list engines,
panel becomes the sole surface; or **(B)** route all panel stars through
`AOP_HOST_SET_HIGHLIGHT` so `main.js` stays the single store of record. See
`05_special_operation/_limiting_code_register.md` (the "third list engine /
second store" row) — flagged so it is not silently absorbed into the
universal-layer work.
