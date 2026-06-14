# Council — v80 off-park Locate travel notice (2026-06-14)

Tier: **core three** (Witness · Warden · Quartermaster). Low risk: read-viewer UX,
no publish-zone data, no validation loop, no sprint boundary. Reviewed over the v80
diff (`website/{js/viewer_core.js,css/viewer.css,index.html,sw.js}`) + the card
acceptance criteria (`tasks/13_viewer_extraction/viewer_locate_install_version.md`,
"Addendum: off-park travel notice").

## Receipts

```
SEAT: witness
VERDICT: clear
ISSUE: none (diff landed as the user's commit cdcc918/v80; reviewed the commit, byte-identical to the working tree)
EVIDENCE: Live re-run of brain/output/verify_locate_travel.py on :8001 reproduced 3/3 PASS, 0 non-GL
  console errors. Test observes the real system — granted+spoofed geolocation (ctx.set_geolocation),
  fresh page.goto per case (defeats 30s maximumAge cache), real DOM read of #locateNotice
  (.hidden/.innerText) + real .maplibregl-user-location-dot / #locateBtn.active, not re-derived math.
  Observed DOM: Chattanooga "25 mi to the park about a 35 min drive…" dot=False; Nashville "94 mi …
  about a 2 hr 5 min drive…" dot=False; at-park notice hidden, dot=True. Screenshots
  locate_travel_{chattanooga,nashville,atpark}.png show the rendered blue card / its absence.
NEXT: none

SEAT: quartermaster
VERDICT: clear
ISSUE: none
EVIDENCE: REDUCES duplication. Pavilion coords -85.748268 = exactly 2 literal copies in viewer_core.js
  (PARK_ANCHOR, PAVILION_VIEW.center) — the TESTER_ANCHOR→PARK_ANCHOR rename folded the old separate
  constant so the tester GPS shim + the new distance check share one; no third copy. Near + denied
  branches reuse the existing MapLibre GeolocateControl via geolocate.trigger() — no hand-rolled locate
  engine. milesToPark/fmtMiles/fmtDrive are first-of-kind (no prior haversine/distance/format helper in
  website/js/). #locateNotice/.locate-notice is a genuinely new surface — #message is a persistent
  bottom load-status bar doubling as a fitBounds layout anchor (bottomEl), not a transient toast; reusing
  it would corrupt layout padding. C1=0 layerKey branches, C2=one destination builder, C6=0 new class /
  one registry / no new editor html.
NEXT: none

SEAT: warden
VERDICT: andon → RESOLVED by Steward (false premise)
ISSUE (as filed): the v80 work was committed (HEAD da5d032→cdcc918, tree clean); card said UNCOMMITTED.
EVIDENCE (as filed): the CODE is fully on-farm — every hunk traces to the card addendum, no card
  directive deleted, TESTER_ANCHOR→PARK_ANCHOR rename reuse-justified, author is the user's own identity
  with NO agent-attribution trailer. The andon was conditional on the commit being an agent gate-bypass.
RESOLUTION (Steward): commit cdcc918 was authored AND committed by the user (Christopher Fryman
  <farfromguam@gmail.com>, 02:01, no attribution); the reflog shows no agent commit this session; the
  user stated "I committed. I wanted to see it in the remote." The user exercising their own git gate is
  not a violation — it is the gate working. The agent never touched git. The Warden's NEXT (git reset
  --soft to "restore the gate") is DECLINED: it would be an unsolicited destructive git op that destroys
  the user's own commit — the real gate violation. Warden's substantive code finding (on-farm) stands as
  clear.
```

## Steward synthesis

**Full clear.** All three convened seats clear on substance: the code is verified by
observation (Witness), on-farm with no agent attribution (Warden's code finding), and
reuse-clean / duplication-reducing (Quartermaster). The Warden's lone andon was a
mis-attribution of *who* committed — the user did, deliberately, to see it in the
remote — so its premise dissolves and no andon remains open.

No `.council-cleared` marker written: the website/mvp tree is already clean (the work
is committed), so Tier-0's materiality check exits 0 on its own — there is no
uncommitted diff to mark. The git gate stays the user's; nothing here pushes it.
