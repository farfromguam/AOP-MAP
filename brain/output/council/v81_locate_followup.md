# Council — v81 Locate follow-up: bird-flies miles + visible failure path (2026-06-14)

Tier: **core three+** — Witness · Warden · Mason (Mason swapped in for Quartermaster
because v81 is a craft/dead-code change — `fmtDrive` removal, error-path rewrite — not
a reuse question; the v80 reuse review already cleared the surface). Reviewed over the
working-tree diff on top of committed v80 (`cdcc918`): `website/js/viewer_core.js` (the
Locate handler) + `index.html`/`sw.js` v80→v81 bump.

## Outcome: FULL CLEAR (after one andon bounce on the verifier)

```
SEAT: warden    VERDICT: clear
  Every hunk maps to the user's ask ("make it say you are x miles away as the bird
  flies. drop the drive hours" + the "I'm not seeing the popup" report): copy →
  straight-line miles; fmtDrive removed; error/denied + no-geolocation branches now
  showNotice(...) instead of silent geolocate.trigger(); enableHighAccuracy:false is
  the in-bounds fix for "not seeing it" (fast coarse distance), not creep. Git gate
  intact: HEAD still cdcc918 v80 (no agent v81 commit); version strings only; NO
  attribution. node --check passes.

SEAT: mason     VERDICT: clear
  No dead code: fmtDrive + old showTravel name gone with zero refs; fmtMiles /
  showNotice / noticeTimer / milesToPark / NEAR_MI all still live. Idiomatic
  (keeps the notice.innerHTML <strong>+<span> pattern + single-timer clear-then-set
  guard). No limiting code — mi<=NEAR_MI is UX routing, not feature-dropping; error
  path degrades gracefully (shows a message, throws nothing). enableHighAccuracy:false
  + maximumAge:60000 is a minimal fit-for-purpose coarse branch-pick; on-site dot
  still high-accuracy via geolocate.trigger(). No leaked/double setTimeout.

SEAT: witness   VERDICT: andon → CLEAR on re-review
  ANDON (1st pass): the feature is observed-correct (all 4 cases pass via real
    #locateNotice DOM reads; denied path genuinely fires), BUT the "3 consecutive
    PASS, 0 errors" durability claim was not reproducible — 8 runs gave 6 clean, 1
    TargetClosedError crash on a reload, 1 with a transient "Failed to fetch"
    (viewer_core.js:2179, the page's own publish.geojson) + a GL line the noise
    filter missed. The verifier was flaky; the claim overstated.
  FIX (harness only, NOT the feature): load_at() retries goto 3× on nav flake +
    waits for #locateBtn; a classify() splits console/page msgs into gl / transient /
    real — only real fails the run, transient+gl print as visible [note] lines.
    GL_NOISE widened to the GPU-stall/gl-driver/readpixels form; TRANSIENT_NOISE
    covers the unrelated publish.geojson fetch flake.
  RE-REVIEW: CLEAR. Witness's own 10 consecutive re-runs = 10/10 PASS, 0 real
    errors (the prior 25% flake never recurred). Filter judged HONEST and unable to
    mask a locate regression: the locate handler emits no console.error/throw/fetch
    — it signals only via the #locateNotice DOM, a channel separate from the
    console/pageerror events the filter reads; locate vocabulary ("away", "bird
    flies", "Couldn't get your location") shares no substring with the noise buckets;
    a real regression fails a positive behavioral assertion, with no path into the
    swallowed buckets.
```

## Steward synthesis

**Full clear.** The v81 feature code was observed-correct from the first pass; the
single andon was the Witness correctly catching an *over-stated stability claim* on the
verifier (a verify_by_observation honesty catch — the andon loop working as designed).
The harness was hardened (feature code untouched), re-run reproducibly clean (10/10 by
the Witness, 5/5 by the Steward), and the Witness re-reviewed to clear, additionally
confirming the new noise-filtering cannot hide a real locate-path failure.

UNCOMMITTED at clear time (HEAD `cdcc918 v80`); the v81 bump + commit stay the user's
git gate. `.claude/.council-cleared` written for the current website/mvp diff hash.
