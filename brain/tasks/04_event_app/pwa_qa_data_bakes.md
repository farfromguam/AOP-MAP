# PWA QA — data bakes & coverage (split out of pwa_qa.md)

TL;DR:
- Three items from `pwa_qa.md` were too big for the front-end QA swarm because
  they are **data-pipeline / acquisition** work, not viewer chrome. They need
  source-provenance decisions and the `raw → core → publish → bake` spine, so
  they were carved out here on 2026-05-31.
- Owner decisions are required (which buildings are "in park" vs "region", how
  far to extend the imagery AOI). Hold to `northstar/source_register.md` and
  `no_limiting_code_mvp.md` — surface integrity risks as notes, do not add
  rejecting/filtering constraints.

#aop #sprint #04_event_app #pwa_qa #data #bake

-----

## Why these split off

`pwa_qa.md` is mostly viewer/PWA chrome that parallel front-end agents resolved
in worktrees on 2026-05-31. These three need the data spine and a source call,
so they get their own card instead of blocking the chrome swarm.

## Item 4 — bake map region callouts into geojson

> "bake in map region callouts to geojson"

- **Status: possibly partial.** The 2026-05-30 handoff says `misc_4` shipped an
  "images/region-callout export bake." First step: confirm what already exists
  (`website/data/aop_visitor_context_callouts.geojson`? the region-callout export
  path in `misc_4.md`) before re-baking.
- Goal: region-level callouts are part of the served geojson (baked), not
  computed/placed only at runtime, so a fresh static install renders them.
- Route through `export_publish_geojson.sh` / the gold-export pattern if these
  are publishable features; keep the source GeoJSON clean so re-exports do not
  overwrite authored copy (the `aop_poi_index.json` precedent).

## Item 6 — buildings: bake in-park, exclude region, drop from search

> "bake buildings in park / exclude buildings in region. — do not allow them to
> be searched."

- **Owner decision owed:** what defines "in park" vs "region"? Likely the parcel
  envelope in `research/aop_data_bounds.md` (two-parcel working envelope) vs the
  wider 9-patch AOI. Pick the boundary that classifies a building as park vs
  region before any code.
- Bake the in-park buildings as published facilities; region buildings stay as
  raw reference context (the current `#showBuildings` note already warns FEMA
  footprints are "raw reference context; verify against imagery").
- **Search:** region buildings must not appear in viewer search results. The
  front-end half lives in `indexFeatures(...)` for the buildings layer
  (`website/index.html`) — gate which building features get registered by the
  park/region flag baked in the prior step. This half is blocked until the
  classification exists, which is why item 6 stayed off the chrome swarm.
- Honor `no_limiting_code_mvp.md`: the search exclusion is a *display* scope, not
  a data-rejecting constraint — it must not drop rows from the source data.

## Item 17 — extend the 9-patch imagery coverage

> "on tall phones or wide monitors our 9 patch is not enough coverage to not see
> the edges of the map. we need to extend the 9 patch to ~bigger."

- Symptom: on tall phones / wide monitors, fitting the camera shows past the
  imagery/terrain edge → the cream background (`#efe7d5`) shows at the map edges.
- This is **data acquisition**, not CSS: the 9-patch data-acquisition AOI
  (`research/aop_data_bounds.md`, `REGION_BOUNDS` = the camera leash/maxBounds)
  defines how far imagery/topo/DEM/lidar were pulled. To stop the edge showing,
  re-acquire imagery + terrain at a larger AOI **and** widen `REGION_BOUNDS`
  to match (the leash must not exceed the data, or the edge just moves).
- Owner decision owed: how much bigger. Tie the new AOI to the worst-case
  aspect ratios (tall phone portrait, wide desktop landscape) so the fitted
  camera never reaches the data edge.
- Cross-links: `research/aop_data_bounds.md`, `data_integrity_publishability.md`
  (item 10 DEM swap lives there too), `research/viewer.md`.

## Done-when

- Item 4: a fresh static install renders region callouts from the baked geojson;
  source GeoJSON stays authoring-clean.
- Item 6: in-park buildings baked as facilities, region buildings excluded from
  search results, no source rows dropped.
- Item 17: at the worst-case viewport aspect ratios, the fitted camera shows map
  data to every edge — no cream band — with `REGION_BOUNDS` widened to match the
  new imagery AOI.
