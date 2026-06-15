---
session: smores-at-firepit
status: done
claim: website/data/aop_event_schedule.json (fri-fire + sat-fire location_tag)
started: 2026-06-14T19:10
---

User: "Smores should be at the firepit. what happened?" The v87 batch tagged the
PRO Line race to #firepit but left both "Fire + s'mores" sessions at #pavilion.
Source (brain/import/TBI.copy) says they "head to the fire pit for some smores".

- 19:10 claimed aop_event_schedule.json; retagged fri-fire + sat-fire #pavilion → #firepit.
  Tree is commingled with a live session's viewer_core.js "clear-search-defocus"
  feature (+ its v90→v91 bump in sw.js/index.html). I did NOT touch those — the v91
  bump already re-keys DATA_CACHE so my data change rides it; no second bump.
- Verified by observation on :8001 — brain/output/verify_smores_at_firepit.py 12/12
  PASS, 0 console errors (both s'mores sessions resolve to firepit coords; firepit
  anchor renders; PRO Line regression holds; calendar row drives to firepit + active).
- DONE → next: nothing owed for this slice. (The data fix is served-only; raw/ has no
  event schedule, so no DB/raw durability gap.)
