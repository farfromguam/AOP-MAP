# Sprint 05 — on-device (iOS PWA) smoke of the v52 universal-feature-layer refactor

TL;DR:
- Sprint 05 rewrote the editor's dispatch core (one dock spec axis, one
  `collectStarredDestinations` list engine, trails as a starrable destination, one
  `makeFlyButton`). All of it was validated headless by observation, but headless
  proves **logic + DOM**, not real iOS-PWA touch, GL rendering, or feel.
- This is the perennial "on-device feel owed" item, made concrete for the v52 build:
  one device session that taps through the changed surfaces and confirms nothing
  regressed on real hardware.

#aop #sprint #10_deferred #05_special_operation #editor #verify #on_device #pwa

-----

## Deferred because

On-device touch + GL behavior is unverifiable in the headless sandbox (no real
multi-touch, no device viewport/safe-areas, basemap tiles blocked so MapLibre `load`
never fires). It needs the build running on an actual iOS PWA install. See the locked
known-good layout snapshot `spinup/working_pwa_css.md` to diff against if anything looks
off.

## Precondition (the git gate)

The sprint-05 work is **uncommitted** (v51→v52). Commit + the v52 bump are the user's
git gate (`ai_rules/no_commits.md`). Run this smoke against the committed/deployed v52
build on the phone.

## What to tap through (each is a sprint-05 change)

- **Edit dock (card 02):** select a drawn POI → Category select + Duplicate + Delete
  feel right; select a building → read-only Status, no Duplicate/Delete (this overlaps
  `sprint05_buildings_dock_on_device.md` — the precise behavioral acceptance lives there;
  here it's just "does it feel right").
- **★ destination lists (card 06):** star a feature in the editor; confirm the SAME
  feature shows in both the left POI tab and the right ★ Visitor list (the converged
  one-collector path), and the POI tab still renders the rows it shipped (wholesale
  layers unchanged — the "start empty" flip is still DEFERRED, see `star_driven_poi_list.md`).
- **Trails starrable (card 05):** star a trail; confirm the trail row surfaces in the
  right ★ Visitor list (proven at the collector level headless; confirm the UI/touch).
- **Fly buttons (card 08):** tap the 🎯 fly button on a feature-list row, on the dock
  head, and on a ★ Visitor-list row — each flies the map to the feature (the third
  surface, `.vrow-fly`, is the only one not exercised live headless).
- **General:** no console errors, no layout regression vs `spinup/working_pwa_css.md`,
  presets still switch cleanly, scroll/safe-areas intact.

## Observable acceptance

- Every surface above behaves on a real iOS PWA install; layout matches the known-good
  snapshot; 0 console errors.

## Done when

A device pass confirms the v52 editor refactor feels right and nothing regressed on
hardware. Record the result here. Any regression that traces to a specific card reopens
THAT card (`05_special_operation/_done/…`), not this smoke card.
