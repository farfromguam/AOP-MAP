# Data Integrity + Publishability

The viewer chrome is ahead of the trusted data spine.

Sprint 04 needs to pay down the publishability blockers before the event app
adds another layer of confidence theater.

#aop #04_event_app #data_integrity #publishability #sources

-----

## Source

- `../03_event_app/_done/sprint_02_critique_followups.md`
- `../03_event_app/_done/left_panel_poi_browser.md`
- `../03_event_app/_done/viewer_polish_carryover.md` Lane 7 pointer
- `../01_mvp/_readme.md` Immediate next work
- `../01_mvp/_done/community_trails_import.md`
- `../../northstar/source_register.md`

## Work

### Real Trails + Trailheads

- [ ] Replace demo/smoke `trail_centerlines` and trailheads with real source-backed AOP data.
- [ ] Promote at least one real source-backed centerline before declaring V1 publishable.
- [ ] Continue SFWDA numbered-trail-name research on the community-trails card and promote only when source posture is clean.
- [ ] Connect QGIS to `localhost:55432` and inspect source/feature tables if that is still undone locally.

### Acreage Reconciliation

- [ ] Reconcile AOP's 600+ acre public claim against the parcel envelope, deed acreage, and any related holdings.
- [ ] Record the answer in the bounds/source docs before the viewer leans on a hard acreage claim.

### DEM Source

- [ ] Swap the AWS Terrarium DEM for AOP-specific USGS 3DEP 1 m derived tiles when the current 10 m terrain stops being good enough.
- [ ] Extend terrain verifier coverage when the new source lands.

### POI Gap Pass

The Sprint 03 POI tab shipped with `info needed - revisit` placeholders.

- [ ] Resolve Event anchor placeholders: `#proving-grounds`, `#north-technical`, `#night-checkpoint`, `#photo-waypoint`.
- [ ] Resolve building placeholders: 1033, 665, and 880 Ellis Cove Road.
- [ ] Resolve cemetery placeholders: Gilliam, Bible, Tate.
- [ ] Promote synthetic activity segment labels to real named trails only after the trail-name source work lands.
- [ ] Decide whether `aop_poi_index.json` `owed_work` should render in the POI tab for non-coder review.

### Synthetic Activity Boundary

- [ ] Decide whether first-party activity hotspots are clearly synthetic/test-grade or ready for visitor-facing "activity" treatment.
- [ ] If still synthetic, badge popups and hot-button fallback honestly or hold the fallback until real GPX backs it.

## Acceptance

- [ ] Publishable trail/trailhead layers no longer depend on demo geometry.
- [ ] Acreage claim has a documented source-backed answer.
- [ ] Terrain source posture is either upgraded or explicitly deferred with reason.
- [ ] POI placeholder count is reduced or each remaining placeholder has a named owner/source path.
- [ ] Activity-hotspot UI cannot be mistaken for live or real-user data when the source is synthetic.
