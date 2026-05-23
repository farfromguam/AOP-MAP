# Building Footprints Layer

Status: DONE (2026-05-21)

Review the 9-patch for accessible building / structure footprint layers and
import the usable source into the static viewer.

#aop #tasks #mvp #buildings #fema #structures

-----

## Outcome

Imported FEMA USA Structures as the building-footprint reference layer.

- Importer: `mvp/scripts/import_fema_buildings.py`
- Output: `website/data/aop_buildings.geojson`
- Viewer toggle: `Building footprints (FEMA USA Structures)`, default ON in
  Park/Topo/Trace (Sprint 02 A2 + Bucket E). The feature-list panel keeps
  the 4 in-park rows pre-ticked and the 198 outside-park rows collapsed
  under a default-off bulk toggle, so a fresh Park view only draws the
  in-park footprints unless the user expands the rest.
- Viewer layers: `building-footprint-fill`, `building-footprint-outline`,
  `building-footprint-aop-outline`
- Verification: `mvp/scripts/playwright_verify_buildings.py`

Counts from the 2026-05-21 import:

| Class | Count |
| --- | ---: |
| Residential | 166 |
| Agriculture | 24 |
| Unclassified | 7 |
| Assembly | 3 |
| Government | 2 |
| Total | 202 |

Four footprint centroids fall inside the current AOP candidate boundary, all
on Ellis Cove Road:

| Label | Class | Area |
| --- | --- | ---: |
| 1010 Ellis Cove Road | Residential | 3,626.1 sq ft |
| 1033 Ellis Cove Road | Residential | 2,307.5 sq ft |
| 665 Ellis Cove Road | Residential | 1,186.7 sq ft |
| 880 Ellis Cove Road | Residential | 692.3 sq ft |

These are raw reference context, not confirmed AOP facilities. Verify against
TNMap imagery and/or field knowledge before promoting any of them into a park
facilities layer.

## Source Review

### Selected: FEMA USA Structures

- Service item: `https://www.arcgis.com/home/item.html?id=e9fc147eaeae4dcaa4e9ad9802c7b9c6`
- FeatureServer:
  `https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/USA_Structures_View/FeatureServer/0`
- Result in the 9-patch: 202 polygon footprints.
- Useful fields: occupancy class, primary occupancy, address, square feet,
  height, image date, production date, source, validation method, UUID.
- Source note: the item describes footprints for U.S. structures greater than
  450 sq ft. The local sample shows ORNL as the source and automated validation,
  with image dates in December 2016.

Why selected: broad footprint coverage, direct ArcGIS REST access, GeoJSON
output, usable attributes, and no bulk download/tooling needed.

### Checked: OpenStreetMap building ways

- Query: Overpass `building=*` across the 9-patch bbox.
- Result: 11 building ways.
- Decision: not imported in this pass. The OSM result is smaller than FEMA and
  brings ODbL context into a layer where FEMA already covers the area. Keep it as
  a cross-check source if a specific footprint looks wrong.

### Checked: TNMap FEMA BLE Building Footprints

- Service: `https://tnmap.tn.gov/arcgis/rest/services/ENVIRONMENTAL/FEMA_BLE/MapServer/1`
- Result in the 9-patch: 0 features.
- Decision: not usable here.

### Deferred: Microsoft / Overture bulk footprints

Microsoft and Overture-style footprint datasets may be useful as a second-pass
cross-check, but they require heavier bulk extraction or cloud-parquet tooling.
The FEMA layer is enough for the viewer slice.

## Import Notes

The FEMA service returned count/ids quickly, but direct bbox GeoJSON feature
queries rejected the parameters. The importer therefore:

1. Queries the bbox with `returnIdsOnly=true`.
2. Fetches the matching object ids in chunks with `f=geojson`.
3. Normalizes source fields into compact viewer properties.
4. Loads `website/data/publish.geojson` and tags each footprint by whether its
   representative point is inside the current AOP boundary.
5. Writes atomically to `website/data/aop_buildings.geojson`.

As of Sprint 02 A2 (2026-05-23) the layer is default ON in Park, Topo, and
Trace. The feature-list panel keeps only the 4 in-park rows pre-ticked, so a
fresh Park view draws the in-park footprints while the 198 outside-park
footprints stay collapsed off until the user expands them. Indexed for search
only where the FEMA feature has an address. Searching `1010 Ellis` lands on
the corresponding footprint and turns the building layer on if it is off.

## Source Register

This is raw-zone context. Before any footprint becomes a publishable park
facility, add a source-register row and review it against imagery or field
knowledge. Suggested defaults:

- `name`: `FEMA USA Structures / ORNL 9-patch import 2026-05-21`
- `source_type`: `federal_structure_footprints`
- `license_or_permission`: `FEMA public data layer; no warranty`
- `publish_status`: `raw_context`
- `confidence_default`: `medium`

## Verification

- `python3 -m py_compile mvp/scripts/import_fema_buildings.py`
- `python3 mvp/scripts/import_fema_buildings.py`
- `node` inline script syntax check for `website/index.html`
- `python3 mvp/scripts/playwright_verify_buildings.py` -- PASS on 2026-05-21,
  0 console errors.
