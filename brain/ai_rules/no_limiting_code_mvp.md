# No limiting code during MVP

TL;DR: During the AOP MVP phase, no code that can reject, hide, or filter out data. Everything should display.

#ai_rules #mvp #data #permissive

-----

No `CHECK` constraints, no enum locks, no strict input validation, no row-dropping filters. Publish views currently gate on exact-string equality and a typo silently drops a feature — that is the failure mode the user accepts for now.

The user's call when asked about adding status-column constraints: "skip any limiting code. we want everything to display for now." Visibility beats enforcement at this stage. A constraint that rejects an unexpected value, or a filter that hides a row, costs more than the typo it would catch.

When reviewing or writing AOP code, surface data-integrity risks as documented notes in the relevant task card — not as enforced rules. Do not propose constraints, validators, or gates as fixes.

The "for now" is explicit. Re-confirm before treating this as permanent; it lifts once real trail data exists and vocabularies have settled.
