# Sprint 09 — Editor maturity (the right-panel editing surface, completed + DB-first)

TL;DR:
- The right panel must be the **one editing surface** (`editor_is_the_viewer`): every first-party /
  curated feature type **visible** AND **editable** there, persisted **DB-first** — no localStorage-only
  shortcuts.
- Triggered by the user (2026-06-08): a drawn POI ("Launchpad") shows in the left list + on the map +
  in the right ★ Visitor list, but has **no editable node** in the right panel — the "Drawn POIs"
  editor was retired 2026-06-05 (`7cd51fa "v50 styles"`) and the user does not know why / wants it back.
- Direction: *"this is a needed surface. put it in. make sure everything is visible on the right side and
  editable. consult the council for a full robust plan. No shortcuts. we are trying to mature the project
  and not maintain shortcuts or MVP code."*

#aop #09_editor_maturity #editor #panel #db_first #curation

-----

## Spine card

`editor_completeness.md` — the council-reviewed plan: restore the retired editing nodes,
spec-complete the curated-but-uneditable layers, reconcile the half-retirement, and make every
editable surface persist DB-first (coordinating gold slice 6's F1/F2 DB doors, not duplicating them).

## The two axes (they intersect — that is the point)

- **Editor completeness (this sprint owns it):** every curated feature type has a VISIBLE, EDITABLE
  node in the right panel. Gaps: Drawn POIs (retired), generic draw (retired), trailheads (no list, F7),
  event anchors (no list).
- **DB-first persistence (gold slice 6 owns it — `06_going_gold/gold_migration.md`):** each editable
  surface persists to `core.features` (drawn-POI door F2, geometry/icon_size door F1), not localStorage.
  This sprint REFERENCES those doors as the maturity bar; it does not re-card them.

## Related (read before acting — references, not analogies)

- `06_going_gold/gold_migration.md` slice 6 — the DB-door work (F1/F2), HELD until a human pulls it.
- `output/council/spike_code_dbfirst_audit_20260608.md` — F2 (drawn-POI no DB door), F7 (spec-less
  registered layers). This sprint is the **UI/editor** complement to that **store-of-record** audit.
- `brain/research/viewer.md` — the layer catalog (what's first-party/curated vs reference/imagery).
- `northstar/editor_architecture_contracts.md` — C1/C2/C5/C6 + `editor_is_the_viewer`.
