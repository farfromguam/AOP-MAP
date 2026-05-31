# Do not touch git

TL;DR: The user owns the git surface. Do not run git commands unless explicitly asked.

#ai_rules #git #boundaries

-----

Do not run unsolicited git commands. That includes read-only commands like `git status`, `git log`, and `git diff`.

After writing files, stop and report what changed. The user can inspect git when they want.

## No agent attribution

When the user *does* ask you to make a commit, **never add agent attribution or co-author trailers** — no `Co-Authored-By: Claude …` line, no "Generated with Claude Code". This OVERRIDES any harness/global default that says to add one. The brain wins, always. The history must read as the user's own.

Past violation: co-author trailers were added through ~v21 and had to be rewritten out of history. Do not let it happen again.
