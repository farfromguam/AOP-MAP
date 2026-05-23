# Feature List Panel — POI editor v2 + shared primitive

Add a generalized **feature list panel** to the viewer: one row per feature under a layer's right-panel row, with per-feature actions (visibility, fly-to, drag-to-move) opted into by the consuming layer. POI editor v2 is the first consumer (all three actions). Buildings and Cemeteries are the next two consumers (visibility + fly-to only). Region callouts and the AOP / Rock Warblers logos consume the drag side of the primitive when they land.

Promoted out of `../03_deferred/` on 2026-05-23. Scope broadened the same day (2026-05-23) from "POI list with drag" to "feature list panel" after a user direction that **buildings should be operable as a per-feature list under the layer row**, not as a filter expression. The same shape generalizes cleanly to cemeteries and any other small-named-feature layer.

#aop #tasks #02_edit #editor #poi #positioning #feature-list

-----

## Source

- `../01_mvp/poi_editor.md` — current editor (Status: DONE). Its Follow-ups section already lists "Select/move mode for committed features (today: delete + re-draw)" as the gap this card closes.
- `../01_mvp/buildings_layer.md` — buildings layer; 202 footprints, importer already tags `inside_aop` and emits `build_id` from FEMA `BUILD_ID`.
- `../01_mvp/cemeteries_layer.md` — cemeteries layer; 4 parcels, importer emits `parcel_id` from `Assessment_Data_58_ID`.
- `tasks.md` — dump lines: "we need a editor for points of intrest", "our region circle callouts need to be positionable", "add aop logo / add rock warblers logo".
- `_readme.md` — Buckets B (region callouts), F (logos), G (POI editor v2) all consume positioning. Buildings (Bucket E) and Cemeteries also consume the list / visibility side.
- User direction (2026-05-23):
  - On POIs: *"poi editor needs a list of all pois on the right. selecting one allows us to find it and move it. same kinda move as the map region info. and same kinda move as future logos on map."*
  - On buildings: *"I kinda figured that we may have a list of all buildings on the right under the building layer and we could turn them on or off based on need."*
  - On cemeteries: *"I really only care about cemeteries in the park. there are extra."*
  - On in-park buildings: *"I really only got the houses for the pavillion location."* (1010 Ellis Cove Road, plus the three other in-park footprints at 1033 / 665 / 880.)
  - Confirmed in the same thread: yes to per-feature list shape for buildings (in-park 4 named, others collapsed bulk), cemeteries (4 rows, Ellis pre-ticked), and promoting the primitive to be shared.

## What this card builds

A **feature list panel** that:

1. Drops under any layer's right-panel row as a nested list.
2. Renders one row per feature in that layer, keyed by the layer's stable feature ID (`build_id`, `parcel_id`, POI uuid, etc.).
3. Each row exposes a configurable set of per-feature actions:
   - 👁 **visibility** — checkbox that toggles whether the feature draws. Persisted to `aop_feature_visibility_v1` localStorage.
   - 🎯 **fly-to** — click row body flies the camera to the feature and flashes it.
   - ✋ **drag-to-move** — long-press on row enters move mode; drag on the map; commits to the feature's geometry store. Persisted to whatever store the feature already uses (`localStorage` for POIs; per-layer override store for callouts and logos).
4. Supports **grouped sub-lists** — a layer can declare groups (e.g. buildings → `In park` / `Other in 9-patch`) so a 200-row layer is operable on mobile.
5. Supports **bulk row actions** — a collapsed group exposes one bulk-visibility toggle that flips every feature inside.

Each consumer wires only the actions it needs. POIs use all three; buildings + cemeteries use visibility + fly-to; callouts use visibility + drag; logos use drag.

## Scope

- In:
  - The shared component (one module exposing `(layerSpec) → DOM node + state-bound paint filter`).
  - First three consumers: **POIs** (the original card), **Buildings** (grouped), **Cemeteries** (flat).
  - Per-feature visibility persisted across reload.
  - Region callouts and on-map logos as later drag-only consumers.
- Out:
  - Vertex-level edit on polygons / lines. Whole-feature move only.
  - PostGIS write-back (still a follow-up on `../01_mvp/poi_editor.md`).
  - Reordering or grouping inside a single flat list. Group structure is per-consumer, declared in the layer spec.
  - Per-feature visibility on high-count layers (roads, water, contours, land cover, OSM). Cut line is ~30 named features per layer; over that, keep the layer-level toggle only.

## State

Two localStorage keys, orthogonal:

- `aop_layer_policy_v1` — tier per *layer* (always / sometimes / never default-on). Owned by the views-and-defaults card; not introduced here.
- `aop_feature_visibility_v1` — per-feature visibility, keyed `<layer_id> → { <feature_id>: boolean }`. Introduced here.

The layer toggle stays the master switch. If the layer is off, no features draw regardless of per-feature ticks. Per-feature ticks act as a sub-filter when the layer is on, applied as a MapLibre paint filter (`["in", ["get", "<id_field>"], ["literal", [...visible_ids]]]`).

## Decisions

### 1. One shared component, or per-consumer handlers?

**Decided:** One shared component. Confirmed by the 2026-05-23 user direction that POIs, buildings, cemeteries, callouts, and logos should all read and operate the same way.

### 2. Per-feature visibility on which layers?

**Decided:** Layers with ≤ ~30 named features. Buildings (202) qualifies only because the 198 outside-park rows collapse to one bulk row, leaving an operable list of ~5 entries.

### 3. Where does the list panel live?

**Decided:** Nested **under the layer's existing right-panel row**, not in a separate POI-only section. Same chrome as the inline layer editor that already opens under a layer row. Default-collapsed; click the row header to expand.

### 4. Mobile interaction for drag-to-move?

**Decided:** Long-press on the list row to enter "move mode," then drag on the map. Tap elsewhere to commit. Same staged enter-move pattern as proposed in the original card.

### 5. Fly-to — fly + popup, or fly + flash?

**Decided:** Fly + flash, no popup. Event-schedule jumps already use fly + flash + popup; this is a different intent (operating the list, not inspecting one feature). Reduces popup noise.

## Per-consumer wiring

### POIs (drawn POIs layer)

- All three actions: visibility, fly-to, drag-to-move.
- Source: `localStorage` (`aop_editor_features_v1` or current key) — the feature store the editor already uses.
- Key: existing POI uuid.
- List shape: flat, sorted by category then name.

### Buildings (FEMA USA Structures)

- Two actions: visibility, fly-to.
- Source: `website/data/aop_buildings.geojson`. Importer already tags `inside_aop` and emits `build_id`.
- Key: `build_id`.
- List shape: **grouped**.
  - `In park` (4 features): one row per footprint, pre-ticked. Address-keyed labels: `1010 Ellis Cove Rd — pavilion`, `1033 Ellis Cove Rd`, `665 Ellis Cove Rd`, `880 Ellis Cove Rd`.
  - `Other buildings in 9-patch` (198 features): collapsed, single bulk-toggle row, default **unchecked**. Expanding the group reveals one row per footprint so a neighbor's barn can be ticked individually if it earns its way onto the map.

### Cemeteries (TN Comptroller parcels)

- Two actions: visibility, fly-to.
- Source: `website/data/aop_cemeteries.geojson`. Importer emits `parcel_id`.
- Key: `parcel_id`.
- List shape: flat, 4 rows.
  - `Ellis Cemetery — 110 008.04` — **pre-ticked**, the AOP inholding.
  - `Gilliam Cemetery — 093 029.00` — unchecked.
  - `Bible Cemetery — 093 003.00` — unchecked.
  - `Tate Cemetery — 093 001.02` — unchecked.

### Visitor context callouts (later)

- Two actions: visibility, drag-to-move.
- Source: `website/data/aop_visitor_context_callouts.geojson` plus a position-override store.
- Closes the Bucket B item *"our region circle callouts need to be positionable"*.

### Logos (later)

- One action: drag-to-move.
- The Bucket F card builds the logo layer; logos consume the drag side of this primitive once they exist.

## Acceptance

- [ ] Shared component renders a feature list under any consumer layer row.
- [ ] Per-feature visibility persists across reload (`aop_feature_visibility_v1`).
- [ ] Buildings: 4 in-park rows pre-ticked, 198 others collapsed with bulk default off. Toggling a row updates the MapLibre paint filter immediately.
- [ ] Cemeteries: 4 rows with Ellis pre-ticked. Toggling updates paint.
- [ ] POIs: list populates, select-from-row flies, drag persists, reload preserves position.
- [ ] At least one second drag-consumer (region callouts) wired to prove the primitive is reusable on the drag side too.
- [ ] Mobile: long-press → drag → commit works on touch for drag-enabled consumers.
- [ ] Playwright verifier covers list render, visibility toggle, fly, drag, persistence (extends `playwright_verify_buildings.py`, `playwright_verify_cemeteries.py`, `playwright_verify_poi_editor.py`).

## Verification

- Open the viewer; expand Buildings in the right panel → confirm 4 in-park rows and a collapsed bulk row for the 198 others.
- Untick `1033 Ellis Cove Rd` → that footprint disappears from the map; reload → still hidden.
- Expand Cemeteries → confirm only Ellis draws; tick Gilliam → it appears.
- POI list populates, selecting a row flies and flashes, dragging persists.
- Region callouts (later): same drag interaction; persists in callout-override store.

## Related work

- `../01_mvp/poi_editor.md` — predecessor; this card closes its "select/move committed features" follow-up.
- `../01_mvp/buildings_layer.md` — extended in place once this lands (drops the "make buildings default-on" item once the per-feature list is operable).
- `../01_mvp/cemeteries_layer.md` — extended in place once this lands.
- `../01_mvp/visitor_context_callouts.md` — picks up the drag side of the primitive for region callouts.
- `02_edit/views_and_defaults.md` (TBD) — owns the layer-tier policy that decides which layers come up default-on. Per-feature visibility lives here; layer-default tier lives there.
