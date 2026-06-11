# Brand Assets + Permission Posture

> **Deferred — Sprint 04 triage (2026-05-30).** Nothing on this card is done.
> **Deferred because** the load-bearing item is a user/external decision: the
> brand-use permission posture must be settled to resolve the default-on conflict
> (the live viewer currently ships `showBrandLogos: true` while this card's
> original text said keep it off until permission lands). The asset cleanup
> (downsize rasters, transparent Rock Warblers PNG, normalize the size-slider
> range) can follow once the posture is fixed.

Sprint 03 defaulted brand logos off until reuse permission is confirmed.

Sprint 04 should clean the assets themselves and keep the permission posture
visible.

#aop #04_event_app #branding #assets #permission

-----

## Source

- `../03_event_app/_done/sprint_02_critique_followups.md`
- `../03_event_app/misc_3.md` (item 18, 2026-05-27 triage)
- `../02_edit/_done/branding.md`
- `../../spinup/add_image_to_viewer.md`

## Work

- [ ] Downsize raster brand assets in `website/assets/branding/`.
- [ ] After downsizing, normalize the brand-logo size slider range away from the tiny `0.02-0.20` workaround and toward a normal icon range.
- [ ] Replace the Rock Warblers JPEG with transparent PNG or SVG artwork so the white card around the bird art drops out.
- [ ] **Reconcile default-on conflict.** 2026-05-27 misc_3.md item 18 flipped `showBrandLogos: true` in Park / Topo / Trace presets and `playwright_verify_brand_logos.py` was updated to assert the default-on policy. This card's prior text said "Keep default-off until permission confirmed." Either: (a) confirm permission is now in hand and retire the off-by-default safeguard here, or (b) roll back the preset toggles + verifier and re-route item 18 as "pending permission." Until reconciled the live viewer ships default-on.
- [ ] When permission lands (if it has not already), update the branding card and default-layer policy together.
- [ ] Keep `spinup/add_image_to_viewer.md` aligned with any asset-size or format decision.

## Acceptance

- [ ] Brand-logo assets are web-sized and visually clean.
- [ ] Slider range makes sense for the shipped asset dimensions.
- [ ] Permission/default-on posture is documented in the branding card and viewer catalog.
- [ ] Permission posture and live default state agree — no quiet drift between this card and the preset toggles.
