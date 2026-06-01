#!/usr/bin/env bash
# cleanup_stale_branches.sh — one call to remove the redundant stale branches.
#
# Does, in safe order:
#   1. switch the working tree to master
#   2. remove the pinned copy-review worktree
#   3. delete the two stale safety-net branches: integration-pwa-qa + copy-review
#   4. print the resulting branch list
#
# Both branches are verified redundant:
#   - copy-review        : its tip (d4cf793) is already in master's history.
#   - integration-pwa-qa : v18-frozen PWA-swarm backup; master is 29 commits past
#                          it and already contains the swarm work. Its only unique
#                          content was the intentionally-dropped tree-landcover
#                          pattern, recoverable at 5d825f4.
#
# Agents must not run git in this repo (brain/ai_rules/no_commits.md) — YOU run
# this; the agent only wrote it. Idempotent (safe to re-run). Delete after use.
#
# NOTE: the project git hook blocks mutating git from INSIDE Claude Code (it can't
# tell you from the agent). If `! bash <this>` is blocked, run it in your own
# terminal instead.
set -euo pipefail

REPO="/Users/christopherfryman/Documents/code/AOP MAP"
COPY_WT="/Users/christopherfryman/Documents/code/aop-copy-review"
cd "$REPO"

printf '\n[1/4] switch to master\n'
git switch master 2>/dev/null || git checkout master
echo "  on: $(git rev-parse --abbrev-ref HEAD)"

printf '\n[2/4] remove copy-review worktree (if present)\n'
if git worktree list | grep -qF "$COPY_WT"; then
  git worktree remove "$COPY_WT" 2>/dev/null || git worktree remove --force "$COPY_WT"
  echo "  removed: $COPY_WT"
else
  echo "  already gone"
fi
git worktree prune

printf '\n[3/4] delete stale branches\n'
for b in integration-pwa-qa copy-review; do
  if git show-ref --verify --quiet "refs/heads/$b"; then
    git branch -D "$b"
  else
    echo "  no branch $b (already gone)"
  fi
done

printf '\n[4/4] branches remaining:\n'
git branch -vv

printf '\nDone. Stale branches removed; trailers next (strip-claude-trailers.sh).\n'
