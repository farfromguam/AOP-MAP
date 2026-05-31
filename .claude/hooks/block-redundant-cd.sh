#!/usr/bin/env bash
# Auto-strips a redundant `cd <project-root> &&` (or `;`) prefix from a Bash
# command and lets the CLEANED command run — instead of denying and bouncing it
# back to the model to retry.
#
# Why strip instead of deny: the Bash working directory is ALREADY the project
# root on every call, so `cd "<root>" && <cmd>` is pure noise. Bundled that way,
# the compound command leads with `cd` and used to force a permission approval
# the user was tired of granting; the older version of this hook DENIED it,
# which made the model fumble and retry on nearly every turn. Stripping makes it
# just work — no retry, nothing for the user to watch fail.
#
# Why NOT auto-approve: we emit `updatedInput` with NO `permissionDecision`, so
# the CLEANED command is still re-evaluated by the normal settings.json
# allow/deny/ask rules. This keeps the denylist intact — we never punch a hole
# for e.g. `cd <root> && git push --force`. (If a future Claude Code build
# ignores `updatedInput` without a decision, the worst case is the old
# pass-through behavior, never a denylist bypass.)
#
# Enforces brain/ai_rules/no_redundant_cd.md at the harness level instead of
# trusting the model to remember mid-session.
#
# What passes through UNTOUCHED:
#   - a real `cd` into a SUBDIR (cd website && ... / cd mvp && ...) — the
#     canonical spinup commands; brain/ai_rules/canonical_spinup_commands.md
#   - a `cd` into any other path (worktrees, /tmp, etc.)
#   - a bare `cd <root>` with no following command
#   - a `||` separator (stripping `cd root || cmd` would change its semantics)
#   - any command that does not start with `cd <root>`
#
# PreToolUse contract: print nothing + exit 0 to let the normal permission flow
# proceed unchanged; print {hookSpecificOutput:{updatedInput:...}} to replace
# the tool input (here, the cleaned command) before normal evaluation.

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Project root: prefer the harness-provided var, fall back to cwd (which is the
# project root when this hook runs). Keeps the script portable across machines.
root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
root="${root%/}"

# Leading optional quote, the root (optional trailing slash), optional closing
# quote, optional whitespace, then a SAFE separator (&& or ;), optional
# whitespace, then the rest of the command captured for re-emission.
re="^[[:space:]]*cd[[:space:]]+[\"']?${root}/?[\"']?[[:space:]]*(&&|;)[[:space:]]*(.+)$"

if [[ "$cmd" =~ $re ]]; then
  stripped="${BASH_REMATCH[2]}"
  jq -nc --arg c "$stripped" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",updatedInput:{command:$c}}}'
fi
exit 0
