# Search tags — Sprint 02 Bucket C — **shipped 2026-05-23**

Extend the viewer's feature search so hashtag-style tags resolve to the right
feature. Before this card, the search indexed `name` (and `gnis_name`) only —
typing `pavilion` landed on the pavilion location, but typing `#pavilion`
landed on nothing. The event-schedule vocabulary in
`website/data/aop_event_schedule.json` already speaks in tags
(`#pavilion`, `#registration`, `#observed-trailhead`, …) and the brain triage
flagged this as a duplicated user dump item.

#aop #tasks #02_edit #search #tags

-----

## Source

- `_readme.md` — Bucket C in the Sprint 02 triage.
- `tasks.md` — *"search should be able to search tags"* + *"ability to
  search tags"* (the same line twice — a duplication the user used as a
  signal of priority).
- `../01_mvp/event_schedule_layer.md` — owns the tag vocabulary that this
  card makes searchable.
- `research/viewer.md` "Feature search" — the section this card extends.

## What this card builds

The search index already groups one row per named feature. This card adds a
parallel **alias list** per row, so a search query can match either the
display name *or* any alias.

Concretely:

1. `indexFeatures(data, kindFor, toggleFor, featureListBindingFor)` gains a
   trailing optional `aliasesFor(props) → string[]` argument. The returned
   strings are stored on the index entry as `aliases`.
2. Event-schedule indexing (the call site that registers anchors and
   sessions) passes `location_tag` as the alias for anchors. Sessions stay
   indexed by title (no per-session alias spam — searching `#pavilion`
   should land on the pavilion, not produce twelve hits for every Friday /
   Saturday / Sunday session that staged there).
3. `buildSearchGroups()` merges aliases into the group it builds, so a
   multi-segment feature carries the union of its segments' aliases.
4. `renderSearchResults()` matches the query against the group's display
   name *or* any alias.
5. Query normalization: queries are matched case-insensitively. A leading
   `#` in the query is honored — `#pav` still matches `#pavilion`. A
   tag-only query (starts with `#`) skips name matching and goes alias-only,
   so the dropdown stays tight.

The result row UI is unchanged at first pass: the display name still shows,
and the kind badge already speaks to "event location" vs "trail". A future
pass can add a "via #tag" hint if the user wants disambiguation between
two anchors that share a label (none exist today).

## Decisions

### 1. Anchors only, not sessions

**Decided:** Index each event-schedule **location anchor** with its tag as
an alias. Do not index `location_tag` or `route_tags[]` on the session
features.

Why: typing `#pavilion` returns one result (the pavilion anchor) instead of
the dozen sessions that happen to start or route through pavilion. Sessions
remain searchable by their title (the current path).

### 2. Aliases as a per-row list, not a global tag map

**Decided:** Store aliases on the index entry. Don't build a parallel
`tagIndex` keyed by tag → entries.

Why: the matching path is already one substring sweep across the
`searchGroups` list. Adding a parallel index doubles the data structure
without changing the matching algorithm. The alias list per row is fine
until the dataset grows past a few hundred named features (today ~127).

### 3. POI editor stays out of scope here

**Decided:** Drawn POIs continue to be indexed by their `name` (currently
the category string). A future card can add a user-editable tag field on
POI properties; that's a data-model change with PostGIS write-back
implications, not a search change.

Why: the triage's POI-tags phrasing was illustrative. The vocabulary that
actually exists today is the event-schedule tag set. Promoting POIs to
carry tags is a separate decision — and lands in the editor card, not this
one.

### 4. Aliased locations get their own row

`#registration` is a `alias_of: "#pavilion"` location with its own label
("Registration Desk"). `eventScheduleToGeojson` already emits **two**
anchor features (one per non-hidden location), so the search index gets
two rows — one named "AOP Pavilion / G-Central" aliased by `#pavilion`,
and one named "Registration Desk" aliased by `#registration`. They sit at
the same coordinates; flying to either lands the same place but the label
the user sees in the dropdown is the right one for the tag they typed.

`#pavillion` (misspelling alias) is `hidden: true` so it does not emit an
anchor — but if a user types `#pavillion` in the box, no match. If that
shows up in the wild, the fix is to index hidden aliases as extra alias
strings on the base location's anchor entry. Out of scope for the first
pass; captured here.

## Scope

In:
- `website/index.html` only.
- `indexFeatures` + `buildSearchGroups` + `renderSearchResults` + the
  event-schedule indexer call site.
- Verifier coverage in `mvp/scripts/playwright_verify_search.py`.

Out:
- POI editor tag field (see Decision 3).
- Visitor-context callout tags (no hashtag vocabulary in their data).
- A "via #tag" hint in the dropdown row (UI polish; deferred until a real
  collision exists).
- Hidden-alias passthrough (Decision 4 caveat; deferred until reported).

## Acceptance

- [x] Typing `#pavilion` returns the pavilion anchor as the first (and only)
      result and flies the map to its coordinates. Verifier:
      `count=1 results=['AOP Pavilion / G-Central\nevent location']`.
- [x] Typing `#registration` returns the Registration Desk anchor (label
      shows "Registration Desk", same coords as pavilion). Verifier:
      `count=1 results=['Registration Desk\nevent location']`.
- [x] Typing bare `pavilion` still returns the pavilion anchor (name path
      unchanged). Verifier: surfaces both pavilion and the
      "Observed trail finish near pavilion" anchor by name substring —
      same behavior as master.
- [x] Typing `#observed-trailhead` returns the trailhead anchor.
- [x] A `#tag` query does not surface sessions that *use* that tag — only
      the anchor. Tag-only mode in `searchGroupMatchesQuery` skips the name
      path so session titles containing the same word do not pollute the
      dropdown.
- [x] Typing the `#`-prefix `#pav` still substrings into `#pavilion`.
- [x] `playwright_verify_search.py` extended with five new sections (tag
      `#pavilion`, `#registration`, `#observed-trailhead`, prefix `#pav`,
      bare `pavilion`, and a fly + auto-enable round trip). All new
      assertions PASS, zero console errors. Pre-existing FAIL
      ("multi-segment trail collapses to one result", from master) confirmed
      unrelated — same failure reproduces on master before this diff.

## Verification

`python3 mvp/scripts/playwright_verify_search.py` (server on 8001). New
sections assert the tag queries above. Screenshots land in
`brain/output/playwright_search_tag_pavilion.png` and
`brain/output/playwright_search_tag_registration.png`.

## Related work

- `_readme.md` Bucket C — triage source.
- `../01_mvp/event_schedule_layer.md` — tag vocabulary lives in its JSON.
- `research/viewer.md` "Feature search" — extend this section once shipped.
- `02_edit/named_feature_tagging.md` (TBD) — Bucket D. When POIs grow a
  tag field, this card's indexer hook is where they wire in.
