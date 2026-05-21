# Imagery tracing layer

Started: 2026-05-21
Status: DONE (2026-05-21)

Add the best available official imagery as a viewer layer option and make it
usable for raw trace capture without pretending those traces are publishable.

#aop #imagery #naip #tracing #viewer #source-register

-----

## Source search

Best accessible sources found:

- **USDA NAIP public ImageServer**:
  `https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer`
  -- public cached tiles, 4-band source, Tennessee listed by USDA's NAIP Public
  Image Services map as year `2023`, resolution `60 Centimeters`. This is the
  practical browser tracing layer.
- **USDA 2025 Tennessee county archive**:
  `ortho_1-1_hm_s_tn115_2025_1.zip`, Marion County, downloaded from USDA's
  public NAIP Box archive to `mvp/cache/imagery/`. Image-date index over the AOP
  block reports acquisition `2025-08-30`, 4-band (`M4B`) imagery.

## Decision

Use USDA `USDA_CONUS_PRIME` as the viewer layer because it exposes standard
ArcGIS cached tiles and works directly in MapLibre:

```text
https://gis.apfo.usda.gov/arcgis/rest/services/NAIP/USDA_CONUS_PRIME/ImageServer/tile/{z}/{y}/{x}
```

Keep the 2025 county archive cached but **do not wire it to the browser yet**.
It is MrSID, and the repo's current GDAL Docker image does not have a MrSID
driver. It is useful for QGIS or any desktop GIS with MrSID support; it is not
currently reproducible through the repo toolchain.

## What shipped

- `website/index.html`
  - Toggle `USDA NAIP imagery (TN 2023)`, default OFF.
  - Raster source `usda-naip-imagery`, layer `usda-naip-satellite`.
  - Editor button `Trace line`, backed by Terra Draw LineString mode.
  - Trace features render as lines and export with:
    `layer=editor_trace`, `source_name`, `source_url`, `source_year`,
    `source_resolution`, `confidence=draft`, and `review_status`.
- `mvp/scripts/playwright_verify_satellite.py`
  - Verifies the USDA imagery toggle and tile requests.
- `mvp/scripts/playwright_verify_poi_editor.py`
  - Verifies LineString tracing, persistence, export metadata, and layer toggle
    behavior.

## Source discipline

Imagery traces are raw candidates. Before anything moves to `core` or
`publish`, attach source-register rows and review against field data, hillshade,
the SFWDA map, and/or repeat imagery. A clean-looking image trace under canopy
is still low confidence until confirmed.

## Verification

Run against `WEBSITE_URL=http://localhost:8001/` on 2026-05-21:

- `mvp/scripts/playwright_verify_satellite.py` -- PASS, 0 console errors; USDA
  toggle requested 24 tiles from `gis.apfo.usda.gov`.
- `mvp/scripts/playwright_verify_poi_editor.py` -- PASS, 0 console errors;
  trace LineString persisted through reload and carried USDA NAIP source
  metadata.

## Acceptance

- [x] Best practical official imagery source identified.
- [x] 2025 county archive downloaded to gitignored cache.
- [x] Viewer has a USDA NAIP imagery toggle.
- [x] Viewer can trace LineStrings against imagery.
- [x] Trace export carries raw/source/review metadata.
- [x] No trace is promoted into `publish`.
- [x] Playwright verification passes.
