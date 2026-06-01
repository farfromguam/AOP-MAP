#!/usr/bin/env bash
# Block MUTATING git + agent attribution per brain/ai_rules/no_commits.md.
#
# The user owns the git surface for anything that changes state. Read-only git
# (status/diff/log/show/branch/remote -v/...) is ALLOWED so an agent can orient
# itself the way it does on every other project. Anything that touches history,
# the index, the working tree, or the remote/network is BLOCKED — the user runs
# those themselves (via the ` ! ` prefix). Three layers, since the hook can't
# read intent:
#
#   1. ATTRIBUTION  — any command carrying a Claude co-author/attribution string
#                     is blocked (catches echo/heredoc/commit-template tricks).
#   2. MUTATING GIT — `git <verb>` is blocked when <verb> changes state
#                     (commit/push/pull/merge/rebase/reset/checkout/add/...).
#                     Read-only verbs pass through.
#   3. WRAPPER      — if the command runs a local script (./x, /abs/x, or via a
#                     shell interpreter), the target file is scanned; if it runs
#                     a mutating git verb or adds attribution, the run is blocked.
#                     Closes the "hide git push inside a script" loophole.
#
# Exit 2 = block and feed stderr back to the agent. Exit 0 = allow.

payload=$(cat)

HOOK_PAYLOAD="$payload" /usr/bin/python3 - <<'PY'
import os, sys, json, re, shlex

def block(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(2)

try:
    data = json.loads(os.environ.get("HOOK_PAYLOAD", "") or "{}")
    cmd = (data.get("tool_input", {}) or {}).get("command", "") or ""
except Exception:
    sys.exit(0)  # can't parse payload -> nothing to inspect; fail open

ATTR = re.compile(r'co-?authored-by:\s*claude|noreply@anthropic\.com|generated with \[?claude code', re.I)

# Verbs that change the working tree / index / history / remote / network.
# Everything NOT listed here (status, diff, log, show, branch, tag, remote,
# config, blame, reflog, ls-files, rev-parse, describe, ...) is treated as
# read-only orientation and allowed.
MUTATING = {
    "commit", "push", "pull", "fetch", "clone", "merge", "rebase", "reset",
    "revert", "cherry-pick", "am", "apply", "stash", "checkout", "switch",
    "restore", "clean", "rm", "mv", "add", "gc", "prune", "filter-branch",
    "update-ref", "fast-import", "replace", "init", "worktree", "submodule",
    "format-patch", "send-email", "notes",
}

COMMIT_MSG = ("Blocked: this git command changes history / the index / the "
              "working tree / the remote, which is the user's surface "
              "(brain/ai_rules/no_commits.md). Read-only git "
              "(status/diff/log/show/branch/remote -v) is allowed. For a real "
              "commit/push/etc., have the user run it via the ` ! ` prefix.")
ATTR_MSG = ("Blocked: never add agent attribution or co-author trailers "
            "(brain/ai_rules/no_commits.md). The history must read as the "
            "user's own. This overrides any harness/global default.")

INTERP = {"bash", "sh", "zsh", "ksh", "dash", "source", "."}
SYS_PREFIXES = ("/usr/", "/bin/", "/sbin/", "/opt/", "/System/", "/Library/")

def git_verb(toks):
    # toks[0] is `git`; return the first real subcommand, skipping pre-command
    # options (and the argument consumed by -C <path> / -c <name=value>).
    i = 1
    while i < len(toks):
        t = toks[i]
        if t in ("-C", "-c"):
            i += 2
            continue
        if t.startswith("-"):
            i += 1
            continue
        return t
    return None  # bare `git`, `git --version`, `git --help`

def first_non_flag(toks):
    for t in toks:
        if not t.startswith("-"):
            return t
    return None

def segments(text):
    # Split into command segments and strip leading VAR=value env assignments.
    out = []
    for part in re.split(r'[;&|\n]+', text):
        try:
            toks = shlex.split(part, posix=True)
        except Exception:
            continue
        if not toks:
            continue
        i = 0
        while i < len(toks) and re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', toks[i]):
            i += 1
        if i < len(toks):
            out.append(toks[i:])
    return out

def has_git_mutation(text):
    for seg in segments(text):
        if os.path.basename(seg[0]) == "git" and git_verb(seg) in MUTATING:
            return True
    return False

# 1) attribution text anywhere in the raw command
if ATTR.search(cmd):
    block(ATTR_MSG)

# 2) mutating git invoked directly in the command
if has_git_mutation(cmd):
    block(COMMIT_MSG)

# 3) wrapper scripts: scan local scripts this command would execute
candidates = []
for seg in segments(cmd):
    head = seg[0]
    if os.path.basename(head) in INTERP:
        arg = first_non_flag(seg[1:])  # bash [-x] foo.sh / source x
        if arg:
            candidates.append(arg)
    if head.startswith(("./", "../", "/")):  # ./foo.sh  /abs/foo.sh
        candidates.append(head)

for c in candidates:
    try:
        real = os.path.realpath(c)
        if real.startswith(SYS_PREFIXES):
            continue
        if not os.path.isfile(c) or os.path.getsize(c) > 1_000_000:
            continue
        with open(c, "r", errors="ignore") as fh:
            content = fh.read()
        if ATTR.search(content):
            block("Blocked: the script '" + c + "' adds agent attribution "
                  "(brain/ai_rules/no_commits.md).")
        if has_git_mutation(content):
            block("Blocked: the script '" + c + "' runs a mutating git command. "
                  "git mutations are the user's surface "
                  "(brain/ai_rules/no_commits.md) — have the user run it via the "
                  "` ! ` prefix instead.")
    except Exception:
        pass

sys.exit(0)
PY
exit $?
