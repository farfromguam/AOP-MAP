# Extend the 9-patch imagery coverage (no cream edge on tall/wide screens)

> **Split out of `_done/pwa_qa_data_bakes.md` Item 17 — council triage 2026-06-06.**
> The other three items on that card (region-callout bake, building tiering,
> Ellis-cemetery derived bake) are DONE and verified by observation; this was the
> one open item, and it is a distinct **data-acquisition** task gated on an owner
> decision, so it earns its own card here rather than holding the closed card open.

TL;DR:
- On tall phones / wide monitors the fitted camera shows **past the imagery/terrain
  edge**, so the cream background (`#efe7d5`) bands the map edges.
- This is **data acquisition, not CSS**: the 9-patch AOI defines how far imagery /
  topo / DEM / lidar were pulled. To stop the edge showing, re-acquire at a larger
  AOI **and** widen `REGION_BOUNDS` to match (the camera leash must not exceed the
  data, or the edge just moves).

#aop #sprint #10_deferred #data #imagery #9patch #acquisition

-----

## Deferred because

Two things gate it, neither headless-actionable:

1. **Owner decision — how much bigger.** Tie the new AOI to the worst-case aspect
   ratios (tall phone portrait, wide desktop landscape) so the fitted camera never
   reaches the data edge. The user sets the target extent.
2. **Imagery + terrain re-acquisition.** Pull satellite/topo/DEM/lidar at the larger
   AOI (the heavy, network/source-gated step), then widen `REGION_BOUNDS` (the
   `maxBounds` camera leash) to match.

## Source / context

- Was `pwa_qa_data_bakes.md` Item 17 (now in `_done/`).
- `research/aop_data_bounds.md` — the current two-parcel envelope + 9-patch AOI;
  `REGION_BOUNDS` = the camera leash/maxBounds.
- Cross-links: `data_integrity_publishability.md` (Item-10 DEM swap lives there too),
  `research/viewer.md`.

## Work

- [ ] Owner sets the target AOI (how much bigger), keyed to worst-case aspect ratios.
- [ ] Re-acquire imagery + terrain (satellite, topo, DEM, lidar) at the larger AOI.
- [ ] Widen `REGION_BOUNDS` to match the new data extent.
- [ ] Honor `no_limiting_code_mvp.md` — this is an extent change, not a constraint.

## Acceptance

- [ ] On worst-case tall-phone portrait and wide-desktop landscape, the fitted camera
      shows map data to every edge — **no cream band** anywhere.
- [ ] `REGION_BOUNDS` and the acquired data extent agree (leash ≤ data).

## Verification

- Load on a tall portrait viewport and a wide landscape viewport; fit the camera to
  bounds; confirm by observation that no `#efe7d5` cream band shows at any edge.
