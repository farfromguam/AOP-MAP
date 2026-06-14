# Council receipt — left-rail drawer open/close persistence (+ height verify)

Date: 2026-06-13 · Steward: main agent · Tier: core three (bounded read-core localStorage tweak + owed v-bump)

**Card:** `brain/tasks/13_viewer_extraction/viewer_drawer_schedule.md` (addendum "drawer OPEN/CLOSE persistence restored").

**Diff reviewed (in scope):**
- `website/js/viewer_core.js` — drawer block: `aop_left_rail_drawer_v1` open/close persistence (`readDrawerOpen`/`writeDrawerOpen`, `lrOpen` seeded from storage, `writeDrawerOpen()` appended to the tab-click handler).
- `website/sw.js` + `website/index.html` — shell version `v69 → v70` (owed-and-done bump; `viewer_core.js` is a `SHELL_ASSETS` file).

**Out of scope (not this council):** `website/js/viewer_band.js` — pre-existing prior-session label delta, separately cleared in `band_labels_council_receipt.md`.

**Acceptance:** user — *"on load search and clipboard are open on the left; make the open/close state saved in local storage; also persist the drawer height of the clipboard."*

```md
SEAT: witness
VERDICT: clear
ISSUE: none — every doneness claim backed by an observation the seat reproduced, not narration.
EVIDENCE: re-ran verify_drawer_persist.py against the live :8001 server → 18/18 PASS, exit 0, 0
  console/page errors. Reads real DOM .open classes + localStorage across an actual page.reload():
  BASELINE storeDrawer=None (default first-load unchanged), AFTER search=closed/hot=open +
  storeDrawer={"search":false,"hot":true,"cal":true}, height 240→432 (storeHeight=432, cssHeight=432px,
  calBodyH=432); AFTER RELOAD all survived identically. Screenshot brain/output/drawer_persist.png shows
  the reloaded state. node --check clean.
NEXT: none.
```
```md
SEAT: warden
VERDICT: clear
ISSUE: none — every website hunk traces to the card; git gate intact.
EVIDENCE: HEAD unchanged at 9274a19 (user's own commit), nothing staged, working tree uncommitted, no
  mutating git / no attribution touched. v69→v70 is the owed shell-asset bump (completion_gate L146).
  Card change is an appended addendum — prior directives preserved. Diff confined to the read core
  (viewer_core.js); no main.js, no mvp/. viewer_band.js noticed but not attributed here.
NEXT: none — commit + version-label commit remain the user's git gate.
```
```md
SEAT: quartermaster
VERDICT: clear
ISSUE: none — extended existing machinery; no duplicate engine/key/state.
EVIDENCE: aop_left_rail_drawer_v1 (viewer_core.js) is the same key main.js reserved as
  LEFT_RAIL_DRAWER_KEY; readDrawerOpen tolerates the old {open:{...}} envelope (a real port).
  readJsonStore/writeJsonStore NOT imported — new helpers mirror the sibling height-pref shape
  (readStoredHeight/writeStoredHeight, aop_lr_card_height_v1). Single lrOpen state, unchanged lrRender,
  one window.lrReflow. C1=0, C6=0 new class/HTML, C2 one collector. node --check passes.
NEXT: none.
```

**Steward verdict:** CLEAR (all convened seats clear). The full `website/mvp` working-tree diff is now council-cleared — the band label delta (`band_labels_council_receipt.md`) plus this drawer change. Marker written to `.claude/.council-cleared`. The `v70` bump and the commit remain the user's git gate (UNCOMMITTED).
