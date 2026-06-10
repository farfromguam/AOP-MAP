# Council receipts — G_E events overlay convergence (2026-06-10)

Slice: `brain/tasks/06_going_gold/gold_slice6_backlog.md` G_E + the G_A "Event umbrella metadata → core.events row" item.
Reviewed diff: all uncommitted changes vs HEAD `1cbd439 "v61"` (the G_E slice + the in-tree v60→v61 bump correction).
Tier: **full six** (publish-zone served data + DB schema addition + live-viewer JS refactor).
Result: **FULL SIX CLEAR** (Mason andon'd once on a dead local → fixed + re-reviewed → clear).

-----

```md
SEAT: witness
VERDICT: clear
ISSUE: none — every "verified/works/done" claim points at an observation of the real running system that I
  independently re-ran and watched fire, not narration or re-derived math.
EVIDENCE: LIVE `--baked` re-run (mine, :8001) 14/14 PASS against live DOM — fresh empty localStorage proven
  ({tags:None,pois:None}), #pavilion session resolves to baked [-85.7482512,35.0907264], 4 route LineStrings on
  BOTH embedded + standalone, 0 console errors. LIVE `export_publish_geojson.sh --check` exit 0, "NO REVERT" all
  6 files incl aop_event_schedule.json, "Event umbrella: read from core.event_meta". LIVE DB: event_meta 1 row,
  events 13/activities 12/features active 159. "7 fails pre-existing" independently confirmed: HEAD served via
  git archive on :8009 + current verifier = 9 FAIL; working tree = 7 FAIL (strict subset); the 2 deltas are the
  diff's own new baked-coord assertions HEAD can't satisfy. Zero new fails introduced.
NEXT: none for the Witness lens — clear.
```

```md
SEAT: warden
VERDICT: clear
ISSUE: none. Every hunk traces to a G_E card line; the git gate is untouched; the DB change is additive; no card
  directive deleted or weakened.
EVIDENCE: HEAD intact at 1cbd439; no loop commit/reset/amend; all recent commits authored by the user, no agent
  attribution, no co-author trailers in the diff. Version bump owed-not-committed: HEAD's sw.js/#appVersion read
  v60 (the bump was missing from the committed "v61"); working tree corrects both to v61, uncommitted, not
  re-bumped. No destructive DB action (no down -v / DROP / TRUNCATE / DELETE); core.event_meta is CREATE IF NOT
  EXISTS + idempotent upsert. main.js = single hunk in the resolver region; panel.js = single hunk in
  resolveEventSchedule. Card unmodified — no directive softened.
NEXT: noticed (not breaches): card line 80 phrased the home as `core.events` row while impl landed `core.event_meta`
  table — reconcile in card text (done in the post-council write-up). Owed v60→v61 bump + commit stay the user's.
```

```md
SEAT: quartermaster
VERDICT: clear
ISSUE: none. Genuine convergence, not duplication. `event_schedule_geojson.js` (window.AOPEventSchedule) is the
  single document→GeoJSON transform; both surfaces DELEGATE with old implementations DELETED (not dormant).
EVIDENCE: main.js (6279–6318) deleted ~120 lines of its own resolver (resolveEventLocation/buildEventLocationIndex/
  eventDayShort/formatEventStartLocal/composeEventWindowLabel/eventRouteCoordinates + inline FC builder);
  eventScheduleToGeojson now a thin wrapper. panel.js: stripped resolver + roleForTag GONE (grep roleForTag = 0).
  Umbrella one home: init_db core.event_meta (soft event_id, no FK/CHECK); export heredoc demoted to
  EVENT_META_FALLBACK; seed_event_meta.py reuses the importer's SQL helpers verbatim. C1 layerKey branches in
  main.js = 0; C6 no new class, no new registry, no new editor *.html. Sole writer of aop_event_schedule.json
  remains the bake's SCHED_OUT. node --check passes on all 3 JS.
NEXT: none — clear.
```

```md
SEAT: mason
VERDICT: clear (after andon bounce)
ISSUE (first pass, andon): one dead local — `const normalizeLocationTag = window.AOPEventSchedule.normalizeLocationTag;`
  at main.js:6292 had zero call sites and a false justifying comment.
FIX: removed the alias line + the false comment sentence; node --check main.js PASS; grep normalizeLocationTag = 0.
EVIDENCE (re-review): comment block flows into hostResolveTagCoords; eventScheduleToGeojson wrapper intact,
  identity preserved. No CHECK/enum/validator/row-dropping filter; no throwing strategy; no remaining dead code.
  First-pass clears that stand: C5/no-limiting clean (event_meta DDL has no constraint gating data; resolver/seed
  never throw/drop on unknown values — NULL activity_key / missing tag pass through); bake umbrella read falls back
  to heredoc (matches the DB row 1:1, no silent divergence); compositing parity (the {geojson,locationByTag,
  sessionById} return re-populates the host maps the 5 consumers read); idiomatic IIFE + window namespace.
NEXT: none — clear.
```

```md
SEAT: scribe
VERDICT: clear
ISSUE: durable artifacts exist and are honest; provenance loss-free; references treated as the thing; voice plain.
  Three cosmetic sub-notes (none andon), all addressed in the post-council write-up.
EVIDENCE: Provenance loss-free (hard catch) — served event{}/schema/status/updated_at byte-identical across HEAD,
  working file, and the old heredoc (all 10 owner-authored keys carried, incl. caveat/source_context/source_summary);
  7 location tags, 0 keys dropped, #pavilion only GAINED coordinates; 13/13 sessions preserved in order, 0 keys
  dropped, only `activity` ADDED. core.event_meta has an attrs jsonb catch-all (no allowlist); seed routes non-column
  keys into attrs. Recorded: design doc records the actual convergence (consumer map, the one transform, the DB home);
  verifier assertions name the finding ids verbatim; receipts/logs/screenshots on disk. References verbatim in the
  audit catalog and addressed (not paraphrased). Voice plain, no marketing gloss. node --check clean on all 3 JS.
NEXT (post-council write-up, done): soften design-doc "DELETED"→"delegating wrapper" and "init_db carries the seed
  INSERT"→"DDL only; seeded by seed_event_meta.py"; record the card acceptance as observed with the 7 fails noted
  pre-existing; state the user's git gate (the v60→v61 bump the prior batch owes; commit stays the user's).
```

```md
SEAT: steward (chair, product lens)
VERDICT: clear
ISSUE: none. Serves the promise — make the map trustworthy before interactive. Event data moves into the DB store
  of record; localStorage demoted to a working buffer (the validation-loop discipline: observations don't overwrite
  truth). The owner-authored umbrella provenance (id/label/source_context/source_summary/caveat, incl. the
  "proposed planning context only; confirm before publishing as official" caveat) is carried DB→bake→served
  loss-free (Scribe-confirmed) — publishability preserved. Tier was correct for publish-zone data. No northstar
  drift, no app-before-trustworthy-map inversion.
NEXT: G_B is the next slice (the one DB home now exists). Clear to proceed.
```
