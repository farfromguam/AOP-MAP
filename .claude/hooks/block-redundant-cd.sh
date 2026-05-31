#!/usr/bin/env bash
# Blocks a redundant `cd` into the project root at the START of a Bash command.
#
# Why: the Bash working directory ALREADY persists as the project root on every
# call, so `cd "<project root>" && <cmd>` is pure noise. Bundled that way, the
# whole compound command leads with `cd` and forces a permission approval the
# user is tired of granting. This enforces brain/ai_rules/no_redundant_cd.md at
# the harness level instead of trusting the agent to remember.
#
# What passes through untouched:
#   - a real `cd` into a SUBDIR (cd website && ...  /  cd mvp && ...) — the
#     canonical spinup commands; brain/ai_rules/canonical_spinup_commands.md
#   - a `cd` into any other path (worktrees, /tmp, etc.)
#   - a bare `cd <root>` with no following command
#   - any command that does not start with `cd`
#
# PreToolUse contract: print nothing + exit 0 to let the normal permission flow
# proceed; print a permissionDecision:"deny" JSON to bounce the call back to the
# model with guidance (the user is NOT prompted on a hook deny).

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Project root: prefer the harness-provided var, fall back to cwd (which is the
# project root when this hook runs). Keeps the script portable across machines.
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
root="${root%/}"

# Leading optional quote, the root (optional trailing slash), optional closing
# quote, optional whitespace, then a command separator (&& ; ||).
re="^[[:space:]]*cd[[:space:]]+[\"']?${root}/?[\"']?[[:space:]]*(&&|;|\|\|)"

if [[ "$cmd" =~ $re ]]; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Redundant `cd` into the project root. The Bash working directory is ALREADY the project root on every call — re-run the command WITHOUT the leading `cd \"...AOP MAP\" && `. Use paths relative to the project root, or absolute paths. (Blocked by .claude/hooks/block-redundant-cd.sh enforcing brain/ai_rules/no_redundant_cd.md. A real `cd` into a subdir like `cd website` is fine.)"}}
JSON
fi
exit 0
