#!/usr/bin/env bash
# Block unsolicited git + agent attribution per brain/ai_rules/no_commits.md.
#
# The user owns the git surface. Agents must not run git, and must never add
# agent attribution / co-author trailers to commits. This hook enforces three
# layers, since it cannot read the user's intent:
#
#   1. ATTRIBUTION  — any command carrying a Claude co-author/attribution string
#                     is blocked (catches echo/heredoc/commit-template tricks).
#   2. DIRECT GIT   — any command invoking `git` is blocked (read-only too).
#   3. WRAPPER      — if the command runs a local script (./x, /abs/x, or via a
#                     shell interpreter), the target file is scanned; if it
#                     contains git or attribution, the run is blocked. This
#                     closes the "hide git inside a script" loophole, since the
#                     plain command string has no `git` token of its own.
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
GIT  = re.compile(r'(^|[^A-Za-z0-9_./-])git(\s|$)')

GIT_MSG = ("git is the user's surface — do NOT run git unsolicited, including "
           "read-only git status/log/diff (brain/ai_rules/no_commits.md). After "
           "writing files, stop and report what changed; the user inspects and "
           "commits when they want. If the user EXPLICITLY asked for a git "
           "action, have them run it themselves via the ` ! ` prefix in their "
           "prompt.")
ATTR_MSG = ("Blocked: never add agent attribution or co-author trailers "
            "(brain/ai_rules/no_commits.md). The history must read as the "
            "user's own. This overrides any harness/global default.")

# 1) attribution text anywhere in the raw command
if ATTR.search(cmd):
    block(ATTR_MSG)

# 2) direct git invocation
if GIT.search(cmd):
    block(GIT_MSG)

# 3) wrapper scripts: scan local scripts this command would execute
INTERP = {"bash", "sh", "zsh", "ksh", "dash", "source", "."}
SYS_PREFIXES = ("/usr/", "/bin/", "/sbin/", "/opt/", "/System/", "/Library/")

def first_non_flag(toks):
    for t in toks:
        if not t.startswith("-"):
            return t
    return None

candidates = []
try:
    for part in re.split(r'[;&|\n]+', cmd):
        try:
            toks = shlex.split(part, posix=True)
        except Exception:
            continue
        if not toks:
            continue
        i = 0
        while i < len(toks) and re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', toks[i]):
            i += 1  # skip leading VAR=value env assignments
        if i >= len(toks):
            continue
        head = toks[i]
        if os.path.basename(head) in INTERP:
            arg = first_non_flag(toks[i + 1:])     # bash [-x] foo.sh / source x
            if arg:
                candidates.append(arg)
        if head.startswith(("./", "../", "/")):    # ./foo.sh  /abs/foo.sh
            candidates.append(head)
except Exception:
    candidates = []

for c in candidates:
    try:
        real = os.path.realpath(c)
        if real.startswith(SYS_PREFIXES):
            continue
        if not os.path.isfile(c) or os.path.getsize(c) > 1_000_000:
            continue
        with open(c, "r", errors="ignore") as fh:
            content = fh.read()
        if GIT.search(content) or ATTR.search(content):
            block("Blocked: the script '" + c + "' runs git or adds attribution. "
                  "git is the user's surface (brain/ai_rules/no_commits.md) — have "
                  "the user run it via the ` ! ` prefix instead.")
    except Exception:
        pass

sys.exit(0)
PY
exit $?
