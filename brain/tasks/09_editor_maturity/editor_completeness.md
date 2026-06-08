# Editor completeness — every curated feature visible + editable on the right, DB-first

> **PLAN — COUNCIL-CLEARED (full six, 2026-06-08, 1 round + 1 Mason re-review).** Not yet executed.
> Receipt: `../../output/council/editor_completeness_plan_review_20260608.md`. The Mason andon (the host
> editor engine is live-but-CSS-hidden, not retired → restoring naively = a SECOND editor + twin-store
> desync) was folded into the corrected grounding + Slice 1 (consolidate to ONE engine + ONE store with a
> write-back bridge) + Fork #0. **NEXT (user's gates):** decide the forks (esp. Fork #0 — which editor
> survives), then commit-pause the plan, then ralph-loop the slices in a fresh session. The commit +
> any `sw.js`/`#appVersion` bump stay the user's.

Date: 2026-06-08
Trigger (user): *"I dont know why the editor was retired. this is a needed surface. put it in. make
sure everything is visible on the right side and editable. consult the council for a full robust plan.
No shortcuts. we are trying to mature the project and not maintain shortcuts or MVP code."*

> ## ✅ SLICE 1 — DONE (2026-06-08; CODE, UNCOMMITTED, v57→v58 bump PERFORMED, commit OWED)
> Drawn-POI editing restored as ONE editor + ONE store of record. **Shipped:** (main.js) 3 bridge hooks
> `AOP_HOST_SET_FEATURE_PROPS` / `_GEOM` / `AOP_HOST_DELETE_FEATURE` — pure delegation to the existing
> spec-routed host writers (`setFeatureProperty`/`deleteFeature` → editorPois `persistProperty`/
> `removeFeature` → `saveEditorPois`), fail-safe (try/catch → false, no throw). (panel.js) restored the
> **Drawn POIs** (`editorPois`) node with `hostKey:'editorPois'` + `hostEdit:true`; `commitChange` /
> `persistDelete` route to the bridge when `node.hostEdit` (before the OVERRIDES path, with `return` — no
> twin write). The retirement comment was annotated (restored, not deleted — Warden). Generic draw stays
> retired (Fork #1). **Verified by observation (`playwright_verify_drawn_poi_editor.py`, clean profile):**
> the panel has a Drawn POIs node; editing the name field THROUGH THE PANEL UI (expand → click item →
> edit field) lands in `aop_editor_pois_v1`; **NO twin-store leak** (`aop_panel_overrides_v1` carries no
> `editor-poi:` entry); survives reload; UI 🗑 Delete removes it from the one store; 0 console errors.
> Only the panel editor opens (host `buildEditDock` stays CSS-hidden in embedded — still the standalone
> editor, correct scoping; Mason CLEAR). No regression: `playwright_verify_data_groups_embed.py` updated
> to the new contract (8 sections incl Map editor, Drawn POIs present, generic draw gone) → PASS;
> `playwright_verify_starred_poi_flip.py` PASS. **Council done-review:** Mason CLEAR; Witness ANDON
> (red embed verifier + verifier didn't assert twin-store/UI-delete + not recorded) → all folded →
> re-review. **NEXT:** Slice 2 (reconcile the half-retirement — surface the create affordance), then
> Slice 3 (trailheads), Slice 5 (DB doors, gold slice 6). **OWED:** the commit (main.js + panel.js +
> sw.js + index.html + the new/updated verifiers + brain) with the v58 bump — the user's git gate.

-----

## Goal (one line)

The right panel is the single editing surface (`editor_is_the_viewer`): every **first-party / curated**
feature is **visible** as a node, **drillable** to its feature list, **editable** (rename / describe /
move / tag / ★ / delete), and **persisted to a store-of-record** (`core.features` via the DB door) —
never stranded in localStorage. Reference/imagery layers (FEMA raw, USGS, OSM, rasters) stay
visibility-only by design — you do not feature-edit someone else's dataset.

## Grounding — what is true today (observed 2026-06-08, not re-derived)

Panel model = `website/js/panel.js` `PANEL_MODEL.sections` (`:573`). Classified by editability:

| State | Nodes |
|---|---|
| **Editable** (feature list + inline editor via `refItems`) | aopTrails, boundaries, buildings, visitorContext, brandLogos, cemeteries, pubTrails |
| **Visibility-only, but SHOULD be editable (curated/first-party)** | **trailheads** (`:627`, no `items` — F7), **eventSchedule** (`:628`, no `items`) |
| **Visibility-only, correctly** (reference/imagery) | satellite, NAIP, lidar tiles, 9-patch, landcover×2, hillshade, contours, activityHotspots, water, roads, OSM×4, sfwda raster |
| **MISSING — retired** (`7cd51fa "v50 styles"`, 2026-06-05) | **Drawn POIs** (`editorPois` → `editor-poi` source), **Points/Lines/Polygons** generic draw (`userPoints`/`userLines`/`userPolys` → `userFeatures`) |

**⚠️ CORRECTED GROUNDING (council R1 — Mason andon, folded). There are TWO live editor engines, not
one.** What `7cd51fa` retired was only the panel-side *node*, NOT the host's drawn-POI editor:

1. **Panel engine** (`panel.js`) — `refItems(source,{…})` (`:569`) builds the editable feature list;
   the ONE inline editor frame ("ONE editor frame for every feature" `:1334`) does
   rename/describe/move/tag/★/delete; edits persist to `aop_panel_overrides_v1` (`OVERRIDES` —
   created/deleted/edits, replayed at boot by `applyStoredOverrides` `:167`); DB door
   `mvp/scripts/apply_panel_overrides_to_core.py` (`created[]` → `core.features`).
2. **Host engine** (`main.js`) — STILL LIVE, just `display:none` in embedded mode
   (`css/panel-embed.css:271-273` hides `#editorTree` + `#editDock`). It is a *full* second editor:
   `buildEditorTree` (`:612`/`:3248`), `buildEditDock` tabbed editor (`:4538`), `setFeatureProperty`
   (`:4841`), the `#placePoiBtn`/`setDrawMode` draw path (`:9872`/`:9901`), persisting drawn POIs to the
   `editorPois` **array** → `aop_editor_pois_v1` (`saveEditorPois`), which feeds the `editor-poi` map
   source via `refreshEditorSource` (`:6532`).

**So drawn POIs already have a store of record (`aop_editor_pois_v1`, the host array) and a working
editor (the host's `buildEditDock`) — it is just CSS-hidden.** That changes the work: restoring
drawn-POI editing is NOT "re-add a panel node and wire `refItems`." Done naively that stands up a
SECOND engine editing one feature class, plus a TWIN-STORE desync (panel `OVERRIDES` vs host
`aop_editor_pois_v1`, both writing the one `editor-poi` source — the F6 bug class). The real work is
**consolidate to ONE engine + ONE store of record** (Slice 1).

The half-retirement (the live inconsistency): the create affordance still exists — the host
`#placePoiBtn` (`index.html:478`, wired `main.js:271`/`:10461`, today inside the hidden legacy block)
and the per-bucket inline "+ add" create rows — and the help text still says *"the new feature lands in
Drawn POIs… Click the ▸ chevron on any row to rename, edit, move, tag, add notes"* (`index.html:450`) —
but the panel Drawn POIs node was deleted. So a drawn+starred POI still renders, yet has **no panel
editing home**, and (spike audit F2) a drawn POI that never goes through the panel's `created[]` export
**never reaches `core.features` and is lost on a different browser / at publish**.

## Slices (each: tile-independent acceptance, verify by observation, record on green)

### Slice 1 — Restore drawn-POI editing as ONE engine + ONE store of record  [PRIMARY — the user's ask]
Drawn-POI editing must come back as a **single** editor over a **single** store of record — not a
second engine. Two sub-steps, in order:

- **1a — Decide & consolidate the engine (the core fork, FORK #0 below).** Today the host's
  `buildEditDock` edits drawn POIs (into the `aop_editor_pois_v1` array) but is CSS-hidden in embedded
  mode; the panel's inline frame is the visible editor for every *other* layer. *Rec: the **panel**
  inline frame is the one editor (`editor_is_the_viewer` + the one-model-panel direction), and the
  host-side `buildEditDock`/bucket-tree drawn-POI editing path is **retired** so exactly one engine edits
  `editor-poi`.* Whatever survives, the OTHER must be removed in the same slice — restoring without
  retiring is the C2/C6 second-editor violation the council caught.
- **1b — Re-register the panel `editorPois` node (the retired `items:{ source:'editor-poi', … }`,
  recoverable from `7cd51fa^:website/js/panel.js`) over the one store.** The store of record stays the
  host array `aop_editor_pois_v1` (the left POI list + map already read it). The panel must **write back
  into that host array**, not only seed-read from it: `seedLoadedFromHost` (`panel.js:1893`) only READS
  the host source into `LOADED` — it does not push panel edits back, so a panel edit through `OVERRIDES`
  + `setData('editor-poi')` would be overwritten by the host's next `refreshEditorSource` and double-
  applied on reload (the twin-store desync, F6). So this slice adds the missing write-back bridge: new
  `window.AOP_HOST_*` hooks for drawn-POI **property / geometry / delete** (mirroring the existing
  `AOP_HOST_SET_HIGHLIGHT` ★ bridge), so a panel edit lands in the host `editorPois` array → `saveEditorPois`
  → one store. The ★ likewise routes to the host store (today `hostHighlight` returns false for
  `isUserFeature`, `panel.js:831` — that exclusion is revisited so a drawn-POI ★ persists in the one store).

**Acceptance (tile-independent, clean profile, inject a drawn POI):** a drawn POI ("Launchpad") is
visible + editable in the right panel; rename/move/★/delete each persist to `aop_editor_pois_v1` and
survive reload; it does **NOT** double-show (no second editor surface, no twin-store double-apply); the
host `buildEditDock` drawn-POI path is gone (grep + observe only one editor opens); 0 console errors.

### Slice 2 — Reconcile the half-retirement
Make the live surface self-consistent: the create affordance (`#placePoiBtn`, `main.js:271`, currently in
the hidden legacy block — surface it or route the per-bucket inline "+ add") lands a new POI in the
restored editor over the one store; the `index.html:450` help text is true again. **Acceptance:** create a
POI → it appears in the restored editor, editable immediately, persisted to `aop_editor_pois_v1`; no stale
instructions.

### Slice 3 — Spec-complete the curated visibility-only layers (F7)
**trailheads** gets an editable feature list (it is a *publishable* layer awaiting data — it must be
authorable). Use `refItems('publish-trailheads', {...})` with **key/label fallbacks** exactly like the
sibling silver nodes (`p.name || 'trailhead'`, `panel.js:606-625`) so an unnamed/empty trailhead renders
a row rather than keying to `undefined` (Mason note). Audit eventSchedule: event anchors are resolved
from `aop_event_schedule.json` + tags; decide whether they are editable HERE or remain owned by the
Events-tab/schedule surface (**FORK #2**). Any registered-but-spec-less layer that should be a destination
gets a `listRow`/`highlightable` with R13 safe defaults (no registration-time throw — Mason audit note).
**Acceptance:** trailheads drills to an editable list; a trailhead can be authored/renamed/moved; an
unnamed trailhead still renders a row.

### Slice 4 — Generic draw (Points / Lines / Polygons)  [FORK #1 — see below]
Either restore the three generic-draw nodes (from-scratch geometry authoring) OR confirm the per-layer
"+ add" controls suffice and formally retire the generic group (fix the docs). **Mason note (DOA
warning):** the retired generic-draw nodes were backed by the `userFeatures` source, which is **empty in
embedded mode** — the host owns draws via `editorPois`/`editor-poi`, and the panel only adds the
`userFeatures` source in standalone mode (`panel.js:2091-2094`, `main.js:693-694` "userFeatures is
empty"). So the *restore* arm is **dead-on-arrival** unless `userFeatures` is first wired to the host;
the *retire-cleanly* arm (per-layer "+ add" + fix docs) is the low-risk path. Decide the fork with that
known.
**Acceptance:** the user can author a new geometry of each type into a real (non-empty) source, and it
persists + is editable.

### Slice 5 — Persistence is DB-first (the maturity bar — gold slice 6, REFERENCED not duplicated)
Restoring an editor that writes only localStorage would be exactly the MVP shortcut the user rejects.
So Slices 1–4 are not "done" until the edited features have a store-of-record:
- **Drawn-POI DB door (F2)** — `06_going_gold/gold_migration.md` slice 6. A drawn POI persists to
  `core.features (layer='poi')` (reuse `apply_panel_overrides_to_core.py`'s upsert-fold-archive, no
  allowlist — Mason audit note). **This sprint coordinates/sequences it; gold slice 6 owns the card.**
- **Geometry/icon_size DB door (F1)** — extend `apply_positioned_features_to_core.py` so a move/resize
  persists to core. Same ownership.
**Acceptance:** draw+star a POI → apply → bake → it publishes; a browser reset does NOT lose it; move a
building → apply → bake → the new position is in the served file from the DB.

## ✅ FORK RESOLUTIONS (user, 2026-06-08)

- **Fork #0 — engine:** **Panel inline frame survives.** Retire the hidden host `buildEditDock`
  drawn-POI editing path; host array `aop_editor_pois_v1` stays the single store of record; panel edits
  write back into it via the new `AOP_HOST_*` bridge.
- **Fork #1 — generic draw:** retire the generic group cleanly (the restore arm is DOA in embedded).
- **Fork #2 — event anchors:** stay schedule-owned (NOT editable in the panel).
- **Fork #3 — home:** own Sprint 09 (this dir); gold slice 6 keeps the DB axis.
- **Fork #4 — DB-first:** interleave per slice (persist DB-first, not localStorage-then-migrate).
- **Execution:** the user accepted all recs and directed execute-now (ralph-loop, council done-review per
  slice). The plan commit + any `sw.js`/`#appVersion` bump stay the user's git gate.

## The forks (user decisions — do NOT pick unilaterally)

0. **Which editor survives (Slice 1a — the core architectural fork, surfaced by the Mason andon).**
   Two live engines edit drawn POIs: the host `buildEditDock` (CSS-hidden) and the panel inline frame.
   Consolidate to one. *Rec: the **panel inline frame** survives (`editor_is_the_viewer` + the one-model
   panel is the deliberate direction), and the host-side `buildEditDock`/bucket-tree drawn-POI editing is
   retired — with the host array `aop_editor_pois_v1` kept as the single store of record that the panel
   writes back into.* This is the load-bearing decision; it sets how much code Slice 1 touches.
1. **Generic draw (Slice 4):** restore Points/Lines/Polygons from-scratch authoring, or rely on
   per-layer "+ add" and retire the generic group cleanly? *Rec: retire the generic group cleanly — its
   `userFeatures` source is empty in embedded mode (restore arm is DOA); per-layer "+ add" is the path.*
2. **Event anchors (Slice 3):** editable in the right panel, or owned by the Events-tab/schedule
   surface? *Rec: keep schedule editing in its own surface (the schedule JSON drives it); the panel
   shows event anchors visibility-only — do not split the schedule model across two editors.*
3. **Sprint home:** is this its own Sprint 09, or does it fold into gold slice 6 / `02_edit`?
   *Rec: own sprint for the UI-completeness axis; gold slice 6 keeps the DB-door axis — cross-linked,
   one planning surface each.* (Council to confirm — Quartermaster lens.)
4. **DB-first gating:** must each UI slice land WITH its DB door (Slice 5 interleaved), or can the UI
   restore first (localStorage) and the DB door follow? *Rec: interleave — "no shortcuts" means the
   restored editor persists DB-first, not localStorage-then-maybe-migrate.*

## Guardrails (inherited contracts — the council enforces)

- **C2/C6 — ONE engine.** Restore by RE-REGISTERING into one editor engine (`refItems` + the one inline
  frame) AND retire the redundant other (Slice 1a). No second editor, no new editor `*.html`, no `class`.
- **C5/R13** — new specs use safe-default `listRow`/`highlightable`; never a registration-time throw or
  a row-dropping filter.
- **C3 / DB-first** — localStorage is a working buffer; `core.features` is the store of record. No new
  localStorage-only edit path. One store of record per feature class (no twin stores — F6).
- **`editor_is_the_viewer`** — the right panel is THE editor; do not stand up a second editing surface.
- **Reuse** — recover the retired node text from `7cd51fa^:website/js/panel.js` (NOT `git show 7cd51fa --
  …`, which shows an empty diff for that commit — Witness note); reuse the existing OVERRIDES/apply
  machinery and the gold DB doors. Do not re-invent.

## Execution-time notes (Warden — honor these when code lands)

- **Preserve the record, don't silently delete.** The `panel.js:690-697` "MAP EDITOR — RETIRED
  2026-06-05" comment is annotated ("restored 2026-06-08 per user — retirement reversed"), not deleted.
  The Slice C / prior decisions stay as history (`cards_not_gospel`).
- **The version bump is owed to the user.** Restoring a panel node touches shell assets → a
  `sw.js` VERSION + `#appVersion` bump is owed; **report it, the commit is the user's git gate** (do not
  commit). Each slice records what's owed.

## Out of scope (named, so it is not silently pulled in)

- Re-architecting identity resolution (F6 — gold slice 6, highest risk, last).
- Fresh-volume DB parity (F5), re-baking `publish.geojson` (F4) — gold/Retirement gaps, the user's git gate.
- Making reference/imagery layers feature-editable (they stay visibility-only by design).
