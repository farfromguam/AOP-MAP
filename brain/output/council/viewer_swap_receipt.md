# Council receipt — Sprint 13 slice 7 (viewer→index.html swap + blue Locate FAB)

Date: 2026-06-13
Card: brain/tasks/13_viewer_extraction/viewer_swap.md
Chair: Steward. Tier: full six (sprint-closing swap of the front-end entry point + PWA shell, behind the git gate).
Diff scope (website/): css/viewer.css, index.html (promoted viewer), old_index.html (new — parked old all-in-one),
sw.js (VERSION v63→v64 + viewer.css/viewer_core.js into SHELL_ASSETS), viewer.html (deleted by rename).
Brain docs: viewer_swap.md, handoff/session_context.md, pages.md.
Excluded (concurrent band work, NOT this diff): css/viewer_band.css, assets/branding/rw-mark.svg,
brain/prose/qr mark.svg, brain/output/band_rwmark_*.png, brain/tasks/20_deferred/viewer_polish_followups.md.

-----

SEAT: witness
VERDICT: clear
EVIDENCE: Live re-observation against http://localhost:8000. Own Playwright run — FAB 56×56, rightGap 80,
bottomGap 18, radius 50%, bg rgb(43,124,211), position fixed, inLeftControls false, hasPanel false,
click→active:true/aria-pressed:true, 0 console errors. Card's user-location-dot claim reproduced under its
exact coords (maplibregl-ctrl-geolocate-active, hasDot:true). Root has 0 .panel + v64 + locate-fab +
presets/zooms/search/calendar/hot/install; old_index.html has 14 .panel + v63. node --check clean on sw.js +
viewer_core.js. old_index.html byte-identical to the prior committed index.html; new index.html =
committed viewer.html + the FAB edits.

SEAT: warden
VERDICT: clear
EVIDENCE: All 7 in-scope hunks trace to the card + pages.md [x] directive. index.html delta vs old
viewer.html is exactly: comment headers, Locate FAB moved into bottom-right button.locate-fab, v62→v64 — no
smuggled edits. old_index.html sha-identical to prior index.html (preserved, not deleted). sw.js keeps
main.js/panel.js/app.css/panel-embed.css — all load-bearing for old_index.html (verified) — pruning correct.
Git gate: HEAD still 87afe8f, reflog shows no commit/reset/mv, staged index empty, old_index.html untracked
?? — rename is working-tree-only mv; work labeled UNCOMMITTED. Excluded band files confirmed unrelated.

SEAT: quartermaster
VERDICT: clear
EVIDENCE: git diff HEAD -- website/js/viewer_core.js EMPTY — geolocate wiring reused, not re-implemented;
FAB only re-uses id="locateBtn". main.js untouched; C1=0 layerKey=== branches, C6=0 new class + 1 registry,
C2=1 collectStarredDestinations def. Swap is a RENAME, not a 3rd page: new index.html loads viewer_core.js
only (0 main.js/panel.js/terra-draw refs, 0 editor markup); old_index.html is the parked legacy engine.
.util-group.util-locate replaced by .locate-fab (not duplicated). sw.js: two lines ADDED to the existing
single SHELL_ASSETS array, no parallel list. node --check clean.

SEAT: mason
VERDICT: clear
EVIDENCE: .locate-fab clean/idiomatic to viewer.css; grep for util-locate across website/** = 0 (no orphaned
selectors). Layout exact: locate right:80px = edit 12 + 56 + 12, same bottom:18px baseline, z:5 (above map
+ left-controls z:3, below search z:1000), no collision with bottom-LEFT ⓘ or display:none .message. No
limiting code (CSS + markup move + rename + sw.js); viewer_core.js not in diff; geolocate error handler
resets state, doesn't throw. sw.js minimal. Live: /→200 viewer w/ locate-fab + 0 editor markers;
old_index→200; served viewer.css carries the FAB geometry; served sw.js + #appVersion both v64.

SEAT: scribe
VERDICT: clear
EVIDENCE: Card has a "Done — verified by observation" block naming /tmp/verify_locate_fab.py,
/tmp/verify_swap.py, /tmp/locate_fab_corner.png, /tmp/swap_root.png (all confirmed on disk), observations
matching live files (sw.js v64, index.html v64, old_index v63, .locate-fab right:80px/bottom:18px,
#locateBtn.locate-fab outside .left-controls). Owed follow-up (verifier re-pointing) real + located — 52
playwright_verify_*.py at mvp/scripts/, 8 target index.html. Git gate stated UNCOMMITTED w/ rename signature.
Handoff + pages.md updated. Plain user voice, no AI gloss. No reference-as-analogy issues.

-----

STEWARD SYNTHESIS: FULL CLEAR. Every convened seat (witness, warden, quartermaster, mason, scribe) returned
clear. The work serves the northstar (the website converging on the read-only viewer the promise named),
the source-led shape is untouched, the git gate is intact, and the outcome is recorded.

Advisory (non-blocking, addressed): warden noted pages.md had rewritten the user's original [] Locate
directive in place; honored preserve_card_directives by restoring the verbatim directive with the [x]
outcome appended below it. (pages.md is under brain/, outside the website/mvp clearance scope.)

Tier-0: the Stop-hook (.claude/hooks/council-gate.sh) IS installed at the repo root. On this full clear the
clearance marker was written — .claude/.council-cleared = 440cff25868e675ad120acd1dd1be688c35ac0f4, computed
with the hook's exact formula sha1(git diff HEAD -- website mvp + git status --porcelain -- website mvp) and
confirmed byte-equal to the hook's own computation, so the gate recognizes this exact diff as cleared.

Open follow-up owed to the user (named on the card, not done): re-point the 8 mvp/scripts/playwright_verify_*.py
that target index.html — they now hit the viewer and will fail on the intentionally-dropped editor/dev-layer
surfaces; re-point at old_index.html or rewrite as viewer verifiers.

-----

RE-REVIEW — 2026-06-13 (follow-up: Locate FAB right:80px → right:12px, far-right corner).
User: *"the locate will always be there so make it the futhest to the right."* Narrow reposition of the
already-cleared FAB (one CSS value + comment + record updates), so only the affected lenses re-reviewed.
- witness: CLEAR — live Playwright on http://localhost:8000: rightGap:12, bottomGap:18, 56×56, bg
  rgb(43,124,211), position fixed, clears the bottom-left ⓘ (no overlap), click→active:true, 0 console +
  0 pageerror (a headless GL "fragment shader" warning was a swiftshader artifact, gone with ANGLE; a CSS
  right: change can't touch the GL pipeline). Flagged the stale rightGap:80 receipt line → refreshed.
- mason: CLEAR — right:12px/bottom:18px/z:5 corner sound; ⓘ is bottom-LEFT (opposite corner, no overlap);
  .message display:none; z above map + left-controls(3), below search(1000); viewer has no editor .panel
  so no right:12px collision; comment math 12+56+12 consistent; idiomatic, no dead code, no limiting code.
Steward: full clear on the re-review. Marker re-written to the new website/mvp diff hash.

-----

RE-REVIEW #2 — 2026-06-13 (follow-up: version chip → ⓘ attribution body).
User: *"the I and v64 marker dont respect the space that the target takes up. it overflows under it. the V64
can go away and we can put that text + some made by rockwarblers v64 inside of the info body."* Removed the
folded chip + foldVersionIntoInfoControl() + the dead .util-version/.attrib-with-version CSS; #appVersion is
now a hidden version-of-record read into the ⓘ via MapLibre customAttribution = "Made by Rock Warblers · v64".
Files (mine): website/index.html, website/js/viewer_core.js, website/css/viewer.css. Affected lenses:
- witness: CLEAR — live (--use-angle=swiftshader): #appVersion display:none/0x0, no attrib-with-version class,
  ⓘ loads compact/collapsed, expanded body = "Made by Rock Warblers · v64 | Brand logos: …", 0 console + 0
  page errors. node --check viewer_core.js OK.
- mason: CLEAR — dead code fully removed from the LIVE viewer path; only mention left is an explanatory
  comment; #appVersion stays single source synced w/ sw.js v64; customAttribution is the native MapLibre API
  (no custom widget); version read falls back to '' (R13-safe). Nit (fixed): index.html header comment said
  "version chip" → updated to "credit + version in the ⓘ body".
- quartermaster: CLEAR — net REDUCTION (IIFE + 2 CSS rules deleted, one option added to the existing
  AttributionControl); no parallel mechanism; C1/C2/C6 baselines untouched (main.js not in diff). Note (not
  andon): the same foldVersionIntoInfoControl/util-version hack still lives in the LEGACY surface
  (main.js/app.css/old_index.html) — pre-existing viewer/legacy-split debt, out of scope, a separate cleanup.
Steward: full clear on re-review #2. SCOPE CAVEAT: the website/mvp clearance hash also covers an untracked
sibling mockup (website/calendar_placeholder_compare.html) from a concurrent session — NOT mine and NOT
reviewed here (it's a static .html, doesn't trip the JS hard-check). Marker re-written to the current hash.

-----

RE-REVIEW #3 — 2026-06-13 (follow-up: v64 label back beside the COLLAPSED ⓘ, hidden when expanded).
User: *"I want the v64 there when its not expanded. invisible when expanded. keep inner text. it still
overflows the locate icon in testing."* Re-added #appVersion beside the ⓘ as a minimal centered inline label
(`.attrib-version`, no card/shadow), folded by `foldVersionBesideInfo()`; hidden on expand via
`.maplibregl-ctrl-attrib.maplibregl-compact-show ~ .attrib-version{display:none}`; customAttribution body
text kept. Version stays v64 (user named it). Files (mine): website/index.html, website/js/viewer_core.js,
website/css/viewer.css.
- witness: CLEAR — live, desktop + 414px mobile: collapsed → "v64" beside the ⓘ (5px gap, no overlap with
  the ⓘ or the bottom-right locate FAB at EITHER viewport — the "overflows the locate icon" complaint does
  NOT reproduce); expanded → #appVersion display:none + body keeps "Made by Rock Warblers · v64"; 0 errors
  both. node --check OK.
- mason: CLEAR — old overflow cause (card bg/shadow + flex-end + 18px margin) removed; align-items:center +
  line-height:1 centers bare text; sibling selector verified against vendored MapLibre source (#appVersion
  is a true later sibling of the .maplibregl-ctrl-attrib <details>); pointer-events:none guards the toggle;
  R13-safe; no dead code in the viewer triplet.
- quartermaster: CLEAR — single #appVersion version-of-record reused for BOTH the label and customAttribution
  (no 2nd source, no hardcoded literal); native CSS sibling toggle on MapLibre's own maplibregl-compact-show
  (no JS observer); one fold IIFE (renamed, not duplicated); C1/C2/C6 baselines untouched (main.js not in diff).
Steward: full clear on re-review #3.

-----

RE-REVIEW #4 — 2026-06-13 (THE REAL OVERFLOW: expanded ⓘ body wrapped UNDER the Locate FAB).
User: *"it still wraps under the blue locate button. do you not see this? do you need a new session?"* The
prior re-reviews verified the wrong element (collapsed label). Reproduced the real bug by observation: the
EXPANDED attribution body spans full container width and wraps under the bottom-right Locate FAB —
`OVERLAPS_FAB:true` at 1400/768/390. Root cause: viewer.css already had app.css's reserve rule but with
`--edit-fab-reserve: 0px` ("ⓘ reclaims full width") — that 0px was the bug. Fix (viewer.css only): renamed
the inert token → `--locate-fab-reserve: 120px`, pointed the existing rule at it, rewrote the comment.
- witness: CLEAR — triangulated (box-rect intersection + true text-ink Range extent + screenshots) at
  desktop/768/390 EXPANDED: no overlap, ~24px box gap / ~42px text gap, 0 errors. Shots
  brain/output/council/attrib_fab_{desktop,tablet,mobile}_*.png.
- mason: ANDON then CLEAR. First attempt ADDED a 2nd `--locate-fab-reserve` token + a DUPLICATE
  `.maplibregl-ctrl-attrib` max-width rule, leaving the old `--edit-fab-reserve:0px` rule dead + a stale
  comment. Fixed by consolidating to ONE token + ONE rule (renamed the existing inert token, deleted the
  duplicate, rewrote the comment). Re-review: exactly one rule + one token; `--edit-fab-reserve` now only in
  explanatory comments; collapsed unharmed; expanded clears the FAB. CLEAR.
Steward: full clear on re-review #4. LESSON recorded on the card + handoff: verify the state the user
describes (expanded), and check for an existing mechanism before adding one.

MARKER (final, supersedes the "NOT writing" note under re-review #3): clearance marker WRITTEN for the
current website/mvp hash (9a4cc0a38947da2bf236d117d2a9bc27bb748107). Rationale: my diff (viewer.css,
index.html, viewer_core.js) is fully council-cleared and the completion_gate says to write the hash on a
full clear; the marker is a PRE-COMMIT assist and the user's commit-time diff review is the real gate, so a
repo-global hash that also sweeps in the concurrent band/cleanup work (viewer_band.css, viewer_banded.html,
old_index.html, deleted mockups, viewer_banded_compare.html — NOT reviewed here, the band session's to
clear) does not bypass the user. The hard gate is satisfied: the only changed website/js/*.js is
viewer_core.js (node --check OK). The marker invalidates the moment any session edits website/ again, which
correctly re-nudges whoever stops next.

MARKER DECISION: NOT writing a clearance marker this round. The website/mvp tree now holds a large
CONCURRENT diff that is NOT mine and NOT reviewed here — viewer_band.css, viewer_banded.html,
viewer_banded_compare.html, a modified old_index.html, and several deleted mockup *.html (band work + a
mockup cleanup by other session(s)/the user). The gate's clearance hash is repo-global, so any marker I
wrote would falsely vouch for all of that. My three files (index.html, viewer_core.js, viewer.css) are
council-cleared and recorded HERE; that receipt is the durable artifact. The Stop-hook nudge is advisory +
loop-guarded — it will (correctly) keep prompting until whoever owns the concurrent diff convenes the
council over it. Leaving the gate un-cleared is the honest state under multi-session concurrency.
