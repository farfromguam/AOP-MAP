# AOP South Pittsburg Map Sources

Last touched: 2026-05-20

AOP here means Adventure Off Road Park in South Pittsburg, Tennessee.

Current public anchor:
- Official site: https://adventureoffroadpark.com/
- Address: 1040 Ellis Cove Road, South Pittsburg, TN 37380
- Current official claim: 600+ acres, 120+ trails, beginner-to-extreme trail range.
- Phone / office source: 423-582-7060

The clean map stack is not one source. It is a stack:

1. TDOT / TNMap orthoimagery for highest-resolution statewide imagery.
2. USGS 3DEP / Tennessee LiDAR for terrain.
3. Tennessee Comptroller parcel data for the legal-ish land envelope.
4. Official AOP + off-road app data for trail names, difficulty, and ride routing.
5. Field validation, because private OHV trail maps drift.

-----

## Best Sources Found

### Imagery

**TNMap TDOT orthoimagery**

Best first imagery source for close inspection. The TNMap service says it is built from TDOT orthoimagery, with 1-foot source imagery before 2022 and 6-inch source imagery from 2022 onward. That is better than normal satellite and better than NAIP for small road/trail scars when the coverage is current for Marion County.

- Portal: https://gis.extglb.tn.gov/
- Service: https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/IMAGERY_WEB_MERCATOR/MapServer
- Why it matters: high-resolution orthophoto, GIS-ready service, statewide authority.
- Caveat: service updates county-by-county as TDOT releases flights. Need to check the imagery date over AOP.

**USDA NAIP**

Best federal imagery fallback and good for GIS download. NAIP is leaf-on aerial imagery, orthorectified, and downloadable through USGS/USDA paths. It is usually not as sharp as 6-inch TDOT imagery, but it is easier to archive as data.

- Data.gov record: https://catalog.data.gov/dataset/national-agriculture-imagery-program-naip-imagery
- USGS National Map entry point: https://www.usgs.gov/index.php/tools/download-data-maps-national-map
- USDA image services commonly start here: https://naip-usdaonline.hub.arcgis.com/
- Why it matters: public, stable, GIS-friendly, useful for historical comparison.
- Caveat: leaf-on canopy can hide trail beds. Great for open cuts, weaker under trees.

**Commercial visual checks**

Google Earth, Apple Maps, MapQuest, Esri World Imagery, onX, and Gaia are useful cross-checks. Treat them as inspection basemaps unless license terms explicitly allow reuse/export.

-----

## Topography / Terrain

**USGS National Map / 3DEP**

Primary elevation source. Use this for DEMs, contours, hillshade, slope, landform, and drainage work.

- National Map downloads: https://www.usgs.gov/index.php/tools/download-data-maps-national-map
- Data delivery tools: https://www.usgs.gov/the-national-map-data-delivery
- Lidar availability viewer: https://apps.nationalmap.gov/lidar-availability-viewer/
- Tennessee 3DEP fact sheet: https://pubs.usgs.gov/publication/fs20253037/full
- Why it matters: 1-meter DEM and lidar source data where available; federal baseline; QGIS-friendly.
- Caveat: raw lidar is heavier than we need for a first map. Start with 1-meter DEM if available, then pull point clouds only if trail benching / drainage scars matter.

**Tennessee Elevation / LiDAR Program**

State-facing lidar portal. Use alongside USGS LidarExplorer.

- Portal: https://lidar.tn.gov/
- STS GIS page: https://www.tn.gov/finance/sts-gis.html
- TennesseeView source list: https://tnview.utk.edu/data/
- Why it matters: Tennessee-specific elevation/LiDAR routing and derived products.

**USGS topo maps**

Use for named landforms, contours, roads, creeks, and historical context.

- TNMap USGS topo service: https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS/USGS_TOPO/MapServer
- South Pittsburg US Topo GeoPDF: https://prd-tnm.s3.amazonaws.com/StagedProducts/Maps/USTopo/PDF/TN/TN_South_Pittsburg_20130410_TM_geo.pdf
- Why it matters: fast orientation and printable field reference.
- Caveat: AOP may cross or sit near adjacent quadrangles. Check South Pittsburg first, then Orme / Monteagle / Burrow Cove if the AOI spills northwest.

-----

## Parcel / GIS Boundaries

**Tennessee Comptroller parcel data**

Primary parcel source. Download Marion County parcel shapefiles or use the TN Property Viewer for inspection.

- Parcel data download page: https://comptroller.tn.gov/office-functions/pa/gisredistricting/redistricting-and-land-use-maps/parcel-data.html
- TN Property Viewer: https://tnmap.tn.gov/assessment/
- TPAD search: https://assessment.cot.tn.gov/TPAD/
- ArcGIS item for statewide property boundaries: https://www.arcgis.com/home/item.html?id=e356f1a241844d6f9025f2fa4e977df3&sublayer=0
- Why it matters: gives the working land envelope and parcel links into assessment records.
- Caveat: parcel GIS is graphical reference, not a survey. Good enough for mapping context; not legal boundaries.

Working lead:
- Third-party property records point 1040 Ellis Cove Road to APN / parcel ID `110-008.00-001`.
- A nearby LoopNet record also shows a 482.26-acre figure for 1040 Ellis Cove Road.
- Official AOP says 600+ acres. That mismatch may mean multiple parcels, changed holdings, marketing acreage, or stale third-party data. Verify with Comptroller data before drawing the park boundary.

Current MVP import result, 2026-05-20:
- Source layer: Tennessee Comptroller `TN_County_Parcel_Map` ArcGIS FeatureServer layer `35` / `Marion_Parcels`.
- Query used: `Assessment_Data_58_ADDRESS = 'ELLIS COVE RD 1040' OR Assessment_Data_58_ID = '093 030.01'`.
- Returned two parcel features.
- Parcel 1 assessment ID: `110 008.00`.
- Parcel 1 assessment parcel ID: `058 110    00800 000 2023`.
- Parcel 1 object ID: `20707`.
- Parcel 1 global ID: `d1d093ee-9995-42a8-8676-da5570950697`.
- Parcel 1 address field: `ELLIS COVE RD 1040`.
- Parcel 1 class: `12 FOREST`.
- Parcel 1 land use: `81 - AGRICULTURE AND RELATED ACTIVITIES`.
- Parcel 1 calculated acres: `502.49725246`.
- Parcel 1 deed acres: `483.46`.
- Parcel 2 was added from the user-provided connected parcel lead `058 093 03001 000 2026`; the current ArcGIS parcel layer identifies it as assessment ID `093 030.01` and assessment parcel ID `058 093    03001 000 2023`.
- Parcel 2 object ID: `18788`.
- Parcel 2 global ID: `593a88f0-ab87-4f64-ab54-12c29c2a41e2`.
- Parcel 2 address field: `ELLIS RD`.
- Parcel 2 class: `12 FOREST`.
- Parcel 2 calculated acres: `89.8211522`.
- Parcel 2 deed acres: `90`.
- Imported candidate parcel calculated acres total: `592.31840466`.
- Imported candidate parcel deed acres total: `573.46`.

Interpretation:
- This gives a real source-backed parcel envelope for the MVP viewer and includes the connected `093 030.01` parcel in the published mapping extent.
- It gets closer to, but still does not fully reconcile, the official 600+ acre AOP claim.
- Treat the imported boundary as a candidate working envelope, not as a legal survey or confirmed complete park boundary.
- Next parcel pass should inspect adjacent or related parcels around Ellis Cove Road and South Pittsburg Mountain Road.

Working data bounds:
- Stable bounds note: `brain/research/aop_data_bounds.md`.
- GIS concept artifact: `brain/output/aop_9_patch_data_bounds.geojson`.
- The current center data bounds are the exported bbox of the two-parcel candidate envelope: `-85.761008221, 35.084085624, -85.739081159, 35.101007060`.
- The 9-patch acquisition bounds expand that center cell one full cell in every direction: `-85.782935283, 35.067164188, -85.717154097, 35.117928496`.
- Use the 9-patch for satellite/orthoimagery, topo, DEM, hillshade, contours, and lidar acquisition. Trails stay inside the park working envelope unless AOP confirms otherwise.

**TNMap services**

Useful for base layers, roads, historical imagery, public safety layers, administrative boundaries, and environmental overlays.

- REST root: https://tnmap.tn.gov/arcgis/rest/services
- Basemaps folder: https://tnmap.tn.gov/arcgis/rest/services/BASEMAPS
- Historical imagery folder: https://tnmap.tn.gov/arcgis/rest/services/HISTORICAL_IMAGERY_BASEMAPS
- Transportation folder: https://tnmap.tn.gov/arcgis/rest/services/TRANSPORTATION

-----

## Trail Sources

This is the weak part. AOP is private land. Public transportation/trail datasets will not be the source of truth for internal OHV trails.

**Official AOP**

Start here for current trails and permissions.

- Official site: https://adventureoffroadpark.com/
- Current site exposes a "View Trail Map" path and says trails range from scenic green rides to hardcore rock crawling.
- RiderPlanet says trail maps are provided at check-in.

Need next: obtain the current AOP trail map directly from the park or current site, then ask whether digital reuse is allowed.

**SFWDA AOP page**

Old but useful because it shows a trail map artifact and confirms the trail-difficulty marking scheme.

- Page: https://www.sfwda.org/aop
- Notes: AOP trail map listed as last updated 2015-03-11. Trail markers described as black / blue / green, ski-slope style.
- Caveat: current official acreage/trail count is larger. Use as historical reference, not current truth.

**RiderPlanet**

Best public trail-directory page found in this pass.

- Main page: https://www.riderplanet-usa.com/atv/trails/info/tennessee_15194/ride_d19a.htm
- Map page: https://www.riderplanet-usa.com/atv/trails/info/tennessee_15194/map_498b.htm
- Notes: updated May 10, 2025; lists 600 acres, 120 miles of marked/designated trails, elevation 650-1800 ft, staging area and several trail GPS points.
- Caveat: directory data is not official park data. Good for triangulation.

**Maprika**

Potentially useful for georeferenced image maps.

- Map list found `Adventure off road park (AOP)` and `Adventure Offroad Park`.
- One entry is explicitly marked "Probably way off": https://www.maprika.com/maplink.php?id=16054
- Caveat: community maps vary wildly. Use only after checking alignment against known roads, parcel boundaries, and imagery.

**Gather Offroad**

New 2026 app worth testing because it claims offline trail packs covering Tennessee / Kentucky / Virginia adventure parks.

- Site: https://gatheroffroad.com/
- Notes: site says the Tennessee/Kentucky/Virginia live pack covers Windrock, Brimstone, Royal Blue, Tackett Creek, Catoosa, Pickett, Hillbilly, and adventure parks.
- Caveat: verify AOP coverage inside the app before treating it as a source.

**Other app checks**

Check onX Offroad, Gaia GPS, Garmin Tread, and possibly Where2Wheel as comparison layers. These are useful in the vehicle. They are not automatically usable as data sources.

The question to ask of each app:
- Does it include AOP internal trails?
- Does it show difficulty per trail?
- Can it export GPX/KML legally?
- Does it work offline at AOP?
- Does it distinguish legal/private/internal park trails from nearby public roads?

-----

## Build Recipe

First QGIS pass:

1. Create an AOP AOI around 1040 Ellis Cove Road.
2. Load Tennessee Comptroller Marion County parcels.
3. Find parcel `110-008.00-001`, then inspect adjacent/related parcels until the AOP acreage mismatch is explained.
4. Add TNMap TDOT orthoimagery.
5. Add TNMap USGS topo service.
6. Download USGS 3DEP 1-meter DEM for the AOI.
7. Generate hillshade, slope, and 10-foot / 20-foot contours.
8. Add hydrography / drainage lines from USGS National Map or TNMap.
9. Register the official or SFWDA trail-map image as a raster overlay if permission and image quality allow.
10. Compare any exported GPX/KML from apps against imagery and hillshade.

Field / validation pass:

1. Ask AOP for the current map and whether digital use is allowed.
2. Confirm whether trails are one-way, vehicle-specific, temporarily closed, or event-only.
3. Record a sample ride track.
4. Compare the sample GPX against app trails, SFWDA map, RiderPlanet points, and visible trail scars.

-----

## Open Questions

- Does the current official AOP trail map have a downloadable PDF/KML/GPX, or is it only web/paper/app?
- Which parcel or parcels make up the current 600+ acre park boundary?
- What is the current imagery date for the AOP area in the TDOT TNMap service?
- Is 1-meter DEM enough for the use case, or do we need raw lidar-derived hillshade to see bench cuts and drainage better?
- Are we making an internal research map, a ride-navigation map, or a publishable/public map? Licensing changes depending on the answer.

-----

## Current Best Answer

For an accurate AOP terrain research base, use TDOT/TNMap imagery plus USGS 3DEP lidar-derived DEM. For boundaries, use Tennessee Comptroller parcels and verify the acreage mismatch. For trails, get the official AOP map first, then compare it against RiderPlanet, SFWDA's 2015 artifact, Gather/off-road app coverage, and field GPX.

No single public trail source is good enough by itself. The trail map has to be assembled by triangulation.
