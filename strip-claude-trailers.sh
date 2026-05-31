#!/usr/bin/env bash
# strip-claude-trailers.sh
#
# One-off maintenance: remove "Co-Authored-By: Claude ..." (and any
# "Generated with Claude Code") trailers from every commit on the CURRENT branch.
#
# Why a script: agents in this repo must not run git themselves
# (brain/ai_rules/no_commits.md). You run this; the agent only wrote it.
#
# Safe to delete after use.
set -euo pipefail

branch=$(git rev-parse --abbrev-ref HEAD)

echo "Branch: ${branch}"
echo "Commits carrying a Claude trailer (before):"
git log -i --grep='co-authored-by: claude' --format='  %h %s' || true
count_before=$(git log -i --grep='co-authored-by: claude' --format='%h' | wc -l | tr -d ' ')
echo "  total: ${count_before}"

if [ "${count_before}" -eq 0 ]; then
  echo "Nothing to strip. Exiting clean."
  exit 0
fi

echo
echo "Rewriting history (a backup is kept under refs/original/)..."
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f \
  --msg-filter 'grep -vi -e "co-authored-by: claude" -e "generated with \[claude code\]" || true' \
  -- HEAD

echo
echo "Verifying (should print nothing):"
git log -i --grep='co-authored-by: claude' --oneline || true
count_after=$(git log -i --grep='co-authored-by: claude' --format='%h' | wc -l | tr -d ' ')

echo
echo "Done. Cleaned ${count_before} commit(s); ${count_after} remaining."
echo
echo "Next steps (your call):"
echo "  - If already pushed:  git push --force-with-lease"
echo "  - To undo the rewrite: git reset --hard refs/original/refs/heads/${branch}"
echo "  - Then drop the backup: git update-ref -d refs/original/refs/heads/${branch}"
echo "  - You can delete this script when satisfied."
