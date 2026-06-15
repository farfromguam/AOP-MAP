# Council receipt — waypoint ★ durability on re-import (2026-06-14)

**Goal:** *"fix the star durability … survive a db export or a re-import. save it to the
gold data directly. no shortcuts."* Make the camp-waypoint ★ (`highlight`) + authored
fields survive an Affinity re-import.

**Change (mvp/scripts/import_illustrator_trace.py — build-pipeline only, NOT served):**
- `import_points()` now provenance-preserving (mirrors `import_trails`): edited
  geometry+name win, authored gold props (highlight/description/location_tag/…) carry
  forward from prior gold by name; returns `(feats, matched)`.
- new `preserve_unmatched_authored()`: re-adds prior ★/`#location_tag` POIs not in the
  SVG (e.g. Gravity Gauntlet from a GPX) — delete-from-gold-directly is the documented rule.
- `_is_dropped_cemetery` lifted to module scope (reused; never resurrects dropped cemeteries).
- No served data changed; the ★ stays ON the gold feature (no sidecar).

**Tier:** core three + Mason (no-limiting-code + resurrection-safety of the preserve step).
**Deterministic gate:** `python3 -m py_compile` passes; no `website/js/*.js` touched.

## Verdicts

```md
SEAT: witness — VERDICT: clear
Re-ran verify_waypoint_star_durability.py → 14/14 PASS, exit 0. Verifier imports the REAL module
and calls the actual import_points / preserve_unmatched_authored / _is_dropped_cemetery (no logic copy),
against the REAL current gold as prior; independently confirmed the prior carries the asserted props
(Hot Rocks ★+desc, GG ★+#tag, Firepit #tag, RV Site 1 none). git: only the pipeline script modified,
website/data untouched. py_compile clean.
BLIND SPOT (named, inherent — not a defect): SYNTHETIC SVG vs REAL AFFINITY MASTER. The in-repo
aop_satellite_trace.svg holds 5 circles (Pavilion + 4 cemeteries), NONE of the 24 curated POIs, so a real
run would exercise zero carry assertions — the synthetic SVG is the necessary instrument. Carry-forward
LOGIC is verified; a real Affinity round-trip (metadata-frame recovery, Affinity wrapper-<g>/data-* stripping
on the genuine POI set) is NOT yet observed.
NEXT: one real round-trip against a COPY of gold — `import_illustrator_trace.py <real_master>.svg --all` —
then diff to confirm Hot Rocks keeps ★+desc and GG/Firepit survive on the real file.

SEAT: warden — VERDICT: clear
Directive satisfied with no shortcut: the ★ is literally "highlight":true ON the gold feature (committed
v93/d212d5e), NOT a sidecar (aop_poi_index.json has no waypoint entry; bake_poi_stars SOURCES excludes
waypoints). "DB export is a non-threat" VERIFIED TRUE by exhaustive grep — the ONLY writer of the gold
waypoints file is the import script; rebake_canonical CONFIG, export_publish_geojson.sh REFERENCE_LAYERS,
bake_poi_stars SOURCES, and SQL all exclude it; no waypoints DB table. This task's diff is pipeline-only
(git diff of the gold waypoints file is EMPTY) → no vNN owed for it. Git gate untouched (all commits
"Christopher Fryman", no attribution). The preserve step's workflow exception (delete-from-gold-directly)
is documented in the docstring + card, not silent.

SEAT: quartermaster — VERDICT: clear
Carry-forward MIRRORS import_trails (same copy.deepcopy(prior props) + edited-name-wins + review_status
idiom, by-name match) — not a novel mechanism. _is_dropped_cemetery is a DEDUP (exactly one def, now
module-level, reused by main() + preserve; old nested def deleted). Reuses walk_layer/feature_name/
frame_to_lnglat/apply — no re-implemented geometry. preserve_unmatched_authored reads the SAME
properties.highlight field as bake_poi_stars + the viewer (not a parallel notion); distinct concern (retain
vs seed), small helper. import_points( has 1 def + 1 call; main() unpacks the tuple — no orphaned caller.

SEAT: mason — VERDICT: clear
C5/no-limiting-code: preserve_unmatched_authored is purely ADDITIVE (builds kept, main wf.extend); its
continues skip what to re-add, not drop from the import stream. import_points permissive: missing name→None
(no throw), missing kind→"poi", no-match→thin POI. No new raise/assert/silent-drop (the cemetery filter is
pre-existing, user-confirmed, merely lifted). Resurrection: deleting a ★ POI from the SVG re-adds it — the
DOCUMENTED delete-from-gold rule (acceptable, not andon); dropped cemeteries excluded. No double-add (matched
set, lowercased, accumulated across layers + guarded). copy.deepcopy avoids aliasing. Mirrors import_trails;
py_compile clean.
NEXT (optional card note, not a gate): the by-name index collapses case-insensitive name collisions — two
distinct prior POIs sharing a lowercased name would both survive preserve. Pre-existing index property;
surface as a data-integrity note, don't enforce.
```

**Steward synthesis:** full clear — Witness · Warden · Quartermaster · Mason all `clear`,
no open andon. The fix closes the waypoint-★ durability gap on the file round-trip (the DB
export was never a threat — waypoints are file-only), keeps the star ON the gold feature
(no sidecar), and is additive/permissive (no limiting code). **Carry-forward verified
against the real gold via a synthetic edited SVG; a real-Affinity-master round-trip is the
named NEXT** before treating end-to-end durability as fully observed. No `vNN` bump owed
(pipeline-only). Commit remains the user's.
