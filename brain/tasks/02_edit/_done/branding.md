# Sprint 02 Branding

Bucket F from the Sprint 02 triage: add the AOP logo and Rock Warblers logo.

## Status

Shipped on-map (2026-05-24): both logos render as MapLibre icon symbols on
top of the publishable stack and consume the shared drag-to-move primitive
from `poi_editor_v2.md`. Toggle `showBrandLogos` lives in the Publishable
section and defaults on; Park + Topo presets show it, Trace hides it.

## Working Rule

Raw assets stay in `assets/branding/raw/` as the source-of-truth provenance
copies (see `assets/branding/README.md` for hashes, sizes, and source URLs).
Viewer-served copies live at `website/assets/branding/aop-badge.png` and
`website/assets/branding/rock-warblers.jpg`.

- **AOP badge**: reference-only until AOP confirms public reuse. On-map
  rendering is internal/inspection-grade until that confirmation lands.
- **Rock Warblers**: cleared for this AOP map project by the user grant on
  2026-05-23 (the user is Rock Warblers). Attribution + provenance stay in
  the asset manifest.

## How it works

- Seed data: `website/data/aop_brand_logos.geojson` carries two Point
  features (`aop_badge`, `rock_warblers`) with `icon_image` (matches the
  `map.addImage` name) and per-feature `icon_size`. Editing the seed file
  changes first-load positions; override store wins on subsequent loads.
- Source / layer: GeoJSON source `brand-logos`, single symbol layer
  `brand-logos-icons` reading icon-image + icon-size from feature props,
  with `icon-allow-overlap` + `icon-ignore-placement` so the icons always
  draw at their exact coordinates.
- Override store: `aop_brand_logos_overrides_v1` (localStorage), keyed by
  `logo_id`. `applyBrandLogoOverrides` runs before `addSource` so moved
  logos draw at their new spot from the first frame.
- Feature list panel: `brandLogos` consumer in `FEATURE_LIST_LAYERS` with
  visibility + drag-to-move + fly-to. `TUNABLE_LAYERS.brandLogos` exposes
  only the toggle + an `icon-opacity` slider (no color/width on raster
  icons).
- Bulk Export/Import: brand-logos overrides ride along in the v2 bundle
  via `captureRuntimeOverrides` / `applyExportAllPayload`.

## Placement Decision

Settled: on-map overlay, draggable. Default seed coordinates are nudged
off the 1010 Ellis Cove Road pavilion (north and south) so both logos are
visible at first load without overlapping the pavilion building.

Chrome placement (header / footer / attribution corner) intentionally
**not** done. On-map placement is the demonstrative artifact the user
asked for; chrome can layer on top later without affecting the on-map
work surface.

## Next Work

- Request official AOP logo originals (SVG or transparent PNG) and replace
  the favicon-sourced badge under the same path.
- Replace the Rock Warblers JPEG with a transparent PNG or SVG so the
  white card around the bird artwork drops out. Cosmetic, not blocking.
- Confirm AOP permission scope (internal draft / public website / print
  board / event map / all) and surface the asset's publish status in the
  popup once confirmed.

## Verification

`python3 mvp/scripts/playwright_verify_brand_logos.py` (server on 8001).
18 assertions cover: toggle defaults on, both icons register via
`map.addImage`, both icons render, layer hides on toggle off, feature
list panel opens with two move-enabled rows, drag-to-move commits the new
coordinate, override store persists, moved position survives a reload, no
console errors.

Screenshots land under `brain/output/playwright_brand_logos_*.png`.

## Related work

- `assets/branding/README.md` — raw asset manifest, provenance, hashes.
- `poi_editor_v2.md` — the shared drag-to-move primitive this consumer
  bolts onto. Brand logos close the "logos consume the drag side of the
  primitive once they land" follow-up from that card.
- `viewer_chrome_polish.md` / `_readme.md` Bucket F — the Sprint 02 dump
  line *"add aop logo / add rock warblers logo"* closes here.
