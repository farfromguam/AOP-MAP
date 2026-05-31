# No redundant cd; prefer read-only tools

TL;DR: The Bash working directory already persists as the project root on every call. Do not prefix commands with `cd "/Users/.../AOP MAP" && …`. For reading and searching, use the dedicated Read / Grep / Glob tools, which never trigger a permission prompt.

#ai_rules #pacing #permissions

-----

A transcript audit (2026-05-29) found that 86% of Bash calls were compound and 56% started with `cd` into the project root — which is *already* the working directory. `cd` was the one command not on the allowlist, so each redundant `cd … && grep …` forced the user to approve what looked like a read. The user's complaint — "why are you asking if you can read a file??" — traced entirely to this.

## How to apply

- The Bash cwd is the project root at the start of every call. Run `grep …`, `ls …`, `git …` directly. No leading `cd`.
- Only `cd` when you genuinely need a different directory (e.g. a worktree). `Bash(cd *)` is now allowlisted, but the chained `cd` is still noise — set the directory once, not on every command.
- For reading and searching code, reach for the **Read / Grep / Glob** tools before Bash `cat`/`grep`/`find`. They are read-only and never prompt. Use Bash for reads only when a pipeline genuinely needs it.

## Harness-level enforcement (2026-05-31)

The rule alone kept getting ignored across sessions, so it is now enforced by a
hook, not just trusted to memory. `.claude/hooks/block-redundant-cd.sh` is a
`PreToolUse` Bash hook (wired in `.claude/settings.local.json`) that **denies**
any command starting with `cd <project root> && …` (or `;` / `||`) and bounces
it back with instructions to drop the `cd`. The user is not prompted on a hook
deny. A real `cd` into a *subdir* (`cd website`, `cd mvp` — the canonical
spinup commands) passes straight through, as does `cd` into a worktree or
`/tmp`. `Bash(cd *)` is allowlisted so legitimate `cd` never prompts.

If you get bounced by this hook: you wrote a redundant root-`cd`. Re-run the
command on its own — the cwd is already the project root. Adding a hook
mid-session needs a config reload (`/hooks` then Esc, or restart) before it goes
live.

See also: `act_dont_ask.md` (questions are fatigue; so are permission prompts), `canonical_spinup_commands.md`.
