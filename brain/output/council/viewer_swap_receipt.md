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
