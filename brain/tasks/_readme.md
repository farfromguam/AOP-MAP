# Tasks

TL;DR: Work cards and execution notes live here. Active sprints sit at this top
level; fully-done sprints are archived under `_done/`.

Writing here: see `../voice/voice_guide.md` first, then `_extend.md`.

#aop #tasks #cards

-----

Task cards are the working edge of the project. They are directional, not sacred.
Research and field evidence can update them. User-written directives stay visible;
analysis and corrections go below the divider rather than silently deleting the
original shape.

## Two move rules (2026-06-14)

- A shipped **card** moves into its own sprint's `_done/`.
- A **sprint that is fully done** relocates as a whole to `tasks/_done/<sprint>/`,
  keeping its internal shape (its own `_done/`, its readme, and any spine card).
- A **spine card** that other docs link to by path stays at its sprint root with a
  DONE banner so its inbound links survive — it does **not** drop into the sprint's
  own `_done/`. (See `05_special_operation/universal_feature_layer.md`,
  `08_data_normalization/star_driven_poi_normalization.md`.)

## Layout

**Active / open sprints** keep a numbered dir at this top level, each with its own
`_done/` for shipped cards:

- `01_mvp/` — open data-integrity backlog items (acreage, real trail data, DEM).
- `03_event_app/` — closed except `misc_3.md`, left active by request.
- `06_going_gold/` — spine (`gold_migration.md`) done; the guardrail slate is open.
- `09_editor_maturity/` — UI / Path-A work done; the DB-door slice is held (gold slice 6).
- `14_illustrator_trace/` — the current Affinity trace round-trip lane (uncommitted).
- `20_deferred/` — parking lot (each card carries a "Deferred because").
- `backlog/` — research and feature-review notes.

**Fully-done sprints archived under `_done/`** (moved 2026-06-14):
`02_edit`, `04_edit`, `05_special_operation`, `07_tables`, `08_data_normalization`,
`11_client_convergence`, `12_field_schedule_editor`, `13_viewer_extraction`.

When a sprint moved, inbound references in active docs were repointed to the new
`tasks/_done/<sprint>/...` path; references inside point-in-time records (council
receipts under `output/`, dated handoff archives) were left pointing at the old
paths, as historical record.
