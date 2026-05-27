# AOP Brain Map

TL;DR:
- This is the territory map for the staged AOP brain.
- The load-bearing branches are `northstar/`, `research/`, `tasks/`, `practices/`, `flows/`, `voice/`, and `ai_rules/`.
- The map project is source-led: provenance, permission, confidence, and field validation are part of the product, not admin paperwork.

#aop #brain #map #orientation

-----

## Top-level layout

```text
brain/
├── _readme.md
├── brain_map.md
├── search_map.md
├── split_manifest.md
├── northstar/      what is locked for the AOP map
├── research/       source briefs, evidence, current facts
├── import/         raw zone for community-sourced trail material
├── tasks/          work cards and execution notes
├── practices/      portable methods from the Soka brain
├── flows/          reusable work flows
├── spinup/         local startup, runbooks, and troubleshooting
├── voice/          how docs should read and be shaped
├── ai_rules/       how the assistant collaborates here
├── handoff/        session-specific handoff and onboarding notes
└── output/         future scratch artifacts
```

## What carries authority

`northstar/map_northstar.md` is the project promise. If a task card drifts from it, pull andon.

`northstar/whats_this_for.md` is the hobby and event-context briefing. Read it before drawing layers, picking difficulty language, or sizing course features -- AOP is a scale RC park, not an OHV park, and the wrong mental model produces the wrong map.

`northstar/source_register.md` is the data-integrity contract. It decides how source, confidence, permission, and publishability are carried through the map.

`northstar/personas.md` is the durable persona filter for view defaults, schedule surfaces, hot-button behavior, activity heat, and print handouts.

`research/aop_south_pittsburg_sources.md` is the current source stack for Adventure Off Road Park in South Pittsburg, Tennessee.

`research/aop_data_bounds.md` records the current two-parcel working envelope and the 9-patch data acquisition AOI for imagery, topo, DEM, and lidar pulls.

`research/viewer.md` is the catalog for the static MapLibre viewer (`website/index.html`): every layer, where its data comes from, and which doc records how it was built. Read it before adding or changing a viewer layer.

`spinup/mvp_runbook.md` is the durable local MVP runbook. Use it for CWC checks, Docker/PostGIS startup, QGIS connection settings, port collisions, publish export checks, and viewer spinup. `spinup/add_image_to_viewer.md` is the runbook for putting a new raster icon on the map; `spinup/viewer_storage_migration.md` is the forward-only rule for bumping `aop_*_v1` localStorage keys and `aop-*-v1` bundle schemas.

Sprint 03 is closed. Its reviewed cards live in `tasks/03_event_app/_done/`,
with `tasks/03_event_app/misc_3.md` left active by request. Sprint 04 starts at
`tasks/04_event_app/_readme.md`; it carries the extracted app-loop,
dev-reseed, content-audit, data-integrity, viewer-polish, POI-editor, brand,
and Park-icon work. `tasks/01_mvp/_done/aop_south_pittsburg_map_build_card.md`
is the closed Sprint 01 build card, kept as the historical promise. Cards are
direction, not gospel; update them as the map learns.

`voice/voice_guide.md` and `voice/style_guide.md` govern docs.

`practices/` holds the transferable thinking habits: apparent answers first, triangulation, andon, and thin vertical slices.

`split_manifest.md` records what was copied, adapted, and deliberately left behind.

## Split status

The brain has split out of Soka into its own repo. The directory is `brain/`,
and the repo root carries its own `AGENTS.md` and `CLAUDE.md`.

Remaining split chores:

- Replace any remaining Soka-rooted paths that should become local paths.
- Import only the voice corpus samples that the new project actually needs.
