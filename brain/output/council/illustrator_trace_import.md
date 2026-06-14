# Council receipt — first real Affinity hand-trace import (2026-06-14)

Work: ingest the user's first real Affinity-Designer-saved hand-trace SVG
(`brain/import/trace_upload/aop_satellite_trace.svg`) back into GeoJSON, using
object names as truth and preserving gold provenance. Importer hardened for
Affinity's export. Card: `tasks/14_illustrator_trace/satellite_illustrator_export.md`.

Diff reviewed (this session only; tree is commingled with a concurrent
landcover-trace session + the v83 five-item review — those paths were scoped OUT):
- `mvp/scripts/import_illustrator_trace.py` (+110/−33 — Affinity hardening)
- `website/data/aop_trail_network.geojson` (130 trails: 120 gold carried, 10 new)
- `website/data/aop_waypoints_traced.geojson` (26, NEW), `aop_buildings_traced.geojson` (6, NEW)
- `brain/output/verify_ingest_viewer.py` (NEW verifier) + `_verify_ingest*.png`, `_verify_viewer.png`
- card + `handoff/session_context.md` records

Tier: **full six** (provenance-bearing served data + non-trivial importer logic).

| Seat | Verdict | Note |
| --- | --- | --- |
| Witness | **clear** (after one andon) | Andon on the card's "0.7 cm round-trip" wording — that figure was the importer's *in-memory* self-round-trip, not a measure of the committed file. Live-vs-HEAD: unedited vertices on a ~1–2.4 cm SVG 2-decimal-metre floor, Ground Control hand-edited ~1 m, 3 ids vertex-count-changed (incl. the 67 split). Card corrected → re-reviewed, independently re-measured, **clear**. All other claims (130/26/6 counts, provenance on 120, viewer PASS 0 fatal errors, overlay placement) verified by direct observation. |
| Warden | **clear** | Scope on-farm (Affinity hardening IS the ingest). Git gate untouched — the `git show HEAD:… > file` baseline restore is read-only `git show` piped to a file write, not a mutating git op; HEAD still `084e794`, nothing staged. Owed items correctly reported, not silently done. |
| Quartermaster | **clear** | Reuses `path_points`/`parse_transform`/`apply`/`utm_to_geodetic`/`ai_escape`; extends the ONE importer in place; no fork, no second engine; new verifier is distinct. C1/C2/C6 grep contracts at target (Python diff doesn't touch `main.js`). |
| Mason | **clear** | No row-dropping filters (the length checks are degenerate-geometry guards; the stray-circle sweep + 4-rung provenance chain only ever *grant*, never drop). Number-prefix strip is safe (fires only when leading int == trail_number). `load_meta` epsg assert is a frame-sanity fail-loud, not a per-row vocab lock. No dead code; the abandoned inline 67-correction left nothing in the script. |
| Scribe | **clear** | Outcome durably recorded (card acceptance section + handoff pointer + owed list). Provenance story intact: 120 carried keep maturity:gold + permission TBD; new trails/waypoints/buildings are raw-zone (`*_traced`, not wired into publish — grep-confirmed). Voice plain, user's words quoted. Corrected 0.7 cm text reads honestly. |

**Result: CLEAR (full six).** No open andon.

## Increment 2 — wired the POIs into the read viewer (2026-06-14)

Follow-on, after the user said "I am not seeing it in the map." Made the traced
waypoints + Shower House visible: new `aop-waypoints` circle+label layer in
`viewer_core.js` (reads `aop_waypoints_traced.geojson`, precached in `sw.js`),
**Shower House merged** into the wired `aop_buildings.geojson` (not swapped — the 5
existing keep FEMA provenance), `v83`→`v84` bump (`sw.js`+`index.html`). Tier: core
three + Mason + Scribe (new viewer JS + served data + version, not publish-zone).

| Seat | Verdict | Note |
| --- | --- | --- |
| Witness | **clear** | Re-ran `verify_waypoints_layer.py` on `:8001` → PASS; 26/26 render (queryRenderedFeatures, observed 4×), Shower House present, 0 fatal errors, `node --check` clean. Nuance (non-blocking): the screenshot lands at the viewer's reverted z14 so it's a weak *human-eye* artifact — the strong proof is the rendered-feature query, which the records correctly lean on. |
| Warden | **clear** | One isolated `viewer_core.js` hunk; merge-not-swap confirmed (existing 5 byte-identical); git gate untouched; v84 = string edit, commit left to user. Flagged the buildings file pretty-print inflation → **fixed** (re-minified to HEAD's one-line format; diff now 1 line). |
| Quartermaster | **clear** | Waypoints block mirrors the trail-network/water-points idiom, reuses `fetchJson`; ONE buildings source (`fema-buildings`), no parallel layer; verifier distinct from `verify_ingest_viewer.py`. |
| Mason | **clear** | No limiting code (circle layer unfiltered → all 26 markers paint; `to-boolean name` filters only the empty label, a verbatim trail-label idiom). Idiomatic, no dead code, raw-zone Shower House props sensible. Non-blocking: Shower House ring has a duplicate closing vertex (harmless). |
| Scribe | **clear** | Card + handoff record what/how/why honestly; no overclaim on the weak screenshot (PASS rests on queryRenderedFeatures); provenance + raw-zone + git-gate stated. |

**Result: CLEAR (increment 2).** No open andon.

**`.claude/.council-cleared` deliberately NOT written (both increments).** The Tier-0
hash formula spans all of `website/`+`mvp/`, which here includes a concurrent
landcover-trace session's and the v83 five-item review's changes that THIS council
did not review. Writing the marker would falsely certify that other code. Per the
established precedent (same call in the prior export receipt, the landcover receipt,
and v83), the Stop hook will keep nudging until the user separates or commits the
trees. The commit + the `v84` bump remain the user's git gate.
