# Slice 5 — Hot now (Event lane) into the drawer

TL;DR:
- Port the **Hot now** control into the drawer's third tab: the **Event lane** — "Live event" / "Starting
  soon" / "Next event" — driven by the same clock + schedule the calendar already carries. Clicking it
  flies to the session (`gotoEventSession`).
- **Defer the Trails lane.** It toggles the `activity-hotspots` layer (raw GPS evidence,
  `permission=internal / publish_status=hold`) — which slice 1 did not carry. Whether that layer is part
  of the published read product is the user's call (sprint readme **fork 2**). `refreshHotButton` is
  already designed to degrade to event-only when there's no hotspot data, so the Event lane ships cleanly
  alone.
- Wires the `refreshHotButton()` hook the schedule slice already calls behind its `typeof` guard.

#aop #sprint #13 #viewer #hot #slice

-----

## What to build

**`website/viewer.html`** — add the **Hot tab** (3rd icon, from `index.html:92-98`) and the `lrPanelHot`
with the `hot-control` (the **event button only** — drop `#hotTrailButton`). `LR_CARDS` becomes
`['search','hot','cal']`; the icon column reserves 3 tab-heights. Hot defaults **closed** (matching the
live desktop default; the auto-open-on-data needs the `lrOpenCard` persistence hook, slice-6 polish).

**`website/css/viewer.css`** — pull the `.hot-control*` / `.hot-lanes` / `.hot-button*` rules from
`app.css:820-853` (the trail-specific `[data-hot-lane="trails"]` rules can come too, harmless).

**`website/js/viewer_core.js`** — port the Event-lane machinery from `main.js`:
`HOT_BUTTON_IMMINENT_MIN`/`HOT_BUTTON_SESSION_LEN_MIN`, `eventScheduleAnchorForward`,
`computeHotButtonTarget`, `hotEventAvailable`, `attachHotButton` (event button only), and
`refreshHotButton` **simplified to the event lane** (the hot-now/coming-up branches; the control hides when
no event is available). All its deps — `eventSessionById`, `eventScheduleNow`,
`eventScheduleFormatMinutes`, `gotoEventSession` — are already in the core. Add `'hot'` to `LR_CARDS`.

**Drop (Trails lane — fork 2):** `hotspotPolygonCentroid`, `hotspotMetersBetween`,
`findDensestHotspotCluster`, `trailHotspotsActive`, `setTrailHotspotsVisible`, `hotButtonFlyToHotspots`,
`selectedHotLane`/`preferredHotLane`, and the `aopActivityHotspotsData` load + the activity-hotspots
layer. Drop the `window.AOP_UI?.hot` copy lookups (use the literal fallbacks).

## Acceptance

- [x] The Hot tab opens a panel; pre-event it shows **"Next event"** (coming-up); a during-event `?clock`
      shows **"Live event"** (hot-now). Observed.
- [x] Clicking the Hot event button flies to the session (same path as a calendar row).
- [x] The Trails lane is absent (no `#hotTrailButton`, no activity-hotspots layer) — documented as fork 2.
- [x] **0 console/page errors**; `index.html` untouched; no editor seam carried.
- [x] Line-cost recorded.

### Done — 2026-06-13 (slice 5 shipped, verified by observation)

**Files (built alongside; `index.html`/`main.js` untouched):** `viewer_core.js` 1848 → **1969** (+121) ·
`viewer.html` +25 (Hot tab + panel) · `viewer.css` +21 (hot-control rules).

**Verification (real running system).** `/tmp/verify_viewer_hot.py`, `?clock=` fixtures: **11/11 PASS, 0
console errors.** Pre-event: Hot tab opens, `data-hot-state="coming-up"`, title **"Next event"**.
During-event (`?clock=2026-06-20T14:00`): `data-hot-state="hot-now"`, title **"Live event"**, detail
**"Proving Grounds / comp gates · 1h left"**; clicking the button opens the session popup. Screenshots
`viewer_hot_{pre,live}.png` — the rust HOT NOW lane with the flame glyph above the calendar's LIVE row.

**Line-cost.** +121 in `viewer_core.js`: `computeHotButtonTarget` + `eventScheduleAnchorForward` + the
constants (~50), `refreshHotButton` event-lane (~55), `attachHotButton` + `hotEventAvailable` (~16). The
Hot Event lane is cheap because its whole engine — `eventSessionById`, the clock, `eventScheduleNow`,
`eventScheduleFormatMinutes`, `gotoEventSession` — was already carried by the schedule slice; Hot is a thin
new view over it. It wires the `refreshHotButton()` hook the schedule already called behind its `typeof`
guard, so the lane updates on every 60s tick in lockstep with the calendar.

**Deferred — the Trails lane (sprint readme fork 2).** It toggles `activity-hotspots` (raw GPS evidence,
`permission=internal / publish_status=hold`) which slice 1 did not carry. Dropped with it:
`hotspotPolygonCentroid`/`hotspotMetersBetween`/`findDensestHotspotCluster`/`trailHotspotsActive`/
`setTrailHotspotsVisible`/`hotButtonFlyToHotspots`/`selectedHotLane`/`preferredHotLane` and
`aopActivityHotspotsData` — none ported, so no dead trail code rides along. `#hotTrailButton` is not in the
markup; `data-lane-count="1"`. The Trails lane lands if/when the user draws the published-layer line to
include `activity-hotspots`.

**Owed / git gate.** UNCOMMITTED (the user's gate). `viewer.html` still not in `sw.js` → **no `#appVersion`
bump owed.** Remaining slate: POI (slice 4), Locate/Install/version (slice 6), the swap (slice 7).

### Addendum — 2026-06-13 (FORK 2 RESOLVED by the user: Trails lane + hotspots restored)

User: *"put our hotspots back in the viewer. this is basically THE feature of the app — discovery of where
the cool spots are known to be."* That settles sprint-readme **fork 2**: the published-layer line
**includes** `activity-hotspots`. The deferral above is reversed — the hotspots layer and the Hot **Trails
lane** are now carried.

**Restored:** the `activity-hotspots` source + 4 layers (heat / fill / outline / labels, default OFF,
`main.js:8017`) in the layer build — added after contours so the heatmap sits beneath roads/trails, same
z-order as live. The full two-lane Hot control: `hotspotPolygonCentroid`/`hotspotMetersBetween`/
`findDensestHotspotCluster`/`trailHotspotsActive`/`setTrailHotspotsVisible`/`hotButtonFlyToHotspots`/
`selectedHotLane`/`preferredHotLane`, and the trail branches of `attachHotButton`/`refreshHotButton`. The
`#hotTrailButton` markup + the trail-lane CSS are back. **Severance kept:** the live page's
`activityHotspotsToggle` checkbox is replaced by `setLayerVisibility` over `ACTIVITY_HOTSPOT_LAYERS`;
`trailHotspotsActive()` reads the live layer visibility. **Improvement over main.js:** `activity-hotspots`
is NOT in `PRESET_LAYERS`, so a preset switch no longer turns the hotspots off — the discovery layer
persists once the user reveals it (independent of presets, like 3D).

**Verified by observation.** `/tmp/verify_viewer_hotspots.py`: **8/8 PASS, 0 console errors.** The Trails
lane reads "Where rigs spent time"; tapping it sets `data-hot-on="true"` (derived from the live layer
visibility), the glyph → ✓, title → "Trail activity on", and the camera flies to the densest dwell
cluster; a second tap hides it. Screenshot `brain/output/viewer_hotspots_on.png` — the moss active Trails
lane + the amber hotspot cells on the map.

**Line-cost.** `viewer_core.js` 1969 → **2151** (+182) · `viewer.html` +9 (trail button) · `viewer.css` +3.

## Verification

- Playwright: default load → click Hot tab → `#hotControl` not hidden, `#hotButton[data-hot-state]` =
  "coming-up", title "Next event". `?clock=2026-06-20T14:00` → `data-hot-state`="hot-now", title
  "Live event"; clicking it opens the session popup (fly). Screenshot. 0 console errors.
- _(fill in on completion: line counts, what was deferred.)_

## Notes

Built alongside; no commits without the user's git gate; `viewer.html` not in `sw.js` → no `#appVersion`
bump owed. The **Trails lane** lands if/when the user draws the published-layer line to include
`activity-hotspots` (fork 2). Remaining slate: POI (slice 4), Locate/Install/version (slice 6), the swap
(slice 7).
