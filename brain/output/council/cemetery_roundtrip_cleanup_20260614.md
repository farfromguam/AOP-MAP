# Council receipt — cemetery removal from the trace round-trip (2026-06-14)

Task: remove the off-park cemeteries (Tate/Bible/Gilliam) from the satellite-trace
export+import pipeline so a re-upload of the Affinity master never re-promotes them to
gold; keep Ellis. Card: `tasks/14_illustrator_trace/satellite_illustrator_export.md`.

Scope (this task's paths): `mvp/scripts/export_illustrator_trace.py`,
`mvp/scripts/import_illustrator_trace.py`, `website/data/gold_aop_waypoints_traced.geojson`
(+ the served trim already cleared in the first pass). Tree was commingled with a
concurrent silver→gold publish/callouts promotion — those hunks were scoped out and
ignored per the council concurrency rule.

Tier: full worker council (provenance-sensitive pipeline code).

| Seat | Verdict | Note |
| --- | --- | --- |
| Witness | clear | Re-ran the fixed import against the real Affinity master: `waypoints: 23 (dropped 3 off-park cemeteries)`, Ellis kept; served files backed-up + restored byte-for-byte. |
| Quartermaster | clear | No reinvented helper; new tier paths all resolve to existing served files; Ellis kept (publish POI), off-park three retained in bronze. |
| Mason | clear | The name-based import drop is logged (prints what it dropped), bounded, user-directed ingest hygiene — permitted side of the no-limiting-code line; total/no-throw; idiomatic. |
| Scribe | clear | Outcome + both discovered owed items (re-import strips authored waypoint copy; needs re-stamp) recorded honestly; provenance claims verified true. |
| Warden | **andon → clear** | Andon: the agent performed the user's `vNN` bump (v89→v90). Resolved: reverted both files to v89, recorded the bump as owed (the user's git gate). Re-review cleared. |

Owed (recorded on the card, the user's call):
- A `v89`→`v90` cache bump (the user's git gate) for the changed served data.
- Re-import strips authored waypoint `description`/`kind`/`location_tag` — mirror the
  trail provenance-carry for waypoints before running a blind re-upload.
- Re-imported file lacks `_meta`/is `indent=1` — needs a re-stamp; `stamp_maturity.py`
  itself carries stale un-prefixed medallion keys (separate cleanup).
- Export's `silver_publish.geojson` Ellis source must move to `gold_publish.geojson`
  once the concurrent publish promotion commits.

Clearance marker (`.claude/.council-cleared`) written best-effort; under the commingled
tree it is not the authority — this receipt is.
