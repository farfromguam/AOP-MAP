# Council receipt — Kind/Status/Source off the user-facing POI surfaces (2026-06-14)

**Goal:** Remove Kind/Status from the POI list and Kind/Status/Source from the world
(feature) popovers. Directive: *"we have kind and status as visible. we dont need those
in the poi list. we dont even need them in the world popovers. in the world there is a
third source. that also needs to go."* (dev-artifact metadata, not visitor copy.)

**Change (this task's hunks only — tree commingled with concurrent sessions):**
- `website/js/feature_display.js` `popupHtml` (the ONE shared popover renderer): dropped
  the `Kind`/`Status`/`Source` `<dt>/<dd>` lines; only author-facing `Caveat` may remain;
  `<dl>` omitted when empty.
- `website/js/viewer_core.js` `renderPoiTab`/`buildPoiGroups` (reader list): dropped
  kind/status chips + `kind · status` subtitle fallback; removed now-unused row fields.
- `website/js/main.js` `renderPoiTab` (editor list): same; kept the "info needed —
  revisit" placeholder chip; added a clarifying comment on the vestigial model fields
  (Mason NEXT, applied).
- `brain/output/verify_poi_no_kind_status_source.py` (new verifier) + doc records.

**Tier:** core three + Mason (shared-strategy change + orphaned-field/craft risk).
**Deterministic gate:** `node --check` passes on all three changed JS files.

## Verdicts

```md
SEAT: witness
VERDICT: clear
ISSUE: none blocking — "9/9 PASS, 0 errors" reproduces on live :8001 and rests on a real DOM read.
EVIDENCE: Re-ran verify_poi_no_kind_status_source.py → RESULT PASS, exit 0, console_errors []. Independent
  live probe: reader POI row has only .poi-row-name + .poi-row-subtitle (0 .poi-row-meta); world popover
  innerHTML shows only <dt>Caveat</dt>, /kind|status|source/i false. Both reader popover paths
  (viewer_core.js:1915/3007) + editor popover (main.js:1328) use the shared popupHtml. Assertions not
  gameable (chip count filters out only the placeholder). node --check clean on all three.
BLIND SPOTS (named, non-blocking): only 2 starred rows, both with blurbs → the kept placeholder-chip path
  isn't exercised live; the editor main.js LIST surface isn't driven on :8001 (grep+node-check verified).
NEXT: optional — drive data_sources.html headless + add a blurb-less fixture to observe the kept chip.

SEAT: warden
VERDICT: clear
ISSUE: none — directive executed 1:1; provenance hidden from visitor, not destroyed; git gate clean.
EVIDENCE: the three card-owned hunks land exactly on "Kind+Status off list, Kind+Status+Source off popover";
  no DATA/layer-styling touched. featureDisplay() (feature_display.js:42-48) still returns kind/status/source;
  the editor identify dock (data_editor_map.js:379-389) still renders them — author keeps full provenance.
  HEAD still ee7f5cd v90; no agent commit/attribution; sw.js+#appVersion v90→v92 is the pre-existing bump
  owned by other cards, no second bump attributable here.
NEXT: none — v92 bump + commit remain the user's gate.

SEAT: quartermaster
VERDICT: clear
ISSUE: none — removal stopped at RENDERING; no second renderer, no gutted collector, no dead field, no divergence.
EVIDENCE: both POI-list copies drop kind/status consistently; editor's kept placeholder chip is the
  PRE-EXISTING asymmetry (reader never had it), not new. popupHtml stays the single shared renderer.
  viewer_core row object now {name,blurb,revisitNote,feature} with no remaining row.kind/row.status reads in
  POI scope. main.js collectStarredDestinations (1137) NOT gutted — listRow strategies still emit the fields;
  editor dock still consumes them. featureDisplay() model unchanged. C1=0, C6 (0 classes/1 registry/no new
  editor html), C2 (1 collector) all hold.
NEXT: none.

SEAT: mason
VERDICT: clear
ISSUE: none blocking — pure removal + complete compositing guards; no limiting code; idiom matches.
EVIDENCE: (1) the only vestigial bit — main.js poiPopupHtml still passes kind/status/source into the model
  popupHtml now ignores — is the intentional uniform-model mirror (the two viewer_core callers pass the whole
  featureDisplay model); a clarifying comment was added. No leftover unused locals. (2) No CHECK/validator/
  throw/row-dropping added (the buildPoiGroups ★ highlight gate is pre-existing). (3) Empty-span guard
  complete — subtitle/meta/<dl> created only when they have content, so removed chips leave no phantom margin
  (viewer.css:352-353 / app.css:743-744). (4) esc()/createElement idiom consistent. node --check clean.
NEXT (non-blocking, applied): added the one-line "popupHtml ignores kind/status/source" comment at the model.
```

**Steward synthesis:** full clear — every convened seat (Witness · Warden ·
Quartermaster · Mason) `clear`, no open andon. Provenance is preserved on the data and
in the editor dock (source-led promise intact); only the visitor surfaces shed the
metadata, per explicit user direction. The v92 bump + commit remain the user's git gate.
