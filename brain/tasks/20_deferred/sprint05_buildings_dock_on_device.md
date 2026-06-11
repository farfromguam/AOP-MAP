# Sprint 05 — buildings edit-dock on-device pixel check (the one headless-gated card-02 behavior)

TL;DR:
- Sprint 05 card 02 (`05_special_operation/_done/02_spec_fields_actions_persist_axis.md`)
  migrated the edit-dock per-layer behavior onto `FEATURE_LIST_LAYERS` spec strategies.
  The **editorPois** dock was proven live headless (Category select + Duplicate + Delete);
  the **buildings** dock is the ONE sprint-05 behavior that could not be observed in the
  sandbox, because the buildings layer registers into `featureListRuntime` only at
  MapLibre `load`, which never fires headless (basemap tiles blocked).
- This is a ~30-second on-device/on-desktop confirm, not a logic risk. The dispatch
  mechanism is identical to the editorPois dock proven live, and the buildings spec
  shape was confirmed by evaluating the real registry.

#aop #sprint #10_deferred #05_special_operation #editor #verify #on_device

-----

## Deferred because

Headless verification cannot boot the buildings feature list — `registerFeatureListLayer('buildings', …)`
runs inside the map-`load` handler, and `load` never fires when the external basemap
tiles are blocked (the sandbox / CI condition). So no buildings row surfaces, the dock
never opens for a building, and the live pixels can't be read. It needs a real booted
viewer with tiles. Everything else on card 02 is proven by observation.

## Precondition (the git gate)

The sprint-05 work is **uncommitted** (v51→v52). Commit + the v52 bump are the user's
git gate (`ai_rules/no_commits.md`). Do this check against the committed/deployed v52
build (or a local viewer with tiles reachable).

## What to check (live, with tiles loading)

1. Open the viewer, let the basemap load, open the right edit panel.
2. Expand the buildings group, select a building (e.g. **Front Office / 880 Ellis Cove
   Road** — a facility) so its edit dock opens.
3. Confirm the dock renders:
   - a **read-only Status** row (not an editable input),
   - **no Duplicate and no Delete** action (served layers omit those — only drawn POIs
     get them),
   - the name field editable; a name edit persists via `savePositionedFeature` +
     `refreshServedSource('buildings')` (survives reload).
4. For contrast, open a **drawn POI** dock and confirm it DOES show the Category select
   (`EDITOR_POI_CATEGORIES`) + Duplicate + Delete — the already-proven side, as a sanity anchor.

## Observable acceptance

- buildings dock: read-only Status, no Duplicate/Delete, name persists across reload.
- drawn-POI dock: Category select + Duplicate + Delete present.
- 0 console errors.

## Done when

Both docks render their correct per-layer shape on a real booted viewer and a buildings
name edit survives a reload. Record the result on this card (and clear the "live pixels
owed" note in `_done/02_spec_fields_actions_persist_axis.md`). If it renders wrong, that
is a real card-02 regression — reopen card 02, do not patch around it here.
