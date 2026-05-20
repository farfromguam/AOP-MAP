# Validation Loop

TL;DR: The MVP is not complete until one round of observation capture, review, and promotion proves the loop works.

This northstar doc locks the first validation loop behavior for the AOP map.

## Promise

- Observations enter as evidence, not as direct map edits.
- The first product is a trustworthy map, not a submission UI.
- Evidence must trace back to a source and a confidence level before it becomes part of the core map.
- The map should be able to answer: where did this come from, who observed it, can it be published, and when was it last checked.

## Loop steps

1. Capture an observation from a field session, ride, photo, board markup, or rider note.
2. Record the evidence source and confidence.
3. Review the evidence on the validation board or in the MVP environment.
4. Promote the evidence into the map only when the observation is validated.
5. Document the promotion path and the review result.

## Why this matters

This is the difference between a living map and a rumor collector. Without the loop, the project is building an app before it has a stable data product.

## Next session

- Continue testing this loop in the MVP environment.
- Use `aop_brain/handoff/session_context.md` for the current session context.
- Keep the loop contract in `aop_brain/northstar/validation_loop.md`.
- If the next session discovers a failure in the MVP stack, record it as a session note and only promote stable process changes into `northstar/`.

#northstar #validation #mvp #handoff
