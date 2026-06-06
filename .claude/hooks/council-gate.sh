#!/usr/bin/env bash
# Stop hook: the AOP completion gate (Tier 0), per brain/council/completion_gate.md.
#
# When a main agent tries to finish a turn that touched website/ or mvp/, this runs
# the cheap, deterministic checks and then nudges the agent to convene the council
# (/council) before declaring done. It holds NO rule content of its own — the durable
# gate lives in brain/council/. Three properties keep it from babysitting:
#   - loop guard:   stop_hook_active=true -> exit 0 (never re-block in a loop).
#   - materiality:  no change under website/ or mvp/ -> exit 0 (a chat turn isn't a "done").
#   - nudge-once:   blocks at most once per DISTINCT diff (hash markers in .claude/).
# node --check failures always block (broken code). The council nudge is governed by
# BLOCKING: AOP_COUNCIL_BLOCKING=0 downgrades it to advisory (exit 0 with a message).
# Fails OPEN on any unexpected error — a gate that crashes-closed is worse than no gate.

BLOCKING="${AOP_COUNCIL_BLOCKING:-1}"
ROOT="${AOP_COUNCIL_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
payload=$(cat)

HOOK_PAYLOAD="$payload" AOP_ROOT="$ROOT" AOP_BLOCKING="$BLOCKING" /usr/bin/python3 - <<'PY'
import os, sys, json, subprocess, hashlib, shutil

root = os.environ.get("AOP_ROOT", "")
blocking = os.environ.get("AOP_BLOCKING", "1") == "1"

def sh(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=20)
    except Exception:
        return None

def git(*a):
    r = sh(["git", "-C", root, *a])
    return r.stdout if (r and r.returncode == 0) else ""

try:
    data = json.loads(os.environ.get("HOOK_PAYLOAD", "") or "{}")
except Exception:
    sys.exit(0)  # unparseable payload -> fail open

# 1) loop guard
if data.get("stop_hook_active") is True:
    sys.exit(0)

# 2) materiality — read-only git, scoped to code/data
porc = git("status", "--porcelain", "--", "website", "mvp")
if not porc.strip():
    sys.exit(0)

changed = set()
for line in porc.splitlines():
    p = line[3:].strip()
    if " -> " in p:                       # rename: take the destination
        p = p.split(" -> ", 1)[1].strip()
    if p:
        changed.add(p)

fpath = lambda p: os.path.join(root, p)

# 3) hard checks — changed website/js/*.js must parse (broken code always blocks)
node = shutil.which("node")
synt = []
if node:
    for p in sorted(changed):
        if p.startswith("website/js/") and p.endswith(".js") and os.path.isfile(fpath(p)):
            r = sh([node, "--check", fpath(p)])
            if r and r.returncode != 0:
                errtext = (r.stderr or r.stdout or "")
                errline = next((l.strip() for l in errtext.splitlines() if "Error" in l), "")
                if not errline:                       # fall back to the "file:line" header
                    nonempty = [l.strip() for l in errtext.splitlines() if l.strip()]
                    errline = nonempty[0] if nonempty else "node --check failed"
                synt.append((p, errline))
if synt:
    out = ["BLOCKED (completion gate): changed JS does not parse — fix before declaring done:"]
    out += [f"  {p}: {err}" for p, err in synt]
    sys.stderr.write("\n".join(out) + "\n")
    sys.exit(2)

# 4) advisory findings (carried into the nudge, never block)
adv = []
mainjs = fpath("website/js/main.js")
if os.path.isfile(mainjs):
    try:
        n = sum(1 for l in open(mainjs, encoding="utf-8", errors="ignore")
                if "layerKey === '" in l and not l.strip().startswith("//"))
        if n > 1:
            adv.append(f"C1: {n} non-comment `layerKey === '` branches in main.js "
                       "(target 0, or 1 for the editorPois guard) — Quartermaster.")
    except Exception:
        pass
shell_changed = any(p.startswith("website/js/") or p.startswith("website/css/")
                    or p == "website/index.html" for p in changed)
if shell_changed and "website/sw.js" not in changed:
    adv.append("Version: a shell asset changed but website/sw.js didn't — the sw.js/#appVersion "
               "bump is owed (the user's git gate).")

# 5) clearance marker, keyed to the EXACT diff (any new change invalidates it)
h = hashlib.sha1((git("diff", "HEAD", "--", "website", "mvp") + porc).encode("utf-8", "ignore")).hexdigest()
cleared = os.path.join(root, ".claude", ".council-cleared")
nudged  = os.path.join(root, ".claude", ".council-nudged")
def read(p):
    try:
        return open(p).read().strip()
    except Exception:
        return ""
if read(cleared) == h:
    sys.exit(0)                            # council already cleared THIS diff
if read(nudged) == h:
    sys.exit(0)                            # already nudged this exact diff — don't nag every turn

# 6) nudge once per distinct diff
try:
    open(nudged, "w").write(h)
except Exception:
    pass
lines = ["The work touched website/ or mvp/ and hasn't been run past the council.",
         "Convene it before declaring done:  /council   "
         "(it reviews the diff in fresh, adversarial seats — see brain/council/completion_gate.md)."]
if adv:
    lines.append("Objective gate (advisory):")
    lines += ["  - " + a for a in adv]
sys.stderr.write("\n".join(lines) + "\n")
sys.exit(2 if blocking else 0)
PY
exit $?
