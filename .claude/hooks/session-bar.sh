#!/usr/bin/env bash
# SessionStart hook: makes the AGENTS.md boot-read un-skippable by injecting a
# thin POINTER into context at the start of every session. It deliberately holds
# NO rule content of its own — the durable rules live only in brain/ai_rules/,
# the single source of truth read by every agent. This hook only ensures the
# agent is pointed at them before acting, so they cannot fade or be skipped.
#
# SessionStart contract: emit {hookSpecificOutput:{additionalContext:"..."}} on
# stdout to prepend text to the model's context for the session.

cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"AOP repo: complete the AGENTS.md boot reads before acting — especially brain/ai_rules/ (work_independently.md is THE BAR, plus act_dont_ask.md, no_redundant_cd.md, verify_by_observation.md). They are non-optional. The brain is the single source of truth — act from it, not from this reminder."}}
JSON
