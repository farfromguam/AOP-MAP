# AOP Search Map

TL;DR:
- Keyword routing for the staged AOP brain.
- Use this before grepping blindly.
- If a question asks "what did we decide," start in `northstar/`; if it asks "where did that fact come from," start in `research/`.

#aop #search #routing

-----

## Map project

- AOP, Adventure Off Road Park, South Pittsburg, Ellis Cove Road: `research/aop_south_pittsburg_sources.md`
- bounds, AOI, 9-patch, satellite, topography, lidar, current parcel envelope: `research/aop_data_bounds.md`, then `research/aop_south_pittsburg_sources.md`
- map build, PostGIS, QGIS, MapLibre, PMTiles, Cloudflare, Phoenix: `tasks/01_mvp/aop_south_pittsburg_map_build_card.md`
- source ledger, permission, confidence, provenance, publishable: `northstar/source_register.md`
- print map, wall map, whiteboard validation, board markup: `northstar/map_northstar.md`, then `tasks/01_mvp/aop_south_pittsburg_map_build_card.md`

## Working method

- open question, should we, decision: `practices/01_apparent_answers_first.md`
- conflicting facts, sources disagree, evidence mismatch: `practices/02_triangulation.md`
- stop the line, drift, unreconciled conflict: `practices/03_andon.md`
- first pass, slice, V1, proof: `practices/04_thin_vertical_slices.md`
- research brief: `flows/research_flow.md`
- task planning: `flows/plan_task.md`, `tasks/_extend.md`
- task execution: `flows/work_task.md`

## Collaboration

- durable rules, memory vs brain: `ai_rules/brain_is_durable.md`
- extract before invent: `ai_rules/extract_before_invent.md`
- don't touch git: `ai_rules/no_commits.md`
- cards are direction: `ai_rules/cards_not_gospel.md`
- preserve user directives in cards: `ai_rules/preserve_card_directives.md`
- recommendation requested, option menu, decision: `ai_rules/commit_in_prose.md`
- writing style: `ai_rules/user_writing_style.md`, `voice/voice_guide.md`
