# Add An Image To The Viewer

TL;DR:
- Keep raw image provenance in the brain.
- Put viewer-served copies under `website/assets/`.
- Register the image in `website/index.html`, then point GeoJSON features at the registered `icon_image` name.

#aop #spinup #viewer #images #branding

-----

This is the short runbook for adding a raster image as a MapLibre icon layer,
using the AOP / Rock Warblers brand logos as the current pattern.

## Steps

1. Save the source image in the appropriate raw asset folder under `brain/`.
   Record source URL, dimensions, byte size, hash, permission, and publish
   status beside it. For branding assets, use
   `brain/tasks/_done/02_edit/assets/branding/README.md`.
2. Copy the viewer-served image into `website/assets/<topic>/`. Keep the file
   name stable if existing GeoJSON already references it.
3. Add or update a Point feature in `website/data/<layer>.geojson`. The feature
   needs a stable id property, an `icon_image` value, and an `icon_size` value.
   For brand logos, the stable id is `logo_id` in
   `website/data/aop_brand_logos.geojson`.
4. Register the image in `website/index.html` with `map.addImage`. The
   registration name must exactly match the feature's `icon_image` value.
5. Make or update the symbol layer so `icon-image` reads from `icon_image` and
   `icon-size` reads from `icon_size`.
6. If the image should be moveable or hideable per feature, add the layer to
   `FEATURE_LIST_LAYERS` and give it an override store. Brand logos use
   `aop_brand_logos_overrides_v1`.
7. Run the relevant Playwright verifier. For the current brand-logo layer:

```bash
python3 mvp/scripts/playwright_verify_brand_logos.py
```

## Current Branding Notes

- AOP badge reuse is reference-only until AOP grants explicit permission for the
  target surface.
- Rock Warblers reuse is cleared for this AOP map project by the user grant.
- The on-map brand logos are draggable and size-editable from the Brand logos
  drawer. Coordinate and `icon_size` overrides persist in
  `aop_brand_logos_overrides_v1`.
