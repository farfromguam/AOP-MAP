#!/usr/bin/env bash
#
# remove-claude-attribution.sh
# One-shot: strip every "Co-Authored-By: Claude" trailer from master history,
# force-push the cleaned history to GitHub, and delete every local ref that
# still points at the old (trailered) commits.
#
# Generated for Christopher Fryman. Safe to delete this file afterward.
#
# Run from anywhere:   bash "remove-claude-attribution.sh"
#
# It aborts on the first error (set -e). Backup tags created earlier
# (backup/pre-decoauthor-master, backup/pre-decoauthor-worktree) are your
# recovery point until step 4 deletes them.

set -euo pipefail

REPO="/Users/christopherfryman/Documents/code/AOP MAP"
cd "$REPO"

echo "==> Repo: $REPO"
echo "==> Step 0: state before"
git log --oneline -3
echo

echo "==> Step 1: rewrite master, dropping 'Co-Authored-By: Claude' lines"
FILTER_BRANCH_SQUELCH_WARNING=1 \
  git filter-branch --msg-filter 'sed "/^Co-Authored-By: Claude/d"' -- master

echo
echo "==> Step 2: verify trailer gone AND content unchanged"
if git log --grep='Co-Authored-By' -i --oneline | grep -q .; then
  echo "!! ABORT: a Co-Authored-By trailer still exists on master."
  exit 1
fi
if ! git diff --quiet backup/pre-decoauthor-master master; then
  echo "!! ABORT: content differs from backup — rewrite changed more than messages."
  echo "   Inspect with: git diff backup/pre-decoauthor-master master"
  exit 1
fi
echo "   OK: only commit messages changed; no file content touched."

echo
echo "==> Step 3: force-push cleaned history to origin/master"
git push --force-with-lease origin master

echo
echo "==> Step 4: delete everything still pointing at the old trailered commits"
git worktree remove --force .claude/worktrees/pwa-offline
git branch -D worktree-pwa-offline
git tag -d backup/pre-decoauthor-master backup/pre-decoauthor-worktree
git update-ref -d refs/original/refs/heads/master 2>/dev/null || true
git reflog expire --expire=now --all
git gc --prune=now

echo
echo "==> Step 5: final check — must print NOTHING under the arrow"
git log --all --grep='Co-Authored-By' -i --oneline
echo "^^ must be empty across ALL refs"
echo
echo "==> DONE."
