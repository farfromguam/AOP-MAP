# Verify by observation

TL;DR: Verification means observing the real running system. Never re-derive the expected result yourself and call that verified.

#ai_rules #verification #honesty

-----

Observe rendered pixels, real API return values, real DOM state. Do not re-implement the logic yourself and check your own math.

Origin: on the AOP viewer I claimed the contour zoom-fade was "verified" when I had only reimplemented the MapLibre `interpolate` math in my own JavaScript and checked that. I never observed MapLibre actually render the fade. The user caught it: "did you actually verify that they fade?" Separately, I stated a maxBounds zoom floor of ~15.3 from estimation; the measured value was 13.74 — a wrong claim that changed the diagnosis.

How to apply:

- For a viewer change, take screenshots and look, or use a fixed-camera control test (hold the camera, change one variable, confirm the rendered pixels change).
- For numbers (zoom ranges, counts, sizes), measure them in the running system. Never estimate and present the estimate as fact.
- If a tool to observe directly is missing (e.g. PIL for pixel counts), say the check is visual-only — do not dress up a partial check as full verification.

See `tasks_persist_to_brain.md` for the parallel rule on durable artifacts.
