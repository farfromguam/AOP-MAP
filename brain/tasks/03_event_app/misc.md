park topo trace should reset tilt and rotation of map


create some sort of data dump that allows us to take db data and put to a file so that if we loose db we dont loose configured data.

this will also help new port spinup test consistancy with whats in dev.

that dump will be cleaned up and go to dev.

some items may get moved into it
IE fema houses may get moved to a polygon then dumped to file and tagged  && this should re-seed to the same dev pre prod state

-----

## Routed 2026-05-24

- Camera / preset policy belongs to `viewer_polish_carryover.md`.
- DB dump / reseed belongs to `dev_db_snapshot_reseed.md`.


---

the map starts out east down west up - good
then something rotates it north up. - bad.

the park should reset rotation to west up when clicking the zoom presets.

the park topo trace resets should not reset zoom or rotation.

## Resolved 2026-05-25

- Zoom shortcuts (`Region`, `Park`, `Pavilion`) reset to flat west-up.
- Park / Topo / Trace layer presets preserve zoom, pitch, bearing, and the
  independent 3D state.


---

need a poi viewer on the left side so that a user can browse locations and read about them.
clicking will take them to the location on the map.

## Routed 2026-05-25

- POI browser belongs to a new card: `left_panel_poi_browser.md` (Sprint 03,
  reuses the `Park` tab inside `#calendarCard` so the left-rail footprint
  doesn't grow).

---

the left side event calendar now has a transparent or no background. it should have one.

## Resolved 2026-05-25

- `.calendar-card` lost its panel chrome when the cream-surface group was
  refactored to `.search-shell, .preset-bar, .left-context-card, .hot-control`
  (commit 7a17b84) and an explicit `background: transparent` was added on the
  `.calendar-card` selector. Restored: `.calendar-card` is back in the
  cream-surface group at `website/index.html:31`, the transparent override is
  removed at `website/index.html:185`, the moss-tint tab strip still sits on
  top of the cream surface. Verifiers: `event_schedule` and `presets` both
  PASS against the post-fix viewer.
