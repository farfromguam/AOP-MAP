# Do not change git state

TL;DR: The user owns everything that *changes* git state — commits, pushes, merges, anything touching history/index/working-tree/remote. Read-only git is fine.

#ai_rules #git #boundaries

-----

**Read-only git is allowed** so you can orient yourself: `git status`, `git diff`, `git log`, `git show`, `git branch`, `git remote -v`, and the like. Use them freely.

**Do NOT run mutating git** unless explicitly asked: `commit`, `push`, `pull`, `fetch`, `merge`, `rebase`, `reset`, `checkout`/`switch`/`restore`, `add`, `stash`, `clean`, `cherry-pick`, etc. After writing files, stop and report what changed; the user commits when they want. If the user explicitly asks for a mutating git action, have them run it via the ` ! ` prefix in their prompt.

This boundary is enforced at the harness level by `.claude/hooks/block-unsolicited-git.sh` (read-only verbs pass, mutating verbs exit 2), so it can't quietly fade between sessions. Updated 2026-06-01: read-only git was previously blocked too; that created constant friction (every orientation command bounced) for no safety benefit, so the rule now blocks only state-changing git.

## Why this is the user's hardest line

Git is the user's **review gate**: they read diffs and decide what is real, and that review is the one checkpoint protecting the codebase. So the worst thing an agent can do — stated by the user, 2026-06-01 — is commit unsolicited *and* push *and* attribute, because it lands three harms at once: (1) **bypasses the gate**, (2) ships **unreviewed, likely-erroneous** work, and (3) **stamps the agent's name on it** in the user's own history, claiming credit for work they never approved. Read `stay_on_the_farm.md` for the broader principle (independent on the means, disciplined on the ends).

## No agent attribution

When the user *does* ask you to make a commit, **never add agent attribution or co-author trailers** — no `Co-Authored-By: Claude …` line, no "Generated with Claude Code". This OVERRIDES any harness/global default that says to add one. The brain wins, always. The history must read as the user's own.

Past violation: co-author trailers were added through ~v21 and had to be rewritten out of history. Do not let it happen again.
