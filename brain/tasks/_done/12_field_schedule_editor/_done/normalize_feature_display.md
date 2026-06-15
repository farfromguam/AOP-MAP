# Normalize feature display — one text strategy for all data

User's call (2026-06-13), after seeing the editor preview couldn't match the map for some layers:
*"there should not [be] per-layer display rules — if there are it's an artifact of development. we need to
find and normalise. only one text concatenation strategy for all data."*

This card finds every per-layer display rule and replaces it with ONE branch-free strategy used by both the
reader view and the editors.

#aop #sprint12 #normalize #display #convergence #reader-view

-----

## The inventory (what "find" turned up)

Two layers to "how a feature reads when active on the map":

1. **Renderer — already uniform.** One function, `poiPopupHtml(row)` (`main.js:1339`): title → blurb (or
   "Info needed — revisit" placeholder) → `Kind · Status · Source · Caveat` meta list. (Schedule sessions
   use a separate `sessionPopupHtml` — a different surface, out of scope.)

2. **Field derivation — SIX per-layer rules** in the `FEATURE_LIST_LAYERS` registry (`main.js:2187`), each a
   `listRow(feature)` that maps props → the row. The shape is uniform; the rules are not:

   | layer | kind from | blurb from | status | source |
   |---|---|---|---|---|
   | cemeteries (2232) | `cemetery_type` | `description` | **const `'parcel record'`** | **const `'TN Comptroller parcels'`** |
   | buildings (2310) | `primary_occupancy` | `description` | `confidence` | `footprint_source` |
   | editorPois/drawn (2446) | `category` | `notes` | **const `'user-drawn'`** | **const `'editor — this browser'`** |
   | visitor (2635) | `kind` (`_`→space) | `description \|\| services` | **const `'planning callout'`** | **const `'AOP / RiderPlanet…'`** |
   | brand logos (2764) | **const `'brand logo'`** | — | **const `'brand'`** | **const `'editor — brand logos'`** |
   | trails (2903) | `'trail · '+difficulty` | `description` | `status \|\| 'observed'` | `source \|\| 'aop_trail_network.geojson'` |

## The key finding (why the hard-codes are an artifact)

Ran the served data through the new strategy (`node` on `feature_display.js`):

- **The data often already carries the real field, and main.js overrides it with a worse constant.**
  `aop_cemeteries.geojson`'s first feature carries `source` = *"Tennessee Comptroller of the Treasury —
  Marion County parcels (TN_County_Parcel_Map FeatureServer layer 35)"* and `status` = "raw context" and a
  full `revisit_note` — but `main.js` hard-codes Source = "TN Comptroller parcels", Status = "parcel record".
  Reading the feature's own field is strictly better and more honest.
- **Some served features lack the field**, so main.js injects a default: `publish.geojson` trails have no
  `source` and use `difficulty` (not `kind`). Normalizing means the **bake writes these fields onto the data**
  uniformly, so the one strategy has real data to read.

## The target

- **One branch-free strategy** — `featureDisplay(props)`: every field reads the SAME fallback chain for ALL
  data (no per-layer switch). **Shipped: `website/js/feature_display.js`** (`featureDisplay` + the one
  `popupHtml` renderer + `esc`). Loaded by both surfaces via `<script>`; attaches `window.AOPFeatureDisplay`.
- **Display values live on the feature (baked), not in code.** Where a layer injected a constant, that value
  becomes a baked property (or the feature's existing field wins).
- Zero per-layer display branches remain in `main.js`.

## Slices

- **S1 — shared strategy + editor proof. ✅ DONE (2026-06-13).** `js/feature_display.js` is the one strategy;
  the editor preview now calls it, not a local copy. 4/4 Playwright PASS, 0 errors, node-checked.
- **S2 — bake the uniform display fields. ✅ NOT NEEDED (verified 2026-06-13).** Investigation found the
  **data is already CMFS-normalized**: every POI source file (`aop_cemeteries`, `aop_buildings`,
  `aop_trail_network`, `aop_visitor_context_callouts`, the editor seed) already carries real
  `status`/`source`/`kind`/`description` on every feature. The per-layer constants in `main.js` were PURE
  artifacts overriding good data — no bake required. (Verified by dumping every served file's fields + the
  real values: cemetery source = the full Comptroller string, trail source = `sfwda_trace_edited`, etc.)
- **S3 — refactor `main.js` to the one strategy. ✅ DONE + VERIFIED (2026-06-13).** All 6 per-layer `listRow`
  derivations now call `window.AOPFeatureDisplay.featureDisplay(props)` (only structural `id`/`popupCoord`
  stay per-layer); `poiPopupHtml` delegates to `window.AOPFeatureDisplay.popupHtml`; `feature_display.js`
  loads before `main.js` in `index.html` and is precached in `sw.js` SHELL_ASSETS. **Zero per-layer display
  constants remain** (grep clean). Verified by observation: viewer loads 0 console/page errors; live Pavilion
  popup renders via the shared renderer with real values (Kind poi · Status draft · Source editor
  (first-party)); the shipped `window.AOPFeatureDisplay` run in the live page on real cemetery/trail/visitor/
  building features now shows their REAL provenance instead of the constants (see table below).
- **S4 — exact by construction. ✅** Both surfaces call the same module over the same data, so the editor
  preview == the map popup. (Editor verified round-2; viewer verified S3.)

### What S3 intentionally changed (richer/real, nothing lost — relocated to the data)

| layer | was (constant) | now (the feature's own field) |
|---|---|---|
| cemetery | source "TN Comptroller parcels", status "parcel record" | source = full Comptroller string, status "raw context" |
| trail | source "aop_trail_network.geojson", status "observed", kind "trail · {difficulty}" | source "sfwda_trace_edited", status "hand-edited…", kind "trail" (difficulty still a field) |
| building | status confidence, source footprint_source | status/source (the canonical fields) |
| brand | "brand"/"editor — brand logos" | status "decorative", source "Adventure Off Road Park" |
| drawn | status "user-drawn", source "editor — this browser" | the feature's own status/source (blank until filled) |

Two per-layer placeholders also dropped (they were display rules): trails' "Name / description owed…" owed-
message, and the layer-specific empty-name fallbacks ("Cemetery"/"Building"/"Logo") → uniform "(unnamed)".

## Acceptance

[x] S1: one strategy module exists, is branch-free, and the editor uses it (not a copy). 4/4 verified.
[x] S2: not needed — served data already carries the fields (verified); the artifact was display-code only.
[x] S3: `main.js` has zero per-layer display rules (grep clean); popups verified by observation; node OK.
[x] S4: editor preview == map popup (same module + same data, by construction).

## Owed / git gate

S3 touched the shipped viewer (`index.html`, `js/main.js`) + `sw.js` SHELL_ASSETS → the user's
**`VERSION`/`#appVersion` bump (v62→v63) + commit**. Done by the agent: SHELL_ASSETS now lists
`feature_display.js`; `VERSION`/`#appVersion` left at v62 for the user. UNCOMMITTED.

## Addendum 2026-06-14 — Kind/Status/Source off the user-facing surfaces (rides v92)

S3 made the popover read the feature's REAL Kind/Status/Source. The user now wants
those **off the visitor surfaces entirely** — they're provenance / dev-artifact
metadata, not visitor copy. Verbatim: *"we have kind and status as visible. we dont
need those in the poi list. we dont even need them in the world popovers. in the world
there is a third source. that also needs to go."* (POI list: drop Kind+Status. World
popover: drop Kind+Status **and** Source.)

Done — three surfaces, one coherent change:
- **`feature_display.js` `popupHtml`** (the ONE shared popover renderer, used by the
  reader AND the editors): dropped the `Kind`/`Status`/`Source` `<dt>/<dd>` lines.
  Only an author-facing `Caveat` may remain, and the `<dl class="poi-popup-meta">` is
  omitted entirely when there's nothing to show (no empty list). `featureDisplay()`
  still returns kind/status/source — the **editor's identify dock**
  (`data_editor_map.js` `row('Kind'/'Status'/'Source')`, `panel.js`) keeps them for
  editing; only the popover stops rendering them. One strategy preserved — no per-
  surface branch.
- **`viewer_core.js` `renderPoiTab`/`buildPoiGroups`** (reader POI list): dropped the
  kind/status `.poi-row-meta` chips and the `kind · status` subtitle fallback; rows
  show blurb → revisit note. Removed the now-unused `kind`/`status` from the local row
  object (no dead fields).
- **`main.js` `renderPoiTab`** (editor POI list, served by `data_sources.html`/
  `old_index.html`): same — dropped the kind/status chips and the `kind · source`
  subtitle fallback; **kept** the editorial "info needed — revisit" placeholder chip
  (not kind/status). Both subtitle and meta spans now append only when they have
  content, so removed chips leave no margin gaps.

Shell-asset change (`feature_display.js`, `viewer_core.js` are precached) but **rides
the existing uncommitted v90→v92 bump** — HEAD is v90, v92 unshipped, no second bump.

Verified by observation on `:8001` — `brain/output/verify_poi_no_kind_status_source.py`
**9/9 PASS**, 0 console errors: reader POI list has 0 kind/status chips and no
`x · y` subtitle; the world popover opens with no Kind/Status/Source `<dt>` (only a
`Caveat` line survives for a feature that carries one). Reader is live-verified; the
`main.js` editor copy is the parallel change (`node --check` clean, mirrors the
verified reader) served on the editor pages.
