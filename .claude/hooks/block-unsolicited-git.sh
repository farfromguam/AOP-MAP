#!/usr/bin/env bash
# Denies unsolicited git commands at the harness level, enforcing
# brain/ai_rules/no_commits.md ("Do not touch git" — the user owns the git
# surface, INCLUDING read-only git status/log/diff).
#
# Thin pointer per brain/ai_rules/harness_adapters_are_thin.md: the rule and its
# rationale live in the brain; this script only blocks and points back.
#
# PreToolUse contract: print a permissionDecision:"deny" JSON to bounce the call
# back to the model with guidance (the user is NOT prompted on a hook deny);
# print nothing + exit 0 to let the call proceed.

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Match `git` as a command token: at the start of the command, or right after a
# shell separator (; & | and so && / ||). Avoids false positives like
# `grep git file`, a `.git/` path, or `gh` / `github` / `gitk`.
re='(^|[;&|])[[:space:]]*git([[:space:]]|$)'

if [[ "$cmd" =~ $re ]]; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"git is the user's surface — do NOT run git unsolicited, including read-only git status/log/diff (brain/ai_rules/no_commits.md). After writing files, stop and report what changed; the user inspects and commits when they want. If the user EXPLICITLY asked for a git action, have them run it themselves via the `!` prefix in their prompt."}}
JSON
fi
exit 0
