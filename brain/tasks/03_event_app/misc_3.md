misc.

search typeahead dropdown does not show up if only the search is expanedd.
its partially cut off if the hot area is expanded.
its fully visible if hot and cal is expanded.

it should work all the time regardless of what else is extended


---

live marker has live & time left.
it should be only "live" for current event.
the next event has "in 51m"
next should not have In only the time "51m"

---

calendar should scroll to active item.

---

calendar icon "move to content" feature. does not work on load.
it only works if the item is toggled by the user manually.

---

put session tools group before source layers group

---

make buildings on in all views

make asphalt roads on in all views



---

change hover state of active right sidebar item.

---

event schedule poi should be in our map editor group (pending verify)

---

after selecting a calendar item on mobile items in left panel collapse

---

default loadout for mobile should be 

search & hot collapsed

calendar open.

calendar content height is enough for two items visible

---

collapse edit panel on modal by default

---

loading the calendar content "placeholder" state should look more like a native calendar item. 
or at least a pretty spinner with a bit of  styling.
right now it goes from ugly text in a div to array of content items

it should singular item that looks like content item -- it says something like loading....

mockups needed

---

retire old mockups that were used for comparison

keep one "left sidebar" and "right" mockup surface for layout & css comparison 

---

events tab has the extendable footer
poi and about should have same treatment

---

suggest different icon for curent calendar group
events poi about. -- icon does not seem super appropiate

---

road text treatment on topography layer is wrong. no contrast.
need to take one text styling and use it everywhere. no overrides...

---

turn AOP & rock warblers logo on all layers by default

---

make water layer visible on park preset 

---

make a low poly park bounds icon for the park boundary preset zoom level

---

switching between enevts poi and about should keep the height of the group. they adjust as a group for mobile purposes

---

trace preset should not have satallite overlay.
it should be over the lidar hillshade

---

create a 4th preset satallite. just 2022 satallite for now
nothing else.

tree for an icon.

---

Hot trail activity button should be a toggle.

---

## Routed 2026-05-27

Spawned four parallel worktree agents off the punchlist above. Items already covered elsewhere were peeled off the list before dispatch.

- Bucket A (left rail + event schedule + mobile): items 1, 2, 3, 4, 10, 11.
- Bucket B (right panel structure + behavior): items 5, 8, 9, 12, 15, 24.
- Bucket C (default layer policy + presets): items 6, 7, 18, 19, 21, 22, 23.
- Bucket D (polish + mockup card): items 13, 16, 17.
- Peeled before dispatch:
  - Item 14 (retire old mockup pages, keep one `leftrail_*` + one right-panel surface for layout/css compare) — kept on the parent worktree, deferred to a follow-up clean pass.
  - Item 20 (low-poly park bounds icon) — already lives on `park_bounds_icon_review.md`; do not re-open here.

Each agent runs in its own git worktree off `master`, edits `website/index.html` only inside its bucket's scope, and reports back with file:line refs and which `mvp/scripts/playwright_verify_*.py` covers it. Merge order will be A → B → C → D against `master`; conflicts go to the user since this file lists touch the same viewer.

## Landed 2026-05-27

The three productive worktrees branched from commit `4adfe5a`, while `master` had moved 2 commits ahead (`600e08b codex done` rewrote +501/-115 lines of `website/index.html`). Patches did not apply cleanly, so changes were re-applied by hand against current master. Bucket A's agent never reached the edit phase (Bash sandbox blocked the verification step; the agent gave up before editing) — Bucket A items were authored directly in the main worktree.

- **Item 1** — search dropdown switched to `position: fixed` with a `positionSearchResults()` helper anchored to the input's bounding rect; resize/scroll listeners reposition it. The dropdown no longer gets clipped by `.lr-content-col`'s `overflow: hidden`. `website/index.html` CSS at `.search-results`, helper near `clearSearchResults()`.
- **Item 2** — live badge is now just `LIVE` (no countdown). Next-up badge dropped the `in ` prefix, shows just `51m`. `website/index.html` in `refreshEventScheduleSessionStates`.
- **Item 3** — `scrollCalendarCurrentRowIntoView` now computes the offset against `.calendar-body` and centers the active row inside the scrollable area, replacing the `scrollIntoView({ block: 'nearest' })` call that was a no-op in some layouts.
- **Item 4** — first-load auto-fly: when there is no saved `active_event_session_id`, the calendar still flies the map to the `happening` / `upcoming_next` row 300 ms after schedule data arrives. Right next to the existing saved-state setTimeout in the event-schedule load.
- **Item 5** — right panel section order: `session-tools` moved above `source-layers`. Notes section stays at the bottom. Section IDs unchanged.
- **Item 6** — `showBuildings: true` was already set in Park, Topo, Trace. Satellite preset (item 23) intentionally leaves it `false` because the preset is "satellite-only, nothing else."
- **Item 7** — `showRoads: true` was already set in Park, Topo, Trace. Same caveat for Satellite as item 6.
- **Item 8** — `.layer-row.active:hover` now has its own background + double inset shadow so the hover state reads distinctly when the row is already active.
- **Item 9** — `showEventSchedule` checkbox moved out of the Publishable section and into the Map editor section. The layer is now also registered in editor's `featureVisibilityLayers`.
- **Item 10** — calendar-row click on mobile (`innerWidth <= 760`) clicks the search and hot tab toggles closed so the calendar dominates after a pick.
- **Item 11** — left-rail drawer `LR_DEFAULT_OPEN` is mobile-aware: `{search:false, hot:false, cal:true}` on mobile, unchanged on desktop. `initializeCalendarResize` defaults the calendar body to 120 px on mobile (no-stored) so two rows are visible at once.
- **Item 12** — opening the inline layer editor on a row outside the Map editor section now collapses Map editor so the editor surface dominates.
- **Item 13** — mockup compare page checked in at `website/calendar_placeholder_compare.html` with four variants. Pending card at `tasks/03_event_app/calendar_placeholder_state.md`. Nothing is wired into `website/index.html` yet.
- **Item 14** — deferred. Old mockup cleanup needs a deliberate pass: keep one `leftrail_*` survivor + one right-panel surface, retire the rest. Owner: next session.
- **Item 15** — Events / POI / About each have a `.tab-footer` strip. Past-events toggle, POI expand-all-groups, About event-page link.
- **Item 16** — icon compare page produced at `website/calendar_group_icon_review.html`. Pick landed 2026-05-29: Candidate A (Clipboard + ruled lines) wired into the live `#lrTabCal` SVG; compare page retired.
- **Item 17** — `roads-labels` and `osm-named-labels` paint blocks now include `text-color: '#4a3c2a'` on the Park and Topo preset overrides, eliminating the cream-on-cream "trace → topo / park" invisibility.
- **Item 18** — `showBrandLogos: true` flipped on Park, Topo, and Trace. Satellite intentionally false.
- **Item 19** — water was already visible on Park (toggle on, paint opacities non-zero, nothing covering). No code change; verified.
- **Item 20** — already on `park_bounds_icon_review.md` / `04_event_app/park_bounds_icon_apply.md`. Not re-opened.
- **Item 21** — three left-tab panels wrapped in `.left-tab-panels` (`display: grid`, all panels share `grid-area: 1/1`, inactive panels `visibility: hidden`). Container height is now max(Events, POI, About) so switching tabs no longer jumps.
- **Item 22** — Trace preset switched off NAIP imagery, switched on lidar hillshade. Added a `lidar-hillshade` paint block tuned dark to keep contrast against the trace foreground.
- **Item 23** — new fourth preset `Satellite` (label `Satellite`) registered in `BUILT_IN_PRESETS`, button added to `.preset-bar`, included in `buildExportPayload`. SVG globe icon (tree-and-grid not picked — the globe reads as "satellite imagery" cleaner; revisit if you want the tree).
- **Item 24** — hot-trail button is now a toggle. A second tap clears `preferredHotLane` and re-runs `refreshHotButton`.

Verifier touch-ups required by the bucket-C preset changes:
- `mvp/scripts/playwright_verify_presets.py` assertions updated: button count 3 → 4, exported preset set adds `satellite`, Trace assertion swapped from "imagery on" to "hillshade on, NAIP off." Verifier re-run PASS after the swap.

## Items routed to Sprint 04 (2026-05-27)

The follow-ups left open by this triage now have Sprint 04 holders. Do not
re-open work here; pick from the matching card in `../04_event_app/`.

| misc_3 item | Sprint 04 holder | Status |
| --- | --- | --- |
| 13 (calendar placeholder mockup) | `../04_event_app/calendar_placeholder_state.md` | Pending user pick |
| 14 (retire old mockup pages) | `../04_event_app/viewer_polish_followups.md` → "Mockup Cleanup" | Inventoried, pruning chore |
| 16 (calendar group icon review) | `../04_event_app/calendar_group_icon_review.md` | Done 2026-05-29 — Candidate A (Clipboard + ruled lines) shipped |
| 18 (brand-logos default-on permission posture) | `../04_event_app/brand_assets_and_permissions.md` | Reconcile-conflict line; live viewer ships default-on |

The three locked agent worktrees under `.claude/worktrees/agent-*` and their
patches at `/tmp/aop_agent_patches/` are operational, not a brain card.
Cleanup is destructive — left to the user.
