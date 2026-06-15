# Six-item viewer batch (2026-06-14)

TL;DR: one user drop of six fixes — trail label/search consistency, borderless
tree cover, medallion data tiers, a production data-tier alert, search/event
"active item" persistence, and placing the Pro-Line race at the firepit. All six
shipped on **v87** and **verified by observation** on `:8001` (13/13 + alert PASS,
0 console errors).

#aop #viewer #maturity #medallion #search #events #done

-----

## What the user asked (verbatim intent)

1. Trail 1 shows "1 Launchpad" on the map but only "Launchpad" in search — a
   label-only shortcut. "make the proper fix so its Number Name."
2. The tree cover has a border that shows the load-patching. "remove borders."
3. "rename all our data sources to bronze_* silver_* or gold_*. ellis cemetery
   made it from bronze to gold. no other cemeteries did. same with park buildings —
   only 5 made it. others did not."
4. "alert developer of any bronze or silver data making it to 'production'."
5. Search keeps a trail highlighted until "de-throned"; selecting an event makes
   it the active item; the selection stays highlighted for orientation.
6. "proline before the fire should be at the firepit poi. that should be tagged."

## What shipped

1. **Trail number-first display name (single source).** New `trailDisplayName(props)`
   in `viewer_core.js` → "1 Launchpad" / "15" (unnamed) / bare name. Stamped onto
   each trail as `display_name` at load; the label layer text-field reads
   `['get','display_name']` and the search index uses the same string (new `nameFor`
   arg on `indexFeatures`). The trail `name`/`trail_number` stay separate in the file
   so the Affinity trace re-import (which strips leading numbers) still round-trips —
   NOT baked into the name. Map label and search now read identically.
2. **Borderless tree cover.** Removed both landcover `-outline` LineString layers
   (the canopy-edge line read as a sage border on the tan base and exposed the grid
   patching) + their toggle-array/preset-paint refs + the now-unused
   `LANDCOVER_*_OUTLINE` consts. Fill stays solid (opacity 1, from the in-flight v87).
3. **Medallion data tiers.** Re-tiered every served file to bronze/silver/gold via
   `stamp_maturity.py` (file `_meta`) + new `set_feature_maturity.py` (per-feature for
   mixed files). gold=9, silver=2, bronze=11, delete=3 (delete kept as an orthogonal
   lifecycle flag). Decisions (AskUserQuestion): **full rename**, and **derived/reference
   layers that render in production (land cover, contours, water, roads) = gold**.
   Ellis Cemetery → gold (others bronze); 5 ORNL buildings → gold, Shower House → bronze.
   See `research/data_maturity_tiers.md`.
4. **Production data-tier alert.** `auditProductionTiers()` in `viewer_core.js` warns
   the developer (console.warn) when a production-rendered source carries bronze/silver
   data — currently Park buildings (Shower House bronze), Visitor context callouts
   (silver), Publishable layers (silver). Per [[no-limiting-code-mvp]] it NEVER
   hides/filters; it only surfaces "production should be gold."
5. **One persistent "active item."** `gotoMatch` (search) now clears
   `activeEventSessionId` so a search de-thrones an active event row, and the event
   popup-close no longer clears the selection — the chosen event/trail stays
   highlighted (shared `search-highlight` + `pulseHighlight` hold) until the next
   selection de-thrones it.
6. **Pro-Line at the firepit.** `aop_event_schedule.json`: `sat-proline-fire`
   `location_tag` `#pavilion`→`#firepit`, and a new baked `#firepit` location (firepit
   waypoint coords). The Firepit waypoint in `aop_waypoints_traced.geojson` carries
   `location_tag:"#firepit"`.

   **Follow-up (2026-06-14): s'mores moved to the firepit too.** Item 6 tagged the
   PRO Line *race* to the firepit but left both **"Fire + s'mores"** sessions
   (`fri-fire`, `sat-fire`) at `#pavilion` — so the firepit POI showed the obstacle
   race but not the campfire. User: *"Smores should be at the firepit. what happened?"*
   Source (`brain/import/TBI.copy`) is explicit — after the PRO Line challenge they
   *"head to the fire pit for some smores"* — so both s'mores sessions are now
   `location_tag` `#pavilion`→`#firepit`. Data-only change; no JS touched. The
   concurrent `clear-search-defocus` session's `v90→v91` bump already re-keys
   `DATA_CACHE`, so this rides that bump (no second version bump). Verified by
   observation on `:8001` — `brain/output/verify_smores_at_firepit.py` **12/12 PASS**,
   0 console errors (both s'mores sessions resolve to firepit coords, firepit anchor
   renders, PRO Line regression holds, the Sat s'mores calendar row drives to the
   firepit + becomes the active item).

## Verified by observation (`:8001`, Playwright)

- `brain/output/verify_label_border_persist_firepit.py` → **13/13 PASS**, 0 console
  errors (T1 label+search "1 Launchpad"; T2 outline layers gone + fill opacity 1;
  T5 event active + search de-thrones it, highlight holds; T6 anchor at firepit
  coords). Screenshot `brain/output/verify_treecover_borderless.png` (borderless sage).
- `brain/output/verify_production_tier_alert.py` → **PASS**: alert fires for the 3
  bronze/silver production layers, stays quiet on all gold, 0 console errors.
- Harness note: programmatic camera-move `evaluate` (`jumpTo`/`flyTo`) deadlocks the
  headless swiftshader build — verifiers drive via the app's own handlers (DOM click +
  real keydown) and avoid camera moves; the verdict prints before `browser.close()`.

## Owed / deferred (reported, not done)

- **Editor (`panel.js`) medallion re-group.** Chip renderer learned `bronze`, but the
  editor's group TREE still uses the pre-medallion layout (buildings node now gold but
  sits in Silver; SFWDA node now bronze; no Bronze section). Full re-group deferred —
  semi-retired surface, not blocking. See `research/data_maturity_tiers.md`.
- The 10 new user-traced trails still need names (carried from the trace card).

## Git

The six items were **committed by the user as HEAD `91a017e` ("medallion rename")**
(v87). No agent touched git.

## Addendum — physical file rename + data-editor re-group (2026-06-14, v88)

After committing the six items, the user asked to actually rename the files (the tier
*values* were done; the *filenames* were not) and re-group the data editor page:
*"rename and re-group. dont touch treecover."*

- **Files renamed to `<tier>_<name>.geojson`** (25 files): `gold_aop_trail_network`,
  `bronze_aop_cemeteries`, `silver_publish`, `delete_aop_synthetic_activity_*`, etc.
  New `mvp/scripts/rename_data_medallion.py` (imports `stamp_maturity.MATURITY`)
  renames + sweeps every runtime reference (viewer_core, main, panel, data_editor_map,
  sw, old_index, `_schema.json`, `_data_manifest.json`). The brain's prior "physical
  renames deferred — little gain" note (`research/data_maturity_tiers.md`) is overridden
  by this user directive.
- **Re-group:** `data_editor_map.js` groups the data-editor file picker into `<optgroup>`
  Gold / Silver / Bronze / Delete (read from the filename prefix). This is "our data
  editor page" — `data_editor.html` lists sources by filename, so the rename is what
  surfaces the medallion there.
- **Tree cover NOT touched** (per the directive) — the concurrent landcover session's
  60% non-park opacity + `fill-antialias:false` are intact.
- `sw.js`/`#appVersion` **v87→v88**.
- **Verified by observation** (`:8001`, 0 console errors): `verify_label_border_persist_firepit.py`
  13/13, `verify_production_tier_alert.py` PASS (alert + production viewer survive the
  rename), `verify_data_editor_regroup.py` PASS (4 tier groups, prefixed files).
- **Owed (pipeline consistency):** the ~50 `mvp/scripts` (importers/exporters/bakers +
  ~30 verifiers) still use canonical names; `rename_data_medallion.py` is the documented
  FINAL pipeline step — re-run after any bake (like `stamp_maturity.py`). Rewiring the
  generators to emit prefixed names directly is Docker-gated, deferred.
- **COMMINGLED + git gate:** working tree commingles this rename with the concurrent
  landcover-opacity session (tree cover v88). Both UNCOMMITTED; the landcover session's
  `.council-cleared` is now stale (my rename changed the diff). The user separates at the
  gate. Coord: `handoff/coord/six-item-viewer-batch.md`.

## Addendum — clearing the search bar de-thrones the held highlight (2026-06-14, v91)

Item 5 made one selection HOLD until the next selection replaced it — but nothing
ever *removed* the highlight. The user: *"the app holds the highlight until something
else takes it. -- if the searchbar is cleared then the highlighted item also needs to
be cleared. this defocuses it as well."*

- **New `clearActiveSelection()` in `viewer_core.js`** (right after `gotoMatch`): the
  ONE path that removes the held highlight — cancels any in-flight `pulseRAF`, empties
  the `search-highlight` source, and de-thrones `activeEventSessionId` (re-rendering the
  schedule so the active calendar row drops). Every other path still only *replaces* the
  highlight; this is the only one that clears it.
- **Wired into both clear paths.** The `input` listener calls it when the field goes
  empty (backspace / select-all-delete); the `Escape` keydown calls it alongside the
  existing value-clear + `blur()`. No blur on the typing path (yanking focus mid-edit
  would be hostile) — Escape already defocuses the input.
- **Shared `dethroneActiveEvent()` (no copy).** The de-throne block (`activeEventSessionId
  = null` + `renderEventSchedule`) was extracted into one helper called by BOTH `gotoMatch`
  (search de-thrones an active event) and `clearActiveSelection`, rather than copied — the
  `activeEventSessionId = null` assignment now lives once. (The inverse SET path in
  `gotoEventSession` is left untouched — a separate concern, not the flagged duplication.)
- **Verified by observation** (`:8001`, `brain/output/verify_search_clear_dethrone.py`):
  **8/8 PASS**, 0 console errors — search sets a highlight, backspace-to-empty clears it
  (1→0), and Escape empties the input + clears the highlight + de-thrones the active event
  row. Regression: `verify_label_border_persist_firepit.py` still **13/13** (the hold
  model is intact). Re-verified after the dedup extraction (both still pass).
  `sw.js`/`#appVersion` **v90→v91**. UNCOMMITTED (user's git gate).
- **Council:** core-three over the scoped diff — Witness **clear** (re-ran both verifiers
  live, 8/8 + 13/13), Warden **clear** (on the farm, git gate untouched), Quartermaster
  **andon → resolved clear** (flagged the de-throne copy; fixed by the shared helper above,
  re-reviewed clear). Receipt: `brain/output/council/search_clear_dethrone_20260614.md`.
