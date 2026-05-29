# brain/import

TL;DR:
- This is the **raw zone** for community-sourced AOP trail material.
- Anything in here is provenance-tagged, inspection-only, **not publishable** until promoted.
- Path from here is `import/` -> review -> `raw.*` Postgres tables -> `core.*` -> `publish.*` (see `northstar/source_register.md`).

#aop #import #raw-zone #community-sources

-----

## What lives here

- `Saturday_Afternoon_Activity.gpx` -- the user's own Gaia GPS track recorded 2026-05-16 inside AOP (368 trackpoints, starts near 35.0915, -85.7486). Treat as a personal field GPX, not a community map.
- `community_trails/` -- the May 2026 community-sources pull. Manifest below.

## community_trails/ manifest

Pulled 2026-05-20 against the 9-patch acquisition bounds
`-85.782935, 35.067164, -85.717154, 35.117928` (the data-acquisition AOI
around the two-parcel working envelope; see `research/aop_data_bounds.md`).

| File | What | Source | License | Confidence | Use |
| --- | --- | --- | --- | --- | --- |
| `osm_aop_9patch_raw.json` | Overpass API raw JSON dump | OpenStreetMap via Overpass | ODbL (c) OSM contributors | medium | archive only |
| `osm_aop_9patch.geojson` | Converted FeatureCollection: 71 features incl. 47 `highway=track`, 19 `service`, plus park polygon and named landmarks | OSM via Overpass | ODbL | medium | inspection basemap; cross-check against TNMap imagery before trusting any single line |
| `osm_aop_9patch_named.geojson` | Filtered subset: 5 named features (`Adventure Off Road Park` polygon, `Jackson Point`, `Smithtown`, `Pinhook`, `Stagecoach Road`) | derived | ODbL | medium-high (names) / medium (geometry) | cross-reference against RiderPlanet landmark list |
| `sfwda_aop_trail_map_2015-03-11.webp` | SFWDA archived AOP trail map raster (original served as WebP despite `.jpg` extension) | https://www.sfwda.org/aop image asset | (c) Adventure Off Road Park (per SFWDA page) | high for **shape**, low for **current trails** | georeference as raster overlay only; do not redistribute |
| `sfwda_aop_trail_map_2015-03-11.png` | Same image converted to PNG for downstream tooling | derived | as above | as above | as above |
| `aop_official_trail_map_2025-11.webp` / `.png` | **Current** official AOP trail map (≈Nov 2025), pulled by rendering the `/trails` SPA. Same numbers-only scheme as 2015. | adventureoffroadpark.com `/assets/AOP MAP_1764447008903…` | (c) Adventure Off Road Park | high for **current shape**, none for **names** (numbers only) | georeference as raster overlay only; do not redistribute |
| `aop_official_map_rules_2025-11.pdf` | Official 4-page Map+Rules PDF (page 1 = same map, 2–4 = rules) | adventureoffroadpark.com `/assets/AOP Map_Rules_1764607479109…` | as above | reference | do not redistribute |
| `aop_trail_descriptions.json` | Harvested prose for 9 numbered trails (8 AOP via onX `og:description` + park's own Trail 96 via Wayback) + named-landmark list. See `research/aop_trail_name_index.md`. | onX trail pages; AOP 2015 blog (Wayback) | onX-copyright (8 trails); AOP-copyright-via-Wayback (#96) | high for those 9; names are onX labels not park nomenclature | raw only — no promote to publish.* without source rows + license clearance |

## Sources known but not pulled (need login / JS / permission)

These are listed in `research/aop_south_pittsburg_sources.md`. None of these were
downloaded into this folder because they either require an account, render in
JS, or have terms that disallow scrape:

- **onX Offroad** -- South Pittsburg trail directory and per-trail pages. Proprietary; trails can be exported as GPX from inside the app per their TOS. Best community-curated source for the ski-slope green/blue/black difficulty system. URL: https://www.onxmaps.com/offroad/beginner-offroad-trails-near-me/south-pittsburg-tn
- **Trails Offroad** -- hand-curated routes, GPX export for members; bundled into Gaia GPS via partnership. URL: https://www.trailsoffroad.com/
- **Gaia GPS** -- pulls Trailforks + Trails Offroad layers, exports GPX/KML/GeoJSON per track.
- **Trailforks** -- crowdsourced MTB-leaning trail data. AOP coverage is thin but worth a per-region scrape after auth. URL: https://www.trailforks.com/
- **Wikiloc** -- community GPX uploads. Search responds with a Cloudflare challenge to scripted clients; needs a real browser session. URL: https://www.wikiloc.com/
- **AllTrails** -- South Pittsburg area listing returned 403 to anonymous clients. URL: https://www.alltrails.com/explore/us/tennessee/south-pittsburg
- **Maprika** -- two community AOP map IDs exist. `id=16054` "Adventure Offroad Park" is explicitly flagged "Probably way off"; centroid 35.090951, -85.750444. Mobile-only download via `maprika://app/?map=16054`. URL: https://www.maprika.com/maplink.php?id=16054
- **Gather Offroad** -- 2026 offline trail-pack app that claims Tennessee adventure-park coverage. Verify AOP-internal coverage inside the app before using. URL: https://gatheroffroad.com/
- **Scaletra** -- the RC-scale trail tracking app (the right peer for AOP's actual hobby). User-uploaded scale-trail tracks, free. URL: https://www.scaletra.com/
- **rcmap.io** -- RC-scale community map directory; AOP listing not confirmed from public search. Cross-check from inside the app.
- **Hardline Crawlers thread** -- community photos of the AOP paper map (403 to scripted clients). URL: https://www.hardlinecrawlers.com/threads/aop-adventure-offroad-park-paper-map.49037/
- **Adventure Off Road Park official site** -- map page is a JS shell (`adventure-offroad-clone--AdventureORP.replit.app`). The current "View Trail Map" button and QR code-linked digital map are behind that render. URL: https://www.adventureoffroadpark.com/pages/map

Next agent: render the AOP map page with the existing Playwright tooling in `mvp/scripts/` to extract the live trail-map asset.

## Provenance crib

When promoting any of this into `raw.*` Postgres tables, attach:

- `name` -- e.g. `OSM Overpass 9-patch 2026-05-20`
- `source_type` -- `community_geo` for OSM, `community_raster` for SFWDA, `personal_gpx` for the user's Gaia track
- `url_or_contact`
- `retrieved_on` -- `2026-05-20`
- `license_or_permission` -- ODbL for OSM, AOP-copyright-via-SFWDA for the 2015 raster, user-owned for the GPX
- `publish_status` -- start `internal`; promote only after permission and geometry confidence are settled
- `confidence_default` -- per the table above

## What we deliberately did not import

- App screenshots from onX, Gaia, Trailforks, AllTrails. They are inspection material only and re-publishing screenshots breaks those apps' TOS.
- Tumblr / Instagram hero photos. Atmospheric, no map value.
- Trail-name lists scraped from blog content (e.g. "Launchpad", "Little Dipper", "Megabit", "Convergence", "Ground Control", "Major Tom"). The names came back in plain prose only; we cannot attribute them to a specific trail polyline without the live AOP map asset.

## Named landmarks cross-check (from `osm_aop_9patch_named.geojson`)

- `Adventure Off Road Park` polygon -- OSM way 1215497712 -- envelope `-85.7601, 35.0834` to `-85.7455, 35.0995`. Tighter than the two-parcel candidate envelope. Treat as a community-supplied boundary candidate, not a survey.
- `Jackson Point` -- node 11371549562 -- 35.0997725, -85.756452. Matches the RiderPlanet landmark list (Jackson Point, Goat Rock, Tate Cove Creek, Fishtrap Point, Beene Cove, Rogers Cove, Ballard Point). Only Jackson Point appears in OSM at present; the rest are open candidates.
- `Smithtown` -- node 153366614 -- 35.0811915, -85.7349718. Place name, outside the AOP polygon to the southeast.
- `Pinhook` -- node 153662392 -- 35.1106359, -85.7402498. Place name, north edge of the 9-patch.
- `Stagecoach Road` -- way 392166283 -- runs along the western edge of the 9-patch, `highway=unclassified`.

#tag-import #tag-provenance
