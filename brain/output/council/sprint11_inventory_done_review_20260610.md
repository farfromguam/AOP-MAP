# Council done-review — Sprint 11 data-source inventory (x-ray)

Date: 2026-06-10. Chair: Steward. Diff: `website/data_sources.html`, `mvp/scripts/build_data_manifest.py`,
`website/data/_data_manifest.json`, the three `brain/tasks/11_client_convergence/*.md` cards, the
`handoff/session_context.md` pointer. Card: `tasks/11_client_convergence/data_source_inventory.md`.
Tier: 5 seats (sprint boundary + a new classifier script + a user-facing artifact).

**Outcome: CLEAR to proceed.** 4 clear; 1 andon resolved by the gate-owner (user committed).

```
SEAT: witness        VERDICT: clear
Re-ran the generator (db: reachable 8 tables / served: 31 files) and an independent Playwright drive
(3 sections, 40 cards, stat strip 8/160/31/6/18, expanded aop_buildings → 5 real rows, 0 console/page
errors). All doneness claims hold under fresh observation.

SEAT: quartermaster  VERDICT: clear
Not a dup of _schema.json (field crosswalk vs live introspection — and the page reuses _schema.json as
its section 3). No prior inventory page among 94 *.html to extend. run_psql follows the established
per-script idiom (5 existing local copies; returns (str,bool) only to tell "DB down" from "empty").
CLIENT_LAYER/ORIGINS are documentation, not a runtime registry — nothing in website/js consumes them, so
no drift risk. C1/C2/C6 greps unchanged; no editor bundle loaded by the new page.

SEAT: mason          VERDICT: clear
C5 non-limiting: unknown file → served-other (tested), never dropped; DB-down → honest partial (tested);
unreadable file → reported not skipped (tested). Idiom matches sibling scripts byte-for-byte. The only
JS filter drops empty origin groups for layout, includes served-other in its order array → no source
class hidden; caps announce themselves. NIT (non-blocking): build_data_manifest.py:139-141 uses
`ok, _ = run_psql(...)` then branches on `_` and returns `error: ok` — names inverted vs the clean
`out, ok` on line 144. Rename `err, ok` when the file is next touched.

SEAT: scribe         VERDICT: clear
Card carries ticked acceptance + reproducible verification with observed numbers; handoff is a short
pointer (not an appended block); no-version-bump claim verified correct against sw.js (data_sources.html
not in SHELL_ASSETS → stale-while-revalidate; the mvp script isn't served; manifest lazy-fetched). Prose
plain and self-true, the user's own "paper mache" framing carried honestly.

SEAT: warden         VERDICT: andon → RESOLVED
Flagged the diff as committed (0c57f6e) while the handoff said "UNCOMMITTED", and that the
10_→20_deferred rename rode in that commit. Resolution: the commit is the USER's (the git gate is
theirs; they committed and said "you are free to work"). Rename is content-preserving — no card
directive deleted/modified (git diff DM on brain/tasks = empty). Handoff line corrected to name 0c57f6e.
Scope otherwise clean: no main.js, no sw.js bump, the risky client refactor carded but not executed.
```

Carried-forward nits (logged, non-blocking): the `err, ok` rename in `build_data_manifest.py`.
