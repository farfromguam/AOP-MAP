SEAT: witness
VERDICT: andon
ISSUE: "Index holds park zoom, no jump (z14 flat, spread 0)" is contradicted by a re-run of the producer's own verifier — it flaps PASS/FAIL and on a slow load shows z12.509 -> z14 climb (spread 1.491).
EVIDENCE: 7 live re-runs of brain/output/verify_no_load_peek.py vs http://localhost:8001/ -> 1 FAIL (samples 30, settled 12.509/14, spread=1.491, 0 console errors) + 6 PASS (flat 14/14, spread 0). Sample count drifts 30/41/41/43/44/41/44 = harness races page load; the >12.5 gate admits the 12.509 settle frame. Peek tokens 0 in c157acc:viewer_band.js and 0 in working tree. 3 scaffolding files deleted, 0 references in index.html/sw.js. Screenshot regenerated (590801->590909 B) but only shows settled z14, cannot witness the early jump.
NEXT: Tighten the verifier gate (wait getZoom()>=13.9 before sampling) OR confirm the 12.5->14 climb is the intended initial framing; re-run until deterministic (no PASS/FAIL flap across 5 runs), then re-witness.
