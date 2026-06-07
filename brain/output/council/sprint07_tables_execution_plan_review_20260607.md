# Council review — Sprint 07 execution plan (FULL CLEAR)

Date: 2026-06-07
Chair: Steward
Tier: full six (sprint-boundary architectural migration plan; runs autonomously as a ralph loop)
Under review: the `# Execution plan — slices (ready to pull)` section appended to
`brain/tasks/07_tables/tables_model.md` + the new top entry in
`brain/handoff/session_context.md`. **Plan review** (brain-only diff), like the
`gold_migration.md` review — not a code-diff review.

Goal (Steward, one line): make the Sprint 07 execution plan correct and safe before the user
runs it as a ralph loop — verify the slices, acceptance, and reuse claims hold against the
real repo.

## Result: FULL CLEAR (all five worker seats `clear`, 1 round)

No andons. Two non-blocking precision notes (the seats' own suggested wording refinements)
were folded into the plan before clearing — see "Folded in" below.

## Verdict receipts

```
SEAT: warden
VERDICT: clear
ISSUE: none
EVIDENCE: Every diff hunk traces to a card line. The contested 6-anchor migration is REQUIRED
by the card's own mechanism — place_key→core.features.source_key (tables_model.md:118-120,
:236-238) cannot resolve uniformly when only 1 of 7 tags is feature-backed (verified live).
Bounded (6 named anchors), reuses the gold spine with NO third table, non-publish via
layer='event' excluded by the publish gate (export_publish_geojson.sh:39), drops no rows
(resolver main.js:6226-6232), flagged "council to confirm" not executed. Git gate preserved
verbatim (Loop contract: "Do NOT commit," no sw.js/#appVersion bump, restore served files
byte-identical). Same served filename → no main.js change → no shell bump. Slices bounded and
sequenced (unlike gold's bounced unbounded slice 6).
NEXT: none
```

```
SEAT: witness
VERDICT: clear
ISSUE: none (one note, folded in: the file the plan says to "extend",
playwright_verify_event_schedule.py, is itself render-dependent — uses queryRenderedFeatures
via rendered_count :211/:1041 and wait_until="load" — so "extend it" must mean adding a NEW
tile-independent getSource(...).serialize() assertion, not inheriting that file's pattern; the
technique is real and proven in playwright_verify_baked_reference_author.py:11,125-127)
EVIDENCE: Live DB aop_map:55432 — core.features has source_key UNIQUE + attrs + archived_at +
geom; layer counts buildings 5 / cemeteries 8 / poi 4 (1 archived) / trails 120 / visitor 4 =
141; core.pois + publish.pois both dropped (to_regclass NULL); #pavilion → editorPois:aop-pavilion.
Resolver lines confirmed (main.js:6202/6280/6287/6360/1152/8181/8185). aop_event_schedule.json:
7 tags, 13 sessions, only #pavilion lacks inline coordinates — the 6 anchors have no
core.features row, confirming the central new finding. The serialize() technique the plan
prescribes is proven and tile-independent.
NEXT: none
```

```
SEAT: quartermaster
VERDICT: clear
ISSUE: none (one precision nit, folded in: "the REFERENCE_LAYERS loop pattern at :55/:73"
could be misread as appending a REFERENCE_LAYERS entry; the schedule arm is a sibling emit
block in the same one-writer script — the schedule is a {schema,event,locations,sessions}
document, not a FeatureCollection the loop body can emit)
EVIDENCE: C1=0 layerKey branches, C6=0 new class/registry/editor html, C2=one
collectStarredDestinations (main.js:1152). ONE card: 07_tables/ holds only tables_model.md +
breif.md, no sibling executable card (appended to the cleared card). All three referenced
scripts exist. New geometry-less importer is reuse-true (import_layer_to_core_features.py is
geometry-bearing; core.events is the WHEN junction). Anchor-migration reuses the gold spine,
no parallel registry, excluded from publish. There is NO existing schedule emitter (bake has
0 schedule refs today; the file is hand-curated source) — the plan honestly frames a new emit
arm extending the one bake, not a parallel pipeline.
NEXT: none (optional reword applied)
```

```
SEAT: mason
VERDICT: clear
ISSUE: none
EVIDENCE: Plan declares place_key/activity_key as plain text with "No CHECK/enum, no FK
constraint" (consistent across both tables + DDL + Loop contract); count==input is a live
check at import_layer_to_core_features.py:227-229; geom-required is real at main.js:6287 and
:1264, so the "never geom NULL" anchor for place-less abouts is correct, not gold-plating; 6
of 7 tags carry inline coords confirming the wrinkle the anchor-migration fixes by reusing the
gold spine (no third table); publish gate init_db.sql:263-264 confirms non-publish event
anchors stay out of publish.features. No row-dropping bake, no throw-on-unmatched, no smuggled
constraint, no dead code, idiomatic to the gold pattern. Slice 3 correctly scoped as not-DDL.
NEXT: none
```

```
SEAT: scribe
VERDICT: clear
ISSUE: none (one nit, not an andon: the handoff entry is long for a "short pointer," but it is
accurate and states true-and-owed)
EVIDENCE: tables_model.md:251-390; handoff:38-64; every cited path/line real and accurate
(resolveEventLocation 6202, stale comment literally at 6224, eventScheduleToGeojson 6280 with
geom-drop 6287, schedule load 8181, pavilion-binding move at 37/2378 both dated 2026-05-26).
Dependency verified by observation (DB core.features=141, core.pois/publish.pois dropped).
Both deltas recorded as findings not silently fixed; the decision to NOT edit the stale
comment (avoid a shell bump) is stated and tied to the gold precedent. Plan is
executor-runnable (DDL, soft-ref posture, tile-independent acceptance, run commands, Loop
contract, inherited conditions, user-owned git gate). Voice is the user's plain register.
NEXT: none
```

## Folded in (the two seat-proposed refinements, applied before clearing)

1. **Quartermaster** — Slice 1 bake bullet reworded: the schedule arm is "a new schedule emit
   arm in the same one-writer script, sibling to the `REFERENCE_LAYERS` loop" — NOT a new
   `REFERENCE_LAYERS` entry (the schedule is a document, not a FeatureCollection).
2. **Witness** — Slice 1 acceptance (b) clarified: add a NEW tile-independent
   `getSource(...).serialize()` assertion inside `playwright_verify_event_schedule.py`; do NOT
   inherit that file's render-dependent (`queryRenderedFeatures` / `wait_until="load"`)
   pattern; copy the proven technique from `playwright_verify_baked_reference_author.py`.

Both are precision-only; no substantive plan change escaped review.

## Standing conditions the loop inherits (from the gold council, reaffirmed)

- **Witness** — re-witness Slice 1's REAL verifier output before trusting "green." The
  bake-from-`core.events` path, the anchor migration, and the new tile-independent assertion
  are all new.
- **Mason** — confirm the `count==input` acceptance runs against a live apply before Slice 1
  closes; no CHECK/enum/FK introduced.

## Next (the user's, per the gold precedent)

Commit pause → ralph loop on Slice 1. The commit and any version bump are the user's git gate;
the loop does not commit.

Resumable seat subagents: warden a33830a4c30a26865 · witness a1f0beb5e80e21477 · quartermaster
a20459a603850a7ba · mason a5658ef0653ffaa76 · scribe afa1de5487b5a19fe.
