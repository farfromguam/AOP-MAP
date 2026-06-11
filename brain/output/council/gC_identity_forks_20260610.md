# Council receipts — G_C slice (collapse identity forks)

Date: 2026-06-10 · HEAD `bcea502` · Tier: **full six** (publish-zone identity data; highest-risk slice, "do last").
Marker `.claude/.council-cleared` = `7eecec92068aff8972c3269d109ee1634977862a` (covers the combined uncommitted
G_meta + G_C batch). G_meta had cleared its own council earlier; G_C grew the diff, so this clears the whole batch.

Goal: one canonical `id` per real-world feature (`spec.idField == panel key == DB source_key business part`);
collapse the cemetery parcel/marker twin's non-unique id; the live editor must still resolve/star/edit the RIGHT
single feature after the id changes. Findings: `served-id-heterogeneous-no-canonical-key`,
`cemetery-parcel-marker-twin-nonunique-id`, `ellis-cemetery-multi-id-across-files`,
`buildings-served-id-is-attrs-businesskey-not-pk`, `two-editor-sinks-opposite-homes` (already done by Approach-C),
`publish-kind-taxonomy-fork`.

## Verdicts — FULL SIX CLEAR (no andons)

```
SEAT: witness        VERDICT: clear
```
Re-drove the live host bridge himself: marker props → `cemeteries:093 001.02:marker`; parcel props → `:parcel`;
a BOGUS id → `ok=false`, store empty (proves real `findFeatureById` resolution, not a string echo of the test
input). Re-ran `playwright_verify_gC_identity.py` → 20/20 PASS on :8001. Own geometry-matched diff vs HEAD: 0
features dropped/added, 0 geometry change, delta within {id, kind, category, same_as, maturity, uuid}. Cemetery ids
unique (HEAD had `093 001.02` twice). `export --check` NO REVERT ×6. DB 160/159/1 (1 archive pre-existing). **Process
flag (not a defect):** the served reference files can transiently revert to HEAD content between/among concurrent
bake runs — the DB is the source of record; re-run `export_publish_geojson.sh` to materialize the served tree before
reviewing. (Orchestrator re-confirmed the current on-disk state is the correct fixed point.)

```
SEAT: warden         VERDICT: clear
```
**Ruled the flagged cemetery-parcel non-archive a justified loss-free reading, NOT a deleted directive**, on three
grounds: (1) the directive's actual target — the non-unique shared id — IS fixed (HEAD had 4 colliding bare-parcel_id
ids; WORK has 8 unique); (2) archiving the parcel would gate-drop its served polygon (the bake excludes
`archived_at IS NOT NULL`), which the additive contract forbids — choosing the loss-free mechanism is independence on
the means, not dropping the ends; (3) the deviation is named verbatim in the card + status log, not buried. Git gate
untouched (HEAD `bcea502`, no bump — still v62, no attribution, no `down -v`/DROP/TRUNCATE/DELETE). main.js delta = 6
non-comment lines (the cemetery-id rebind), rest comments. G_D/G_F untouched.

```
SEAT: quartermaster  VERDICT: clear
```
One id scheme: the canonical id is the existing DB `source_key` business part, derived inline in the ONE bake overlay
(`ID_OVERLAY`) — no second crosswalk/mint. `main.js` flips the existing `FEATURE_LIST_LAYERS` cemeteries
`idField parcel_id→id` (1 registry, unchanged) and routes through the one `positionedFeatureIdFor` resolver. C1=0 /
C2=1 / C6=0 greps at target; no new `*.html`. `POI_KIND_MAP` is a 2-entry display map, not a taxonomy engine. Finding
5 left as Approach-C did it (not redone); the apply-script edit is the cemetery door resolver in place (4 layerkey
branches HEAD and WORK), no forked path.

```
SEAT: mason          VERDICT: clear
```
Additive / non-limiting: `POI_KIND_MAP` touches only `layer='poi'` rows, `if k in POI_KIND_MAP` skips unknown
(passthrough, no throw/whitelist-drop), original class preserved additively in `category`; `park_boundaries:ellis-inholding`
correctly keeps `kind=cemetery`. id overlay `regexp_replace` never coerces blank (no-op on a prefix-less key → full
source_key). No DELETE/TRUNCATE/DROP; parcel row + polygon stay served. No orphaned parcel-id resolver. Idiomatic;
verifier lean (no networkidle). `node --check` both JS OK. **Non-blocking craft note:** the comment at `main.js:3899-3905`
still narrates the old parcel-dedup regime the idField flip superseded — stale comment only, code correct; worth a
one-line refresh in a later pass.

```
SEAT: scribe         VERDICT: clear
```
All 6 G_C checkboxes flipped with acceptance results + finding ids; finding 5 recorded honestly as "already done by
Approach-C, not redone"; the cemetery-parcel deviation + loss-free rationale recorded plainly in card + handoff +
audit; shared v62→v63 bump stated (strings still v62), HEAD `bcea502` named, file batch listed and correctly separating
G_meta's files. Trails "id unchanged" verified honest (id↔geometry binding preserved; the index-0 shift is pure
`ORDER BY`). References are concrete/grep-able. **Non-blocking voice note:** the records lean heavily on **bold** key
terms (the one AI tell the voice guide flags) — trim to the load-bearing term per entry if they keep growing.

```
SEAT: steward        VERDICT: clear
```
Product lens: the slice serves the promise (trustworthy, source-traceable map) by giving every feature one canonical
identity — the root of the recurring twin bugs — while preserving every geometry and all provenance (loss-free). The
cemetery-parcel call is correct: identity-of-record on the marker, polygon kept as related geometry, no data lost.
Tier (full six) right for publish-zone identity. Synthesis: every convened seat clear, no andon.

## Outcome
**FULL SIX CLEAR.** Owed — the user's git gate: the SAME uncommitted **v62→v63** bump (G_C rides the G_meta batch;
no second bump), not made. Non-blocking follow-ups recorded (not gating): the stale `main.js:3899-3905` comment, the
bold-key-term voice density, and the Witness's "materialize served tree from the DB before review" process note.
With G_C done, normalization is functionally complete — only **G_D** (destructive fresh-volume parity, the user's
explicit call) and the deferred-lows remain.
