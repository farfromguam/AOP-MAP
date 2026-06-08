# Council done-review — left POI list made STAR-ONLY (Sprint 08, Slice D)

Date: 2026-06-08
Mode: DONE-REVIEW over the diff. Chair: Steward. Tier: full worker set
(Witness · Quartermaster · Mason · Warden) — product-behavior change touching shell assets.
Result: **FULL CLEAR** (Mason after 2 andon-fixes; the rest clear first pass).

-----

## What was reviewed

User directive: *"make the list star-only … where did you get the idea that this old static code
not db powered is good to keep around? we are maintaining a bunch of spike code left and right."*

The diff (overriding Slice C's "keep published wholesale" decision, `cards_not_gospel`):
- **main.js** — removed the two wholesale unions from `collectStarredDestinations` (published `poi`
  from `publish.geojson`; event anchors from `aop_event_schedule.json`). The left POI list is now a
  single walk over the registry's ★-gated specs. Removed the now-dead `publishDataCache`; rewrote the
  collector header + two stale trails-spec comments + the event-bindings comment.
- **aop_poi_index.json** — dropped the `published_destinations` + `event_anchors` group defs + 8 dead
  blurb entries; re-emitted to HEAD's inline-`match` style so the diff is removals-only (1 ins / 60 del).
- **sw.js + index.html** — v56→v57.
- **playwright_verify_starred_poi_flip.py** + **playwright_verify_star_collector.py** — updated to the
  star-only contract (published/event groups asserted ABSENT).

## Verdicts

**Witness — CLEAR.** Re-observed every claim against the real system, including serving HEAD on a
parallel docroot (:8002) for a differential. Confirmed: clean profile renders 1 row (the seed drawn
POI), no published/event groups; `star_links_live` PASS (authoring a ★ on each of 4 reference layers
surfaces its row + survives reload); `starred_poi_flip` + `star_collector` PASS (groups absent); the
map's published layer + feature search unregressed (live DOM reads). **Correction folded:** the agent
claimed "only #pavillion" fails in `event_schedule`; the Witness proved **8 FAILs, all byte-identical on
HEAD and the working tree** (`IDENTICAL_FAIL_SETS`) — pre-existing, none caused by this diff (the
schedule JSON is byte-identical to HEAD; the diff only stopped the POI list from mirroring the schedule).
The card was corrected to "8 pre-existing Events FAILs."

**Quartermaster — CLEAR.** The change only DELETES/EXTRACTS — no second path, store, engine, or surface.
`publishDataCache` truly dead (0 refs) and removed. `normalizeLocationTag`/`eventLocationByTag`/
`eventScheduleToggle`/`firstCoordinate`/`poiGroupLabel` all still used elsewhere (Events tab) — correctly
kept. C2 holds (one collector; `buildPoiGroups`/`renderVisitorListGroup` thin renderers). C1=0 branches,
C6=0 classes/one registry/no new editor HTML. The two `publish`/`trail_centerlines` orphan entries left
in poi_index.json is the right in-scope call (no `poiIndexLookup` consumer; pre-existing).

**Mason — CLEAR (after 2 andon-fixes).** R1 andon: a stale trails-spec HEADER comment claimed "the
wholesale buildPoiGroups trails block still runs" — false; fixed. R2 andon: the trails `listRow` comment
still said "until then it is unused / the legacy block is still the live path / no behavior change this
card" — same defect class; fixed. R3: both now present-truth; grep for the lie-phrases returns 0; the
surviving "Replaces the buildPoiGroups X block" mentions are accurate past-tense history. C5/R13 clean:
`listMode:'starred'` is a permissive declared-mode dispatch (fallback emits; no throw), every 'starred'
layer pairs with `highlightable:true`; no dead code, no row-dropping filter. `node --check` passes.

**Warden — CLEAR.** Star-only honored exactly — removing BOTH non-star feeds is in-scope (they are the
exactly-two wholesale, non-DB-star inputs the prior consult identified). Co-removals (publishDataCache,
poi_index trim) are necessary, not creep. The event SCHEDULE system is intact (Events tab works) — only
the POI-list mirror was removed. Git gate clean: HEAD still `c781f59`, no commit, no attribution; the
v56→v57 bump performed by the agent (its to perform), the commit left OWED for the user. `cards_not_gospel`
handled right — Slice C's record preserved, the override recorded as a new Slice D block. Flagged the
poi_index reformat churn; the agent then **fixed** it (re-emitted to HEAD style, diff now removals-only).

## Steward synthesis

All convened seats CLEAR. Two real Mason andons (stale comment-rot adjacent to the work) and one Witness
correction (the Events fail-count) were folded; one Warden hygiene note (poi_index reformat) was fixed,
not just disclosed. The work does what the user directed — the left POI list is now exactly the
★-curated set — verified by observation in both directions (empty when nothing's starred; the row appears
when you star it). **Gate cleared.** OWED (the user's git gate): the commit, with the v57 bump.
