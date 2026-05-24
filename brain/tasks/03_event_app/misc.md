park topo trace should reset tilt and rotation of map


create some sort of data dump that allows us to take db data and put to a file so that if we loose db we dont loose configured data.

this will also help new port spinup test consistancy with whats in dev.

that dump will be cleaned up and go to dev.

some items may get moved into it
IE fema houses may get moved to a polygon then dumped to file and tagged  && this should re-seed to the same dev pre prod state

-----

## Routed 2026-05-24

- Park / Topo / Trace camera reset belongs to `viewer_polish_carryover.md`.
- DB dump / reseed belongs to `dev_db_snapshot_reseed.md`.


---

the map starts out east down west up - good
then something rotates it north up. - bad.

the park should reset rotation to west up when clicking the zoom presets.

the park topo trace resets should not reset zoom or rotation.