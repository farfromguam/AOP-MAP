# Council receipt — band merge into the clean read viewer

Date: 2026-06-13 · Steward: main agent · Tier: full six (witness · warden · quartermaster · mason · scribe · steward)

**Goal (from the card `tasks/13_viewer_extraction/viewer_band_merge.md`):** carry the geolocated
decorative "neat-line" band (`website/js/viewer_band.js`) into the clean read viewer
(`website/index.html`) — extraction, not subtraction — via a seam in `viewer_core.js` (expose
`window.AOPViewer`, pad `maxBounds`) + precache/version bump in `sw.js`. User directive: *"be sure not to
pull over the crud."*

**Diff reviewed (website only — the gate's clearance scope):** `index.html` (+band `<script>`, `#appVersion`
v70→v71), `js/viewer_core.js` (`REGION_MAXBOUNDS`/`BAND_PAD 0.13` leash, `window.AOPViewer` seam, Region
preset 15% inset → 7% outset), `js/viewer_band.js` (z-order re-float: `raiseBand`/`bandIsOnTop`/`queueRaise`
bound to `styledata`+`idle`), `sw.js` (`viewer_band.js` + `rw-mark.svg` into `SHELL_ASSETS`, `VERSION`
v70→v71). Tier chosen full six: shipped-viewer feature merge, new control flow, camera-behavior change,
and it edits a previously council-cleared module.

**Why full six and not core three:** the change added non-trivial control flow (the z-order raise loop —
Mason's lens) and had a recording obligation (Scribe's lens), beyond the core three.

## Seat verdicts

```md
SEAT: witness
VERDICT: clear
ISSUE: none — every "verified by observation" claim reproduced under the seat's own independent Chrome drive.
EVIDENCE: drove :8000 headless, attached window.AOPViewer.map, read getStyle().layers / live getMaxBounds()
  / console / PIL pixels. 38 band layers (mask+keyline+36 art); band reaches top and stays above:[] through
  the ~13s load, the Region switch, and 3D (pitch 60, terrain on); live maxBounds = REGION_BOUNDS padded 0.13;
  PIL Region perimeter reads paper #e3d7bb; satellite contained in 9-patch; lettering foreshortens in 3D; no
  console/pageerrors; node --check clean; window.TerraDraw false / no editor panel; rw-mark.svg + viewer_band.js
  in SHELL_ASSETS; VERSION/#appVersion v71.
NEXT: none.
```
```md
SEAT: warden
VERDICT: clear
ISSUE: all four website hunks trace to the card; no editor/CRUD touched; git gate untouched (v71 bump was
  uncommitted + flagged at review time).
EVIDENCE: diff = exactly index.html/viewer_core.js/viewer_band.js/sw.js, each traced to card lines; editor/CRUD
  name-only check (panel.js, data_editor*.html, data_editor_map.js, schedule_editor.html, main.js) empty;
  window.AOPViewer leaks only {map, regionBounds}; no agent attribution; non-website tree changes (.claude/hooks,
  brain/pages.md, session_context.md) are harness/skill machinery, not attributable to this work.
NEXT: none — retire of spent scaffolding remains card-named and owed.
```
```md
SEAT: quartermaster
VERDICT: clear
ISSUE: the pad() "duplicate" and a second window.AOPViewer are the RETIRING proof shim, not a persisting
  parallel surface.
EVIDENCE: window.AOPViewer defined once in prod (viewer_core.js:73), consumed once (viewer_band.js:46); the
  other copy is viewer_banded.html (carded for retirement). New raiseBand is a single clean extension, old idle
  handler body fully replaced, no dead code. C1 region grep on main.js = 0; one collectStarredDestinations; no
  new class [A-Z]; no new editor *.html. node --check clean.
NEXT: none — retire the proof so pad()/AOPViewer don't linger (separate change, user's gate).
```
```md
SEAT: mason
VERDICT: clear
ISSUE: no limiting code, no throw-on-unknown, no harmful dead code; the z-order loop terminates and the camera
  leash is a bound, not a data filter.
EVIDENCE: traced moveLayer→styledata→queueRaise→raiseBand: queueRaise always rAF-defers, bandIsOnTop() breaks
  the loop, idle short-circuits once settled — no storm, no per-frame thrash. bandIsOnTop() guards null/empty
  getStyle().layers; pre-addBand stale BAND_LAYERS unreachable behind the getSource('band-mask') gate.
  REGION_MAXBOUNDS/outset are camera bounds (drop no rows), idiomatic. Only nit: the `raising` flag is redundant
  given the always-deferred queueRaise — cheap, documented, not a gate.
NEXT: none.
```
```md
SEAT: scribe
VERDICT: andon → resolved → clear
ISSUE: the merge was recorded in the CARD but NOT in handoff/session_context.md (DoD line 6 / Scribe failure).
EVIDENCE: card "Implemented — 2026-06-13" block records the four files, the v70→v71 bump as the user's git gate,
  observed results, and the retire list; but session_context.md's only change vs HEAD was an unrelated hook note.
RESOLUTION: the Scribe added a v71 band-merge pointer to the handoff and corrected a stale "unreviewed band" line,
  then re-reviewed clear. (The user has since run a "session prune" commit over the handoff — its end-state is
  the user's.)
NEXT: none.
```

**Steward verdict:** CLEAR — every convened seat clear (the Scribe's andon raised a genuine recording gap,
which was repaired and re-reviewed). Synthesis: the band merge is observed-correct, on-card, non-limiting,
non-duplicating, and recorded.

**Note on git state:** while the council ran, the **user** committed the reviewed website work — HEAD
`2980c27` now carries `index.html` band `<script>` + `#appVersion v71` and `sw.js VERSION v71`; the working
tree is clean. The version bump that was "owed to the user" has been taken by the user. No agent commit, no
attribution (verified by the Warden).

**Owed (the user's, still open):** retire the spent scaffolding — `viewer_banded.html`,
`viewer_banded_compare.html`, `css/viewer_band.css` (+ adjacent `old_index.html`).
