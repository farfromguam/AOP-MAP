# AOP Map Northstar

TL;DR:
- Build a serious AOP map before building an app.
- The first product is a trustworthy source-traceable map: PostGIS spine, QGIS cartography, print board, read-only web map.
- Community or rider submissions wait until the whiteboard validation loop proves what people actually contribute.

#aop #map #northstar #gis

-----

The promise: make the map trustworthy before making it interactive.

Adventure Off Road Park is private land. Public trail data will be incomplete, stale, licensed awkwardly, or all three. The map succeeds only if every line carries where it came from, how much we trust it, and whether it can be published.

## Locked shape

PostGIS is the living data spine once the project leaves pure prototype mode.

QGIS is the cartography and editing surface.

Print V1 is a large-format validation board.

Website V1 is a static read-only MapLibre view of publishable layers.

Website V2, if it happens, is submission and moderation. It does not come first.

## Product tests

A usable AOP map must let a reader answer:

- What is this line?
- Where did it come from?
- Is it official, observed, inferred, or guessed?
- Can we publish it?
- When was it last checked?
- What would close the uncertainty?

If the map cannot answer those, it is drawing faster than it is learning.

## Validation loop

Observations do not overwrite trails directly.

Board marks, GPX rides, app checks, photos, rider notes, and field corrections land as observations. Review promotes them into core map layers when the evidence holds.

That is the difference between a living map and a rumor collector.
