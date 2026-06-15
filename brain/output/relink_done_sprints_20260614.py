#!/usr/bin/env python3
"""Rewrite brain links after relocating 8 done sprints into tasks/_done/.
Deterministic: each relative link's target is computed from the file's OLD
location, then re-expressed relative to its NEW location (depth never guessed).
Shorthand `tasks/<moved>/...` tokens are repointed to `tasks/_done/<moved>/...`.
Historical records are skipped (left stale by user's choice).
Usage: aop_relink.py [--apply]   (default = dry run)
"""
import os, re, sys

BRAIN = "/Users/christopherfryman/Documents/code/AOP MAP/brain"
MOVED = ["02_edit","04_edit","05_special_operation","07_tables",
         "08_data_normalization","11_client_convergence",
         "12_field_schedule_editor","13_viewer_extraction"]
APPLY = "--apply" in sys.argv

PATH_RE = re.compile(r'((?:\.\./|\./)[A-Za-z0-9_./\-]+|tasks/[A-Za-z0-9_./\-]+)')

def is_historical(rel):
    if rel.startswith("output/"):
        return True
    if rel.startswith("handoff/coord/"):
        return True
    if re.match(r"handoff/session_context_\d", rel):
        return True
    return False

def old_rel(rel):
    """Map a file's current brain-relative path to where it lived before the move."""
    for s in MOVED:
        pre = f"tasks/_done/{s}/"
        if rel.startswith(pre):
            return "tasks/" + rel[len("tasks/_done/"):]
    if rel == "tasks/_done" or rel.startswith("tasks/_done/"):
        pass
    return rel

def map_target(abs_in_brain):
    """If an intended target falls under a moved sprint's OLD path, return its NEW path."""
    for s in MOVED:
        pre = f"tasks/{s}/"
        if abs_in_brain == f"tasks/{s}" or abs_in_brain.startswith(pre):
            return "tasks/_done/" + abs_in_brain[len("tasks/"):]
    return abs_in_brain

changes = []  # (file, old_token, new_token)

def process(path_rel_current):
    full = os.path.join(BRAIN, path_rel_current)
    with open(full, "r", encoding="utf-8") as fh:
        text = fh.read()
    f_old = old_rel(path_rel_current)
    old_dir = os.path.dirname(f_old)
    cur_dir = os.path.dirname(path_rel_current)
    file_changes = []

    def exists(brain_rel):
        return os.path.exists(os.path.join(BRAIN, brain_rel))

    def repl(m):
        tok = m.group(1)
        if tok.startswith("tasks/"):
            # shorthand brain-relative path; only repoint moved-sprint prefixes
            for s in MOVED:
                if tok == f"tasks/{s}" or tok.startswith(f"tasks/{s}/"):
                    new = "tasks/_done/" + tok[len("tasks/"):]
                    if exists(new.rstrip("/")) and new != tok:
                        file_changes.append((tok, new))
                        return new
                    return tok
            return tok
        # relative ./ or ../ link
        target = os.path.normpath(os.path.join(old_dir, tok))
        mapped = map_target(target)
        # existence guard: only touch links that were VALID before the move
        if not exists(mapped.rstrip("/")):
            return tok
        file_moved = (path_rel_current != f_old)
        target_moved = (mapped != target)
        if not file_moved and not target_moved:
            return tok  # unaffected by the move — leave byte-for-byte
        new = os.path.relpath(mapped, cur_dir) if cur_dir else mapped
        if tok.startswith("./") and not new.startswith("."):
            new = "./" + new
        if tok.endswith("/") and not new.endswith("/"):
            new = new + "/"
        if new != tok:
            file_changes.append((tok, new))
            return new
        return tok

    new_text = PATH_RE.sub(repl, text)
    if file_changes:
        for o, n in file_changes:
            changes.append((path_rel_current, o, n))
        if APPLY and new_text != text:
            with open(full, "w", encoding="utf-8") as fh:
                fh.write(new_text)

for root, dirs, files in os.walk(BRAIN):
    for fn in files:
        if not fn.endswith(".md"):
            continue
        rel = os.path.relpath(os.path.join(root, fn), BRAIN)
        if is_historical(rel):
            continue
        process(rel)

# summarize
byfile = {}
for f, o, n in changes:
    byfile.setdefault(f, []).append((o, n))
print(f"{'APPLIED' if APPLY else 'DRY RUN'} — {len(changes)} link rewrites across {len(byfile)} files\n")
for f in sorted(byfile):
    print(f"### {f}")
    for o, n in byfile[f]:
        print(f"    {o}  ->  {n}")
    print()
