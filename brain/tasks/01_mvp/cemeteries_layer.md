# Cemeteries layer — Marion County cemetery parcels in the viewer

Started: 2026-05-21
Status: DONE (2026-05-21)

Add Marion County cemetery parcels to the static viewer as a toggleable,
searchable layer. The trigger: confirming that the hole in the AOP boundary
polygon is the Ellis Cemetery inholding.

#aop #cemetery #parcels #viewer #search #editor-is-the-viewer

-----

## Why now

The AOP working-envelope polygon (`website/data/publish.geojson`) carries an
interior ring — a hole — in parcel `110 008.00`. A USGenWeb cemetery record
for "Ellis Cemetery" was reviewed and the question was whether that cemetery
is the hole.

It is. Confirmed against the Tennessee Comptroller Marion County parcel layer:
the hole is parcel `110 008.04`, owner of record `BRYSON & ELLIS CEMETERY`,
class `05 RELIGIOUS`, ~0.12 acre — a family burying ground excepted out of the
deed when the surrounding Ellis land became the park. Full evidence and the
source record are in `research/aop_ellis_cemetery.md`.

The user asked to confirm it and add it to the map, searchable.

## What was added

### Importer

- `mvp/scripts/import_marion_cemeteries.py` — queries the Comptroller
  `TN_County_Parcel_Map` FeatureServer layer 35 for cemetery-owned parcels
  (`OWNER LIKE '%CEMETERY%'`) intersecting the 9-patch, normalizes each into a
  readable cemetery feature, joins a hand-curated burial roster where one is
  known, and atomic-writes the GeoJSON. Stdlib only (urllib); no curl/jq.

The burial roster currently lives as a constant (`CEMETERY_OVERRIDES`) inside
the importer — one cemetery has a roster. Promote it to a sidecar input file
if a second roster is ever added.

### New website data file

- `website/data/aop_cemeteries.geojson` — 4 cemeteries, 8 features. Per
  cemetery: one parcel feature (Polygon/MultiPolygon) and one centroid marker
  (Point), distinguished by a `geom_role` property and carrying the same
  attributes so either is clickable and search collapses them to one result.

The four cemeteries (only Ellis is an AOP inholding):

| Parcel | Name | ~Acres | AOP inholding |
| --- | --- | ---: | --- |
| `110 008.04` | Ellis Cemetery | 0.12 | yes (12 recorded burials) |
| `093 029.00` | Gilliam Cemetery | 2.91 | no |
| `093 003.00` | Bible Cemetery | 0.74 | no |
| `093 001.02` | Tate Cemetery | 0.70 | no |

### New viewer layers in `website/index.html`

- `cemetery-fill` / `cemetery-outline` — the parcel polygon (filter
  `geom_role = parcel`).
- `cemetery-marker` — a centroid circle (filter `geom_role = marker`). The AOP
  inholding gets an amber ring via a `case` on `aop_inholding`, so the hole
  reads at a glance.
- `cemetery-label` — the cemetery name at the centroid.

One toggle, `Cemeteries (TN Comptroller parcels)`, default OFF — consistent
with the other overlays. Search turns the layer on when it jumps to a result.

Popup carries name, also-known-as, parcel, owner of record, class, area,
inholding status, recorded-burial count, source, and (for Ellis) the burial
roster with its USGenWeb attribution.

### Search

Cemeteries are indexed for the in-viewer search. The county owner-of-record
name is indexed as an alias, so both "Ellis Cemetery" and "Bryson & Ellis
Cemetery" resolve to the same place.

### Verification

- `mvp/scripts/playwright_verify_cemeteries.py` — 25 checks, all PASS on
  2026-05-21, 0 console errors. Covers toggle/visibility, feature counts, the
  inholding flag, the burial roster, search by name and by alias, and the
  search jump re-enabling the layer and landing on parcel `110 008.04`.
- Screenshots: `brain/output/playwright_cemeteries_*.png`.

## Out of scope here

- Promoting cemeteries into `core` / `publish` PostGIS layers. They are a
  raw-zone viewer overlay, like roads and water. Promotion needs a
  `source_register` row per `northstar/source_register.md`.
- Publishing the burial roster beyond the inspection viewer — USGenWeb terms
  are non-commercial with a notice-retention requirement. See
  `research/aop_ellis_cemetery.md`.
- The `BRYSON & ELLIS CEMETERY` vs `Ellis Cemetery` name question, and the
  cemetery-access easement question, both flagged in the research doc.

## Acceptance

- [x] `import_marion_cemeteries.py` runs and writes `aop_cemeteries.geojson`.
- [x] The viewer panel has a `Cemeteries` toggle, default OFF.
- [x] Toggling it ON shows the parcel polygons, markers, and labels.
- [x] The Ellis Cemetery inholding is visibly distinct (amber marker ring).
- [x] Search finds the cemetery by name and by county owner-of-record name.
- [x] A search jump turns the layer on and lands on parcel `110 008.04`.
- [x] Playwright verification passes with 0 console errors.
