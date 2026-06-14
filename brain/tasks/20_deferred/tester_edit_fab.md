# Tester edit-FAB — the on-tester "Edit" affordance beside Locate

> **Deferred out of Sprint 13 (viewer extraction) on 2026-06-14**, when that
> sprint's slate (slices 1–8) closed to `../13_viewer_extraction/_done/`. This is
> the one named **future** item the sprint surfaced but did not build.

#aop #deferred #13_viewer_extraction #tester #editor #fab

-----

## What this is

The `?tester=1` surface (shipped in `../13_viewer_extraction/_done/viewer_locate_install_version.md`)
reserves a right:80px FAB slot and a `.tester` html class for an **edit FAB** that would sit to the
LEFT of the blue Locate FAB, so a field tester sees **Locate + Edit side by side** (per `brain/pages.md`).
The slot and the class are already in place; the button itself is not built.

## Deferred because

The edit FAB opens the editor, but **the editor has not been ported into the extracted read core.**
After the slice-7 swap, the read viewer is `index.html` (`viewer_core.js`); the editor still lives in
`website/js/panel.js` + `old_index.html` + the standalone field tools (`schedule_editor.html`,
`data_editor.html`) + QGIS. Wiring an edit FAB into the clean read core before the editor is ported would
either re-introduce the tangled editor into the surface the extraction just cleaned, or stand up a second
editor path — both against `editor_is_the_viewer` and the extraction's whole point.

## Unblock condition

The editor (or the slice of it the day-of tester needs) is ported into / reachable from the read core as
its own clean surface — then the FAB is a thin button that opens it, dropped into the reserved slot. Until
then this is a real future item, parked here so it is not lost.

## Related

- `../13_viewer_extraction/_done/viewer_locate_install_version.md` — the `?tester=1` surface + the
  reserved FAB slot + the `.tester` hook.
- `../13_viewer_extraction/_done/viewer_swap.md` — the swap that made the read viewer `index.html`.
- `brain/pages.md` — the page map where Locate + Edit show side by side on the tester surface.
- `../../ai_rules/editor_is_the_viewer.md` — V2 is V1 with more controls, not a fork.
