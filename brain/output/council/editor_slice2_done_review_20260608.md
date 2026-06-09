# Council done-review — Sprint 09 Slice 2 (drawn-POI CREATE → the ONE store)

Date: 2026-06-08
Chair: Steward. Tier: **full six** (store-of-record boundary = the F6 twin-store class, the highest-risk
class in this codebase; the C2/C6 one-engine contract; plus a deliberate scope call — the help text —
needing the Warden/Scribe lens; matches Slice 1's rigor and the user's "no shortcuts" mandate).

**Goal (one line, from the card):** the right panel's CREATE affordance must land a new drawn POI in the
ONE store of record (`aop_editor_pois_v1`), editable immediately, no twin-store leak, surviving reload —
reconciling the half-retirement.

## Diff reviewed
- `website/js/main.js` — new `AOP_HOST_CREATE_FEATURE` bridge + extracted `addDrawnPoi(geometry, category)`
  shared by the host TerraDraw `finish` handler and the bridge (finish handler refactored to call it).
- `website/js/panel.js` — `commitFeature` `hostEdit` branch → bridge + `seedLoadedFromHost()` re-seed +
  auto-select, returns before the OVERRIDES write.
- `website/sw.js` + `website/index.html` — v58→v59 bump.
- new `mvp/scripts/playwright_verify_drawn_poi_create.py`.
- `website/index.html:450` help text — deliberately UNCHANGED (review the call).

## Verdicts — FULL SIX CLEAR (1 round, no andons)

**witness — clear.** Ran all four verifiers live against http://localhost:8001/.
`playwright_verify_drawn_poi_create.py` PASS 9/9 (create lands in `aop_editor_pois_v1` before=1/after=2,
id `poi_…`, layer `editor_poi`; NO `aop_panel_overrides_v1` leak; Name field editable; rename persists;
survives reload; 0 console errors). Regression guards `playwright_verify_drawn_poi_editor.py`,
`_data_groups_embed.py` (8 sections, generic draw retired), `_starred_poi_flip.py` all PASS. `node --check`
clean on both JS files. Verifier drives the real panel (`.node-select` → `button.add-type` "Add POI" →
`map.fire('click')`) and asserts localStorage, not a re-implementation. `addDrawnPoi` resolves at all
three sites (bridge / def / finish handler) with the trace branch preserved verbatim. Non-andon note:
trace-via-panel isn't a Slice 2 card claim ("create a POI" = point, covered); in-scope-complete.

**mason — clear.** `addDrawnPoi` is a behavior-preserving lift of the former inline `finish` build (finish
now delegates; no dead leftover). Bridge is try/catch → null; the `layerKey !== 'editorPois'` guard is a
fail-safe scope guard (only `editorPois` carries `hostEdit:true`), NOT a row-dropping filter. `category`
default `'Other'` is a safe neutral default the user edits immediately (R13). Panel hostEdit branch returns
before the OVERRIDES write (C3, one store), correct order create→endDraw→seed→select→rerender, `if (newId
!= null)` degrades safely. C1 = 0 non-comment `layerKey === '`; no new `class`; no new editor `*.html`.

**quartermaster — clear.** `addDrawnPoi` defined once, extracted not duplicated; `AOP_HOST_CREATE_FEATURE`
mirrors the Slice 1 `AOP_HOST_*` family; panel branch reuses the Slice 1 `commitChange`/`persistDelete`
hostEdit pattern + `seedLoadedFromHost()`; verifier reuses `playwright_base` + the Slice 1 boot/store
idioms. No second store of record. C1 grep holds at 0 (the `!==` guard is a fail-safe bridge entry guard,
not a behavior-dispatch branch in any C1 region).

**warden — clear.** Every hunk traces to Slice 2 / its Execution-time notes. Git gate untouched: status =
`M website/*` + `?? mvp/scripts/playwright_verify_drawn_poi_create.py`, HEAD still `63e5690`, no
add/commit/push, no attribution. v58→v59 performed not committed (the owed bump). Help-text-left-unchanged
is defensible — it lives in `<section data-section="editor">` (not `.aop-keep`), hidden by
`panel-embed.css:272` in embedded mode; renders only in the host standalone fallback where it's accurate;
the card's staleness was cured by Slice 1 restoring the node. Nothing silently deleted.

**scribe — clear (conditioned on the four records landing, now written).** Required: (1) Slice 2 DONE block
on the card with the acceptance result + OWED; (2) handoff entry (CODE/UNCOMMITTED, v59 performed, commit
owed, NEXT = Slice 3); (3) the help-text decision recorded with reasoning; (4) wikilinks + in-code F6 /
bridge-family references kept as the real things. The in-code comments cite "audit F6" / the bridge family
as the actual things in this codebase, not analogies — passes `references_are_not_analogies`. Voice plain.
→ Records 1–4 written by the Steward post-clearance (card DONE block, handoff entry, this receipt).

**steward (cross-check) — clear.** Serves the promise (one editing surface, one store), not motion — the
create path now mirrors the Slice 1 edit path (same `node.hostEdit` gate, same bridge → `aop_editor_pois_v1`).
Source-led shape held: `addDrawnPoi` is a byte-for-byte extraction; provenance preserved (LineString keeps
the full NAIP block). Help-text call right at the product level — no real user sees the hidden text; the
embedded surface is self-consistent. Not a batched fork (Fork #0 was user-resolved in Slice 1; Slice 2 is
the narrow create half, verified beside the work). Non-blocking note: panel passes `opts:{}` so the bridge
defaults `category:'Other'` — correct, since the panel's add affordance is geometry-typed with no pre-place
category picker (category chosen post-create in the opened editor).

## Result
Gate CLEARED. Clearance marker written to `.claude/.council-cleared` (the website+mvp diff hash). The
commit + the v58→v59 bump remain the user's git gate.

-----

# Council done-review — Sprint 09 Slices 3+4 (trailheads editable F7 + generic-draw cleanly retired)

Date: 2026-06-08 (same session; user directed "continue all the slices until done"). Chair: Steward.
Tier: **full six** (closes the sprint's UI-completeness axis; "no shortcuts" mandate).

**Goal:** Slice 3 — make the curated visibility-only `trailheads` layer (F7) an editable, authorable
feature list with safe fallbacks. Slice 4 — confirm the retired generic draw group (Fork #1) is cleanly
retired because per-layer "+ add" authors every geometry type into a real source; fix the stale docs.

## Diff reviewed (incremental — Slice 2 already cleared above)
- `website/js/panel.js` — the `trailheads` node (editable list + createDefaults layer stamp + safe
  key/label fallbacks) and two stale generic-draw doc-comment fixes.
- new `mvp/scripts/playwright_verify_trailheads_editable.py` + `playwright_verify_per_layer_add.py`.
- de-flake of the Slice-1 guard `playwright_verify_drawn_poi_editor.py` (post-reload expand: `state='attached'` + settle).

## Verdicts — FULL SIX CLEAR (1 round + Scribe andon-bounce)

**witness — clear.** Ran all six verifiers live. Slice 3 `playwright_verify_trailheads_editable.py` PASS
8/8 — an UNNAMED SERVED trailhead (no `_id`, injected via `page.route` with `service_workers="block"` so
the route fires) renders `rows=['Trailhead']` via the `spec.label` fallback (deriveItems panel.js:1238-1243:
no `_id` → `spec.label`, not the user-feature 'Untitled' path); authored trailhead lands in publish-data
1→2 tagged `layer:'trailheads'`, editable, rename persists. Slice 4 `playwright_verify_per_layer_add.py`
PASS 11/11 on a RENDERED panel — generic-draw nodes absent, Line→aop-trail-network 120→121, Polygon→
fema-buildings 5→6, each editable. Guards PASS: create 9/9, data_groups_embed, starred_poi_flip;
drawn_poi_editor was flaky (its own post-reload visibility race, not the diff) → **de-flaked** (now 3/3).

**mason — clear.** Trailheads mirrors the sibling boundaries/pubTrails pattern; key/label fall back
(`'trailhead'`/`'Trailhead'`, never undefined — R13); `createDefaults` is an additive per-node hook (same
shape as cemeteries' geom_role), not a filter; `locked:true` gates only existing features; the publish-data
filter is a shared-source selector, not a row-dropping gate. Doc fixes accurate; no dead code introduced
(no node declares `create:`; the `node.create` guards are inert-but-retained hooks for the live standalone
path). No new class / layerKey branch / throw; node --check passes.

**quartermaster — clear.** Pure spec reuse of the one `refItems` + shared `createDefaults` machinery;
Slice 4 is verify-only + comment edits (no generic nodes re-added, no second create path, no new source);
verifiers reuse playwright_base + established idioms; no DB-star duplication (trailheads carries no
hostKey — defers to gold slice 6). C1/C2/C6 greps hold.

**warden — clear.** Every hunk traces to Slice 3/4; Fork #2 honored (eventSchedule unchanged,
visibility-only); Fork #1 honored (generic nodes not restored). CRITICAL: the live standalone draw path
(`userFeatures`, `geometryDefaultGroup`, host draw machinery) was NOT deleted — the generic-draw cleanup
touched COMMENTS only. Git gate untouched: single v58→v59 bump for the batch, HEAD still 63e5690, no
mutating git.

**steward (cross-check) — clear.** Serves the promise (a publishable first-party layer becomes authorable)
within the existing silver-node pattern; provenance intact (create stamps source/confidence/permission/
status before the layer tag); per-layer "+ add" is more source-led than a generic bucket; DB-first
correctly deferred to gold slice 6 (HELD).

**scribe — andon → re-review clear.** First pass: andon (the Slice 3/4 DONE blocks + handoff entry were
not yet written — DoD item 6). The Steward wrote the three records (Slice 3 DONE, Slice 4 DONE, handoff
entry) in the user's voice, matching the Slice-1/2 block format, with the references treated as the real
things (sibling boundaries/pubTrails pattern; the standalone path). Re-review: clear.

## Result
Gate CLEARED for Slices 3+4. Slices 1–4 (the UI-completeness axis Sprint 09 owns) are COMPLETE. Clearance
marker re-written over the new website+mvp diff hash. The commit + the v59 bump remain the user's git gate.
**Slice 5 (the DB doors = gold slice 6) is HELD — the user's pull decision, surfaced not executed.**
